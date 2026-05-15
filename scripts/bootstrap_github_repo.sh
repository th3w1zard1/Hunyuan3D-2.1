#!/usr/bin/env bash

set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

repo_name="${GH_REPO_NAME:-$(basename "$repo_root")}"
repo_owner="${GH_REPO_OWNER:-$(gh api user --jq .login)}"
repo_visibility="${GH_REPO_VISIBILITY:-public}"
remote_name="${GH_REMOTE_NAME:-github}"
push_after_create="${GH_PUSH_AFTER_CREATE:-true}"

if [[ "$repo_visibility" != "public" && "$repo_visibility" != "private" && "$repo_visibility" != "internal" ]]; then
    echo "Unsupported GH_REPO_VISIBILITY: $repo_visibility" >&2
    exit 1
fi

repo_id="$repo_owner/$repo_name"

if gh repo view "$repo_id" >/dev/null 2>&1; then
    echo "GitHub repository already exists: $repo_id"
    if ! git remote get-url "$remote_name" >/dev/null 2>&1; then
        git remote add "$remote_name" "https://github.com/$repo_id.git"
        echo "Added remote '$remote_name' -> https://github.com/$repo_id.git"
    fi
    exit 0
fi

create_args=(repo create "$repo_id" "--$repo_visibility" --source=. --remote="$remote_name")

if [[ "$push_after_create" == "true" ]]; then
    create_args+=(--push)
fi

gh "${create_args[@]}"
echo "Created GitHub repository: $repo_id"