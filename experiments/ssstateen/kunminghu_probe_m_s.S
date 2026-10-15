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
    li      s0, 0                  /* count each required M.SE gate trap */
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

    li      a1, 1
    li      t6, 4041
    ecall                          /* ask M to clear M.SE for sstateen1 */
sstateen1_blocked:
    li      t6, 4042
    csrr    t2, 0x10d              /* expected illegal-instruction cause 2 */
    li      t6, 4043
    csrr    t2, 0x10d              /* read after M.SE restoration */

    li      a1, 2
    li      t6, 4051
    ecall                          /* ask M to clear M.SE for sstateen2 */
sstateen2_blocked:
    li      t6, 4052
    csrr    t2, 0x10e              /* expected illegal-instruction cause 2 */
    li      t6, 4053
    csrr    t2, 0x10e              /* read after M.SE restoration */

    li      a1, 3
    li      t6, 4061
    ecall                          /* ask M to clear M.SE for sstateen3 */
sstateen3_blocked:
    li      t6, 4062
    csrr    t2, 0x10f              /* expected illegal-instruction cause 2 */
    li      t6, 4063
    csrr    t2, 0x10f              /* read after M.SE restoration */

    li      a1, 0
    li      t6, 4023
    ecall                          /* ask M handler to clear M SE0 */
s_blocked:
    li      t6, 4031
    csrr    t2, 0x10c              /* expected illegal-instruction cause 2 */
    li      t6, 4032
    csrr    t2, 0x10c              /* read after M SE0 restoration */
    li      a1, 4
    li      t6, 4073
    ecall                          /* expected final S ecall cause 9 */

m_trap:
    csrr    t0, mcause
    li      t1, 9
    beq     t0, t1, handle_ecall
    li      t1, 2
    bne     t0, t1, bad_trap
    addi    s0, s0, 1
    li      t1, -1
    csrw    0x30c, t1              /* restore M SE0 after the blocked access */
    li      t1, 1
    beq     a1, t1, skip_sstateen1
    li      t1, 2
    beq     a1, t1, skip_sstateen2
    li      t1, 3
    beq     a1, t1, skip_sstateen3
    csrr    t0, mepc
    addi    t0, t0, 4
    csrw    mepc, t0
    mret
skip_sstateen1:
    li      t1, -1
    csrw    0x30d, t1
    la      t0, sstateen1_blocked
    j       resume_s
skip_sstateen2:
    li      t1, -1
    csrw    0x30e, t1
    la      t0, sstateen2_blocked
    j       resume_s
skip_sstateen3:
    li      t1, -1
    csrw    0x30f, t1
    la      t0, sstateen3_blocked
resume_s:
    csrw    mepc, t0
    mret
handle_ecall:
    beqz    a1, clear_se0
    li      t1, 1
    beq     a1, t1, clear_sstateen1
    li      t1, 2
    beq     a1, t1, clear_sstateen2
    li      t1, 3
    beq     a1, t1, clear_sstateen3
    li      t1, 4
    beq     a1, t1, final_check
    j       bad_trap
final_check:
    li      t1, 4
    bne     s0, t1, bad_trap
    j       good_trap
clear_se0:
    csrw    0x30c, zero            /* clear M SE0 before the S access */
    la      t0, s_blocked
    j       resume_ecall
clear_sstateen1:
    csrw    0x30d, zero
    la      t0, sstateen1_blocked
    j       resume_ecall
clear_sstateen2:
    csrw    0x30e, zero
    la      t0, sstateen2_blocked
    j       resume_ecall
clear_sstateen3:
    csrw    0x30f, zero
    la      t0, sstateen3_blocked
resume_ecall:
    csrw    mepc, t0
    mret
bad_trap:
    li      a0, 1
    .word   0x0005006b
.globl good_trap
good_trap:
    .word   0x0005006b

    .section .bss
    .align  4
stack:
    .space  256
stack_top:
