/* Locked PMP denies one DRAM NAPOT page; the M-mode trap path stays accessible. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x80002000
    srli    t1, t0, 2
    ori     t1, t1, 0x1ff
    csrw    pmpaddr0, t1
    li      t1, 0x98
    csrw    pmpcfg0, t1
    csrr    t2, pmpaddr0
    li      t3, 0x200009ff
    bne     t2, t3, failed
    csrr    t2, pmpcfg0
    li      t3, 0x98
    bne     t2, t3, failed
.globl ld_data
.equ    ld_data, 0x80002000
    li      t0, 0x80002000
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    j       failed

machine_trap:
    csrr    t0, mcause
    li      t1, 5
    bne     t0, t1, failed
    la      t1, ld_target
    csrr    t2, mepc
    bne     t1, t2, failed
    csrr    t2, mtval
    li      t3, 0x80002000
    bne     t2, t3, failed
    la      t0, tohost
    li      t1, 1
    sw      t1, 0(t0)
.globl good_trap
good_trap:
    .word   0x0005006b

failed:
    li      a0, 1
    .word   0x0005006b

    .section .tohost,"aw",@progbits
    .balign 8
    .globl tohost
tohost:
    .word   0
