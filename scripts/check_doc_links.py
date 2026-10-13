#!/usr/bin/env python3
"""Check local Markdown links and anchors in the project's learning documents."""
from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCS = (
    ROOT / "notes",
    ROOT / "_agile-output/implementation-artifacts/epic-5-context.md",
    ROOT / "_agile-output/implementation-artifacts/epic-5-start-gate-2026-10-13.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-1-activity-path-and-validation-readiness.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-2-compare-zifencei-fencei.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-3-compare-sstc-timers.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-4-compare-sscofpmf-overflow-filter.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-5-compare-ssnpm-pointer-masking.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-6-compare-ssstateen.md",
    ROOT / "_agile-output/implementation-artifacts/spec-5-7-audit-rva23s64-closeout.md",
)
LINK_RE = re.compile(r"(?<!!)\[([^\]]*)\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+['\"].*?['\"])?\s*\)")
REF_RE = re.compile(r"(?<!!)\[([^\]]+)\]\[([^\]]*)\]")
DEF_RE = re.compile(r"^\s*\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+))", re.MULTILINE)
HTML_LINK_RE = re.compile(r"\b(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", re.IGNORECASE)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
EXPLICIT_ID_RE = re.compile(r"<a\s+(?:[^>]*\s)?id=['\"]([^'\"]+)['\"]\s*[^>]*>|<[^>]+\s+id=['\"]([^'\"]+)['\"]\s*[^>]*>", re.IGNORECASE)


def visible_markdown(text: str, *, strip_inline_code: bool = False) -> str:
    """Remove fenced code so examples are not interpreted as links/headings."""
    out: list[str] = []
    fence: tuple[str, int] | None = None
    for line in text.splitlines():
        match = FENCE_RE.match(line)
        if match:
            marker, tail = match.groups()
            if fence is None:
                if marker[0] == "~" or "`" not in tail:
                    fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not tail.strip():
                fence = None
            out.append("")
        else:
            out.append("" if fence else line)
    visible = "\n".join(out)
    if strip_inline_code:
        # Inline code spans can contain text that resembles links.
        visible = re.sub(r"(?<!`)`+[^`\n]*`+(?!`)", "", visible)
    return visible


def anchor_slug(heading: str) -> str:
    heading = re.sub(r"`([^`]*)`", r"\1", heading)
    heading = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", heading)
    heading = heading.strip().lower()
    # GitHub-style heading anchors retain letters (including CJK), digits,
    # underscores and hyphens; whitespace becomes a hyphen.
    heading = re.sub(r"[^\w\-\s]", "", heading, flags=re.UNICODE)
    return re.sub(r"\s+", "-", heading)


def document_anchors(text: str) -> set[str]:
    text = visible_markdown(text)
    anchors = {a or b for a, b in EXPLICIT_ID_RE.findall(text)}
    counts: Counter[str] = Counter()
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        if not match:
            continue
        slug = anchor_slug(match.group(1))
        if not slug:
            continue
        suffix = counts[slug]
        anchors.add(slug if suffix == 0 else f"{slug}-{suffix}")
        counts[slug] += 1
    return anchors


def links_in_document(text: str):
    text = visible_markdown(text, strip_inline_code=True)
    definitions = {key.strip().lower(): target for key, angle, bare in DEF_RE.findall(text) for target in [angle or bare]}
    found = []
    for match in LINK_RE.finditer(text):
        found.append((match.group(1), match.group(2) or match.group(3), text.count("\n", 0, match.start()) + 1))
    for match in REF_RE.finditer(text):
        ref = (match.group(2) or match.group(1)).strip().lower()
        if ref in definitions:
            found.append((match.group(1), definitions[ref], text.count("\n", 0, match.start()) + 1))
    for match in HTML_LINK_RE.finditer(text):
        found.append((match.group(1), match.group(1), text.count("\n", 0, match.start()) + 1))
    for match in DEF_RE.finditer(text):
        target = match.group(2) or match.group(3)
        found.append((target, target, text.count("\n", 0, match.start()) + 1))
    return found


def display(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def check_document(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        return [f"{display(path)}: cannot read document: {exc}"]
    for _, target, line in links_in_document(text):
        try:
            parsed = urlsplit(target)
        except ValueError as exc:
            errors.append(f"{display(path)}:{line}: invalid target {target}: {exc}")
            continue
        if parsed.scheme or target.startswith("//"):
            continue
        target_path = unquote(parsed.path)
        fragment = unquote(parsed.fragment)
        # The learning notes also use editor-style file:line references.
        line_number = None
        line_match = re.fullmatch(r"(.+?):(\d+)", target_path)
        if line_match:
            target_path, raw_line = line_match.groups()
            line_number = int(raw_line)
        resolved = (path.parent / target_path).resolve() if target_path else path.resolve()
        label = f"{display(path)}:{line}: {target}"
        if not resolved.exists():
            errors.append(f"{label}: target does not exist")
        elif not resolved.is_file() and not resolved.is_dir():
            errors.append(f"{label}: target is not a file or directory")
        elif line_number is not None:
            if not resolved.is_file():
                errors.append(f"{label}: line reference target is not a file")
            else:
                try:
                    line_count = len(resolved.read_text(encoding="utf-8").splitlines())
                except (OSError, UnicodeDecodeError) as exc:
                    errors.append(f"{label}: cannot read line-reference target: {exc}")
                else:
                    if line_number < 1 or line_number > line_count:
                        errors.append(f"{label}: line {line_number} is outside {display(resolved)} ({line_count} lines)")
        elif fragment:
            if not resolved.is_file():
                errors.append(f"{label}: anchor cannot be checked on a directory")
            elif re.fullmatch(r"L\d+", fragment):
                try:
                    line_count = len(resolved.read_text(encoding="utf-8").splitlines())
                except (OSError, UnicodeDecodeError) as exc:
                    errors.append(f"{label}: cannot read line anchor target: {exc}")
                else:
                    line_number = int(fragment[1:])
                    if line_number < 1 or line_number > line_count:
                        errors.append(f"{label}: line anchor #{fragment} is outside {display(resolved)} ({line_count} lines)")
            else:
                try:
                    target_text = resolved.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    errors.append(f"{label}: cannot read anchor target: {exc}")
                else:
                    if fragment not in document_anchors(target_text):
                        errors.append(f"{label}: anchor #{fragment} does not exist in {display(resolved)}")
    return errors


def collect_documents(entries: list[str]) -> list[Path]:
    paths: set[Path] = set()
    for entry in entries:
        path = Path(entry)
        path = path if path.is_absolute() else ROOT / path
        if path.is_dir():
            paths.update(item for item in path.rglob("*.md") if item.is_file())
        else:
            paths.add(path)
    return sorted(paths)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("documents", nargs="*", help="Markdown files/directories; defaults to the learning docs")
    args = parser.parse_args(argv)
    documents = collect_documents(args.documents or [str(path) for path in DEFAULT_DOCS])
    errors = [error for doc in documents for error in check_document(doc)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        print(f"invalid: {len(errors)} broken local link(s) across {len(documents)} document(s)")
        return 1
    print(f"valid: {len(documents)} document(s); all supported local targets and anchors exist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
