from __future__ import annotations

import os
from pathlib import Path


def _default_repo_name() -> str:
    github_repository = os.getenv("GITHUB_REPOSITORY", "")
    if "/" in github_repository:
        return github_repository.rsplit("/", 1)[1]
    return Path.cwd().name


def _default_namespace() -> str:
    return (
        os.getenv("HF_SPACE_NAMESPACE")
        or os.getenv("GITHUB_REPOSITORY_OWNER")
        or os.getenv("GITHUB_ACTOR")
        or ""
    )


def main() -> int:
    repo_name = os.getenv("HF_SPACE_NAME") or _default_repo_name()
    namespace = _default_namespace()
    if not namespace:
        raise SystemExit(
            "Unable to resolve HF space namespace. Set HF_SPACE_NAMESPACE or GITHUB_REPOSITORY_OWNER."
        )

    sdk = os.getenv("HF_SPACE_SDK", "gradio")
    repo_id = f"{namespace}/{repo_name}"

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output_file:
            output_file.write(f"repo_id={repo_id}\n")
            output_file.write(f"repo_name={repo_name}\n")
            output_file.write(f"repo_namespace={namespace}\n")
            output_file.write(f"space_sdk={sdk}\n")

    print(f"repo_id={repo_id}")
    print(f"repo_name={repo_name}")
    print(f"repo_namespace={namespace}")
    print(f"space_sdk={sdk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
