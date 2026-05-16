from importlib import import_module

_EXPORTS = {
    "Hunyuan3DPaintConfig": ".config",
    "Hunyuan3DPaintPipeline": ".textureGenPipeline",
    "create_glb_with_pbr_materials": ".convert_utils",
    "get_glb_conversion_dependency_error_message": ".glb_support",
    "is_glb_conversion_available": ".glb_support",
}


def __getattr__(name):
    module_name = _EXPORTS.get(name)
    if module_name is None:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")

    module = import_module(module_name, __name__)
    value = getattr(module, name)
    globals()[name] = value
    return value


__all__ = sorted(_EXPORTS)
