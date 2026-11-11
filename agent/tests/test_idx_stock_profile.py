"""Synthetic IDX profile contracts; no Yahoo/account access."""

import json
import asyncio
from datetime import datetime, timezone

import pytest

from src.tools import stock_profile_tool as profiles


@pytest.fixture
def summary():
    return {
        "price": {
            "symbol": "BBCA.JK",
            "exchange": "JKT",
            "quoteType": "EQUITY",
            "currency": "IDR",
        },
        "defaultKeyStatistics": {"forwardPE": {"raw": 20.5}},
        "financialData": {
            "financialCurrency": "USD",
            "totalRevenue": {"raw": 1234},
        },
    }


def execute(monkeypatch, summary, **kwargs):
    monkeypatch.setattr(profiles, "get_quote_summary", lambda *args: summary)
    return json.loads(profiles.StockProfileTool().execute(ticker="BBCA.JK", **kwargs))


def test_idx_profile_is_labeled_idx(monkeypatch, summary):
    result = execute(monkeypatch, summary)
    assert result["ok"] is True
    assert result["market"] == "idx"
    assert result["data"]["listing"]["currency"] == "IDR"


def test_idx_profile_keeps_reporting_currency_separate(monkeypatch, summary):
    result = execute(monkeypatch, summary)
    assert result["data"]["listing"]["financial_currency"] == "USD"
    assert result["data"]["sections"]["financials"]["totalRevenue"] == 1234


def test_idx_profile_retrieval_is_not_a_publication_date(monkeypatch, summary):
    class Clock:
        @staticmethod
        def now(tz):
            return datetime(2026, 11, 11, 3, tzinfo=timezone.utc)

    monkeypatch.setattr(profiles, "datetime", Clock)
    result = execute(monkeypatch, summary)
    provenance = result["provenance"]
    assert provenance["retrieved_at"] == "2026-11-11T03:00:00+00:00"
    assert provenance["financial_period"] is None
    assert provenance["publication_time"] is None
    assert provenance["historical_use"] == "not_supported"


@pytest.mark.parametrize(
    "field,value",
    [
        ("symbol", "BBRI.JK"),
        ("symbol", None),
        ("symbol", "AAPL"),
        ("exchange", "NMS"),
        ("exchange", None),
        ("quoteType", "INDEX"),
        ("quoteType", None),
        ("currency", "USD"),
        ("currency", None),
    ],
)
def test_idx_profile_rejects_unverified_listing(monkeypatch, summary, field, value):
    summary["price"][field] = value
    result = execute(monkeypatch, summary)
    assert result["ok"] is False
    assert result["error"] == "IDX listing requires matching symbol, IDX equity venue and IDR quote currency"
    assert "data" not in result


@pytest.mark.parametrize("price", [None, [], "malformed", {}])
def test_idx_profile_requires_listing_object(monkeypatch, summary, price):
    summary["price"] = price
    assert execute(monkeypatch, summary)["ok"] is False


@pytest.mark.parametrize("ticker", ["BBCA-W.JK", "1234.JK", "LOCAL:BBCA.JK", "^JKSE.JK"])
def test_unsupported_idx_profile_never_fetches(monkeypatch, ticker):
    def forbidden(*args):
        pytest.fail("unsupported symbol reached the network boundary")

    monkeypatch.setattr(profiles, "get_quote_summary", forbidden)
    result = json.loads(profiles.StockProfileTool().execute(ticker=ticker))
    assert result["ok"] is False


def test_idx_profile_normalizes_case_before_fetch(monkeypatch, summary):
    requested = []

    def fetch(ticker, modules):
        requested.append(ticker)
        return summary

    monkeypatch.setattr(profiles, "get_quote_summary", fetch)
    result = json.loads(profiles.StockProfileTool().execute(ticker=" bbca.jk ", sections=["key_stats"]))
    assert result["market"] == "idx"
    assert result["data"]["ticker"] == "BBCA.JK"
    assert requested == ["BBCA.JK"]


def test_idx_alias_venue_is_accepted(monkeypatch, summary):
    summary["price"]["exchange"] = "IDX"
    assert execute(monkeypatch, summary)["market"] == "idx"


def test_idx_missing_financial_values_remain_unavailable(monkeypatch, summary):
    summary.pop("financialData")
    result = execute(monkeypatch, summary)
    assert result["data"]["sections"]["financials"]["totalRevenue"] is None
    assert result["data"]["listing"]["financial_currency"] is None


def test_idx_provider_errors_are_sanitized(monkeypatch, caplog):
    def unavailable(*args):
        raise RuntimeError("synthetic-private-url?crumb=do-not-log")

    monkeypatch.setattr(profiles, "get_quote_summary", unavailable)
    result = profiles.StockProfileTool().execute(ticker="BBCA.JK")
    assert json.loads(result)["ok"] is False
    assert "do-not-log" not in result + caplog.text
    assert "RuntimeError" in caplog.text


@pytest.mark.parametrize("malformed", [None, [], "bad"])
def test_idx_malformed_summary_is_a_structured_failure(monkeypatch, malformed):
    assert execute(monkeypatch, malformed)["ok"] is False


