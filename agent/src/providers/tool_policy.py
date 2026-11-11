"""Provider-agnostic tool screening: the deny list and the bash policy.

Both are convenience filters, not a security boundary: ``python -c`` can still
run anything, and live orders stay bound by the mandate gate and kill switch.
"""

from __future__ import annotations

import shlex
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

from src.config.accessor import get_env_config

_PYTHON_COMMANDS = frozenset({"python", "python3"})
_READONLY_COMMANDS = frozenset({"ls", "cat", "head", "tail", "wc", "pwd"})
_SHELL_PROCESS_TOOLS = frozenset({"background_run", "cancel_background"})
_SHELL_OPERATOR_CHARS = set("();<>|&")


def _policy_value(generic: str, legacy: str, default: str, legacy_defaults: bool) -> tuple[str, str]:
    config = get_env_config().llm
    if (value := getattr(config, generic)) is not None:
        return value, type(config).model_fields[generic].alias
    if legacy_defaults or legacy in config.model_fields_set:
        return getattr(config, legacy), type(config).model_fields[legacy].alias
    return default, "default"


def _deny_prefixes(*, legacy_defaults: bool = False) -> tuple[str, ...]:
    """Tool-name prefixes never offered to the model; ``""`` disables the list."""
    raw, _ = _policy_value("vibe_trading_deny_tool_prefixes", "claude_cli_deny_tool_prefixes", "", legacy_defaults)
    return tuple(p.strip() for p in raw.split(",") if p.strip())


def bash_policy(*, legacy_defaults: bool = False) -> str:
    """Resolve an explicitly configured cross-provider policy or prior defaults."""
    raw, source = _policy_value("vibe_trading_bash_policy", "claude_cli_bash_policy", "off", legacy_defaults)
    value = raw.strip().lower()
    if value not in {"python-only", "off"}:
        raise RuntimeError(f"{source} must be python-only or off, got {value!r}")
    return value


def policy_status() -> dict[str, Any]:
    """Return the active, non-secret policy for provider diagnostics."""
    config = get_env_config().llm
    legacy_defaults = config.langchain_provider.replace("-", "_") == "claude_cli"
    _, deny_source = _policy_value("vibe_trading_deny_tool_prefixes", "claude_cli_deny_tool_prefixes", "", legacy_defaults)
    _, bash_source = _policy_value("vibe_trading_bash_policy", "claude_cli_bash_policy", "off", legacy_defaults)
    return {
        "deny_tool_prefixes": list(_deny_prefixes(legacy_defaults=legacy_defaults)),
        "deny_tool_prefixes_source": deny_source,
        "bash_policy": bash_policy(legacy_defaults=legacy_defaults),
        "bash_policy_source": bash_source,
    }


def tool_name(definition: dict[str, Any]) -> str:
    return str((definition.get("function") or definition).get("name") or "")


def offered_tools(tools: list[dict[str, Any]], *, legacy_defaults: bool = False) -> list[dict[str, Any]]:
    prefixes = _deny_prefixes(legacy_defaults=legacy_defaults)
    return (
        [t for t in tools if not tool_name(t).startswith(prefixes)]
        if prefixes
        else list(tools)
    )


def _relative_path(token: str) -> bool:
    return not token.startswith(("/", "~")) and ".." not in Path(token).parts


def _hidden_path(token: str) -> bool:
    # ``.env`` and ``.git`` hold credentials; a read would put them in the trace.
    return any(part.startswith(".") and part != "." for part in Path(token).parts)


def _windows_quoted_command(tokens: list[str]) -> str:
    def quote(argument: str) -> str:
        encoded = subprocess.list2cmdline([argument])
        if encoded.startswith('"') and encoded.endswith('"'):
            return encoded
        # list2cmdline doubles trailing slashes only when it adds outer quotes.
        trailing = len(argument) - len(argument.rstrip("\\"))
        return '"' + encoded + "\\" * trailing + '"'

    return " ".join(quote(token) for token in tokens)


