# Environment Configuration

This project now supports two configuration layers:

1. Runtime application configuration via `HY3D_*` and hardware-related variables.
2. Deployment automation configuration via `HF_*` and GitHub Actions variables.

## Runtime Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `HY3D_MODEL_PATH` | `tencent/Hunyuan3D-2.1` | Shape model repository or local path. |
| `HY3D_SHAPE_SUBFOLDER` | `hunyuan3d-dit-v2-1` | Shape model subfolder within the model repo. |
| `HY3D_TEXGEN_MODEL_PATH` | `tencent/Hunyuan3D-2.1` | Texture model repository or local path. |
| `HY3D_DEVICE` | `cuda` if available, otherwise `cpu` | Primary inference device. |
| `HY3D_CACHE_PATH` | `/tmp/hy3d_save_dir` on Spaces, otherwise `./save_dir` | Generated asset cache/output directory. |
| `HY3D_DISABLE_TEX` | Auto-derived from hardware on Spaces | Force-disable texture generation. |
| `HY3D_LOW_VRAM_MODE` | Auto-derived from hardware on Spaces | Enable lower-memory execution mode. |
| `HY3D_DINO_MODEL_PATH` | `facebook/dinov2-giant` | DINO checkpoint or repo id used by texture generation. |
| `HY3D_REALESRGAN_PATH` | bundled `hy3dpaint` checkpoint | Override the packaged RealESRGAN checkpoint path. |
| `HY3D_TEX_CFG_PATH` | bundled `hy3dpaint` config | Override the packaged texture model config path. |
| `HY3D_TEX_CUSTOM_PIPELINE` | bundled `hy3dpaint` pipeline module | Override the packaged custom Diffusers pipeline path. |
| `HY3D_TEX_DEVICE` | `cuda` | Texture generation device override. |
| `ACCELERATOR` | unset | Hugging Face hardware hint used to decide whether full texture generation should be enabled. |

## Hugging Face Space Sync Variables

These variables are intended for GitHub Actions repo variables or workflow inputs.

| Variable | Default | Purpose |
| --- | --- | --- |
| `HF_SPACE_NAMESPACE` | `GITHUB_REPOSITORY_OWNER` | Target Hugging Face user or org. By default this matches the GitHub owner. |
| `HF_SPACE_NAME` | GitHub repository name | Target Space name. |
| `HF_SPACE_SDK` | `gradio` | Space SDK passed during Space creation. |
| `HF_SPACE_AUTO_SYNC` | `false` | When set to `true`, pushes to `main` trigger the Space mirror workflow automatically. |
| `HF_SPACE_PRIVATE` | `false` | Create a private Space if a new one must be bootstrapped. |
| `HF_SPACE_CREATE_IF_MISSING` | `true` | Allow automation to create the Space when it does not exist yet. |
| `HF_CLI_BIN` | `huggingface-cli` | CLI binary to use. Override this to `hf` if your environment exposes the newer alias. |

## Required Secrets

| Secret | Scope | Purpose |
| --- | --- | --- |
| `HF_TOKEN` | GitHub Actions | Write-capable Hugging Face token for Space creation and mirroring. |

## Notes

- Texture generation defaults now resolve relative to the installed `hy3dpaint` package. Set `HY3D_REALESRGAN_PATH`, `HY3D_TEX_CFG_PATH`, or `HY3D_TEX_CUSTOM_PIPELINE` only when you need to override the bundled assets.
- The pinned PyTorch runtime in this repo must be installed on a Python version with matching wheels. During current validation on Linux, `torch==2.5.1` did not resolve on Python 3.14, and the official CUDA 12.4 wheel index exposes `cp310` through `cp313` builds but not `cp314`.
- The runtime bootstrap script is [scripts/bootstrap_runtime.py](../scripts/bootstrap_runtime.py).
- The GitHub bootstrap helper is [scripts/bootstrap_github_repo.sh](../scripts/bootstrap_github_repo.sh).
- The Space sync helper scripts are [scripts/resolve_hf_space_config.py](../scripts/resolve_hf_space_config.py) and [scripts/ensure_hf_space.py](../scripts/ensure_hf_space.py).
