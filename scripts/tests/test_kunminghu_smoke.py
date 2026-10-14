import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import sys
import subprocess
import datetime as dt
import tempfile
import threading
import types

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[2]
RUNNER_PATH = ROOT / "experiments/kunminghu-smoke/run.py"
spec = importlib.util.spec_from_file_location("kunminghu_smoke_runner", RUNNER_PATH)
runner = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = runner
spec.loader.exec_module(runner)

sys.path.insert(0, str(ROOT / "scripts"))
from run_cpu_smoke import validate_record
import run_cpu_smoke


def test_success_requires_image_commit_and_good_trap():
    output = ("The image is fixture.bin\n" + runner.FIRST_COMMIT
              + "\n[01] commit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x8000002c")
    result = runner.classify_output(output, 0,
                                   expected_start_pc=0x80000000,
                                   expected_trap_pc=0x8000002c)
    assert result["result"] == "run-pass"
    assert result["cpu_started"] is True
    assert result["expected_observed"] is True


def test_missing_first_commit_is_blocked():
    output = "The image is fixture.bin\n" + runner.GOOD_TRAP
    result = runner.classify_output(output, 0)
    assert result["result"] == "blocked"
    assert result["cpu_started"] is False


def test_start_marker_is_required_for_expected_observation():
    output = ("The image is fixture.bin\ncommit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x80000010")
    result = runner.classify_output(output, 0, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x80000010)
    assert result["result"] == "blocked"
    assert result["expected_observed"] is False


def test_started_without_good_marker_is_run_fail():
    output = "The image is fixture.bin\n" + runner.FIRST_COMMIT
    result = runner.classify_output(output, 0)
    assert result["result"] == "run-fail"
    assert result["assertion_failed"] is True


def test_badtrap_is_run_fail():
    output = "The image is fixture.bin\n" + runner.FIRST_COMMIT + "\n" + runner.BAD_TRAP
    assert runner.classify_output(output, 1)["result"] == "run-fail"


def test_timeout_after_cpu_start_is_run_fail():
    output = "The image is fixture.bin\n" + runner.FIRST_COMMIT
    result = runner.classify_output(output, 124, timed_out=True)
    assert result["result"] == "run-fail"
    assert result["blocker"]


def test_process_timeout_preserves_partial_output(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs.get("timeout"),
                                        output=b"partial stdout", stderr=b"partial stderr")
    monkeypatch.setattr(runner.subprocess, "run", timeout)
    code, stdout, stderr, timed_out = runner._run(["emu"], ROOT, timeout=0.1)
    assert (code, stdout, stderr, timed_out) == (124, "partial stdout", "partial stderr", True)


def test_process_invalid_utf8_is_preserved_with_replacement():
    code, stdout, stderr, timed_out = runner._run(
        [sys.executable, "-c", "import os; os.write(1, b'\\xff'); os.write(2, b'\\xfe')"], ROOT)
    assert code == 0
    assert stdout == "\ufffd"
    assert stderr == "\ufffd"
    assert timed_out is False


def test_good_marker_at_unexpected_pc_is_run_fail():
    output = "The image is fixture.bin\n" + runner.FIRST_COMMIT + "\n" + runner.GOOD_TRAP + " at pc = 0xe"
    result = runner.classify_output(output, 0, expected_trap_pc=0x8000002c)
    assert result["result"] == "run-fail"
    assert "does not match linked marker" in result["blocker"]


def test_critical_error_cannot_be_counted_as_success():
    output = ("The image is fixture.bin\n" + runner.FIRST_COMMIT
              + "\ncommit pc 0000000080000000\nHIT CRITICAL ERROR\n"
              + runner.GOOD_TRAP + " at pc = 0x8000002c")
    result = runner.classify_output(output, 0, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x8000002c)
    assert result["result"] == "run-fail"


def test_abort_cannot_be_counted_as_success():
    output = ("The image is fixture.bin\n" + runner.FIRST_COMMIT
              + "\ncommit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x80000010\nABORT at pc = 0x80000014")
    result = runner.classify_output(output, 0, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x80000010)
    assert result["result"] == "run-fail"
    assert result["expected_observed"] is False


def test_missing_tools_and_simulator_are_reported():
    missing = runner.missing_dependencies(None, None, pathlib.Path("no-emu"), pathlib.Path("no-nemu"))
    assert "riscv64-unknown-elf-gcc" in missing
    assert "riscv64-unknown-elf-objcopy" in missing
    assert "no-emu" in missing
    assert "no-nemu" in missing


