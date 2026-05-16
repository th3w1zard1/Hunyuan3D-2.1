from pathlib import Path
import tomllib


PROJECT_ROOT = Path(__file__).resolve().parents[1]


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

    assert "gradio==4.44.0" in dependencies
    assert "gradio==4.44.0" in _read_lines("requirements/base.txt")
    assert not any(line.startswith("gradio") for line in space_requirements)
