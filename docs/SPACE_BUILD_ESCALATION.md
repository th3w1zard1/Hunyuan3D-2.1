# HF Space Build Escalation

## Status

- [REPO] GitHub Pages is healthy at `https://th3w1zard1.github.io/Hunyuan3D-2.1/` and returned HTTP `200` during validation on 2026-05-18.
- [REPO] The Hugging Face Space host `https://th3w1zard1-hunyuan3d-2-1.hf.space/` returned HTTP `503` and the public Space page showed `Build error` on 2026-05-18.
- [REPO] The latest pushed Space revision is commit `2cad11f` (`Trim Space startup dependencies`).

## Current Runtime Error

- [UI]{public} Hugging Face Space page shows: `Job failed with exit code: 1` during `base 7/7` at `pip install --no-cache-dir -r /tmp/requirements.txt "torch<=2.11.0" gradio[oauth,mcp]==5.33.0 "uvicorn>=0.14.0" "websockets>=10.4" spaces==0.50.2`.
- [UI]{public} Build logs panel shows: `Failed to retrieve error logs: SSE is not enabled`.
- [REPO] Runtime API payload on 2026-05-18 kept the same opaque failure shape after commits `57a051c`, `354adb2`, `4a34332`, and `2cad11f`.

## Repo-Side Changes Already Tested

- [REPO] `f9ff593` skips Space texture bootstrap when the runtime profile disables texture generation.
- [REPO] `08a083c` removed the old `g++` package requirement by trimming the Space builder package path.
- [REPO] `57a051c` moved the Space front matter from Python `3.10.13` to `3.12.12`.
- [REPO] `354adb2` removed `packages.txt` entirely so the optional HF system-packages layer is skipped.
- [REPO] `4a34332` switched the Space requirements to the PyTorch CPU wheel index so HF resolves `torch` and `torchvision` to `+cpu` wheels.
- [REPO] `2cad11f` removed optional Space startup dependencies and made `pymeshlab` optional for shape-only runtime via a no-op fallback loader.

## Local Reproduction Results

- [REPO] The exact HF `pip install` command succeeds locally from the committed manifests in both `python:3.12-bookworm` and `python:3.12-bullseye` containers.
- [REPO] The latest reduced manifest no longer resolves `pymeshlab`, `pybind11`, or `xatlas` in the default shape-only Space startup slice.
- [REPO] Focused validation passed before deployment:
  - `pytest tests/test_space_runtime_deps.py tests/test_dependency_manifests.py`
  - `ruff check gradio_app.py hy3dpaint/space_runtime_deps.py tests/test_space_runtime_deps.py tests/test_dependency_manifests.py`

## Reproduction Command

- [REPO] Run `bash scripts/reproduce_space_pip_layer.sh` from the repository root.
- [REPO] Optional alternate base image: `bash scripts/reproduce_space_pip_layer.sh python:3.12-bookworm`.

## HF Git Transport Note

- [REPO] On this machine, `hf auth whoami` was not sufficient for Git HTTPS pushes to the `space` remote.
- [REPO] The push path only worked after running `hf auth login --token "$HF_TOKEN" --add-to-git-credential`.

## Assessment

- [SYNTH] The repository now reproduces the failing HF builder layer successfully in local containers while the remote builder still returns the same opaque `base 7/7` failure.
- [SYNTH] The remaining blocker is most likely a Hugging Face managed-builder issue or an HF-specific network/package fetch failure that is not surfaced in public logs.

## Open Questions For HF Support

- [OPEN] What is the underlying stderr for the failing `pip install` step for Space revision `2cad11f`?
- [OPEN] Is the managed builder able to fetch from both PyPI and `https://download.pytorch.org/whl/cpu` for this Space region and hardware profile?
- [OPEN] Why are public build logs unavailable with `Failed to retrieve error logs: SSE is not enabled` for this Space?