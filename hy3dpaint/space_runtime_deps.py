from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any


class NoOpMeshProcessor:
    def __call__(self, mesh, *args, **kwargs):
        return mesh


class NoOpBackgroundRemover:
    def __call__(self, image, *args, **kwargs):
        return image


@dataclass(frozen=True)
class ShapeRuntimeComponents:
    export_to_trimesh: Any
    BackgroundRemover: type
    Hunyuan3DDiTFlowMatchingPipeline: type
    FloaterRemover: type
    DegenerateFaceRemover: type
    FaceReducer: type
    using_background_removal_fallback: bool
    using_mesh_postprocess_fallback: bool


def _is_missing_pymeshlab(error: ImportError) -> bool:
    return getattr(error, "name", None) == "pymeshlab" or "pymeshlab" in str(error)


def _is_missing_background_dep(error: ImportError) -> bool:
    missing_name = getattr(error, "name", None)
    return missing_name in {"rembg", "onnxruntime"} or any(
        token in str(error) for token in ("rembg", "onnxruntime")
    )


def load_shape_runtime_components(*, logger=None) -> ShapeRuntimeComponents:
    pipelines_module = importlib.import_module("hy3dshape.hy3dshape.pipelines")

    using_background_removal_fallback = False
    try:
        rembg_module = importlib.import_module("hy3dshape.hy3dshape.rembg")
        background_remover = rembg_module.BackgroundRemover
    except ImportError as error:
        if not _is_missing_background_dep(error):
            raise

        using_background_removal_fallback = True
        if logger is not None:
            logger.warning(
                "Background removal dependencies are unavailable; input images will be used as-is: %s",
                error,
            )
        background_remover = NoOpBackgroundRemover

    using_mesh_postprocess_fallback = False
    try:
        postprocessors_module = importlib.import_module(
            "hy3dshape.hy3dshape.postprocessors"
        )
        floater_remover = postprocessors_module.FloaterRemover
        degenerate_face_remover = postprocessors_module.DegenerateFaceRemover
        face_reducer = postprocessors_module.FaceReducer
    except ImportError as error:
        if not _is_missing_pymeshlab(error):
            raise

        using_mesh_postprocess_fallback = True
        if logger is not None:
            logger.warning(
                "pymeshlab is unavailable; mesh cleanup and face reduction will run in no-op fallback mode: %s",
                error,
            )
        floater_remover = NoOpMeshProcessor
        degenerate_face_remover = NoOpMeshProcessor
        face_reducer = NoOpMeshProcessor

    return ShapeRuntimeComponents(
        export_to_trimesh=pipelines_module.export_to_trimesh,
        BackgroundRemover=background_remover,
        Hunyuan3DDiTFlowMatchingPipeline=pipelines_module.Hunyuan3DDiTFlowMatchingPipeline,
        FloaterRemover=floater_remover,
        DegenerateFaceRemover=degenerate_face_remover,
        FaceReducer=face_reducer,
        using_background_removal_fallback=using_background_removal_fallback,
        using_mesh_postprocess_fallback=using_mesh_postprocess_fallback,
    )