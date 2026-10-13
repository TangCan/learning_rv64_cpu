"""Acceptance checks for the Story 5.7 evidence summary."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AUDIT = ROOT / "notes/units/rva23s64-closeout-audit-v1.md"


def test_five_topics_map_to_exact_profile_keys_and_both_units():
    text = AUDIT.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| ")]
    expected = {
        "Zifencei": "rva23s64-zifencei-v1.md",
        "Sstc": "rva23s64-sstc-v1.md",
        "Sscofpmf": "rva23s64-sscofpmf-v1.md",
        "Ssnpm": "rva23s64-ssnpm-v1.md",
        "Ssstateen": "rva23s64-ssstateen-v1.md",
    }
    for topic, unit in expected.items():
        matching = [row for row in rows if f"| {topic} |" in row and "RVA23S64/v1.0/§3.1.2.2/" in row]
        assert len(matching) == 1, f"expected one exact profile mapping for {topic}"
        assert unit in matching[0]
        assert "studied-unverified" in matching[0]
    assert "c098f996bf4d301b88693b20315486d31e93bc9d" in text
    assert "94e9c5821c24a8941c3ddc3b76daddc7124a855a" in text


def test_cpu_run_failure_is_distinguished_from_pre_run_blockers():
    text = AUDIT.read_text(encoding="utf-8")
    plan_section = text.split("## 计划案例、结果与范围", 1)[1].split("## 检查器与 sprint 记录", 1)[0]
    topic_rows = [line for line in plan_section.splitlines() if line.startswith("| 5.")]
    assert len(topic_rows) == 5
    assert sum("`run-fail`" in row for row in topic_rows) == 1
    for story in ("5.2", "5.3", "5.4", "5.5"):
        row = next(row for row in topic_rows if row.startswith(f"| {story}："))
        assert "未启动" in row or "未运行" in row
        assert "run-fail" not in row
    assert "没有任何下列单元产生 `run-pass` 的 CPU 行为证据" in plan_section


def test_learning_closeout_does_not_claim_cpu_validation_or_conformance():
    text = AUDIT.read_text(encoding="utf-8")
    conclusion = text.split("## 学习结项决定与自检", 1)[1].split("## 未决项", 1)[0]
    assert "接受本项目的 Epic 5 学习交付，但不接受为 CPU 行为验证完成" in conclusion
    assert "不意味着" in conclusion
    assert "认证" in conclusion
