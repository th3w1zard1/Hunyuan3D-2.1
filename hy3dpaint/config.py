import os

from hy3dpaint.runtime_paths import get_default_runtime_paths


class Hunyuan3DPaintConfig:
    def __init__(self, max_num_view=6, resolution=512):
        runtime_paths = get_default_runtime_paths()
        self.device = os.getenv(
            "HY3D_TEX_DEVICE", os.getenv("HY3D_DEVICE", "cuda")
        )

        self.multiview_cfg_path = os.getenv(
            "HY3D_TEX_CFG_PATH", runtime_paths["multiview_cfg_path"]
        )
        self.custom_pipeline = os.getenv(
            "HY3D_TEX_CUSTOM_PIPELINE", runtime_paths["custom_pipeline"]
        )
        self.multiview_pretrained_path = os.getenv(
            "HY3D_TEXGEN_MODEL_PATH", "tencent/Hunyuan3D-2.1"
        )
        self.dino_ckpt_path = os.getenv("HY3D_DINO_MODEL_PATH", "facebook/dinov2-giant")
        self.realesrgan_ckpt_path = os.getenv(
            "HY3D_REALESRGAN_PATH", runtime_paths["realesrgan_ckpt_path"]
        )

        self.raster_mode = "cr"
        self.bake_mode = "back_sample"
        self.render_size = 1024 * 2
        self.texture_size = 1024 * 4
        self.max_selected_view_num = max_num_view
        self.resolution = resolution
        self.bake_exp = 4
        self.merge_method = "fast"

        self.candidate_camera_azims = [0, 90, 180, 270, 0, 180]
        self.candidate_camera_elevs = [0, 0, 0, 0, 90, -90]
        self.candidate_view_weights = [1, 0.1, 0.5, 0.1, 0.05, 0.05]

        for azim in range(0, 360, 30):
            self.candidate_camera_azims.append(azim)
            self.candidate_camera_elevs.append(20)
            self.candidate_view_weights.append(0.01)

            self.candidate_camera_azims.append(azim)
            self.candidate_camera_elevs.append(-20)
            self.candidate_view_weights.append(0.01)
