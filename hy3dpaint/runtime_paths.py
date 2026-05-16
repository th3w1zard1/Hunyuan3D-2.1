from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parent


def get_default_runtime_paths():
    return {
        "multiview_cfg_path": str(_PACKAGE_ROOT / "cfgs" / "hunyuan-paint-pbr.yaml"),
        "custom_pipeline": str(_PACKAGE_ROOT / "hunyuanpaintpbr"),
        "realesrgan_ckpt_path": str(_PACKAGE_ROOT / "ckpt" / "RealESRGAN_x4plus.pth"),
    }
