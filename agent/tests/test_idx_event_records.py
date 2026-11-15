"""Loader for caller-supplied, sourced IDX event records (DATA-03).

Every record here is synthetic (codes SYN*.JK, year 2030). The loader holds no
suspension, delisting or corporate-action data of its own.
"""

from datetime import date
import json

import pytest

from src.markets.idx_bar_quality import IDXCorporateAction, IDXDelisting, IDXSuspension
from src.markets.idx_event_records import SCHEMA, IDXEventRecords, load_event_records

SUSPENSION = {"symbol": "SYNE.JK", "source": "synthetic notice", "first_day": "2030-01-14", "last_day": "2030-01-15"}
DELISTING = {"symbol": "SYNF.JK", "source": "synthetic notice", "effective_day": "2030-01-15"}
ACTION = {"symbol": "SYNH.JK", "source": "synthetic notice", "kind": "cash_dividend", "ex_day": "2030-01-15"}


def document(**groups):
    return {"schema": "idx_event_records_v1", **groups}


@pytest.fixture
def write(tmp_path):
    def write(payload, *, raw=False):
        path = tmp_path / "events.json"
        path.write_text(payload if raw else json.dumps(payload), encoding="utf-8")
        return path

    return write


def test_valid_file_loads_into_typed_records(write):
    records = load_event_records(
        write(document(suspensions=[SUSPENSION], delistings=[DELISTING], corporate_actions=[ACTION]))
    )

    assert SCHEMA == "idx_event_records_v1"
    assert isinstance(records, IDXEventRecords)
    assert records.suspensions == (
        IDXSuspension(
            symbol="SYNE.JK", source="synthetic notice", first_day=date(2030, 1, 14), last_day=date(2030, 1, 15)
        ),
    )
    assert records.delistings == (
        IDXDelisting(symbol="SYNF.JK", source="synthetic notice", effective_day=date(2030, 1, 15)),
    )
    assert records.corporate_actions == (
        IDXCorporateAction(symbol="SYNH.JK", source="synthetic notice", kind="cash_dividend", ex_day=date(2030, 1, 15)),
    )


def test_absent_groups_are_empty_tuples_not_defaults(write):
    records = load_event_records(write(document()))

    assert records == IDXEventRecords(suspensions=(), delistings=(), corporate_actions=())


def test_records_keep_file_order(write):
    later = {**SUSPENSION, "first_day": "2030-01-16", "last_day": "2030-01-16"}
    records = load_event_records(write(document(suspensions=[later, SUSPENSION])))

    assert [item.first_day for item in records.suspensions] == [date(2030, 1, 16), date(2030, 1, 14)]


def test_loaded_records_feed_the_audits_as_tuples(write):
    records = load_event_records(write(document(delistings=[DELISTING])))

    assert isinstance(records.delistings, tuple)
    assert isinstance(records.suspensions, tuple)
    assert isinstance(records.corporate_actions, tuple)


@pytest.mark.parametrize(
    "payload",
    [
        [],
        "idx_event_records_v1",
        {"suspensions": []},
        {"schema": "idx_event_records_v2"},
        {"schema": "idx_event_records_v1", "extra": []},
        {"schema": "idx_event_records_v1", "suspensions": {}},
        {"schema": "idx_event_records_v1", "delistings": None},
        {"schema": "idx_event_records_v1", "corporate_actions": [["SYNH.JK"]]},
    ],
    ids=[
        "list-top-level",
        "string-top-level",
        "no-schema",
        "unknown-schema",
        "unknown-group",
        "group-not-list",
        "group-null",
        "entry-not-object",
    ],
)
def test_malformed_document_is_refused(write, payload):
    with pytest.raises(ValueError):
        load_event_records(write(payload))


@pytest.mark.parametrize(
    "group, entry",
    [
        ("suspensions", {**SUSPENSION, "note": "x"}),
        ("suspensions", {key: value for key, value in SUSPENSION.items() if key != "source"}),
        ("suspensions", {**SUSPENSION, "source": " "}),
        ("suspensions", {**SUSPENSION, "symbol": "AAPL"}),
        ("suspensions", {**SUSPENSION, "last_day": "2030-01-13"}),
        ("delistings", {**DELISTING, "effective_day": "20300115"}),
        ("delistings", {**DELISTING, "effective_day": "2030-1-15"}),
        ("delistings", {**DELISTING, "effective_day": "2030-01-15T00:00:00"}),
        ("delistings", {**DELISTING, "effective_day": 20300115}),
        ("delistings", {**DELISTING, "effective_day": "2030-02-30"}),
        ("corporate_actions", {**ACTION, "kind": "dividend"}),
        ("corporate_actions", {**ACTION, "ratio": 0.2}),
        ("corporate_actions", {**ACTION, "symbol": None}),
    ],
    ids=[
        "unknown-field",
        "missing-source",
        "blank-source",
        "non-idx-symbol",
        "reversed-suspension",
        "compact-date",
        "unpadded-date",
        "datetime",
        "numeric-date",
        "impossible-date",
        "unknown-kind",
        "amount-field",
        "null-symbol",
    ],
)
def test_invalid_entry_is_refused(write, group, entry):
    with pytest.raises(ValueError):
        load_event_records(write(document(**{group: [entry]})))


def test_error_names_the_entry_without_echoing_raw_values(write):
    marker = "SYNTHETIC_PRIVATE_MARKER"
    with pytest.raises(ValueError) as caught:
        load_event_records(write(document(corporate_actions=[ACTION, {**ACTION, "kind": marker}])))

    message = str(caught.value)
    assert "corporate_actions[1]" in message
    assert marker not in message


def test_duplicate_records_are_refused(write):
    with pytest.raises(ValueError):
        load_event_records(write(document(corporate_actions=[ACTION, dict(ACTION)])))


def test_two_delistings_for_one_symbol_are_refused(write):
    second = {**DELISTING, "effective_day": "2030-01-16"}
    with pytest.raises(ValueError):
        load_event_records(write(document(delistings=[DELISTING, second])))


def test_duplicate_json_keys_are_refused(write):
    raw = '{"schema": "idx_event_records_v1", "delistings": [], "delistings": []}'
    with pytest.raises(ValueError):
        load_event_records(write(raw, raw=True))


@pytest.mark.parametrize("raw", ["{", "", '{"schema": NaN}', "﻿{}"])
def test_invalid_json_is_refused(write, raw):
    with pytest.raises(ValueError):
        load_event_records(write(raw, raw=True))


def test_missing_file_is_refused(tmp_path):
    with pytest.raises(ValueError):
        load_event_records(tmp_path / "absent.json")
