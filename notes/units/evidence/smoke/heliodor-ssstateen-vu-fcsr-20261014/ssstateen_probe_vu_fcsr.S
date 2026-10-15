/* Heliodor VU probe: observe FCSR state under the H.FCSR control. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    la      t0, m_trap
    csrw    mtvec, t0
    li      t0, -1
    csrw    0x30c, t0
    csrw    0x30d, t0
    csrw    0x30e, t0
    csrw    0x30f, t0
    li      t0, (1 << 2) | (1 << 8) | (1 << 22)
    csrw    medeleg, t0
    la      t0, hs_stage
    csrw    mepc, t0
    li      t0, 0x6800             /* FS=Initial, MRET to HS */
    csrw    mstatus, t0
    mret

hs_stage:
    la      t0, report
    la      t1, hs_trap
    csrw    stvec, t1
    csrw    hedeleg, zero
    csrw    0x60c, zero
    csrw    0x60d, zero
    csrw    0x60e, zero
    csrw    0x60f, zero
    csrr    t1, 0x60c
    sd      t1, 1184(t0)
    csrr    t1, 0x60d
    sd      t1, 1192(t0)
    csrr    t1, 0x60e
    sd      t1, 1200(t0)
    csrr    t1, 0x60f
    sd      t1, 1208(t0)
    li      t1, 2
    csrw    0x60c, t1              /* attempt H.FCSR=1 */
    csrr    t2, 0x60c
    sd      t2, 1312(t0)           /* H.FCSR readback */
    li      t1, 0x6000
    csrw    0x200, t1              /* VS FS=Initial */
    li      t1, 0x80               /* SPV=1, SPVP=0 */
    csrw    hstatus, t1
    li      t1, 0                  /* SPP=0 */
    csrw    sstatus, t1
    la      t1, vu_stage
    csrw    sepc, t1
    sret

vu_stage:
    la      t0, report
    li      t6, 311
    csrr    t1, 0x001              /* VU fflags read under H.FCSR clear */
    sd      t1, 1088(t0)
    li      t1, 411
    sd      t1, 1120(t0)
    li      t2, 1
    li      t6, 312
    csrw    0x001, t2              /* VU fflags write */
    li      t1, 412
    sd      t1, 1128(t0)
    li      t6, 313
    csrr    t1, 0x001              /* VU fflags readback */
    sd      t1, 1104(t0)
    li      t1, 413
    sd      t1, 1136(t0)
    li      t6, 399
    ecall

hs_trap:
    addi    sp, sp, -40
    sd      t0, 0(sp)
    sd      t1, 8(sp)
    sd      t2, 16(sp)
    sd      t3, 24(sp)
    sd      t4, 32(sp)
    la      t0, report
    ld      t1, 0(t0)
    csrr    t2, scause
    slli    t3, t1, 3
    addi    t4, t3, 8
    add     t4, t4, t0
    sd      t2, 0(t4)
    addi    t4, t3, 520
    add     t4, t4, t0
    sd      t6, 0(t4)
    addi    t1, t1, 1
    sd      t1, 0(t0)
    li      t3, 22
    beq     t2, t3, resume_vs
    li      t3, 2
    beq     t2, t3, resume_vs
    li      t3, 8
    bne     t2, t3, fail
    li      t0, 0x80001000
    li      t1, 1
    sw      t1, 0(t0)
1:  j       1b
resume_vs:
    csrr    t2, sepc
    addi    t2, t2, 4
    csrw    sepc, t2
    ld      t0, 0(sp)
    ld      t1, 8(sp)
    ld      t2, 16(sp)
    ld      t3, 24(sp)
    ld      t4, 32(sp)
    addi    sp, sp, 40
    sret

m_trap:
    la      t0, report
    csrr    t1, mcause
    sd      t1, 1400(t0)
    csrr    t1, mepc
    sd      t1, 1408(t0)
    li      t0, 0x80001000
    li      t1, 2
    sw      t1, 0(t0)
2:  j       2b
fail:
    li      t0, 0x80001000
    li      t1, 3
    sw      t1, 0(t0)
3:  j       3b

    .section .bss
    .align  4
report:
    .space  1536
stack:
    .space  256
stack_top:
