from __future__ import annotations

import sys


SUPPORTED_RUNTIME_PYTHON_MIN = (3, 10)
SUPPORTED_RUNTIME_PYTHON_MAX_EXCLUSIVE = (3, 14)


def get_runtime_python_version(version_info: object | None = None) -> tuple[int, int]:
    current = version_info or sys.version_info
    return int(current[0]), int(current[1])


def is_supported_runtime_python(version_info: object | None = None) -> bool:
    version = get_runtime_python_version(version_info)
    return (
        SUPPORTED_RUNTIME_PYTHON_MIN <= version < SUPPORTED_RUNTIME_PYTHON_MAX_EXCLUSIVE
    )


def get_runtime_python_error_message(version_info: object | None = None) -> str:
    version = get_runtime_python_version(version_info)
    min_major, min_minor = SUPPORTED_RUNTIME_PYTHON_MIN
    max_major, max_minor = SUPPORTED_RUNTIME_PYTHON_MAX_EXCLUSIVE
    return (
        "Hunyuan3D runtime entrypoints require Python "
        f"{min_major}.{min_minor} through {max_major}.{max_minor - 1} for the pinned "
        "PyTorch 2.5.1 stack. "
        f"Detected Python {version[0]}.{version[1]}. "
        "Use a supported interpreter before installing runtime dependencies or running "
        "bootstrap/demo/app entrypoints."
    )


def assert_supported_runtime_python(version_info: object | None = None) -> None:
    if is_supported_runtime_python(version_info):
        return
    raise RuntimeError(get_runtime_python_error_message(version_info))


def exit_if_unsupported_runtime_python(version_info: object | None = None) -> None:
    if is_supported_runtime_python(version_info):
        return
    raise SystemExit(get_runtime_python_error_message(version_info))
