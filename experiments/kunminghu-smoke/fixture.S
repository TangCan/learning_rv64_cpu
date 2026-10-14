/* Small, self-checking RV64I program for the locked Kunminghu smoke target. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function
_start:
    addi t0, zero, 7
    addi t1, zero, 11
    add  t2, t0, t1
    addi t3, zero, 18
    bne  t2, t3, .Lbad

    /* XiangShan's pinned NEMU trap instruction consumes a0: zero passes. */
    addi a0, zero, 0
    .globl good_trap
good_trap:
    .word 0x0005006b
.Lbad:
    addi a0, zero, 1
    .word 0x0005006b
    .size _start, .-_start
