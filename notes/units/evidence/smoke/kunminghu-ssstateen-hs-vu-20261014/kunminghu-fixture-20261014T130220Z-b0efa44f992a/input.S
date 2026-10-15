/* VU FCSR availability probe with native trace; this does not claim a stateen gate pass. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f
    csrw    pmpcfg0, t0
    li      t6, 3001
    csrr    t2, misa               /* dynamically record F availability */
    li      t6, 3002
    csrr    t2, 0x30c              /* M FCSR control reads RO-zero */
    li      t0, 0x6800             /* FS=Dirty, MPP=HS */
    csrw    mstatus, t0
    li      t0, (1 << 2) | (1 << 8) /* delegate illegal instruction and U ecall to HS */
    csrw    medeleg, t0
    la      t0, hs_stage
    csrw    mepc, t0
    mret

hs_stage:
    li      t6, 3003
    csrr    t2, 0x60c              /* H FCSR control reads RO-zero */
    li      t6, 3004
    csrr    t2, 0x10c              /* S FCSR control reads RO-zero */
    la      t0, hs_trap
    csrw    stvec, t0
    csrw    hedeleg, zero
    li      t0, 0x80               /* SPV=1, SPVP=0: sret to VU */
    csrw    hstatus, t0
    li      t0, 0x6000             /* enable FS in HS view */
    csrw    sstatus, t0
    csrw    0x200, t0              /* enable FS in VS status */
    la      t0, vu_stage
    csrw    sepc, t0
    sret

vu_stage:
    li      t6, 3011
    csrr    t2, 0x001              /* VU fflags read with FS enabled */
    li      t6, 3012
    ecall                          /* expected U ecall cause 8 in HS */

hs_trap:
    csrr    t0, scause
    li      t1, 8
    bne     t0, t1, bad_trap
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b
bad_trap:
    li      a0, 1
    .word   0x0005006b

    .section .bss
    .align  4
stack:
    .space  256
stack_top:
