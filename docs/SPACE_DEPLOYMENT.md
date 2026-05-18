# Hugging Face Space Deployment

## Goals

- Keep GitHub as the primary development repository.
- Keep the Hugging Face Space on the same commit you have locally validated.
- Default the Hugging Face namespace to the same owner as GitHub unless explicitly overridden.
- Use the Hugging Face CLI plus a direct git push to the Space remote as the primary deployment path.
- Avoid manual repo bootstrap steps where automation is safe.

## Local Bootstrap

### 1. Create or attach the GitHub repository

```bash
bash scripts/bootstrap_github_repo.sh
```

This creates the GitHub repo under the authenticated `gh` user by default and adds it as the `github` remote. The existing Hugging Face Space remote can remain as `origin`.

### 2. Prepare runtime artifacts locally

```bash
python -m pip install -e .[torch,build,glb]
python scripts/bootstrap_runtime.py
```

The bootstrap script applies the torchvision compatibility fix, installs `custom_rasterizer` from the bundled wheel when that wheel is compatible with the active interpreter, falls back to building it from source otherwise, and compiles the mesh painter helper if needed.

### 3. Push the validated commit to the Space

```bash
python scripts/push_hf_space.py
```

This script:

1. Resolves the target Space id from `HF_SPACE_*` and GitHub-derived defaults.
2. Authenticates with `hf auth login` when `HF_TOKEN` is set, or reuses an existing `hf` login session.
3. Ensures the Space exists.
4. Configures the local `space` git remote.
5. Pushes the current `HEAD` to the target Space branch.

Treat this as the canonical deploy path for operator validation. Do not use ad hoc uploads or file mirroring as the main path.

## GitHub Actions Setup

Configure these repository variables:

- `HF_SPACE_NAMESPACE` if the Space should live under an org or a different account. Otherwise it defaults to the GitHub owner.
- `HF_SPACE_NAME` if the Space name should differ from the GitHub repository name.
- `HF_SPACE_SDK` if the Space is not a Gradio Space.
- `HF_SPACE_AUTO_SYNC=true` to automatically mirror `main` pushes.
- `HF_CLI_BIN=hf` if you need to override the default Hugging Face CLI binary.

Configure this repository secret:

- `HF_TOKEN`

## Workflow Layout

- [python-ci.yml](../.github/workflows/python-ci.yml) runs linting, package discovery smoke tests, and package builds.
- [release.yml](../.github/workflows/release.yml) builds and uploads distribution artifacts on version tags.
- [sync-hf-space.yml](../.github/workflows/sync-hf-space.yml) resolves the target Space id, ensures the Space exists, authenticates with `hf`, and pushes the checked-out commit directly to the Space git remote.

## Sync Workflow Behavior

1. Install the Hugging Face Hub CLI support package.
2. Log in non-interactively with `hf auth login --token "$HF_TOKEN" --add-to-git-credential`.
3. Resolve the target Space id from repo variables or workflow inputs.
4. Ensure the Space exists. The helper prefers the Hugging Face CLI for public Space creation and falls back to the Python API where the CLI does not expose the needed option set.
5. Push the checked-out Git commit to the Space git remote.

## Manual Trigger

Use the `Sync Hugging Face Space` workflow in GitHub Actions and override the namespace or Space name only when needed.

## Required Validation Loop

When a change affects the Space runtime, do not stop at a successful push. Complete the full operator loop:

1. Run the narrowest local check first.
2. Commit the change you just validated.
3. Push the current commit with `python scripts/push_hf_space.py`.
4. Wait for the Space rebuild to complete.
5. Open the public Space and validate generate, export, and download with [jimeng2.png](../assets/example_images/jimeng2.png).
6. If Hugging Face runtime behavior changed, validate HF CPU and HF ZeroGPU sequentially by switching the Space hardware, because one Space cannot run both modes simultaneously.
7. If any step fails, fix the smallest affected slice and repeat the same loop.

## Rollback

If a sync introduces a bad deployment:

1. Disable `HF_SPACE_AUTO_SYNC`.
2. Re-run the workflow against a known-good GitHub commit by checking out that revision and pushing it to `main`, or by re-running after reverting the offending commit.
3. If a private Space was created in error, remove it manually from Hugging Face or reuse it by changing `HF_SPACE_NAME`.
