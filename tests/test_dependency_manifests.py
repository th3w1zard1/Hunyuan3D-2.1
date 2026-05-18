from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _read_readme_front_matter_lines() -> list[str]:
    lines = (PROJECT_ROOT / "README.md").read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        raise AssertionError("README.md is missing YAML front matter")

    front_matter_lines: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        front_matter_lines.append(line.rstrip())
    return front_matter_lines


def _read_readme_front_matter() -> dict[str, str]:
    front_matter: dict[str, str] = {}
    for line in _read_readme_front_matter_lines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        front_matter[key.strip()] = value.strip()
    return front_matter


def _read_readme_front_matter_list(key: str) -> list[str]:
    items: list[str] = []
    in_target_list = False

    for line in _read_readme_front_matter_lines():
        if not in_target_list:
            if line.strip() == f"{key}:":
                in_target_list = True
            continue

        if line.startswith("  - "):
            items.append(line.removeprefix("  - ").strip())
            continue

        if line and not line.startswith(" "):
            break

    return items


def _read_lines(relative_path: str) -> list[str]:
    return [
        line.strip()
        for line in (PROJECT_ROOT / relative_path).read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_pillow_is_declared_in_root_runtime_manifests():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
    dependencies = pyproject["project"]["dependencies"]

    assert "pillow>=10,<12" in dependencies
    assert "pillow>=10,<12" in _read_lines("requirements/base.txt")
    assert "pillow>=10,<12" in _read_lines("requirements/space.txt")


def test_packaging_is_declared_in_root_runtime_manifests():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
    dependencies = pyproject["project"]["dependencies"]

    assert "packaging>=24,<26" in dependencies
    assert "packaging>=24,<26" in _read_lines("requirements/base.txt")
    assert "packaging>=24,<26" in _read_lines("requirements/space.txt")


def test_pillow_is_declared_in_hy3dshape_standalone_requirements():
    assert "pillow>=10,<12" in _read_lines("hy3dshape/requirements.txt")


def test_requires_python_matches_runtime_support_envelope():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["requires-python"] == ">=3.10,<3.14"


def test_glb_extra_declares_blender_dependency():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())

    assert pyproject["project"]["optional-dependencies"]["glb"] == ["bpy==4.0"]


def test_gradio_runtime_pin_matches_space_runtime_contract():
    pyproject = tomllib.loads((PROJECT_ROOT / "pyproject.toml").read_text())
    dependencies = pyproject["project"]["dependencies"]
    space_requirements = _read_lines("requirements/space.txt")
    sdk_version = _read_readme_front_matter()["sdk_version"]

    assert f"gradio=={sdk_version}" in dependencies
    assert f"gradio=={sdk_version}" in _read_lines("requirements/base.txt")
    assert not any(line.startswith("gradio") for line in space_requirements)


def test_space_requirements_keep_optional_glb_and_build_tooling_out_of_builder_path():
    space_requirements = _read_lines("requirements/space.txt")

    assert "pybind11==2.13.4" in space_requirements
    assert "-r build.txt" not in space_requirements
    assert not any(line.startswith("basicsr") for line in space_requirements)
    assert not any(line.startswith("bpy") for line in space_requirements)
    assert not any(line.startswith("open3d") for line in space_requirements)
    assert not any(line.startswith("pygltflib") for line in space_requirements)
    assert not any(line.startswith("realesrgan") for line in space_requirements)
    assert not any(line.startswith("--extra-index-url") for line in space_requirements)


def test_space_preloads_only_public_unauthenticated_hub_repos():
    preload_repos = _read_readme_front_matter_list("preload_from_hub")

    assert "tencent/Hunyuan3D-2.1" in preload_repos
    assert "facebook/dinov2-giant" in preload_repos
    assert "stabilityai/stable-diffusion-2-1-base" not in preload_repos
