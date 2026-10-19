/* Control: an aligned 8-byte LD stays inside one RWX TOR entry. */
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
    li      t0, 0x001f0f0f
    csrw    pmpcfg0, t0               /* entries 0 and 1: TOR RWX; entry 2: RWX */
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
    li      t2, 0x001f0f0f
    bne     t1, t2, failed

    li      t0, 0x80001ff8
    li      t1, 0x1122334455667788
    sd      t1, 0(t0)
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
    li      t0, 0x80001ff8
.globl ld_data
.equ    ld_data, 0x80001ff8
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    li      t2, 0x1122334455667788
    bne     t1, t2, failed
    la      t0, tohost
    li      t1, 1
    sw      t1, 0(t0)
.globl good_trap
good_trap:
    .word   0x0005006b

supervisor_trap:
machine_trap:
failed:
    li      a0, 1
    .word   0x0005006b

    .section .tohost,"aw",@progbits
    .balign 8
    .globl tohost
tohost:
    .word   0
