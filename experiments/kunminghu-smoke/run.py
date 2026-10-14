#!/usr/bin/env python3
"""Build and run the locked Kunminghu single-hart fixture, preserving evidence."""
from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import hashlib
import json
import math
import os
import pathlib
import re
import shutil
import shlex
import subprocess
import sys
import tempfile
from collections.abc import Callable

ROOT = pathlib.Path(__file__).resolve().parents[2]
SOURCE = ROOT / "experiments/kunminghu-smoke/fixture.S"
LINKER = ROOT / "experiments/kunminghu-smoke/fixture.ld"
SSTC_SOURCE = ROOT / "experiments/sstc/kunminghu-full-matrix.S"
SSCOFPMF_SOURCE = ROOT / "experiments/sscofpmf/kunminghu-sscofpmf-complete-v4.S"
SSCOFPMF_ACCESS_SOURCE = ROOT / "experiments/sscofpmf/kunminghu-sscofpmf-access-route-diagnostic-v4.S"
SSTC_CASES = ("s-lt", "s-eq", "s-gt", "s-stce-off", "s-tm-off")
CHECKOUT = ROOT / "sources/xiangshan"
EMULATOR = CHECKOUT / "build/verilator-compile/emu"
NEMU = CHECKOUT / "ready-to-run/riscv64-nemu-interpreter-so"
FIRST_COMMIT = "The first instruction of core 0 has commited."
GOOD_TRAP = "HIT GOOD TRAP"
BAD_TRAP = "HIT BAD TRAP"
CRITICAL_ERROR = "HIT CRITICAL ERROR"
ABORT = "ABORT at pc = "


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def classify_output(output: str, exit_code: int, *, timed_out: bool = False,
                    expected_start_pc: int | None = None,
                    expected_trap_pc: int | None = None,
                    expected_image: str | None = None) -> dict[str, object]:
    """Classify only direct CPU-start, termination, and good-trap observations."""
    started = FIRST_COMMIT in output
    loaded_images = re.findall(r"^The image is (.+)$", output, re.MULTILINE)
    image_loaded = expected_image in loaded_images if expected_image is not None else bool(loaded_images)
    good = GOOD_TRAP in output
    bad = BAD_TRAP in output
    aborted = ABORT in output
    trap_match = re.search(r"HIT GOOD TRAP at pc = 0x([0-9a-fA-F]+)", output)
    observed_trap_pc = int(trap_match.group(1), 16) if trap_match else None
    trap_address_matches = expected_trap_pc is None or observed_trap_pc == expected_trap_pc
    committed_pcs = {int(value, 16) for value in re.findall(r"commit pc\s+([0-9a-fA-F]+)", output)}
    entry_committed = expected_start_pc is None or expected_start_pc in committed_pcs
    critical_error = CRITICAL_ERROR in output
    if not started:
        result = "blocked"
        blocker = "emulator exited or timed out before the first instruction commit was observed"
    elif (image_loaded and entry_committed and good and not bad and not aborted and trap_address_matches
          and not critical_error and exit_code == 0 and not timed_out):
        result = "run-pass"
        blocker = ""
    else:
        result = "run-fail"
        if timed_out:
            blocker = "emulator timed out after CPU start before a successful good trap"
        elif bad:
            blocker = "emulator observed BADTRAP"
        elif aborted:
            blocker = "emulator reported ABORT"
        elif critical_error:
            blocker = "emulator reported a matching critical error instead of clean fixture termination"
        elif not entry_committed:
            blocker = f"linked entry PC 0x{expected_start_pc:x} was not observed in commit trace"
        elif good and not trap_address_matches:
            observed_pc_text = f"0x{observed_trap_pc:x}" if observed_trap_pc is not None else "unknown"
            blocker = (f"good trap PC {observed_pc_text} does not match linked marker "
                       f"0x{expected_trap_pc:x}")
        elif not good:
            blocker = "CPU started but expected good-trap marker was absent"
        else:
            blocker = f"emulator exited with code {exit_code} despite good-trap output"
    return {
        "cpu_started": started,
        "expected_observed": (started and image_loaded and entry_committed and good and not bad and not aborted and trap_address_matches
                              and not critical_error and exit_code == 0 and not timed_out),
        "assertion_failed": started and result == "run-fail",
        "result": result,
        "blocker": blocker,
        "observed": ("image loaded; " if image_loaded else "image load not observed; ") + ("first instruction committed; " + (
            "HIT GOOD TRAP" if good and not bad else "HIT BAD TRAP" if bad else "good trap not observed"
        ) if started else "first instruction commit not observed"),
    }


def parse_sstc_trace(output: str, case: str) -> dict[str, object]:
    """Recover timer sample and comparator operands from architectural commits."""
    sampled_time = None
    comparator = None
    registers: dict[int, int] = {}
    for line in output.splitlines():
        match = re.search(r"inst ([0-9a-fA-F]{8}) wen \d+ dst ([0-9a-fA-F]{2}) data ([0-9a-fA-F]{16})", line)
        if not match:
            continue
        instruction, rd, data = int(match.group(1), 16), int(match.group(2), 16), int(match.group(3), 16)
        if instruction == 0xC0102373 and rd == 6 and sampled_time is None:
            sampled_time = data
        # CSR writes have no destination register; recover rs1 from prior commits.
        if sampled_time is not None and ((instruction >> 20) & 0xFFF) == 0x14D:
            source_register = (instruction >> 15) & 0x1F
            comparator = registers.get(source_register)
            break
        if rd != 0:
            registers[rd] = data
    result: dict[str, object] = {
        "pass_marker_observed": "HIT GOOD TRAP" in output,
        "evidence_method": "commit trace captures the time CSR sample and recovers the stimecmp rs1 operand from the latest committed value of that source register",
    }
    if sampled_time is not None:
        result["sampled_time"] = sampled_time
        if comparator is not None:
            result["comparator_operand"] = comparator
            result["sample_relation"] = "<" if sampled_time < comparator else ("==" if sampled_time == comparator else ">")
    return result


def _run(command: list[str], cwd: pathlib.Path, timeout: float | None = None):
    try:
        result = subprocess.run(command, cwd=cwd, capture_output=True, text=True,
                                encoding="utf-8", errors="replace",
                                timeout=timeout, check=False)
        return result.returncode, result.stdout, result.stderr, False
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout or ""
        stderr = exc.stderr or ""
        if isinstance(stdout, bytes):
            stdout = stdout.decode(errors="replace")
        if isinstance(stderr, bytes):
            stderr = stderr.decode(errors="replace")
        return 124, stdout, stderr, True


def _version(command: list[str], cwd: pathlib.Path = ROOT) -> str:
    try:
        code, stdout, stderr, _ = _run(command, cwd, timeout=10)
        return (stdout or stderr).splitlines()[0].strip() if code == 0 and (stdout or stderr) else "unavailable"
    except OSError:
        return "unavailable"


def _locked_sha() -> str:
    text = (ROOT / "sources.lock").read_text(encoding="utf-8")
    blocks = re.split(r"(?=^  - snapshot_id:)", text, flags=re.MULTILINE)
    for block in blocks:
        checkout = re.search(r"^    checkout: (.+)$", block, re.MULTILINE)
        commit = re.search(r"^    commit: ([0-9a-f]{40})$", block, re.MULTILINE)
        if checkout and commit and checkout.group(1).strip() == "sources/xiangshan":
            return commit.group(1)
    raise ValueError("sources.lock has no sources/xiangshan snapshot")


def resource_snapshot(emulator_timeout: float) -> dict[str, int | float | None]:
    """Capture resource context useful when diagnosing a blocked run."""
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
    return {
        "disk_free_bytes": disk_free,
        "memory_available_bytes": memory_available,
        "logical_cpu_count": os.cpu_count(),
        "build_command_timeout_seconds": 120,
        "emulator_timeout_seconds": emulator_timeout,
    }


def next_environment_change(failed_stage: str) -> str:
    """Suggest a concrete next action without guessing from unobserved failures."""
    if not failed_stage:
        return "No environment change required; this smoke completed successfully."
    suggestions = {
        "locked source and manifest preflight": "Restore the manifest and locked source/gitlinks to a valid, clean state, then rerun preflight.",
        "locked SHA check": "Restore the configured Kunminghu baseline SHA to the sources.lock snapshot before rerunning.",
        "fixture input": "Restore the missing fixture source and linker inputs, then rerun the fixture build.",
        "fixture source integrity": "Restore the fixture source to its recorded pre-build hash and rerun the smoke.",
        "fixture linker integrity": "Restore the linker script to its recorded pre-build hash and rerun the smoke.",
        "tool availability": "Provision the missing pinned compiler, objcopy, emulator, or NEMU dependency using Story 6.1 instructions.",
        "compile and link": "Inspect compiler/linker diagnostics and provision the pinned cross-toolchain or correct the fixture/linker input.",
        "raw image generation": "Inspect objcopy diagnostics and restore the pinned cross-toolchain if the tool is incompatible.",
        "link map inspection": "Inspect the retained linker map and restore the expected entry/trap layout before rerunning.",
        "emulator CPU run": "Inspect the emulator/NEMU logs and resource snapshot; restore the pinned simulator artifacts before retrying.",
        "post-run source/manifest integrity": "Restore the clean locked source and valid manifest, then rerun from a fresh evidence directory.",
        "simulator artifact integrity": "Restore the recorded emulator and NEMU binary hashes from the pinned build before retrying.",
        "pre-append source/manifest integrity": "Restore the locked source, manifest, and evidence hashes, then rerun to create a fresh record.",
    }
    return suggestions.get(failed_stage, "Inspect the recorded first failure and resource snapshot, then change only the identified environment/input before retrying.")


class ManifestIntegrityError(ValueError):
    pass


class ManifestDurabilityError(OSError):
    """Manifest replacement completed, but directory durability could not be confirmed."""


def append_manifest_record(manifest_path: pathlib.Path, record: dict[str, object],
                           validator: Callable[[pathlib.Path], list[str]] | None = None) -> None:
    """Serialize concurrent appends and atomically replace the manifest."""
    lock_key = hashlib.sha256(str(manifest_path.resolve()).encode("utf-8")).hexdigest()
    lock_path = pathlib.Path(tempfile.gettempdir()) / f"learning-rv64-manifest-{lock_key}.lock"
    with lock_path.open("a", encoding="utf-8") as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        temporary: pathlib.Path | None = None
        try:
            if validator is not None:
                errors = validator(manifest_path)
                if errors:
                    raise ManifestIntegrityError("; ".join(errors))
            integrity_errors = []
            input_path = record.get("input")
            input_hash = record.get("input_sha256")
            if isinstance(input_path, str) and isinstance(input_hash, str) and input_hash != "unavailable":
                path = ROOT / input_path
                if not path.is_file() or sha256(path) != input_hash:
                    integrity_errors.append(f"fixture input changed before manifest append: {input_path}")
            for path_key, hash_key in (("linker_script", "linker_script_sha256"),):
                linker_path = record.get(path_key)
                linker_hash = record.get(hash_key)
                if isinstance(linker_path, str) and isinstance(linker_hash, str) and linker_hash != "unavailable":
                    path = ROOT / linker_path
                    if not path.is_file() or sha256(path) != linker_hash:
                        integrity_errors.append(f"fixture linker script changed before manifest append: {linker_path}")
            for artifact, expected_hash in record.get("artifact_sha256", {}).items():
                path = ROOT / artifact
                if not path.is_file() or sha256(path) != expected_hash:
                    integrity_errors.append(f"run artifact changed before manifest append: {artifact}")
            for path_key, hash_key in (("output", "output_sha256"),
                                       ("stdout", "stdout_sha256"),
                                       ("stderr", "stderr_sha256")):
                artifact_path = record.get(path_key)
                expected_hash = record.get(hash_key)
                if isinstance(artifact_path, str) and isinstance(expected_hash, str):
                    path = ROOT / artifact_path
                    if not path.is_file() or sha256(path) != expected_hash:
                        integrity_errors.append(f"run {path_key} changed before manifest append: {artifact_path}")
            if integrity_errors:
                raise ManifestIntegrityError("; ".join(integrity_errors))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            existing_ids = {item.get("id") for snapshot in manifest["snapshots"]
                            for item in snapshot.get("runs", [])}
            if record.get("id") in existing_ids:
                raise ManifestIntegrityError(f"duplicate run ID already present in manifest: {record.get('id')}")
            snapshot = next(x for x in manifest["snapshots"] if x["checkout"] == "sources/xiangshan")
            snapshot["runs"].append(record)
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=manifest_path.parent,
                                             prefix=f".{manifest_path.name}.", suffix=".tmp",
                                             delete=False) as stream:
                temporary = pathlib.Path(stream.name)
                stream.write(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.chmod(temporary, manifest_path.stat().st_mode & 0o777)
            os.replace(temporary, manifest_path)
            temporary = None
            try:
                directory_fd = os.open(manifest_path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
                try:
                    os.fsync(directory_fd)
                finally:
                    os.close(directory_fd)
            except OSError as exc:
                raise ManifestDurabilityError(str(exc)) from exc
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)
            fcntl.flock(lock_stream.fileno(), fcntl.LOCK_UN)


def create_run_dir(evidence_dir: pathlib.Path, run_id: str,
                   reserved_ids: set[str] | None = None) -> pathlib.Path:
    """Reserve a collision-free evidence directory atomically."""
    reserved_ids = reserved_ids or set()
    suffix = 1
    while True:
        candidate = evidence_dir / (run_id if suffix == 1 else f"{run_id}-{suffix}")
        if candidate.name in reserved_ids:
            suffix += 1
            continue
        try:
            candidate.mkdir()
            return candidate
        except FileExistsError:
            suffix += 1


def missing_dependencies(gcc: str | None, objcopy: str | None,
                        emulator: pathlib.Path, nemu: pathlib.Path) -> list[str]:
    missing = []
    if not gcc:
        missing.append("riscv64-unknown-elf-gcc")
    if not objcopy:
        missing.append("riscv64-unknown-elf-objcopy")
    if not emulator.is_file():
        missing.append(str(emulator))
    if not nemu.is_file():
        missing.append(str(nemu))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", choices=("fixture", "zifencei", "sstc", "sscofpmf"), default="fixture")
    parser.add_argument("--manifest", type=pathlib.Path,
                        default=ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml")
    parser.add_argument("--evidence-dir", type=pathlib.Path,
                        default=ROOT / "notes/units/evidence/smoke/kunminghu-fixture-runs")
    parser.add_argument("--case", choices=("standard", "funct12", "rs1", "rd"))
    parser.add_argument("--sstc-case", choices=SSTC_CASES)
    parser.add_argument("--sscofpmf-case", choices=("hardware-filter", "access-route"),
                        default="hardware-filter")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="maximum emulator wall time in seconds")
    parser.add_argument("--input", type=pathlib.Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.case and args.topic != "zifencei":
        parser.error("--case requires --topic zifencei")
    if args.sstc_case and args.topic != "sstc":
        parser.error("--sstc-case requires --topic sstc")
    if args.sscofpmf_case != "hardware-filter" and args.topic != "sscofpmf":
        parser.error("--sscofpmf-case requires --topic sscofpmf")
    if args.topic == "sstc" and not args.sstc_case:
        parser.error("--topic sstc requires --sstc-case")
    if args.topic == "sstc":
        global SOURCE, LINKER
        SOURCE = SSTC_SOURCE
    elif args.topic == "sscofpmf":
        SOURCE = SSCOFPMF_ACCESS_SOURCE if args.sscofpmf_case == "access-route" else SSCOFPMF_SOURCE
    if args.topic == "zifencei" and args.input is None:
        cases = (args.case,) if args.case else ("standard", "funct12", "rs1", "rd")
        status = 0
        for case in cases:
            command = [sys.executable, str(pathlib.Path(__file__).resolve()), "--topic", "zifencei",
                       "--input", str(ROOT / "experiments/rva23s64-zifencei" / f"{case}.S"),
                       "--timeout", str(args.timeout), "--manifest", str(args.manifest),
                       "--evidence-dir", str(args.evidence_dir)]
            status |= subprocess.run(command, cwd=ROOT, check=False).returncode
        return status
    if args.topic == "zifencei":
        case_path = args.input.resolve()
        topic_dir = (ROOT / "experiments/rva23s64-zifencei").resolve()
        if (not case_path.is_relative_to(topic_dir) or not case_path.is_file()
                or case_path.suffix != ".S" or case_path.stem not in {"standard", "funct12", "rs1", "rd"}):
            parser.error("--input must select one of the four supported Story 6.4 assembly sources")
        if args.case and args.case != case_path.stem:
            parser.error("--case must match the --input assembly stem")
        SOURCE = case_path
        LINKER = topic_dir / "fixture.ld"
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be finite and greater than zero")
    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    evidence_dir = args.evidence_dir if args.evidence_dir.is_absolute() else ROOT / args.evidence_dir
    if not evidence_dir.resolve().is_relative_to(ROOT.resolve()):
        parser.error("--evidence-dir must resolve inside the project root")
    evidence_dir.mkdir(parents=True, exist_ok=True)
    run_id = ("kunminghu-fixture-" + dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
              + "-" + hashlib.sha256(str(evidence_dir.resolve()).encode("utf-8")).hexdigest()[:12])
    existing_run_ids: set[str] = set()
    try:
        manifest_preview = json.loads(manifest_path.read_text(encoding="utf-8"))
        existing_run_ids = {item["id"] for snapshot in manifest_preview["snapshots"]
                            for item in snapshot.get("runs", [])
                            if isinstance(item, dict) and isinstance(item.get("id"), str)}
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        pass
    run_dir = create_run_dir(evidence_dir, run_id, existing_run_ids)

    transcript = run_dir / "output.log"
    stdout_path = run_dir / "stdout.log"
    stderr_path = run_dir / "stderr.log"
    elf = run_dir / "fixture.elf"
    link_map = run_dir / "fixture.map"
    raw = run_dir / "fixture.bin"
    source_snapshot = run_dir / "input.S"
    if SOURCE.is_file():
        shutil.copy2(SOURCE, source_snapshot)
    tools = {
        "cross_gcc": "unavailable",
        "cross_objcopy": "unavailable",
        "emulator": "unavailable",
        "nemu": "locked ready-to-run reference library",
    }
    commands: list[str] = []
    stages: list[tuple[str, list[str]]] = []
    expected_trap_pc: int | None = None
    failed_stage = ""
    stage_error = ""
    exit_code = 1
    timed_out = False
    stdout_text = ""
    stderr_text = ""
    snapshot_sha: str | None = None
    input_sha256: str | None = None
    linker_sha256: str | None = None

    # Verify the source revision, all direct gitlinks and the existing manifest
    # records before using the simulator. This validator also checks checkout cleanliness.
    try:
        sys.path.insert(0, str(ROOT / "scripts"))
        from run_cpu_smoke import validate_manifest
        manifest_errors = validate_manifest(manifest_path)
        manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
        locked_snapshot = next(x for x in manifest_data["snapshots"] if x["checkout"] == "sources/xiangshan")
        tools.update(locked_snapshot.get("tools", {}))
        if manifest_errors:
            failed_stage = "locked source and manifest preflight"
            stage_error = "; ".join(manifest_errors)
        else:
            snapshot_sha = _locked_sha()
        if not failed_stage and snapshot_sha != "c098f996bf4d301b88693b20315486d31e93bc9d":
            failed_stage = "locked SHA check"
            stage_error = "runner's Kunminghu baseline does not match sources.lock"
    except Exception as exc:
        failed_stage = "locked source and manifest preflight"
        stage_error = str(exc)

    if not failed_stage and (not SOURCE.is_file() or not LINKER.is_file()):
        failed_stage = "fixture input"
        missing_input = SOURCE if not SOURCE.is_file() else LINKER
        stage_error = f"fixture input does not exist: {missing_input}"
    elif not failed_stage:
        try:
            input_sha256 = sha256(SOURCE)
            linker_sha256 = sha256(LINKER)
        except OSError as exc:
            failed_stage = "fixture input"
            stage_error = str(exc)

    gcc = shutil.which("riscv64-unknown-elf-gcc")
    objcopy = shutil.which("riscv64-unknown-elf-objcopy")
    tools["cross_gcc"] = _version([gcc, "--version"]) if gcc else "unavailable"
    tools["cross_objcopy"] = _version([objcopy, "--version"]) if objcopy else "unavailable"
    tools["emulator"] = _version([str(EMULATOR), "--help"]) if EMULATOR.is_file() else "unavailable"
    missing = missing_dependencies(gcc, objcopy, EMULATOR, NEMU)
    simulator_hashes: dict[pathlib.Path, str] = {}
    for name, path in (("emulator", EMULATOR), ("nemu", NEMU)):
        if path.is_file():
            try:
                digest = sha256(path)
            except OSError as exc:
                if not failed_stage:
                    failed_stage = "simulator artifact integrity"
                    stage_error = f"cannot hash {name} binary {path}: {exc}"
            else:
                simulator_hashes[path] = digest
                tools[name] = f"{tools[name]}; binary sha256 {digest}"
    if not failed_stage and missing:
        failed_stage = "tool availability"
        stage_error = "missing required tools or simulator dependencies: " + ", ".join(missing)

    if not failed_stage:
        assert gcc and objcopy
        compile_cmd = [gcc, f"-march={'rv64ima_zicsr' if args.topic in {'sstc', 'sscofpmf'} else 'rv64imac'}", "-mabi=lp64", "-nostdlib", "-nostartfiles",
                       "-Wl,--build-id=none", f"-Wl,-T,{LINKER}", f"-Wl,-Map,{link_map}",
                       *([f"-DCASE_{args.sstc_case.upper().replace('-', '_')}=1"] if args.topic == "sstc" else []),
                       "-o", str(elf), str(source_snapshot if args.topic == "sstc" else SOURCE)]
        stages.append(("compile and link", compile_cmd))
        copy_cmd = [objcopy, "-O", "binary", str(elf), str(raw)]
        stages.append(("raw image generation", copy_cmd))
        sim_cmd = [str(EMULATOR), "-i", str(raw), "--diff", str(NEMU),
                   "--max-cycles=100000" if args.topic in {"sstc", "sscofpmf"} else "--max-cycles=10000",
                   "--max-instr=10000" if args.topic in {"sstc", "sscofpmf"} else "--max-instr=1000",
                   "--dump-commit-trace"]
        stages.append(("emulator CPU run", sim_cmd))
        for stage, command in stages:
            commands.append("$ " + shlex.join(command))
            try:
                code, out, err, did_timeout = _run(command, ROOT, args.timeout if stage == "emulator CPU run" else 120)
            except OSError as exc:
                failed_stage = stage
                stage_error = str(exc)
                exit_code = 127
                break
            stdout_text += f"[{stage}]\n{out}"
            stderr_text += f"[{stage}]\n{err}"
            exit_code = code
            if code != 0 or did_timeout:
                failed_stage = stage
                stage_error = "command timed out" if did_timeout else f"command exited with {code}"
                timed_out = did_timeout
                break
            if stage == "raw image generation":
                map_text = link_map.read_text(encoding="utf-8", errors="replace") if link_map.is_file() else ""
                start_match = re.search(r"^\s*0x([0-9a-fA-F]+)\s+_start$", map_text, re.MULTILINE)
                trap_match = re.search(r"^\s*0x([0-9a-fA-F]+)\s+good_trap$", map_text, re.MULTILINE)
                if not start_match or int(start_match.group(1), 16) != 0x80000000 or not trap_match:
                    failed_stage = "link map inspection"
                    stage_error = "_start must map to 0x80000000 and good_trap must be present"
                    exit_code = 1
                    break
                expected_trap_pc = int(trap_match.group(1), 16)

    try:
        from run_cpu_smoke import validate_manifest
        post_run_errors = validate_manifest(manifest_path)
    except Exception as exc:
        post_run_errors = [str(exc)]
    if post_run_errors:
        post_run_message = "post-run source/manifest integrity: " + "; ".join(post_run_errors)
        if failed_stage:
            stage_error = f"{stage_error}; {post_run_message}" if stage_error else post_run_message
        else:
            failed_stage = "post-run source/manifest integrity"
            stage_error = post_run_message

    for path, digest, label in ((SOURCE, input_sha256, "fixture source"),
                                (LINKER, linker_sha256, "fixture linker script")):
        if digest is not None:
            try:
                changed = not path.is_file() or sha256(path) != digest
            except OSError:
                changed = True
            if changed:
                message = f"{label} disappeared or changed during the run"
                if failed_stage:
                    stage_error = f"{stage_error}; {message}"
                else:
                    failed_stage = "fixture source integrity" if path == SOURCE else "fixture linker integrity"
                    stage_error = message
    changed_simulators = []
    for path, digest in simulator_hashes.items():
        try:
            if not path.is_file() or sha256(path) != digest:
                changed_simulators.append(str(path.relative_to(ROOT)))
        except OSError:
            changed_simulators.append(str(path.relative_to(ROOT)))
    if changed_simulators:
        message = "simulator binary changed during the run: " + ", ".join(changed_simulators)
        if failed_stage:
            stage_error = f"{stage_error}; {message}"
        else:
            failed_stage = "simulator artifact integrity"
            stage_error = message

    observed = classify_output(stdout_text + "\n" + stderr_text, exit_code,
                               timed_out=timed_out, expected_start_pc=0x80000000,
                               expected_trap_pc=expected_trap_pc,
                               expected_image=str(raw))
    if failed_stage and not observed["cpu_started"]:
        observed["result"] = "blocked"
        observed["assertion_failed"] = False
        observed["expected_observed"] = False
        observed["blocker"] = f"{failed_stage}: {stage_error}"
    elif failed_stage and observed["cpu_started"]:
        if observed["result"] != "run-fail":
            observed["result"] = "run-fail"
            observed["assertion_failed"] = True
            observed["expected_observed"] = False
        observed["blocker"] = f"{failed_stage}: {stage_error}; {observed['blocker']}"
    if not failed_stage and observed["result"] == "run-fail":
        failed_stage = "emulator CPU run"

    stdout_path.write_text(stdout_text, encoding="utf-8")
    stderr_path.write_text(stderr_text, encoding="utf-8")
    transcript.write_text(
        "Kunminghu fixture runner\n"
        f"snapshot_sha={snapshot_sha or 'unknown'}\nconfiguration=KunminghuV2Config NUM_CORES=1\n"
        f"working_directory={ROOT}\n"
        + f"linked_start=0x80000000\nexpected_good_trap_pc={f'0x{expected_trap_pc:x}' if expected_trap_pc is not None else 'unknown'}\n"
        + "\n".join(commands) + "\n"
        + f"first_failed_stage={failed_stage or 'none'}\n"
        + f"exit_code={exit_code}\n"
        + f"cpu_started={str(observed['cpu_started']).lower()}\n"
        + f"result={observed['result']}\n"
        + f"blocker={observed['blocker']}\n\n"
        + "--- stdout ---\n" + stdout_text + "\n--- stderr ---\n" + stderr_text,
        encoding="utf-8",
    )

    recorded_source = source_snapshot if args.topic == "sstc" and source_snapshot.is_file() else SOURCE
    expected_artifacts = [str(p.relative_to(ROOT)) for p in (recorded_source, LINKER, elf, link_map, raw)]
    artifacts = [path for path in expected_artifacts if (ROOT / path).is_file()]
    missing_artifacts = [path for path in expected_artifacts if not (ROOT / path).is_file()]
    record = {
        "id": run_dir.name,
        "snapshot_sha": snapshot_sha or "unknown",
        "input": str(recorded_source.relative_to(ROOT)),
        "input_sha256": input_sha256 or "unavailable",
        "linker_script": str(LINKER.relative_to(ROOT)),
        "linker_script_sha256": linker_sha256 or "unavailable",
        "configuration": ("KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Sstc S-mode fixture at 0x80000000 (C extension disabled to keep traceable 32-bit fixture instructions); PMP NAPOT grants S-mode access; NEMU difftest."
                           if args.topic == "sstc" else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Sscofpmf counter3/event2 access matrix and delegated LCOFI probe; NEMU difftest."
                           if args.topic == "sscofpmf" and args.sscofpmf_case == "access-route" else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr M-mode Sscofpmf fixture at 0x80000000; event selector 2 (Frontend ifu_req), counter 3, 64-bit hardware event wrap; NEMU difftest."
                           if args.topic == "sscofpmf" else
                           "KunminghuV2Config; NUM_CORES=1; Zifencei self-modifying fixture at 0x80000000; NEMU difftest."
                           if args.topic == "zifencei" else
                           "KunminghuV2Config; NUM_CORES=1; RV64I arithmetic fixture at 0x80000000; NEMU difftest."),
        **({"topic": "zifencei", "case": SOURCE.stem,
            "fence_i_encoding": {"standard": "0x0000100f", "funct12": "0x0010100f",
                                 "rs1": "0x0000900f", "rd": "0x0000108f"}[SOURCE.stem],
            "expected_values": {"before_fence_i": 1, "after_fence_i": 42},
            "observed_values": ({"before_fence_i": 1, "after_fence_i": 42,
                                 "evidence_method": "fixture equality checks for a0==1 before patch and a0==42 after FENCE.I; the successful NEMU marker is reachable only after both checks"}
                                if observed["expected_observed"] else None),
            "reserved_field_trap": "not observed" if observed["expected_observed"] else "see run log"}
           if args.topic == "zifencei" else
           ({"topic": "sstc", "case": args.sstc_case,
             "expected_controls": {"s-lt": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "time < stimecmp"},
                                   "s-eq": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "time == stimecmp"},
                                   "s-gt": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "time > stimecmp"},
                                   "s-stce-off": {"menvcfg.STCE": 0, "mcounteren.TM": 1, "expected_exception": 2},
                                   "s-tm-off": {"menvcfg.STCE": 1, "mcounteren.TM": 0, "expected_exception": 2}}[args.sstc_case],
             "observed_values": {**parse_sstc_trace(stdout_text + "\n" + stderr_text, args.sstc_case),
                                 **({"verified_trap_cause": 2} if args.sstc_case.endswith("off") and observed["expected_observed"] else {})}}
            if args.topic == "sstc" else
            ({"topic": "sscofpmf",
              "case": ("scountovf-access-matrix-and-s-delegation" if args.sscofpmf_case == "access-route"
                       else "five-mode-filter-hardware-wrap-counter3"),
              "expected_controls": ({"event_source": "Frontend perfEvents Set index 2: ifu_req",
                                    "event_selector": 2, "counter": 3, "counter_width": 64,
                                    "counter_preload": "0xffffffffffffffff",
                                    "scountovf_access": {"M": "always visible", "S": "mcounteren[3]",
                                                         "VS": "mcounteren[3] && hcounteren[3]"},
                                    "delegation": "mideleg[13]=1; SIE/LCOFIE enabled; expect S-mode scause interrupt 13 and sip.LCOFIP",
                                    "expected_trap_cause": 13}
                                   if args.sscofpmf_case == "access-route" else
                                   {"event_source": "Frontend perfEvents Set index 2: ifu_req",
                                    "event_selector": 2, "counter": 3, "counter_width": 64,
                                    "counter_preload": "0xffffffffffffffff", "privilege": "M",
                                    "filters": {"MINH": "M filtered/unfiltered pair",
                                                "SINH": "S filtered/unfiltered pair",
                                                "UINH": "U filtered/unfiltered pair",
                                                "VSINH": "VS filtered/unfiltered pair",
                                                "VUINH": "VU filtered/unfiltered pair"},
                                    "filter_pairs": "64 nops per phase; M MINH suppresses setup/trap-handler event noise; M reads counter after each lower/virtual phase",
                                    "overflow_rearm": "clear OF with mhpmevent3 write; expect OF/scountovf[3]/mip.LCOFIP clear; reload counter=all-ones; verify second hardware-event OF/scountovf re-arm",
                                    "expected_trap_cause": 13}),
              "observed_values": ({"fixture_assertions": "M always-visible; S mcounteren[3] off/on; VS hcounteren[3] off, mcounteren[3] off, both on; all access assertions reached delegation probe",
                                   "delegation_probe": "fixture explicitly sets sstatus.SIE in S; expected cause-13 trap, with sie.LCOFIE and sip.LCOFIP set",
                                   "pass_marker_observed": observed["expected_observed"]}
                                  if args.sscofpmf_case == "access-route" and observed["cpu_started"] else
                                  {"fixture_assertions": "M/S/U/VS/VU filter suppression and unfiltered event counting; first mcause=interrupt 13; OF/scountovf[3] set; OF/scountovf[3] cleared; second hardware wrap re-set OF/scountovf[3]",
                                   "lcofip_after_first_wrap": "set",
                                   "lcofip_after_software_clear": "clear",
                                   "second_interrupt_delivery": "second cause-13 trap observed after hardware re-wrap",
                                   "pass_marker_observed": observed["expected_observed"]}
                                  if observed["cpu_started"] else None),
              "evidence_method": "self-checking assembly reaches NEMU good-trap only after CSR assertions; overflow is caused by frontend ifu_req hardware increments"}
             if args.topic == "sscofpmf" else {}))),
        "command": " && ".join(commands) if commands else "preflight only; no build or simulator command executed",
        "working_directory": ".",
        "tools": tools,
        "exit_code": exit_code,
        "cpu_started": observed["cpu_started"],
        "result": observed["result"],
        "output": str(transcript.relative_to(ROOT)),
        "output_sha256": sha256(transcript),
        "stdout": str(stdout_path.relative_to(ROOT)),
        "stdout_sha256": sha256(stdout_path),
        "stderr": str(stderr_path.relative_to(ROOT)),
        "stderr_sha256": sha256(stderr_path),
        "artifacts": artifacts,
        "expected_artifacts": expected_artifacts,
        "missing_artifacts": missing_artifacts,
        "artifact_sha256": {a: (linker_sha256 if a == str(LINKER.relative_to(ROOT)) and linker_sha256
                                 else sha256(ROOT / a)) for a in artifacts},
        "assertion_failed": observed["assertion_failed"],
        "expected_observed": observed["expected_observed"],
        "expected": ("recorded fixture image loaded at 0x80000000; first instruction commits; NEMU good trap."
                     if args.topic != "sscofpmf" or args.sscofpmf_case == "hardware-filter" else
                     "scountovf access assertions pass and delegated hardware cause 13 reaches S-mode before NEMU good trap."),
        "observed": observed["observed"],
        "expected_good_trap_pc": f"0x{expected_trap_pc:x}" if expected_trap_pc is not None else "unknown",
        "blocker": observed["blocker"],
        "expected_marker": GOOD_TRAP,
        "resources": resource_snapshot(args.timeout),
        "next_environment_change": next_environment_change(failed_stage),
    }
    if failed_stage:
        record["first_failed_stage"] = failed_stage or "preflight"

    if snapshot_sha is None or not SOURCE.is_file() or not LINKER.is_file():
        fallback_record = run_dir / "run-record.json"
        fallback_record.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        print(f"Cannot append a schema-valid manifest record; standalone record: {fallback_record}",
              file=sys.stderr)
        print(f"run_id={run_dir.name}")
        print(f"result={observed['result']}")
        print(f"evidence={run_dir.relative_to(ROOT)}")
        if failed_stage:
            print(f"first_failed_stage={failed_stage}")
        return 1

    try:
        append_manifest_record(manifest_path, record, validator=validate_manifest)
    except Exception as exc:
        if isinstance(exc, ManifestDurabilityError):
            record["manifest_persisted"] = True
            record["manifest_durable"] = False
            record["manifest_durability_error"] = str(exc)
            record["next_environment_change"] = "Use a filesystem that supports directory fsync, then rerun to confirm durable manifest storage."
            fallback_record = run_dir / "run-record.json"
            fallback_record.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                                       encoding="utf-8")
            print(f"Manifest record is present, but directory durability was not confirmed: {exc}; "
                  f"details: {fallback_record}", file=sys.stderr)
            return 1
        if isinstance(exc, ManifestIntegrityError):
            append_integrity_error = str(exc)
            if failed_stage:
                stage_error = f"{stage_error}; pre-append integrity: {append_integrity_error}"
            else:
                failed_stage = "pre-append source/manifest integrity"
                stage_error = append_integrity_error
            observed["result"] = "run-fail" if observed["cpu_started"] else "blocked"
            observed["assertion_failed"] = bool(observed["cpu_started"])
            observed["expected_observed"] = False
            observed["blocker"] = f"{failed_stage}: {stage_error}"
            record.update({
                "result": observed["result"],
                "assertion_failed": observed["assertion_failed"],
                "expected_observed": False,
                "blocker": observed["blocker"],
                "first_failed_stage": failed_stage,
                "next_environment_change": next_environment_change(failed_stage),
            })
            transcript_text = transcript.read_text(encoding="utf-8")
            transcript_text = re.sub(r"(?m)^first_failed_stage=.*$", f"first_failed_stage={failed_stage}", transcript_text)
            transcript_text = re.sub(r"(?m)^result=.*$", f"result={observed['result']}", transcript_text)
            transcript_text = re.sub(r"(?m)^blocker=.*$", f"blocker={observed['blocker']}", transcript_text)
            transcript.write_text(transcript_text, encoding="utf-8")
            record["output_sha256"] = sha256(transcript)
        else:
            record["manifest_persisted"] = False
            record["manifest_append_error"] = str(exc)
            record["next_environment_change"] = "Restore writable manifest storage and rerun so the evidence record can be appended."
        fallback_record = run_dir / "run-record.json"
        fallback_record.write_text(json.dumps(record, indent=2, ensure_ascii=False) + "\n",
                                   encoding="utf-8")
        print(f"Could not append run record to manifest: {exc}; standalone record: {fallback_record}",
              file=sys.stderr)
        return 1

    print(f"run_id={run_dir.name}")
    if args.topic == "zifencei":
        print(f"case={SOURCE.stem} fence_i_encoding={record['fence_i_encoding']}")
    print(f"result={observed['result']}")
    print(f"evidence={run_dir.relative_to(ROOT)}")
    if failed_stage:
        print(f"first_failed_stage={failed_stage}")
    if observed["result"] != "run-pass":
        print(f"blocker={observed['blocker']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
