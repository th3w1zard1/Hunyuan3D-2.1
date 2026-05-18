from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping


HF_SPACE_ENV_VARS = (
    "SPACE_ID",
    "SPACE_HOST",
    "SPACE_AUTHOR_NAME",
    "SPACE_REPO_NAME",
)
FULL_TEXTURE_ACCELERATORS = ("l40s", "a100")
ZERO_GPU_ACCELERATORS = {"zero", "zerogpu"}
DEFAULT_SHAPE_MODEL_PATH = "tencent/Hunyuan3D-2.1"
DEFAULT_SHAPE_SUBFOLDER = "hunyuan3d-dit-v2-1"
CPU_SAFE_SHAPE_MODEL_PATH = "tencent/Hunyuan3D-2mini"
SHAPE_MODEL_SUBFOLDERS = {
    "tencent/Hunyuan3D-2.1": "hunyuan3d-dit-v2-1",
    "Hunyuan3D-2.1": "hunyuan3d-dit-v2-1",
    "tencent/Hunyuan3D-2": "hunyuan3d-dit-v2-0",
    "Hunyuan3D-2": "hunyuan3d-dit-v2-0",
    "tencent/Hunyuan3D-2mini": "hunyuan3d-dit-v2-mini",
    "Hunyuan3D-2mini": "hunyuan3d-dit-v2-mini",
}


@dataclass(frozen=True)
class RuntimeProfile:
    mode: str
    in_huggingface_space: bool
    is_zerogpu: bool
    accelerator: str
    supports_full_texture: bool
    device: str
    disable_tex: bool
    low_vram_mode: bool
    cache_path: str
    should_enable_cpu_offload: bool
    requested_device: str


def _env_flag(name: str, env: Mapping[str, str], default: bool = False) -> bool:
    value = env.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def running_in_huggingface_space(env: Mapping[str, str] | None = None) -> bool:
    env = os.environ if env is None else env
    return any(env.get(name) for name in HF_SPACE_ENV_VARS)


def supports_full_texture(accelerator: str | None = None) -> bool:
    accelerator = (accelerator or "").lower()
    return any(token in accelerator for token in FULL_TEXTURE_ACCELERATORS)


def is_zero_gpu_accelerator(accelerator: str | None = None) -> bool:
    accelerator = (accelerator or "").strip().lower()
    return accelerator in ZERO_GPU_ACCELERATORS


def zero_gpu_startup_enabled(env: Mapping[str, str] | None = None) -> bool:
    env = os.environ if env is None else env
    if not running_in_huggingface_space(env):
        return False
    return (
        _env_flag("SPACES_ZERO_GPU", env)
        or bool(env.get("SPACES_ZERO_DEVICE_API_URL"))
        or is_zero_gpu_accelerator(env.get("ACCELERATOR"))
    )


def default_shape_model_path(device: str) -> str:
    if device == "cpu":
        return CPU_SAFE_SHAPE_MODEL_PATH
    return DEFAULT_SHAPE_MODEL_PATH


def resolve_shape_subfolder(model_path: str) -> str:
    normalized_path = model_path.strip().rstrip("/")
    model_name = normalized_path.split("/")[-1] if normalized_path else ""
    return SHAPE_MODEL_SUBFOLDERS.get(
        normalized_path,
        SHAPE_MODEL_SUBFOLDERS.get(model_name, DEFAULT_SHAPE_SUBFOLDER),
    )


