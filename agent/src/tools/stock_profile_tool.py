"""Read-only company-profile tool: key stats, estimates, and ownership.

Backed by the shared Yahoo Finance quoteSummary client
(:func:`backtest.loaders.yahoo_client.get_quote_summary`), which routes every
request through the throttled HTTP layer and handles the cookie+crumb
handshake. This tool only selects modules, projects the verbose Yahoo payload
into compact rows, and wraps the result in the project envelope.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backtest.engines._market_hooks import _detect_market, code_currency
from backtest.loaders.yahoo_client import IDX_EQUITY_EXCHANGES, get_quote_summary
from src.agent.tools import BaseTool

logger = logging.getLogger(__name__)

# Section name (tool-facing) -> Yahoo quoteSummary module name.
_SECTION_MODULES: Dict[str, str] = {
    "key_stats": "defaultKeyStatistics",
    "financials": "financialData",
    "earnings_trend": "earningsTrend",
    "institution_ownership": "institutionOwnership",
    "insider_holders": "insiderHolders",
    "recommendation_trend": "recommendationTrend",
}
_ALL_SECTIONS = tuple(_SECTION_MODULES)

# Always fetched (in addition to the requested sections) to carry Yahoo's own
# listing identity: venue and quote currency, kept separate from fundamentals.
_LISTING_MODULE = "price"

# Cap list-valued sections so a verbose payload cannot bloat the envelope.
_MAX_ROWS = 25


def _raw(value: Any) -> Any:
    """Unwrap a Yahoo ``{"raw":..,"fmt":..}`` cell to its numeric ``raw`` value.

    Args:
        value: A Yahoo scalar, which may be a plain value or a formatted dict.

    Returns:
        The ``raw`` member when ``value`` is a Yahoo formatted dict, the value
        itself when scalar, or ``None`` for an empty/absent cell.
    """
    if isinstance(value, dict):
        return value.get("raw")
    return value


def _pick(source: Dict[str, Any], fields: tuple[str, ...]) -> Dict[str, Any]:
    """Project selected Yahoo fields into a flat, raw-unwrapped row."""
    return {field: _raw(source.get(field)) for field in fields}


def _key_stats(module: Dict[str, Any]) -> Dict[str, Any]:
    """Shape the defaultKeyStatistics module into a compact row."""
    return _pick(
        module,
        (
            "enterpriseValue",
            # EV multiples arrive in the same payload and were being dropped,
            # leaving no capital-structure-neutral valuation measure at all.
            "enterpriseToEbitda",
            "enterpriseToRevenue",
            "forwardPE",
            "trailingEps",
            "forwardEps",
            "pegRatio",
            "priceToBook",
            "profitMargins",
            "beta",
            "sharesOutstanding",
            "floatShares",
            "heldPercentInsiders",
            "heldPercentInstitutions",
        ),
    )


def _financials(module: Dict[str, Any]) -> Dict[str, Any]:
    """Shape the financialData module into a compact row."""
    return _pick(
        module,
        (
            "currentPrice",
            "targetMeanPrice",
            "targetHighPrice",
            "targetLowPrice",
            "recommendationKey",
            "numberOfAnalystOpinions",
            "totalRevenue",
            "revenueGrowth",
            "grossMargins",
            "operatingMargins",
            "returnOnEquity",
            "totalCash",
            "totalDebt",
        ),
    )


def _earnings_trend(module: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Shape the earningsTrend periods into per-period estimate rows."""
    rows: List[Dict[str, Any]] = []
    for entry in (module.get("trend") or [])[:_MAX_ROWS]:
        if not isinstance(entry, dict):
            continue
        eps = entry.get("earningsEstimate") or {}
        rev = entry.get("revenueEstimate") or {}
        # The consensus level alone is a snapshot. Its trajectory and the
        # up/down revision counts arrive in the same payload and are what
        # estimate-revision momentum is actually built from.
        trend = entry.get("epsTrend") or {}
        revisions = entry.get("epsRevisions") or {}
        rows.append(
            {
                "period": entry.get("period"),
                "end_date": entry.get("endDate"),
                "growth": _raw(entry.get("growth")),
                "eps_avg": _raw(eps.get("avg")),
                "eps_low": _raw(eps.get("low")),
                "eps_high": _raw(eps.get("high")),
                "eps_analysts": _raw(eps.get("numberOfAnalysts")),
                "revenue_avg": _raw(rev.get("avg")),
                "eps_trend_current": _raw(trend.get("current")),
                "eps_trend_7d_ago": _raw(trend.get("7daysAgo")),
                "eps_trend_30d_ago": _raw(trend.get("30daysAgo")),
                "eps_trend_90d_ago": _raw(trend.get("90daysAgo")),
                "eps_revisions_up_30d": _raw(revisions.get("upLast30days")),
                "eps_revisions_down_30d": _raw(revisions.get("downLast30days")),
            }
        )
    return rows


def _institution_ownership(module: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Shape the institutionOwnership holders into per-holder rows."""
    rows: List[Dict[str, Any]] = []
    for entry in (module.get("ownershipList") or [])[:_MAX_ROWS]:
        if not isinstance(entry, dict):
            continue
        rows.append(
            {
                "organization": entry.get("organization"),
                "report_date": _raw(entry.get("reportDate")),
                "pct_held": _raw(entry.get("pctHeld")),
                "position": _raw(entry.get("position")),
                "value": _raw(entry.get("value")),
            }
        )
    return rows


def _insider_holders(module: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Shape the insiderHolders holders into per-insider rows."""
    rows: List[Dict[str, Any]] = []
    for entry in (module.get("holders") or [])[:_MAX_ROWS]:
        if not isinstance(entry, dict):
            continue
        rows.append(
            {
                "name": entry.get("name"),
                "relation": entry.get("relation"),
                "latest_transaction": entry.get("latestTransDate"),
                "position": _raw(entry.get("positionDirect")),
            }
        )
    return rows


def _recommendation_trend(module: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Shape the recommendationTrend periods into per-period rating rows."""
    rows: List[Dict[str, Any]] = []
    for entry in (module.get("trend") or [])[:_MAX_ROWS]:
        if not isinstance(entry, dict):
            continue
        rows.append(
            {
                "period": entry.get("period"),
                "strong_buy": entry.get("strongBuy"),
                "buy": entry.get("buy"),
                "hold": entry.get("hold"),
                "sell": entry.get("sell"),
                "strong_sell": entry.get("strongSell"),
            }
        )
    return rows


def _listing_identity(
    price_module: Dict[str, Any], financial_module: Dict[str, Any]
) -> Dict[str, Any]:
    """Shape Yahoo-declared listing identity, distinct from issuer fundamentals.

    Only fields the provider explicitly supplies are used here; none of this
    is inferred from the ticker suffix or company name. The underlying-issuer
    relationship is included only when Yahoo's payload names one.

    Args:
        price_module: The raw ``price`` quoteSummary module.
        financial_module: The raw ``financialData`` module, or ``{}`` when
            the ``financials`` section was not requested.

    Returns:
        A compact row with the listing symbol, venue, and quote currency,
        plus ``financial_currency``/``underlying_symbol`` when Yahoo supplies
        them.
    """
    row: Dict[str, Any] = {
        "symbol": price_module.get("symbol"),
        "exchange": price_module.get("exchange"),
        "exchange_name": (
            price_module.get("fullExchangeName") or price_module.get("exchangeName")
        ),
        "quote_type": price_module.get("quoteType"),
        "currency": price_module.get("currency"),
    }
    underlying_symbol = price_module.get("underlyingSymbol")
    if underlying_symbol:
        row["underlying_symbol"] = underlying_symbol
    financial_currency = financial_module.get("financialCurrency")
    if financial_currency:
        row["financial_currency"] = financial_currency
    return row


# Section name -> (yahoo module name, shaper). One entry per supported section.
_SHAPERS = {
    "key_stats": _key_stats,
    "financials": _financials,
    "earnings_trend": _earnings_trend,
    "institution_ownership": _institution_ownership,
    "insider_holders": _insider_holders,
    "recommendation_trend": _recommendation_trend,
}


def _resolve_sections(sections: Optional[List[str]]) -> List[str]:
    """Validate the requested sections, defaulting to all when omitted.

    Args:
        sections: Requested section names, or ``None`` for every section.

    Returns:
        An ordered, de-duplicated list of valid section names.

    Raises:
        ValueError: If any requested name is not a supported section.
    """
    if not sections:
        return list(_ALL_SECTIONS)
    resolved: List[str] = []
    for name in sections:
        key = str(name).strip().lower()
        if key not in _SECTION_MODULES:
            raise ValueError(
                f"unknown section '{name}'; valid: {', '.join(_ALL_SECTIONS)}"
            )
        if key not in resolved:
            resolved.append(key)
    return resolved


def _market_for(ticker: str) -> str:
    """Classify a ticker into a coarse market label for the envelope."""
    upper = ticker.strip().upper()
    if upper.endswith(".JK"):
        if upper.startswith("LOCAL:") or _detect_market(upper) != "id_equity":
            raise ValueError("use an explicit regular-share .JK symbol")
        return "idx"
    if upper.endswith(".HK"):
        return "hk"
    if upper.endswith(".L"):
        return "uk"
    if upper.endswith(".BA"):
        return "ar"
    if upper.endswith(".SA"):
        return "br"
    return "us"


def _validate_idx_summary(summary: Any, ticker: str, sections: List[str]) -> None:
    """Require provider-declared identity before exposing IDX profile values."""
    price = summary.get(_LISTING_MODULE) if isinstance(summary, dict) else None
    if not isinstance(price, dict) or (
        price.get("symbol") != ticker
        or not isinstance(price.get("exchange"), str)
        or price["exchange"] not in IDX_EQUITY_EXCHANGES
        or price.get("quoteType") != "EQUITY"
        or price.get("currency") != code_currency(ticker)
    ):
        raise ValueError("IDX listing requires matching symbol, IDX equity venue and IDR quote currency")
    for name in sections:
        module = summary.get(_SECTION_MODULES[name])
        if module is not None and not isinstance(module, dict):
            raise ValueError("IDX profile section must be an object or unavailable")


def _validate_idx_numeric_values(sections: Dict[str, Any]) -> None:
    """Reject JSON-compatible non-numbers in the shaped numeric fields.

    The shapers own field selection. All their output fields are numeric except
    the labels/dates below; null still means unavailable. Finiteness remains
    enforced by strict JSON serialization. No coercion or unit inference occurs.
    """
    text_fields = {
        "recommendationKey", "period", "end_date", "organization",
        "name", "relation", "latest_transaction",
    }
    for section in sections.values():
        rows = [section] if isinstance(section, dict) else section
        for row in rows:
            for field, value in row.items():
                if field not in text_fields and value is not None and type(value) not in (int, float):
                    raise ValueError("invalid IDX profile values")


class StockProfileTool(BaseTool):
    """Company profile: key stats, analyst estimates, and ownership."""

    name = "get_stock_profile"
    description = (
        "Fetch a read-only company profile for a US, Hong Kong, UK (LSE .L), "
        "Argentina (BYMA .BA), Brazil (B3 .SA), or IDX (.JK) "
        "listing from Yahoo Finance: valuation key statistics, analyst price "
        "targets and earnings/revenue estimates, institutional and insider "
        "ownership, and the analyst recommendation trend. Always includes "
        "the listing's own venue and quote currency, kept separate from "
        "issuer fundamentals so a secondary/international listing does not "
        "read as the primary one. Use this for fundamentals and consensus "
        "context, not for OHLCV price bars (use get_market_data). Example: "
        'get_stock_profile(ticker="AAPL.US", '
        'sections=["key_stats", "financials"]). '
        "IDX requires matching provider-declared equity venue and IDR quote currency. "
        "Financial reporting currency stays separate; snapshots are not publication-dated history."
    )
    parameters = {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": (
                    "US, HK, UK (LSE .L), Argentina (BYMA .BA), Brazil (B3 .SA), or IDX (BBCA.JK) symbol. US uses a bare or .US suffix "
                    "(AAPL or AAPL.US); HK uses a zero-padded .HK code "
                    "(00700.HK); UK uses the .L suffix (VOD.L)."
                ),
            },
            "sections": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": list(_ALL_SECTIONS),
                },
                "description": (
                    "Which profile sections to return. One or more of: "
                    "key_stats, financials, earnings_trend, "
                    "institution_ownership, insider_holders, "
                    "recommendation_trend. Defaults to all sections."
                ),
                "default": list(_ALL_SECTIONS),
            },
        },
        "required": ["ticker"],
    }

    def execute(self, **kwargs: Any) -> str:
        """Fetch and shape the requested profile sections for one ticker.

        Args:
            **kwargs: ``ticker`` (str, required) and ``sections`` (list[str],
                optional; defaults to all sections).

        Returns:
            A JSON envelope string. On success:
            ``{"ok": true, "market": str, "source": "yahoo",
            "data": {"ticker": str, "listing": {...}, "sections":
            {<name>: <shaped>}}}``. ``listing`` carries Yahoo's own venue and
            quote-currency identity for the instrument, independent of the
            issuer fundamentals in ``sections``.
            On failure: ``{"ok": false, "error": str}``.
        """
        ticker = str(kwargs.get("ticker") or "").strip()
        if not ticker:
            return self._error("ticker is required")

        try:
            market = _market_for(ticker)
        except ValueError:
            return self._error("use an explicit regular-share .JK symbol")
        if market == "idx":
            ticker = ticker.upper()

        try:
            sections = _resolve_sections(kwargs.get("sections"))
        except ValueError as exc:
            return self._error(str(exc))

        modules = list(
            dict.fromkeys([_LISTING_MODULE, *(_SECTION_MODULES[n] for n in sections)])
        )
        try:
            summary = get_quote_summary(ticker, modules)
        except Exception as exc:  # noqa: BLE001 - surface upstream as envelope
            if market == "idx":
                logger.warning("IDX profile acquisition failed (%s)", type(exc).__name__)
                return self._error("yahoo quoteSummary request failed; retry later or check provider availability")
            logger.warning("get_stock_profile failed for %s: %s", ticker, exc)
            return self._error(f"yahoo quoteSummary request failed: {exc}")

        if market == "idx":
            try:
                _validate_idx_summary(summary, ticker, sections)
            except ValueError as exc:
                logger.warning("IDX profile declarations rejected (%s)", type(exc).__name__)
                return self._error(str(exc))

        shaped: Dict[str, Any] = {}
        try:
            for name in sections:
                module = summary.get(_SECTION_MODULES[name]) or {}
                shaped[name] = _SHAPERS[name](module if isinstance(module, dict) else {})
        except (AttributeError, TypeError, ValueError, KeyError) as exc:
            if market != "idx":
                raise
            logger.warning("IDX profile section rejected (%s)", type(exc).__name__)
            return self._error("invalid IDX profile section data")

        price_module = summary.get(_LISTING_MODULE) or {}
        financial_module = summary.get(_SECTION_MODULES["financials"]) or {}
        listing = _listing_identity(
            price_module if isinstance(price_module, dict) else {},
            financial_module if isinstance(financial_module, dict) else {},
        )

        result = {
            "ok": True,
            "market": market,
            "source": "yahoo",
            "data": {"ticker": ticker, "listing": listing, "sections": shaped},
        }
        if market == "idx":
            listing.setdefault("financial_currency", None)
            result["provenance"] = {
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "financial_period": None,
                "publication_time": None,
                "historical_use": "not_supported",
            }
        try:
            if market == "idx":
                _validate_idx_numeric_values(shaped)
            return json.dumps(result, ensure_ascii=False, allow_nan=market != "idx")
        except (TypeError, ValueError, RecursionError) as exc:
            if market != "idx":
                raise
            logger.warning("IDX profile values rejected (%s)", type(exc).__name__)
            return self._error("invalid IDX profile values")

    @staticmethod
    def _error(message: str) -> str:
        """Render a failure envelope as a JSON string."""
        return json.dumps({"ok": False, "error": message}, ensure_ascii=False)
