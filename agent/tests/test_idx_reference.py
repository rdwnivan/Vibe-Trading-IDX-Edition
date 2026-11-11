"""Synthetic reference artifacts: no official data or redistribution rights implied."""

from datetime import date
from decimal import Decimal
import hashlib
import json
from pathlib import Path

import pytest

from src.markets.idx_reference import load_idx_reference, main


@pytest.fixture
def artifact():
    path = Path(__file__).parent / "fixtures/idx_reference/instruments.synthetic.json"
    return json.loads(path.read_text(encoding="utf-8"))


def write_artifact(tmp_path, artifact):
    path = tmp_path / "reference.json"
    path.write_text(json.dumps(artifact), encoding="utf-8")
    return path


def test_import_resolves_only_exact_snapshot_and_preserves_provenance(tmp_path, artifact):
    path = write_artifact(tmp_path, artifact)
    snapshot = load_idx_reference(path)
    instrument = snapshot.data.resolve("BBCA", as_of=date(2026, 11, 3))
    assert instrument.symbol == "BBCA.JK"
    assert instrument.source == "fixture://synthetic-reference"
    assert snapshot.usage_terms == "Synthetic test only"
    assert snapshot.sha256 == hashlib.sha256(path.read_bytes()).hexdigest()
    with pytest.raises(ValueError, match="dated"):
        snapshot.data.resolve("BBCA", as_of=date(2026, 11, 2))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("schema_version", True),
        ("schema_version", 2),
        ("currency", "USD"),
        ("market", "us_equity"),
        ("timezone", "UTC"),
        ("source", " "),
        ("usage_terms", None),
        ("retrieved_at", "2026-11-03T10:00:00"),
        ("kind", "unknown"),
        ("payload", []),
    ],
)
def test_invalid_envelope_is_rejected(tmp_path, artifact, field, value):
    artifact[field] = value
    with pytest.raises(ValueError):
        load_idx_reference(write_artifact(tmp_path, artifact))


@pytest.mark.parametrize("as_of", ["20261103", "2026-02-30", "2026-11-03T00:00:00", None])
def test_ambiguous_or_invalid_snapshot_date_is_rejected(tmp_path, artifact, as_of):
    artifact["payload"]["as_of"] = as_of
    with pytest.raises(ValueError):
        load_idx_reference(write_artifact(tmp_path, artifact))


def test_normalized_duplicate_symbols_are_rejected(tmp_path, artifact):
    artifact["payload"]["instruments"].append({"symbol": "BBCA.JK", "name": "Duplicate"})
    with pytest.raises(ValueError, match="Duplicate"):
        load_idx_reference(write_artifact(tmp_path, artifact))


@pytest.mark.parametrize("symbol", ["BBCA", "AAPL.US", "BBCA-W.JK"])
def test_import_does_not_guess_venue_or_instrument_class(tmp_path, artifact, symbol):
    artifact["payload"]["instruments"][0]["symbol"] = symbol
    with pytest.raises(ValueError, match="regular-share"):
        load_idx_reference(write_artifact(tmp_path, artifact))


def test_unknown_fields_cannot_be_silently_dropped(tmp_path, artifact):
    artifact["payload"]["instruments"][0]["tradable"] = True
    with pytest.raises(ValueError, match="unsupported fields"):
        load_idx_reference(write_artifact(tmp_path, artifact))


def test_duplicate_json_keys_are_rejected(tmp_path):
    path = tmp_path / "duplicate.json"
    path.write_text('{"currency":"IDR","currency":"USD"}', encoding="utf-8")
    with pytest.raises(ValueError, match="Duplicate JSON"):
        load_idx_reference(path)


@pytest.fixture
def calendar(artifact):
    artifact["kind"] = "calendar"
    artifact["payload"] = {
        "covered_from": "2026-11-02",
        "covered_until": "2026-11-08",
        "complete": True,
        "sessions": ["2026-11-02", "2026-11-03"],
    }
    return artifact


def test_calendar_closure_is_bounded_by_explicit_coverage(tmp_path, calendar):
    data = load_idx_reference(write_artifact(tmp_path, calendar)).data
    assert data.is_session(date(2026, 11, 3)) is True
    assert data.is_session(date(2026, 11, 4)) is False
    with pytest.raises(ValueError, match="outside"):
        data.is_session(date(2026, 11, 9))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("complete", False),
        ("complete", 1),
        ("sessions", []),
        ("sessions", ["2026-11-02", "2026-11-02"]),
        ("sessions", ["2026-11-09"]),
        ("covered_until", "2026-11-01"),
    ],
)
def test_incomplete_duplicate_or_uncovered_calendar_is_rejected(tmp_path, calendar, field, value):
    calendar["payload"][field] = value
    with pytest.raises(ValueError):
        load_idx_reference(write_artifact(tmp_path, calendar))


@pytest.fixture
def rules(artifact):
    artifact["kind"] = "regular_rules"
    artifact["payload"] = {
        "version": "SYNTHETIC-ONLY",
        "effective_from": "2026-11-02",
        "effective_until": "2026-11-03",
        "lot_shares": 10,
        "tick_tiers": [["0", "1"], ["100", "2"]],
    }
    return artifact


def test_rule_import_preserves_exact_decimal_and_effective_interval(tmp_path, rules):
    data = load_idx_reference(write_artifact(tmp_path, rules)).data
    assert data.tick_size(Decimal("100"), session_date=date(2026, 11, 3)) == Decimal("2")
    assert data.shares_from_lots(3) == 30
    with pytest.raises(ValueError, match="outside"):
        data.tick_size(Decimal("100"), session_date=date(2026, 11, 4))


@pytest.mark.parametrize("tiers", [[[0, 1]], [["0", "NaN"]], [["0", "-1"]], [["100", "2"]], [["0", "oops"]]])
def test_invalid_or_float_rule_tiers_are_rejected(tmp_path, rules, tiers):
    rules["payload"]["tick_tiers"] = tiers
    with pytest.raises(ValueError):
        load_idx_reference(write_artifact(tmp_path, rules))


def test_cli_prints_structure_only_summary(tmp_path, artifact, capsys):
    assert main([str(write_artifact(tmp_path, artifact))]) == 0
    output = json.loads(capsys.readouterr().out)
    assert output["records"] == 1
    assert output["validation"] == "structure_only"
    assert "Synthetic issuer" not in str(output)


def test_cli_returns_nonzero_without_echoing_private_input(tmp_path, capsys):
    path = tmp_path / "private.json"
    path.write_text('{"private":"PRIVATE_SENTINEL"}', encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        main([str(path)])
    assert error.value.code == 2
    stderr = capsys.readouterr().err
    assert "Invalid IDX reference" in stderr
    assert "PRIVATE_SENTINEL" not in stderr
    assert str(path) not in stderr
