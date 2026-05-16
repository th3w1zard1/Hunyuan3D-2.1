from pathlib import Path

from PIL import Image
from hy3dpaint import Hunyuan3DPaintConfig
from hy3dpaint.image_batches import resize_image_groups
from hy3dpaint.output_paths import resolve_texture_output_paths
from hy3dpaint.pipeline_inputs import normalize_image_prompt
from hy3dpaint.runtime_paths import get_default_runtime_paths


def test_default_hy3dpaint_runtime_paths_exist():
    runtime_paths = get_default_runtime_paths()

    assert Path(runtime_paths["multiview_cfg_path"]).is_file()
    assert Path(runtime_paths["custom_pipeline"]).is_dir()
    assert Path(runtime_paths["realesrgan_ckpt_path"]).is_file()


def test_public_hy3dpaint_config_import_works_without_runtime_deps(monkeypatch):
    monkeypatch.delenv("HY3D_REALESRGAN_PATH", raising=False)
    monkeypatch.delenv("HY3D_TEX_CFG_PATH", raising=False)
    monkeypatch.delenv("HY3D_TEX_CUSTOM_PIPELINE", raising=False)

    runtime_paths = get_default_runtime_paths()
    conf = Hunyuan3DPaintConfig()

    assert conf.multiview_cfg_path == runtime_paths["multiview_cfg_path"]
    assert conf.custom_pipeline == runtime_paths["custom_pipeline"]
    assert conf.realesrgan_ckpt_path == runtime_paths["realesrgan_ckpt_path"]


def test_resize_image_groups_resizes_every_view_without_mutating_inputs():
    original = {
        "albedo": [Image.new("RGB", (32 + index, 48 + index)) for index in range(3)],
        "mr": [Image.new("RGB", (24 + index, 40 + index)) for index in range(3)],
    }

    resized = resize_image_groups(original, (128, 128))

    assert all(
        image.size == (128, 128) for images in resized.values() for image in images
    )
    assert [image.size for image in original["albedo"]] == [
        (32, 48),
        (33, 49),
        (34, 50),
    ]
    assert [image.size for image in original["mr"]] == [
        (24, 40),
        (25, 41),
        (26, 42),
    ]


def test_normalize_image_prompt_accepts_single_image_and_sequences(tmp_path):
    path_image = tmp_path / "prompt.png"
    Image.new("RGB", (16, 16), color=(255, 0, 0)).save(path_image)

    pil_image = Image.new("RGB", (32, 32), color=(0, 255, 0))

    single = normalize_image_prompt(pil_image)
    sequence = normalize_image_prompt([path_image, pil_image])

    assert len(single) == 1
    assert single[0] is pil_image
    assert len(sequence) == 2
    assert [image.size for image in sequence] == [(16, 16), (32, 32)]


def test_normalize_image_prompt_requires_image_input():
    try:
        normalize_image_prompt(None)
    except ValueError as error:
        assert "image_path is required" in str(error)
    else:
        raise AssertionError("Expected missing image_path to raise ValueError")


def test_resolve_texture_output_paths_defaults_to_glb_result_when_enabled():
    obj_path, glb_path, result_path = resolve_texture_output_paths(
        "assets/demo.glb", None, save_glb=True
    )

    assert obj_path.endswith("textured_mesh.obj")
    assert glb_path is not None and glb_path.endswith("textured_mesh.glb")
    assert result_path.endswith("textured_mesh.glb")


def test_resolve_texture_output_paths_supports_explicit_glb_target():
    obj_path, glb_path, result_path = resolve_texture_output_paths(
        "assets/demo.glb", "demo_textured.glb", save_glb=True
    )

    assert obj_path == "demo_textured.obj"
    assert glb_path == "demo_textured.glb"
    assert result_path == "demo_textured.glb"


def test_resolve_texture_output_paths_rejects_glb_target_without_glb_output():
    try:
        resolve_texture_output_paths(
            "assets/demo.glb", "demo_textured.glb", save_glb=False
        )
    except ValueError as error:
        assert ".glb" in str(error)
    else:
        raise AssertionError("Expected incompatible .glb target to raise ValueError")
