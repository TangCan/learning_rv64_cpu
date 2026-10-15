/* Focused HS/VS access probe: leave the existing M/HS matrix input untouched. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f              /* NAPOT allow RWX, matching ssnpm fixture */
    csrw    pmpcfg0, t0
    li      t1, -1
    li      t6, 2001
    csrw    0x30c, t1              /* open M SE0 */
    li      t6, 2002
    csrw    0x60c, t1              /* open H SE0 */
    li      t0, 1 << 10
    csrw    medeleg, t0              /* delegate VS ecall to HS */
    la      t0, hs_stage
    csrw    mepc, t0
    li      t0, 0x800              /* MRET to HS (MPP=S with H enabled) */
    csrw    mstatus, t0
    mret

hs_stage:
    li      t6, 2011
    csrr    t2, 0x10c              /* HS sstateen0 read */
    li      t6, 2012
    csrw    0x10c, t1              /* HS sstateen0 write */
    li      t6, 2013
    csrr    t2, 0x60c              /* HS hstateen0 read */
    li      t6, 2014
    csrw    0x60c, t1              /* HS hstateen0 write */

    la      t0, hs_trap
    csrw    stvec, t0
    csrw    hedeleg, zero
    li      t0, 0x180              /* SPV=1, SPVP=1: sret to VS */
    csrw    hstatus, t0
    li      t0, 0x100              /* SPP=1: supervisor privilege */
    csrw    sstatus, t0
    la      t0, vs_stage
    csrw    sepc, t0
    sret

vs_stage:
    li      t6, 2021
    csrr    t2, 0x10c              /* VS virtual sstateen0 read */
    li      t6, 2022
    csrw    0x10c, t1              /* VS virtual sstateen0 write */
    li      t6, 2023
    ecall                          /* expected VS ecall cause 10 in HS */

hs_trap:
    csrr    t0, scause
    li      t1, 10
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