def test_manifest_log_and_artifact_hashes_must_match(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][1]["runs"][1].copy()
    changed = tmp_path / "tampered.log"
    changed.write_text("tampered transcript", encoding="utf-8")
    record.update(output=str(changed), stdout=str(changed), stderr=str(changed))
    artifact = tmp_path / "artifact.bin"
    artifact.write_bytes(b"changed artifact")
    record["artifacts"] = [str(artifact)]
    record["artifact_sha256"] = {str(artifact): hashlib.sha256(b"original artifact").hexdigest()}
    errors = validate_record(record, "kunminghu-test")
    assert sum("SHA-256 mismatch" in error for error in errors) == 4


def test_fixture_links_at_ram_base_and_declares_start():
    source = (ROOT / "experiments/kunminghu-smoke/fixture.S").read_text(encoding="utf-8")
    linker = (ROOT / "experiments/kunminghu-smoke/fixture.ld").read_text(encoding="utf-8")
    assert ".globl _start" in source
    assert "ENTRY(_start)" in linker
    assert "0x80000000" in linker


def test_sstc_matrix_sources_cover_all_supported_cases_and_permission_macros():
    source = (ROOT / "experiments/sstc/kunminghu-full-matrix.S").read_text(encoding="utf-8")
    assert runner.SSTC_SOURCE == ROOT / "experiments/sstc/kunminghu-full-matrix.S"
    assert runner.SSTC_SOURCE.is_file()
    for case in runner.SSTC_CASES:
        assert f"CASE_{case.upper().replace('-', '_')}" in source
    assert "csrw pmpcfg0, t0" in source
    assert "csrw menvcfg, zero" in source
    assert "csrw mcounteren, zero" in source
    assert "csrw 0x14d, t1" in source
    assert "bne t0, t1, fail" in source


def test_sscofpmf_fixture_covers_all_five_filters_and_hardware_overflow():
    source = runner.SSCOFPMF_SOURCE.read_text(encoding="utf-8")
    assert runner.SSCOFPMF_SOURCE.is_file()
    for field in ("MINH", "SINH", "UINH", "VSINH", "VUINH"):
        assert field in source
    assert "FILTER_CASE s_filter" in source
    assert "FILTER_CASE u_filter" in source
    assert "FILTER_CASE vs_filter" in source
    assert "FILTER_CASE vu_filter" in source
    assert "csrw    mhpmcounter3, t0" in source
    assert "mcause" in source and "0x800000000000000d" in source
    assert "mhpmevent3" in source and "scountovf" in source
    assert "srli    t0, t0, 63" in source  # read mhpmevent3.OF in the trap
    assert "clear_and_rearm:" in source
    assert "csrr    t0, mip" in source
    assert "csrw    mhpmcounter3, t0           /* next OF must come from a hardware event */" in source


def test_sscofpmf_access_route_fixture_checks_scounter_gates_and_delegation():
    source = runner.SSCOFPMF_ACCESS_SOURCE.read_text(encoding="utf-8")
    assert "csrr    t0, scountovf" in source
    assert "csrw    mcounteren, zero" in source
    assert "csrw    hcounteren, zero" in source
    assert "csrw    mideleg, t0" in source
    assert "csrw    sie, t0" in source
    assert "csrr    t0, sstatus" in source
    assert "csrr    t1, sie" in source
    assert "csrr    t2, sip" in source
    assert "csrw    mcounteren, t0              /* keep scountovf[3] visible in S trap */" in source
    assert "csrs    sstatus, t0" in source
    assert "0x800000000000000d" in source


