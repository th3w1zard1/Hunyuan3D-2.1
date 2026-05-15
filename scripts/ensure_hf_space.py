from __future__ import annotations

import os
import subprocess

from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError


def _env_flag(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _resolve_repo_id() -> str:
    repo_id = os.getenv("HF_SPACE_REPO_ID")
    if repo_id:
        return repo_id

    namespace = os.getenv("HF_SPACE_NAMESPACE") or os.getenv("GITHUB_REPOSITORY_OWNER")
    github_repository = os.getenv("GITHUB_REPOSITORY", "")
    repo_name = os.getenv("HF_SPACE_NAME") or github_repository.rsplit("/", 1)[-1]

    if not namespace or not repo_name:
        raise RuntimeError(
            "Unable to resolve HF space repo id. Set HF_SPACE_REPO_ID or provide HF_SPACE_NAMESPACE and HF_SPACE_NAME."
        )

    return f"{namespace}/{repo_name}"


def _resolve_create_command(
    cli_bin: str, repo_id: str, sdk: str, owner_name: str
) -> list[str]:
    namespace, repo_name = repo_id.split("/", 1)
    command = [
        cli_bin,
        "repo",
        "create",
        repo_name,
        "--type",
        "space",
        "--space_sdk",
        sdk,
        "-y",
    ]

    if namespace != owner_name:
        command.extend(["--organization", namespace])

    return command


def main() -> int:
    token = os.getenv("HF_TOKEN")
    if not token:
        raise RuntimeError("HF_TOKEN is required.")

    repo_id = _resolve_repo_id()
    sdk = os.getenv("HF_SPACE_SDK", "gradio")
    private = _env_flag("HF_SPACE_PRIVATE")
    create_if_missing = _env_flag("HF_SPACE_CREATE_IF_MISSING", True)
    cli_bin = os.getenv("HF_CLI_BIN", "huggingface-cli")

    api = HfApi(token=token)
    owner_name = api.whoami(token=token)["name"]

    try:
        api.repo_info(repo_id=repo_id, repo_type="space")
        print(f"Space exists: {repo_id}")
    except HfHubHTTPError as error:
        if not create_if_missing:
            raise RuntimeError(f"Space does not exist: {repo_id}") from error

        if private:
            api.create_repo(
                repo_id=repo_id,
                repo_type="space",
                private=True,
                exist_ok=True,
                space_sdk=sdk,
            )
        else:
            create_command = _resolve_create_command(cli_bin, repo_id, sdk, owner_name)
            subprocess.run(create_command, check=True)
        print(f"Space created or confirmed: {repo_id}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
