/* An aligned 8-byte LD straddles a 4-byte TOR boundary: low half allowed, high half denied. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x20000801
    csrw    pmpaddr0, t0              /* TOR top: 0x80002004 */
    li      t0, 0x20000802
    csrw    pmpaddr1, t0              /* TOR top: 0x80002008 */
    li      t0, 0x2007ffff
    csrw    pmpaddr2, t0              /* fallback 4 MiB DRAM NAPOT */
    li      t0, 0x001f080f
    csrw    pmpcfg0, t0               /* entry 0: TOR RWX; 1: TOR deny; 2: RWX */
    csrr    t1, pmpaddr0
    li      t2, 0x20000801
    bne     t1, t2, failed
    csrr    t1, pmpaddr1
    li      t2, 0x20000802
    bne     t1, t2, failed
    csrr    t1, pmpaddr2
    li      t2, 0x2007ffff
    bne     t1, t2, failed
    csrr    t1, pmpcfg0
    li      t2, 0x001f080f
    bne     t1, t2, failed
    la      t0, supervisor_trap
    csrw    stvec, t0
    li      t0, 1 << 5
    csrw    medeleg, t0
    la      t0, supervisor_start
    csrw    mepc, t0
    li      t0, 0x800
    csrw    mstatus, t0
    mret

supervisor_start:
    li      t0, 0x80002000
.globl ld_data
.equ    ld_data, 0x80002000
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    j       failed

supervisor_trap:
    csrr    t0, scause
    li      t1, 5
    bne     t0, t1, failed
    la      t1, ld_target
    csrr    t2, sepc
    bne     t1, t2, failed
    csrr    t2, stval
    li      t3, 0x80002000
    bne     t2, t3, failed
    la      t0, tohost
    li      t1, 1
    sw      t1, 0(t0)
.globl good_trap
good_trap:
    .word   0x0005006b

machine_trap:
failed:
    li      a0, 1
    .word   0x0005006b

    .section .tohost,"aw",@progbits
    .balign 8
    .globl tohost
tohost:
    .word   0
