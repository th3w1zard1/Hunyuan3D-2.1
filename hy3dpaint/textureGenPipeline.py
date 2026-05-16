# Hunyuan 3D is licensed under the TENCENT HUNYUAN NON-COMMERCIAL LICENSE AGREEMENT
# except for the third-party components listed below.
# Hunyuan 3D does not impose any additional limitations beyond what is outlined
# in the repsective licenses of these third-party components.
# Users must comply with all terms and conditions of original licenses of these third-party
# components and must ensure that the usage of the third party components adheres to
# all relevant laws and regulations.

# For avoidance of doubts, Hunyuan 3D means the large language models and
# their software and algorithms, including trained model weights, parameters (including
# optimizer states), machine-learning model code, inference-enabling code, training-enabling code,
# fine-tuning enabling code and other elements of the foregoing made publicly available
# by Tencent in accordance with TENCENT HUNYUAN COMMUNITY LICENSE AGREEMENT.

import os
import torch
import copy
import trimesh
import numpy as np
from PIL import Image
from typing import Any, List
from hy3dpaint.image_batches import resize_image_groups
from hy3dpaint.glb_support import resolve_save_glb
from hy3dpaint.output_paths import resolve_texture_output_paths
from hy3dpaint.pipeline_inputs import normalize_image_prompt
from hy3dpaint.config import Hunyuan3DPaintConfig
from hy3dpaint.DifferentiableRenderer.MeshRender import MeshRender
from hy3dpaint.DifferentiableRenderer.mesh_utils import convert_obj_to_glb
from hy3dpaint.utils.image_super_utils import imageSuperNet
from hy3dpaint.utils.multiview_utils import multiviewDiffusionNet
from hy3dpaint.utils.pipeline_utils import ViewProcessor
from hy3dpaint.utils.simplify_mesh_utils import remesh_mesh
from hy3dpaint.utils.uvwrap_utils import mesh_uv_wrap
import warnings

warnings.filterwarnings("ignore")
from diffusers.utils import logging as diffusers_logging

diffusers_logging.set_verbosity(50)


class Hunyuan3DPaintPipeline:
    def __init__(self, config: Hunyuan3DPaintConfig | None = None) -> None:
        self.config = config if config is not None else Hunyuan3DPaintConfig()
        self.models: dict[str, Any] = {}
        self.stats_logs: dict[str, Any] = {}
        self.render = MeshRender(
            default_resolution=self.config.render_size,
            texture_size=self.config.texture_size,
            bake_mode=self.config.bake_mode,
            raster_mode=self.config.raster_mode,
        )
        self.view_processor = ViewProcessor(self.config, self.render)
        self.load_models()

    def load_models(self):
        torch.cuda.empty_cache()
        self.models["super_model"] = imageSuperNet(self.config)
        self.models["multiview_model"] = multiviewDiffusionNet(self.config)
        print("Models Loaded.")

    @torch.no_grad()
    def __call__(
        self,
        mesh_path=None,
        image_path=None,
        output_mesh_path=None,
        use_remesh=True,
        save_glb=True,
    ):
        """Generate texture for 3D mesh using multiview diffusion"""
        if mesh_path is None:
            raise ValueError("mesh_path is required")

        save_glb = resolve_save_glb(output_mesh_path, save_glb)
        obj_output_path, glb_output_path, result_output_path = (
            resolve_texture_output_paths(mesh_path, output_mesh_path, save_glb)
        )

        image_prompt = normalize_image_prompt(image_path)

        # Process mesh
        path = os.path.dirname(mesh_path)
        if use_remesh:
            processed_mesh_path = os.path.join(path, "white_mesh_remesh.obj")
            remesh_mesh(mesh_path, processed_mesh_path)
        else:
            processed_mesh_path = mesh_path

        # Load mesh
        mesh = trimesh.load(processed_mesh_path)
        mesh = mesh_uv_wrap(mesh)
        self.render.load_mesh(mesh=mesh)

        ########### View Selection #########
        selected_camera_elevs, selected_camera_azims, selected_view_weights = (
            self.view_processor.bake_view_selection(
                self.config.candidate_camera_elevs,
                self.config.candidate_camera_azims,
                self.config.candidate_view_weights,
                self.config.max_selected_view_num,
            )
        )

        normal_maps = self.view_processor.render_normal_multiview(
            selected_camera_elevs, selected_camera_azims, use_abs_coor=True
        )
        position_maps = self.view_processor.render_position_multiview(
            selected_camera_elevs, selected_camera_azims
        )

        ##########  Style  ###########
        image_caption = "high quality"
        image_style = []
        for image in image_prompt:
            image = image.resize((512, 512))
            if image.mode == "RGBA":
                white_bg = Image.new("RGB", image.size, (255, 255, 255))
                white_bg.paste(image, mask=image.getchannel("A"))
                image = white_bg
            image_style.append(image)
        image_style = [image.convert("RGB") for image in image_style]

        ###########  Multiview  ##########
        multiviews_pbr = self.models["multiview_model"](
            image_style,
            normal_maps + position_maps,
            prompt=image_caption,
            custom_view_size=self.config.resolution,
            resize_input=True,
        )
        ###########  Enhance  ##########
        enhance_images = {}
        enhance_images["albedo"] = copy.deepcopy(multiviews_pbr["albedo"])
        enhance_images["mr"] = copy.deepcopy(multiviews_pbr["mr"])

        for i in range(len(enhance_images["albedo"])):
            enhance_images["albedo"][i] = self.models["super_model"](
                enhance_images["albedo"][i]
            )
            enhance_images["mr"][i] = self.models["super_model"](
                enhance_images["mr"][i]
            )

        ###########  Bake  ##########
        enhance_images = resize_image_groups(
            enhance_images, (self.config.render_size, self.config.render_size)
        )
        texture, mask = self.view_processor.bake_from_multiview(
            enhance_images["albedo"],
            selected_camera_elevs,
            selected_camera_azims,
            selected_view_weights,
        )
        mask_np = (mask.squeeze(-1).cpu().numpy() * 255).astype(np.uint8)
        texture_mr, mask_mr = self.view_processor.bake_from_multiview(
            enhance_images["mr"],
            selected_camera_elevs,
            selected_camera_azims,
            selected_view_weights,
        )
        mask_mr_np = (mask_mr.squeeze(-1).cpu().numpy() * 255).astype(np.uint8)

        ##########  inpaint  ###########
        texture = self.view_processor.texture_inpaint(texture, mask_np)
        self.render.set_texture(texture, force_set=True)
        if "mr" in enhance_images:
            texture_mr = self.view_processor.texture_inpaint(texture_mr, mask_mr_np)
            self.render.set_texture_mr(texture_mr)

        self.render.save_mesh(obj_output_path, downsample=True)

        if glb_output_path is not None and not convert_obj_to_glb(
            obj_output_path, glb_output_path
        ):
            raise RuntimeError(
                f"Failed to convert textured mesh from {obj_output_path} to {glb_output_path}"
            )

        return result_output_path
