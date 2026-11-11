"""IDX foundation regressions. All market observations below are synthetic."""

from datetime import date
from decimal import Decimal

import pandas as pd
import pytest

from backtest.engines._market_hooks import _detect_market, code_currency
from backtest.engines.composite import _build_rule_engines, _reject_mixed_currency
from backtest.loaders.base import normalize_declared_quote_currency
from backtest.loaders.idx_contract import validate_idx_interval
from backtest.loaders.registry import FALLBACK_CHAINS
from backtest.loaders.yahoo_loader import DataLoader as YahooLoader
from backtest.runner import _create_market_engine, _detect_source
from src.market_data import detect_source, fetch_market_data
from src.markets.idx import IDXInstrument, IDXInstrumentRegistry
from src.markets.idx_rules import IDXRegularRules, IDXSessionCalendar


@pytest.mark.parametrize("symbol", ["BBCA.JK", "BBRI.JK", " bbca.jk ", "local:BBCA.JK"])
def test_idx_identity_and_currency(symbol):
    assert _detect_market(symbol) == "id_equity"
    assert code_currency(symbol) == "IDR"


@pytest.mark.parametrize("symbol", ["B.JK", "1234.JK", "BBCA-W.JK", "BBCA.JK.JK"])
def test_unsupported_idx_forms_do_not_fall_back_to_a_shares(symbol):
    with pytest.raises(ValueError, match="Unsupported IDX"):
        _detect_market(symbol)


@pytest.mark.parametrize(
    "symbol,market",
    [
        ("BBCA", "us_equity"),
        ("AAPL.US", "us_equity"),
        ("700.HK", "hk_equity"),
        ("RELIANCE.NS", "india_equity"),
        ("PETR4.SA", "br_equity"),
        ("BTC-USDT", "crypto"),
        ("RB2410", "futures"),
        ("^JKSE", "index"),
    ],
)
def test_idx_extension_preserves_other_market_meanings(symbol, market):
    assert _detect_market(symbol) == market


def test_idx_research_routes_to_existing_yahoo_transports():
    assert _detect_source("BBCA.JK") == "yahoo"
    assert detect_source(" bbca.jk ") == "yahoo"
    assert FALLBACK_CHAINS["id_equity"] == ["yahoo", "yfinance", "local"]


@pytest.mark.parametrize("source", ["auto", "yahoo", "yfinance", "local", "tushare"])
def test_idx_backtests_reject_every_source_instead_of_borrowing_rules(source):
    with pytest.raises(ValueError, match="IDX .*backtesting is unavailable"):
        _create_market_engine(source, {}, ["BBCA.JK"])


def test_direct_composite_construction_also_rejects_idx_rules():
    with pytest.raises(ValueError, match="IDX .*backtesting is unavailable"):
        _build_rule_engines({}, ["BBCA.JK", "AAPL.US"])


@pytest.mark.parametrize("other", ["AAPL.US", "600519.SH", "700.HK"])
def test_idx_capital_cannot_be_added_to_other_currency_pools(other):
    with pytest.raises(ValueError, match="one settlement currency"):
        _reject_mixed_currency(["BBCA.JK", other])


@pytest.fixture
def registry():
    return IDXInstrumentRegistry(
        [
            IDXInstrument("BBCA.JK", "Synthetic issuer", "fixture://reference", date(2026, 11, 3)),
        ]
    )


def test_bare_ticker_normalizes_only_in_verified_idx_context(registry):
    assert registry.resolve(" bbca ", as_of=date(2026, 11, 3)).symbol == "BBCA.JK"
    assert _detect_market("BBCA") == "us_equity"


def test_registry_rejects_unverified_listing(registry):
    with pytest.raises(ValueError, match="unverified"):
        registry.resolve("BBRI", as_of=date(2026, 11, 3))


@pytest.mark.parametrize("day", [date(2026, 11, 2), date(2026, 11, 4)])
def test_snapshot_cannot_claim_historical_or_current_listing_on_another_day(registry, day):
    with pytest.raises(ValueError, match="snapshot.*dated"):
        registry.resolve("BBCA", as_of=day)


@pytest.mark.parametrize("currency", ["USD", None, ""])
def test_idx_price_frame_requires_provider_declared_idr(currency):
    with pytest.raises(ValueError, match="must be quoted in IDR"):
        normalize_declared_quote_currency(pd.DataFrame(), "BBCA.JK", currency)


@pytest.mark.parametrize("interval", ["5m", "1H", "1W", "1M"])
def test_unvalidated_idx_intervals_are_rejected(interval):
    with pytest.raises(ValueError, match="daily"):
        validate_idx_interval(["BBCA.JK"], interval)


@pytest.fixture
def chart(monkeypatch):
    # 18:00 UTC is the following Jakarta session date. A null volume is
    # unavailable, not evidence of zero trading or suspension.
    import backtest.loaders.yahoo_loader as yahoo

    payload = [
        {
            "trade_date": int(pd.Timestamp("2026-11-02T18:00:00Z").timestamp()),
            "open": 100,
            "high": 110,
            "low": 90,
            "close": 105,
            "volume": None,
        }
    ]
    monkeypatch.setattr(yahoo.yahoo_client, "get_chart", lambda *a, **k: (payload, "IDR"))
    return payload


def test_yahoo_idx_keeps_jakarta_date_missing_volume_and_metadata(chart):
    frame = YahooLoader().fetch(["BBCA.JK"], "2026-11-03", "2026-11-03")["BBCA.JK"]
    assert frame.index[0] == pd.Timestamp("2026-11-03")
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame.attrs["quote_currency"] == "IDR"
    assert frame.attrs["exchange_timezone"] == "Asia/Jakarta"
    assert frame.attrs["adjustment"] == "unknown"
    assert frame.attrs["data_quality"] == "incomplete"


def test_idx_provenance_survives_shared_tool_surface(chart):
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-11-03",
        end_date="2026-11-03",
        loader_resolver=lambda _: YahooLoader,
        include_provenance=True,
    )
    provenance = result["_provenance"]["BBCA.JK"]
    assert provenance["source"] == "yahoo"
    assert provenance["quote_currency"] == "IDR"
    assert provenance["volume_unit"] == "shares"
    assert provenance["freshness"] == "not_evaluated"
    assert provenance["retrieved_at"] != "unknown"


def test_yfinance_idx_preserves_missing_volume_and_declared_currency(monkeypatch):
    import backtest.loaders.yfinance_loader as yfl

    raw = pd.DataFrame(
        {"Open": [100], "High": [110], "Low": [90], "Close": [105]}, index=pd.DatetimeIndex(["2026-11-02T18:00:00Z"])
    )

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yfl.yf, "download", lambda *a, **k: raw)
    monkeypatch.setattr(yfl.yf, "Ticker", Ticker)
    frame = yfl.DataLoader().fetch(["BBCA.JK"], "2026-11-03", "2026-11-03")["BBCA.JK"]
    assert frame.index[0] == pd.Timestamp("2026-11-03")
    assert pd.isna(frame.iloc[0]["volume"])
    assert frame.attrs["quote_currency"] == "IDR"
    assert frame.attrs["source"] == "yfinance"


def test_idx_explicit_local_failure_never_invokes_a_network_source():
    from backtest.loaders.base import NoAvailableSourceError

    requested = []

    def unavailable(source):
        requested.append(source)
        raise NoAvailableSourceError("Synthetic local configuration unavailable")

    result = fetch_market_data(
        codes=["BBCA.JK"], start_date="2026-11-02", end_date="2026-11-03", source="local", loader_resolver=unavailable
    )
    assert requested == ["local"]
    assert "BBCA.JK" in result["_unresolved"]


@pytest.fixture
def rules():
    # Synthetic effective interval: this does not assert an official rule's
    # commencement date. Official observations are documented separately.
    return IDXRegularRules(
        "fixture-v1",
        "fixture://rules",
        date(2026, 11, 3),
        date(2026, 11, 3),
        100,
        tuple(
            (Decimal(a), Decimal(b))
            for a, b in [("0", "1"), ("200", "2"), ("500", "5"), ("2000", "10"), ("5000", "25")]
        ),
    )


@pytest.mark.parametrize(
    "close,tick",
    [
        ("199", "1"),
        ("200", "2"),
        ("499", "2"),
        ("500", "5"),
        ("1999", "5"),
        ("2000", "10"),
        ("4999", "10"),
        ("5000", "25"),
    ],
)
def test_configured_tick_tier_uses_previous_close(rules, close, tick):
    assert rules.tick_size(Decimal(close), session_date=date(2026, 11, 3)) == Decimal(tick)


def test_rulebook_cannot_be_used_before_effective_date(rules):
    with pytest.raises(ValueError, match="effective interval"):
        rules.tick_size(Decimal("500"), session_date=date(2026, 11, 2))


def test_lot_units_convert_to_shares_explicitly(rules):
    assert rules.shares_from_lots(3) == 300


def test_fractional_lots_are_rejected_without_rounding(rules):
    with pytest.raises(ValueError, match="integer"):
        rules.shares_from_lots(1.5)


def test_calendar_distinguishes_known_closure_from_uncovered_date():
    calendar = IDXSessionCalendar(
        "fixture://calendar", date(2026, 11, 1), date(2026, 11, 3), frozenset({date(2026, 11, 3)})
    )
    assert calendar.is_session(date(2026, 11, 3)) is True
    assert calendar.is_session(date(2026, 11, 2)) is False
    with pytest.raises(ValueError, match="coverage"):
        calendar.is_session(date(2026, 11, 4))


def test_shared_data_surface_cannot_bypass_daily_only_idx_contract():
    with pytest.raises(ValueError, match="daily"):
        fetch_market_data(codes=["BBCA.JK"], start_date="2026-11-02", end_date="2026-11-03", interval="1W")


