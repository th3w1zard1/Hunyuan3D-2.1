from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from hy3dpaint.hf_space_push import (
    build_git_push_command,
    build_hf_auth_login_command,
    build_hf_auth_whoami_command,
    build_space_remote_url,
    resolve_cli_bin,
    resolve_space_config,
)
from scripts.ensure_hf_space import main as ensure_hf_space_main


def _run(command: list[str], cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def _ensure_command(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"Required command not found on PATH: {name}")


def _ensure_hf_auth(cli_bin: str, token: str | None) -> None:
    if token:
        _run(build_hf_auth_login_command(cli_bin, token))
        return

    try:
        _run(build_hf_auth_whoami_command(cli_bin))
    except subprocess.CalledProcessError as error:
        raise RuntimeError(
            "HF_TOKEN is not set and the Hugging Face CLI is not already authenticated. "
            "Run `hf auth login` or export HF_TOKEN before pushing the Space."
        ) from error


def _get_authenticated_hf_user(cli_bin: str) -> str:
    result = subprocess.run(
        build_hf_auth_whoami_command(cli_bin),
        check=True,
        capture_output=True,
        text=True,
    )
    for line in result.stdout.splitlines():
        if line.lower().startswith("user:"):
            return line.split(":", 1)[1].strip()
    raise RuntimeError("Unable to resolve authenticated Hugging Face user from `hf auth whoami`.")


def _configure_remote(remote_name: str, remote_url: str) -> None:
    result = subprocess.run(
        ["git", "remote", "get-url", remote_name],
        cwd=PROJECT_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode == 0:
        current_url = result.stdout.strip()
        if current_url != remote_url:
            _run(["git", "remote", "set-url", remote_name, remote_url], cwd=PROJECT_ROOT)
        return

    _run(["git", "remote", "add", remote_name, remote_url], cwd=PROJECT_ROOT)


def main() -> int:
    env = os.environ.copy()
    cli_bin = resolve_cli_bin(env)
    remote_name = env.get("HF_SPACE_REMOTE_NAME", "space")
    branch = env.get("HF_SPACE_REMOTE_BRANCH", "main")

    _ensure_command("git")
    _ensure_command(cli_bin)
    _ensure_hf_auth(cli_bin, env.get("HF_TOKEN"))
    fallback_namespace = _get_authenticated_hf_user(cli_bin)
    config = resolve_space_config(
        env,
        cwd=PROJECT_ROOT.name,
        fallback_namespace=fallback_namespace,
    )

    env.setdefault("HF_SPACE_REPO_ID", config.repo_id)
    env.setdefault("HF_SPACE_SDK", config.sdk)
    env.setdefault("HF_CLI_BIN", cli_bin)
    os.environ.update(env)
    ensure_hf_space_main()

    _run(["git", "lfs", "install", "--local"], cwd=PROJECT_ROOT)
    remote_url = build_space_remote_url(config.repo_id)
    _configure_remote(remote_name, remote_url)
    _run(build_git_push_command(remote_name, branch), cwd=PROJECT_ROOT)

    print(f"Pushed current HEAD to {config.repo_id} via remote '{remote_name}'")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())