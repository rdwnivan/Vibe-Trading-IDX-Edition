# Sourced IDX session calendars

`bei_sessions_2026.json` (`idx_session_calendar_v1`) lists the 239 exchange
days of 2026. It holds dates only, taken from public announcements of
**PT Bursa Efek Indonesia (BEI, Indonesia Stock Exchange)**:

- II-A Kep-00158/BEI/10-2026, item I.16 (20 Oct 2026): an exchange day is a
  weekday that is not a national or declared exchange holiday. Accessed
  2026-11-12.
- Peng-00171/BEI.POP/09-2025 (23 Sep 2025): the 22 weekday closures of 2026.
  Accessed 2026-11-12. KSEI PENG-0005/DIR/KSEI/1025 and PENG-0002/DIR/KSEI/0126
  list the same closures.
- BEI announcement index, keyword "Libur Bursa": no 2026 amendment listed.
  Accessed 2026-11-15.

Source: BEI, [idx.co.id](https://www.idx.co.id). The `source` field of the file
names each announcement number with its announcement date and the date it was
read; `agent/tests/test_idx_bei_fixture_attribution.py` fails if one is
missing.

**Terms.** Use follows clause 6 of the BEI website terms
([idx.id/id/syarat-penggunaan](https://www.idx.id/id/syarat-penggunaan)):
noncommercial use with full source attribution and access date. This file is
kept for noncommercial, personal research and testing. Commercial use or
dissemination needs written permission from BEI and is not granted here.

**What is not here.** The announcement PDFs and their text are not copied; only
dates and announcement numbers are recorded. No BEI price data or statistics
are stored, and nothing was scraped or crawled. BEI may revise the calendar by
a later notice; trading hours, half days and instrument suspensions are not
covered.

The file is a test fixture. Nothing loads it automatically; an operator opts
in with `VIBE_TRADING_IDX_CALENDAR_PATH`. Decision record:
[IDX_RESEARCH_PREVIEW.md](../../../IDX_RESEARCH_PREVIEW.md#4-hak-distribusi-fakta-bersumber-bei-data-03).