def _windows_argv(command: str) -> list[str]:
    """Decode native argv, freeing the block allocated by CommandLineToArgvW."""
    import ctypes

    parse = ctypes.WinDLL("shell32", use_last_error=True).CommandLineToArgvW
    parse.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_int)]
    parse.restype = ctypes.POINTER(ctypes.c_wchar_p)
    release = ctypes.WinDLL("kernel32", use_last_error=True).LocalFree
    release.argtypes = [ctypes.c_void_p]
    release.restype = ctypes.c_void_p
    count = ctypes.c_int()
    values = parse(command, ctypes.byref(count))
    if not values:
        raise ctypes.WinError(ctypes.get_last_error())
    try:
        return [values[index] for index in range(count.value)]
    finally:
        if release(ctypes.cast(values, ctypes.c_void_p)):
            raise ctypes.WinError(ctypes.get_last_error())


def check_bash_command(command: str) -> tuple[Optional[str], Optional[str]]:
    """Apply the ``python-only`` policy to one shell command.

    Args:
        command: The command the model asked ``bash`` to run.

    Returns:
        ``(rewritten_command, None)`` when allowed, else ``(None, reason)``.
        An allowed ``python``/``python3`` call is rewritten to this process's
        interpreter so scripts can import Vibe-Trading's own packages.
    """
    if "\x00" in command:
        return None, "null characters are not allowed"
    if "\n" in command or "`" in command or "$(" in command:
        return None, "newlines, backticks and $( ) are not allowed"
    tokens = None
    if os.name == "nt" and sys.platform == "win32" and command.startswith(_windows_quoted_command([sys.executable]) + " "):
        try:
            native = _windows_argv(command)
        except OSError:
            return None, "unparseable Windows command"
        # Only our fully quoted canonical form bypasses the raw-command lexer.
        # Appending operators or changing quote boundaries cannot use this path.
        if _windows_quoted_command(native) == command:
            tokens = native
    if tokens is None:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        try:
            tokens = list(lexer)
        except ValueError as exc:
            return None, f"unparseable command: {exc}"
    if not tokens:
        return None, "empty command"
    if any(tok and set(tok) <= _SHELL_OPERATOR_CHARS for tok in tokens):
        return None, "shell operators (; && || | redirection) are not allowed"
    program, args = tokens[0], tokens[1:]
    join = subprocess.list2cmdline if os.name == "nt" else shlex.join
    if program in _PYTHON_COMMANDS or program == sys.executable:
        # CRT quoting alone cannot protect a literal quote next to cmd.exe's
        # metacharacters. Refuse this representation instead of splitting the
        # intended Python argument into another shell command.
        if os.name == "nt" and any('"' in arg and any(char in arg for char in "&|<>") for arg in args):
            return None, "quoted Windows shell metacharacters require a relative .py script"
        python_join = _windows_quoted_command if os.name == "nt" else shlex.join
        if args[:1] == ["-c"] and len(args) >= 2:
            return python_join([sys.executable, *args]), None
        if args and args[0].endswith(".py") and _relative_path(args[0]):
            return python_join([sys.executable, *args]), None
        return (
            None,
            "python may only run `python <relative script>.py` or `python -c <code>`",
        )
    if program in _READONLY_COMMANDS:
        paths = [a for a in args if not a.startswith("-")]
        if all(_relative_path(p) and not _hidden_path(p) for p in paths):
            return join(tokens), None
        return (
            None,
            f"{program} may only read non-hidden relative paths inside the working directory",
        )
    return None, f"program {program!r} is not allowed (python-only policy)"


def screen_calls(
    calls: list[dict[str, Any]], offered: set[str], *, legacy_defaults: bool = False
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return calls the host may execute, plus one rejection note per refused call."""
    policy = bash_policy(legacy_defaults=legacy_defaults)
    accepted: list[dict[str, Any]] = []
    notes: list[str] = []
    for call in calls:
        name = str(call.get("name") or "")
        args = dict(call.get("arguments") or {})
        if name not in offered:
            notes.append(f"- {name}: not an available tool")
            continue
        if policy == "python-only" and name in _SHELL_PROCESS_TOOLS:
            notes.append(
                f"- {name}: background processes are not allowed (python-only policy)"
            )
            continue
        if policy == "python-only" and name == "bash":
            rewritten, reason = check_bash_command(str(args.get("command") or ""))
            if reason:
                notes.append(f"- bash `{args.get('command')}`: {reason}")
                continue
            args["command"] = rewritten
        accepted.append({"name": name, "arguments": args})
    return accepted, notes