def test_sscofpmf_fixtures_repeatable_without_official_evidence_writes():
    if os.environ.get("RUN_KUNMINGHU_SSCOFPMF_REGRESSION") != "1":
        pytest.skip("set RUN_KUNMINGHU_SSCOFPMF_REGRESSION=1 to run the locked CPU fixture")
    temp_root = pathlib.Path(tempfile.mkdtemp(prefix=".sscofpmf-regression-", dir=ROOT))
    try:
        manifest = temp_root / "manifest.json"
        shutil.copy2(ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml", manifest)
        expected_cases = {
            "hardware-filter": "five-mode-filter-hardware-wrap-counter3",
            "access-route": "scountovf-access-matrix-and-s-delegation",
        }
        for fixture_case, expected_record_case in expected_cases.items():
            evidence_dir = temp_root / "evidence" / fixture_case
            completed = subprocess.run(
                [sys.executable, str(RUNNER_PATH), "--topic", "sscofpmf",
                 "--sscofpmf-case", fixture_case, "--manifest", str(manifest),
                 "--evidence-dir", str(evidence_dir)],
                cwd=ROOT, capture_output=True, text=True, timeout=180, check=False)
            assert completed.returncode == 0, completed.stdout + completed.stderr
            run_id = next(line.split("=", 1)[1] for line in completed.stdout.splitlines()
                          if line.startswith("run_id="))
            recorded = json.loads(manifest.read_text(encoding="utf-8"))
            runs = [run for snapshot in recorded["snapshots"] for run in snapshot.get("runs", [])
                    if run.get("id") == run_id]
            assert len(runs) == 1
            assert runs[0]["result"] == "run-pass"
            assert runs[0]["expected_observed"] is True
            assert runs[0]["case"] == expected_record_case
    finally:
        shutil.rmtree(temp_root, ignore_errors=True)


def test_ssnpm_fixture_separates_canonical_and_tagged_s_mode_loads():
    source = (ROOT / "experiments/kunminghu-smoke/ssnpm.S").read_text(encoding="utf-8")
    assert "csrw    senvcfg, zero" in source
    assert "csrw    senvcfg, t0" in source
    assert "csrr    t1, senvcfg" in source
    assert "bne     t1, t2, failed" in source
    assert "#ifdef SSNPM_PMLEN7" in source
    assert "#ifdef SSNPM_BIT56" in source
    assert "0x0100000000000000" in source
    assert "0xfe00000000000000" in source
    assert '"pmlen7-bit56"' in (ROOT / "experiments/kunminghu-smoke/run.py").read_text(encoding="utf-8")
    assert "mret" in source and "u_mode:" in source
    assert "ld      t2, 0(t0)" in source
    assert "sd      t3, 0(t0)" in source
    assert "lr.d    t2, (t0)" in source
    assert "sc.d    t4, t3, (t0)" in source
    assert "amoadd.d t2, t3, (t0)" in source
    assert "bne     t2, t3, failed" in source
    assert "tagged_load:" in source
    assert "csrr    t0, mcause" in source and "li      t1, 5" in source
    assert "la      t1, tagged_load" in source and "csrr    t2, mepc" in source
    assert "csrr    t2, mtval" in source
    assert runner.SSNPM_SOURCE.is_file()


def test_sscofpmf_act4_sail_blockers_are_explicit():
    act_dir = ROOT / "sources/heliodor/test/act/config/heliodor"
    sail = (act_dir / "sail.json").read_text(encoding="utf-8")
    assert '"Sscofpmf": {\n      "supported": false' in sail
    act = (act_dir / "heliodor.yaml").read_text(encoding="utf-8")
    assert "name: Sscofpmf" not in act


def test_sscofpmf_topic_is_available_and_misplaced_sstc_controls_are_rejected(monkeypatch):
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--topic", "sscofpmf", "--sstc-case", "s-eq"])
    with pytest.raises(SystemExit) as exc:
        runner.main()
    assert exc.value.code == 2


def test_sstc_cli_requires_a_supported_case_and_topic(monkeypatch):
    for argv in (("--sstc-case", "s-eq"), ("--topic", "sstc")):
        monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), *argv])
        with pytest.raises(SystemExit) as exc:
            runner.main()
        assert exc.value.code == 2


def test_sstc_trace_records_sample_and_comparator_operand():
    trace = ("[1] commit pc 80000010 inst c0102373 wen 1 dst 06 data 0000000000000029 idx 001 (S)\n"
             "[2] commit pc 80000014 inst 00030293 wen 1 dst 05 data 0000000000000029 idx 002\n"
             "[3] commit pc 80000018 inst 00028313 wen 1 dst 06 data 0000000000000029 idx 003\n"
             "[4] commit pc 8000001c inst 14d31073 wen 0 dst 00 data 0000000000000000 idx 004\n"
             + runner.GOOD_TRAP)
    observed = runner.parse_sstc_trace(trace, "s-eq")
    assert observed["sampled_time"] == 0x29
    assert observed["comparator_operand"] == 0x29
    assert observed["sample_relation"] == "=="
    assert observed["pass_marker_observed"]


def _prepare_main(tmp_path, monkeypatch, *, post_run_errors=None, pre_append_errors=None):
    root = tmp_path
    source = root / "experiments/kunminghu-smoke/fixture.S"
    linker = root / "experiments/kunminghu-smoke/fixture.ld"
    checkout = root / "sources/xiangshan"
    emulator = checkout / "build/emu"
    nemu = checkout / "ready-to-run/nemu.so"
    for path, content in ((source, "fixture source\n"), (linker, "fixture linker\n"),
                          (emulator, "emu"), (nemu, "nemu")):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    manifest = root / "manifest.json"
    manifest.write_text(json.dumps({"snapshots": [{"checkout": "sources/xiangshan",
                                                     "tools": {}, "runs": []}]}),
                        encoding="utf-8")
    evidence = root / "evidence dir"
    monkeypatch.setattr(runner, "ROOT", root)
    monkeypatch.setattr(runner, "SOURCE", source)
    monkeypatch.setattr(runner, "LINKER", linker)
    monkeypatch.setattr(runner, "CHECKOUT", checkout)
    monkeypatch.setattr(runner, "EMULATOR", emulator)
    monkeypatch.setattr(runner, "NEMU", nemu)
    monkeypatch.setattr(runner, "_locked_sha", lambda: "c098f996bf4d301b88693b20315486d31e93bc9d")
    monkeypatch.setattr(run_cpu_smoke, "ROOT", root)
    validations = 0

    def validate_manifest(_path):
        nonlocal validations
        validations += 1
        if validations > 1 and post_run_errors:
            return post_run_errors
        if validations > 2 and pre_append_errors:
            return pre_append_errors
        return []

    monkeypatch.setattr(run_cpu_smoke, "validate_manifest", validate_manifest)
    monkeypatch.setattr(runner.shutil, "which", lambda name: f"/tools/{name}")

    def fake_run(command, _cwd, timeout=None):
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        if "-o" in command:
            pathlib.Path(command[command.index("-o") + 1]).write_text("ELF", encoding="utf-8")
            map_arg = next(arg for arg in command if arg.startswith("-Wl,-Map,"))
            map_path = pathlib.Path(map_arg.removeprefix("-Wl,-Map,"))
            map_path.write_text("0x0000000080000000 _start\n0x0000000080000010 good_trap\n",
                                encoding="utf-8")
            return 0, "", "", False
        if "-O" in command:
            pathlib.Path(command[-1]).write_bytes(b"fixture")
            return 0, "", "", False
        image_path = command[command.index("-i") + 1]
        output = (f"The image is {image_path}\n" + runner.FIRST_COMMIT
                  + "\ncommit pc 0000000080000000\n"
                  + runner.GOOD_TRAP + " at pc = 0x80000010\n")
        return 0, output, "", False

    monkeypatch.setattr(runner, "_run", fake_run)

    class FixedDateTime:
        @classmethod
        def now(cls, tz=None):
            return dt.datetime(2026, 10, 14, 4, 32, 11, tzinfo=tz)

    monkeypatch.setattr(runner, "dt", types.SimpleNamespace(datetime=FixedDateTime,
                                                               timezone=dt.timezone))
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(manifest),
                                      "--evidence-dir", str(evidence), "--timeout", "5"])
    return root, manifest, evidence


def _expected_run_id(evidence_dir, suffix=1):
    path_hash = hashlib.sha256(str(evidence_dir.resolve()).encode("utf-8")).hexdigest()[:12]
    base = f"kunminghu-fixture-20261014T043211Z-{path_hash}"
    return base if suffix == 1 else f"{base}-{suffix}"


def test_runner_appends_valid_manifest_record_and_unique_run_ids(tmp_path, monkeypatch, capsys):
    root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)

    assert runner.main() == 0
    first = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert first["id"] == _expected_run_id(evidence)
    assert f"'{evidence}/" in first["command"]
    assert f"--diff {runner.NEMU}" in first["command"]
    assert "binary sha256" in first["tools"]["emulator"]
    assert "binary sha256" in first["tools"]["nemu"]
    assert validate_record(first, "runner test") == []

    assert runner.main() == 0
    runs = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"]
    assert [record["id"] for record in runs] == [
        _expected_run_id(evidence),
        _expected_run_id(evidence, 2),
    ]
    assert all(record["id"] == pathlib.Path(record["output"]).parent.name for record in runs)
    assert (evidence / runs[1]["id"] / "output.log").is_file()


def test_run_id_is_unique_across_different_evidence_directories(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    assert runner.main() == 0
    second_evidence = tmp_path / "other evidence"
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(manifest_path),
                                      "--evidence-dir", str(second_evidence), "--timeout", "5"])
    assert runner.main() == 0
    runs = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"]
    assert len({record["id"] for record in runs}) == 2
    assert runs[1]["id"] == _expected_run_id(second_evidence)
    assert (second_evidence / runs[1]["id"] / "output.log").is_file()


def test_runner_rejects_mismatched_reported_image_path(tmp_path, monkeypatch):
    _root, manifest_path, _evidence = _prepare_main(tmp_path, monkeypatch)
    original_run = runner._run

    def mismatched_image(command, cwd, timeout=None):
        code, output, error, did_timeout = original_run(command, cwd, timeout)
        if "--dump-commit-trace" in command:
            output = output.replace(command[command.index("-i") + 1], "/tmp/other-image.bin")
        return code, output, error, did_timeout

    monkeypatch.setattr(runner, "_run", mismatched_image)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == "run-fail"
    assert record["expected_observed"] is False
    assert "image load not observed" in record["observed"]


