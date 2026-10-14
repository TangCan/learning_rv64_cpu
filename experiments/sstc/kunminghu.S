/* Single-case Kunminghu S-mode Sstc probe. Built with CASE_* by run.py. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function
_start:
    /* NAPOT, RWX, for the full address range containing this S-mode image. */
    li t0, -1
    csrw pmpaddr0, t0
    li t0, 0x1f
    csrw pmpcfg0, t0
    la t0, m_trap
    csrw mtvec, t0
    la t0, s_trap
    csrw stvec, t0
    li t0, (1 << 2)              /* delegate illegal-instruction gate traps to S */
    csrw medeleg, t0
    li t0, (1 << 5)
    csrw mideleg, t0             /* delegate STIP to S */
    li t0, (1 << 1)
    csrw mcounteren, t0
    li t0, (1 << 63)
    csrw menvcfg, t0

#if defined(CASE_S_STCE_OFF)
    csrw menvcfg, zero
#elif defined(CASE_S_TM_OFF)
    csrw mcounteren, zero
#endif
    li t0, (1 << 11)              /* MPP = S */
    csrw mstatus, t0
    la t0, s_probe
    csrw mepc, t0
    mret

s_probe:
#if defined(CASE_S_STCE_OFF) || defined(CASE_S_TM_OFF)
target_access:
    csrw 0x14d, zero              /* stimecmp: must trap with cause 2 */
    j fail
#else
    li t0, -1
    csrw 0x14d, t0
    csrr t3, sip
    andi t3, t3, (1 << 5)
    bnez t3, fail                 /* pending low before target write */
    csrr t0, time                 /* single sample also defines equality */
#if defined(CASE_S_LT)
    li t1, 10000
    add t1, t0, t1
#elif defined(CASE_S_EQ)
    mv t1, t0
#elif defined(CASE_S_GT)
    addi t1, t0, -1
#else
    j fail
#endif
    csrw 0x14d, t1
 #if defined(CASE_S_LT)
    csrr t3, mip
    andi t3, t3, (1 << 5)
    bnez t3, fail                /* < must initially leave pending low */
#endif
    li t2, 100000                 /* bounded eventual-pending observation */
1:  csrr t3, mip
    andi t3, t3, (1 << 5)
    bnez t3, 2f
    addi t2, t2, -1
    bnez t2, 1b
    j fail                       /* eventual pending did not appear */
2:  li t0, (1 << 5)
    csrs sie, t0
    li t0, (1 << 1)
    csrs sstatus, t0
6:  j 6b
#endif
fail:
    li a0, 1
    ecall

s_trap:
    csrr t0, scause
#if defined(CASE_S_STCE_OFF) || defined(CASE_S_TM_OFF)
    li t1, 2
    bne t0, t1, fail
    la t1, target_access
    csrr t0, sepc
    bne t0, t1, fail             /* expected trap is the target stimecmp CSR */
    li a0, 0
#else
    li t1, 0x8000000000000005
    bne t0, t1, fail
    csrr t0, sip
    andi t0, t0, (1 << 5)
    beqz t0, fail
    li t0, -1
    csrw 0x14d, t0               /* disarm; pending clears eventually */
7:  csrr t0, sip
    andi t0, t0, (1 << 5)
    bnez t0, 7b
    li a0, 0
#endif
    ecall

m_trap:
    csrr t0, mcause
    li t1, 9                      /* S-mode ecall reports pass/fail in a0 */
    bne t0, t1, fail_m
    beqz a0, good_trap
fail_m:
    li a0, 1
    j good_trap
    .globl good_trap
good_trap:
    .word 0x0005006b
    .size _start, .-_start
