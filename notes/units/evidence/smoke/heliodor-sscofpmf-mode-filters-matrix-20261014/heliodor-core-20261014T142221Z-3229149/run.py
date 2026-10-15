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
SSTC_CASES = ("s-lt", "s-eq", "s-gt", "s-stce-off", "s-tm-off",
              "vs-lt", "vs-eq", "vs-gt", "vs-mstce-off", "vs-hstce-off",
              "vs-mtm-off", "vs-htm-off", "vs-route", "vs-hs-route")
SSCOFPMF_CASES = ("hardware-overflow", "mode-filters")
SSCOFPMF_FIXTURES = {
    "hardware-overflow": ("experiments/sscofpmf/heliodor-sscofpmf-v4.hex",
                           "experiments/sscofpmf/heliodor-sscofpmf-v4.S"),
    "mode-filters": ("experiments/sscofpmf/heliodor-sscofpmf-mode-filters-matrix.hex",
                     "experiments/sscofpmf/heliodor-sscofpmf-mode-filters-matrix.S"),
}
SSCOFPMF_LINKER = "experiments/sscofpmf/heliodor-sscofpmf.ld"
SSNPM_CASES = ("pmlen0-canonical", "pmlen0-tagged", "pmlen7-canonical", "pmlen7-tagged", "pmlen7-bit56")
SSNPM_LINKER = ROOT / "experiments/rva23s64-zifencei/fixture.ld"
SSNPM_TOOL_HASHES = {
    "riscv64-unknown-elf-gcc": "3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
    "riscv64-unknown-elf-objcopy": "0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
}

SSTC_CONTROLS = {
    "s-lt": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "time < stimecmp", "delta": 8},
    "s-eq": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "one sampled time value == stimecmp"},
    "s-gt": {"menvcfg.STCE": 1, "mcounteren.TM": 1, "relation": "time > stimecmp", "delta": -8},
    "s-stce-off": {"menvcfg.STCE": 0, "mcounteren.TM": 1, "expected_cause": 2},
    "s-tm-off": {"menvcfg.STCE": 1, "mcounteren.TM": 0, "expected_cause": 2},
    "vs-lt": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "delta": 64, "relation": "guest time < vstimecmp"},
    "vs-eq": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "delta": 0, "relation": "one sampled guest time == vstimecmp"},
    "vs-gt": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "delta": -64, "relation": "guest time > vstimecmp"},
    "vs-mstce-off": {"menvcfg.STCE": 0, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "expected_cause": 2},
    "vs-hstce-off": {"menvcfg.STCE": 1, "henvcfg.STCE": 0, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "expected_cause": 22},
    "vs-mtm-off": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 0, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "expected_cause": 2},
    "vs-htm-off": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 0, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "expected_cause": 22},
    "vs-route": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 1, "expected_mode": "VS", "expected_cause": 5},
    "vs-hs-route": {"menvcfg.STCE": 1, "henvcfg.STCE": 1, "mcounteren.TM": 1, "hcounteren.TM": 1, "htimedelta": "0x10000", "hideleg.VSTIP": 0, "expected_mode": "HS", "expected_cause": 6},
}
for _case, _values in SSTC_CONTROLS.items():
    _values["mcounteren.value"] = "0x2" if _values.get("mcounteren.TM") else "0x0"
    if _case.startswith("vs-"):
        _values["hcounteren.value"] = "0x2" if _values.get("hcounteren.TM") else "0x0"
        _values["hie.VSTIE"] = 1 if _case == "vs-hs-route" else 0


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


def isolated_inputs_sha256(path: pathlib.Path, arch_fixture: str = ARCH_FIXTURE) -> str:
    """Hash copied build inputs while excluding files Veryl generates during a run."""
    h = hashlib.sha256()
    roots = [path / "src", path / "Veryl.toml", path / "Veryl.lock",
             path / "tb/test_smoke.veryl", path / "tb/test_arch_common.veryl",
             path / "test/v4_smoke.hex", path / arch_fixture]
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


def observe(output: str, exit_code: int, arch_label: str = "v4 rv64ui-add") -> tuple[bool, dict[str, int], bool, bool]:
    """Require CPU-produced smoke and ordinary arch-harness observations."""
    smoke_started = bool(re.search(r"\[test_smoke\]\s+cy=\d+.*\bcommit=\d+", output))
    arch_result = re.search(re.escape(arch_label) + r" tohost=([0-9a-fA-F]+) pass=([01])", output)
    arch_started = arch_result is not None
    # For the Zifencei arch-only invocation, the earlier generic smoke marker
    # cannot prove that this separate target began execution. Without an arch
    # result marker, report startup as unobserved (blocked) rather than assert
    # either that the target ran or that it did not.
    target_only_case = arch_label in {"v4 rv64ui-fence_i", "sscofpmf", "supm"} or arch_label.startswith("ssnpm ")
    cpu_started = arch_started if target_only_case else (smoke_started or arch_started)
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
              f"{arch_label} PASS" in output and exit_code == 0)
    failed = cpu_started and not passed
    return cpu_started, values, passed, failed


def expected_arch_marker(arch_label: str, *, zifencei_case: bool = False,
                         sscofpmf: bool = False, ssnpm_case: str | None = None) -> str:
    """Return the marker that identifies the selected arch target."""
    return f"{arch_label} PASS" if zifencei_case or sscofpmf or ssnpm_case or arch_label == "supm" else "[test_smoke] PASS"


def sscofpmf_observed_values(case: str, values: dict[str, int], passed: bool) -> dict | None:
    if passed and case == "hardware-overflow":
        return {"tohost": 1, "pass": True, "cause13_traps": 2,
                "fixture_assertions": "MINH filtering, hardware counter wrap, cause 13, OF, scountovf[3], mip.LCOFIP, OF clear, pending withdrawal, and second hardware wrap/interrupt"}
    if passed and case == "mode-filters":
        return {"tohost": 1, "pass": True,
                "fixture_assertions": "S/SINH and U/UINH inhibit and resume phases all passed"}
    if case == "mode-filters" and values.get("arch_tohost") == 21:
        return {"partial_observations": {"S with SINH=1": "counter read was zero; fixture advanced past the inhibit assertion"},
                "unverified": ["S with SINH=0", "U with UINH=1", "U with UINH=0"]}
    if case == "mode-filters" and values.get("arch_tohost") == 54:
        return {"partial_observations": {
                    "S with SINH=1": "counter read was zero",
                    "S with SINH=0": "counter read was nonzero",
                    "U with UINH=1": "counter read was zero",
                    "U with UINH=0": "counter read was zero; expected nonzero"
                }, "mismatch": "U-mode counter did not advance after UINH was cleared"}
    return None


def transform_testbench(original: str) -> str:
    if original.count(IMEM_DECL) != 1:
        raise ValueError("pinned test_smoke imem declaration drifted; re-review workaround anchor")
    return original.replace(IMEM_DECL, "    #[allow(initial_assign)]\n" + IMEM_DECL, 1)


def transform_arch_harness(original: str, *, target: str = "test_arch_rv64ui_add", fixture: str = ARCH_FIXTURE, label: str = "v4 rv64ui-add", mtime_enable: bool = False, arch_cycles: int = 200000) -> str:
    """Keep the ordinary harness and one RV64UI target; omit the debug harness and unrelated tests."""
    if original.count(ARCH_DEBUG_MARKER) != 1 or original.count(ARCH_DRAM_DECL) != 1:
        raise ValueError("pinned arch harness boundary/DRAM declaration drifted; re-review isolation workaround")
    target_marker = f"#[test({target})]\nmodule {target}"
    source_target = target
    if original.count(target_marker) != 1:
        # SSTC uses the pinned, ordinary arch target's RAM/tohost harness shape,
        # with a local fixture path and label substituted in the isolated copy.
        source_target = "test_arch_rv64ui_add"
        target_marker = ARCH_TARGET_MARKER
    if original.count(target_marker) != 1:
        raise ValueError(f"pinned {target} target drifted; re-review selected target")
    normal_harness = original.split(ARCH_DEBUG_MARKER, 1)[0]
    normal_harness = normal_harness.replace(
        ARCH_DRAM_DECL, "    #[allow(initial_assign)]\n" + ARCH_DRAM_DECL, 1)
    target_start = original.index(target_marker)
    next_target = original.find("\n#[test(", target_start + len(target_marker))
    if next_target < 0:
        next_target = len(original)
    selected_target = original[target_start:next_target].strip() + "\n"
    if target != source_target:
        selected_target = selected_target.replace(source_target, target)
    if fixture != ARCH_FIXTURE or label != "v4 rv64ui-add":
        hex_path_pattern = r'HEX_FILE\s*:\s*"[^"]+"'
        if len(re.findall(hex_path_pattern, selected_target)) != 1:
            raise ValueError(f"pinned {target} HEX_FILE anchor drifted; expected exactly one path")
        selected_target = re.sub(hex_path_pattern, f'HEX_FILE  : "{fixture}"', selected_target, count=1)
        selected_target = selected_target.replace("v4 rv64ui-add", label)
    if arch_cycles != 200000:
        selected_target, changed = re.subn(r"clk\.next\s*\(\s*200000\s*\);",
                                           f"clk.next  ({arch_cycles});", selected_target)
        if changed != 1:
            raise ValueError(f"pinned {target} cycle-budget anchor drifted")
    if mtime_enable:
        normal_harness, changed = re.subn(
            r"o_tohost\s*:\s*output\s+logic<32>\s*,",
            "o_tohost: output logic<32>,\n    o_sstc_sample_time: output logic<32>,\n    o_sstc_compare: output logic<32>,\n    o_sstc_time_after: output logic<32>,",
            normal_harness, count=1)
        if changed != 1:
            raise ValueError("pinned arch harness lacks the tohost output anchor")
        normal_harness, changed = re.subn(
            r"assign\s+o_tohost\s*=\s*tohost_lo\s*;",
            "assign o_tohost = tohost_lo;\n"
            "    assign o_sstc_sample_time = dram[TOHOST_IDX[19:0] + 20'd1];\n"
            "    assign o_sstc_compare = dram[TOHOST_IDX[19:0] + 20'd2];\n"
            "    assign o_sstc_time_after = dram[TOHOST_IDX[19:0] + 20'd3];",
            normal_harness, count=1)
        if changed != 1:
            raise ValueError("pinned arch harness lacks the tohost assignment anchor")
        selected_target, changed = re.subn(
            r"(var\s+tohost\s*:\s*logic<32>\s*;)",
            r"\1\n    var sstc_sample_time: logic<32>;\n"
            "    var sstc_compare: logic<32>;\n"
            "    var sstc_time_after: logic<32>;",
            selected_target, count=1)
        if changed != 1:
            raise ValueError("selected SSTC target lacks the tohost signal anchor")
        selected_target, changed = re.subn(
            r"o_tohost\s*:\s*tohost\s*,",
            "o_tohost: tohost,\n"
            "        o_sstc_sample_time: sstc_sample_time,\n"
            "        o_sstc_compare: sstc_compare,\n"
            "        o_sstc_time_after: sstc_time_after,",
            selected_target, count=1)
        if changed != 1:
            raise ValueError("selected SSTC target lacks the tohost port connection anchor")
        display_pattern = r'(\$display\s*\("' + re.escape(label) + r' tohost=%h pass=%b",\s*tohost,\s*pass\);)'
        selected_target, changed = re.subn(
            display_pattern,
            f'$display ("{label} tohost=%h pass=%b sample_time=%h cmp=%h time_after=%h", '
            "tohost, pass, sstc_sample_time, sstc_compare, sstc_time_after);",
            selected_target, count=1)
        if changed != 1:
            raise ValueError("selected SSTC target lacks its result display anchor")
        selected_target, changed = re.subn(r"TOHOST_IDX\s*:\s*1024\s*,", "TOHOST_IDX: 1024, MTIME_EN: 1'b1,", selected_target, count=1)
        if changed != 1:
            raise ValueError("pinned arch target lacks TOHOST_IDX anchor for MTIME_EN")
        # The isolated SSTC harness advances its free-running cycle counter,
        # but expose time at 1/256 that rate so firmware can sample a stable
        # timer value, program the comparator, and verify the requested edge.
        normal_harness, changed = re.subn(r"i_mtime\s*:\s*mtime_ctr\s*,", "i_mtime: mtime_ctr >> 8,", normal_harness, count=1)
        if changed != 1:
            raise ValueError("pinned arch harness lacks the mtime input anchor")
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
    zifencei_case = getattr(args, "zifencei_case", None)
    sstc_case = getattr(args, "sstc_case", None)
    sscofpmf = getattr(args, "topic", "smoke") == "sscofpmf"
    sscofpmf_case = getattr(args, "sscofpmf_case", None) or "hardware-overflow"
    sscofpmf_fixture, sscofpmf_source = SSCOFPMF_FIXTURES[sscofpmf_case]
    arch_cycles = 1000000 if sscofpmf and sscofpmf_case == "mode-filters" else 200000
    ssnpm_case = getattr(args, "ssnpm_case", None)
    ssnpm = bool(ssnpm_case)
    arch_target = "test_arch_rv64ui_add"
    arch_label = "v4 rv64ui-add"
    fixture_rel = ARCH_FIXTURE
    if zifencei_case:
        fixture_rel = f"test/zifencei/{zifencei_case}.hex"
        arch_target = "test_arch_rv64ui_fence_i"
        arch_label = "v4 rv64ui-fence_i"
    elif sstc_case:
        fixture_rel = f"experiments/sstc/heliodor/{sstc_case}.hex"
        arch_target = "test_arch_rv64ui_sstc"
        arch_label = f"sstc {sstc_case}"
    elif sscofpmf:
        fixture_rel = sscofpmf_fixture
        arch_target = "test_arch_sscofpmf"
        arch_label = "sscofpmf"
    elif ssnpm:
        fixture_rel = f"experiments/ssnpm/heliodor/{ssnpm_case}.hex"
        arch_target = "test_arch_rv64ui_ssnpm"
        arch_label = f"ssnpm {ssnpm_case}"
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
    snapshot_sha = LOCKED_SHA; input_path = ((ROOT / "experiments/rva23s64-zifencei" / f"{zifencei_case}.hex") if zifencei_case else (ROOT / "experiments/sstc/heliodor" / f"{sstc_case}.hex") if sstc_case else (ROOT / fixture_rel) if ssnpm or sscofpmf else SOURCE / fixture_rel)
    archived_arch_fixture = archive / (f"zifencei-{zifencei_case}.hex" if zifencei_case else f"sstc-{sstc_case}.hex" if sstc_case else f"sscofpmf-{sscofpmf_case}.hex" if sscofpmf else f"ssnpm-{ssnpm_case}.hex" if ssnpm else "rv64ui-add.hex")
    ssnpm_build_record: dict = {}
    # Snapshot the exact arch input before source preflight so even blocked runs
    # retain a stable, hash-verifiable input artifact.
    if input_path.is_file():
        shutil.copy2(input_path, archived_arch_fixture)
    smoke_input_path = SOURCE / "test/v4_smoke.hex"
    input_hash = sha256(input_path) if input_path.is_file() else "0" * 64
    smoke_input_hash = sha256(smoke_input_path) if smoke_input_path.is_file() else "0" * 64
    tools: dict[str, str] = {"veryl": "unavailable", "verilator": "unavailable", "cxx": "unavailable"}
    command: list[str] = []
    commands: list[list[str]] = []
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
        if ssnpm:
            for name, expected_hash in SSNPM_TOOL_HASHES.items():
                binary_path = shutil.which(name)
                if not binary_path or sha256(pathlib.Path(binary_path)) != expected_hash:
                    raise ValueError(f"{name} unavailable or differs from pinned Story 6.1 SHA-256")
                tools[name] = f"{subprocess.check_output([binary_path, '--version'], text=True).splitlines()[0]}; binary sha256 {expected_hash}"
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
        transformed_arch = transform_arch_harness(arch_source.read_text(encoding="utf-8"), target=arch_target, fixture=fixture_rel, label=arch_label, mtime_enable=bool(sstc_case), arch_cycles=arch_cycles)
        (work / "tb/test_arch_common.veryl").write_text(transformed_arch, encoding="utf-8")
        shutil.copy2(smoke_input_path, work / "test/v4_smoke.hex")
        arch_fixture = work / fixture_rel
        arch_fixture.parent.mkdir(parents=True)
        shutil.copy2(input_path, arch_fixture)
        isolated_tree_hash = tree_sha256(work)
        isolated_inputs_hash = isolated_inputs_sha256(work, fixture_rel)
        transformed_hash = sha256(work / "tb/test_smoke.veryl")
        transformed_arch_hash = sha256(work / "tb/test_arch_common.veryl")
        fixture_hash = sha256(arch_fixture)
        smoke_fixture_hash = sha256(work / "test/v4_smoke.hex")
        if fixture_hash != input_hash or smoke_fixture_hash != smoke_input_hash:
            raise ValueError("copied smoke/arch fixture SHA-256 differs from locked input")
        shutil.copy2(work / "tb/test_smoke.veryl", archive / "test_smoke.veryl")
        shutil.copy2(work / "test/v4_smoke.hex", archive / "v4_smoke.hex")
        shutil.copy2(work / "tb/test_arch_common.veryl", archive / "test_arch_common.veryl")
        shutil.copy2(arch_fixture, archived_arch_fixture)
        if sscofpmf:
            shutil.copy2(ROOT / sscofpmf_source, archive / pathlib.Path(sscofpmf_source).name)
            shutil.copy2(ROOT / SSCOFPMF_LINKER, archive / pathlib.Path(SSCOFPMF_LINKER).name)
        if ssnpm:
            shutil.copy2(ROOT / "experiments/ssnpm/build_heliodor_fixtures.py", archive / "build_heliodor_fixtures.py")
            shutil.copy2(input_path.with_suffix(".S"), archive / f"{ssnpm_case}.S")
            build_record_path = input_path.with_suffix(".build.json")
            ssnpm_build_record = json.loads(build_record_path.read_text(encoding="utf-8"))
            shutil.copy2(build_record_path, archive / f"{ssnpm_case}.build.json")
            shutil.copy2(SSNPM_LINKER, archive / "fixture.ld")
        for test_name in ("test_smoke", arch_target):
            first_stage = test_name
            command = [binary, "test", "--include-ignored", "--test", test_name]
            commands.append(command)
            exit_code, child_out, child_err, timeout_error = execute_test(command, work, args.timeout)
            out.extend(child_out); err.extend(child_err)
            blocker = timeout_error or blocker
            if timeout_error or exit_code != 0:
                break
        combined = (out + err).decode("utf-8", "replace")
        cpu_started, values, expected_observed, assertion_failed = observe(combined, exit_code, arch_label)
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
        if isolated_inputs_sha256(work, fixture_rel) != isolated_inputs_hash:
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
    sstc_observed = None
    if sstc_case:
        text_out = bytes(out).decode("utf-8", errors="replace")
        marker = re.search(rf"sstc {re.escape(sstc_case)} tohost=([0-9a-fA-F]+) pass=([01])(?: sample_time=([0-9a-fA-F]+) cmp=([0-9a-fA-F]+) time_after=([0-9a-fA-F]+))?", text_out)
        if marker:
            value = int(marker.group(1), 16)
            mode = "VS" if sstc_case.startswith("vs-") else "S"
            if value == 0x210:
                sstc_observed = {"tohost": value, "trap_observed": False, "cause": None,
                                 "mode": mode, "pc": "target_access+4; CSR write completed and fallthrough marker executed"}
            elif value == 0x211:
                sstc_observed = {"tohost": value, "trap_observed": False, "cause": None,
                                 "mode": mode, "pc": "bounded pending poll exhausted"}
            elif value > 0xFFFF:
                sstc_observed = {"tohost": value, "trap_observed": True,
                                 "cause": value >> 16,
                                 "mode": "unknown (trap origin is not encoded)" if sstc_case.startswith("vs-") else "M",
                                 "pc_offset_from_target_access": value & 0xFFFF}
            else:
                sstc_observed = {"tohost": value, "pass": marker.group(2) == "1",
                                 "fixture_assertions": "comparator/pending/cause/routing checks precede tohost=1" if value == 1 else "see marker-specific fixture path"}
            observes_comparator = sstc_case in {"s-lt", "s-eq", "s-gt", "vs-lt", "vs-eq", "vs-gt", "vs-route", "vs-hs-route"}
            if observes_comparator and sstc_observed is not None and marker.group(3) is not None:
                sstc_observed["sampled_time"] = int(marker.group(3), 16)
                sstc_observed["comparator"] = int(marker.group(4), 16)
                sstc_observed["time_after_write"] = int(marker.group(5), 16)
    record = {
        **({"topic": "ssnpm", "case": ssnpm_case,
            "expected_controls": {"effective_privilege": "U", "instruction_family": "integer load/store", "instruction": "ld",
                                  "senvcfg.PMM": 2 if ssnpm_case.startswith("pmlen7-") else 0,
                                  "PMLEN": 7 if ssnpm_case.startswith("pmlen7-") else 0,
                                  "senvcfg.PMM_readback": 2 if ssnpm_case.startswith("pmlen7-") else 0,
                                  "input_address": "probe_data | 0x0100000000000000 (bit 56 set)" if ssnpm_case == "pmlen7-bit56" else "probe_data | 0xfe00000000000000" if ssnpm_case.endswith("-tagged") else "canonical probe_data",
                                  "expected_effective_address": "PMLEN7 VA sign-extends bit 56" if ssnpm_case == "pmlen7-bit56" else "probe_data" if ssnpm_case not in {"pmlen0-tagged"} else "unmasked tagged VA faults",
                                  "expected_trap_cause": 5 if ssnpm_case == "pmlen0-tagged" else None,
                                  "expected_trap_mepc": "tagged_load" if ssnpm_case == "pmlen0-tagged" else None,
                                  "expected_trap_mtval": "probe_data | 0xfe00000000000000" if ssnpm_case == "pmlen0-tagged" else None,
                                  "expected_stored_and_loaded_value": "0x5678" if ssnpm_case != "pmlen0-tagged" else None},
            "observed_values": ({"tohost": 1, "pass": True,
                                 "fixture_assertions": "M-mode senvcfg.PMM readback; U-mode store/load result or tagged-load cause/mepc/mtval checks",
                                 "harness_limit": "high-address accesses are indexed by low DRAM address bits; raw and masked addresses are not distinguished"}
                                if expected_observed else None),
            "fixture_linker_script": str((archive / "fixture.ld").relative_to(ROOT)),
            "fixture_linker_sha256": sha256(archive / "fixture.ld"),
            "fixture_build_commands": {"gcc": ssnpm_build_record.get("gcc_argv"), "objcopy": ssnpm_build_record.get("objcopy_argv")},
            "evidence_method": "U-mode fixture stores and reloads through canonical/tagged/boundary pointer; PMLEN0 tagged pass requires cause 5 at tagged_load with matching mtval"} if ssnpm else {}),
        **({"topic": "zifencei", "case": zifencei_case, "fence_i_encoding": {"standard": "0x0000100f", "funct12": "0x0010100f", "rs1": "0x0000900f", "rd": "0x0000108f"}[zifencei_case], "expected_values": {"before_fence_i": 1, "after_fence_i": 42}, "observed_values": {"before_fence_i": 1, "after_fence_i": 42, "evidence_method": "fixture equality checks for a0==1 before patch and a0==42 after FENCE.I; successful tohost/pass marker is reachable only after both checks"} if expected_observed else None, "reserved_field_trap": "no trap prevented the pass marker; trap-cause telemetry unavailable" if expected_observed else "startup/result not established or see run log; harness does not expose trap cause"} if zifencei_case else {}),
        **({"topic": "sscofpmf", "case": sscofpmf_case,
            "expected_controls": ({"event_selector": 5, "counter": 3, "counter_width": 64,
                                  "counter_preload": "0xffffffffffffffff", "privilege": "M",
                                  "filter_phase": "MINH=1 then MINH=0", "expected_trap_cause": 13,
                                  "pending": "mip.LCOFIP checked at each cause-13 handler; first pending is cleared separately before re-arm"} if sscofpmf_case == "hardware-overflow" else
                                  {"event_selector": 5, "counter": 3, "counter_width": 64,
                                   "privilege_modes": ["S", "U"], "filter_phases": ["SINH=1 then 0", "UINH=1 then 0"],
                                   "expected_counter_behavior": "zero while inhibited, nonzero after filter clear"}),
            "observed_values": sscofpmf_observed_values(sscofpmf_case, values, expected_observed),
            "fixture_build": {"source": sscofpmf_source, "source_sha256": sha256(ROOT / sscofpmf_source),
                              "linker": SSCOFPMF_LINKER, "linker_sha256": sha256(ROOT / SSCOFPMF_LINKER),
                              "gcc": "riscv64-unknown-elf-gcc () 15.1.0; sha256 3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
                              "objcopy": "GNU objcopy 2.44; sha256 0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
                              "command": f"riscv64-unknown-elf-gcc -march=rv64imafdc_zicsr -mabi=lp64d -nostdlib -nostartfiles -ffreestanding -T {SSCOFPMF_LINKER} -Wl,--build-id=none -o {pathlib.Path(sscofpmf_source).with_suffix('.elf').name} {pathlib.Path(sscofpmf_source).name} && riscv64-unknown-elf-objcopy -O binary {pathlib.Path(sscofpmf_source).with_suffix('.elf').name} {pathlib.Path(sscofpmf_source).with_suffix('.bin').name} && python3 sources/heliodor/test/c/bin2hex.py {pathlib.Path(sscofpmf_source).with_suffix('.bin').name} {pathlib.Path(sscofpmf_fixture).name}"},
            "evidence_method": ("Self-checking local assembly; event5 mem-port-busy increments cause hardware wraps; MIP.LCOFIP is read in each cause-13 handler" if sscofpmf_case == "hardware-overflow" else "Self-checking local assembly; event5 mem-port-busy counter reads assert SINH/UINH inhibition and resume in S/U mode")} if sscofpmf else {}),
        **({"topic": "sstc", "case": sstc_case,
            "expected_controls": {**SSTC_CONTROLS.get(sstc_case, {}), "mtime_enabled": True, "mtime_observation": "harness counter increments each cycle; CSR time is mtime_ctr >> 8"},
            "observed_values": sstc_observed,
            "evidence_method": "case-specific assembly checks enforce expected architecture state; pending uses a bounded loop, without a cycle-exact latency requirement"} if sstc_case else {}),
        "id": run_id, "snapshot_sha": snapshot_sha,
        "input": str(archived_arch_fixture.relative_to(ROOT)) if archived_arch_fixture.is_file() else str(input_path.relative_to(ROOT)),
        "input_sha256": input_hash,
        "inputs": [{"path": "sources/heliodor/test/v4_smoke.hex", "sha256": smoke_input_hash},
                   {"path": str(archived_arch_fixture.relative_to(ROOT)) if archived_arch_fixture.is_file() else str(input_path.relative_to(ROOT)), "sha256": input_hash},
                   *([{"path": sscofpmf_source, "sha256": sha256(ROOT / sscofpmf_source)},
                      {"path": SSCOFPMF_LINKER, "sha256": sha256(ROOT / SSCOFPMF_LINKER)}] if sscofpmf else [])],
        "configuration": (f"Heliodor test_smoke plus isolated test_arch_rv64ui_ssnpm ({ssnpm_case}); one harness/DUT; U-mode senvcfg.PMM PMLEN/tagged-pointer probe." if ssnpm else
                          f"Heliodor test_smoke plus {arch_target}; one harness/DUT; 5000 smoke cycles and 300000 arch cycles; expected Zifencei old/new return 1/42 and tohost=1." if zifencei_case else
                          f"Heliodor test_smoke plus {arch_target}; one harness/DUT; 5000 smoke cycles and {arch_cycles} Sscofpmf arch cycles; event5 mem-port-busy, counter3; expected tohost=1 after {sscofpmf_case} assertions." if sscofpmf else
                          f"Heliodor test_smoke plus {arch_target}; one harness/DUT; 5000 smoke cycles and 300000 arch cycles; mtime counter increments each cycle and CSR time is mtime_ctr >> 8; controls={SSTC_CONTROLS.get(sstc_case, {})}; expected tohost=1." if sstc_case else
                          "Heliodor test_smoke plus test_arch_rv64ui_add; one harness/DUT; 5000 smoke cycles and 300000 arch cycles; expected x10=7, x11=11, x12=77, x13=11 and tohost=1."),
        "command": json.dumps(([ [sys.executable, str(ROOT / "experiments/ssnpm/build_heliodor_fixtures.py")] ] if ssnpm else []) + commands, ensure_ascii=False) if commands else "preflight not reached",
        "working_directory": str(work) if work else str(ROOT), "tools": tools,
        "exit_code": exit_code, "cpu_started": cpu_started,
        "result": "run-pass" if expected_observed else ("run-fail" if cpu_started and assertion_failed else "blocked"),
        "assertion_failed": assertion_failed, "expected_observed": expected_observed,
        "expected": (f"U-mode Ssnpm fixture {ssnpm_case} verifies senvcfg.PMM readback and expected explicit access behavior before tohost=1/pass=1." if ssnpm else
                     "test_smoke registers pass; Zifencei fixture checks old return 1 then new return 42 and reports tohost=1/pass=1." if zifencei_case else
                     "Heliodor Sscofpmf fixture checks MINH filtering, hardware event5 counter3 wrap, cause 13, OF, and scountovf[3] before tohost=1." if sscofpmf else
                     f"Heliodor fixture {sstc_case} asserts its named Sstc condition and reports tohost=1." if sstc_case else
                     "Both CPU tests pass: test_smoke reports x10=7, x11=11, x12=77, x13=11; test_arch_rv64ui_add reports tohost=1/pass=1 and its PASS marker."),
        "observed": f"CPU-start={cpu_started}; results={values if 'values' in locals() else {}}; smoke_marker={'[test_smoke] PASS' in (out + err).decode('utf-8','replace')}; arch_marker={f'{arch_label} PASS' in (out + err).decode('utf-8','replace')}",
        "output": str(combined_path.relative_to(ROOT)), "output_sha256": sha256(combined_path),
        "stdout": str(stdout_path.relative_to(ROOT)) if stdout_path.is_relative_to(ROOT) else str(stdout_path),
        "stdout_sha256": sha256(stdout_path),
        "stderr": str(stderr_path.relative_to(ROOT)) if stderr_path.is_relative_to(ROOT) else str(stderr_path),
        "stderr_sha256": sha256(stderr_path),
        "artifacts": [str(p.relative_to(ROOT)) for p in
                      [archive / "run.py", archive / "test_smoke.veryl", archive / "v4_smoke.hex",
                       archive / "build_heliodor_fixtures.py", archive / f"{ssnpm_case}.S",
                       *( [archive / pathlib.Path(sscofpmf_source).name, archive / pathlib.Path(SSCOFPMF_LINKER).name] if sscofpmf else [])] if p.is_file()],
        "artifact_sha256": {}, "expected_marker": expected_arch_marker(
            arch_label, zifencei_case=bool(zifencei_case), sscofpmf=sscofpmf, ssnpm_case=ssnpm_case), "blocker": blocker,
        "log_path_warnings": log_persistence_errors,
        "first_failed_stage": first_stage if not expected_observed else "",
        "resources": resource_snapshot(args.timeout),
        "next_environment_change": next_environment_change(first_stage if not expected_observed else "", blocker),
        "source_tree_sha256": source_tree_hash, "source_commit": snapshot_sha,
        "isolated_tree_sha256": isolated_tree_hash,
        "isolated_inputs_sha256": isolated_inputs_hash,
        "expected_markers": ["[test_smoke] PASS", f"{arch_label} PASS"],
        "transformed_test_sha256": transformed_hash,
        "transformed_arch_harness_sha256": transformed_arch_hash,
        "fixture_sha256": fixture_hash, "smoke_fixture_sha256": smoke_fixture_hash,
        "run_seconds": round(time.time() - started_at, 3),
    }
    # Archive the exact runner before recording artifact identities so later
    # runner edits cannot invalidate this run's provenance.
    runner_snapshot = archive / "run.py"
    shutil.copy2(pathlib.Path(__file__).resolve(), runner_snapshot)
    artifact_names = ["run.py", "test_smoke.veryl", "v4_smoke.hex", "test_arch_common.veryl", archived_arch_fixture.name]
    if ssnpm:
        artifact_names.extend(["build_heliodor_fixtures.py", f"{ssnpm_case}.S", f"{ssnpm_case}.build.json", "fixture.ld"])
    record["artifact_sha256"] = {str((archive / n).relative_to(ROOT)): sha256(archive / n)
                                 for n in artifact_names if (archive / n).is_file()}
    record["artifacts"] = [str((archive / n).relative_to(ROOT)) for n in
                            artifact_names if (archive / n).is_file()]
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
    parser.add_argument("--topic", choices=("smoke", "zifencei", "sstc", "sscofpmf", "ssnpm"), default="smoke")
    parser.add_argument("--case", choices=("standard", "funct12", "rs1", "rd"))
    parser.add_argument("--sstc-case", choices=SSTC_CASES)
    parser.add_argument("--ssnpm-case", choices=SSNPM_CASES)
    parser.add_argument("--sscofpmf-case", choices=SSCOFPMF_CASES)
    args = parser.parse_args()
    if args.timeout <= 0 or not (args.timeout < float("inf")):
        parser.error("--timeout must be finite and positive")
    if args.sstc_case and args.topic != "sstc":
        parser.error("--sstc-case requires --topic sstc")
    if args.ssnpm_case and args.topic != "ssnpm":
        parser.error("--ssnpm-case requires --topic ssnpm")
    if args.sscofpmf_case and args.topic != "sscofpmf":
        parser.error("--sscofpmf-case requires --topic sscofpmf")
    if args.topic == "zifencei":
        if args.case:
            args.zifencei_case = args.case
            try:
                record = run(args)
                return 0 if record["result"] == "run-pass" else 1
            except ValueError as exc:
                parser.error(str(exc))
        status = 0
        for case in ("standard", "funct12", "rs1", "rd"):
            args.zifencei_case = case
            record = run(args)
            status |= 0 if record["result"] == "run-pass" else 1
        return status
    if args.topic == "sstc":
        if args.case:
            parser.error("--case is for zifencei; use --sstc-case")
        if args.sstc_case:
            cases = (args.sstc_case,)
        else:
            cases = SSTC_CASES
        status = 0
        built_groups: set[str] = set()
        for case in cases:
            group = "vs" if case.startswith("vs-") else "s"
            if group not in built_groups:
                builder = ROOT / f"experiments/sstc/heliodor/build_heliodor_{group}_fixtures.py"
                build = subprocess.run([sys.executable, str(builder)], cwd=ROOT, check=False)
                if build.returncode:
                    status |= build.returncode
                    continue
                built_groups.add(group)
            args.sstc_case = case
            record = run(args)
            status |= 0 if record["result"] == "run-pass" else 1
        return status
    if args.topic == "sscofpmf":
        record = run(args)
        return 0 if record["result"] == "run-pass" else 1
    if args.topic == "ssnpm":
        if args.case or args.sstc_case:
            parser.error("--case and --sstc-case do not apply to --topic ssnpm")
        build = subprocess.run([sys.executable, str(ROOT / "experiments/ssnpm/build_heliodor_fixtures.py")], cwd=ROOT, check=False)
        if build.returncode:
            return build.returncode
        cases = (args.ssnpm_case,) if args.ssnpm_case else SSNPM_CASES
        status = 0
        for case in cases:
            args.ssnpm_case = case
            record = run(args)
            status |= 0 if record["result"] == "run-pass" else 1
        return status
    try:
        record = run(args)
        return 0 if record["result"] == "run-pass" else 1
    except ValueError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
