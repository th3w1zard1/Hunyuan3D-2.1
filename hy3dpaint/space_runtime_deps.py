from __future__ import annotations

import importlib
from dataclasses import dataclass
from typing import Any


class NoOpMeshProcessor:
    def __call__(self, mesh, *args, **kwargs):
        return mesh


@dataclass(frozen=True)
class ShapeRuntimeComponents:
    export_to_trimesh: Any
    BackgroundRemover: type
    Hunyuan3DDiTFlowMatchingPipeline: type
    FloaterRemover: type
    DegenerateFaceRemover: type
    FaceReducer: type
    using_mesh_postprocess_fallback: bool


def _is_missing_pymeshlab(error: ImportError) -> bool:
    return getattr(error, "name", None) == "pymeshlab" or "pymeshlab" in str(error)


def load_shape_runtime_components(*, logger=None) -> ShapeRuntimeComponents:
    pipelines_module = importlib.import_module("hy3dshape.hy3dshape.pipelines")
    rembg_module = importlib.import_module("hy3dshape.hy3dshape.rembg")

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
        BackgroundRemover=rembg_module.BackgroundRemover,
        Hunyuan3DDiTFlowMatchingPipeline=pipelines_module.Hunyuan3DDiTFlowMatchingPipeline,
        FloaterRemover=floater_remover,
        DegenerateFaceRemover=degenerate_face_remover,
        FaceReducer=face_reducer,
        using_mesh_postprocess_fallback=using_mesh_postprocess_fallback,
    )