# /// script
# requires-python = ">=3.10"
# dependencies = ["pytest>=8.0"]
# ///
"""Regression tests for mandatory inventory, summaries, and evidence links."""
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "scripts/check_rva23_coverage.py"
spec = importlib.util.spec_from_file_location("check_rva23_coverage", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
COVERAGE = (ROOT / "notes/rva23-coverage.md").read_text(encoding="utf-8")
AUDIT = (ROOT / "notes/units/rva23-mandatory-coverage-audit-v1.md").read_text(encoding="utf-8")
FIRST_ROW = next(line for line in COVERAGE.splitlines() if line.startswith("| `RVA23U64/"))


def replace_row(text, transform):
    return text.replace(FIRST_ROW, transform(FIRST_ROW), 1)


def test_inventory_accepts_indented_markdown_rows():
    indented = replace_row(COVERAGE, lambda row: "   " + row)
    assert len(checker.validate_inventory(indented)) == 92


def test_inventory_rejects_duplicate_key():
    with pytest.raises(SystemExit, match="duplicate mandatory key"):
        checker.validate_inventory(COVERAGE + "\n" + FIRST_ROW + "\n")


def test_inventory_rejects_two_statuses_in_one_implementation_cell():
    bad = replace_row(COVERAGE, lambda row: row.replace("状态：`partially-studied`", "状态：`partially-studied`；状态：`studied-unverified`", 1))
    with pytest.raises(SystemExit, match="exactly one legal status"):
        checker.validate_inventory(bad)


def test_inventory_rejects_wrong_section():
    bad = replace_row(COVERAGE, lambda row: row.replace("§3.1.1.1", "§3.1.1.2", 1))
    with pytest.raises(SystemExit, match="must use section"):
        checker.validate_inventory(bad)


def test_inventory_rejects_missing_key():
    with pytest.raises(SystemExit, match="inventory mismatch"):
        checker.validate_inventory(COVERAGE.replace(FIRST_ROW + "\n", "", 1))


def test_inventory_rejects_illegal_status():
    bad = replace_row(COVERAGE, lambda row: row.replace("partially-studied", "unsupported", 1))
    with pytest.raises(SystemExit, match="exactly one legal status"):
        checker.validate_inventory(bad)


def test_both_status_summary_tables_match_derived_counts():
    rows = checker.validate_inventory(COVERAGE)
    checker.validate_summary_table(COVERAGE, rows, ROOT / "notes/rva23-coverage.md")
    checker.validate_summary_table(AUDIT, rows, ROOT / "notes/units/rva23-mandatory-coverage-audit-v1.md")


def test_summary_rejects_status_or_profile_row_count_drift():
    rows = checker.validate_inventory(COVERAGE)
    wrong_status = COVERAGE.replace("| RVA23U64 | Kunminghu | 21 |", "| RVA23U64 | Kunminghu | 22 |", 1)
    with pytest.raises(SystemExit, match="summary mismatch"):
        checker.validate_summary_table(wrong_status, rows, ROOT / "notes/rva23-coverage.md")
    wrong_rows = AUDIT.replace("| RVA23S64 | Heliodor | 26 | 29 | 1 | 2 | 0 | 0 | 58 |", "| RVA23S64 | Heliodor | 26 | 28 | 2 | 2 | 0 | 0 | 57 |", 1)
    with pytest.raises(SystemExit, match="summary mismatch"):
        checker.validate_summary_table(wrong_rows, rows, ROOT / "notes/units/rva23-mandatory-coverage-audit-v1.md")


def test_narrative_totals_and_dedup_formula_are_checked():
    checker.validate_narrative_totals(COVERAGE, AUDIT)
    with pytest.raises(SystemExit, match="narrative dedup total"):
        checker.validate_narrative_totals(COVERAGE.replace("**59**", "**58**", 1), AUDIT)


def test_evidence_link_requires_existing_file_anchor_and_id(tmp_path):
    unit = tmp_path / "unit.md"
    unit.write_text('<a id="evidence-table"></a>\n| E1 | claim |\n', encoding="utf-8")
    source = tmp_path / "coverage.md"
    checker.validate_evidence_links("[E1](unit.md#evidence-table)", source)
    with pytest.raises(SystemExit, match="absent evidence IDs"):
        checker.validate_evidence_links("[E2](unit.md#evidence-table)", source)
    unit.write_text("| E1 | claim |\n", encoding="utf-8")
    with pytest.raises(SystemExit, match="lacks #evidence-table"):
        checker.validate_evidence_links("[E1](unit.md#evidence-table)", source)
    with pytest.raises(SystemExit, match="target missing"):
        checker.validate_evidence_links("[E1](missing.md#evidence-table)", source)


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


def test_summary_table_accepts_indented_rows():
    rows = checker.validate_inventory(COVERAGE)
    indented = "\n".join("  " + line if line.startswith("| RVA23") else line for line in COVERAGE.splitlines())
    checker.validate_summary_table(indented, rows, ROOT / "notes/rva23-coverage.md")


def test_validate_all_runs_full_inventory_summary_and_link_audit():
    rows = checker.validate_all(checker.COVERAGE, checker.AUDIT)
    assert len(rows) == 92


def test_suffixed_ranges_expand_every_intermediate_evidence_id(tmp_path):
    unit = tmp_path / "unit.md"
    ids = [*(f"E1{chr(letter)}" for letter in range(ord('a'), ord('z') + 1)), "E2a", "E2b"]
    unit.write_text('<a id="evidence-table"></a>\n' + "".join(f"| {item} | claim |\n" for item in ids), encoding="utf-8")
    checker.validate_evidence_links("[E1a–E2b](unit.md#evidence-table)", tmp_path / "coverage.md")
    assert checker.evidence_ids("E1a–E2b") == set(ids)


def test_evidence_table_anchor_alias_matches_its_declared_id(tmp_path):
    unit = tmp_path / "unit.md"
    unit.write_text('<a id="evidence_table"></a>\n| E1 | claim |\n', encoding="utf-8")
    checker.validate_evidence_links("[E1](unit.md#evidence_table)", tmp_path / "coverage.md")


def test_evidence_table_anchor_is_checked_without_id_in_link_label(tmp_path):
    unit = tmp_path / "unit.md"
    unit.write_text("## 证据表\n| E1 | claim |\n", encoding="utf-8")
    source = tmp_path / "coverage.md"
    checker.validate_evidence_links("[审计记录](unit.md#证据表)", source)
    with pytest.raises(SystemExit, match="lacks #evidence-table"):
        checker.validate_evidence_links("[审计记录](unit.md#evidence-table)", source)
