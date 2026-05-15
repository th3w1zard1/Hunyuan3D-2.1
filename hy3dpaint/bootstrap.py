from __future__ import annotations

import importlib
import subprocess
import sysconfig
from pathlib import Path


def _log(level: str, message: str, *args, logger=None) -> None:
    rendered = message % args if args else message
    if logger is None:
        print(rendered)
        return

    log_method = getattr(logger, level, None) or getattr(logger, "info", None)
    if log_method is None:
        print(rendered)
        return

    log_method(message, *args)


def apply_torchvision_compatibility_fix(logger=None) -> bool:
    try:
        from hy3dpaint.utils.torchvision_fix import apply_fix
    except ImportError:
        _log(
            "warning",
            "Torchvision compatibility module not found; proceeding without the compatibility fix.",
            logger=logger,
        )
        return False
    except Exception as error:
        _log(
            "warning",
            "Failed to load torchvision compatibility fix: %s",
            error,
            logger=logger,
        )
        return False

    try:
        return bool(apply_fix())
    except Exception as error:
        _log(
            "warning",
            "Failed to apply torchvision compatibility fix: %s",
            error,
            logger=logger,
        )
        return False


def _ensure_custom_rasterizer(
    project_root: Path, python_executable: str, logger=None
) -> None:
    try:
        custom_rasterizer = importlib.import_module("custom_rasterizer")
        _log(
            "info",
            "custom_rasterizer already installed at %s",
            getattr(custom_rasterizer, "__file__", "<namespace package>"),
            logger=logger,
        )
        return
    except ImportError:
        pass

    wheel_path = project_root / "custom_rasterizer-0.1-cp310-cp310-linux_x86_64.whl"
    source_package = project_root / "hy3dpaint" / "packages" / "custom_rasterizer"

    if wheel_path.exists():
        install_target = str(wheel_path)
        _log(
            "info",
            "Installing custom_rasterizer wheel from %s",
            wheel_path,
            logger=logger,
        )
    elif source_package.exists():
        install_target = str(source_package)
        _log(
            "info",
            "Bundled custom_rasterizer wheel missing; building from source package at %s",
            source_package,
            logger=logger,
        )
    else:
        raise FileNotFoundError(
            f"Missing custom_rasterizer install target. Checked {wheel_path} and {source_package}."
        )

    subprocess.run(
        [python_executable, "-m", "pip", "install", install_target], check=True
    )


def _ensure_mesh_painter(project_root: Path, logger=None) -> None:
    renderer_dir = project_root / "hy3dpaint" / "DifferentiableRenderer"
    ext_suffix = sysconfig.get_config_var("EXT_SUFFIX") or ".so"
    mesh_painter_path = renderer_dir / f"mesh_inpaint_processor{ext_suffix}"

    if mesh_painter_path.exists():
        _log(
            "info",
            "Mesh painter helper already built at %s",
            mesh_painter_path,
            logger=logger,
        )
        return

    _log("info", "Compiling mesh painter helper at %s", renderer_dir, logger=logger)
    subprocess.run(["bash", "compile_mesh_painter.sh"], cwd=renderer_dir, check=True)


def prepare_runtime_environment(
    project_root: str | Path, python_executable: str, logger=None
) -> None:
    resolved_root = Path(project_root).resolve()
    _ensure_custom_rasterizer(resolved_root, python_executable, logger=logger)
    _ensure_mesh_painter(resolved_root, logger=logger)
