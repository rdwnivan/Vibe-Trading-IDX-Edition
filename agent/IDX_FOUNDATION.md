# IDX Edition: assessment and foundation

Snapshot: 2026-11-03, Asia/Jakarta. Foundation: existing checkout of
[HKUDS/Vibe-Trading](https://github.com/HKUDS/Vibe-Trading), baseline `2ac20879`.
This is an incremental research implementation. Phase 1 assessment is complete;
Phase 2 has tested identity/data primitives, with reference-data and rulebook
coverage still incomplete. It is not an IDX backtesting or paper-trading release.

## Architecture assessment

Reuse the existing entry points: `api_server.py:153` assembles FastAPI lifecycle,
`src/session/service.py:77` owns sessions, and `src/agent/loop.py:170` owns the
agent loop. CLI and MCP share those services/tools. No replacement application,
database, scheduler, or parallel tool framework is needed.

The seam for market identity is `backtest/engines/_market_hooks.py:104`; source
fallback belongs in `backtest/loaders/registry.py:231`. Research data is served
by `src/market_data.py`, then the existing agent/MCP tools. Execution selection
is separate (`backtest/runner.py:1765`, `backtest/engines/composite.py:32`).
An added source or locale cannot establish execution support.

Frontend remains React/Vite with existing routes (`frontend/src/router.tsx:61`,
path relative to repository root) and Indonesian locale. Storage is owned by
each subsystem (SQLite, JSON/JSONL, files and market cache), rooted through
`src/config/paths.py:13`. No schema migration is needed for this increment.
Paper matching, portfolio accounting, Shadow Account and live trading retain
their separate contracts; none gains IDX execution from this change.

The baseline defect was `BBCA.JK -> a_share`, while bare `BBCA -> us_equity`.
Adding only a loader declaration would leave classification, money units,
identity grounding and execution rules inconsistent. The implementation
therefore extends their existing owners and tests parity across them.

## Available behavior

- Four-letter regular-share `.JK` symbols classify as `id_equity`, currency IDR.
  Case/outer whitespace and `local:` are supported. Unsupported `.JK` shapes
  raise instead of borrowing A-share rules. Bare `BBCA` retains its US meaning.
- `src.markets.idx.IDXInstrumentRegistry` resolves bare tickers only within an
  explicitly supplied, dated reference snapshot. Records require name/source.
  No built-in universe claims to represent all listed or historical shares.
- Existing Yahoo HTTP and yfinance adapters serve daily IDX research; automatic
  fallback is Yahoo → yfinance → configured local Data Bridge. These are two
  transports for one vendor, not independent confirmation. Explicit local
  requests retain their prohibition on network fallback.
- Both Yahoo paths require declared IDR. Jakarta session dates, source,
  retrieval/as-of timestamps, interval, share-volume unit, adjustment and data
  quality travel with frames/provenance. Missing volume remains unavailable.
  Cache format v10 preserves this metadata and does not refresh retrieval time.
- Direct Yahoo adjustment is `unknown`: its parser can fall back when adjclose
  is absent. yfinance uses the existing `auto_adjust=True` contract. Neither
  source certifies historical corporate-action completeness. Freshness is
  `not_evaluated`; delay is `unknown`, never labelled real-time.
- `IDXRegularRules` accepts a source/version/effective interval and exact
  Decimal tick tiers. Tiers use previous close; lot conversion never rounds.
  `IDXSessionCalendar` accepts a complete bounded session-date set and refuses
  dates outside coverage. Both are reference primitives; no default historical
  rules/calendar are bundled and they do not enable matching.
- `src.markets.idx_bar_quality.audit_daily_bars` reports vendor daily-bar
  hazards without changing the bars: rows on closed or uncovered dates against
  a supplied calendar, missing sessions, zero-volume bars whose prices differ
  from the last traded close (placeholder prices), and flat zero-volume days,
  marked `suspended` only when a supplied `IDXSuspension` record covers them.
  Without a calendar the calendar findings are `None`. The `idx_research` tool
  (API, MCP, CLI) returns its zero-volume price-change dates for the analyzed
  window as `bar_audit`, and the research page shows them; no calendar is
  passed, so holiday and suspension checks do not run there.
- `src.markets.idx_bar_quality.audit_series_events` reports, for one symbol,
  where the series ends relative to a supplied `as_of` date, the number of
  supplied-calendar sessions after the last bar (`None` without a calendar or
  outside coverage), and prices around supplied ex dates. `delisted` comes
  only from a supplied `IDXDelisting` record; a series that stops without one
  is `ended_or_stale`. `IDXCorporateAction` records give the previous and
  ex-date closes, their ratio and `adjusted_close`/`close` factors; no price
  is adjusted and no entitlement is checked. No delisting or corporate-action
  list is bundled; `idx_research` calls it only when sourced files are
  configured (below).
- `agent/tests/fixtures/idx_data_quality/` is a shareable synthetic fixture
  pack (made-up `SYN*.JK` codes, January 2030) whose manifest lists the
  findings both audits and the explicit local loader must report for each
  DATA-03 category. Its calendar and records are fixtures, not IDX facts.
- `src.markets.idx_event_records.load_event_records` parses a caller-supplied
  JSON file (`idx_event_records_v1`) of sourced suspensions, delistings and
  corporate actions into those records, refusing the whole file on any
  invalid entry without echoing raw values. It ships no records;
  `idx_research` uses it only through the opt-in env below.
- `src.markets.idx_calendar_file.load_session_calendar` parses a
  caller-supplied JSON file (`idx_session_calendar_v1`: source, coverage and
  strictly ascending sessions) into `IDXSessionCalendar`. It assumes no
  weekday or holiday rule and ships no calendar; `idx_research` uses it only
  through the opt-in env below.
- `agent/tests/fixtures/idx_calendar/bei_sessions_2026.json` (2026-11-15) is
  a sourced BEI 2026 session calendar in that format: Monday to Friday
  exchange days (II-A Kep-00158/BEI/10-2026, I.16) minus the 22 weekday
  closures of BEI Peng-00171/BEI.POP/09-2025, 239 sessions. It is a reference
  fixture that nothing loads automatically, covers 2026 only and stays
  revisable by later BEI notice.
- BEI-sourced fixtures (decision of 2026-11-15) may stay in the public
  repository because they hold only dates and announcement numbers, used
  noncommercially with attribution and access date. Every BEI number in a
  `source` field of `idx_calendar/` and `idx_event_records/` must read
  `<number> (<announcement date>; read YYYY-MM-DD`; each folder has a README
  and holds only JSON files. `test_idx_bei_fixture_attribution.py` enforces
  this. Copying BEI PDFs/text, storing BEI prices or statistics, scraping and
  commercial use remain out of bounds.
- Opt-in research wiring (2026-11-15): when `VIBE_TRADING_IDX_CALENDAR_PATH`
  and/or `VIBE_TRADING_IDX_EVENT_RECORDS_PATH` name such files, `idx_research`
  adds a top-level `sourced_reference` (`idx_sourced_reference_v1`, per-file
  `loaded`/`not_configured`/`unavailable`) and a per-symbol `sourced_audit`
  (`idx_sourced_audit_v1`: calendar findings, suspension status, series end in
  sessions against `end_date`, ex-date moves). Without env nothing changes,
  including `bar_audit` v1 and the 14-day recency. An unreadable or invalid file
  degrades to `unavailable` without echoing its path or content. The
  research page shows these findings, in 11 locales, only when the response
  carries `sourced_reference`.
- Both runner and direct composite construction reject IDX backtesting until
  the historical rulebook/calendar/action model exists. Mixed IDR/USD/CNY/HKD
  pools are rejected by the existing currency guard.

Release scope (2026-11-15) is an "IDX research preview": research, data-quality
audits and opt-in sourced files only; see [the decision record](IDX_RESEARCH_PREVIEW.md).

## Official rule observations and open evidence

Observed 2026-11-03: [IDX trading mechanism](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan)
references II-A Kep-00158/BEI/10-2026. It describes 100-share round lots for
Regular/Cash Market and T+2 Regular settlement. Price tiers use increments
IDR 1/2/5/10/25 at boundaries 200/500/2,000/5,000, held for the session using
the prior close. These observations do not establish historical commencement
dates. The page separates special-monitoring auctions from regular sessions.

Do not infer effective dates from the decree's month or reuse present-day rules
for earlier simulations. Full dated decrees, amendment history, historical
board assignments, price-limit exceptions, holidays, suspensions, corporate
actions and broker fee/tax schedules remain required. Test rule dates are
explicitly synthetic. Registry/holiday inputs must come from authorized
reference exports, not from price gaps.

[IDX company profiles](https://www.idx.id/en/listed-companies/company-profiles/)
is a reference-discovery source, not an integrated or redistributable universe.
Provider access/licensing must be evaluated for the intended deployment.
[Yahoo BBCA history](https://finance.yahoo.com/quote/BBCA.JK/history/)
labels the instrument in IDR with delayed quotes; no real-time entitlement is
claimed. Public endpoint availability does not grant redistribution rights.

## Milestones and acceptance

1. **Phase 1 — assessed:** preserve existing service/tool/state boundaries;
   identify classifier, routing, currency and execution gaps. This document and
   `PROJECT_STATUS.md` hold the assessment; `TODO.md` holds acceptance tasks.
2. **Phase 2A — implemented:** identity/parity, sourced registry primitives,
   daily provider routing, provenance/cache, currency and execution rejection.
   Verify offline fixtures plus a separately reported provider probe.
3. **Phase 2B — import tooling implemented, external evidence pending:**
   read-only normalized JSON import validates source declarations, exact dates,
   duplicates, identity, calendar coverage and Decimal lot/tick primitives using
   existing domain owners. [Import contract and official source findings](IDX_REFERENCE.md).
   Complete authorized snapshots, dated full rulebooks, provider coverage/terms
   and corporate-action calibration remain pending; see RULE-01, DATA-01,
   IDX-02 and RESEARCH-01. No fabricated defaults substitute for these inputs.
   Follow-up discovery records the KSEI notice chain, official rule attachment
   links/access failures and instrument-export limitations in that reference;
   [provider evidence](IDX_PROVIDER_RESEARCH.md) separately records public EoD
   samples and unresolved technical specifications/entitlements. The 2026
   catalogue was subsequently checked page by page: its Professional description
   omits opening price and Basic also omits high/low. Data Reference advertises
   suspension reports, without proving historical event coverage. Supporting
   I-L/I-I/I-N rule attachments were discovered but returned 403, like the main
   rule PDFs. The calendar amendment chain remains incomplete. These findings
   do not satisfy the external-evidence acceptance gates.
   Local disposition now separates a minimal authorized instrument-export intake
   from calendar/rule and provider acceptance; see the
   [minimum handoff and receipt procedure](IDX_REFERENCE.md#phase-2b-disposition-and-minimum-handoff).
   The mapping and review procedure are prepared. Their execution awaits actual
   authorized inputs; no production schema or adapter is inferred from catalogue
   descriptions. Phase 2B remains open, with no new runtime behavior.
4. **Phases 3–8 — planned:** financial statements/events, broker/foreign flow,
   quantitative engines, analyst workflows/valuation, dashboard and release.
   Index Alpha now has publicly readable API documentation, including daily OHLCV,
   base URL, Bearer authentication and limits; see [provider evidence](IDX_PROVIDER_RESEARCH.md).
   Actual responses, OHLCV units/coverage, historical events and usage entitlements
   still require validation. No account, provider integration or execution support
   is supplied by reading those documents.

## Reproduction

Personal research now has a manual watchlist UI at `/research/idx`, shared
`idx_research` agent/MCP tool and standalone module CLI. Chart rows and the
existing indicators derive from one acquisition; this does not enable execution
or complete reference-data acceptance. See [usage, verification and handoff](IDX_PERSONAL_RESEARCH.md).

On this Windows checkout the runtime is `.venv/idx312/Scripts/python.exe`
(Python 3.12.13), installed with hash verification from
`desktop/electron/requirements-windows-lock.txt`. The lock's scipy pin requires
Python >=3.12; the initial 3.11 install failed resolution without modifying pins.
Dev tools use the constraints in `pyproject.toml`; no dependency manifest changed.

From repository root:

```powershell
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_idx_foundation.py agent/tests/test_idx_bar_quality.py agent/tests/test_idx_series_events.py agent/tests/test_idx_data_quality_fixtures.py agent/tests/test_idx_event_records.py agent/tests/test_idx_calendar_file.py agent/tests/test_idx_bei_calendar_2026.py agent/tests/test_market_detection.py agent/tests/test_registry.py agent/tests/test_composite_currency_guard.py agent/tests/test_market_identity_parity.py agent/tests/test_yahoo_loader.py agent/tests/test_yfinance_declared_currency.py agent/tests/test_market_data.py agent/tests/test_market_data_serving_source.py agent/tests/test_loader_retry_helpers.py -q --disable-socket
.venv/idx312/Scripts/python.exe -m pytest agent/tests/test_sdk_order_gate.py agent/tests/test_mandate_enforcement.py agent/tests/test_killswitch_blocks_orders.py agent/tests/test_readonly_default.py -q --allow-hosts=127.0.0.1,::1
git diff --check
```

Windows asyncio needs loopback sockets even with mocked MCP transports, hence
the second command restricts connections to loopback instead of disabling socket
creation. Ordinary IDX tests require no network, credentials or broker access.
For a live provider probe, isolate `VIBE_TRADING_HOME`/home in a temporary
directory and call the existing Yahoo loader for explicit `.JK` symbols; record
requested window, source, row counts and metadata separately from unit results.

Rollback: revert the source changes and cache version together. No database,
account, mandate, credential, broker order or deployment migration is involved.