def resolve_shape_model_selection(
    profile: RuntimeProfile,
    env: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    env = os.environ if env is None else env

    model_path = env.get("HY3D_MODEL_PATH", "").strip() or default_shape_model_path(
        profile.device
    )
    subfolder = env.get("HY3D_SHAPE_SUBFOLDER", "").strip() or resolve_shape_subfolder(
        model_path
    )
    return model_path, subfolder


def resolve_runtime_profile(
    env: Mapping[str, str] | None = None,
    *,
    has_cuda: bool,
    is_zerogpu: bool,
) -> RuntimeProfile:
    env = os.environ if env is None else env
    in_huggingface_space = running_in_huggingface_space(env)
    accelerator = env.get("ACCELERATOR", "")
    effective_zerogpu = is_zerogpu or zero_gpu_startup_enabled(env)
    full_texture = not effective_zerogpu and (
        not in_huggingface_space or supports_full_texture(accelerator)
    )

    default_device = "cuda" if has_cuda else "cpu"
    if in_huggingface_space and effective_zerogpu:
        default_device = "cuda" if has_cuda else "cpu"
    elif in_huggingface_space and not full_texture:
        default_device = "cpu"

    requested_device = (
        env.get("HY3D_DEVICE", default_device).strip().lower() or default_device
    )
    device = requested_device
    if device == "cuda" and not has_cuda:
        device = "cpu"

    if "HY3D_DISABLE_TEX" in env:
        disable_tex = _env_flag("HY3D_DISABLE_TEX", env)
    else:
        disable_tex = effective_zerogpu or not full_texture or device != "cuda"

    if "HY3D_LOW_VRAM_MODE" in env:
        low_vram_mode = _env_flag("HY3D_LOW_VRAM_MODE", env)
    else:
        low_vram_mode = effective_zerogpu or (
            in_huggingface_space and not full_texture
        )

    cache_path = env.get(
        "HY3D_CACHE_PATH",
        "/tmp/hy3d_save_dir" if in_huggingface_space else "./save_dir",
    )

    if in_huggingface_space and effective_zerogpu:
        mode = "hf-zerogpu"
    elif in_huggingface_space and device == "cuda":
        mode = "hf-gpu"
    elif in_huggingface_space:
        mode = "hf-cpu"
    elif device == "cuda":
        mode = "local-gpu"
    else:
        mode = "local-cpu"

    return RuntimeProfile(
        mode=mode,
        in_huggingface_space=in_huggingface_space,
        is_zerogpu=effective_zerogpu,
        accelerator=accelerator,
        supports_full_texture=full_texture,
        device=device,
        disable_tex=disable_tex,
        low_vram_mode=low_vram_mode,
        cache_path=cache_path,
        should_enable_cpu_offload=low_vram_mode and device == "cuda",
        requested_device=requested_device,
    )


def format_runtime_profile(profile: RuntimeProfile) -> str:
    return (
        f"mode={profile.mode}, device={profile.device}, "
        f"disable_tex={profile.disable_tex}, low_vram_mode={profile.low_vram_mode}, "
        f"supports_full_texture={profile.supports_full_texture}, "
        f"zerogpu={profile.is_zerogpu}, accelerator={profile.accelerator or 'unset'}"
    )


def should_use_spaces_gpu(profile: RuntimeProfile) -> bool:
    return profile.in_huggingface_space and profile.is_zerogpu


def get_runtime_notice(
    profile: RuntimeProfile,
    *,
    disable_tex: bool | None = None,
    low_vram_mode: bool | None = None,
) -> str:
    disable_tex = profile.disable_tex if disable_tex is None else disable_tex
    low_vram_mode = profile.low_vram_mode if low_vram_mode is None else low_vram_mode

    if profile.mode == "hf-zerogpu":
        return (
            "Hugging Face ZeroGPU mode is active. Shape generation and export stay available, "
            "while texture generation is disabled by default."
        )
    if profile.mode == "hf-cpu":
        return (
            "Hugging Face CPU mode is active. Shape generation and export stay available, "
            "while texture generation is disabled by default."
        )
    if profile.mode == "local-cpu":
        return (
            "Local CPU mode is active. Shape generation and export stay available, "
            "while texture generation is disabled by default."
        )
    if disable_tex:
        return "Shape-only mode is active because texture generation is disabled for this runtime."
    if low_vram_mode:
        return "Low-VRAM GPU mode is active. The app may offload models back to CPU between steps."
    return "GPU textured generation is available."
