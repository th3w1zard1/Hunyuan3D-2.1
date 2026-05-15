# Hugging Face Space Deployment

## Goals

- Keep GitHub as the primary development repository.
- Keep the Hugging Face Space as an exact mirror of the GitHub repo contents.
- Default the Hugging Face namespace to the same owner as GitHub unless explicitly overridden.
- Avoid manual repo bootstrap steps where automation is safe.

## Local Bootstrap

### 1. Create or attach the GitHub repository

```bash
bash scripts/bootstrap_github_repo.sh
```

This creates the GitHub repo under the authenticated `gh` user by default and adds it as the `github` remote. The existing Hugging Face Space remote can remain as `origin`.

### 2. Prepare runtime artifacts locally

```bash
python -m pip install -e .[torch,build]
python scripts/bootstrap_runtime.py
```

The bootstrap script applies the torchvision compatibility fix, installs `custom_rasterizer` from the bundled wheel when available, falls back to building it from source when the wheel is absent, and compiles the mesh painter helper if needed.

## GitHub Actions Setup

Configure these repository variables:

- `HF_SPACE_NAMESPACE` if the Space should live under an org or a different account. Otherwise it defaults to the GitHub owner.
- `HF_SPACE_NAME` if the Space name should differ from the GitHub repository name.
- `HF_SPACE_SDK` if the Space is not a Gradio Space.
- `HF_SPACE_AUTO_SYNC=true` to automatically mirror `main` pushes.
- `HF_CLI_BIN=hf` if your CI image exposes the newer `hf` alias instead of `huggingface-cli`.

Configure this repository secret:

- `HF_TOKEN`

## Workflow Layout

- [python-ci.yml](../.github/workflows/python-ci.yml) runs linting, package discovery smoke tests, and package builds.
- [release.yml](../.github/workflows/release.yml) builds and uploads distribution artifacts on version tags.
- [sync-hf-space.yml](../.github/workflows/sync-hf-space.yml) resolves the target Space id, ensures the Space exists, and mirrors the GitHub repo using `huggingface/hub-sync`.

## Sync Workflow Behavior

1. Install the Hugging Face Hub CLI support package.
2. Log in non-interactively with `HF_TOKEN`.
3. Resolve the target Space id from repo variables or workflow inputs.
4. Ensure the Space exists. The helper prefers the Hugging Face CLI for public Space creation and falls back to the Python API where the CLI does not expose the needed option set.
5. Mirror the GitHub repository to the Space with deletion-aware sync.

## Manual Trigger

Use the `Sync Hugging Face Space` workflow in GitHub Actions and override the namespace or Space name only when needed.

## Rollback

If a sync introduces a bad deployment:

1. Disable `HF_SPACE_AUTO_SYNC`.
2. Re-run the workflow against a known-good GitHub commit by checking out that revision and pushing it to `main`, or by re-running after reverting the offending commit.
3. If a private Space was created in error, remove it manually from Hugging Face or reuse it by changing `HF_SPACE_NAME`.
