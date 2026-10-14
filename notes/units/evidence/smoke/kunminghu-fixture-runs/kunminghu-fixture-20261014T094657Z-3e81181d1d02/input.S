/* Hardware-driven Sscofpmf overflow case for the locked Kunminghu fixture runner. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function

/* Each case proves the inhibit bit suppresses a real selected event, then
 * proves that clearing the bit permits the same hardware event to increment. */
    .macro FILTER_CASE name, mstatus_value, filter_value, ecall_cause, inhibit_fail_bit, enabled_fail_bit
    li      t0, \filter_value
    csrw    mhpmevent3, t0
    csrw    mhpmcounter3, zero
    li      t0, \ecall_cause
    csrw    mscratch, t0
    li      t0, \mstatus_value
    csrw    mstatus, t0
    la      t0, \name\()_filtered
    csrw    mepc, t0
    mret
\name\()_filtered:
    csrr    t2, hpmcounter3            /* establish the target-mode baseline */
    .rept 64
    addi    zero, zero, 0
    .endr
    csrr    t1, hpmcounter3
    beq     t1, t2, 1f
    ori     t3, t3, \inhibit_fail_bit
1:
    ecall
    li      t0, 2                      /* same event, inhibit cleared */
    csrw    mhpmevent3, t0
    csrw    mhpmcounter3, zero
    li      t0, \mstatus_value
    csrw    mstatus, t0
    la      t0, \name\()_enabled
    csrw    mepc, t0
    mret
\name\()_enabled:
    csrr    t2, hpmcounter3
    .rept 64
    addi    zero, zero, 0
    .endr
    csrr    t1, hpmcounter3
    bne     t1, t2, 2f
    ori     t3, t3, \enabled_fail_bit
2:
    ecall
    .endm

_start:
    li      t0, -1
    csrw    pmpaddr0, t0               /* grant S/VS/U/VU access to the image */
    li      t0, 0x1f
    csrw    pmpcfg0, t0                /* NAPOT, RWX */
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

    /* Exercise each lower/virtual privilege filter in both states. */
    li      t0, 8
    csrw    mcounteren, t0              /* permit S/U HPM counter reads */
    csrw    hcounteren, t0              /* permit VS/VU HPM counter reads */
    li      t3, 0                        /* accumulate per-mode assertion failures */
    FILTER_CASE s_filter, 0x800, 0x2000000000000002, 9, 1, 2
    FILTER_CASE u_filter, 0x0,   0x1000000000000002, 8, 4, 8
    FILTER_CASE vs_filter, 0x8000000800, 0x0800000000000002, 10, 16, 32
    FILTER_CASE vu_filter, 0x8000000000, 0x0400000000000002, 8, 64, 128

    /* Enable machine interrupts and let the hardware event wrap the counter. */
    li      t0, 2
    csrw    mhpmevent3, t0
    li      t0, 13
    csrw    mscratch, t0
    li      t0, 8
    csrw    mstatus, t0
    li      t0, -1
    csrw    mhpmcounter3, t0
1:  j       1b                          /* must be interrupted by LCOFI */

machine_trap:
    csrr    t0, mcause
    li      t1, 0x800000000000000d
    beq     t0, t1, overflow_trap
    csrr    t1, mscratch
    beq     t0, t1, 3f
    ori     t3, t3, 256                /* unexpected lower/virtual ecall destination */
3:
    csrr    t0, mepc
    addi    t0, t0, 4                  /* exception mepc points at the ecall itself */
    csrw    mepc, t0
    li      t0, 0x1800                  /* return from the probe to M-mode */
    csrw    mstatus, t0
    mret

overflow_trap:
    csrr    t0, mhpmevent3
    srli    t0, t0, 63
    beqz    t0, failed                 /* OF is sticky after hardware wrap */
    csrr    t0, scountovf
    andi    t0, t0, 8
    beqz    t0, failed                 /* counter 3 overflow is M-visible */
    bnez    t3, failed                 /* all four filter mode pairs have run */
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