def test_post_run_source_validation_failure_cannot_pass(tmp_path, monkeypatch, capsys):
    _root, manifest_path, _evidence = _prepare_main(
        tmp_path, monkeypatch, post_run_errors=["sources/xiangshan: working tree is dirty"])

    assert runner.main() == 1
    run_dir = _evidence / _expected_run_id(_evidence)
    record = json.loads((run_dir / "run-record.json").read_text(encoding="utf-8"))
    assert record["result"] == "run-fail"
    assert record["expected_observed"] is False
    assert "source/manifest integrity" in record["blocker"]
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_pre_append_integrity_failure_reclassifies_standalone_record(tmp_path, monkeypatch, capsys):
    _root, manifest_path, evidence = _prepare_main(
        tmp_path, monkeypatch, pre_append_errors=["sources/xiangshan: changed before append"])

    assert runner.main() == 1
    run_dir = evidence / _expected_run_id(evidence)
    record = json.loads((run_dir / "run-record.json").read_text(encoding="utf-8"))
    transcript = (run_dir / "output.log").read_text(encoding="utf-8")
    assert record["result"] == "run-fail"
    assert record["expected_observed"] is False
    assert "pre-append source/manifest integrity" in transcript
    assert "Restore the locked source" in record["next_environment_change"]
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_linker_script_change_during_run_fails_closed(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    original_run = runner._run

    def changing_linker(command, cwd, timeout=None):
        if "--dump-commit-trace" in command:
            runner.LINKER.write_text("changed linker\n", encoding="utf-8")
        return original_run(command, cwd, timeout)

    monkeypatch.setattr(runner, "_run", changing_linker)
    assert runner.main() == 1
    record = json.loads((evidence / _expected_run_id(evidence) / "run-record.json").read_text(encoding="utf-8"))
    assert record["result"] == "run-fail"
    assert record["first_failed_stage"] == "fixture linker integrity"
    assert "linker script changed" in record["blocker"]


def test_simulator_disappearing_during_hashing_is_recorded(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    original_hash = runner.sha256

    def disappearing_hash(path):
        if path == runner.EMULATOR:
            path.unlink()
        return original_hash(path)

    monkeypatch.setattr(runner, "sha256", disappearing_hash)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == "blocked"
    assert record["first_failed_stage"] == "simulator artifact integrity"
    assert "cannot hash emulator binary" in record["blocker"]


def test_non_finite_or_nonpositive_timeout_is_rejected(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(manifest_path),
                                      "--evidence-dir", str(evidence), "--timeout", "inf"])
    with pytest.raises(SystemExit) as exc:
        runner.main()
    assert exc.value.code == 2
    assert not evidence.exists()


def test_evidence_directory_must_resolve_inside_project(tmp_path, monkeypatch):
    root, manifest_path, _evidence = _prepare_main(tmp_path, monkeypatch)
    outside = root.parent / "outside evidence"
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(manifest_path),
                                      "--evidence-dir", str(outside)])
    with pytest.raises(SystemExit) as exc:
        runner.main()
    assert exc.value.code == 2
    assert not outside.exists()


def test_missing_manifest_preserves_standalone_failure_record(tmp_path, monkeypatch, capsys):
    root, _manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    missing_manifest = root / "missing.json"
    monkeypatch.setattr(run_cpu_smoke, "validate_manifest", lambda _path: ["manifest not found"])
    monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(missing_manifest),
                                      "--evidence-dir", str(evidence), "--timeout", "5"])

    assert runner.main() == 1
    run_dir = evidence / _expected_run_id(evidence)
    standalone = json.loads((run_dir / "run-record.json").read_text(encoding="utf-8"))
    assert standalone["result"] == "blocked"
    assert standalone["first_failed_stage"] == "locked source and manifest preflight"


def test_compile_failure_records_expected_but_missing_artifacts(tmp_path, monkeypatch, capsys):
    _root, manifest_path, _evidence = _prepare_main(tmp_path, monkeypatch)

    def failed_compile(command, _cwd, timeout=None):
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        return 2, "compiler error\n", "", False

    monkeypatch.setattr(runner, "_run", failed_compile)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == "blocked"
    assert record["first_failed_stage"] == "compile and link"
    assert record["resources"]["disk_free_bytes"] > 0
    assert record["resources"]["logical_cpu_count"] >= 1
    assert record["resources"]["build_command_timeout_seconds"] == 120
    assert "compiler/linker" in record["next_environment_change"]
    assert set(record["missing_artifacts"]) >= {
        f"evidence dir/{_expected_run_id(_evidence)}/fixture.elf",
        f"evidence dir/{_expected_run_id(_evidence)}/fixture.map",
        f"evidence dir/{_expected_run_id(_evidence)}/fixture.bin",
    }
    assert validate_record(record, "compile-failure") == []


