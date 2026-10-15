#!/usr/bin/env python3
"""Validate RVA23S64 runtime matrix structure and operation evidence records."""
from __future__ import annotations

import pathlib
import re
import sys
from typing import Any

ROOT = pathlib.Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
TABLES = {
    "notes/units/rva23s64-ssnpm-v1.md": {
        "## 访问族矩阵": (4, {
            "Integer load/store", "Atomic（LR/SC/AMO）", "Floating-point load/store",
            "Compressed load/store", "Cache management operations", "Vector load/store",
            "Hypervisor HLV/HSV and VS/VU", "Zicfiss shadow-stack explicit accesses",
            "`FENCE` / `FENCE.I` unused address fields", "Instruction fetch and implicit accesses",
        }, False),
        "### 逐核、逐模式状态": (8, {
            "Integer load/store", "Atomic LR/SC/AMO", "FP load/store", "Compressed load/store",
            "Cache management", "Vector load/store", "Hypervisor access family",
            "Zicfiss shadow-stack access", "`FENCE` / `FENCE.I` unused address fields",
            "Instruction fetch and implicit accesses",
        }, True),
    },
    "notes/units/rva23s64-ssstateen-v1.md": {
        "### 逐 CSR 与模式状态": (7, {f"`{kind}{index}`" for kind in ("sstateen", "hstateen") for index in range(4)}, False),
    },
}
ALLOWED_RESULTS = {"blocked", "run-fail", "run-pass", "unverified"}
MATRIX_STATES = ("tested", "run-pass", "run-fail", "blocked", "unverified", "not-applicable", "static")
EVIDENCE_ROW = re.compile(r"^\|\s*E(\d+)\s*\|")
EVIDENCE_CITATION = re.compile(r"\bE(\d+)\b(?:\s*[-–—]\s*E?(\d+)\b)?")


def _defined_evidence_ids(text: str) -> set[int]:
    return {int(match.group(1)) for line in text.splitlines()
            if (match := EVIDENCE_ROW.match(line))}


def _undefined_evidence_citations(cell: str, defined: set[int]) -> list[str]:
    errors: list[str] = []
    for match in EVIDENCE_CITATION.finditer(cell):
        first = int(match.group(1))
        last = int(match.group(2)) if match.group(2) else first
        if last < first:
            errors.append(match.group(0))
        elif last == first:
            if first not in defined:
                errors.append(f"E{first}")
        elif sum(first <= item <= last for item in defined) != last - first + 1:
            errors.append(match.group(0))
    return errors


def _table_rows(text: str, heading: str, *, label: str, errors: list[str]) -> tuple[list[str], int]:
    offset = text.find(heading)
    if offset < 0:
        errors.append(f"{label}: missing heading {heading!r}")
        return [], 0
    tail = text[offset + len(heading):]
    next_heading = re.search(r"\n#{2,3} ", tail)
    section = tail[:next_heading.start()] if next_heading else tail
    rows = [line for line in section.splitlines() if line.startswith("|")]
    if len(rows) < 2:
        errors.append(f"{label} {heading}: missing Markdown table/header")
        return [], 0
    cells = lambda row: [cell.strip() for cell in row.strip().strip("|").split("|")]
    expected_columns = len(cells(rows[0]))
    body = []
    for number, row in enumerate(rows[1:], 1):
        parts = cells(row)
        if all(not cell or set(cell) <= {"-", ":"} for cell in parts):
            continue
        if len(parts) != expected_columns:
            errors.append(f"{label} {heading}: row {number + 1} has {len(parts)} cells; expected {expected_columns}")
        elif any(not cell for cell in parts):
            errors.append(f"{label} {heading}: row {number + 1} has an empty cell")
        body.append((row, parts))
    return [row for row, _ in body], expected_columns


