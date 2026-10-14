/* Hardware-driven Sscofpmf overflow case for the locked Kunminghu fixture runner. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function
_start:
    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x2000
    csrw    mie, t0                    /* LCOFIE: interrupt cause 13 */

    /* Frontend selector 2 is ifu_req in the locked snapshot's event map. */
    li      t0, 0x4000000000000002     /* EVENT0=2, MINH=1 */
    csrw    mhpmevent3, t0
    csrw    mhpmcounter3, zero
    .rept 64
    addi    zero, zero, 0
    .endr
    csrr    t1, mhpmcounter3
    bnez    t1, failed

    li      t0, 2                      /* clear MINH, retain EVENT0=2 */
    csrw    mhpmevent3, t0
    csrw    mhpmcounter3, zero
    .rept 64
    addi    zero, zero, 0
    .endr
    csrr    t1, mhpmcounter3
    beqz    t1, failed                 /* hardware frontend events counted */

    /* Enable machine interrupts and let the hardware event wrap the counter. */
    li      t0, 8
    csrw    mstatus, t0
    li      t0, -1
    csrw    mhpmcounter3, t0
1:  j       1b                          /* must be interrupted by LCOFI */

machine_trap:
    csrr    t0, mcause
    li      t1, 0x800000000000000d
    bne     t0, t1, failed
    csrr    t0, mhpmevent3
    srli    t0, t0, 63
    beqz    t0, failed                 /* OF is sticky after hardware wrap */
    csrr    t0, scountovf
    andi    t0, t0, 8
    beqz    t0, failed                 /* counter 3 overflow is M-visible */
    j       passed

failed:
    li      a0, 1
    .word   0x0005006b
passed:
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b
    .size _start, .-_start