def test_compile_timeout_records_partial_output_and_stops_pipeline(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    calls = []

    def timed_out_compile(command, _cwd, timeout=None):
        calls.append(command)
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        return 124, "compiler partial stdout\n", "compiler partial stderr\n", True

    monkeypatch.setattr(runner, "_run", timed_out_compile)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    run_dir = evidence / record["id"]
    assert record["result"] == "blocked"
    assert record["first_failed_stage"] == "compile and link"
    assert record["missing_artifacts"]
    assert len(calls) == 4  # three version probes plus compile; no objcopy or CPU run
    assert "compiler partial stdout" in (run_dir / "stdout.log").read_text(encoding="utf-8")
    assert "compiler partial stderr" in (run_dir / "stderr.log").read_text(encoding="utf-8")
    assert validate_record(record, "compile-timeout") == []


def test_manifest_appends_are_serialized_and_atomic(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"snapshots": [{"checkout": "sources/xiangshan",
                                                         "runs": []}]}),
                             encoding="utf-8")
    threads = [threading.Thread(target=runner.append_manifest_record,
                                args=(manifest_path, {"id": f"run-{index}"}))
               for index in range(20)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    runs = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"]
    assert {run["id"] for run in runs} == {f"run-{index}" for index in range(20)}


def test_manifest_append_rejects_duplicate_run_ids(tmp_path):
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"snapshots": [{"checkout": "sources/xiangshan",
                                                         "runs": [{"id": "same-id"}]}]}),
                             encoding="utf-8")
    with pytest.raises(runner.ManifestIntegrityError, match="duplicate run ID"):
        runner.append_manifest_record(manifest_path, {"id": "same-id"})
    runs = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"]
    assert runs == [{"id": "same-id"}]


