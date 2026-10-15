from __future__ import annotations

import hashlib
import importlib.util
import json
import pathlib
import shutil
import sys
import tempfile
from types import SimpleNamespace

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "experiments/heliodor-smoke/run.py"
SPEC = importlib.util.spec_from_file_location("heliodor_smoke_runner", RUNNER_PATH)
assert SPEC and SPEC.loader
runner = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = runner
SPEC.loader.exec_module(runner)
BUILD_SPEC = importlib.util.spec_from_file_location(
    "heliodor_ssnpm_fixture_builder", ROOT / "experiments/ssnpm/build_heliodor_fixtures.py")
assert BUILD_SPEC and BUILD_SPEC.loader
fixture_builder = importlib.util.module_from_spec(BUILD_SPEC)
BUILD_SPEC.loader.exec_module(fixture_builder)


def test_success_requires_cpu_start_exact_registers_pass_and_zero_exit() -> None:
    output = ("[test_smoke] cy=5000 x10=0007 x11=000b commit=1651\n"
              "[test_smoke] x12=004d x13=000b\n[test_smoke] PASS\n"
              "v4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")
    assert runner.observe(output, 0) == (
        True, {"x10": 7, "x11": 11, "x12": 77, "x13": 11,
               "arch_tohost": 1, "arch_pass": 1}, True, False)


def test_sscofpmf_success_requires_arch_cpu_marker_and_pass_output() -> None:
    smoke = ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\n"
             "[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n")
    assert runner.observe(smoke + "sscofpmf tohost=00000001 pass=1\nsscofpmf PASS\n",
                          0, "sscofpmf") == (
                              True, {"x10": 7, "x11": 11, "x12": 77, "x13": 11,
                                     "arch_tohost": 1, "arch_pass": 1}, True, False)
    assert runner.observe(smoke, 0, "sscofpmf") == (
        False, {"x10": 7, "x11": 11, "x12": 77, "x13": 11}, False, False)
    assert runner.observe(smoke + "sscofpmf tohost=00000220 pass=0\n",
                          1, "sscofpmf") == (
                              True, {"x10": 7, "x11": 11, "x12": 77, "x13": 11,
                                     "arch_tohost": 0x220, "arch_pass": 0}, False, True)


def test_arch_marker_with_idle_tohost_does_not_prove_cpu_start() -> None:
    assert runner.observe("sscofpmf tohost=00000000 pass=0\n", 1, "sscofpmf") == (
        False, {"arch_tohost": 0, "arch_pass": 0}, False, False)


def test_idle_arch_result_after_a_passing_smoke_is_blocked_not_a_dut_failure() -> None:
    output = ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\n"
              "[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"
              "v4 rv64ui-add tohost=00000000 pass=0\n")
    started, _values, passed, failed = runner.observe(output, 0)
    assert started and not passed and not failed


def test_ssnpm_u_mode_fixture_checks_controls_and_access_result() -> None:
    source = (ROOT / "experiments/ssnpm/build_heliodor_fixtures.py").read_text(encoding="utf-8")
    fixture = runner.ROOT / "experiments/ssnpm/heliodor/pmlen7-tagged.S"
    generated = fixture.read_text(encoding="utf-8")
    assert fixture_builder.CASES == ("pmlen0-canonical", "pmlen0-tagged", "pmlen7-canonical", "pmlen7-tagged", "pmlen7-bit56")
    assert "csrw senvcfg, t0" in generated and "csrr t1, senvcfg" in generated
    assert "mret" in generated and "u_entry:" in generated
    assert "sd t3, 0(t0)" in generated and "ld t2, 0(t0)" in generated
    assert "ssnpm-case" in (ROOT / "experiments/heliodor-smoke/run.py").read_text(encoding="utf-8")

    output = ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\n"
              "[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"
              "ssnpm pmlen7-tagged tohost=00000001 pass=1\nssnpm pmlen7-tagged PASS\n")
    label = "ssnpm pmlen7-tagged"
    assert runner.observe(output, 0, label) == (
        True, {"x10": 7, "x11": 11, "x12": 77, "x13": 11,
               "arch_tohost": 1, "arch_pass": 1}, True, False)
    assert runner.expected_arch_marker(label, ssnpm_case="pmlen7-tagged") == f"{label} PASS"


