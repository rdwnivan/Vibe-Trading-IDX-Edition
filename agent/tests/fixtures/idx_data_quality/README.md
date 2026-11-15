# IDX data-quality fixture pack (DATA-03)

Every file here is **synthetic**: hand-written bars for made-up codes
(`SYNA.JK` … `SYNK.JK`) in January 2030. Nothing is copied from a vendor,
from BEI or from any licensed source, so the pack can be shared and
redistributed with the repository.

- The calendar in `manifest.json` is a test fixture (2030-01-10 is a fixture
  holiday), not an IDX calendar. The suspension, delisting and corporate-action
  records are fixtures too. None of them is a rule, default or fact about IDX.
- Prices are not adjusted by the code under test. `dividend_raw.csv` and
  `split_raw.csv` carry raw OHLC with an `adjusted_close` column, the pattern
  seen in EODHD responses; volume is not checked.
- `manifest.json` lists each case, its category and the findings expected from
  `audit_daily_bars` and `audit_series_events`, or the reason the explicit
  local loader reports (`no_data` for a valid empty file, `fetch_failed` for an
  unparseable price).

The cases are exercised by `agent/tests/test_idx_data_quality_fixtures.py`.
Every CSV here must be referenced by the manifest.