def test_concurrent_runs_reserve_unique_evidence_directories(tmp_path):
    results = []
    threads = [threading.Thread(target=lambda: results.append(
        runner.create_run_dir(tmp_path, "same-second-run"))) for _ in range(12)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(results) == 12
    assert len({path.name for path in results}) == 12


def test_good_trap_without_image_load_is_rejected():
    output = (runner.FIRST_COMMIT + "\ncommit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x80000010")
    result = runner.classify_output(output, 0, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x80000010,
                                    expected_image="/tmp/fixture.bin")
    assert result["result"] == "run-fail"
    assert result["expected_observed"] is False


def test_unexpected_image_path_is_not_loaded_fixture():
    output = ("The image is /tmp/other.bin\n" + runner.FIRST_COMMIT
              + "\ncommit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x80000010")
    result = runner.classify_output(output, 0, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x80000010,
                                    expected_image="/tmp/fixture.bin")
    assert result["result"] == "run-fail"
    assert result["expected_observed"] is False


def test_good_trap_with_nonzero_exit_is_rejected():
    output = ("The image is /tmp/fixture.bin\n" + runner.FIRST_COMMIT
              + "\ncommit pc 0000000080000000\n"
              + runner.GOOD_TRAP + " at pc = 0x80000010")
    result = runner.classify_output(output, 1, expected_start_pc=0x80000000,
                                    expected_trap_pc=0x80000010,
                                    expected_image="/tmp/fixture.bin")
    assert result["result"] == "run-fail"
    assert result["expected_observed"] is False


def test_missing_lock_file_preserves_standalone_failure_record(tmp_path, monkeypatch, capsys):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    monkeypatch.setattr(runner, "_locked_sha", lambda: (_ for _ in ()).throw(ValueError("missing lock")))

    assert runner.main() == 1
    run_dir = evidence / _expected_run_id(evidence)
    standalone = json.loads((run_dir / "run-record.json").read_text(encoding="utf-8"))
    assert standalone["snapshot_sha"] == "unknown"
    assert standalone["first_failed_stage"] == "locked source and manifest preflight"
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_missing_fixture_source_preserves_standalone_failure_record(tmp_path, monkeypatch, capsys):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    runner.SOURCE.unlink()

    assert runner.main() == 1
    run_dir = evidence / _expected_run_id(evidence)
    standalone = json.loads((run_dir / "run-record.json").read_text(encoding="utf-8"))
    assert standalone["input_sha256"] == "unavailable"
    assert standalone["first_failed_stage"] == "fixture input"
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_fixture_change_during_run_cannot_be_recorded_as_pass(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    source_hash = hashlib.sha256(runner.SOURCE.read_bytes()).hexdigest()

    def changing_run(command, _cwd, timeout=None):
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        if "-o" in command:
            pathlib.Path(command[command.index("-o") + 1]).write_text("ELF", encoding="utf-8")
            map_arg = next(arg for arg in command if arg.startswith("-Wl,-Map,"))
            pathlib.Path(map_arg.removeprefix("-Wl,-Map,")).write_text(
                "0x0000000080000000 _start\n0x0000000080000010 good_trap\n", encoding="utf-8")
            return 0, "", "", False
        if "-O" in command:
            pathlib.Path(command[-1]).write_bytes(b"fixture")
            return 0, "", "", False
        output = (f"The image is {command[command.index('-i') + 1]}\n" + runner.FIRST_COMMIT
                  + "\ncommit pc 0000000080000000\n"
                  + runner.GOOD_TRAP + " at pc = 0x80000010\n")
        runner.SOURCE.write_text("changed during run\n", encoding="utf-8")
        return 0, output, "", False

    monkeypatch.setattr(runner, "_run", changing_run)
    assert runner.main() == 1
    record = json.loads((evidence / _expected_run_id(evidence) / "run-record.json")
                        .read_text(encoding="utf-8"))
    assert record["input_sha256"] == source_hash
    assert record["result"] == "run-fail"
    assert record["first_failed_stage"] == "fixture source integrity"


def test_manifest_append_failure_is_explicit_in_standalone_record(tmp_path, monkeypatch, capsys):
    _root, _manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)

    def fail_append(*_args, **_kwargs):
        raise OSError("disk unavailable")

    monkeypatch.setattr(runner, "append_manifest_record", fail_append)
    assert runner.main() == 1
    standalone = json.loads((evidence / _expected_run_id(evidence) / "run-record.json")
                            .read_text(encoding="utf-8"))
    assert standalone["result"] == "run-pass"
    assert standalone["manifest_persisted"] is False
    assert standalone["manifest_append_error"] == "disk unavailable"


def test_directory_fsync_failure_reports_manifest_record_as_present(tmp_path, monkeypatch, capsys):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    original_fsync = runner.os.fsync
    fsync_calls = 0

    def fail_directory_fsync(fd):
        nonlocal fsync_calls
        fsync_calls += 1
        if fsync_calls == 2:
            raise OSError("directory fsync failed")
        return original_fsync(fd)

    monkeypatch.setattr(runner.os, "fsync", fail_directory_fsync)
    assert runner.main() == 1
    manifest_record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    standalone = json.loads((evidence / _expected_run_id(evidence) / "run-record.json")
                            .read_text(encoding="utf-8"))
    assert manifest_record["result"] == "run-pass"
    assert standalone["result"] == "run-pass"
    assert standalone["manifest_persisted"] is True
    assert standalone["manifest_durable"] is False
    assert standalone["manifest_durability_error"] == "directory fsync failed"
    assert "record is present" in capsys.readouterr().err


def test_artifact_change_under_append_lock_cannot_be_recorded_as_pass(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    validations = 0

    def mutate_during_append(_path):
        nonlocal validations
        validations += 1
        if validations == 3:  # preflight, post-run, then the append-lock validation
            runner.SOURCE.write_text("changed immediately before append\n", encoding="utf-8")
        return []

    monkeypatch.setattr(run_cpu_smoke, "validate_manifest", mutate_during_append)
    assert runner.main() == 1
    record = json.loads((evidence / _expected_run_id(evidence) / "run-record.json")
                        .read_text(encoding="utf-8"))
    assert record["result"] == "run-fail"
    assert record["expected_observed"] is False
    assert "fixture input changed before manifest append" in record["blocker"]
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_log_change_under_append_lock_cannot_be_recorded_as_pass(tmp_path, monkeypatch):
    _root, manifest_path, evidence = _prepare_main(tmp_path, monkeypatch)
    validations = 0

    def mutate_during_append(_path):
        nonlocal validations
        validations += 1
        if validations == 3:
            (evidence / _expected_run_id(evidence) / "output.log").write_text(
                "changed before append\n", encoding="utf-8")
        return []

    monkeypatch.setattr(run_cpu_smoke, "validate_manifest", mutate_during_append)
    assert runner.main() == 1
    record = json.loads((evidence / _expected_run_id(evidence) / "run-record.json")
                        .read_text(encoding="utf-8"))
    assert record["result"] == "run-fail"
    assert "run output changed before manifest append" in record["blocker"]
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"] == []


def test_transient_integrity_failure_is_preserved_with_cpu_failure(tmp_path, monkeypatch):
    _root, manifest_path, _evidence = _prepare_main(tmp_path, monkeypatch)
    validations = 0

    def transient_validation(_path):
        nonlocal validations
        validations += 1
        return ["transient source-integrity error"] if validations == 2 else []

    monkeypatch.setattr(run_cpu_smoke, "validate_manifest", transient_validation)

    def badtrap_run(command, _cwd, timeout=None):
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        if "-o" in command:
            pathlib.Path(command[command.index("-o") + 1]).write_text("ELF", encoding="utf-8")
            map_arg = next(arg for arg in command if arg.startswith("-Wl,-Map,"))
            pathlib.Path(map_arg.removeprefix("-Wl,-Map,")).write_text(
                "0x0000000080000000 _start\n0x0000000080000010 good_trap\n", encoding="utf-8")
            return 0, "", "", False
        if "-O" in command:
            pathlib.Path(command[-1]).write_bytes(b"fixture")
            return 0, "", "", False
        output = (f"The image is {command[command.index('-i') + 1]}\n" + runner.FIRST_COMMIT
                  + "\nHIT BAD TRAP at pc = 0x80000010\n")
        return 1, output, "", False

    monkeypatch.setattr(runner, "_run", badtrap_run)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == "run-fail"
    assert "post-run source/manifest integrity" in record["blocker"]
    assert "transient source-integrity error" in record["blocker"]
    assert "BADTRAP" in record["blocker"]


def test_simulator_binary_change_during_run_cannot_be_recorded_as_pass(tmp_path, monkeypatch):
    _root, manifest_path, _evidence = _prepare_main(tmp_path, monkeypatch)

    def changing_simulator(command, _cwd, timeout=None):
        if command[-1] in ("--version", "--help"):
            return 0, "test tool version\n", "", False
        if "-o" in command:
            pathlib.Path(command[command.index("-o") + 1]).write_text("ELF", encoding="utf-8")
            map_arg = next(arg for arg in command if arg.startswith("-Wl,-Map,"))
            pathlib.Path(map_arg.removeprefix("-Wl,-Map,")).write_text(
                "0x0000000080000000 _start\n0x0000000080000010 good_trap\n", encoding="utf-8")
            return 0, "", "", False
        if "-O" in command:
            pathlib.Path(command[-1]).write_bytes(b"fixture")
            return 0, "", "", False
        runner.EMULATOR.write_text("changed simulator binary", encoding="utf-8")
        output = (f"The image is {command[command.index('-i') + 1]}\n" + runner.FIRST_COMMIT
                  + "\ncommit pc 0000000080000000\n"
                  + runner.GOOD_TRAP + " at pc = 0x80000010\n")
        return 0, output, "", False

    monkeypatch.setattr(runner, "_run", changing_simulator)
    assert runner.main() == 1
    record = json.loads(manifest_path.read_text(encoding="utf-8"))["snapshots"][0]["runs"][0]
    assert record["result"] == "run-fail"
    assert record["first_failed_stage"] == "simulator artifact integrity"
    assert "simulator binary changed during the run" in record["blocker"]


REAL_TOOL_MISSING = runner.missing_dependencies(
    shutil.which("riscv64-unknown-elf-gcc"), shutil.which("riscv64-unknown-elf-objcopy"),
    runner.EMULATOR, runner.NEMU)


def test_real_fixture_arithmetic_passes_and_wrong_sum_fails(monkeypatch):
    assert not REAL_TOOL_MISSING, (
        "provision the locked Kunminghu smoke dependencies before running this suite: "
        + ", ".join(REAL_TOOL_MISSING)
    )
    with tempfile.TemporaryDirectory(prefix=".kunminghu-smoke-test-", dir=ROOT) as temp:
        temp_root = pathlib.Path(temp)
        manifest_path = temp_root / "manifest.json"
        shutil.copy2(ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml", manifest_path)
        evidence_dir = temp_root / "evidence"
        monkeypatch.setattr(sys, "argv", [str(RUNNER_PATH), "--manifest", str(manifest_path),
                                          "--evidence-dir", str(evidence_dir), "--timeout", "120"])

        assert runner.main() == 0
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        snapshot = next(item for item in manifest["snapshots"] if item["checkout"] == "sources/xiangshan")
        good_run = snapshot["runs"][-1]
        assert good_run["result"] == "run-pass"
        assert good_run["expected_good_trap_pc"] == "0x80000010"
        assert runner.GOOD_TRAP in (ROOT / good_run["output"]).read_text(encoding="utf-8")

        wrong_fixture = temp_root / "wrong-sum.S"
        source_text = runner.SOURCE.read_text(encoding="utf-8")
        assert "addi t1, zero, 11" in source_text
        wrong_fixture.write_text(source_text.replace("addi t1, zero, 11", "addi t1, zero, 10"),
                                 encoding="utf-8")
        monkeypatch.setattr(runner, "SOURCE", wrong_fixture)
        assert runner.main() == 1
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        snapshot = next(item for item in manifest["snapshots"] if item["checkout"] == "sources/xiangshan")
        bad_run = snapshot["runs"][-1]
        assert bad_run["result"] == "run-fail"
        assert bad_run["expected_observed"] is False
        assert runner.BAD_TRAP in (ROOT / bad_run["output"]).read_text(encoding="utf-8")
