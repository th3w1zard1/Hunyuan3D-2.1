from importlib import import_module
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent
_INNER_PACKAGE = _PACKAGE_ROOT / "hy3dshape"
_EXPORTS = {
    "DEFAULT_IMAGEPROCESSOR",
    "IMAGE_PROCESSORS",
    "DegenerateFaceRemover",
    "FaceReducer",
    "FloaterRemover",
    "Hunyuan3DDiTFlowMatchingPipeline",
    "Hunyuan3DDiTPipeline",
    "ImageProcessorV2",
    "MeshSimplifier",
}

if _INNER_PACKAGE.is_dir():
    __path__.append(str(_INNER_PACKAGE))


def __getattr__(name):
    if name in _EXPORTS:
        module = import_module(".hy3dshape", __name__)
        value = getattr(module, name)
        globals()[name] = value
        return value
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = sorted(_EXPORTS)