"""Attribution gate for the BEI-sourced fixture folders (DATA-03, decision A of 2026-11-15).

The session calendar and event-record folders may hold facts taken from BEI
announcements (dates and announcement numbers only). BEI website terms, clause
6, allow noncommercial use with full attribution and access date. So every
BEI announcement number cited in a ``source`` field must carry its
announcement date and the date it was read, and each folder must carry a
README stating the source, attribution, access date, noncommercial use and
that no announcement PDF or text is copied. Only JSON files and the README
may live in these folders.
"""

import json
import re
from datetime import date, datetime
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
BEI_FOLDERS = [FIXTURES / "idx_calendar", FIXTURES / "idx_event_records"]
EVENT_GROUPS = ("suspensions", "delistings", "corporate_actions")

# A BEI announcement or decision number, e.g. Peng-00171/BEI.POP/09-2025,
# Peng-SPT-00097/BEI.WAS/03-2026 or Kep-00158/BEI/10-2026.
BEI_NUMBER = r"(?:Peng|Kep)(?:-[A-Z]+)?-\d{5}/BEI(?:\.[A-Z]+)?/\d{2}-\d{4}"
# The number must be followed by "(<announcement date>; read <YYYY-MM-DD>".
ATTRIBUTED = re.compile(
    rf"(?P<number>{BEI_NUMBER})(?:, [^(;]*)? \((?P<announced>\d{{1,2}} [A-Z][a-z]{{2}} \d{{4}}); read (?P<read>\d{{4}}-\d{{2}}-\d{{2}})"
)
NUMBER = re.compile(BEI_NUMBER)


def _json_files():
    return sorted(path for folder in BEI_FOLDERS for path in folder.glob("*.json"))


def _sources(path: Path) -> list[str]:
    document = json.loads(path.read_text(encoding="utf-8"))
    if "sessions" in document:
        return [document["source"]]
    return [entry["source"] for group in EVENT_GROUPS for entry in document.get(group, [])]


def attribution_problems(source: str) -> list[str]:
    """Return why ``source`` fails the attribution rule; empty when it passes."""
    numbers = NUMBER.findall(source)
    if not numbers:
        return ["no BEI announcement number"]
    attributed = {match["number"]: match for match in ATTRIBUTED.finditer(source)}
    problems = []
    for number in numbers:
        match = attributed.get(number)
        if match is None:
            problems.append(f"{number}: missing '(<announcement date>; read YYYY-MM-DD'")
            continue
        announced = datetime.strptime(match["announced"], "%d %b %Y").date()
        read = date.fromisoformat(match["read"])
        if read < announced:
            problems.append(f"{number}: read before it was announced")
    return problems


def test_both_folders_hold_at_least_one_bei_sourced_json_file():
    assert {path.parent.name for path in _json_files()} == {"idx_calendar", "idx_event_records"}


@pytest.mark.parametrize("path", _json_files(), ids=lambda path: f"{path.parent.name}/{path.name}")
def test_every_bei_number_in_a_source_has_announcement_and_read_dates(path):
    sources = _sources(path)

    assert sources, "a sourced file must carry at least one source"
    assert {source: attribution_problems(source) for source in sources} == {source: [] for source in sources}


@pytest.mark.parametrize(
    "source",
    [
        "BEI holiday notice, read 2026-11-15",
        "BEI Peng-00171/BEI.POP/09-2025, read 2026-11-12",
        "BEI Peng-00171/BEI.POP/09-2025 (23 Sep 2025)",
        "BEI Peng-00171/BEI.POP/09-2025 (23 Sep 2025; read 2026-11-12); Kep-00158/BEI/10-2026, I.16",
        "BEI Peng-SPT-00097/BEI.WAS/03-2026 (26 Mar 2026; read 2026-03-01)",
    ],
)
def test_the_rule_rejects_sources_without_number_dates_or_with_impossible_dates(source):
    assert attribution_problems(source) != []


def test_the_rule_accepts_a_fully_attributed_source():
    source = (
        "BEI Peng-SPT-00097/BEI.WAS/03-2026 (26 Mar 2026; read 2026-11-15): halt; "
        "II-A Kep-00158/BEI/10-2026, I.16 (20 Oct 2026; read 2026-11-12)"
    )

    assert attribution_problems(source) == []


@pytest.mark.parametrize("folder", BEI_FOLDERS, ids=lambda folder: folder.name)
def test_folder_holds_only_json_files_and_a_readme(folder):
    assert sorted(path.name for path in folder.iterdir() if path.suffix != ".json") == ["README.md"]


@pytest.mark.parametrize("folder", BEI_FOLDERS, ids=lambda folder: folder.name)
def test_readme_states_source_attribution_access_date_noncommercial_use_and_no_copy(folder):
    text = (folder / "README.md").read_text(encoding="utf-8")

    assert "Bursa Efek Indonesia" in text
    assert "idx.id/id/syarat-penggunaan" in text
    assert re.search(r"[Aa]ccessed \d{4}-\d{2}-\d{2}", text)
    assert "noncommercial" in text
    assert "not copied" in text
    for path in folder.glob("*.json"):
        assert path.name in text
