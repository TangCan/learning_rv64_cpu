/* M/HS self-checking stateen probe for locked Kunminghu; no upstream source edits. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    la      t0, m_trap
    csrw    mtvec, t0
    la      t0, report
    csrw    mscratch, t0

    /* M stateen writable bits reset to zero; keep these apart from S/H unspecified reset values. */
    csrr    t1, 0x30c
    sd      t1, 1824(t0)
    csrr    t1, 0x30d
    sd      t1, 1832(t0)
    csrr    t1, 0x30e
    sd      t1, 1840(t0)
    csrr    t1, 0x30f
    sd      t1, 1848(t0)
    /* Record reset contents; stateen reset requirements differ by level. */
    csrr    t1, 0x10c
    sd      t1, 0(t0)
    csrr    t1, 0x10d
    sd      t1, 8(t0)
    csrr    t1, 0x10e
    sd      t1, 16(t0)
    csrr    t1, 0x10f
    sd      t1, 24(t0)
    csrr    t1, 0x60c
    sd      t1, 32(t0)
    csrr    t1, 0x60d
    sd      t1, 40(t0)
    csrr    t1, 0x60e
    sd      t1, 48(t0)
    csrr    t1, 0x60f
    sd      t1, 56(t0)

    /* M-mode write/readback probes, with M SE bits opened for read masking. */
    li      t1, -1
    csrw    0x30c, t1
    csrw    0x30d, t1
    csrw    0x30e, t1
    csrw    0x30f, t1
    csrw    0x10c, t1
    csrr    t2, 0x10c
    sd      t2, 96(t0)
    csrw    0x10d, t1
    csrr    t2, 0x10d
    sd      t2, 104(t0)
    csrw    0x10e, t1
    csrr    t2, 0x10e
    sd      t2, 112(t0)
    csrw    0x10f, t1
    csrr    t2, 0x10f
    sd      t2, 120(t0)
    csrw    0x60c, t1
    csrr    t2, 0x60c
    sd      t2, 128(t0)
    csrw    0x60d, t1
    csrr    t2, 0x60d
    sd      t2, 136(t0)
    csrw    0x60e, t1
    csrr    t2, 0x60e
    sd      t2, 144(t0)
    csrw    0x60f, t1
    csrr    t2, 0x60f
    sd      t2, 152(t0)

    /* Explicitly clear M controls before the HS blocked phase. */
    csrw    0x30c, zero          /* mstateen0: SE0 and ENVCFG clear */
    csrw    0x30d, zero
    csrw    0x30e, zero
    csrw    0x30f, zero
    csrw    0x60c, zero
    csrw    0x60d, zero
    csrw    0x60e, zero
    csrw    0x60f, zero
    la      t0, report
    csrr    t2, 0x30c
    sd      t2, 64(t0)
    csrr    t2, 0x30d
    sd      t2, 72(t0)
    csrr    t2, 0x30e
    sd      t2, 80(t0)
    csrr    t2, 0x30f
    sd      t2, 88(t0)

    la      t0, hs_blocked
    csrw    mepc, t0
    li      t1, 0x800
    csrw    mstatus, t1          /* MPP=HS/S */
    mret

/* IDs 1-20 identify each gated CSR operation; handler records ID+mcause per trap. */
/* With M stateen SE bits and ENVCFG clear, these HS accesses should trap. */
hs_blocked:
    li      t1, -1
    li      t6, 1          /* blocked access ID */
    csrw    0x10c, t1
    li      t6, 2          /* blocked access ID */
    csrr    t2, 0x10c
    li      t6, 3          /* blocked access ID */
    csrw    0x10d, t1
    li      t6, 4          /* blocked access ID */
    csrr    t2, 0x10d
    li      t6, 5          /* blocked access ID */
    csrw    0x10e, t1
    li      t6, 6          /* blocked access ID */
    csrr    t2, 0x10e
    li      t6, 7          /* blocked access ID */
    csrw    0x10f, t1
    li      t6, 8          /* blocked access ID */
    csrr    t2, 0x10f
    li      t6, 9          /* blocked access ID */
    csrw    0x60c, t1
    li      t6, 10          /* blocked access ID */
    csrr    t2, 0x60c
    li      t6, 11          /* blocked access ID */
    csrw    0x60d, t1
    li      t6, 12          /* blocked access ID */
    csrr    t2, 0x60d
    li      t6, 13          /* blocked access ID */
    csrw    0x60e, t1
    li      t6, 14          /* blocked access ID */
    csrr    t2, 0x60e
    li      t6, 15          /* blocked access ID */
    csrw    0x60f, t1
    li      t6, 16          /* blocked access ID */
    csrr    t2, 0x60f
    li      t6, 17          /* blocked access ID */
    csrw    0x60a, t1
    li      t6, 18          /* blocked access ID */
    csrr    t2, 0x60a            /* henvcfg */
    li      t6, 19          /* blocked access ID */
    csrw    0x10a, t1
    li      t6, 20          /* blocked access ID */
    csrr    t2, 0x10a            /* senvcfg */
    li      t6, 21             /* HS ecall control-flow marker */
    ecall                        /* M trap enables the controls, then resumes */

/* With SE0/ENVCFG enabled, read/write all required CSRs and capture results. */
hs_enabled:
    la      t0, report
    li      t1, -1
    csrw    0x10c, t1
    csrr    t2, 0x10c
    sd      t2, 192(t0)
    csrw    0x10d, t1
    csrr    t2, 0x10d
    sd      t2, 200(t0)
    csrw    0x10e, t1
    csrr    t2, 0x10e
    sd      t2, 208(t0)
    csrw    0x10f, t1
    csrr    t2, 0x10f
    sd      t2, 216(t0)
    csrw    0x60c, t1
    csrr    t2, 0x60c
    sd      t2, 224(t0)
    csrw    0x60d, t1
    csrr    t2, 0x60d
    sd      t2, 232(t0)
    csrw    0x60e, t1
    csrr    t2, 0x60e
    sd      t2, 240(t0)
    csrw    0x60f, t1
    csrr    t2, 0x60f
    sd      t2, 248(t0)
    csrw    0x60a, t1
    csrr    t2, 0x60a
    sd      t2, 256(t0)
    csrw    0x10a, t1
    csrr    t2, 0x10a
    sd      t2, 264(t0)

    /* Assert M reset, normative WARL/RO-zero fields, all 20 gate traps, and H SE bits. */
    la      t0, report
    ld      t1, 1824(t0)
    bnez    t1, bad_trap
    ld      t1, 1832(t0)
    bnez    t1, bad_trap
    ld      t1, 1840(t0)
    bnez    t1, bad_trap
    ld      t1, 1848(t0)
    bnez    t1, bad_trap
    ld      t1, 272(t0)
    li      t2, 21
    bne     t1, t2, bad_trap
    li      t3, 0
check_gate_trace:
    li      t4, 20
    beq     t3, t4, check_ecall_trace
    slli    t4, t3, 3
    addi    t5, t4, 280
    add     t5, t5, t0
    ld      a1, 0(t5)
    li      a2, 2
    bne     a1, a2, bad_trap
    addi    t5, t4, 800
    add     t5, t5, t0
    ld      a1, 0(t5)
    addi    a2, t3, 1
    bne     a1, a2, bad_trap
    addi    t3, t3, 1
    j       check_gate_trace
check_ecall_trace:
    ld      t1, 440(t0)
    li      t2, 9
    bne     t1, t2, bad_trap
    ld      t1, 960(t0)
    li      t2, 21
    bne     t1, t2, bad_trap
    /* sstateen0 JVT/FCSR and sstateen1-3 are normative RO-zero. */
    ld      t1, 96(t0)
    andi    t1, t1, 6
    bnez    t1, bad_trap
    ld      t1, 104(t0)
    bnez    t1, bad_trap
    ld      t1, 112(t0)
    bnez    t1, bad_trap
    ld      t1, 120(t0)
    bnez    t1, bad_trap
    ld      t1, 136(t0)
    slli    t1, t1, 1
    srli    t1, t1, 1
    bnez    t1, bad_trap
    ld      t1, 144(t0)
    slli    t1, t1, 1
    srli    t1, t1, 1
    bnez    t1, bad_trap
    ld      t1, 152(t0)
    slli    t1, t1, 1
    srli    t1, t1, 1
    bnez    t1, bad_trap
    /* H SE0/SE bits must survive the set-gate write/read phase. */
    li      t3, 0
check_hstateen:
    li      t4, 4
    beq     t3, t4, success_trap
    slli    t4, t3, 3
    addi    t5, t4, 128
    add     t5, t5, t0
    ld      a1, 0(t5)
    srli    a1, a1, 63
    beqz    a1, bad_trap
    addi    t5, t4, 224
    add     t5, t5, t0
    ld      a1, 0(t5)
    srli    a1, a1, 63
    beqz    a1, bad_trap
    addi    t3, t3, 1
    j       check_hstateen
success_trap:
    li      a0, 0
    .globl good_trap
    .word   0x0005006b
bad_trap:
    li      a0, 1
    .word   0x0005006b

/* Trap count at report+272; mcause/operation-ID arrays at +280/+800, capped at 64 records. */
/* Every synchronous trap resumes at the next 32-bit op. */
m_trap:
    addi    sp, sp, -32
    sd      t0, 0(sp)
    sd      t1, 8(sp)
    sd      t2, 16(sp)
    la      t0, report
    ld      t1, 272(t0)
    csrr    t2, mcause
    li      t3, 64
    bgeu    t1, t3, trap_skip_record
    slli    t3, t1, 3
    addi    t4, t3, 280
    add     t4, t4, t0
    sd      t2, 0(t4)          /* mcause log */
    addi    t4, t3, 800
    add     t4, t4, t0
    sd      t6, 0(t4)          /* operation ID log */
trap_skip_record:
    addi    t1, t1, 1
    sd      t1, 272(t0)
    csrr    t2, mcause
    li      t3, 9              /* environment call from HS */
    bne     t2, t3, trap_resume

    /* Enable SE0/ENVCFG and all SE bits, then resume at hs_enabled. */
    li      t4, -1
    slli    t4, t4, 62
    csrw    0x30c, t4
    csrw    0x60c, t4
    li      t4, 0x8000000000000000
    csrw    0x30d, t4
    csrw    0x60d, t4
    csrw    0x30e, t4
    csrw    0x60e, t4
    csrw    0x30f, t4
    csrw    0x60f, t4
trap_resume:
    csrr    t2, mepc
    addi    t2, t2, 4
    csrw    mepc, t2
    ld      t0, 0(sp)
    ld      t1, 8(sp)
    ld      t2, 16(sp)
    addi    sp, sp, 32
    mret

    .section .bss
    .align  4
report:
    .space  2048
stack:
    .space  256
stack_top:
