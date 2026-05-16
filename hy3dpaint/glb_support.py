from __future__ import annotations

import importlib
from os import PathLike
from pathlib import Path
from types import ModuleType


__all__ = [
    "get_glb_conversion_dependency_error_message",
    "is_glb_conversion_available",
    "load_bpy",
    "resolve_save_glb",
]


def get_glb_conversion_dependency_error_message() -> str:
    return (
        "GLB conversion requires bpy==4.0. Install the optional 'glb' extra "
        "or stop targeting a .glb output path and call the paint pipeline with "
        "save_glb=False to keep the textured OBJ output."
    )


def is_glb_conversion_available(import_module=importlib.import_module) -> bool:
    try:
        import_module("bpy")
    except ImportError:
        return False
    return True


def resolve_save_glb(
    output_mesh_path: str | PathLike[str] | None,
    save_glb: bool,
    import_module=importlib.import_module,
) -> bool:
    if not save_glb:
        return False

    if is_glb_conversion_available(import_module=import_module):
        return True

    if output_mesh_path is not None and Path(output_mesh_path).suffix.lower() == ".glb":
        raise RuntimeError(get_glb_conversion_dependency_error_message())

    return False


def load_bpy(import_module=importlib.import_module) -> ModuleType:
    try:
        return import_module("bpy")
    except ImportError as error:
        raise RuntimeError(get_glb_conversion_dependency_error_message()) from error
