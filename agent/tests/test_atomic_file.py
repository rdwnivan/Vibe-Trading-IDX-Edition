"""An atomic replacement either commits or preserves the previous target."""

import os

import pytest

from src.atomic_file import replace_with_retry


def _windows_error(code):
    error = PermissionError("simulated Windows failure")
    error.winerror = code
    return error


@pytest.mark.parametrize("code", [5, 32])
def test_transient_windows_replace_commits_after_bounded_backoff(tmp_path, code):
    source, target = tmp_path / "new", tmp_path / "target"
    source.write_bytes(b"new")
    target.write_bytes(b"old")
    attempts, delays = [], []

    def replace(src, dst):
        attempts.append(src)
        if len(attempts) <= 2:
            raise _windows_error(code)
        os.replace(src, dst)

    replace_with_retry(source, target, replace=replace, sleep=delays.append)

    assert target.read_bytes() == b"new"
    assert not source.exists()
    assert len(attempts) == 3
    assert delays == [0.025, 0.05]


def test_exhausted_replace_preserves_target_and_original_error(tmp_path):
    source, target = tmp_path / "new", tmp_path / "target"
    source.write_bytes(b"new")
    target.write_bytes(b"old")
    error = _windows_error(32)
    attempts, delays = [], []

    def replace(src, dst):
        attempts.append(src)
        raise error

    with pytest.raises(PermissionError) as raised:
        replace_with_retry(source, target, replace=replace, sleep=delays.append)

    assert raised.value is error
    assert len(attempts) == 6
    assert delays == [0.025, 0.05, 0.1, 0.2, 0.4]
    assert source.read_bytes() == b"new"
    assert target.read_bytes() == b"old"


@pytest.mark.parametrize("error", [OSError("POSIX error"), _windows_error(2)])
def test_unexpected_replace_error_is_not_retried(tmp_path, error):
    attempts, delays = [], []

    def replace(src, dst):
        attempts.append(src)
        raise error

    with pytest.raises(OSError) as raised:
        replace_with_retry(tmp_path / "new", tmp_path / "target", replace=replace, sleep=delays.append)

    assert raised.value is error
    assert len(attempts) == 1
    assert delays == []
