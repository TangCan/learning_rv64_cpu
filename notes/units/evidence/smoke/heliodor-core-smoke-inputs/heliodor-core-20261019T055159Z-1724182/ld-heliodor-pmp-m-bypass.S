/* An unlocked no-permission NAPOT match must be bypassed by M-mode. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x80002000
    ld      s0, 0(t0)
    srli    t1, t0, 2
    ori     t1, t1, 0x1ff
    csrw    pmpaddr0, t1
    li      t1, 0x18
    csrw    pmpcfg0, t1
    csrr    t2, pmpaddr0
    li      t3, 0x200009ff
    bne     t2, t3, failed
    csrr    t2, pmpcfg0
    li      t3, 0x18
    bne     t2, t3, failed
    .rept   256
    nop
    .endr
.globl ld_data
.equ    ld_data, 0x80002000
    li      t0, 0x80002000
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    bne     t1, s0, failed
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
