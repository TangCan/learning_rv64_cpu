#!/usr/bin/env python3
"""Build Story 6.5 Heliodor S-mode comparator and permission fixtures."""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import struct
import subprocess
import tempfile

OUT = pathlib.Path(__file__).resolve().parent
ROOT = OUT.parents[2]
CASES = ("s-lt", "s-eq", "s-gt", "s-stce-off", "s-tm-off")
PINNED = {
    "riscv64-unknown-elf-gcc": "3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32",
    "riscv64-unknown-elf-objcopy": "0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858",
}

def hash_file(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source(case: str) -> str:
    stce = 0 if case == "s-stce-off" else 1
    tm = 0 if case == "s-tm-off" else 2
    relation = {"s-lt": "li t1,8\n    add t1,t0,t1", "s-eq": "mv t1,t0",
                "s-gt": "li t1,8\n    sub t1,t0,t1"}.get(case, "li t1,-1")
    body = """    csrr t0,sip
    andi t0,t0,32
    bnez t0,fail
.Lsample_time:
    csrr t0,time
    .rept 256
    nop
    .endr
    csrr t1,time
    beq t0,t1,.Lsample_time
    mv t0,t1
    RELATION
    csrw 0x14d,t1
    csrr t3,time
    li t4,0x80001004
    sw t0,0(t4)                 /* sampled time */
    sw t1,4(t4)                 /* programmed comparator */
    sw t3,8(t4)                 /* time immediately after comparator write */
#if defined(CASE_S_LT)
    bgeu t3,t1,fail
#elif defined(CASE_S_GT)
    bltu t3,t1,fail
#endif
    li t2,10000
1:  csrr t3,sip
    andi t3,t3,32
    bnez t3,2f
    addi t2,t2,-1
    bnez t2,1b
    j fail
2:  li t0,32
    csrs sie,t0
    li t0,2
    csrs sstatus,t0
3:  j 3b
""".replace("RELATION", relation)
    if case.endswith("-off"):
        body = """    csrw 0x14d,zero             /* no earlier time access */
    li t0,0x210                 /* expected trap did not occur */
    li t1,0x80001000
    sw t0,0(t1)
8:  j 8b
"""
    elif case == "s-gt":
        body = """.Lwait_nonzero_time:
    csrr t0,time
    li t1,8
    bltu t0,t1,.Lwait_nonzero_time
""" + body
    return f'''/* Generated Heliodor Sstc fixture: {case}; STCE={stce}, TM={tm}. */
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0,m_trap
    csrw mtvec,t0
    li t0,{stce}
    slli t0,t0,63
    csrw 0x30a,t0
    li t0,{tm}
    csrw 0x306,t0
    li t0,-1
    csrw 0x14d,t0
    li t0,32
    csrw 0x303,t0
    la t0,s_trap
    csrw stvec,t0
    li t0,32
    csrw sie,t0
    li t0,0x800
    csrs mstatus,t0
    la t0,s_entry
    csrw mepc,t0
    mret
s_entry:
target_access:
{body}
    .balign 4
s_trap:
    csrr t0,scause
    li t1,0x8000000000000005
    bne t0,t1,fail
    csrr t0,sip
    andi t0,t0,32
    beqz t0,fail
    li t0,-1
    csrw 0x14d,t0
4:  csrr t0,sip
    andi t0,t0,32
    bnez t0,4b
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
5:  j 5b
    .balign 4
m_trap:
    csrr t0,mcause
    li t1,2
    beq t0,t1,8f
    csrr t1,mepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    li t1,0x80001000
    sw t0,0(t1)
9:  j 9b
8:  la t1,target_access
    csrr t0,mepc
    bne t0,t1,fail
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
6:  j 6b
fail:
    li t0,3
    li t1,0x80001000
    sw t0,0(t1)
7:  j 7b
    .section .tohost,"aw",@progbits
    .align 6
    .globl tohost
tohost: .dword 0
'''

def main() -> None:
    tools = {name: shutil.which(name) for name in PINNED}
    if any(path is None for path in tools.values()):
        raise SystemExit("install the Story 6.1 pinned riscv64 cross toolchain")
    for name, expected in PINNED.items():
        if hash_file(pathlib.Path(tools[name])) != expected:
            raise SystemExit(f"{name} SHA-256 differs from pinned Story 6.1 tool")
    OUT.mkdir(parents=True, exist_ok=True)
    linker = OUT.parents[1] / "rva23s64-zifencei/fixture.ld"
    with tempfile.TemporaryDirectory(prefix="heliodor-sstc-s-") as tmp_name:
        tmp = pathlib.Path(tmp_name)
        for case in CASES:
            asm = OUT / f"{case}.S"
            asm.write_text(source(case), encoding="ascii")
            elf, raw = tmp / f"{case}.elf", tmp / f"{case}.bin"
            subprocess.run([tools["riscv64-unknown-elf-gcc"], "-march=rv64imac_zicsr", "-mabi=lp64",
                            "-nostdlib", "-nostartfiles", "-Wl,--build-id=none",
                            f"-Wl,-T,{linker}", "-o", str(elf), str(asm)], check=True)
            subprocess.run([tools["riscv64-unknown-elf-objcopy"], "-O", "binary", str(elf), str(raw)], check=True)
            image = raw.read_bytes().ljust(0x1008, b"\0")
            words = struct.unpack("<" + "I" * (len(image) // 4), image)
            (OUT / f"{case}.hex").write_text("".join(f"{word:08x}\n" for word in words), encoding="ascii")
    print(f"built {len(CASES)} Heliodor Sstc fixtures")

if __name__ == "__main__":
    main()
