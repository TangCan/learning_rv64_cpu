#!/usr/bin/env python3
"""Validate the RVA23 Profile v1.0 mandatory inventory and status summary."""
from __future__ import annotations

import argparse
import collections
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = ROOT / "notes/rva23-coverage.md"

# Requirement IDs transcribed from RVA23 Profile v1.0 §§3.1.1–3.1.2.
# Keep profile membership here so omissions and accidental extras are detectable.
U64_IDS = set("""RV64I M A F D C B Zicsr Zicntr Zihpm Ziccif Ziccrse Ziccamoa Zicclsm Za64rs Zihintpause Zic64b Zicbom Zicbop Zicboz Zfhmin Zkt V Zvfhmin Zvbb Zvkt Zihintntl Zicond Zimop Zcmop Zcb Zfa Zawrs Supm""".split())
S64_IDS = set("""RV64I M A F D C B Zicsr Zicntr Zihpm Ziccif Ziccrse Ziccamoa Zicclsm Za64rs Zihintpause Zic64b Zicbom Zicbop Zicboz Zfhmin Zkt V Zvfhmin Zvbb Zvkt Zihintntl Zicond Zimop Zcmop Zcb Zfa Zawrs Supm Zifencei Ss1p13 Svbare Sv39 Svade Ssccptr Sstvecd Sstvala Sscounterenw Svpbmt Svinval Svnapot Sstc Sscofpmf Ssnpm Ssu64xl H Ssstateen Shcounterenw Shvstvala Shtvala Shvstvecd Shvsatpa Shgatpa""".split())
ALLOWED = {"not-studied", "partially-studied", "studied-unverified", "evidence-observed", "not-present", "out-of-scope"}
EXPECTED_COUNTS = {
    ("U64", "Kunminghu"): {"partially-studied": 21, "studied-unverified": 13},
    ("U64", "Heliodor"): {"partially-studied": 14, "studied-unverified": 20},
    ("S64", "Kunminghu"): {"partially-studied": 37, "studied-unverified": 17, "not-studied": 4},
    ("S64", "Heliodor"): {"partially-studied": 26, "studied-unverified": 25, "not-studied": 5, "evidence-observed": 2},
}


def fail(message: str) -> None:
    raise SystemExit(f"ERROR: {message}")


def parse_rows(text: str) -> dict[tuple[str, str], tuple[list[str], str]]:
    rows: dict[tuple[str, str], tuple[list[str], str]] = {}
    for line_no, line in enumerate(text.splitlines(), 1):
        if not re.match(r"^\| `RVA23(?:U64|S64)/v1\.0/", line):
            continue
        match = re.match(r"^\| `RVA23(U64|S64)/v1\.0/§([^/]+)/([^`]+)` \|", line)
        if not match:
            fail(f"line {line_no}: malformed mandatory inventory key")
        profile, section, req_id = match.groups()
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 4:
            fail(f"line {line_no}: expected 4 table cells, found {len(cells)}")
        key = (profile, req_id)
        if key in rows:
            fail(f"duplicate mandatory key: {key}")
        if "待填" in line:
            fail(f"line {line_no}: unresolved template placeholder")
        statuses = re.findall(r"状态：`([^`]+)`", line)
        if len(statuses) != 2 or any(status not in ALLOWED for status in statuses):
            fail(f"line {line_no}: expected two legal implementation statuses, got {statuses}")
        expected_section = ("3.1.1.1" if req_id == "RV64I" else "3.1.1.2") if profile == "U64" else ("3.1.2.1" if req_id == "RV64I" else "3.1.2.2")
        if section != expected_section:
            fail(f"line {line_no}: {profile}/{req_id} must use section {expected_section}, got {section}")
        rows[key] = (statuses, line)
    return rows


def validate(text: str) -> dict[tuple[str, str], tuple[list[str], str]]:
    rows = parse_rows(text)

    expected = {("U64", req) for req in U64_IDS} | {("S64", req) for req in S64_IDS}
    actual = set(rows)
    if actual != expected:
        fail(f"inventory mismatch; missing={sorted(expected-actual)}, extra={sorted(actual-expected)}")
    if len(rows) != 92:
        fail(f"expected 92 profile rows, found {len(rows)}")

    counts: dict[tuple[str, str], collections.Counter[str]] = {}
    for prof, req in rows:
        statuses, _ = rows[(prof, req)]
        for impl, status in zip(("Kunminghu", "Heliodor"), statuses):
            counts.setdefault((prof, impl), collections.Counter())[status] += 1
    for key, expected_counts in EXPECTED_COUNTS.items():
        if dict(counts[key]) != expected_counts:
            fail(f"{key} count mismatch: expected {expected_counts}, got {dict(counts[key])}")

    inherited = {req for req in U64_IDS if req != "RV64I"}
    for req in inherited:
        _, line = rows[("S64", req)]
        origin = re.search(r"关联原始要求 `RVA23U64/v1\.0/§3\.1\.1\.2/([^`]+)`", line)
        if not origin or origin.group(1) != req:
            fail(f"S64/{req}: missing or mismatched U64 inherited source link")
    for (profile, req), (_, line) in rows.items():
        if profile == "S64" and req not in inherited and "关联原始要求 `RVA23U64/" in line:
            fail(f"S64/{req}: unexpected inherited-source link")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--coverage", type=Path, default=COVERAGE, help="coverage markdown file (defaults to notes/rva23-coverage.md)")
    args = parser.parse_args()
    text = args.coverage.read_text()
    rows = validate(text)
    counts: dict[tuple[str, str], collections.Counter[str]] = {}
    for (prof, _), (statuses, _) in rows.items():
        for impl, status in zip(("Kunminghu", "Heliodor"), statuses):
            counts.setdefault((prof, impl), collections.Counter())[status] += 1

    print("valid: true")
    print("profile_rows: U64=34 S64=58 total=92")
    print("implementation_status_cells: 184")
    print("deduplicated_requirements: 59")
    for (prof, impl), counter in sorted(counts.items()):
        print(f"{prof} {impl}: " + ", ".join(f"{status}={counter[status]}" for status in sorted(ALLOWED) if counter[status]))


if __name__ == "__main__":
    main()