def _validate_tables(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for relpath, headings in TABLES.items():
        try:
            text = (root / relpath).read_text(encoding="utf-8")
        except OSError as exc:
            errors.append(f"{relpath}: cannot read matrix: {exc}")
            continue
        defined_evidence = _defined_evidence_ids(text)
        for heading, (columns, required, check_statuses) in headings.items():
            rows, actual_columns = _table_rows(text, heading, label=relpath, errors=errors)
            if not rows:
                continue
            if actual_columns != columns:
                errors.append(f"{relpath} {heading}: expected {columns} columns, found {actual_columns}")
            parsed = [row.strip().strip("|").split("|") for row in rows]
            labels = [cells[0].strip() for cells in parsed if cells]
            duplicates = sorted({label for label in labels if labels.count(label) > 1})
            if duplicates:
                errors.append(f"{relpath} {heading}: duplicate rows: {', '.join(duplicates)}")
            missing = required - set(labels)
            if missing:
                errors.append(f"{relpath} {heading}: missing rows: {', '.join(sorted(missing))}")
            if check_statuses:
                for cells in parsed:
                    if not cells:
                        continue
                    label = cells[0].strip()
                    for index, cell in enumerate(cells[1:-1], 1):
                        if not any(re.search(rf"(?<![A-Za-z-]){re.escape(state)}(?![A-Za-z-])", cell)
                                   for state in MATRIX_STATES):
                            errors.append(f"{relpath} {heading}: {label} cell {index} has no allowed evidence state")
                    evidence = cells[-1]
                    if not evidence.strip():
                        errors.append(f"{relpath} {heading}: {label} has no evidence reference/limitation")
                    if any(state in "|".join(cells[1:-1]) for state in ("tested", "run-pass", "run-fail")) and not re.search(r"\bE\d+\b", evidence):
                        errors.append(f"{relpath} {heading}: {label} has runtime state but no evidence ID")
                    for citation in _undefined_evidence_citations(evidence, defined_evidence):
                        errors.append(f"{relpath} {heading}: {label} cites undefined evidence ID/range {citation}")
    return errors


def _validate_manifest(manifest: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(manifest, dict):
        return ["CPU manifest root must be a mapping"]
    snapshots = manifest.get("snapshots")
    if not isinstance(snapshots, list):
        return ["CPU manifest snapshots must be a list"]
    for si, snapshot in enumerate(snapshots):
        label = f"snapshot[{si}]"
        if not isinstance(snapshot, dict):
            errors.append(f"{label} must be a mapping")
            continue
        runs = snapshot.get("runs", [])
        if not isinstance(runs, list):
            errors.append(f"{label} runs must be a list")
            continue
        for ri, run in enumerate(runs):
            run_label = str(run.get("id", f"{label}.run[{ri}]")) if isinstance(run, dict) else f"{label}.run[{ri}]"
            if not isinstance(run, dict):
                errors.append(f"{run_label} must be a mapping")
                continue
            result = run.get("result")
            if not isinstance(result, str) or result not in ALLOWED_RESULTS:
                errors.append(f"{run_label}: invalid result state {result!r}")
            records = run.get("operation_records", [])
            if not isinstance(records, list):
                errors.append(f"{run_label}: operation_records must be a list")
                continue
            ids: list[int] = []
            for oi, item in enumerate(records):
                op_label = f"{run_label}.operation[{oi}]"
                if not isinstance(item, dict):
                    errors.append(f"{op_label} must be a mapping")
                    continue
                op_id = item.get("operation_id")
                if not isinstance(op_id, int) or isinstance(op_id, bool):
                    errors.append(f"{op_label}: operation_id must be an integer")
                else:
                    ids.append(op_id)
                for field in ("mode", "csr", "operation"):
                    if not isinstance(item.get(field), str) or not item[field].strip():
                        errors.append(f"{op_label}: {field} must be a non-empty string")
                expected = item.get("expected")
                expected_cause = item.get("expected_cause")
                if not (isinstance(expected, str) and expected.strip()) and not (
                        isinstance(expected_cause, int) and not isinstance(expected_cause, bool)):
                    errors.append(f"{op_label}: missing expected behavior/cause")
                observed = item.get("observed")
                observed_cause = item.get("observed_cause")
                if not (isinstance(observed, str) and observed.strip()) and not (
                        isinstance(observed_cause, int) and not isinstance(observed_cause, bool)):
                    errors.append(f"{op_label}: missing observation")
            if len(ids) != len(set(ids)):
                errors.append(f"{run_label}: duplicate operation_id")
    return errors


def validate() -> list[str]:
    errors = _validate_tables(ROOT)
    try:
        import yaml
    except ImportError as exc:
        return errors + [f"cannot read CPU manifest: {exc}"]
    try:
        manifest = yaml.safe_load(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, ValueError, yaml.YAMLError) as exc:
        return errors + [f"cannot read CPU manifest: {exc}"]
    return errors + _validate_manifest(manifest)


def main() -> int:
    errors = validate()
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("RVA23S64 run matrices and operation IDs are complete")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
