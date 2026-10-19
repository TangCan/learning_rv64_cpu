/* M-mode code uses MPRV= S for LD; deny the root PTE page used by its Sv39 walk. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    li      t0, 0x80003000
    li      t1, 0x20001001
    sd      t1, 16(t0)                 /* root[2] -> level 1 table at 0x80004000 */
    li      t0, 0x80004000
    li      t1, 0x200000cf
    sd      t1, 0(t0)                  /* VA 0x80000000: 2 MiB RWX leaf */
    li      t1, 0x20001401
    sd      t1, 8(t0)                  /* VA 0x80200000 -> level 0 table */
    li      t0, 0x80005000
    li      t1, 0x200808cf
    sd      t1, 16(t0)                 /* VA 0x80202000: RWX leaf */

    la      t0, machine_trap
    csrw    mtvec, t0
    li      t0, 0x80003000
    srli    t1, t0, 2
    ori     t1, t1, 0x1ff
    csrw    pmpaddr0, t1
    li      t1, 0x2007ffff
    csrw    pmpaddr1, t1
    li      t1, 0x1f18
    csrw    pmpcfg0, t1
    csrr    t2, pmpaddr0
    li      t3, 0x20000dff
    bne     t2, t3, failed
    csrr    t2, pmpaddr1
    li      t3, 0x2007ffff
    bne     t2, t3, failed
    csrr    t2, pmpcfg0
    li      t3, 0x1f18
    bne     t2, t3, failed

    li      t0, 0x8000000000080003
    csrw    satp, t0
    sfence.vma
    li      t0, 0x20800                 /* MPRV=1, MPP=S: data LD uses Sv39 as S-mode */
    csrw    mstatus, t0
    li      t0, 0x80202000
.globl ld_target
ld_target:
    ld      t1, 0(t0)
    j       failed

machine_trap:
    csrr    t0, mcause
    li      t1, 5
    bne     t0, t1, failed
    la      t1, ld_target
    csrr    t2, mepc
    bne     t1, t2, failed
    csrr    t2, mtval
    li      t3, 0x80202000
    bne     t2, t3, failed
    la      t0, tohost
    li      t1, 1
    sw      t1, 0(t0)
.globl good_trap
good_trap:
    .word   0x0005006b

failed:
    li      a0, 1
    .word   0x0005006b

    .section .tohost,"aw",@progbits
    .balign 8
    .globl tohost
tohost:
    .word   0
