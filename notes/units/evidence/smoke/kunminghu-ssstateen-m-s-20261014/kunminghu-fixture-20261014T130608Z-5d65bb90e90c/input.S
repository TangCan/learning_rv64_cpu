/* Focused M/S path: all four sstateen slots plus an SE0 clear/set trap pair. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    la      sp, stack_top
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f
    csrw    pmpcfg0, t0
    li      t1, -1
    li      t6, 4001
    csrw    0x30c, t1              /* M SE0 */
    li      t6, 4002
    csrw    0x30d, t1              /* M SE for slot 1 */
    li      t6, 4003
    csrw    0x30e, t1              /* M SE for slot 2 */
    li      t6, 4004
    csrw    0x30f, t1              /* M SE for slot 3 */
    la      t0, m_trap
    csrw    mtvec, t0
    la      t0, s_stage
    csrw    mepc, t0
    li      t0, 0x800              /* MRET to S */
    csrw    mstatus, t0
    mret

s_stage:
    li      t6, 4011
    csrr    t2, 0x10c              /* sstateen0 initial observation */
    li      t6, 4012
    csrw    0x10c, t1
    li      t6, 4013
    csrr    t2, 0x10c
    li      t6, 4014
    csrr    t2, 0x10d              /* sstateen1 initial observation */
    li      t6, 4015
    csrw    0x10d, t1
    li      t6, 4016
    csrr    t2, 0x10d
    li      t6, 4017
    csrr    t2, 0x10e              /* sstateen2 initial observation */
    li      t6, 4018
    csrw    0x10e, t1
    li      t6, 4019
    csrr    t2, 0x10e
    li      t6, 4020
    csrr    t2, 0x10f              /* sstateen3 initial observation */
    li      t6, 4021
    csrw    0x10f, t1
    li      t6, 4022
    csrr    t2, 0x10f

    li      a0, 0
    li      t6, 4023
    ecall                          /* ask M handler to clear M SE0 */
s_blocked:
    li      t6, 4031
    csrr    t2, 0x10c              /* expected illegal-instruction cause 2 */
    li      t6, 4032
    csrr    t2, 0x10c              /* read after M SE0 restoration */
    li      a0, 1
    li      t6, 4033
    ecall                          /* expected final S ecall cause 9 */

m_trap:
    csrr    t0, mcause
    li      t1, 9
    beq     t0, t1, handle_ecall
    li      t1, 2
    bne     t0, t1, bad_trap
    li      t1, -1
    csrw    0x30c, t1              /* restore M SE0 after the blocked access */
    csrr    t0, mepc
    addi    t0, t0, 4
    csrw    mepc, t0
    mret
handle_ecall:
    bnez    a0, good_trap
    csrw    0x30c, zero            /* clear M SE0 before the S access */
    la      t0, s_blocked
    csrw    mepc, t0
    mret
bad_trap:
    li      a0, 2
    .word   0x0005006b
.globl good_trap
good_trap:
    .word   0x0005006b

    .section .bss
    .align  4
stack:
    .space  256
stack_top:
