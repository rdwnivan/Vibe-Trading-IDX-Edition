## get_stock_profile (agent tool)

----

Tool: `get_stock_profile`
Backed by: `backtest.loaders.yahoo_client.get_quote_summary`
Description: Read-only agent/CLI tool that returns a compact company profile for
a US, Hong Kong, UK (LSE .L), Argentina (.BA), Brazil (.SA), or IDX (.JK) listing — valuation key statistics, analyst price
targets and earnings/revenue estimates, institutional and insider ownership,
and the analyst recommendation trend. Use it for fundamentals and consensus
context, not for OHLCV price bars (use `get_market_data` for prices).

The tool selects the right Yahoo quoteSummary modules, unwraps Yahoo
`{"raw","fmt"}` cells to their numeric `raw` value, caps each list section at
25 rows, and wraps the result in the project envelope.

<br>
<br>

**Input parameters**

Name | Type | Required | Description
---- | ---- | -------- | -----------
ticker | str | Y | US (`AAPL` or `AAPL.US`), HK (`00700.HK`), UK (`VOD.L`), Argentina (`GOOGL.BA`), Brazil (`PETR4.SA`), or IDX (`BBCA.JK`) symbol.
sections | list[str] | N | Which sections to return (one or more of the section names below). Defaults to all sections. Unknown names return an error envelope.

Section name → underlying Yahoo module:

Section | Yahoo module | Contents
------- | ------------ | --------
key_stats | defaultKeyStatistics | Enterprise value, forward PE, EPS, PEG, price-to-book, profit margin, beta, shares outstanding, float, insider/institution held %.
financials | financialData | Current price, analyst target prices, recommendation key, analyst count, revenue/growth/margins, ROE, cash, debt.
earnings_trend | earningsTrend | Per-period EPS/revenue estimates (avg/low/high), growth, analyst count.
institution_ownership | institutionOwnership | Top institutional holders (organization, report date, pct held, position, value).
insider_holders | insiderHolders | Insider holders (name, relation, latest transaction date, position).
recommendation_trend | recommendationTrend | Strong-buy / buy / hold / sell / strong-sell counts per period.

<br>
<br>

**Output**

A JSON-string envelope.

On success:

```json
{"ok": true, "market": "us|hk|uk|ar|br|idx", "source": "yahoo",
 "data": {"ticker": "<input>", "listing": {"symbol": "<provider symbol>", "exchange": "<provider venue>", "currency": "<quote currency>"}, "sections": {"<name>": "<shaped>"}}}
```

`market` is `hk` for `.HK`, `uk` for `.L`, `ar` for `.BA`, `br` for `.SA`,
and `idx` for supported regular-share `.JK` symbols; other existing inputs
retain `us`. Bare `BBCA` is not automatically treated as IDX. Scalar sections
(`key_stats`, `financials`) shape to a flat dict; list sections
(`earnings_trend`, `institution_ownership`, `insider_holders`,
`recommendation_trend`) shape to a list of rows (≤ 25).

On failure:

```json
{"ok": false, "error": "<message>"}
```

Failures are returned as an envelope (never raised) — e.g. a missing/blank
`ticker`, an unknown section name, or an upstream Yahoo request error.

**IDX snapshot contract**

An IDX response must declare the exact requested symbol, an equity listing on
Yahoo's shared IDX venue aliases, and IDR quote currency. Unsupported `.JK`
instrument shapes and `local:` inputs fail before fetching. Missing/conflicting
listing identity, malformed sections, non-JSON/nonfinite values and provider
errors return sanitized failure envelopes rather than fabricated fundamentals.
The aliases describe provider responses, not an official instrument master.

`listing.financial_currency` preserves the provider's financial reporting
currency independently of IDR quotes; it is null when unavailable. Monetary
fields with unresolved units remain unsuitable for cross-currency ratios or
valuation. Missing fields stay null/list sections stay empty.

IDX envelopes additionally return `provenance.retrieved_at` (UTC retrieval
time), `financial_period: null`, `publication_time: null`, and
`historical_use: "not_supported"`. Retrieval is not publication or a verified
fundamental period. This profile cannot supply point-in-time historical
fundamentals, complete corporate actions, trading permission or data rights.
Synthetic contract tests do not establish live IDX provider coverage. Use
`load_skill(name="idx-research")` for the bounded local research workflow.

<br>
<br>

**Example**

```text
get_stock_profile(ticker="AAPL.US")
get_stock_profile(ticker="AAPL", sections=["key_stats", "financials"])
get_stock_profile(ticker="00700.HK", sections=["key_stats"])
get_stock_profile(ticker="VOD.L", sections=["key_stats"])
```

<br>
<br>

**Data example**

```json
{
  "ok": true, "market": "us", "source": "yahoo",
  "data": {
    "ticker": "AAPL.US",
    "sections": {
      "key_stats": {"enterpriseValue": 2980000000000, "forwardPE": 27.4,
                     "trailingEps": 6.43, "priceToBook": 45.1, "beta": 1.28,
                     "heldPercentInstitutions": 0.612},
      "financials": {"currentPrice": 192.2, "targetMeanPrice": 205.0,
                      "recommendationKey": "buy", "numberOfAnalystOpinions": 41,
                      "returnOnEquity": 1.47}
    }
  }
}
```
