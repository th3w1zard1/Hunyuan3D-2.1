from hy3dpaint.config import Hunyuan3DPaintConfig
from hy3dpaint.runtime_profile import (
    default_shape_model_path,
    get_runtime_notice,
    resolve_runtime_profile,
    resolve_shape_model_selection,
    resolve_shape_subfolder,
    should_use_spaces_gpu,
    zero_gpu_startup_enabled,
)


def test_local_gpu_profile_defaults_to_textured_cuda_mode():
    profile = resolve_runtime_profile({}, has_cuda=True, is_zerogpu=False)

    assert profile.mode == "local-gpu"
    assert profile.device == "cuda"
    assert profile.disable_tex is False
    assert profile.low_vram_mode is False
    assert profile.cache_path == "./save_dir"


def test_local_cpu_profile_defaults_to_shape_only_mode():
    profile = resolve_runtime_profile({}, has_cuda=False, is_zerogpu=False)

    assert profile.mode == "local-cpu"
    assert profile.device == "cpu"
    assert profile.disable_tex is True
    assert profile.low_vram_mode is False
    assert resolve_shape_model_selection(profile, {}) == (
        "tencent/Hunyuan3D-2mini",
        "hunyuan3d-dit-v2-mini",
    )


def test_hf_cpu_profile_disables_texture_and_uses_tmp_cache():
    profile = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "cpu-basic"},
        has_cuda=False,
        is_zerogpu=False,
    )

    assert profile.mode == "hf-cpu"
    assert profile.device == "cpu"
    assert profile.disable_tex is True
    assert profile.low_vram_mode is True
    assert profile.cache_path == "/tmp/hy3d_save_dir"
    assert resolve_shape_model_selection(profile, {}) == (
        "tencent/Hunyuan3D-2mini",
        "hunyuan3d-dit-v2-mini",
    )


def test_hf_gpu_profile_keeps_texture_enabled_on_l40s():
    profile = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "l40sx1"},
        has_cuda=True,
        is_zerogpu=False,
    )

    assert profile.mode == "hf-gpu"
    assert profile.device == "cuda"
    assert profile.disable_tex is False
    assert profile.low_vram_mode is False
    assert profile.supports_full_texture is True


def test_hf_zerogpu_profile_keeps_cuda_when_available_but_disables_texture():
    profile = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "zerogpu"},
        has_cuda=True,
        is_zerogpu=True,
    )

    assert profile.mode == "hf-zerogpu"
    assert profile.device == "cuda"
    assert profile.disable_tex is True
    assert profile.low_vram_mode is True
    assert profile.should_enable_cpu_offload is True


def test_hf_zerogpu_profile_accepts_accelerator_zero_hint_without_spaces_probe():
    profile = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "zero"},
        has_cuda=True,
        is_zerogpu=False,
    )

    assert profile.mode == "hf-zerogpu"
    assert profile.device == "cuda"
    assert profile.disable_tex is True
    assert profile.low_vram_mode is True


def test_runtime_notice_calls_out_shape_only_zerogpu_mode():
    profile = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "zerogpu"},
        has_cuda=True,
        is_zerogpu=True,
    )

    notice = get_runtime_notice(profile)

    assert "ZeroGPU" in notice
    assert "texture generation is disabled by default" in notice


def test_runtime_notice_calls_out_local_cpu_fallback():
    profile = resolve_runtime_profile({}, has_cuda=False, is_zerogpu=False)

    notice = get_runtime_notice(profile)

    assert "Local CPU mode" in notice
    assert "Shape generation and export stay available" in notice


def test_spaces_gpu_wrapper_is_reserved_for_hf_zerogpu():
    local_gpu = resolve_runtime_profile({}, has_cuda=True, is_zerogpu=False)
    hf_cpu = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "cpu-basic"},
        has_cuda=False,
        is_zerogpu=False,
    )
    hf_gpu = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "l40sx1"},
        has_cuda=True,
        is_zerogpu=False,
    )
    hf_zerogpu = resolve_runtime_profile(
        {"SPACE_ID": "owner/space", "ACCELERATOR": "zerogpu"},
        has_cuda=True,
        is_zerogpu=True,
    )

    assert should_use_spaces_gpu(local_gpu) is False
    assert should_use_spaces_gpu(hf_cpu) is False
    assert should_use_spaces_gpu(hf_gpu) is False
    assert should_use_spaces_gpu(hf_zerogpu) is True


def test_zero_gpu_startup_detects_accelerator_and_platform_hints():
    assert zero_gpu_startup_enabled({"SPACE_ID": "owner/space", "ACCELERATOR": "zero"}) is True
    assert (
        zero_gpu_startup_enabled(
            {
                "SPACE_ID": "owner/space",
                "SPACES_ZERO_DEVICE_API_URL": "https://device-api.example",
            }
        )
        is True
    )
    assert (
        zero_gpu_startup_enabled(
            {"SPACE_ID": "owner/space", "ACCELERATOR": "cpu-basic"}
        )
        is False
    )


def test_explicit_env_overrides_take_precedence_when_supported():
    profile = resolve_runtime_profile(
        {
            "SPACE_ID": "owner/space",
            "ACCELERATOR": "cpu-basic",
            "HY3D_DEVICE": "cpu",
            "HY3D_DISABLE_TEX": "0",
            "HY3D_LOW_VRAM_MODE": "0",
            "HY3D_CACHE_PATH": "/data/cache",
        },
        has_cuda=False,
        is_zerogpu=False,
    )

    assert profile.mode == "hf-cpu"
    assert profile.device == "cpu"
    assert profile.disable_tex is False
    assert profile.low_vram_mode is False
    assert profile.cache_path == "/data/cache"


def test_requested_cuda_falls_back_to_cpu_when_cuda_is_unavailable():
    profile = resolve_runtime_profile(
        {"HY3D_DEVICE": "cuda"},
        has_cuda=False,
        is_zerogpu=False,
    )

    assert profile.mode == "local-cpu"
    assert profile.requested_device == "cuda"
    assert profile.device == "cpu"
    assert profile.disable_tex is True


def test_shape_subfolder_tracks_selected_model_path():
    assert resolve_shape_subfolder("tencent/Hunyuan3D-2mini") == "hunyuan3d-dit-v2-mini"
    assert resolve_shape_subfolder("/models/Hunyuan3D-2") == "hunyuan3d-dit-v2-0"


def test_explicit_shape_model_override_keeps_override_but_infers_matching_subfolder():
    profile = resolve_runtime_profile({}, has_cuda=True, is_zerogpu=False)

    assert default_shape_model_path("cpu") == "tencent/Hunyuan3D-2mini"
    assert resolve_shape_model_selection(
        profile,
        {"HY3D_MODEL_PATH": "tencent/Hunyuan3D-2mini"},
    ) == ("tencent/Hunyuan3D-2mini", "hunyuan3d-dit-v2-mini")


def test_paint_config_defaults_to_primary_device_when_texture_override_is_unset(
    monkeypatch,
):
    monkeypatch.delenv("HY3D_TEX_DEVICE", raising=False)
    monkeypatch.setenv("HY3D_DEVICE", "cpu")

    conf = Hunyuan3DPaintConfig()

    assert conf.device == "cpu"
