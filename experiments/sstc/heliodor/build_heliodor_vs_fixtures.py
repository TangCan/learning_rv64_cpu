#!/usr/bin/env python3
"""Build the complete Heliodor Sstc-in-VS fixture matrix."""
from __future__ import annotations
import pathlib, subprocess, shutil, tempfile, hashlib, struct

OUT=pathlib.Path(__file__).resolve().parent
CASES=("vs-lt","vs-eq","vs-gt","vs-mstce-off","vs-hstce-off","vs-mtm-off","vs-htm-off","vs-route","vs-hs-route")
PINNED={"riscv64-unknown-elf-gcc":"3b2b5d5ad7f9c7821c8ca1b11c6c512f30e3d63dcbdc726836c1c7bc0bceed32","riscv64-unknown-elf-objcopy":"0ed4d26870589f4ba1e5678b62305d66c2df6ee8906da706c830a6f42950c858"}

def fixture(case):
    mstce=0 if case=="vs-mstce-off" else 1
    hstce=0 if case=="vs-hstce-off" else 1
    mtm=0 if case=="vs-mtm-off" else 2
    htm=0 if case=="vs-htm-off" else 2
    hideleg=0 if case=="vs-hs-route" else 64
    if case in ("vs-mstce-off","vs-hstce-off","vs-mtm-off","vs-htm-off"):
        target="    csrw 0x14d,zero          /* first VS CSR access */\n    li t0,0x210                /* expected trap did not occur */\n    j report_trap"
        expected=22 if case in ("vs-hstce-off","vs-htm-off") else 2
    else:
        relation={"vs-lt":"    li t1,64\n    add t1,t0,t1", "vs-eq":"    mv t1,t0", "vs-gt":"    li t1,64\n    sub t1,t0,t1"}.get(case)
        if relation:
            target=f'''.Lsample_guest_time:
    csrr t2,sip
    andi t2,t2,32
    bnez t2,fail                /* no stale VSTIP before comparator write */
    csrr t0,0xc01
    .rept 256
    nop
    .endr
    csrr t1,0xc01
    beq t0,t1,.Lsample_guest_time
    mv t0,t1
    REL
    csrw 0x14d,t1
    csrr t3,0xc01
    li t4,0x80001004
    sw t0,0(t4)                 /* sampled guest time */
    sw t1,4(t4)                 /* programmed comparator */
    sw t3,8(t4)                 /* guest time after comparator write */
#if defined(CASE_VS_LT)
    bgeu t3,t1,fail
#elif defined(CASE_VS_GT)
    bltu t3,t1,fail
#endif
    li t2,100000
1:  csrr t3,sip
    andi t3,t3,32
    bnez t3,2f
    addi t2,t2,-1
    bnez t2,1b
    li t0,0x211                /* no pending observed within poll budget */
    j report_trap
2:  li t0,-1
    csrw 0x14d,t0
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
3:  j 3b'''.replace("REL",relation)
        else:
            target='''    csrr t2,sip
    andi t2,t2,32
    bnez t2,fail                /* no stale VSTIP before comparator write */
    csrr t0,0xc01
    li t1,256
    add t1,t0,t1
    csrw 0x14d,t1
    csrr t3,0xc01
    li t4,0x80001004
    sw t0,0(t4)                 /* sampled guest time */
    sw t1,4(t4)                 /* programmed comparator */
    sw t3,8(t4)                 /* guest time after comparator write */
    li t0,32
    csrs sie,t0
    li t0,2
    csrs sstatus,t0
1:  j 1b'''
        expected=0
    return f'''/* {case}; htimedelta=0x10000; M/H STCE={mstce}/{hstce}, TM={mtm}/{htm}. */
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0,m_trap
    csrw mtvec,t0
    li t0,0x400004
    csrw medeleg,t0
    csrw 0x602,zero
    li t0,{mstce}
    slli t0,t0,63
    csrw 0x30a,t0
    li t0,{hstce}
    slli t0,t0,63
    csrw 0x60a,t0
    li t0,{mtm}
    csrw 0x306,t0
    li t0,{htm}
    csrw 0x606,t0
    li t0,{hideleg}
    csrw 0x603,t0
    li t0,{(64 if case == "vs-hs-route" else 0)}
    csrw 0x604,t0
    li t0,0x10000
    csrw 0x605,t0
    csrw 0x280,zero
    li t0,-1
    csrw 0x24d,t0               /* keep VSTIP clear before entering VS */
    csrw 0x680,zero             /* hgatp bare */
    la t0,hs_trap
    csrw stvec,t0
    la t0,vs_trap
    csrw 0x205,t0
    li t0,0x8000000802
    csrs mstatus,t0
    la t0,vs_entry
    csrw mepc,t0
    mret
vs_entry:
target_access:
{target}
    .balign 4
vs_trap:
    csrr t0,scause
    li t1,0x8000000000000005
    bne t0,t1,vs_bad_cause
    csrr t0,sip
    andi t0,t0,32
    beqz t0,vs_no_pending
    li t0,-1
    csrw 0x14d,t0
    li t2,100000
vs_pending_poll:
    csrr t0,sip
    andi t0,t0,32
    beqz t0,vs_pending_cleared
    addi t2,t2,-1
    bnez t2,vs_pending_poll
    j vs_pending_not_cleared
vs_pending_cleared:
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
4:  j 4b
    .balign 4
vs_bad_cause:
    csrr t1,sepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
vs_no_pending:
    li t0,0x302
    j report_trap
vs_pending_not_cleared:
    li t0,0x212
    j report_trap
    .balign 4
hs_trap:
    csrr t0,scause
    li t1,{expected}
    bnez t1,hs_gate_check
    li t1,0x8000000000000006
    bne t0,t1,hs_bad_cause
    csrr t0,0x644
    andi t0,t0,64
    beqz t0,hs_no_pending
    li t0,-1
    csrw 0x24d,t0
    li t2,100000
hs_pending_poll:
    csrr t0,0x644
    andi t0,t0,64
    beqz t0,hs_pending_cleared
    addi t2,t2,-1
    bnez t2,hs_pending_poll
    j hs_pending_not_cleared
hs_pending_cleared:
    j hs_pass
hs_gate_check:
    bne t0,t1,hs_bad_cause
    csrr t0,sepc
    la t1,target_access
    bne t0,t1,hs_bad_pc
    j hs_pass
hs_bad_cause:
    csrr t1,sepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
hs_no_pending:
    li t0,0x402
    j report_trap
hs_bad_pc:
    li t0,0x403
    j report_trap
hs_pending_not_cleared:
    li t0,0x412
    j report_trap
hs_pass:
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
5:  j 5b
    .balign 4
m_trap:
    csrr t0,mcause
    li t1,{expected}
    beqz t1,m_bad_cause
    bne t0,t1,m_bad_cause
    csrr t0,mepc
    la t1,target_access
    bne t0,t1,m_bad_pc
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
6:  j 6b
m_bad_cause:
    csrr t1,mepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
m_bad_pc:
    li t0,0x403
    j report_trap
report_trap:
    li t1,0x80001000
    sw t0,0(t1)
    j 7f
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

def main():
    tools={k:shutil.which(k) for k in PINNED}
    for k,h in PINNED.items():
        if not tools[k] or hashlib.sha256(pathlib.Path(tools[k]).read_bytes()).hexdigest()!=h: raise SystemExit(f"missing or unpinned {k}")
    linker=OUT.parents[1]/"rva23s64-zifencei/fixture.ld"
    with tempfile.TemporaryDirectory() as d:
        for c in CASES:
            asm=OUT/f"{c}.S"; asm.write_text(fixture(c))
            elf=pathlib.Path(d)/f"{c}.elf"; raw=pathlib.Path(d)/f"{c}.bin"
            subprocess.run([tools["riscv64-unknown-elf-gcc"],"-march=rv64imac_zicsr","-mabi=lp64","-nostdlib","-nostartfiles","-Wl,--build-id=none",f"-Wl,-T,{linker}","-o",str(elf),str(asm)],check=True)
            subprocess.run([tools["riscv64-unknown-elf-objcopy"],"-O","binary",str(elf),str(raw)],check=True)
            b=raw.read_bytes().ljust(0x1008,b"\0"); (OUT/f"{c}.hex").write_text("".join(f"{x:08x}\n" for x in struct.unpack("<"+"I"*(len(b)//4),b)))
    print(f"built {len(CASES)} Heliodor VS fixtures")
if __name__=="__main__": main()
