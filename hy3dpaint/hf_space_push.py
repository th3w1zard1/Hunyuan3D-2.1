from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class HfSpaceConfig:
    repo_id: str
    repo_name: str
    namespace: str
    sdk: str


def _default_repo_name(env: Mapping[str, str], cwd: str | None = None) -> str:
    github_repository = env.get("GITHUB_REPOSITORY", "")
    if "/" in github_repository:
        return github_repository.rsplit("/", 1)[1]
    if cwd is not None:
        return cwd
    return Path.cwd().name


def _default_namespace(
    env: Mapping[str, str], fallback_namespace: str | None = None
) -> str:
    return (
        env.get("HF_SPACE_NAMESPACE")
        or env.get("GITHUB_REPOSITORY_OWNER")
        or env.get("GITHUB_ACTOR")
        or (fallback_namespace or "")
        or ""
    )


def resolve_space_config(
    env: Mapping[str, str] | None = None,
    *,
    cwd: str | None = None,
    fallback_namespace: str | None = None,
) -> HfSpaceConfig:
    env = os.environ if env is None else env
    repo_name = env.get("HF_SPACE_NAME") or _default_repo_name(env, cwd)
    namespace = _default_namespace(env, fallback_namespace)
    if not namespace:
        raise RuntimeError(
            "Unable to resolve HF space namespace. Set HF_SPACE_NAMESPACE or GITHUB_REPOSITORY_OWNER."
        )

    sdk = env.get("HF_SPACE_SDK", "gradio")
    return HfSpaceConfig(
        repo_id=f"{namespace}/{repo_name}",
        repo_name=repo_name,
        namespace=namespace,
        sdk=sdk,
    )


def resolve_cli_bin(env: Mapping[str, str] | None = None) -> str:
    env = os.environ if env is None else env
    return env.get("HF_CLI_BIN", "hf")


def build_hf_auth_login_command(cli_bin: str, token: str) -> list[str]:
    return [
        cli_bin,
        "auth",
        "login",
        "--token",
        token,
        "--add-to-git-credential",
    ]


def build_hf_auth_whoami_command(cli_bin: str) -> list[str]:
    return [cli_bin, "auth", "whoami"]


def build_space_remote_url(repo_id: str) -> str:
    return f"https://huggingface.co/spaces/{repo_id}"


def build_git_push_command(remote_name: str, branch: str = "main") -> list[str]:
    return ["git", "push", remote_name, f"HEAD:{branch}"]
