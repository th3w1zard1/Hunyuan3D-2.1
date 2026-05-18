from types import SimpleNamespace

import pytest

import hy3dpaint.space_runtime_deps as space_runtime_deps


def test_load_shape_runtime_components_uses_postprocessors_when_available(monkeypatch):
    pipeline_class = type("Pipeline", (), {})
    background_remover = type("BackgroundRemover", (), {})
    floater_remover = type("FloaterRemover", (), {})
    degenerate_face_remover = type("DegenerateFaceRemover", (), {})
    face_reducer = type("FaceReducer", (), {})

    modules = {
        "hy3dshape.hy3dshape.pipelines": SimpleNamespace(
            export_to_trimesh="exporter",
            Hunyuan3DDiTFlowMatchingPipeline=pipeline_class,
        ),
        "hy3dshape.hy3dshape.rembg": SimpleNamespace(
            BackgroundRemover=background_remover,
        ),
        "hy3dshape.hy3dshape.postprocessors": SimpleNamespace(
            FloaterRemover=floater_remover,
            DegenerateFaceRemover=degenerate_face_remover,
            FaceReducer=face_reducer,
        ),
    }

    monkeypatch.setattr(
        space_runtime_deps.importlib,
        "import_module",
        lambda name: modules[name],
    )

    components = space_runtime_deps.load_shape_runtime_components()

    assert components.export_to_trimesh == "exporter"
    assert components.BackgroundRemover is background_remover
    assert components.Hunyuan3DDiTFlowMatchingPipeline is pipeline_class
    assert components.FloaterRemover is floater_remover
    assert components.DegenerateFaceRemover is degenerate_face_remover
    assert components.FaceReducer is face_reducer
    assert components.using_background_removal_fallback is False
    assert components.using_mesh_postprocess_fallback is False


def test_load_shape_runtime_components_falls_back_when_pymeshlab_is_missing(
    monkeypatch,
):
    logger_messages = []

    class Logger:
        def warning(self, message, error):
            logger_messages.append((message, str(error)))

    missing_pymeshlab = ModuleNotFoundError("No module named 'pymeshlab'")
    missing_pymeshlab.name = "pymeshlab"

    modules = {
        "hy3dshape.hy3dshape.pipelines": SimpleNamespace(
            export_to_trimesh="exporter",
            Hunyuan3DDiTFlowMatchingPipeline=type("Pipeline", (), {}),
        ),
        "hy3dshape.hy3dshape.rembg": SimpleNamespace(
            BackgroundRemover=type("BackgroundRemover", (), {}),
        ),
    }

    def fake_import(name):
        if name == "hy3dshape.hy3dshape.postprocessors":
            raise missing_pymeshlab
        return modules[name]

    monkeypatch.setattr(space_runtime_deps.importlib, "import_module", fake_import)

    components = space_runtime_deps.load_shape_runtime_components(logger=Logger())

    mesh = object()
    assert components.using_mesh_postprocess_fallback is True
    assert components.FloaterRemover()(mesh) is mesh
    assert components.DegenerateFaceRemover()(mesh) is mesh
    assert components.FaceReducer()(mesh, 5000) is mesh
    assert logger_messages == [
        (
            "pymeshlab is unavailable; mesh cleanup and face reduction will run in no-op fallback mode: %s",
            "No module named 'pymeshlab'",
        )
    ]


def test_load_shape_runtime_components_falls_back_when_background_deps_are_missing(
    monkeypatch,
):
    logger_messages = []

    class Logger:
        def warning(self, message, error):
            logger_messages.append((message, str(error)))

    missing_onnxruntime = ModuleNotFoundError("No module named 'onnxruntime'")
    missing_onnxruntime.name = "onnxruntime"

    modules = {
        "hy3dshape.hy3dshape.pipelines": SimpleNamespace(
            export_to_trimesh="exporter",
            Hunyuan3DDiTFlowMatchingPipeline=type("Pipeline", (), {}),
        ),
        "hy3dshape.hy3dshape.postprocessors": SimpleNamespace(
            FloaterRemover=type("FloaterRemover", (), {}),
            DegenerateFaceRemover=type("DegenerateFaceRemover", (), {}),
            FaceReducer=type("FaceReducer", (), {}),
        ),
    }

    def fake_import(name):
        if name == "hy3dshape.hy3dshape.rembg":
            raise missing_onnxruntime
        return modules[name]

    monkeypatch.setattr(space_runtime_deps.importlib, "import_module", fake_import)

    components = space_runtime_deps.load_shape_runtime_components(logger=Logger())

    image = object()
    assert components.using_background_removal_fallback is True
    assert components.BackgroundRemover()(image) is image
    assert logger_messages == [
        (
            "Background removal dependencies are unavailable; input images will be used as-is: %s",
            "No module named 'onnxruntime'",
        )
    ]


def test_load_shape_runtime_components_reraises_other_import_errors(monkeypatch):
    modules = {
        "hy3dshape.hy3dshape.pipelines": SimpleNamespace(
            export_to_trimesh="exporter",
            Hunyuan3DDiTFlowMatchingPipeline=type("Pipeline", (), {}),
        ),
        "hy3dshape.hy3dshape.rembg": SimpleNamespace(
            BackgroundRemover=type("BackgroundRemover", (), {}),
        ),
    }
    unrelated_error = ModuleNotFoundError("No module named 'yaml'")
    unrelated_error.name = "yaml"

    def fake_import(name):
        if name == "hy3dshape.hy3dshape.postprocessors":
            raise unrelated_error
        return modules[name]

    monkeypatch.setattr(space_runtime_deps.importlib, "import_module", fake_import)

    with pytest.raises(ModuleNotFoundError, match="yaml"):
        space_runtime_deps.load_shape_runtime_components()