def test_ssnpm_expected_fault_requires_tagged_load_cause_pc_and_value() -> None:
    expected_fault = fixture_builder.assembly("pmlen0-tagged")
    assert "tagged_load:\n    ld t2, 0(t0)\n    li t5, 0x12\n    j report_fail" in expected_fault
    assert "li t1, 5\n    bne t0, t1, trap_failure" in expected_fault
    assert "la t2, tagged_load\n    csrr t3, mepc\n    bne t2, t3, trap_failure" in expected_fault
    assert "csrr t3, mtval\n    bne t2, t3, trap_failure" in expected_fault
    boundary = fixture_builder.assembly("pmlen7-bit56")
    assert "li t1, 0x0100000000000000" in boundary
    assert "li t0, 2" in boundary

    label = "ssnpm pmlen0-tagged"
    smoke = "[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"
    pass_output = smoke + f"{label} tohost=00000001 pass=1\n{label} PASS\n"
    unexpected_success = smoke + f"{label} tohost=00000012 pass=0\n"
    assert runner.observe(pass_output, 0, label)[2] is True
    assert runner.observe(unexpected_success, 1, label)[2:] == (False, True)


def test_sscofpmf_run_metadata_expects_arch_marker() -> None:
    assert runner.expected_arch_marker("sscofpmf", sscofpmf=True) == "sscofpmf PASS"
    assert runner.expected_arch_marker("v4 rv64ui-fence_i", zifencei_case=True) == "v4 rv64ui-fence_i PASS"
    assert runner.expected_arch_marker("v4 rv64ui-add") == "[test_smoke] PASS"


def test_sscofpmf_observation_keeps_partial_s_filter_evidence_separate() -> None:
    observed = runner.sscofpmf_observed_values("mode-filters", {"arch_tohost": 21}, False)
    assert observed["partial_observations"]["S with SINH=1"].startswith("counter read was zero")
    assert observed["unverified"] == ["S with SINH=0", "U with UINH=1", "U with UINH=0"]
    observed = runner.sscofpmf_observed_values("mode-filters", {"arch_tohost": 54}, False)
    assert observed["partial_observations"]["S with SINH=0"] == "counter read was nonzero"
    assert observed["partial_observations"]["U with UINH=0"] == "counter read was zero; expected nonzero"
    observed = runner.sscofpmf_observed_values("mode-filters", {"arch_tohost": 20}, False)
    assert observed["filter_assertions"]["S/SINH=1 counter remained zero"] is True
    assert observed["filter_assertions"]["S/SINH=0 counter advanced"] is False
    assert observed["filter_assertions"]["U/UINH=1 counter remained zero"] is True
    assert observed["filter_assertions"]["U/UINH=0 counter advanced"] is False
    assert runner.sscofpmf_observed_values("hardware-overflow", {"arch_tohost": 34}, False) is None


@pytest.mark.parametrize("case,budget", [("hardware-overflow", 200000), ("mode-filters", 1000000)])
def test_run_selects_sscofpmf_fixture_target_and_marker(tmp_path: pathlib.Path,
                                                       monkeypatch: pytest.MonkeyPatch,
                                                       case: str, budget: int) -> None:
    source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    args.sscofpmf_case = case
    fixture_rel, source_rel = runner.SSCOFPMF_FIXTURES[args.sscofpmf_case]
    fixture = runner.ROOT / fixture_rel
    fixture.parent.mkdir(parents=True)
    fixture.write_text("00000013\n", encoding="ascii")
    (runner.ROOT / source_rel).write_text("fixture source\n", encoding="utf-8")
    (runner.ROOT / runner.SSCOFPMF_LINKER).write_text("fixture linker\n", encoding="utf-8")
    args.topic = "sscofpmf"
    calls = []
    outputs = iter([
        (0, b"[test_smoke] cy=5000 x10=7 x11=b commit=1\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n", b"", ""),
        (0, b"sscofpmf tohost=00000001 pass=1\nsscofpmf PASS\n", b"", ""),
    ])

    def execute(command, work, timeout):
        calls.append(command)
        return next(outputs)

    monkeypatch.setattr(runner, "execute_test", execute)
    record = runner.run(args)
    assert calls[1][-1] == "test_arch_sscofpmf"
    transformed = (args.archive_dir / record["id"] / "test_arch_common.veryl").read_text(encoding="utf-8")
    assert f'HEX_FILE  : "{fixture_rel}"' in transformed
    assert f"clk.next ({budget});" in transformed or f"clk.next  ({budget});" in transformed
    assert record["expected_marker"] == "sscofpmf PASS"
    assert record["result"] == "run-pass"
    assert record["case"] == case


