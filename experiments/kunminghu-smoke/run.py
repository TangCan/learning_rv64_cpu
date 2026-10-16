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
LD_SOURCE = ROOT / "experiments/rv64-ld-probe/ld.S"
LD_LINKER = ROOT / "experiments/rv64-ld-probe/fixture.ld"
LINKER = ROOT / "experiments/kunminghu-smoke/fixture.ld"
LD_EXPECTED_INSTRUCTION = 0x0002B303  # ld t1, 0(t0)
LD_EXPECTED_VALUE = 0x123456789ABCDEF0
SSTC_SOURCE = ROOT / "experiments/sstc/kunminghu-full-matrix.S"
SSCOFPMF_SOURCE = ROOT / "experiments/sscofpmf/kunminghu-sscofpmf-complete-v5.S"
SSCOFPMF_ACCESS_SOURCE = ROOT / "experiments/sscofpmf/kunminghu-sscofpmf-access-route-v6.S"
SSNPM_SOURCE = ROOT / "experiments/kunminghu-smoke/ssnpm.S"
SSSTATEEN_SOURCE = ROOT / "experiments/ssstateen/kunminghu_probe_operation_ids.S"
SSSTATEEN_VIRTUAL_SOURCE = ROOT / "experiments/ssstateen/kunminghu_probe_hs_vs.S"
SSSTATEEN_VS_GATE_SOURCE = ROOT / "experiments/ssstateen/kunminghu_probe_hs_vs_gates.S"
SSSTATEEN_VU_SOURCE = ROOT / "experiments/ssstateen/kunminghu_probe_hs_vu.S"
SSSTATEEN_M_S_SOURCE = ROOT / "experiments/ssstateen/kunminghu_probe_m_s.S"
SSSTATEEN_LINKER = ROOT / "experiments/ssstateen/ssstateen_probe.ld"
SSSTATEEN_CSRS = {0x10c: "sstateen0", 0x10d: "sstateen1", 0x10e: "sstateen2", 0x10f: "sstateen3",
                  0x60c: "hstateen0", 0x60d: "hstateen1", 0x60e: "hstateen2", 0x60f: "hstateen3",
                  0x30c: "mstateen0", 0x30d: "mstateen1", 0x30e: "mstateen2", 0x30f: "mstateen3",
                  0x10a: "senvcfg", 0x60a: "henvcfg"}
SSSTATEEN_OTHER_CSRS = {0x301: "misa", 0x001: "fflags"}
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


def parse_ld_commit(output: str, target_pc: int, data_address: int) -> dict[str, object] | None:
    """Match the fixture's LD retirement and recover its base from committed state."""
    registers: dict[int, int] = {}
    matches = []
    pattern = re.compile(
        r"commit pc\s+([0-9a-fA-F]{16}) inst\s+([0-9a-fA-F]{8}) "
        r"wen\s+(\d+) dst\s+([0-9a-fA-F]{2}) data\s+([0-9a-fA-F]{16})")
    for line in output.splitlines():
        match = pattern.search(line)
        if not match:
            continue
        pc, instruction, rd, value = (int(match.group(i), 16) for i in (1, 2, 4, 5))
        wen = int(match.group(3), 10)
        if pc == target_pc:
            rs1 = (instruction >> 15) & 0x1F
            immediate = (instruction >> 20) & 0xFFF
            if immediate & 0x800:
                immediate -= 0x1000
            base = registers.get(rs1)
            matches.append({
                "pc": pc, "instruction": instruction, "write_enable": wen,
                "rd": rd, "value": value,
                "effective_address": base + immediate if base is not None else None,
            })
        if wen and rd:
            registers[rd] = value
    if len(matches) != 1:
        return None
    result = matches[0]
    instruction = result["instruction"]
    valid = (instruction == LD_EXPECTED_INSTRUCTION and result["write_enable"] == 1
             and result["rd"] == 6 and result["effective_address"] == data_address
             and data_address % 8 == 0 and result["value"] == LD_EXPECTED_VALUE)
    return {**result, "data_address": data_address, "naturally_aligned": data_address % 8 == 0,
            "cache_hit": "unobserved", "matched_expected_ld_commit": valid}


def parse_ld_cache_counters(output: str) -> dict[str, int] | None:
    counters = {
        "load_hit": r"\.dcache\.ldu_\d+: load_hit,\s*(\d+)",
        "load_miss": r"\.dcache\.ldu_\d+: load_miss,\s*(\d+)",
        "load_replay": r"\.dcache\.ldu_\d+: load_replay,\s*(\d+)",
        "load_succeed": r"\.dcache\.ldu_\d+: load_succeed,\s*(\d+)",
        "real_miss_first_issue": r"\.LoadUnit_\d+: s2_dcache_real_miss_first_issue,\s*(\d+)",
    }
    parsed = {name: sum(map(int, re.findall(pattern, output))) for name, pattern in counters.items()}
    return parsed if all(re.search(pattern, output) for pattern in counters.values()) else None


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


def classify_ssstateen_no_diff(output: str, exit_code: int,
                              observed: dict[str, object]) -> dict[str, object]:
    """Treat the emulator instruction counter as start evidence, never as a pass marker."""
    result = dict(observed)
    if (exit_code == 0 and GOOD_TRAP not in output and BAD_TRAP not in output
            and ABORT not in output and re.search(r"instrCnt\s*=\s*\d+", output)):
        result.update(cpu_started=True, result="unverified", assertion_failed=False,
                      expected_observed=False,
                      blocker="no-diff run reached an instruction limit without a fixture terminal marker; architectural result is unverified")
    return result