@pytest.mark.parametrize("error,reason", [(True, "fetch_failed"), (False, "no_data")])
def test_idx_provider_error_is_distinct_from_empty_data(monkeypatch, error, reason):
    import backtest.loaders.yahoo_loader as yahoo

    def chart(*args, **kwargs):
        if error:
            raise ValueError("Synthetic provider failure")
        return [], "IDR"

    monkeypatch.setattr(yahoo.yahoo_client, "get_chart", chart)
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-11-02",
        end_date="2026-11-03",
        loader_resolver=lambda _: YahooLoader,
    )
    assert result["_diagnostics"]["BBCA.JK"]["attempts"][0]["reason"] == reason


def test_idx_fallback_records_actual_source_and_failed_attempt(monkeypatch):
    import backtest.loaders.yahoo_loader as yahoo
    import backtest.loaders.yfinance_loader as yfl

    def failed_chart(*args, **kwargs):
        raise ValueError("Synthetic chart outage")

    raw = pd.DataFrame(
        {"Open": [100], "High": [110], "Low": [90], "Close": [105], "Volume": [1000]},
        index=pd.DatetimeIndex(["2026-11-03"]),
    )

    class Ticker:
        history_metadata = {"currency": "IDR"}

        def __init__(self, symbol):
            pass

    monkeypatch.setattr(yahoo.yahoo_client, "get_chart", failed_chart)
    monkeypatch.setattr(yfl.yf, "download", lambda *a, **k: raw)
    monkeypatch.setattr(yfl.yf, "Ticker", Ticker)
    result = fetch_market_data(
        codes=["BBCA.JK"],
        start_date="2026-11-03",
        end_date="2026-11-03",
        loader_resolver=lambda source: {"yahoo": YahooLoader, "yfinance": yfl.DataLoader}[source],
        include_provenance=True,
    )
    provenance = result["_provenance"]["BBCA.JK"]
    assert provenance["source"] == "yfinance"
    assert provenance["fallback_used"] is True
    assert provenance["attempts"] == [{"source": "yahoo", "reason": "fetch_failed"}]
    assert provenance["adjustment"] == "split_dividend"


def test_idx_parquet_cache_preserves_retrieval_time_and_missing_volume(chart, tmp_path):
    from backtest.loaders.base import _read_loader_cache_frame, _write_loader_cache_frame

    frame = YahooLoader().fetch(["BBCA.JK"], "2026-11-03", "2026-11-03")["BBCA.JK"]
    path = tmp_path / "idx.parquet"
    _write_loader_cache_frame(path, frame)
    restored = _read_loader_cache_frame(path)
    assert restored is not None
    assert restored.attrs == frame.attrs
    assert pd.isna(restored.iloc[0]["volume"])


def test_registry_rejects_duplicate_reference_entries(registry):
    instrument = registry.resolve("BBCA", as_of=date(2026, 11, 3))
    with pytest.raises(ValueError, match="Duplicate"):
        IDXInstrumentRegistry([instrument, instrument])


def test_rulebook_rejects_mutable_nested_tiers(rules):
    from dataclasses import replace

    with pytest.raises(ValueError, match="immutable pair"):
        replace(rules, tick_tiers=([Decimal("0"), Decimal("1")],))


@pytest.mark.parametrize("value", [Decimal("NaN"), Decimal("Infinity"), Decimal("0"), Decimal("-1")])
def test_rulebook_rejects_nonfinite_or_nonpositive_previous_close(rules, value):
    with pytest.raises(ValueError, match="positive finite Decimal"):
        rules.tick_size(value, session_date=date(2026, 11, 3))


def test_idx_explicit_unrelated_source_does_not_borrow_a_china_fallback_chain():
    from backtest.loaders.base import NoAvailableSourceError

    requested = []

    def unavailable(source):
        requested.append(source)
        raise NoAvailableSourceError("Synthetic source unavailable")

    result = fetch_market_data(
        codes=["BBCA.JK"], start_date="2026-11-02", end_date="2026-11-03", source="tushare", loader_resolver=unavailable
    )
    assert requested == ["tushare"]
    assert result["_unresolved"] == ["BBCA.JK"]


def test_idx_rejects_resolver_substitution_to_another_markets_loader():
    class WrongMarketLoader:
        name = "tencent"
        markets = {"a_share"}

        def fetch(self, *args, **kwargs):
            raise AssertionError("Non-IDX loader must not be invoked")

    result = fetch_market_data(
        codes=["BBCA.JK"], start_date="2026-11-02", end_date="2026-11-03", loader_resolver=lambda _: WrongMarketLoader
    )
    assert result["_unresolved"] == ["BBCA.JK"]
    assert result["_diagnostics"]["BBCA.JK"]["attempts"][0]["reason"] == "source_unavailable"
