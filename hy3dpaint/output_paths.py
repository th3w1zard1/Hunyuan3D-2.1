from __future__ import annotations

from os import PathLike
from pathlib import Path


__all__ = ["resolve_texture_output_paths"]


def resolve_texture_output_paths(
    mesh_path: str | PathLike[str],
    output_mesh_path: str | PathLike[str] | None,
    save_glb: bool,
) -> tuple[str, str | None, str]:
    mesh_parent = Path(mesh_path).parent

    if output_mesh_path is None:
        obj_path = mesh_parent / "textured_mesh.obj"
        glb_path = obj_path.with_suffix(".glb") if save_glb else None
        return (
            str(obj_path),
            str(glb_path) if glb_path else None,
            str(glb_path or obj_path),
        )

    target_path = Path(output_mesh_path)
    suffix = target_path.suffix.lower()

    if suffix == ".glb":
        if not save_glb:
            raise ValueError(
                "output_mesh_path cannot end with .glb when save_glb is False"
            )
        obj_path = target_path.with_suffix(".obj")
        return str(obj_path), str(target_path), str(target_path)

    if suffix in ("", ".obj"):
        obj_path = target_path if suffix == ".obj" else target_path.with_suffix(".obj")
        glb_path = obj_path.with_suffix(".glb") if save_glb else None
        return (
            str(obj_path),
            str(glb_path) if glb_path else None,
            str(glb_path or obj_path),
        )

    raise ValueError("output_mesh_path must end with .obj or .glb")
