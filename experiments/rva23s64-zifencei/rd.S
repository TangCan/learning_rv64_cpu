/* Single-hart self-modifying code fixture for Zifencei Story 6.4. */
    .option norvc
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function
_start:
    la      t0, patched
    jalr    ra, t0, 0
    li      t2, 1
    bne     a0, t2, .Lbad

    li      t1, 0x02a00513       /* addi a0, zero, 42 */
    sw      t1, 0(t0)
    .globl  fence_i_instruction
fence_i_instruction:
    .word   0x0000108f
    jalr    ra, t0, 0
    li      t2, 42
    bne     a0, t2, .Lbad
    li      a0, 0
    li      t2, 1
    j       .Lfinish
.Lbad:
    li      a0, 1
    li      t2, 3
.Lfinish:
    la      t0, tohost
    sd      t2, 0(t0)
    bne     a0, zero, .Lbad_trap
    .globl  good_trap
good_trap:
    .word   0x0005006b
.Lbad_trap:
    li      a0, 1
    .word   0x0005006b
1:  j       1b

    .align  2
patched:
    li      a0, 1
    ret

    .section .tohost, "aw", @progbits
    .align  3
    .globl  tohost
tohost:
    .dword  0
