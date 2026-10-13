/*
 * Local Kunminghu FENCE.I fixture source.
 * Intended for a bare-metal RV64 test harness with writable/executable RAM.
 * The runner must provide a `tohost` word and place this section in RAM.
 */
    .option norvc
    .section .text
    .align  2
    .globl  _start
_start:
    la      t0, patched
    jalr    ra, t0, 0
    li      t2, 1
    bne     a0, t2, fail

    li      t1, 0x02a00513       /* addi a0, zero, 42 */
    sw      t1, 0(t0)
    fence.i
    jalr    ra, t0, 0
    li      t2, 42
    bne     a0, t2, fail
    li      t2, 0x600d
    j       report

fail:
    li      t2, 1
report:
    la      t0, tohost
    sd      t2, 0(t0)
1:  j       1b

    .align  2
patched:
    li      a0, 1
    ret

    .section .tohost,"aw",@progbits
    .align  3
    .globl  tohost
tohost:
    .dword  0
