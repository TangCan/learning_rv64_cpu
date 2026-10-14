import pathlib
import sys
import json

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from run_cpu_smoke import (
    ROOT, ValidationError, classify, validate_manifest, validate_record,
)


def test_missing_fields_are_rejected():
    assert any("missing required fields" in error
               for error in validate_record({}, "sample"))


def test_pre_cpu_failure_is_always_blocked():
    assert classify(cpu_started=False, exit_code=2, assertion_failed=True,
                    expected_observed=False) == "blocked"


def test_post_start_assertion_is_run_fail():
    assert classify(cpu_started=True, exit_code=1, assertion_failed=True,
                    expected_observed=False) == "run-fail"


def test_success_requires_expected_marker():
    assert classify(cpu_started=True, exit_code=0, assertion_failed=False,
                    expected_observed=True) == "run-pass"


def test_started_without_failure_or_marker_is_ambiguous():
    with pytest.raises(ValidationError):
        classify(cpu_started=True, exit_code=1, assertion_failed=False,
                 expected_observed=False)


def test_record_cannot_call_pre_cpu_failure_run_fail():
    record = {
        "snapshot_sha": "a" * 40,
        "input_sha256": "b" * 64,
        "configuration": "test",
        "command": "test",
        "working_directory": ".",
        "tools": {"test": "1"},
        "exit_code": 1,
        "cpu_started": False,
        "result": "run-fail",
        "output": "missing",
        "output_sha256": "c" * 64,
        "artifacts": [],
        "stdout": "missing",
        "stdout_sha256": "c" * 64,
        "stderr": "missing",
        "stderr_sha256": "c" * 64,
        "first_failed_stage": "compile",
        "input": "missing",
        "assertion_failed": False,
        "expected_observed": False,
        "expected": "success marker",
        "observed": "not reached",
        "id": "pre-cpu",
        "blocker": "toolchain compile failed",
        "expected_marker": "success marker",
        "artifact_sha256": {},
    }
    assert any("cannot be classified run-fail" in error
               for error in validate_record(record, "test"))


def test_locked_manifest_and_logs_validate():
    assert validate_manifest(ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml") == []


def test_snapshot_drift_is_reported(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"][0]["snapshot_sha"] = "f" * 40
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    errors = validate_manifest(changed)
    assert any("checkout SHA" in error for error in errors)
    assert any("sources.lock" in error for error in errors)


def test_log_hash_mismatch_is_rejected(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][1]["runs"][0].copy()
    tampered = tmp_path / "tampered.log"
    tampered.write_text("changed transcript", encoding="utf-8")
    for key in ("output", "stdout", "stderr"):
        record[key] = str(tampered)
    errors = validate_record(record, "test")
    assert sum("SHA-256 mismatch" in error for error in errors) == 3


def test_malformed_result_type_is_reported_not_raised():
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][1]["runs"][0].copy()
    record["result"] = []
    assert any("result must be" in error for error in validate_record(record, "test"))


def test_empty_run_list_is_rejected(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"][0]["runs"] = []
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    assert any("runs must be a non-empty list" in error
               for error in validate_manifest(changed))


def test_success_marker_must_exist_in_captured_output(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][1]["runs"][1].copy()
    output = tmp_path / "output.log"
    output.write_text("CPU started, but no success line", encoding="utf-8")
    record.update(output=str(output), output_sha256=__import__("hashlib").sha256(output.read_bytes()).hexdigest())
    assert any("success marker is absent" in error for error in validate_record(record, "test"))


def test_manifest_requires_both_cpu_checkouts(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"] = manifest["snapshots"][:1]
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    assert any("must declare exactly" in error for error in validate_manifest(changed))


def test_run_revision_must_match_snapshot_and_ids_be_unique(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"][1]["runs"][0]["snapshot_sha"] = "0" * 40
    manifest["snapshots"][1]["runs"][1]["id"] = manifest["snapshots"][1]["runs"][0]["id"]
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    errors = validate_manifest(changed)
    assert any("run snapshot_sha must match" in error for error in errors)
    assert any("duplicate run id" in error for error in errors)


def test_artifact_hash_is_verified(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][1]["runs"][1].copy()
    artifact = tmp_path / "artifact"
    artifact.write_text("changed", encoding="utf-8")
    record["artifacts"] = [str(artifact)]
    record["artifact_sha256"] = {str(artifact): "0" * 64}
    assert any("artifact SHA-256 mismatch" in error for error in validate_record(record, "test"))


@pytest.mark.parametrize("blocker", [None, []])
def test_malformed_blocker_is_reported_without_raising(blocker):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    record = manifest["snapshots"][0]["runs"][0].copy()
    record["blocker"] = blocker
    assert any("blocker must be a string" in error for error in validate_record(record, "test"))


def test_external_checkout_path_is_reported_without_raising(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"][0]["checkout"] = str(tmp_path)
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    assert any("checkout path must be inside the repository" in error
               for error in validate_manifest(changed))


def test_invalid_checkout_path_is_reported_without_raising(tmp_path):
    path = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["snapshots"][0]["checkout"] = "bad\u0000checkout"
    changed = tmp_path / "manifest.yaml"
    changed.write_text(json.dumps(manifest), encoding="utf-8")
    assert any("invalid checkout path" in error for error in validate_manifest(changed))
