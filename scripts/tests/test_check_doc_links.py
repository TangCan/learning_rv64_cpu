"""Tests for local document target and anchor validation."""
import importlib.util
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "check_doc_links.py"
spec = importlib.util.spec_from_file_location("check_doc_links", SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)


def test_existing_relative_target_and_heading_anchor_pass(tmp_path):
    target = tmp_path / "target doc.md"
    target.write_text("# Hardware Paths\n\n## `FENCE.I` flow\n", encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text("[doc](target%20doc.md#hardware-paths)\n[flow](target%20doc.md#fencei-flow)\n", encoding="utf-8")
    assert checker.check_document(source) == []


def test_editor_line_references_are_checked(tmp_path):
    target = tmp_path / "code.scala"
    target.write_text("one\ntwo\nthree\n", encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text("[colon line](code.scala:2) [fragment line](code.scala#L3)\n[bad line](code.scala#L4)\n", encoding="utf-8")
    errors = checker.check_document(source)
    assert len(errors) == 1
    assert "line anchor #L4 is outside" in errors[0]


def test_missing_file_and_anchor_report_source_line(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("intro\n[missing](absent.md)\n[bad anchor](#nothing-here)\n", encoding="utf-8")
    errors = checker.check_document(source)
    assert len(errors) == 2
    assert all("source.md:" in item for item in errors)
    assert "target does not exist" in errors[0]
    assert "anchor #nothing-here does not exist" in errors[1]


def test_explicit_duplicate_and_unicode_anchors_pass(tmp_path):
    target = tmp_path / "target.md"
    target.write_text('<a id="custom-anchor"></a>\n# 状态访问\n# Repeated\n# Repeated\n', encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text("[a](target.md#custom-anchor) [b](target.md#状态访问) [c](target.md#repeated-1)\n", encoding="utf-8")
    assert checker.check_document(source) == []


def test_external_links_and_code_examples_are_ignored(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("[external](https://example.com/x)\n`[inline](missing.md)`\n```md\n[example](missing.md)\n```\n", encoding="utf-8")
    assert checker.check_document(source) == []


def test_fence_closing_marker_must_match_length_and_have_no_info_string(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("````md\n```text\n[inside](missing.md)\n````\n[real](missing.md)\n", encoding="utf-8")
    errors = checker.check_document(source)
    assert len(errors) == 1
    assert "[real]" not in errors[0]
    assert "missing.md" in errors[0]


def test_reference_and_html_links_are_checked(tmp_path):
    target = tmp_path / "target.md"
    target.write_text("# Section\n", encoding="utf-8")
    source = tmp_path / "source.md"
    source.write_text('[reference][target]\n[target]: target.md#section\n<a href="missing.html">link</a>\n', encoding="utf-8")
    errors = checker.check_document(source)
    assert len(errors) == 1
    assert "missing.html" in errors[0]


def test_cli_returns_nonzero_for_missing_document(tmp_path, capsys):
    result = checker.main([str(tmp_path / "missing.md")])
    assert result == 1
    assert "cannot read document" in capsys.readouterr().err


def test_cli_reports_supported_success_scope(tmp_path, capsys):
    source = tmp_path / "source.md"
    source.write_text("# Section\n", encoding="utf-8")
    assert checker.main([str(source)]) == 0
    assert "all supported local targets and anchors exist" in capsys.readouterr().out


def test_invalid_utf8_document_is_reported_without_traceback(tmp_path):
    source = tmp_path / "invalid.md"
    source.write_bytes(b"# bad\n\xff")
    errors = checker.check_document(source)
    assert len(errors) == 1
    assert "cannot read document" in errors[0]


def test_malformed_url_is_reported_without_traceback(tmp_path):
    source = tmp_path / "source.md"
    source.write_text("[broken](http://[::1)\n", encoding="utf-8")
    errors = checker.check_document(source)
    assert len(errors) == 1
    assert "invalid target" in errors[0]

