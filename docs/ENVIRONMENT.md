# Environment Configuration

This project now supports two configuration layers:

1. Runtime application configuration via `HY3D_*` and hardware-related variables.
2. Deployment automation configuration via `HF_*` and GitHub Actions variables.

## Runtime Variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `HY3D_MODEL_PATH` | `tencent/Hunyuan3D-2mini` on CPU runtimes, otherwise `tencent/Hunyuan3D-2.1` | Shape model repository or local path. |
| `HY3D_SHAPE_SUBFOLDER` | Matches the selected shape model (`hunyuan3d-dit-v2-mini` on CPU defaults, otherwise `hunyuan3d-dit-v2-1`) | Shape model subfolder within the model repo. |
| `HY3D_TEXGEN_MODEL_PATH` | `tencent/Hunyuan3D-2.1` | Texture model repository or local path. |
| `HY3D_DEVICE` | `cuda` if available, otherwise `cpu` | Primary inference device. |
| `HY3D_CACHE_PATH` | `/tmp/hy3d_save_dir` on Spaces, otherwise `./save_dir` | Generated asset cache/output directory. |
| `HY3D_DISABLE_TEX` | Auto-derived from hardware on Spaces | Force-disable texture generation. |
| `HY3D_LOW_VRAM_MODE` | Auto-derived from hardware on Spaces | Enable lower-memory execution mode. |
| `HY3D_DINO_MODEL_PATH` | `facebook/dinov2-giant` | DINO checkpoint or repo id used by texture generation. |
| `HY3D_REALESRGAN_PATH` | bundled `hy3dpaint` checkpoint | Override the packaged RealESRGAN checkpoint path. |
| `HY3D_TEX_CFG_PATH` | bundled `hy3dpaint` config | Override the packaged texture model config path. |
| `HY3D_TEX_CUSTOM_PIPELINE` | bundled `hy3dpaint` pipeline module | Override the packaged custom Diffusers pipeline path. |
| `HY3D_TEX_DEVICE` | `HY3D_DEVICE` if set, otherwise `cuda` | Texture generation device override for standalone texture workflows. The Gradio app resolves one shared runtime device before startup. |
| `ACCELERATOR` | unset | Hugging Face hardware hint used to decide whether full texture generation should be enabled. |

## Runtime Mode Defaults

The Gradio app now resolves one runtime profile before model startup.

| Mode | Default device | Texture default | Low-VRAM default | Notes |
| --- | --- | --- | --- | --- |
| Local GPU | `cuda` | Enabled | Disabled | Full shape + texture path. |
| Local CPU | `cpu` | Disabled | Disabled | Shape generation and export remain available by default, using the smaller `Hunyuan3D-2mini` shape checkpoint unless overridden. |
| HF GPU (`ACCELERATOR` includes `l40s` or `a100`) | `cuda` | Enabled | Disabled | Full Space path for shape + texture. |
| HF CPU or smaller shared hardware | `cpu` | Disabled | Enabled | Shape-only fallback path for public Space validation, using `Hunyuan3D-2mini` by default to stay within tighter memory budgets. |
| HF ZeroGPU | `cuda` when available, otherwise `cpu` | Disabled | Enabled | Requires the Gradio SDK and `@spaces.GPU`-decorated GPU work. |

When texture generation is disabled by default, shape generation, mesh export, and download must still work. Set `HY3D_DISABLE_TEX=0` only when the underlying hardware and memory budget are known to support it.

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
| `HF_CLI_BIN` | `hf` | CLI binary to use for auth and Space creation. |
| `HF_SPACE_REMOTE_NAME` | `space` | Git remote name used by `python scripts/push_hf_space.py`. |
| `HF_SPACE_REMOTE_BRANCH` | `main` | Target branch used by `python scripts/push_hf_space.py`. |

## Required Secrets

| Secret | Scope | Purpose |
| --- | --- | --- |
| `HF_TOKEN` | Local shell or GitHub Actions | Write-capable Hugging Face token for `hf auth login`, Space creation, and git pushes to the Space remote. |

## Notes

- Texture generation defaults now resolve relative to the installed `hy3dpaint` package. Set `HY3D_REALESRGAN_PATH`, `HY3D_TEX_CFG_PATH`, or `HY3D_TEX_CUSTOM_PIPELINE` only when you need to override the bundled assets.
- The pinned PyTorch runtime in this repo must be installed on a Python version with matching wheels. During current validation on Linux, `torch==2.5.1` did not resolve on Python 3.14, and the official CUDA 12.4 wheel index exposes `cp310` through `cp313` builds but not `cp314`.
- The runtime bootstrap script is [scripts/bootstrap_runtime.py](../scripts/bootstrap_runtime.py).
- The GitHub bootstrap helper is [scripts/bootstrap_github_repo.sh](../scripts/bootstrap_github_repo.sh).
- The Space sync helper scripts are [scripts/resolve_hf_space_config.py](../scripts/resolve_hf_space_config.py), [scripts/ensure_hf_space.py](../scripts/ensure_hf_space.py), and [scripts/push_hf_space.py](../scripts/push_hf_space.py).
