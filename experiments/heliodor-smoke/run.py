#!/usr/bin/env python3
"""Run Heliodor's base-core smoke in a checked, isolated source copy."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import time
import fcntl

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.run_cpu_smoke import validate_manifest
SOURCE = ROOT / "sources/heliodor"
MANIFEST = ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml"
LOCKED_SHA = "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
VERYl_VERSION = "veryl 0.22.0 (967e477 2026-10-02)"
VERYl_SHA256 = "aa57dd31488410769ee61c367f03de6cbf11101be47b510b99bde4ac9155b4c1"
IMEM_DECL = "    var imem: logic<32> [16];"
ARCH_DEBUG_MARKER = "// Debug variant exposing core internals for stuck-test diagnosis."
ARCH_DRAM_DECL = "    var dram: logic<32> [1048576];"
ARCH_TARGET_MARKER = "#[test(test_arch_rv64ui_add)]\nmodule test_arch_rv64ui_add"
ARCH_FIXTURE = "test/riscv-arch-test/build/rv64ui/add.hex"


def sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def tree_sha256(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*")
                        if p.is_file() and ".git" not in p.relative_to(path).parts):
        rel = item.relative_to(path).as_posix().encode()
        h.update(len(rel).to_bytes(8, "big")); h.update(rel); h.update(bytes.fromhex(sha256(item)))
    return h.hexdigest()


def isolated_inputs_sha256(path: pathlib.Path) -> str:
    """Hash copied build inputs while excluding files Veryl generates during a run."""
    h = hashlib.sha256()
    roots = [path / "src", path / "Veryl.toml", path / "Veryl.lock",
             path / "tb/test_smoke.veryl", path / "tb/test_arch_common.veryl",
             path / "test/v4_smoke.hex", path / ARCH_FIXTURE]
    files = []
    for root in roots:
        if root.is_dir():
            files.extend(item for item in root.rglob("*") if item.is_file())
        elif root.is_file():
            files.append(root)
    for item in sorted(files):
        rel = item.relative_to(path).as_posix().encode()
        h.update(len(rel).to_bytes(8, "big")); h.update(rel); h.update(bytes.fromhex(sha256(item)))
    return h.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", "-C", str(SOURCE), *args], text=True).strip()


def load_json_yaml(path: pathlib.Path) -> dict:
    # The project's manifest is JSON syntax, which is also valid YAML.
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("toolchain manifest must be a mapping")
    return value


def expected_tool() -> tuple[str, str, dict]:
    doc = load_json_yaml(MANIFEST)
    snap = next((s for s in doc["snapshots"] if s.get("checkout") == "sources/heliodor"), None)
    if not snap:
        raise ValueError("manifest has no Heliodor snapshot")
    return f"{VERYl_VERSION.removeprefix('veryl ')}; binary sha256 {VERYl_SHA256}", VERYl_SHA256, snap


def verify_source() -> tuple[str, dict]:
    manifest_errors = validate_manifest(MANIFEST)
    if manifest_errors:
        raise ValueError("manifest/source validation failed: " + "; ".join(manifest_errors))
    _, _, snap = expected_tool()
    revision = git("rev-parse", "HEAD")
    if revision != LOCKED_SHA or snap.get("snapshot_sha") != LOCKED_SHA:
        raise ValueError(f"Heliodor revision mismatch: got {revision}, expected {LOCKED_SHA}")
    if git("status", "--porcelain"):
        raise ValueError("Heliodor checkout is not clean")
    links = snap.get("gitlinks", {})
    tree_links = {line.split(None, 3)[3]: line.split()[2]
                  for line in git("ls-tree", "HEAD").splitlines()
                  if len(line.split(None, 3)) == 4 and line.split()[1] == "commit"}
    if links != tree_links:
        raise ValueError("manifest gitlinks differ from the pinned Heliodor tree")
    for rel, rev in links.items():
        if git("-C", str(SOURCE / rel), "rev-parse", "HEAD") != rev:
            raise ValueError(f"Heliodor gitlink mismatch: {rel}")
        if subprocess.check_output(["git", "-C", str(SOURCE / rel), "status", "--porcelain"], text=True).strip():
            raise ValueError(f"Heliodor gitlink is dirty: {rel}")
    return revision, snap


def tool_metadata() -> tuple[str, dict[str, str]]:
    expected_description, expected_hash, snapshot = expected_tool()
    binary = shutil.which("veryl")
    if not binary:
        raise FileNotFoundError("veryl is not on PATH")
    actual_hash = sha256(pathlib.Path(binary))
    if actual_hash != expected_hash:
        raise ValueError(f"Veryl binary SHA-256 mismatch: {actual_hash} != {expected_hash}")
    result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)
    version = (result.stdout + result.stderr).strip()
    if result.returncode or VERYl_VERSION not in version:
        raise ValueError(f"Veryl version mismatch: {version!r}; expected {VERYl_VERSION}")
    verilator = subprocess.run(["verilator", "--version"], capture_output=True, text=True, timeout=10)
    cxx = subprocess.run(["g++", "--version"], capture_output=True, text=True, timeout=10)
    verilator_version = (verilator.stdout + verilator.stderr).splitlines()[0] if verilator.returncode == 0 else "unavailable"
    cxx_version = (cxx.stdout + cxx.stderr).splitlines()[0] if cxx.returncode == 0 else "unavailable"
    tools = {"veryl": f"{version}; binary sha256 {actual_hash}",
             "verilator": verilator_version, "cxx": cxx_version}
    if expected_description.split(";", 1)[0] != version.removeprefix("veryl "):
        raise ValueError(f"Veryl version differs from manifest: {version}")
    expected_tools = snapshot.get("tools", {})
    if not verilator.returncode or not cxx.returncode:
        if not verilator.returncode and expected_tools.get("verilator") not in verilator_version:
            raise ValueError(f"Verilator version differs from manifest: {verilator_version}")
        if not cxx.returncode and expected_tools.get("cxx") != cxx_version:
            raise ValueError(f"C++ compiler version differs from manifest: {cxx_version}")
    else:
        raise ValueError("Verilator and C++ compiler version checks did not complete")
    if verilator.returncode or cxx.returncode:
        raise ValueError("Verilator or C++ compiler is unavailable")
    return binary, tools


def observe(output: str, exit_code: int) -> tuple[bool, dict[str, int], bool, bool]:
    """Require CPU-produced smoke and ordinary arch-harness observations."""
    smoke_started = bool(re.search(r"\[test_smoke\]\s+cy=\d+.*\bcommit=\d+", output))
    arch_result = re.search(r"v4 rv64ui-add tohost=([0-9a-fA-F]+) pass=([01])", output)
    arch_started = arch_result is not None
    cpu_started = smoke_started or arch_started
    values: dict[str, int] = {}
    for reg in (10, 11, 12, 13):
        match = re.search(rf"\bx{reg}=([0-9a-fA-F]+)", output)
        if match:
            values[f"x{reg}"] = int(match.group(1), 16)
    if arch_result:
        values["arch_tohost"] = int(arch_result.group(1), 16)
        values["arch_pass"] = int(arch_result.group(2), 10)
    passed = (smoke_started and "[test_smoke] PASS" in output and
              values.get("x10") == 7 and values.get("x11") == 11 and
              values.get("x12") == 77 and values.get("x13") == 11 and
              arch_result is not None and values["arch_tohost"] == 1 and values["arch_pass"] == 1 and
              "v4 rv64ui-add PASS" in output and exit_code == 0)
    failed = cpu_started and not passed
    return cpu_started, values, passed, failed


def transform_testbench(original: str) -> str:
    if original.count(IMEM_DECL) != 1:
        raise ValueError("pinned test_smoke imem declaration drifted; re-review workaround anchor")
    return original.replace(IMEM_DECL, "    #[allow(initial_assign)]\n" + IMEM_DECL, 1)


def transform_arch_harness(original: str) -> str:
    """Keep the ordinary harness and one RV64UI target; omit the debug harness and unrelated tests."""
    if original.count(ARCH_DEBUG_MARKER) != 1 or original.count(ARCH_DRAM_DECL) != 1:
        raise ValueError("pinned arch harness boundary/DRAM declaration drifted; re-review isolation workaround")
    if original.count(ARCH_TARGET_MARKER) != 1:
        raise ValueError("pinned test_arch_rv64ui_add target drifted; re-review selected target")
    normal_harness = original.split(ARCH_DEBUG_MARKER, 1)[0]
    normal_harness = normal_harness.replace(
        ARCH_DRAM_DECL, "    #[allow(initial_assign)]\n" + ARCH_DRAM_DECL, 1)
    target_start = original.index(ARCH_TARGET_MARKER)
    next_target = original.find("\n#[test(", target_start + len(ARCH_TARGET_MARKER))
    if next_target < 0:
        raise ValueError("selected arch target has no bounded module end")
    selected_target = original[target_start:next_target].strip() + "\n"
    return normal_harness.rstrip() + "\n\n" + selected_target


def execute_test(command: list[str], work: pathlib.Path, timeout: float) -> tuple[int, bytes, bytes, str]:
    try:
        result = subprocess.run(command, cwd=work, capture_output=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr, ""
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, bytes) else (exc.stdout or "").encode()
        stderr = exc.stderr if isinstance(exc.stderr, bytes) else (exc.stderr or "").encode()
        target = command[-1] if command else "unknown target"
        return 124, stdout, stderr, f"Veryl {target} timed out after {timeout:g}s"


def resource_snapshot(timeout: float) -> dict[str, int | float | None]:
    try:
        disk_free = shutil.disk_usage(ROOT).free
    except OSError:
        disk_free = None
    memory_available = None
    try:
        for line in pathlib.Path("/proc/meminfo").read_text(encoding="ascii").splitlines():
            if line.startswith("MemAvailable:"):
                memory_available = int(line.split()[1]) * 1024
                break
    except (OSError, ValueError, IndexError):
        pass
    return {"disk_free_bytes": disk_free, "memory_available_bytes": memory_available,
            "logical_cpu_count": os.cpu_count(), "test_timeout_seconds": timeout}


def next_environment_change(stage: str, blocker: str) -> str:
    if not blocker:
        return "No environment change required; this smoke completed successfully."
    if stage == "locked-source-preflight":
        return "Restore the sources.lock revision, clean Heliodor checkout, gitlinks, and valid toolchain manifest before retrying."
    if stage == "veryl-toolchain-preflight":
        return "Provision the pinned Veryl 0.22.0 binary with the recorded SHA-256 and rerun the isolated smoke."
    if stage == "test_smoke":
        return "Inspect retained Veryl output and resource snapshot; resolve the first compile/check/simulation blocker before rerunning."
    if stage == "post-run-integrity":
        return "Restore the locked source and copied test inputs, then rerun into a fresh evidence directory."
    if stage == "cpu-assertions":
        return "Inspect the archived CPU output and fixture; correct only the identified architectural/test mismatch before rerunning."
    return f"Inspect the recorded {stage} failure and resource snapshot, then change only the identified input or environment."


def run(args: argparse.Namespace) -> dict:
    started_at = time.time()
    run_base = time.strftime("heliodor-core-%Y%m%dT%H%M%SZ", time.gmtime()) + f"-{os.getpid()}"
    run_id = run_base
    work: pathlib.Path | None = None
    archive_base = args.archive_dir.resolve()
    archive = archive_base / run_id
    if not archive.is_relative_to(ROOT.resolve()):
        raise ValueError("--archive-dir must resolve inside the project root")
    suffix = 1
    while archive.exists():
        suffix += 1
        run_id = f"{run_base}-{suffix}"
        archive = archive_base / run_id
    stdout_path = args.stdout.resolve() if args.stdout else ROOT / "notes/units/evidence/smoke" / f"{run_id}.stdout.log"
    stderr_path = args.stderr.resolve() if args.stderr else ROOT / "notes/units/evidence/smoke" / f"{run_id}.stderr.log"
    stdout_path.parent.mkdir(parents=True, exist_ok=True); stderr_path.parent.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)
    out = bytearray(); err = bytearray(); exit_code = 1; cpu_started = False
    assertion_failed = False; expected_observed = False; first_stage = "locked-source-preflight"; blocker = ""
    snapshot_sha = LOCKED_SHA; input_path = SOURCE / ARCH_FIXTURE
    smoke_input_path = SOURCE / "test/v4_smoke.hex"
    input_hash = sha256(input_path) if input_path.is_file() else "0" * 64
    smoke_input_hash = sha256(smoke_input_path) if smoke_input_path.is_file() else "0" * 64
    tools: dict[str, str] = {"veryl": "unavailable", "verilator": "unavailable", "cxx": "unavailable"}
    command: list[str] = []
    transformed_hash = transformed_arch_hash = fixture_hash = smoke_fixture_hash = ""
    source_tree_hash = isolated_tree_hash = isolated_inputs_hash = ""
    try:
        revision, snap = verify_source()
        snapshot_sha = revision
        source_tree_hash = tree_sha256(SOURCE)
        first_stage = "veryl-toolchain-preflight"
        binary, tools = tool_metadata()
        if not input_path.is_file() or not smoke_input_path.is_file():
            raise FileNotFoundError(f"required smoke/arch fixture missing: {input_path if not input_path.is_file() else smoke_input_path}")
        input_hash = sha256(input_path)
        smoke_input_hash = sha256(smoke_input_path)
        first_stage = "isolated-copy"
        if args.work_dir:
            work = args.work_dir.resolve()
            if work.exists() and any(work.iterdir()):
                raise ValueError(f"work directory must be empty: {work}")
            work.mkdir(parents=True, exist_ok=True)
        else:
            work = pathlib.Path(tempfile.mkdtemp(prefix="heliodor-core-smoke-"))
        # Explicit whitelist: production RTL/config/lock, the selected ordinary test,
        # and its fixture. Omitting test_arch_common.veryl also excludes its
        # uninstantiated 64K-word debug harness that fails Veryl 0.22.0 check.
        shutil.copytree(SOURCE / "src", work / "src")
        for name in ("Veryl.toml", "Veryl.lock"):
            shutil.copy2(SOURCE / name, work / name)
        (work / "tb").mkdir(); (work / "test").mkdir(parents=True)
        test_source = SOURCE / "tb/test_smoke.veryl"
        original = test_source.read_text(encoding="utf-8")
        transformed = transform_testbench(original)
        (work / "tb/test_smoke.veryl").write_text(transformed, encoding="utf-8")
        arch_source = SOURCE / "tb/test_arch_common.veryl"
        transformed_arch = transform_arch_harness(arch_source.read_text(encoding="utf-8"))
        (work / "tb/test_arch_common.veryl").write_text(transformed_arch, encoding="utf-8")
        shutil.copy2(smoke_input_path, work / "test/v4_smoke.hex")
        arch_fixture = work / ARCH_FIXTURE
        arch_fixture.parent.mkdir(parents=True)
        shutil.copy2(input_path, arch_fixture)
        isolated_tree_hash = tree_sha256(work)
        isolated_inputs_hash = isolated_inputs_sha256(work)
        transformed_hash = sha256(work / "tb/test_smoke.veryl")
        transformed_arch_hash = sha256(work / "tb/test_arch_common.veryl")
        fixture_hash = sha256(arch_fixture)
        smoke_fixture_hash = sha256(work / "test/v4_smoke.hex")
        if fixture_hash != input_hash or smoke_fixture_hash != smoke_input_hash:
            raise ValueError("copied smoke/arch fixture SHA-256 differs from locked input")
        shutil.copy2(work / "tb/test_smoke.veryl", archive / "test_smoke.veryl")
        shutil.copy2(work / "test/v4_smoke.hex", archive / "v4_smoke.hex")
        shutil.copy2(work / "tb/test_arch_common.veryl", archive / "test_arch_common.veryl")
        archived_arch_fixture = archive / "rv64ui-add.hex"
        shutil.copy2(arch_fixture, archived_arch_fixture)
        commands: list[list[str]] = []
        for test_name in ("test_smoke", "test_arch_rv64ui_add"):
            first_stage = test_name
            command = [binary, "test", "--include-ignored", "--test", test_name]
            commands.append(command)
            exit_code, child_out, child_err, timeout_error = execute_test(command, work, args.timeout)
            out.extend(child_out); err.extend(child_err)
            blocker = timeout_error or blocker
            if timeout_error or exit_code != 0:
                break
        combined = (out + err).decode("utf-8", "replace")
        cpu_started, values, expected_observed, assertion_failed = observe(combined, exit_code)
        if not blocker and not cpu_started:
            blocker = "Veryl completed without the test execution marker; CPU start was not observed"
        if cpu_started and not expected_observed and exit_code == 0:
            first_stage = "cpu-assertions"
        post_revision, _ = verify_source()
        if post_revision != snapshot_sha:
            raise ValueError("Heliodor source revision changed during run")
        if tree_sha256(SOURCE) != source_tree_hash:
            raise ValueError("Heliodor source tree changed during run")
        # Confirm the copied source/test inputs stayed stable through execution.
        if isolated_inputs_sha256(work) != isolated_inputs_hash:
            raise ValueError("isolated source, configuration, testbench, or fixture changed during the run")
    except (OSError, ValueError, subprocess.SubprocessError, KeyError) as exc:
        blocker = blocker or str(exc)
        if cpu_started:
            first_stage = "post-run-integrity"
            expected_observed = False
            assertion_failed = True
    log_persistence_errors = []
    for stream, path, fallback, payload in (
            ("stdout", stdout_path, archive / "stdout.log", bytes(out)),
            ("stderr", stderr_path, archive / "stderr.log", bytes(err))):
        try:
            path.write_bytes(payload)
        except OSError as exc:
            log_persistence_errors.append(f"{path}: {exc}")
            path = fallback
            path.write_bytes(payload)
            if stream == "stdout":
                stdout_path = path
            else:
                stderr_path = path
    combined_path = archive / "output.log"
    combined_path.write_bytes(bytes(out) + b"\n--- STDERR ---\n" + bytes(err))
    record = {
        "id": run_id, "snapshot_sha": snapshot_sha, "input": "sources/heliodor/" + ARCH_FIXTURE,
        "input_sha256": input_hash,
        "inputs": [{"path": "sources/heliodor/test/v4_smoke.hex", "sha256": smoke_input_hash},
                   {"path": "sources/heliodor/" + ARCH_FIXTURE, "sha256": input_hash}],
        "configuration": "Heliodor test_smoke plus test_arch_rv64ui_add; one harness/DUT; 5000 smoke cycles and 300000 arch cycles; expected x10=7, x11=11, x12=77, x13=11 and tohost=1.",
        "command": json.dumps(commands, ensure_ascii=False) if command else "preflight not reached",
        "working_directory": str(work) if work else str(ROOT), "tools": tools,
        "exit_code": exit_code, "cpu_started": cpu_started,
        "result": "run-pass" if expected_observed else ("run-fail" if cpu_started and assertion_failed else "blocked"),
        "assertion_failed": assertion_failed, "expected_observed": expected_observed,
        "expected": "Both CPU tests pass: test_smoke reports x10=7, x11=11, x12=77, x13=11; test_arch_rv64ui_add reports tohost=1/pass=1 and its PASS marker.",
        "observed": f"CPU-start={cpu_started}; results={values if 'values' in locals() else {}}; smoke_marker={'[test_smoke] PASS' in (out + err).decode('utf-8','replace')}; arch_marker={'v4 rv64ui-add PASS' in (out + err).decode('utf-8','replace')}",
        "output": str(combined_path.relative_to(ROOT)), "output_sha256": sha256(combined_path),
        "stdout": str(stdout_path.relative_to(ROOT)) if stdout_path.is_relative_to(ROOT) else str(stdout_path),
        "stdout_sha256": sha256(stdout_path),
        "stderr": str(stderr_path.relative_to(ROOT)) if stderr_path.is_relative_to(ROOT) else str(stderr_path),
        "stderr_sha256": sha256(stderr_path),
        "artifacts": [str(p.relative_to(ROOT)) for p in
                      [archive / "run.py", archive / "test_smoke.veryl", archive / "v4_smoke.hex"] if p.is_file()],
        "artifact_sha256": {}, "expected_marker": "[test_smoke] PASS", "blocker": blocker,
        "log_path_warnings": log_persistence_errors,
        "first_failed_stage": first_stage if not expected_observed else "",
        "resources": resource_snapshot(args.timeout),
        "next_environment_change": next_environment_change(first_stage if not expected_observed else "", blocker),
        "source_tree_sha256": source_tree_hash, "source_commit": snapshot_sha,
        "isolated_tree_sha256": isolated_tree_hash,
        "isolated_inputs_sha256": isolated_inputs_hash,
        "expected_markers": ["[test_smoke] PASS", "v4 rv64ui-add PASS"],
        "transformed_test_sha256": transformed_hash,
        "transformed_arch_harness_sha256": transformed_arch_hash,
        "fixture_sha256": fixture_hash, "smoke_fixture_sha256": smoke_fixture_hash,
        "run_seconds": round(time.time() - started_at, 3),
    }
    # Archive the exact runner before recording artifact identities so later
    # runner edits cannot invalidate this run's provenance.
    runner_snapshot = archive / "run.py"
    shutil.copy2(pathlib.Path(__file__).resolve(), runner_snapshot)
    record["artifact_sha256"] = {str((archive / n).relative_to(ROOT)): sha256(archive / n)
                                 for n in ("run.py", "test_smoke.veryl", "v4_smoke.hex",
                                           "test_arch_common.veryl", "rv64ui-add.hex") if (archive / n).is_file()}
    record["artifacts"] = [str((archive / n).relative_to(ROOT)) for n in
                            ("run.py", "test_smoke.veryl", "v4_smoke.hex",
                             "test_arch_common.veryl", "rv64ui-add.hex") if (archive / n).is_file()]
    metadata_path = archive / "run-metadata.json"
    metadata_path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        lock_path = pathlib.Path(tempfile.gettempdir()) / ("heliodor-smoke-" + hashlib.sha256(str(MANIFEST.resolve()).encode()).hexdigest() + ".lock")
        with lock_path.open("a", encoding="utf-8") as lock:
            fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
            manifest = load_json_yaml(MANIFEST)
            snap = next(s for s in manifest["snapshots"] if s.get("checkout") == "sources/heliodor")
            if any(r.get("id") == run_id for r in snap["runs"]):
                raise ValueError(f"duplicate manifest run ID {run_id}")
            snap["runs"].append(record)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=MANIFEST.parent,
                                             prefix=f".{MANIFEST.name}.", suffix=".tmp", delete=False) as stream:
                tmp = pathlib.Path(stream.name)
                stream.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                stream.flush(); os.fsync(stream.fileno())
            os.chmod(tmp, MANIFEST.stat().st_mode & 0o777)
            os.replace(tmp, MANIFEST)
            dir_fd = os.open(MANIFEST.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
            try:
                os.fsync(dir_fd)
            finally:
                os.close(dir_fd)
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
    except (OSError, ValueError, StopIteration) as exc:
        record["manifest_persisted"] = False
        record["manifest_error"] = str(exc)
        (archive / "run-record.json").write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("id", "result", "first_failed_stage", "exit_code", "cpu_started", "output")}, indent=2))
    return record


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdout", type=pathlib.Path)
    parser.add_argument("--stderr", type=pathlib.Path)
    parser.add_argument("--archive-dir", type=pathlib.Path, default=ROOT / "notes/units/evidence/smoke/heliodor-core-smoke-inputs")
    parser.add_argument("--work-dir", type=pathlib.Path)
    parser.add_argument("--timeout", type=float, default=180.0)
    args = parser.parse_args()
    if args.timeout <= 0 or not (args.timeout < float("inf")):
        parser.error("--timeout must be finite and positive")
    try:
        record = run(args)
        return 0 if record["result"] == "run-pass" else 1
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