def test_run_blocks_when_arch_target_reports_only_idle_tohost(tmp_path: pathlib.Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    _source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    args.topic = "sscofpmf"
    args.sscofpmf_case = "mode-filters"
    (runner.ROOT / runner.SSCOFPMF_FIXTURES["mode-filters"][0]).parent.mkdir(parents=True)
    (runner.ROOT / runner.SSCOFPMF_FIXTURES["mode-filters"][0]).write_text("00000013\n")
    (runner.ROOT / runner.SSCOFPMF_FIXTURES["mode-filters"][1]).write_text("fixture\n")
    (runner.ROOT / runner.SSCOFPMF_LINKER).write_text("linker\n")
    outputs = iter([
        (0, b"[test_smoke] cy=5000 x10=7 x11=b commit=1\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n", b"", ""),
        (0, b"sscofpmf tohost=00000000 pass=0\n", b"", ""),
    ])
    monkeypatch.setattr(runner, "execute_test", lambda *_args: next(outputs))
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert not record["cpu_started"] and not record["assertion_failed"]


def test_combined_passing_smoke_and_idle_arch_target_records_blocked(tmp_path: pathlib.Path,
                                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    _source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    outputs = iter([
        (0, b"[test_smoke] cy=5000 x10=7 x11=b commit=1\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n", b"", ""),
        (0, b"v4 rv64ui-add tohost=00000000 pass=0\n", b"", ""),
    ])
    monkeypatch.setattr(runner, "execute_test", lambda *_args: next(outputs))
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert record["cpu_started"] and not record["assertion_failed"]


def test_heliodor_sscofpmf_mode_fixture_checks_s_and_u_filters() -> None:
    source = (ROOT / runner.SSCOFPMF_FIXTURES["mode-filters"][1]).read_text(encoding="utf-8")
    assert "SINH" in source and "UINH" in source
    assert "slli    t1, t1, 61" in source and "slli    t1, t1, 60" in source
    assert "li      t0, 0x800" in source and "mret" in source
    assert "s_inhibit_ok" in source and "s_enabled_ok" in source
    assert "u_inhibit_ok" in source and "u_enabled_ok" in source
    assert "matrix_fail" in source and "failure bits" in source


def test_heliodor_sscofpmf_mode_case_gets_longer_cycle_budget() -> None:
    source = (ROOT / "sources/heliodor/tb/test_arch_common.veryl").read_text(encoding="utf-8")
    transformed = runner.transform_arch_harness(
        source, target="test_arch_sscofpmf", fixture="experiments/sscofpmf/heliodor-sscofpmf-mode-filters.hex",
        label="sscofpmf", arch_cycles=1_000_000)
    assert "clk.next  (1000000);" in transformed


def test_sscofpmf_fixture_does_not_software_set_of_and_bounds_unsupported_filters() -> None:
    fixture = (ROOT / "sources/heliodor/test/sscofpmf/sscofpmf_test.S").read_text(encoding="utf-8")
    csr = (ROOT / "sources/heliodor/src/core/csr.veryl").read_text(encoding="utf-8")
    assert "event 5, OF clear" in fixture
    assert "csrw    MHPMEVENT3, t0" in fixture
    assert "slli    t5, t5, 63" not in fixture.split("# ===== B. overflow", 1)[0]
    filter_logic = csr.split("let inhibit", 1)[1].split("let ev_hit", 1)[0]
    assert "ev_sel[62]" in filter_logic and "ev_sel[61]" in filter_logic and "ev_sel[60]" in filter_logic
    assert "ev_sel[59]" not in filter_logic and "ev_sel[58]" not in filter_logic


@pytest.mark.parametrize("output,code,expected_failed", [
    ("[test_smoke] PASS", 0, False),  # marker without evidence CPU started
    ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] PASS\nx12=4c x13=b", 0, True),
    ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\nx12=4d x13=b", 0, True),
    ("[test_smoke] cy=5000 x10=7 x11=b commit=1651\nx12=4d x13=b\n[test_smoke] PASS", 1, False),
    ("[INFO ] Executing test (test_smoke)\n[test_smoke] PASS", 0, False),  # harness start alone is not CPU start
])
def test_missing_or_wrong_result_never_passes(output: str, code: int, expected_failed: bool) -> None:
    started, _values, passed, failed = runner.observe(output, code)
    assert not passed
    assert failed is expected_failed


def test_transform_adds_only_the_single_local_lint_allow() -> None:
    text = f"module smoke {{\n{runner.IMEM_DECL}\n}}\n"
    transformed = runner.transform_testbench(text)
    assert transformed == text.replace(runner.IMEM_DECL,
                                       "    #[allow(initial_assign)]\n" + runner.IMEM_DECL, 1)
    with pytest.raises(ValueError, match="declaration drifted"):
        runner.transform_testbench("module smoke {}\n")
    with pytest.raises(ValueError, match="declaration drifted"):
        runner.transform_testbench(text.replace(runner.IMEM_DECL, runner.IMEM_DECL + "\n" + runner.IMEM_DECL))


def test_arch_transform_keeps_normal_harness_and_one_target_only() -> None:
    source = ("module normal {\n" + runner.ARCH_DRAM_DECL + "\n}\n" +
              runner.ARCH_DEBUG_MARKER + "\nmodule debug_variant {}\n" +
              runner.ARCH_TARGET_MARKER + " {\n  inst h: normal;\n}\n\n" +
              "#[test(test_arch_other)]\nmodule other {}\n")
    transformed = runner.transform_arch_harness(source)
    assert runner.ARCH_DRAM_DECL in transformed
    assert "#[allow(initial_assign)]\n" + runner.ARCH_DRAM_DECL in transformed
    assert "debug_variant" not in transformed
    assert "test_arch_other" not in transformed
    assert transformed.count(runner.ARCH_TARGET_MARKER) == 1
    with pytest.raises(ValueError, match="boundary/DRAM declaration drifted"):
        runner.transform_arch_harness(source.replace(runner.ARCH_DEBUG_MARKER, "missing boundary"))


def test_sha256_tracks_fixture_mutation(tmp_path: pathlib.Path) -> None:
    fixture = tmp_path / "fixture.hex"
    fixture.write_text("00000013\n", encoding="ascii")
    before = runner.sha256(fixture)
    fixture.write_text("00000033\n", encoding="ascii")
    assert runner.sha256(fixture) != before
    assert len(before) == hashlib.sha256(b"00000013\n").digest_size * 2
    source_copy = tmp_path / "source"
    source_copy.mkdir()
    tracked = source_copy / "src.veryl"
    tracked.write_text("module source {}\n", encoding="utf-8")
    source_before = runner.tree_sha256(source_copy)
    tracked.write_text("module changed {}\n", encoding="utf-8")
    assert runner.tree_sha256(source_copy) != source_before
    without_git = runner.tree_sha256(source_copy)
    (source_copy / ".git").mkdir()
    (source_copy / ".git/config").write_text("repository-local metadata\n", encoding="utf-8")
    assert runner.tree_sha256(source_copy) == without_git


def test_isolated_input_hash_covers_source_and_configuration(tmp_path: pathlib.Path) -> None:
    source = tmp_path / "src/core.veryl"
    source.parent.mkdir()
    source.write_text("module core {}\n", encoding="utf-8")
    for name in ("Veryl.toml", "Veryl.lock", "tb/test_smoke.veryl",
                 "tb/test_arch_common.veryl", "test/v4_smoke.hex", runner.ARCH_FIXTURE):
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture\n", encoding="utf-8")
    before = runner.isolated_inputs_sha256(tmp_path)
    source.write_text("module changed {}\n", encoding="utf-8")
    assert runner.isolated_inputs_sha256(tmp_path) != before


def test_missing_veryl_is_a_preflight_blocker(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner.shutil, "which", lambda _name: None)
    with pytest.raises(FileNotFoundError, match="veryl is not on PATH"):
        runner.tool_metadata()


def test_veryl_binary_hash_and_version_are_enforced(tmp_path: pathlib.Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    binary = tmp_path / "veryl"
    binary.write_bytes(b"pinned tool")
    digest = runner.sha256(binary)
    monkeypatch.setattr(runner.shutil, "which", lambda _name: str(binary))
    monkeypatch.setattr(runner, "expected_tool", lambda: ("0.22.0", "0" * 64, {}))
    with pytest.raises(ValueError, match="binary SHA-256 mismatch"):
        runner.tool_metadata()
    monkeypatch.setattr(runner, "expected_tool", lambda: ("0.22.0", digest, {}))
    monkeypatch.setattr(runner.subprocess, "run", lambda *a, **kw:
                        SimpleNamespace(returncode=0, stdout="veryl 0.99.0", stderr=""))
    with pytest.raises(ValueError, match="version mismatch"):
        runner.tool_metadata()


def test_tool_metadata_enforces_manifest_verilator_and_cxx_versions(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    binary = tmp_path / "veryl"
    binary.write_bytes(b"pinned tool")
    digest = runner.sha256(binary)
    expected = {"verilator": "5.020 2024-01-01 rev (Debian 5.020-1)",
                "cxx": "g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"}
    monkeypatch.setattr(runner.shutil, "which", lambda _name: str(binary))
    monkeypatch.setattr(runner, "expected_tool", lambda: (runner.VERYl_VERSION.removeprefix("veryl "), digest,
                                                            {"tools": expected}))

    def version_result(command, **_kwargs):
        if command == [str(binary), "--version"]:
            return SimpleNamespace(returncode=0, stdout=runner.VERYl_VERSION, stderr="")
        if command == ["verilator", "--version"]:
            return SimpleNamespace(returncode=0, stdout="Verilator 5.020 2024-01-01 rev (Debian 5.020-1)\n", stderr="")
        return SimpleNamespace(returncode=0, stdout="g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0\n", stderr="")

    monkeypatch.setattr(runner.subprocess, "run", version_result)
    assert runner.tool_metadata()[1]["verilator"].startswith("Verilator 5.020")
    expected["verilator"] = "5.050"
    with pytest.raises(ValueError, match="Verilator version differs from manifest"):
        runner.tool_metadata()


def test_timeout_keeps_partial_output_and_returns_bounded_failure(monkeypatch: pytest.MonkeyPatch,
                                                                  tmp_path: pathlib.Path) -> None:
    def timeout(*_args, **_kwargs):
        raise runner.subprocess.TimeoutExpired("veryl test", 1, output=b"started", stderr=b"partial error")
    monkeypatch.setattr(runner.subprocess, "run", timeout)
    result = runner.execute_test(["veryl", "test", "--test", "test_arch_rv64ui_add"], tmp_path, 1)
    assert result == (124, b"started", b"partial error", "Veryl test_arch_rv64ui_add timed out after 1s")


def test_changed_snapshot_revision_is_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(runner, "validate_manifest", lambda _path: [])
    monkeypatch.setattr(runner, "expected_tool", lambda: ("pinned", "0" * 64,
                    {"snapshot_sha": runner.LOCKED_SHA, "gitlinks": {}}))
    monkeypatch.setattr(runner, "git", lambda *args: "f" * 40 if args == ("rev-parse", "HEAD") else "")
    with pytest.raises(ValueError, match="revision mismatch"):
        runner.verify_source()


def _run_fixture_environment(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch):
    source = tmp_path / "sources/heliodor"
    (source / "src").mkdir(parents=True)
    (source / "src/core.veryl").write_text("module core {}\n", encoding="utf-8")
    (source / "tb").mkdir()
    (source / "tb/test_smoke.veryl").write_text(
        f"module smoke {{\n{runner.IMEM_DECL}\n}}\n", encoding="utf-8")
    (source / "test").mkdir()
    (source / "test/v4_smoke.hex").write_text("00000013\n", encoding="ascii")
    arch_fixture = source / runner.ARCH_FIXTURE
    arch_fixture.parent.mkdir(parents=True)
    arch_fixture.write_text("00000013\n", encoding="ascii")
    (source / "tb/test_arch_common.veryl").write_text(
        "module ordinary_harness {\n    o_tohost: output logic<32>,\n" + runner.ARCH_DRAM_DECL +
        "\n    assign o_tohost = tohost_lo;\n    i_mtime: mtime_ctr,\n}\n" +
        runner.ARCH_DEBUG_MARKER + "\nmodule debug_harness {}\n\n" +
        runner.ARCH_TARGET_MARKER + " {\n    var tohost: logic<32>;\n    var pass: logic;\n" +
        "    inst h: test_arch_common_harness #(HEX_FILE: \"test/riscv-arch-test/build/rv64ui/add.hex\", TOHOST_IDX: 1024,) { o_tohost: tohost, i_mtime: mtime_ctr, };\n" +
        "    clk.next (200000);\n" +
        "    $display (\"v4 rv64ui-add tohost=%h pass=%b\", tohost, pass);\n}\n\n" +
        "#[test(test_arch_next)]\nmodule next_test {}\n", encoding="utf-8")
    (source / "Veryl.toml").write_text("[project]\n", encoding="utf-8")
    (source / "Veryl.lock").write_text("", encoding="utf-8")
    manifest = tmp_path / "manifest.json"
    manifest.write_text(json.dumps({"snapshots": [{"checkout": "sources/heliodor", "runs": [],
        "tools": {"verilator": "5.020 2024-01-01 rev (Debian 5.020-1)",
                  "cxx": "g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"}}]}),
                        encoding="utf-8")
    monkeypatch.setattr(runner, "ROOT", tmp_path)
    monkeypatch.setattr(runner, "SOURCE", source)
    monkeypatch.setattr(runner, "MANIFEST", manifest)
    monkeypatch.setattr(runner, "verify_source", lambda: (runner.LOCKED_SHA, {}))
    monkeypatch.setattr(runner, "tool_metadata", lambda: ("/pinned/veryl", {
        "veryl": "0.22.0; pinned hash", "verilator": "5.020", "cxx": "G++ 13.3.0"}))
    args = SimpleNamespace(stdout=tmp_path / "logs/stdout.log", stderr=tmp_path / "logs/stderr.log",
                           archive_dir=tmp_path / "archive", work_dir=None, timeout=2.0)
    return source, manifest, args


def test_run_records_preflight_tool_blocker(tmp_path: pathlib.Path,
                                           monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    monkeypatch.setattr(runner, "tool_metadata", lambda: (_ for _ in ()).throw(
        FileNotFoundError("veryl is not on PATH")))
    record = runner.run(args)
    saved = json.loads(manifest.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == saved["result"] == "blocked"
    assert not record["cpu_started"]
    assert "veryl is not on PATH" in record["blocker"]


def test_run_timeout_preserves_partial_logs_as_blocked(tmp_path: pathlib.Path,
                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    monkeypatch.setattr(runner, "execute_test", lambda *_args: (
        124, b"partial compile output", b"timeout diagnostic", "Veryl test_smoke timed out after 2s"))
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert "timed out" in record["blocker"]
    assert b"partial compile output" in args.stdout.read_bytes()
    assert b"timeout diagnostic" in args.stderr.read_bytes()
    assert json.loads(manifest.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]["result"] == "blocked"


def test_run_reclassifies_cpu_started_wrong_registers(tmp_path: pathlib.Path,
                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4c x13=b\n"
              b"v4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")
    monkeypatch.setattr(runner, "execute_test", lambda *_args: (0, output, b"", ""))
    record = runner.run(args)
    assert record["result"] == "run-fail"
    assert record["cpu_started"] and record["assertion_failed"]
    assert not record["expected_observed"]
    assert json.loads(manifest.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]["result"] == "run-fail"


def test_run_detects_mutated_fixture_after_cpu_start(tmp_path: pathlib.Path,
                                                    monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"
              b"v4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")

    def mutate_fixture(_command, work, _timeout):
        (work / "test/v4_smoke.hex").write_text("00000033\n", encoding="ascii")
        return 0, output, b"", ""

    monkeypatch.setattr(runner, "execute_test", mutate_fixture)
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert record["infrastructure_blocked"] and not record["assertion_failed"]
    assert record["first_failed_stage"] == "post-run-integrity"
    assert not record["expected_observed"]
    assert "isolated source" in record["blocker"]


def test_run_detects_mutated_isolated_rtl_after_cpu_start(tmp_path: pathlib.Path,
                                                           monkeypatch: pytest.MonkeyPatch) -> None:
    _source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n"
              b"[test_smoke] PASS\nv4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")

    def mutate_rtl(_command, work, _timeout):
        (work / "src/core.veryl").write_text("module changed {}\n", encoding="utf-8")
        return 0, output, b"", ""

    monkeypatch.setattr(runner, "execute_test", mutate_rtl)
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert record["infrastructure_blocked"] and not record["assertion_failed"]
    assert record["first_failed_stage"] == "post-run-integrity"
    assert "isolated source" in record["blocker"]


def test_arch_compile_failure_keeps_the_failed_target_stage(tmp_path: pathlib.Path,
                                                              monkeypatch: pytest.MonkeyPatch) -> None:
    _source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    smoke_output = b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"
    calls = iter([(0, smoke_output, b"", ""), (1, b"compile error\n", b"", "")])
    monkeypatch.setattr(runner, "execute_test", lambda *_args: next(calls))
    record = runner.run(args)
    assert record["result"] == "blocked"
    assert not record["assertion_failed"] and not record["expected_observed"]
    assert record["first_failed_stage"] == "test_arch_rv64ui_add"


def test_manifest_append_preserves_existing_run_records(tmp_path: pathlib.Path,
                                                          monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    payload = json.loads(manifest.read_text(encoding="utf-8"))
    prior = {"id": "prior-run", "result": "blocked"}
    payload["snapshots"][0]["runs"].append(prior)
    manifest.write_text(json.dumps(payload), encoding="utf-8")
    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n"
              b"[test_smoke] PASS\nv4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")
    monkeypatch.setattr(runner, "execute_test", lambda *_args: (0, output, b"", ""))
    record = runner.run(args)
    runs = json.loads(manifest.read_text(encoding="utf-8"))["snapshots"][0]["runs"]
    assert runs == [prior, record]


def test_default_log_paths_follow_collision_suffixed_run_id(tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    _source, _manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    args.stdout = None
    args.stderr = None
    args.archive_dir = tmp_path / "archive"
    run_base = "heliodor-core-20260101T000000Z-1234"
    (args.archive_dir / run_base).mkdir(parents=True)
    monkeypatch.setattr(runner.time, "gmtime", lambda: (2026, 1, 1, 0, 0, 0, 0, 1, 0))
    monkeypatch.setattr(runner.os, "getpid", lambda: 1234)
    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n"
              b"[test_smoke] PASS\nv4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")
    monkeypatch.setattr(runner, "execute_test", lambda *_args: (0, output, b"", ""))
    record = runner.run(args)
    assert record["id"] == run_base + "-2"
    assert record["stdout"].endswith(run_base + "-2.stdout.log")
    assert record["stderr"].endswith(run_base + "-2.stderr.log")


def test_log_write_failure_falls_back_to_archived_logs(tmp_path: pathlib.Path,
                                                        monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    args.stdout = tmp_path / "unwritable" / "stdout.log"
    args.stderr = tmp_path / "unwritable" / "stderr.log"
    real_write = pathlib.Path.write_bytes

    def fail_requested_log(path: pathlib.Path, data: bytes) -> int:
        if "unwritable" in path.parts:
            raise OSError("simulated log destination failure")
        return real_write(path, data)

    output = (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n[test_smoke] x12=4d x13=b\n"
              b"[test_smoke] PASS\nv4 rv64ui-add tohost=00000001 pass=1\nv4 rv64ui-add PASS\n")
    monkeypatch.setattr(pathlib.Path, "write_bytes", fail_requested_log)
    monkeypatch.setattr(runner, "execute_test", lambda *_args: (0, output, b"", ""))
    record = runner.run(args)
    assert record["result"] == "run-pass"
    assert record["log_path_warnings"]
    assert (tmp_path / record["stdout"]).is_file()


def test_actual_locked_arch_harness_smoke_runs_and_is_archived(monkeypatch: pytest.MonkeyPatch) -> None:
    veryl = shutil.which("veryl")
    assert veryl, "add the pinned Story 6.1 Veryl toolchain to PATH before running the regression suite"
    with tempfile.TemporaryDirectory(prefix=".heliodor-smoke-regression-", dir=runner.ROOT) as directory:
        temp = pathlib.Path(directory)
        manifest = temp / "manifest.json"
        manifest.write_text(json.dumps({"snapshots": [{"checkout": "sources/heliodor", "runs": [],
            "tools": {"verilator": "5.020 2024-01-01 rev (Debian 5.020-1)",
                      "cxx": "g++ (Ubuntu 13.3.0-6ubuntu2~24.04.1) 13.3.0"}}]}),
                            encoding="utf-8")
        monkeypatch.setattr(runner, "MANIFEST", manifest)
        monkeypatch.setattr(runner, "verify_source", lambda: (runner.LOCKED_SHA, {}))
        args = SimpleNamespace(stdout=temp / "stdout.log", stderr=temp / "stderr.log",
                               archive_dir=temp / "archive", work_dir=None, timeout=180.0)
        record = runner.run(args)
        assert record["result"] == "run-pass"
        assert record["cpu_started"] and record["expected_observed"]
        assert record["input"].endswith("/rv64ui-add.hex")
        assert record["input_sha256"] == record["inputs"][1]["sha256"]
        archived_output = (runner.ROOT / record["output"]).read_text(encoding="utf-8")
        assert "[test_smoke] PASS" in archived_output
        assert "v4 rv64ui-add tohost=00000001 pass=1" in archived_output
        assert "v4 rv64ui-add PASS" in archived_output
        data = json.loads(manifest.read_text(encoding="utf-8"))
        snapshot = next(item for item in data["snapshots"] if item["checkout"] == "sources/heliodor")
        assert snapshot["runs"][-1]["id"] == record["id"]
        archived_runner = runner.ROOT / record["artifacts"][0]
        assert runner.sha256(archived_runner) == record["artifact_sha256"][record["artifacts"][0]]


def test_sstc_matrix_controls_and_gate_causes_are_complete() -> None:
    assert len(runner.SSTC_CASES) == 14
    assert set(runner.SSTC_CASES) == set(runner.SSTC_CONTROLS)
    for case in ("vs-lt", "vs-eq", "vs-gt"):
        controls = runner.SSTC_CONTROLS[case]
        assert controls["htimedelta"] == "0x10000"
        assert controls["hideleg.VSTIP"] == 1
        assert controls["hcounteren.TM"] == controls["mcounteren.TM"] == 1
    assert runner.SSTC_CONTROLS["vs-hstce-off"]["expected_cause"] == 22
    assert runner.SSTC_CONTROLS["vs-htm-off"]["expected_cause"] == 22
    assert runner.SSTC_CONTROLS["vs-mstce-off"]["expected_cause"] == 2
    assert runner.SSTC_CONTROLS["vs-mtm-off"]["expected_cause"] == 2
    assert runner.SSTC_CONTROLS["vs-route"]["expected_mode"] == "VS"
    assert runner.SSTC_CONTROLS["vs-hs-route"]["expected_mode"] == "HS"


def test_sstc_transform_enables_clock_only_for_fixture() -> None:
    source = (pathlib.Path(__file__).resolve().parents[2] / "sources/heliodor/tb/test_arch_common.veryl").read_text()
    normal = runner.transform_arch_harness(source)
    sstc = runner.transform_arch_harness(
        source, target="test_arch_rv64ui_sstc", fixture="experiments/sstc/heliodor/vs-lt.hex",
        label="sstc vs-lt", mtime_enable=True)
    assert "MTIME_EN: 1'b1" not in normal
    assert "MTIME_EN: 1'b1" in sstc
    assert 'HEX_FILE  : "experiments/sstc/heliodor/vs-lt.hex"' in sstc
    assert "module test_arch_rv64ui_sstc" in sstc


def test_sstc_case_rejects_a_non_sstc_topic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--sstc-case", "s-eq"])
    with pytest.raises(SystemExit) as exc:
        runner.main()
    assert exc.value.code == 2


def test_run_snapshots_repo_fixture_and_records_no_trap_marker(
        tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    _source, manifest, args = _run_fixture_environment(tmp_path, monkeypatch)
    fixture = tmp_path / "experiments/sstc/heliodor/vs-eq.hex"
    fixture.parent.mkdir(parents=True)
    fixture.write_text("deadbeef\n", encoding="ascii")
    args.sstc_case = "vs-eq"
    calls = 0

    def execute(command, *_args):
        nonlocal calls
        calls += 1
        if command[-1] == "test_smoke":
            return 0, (b"[test_smoke] cy=5000 x10=7 x11=b commit=1651\n"
                       b"[test_smoke] x12=4d x13=b\n[test_smoke] PASS\n"), b"", ""
        return 1, b"sstc vs-eq tohost=00000210 pass=0 sample_time=00000029 cmp=00000029 time_after=00000029\n", b"", ""

    monkeypatch.setattr(runner, "execute_test", execute)
    record = runner.run(args)
    assert calls == 2, record.get("blocker")
    saved = json.loads(manifest.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    snapshot = tmp_path / saved["input"]
    assert snapshot.is_file() and snapshot.read_bytes() == fixture.read_bytes()
    assert saved["input_sha256"] == hashlib.sha256(fixture.read_bytes()).hexdigest()
    assert record["result"] == "run-fail" and record["cpu_started"]
    assert record["observed_values"] == {
        "tohost": 0x210, "trap_observed": False, "cause": None, "mode": "VS",
        "pc": "target_access+4; CSR write completed and fallthrough marker executed",
        "sampled_time": 0x29, "comparator": 0x29, "time_after_write": 0x29}
