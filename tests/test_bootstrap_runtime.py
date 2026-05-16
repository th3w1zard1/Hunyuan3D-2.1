from pathlib import Path

from packaging.tags import Tag
from packaging.utils import parse_wheel_filename

from hy3dpaint.bootstrap import _resolve_custom_rasterizer_install_target


def _make_custom_rasterizer_layout(project_root: Path) -> tuple[Path, Path]:
    wheel_path = project_root / "custom_rasterizer-0.1-cp310-cp310-linux_x86_64.whl"
    wheel_path.touch()
    source_package = project_root / "hy3dpaint" / "packages" / "custom_rasterizer"
    source_package.mkdir(parents=True)
    return wheel_path, source_package


def test_custom_rasterizer_prefers_wheel_when_interpreter_tags_match(tmp_path):
    wheel_path, _ = _make_custom_rasterizer_layout(tmp_path)
    _, _, _, wheel_tags = parse_wheel_filename(wheel_path.name)

    target = _resolve_custom_rasterizer_install_target(
        tmp_path, supported_tags=wheel_tags
    )

    assert target == str(wheel_path)


def test_custom_rasterizer_falls_back_to_source_when_wheel_is_incompatible(tmp_path):
    _, source_package = _make_custom_rasterizer_layout(tmp_path)

    target = _resolve_custom_rasterizer_install_target(
        tmp_path,
        supported_tags={Tag("cp311", "cp311", "linux_x86_64")},
    )

    assert target == str(source_package)


def test_custom_rasterizer_requires_source_when_wheel_is_incompatible(tmp_path):
    wheel_path = tmp_path / "custom_rasterizer-0.1-cp310-cp310-linux_x86_64.whl"
    wheel_path.touch()

    try:
        _resolve_custom_rasterizer_install_target(
            tmp_path,
            supported_tags={Tag("cp311", "cp311", "linux_x86_64")},
        )
    except FileNotFoundError as error:
        assert str(wheel_path) in str(error)
    else:
        raise AssertionError(
            "Expected missing source package to raise FileNotFoundError"
        )
