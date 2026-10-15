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
    li      t0, (1 << 10) | (1 << 22)
    csrw    medeleg, t0              /* delegate VS ecall and virtual-instruction to HS */
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

    /* Clear H SE0 so VS access to sstateen0 must raise virtual-instruction. */
    li      t4, 1
    slli    t4, t4, 63
    not     t4, t4
    li      t6, 2015
    csrw    0x60c, t4
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
    li      t1, -1                 /* trap handler used t1 for cause 22 */
    csrw    0x10c, t1              /* VS virtual sstateen0 write */
    li      t6, 2023
    csrr    t2, 0x10c              /* VS readback after write */
    li      t6, 2024
    ecall                          /* expected VS ecall cause 10 in HS */

hs_trap:
    csrr    t0, scause
    li      t1, 22
    beq     t0, t1, open_vs_gate
    li      t1, 10
    bne     t0, t1, bad_trap
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b
bad_trap:
    li      a0, 1
    .word   0x0005006b

open_vs_gate:
    li      t4, 1
    slli    t4, t4, 63
    li      t6, 2016
    csrw    0x60c, t4              /* restore H SE0 before resuming VS */
    csrr    t0, sepc
    addi    t0, t0, 4              /* skip faulting VS CSR instruction */
    csrw    sepc, t0
    sret

    .section .bss
    .align  4
stack:
    .space  256
stack_top:
