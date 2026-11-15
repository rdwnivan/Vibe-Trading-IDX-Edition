"""The sourced MLPT suspension of 27 March 2026 as an event-record file.

The record comes from BEI announcements Peng-SPT-00097/BEI.WAS/03-2026 and
Peng-UPT-00108/BEI.WAS/03-2026 (see IDX_PROVIDER_RESEARCH.md). It is a test
fixture, not a default list. The bars below are synthetic: only the shape of
the vendor row (flat, zero volume) is reproduced, not vendor prices.
"""

from datetime import date
from pathlib import Path

import pandas as pd

from src.markets.idx_bar_quality import IDXSuspension, audit_daily_bars
from src.markets.idx_event_records import load_event_records

RECORD = Path(__file__).parent / "fixtures" / "idx_event_records" / "mlpt_2026-03_suspension.json"


def test_record_file_holds_one_sourced_one_day_mlpt_suspension():
    records = load_event_records(RECORD)

    assert records.delistings == ()
    assert records.corporate_actions == ()
    [halt] = records.suspensions
    assert halt == IDXSuspension(
        symbol="MLPT.JK",
        source=halt.source,
        first_day=date(2026, 3, 27),
        last_day=date(2026, 3, 27),
    )
    assert "Peng-SPT-00097/BEI.WAS/03-2026" in halt.source
    assert "Peng-UPT-00108/BEI.WAS/03-2026" in halt.source
    assert "Regular and Cash" in halt.source


def test_flat_zero_volume_row_on_the_halt_day_is_reported_as_suspended():
    frame = pd.DataFrame(
        {
            "open": [100.0, 100.0, 101.0],
            "high": [100.0, 100.0, 101.0],
            "low": [100.0, 100.0, 101.0],
            "close": [100.0, 100.0, 101.0],
            "volume": [1000.0, 0.0, 1200.0],
        },
        index=pd.DatetimeIndex(["2026-03-26", "2026-03-27", "2026-03-30"]),
    )

    without = audit_daily_bars("MLPT.JK", frame)
    with_record = audit_daily_bars("MLPT.JK", frame, suspensions=load_event_records(RECORD).suspensions)

    assert without["zero_volume_flat_bars"] == [{"date": "2026-03-27", "status": "untraded_or_suspended"}]
    assert with_record["zero_volume_flat_bars"] == [{"date": "2026-03-27", "status": "suspended"}]
    assert with_record["traded_during_suspension_dates"] == []
