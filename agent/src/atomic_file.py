"""Bounded replacement retries for Windows file sharing contention."""

from __future__ import annotations

from collections.abc import Callable
import logging
import os
from pathlib import Path
import time

logger = logging.getLogger(__name__)

TRANSIENT_WINERRORS = (5, 32)
REPLACE_ATTEMPTS = 6
REPLACE_BACKOFF = (0.025, 0.05, 0.1, 0.2, 0.4)


def is_transient_windows_error(exc: OSError) -> bool:
    return getattr(exc, "winerror", None) in TRANSIENT_WINERRORS


def replace_with_retry(
    source: Path,
    target: Path,
    *,
    replace: Callable[[Path, Path], object] | None = None,
    sleep: Callable[[float], None] | None = None,
) -> None:
    """Replace atomically, retrying only WinError 5/32 within a finite budget.

    Callers retain ownership of temporary-file creation, fsync and cleanup.
    Replacement failures propagate; no empty/default state is substituted.
    """
    replace = os.replace if replace is None else replace
    sleep = time.sleep if sleep is None else sleep
    for attempt in range(REPLACE_ATTEMPTS):
        try:
            replace(source, target)
            return
        except OSError as exc:
            code = getattr(exc, "winerror", None)
            if not is_transient_windows_error(exc) or attempt == REPLACE_ATTEMPTS - 1:
                logger.warning("Atomic replacement failed after %d attempt(s), OS code %s", attempt + 1, code)
                raise
            logger.warning("Retrying atomic replacement after Windows contention, code %s, attempt %d", code, attempt + 1)
            sleep(REPLACE_BACKOFF[attempt])
