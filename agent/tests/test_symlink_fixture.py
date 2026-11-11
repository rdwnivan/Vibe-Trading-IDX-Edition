"""Capability skips must not hide unexpected filesystem failures."""

import errno
import os

import pytest


def test_missing_windows_symlink_privilege_is_reported_as_skip(make_symlink, monkeypatch, tmp_path):
    error = OSError("symlink privilege unavailable")
    error.winerror = 1314

    def denied(*args, **kwargs):
        raise error

    monkeypatch.setattr(os, "symlink", denied)

    with pytest.raises(pytest.skip.Exception, match="WinError 1314"):
        make_symlink(tmp_path / "link", tmp_path / "target")


@pytest.mark.parametrize("code", [errno.EACCES, errno.EEXIST, errno.ENOENT, errno.EIO])
def test_unexpected_symlink_errors_are_not_skipped(code, make_symlink, monkeypatch, tmp_path):
    error = OSError(code, "unexpected filesystem failure")

    def broken(*args, **kwargs):
        raise error

    monkeypatch.setattr(os, "symlink", broken)

    with pytest.raises(OSError) as raised:
        make_symlink(tmp_path / "link", tmp_path / "target")
    assert raised.value is error


def test_other_windows_privilege_errors_are_not_skipped(make_symlink, monkeypatch, tmp_path):
    error = OSError("access denied")
    error.winerror = 5

    def denied(*args, **kwargs):
        raise error

    monkeypatch.setattr(os, "symlink", denied)

    with pytest.raises(OSError) as raised:
        make_symlink(tmp_path / "link", tmp_path / "target")
    assert raised.value is error


def test_directory_symlink_request_reaches_the_os(make_symlink, monkeypatch, tmp_path):
    calls = []

    def create(target, link, target_is_directory=False):
        calls.append((target, link, target_is_directory))

    monkeypatch.setattr(os, "symlink", create)
    link, target = tmp_path / "link", tmp_path / "target"

    make_symlink(link, target, target_is_directory=True)

    assert calls == [(target, link, True)]
