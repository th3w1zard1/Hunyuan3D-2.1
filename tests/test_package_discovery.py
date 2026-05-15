import importlib.util


def test_hy3dshape_submodules_are_discoverable_without_sys_path_hacks():
    assert importlib.util.find_spec("hy3dshape.utils") is not None
    assert importlib.util.find_spec("hy3dshape.pipelines") is not None


def test_hy3dpaint_submodules_are_discoverable_without_sys_path_hacks():
    assert importlib.util.find_spec("hy3dpaint.textureGenPipeline") is not None
    assert importlib.util.find_spec("hy3dpaint.utils.multiview_utils") is not None
