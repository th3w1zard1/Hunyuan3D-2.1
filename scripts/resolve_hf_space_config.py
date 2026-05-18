from __future__ import annotations

import os

from hy3dpaint.hf_space_push import resolve_space_config


def main() -> int:
    config = resolve_space_config(os.environ)

    github_output = os.getenv("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as output_file:
            output_file.write(f"repo_id={config.repo_id}\n")
            output_file.write(f"repo_name={config.repo_name}\n")
            output_file.write(f"repo_namespace={config.namespace}\n")
            output_file.write(f"space_sdk={config.sdk}\n")

    print(f"repo_id={config.repo_id}")
    print(f"repo_name={config.repo_name}")
    print(f"repo_namespace={config.namespace}")
    print(f"space_sdk={config.sdk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