@pytest.mark.parametrize(
    "module,value",
    [
        ("defaultKeyStatistics", []),
        ("financialData", "bad"),
        ("earningsTrend", {"trend": [{"earningsEstimate": "bad"}]}),
    ],
)
def test_idx_malformed_sections_are_a_structured_failure(monkeypatch, summary, module, value):
    summary[module] = value
    result = execute(monkeypatch, summary)
    assert result["ok"] is False
    assert "data" not in result


@pytest.mark.parametrize("value", [float("nan"), float("inf"), object()])
def test_idx_profile_values_must_be_strict_json(monkeypatch, summary, value):
    summary["defaultKeyStatistics"]["forwardPE"] = {"raw": value}
    result = execute(monkeypatch, summary)
    assert result == {"ok": False, "error": "invalid IDX profile values"}


@pytest.mark.parametrize("value", [True, False, "20.5", "not-a-number", [20.5], {"value": 20.5}])
def test_idx_numeric_field_rejects_json_values_that_are_not_numbers(monkeypatch, summary, value, caplog):
    summary["defaultKeyStatistics"]["forwardPE"] = {"raw": value}
    result = execute(monkeypatch, summary)
    assert result == {"ok": False, "error": "invalid IDX profile values"}
    assert "IDX profile" in caplog.text
    assert "not-a-number" not in caplog.text


@pytest.mark.parametrize(
    "module,payload",
    [
        ("financialData", {"totalRevenue": {"raw": True}}),
        ("earningsTrend", {"trend": [{"earningsEstimate": {"avg": {"raw": True}}}]}),
        ("institutionOwnership", {"ownershipList": [{"position": {"raw": True}}]}),
        ("insiderHolders", {"holders": [{"positionDirect": {"raw": True}}]}),
        ("recommendationTrend", {"trend": [{"strongBuy": True}]}),
    ],
)
def test_idx_numeric_types_are_checked_across_profile_sections(monkeypatch, summary, module, payload):
    summary[module] = payload
    assert execute(monkeypatch, summary) == {"ok": False, "error": "invalid IDX profile values"}


@pytest.mark.parametrize("value", [None, 0, -1.25, 20.5])
def test_idx_numeric_type_guard_preserves_missing_zero_and_signed_values(monkeypatch, summary, value):
    summary["defaultKeyStatistics"]["forwardPE"] = {"raw": value}
    result = execute(monkeypatch, summary)
    assert result["ok"] is True
    assert result["data"]["sections"]["key_stats"]["forwardPE"] == value


def test_numeric_type_guard_does_not_change_us_profile_contract(monkeypatch):
    monkeypatch.setattr(profiles, "get_quote_summary", lambda *args: {"defaultKeyStatistics": {"forwardPE": True}})
    result = json.loads(profiles.StockProfileTool().execute(ticker="AAPL.US"))
    assert result["ok"] is True
    assert result["data"]["sections"]["key_stats"]["forwardPE"] is True


def test_idx_malformed_numeric_field_is_rejected_through_mcp(monkeypatch, summary):
    from fastmcp import Client
    import mcp_server
    from src.tools import build_registry

    summary["financialData"]["totalRevenue"] = {"raw": True}
    monkeypatch.setattr(profiles, "get_quote_summary", lambda *args: summary)
    monkeypatch.setattr(mcp_server, "_registry", build_registry(include_shell_tools=False))

    async def call():
        async with Client(mcp_server.mcp) as client:
            return await client.call_tool("get_stock_profile", {"ticker": "BBCA.JK", "sections": ["financials"]})

    result = json.loads(asyncio.run(call()).content[0].text)
    assert result == {"ok": False, "error": "invalid IDX profile values"}


def test_idx_profile_round_trips_through_mcp_with_real_registry(monkeypatch, summary):
    from fastmcp import Client
    import mcp_server
    from src.tools import build_registry

    monkeypatch.setattr(profiles, "get_quote_summary", lambda *args: summary)
    registry = build_registry(include_shell_tools=False)
    monkeypatch.setattr(mcp_server, "_registry", registry)

    async def call():
        async with Client(mcp_server.mcp) as client:
            return await client.call_tool("get_stock_profile", {"ticker": "BBCA.JK", "sections": ["financials"]})

    result = json.loads(asyncio.run(call()).content[0].text)
    assert result["market"] == "idx"
    assert result["data"]["sections"]["financials"]["totalRevenue"] == 1234
    assert result["provenance"]["historical_use"] == "not_supported"
    assert registry.get("get_stock_profile").is_readonly is True
    assert registry.get("bash") is None


@pytest.mark.parametrize(
    "ticker,market",
    [
        ("BBCA", "us"),
        ("AAPL.US", "us"),
        ("00700.HK", "hk"),
        ("VOD.L", "uk"),
        ("GOOGL.BA", "ar"),
        ("PETR4.SA", "br"),
    ],
)
def test_other_market_profile_contracts_are_preserved(monkeypatch, ticker, market):
    monkeypatch.setattr(profiles, "get_quote_summary", lambda *args: {})
    result = json.loads(profiles.StockProfileTool().execute(ticker=ticker))
    assert result["ok"] is True
    assert result["market"] == market
    assert "provenance" not in result
