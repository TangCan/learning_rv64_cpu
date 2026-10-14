/* Supplemental scountovf access and delegated LCOFI case; separate from v4. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function

_start:
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f
    csrw    pmpcfg0, t0
    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 2                      /* frontend ifu_req event */
    csrw    mhpmevent3, t0
    li      t0, -1
    csrw    mhpmcounter3, t0
    li      t0, 8
    csrw    mcounteren, t0
    csrw    hcounteren, t0

    /* Create OF in hardware, then use that stable bit for access checks. */
    li      t0, 0
    csrw    mie, t0
    li      t0, 2
    csrw    mhpmevent3, t0
1:  addi    zero, zero, 0
    csrr    t0, mhpmevent3
    srli    t0, t0, 63
    beqz    t0, 1b
    csrr    t0, scountovf
    andi    t0, t0, 8
    beqz    t0, failed                 /* M-mode always sees OF */

    /* S sees the bit only when mcounteren[3] is set. */
    csrw    mcounteren, zero
    la      t0, s_mcounteren_off
    csrw    mepc, t0
    li      t0, 0x800                  /* MPP=S */
    csrw    mstatus, t0
    mret
s_mcounteren_off:
    csrr    t0, scountovf
    andi    t0, t0, 8
    bnez    t0, failed
    ecall

    li      t0, 8
    csrw    mcounteren, t0
    la      t0, s_mcounteren_on
    csrw    mepc, t0
    li      t0, 0x800
    csrw    mstatus, t0
    mret
s_mcounteren_on:
    csrr    t0, scountovf
    andi    t0, t0, 8
    li      t1, 8
    bne     t0, t1, failed
    ecall

    /* VS requires both mcounteren[3] and hcounteren[3]. */
    li      t0, 8
    csrw    mcounteren, t0
    csrw    hcounteren, zero
    la      t0, vs_hcounteren_off
    csrw    mepc, t0
    li      t0, 0x8000000800           /* MPV=1, MPP=S -> VS */
    csrw    mstatus, t0
    mret
vs_hcounteren_off:
    csrr    t0, scountovf
    andi    t0, t0, 8
    bnez    t0, failed
    ecall

    li      t0, 8
    csrw    hcounteren, t0
    csrw    mcounteren, zero
    la      t0, vs_mcounteren_off
    csrw    mepc, t0
    li      t0, 0x8000000800
    csrw    mstatus, t0
    mret
vs_mcounteren_off:
    csrr    t0, scountovf
    andi    t0, t0, 8
    bnez    t0, failed
    ecall

    li      t0, 8
    csrw    mcounteren, t0
    la      t0, vs_both_on
    csrw    mepc, t0
    li      t0, 0x8000000800
    csrw    mstatus, t0
    mret
vs_both_on:
    csrr    t0, scountovf
    andi    t0, t0, 8
    li      t1, 8
    bne     t0, t1, failed
    ecall

    /* Clear old OF/pending, then delegate a fresh hardware wrap to S. */
    li      t0, 2
    csrw    mhpmevent3, t0
    csrw    mip, zero
    li      t0, 0x2000
    csrw    mideleg, t0
    csrw    sie, t0                    /* delegated LCOFIE */
    la      t0, supervisor_trap
    csrw    stvec, t0
    li      t0, -1
    csrw    mhpmcounter3, t0
    li      t0, 2                      /* enable event before entering S */
    csrw    mhpmevent3, t0
    la      t0, s_wait_for_lcofi
    csrw    mepc, t0
    li      t0, 0x820                  /* MPP=S, SPIE=1 => SIE on mret */
    csrw    mstatus, t0
    mret
s_wait_for_lcofi:
    li      t4, 32
2:  csrr    t0, sstatus
    csrr    t1, sie
    csrr    t2, sip
    addi    t4, t4, -1
    bnez    t4, 2b
3:  j       3b

machine_trap:
    csrr    t0, mcause
    li      t1, 9
    beq     t0, t1, 3f
    li      t1, 10
    bne     t0, t1, failed             /* S/VS ecall probes return here */
3:
    csrr    t0, mepc
    addi    t0, t0, 4
    csrw    mepc, t0
    li      t0, 0x1800                 /* return to M for the next access case */
    csrw    mstatus, t0
    mret

supervisor_trap:
    csrr    t0, scause
    li      t1, 0x800000000000000d
    bne     t0, t1, failed             /* delegated interrupt must arrive as S cause 13 */
    csrr    t0, scountovf
    andi    t0, t0, 8
    li      t1, 8
    bne     t0, t1, failed
    csrr    t0, sip
    li      t1, 0x2000
    and     t0, t0, t1
    beqz    t0, failed                 /* delegated LCOFIP is visible in S */
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b

failed:
    li      a0, 1
    .word   0x0005006b
