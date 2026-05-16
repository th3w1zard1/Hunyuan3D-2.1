from hy3dpaint.runtime_compat import (
    assert_supported_runtime_python,
    exit_if_unsupported_runtime_python,
    get_runtime_python_error_message,
    is_supported_runtime_python,
)


def test_runtime_python_support_range_matches_pinned_torch_stack():
    assert is_supported_runtime_python((3, 10)) is True
    assert is_supported_runtime_python((3, 13)) is True
    assert is_supported_runtime_python((3, 9)) is False
    assert is_supported_runtime_python((3, 14)) is False


def test_runtime_python_error_message_is_actionable():
    message = get_runtime_python_error_message((3, 14))

    assert "Python 3.10 through 3.13" in message
    assert "Detected Python 3.14" in message


def test_runtime_python_assertion_raises_for_unsupported_versions():
    try:
        assert_supported_runtime_python((3, 14))
    except RuntimeError as error:
        assert "Detected Python 3.14" in str(error)
    else:
        raise AssertionError("Expected unsupported runtime Python check to raise")


def test_runtime_python_exit_uses_clean_system_exit_message():
    try:
        exit_if_unsupported_runtime_python((3, 14))
    except SystemExit as error:
        assert "Detected Python 3.14" in str(error)
    else:
        raise AssertionError("Expected unsupported runtime Python exit to raise")
