from hy3dpaint.glb_support import (
    get_glb_conversion_dependency_error_message,
    is_glb_conversion_available,
    load_bpy,
    resolve_save_glb,
)


def test_public_package_exports_glb_availability_helpers():
    from hy3dpaint import (
        get_glb_conversion_dependency_error_message as public_error_message,
    )
    from hy3dpaint import is_glb_conversion_available as public_is_available

    assert public_is_available is is_glb_conversion_available
    assert public_error_message is get_glb_conversion_dependency_error_message


def test_glb_conversion_error_message_mentions_bpy_and_obj_fallback():
    message = get_glb_conversion_dependency_error_message()

    assert "bpy==4.0" in message
    assert ".glb output path" in message
    assert "save_glb=False" in message


def test_load_bpy_raises_actionable_runtime_error_when_missing():
    try:
        load_bpy(import_module=lambda _: (_ for _ in ()).throw(ImportError("missing")))
    except RuntimeError as error:
        assert "bpy==4.0" in str(error)
        assert ".glb output path" in str(error)
        assert "save_glb=False" in str(error)
    else:
        raise AssertionError("Expected missing bpy import to raise RuntimeError")


def test_is_glb_conversion_available_is_false_when_bpy_is_missing():
    assert (
        is_glb_conversion_available(
            import_module=lambda _: (_ for _ in ()).throw(ImportError("missing"))
        )
        is False
    )


def test_is_glb_conversion_available_is_true_when_bpy_import_succeeds():
    assert is_glb_conversion_available(import_module=lambda _: object()) is True


def test_resolve_save_glb_falls_back_to_obj_for_implicit_default_output():
    assert (
        resolve_save_glb(
            output_mesh_path=None,
            save_glb=True,
            import_module=lambda _: (_ for _ in ()).throw(ImportError("missing")),
        )
        is False
    )


def test_resolve_save_glb_rejects_explicit_glb_target_without_bpy():
    try:
        resolve_save_glb(
            output_mesh_path="demo_textured.glb",
            save_glb=True,
            import_module=lambda _: (_ for _ in ()).throw(ImportError("missing")),
        )
    except RuntimeError as error:
        assert "bpy==4.0" in str(error)
        assert ".glb output path" in str(error)
        assert "save_glb=False" in str(error)
    else:
        raise AssertionError("Expected explicit .glb target to require bpy")


def test_resolve_save_glb_keeps_glb_enabled_when_bpy_is_available():
    assert (
        resolve_save_glb(
            output_mesh_path=None,
            save_glb=True,
            import_module=lambda _: object(),
        )
        is True
    )
