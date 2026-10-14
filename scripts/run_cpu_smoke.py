#!/usr/bin/env python3
"""Validate reproducibility metadata and classify CPU smoke outcomes."""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import glob
from typing import Any


ROOT = pathlib.Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {
    "snapshot_sha", "input_sha256", "configuration", "command",
    "working_directory", "tools", "exit_code", "cpu_started", "result",
    "output", "output_sha256", "artifacts", "stdout", "stdout_sha256",
    "stderr", "stderr_sha256", "input", "assertion_failed",
    "expected_observed", "expected", "observed", "id", "blocker",
    "expected_marker", "artifact_sha256",
}


class ValidationError(ValueError):
    pass


def classify(*, cpu_started: bool, exit_code: int, assertion_failed: bool,
             expected_observed: bool) -> str:
    """Apply the story's strict distinction between blockers and CPU failures."""
    if not cpu_started:
        return "blocked"
    if assertion_failed:
        return "run-fail"
    if exit_code == 0 and expected_observed:
        return "run-pass"
    raise ValidationError(
        "CPU started without a documented assertion failure or successful expected marker"
    )


def _load(path: pathlib.Path) -> dict[str, Any]:
    content = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        try:
            value = json.loads(content)  # JSON is a valid YAML subset.
        except json.JSONDecodeError as exc:
            raise ValidationError("PyYAML is required to read this YAML manifest") from exc
    else:
        value = yaml.safe_load(content)
    if not isinstance(value, dict):
        raise ValidationError("manifest must be a mapping")
    return value


def _file_hash(path: pathlib.Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repo_path(value: str) -> pathlib.Path:
    path = pathlib.Path(value)
    return path if path.is_absolute() else ROOT / path


def _git(path: pathlib.Path, *args: str) -> str:
    return subprocess.check_output(["git", "-C", str(path), *args], text=True).strip()


def _locked_snapshots() -> dict[str, str]:
    text = (ROOT / "sources.lock").read_text(encoding="utf-8")
    blocks = re.split(r"(?=^  - snapshot_id:)", text, flags=re.MULTILINE)
    locked: dict[str, str] = {}
    for block in blocks:
        checkout = re.search(r"^    checkout: (.+)$", block, re.MULTILINE)
        commit = re.search(r"^    commit: ([0-9a-f]{40})$", block, re.MULTILINE)
        if checkout and commit:
            locked[checkout.group(1).strip()] = commit.group(1)
    return locked


def validate_record(record: dict[str, Any], label: str) -> list[str]:
    errors: list[str] = []
    missing = REQUIRED - record.keys()
    if missing:
        errors.append(f"{label}: missing required fields: {', '.join(sorted(missing))}")
        return errors
    if not isinstance(record["snapshot_sha"], str) or not HEX40.fullmatch(record["snapshot_sha"]):
        errors.append(f"{label}: snapshot_sha must be 40 lowercase hex characters")
    if not isinstance(record["input_sha256"], str) or not HEX64.fullmatch(record["input_sha256"]):
        errors.append(f"{label}: input_sha256 must be 64 lowercase hex characters")
    if not isinstance(record["output_sha256"], str) or not HEX64.fullmatch(record["output_sha256"]):
        errors.append(f"{label}: output_sha256 must be 64 lowercase hex characters")
    if not isinstance(record["stdout_sha256"], str) or not HEX64.fullmatch(record["stdout_sha256"]):
        errors.append(f"{label}: stdout_sha256 must be 64 lowercase hex characters")
    if not isinstance(record["stderr_sha256"], str) or not HEX64.fullmatch(record["stderr_sha256"]):
        errors.append(f"{label}: stderr_sha256 must be 64 lowercase hex characters")
    if (not isinstance(record["tools"], dict) or not record["tools"]
            or any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
                   for k, v in record["tools"].items())):
        errors.append(f"{label}: tools must map each tool name to a non-empty exact version or explicit unknown")
    if not isinstance(record["configuration"], str) or not record["configuration"].strip():
        errors.append(f"{label}: configuration must be a non-empty string")
    if not isinstance(record["command"], str) or not record["command"].strip():
        errors.append(f"{label}: command must be a non-empty exact command")
    if not isinstance(record["working_directory"], str) or not record["working_directory"].strip():
        errors.append(f"{label}: working_directory is required")
    elif not _repo_path(record["working_directory"]).is_dir():
        errors.append(f"{label}: working_directory does not exist: {record['working_directory']}")
    if not isinstance(record["exit_code"], int) or isinstance(record["exit_code"], bool):
        errors.append(f"{label}: exit_code must be an integer")
    if not isinstance(record["cpu_started"], bool):
        errors.append(f"{label}: cpu_started must be boolean")
    for key in ("assertion_failed", "expected_observed"):
        if not isinstance(record[key], bool):
            errors.append(f"{label}: {key} must be boolean")
    for key in ("expected", "observed"):
        if not isinstance(record[key], str) or not record[key].strip():
            errors.append(f"{label}: {key} must be a non-empty string")
    if not isinstance(record["id"], str) or not record["id"].strip():
        errors.append(f"{label}: id must be a non-empty string")
    if not isinstance(record["blocker"], str):
        errors.append(f"{label}: blocker must be a string (empty when not blocked)")
    if not isinstance(record["expected_marker"], str) or not record["expected_marker"].strip():
        errors.append(f"{label}: expected_marker must be a non-empty string")
    artifact_hashes = record["artifact_sha256"]
    if not isinstance(artifact_hashes, dict) or any(
            not isinstance(k, str) or not isinstance(v, str) or not HEX64.fullmatch(v)
            for k, v in (artifact_hashes.items() if isinstance(artifact_hashes, dict) else [])):
        errors.append(f"{label}: artifact_sha256 must map artifact paths to SHA-256")
    if not isinstance(record["artifacts"], list):
        errors.append(f"{label}: artifacts must be a list")
    else:
        for artifact in record["artifacts"]:
            if not isinstance(artifact, str) or not artifact.strip():
                errors.append(f"{label}: artifact paths must be non-empty strings")
                continue
            if artifact.startswith("ephemeral:"):
                if not artifact.removeprefix("ephemeral:").strip():
                    errors.append(f"{label}: ephemeral artifact path must name its location")
                continue
            candidate = _repo_path(artifact)
            if not candidate.exists() and not glob.glob(str(candidate)):
                errors.append(f"{label}: artifact does not exist or match a path pattern: {artifact}")
            elif isinstance(artifact_hashes, dict) and artifact in artifact_hashes:
                if not candidate.is_file():
                    errors.append(f"{label}: hashed artifact must be a file: {artifact}")
                elif HEX64.fullmatch(str(artifact_hashes[artifact])) and _file_hash(candidate) != artifact_hashes[artifact]:
                    errors.append(f"{label}: artifact SHA-256 mismatch: {artifact}")
            elif not artifact.startswith("ephemeral:"):
                errors.append(f"{label}: durable artifact requires a SHA-256 entry: {artifact}")
    for path_key, hash_key in (("output", "output_sha256"), ("stdout", "stdout_sha256"),
                               ("stderr", "stderr_sha256")):
        try:
            path = _repo_path(record[path_key])
            if not path.is_file():
                errors.append(f"{label}: {path_key} file does not exist: {record[path_key]}")
            elif HEX64.fullmatch(str(record[hash_key])) and _file_hash(path) != record[hash_key]:
                errors.append(f"{label}: {path_key} SHA-256 mismatch")
        except (TypeError, OSError) as exc:
            errors.append(f"{label}: invalid {path_key}: {exc}")
    input_path = record.get("input")
    if not isinstance(input_path, str) or not input_path.strip():
        errors.append(f"{label}: input fixture path is required")
    else:
        path = _repo_path(input_path)
        if not path.is_file():
            errors.append(f"{label}: input file does not exist: {input_path}")
        elif _file_hash(path) != record["input_sha256"]:
            errors.append(f"{label}: input SHA-256 mismatch")
    if not isinstance(record.get("result"), str) or record["result"] not in {"blocked", "run-fail", "run-pass"}:
        errors.append(f"{label}: result must be blocked, run-fail, or run-pass")
    elif isinstance(record.get("exit_code"), int) and isinstance(record.get("cpu_started"), bool):
        try:
            derived = classify(
                cpu_started=record["cpu_started"], exit_code=record["exit_code"],
                assertion_failed=record["assertion_failed"],
                expected_observed=record["expected_observed"],
            )
            if record["result"] != derived:
                errors.append(f"{label}: result {record['result']} conflicts with derived {derived}")
            if derived == "run-pass":
                try:
                    output_text = _repo_path(record["output"]).read_text(encoding="utf-8", errors="replace")
                    if record["expected_marker"] not in output_text:
                        errors.append(f"{label}: expected success marker is absent from output")
                except (TypeError, OSError):
                    pass
        except ValidationError as exc:
            errors.append(f"{label}: {exc}")
    if record.get("cpu_started") is False and record.get("result") == "run-fail":
        errors.append(f"{label}: CPU-start failure cannot be classified run-fail")
    if record.get("cpu_started") is False and record.get("expected_observed") is True:
        errors.append(f"{label}: expected CPU marker cannot be observed before CPU start")
    if record.get("result") == "blocked":
        if not isinstance(record.get("first_failed_stage"), str) or not record["first_failed_stage"].strip():
            errors.append(f"{label}: blocked result requires first_failed_stage")
        if isinstance(record["blocker"], str) and not record["blocker"].strip():
            errors.append(f"{label}: blocked result requires a concrete blocker explanation")
    return errors


