from hy3dpaint.hf_space_push import (
    build_git_push_command,
    build_hf_auth_login_command,
    build_space_remote_url,
    resolve_cli_bin,
    resolve_space_config,
)


def test_resolve_space_config_defaults_to_github_repo_name_and_owner():
    config = resolve_space_config(
        {
            "GITHUB_REPOSITORY": "octo/Hunyuan3D-2.1",
            "GITHUB_REPOSITORY_OWNER": "octo",
        },
        cwd="ignored",
    )

    assert config.repo_id == "octo/Hunyuan3D-2.1"
    assert config.repo_name == "Hunyuan3D-2.1"
    assert config.namespace == "octo"
    assert config.sdk == "gradio"


def test_resolve_space_config_honors_explicit_space_overrides():
    config = resolve_space_config(
        {
            "HF_SPACE_NAMESPACE": "team-space",
            "HF_SPACE_NAME": "demo-space",
            "HF_SPACE_SDK": "gradio",
        },
        cwd="workspace-name",
    )

    assert config.repo_id == "team-space/demo-space"


def test_resolve_space_config_can_fall_back_to_authenticated_hf_user():
    config = resolve_space_config({}, cwd="workspace-name", fallback_namespace="hf-user")

    assert config.repo_id == "hf-user/workspace-name"


def test_resolve_cli_bin_defaults_to_hf():
    assert resolve_cli_bin({}) == "hf"


def test_build_hf_auth_login_command_uses_git_credentials():
    assert build_hf_auth_login_command("hf", "token") == [
        "hf",
        "auth",
        "login",
        "--token",
        "token",
        "--add-to-git-credential",
    ]


def test_build_space_remote_url_targets_spaces_git_remote():
    assert build_space_remote_url("octo/demo-space") == "https://huggingface.co/spaces/octo/demo-space"


def test_build_git_push_command_pushes_head_to_main():
    assert build_git_push_command("space") == ["git", "push", "space", "HEAD:main"]