#!/usr/bin/env python3
"""Validate the RVA23 Profile v1.0 inventory, evidence links, and summaries."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "notes/rva23-coverage.md"
AUDIT = ROOT / "notes/units/rva23-mandatory-coverage-audit-v1.md"
IMPLEMENTATIONS = ("Kunminghu", "Heliodor")
STATUS_COLUMNS = ("partially-studied", "studied-unverified", "not-studied", "evidence-observed", "not-present", "out-of-scope")
# Requirement IDs transcribed from RVA23 Profile v1.0 §§3.1.1–3.1.2.
U64_IDS = set("""RV64I M A F D C B Zicsr Zicntr Zihpm Ziccif Ziccrse Ziccamoa Zicclsm Za64rs Zihintpause Zic64b Zicbom Zicbop Zicboz Zfhmin Zkt V Zvfhmin Zvbb Zvkt Zihintntl Zicond Zimop Zcmop Zcb Zfa Zawrs Supm""".split())
S64_IDS = set("""RV64I M A F D C B Zicsr Zicntr Zihpm Ziccif Ziccrse Ziccamoa Zicclsm Za64rs Zihintpause Zic64b Zicbom Zicbop Zicboz Zfhmin Zkt V Zvfhmin Zvbb Zvkt Zihintntl Zicond Zimop Zcmop Zcb Zfa Zawrs Supm Zifencei Ss1p13 Svbare Sv39 Svade Ssccptr Sstvecd Sstvala Sscounterenw Svpbmt Svinval Svnapot Sstc Sscofpmf Ssnpm Ssu64xl H Ssstateen Shcounterenw Shvstvala Shtvala Shvstvecd Shvsatpa Shgatpa""".split())
ALLOWED = {"not-studied", "partially-studied", "studied-unverified", "evidence-observed", "not-present", "out-of-scope"}
EXPECTED_COUNTS = {
    ("U64", "Kunminghu"): {"partially-studied": 21, "studied-unverified": 13},
    ("U64", "Heliodor"): {"partially-studied": 14, "studied-unverified": 20},
    ("S64", "Kunminghu"): {"partially-studied": 37, "studied-unverified": 20, "not-studied": 1},
    ("S64", "Heliodor"): {"partially-studied": 26, "studied-unverified": 28, "not-studied": 2, "evidence-observed": 2},
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def parse_rows(text: str) -> dict[tuple[str, str], tuple[list[str], str]]:
    rows: dict[tuple[str, str], tuple[list[str], str]] = {}
    candidate = re.compile(r"^\s*\|\s*`RVA23(?:U64|S64)/v1\.0/")
    key_pattern = re.compile(r"^\s*\|\s*`RVA23(U64|S64)/v1\.0/§([^/]+)/([^`]+)`\s*\|")
    for line_no, line in enumerate(text.splitlines(), 1):
        if not candidate.match(line):
            continue
        match = key_pattern.match(line)
        if not match:
            fail(f"line {line_no}: malformed mandatory inventory key")
        profile, section, req_id = match.groups()
        cells = table_cells(line)
        if len(cells) != 4:
            fail(f"line {line_no}: expected 4 table cells, found {len(cells)}")
        key = (profile, req_id)
        if key in rows:
            fail(f"duplicate mandatory key: {key}")
        if "待填" in line:
            fail(f"line {line_no}: unresolved template placeholder")
        statuses: list[str] = []
        for impl, cell in zip(IMPLEMENTATIONS, cells[2:4]):
            found = re.findall(r"状态：`([^`]+)`", cell)
            if len(found) != 1 or found[0] not in ALLOWED:
                fail(f"line {line_no}: {impl} cell must contain exactly one legal status; got {found}")
            statuses.append(found[0])
        expected_section = ("3.1.1.1" if req_id == "RV64I" else "3.1.1.2") if profile == "U64" else ("3.1.2.1" if req_id == "RV64I" else "3.1.2.2")
        if section != expected_section:
            fail(f"line {line_no}: {profile}/{req_id} must use section {expected_section}, got {section}")
        rows[key] = (statuses, line)
    return rows


def computed_counts(rows):
    counts: dict[tuple[str, str], collections.Counter[str]] = {}
    for (profile, _), (statuses, _) in rows.items():
        for impl, status in zip(IMPLEMENTATIONS, statuses):
            counts.setdefault((profile, impl), collections.Counter())[status] += 1
    return counts


def deduplicated_requirement_count() -> int:
    inherited = (U64_IDS & S64_IDS) - {"RV64I"}
    # RV64I is a separately stated base requirement in each profile; only the
    # 33 inherited extension rows are cross-profile aliases.
    return len(U64_IDS) + len(S64_IDS) - len(inherited)


def validate_inventory(text: str):
    rows = parse_rows(text)
    expected = {("U64", req) for req in U64_IDS} | {("S64", req) for req in S64_IDS}
    actual = set(rows)
    if actual != expected:
        fail(f"inventory mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    if len(rows) != len(U64_IDS) + len(S64_IDS):
        fail(f"profile row total mismatch: found {len(rows)}")
    counts = computed_counts(rows)
    for key, expected_counts in EXPECTED_COUNTS.items():
        if dict(counts.get(key, {})) != expected_counts:
            fail(f"{key} count mismatch: expected {expected_counts}, got {dict(counts.get(key, {}))}")

    inherited = (U64_IDS & S64_IDS) - {"RV64I"}
    for req in inherited:
        _, line = rows[("S64", req)]
        origin = re.search(r"关联原始要求 `RVA23U64/v1\.0/§3\.1\.1\.2/([^`]+)`", line)
        if not origin or origin.group(1) != req:
            fail(f"S64/{req}: missing or mismatched U64 inherited source link")
    for (profile, req), (_, line) in rows.items():
        if profile == "S64" and req not in inherited and "关联原始要求 `RVA23U64/" in line:
            fail(f"S64/{req}: unexpected inherited-source link")
    return rows


def evidence_ids(label: str) -> set[str]:
    result: set[str] = set()
    pattern = r"E(\d+)([a-z]?)(?:\s*[–-]\s*E?(\d+)([a-z]?))?"
    for start, start_suffix, end, end_suffix in re.findall(pattern, label):
        lo = int(start)
        if not end:
            result.add(f"E{lo}{start_suffix}")
            continue
        hi = int(end)
        if hi < lo or hi - lo > 1000:
            fail(f"invalid or excessive evidence ID range: E{start}{start_suffix}–E{end}{end_suffix}")
        for number in range(lo, hi + 1):
            low_rank = (ord(start_suffix) - 96) if number == lo and start_suffix else 0
            if number == hi and number != lo and end_suffix:
                low_rank = 1
            if lo == hi:
                high_rank = (ord(end_suffix) - 96) if end_suffix else low_rank
            elif number == lo:
                high_rank = 26 if start_suffix else 0
            elif number == hi:
                high_rank = (ord(end_suffix) - 96) if end_suffix else 0
            else:
                high_rank = 0
            for rank in range(low_rank, high_rank + 1):
                suffix = chr(96 + rank) if rank else ""
                result.add(f"E{number}{suffix}")
    return result


def validate_evidence_links(markdown: str, markdown_path: Path) -> None:
    links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", markdown)
    evidence_anchors = {"evidence-table", "evidence_table", "证据表"}
    for label, target in links:
        if re.match(r"^(?:https?://|mailto:|tel:)", target, re.IGNORECASE):
            continue
        ids = evidence_ids(label)
        target_path, _, anchor = target.partition("#")
        if not ids and anchor not in evidence_anchors:
            continue
        local_path = (markdown_path.parent / unquote(target_path)).resolve() if target_path else markdown_path.resolve()
        if not local_path.is_file():
            fail(f"{display_path(markdown_path)}: evidence link target missing: {target}")
        evidence_doc = local_path.read_text(encoding="utf-8")
        if anchor == "evidence-table" and not re.search(r'<a\s+id=["\']evidence-table["\']\s*>', evidence_doc):
            fail(f"{display_path(markdown_path)}: target lacks #{anchor}: {target_path}")
        if anchor == "evidence_table" and not re.search(r'<a\s+id=["\']evidence_table["\']\s*>', evidence_doc):
            fail(f"{display_path(markdown_path)}: target lacks #{anchor}: {target_path}")
        if anchor == "证据表" and not re.search(r"^##\s+证据表\s*$", evidence_doc, re.MULTILINE):
            fail(f"{display_path(markdown_path)}: target lacks #{anchor}: {target_path}")
        if ids:
            present = {f"E{n}" for n in re.findall(r"^\|\s*E(\d+[a-z]?)\s*\|", evidence_doc, re.MULTILINE)}
            missing = ids - present
            if missing:
                fail(f"{display_path(markdown_path)}: {target} references absent evidence IDs {sorted(missing)}")


def parse_summary_table(text: str, path: Path):
    lines = text.splitlines()
    expected_header = ["Profile", "实现", *STATUS_COLUMNS, "行数"]
    header_index = next((i for i, line in enumerate(lines) if table_cells(line)[:2] == ["Profile", "实现"]), None)
    if header_index is None:
        fail(f"{path}: status summary table not found")
    header = table_cells(lines[header_index])
    if header != expected_header:
        fail(f"{path}: unexpected summary columns {header}")
    rows = {}
    for line_no, line in enumerate(lines[header_index + 1:], header_index + 2):
        cells = table_cells(line)
        if not cells or not cells[0].startswith("RVA23"):
            if rows:
                break
            continue
        if len(cells) != len(header):
            fail(f"{path}:{line_no}: summary row has {len(cells)} columns, expected {len(header)}")
        key = ("U64" if cells[0] == "RVA23U64" else "S64" if cells[0] == "RVA23S64" else "?", cells[1])
        if key in rows:
            fail(f"{path}:{line_no}: duplicate summary row {key}")
        try:
            rows[key] = {column: int(value) for column, value in zip(header[2:], cells[2:])}
        except ValueError:
            fail(f"{path}:{line_no}: summary values must be integers")
    expected_keys = {(profile, impl) for profile in ("U64", "S64") for impl in IMPLEMENTATIONS}
    if set(rows) != expected_keys:
        fail(f"{path}: summary rows mismatch; missing={sorted(expected_keys-set(rows))}, extra={sorted(set(rows)-expected_keys)}")
    return rows


def validate_summary_table(text: str, rows, path: Path) -> None:
    summary = parse_summary_table(text, path)
    counts = computed_counts(rows)
    for (profile, impl), values in summary.items():
        expected = {status: counts[(profile, impl)][status] for status in STATUS_COLUMNS}
        expected["行数"] = sum(1 for row_profile, _ in rows if row_profile == profile)
        if values != expected:
            fail(f"{path}: summary mismatch for {profile}/{impl}: expected {expected}, got {values}")


def validate_narrative_totals(coverage_text: str, audit_text: str) -> None:
    counts = {"U64": len(U64_IDS), "S64": len(S64_IDS), "total": len(U64_IDS) + len(S64_IDS), "dedup": deduplicated_requirement_count()}
    patterns = {
        "U64": r"RVA23U64 必选 profile 行：\*\*(\d+)\*\*",
        "S64": r"RVA23S64 必选 profile 行：\*\*(\d+)\*\*",
        "total": r"Profile 行总数：\*\*(\d+)\*\*",
        "dedup": r"去重规范要求数：\*\*(\d+)\*\*",
    }
    for key, pattern in patterns.items():
        found = re.search(pattern, coverage_text)
        if not found or int(found.group(1)) != counts[key]:
            fail(f"{COVERAGE}: narrative {key} total must be {counts[key]}")
    for phrase, expected in ((f"U64 {counts['U64']} 行", counts["U64"]), (f"S64 {counts['S64']} 行", counts["S64"]), (f"合计 {counts['total']} 个 profile 行", counts["total"]), (f"去重总数为 {counts['dedup']}", counts["dedup"])):
        if phrase not in audit_text:
            fail(f"{AUDIT}: narrative summary missing {phrase}")
    # The prose formula is independently pinned so a silent formula change is surfaced.
    formula = f"{len(U64_IDS)}+1+{len(S64_IDS) - len((U64_IDS & S64_IDS) - {'RV64I'}) - 1}={counts['dedup']}"
    if formula not in audit_text:
        fail(f"{AUDIT}: deduplication formula must include {formula}")


def validate_all(coverage_path: Path, audit_path: Path):
    coverage_text = coverage_path.read_text(encoding="utf-8")
    audit_text = audit_path.read_text(encoding="utf-8")
    rows = validate_inventory(coverage_text)
    validate_summary_table(coverage_text, rows, coverage_path)
    validate_summary_table(audit_text, rows, audit_path)
    validate_narrative_totals(coverage_text, audit_text)
    validate_evidence_links(coverage_text, coverage_path)
    validate_evidence_links(audit_text, audit_path)
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=COVERAGE, help="coverage markdown file")
    parser.add_argument("--audit", type=Path, default=AUDIT, help="audit summary markdown file")
    args = parser.parse_args()
    rows = validate_all(args.coverage, args.audit)
    counts = computed_counts(rows)
    print("valid: true")
    print(f"profile_rows: U64={len(U64_IDS)} S64={len(S64_IDS)} total={len(rows)}")
    print(f"implementation_status_cells: {len(rows) * len(IMPLEMENTATIONS)}")
    print(f"deduplicated_requirements: {deduplicated_requirement_count()}")
    for (profile, impl), counter in sorted(counts.items()):
        print(f"{profile} {impl}: " + ", ".join(f"{status}={counter[status]}" for status in STATUS_COLUMNS if counter[status]))


if __name__ == "__main__":
    main()