def validate_manifest(path: pathlib.Path) -> list[str]:
    manifest = _load(path)
    errors: list[str] = []
    if manifest.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    snapshots = manifest.get("snapshots")
    if not isinstance(snapshots, list) or not snapshots:
        return errors + ["snapshots must be a non-empty list"]
    required_checkouts = {"sources/xiangshan", "sources/heliodor"}
    declared_checkouts: set[str] = set()
    for item in snapshots:
        if not isinstance(item, dict):
            continue
        checkout_value = str(item.get("checkout", ""))
        try:
            checkout_path = _repo_path(checkout_value).resolve()
            declared_checkouts.add(checkout_path.relative_to(ROOT.resolve()).as_posix())
        except (OSError, RuntimeError, ValueError) as exc:
            declared_checkouts.add(f"invalid-checkout:{checkout_value}:{type(exc).__name__}")
    if declared_checkouts != required_checkouts:
        errors.append(f"snapshots must declare exactly {sorted(required_checkouts)}")
    all_ids: set[str] = set()
    for snapshot in snapshots:
        if not isinstance(snapshot, dict):
            errors.append("each snapshot must be a mapping")
            continue
        name = str(snapshot.get("name", "unnamed"))
        try:
            checkout = _repo_path(str(snapshot.get("checkout", "")))
            checkout_resolved = checkout.resolve()
        except (OSError, RuntimeError, ValueError) as exc:
            errors.append(f"{name}: invalid checkout path: {exc}")
            continue
        try:
            lock_key = checkout_resolved.relative_to(ROOT.resolve()).as_posix()
        except ValueError:
            errors.append(f"{name}: checkout path must be inside the repository")
            continue
        expected = snapshot.get("snapshot_sha")
        if not checkout.is_dir():
            errors.append(f"{name}: checkout does not exist")
            continue
        try:
            actual = _git(checkout, "rev-parse", "HEAD")
            if actual != expected:
                errors.append(f"{name}: checkout SHA {actual} != locked {expected}")
            locked_sha = _locked_snapshots().get(lock_key)
            if locked_sha != expected:
                errors.append(f"{name}: sources.lock maps {lock_key} to {locked_sha}, expected {expected}")
            dirty = _git(checkout, "status", "--porcelain")
            if dirty:
                errors.append(f"{name}: source checkout is dirty")
            links = snapshot.get("gitlinks", {})
            if not isinstance(links, dict):
                errors.append(f"{name}: gitlinks must be a mapping")
            else:
                tree_links = set()
                for line in _git(checkout, "ls-tree", "HEAD").splitlines():
                    fields = line.split(None, 3)
                    if len(fields) == 4 and fields[1] == "commit":
                        tree_links.add(fields[3])
                if set(links) != tree_links:
                    errors.append(f"{name}: manifest gitlink paths do not exactly match snapshot direct gitlinks")
                for rel, sha in links.items():
                    sub = checkout / rel
                    tree_entry = _git(checkout, "ls-tree", "HEAD", rel).split()
                    parent_sha = tree_entry[2] if len(tree_entry) >= 3 and tree_entry[1] == "commit" else "missing"
                    if parent_sha != sha:
                        errors.append(f"{name}: parent gitlink {rel} is {parent_sha}, expected {sha}")
                    actual_link = _git(sub, "rev-parse", "HEAD") if sub.is_dir() else "missing"
                    if actual_link != sha:
                        errors.append(f"{name}: gitlink {rel} is {actual_link}, expected {sha}")
                    if sub.is_dir() and _git(sub, "status", "--porcelain"):
                        errors.append(f"{name}: gitlink checkout {rel} is dirty")
        except (subprocess.CalledProcessError, OSError) as exc:
            errors.append(f"{name}: git validation failed: {exc}")
        if (not isinstance(snapshot.get("tools"), dict) or not snapshot["tools"]
                or any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
                       for k, v in snapshot["tools"].items())):
            errors.append(f"{name}: exact tools versions are required")
        if not isinstance(snapshot.get("configuration"), str) or not snapshot["configuration"].strip():
            errors.append(f"{name}: configuration must be a non-empty string")
        if (not isinstance(snapshot.get("environment"), dict) or not snapshot["environment"]
                or any(not isinstance(k, str) or not k.strip() or not isinstance(v, str) or not v.strip()
                       for k, v in snapshot.get("environment", {}).items()
                       if isinstance(snapshot.get("environment"), dict))):
            errors.append(f"{name}: environment must map required variable names to non-empty descriptions/values")
        runs = snapshot.get("runs")
        if not isinstance(runs, list) or not runs:
            errors.append(f"{name}: runs must be a non-empty list")
            continue
        for record in runs:
            if isinstance(record, dict):
                run_id = record.get("id")
                if isinstance(run_id, str):
                    if run_id in all_ids:
                        errors.append(f"duplicate run id: {run_id}")
                    all_ids.add(run_id)
                if record.get("snapshot_sha") != expected:
                    errors.append(f"{name}/{run_id or 'run'}: run snapshot_sha must match enclosing snapshot")
                errors.extend(validate_record(record, f"{name}/{record.get('id', 'run')}"))
            else:
                errors.append(f"{name}: each run must be a mapping")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="action", required=True)
    validate = sub.add_parser("validate", help="validate toolchain and run manifest")
    validate.add_argument("--manifest", required=True, type=pathlib.Path)
    args = parser.parse_args()
    errors = validate_manifest(args.manifest)
    if errors:
        print("\n".join(f"ERROR: {error}" for error in errors), file=sys.stderr)
        return 1
    print(f"Valid manifest: {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
