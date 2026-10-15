/* Heliodor S-mode probe: read back all M.SE controls and test all four S CSRs. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    la      t0, m_trap
    csrw    mtvec, t0
    la      t0, report
    csrw    mscratch, t0

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

    /* Switch through M into S after the HS path, then probe all four S CSRs. */
    li      t6, 22
    ecall

s_stage:
    la      t0, report
    li      t1, -1
    li      t6, 23
    ecall                          /* M clears M.SE0-3 before S reads */
    li      t6, 43
    csrr    t2, 0x10c
    sd      t6, 1264(t0)
    sd      t2, 1296(t0)
    li      t6, 44
    csrr    t2, 0x10d
    sd      t6, 1272(t0)
    sd      t2, 1304(t0)
    li      t6, 45
    csrr    t2, 0x10e
    sd      t6, 1280(t0)
    sd      t2, 1312(t0)
    li      t6, 46
    csrr    t2, 0x10f
    sd      t6, 1288(t0)
    sd      t2, 1320(t0)
    li      t6, 24
    ecall                          /* M attempts to set M.SE0-3 and reads them back */
    li      t6, 47
    csrr    t2, 0x10c
    sd      t6, 1328(t0)
    sd      t2, 1360(t0)
    li      t6, 48
    csrr    t2, 0x10d
    sd      t6, 1336(t0)
    sd      t2, 1368(t0)
    li      t6, 49
    csrr    t2, 0x10e
    sd      t6, 1344(t0)
    sd      t2, 1376(t0)
    li      t6, 50
    csrr    t2, 0x10f
    sd      t6, 1352(t0)
    sd      t2, 1384(t0)
    li      t6, 30
    csrr    t2, 0x10c
    sd      t2, 1200(t0)
    li      t6, 31
    csrw    0x10c, t1
    li      t6, 32
    csrr    t2, 0x10c
    sd      t2, 1208(t0)
    li      t6, 33
    csrr    t2, 0x10d
    sd      t2, 1216(t0)
    li      t6, 34
    csrw    0x10d, t1
    li      t6, 35
    csrr    t2, 0x10d
    sd      t2, 1224(t0)
    li      t6, 36
    csrr    t2, 0x10e
    sd      t2, 1232(t0)
    li      t6, 37
    csrw    0x10e, t1
    li      t6, 38
    csrr    t2, 0x10e
    sd      t2, 1240(t0)
    li      t6, 39
    csrr    t2, 0x10f
    sd      t2, 1248(t0)
    li      t6, 40
    csrw    0x10f, t1
    li      t6, 41
    csrr    t2, 0x10f
    sd      t2, 1256(t0)
    li      t6, 42
    ecall

finalize:
    la      t0, report
    ld      t1, 272(t0)
    ld      t2, 224(t0)
    srli    t2, t2, 63
    slli    t1, t1, 1
    or      t1, t1, t2
    li      t0, 0x80001000
    sw      t1, 0(t0)
1:  j       1b

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
    li      t3, 9              /* environment call from HS or S */
    bne     t2, t3, trap_resume
    li      t3, 21
    beq     t6, t3, enable_hs
    li      t3, 22
    beq     t6, t3, enter_s
    li      t3, 23
    beq     t6, t3, clear_m_se0
    li      t3, 24
    beq     t6, t3, set_m_se0
    li      t3, 42
    beq     t6, t3, finalize
    j       trap_resume

enable_hs:
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
    j       trap_resume
enter_s:
    la      t4, s_stage
    csrw    mepc, t4
    li      t4, 0x800
    csrw    mstatus, t4
    ld      t0, 0(sp)
    ld      t1, 8(sp)
    ld      t2, 16(sp)
    addi    sp, sp, 32
    mret
clear_m_se0:
    csrw    0x30c, zero
    csrw    0x30d, zero
    csrw    0x30e, zero
    csrw    0x30f, zero
    la      t0, report
    li      t4, 2301
    sd      t4, 1392(t0)
    csrr    t4, 0x30c
    sd      t4, 1424(t0)
    li      t4, 2302
    sd      t4, 1400(t0)
    csrr    t4, 0x30d
    sd      t4, 1432(t0)
    li      t4, 2303
    sd      t4, 1408(t0)
    csrr    t4, 0x30e
    sd      t4, 1440(t0)
    li      t4, 2304
    sd      t4, 1416(t0)
    csrr    t4, 0x30f
    sd      t4, 1448(t0)
    j       trap_resume
set_m_se0:
    li      t4, 0x8000000000000000
    csrw    0x30c, t4
    csrw    0x30d, t4
    csrw    0x30e, t4
    csrw    0x30f, t4
    la      t0, report
    li      t4, 2305
    sd      t4, 1456(t0)
    csrr    t4, 0x30c
    sd      t4, 1488(t0)
    li      t4, 2306
    sd      t4, 1464(t0)
    csrr    t4, 0x30d
    sd      t4, 1496(t0)
    li      t4, 2307
    sd      t4, 1472(t0)
    csrr    t4, 0x30e
    sd      t4, 1504(t0)
    li      t4, 2308
    sd      t4, 1480(t0)
    csrr    t4, 0x30f
    sd      t4, 1512(t0)
    j       trap_resume
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
    .space  1536
stack:
    .space  256
stack_top:
