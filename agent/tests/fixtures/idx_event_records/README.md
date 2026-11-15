# Sourced IDX event records

`mlpt_2026-03_suspension.json` (`idx_event_records_v1`) holds one trading
suspension of `MLPT.JK` on 27 March 2026. It records dates and announcement
numbers only, taken from public announcements of
**PT Bursa Efek Indonesia (BEI, Indonesia Stock Exchange)**:

- Peng-SPT-00097/BEI.WAS/03-2026 (26 Mar 2026): suspension on 27 Mar 2026 in
  the Regular and Cash Markets. Accessed 2026-11-15.
- Peng-UPT-00108/BEI.WAS/03-2026 (27 Mar 2026): trading reopened on
  30 Mar 2026. Accessed 2026-11-15.

Source: BEI, [idx.co.id](https://www.idx.co.id) (Suspensi page). The `source`
field of each record names each announcement number with its announcement date
and the date it was read; `agent/tests/test_idx_bei_fixture_attribution.py`
fails if one is missing.

**Terms.** Use follows clause 6 of the BEI website terms
([idx.id/id/syarat-penggunaan](https://www.idx.id/id/syarat-penggunaan)):
noncommercial use with full source attribution and access date. This file is
kept for noncommercial, personal research and testing. Commercial use or
dissemination needs written permission from BEI and is not granted here.

**What is not here.** The announcement PDFs and their text are not copied; only
dates and announcement numbers are recorded. No BEI price data or statistics
are stored, and nothing was scraped or crawled (each announcement was read once
in a browser viewer).

The file is a test fixture, not a default list of events. Nothing loads it
automatically; an operator opts in with `VIBE_TRADING_IDX_EVENT_RECORDS_PATH`.
Decision record:
[IDX_RESEARCH_PREVIEW.md](../../../IDX_RESEARCH_PREVIEW.md#4-hak-distribusi-fakta-bersumber-bei-data-03).
