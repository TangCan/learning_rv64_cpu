#!/usr/bin/env python3
"""Build isolated Heliodor U-mode Ssnpm PMLEN/tag/boundary fixtures."""
from __future__ import annotations

import hashlib
import json
import pathlib
import shutil
import struct
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "experiments/ssnpm/heliodor"
LINKER = ROOT / "experiments/rva23s64-zifencei/fixture.ld"
CASES = ("pmlen0-canonical", "pmlen0-tagged", "pmlen7-canonical", "pmlen7-tagged", "pmlen7-bit56")
TOOLS = {
    "riscv64-unknown-elf-gcc": "3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
    "riscv64-unknown-elf-objcopy": "0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
}


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def assembly(case: str) -> str:
    pmlen7 = case.startswith("pmlen7-")
    tagged = case.endswith("-tagged")
    bit56 = case == "pmlen7-bit56"
    expect_fault = case == "pmlen0-tagged"
    pmm = 2 if pmlen7 else 0
    pointer = ("    li t1, 0x0100000000000000\n    or t0, t0, t1\n" if bit56 else
               "    li t1, 0xfe00000000000000\n    or t0, t0, t1\n" if tagged else "")
    if expect_fault:
        access = "tagged_load:\n    ld t2, 0(t0)\n    li t5, 0x12\n    j report_fail\n"
    else:
        access = ("tagged_load:\n" if tagged or bit56 else "") + (
            "    li t3, 0x5678\n    sd t3, 0(t0)\n    ld t2, 0(t0)\n"
            "    bne t2, t3, load_mismatch\n    li a0, 0\n    j good_trap\n")
    trap = ("machine_trap:\n    la t4, tohost\n    ld t5, 0(t4)\n    li t1, 1\n    beq t5, t1, trap_halt\n"
            "    csrr t0, mcause\n    li t1, 5\n    bne t0, t1, trap_failure\n"
            "    la t2, tagged_load\n    csrr t3, mepc\n    bne t2, t3, trap_failure\n"
            "    la t2, probe_data\n    li t3, 0xfe00000000000000\n    or t2, t2, t3\n"
            "    csrr t3, mtval\n    bne t2, t3, trap_failure\n"
            "    li t1, 1\n    sd t1, 0(t4)\n    j trap_halt\ntrap_failure:\n    addi t5, t0, 0x30\n    sd t5, 0(t4)\n    j trap_halt\n" if expect_fault else
            "machine_trap:\n    la t4, tohost\n    ld t5, 0(t4)\n    li t1, 1\n    beq t5, t1, trap_halt\n"
            "    li t5, 3\n    sd t5, 0(t4)\n    j trap_halt\n")
    return f'''/* Heliodor U-mode Ssnpm case {case}. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0, machine_trap
    csrw mtvec, t0
    /* 8 KiB NAPOT grants linked image/tohost while denying tagged high addresses. */
    li t0, 0x200003ff
    csrw pmpaddr0, t0
    li t0, 0x1f
    csrw pmpcfg0, t0
    li t0, {pmm}
    slli t0, t0, 32
    csrw senvcfg, t0
    csrr t1, senvcfg
    srli t1, t1, 32
    andi t1, t1, 3
    li t2, {pmm}
    bne t1, t2, readback_mismatch
    la t0, u_entry
    csrw mepc, t0
    csrw mstatus, zero
    mret
u_entry:
    la t0, probe_data
{pointer}{access}good_trap:
    la t4, tohost
    li t5, 1
    sd t5, 0(t4)
    j trap_halt
{trap}trap_halt:
    j trap_halt
readback_mismatch:
    li t5, 0x11
    j report_fail
load_mismatch:
    li t5, 0x12
    j report_fail
unexpected_trap:
    csrr t0, mcause
    addi t5, t0, 0x20
report_fail:
    la t4, tohost
    sd t5, 0(t4)
    j trap_halt
    .section .data,"aw",@progbits
    .align 3
probe_data:
    .dword 0x1234
    .section .tohost,"aw",@progbits
    .align 6
    .globl tohost
tohost:
    .dword 0
'''


def main() -> None:
    tools = {name: shutil.which(name) for name in TOOLS}
    if any(path is None for path in tools.values()):
        raise SystemExit("install the Story 6.1 pinned riscv64 cross toolchain")
    for name, expected in TOOLS.items():
        if sha256(pathlib.Path(tools[name])) != expected:
            raise SystemExit(f"{name} SHA-256 differs from pinned Story 6.1 tool")
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="heliodor-ssnpm-") as temp_name:
        temp = pathlib.Path(temp_name)
        for case in CASES:
            source = OUT / f"{case}.S"
            source.write_text(assembly(case), encoding="ascii")
            elf, raw = temp / f"{case}.elf", temp / f"{case}.bin"
            gcc_argv = [tools["riscv64-unknown-elf-gcc"], "-march=rv64ima_zicsr", "-mabi=lp64",
                        "-nostdlib", "-nostartfiles", "-Wl,--build-id=none", f"-Wl,-T,{LINKER}",
                        "-o", str(elf), str(source)]
            objcopy_argv = [tools["riscv64-unknown-elf-objcopy"], "-O", "binary", str(elf), str(raw)]
            subprocess.run(gcc_argv, check=True)
            subprocess.run(objcopy_argv, check=True)
            (OUT / f"{case}.build.json").write_text(json.dumps({
                "case": case, "gcc_argv": gcc_argv, "objcopy_argv": objcopy_argv,
                "linker_script": str(LINKER), "linker_sha256": sha256(LINKER),
                "assembly": str(source),
            }, indent=2) + "\n", encoding="utf-8")
            image = raw.read_bytes().ljust(0x1008, b"\0")
            words = struct.unpack("<" + "I" * (len(image) // 4), image)
            (OUT / f"{case}.hex").write_text("".join(f"{word:08x}\n" for word in words), encoding="ascii")
    print(f"built {len(CASES)} Heliodor Ssnpm fixtures")


if __name__ == "__main__":
    main()
