"""Where the API server, MCP server and CLI take the opt-in IDX file paths from (RELEASE-01).

The README for the research preview tells the operator where to put
``VIBE_TRADING_IDX_CALENDAR_PATH``. These tests pin the observed behaviour:
API startup (``run_preflight`` in the lifespan) loads the first existing
dotenv among ``~/.vibe-trading/.env``, ``agent/.env`` and ``./.env``, without
overriding exported variables; the standalone CLI loads none. The candidate
paths are redirected to ``tmp_path``, so the operator's real dotenv files are
never read. Bars are synthetic.
"""

import json
import os
from pathlib import Path

from fastapi.testclient import TestClient
import pandas as pd
import pytest

import api_server
from src import preflight
from src.config.accessor import reset_env_config
from src.providers import llm
from src.tools import idx_research_tool

CALENDAR = Path(__file__).parent / "fixtures" / "idx_calendar" / "bei_sessions_2026.json"
CALENDAR_ENV = "VIBE_TRADING_IDX_CALENDAR_PATH"
RECORDS_ENV = "VIBE_TRADING_IDX_EVENT_RECORDS_PATH"
NETWORK_CHECKS = ("_check_okx", "_check_yfinance", "_check_tushare", "_check_akshare", "_check_ccxt")


@pytest.fixture
def dotenv_slots(tmp_path, monkeypatch):
    """Point the three dotenv candidates at empty temp slots and clear the IDX env."""
    slots = {
        "home": tmp_path / "home" / ".vibe-trading" / ".env",
        "agent": tmp_path / "agent" / ".env",
        "cwd": tmp_path / "cwd" / ".env",
    }
    monkeypatch.setattr(llm, "_ENV_CANDIDATES", [slots["home"], slots["agent"], slots["cwd"]])
    monkeypatch.setattr(llm, "_dotenv_loaded", False)
    for name in (CALENDAR_ENV, RECORDS_ENV, "LANGCHAIN_PROVIDER", "LANGCHAIN_MODEL_NAME"):
        monkeypatch.delenv(name, raising=False)
    reset_env_config()
    yield slots
    for name in (CALENDAR_ENV, RECORDS_ENV):
        os.environ.pop(name, None)
    reset_env_config()


@pytest.fixture
def offline_startup(monkeypatch):
    """Run the real lifespan without the data-source network probes or legacy migration."""
    stub = preflight.CheckResult(name="stub", status="skipped", message="offline test", impact="none")
    for name in NETWORK_CHECKS:
        monkeypatch.setattr(preflight, name, lambda stub=stub: stub)
    monkeypatch.setattr("src.config.migrate.migrate_legacy_state", lambda *_a, **_k: None)
    monkeypatch.delenv("API_AUTH_KEY", raising=False)
    monkeypatch.setattr(api_server, "_API_KEY", "")


@pytest.fixture
def bars(monkeypatch):
    days = pd.bdate_range("2026-03-16", "2026-04-24")
    frame = pd.DataFrame(
        {"open": 100.0, "high": 110.0, "low": 90.0, "close": 105.0, "volume": 1000.0},
        index=pd.DatetimeIndex(days),
    )
    provenance = {
        "source": "yahoo",
        "quote_currency": "IDR",
        "exchange_timezone": "Asia/Jakarta",
        "interval": "1D",
        "volume_unit": "shares",
        "adjustment": "unknown",
        "freshness": "not_evaluated",
    }
    data = {"BBCA.JK": frame, "_provenance": {"BBCA.JK": provenance}}
    monkeypatch.setattr(idx_research_tool, "fetch_market_data", lambda **kwargs: data)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _api_calendar_state():
    with TestClient(api_server.app) as client:
        response = client.post(
            "/api/research/idx", json={"codes": ["BBCA.JK"], "lookback": 20, "end_date": "2026-04-24"}
        )
    assert response.status_code == 200
    return response.json().get("sourced_reference", {}).get("calendar")


def test_candidate_order_is_home_then_agent_then_cwd():
    assert llm._ENV_CANDIDATES == [
        Path.home() / ".vibe-trading" / ".env",
        llm.AGENT_DIR / ".env",
        Path.cwd() / ".env",
    ]
    assert llm.AGENT_DIR == Path(api_server.__file__).resolve().parent


def test_api_startup_takes_the_calendar_path_from_the_home_dotenv(dotenv_slots, offline_startup, bars):
    _write(dotenv_slots["home"], f"{CALENDAR_ENV}={CALENDAR}\n")

    state = _api_calendar_state()

    assert state["status"] == "loaded"
    assert state["covered_from"] == "2026-01-01"


def test_api_startup_falls_back_to_agent_dotenv_when_home_has_none(dotenv_slots, offline_startup, bars):
    _write(dotenv_slots["agent"], f"{CALENDAR_ENV}={CALENDAR}\n")

    assert _api_calendar_state()["status"] == "loaded"


def test_only_the_first_existing_dotenv_is_read(dotenv_slots, offline_startup, bars):
    _write(dotenv_slots["home"], "SOME_OTHER_SETTING=1\n")
    _write(dotenv_slots["agent"], f"{CALENDAR_ENV}={CALENDAR}\n")

    assert _api_calendar_state() is None


def test_an_exported_variable_outranks_the_dotenv(dotenv_slots, offline_startup, bars, monkeypatch):
    _write(dotenv_slots["home"], f"{CALENDAR_ENV}={dotenv_slots['home'].parent / 'missing.json'}\n")
    monkeypatch.setenv(CALENDAR_ENV, str(CALENDAR))

    assert _api_calendar_state()["status"] == "loaded"


def test_without_a_dotenv_or_export_the_api_adds_no_sourced_reference(dotenv_slots, offline_startup, bars):
    assert _api_calendar_state() is None


def test_standalone_cli_does_not_read_any_dotenv(dotenv_slots, bars, monkeypatch, capsys):
    _write(dotenv_slots["home"], f"{CALENDAR_ENV}={CALENDAR}\n")
    monkeypatch.setattr("sys.argv", ["idx_research_tool", "BBCA.JK", "--lookback", "20", "--end-date", "2026-04-24"])

    with pytest.raises(SystemExit) as exit_info:
        idx_research_tool.main()

    result = json.loads(capsys.readouterr().out)
    assert exit_info.value.code == 0
    assert "sourced_reference" not in result
    assert CALENDAR_ENV not in os.environ
