/* The code is mapped through an allowed 2 MiB leaf; target VA uses a denied L1 table page. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    li      t0, 0x80003000
    li      t1, 0x20001801
    sd      t1, 8(t0)                  /* root[1] -> denied L1 table at 0x80006000 */
    li      t1, 0x20001001
    sd      t1, 16(t0)                 /* root[2] -> allowed L1 table at 0x80004000 */
    li      t0, 0x80004000
    li      t1, 0x200000cf
    sd      t1, 0(t0)                  /* VA 0x80000000: 2 MiB RWX leaf */

    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x80006000
    srli    t1, t0, 2
    ori     t1, t1, 0x1ff
    csrw    pmpaddr0, t1
    li      t1, 0x2007ffff
    csrw    pmpaddr1, t1
    li      t1, 0x1f18
    csrw    pmpcfg0, t1
    csrr    t2, pmpaddr0
    li      t3, 0x200019ff
    bne     t2, t3, failed
    csrr    t2, pmpaddr1
    li      t3, 0x2007ffff
    bne     t2, t3, failed
    csrr    t2, pmpcfg0
    li      t3, 0x1f18
    bne     t2, t3, failed

    la      t0, supervisor_trap
    csrw    stvec, t0
    li      t0, 1 << 5
    csrw    medeleg, t0
    li      t0, 0x8000000000080003
    csrw    satp, t0
    sfence.vma
    la      t0, supervisor_start
    csrw    mepc, t0
    li      t0, 0x800
    csrw    mstatus, t0
    mret

supervisor_start:
.globl ld_data
.equ    ld_data, 0x40402000
    li      t0, 0x40402000
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    j       failed

supervisor_trap:
    csrr    t0, scause
    li      t1, 5
    bne     t0, t1, failed
    la      t1, ld_target
    csrr    t2, sepc
    bne     t1, t2, failed
    csrr    t2, stval
    li      t3, 0x40402000
    bne     t2, t3, failed
    la      t0, tohost
    li      t1, 1
    sw      t1, 0(t0)
.globl good_trap
good_trap:
    .word   0x0005006b

machine_trap:
failed:
    li      a0, 1
    .word   0x0005006b

    .section .tohost,"aw",@progbits
    .balign 8
    .globl tohost
tohost:
    .word   0