def ssstateen_operation_specs(case: str = "m-hs-gates-diff") -> dict[int, dict[str, object]]:
    """Fixture operation labels and expectations; IDs are written to x31 before each probe."""
    specs: dict[int, dict[str, object]] = {}

    def add(op_id: int, mode: str, csr: str, operation: str, expected: str,
            expected_cause: int | None = None) -> None:
        specs[op_id] = {"operation_id": op_id, "mode": mode, "csr": csr,
                        "operation": operation, "expected": expected,
                        "expected_cause": expected_cause}

    if case == "hs-vu-fcsr":
        add(3001, "M", "misa", "read", "dynamically observe whether the F extension is present")
        add(3002, "M", "mstateen0", "read", "record M FCSR stateen field; implementation declares it RO-zero")
        add(3005, "M", "mstateen0", "write-open-se0", "set M SE0 so HS can inspect the lower-level control fields")
        add(3003, "HS", "hstateen0", "read", "record H FCSR stateen field; implementation declares it RO-zero")
        add(3004, "HS", "sstateen0", "read", "record S FCSR stateen field; implementation declares it RO-zero")
        add(3011, "VU", "fflags", "read", "with misa.F and FS enabled, observe VU FCSR access; this is not a stateen-gate pass")
        add(3012, "VU", "ecall", "execute", "VU environment call should reach HS with cause 8", 8)
        return specs
    if case == "m-s-gates":
        for op_id, address in zip(range(4001, 4005), range(0x30c, 0x310)):
            add(op_id, "M", SSSTATEEN_CSRS[address], "write-all-ones", "open the matching M SE0/SE gate for S-mode access")
        for slot, address in enumerate(range(0x10c, 0x110)):
            base = 4011 + slot * 3
            name = SSSTATEEN_CSRS[address]
            add(base, "S", name, "read", "record initial S-mode read value without assuming reset/WARL bits")
            add(base + 1, "S", name, "write-all-ones", "record S-mode write acceptance")
            add(base + 2, "S", name, "read", "record S-mode readback; only defined bits may be asserted")
        add(4023, "S", "ecall", "execute", "S ecall asks M to clear M.SE0; expect cause 9", 9)
        add(4031, "S", "sstateen0", "gate-blocked-read", "M.SE0 clear should raise illegal-instruction cause 2", 2)
        add(4032, "S", "sstateen0", "read", "readback after M.SE0 restore; defined C bit should remain observable")
        for slot, address in enumerate(range(0x10d, 0x110), start=1):
            base = 4030 + slot * 10
            add(base + 1, "S", "ecall", "execute", f"S ecall asks M to clear M.SE for sstateen{slot}; expect cause 9", 9)
            add(base + 2, "S", SSSTATEEN_CSRS[address], "gate-blocked-read",
                f"M.SE clear for sstateen{slot} should raise illegal-instruction cause 2", 2)
            add(base + 3, "S", SSSTATEEN_CSRS[address], "read",
                f"readback after M.SE restoration for sstateen{slot}")
        add(4073, "S", "ecall", "execute", "final S ecall should reach M with cause 9", 9)
        return specs

    if case in {"hs-vs-valid", "hs-vs-gates"}:
        add(2001, "M", "mstateen0", "write-all-ones", "open M SE0 gate for lower stateen CSRs")
        add(2002, "M", "hstateen0", "write-all-ones", "open H SE0 gate for VS stateen CSR access")
        add(2003, "M", "mstateen1", "write-all-ones", "open M SE gate for sstateen1")
        add(2004, "M", "mstateen2", "write-all-ones", "open M SE gate for sstateen2")
        add(2005, "M", "mstateen3", "write-all-ones", "open M SE gate for sstateen3")
        add(2011, "HS", "sstateen0", "read", "HS read permitted with M SE0 set")
        add(2012, "HS", "sstateen0", "write-all-ones", "HS write permitted with M SE0 set")
        add(2013, "HS", "hstateen0", "read", "HS read permitted with M SE0 set")
        add(2014, "HS", "hstateen0", "write-all-ones", "HS write permitted with M SE0 set")
        if case == "hs-vs-valid":
            add(2021, "VS", "sstateen0", "read", "VS read permitted with M and H SE0 set")
            add(2022, "VS", "sstateen0", "write-all-ones", "VS write permitted with M and H SE0 set")
            add(2023, "VS", "ecall", "execute", "VS ecall should reach HS with cause 10", 10)
        else:
            add(2015, "HS", "hstateen0", "write-gates-clear", "clear H SE0 before VS access; other gate bits written as one")
            add(2021, "VS", "sstateen0", "gate-blocked-read", "H SE0 clear should raise virtual-instruction cause 22", 22)
            add(2016, "HS", "hstateen0", "write-gates-set", "restore H SE0 and preserve supported C bit before resuming VS")
            add(2022, "VS", "sstateen0", "write-all-ones", "VS write permitted after H SE0 set")
            add(2023, "VS", "sstateen0", "read", "readback must retain the defined C bit set by the all-ones write")
            for slot, address in enumerate(range(0x60d, 0x610)):
                add(2101 + slot, "HS", SSSTATEEN_CSRS[address], "write-gates-set", f"open H SE gate for sstateen{slot + 1}")
                add(2104 + slot, "HS", SSSTATEEN_CSRS[address], "read", f"verify H SE gate readback for sstateen{slot + 1}")
                add(2107 + slot, "HS", SSSTATEEN_CSRS[address], "write-gates-clear", f"clear H SE gate for VS sstateen{slot + 1}")
            for slot, address in enumerate(range(0x10d, 0x110)):
                base = 2111 + slot * 3
                add(base, "VS", SSSTATEEN_CSRS[address], "gate-blocked-read",
                    f"H SE clear for VS slot {slot + 1} should raise virtual-instruction cause 22", 22)
                add(base + 1, "VS", SSSTATEEN_CSRS[address], "write-all-ones", f"VS write permitted with H SE for slot {slot + 1} set")
                add(base + 2, "VS", SSSTATEEN_CSRS[address], "read", f"record VS sstateen{slot + 1} readback")
            add(2024, "VS", "ecall", "execute", "VS ecall should reach HS with cause 10", 10)
            add(2120, "VS", "senvcfg", "gate-blocked-read", "H.ENVCFG clear should raise virtual-instruction cause 22", 22)
            add(2121, "VS", "senvcfg", "read", "read senvcfg after H.ENVCFG is restored")
            add(2122, "HS trap handler", "hstateen0", "write-gates-set", "restore H.ENVCFG and preserve SE0/C")
        return specs

    for offset, address in enumerate(range(0x30c, 0x310)):
        add(1001 + offset, "M", SSSTATEEN_CSRS[address], "read-reset",
            "normative reset value is zero" if address == 0x30c else "record reset readback; do not infer unspecified reset value")
    for offset, address in enumerate((*range(0x10c, 0x110), *range(0x60c, 0x610))):
        add(1011 + offset, "M", SSSTATEEN_CSRS[address], "read-reset",
            "record reset readback; do not infer unspecified reset value")
    for offset, address in enumerate(range(0x30c, 0x310)):
        add(1021 + offset, "M", SSSTATEEN_CSRS[address], "write-all-ones",
            "write source is 0xffffffffffffffff; accepted WARL value requires a later readback")
        add(1025 + offset, "M", SSSTATEEN_CSRS[address], "readback-after-write",
            "record exact implemented writable/RO-zero mask after an all-ones write")
    for index, address in enumerate((*range(0x10c, 0x110), *range(0x60c, 0x610))):
        base = 1031 + index * 2
        add(base, "M", SSSTATEEN_CSRS[address], "write-all-ones",
            "write source is 0xffffffffffffffff; accepted WARL value requires a later readback")
        add(base + 1, "M", SSSTATEEN_CSRS[address], "readback-after-write",
            "record actual WARL readback; assert only normative RO-zero/defined bits")
    for offset, address in enumerate((*range(0x30c, 0x310), *range(0x60c, 0x610))):
        add(1051 + offset, "M", SSSTATEEN_CSRS[address], "write-gates-clear",
            "write source is zero; readback is separately recorded")
    for offset, address in enumerate(range(0x30c, 0x310)):
        add(1061 + offset, "M", SSSTATEEN_CSRS[address], "read-gates-clear",
            "readback should show gate controls cleared")

    for op_id in range(1, 21):
        if op_id <= 16:
            address = (0x10c + ((op_id - 1) // 2) if op_id <= 8
                       else 0x60c + ((op_id - 9) // 2))
            operation = "gate-blocked-write" if op_id % 2 else "gate-blocked-read"
            csr = SSSTATEEN_CSRS[address]
            expected = "M stateen gate clear; expected illegal-instruction cause 2"
        else:
            csr = "henvcfg" if op_id < 19 else "senvcfg"
            operation = "gate-blocked-write" if op_id % 2 else "gate-blocked-read"
            expected = "M ENVCFG gate clear; expected illegal-instruction cause 2"
        add(op_id, "HS", csr, operation, expected, 2)
    add(21, "HS", "ecall", "execute", "HS environment call should reach M with cause 9", 9)

    for index, address in enumerate((*range(0x10c, 0x110), *range(0x60c, 0x610), 0x60a, 0x10a)):
        base = 1071 + index * 2
        add(base, "HS", SSSTATEEN_CSRS[address], "enabled-write-all-ones",
            "write source is 0xffffffffffffffff; accepted WARL value requires a later readback")
        add(base + 1, "HS", SSSTATEEN_CSRS[address], "enabled-readback",
            "record actual WARL readback; assert only normative RO-zero/defined bits")
    for offset, address in enumerate((*range(0x30c, 0x310), *range(0x60c, 0x610))):
        add(1091 + offset, "M trap handler", SSSTATEEN_CSRS[address], "write-gates-set",
            "trap handler writes the selected gate mask; field acceptance is recorded by later readback")
    writable_fields = (
        (0x30c, 0x8000000000000000), (0x30c, 0x4000000000000000),
        (0x30c, 0x1000000000000000), (0x30c, 0x0800000000000000),
        (0x30c, 0x0400000000000000), (0x30c, 0x0200000000000000), (0x30c, 1),
        (0x30d, 0x8000000000000000), (0x30e, 0x8000000000000000),
        (0x30f, 0x8000000000000000),
        (0x60c, 0x8000000000000000), (0x60c, 0x4000000000000000),
        (0x60c, 0x1000000000000000), (0x60c, 0x0800000000000000),
        (0x60c, 0x0400000000000000), (0x60c, 0x0200000000000000), (0x60c, 1),
        (0x60d, 0x8000000000000000), (0x60e, 0x8000000000000000),
        (0x60f, 0x8000000000000000),
    )
    for index, (address, mask) in enumerate(writable_fields):
        write_id = 1101 + index * 2
        read_id = write_id + 1
        csr = SSSTATEEN_CSRS[address]
        add(write_id, "M", csr, "write-one-hot", f"isolate field mask 0x{mask:016x}")
        add(read_id, "M", csr, "readback-one-hot", f"WARL readback should equal 0x{mask:016x}")
    for index, address in enumerate(range(0x30c, 0x310)):
        mask = 0xde00000000000001 if address == 0x30c else 0x8000000000000000
        write_id = 1141 + index * 2
        add(write_id, "M", SSSTATEEN_CSRS[address], "restore-gate-mask", f"restore mask 0x{mask:016x} before testing lower CSR views")
        add(write_id + 1, "M", SSSTATEEN_CSRS[address], "readback-restore-mask", f"restored mask should equal 0x{mask:016x}")
    add(1149, "M", "sstateen0", "write-one-hot", "isolate implemented C field mask 0x0000000000000001")
    add(1150, "M", "sstateen0", "readback-one-hot", "WARL readback should equal 0x0000000000000001")
    return specs


def ssstateen_expected_controls(case: str) -> dict[str, object]:
    if case == "m-s-gates":
        return {"CSR": ["mstateen0-3", "sstateen0-3"], "mode_path": "M -> S -> M -> S -> M",
                "gate_state": "M SE0/SE open for initial S operations; M SE0-3 cleared one at a time for the matching S CSR access and restored in trap handler",
                "expected": "Record all four S CSR read/write/readback sequences; each corresponding S CSR access with its M.SE gate clear should cause 2; final S ecall cause 9",
                "entry": "PMP NAPOT RWX enabled; MRET sets MPP=S; trap handler restores M SE0 and returns to S"}
    if case == "hs-vu-fcsr":
        return {"CSR": ["misa", "mstateen0", "hstateen0", "sstateen0", "fflags"],
                "mode_path": "M -> HS -> VU -> HS",
                "gate_state": "M SE0 set for HS reads; M/H/S FCSR fields observed as implemented RO-zero; no FCSR gate write is possible",
                "expected": "Record MISA.F, all three FCSR control fields, VU fflags result, and VU ecall cause 8; this does not claim stateen gate coverage",
                "entry": "PMP NAPOT RWX enabled; FS set in mstatus, sstatus, and vsstatus; SPV=1/SPVP=0 enters VU"}
    if case == "hs-vs-valid":
        return {"CSR": ["mstateen0", "hstateen0", "sstateen0"],
                "mode_path": "M -> HS -> VS", "gate_state": "M SE0 and H SE0 set",
                "expected": "HS and VS sstateen0/hstateen0 CSR accesses commit; VS ecall reaches HS with cause 10",
                "entry": "PMP NAPOT RWX enabled; MPP=S then HS SRET sets SPV/SPVP for VS"}
    if case == "hs-vs-gates":
        return {"CSR": ["mstateen0-3", "hstateen0-3", "sstateen0-3"],
                "mode_path": "M -> HS -> VS -> HS -> VS -> HS", "gate_state": "M SE0 set; H SE0 clear then restored",
                "expected": "Each VS sstateen0-3 read with its H SE gate clear raises virtual-instruction cause 22; the HS handler restores each gate; VS then writes and reads back all slots, with sstateen0 defined C=1; VS ecall cause 10",
                "entry": "PMP NAPOT RWX enabled; MPP=S then HS SRET sets SPV/SPVP for VS"}
    return {"CSR": ["sstateen0-3", "hstateen0-3"], "mode": "M then HS",
            "gate_clear": "M SE0/SE and ENVCFG clear; expect illegal-instruction traps",
            "reset": "capture reset-visible values without assuming unspecified values",
            "selfcheck": "M reset-zero checks, RO-zero assertions, 20 gate traps with IDs and final ecall; completion only on GOODTRAP"}


def parse_ssstateen_trace(output: str, case: str = "m-hs-gates-diff") -> list[dict[str, object]]:
    """Decode committed CSR instructions and t6 operation labels from a possibly truncated trace."""
    specs = ssstateen_operation_specs(case)
    registers: dict[int, int] = {0: 0}
    seen_markers: set[int] = set()
    observations: dict[int, dict[str, object]] = {}
    cause_for_id: dict[int, int] = {}
    saw_commit_trace = False
    fixture_started = False
    operation_order = list(specs)
    operation_positions = {op_id: position for position, op_id in enumerate(operation_order)}
    last_operation_position = -1
    line_re = re.compile(
        r"\[(?:[0-9a-fA-F]+)\]\s+commit pc\s+([0-9a-fA-F]{16})\s+inst\s+([0-9a-fA-F]{8})"
        r"\s+wen\s+(\d+)\s+dst\s+([0-9a-fA-F]{2})\s+data\s+([0-9a-fA-F]{16})")
    exception_re = re.compile(
        r"\[(?:[0-9a-fA-F]+)\]\s+exception pc\s+([0-9a-fA-F]{16})\s+inst\s+([0-9a-fA-F]{8})"
        r"\s+cause\s+([0-9a-fA-F]{16})")
    for line in output.splitlines():
        exception = exception_re.search(line)
        if exception:
            exception_pc, exception_inst, exception_cause = (int(exception.group(1), 16),
                                                             int(exception.group(2), 16),
                                                             int(exception.group(3), 16))
            active_id = registers.get(31)
            if active_id in specs:
                spec_csr = str(specs[active_id]["csr"])
                opcode = exception_inst & 0x7f
                funct3 = (exception_inst >> 12) & 0x7
                exception_csr = (exception_inst >> 20) & 0xfff
                is_csr = opcode == 0x73 and funct3 in {1, 2, 3, 5, 6, 7}
                is_ecall = exception_inst == 0x00000073
                spec_operation = str(specs[active_id]["operation"])
                read_operations = {"read", "read-reset", "readback-after-write", "readback-one-hot",
                                   "readback-restore-mask", "read-gates-clear", "enabled-readback", "gate-blocked-read"}
                access_kind_matches = (funct3 in {2, 6}) == (spec_operation in read_operations)
                matches_operation = (
                    is_csr and access_kind_matches
                    and SSSTATEEN_CSRS.get(exception_csr, SSSTATEEN_OTHER_CSRS.get(exception_csr)) == spec_csr
                ) or (is_ecall and spec_csr == "ecall")
                # A trap handler can preserve t6 across MRET. Attribute an exception only
                # when its native instruction is the CSR/ecall named by that live marker.
                if matches_operation:
                    cause_for_id[active_id] = exception_cause
                    observations[active_id] = {
                        "observed": f"trap cause={exception_cause}; CPU exception trace",
                        "observed_cause": exception_cause,
                        "cause_status": "observed in CPU-native exception trace",
                        "trace_pc": f"0x{exception_pc:016x}",
                        "trace_instruction": f"0x{exception_inst:08x}",
                        "operation_id_source": "active x31/t6 marker and matching faulting instruction in CPU-native exception trace",
                    }
            continue
        match = line_re.search(line)
        if not match:
            continue
        saw_commit_trace = True
        fields = match.groups()
        pc, instruction, wen, dst, data = (int(fields[0], 16), int(fields[1], 16),
                                            int(fields[2]), int(fields[3]), int(fields[4], 16))
        if pc == 0x80000000:
            registers = {0: 0}
            fixture_started = True
        rd = (instruction >> 7) & 0x1f
        rs1 = (instruction >> 15) & 0x1f
        funct3 = (instruction >> 12) & 0x7
        opcode = instruction & 0x7f
        current_id = registers.get(31)
        csr = (instruction >> 20) & 0xfff
        if opcode == 0x73 and funct3 in {1, 2, 3, 5, 6, 7}:
            if csr in SSSTATEEN_CSRS or csr in SSSTATEEN_OTHER_CSRS:
                csr_name = SSSTATEEN_CSRS.get(csr, SSSTATEEN_OTHER_CSRS.get(csr))
                direct = (current_id in specs and specs[current_id]["csr"] == csr_name
                          and current_id not in observations)
                op_id = current_id if direct else None
                marker_source = "x31/t6 fixture marker decoded from commit trace"
                if op_id is None:
                    is_read = funct3 in {2, 6}
                    read_ops = {"read", "read-reset", "readback-after-write", "readback-one-hot",
                                "readback-restore-mask", "read-gates-clear", "enabled-readback", "gate-blocked-read"}
                    op_id = next((candidate for candidate in operation_order[last_operation_position + 1:]
                                  if candidate not in observations
                                  and specs[candidate]["csr"] == csr_name
                                  and ((specs[candidate]["operation"] in read_ops) == is_read)), None)
                    if op_id is not None:
                        marker_source = ("static fixture operation order matched the committed CSR instruction; "
                                         f"x31/t6 marker {op_id} is absent from native trace")
                if op_id is not None:
                    spec = specs[op_id]
                    if spec["operation"] in {"read", "read-reset", "readback-after-write", "readback-one-hot",
                                             "readback-restore-mask", "read-gates-clear", "enabled-readback", "gate-blocked-read"}:
                        observed = f"readback=0x{data:016x}; committed CSR read"
                    elif spec["operation"] in {"write-one-hot", "restore-gate-mask"}:
                        source = re.search(r"0x([0-9a-fA-F]{16})", str(spec["expected"]))
                        value = source.group(1) if source else None
                        observed = (f"fixture write source=0x{value}; CSR write committed; native source-register value unavailable"
                                    if value else "write instruction committed; source register value unavailable")
                    else:
                        # The native trace omits the t4 shift/not updates in this fixture, so its
                        # reconstructed value is stale for these writes; CSR readback is recorded separately.
                        source_value = (None if op_id in {2015, 2016, 2101, 2102, 2103, 2122, 5201} else
                                        (((rs1 & 0x1f) if funct3 >= 5 else registers.get(rs1))
                                         if direct else None))
                        observed = (f"write-source=0x{source_value:016x}; CSR write committed" if source_value is not None
                                    else "write instruction committed; source register value unavailable")
                    observations[op_id] = {"observed": observed, "observed_cause": "no-trap (CSR instruction committed)",
                                           "cause_status": "no-trap", "trace_pc": f"0x{pc:016x}",
                                           "trace_instruction": f"0x{instruction:08x}",
                                           "operation_id_source": marker_source}
                    last_operation_position = operation_positions[op_id]
            elif current_id in specs and csr in {0x142, 0x342}:
                # The trap handler reads scause or mcause while the faulting operation's t6 ID remains live.
                cause_for_id[current_id] = data
        if wen and rd and fixture_started:
            registers[rd] = data
            if rd == 31 and data in specs:
                seen_markers.add(data)

    rows = []
    selfcheck_passed = GOOD_TRAP in output and case == "m-hs-gates-diff"
    for op_id, spec in specs.items():
        observed = observations.get(op_id)
        cause = cause_for_id.get(op_id)
        if observed is None and selfcheck_passed and op_id <= 21:
            expected_cause = 9 if op_id == 21 else 2
            observed = {
                "observed": f"trap cause={expected_cause}; asserted by fixture GOODTRAP self-check; native operation marker/event unavailable",
                "observed_cause": expected_cause,
                "cause_status": "asserted by fixture trap-log self-check; not individually decoded from native trace",
                "trace_pc": None,
                "trace_instruction": None,
                "operation_id_source": "fixture trap-log array checked against ordered IDs and causes before GOODTRAP",
            }
        if observed is None and selfcheck_passed and 1102 <= op_id <= 1150 and op_id % 2 == 0:
            expected_mask = str(spec["expected"]).rsplit("0x", 1)[1]
            observed = {
                "observed": f"readback=0x{expected_mask}; asserted by fixture GOODTRAP self-check",
                "observed_cause": "no-trap (CSR instruction committed)",
                "cause_status": "no-trap asserted by fixture readback check",
                "trace_pc": None,
                "trace_instruction": None,
                "operation_id_source": "fixture CSR readback compared against one-hot mask before GOODTRAP",
            }
        if observed is None and op_id in seen_markers:
            observed_text = "unavailable: operation marker committed, but its CSR/ECALL has no committed trace entry"
            cause_status = "unavailable: trap cause is not present in the available commit trace"
            observed_cause: int | str | None = None
        elif observed is None and not saw_commit_trace:
            observed_text = "unavailable: simulator output contains no commit trace; operation reachability is unknown"
            cause_status = "unavailable: simulator output contains no commit trace"
            observed_cause = None
        elif observed is None:
            observed_text = "not-reached: operation marker is absent from the available trace"
            cause_status = "not-reached"
            observed_cause = None
        else:
            observed_text = str(observed["observed"])
            cause_status = str(observed["cause_status"])
            observed_cause = observed["observed_cause"]
        if cause is not None and observed is None:
            observed_cause = cause
            cause_status = "observed in trap-handler cause CSR read"
            observed_text += f"; trap-handler cause=0x{cause:016x}"
        row = dict(spec)
        row.update(observed=observed_text, observed_cause=observed_cause,
                   cause_status=cause_status,
                   operation_id_source=(observed.get("operation_id_source") if observed else
                                        "no commit trace available; operation reachability unavailable" if not saw_commit_trace else
                                        "x31/t6 fixture marker decoded from commit trace; CPU-native trace itself has no named operation_id field"))
        if observed is not None:
            if observed["trace_pc"] is not None:
                row.update(trace_pc=observed["trace_pc"], trace_instruction=observed["trace_instruction"])
        rows.append(row)
    return rows


def sscofpmf_observed_values(case: str, expected_observed: bool) -> dict[str, object] | None:
    if not expected_observed:
        return None
    if case == "access-route":
        return {"fixture_assertions": "M always-visible; S mcounteren[3] off/on; VS hcounteren[3] off, mcounteren[3] off, both on; delegation probe reached",
                "delegation_probe": "cause-13 trap, sie.LCOFIE, scountovf[3], and sip.LCOFIP asserted",
                "pass_marker_observed": True}
    return {"fixture_assertions": "M/S/U/VS/VU filter suppression and unfiltered event counting; two cause-13 traps; OF/scountovf/LCOFIP set, cleared, and set again",
            "lcofip_after_first_wrap": "set",
            "lcofip_after_software_clear": "clear",
            "lcofip_after_second_wrap": "set",
            "second_interrupt_delivery": "second cause-13 trap observed after hardware re-wrap",
            "pass_marker_observed": True}


def _run(command: list[str], cwd: pathlib.Path, timeout: float | None = None,
         env: dict[str, str] | None = None):
    try:
        result = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True,
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
                        emulator: pathlib.Path, nemu: pathlib.Path,
                        *, require_nemu: bool = True) -> list[str]:
    missing = []
    if not gcc:
        missing.append("riscv64-unknown-elf-gcc")
    if not objcopy:
        missing.append("riscv64-unknown-elf-objcopy")
    if not emulator.is_file():
        missing.append(str(emulator))
    if require_nemu and not nemu.is_file():
        missing.append(str(nemu))
    return missing


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", choices=("fixture", "ld", "zifencei", "sstc", "sscofpmf", "ssnpm", "ssstateen"), default="fixture")
    parser.add_argument("--manifest", type=pathlib.Path,
                        default=ROOT / "notes/units/evidence/cpu-validation-toolchain-v1.yaml")
    parser.add_argument("--evidence-dir", type=pathlib.Path,
                        default=ROOT / "notes/units/evidence/smoke/kunminghu-fixture-runs")
    parser.add_argument("--case", choices=("standard", "funct12", "rs1", "rd"))
    parser.add_argument("--sstc-case", choices=SSTC_CASES)
    parser.add_argument("--sscofpmf-case", choices=("hardware-filter", "access-route"),
                        default=None)
    parser.add_argument("--ssnpm-case", choices=("pmlen0-canonical", "pmlen0-tagged", "pmlen7-canonical", "pmlen7-tagged", "pmlen7-bit56"))
    parser.add_argument("--ssstateen-case", choices=("m-hs-gates-diff", "m-hs-selfcheck", "hs-vs-valid", "hs-vs-gates", "hs-vu-fcsr", "m-s-gates"))
    parser.add_argument("--ld-source", type=pathlib.Path,
                        help="alternate project-relative LD assembly fixture")
    parser.add_argument("--no-diff", "--ssstateen-no-diff", dest="ssstateen_no_diff", action="store_true",
                        help="disable NEMU differential checking for the ssstateen probe")
    parser.add_argument("--timeout", type=float, default=120.0,
                        help="maximum emulator wall time in seconds")
    parser.add_argument("--max-instr", type=int, default=10000,
                        help="maximum committed instructions for the simulator run")
    parser.add_argument("--input", type=pathlib.Path, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.max_instr <= 0:
        parser.error("--max-instr must be positive")
    if args.ld_source is not None and args.topic != "ld":
        parser.error("--ld-source requires --topic ld")
    if args.case and args.topic != "zifencei":
        parser.error("--case requires --topic zifencei")
    if args.sstc_case and args.topic != "sstc":
        parser.error("--sstc-case requires --topic sstc")
    if args.sscofpmf_case is not None and args.topic != "sscofpmf":
        parser.error("--sscofpmf-case requires --topic sscofpmf")
    if args.topic == "sscofpmf" and args.sscofpmf_case is None:
        args.sscofpmf_case = "hardware-filter"
    if args.ssnpm_case and args.topic != "ssnpm":
        parser.error("--ssnpm-case requires --topic ssnpm")
    if args.ssstateen_case and args.topic != "ssstateen":
        parser.error("--ssstateen-case requires --topic ssstateen")
    if args.ssstateen_no_diff and args.topic != "ssstateen":
        parser.error("--ssstateen-no-diff requires --topic ssstateen")
    if args.topic == "ssnpm" and not args.ssnpm_case:
        parser.error("--topic ssnpm requires --ssnpm-case")
    if args.topic == "ssstateen" and not args.ssstateen_case:
        parser.error("--topic ssstateen requires --ssstateen-case")
    if args.topic == "ssstateen" and args.ssstateen_case == "m-hs-selfcheck" and not args.ssstateen_no_diff:
        parser.error("--ssstateen-case m-hs-selfcheck requires --ssstateen-no-diff")
    if args.topic == "ssstateen" and args.ssstateen_case == "m-hs-gates-diff" and args.ssstateen_no_diff:
        parser.error("--ssstateen-no-diff is reserved for the m-hs-selfcheck case")
    if args.topic == "ssstateen" and args.ssstateen_case in {"hs-vs-valid", "hs-vs-gates", "hs-vu-fcsr", "m-s-gates"} and args.ssstateen_no_diff:
        parser.error(f"--ssstateen-case {args.ssstateen_case} requires commit-trace-capable differential mode")
    if args.topic == "sstc" and not args.sstc_case:
        parser.error("--topic sstc requires --sstc-case")
    if args.topic == "sstc":
        global SOURCE, LINKER
        SOURCE = SSTC_SOURCE
    elif args.topic == "ld":
        SOURCE = (ROOT / args.ld_source).resolve() if args.ld_source else LD_SOURCE
        if (not SOURCE.is_relative_to(ROOT) or not SOURCE.is_file() or SOURCE.suffix != ".S"):
            parser.error("--ld-source must name an existing .S source inside the project")
        LINKER = LD_LINKER
    elif args.topic == "sscofpmf":
        SOURCE = SSCOFPMF_ACCESS_SOURCE if args.sscofpmf_case == "access-route" else SSCOFPMF_SOURCE
    elif args.topic == "ssnpm":
        SOURCE = SSNPM_SOURCE
    elif args.topic == "ssstateen":
        SOURCE = (SSSTATEEN_M_S_SOURCE if args.ssstateen_case == "m-s-gates" else
                  SSSTATEEN_VU_SOURCE if args.ssstateen_case == "hs-vu-fcsr" else
                  SSSTATEEN_VS_GATE_SOURCE if args.ssstateen_case == "hs-vs-gates" else
                  SSSTATEEN_VIRTUAL_SOURCE if args.ssstateen_case == "hs-vs-valid" else SSSTATEEN_SOURCE)
        LINKER = SSSTATEEN_LINKER
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
    expected_ld_pc: int | None = None
    expected_ld_data: int | None = None
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
    missing = missing_dependencies(gcc, objcopy, EMULATOR, NEMU,
                                   require_nemu=not (args.topic == "ssstateen" and args.ssstateen_no_diff))
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
        compile_cmd = [gcc, f"-march={'rv64ima_zicsr' if args.topic in {'sstc', 'sscofpmf', 'ssnpm', 'ssstateen'} else 'rv64imac'}", "-mabi=lp64", "-nostdlib", "-nostartfiles",
                       "-Wl,--build-id=none", f"-Wl,-T,{LINKER}", f"-Wl,-Map,{link_map}",
                       *([f"-DCASE_{args.sstc_case.upper().replace('-', '_')}=1"] if args.topic == "sstc" else []),
                       *(["-DSSNPM_PMLEN7=1"] if args.topic == "ssnpm" and args.ssnpm_case.startswith("pmlen7-") else []),
                       *(["-DSSNPM_BIT56=1"] if args.topic == "ssnpm" and args.ssnpm_case == "pmlen7-bit56" else []),
                       *(["-DSSNPM_TAGGED=1"] if args.topic == "ssnpm" and (args.ssnpm_case.endswith("-tagged") or args.ssnpm_case == "pmlen7-bit56") else []),
                       *(["-DSSNPM_EXPECT_TRAP=1"] if args.topic == "ssnpm" and args.ssnpm_case == "pmlen0-tagged" else []),
                       "-o", str(elf), str(source_snapshot if args.topic == "sstc" else SOURCE)]
        stages.append(("compile and link", compile_cmd))
        copy_cmd = [objcopy, "-O", "binary", str(elf), str(raw)]
        stages.append(("raw image generation", copy_cmd))
        sim_cmd = [str(EMULATOR), "-i", str(raw),
                   *( ["--no-diff"] if args.topic == "ssstateen" and args.ssstateen_no_diff else ["--diff", str(NEMU)] ),
                   "--max-cycles=100000" if args.topic in {"sstc", "sscofpmf", "ssnpm", "ssstateen"} else "--max-cycles=10000",
                   f"--max-instr={args.max_instr if args.topic in {'sstc', 'sscofpmf', 'ssnpm', 'ssstateen'} else min(args.max_instr, 1000)}",
                   "--dump-commit-trace"]
        stages.append(("emulator CPU run", sim_cmd))
        for stage, command in stages:
            run_env = None
            command_display = shlex.join(command)
            if stage == "emulator CPU run" and args.topic == "ssstateen" and args.ssstateen_no_diff:
                run_env = os.environ.copy()
                # This emulator build initializes its ref proxy even with --no-diff.
                # Provide its pinned ready-to-run library through the expected layout,
                # while leaving architectural comparison disabled.
                nemu_home = run_dir / "no-diff-nemu-home"
                build_dir = nemu_home / "build"
                build_dir.mkdir(parents=True, exist_ok=True)
                (build_dir / "riscv64-nemu-interpreter-so").symlink_to(NEMU.resolve())
                run_env["NEMU_HOME"] = str(nemu_home)
                command_display = f"NEMU_HOME={shlex.quote(run_env['NEMU_HOME'])} " + command_display
            commands.append("$ " + command_display)
            try:
                run_timeout = args.timeout if stage == "emulator CPU run" else 120
                if run_env is None:
                    code, out, err, did_timeout = _run(command, ROOT, run_timeout)
                else:
                    code, out, err, did_timeout = _run(command, ROOT, run_timeout, env=run_env)
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
                if args.topic == "ld":
                    target_match = re.search(r"^\s*0x([0-9a-fA-F]+)\s+ld_target$", map_text, re.MULTILINE)
                    data_match = re.search(r"^\s*0x([0-9a-fA-F]+)\s+ld_data$", map_text, re.MULTILINE)
                    if not target_match or not data_match:
                        failed_stage = "link map inspection"
                        stage_error = "LD fixture target/data symbols are absent from the linked image"
                        exit_code = 1
                        break
                    expected_ld_pc = int(target_match.group(1), 16)
                    expected_ld_data = int(data_match.group(1), 16)

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
    ld_commit = (parse_ld_commit(stdout_text + "\n" + stderr_text, expected_ld_pc, expected_ld_data)
                 if args.topic == "ld" and expected_ld_pc is not None and expected_ld_data is not None else None)
    ld_cache_counters = parse_ld_cache_counters(stderr_text) if args.topic == "ld" else None
    if args.topic == "ld" and observed["expected_observed"] and not (
            ld_commit and ld_commit["matched_expected_ld_commit"]):
        observed.update(result="run-fail", assertion_failed=True, expected_observed=False,
                        blocker="good trap passed, but the target LD commit PC/encoding/address/rd/value did not match")
    if args.topic == "ssstateen" and args.ssstateen_no_diff:
        observed = classify_ssstateen_no_diff(stdout_text + "\n" + stderr_text, exit_code, observed)
    if observed["result"] == "unverified":
        failed_stage = "emulator CPU run"
    if failed_stage and not observed["cpu_started"]:
        observed["result"] = "blocked"
        observed["assertion_failed"] = False
        observed["expected_observed"] = False
        observed["blocker"] = f"{failed_stage}: {stage_error}"
    elif failed_stage and observed["cpu_started"] and observed["result"] != "unverified":
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

    recorded_source = source_snapshot if args.topic in {"sstc", "ssnpm", "ssstateen"} and source_snapshot.is_file() else SOURCE
    expected_artifacts = [str(p.relative_to(ROOT)) for p in (recorded_source, LINKER, elf, link_map, raw)]
    if args.topic == "ssstateen" and args.ssstateen_no_diff:
        nemu_alias = run_dir / "no-diff-nemu-home/build/riscv64-nemu-interpreter-so"
        if nemu_alias.exists():
            expected_artifacts.append(str(nemu_alias.relative_to(ROOT)))
    artifacts = [path for path in expected_artifacts if (ROOT / path).is_file()]
    missing_artifacts = [path for path in expected_artifacts if not (ROOT / path).is_file()]
    record = {
        "id": run_dir.name,
        "snapshot_sha": snapshot_sha or "unknown",
        "input": str(recorded_source.relative_to(ROOT)),
        "input_sha256": input_sha256 or "unavailable",
        "linker_script": str(LINKER.relative_to(ROOT)),
        "linker_script_sha256": linker_sha256 or "unavailable",
        "configuration": ("KunminghuV2Config; NUM_CORES=1; U-mode integer LD from canonical or PMLEN=7 tagged VA; senvcfg.PMM selected in M before mret; PMP NAPOT grants U-mode access; NEMU difftest."
                           if args.topic == "ssnpm" else
                           ("KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Ssstateen M/S mode gate/readback probe; PMP NAPOT RWX; NEMU difftest."
                            if args.ssstateen_case == "m-s-gates" else
                            "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Ssstateen HS/VS positive-path probe; PMP NAPOT RWX; NEMU difftest."
                            if args.ssstateen_case == "hs-vs-valid" else
                            "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr HS/VU MISA and FCSR availability probe; PMP NAPOT RWX; NEMU difftest."
                            if args.ssstateen_case == "hs-vu-fcsr" else
                            "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Ssstateen HS/VS SE0 gate probe; PMP NAPOT RWX; NEMU difftest."
                            if args.ssstateen_case == "hs-vs-gates" else
                            "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Ssstateen M/HS probe; NEMU difftest.") if args.topic == "ssstateen" and not args.ssstateen_no_diff else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Ssstateen M/HS self-check probe; NEMU difftest disabled." if args.topic == "ssstateen" else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Sstc S-mode fixture at 0x80000000 (C extension disabled to keep traceable 32-bit fixture instructions); PMP NAPOT grants S-mode access; NEMU difftest."
                           if args.topic == "sstc" else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr Sscofpmf counter3/event2 access matrix and delegated LCOFI probe; NEMU difftest."
                           if args.topic == "sscofpmf" and args.sscofpmf_case == "access-route" else
                           "KunminghuV2Config; NUM_CORES=1; RV64IMA_Zicsr M-mode Sscofpmf fixture at 0x80000000; event selector 2 (Frontend ifu_req), counter 3, 64-bit hardware event wrap; NEMU difftest."
                           if args.topic == "sscofpmf" else
                           "KunminghuV2Config; NUM_CORES=1; naturally aligned M-mode Bare LD fixture at 0x80000000; NEMU difftest; cache state is not PC-correlated."
                           if args.topic == "ld" else
                           "KunminghuV2Config; NUM_CORES=1; Zifencei self-modifying fixture at 0x80000000; NEMU difftest."
                           if args.topic == "zifencei" else
                           "KunminghuV2Config; NUM_CORES=1; RV64I arithmetic fixture at 0x80000000; NEMU difftest."),
        **({"topic": "ssstateen", "case": args.ssstateen_case,
            "differential_enabled": not args.ssstateen_no_diff,
            "operation_records": parse_ssstateen_trace(stdout_text + "\n" + stderr_text, args.ssstateen_case),
            "operation_record_count": len(ssstateen_operation_specs(args.ssstateen_case)),
            "expected_controls": ssstateen_expected_controls(args.ssstateen_case),
            "observed_values": {"first_commit_observed": FIRST_COMMIT in stdout_text,
                                "cpu_start_evidence": ("first instruction commit marker" if FIRST_COMMIT in stdout_text
                                                       else "emulator instruction-count summary" if observed["cpu_started"]
                                                       else "none"),
                                "terminal_marker": "HIT GOOD TRAP" if GOOD_TRAP in stdout_text else "none",
                                "difftest_enabled": not args.ssstateen_no_diff,
                                "matrix_status": ("GOODTRAP self-check passed; native commit trace has some unlabeled/unavailable operations"
                                                if observed["expected_observed"] else
                                                "incomplete: GOODTRAP self-check was not observed")},
            "evidence_method": "Kunminghu smoke runner preflight, fixed fixture build, linker-map inspection, emulator classification, and manifest append; fixture reports CSR operation trap IDs in its memory trace"}
           if args.topic == "ssstateen" else
           {"topic": "ld", "target_pc": f"0x{expected_ld_pc:x}" if expected_ld_pc is not None else None,
            "target_data_address": f"0x{expected_ld_data:x}" if expected_ld_data is not None else None,
            "expected_controls": {"instruction": "ld t1, 0(t0)", "encoding": f"0x{LD_EXPECTED_INSTRUCTION:08x}",
                                  "destination_register": "x6", "value": f"0x{LD_EXPECTED_VALUE:016x}",
                                  "natural_alignment": True, "older_overlapping_store": False,
                                  "privilege": "M-mode Bare (SATP reset state)", "cache_hit": "unobserved"},
            "observed_values": ld_commit,
            "observed_dcache_counters": ld_cache_counters,
            "evidence_method": "linked target symbol matched one native commit trace record; aggregate L1 DCache/load-unit performance counters are archived separately and are not PC-correlated"}
           if args.topic == "ld" else
           {"topic": "ssnpm", "case": args.ssnpm_case,
            "expected_controls": {"effective_privilege": "U", "instruction_families": (["ld"] if args.ssnpm_case == "pmlen0-tagged" else ["ld", "sd", "lr.d", "sc.d", "amoadd.d"]),
                                  "senvcfg.PMM": 2 if args.ssnpm_case.startswith("pmlen7-") else 0,
                                  "PMLEN": 7 if args.ssnpm_case.startswith("pmlen7-") else 0,
                                  "expected_senvcfg.PMM_readback": 2 if args.ssnpm_case.startswith("pmlen7-") else 0,
                                  "input_address": ("probe_data | 0x0100000000000000 (bit 56 set)" if args.ssnpm_case == "pmlen7-bit56" else "probe_data | 0xfe00000000000000" if args.ssnpm_case.endswith("-tagged") else "canonical probe_data"),
                                  "expected_effective_address": ("raw tagged VA; expect load access fault" if args.ssnpm_case == "pmlen0-tagged" else "PMLEN7 sign-extends bit 56; bus address is not externally sampled" if args.ssnpm_case == "pmlen7-bit56" else "PMLEN7 high-tag VA should address probe_data; bus address is not externally sampled" if args.ssnpm_case == "pmlen7-tagged" else "probe_data"),
                                  "expected_value": "access fault cause 5" if args.ssnpm_case == "pmlen0-tagged" else "ld=0x1234, store/readback=0x5678, LR/SC=0x9abc, AMOADD old=0x9abc/new=0x9abd"},
            "observed_values": ({"senvcfg.PMM_readback": 2 if args.ssnpm_case.startswith("pmlen7-") else 0,
                                 **({"load_trap_cause": 5} if args.ssnpm_case == "pmlen0-tagged" else {"load_store_lr_sc_amo_assertions": "all passed"}),
                                 "effective_address": "probe_data alias confirmed by successful memory-family assertions" if args.ssnpm_case != "pmlen0-tagged" else "raw tagged VA faulted before target access"}
                                if observed["expected_observed"] else None),
            "evidence_method": "M-mode asserts senvcfg.PMM readback before mret; U-mode asserts expected load/store/LR.D/SC.D/AMOADD.D values (or the PMLEN0 tagged load access-fault cause 5); success marker follows the assertions"}
           if args.topic == "ssnpm" else
           {"topic": "zifencei", "case": SOURCE.stem,
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
              "observed_values": sscofpmf_observed_values(args.sscofpmf_case,
                                                           bool(observed["expected_observed"])),
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
        "expected": ("Kunminghu LD fixture commits the exact aligned LD with x6=0x123456789abcdef0 and reaches the checked NEMU good trap."
                     if args.topic == "ld" else
                     "Ssstateen fixture built by the locked Kunminghu runner; first instruction commits; self-check GOODTRAP required for pass."
                     if args.topic == "ssstateen" else
                     "recorded fixture image loaded at 0x80000000; first instruction commits; NEMU good trap."
                     if args.topic != "sscofpmf" or args.sscofpmf_case == "hardware-filter" else
                     "scountovf access assertions pass and delegated hardware cause 13 reaches S-mode before NEMU good trap."),
        "observed": (f"CPU execution inferred from emulator instrCnt; {observed['observed']}"
                     if args.topic == "ssstateen" and args.ssstateen_no_diff and observed["result"] == "unverified"
                     else observed["observed"]),
        "expected_good_trap_pc": f"0x{expected_trap_pc:x}" if expected_trap_pc is not None else "unknown",
        "blocker": observed["blocker"],
        "expected_marker": GOOD_TRAP if args.topic == "ssstateen" else GOOD_TRAP,
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
