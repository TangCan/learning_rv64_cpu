/* An A=0 L0 leaf is readable but not writable under PMP; Svadu must fault the load. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    li      t0, 0x80003000
    li      t1, 0x20001001
    sd      t1, 16(t0)                 /* root[2] -> L1 */
    li      t0, 0x80004000
    li      t1, 0x200000cf
    sd      t1, 0(t0)                  /* VA 0x80000000: 2 MiB RWX leaf */
    li      t1, 0x20001401
    sd      t1, 8(t0)                  /* VA 0x80200000 -> L0 */
    li      t0, 0x80005000
    li      t1, 0x2008080f
    sd      t1, 16(t0)                 /* VA 0x80202000: RWX leaf, A=0 */

    la      t0, machine_trap
    csrw    mtvec, t0
    li      t1, 0x20001406             /* Read-only TOR through the whole L0 PTE */
    csrw    pmpaddr0, t1
    li      t1, 0x20100000
    csrw    pmpaddr1, t1
    li      t1, 0x000f0909             /* TOR: R / TOR: RWX */
    csrw    pmpcfg0, t1

    li      t0, 0x2000000000000000     /* menvcfg.ADUE=1 */
    csrw    menvcfg, t0
    li      t0, 0x8000000000080003
    csrw    satp, t0
    sfence.vma
    li      t0, 0x20800                 /* MPRV=1, MPP=S */
    csrw    mstatus, t0
    li      t0, 0x80202000
.globl ld_data
.equ    ld_data, 0x80202000
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
