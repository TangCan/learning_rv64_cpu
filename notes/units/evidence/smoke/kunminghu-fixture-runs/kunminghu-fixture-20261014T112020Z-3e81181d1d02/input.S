/* U-mode load/store/LR-SC/AMO probe across canonical and tagged pointers. */
    .option norvc
    .section .text.init, "ax", @progbits
    .globl _start
_start:
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f
    csrw    pmpcfg0, t0
    la      t0, machine_trap
    csrw    mtvec, t0
#ifdef SSNPM_PMLEN7
    li      t0, 2
    slli    t0, t0, 32
    csrw    senvcfg, t0                 /* U-mode PMLEN=7 */
#else
    csrw    senvcfg, zero                /* U-mode PMLEN=0 */
#endif
    csrr    t1, senvcfg
    srli    t1, t1, 32
    andi    t1, t1, 3
#ifdef SSNPM_PMLEN7
    li      t2, 2
#else
    li      t2, 0
#endif
    bne     t1, t2, failed               /* record WARL readback before U-mode access */
    la      t0, u_mode
    csrw    mepc, t0
    csrw    mstatus, zero               /* MPP=U */
    mret
u_mode:
    la      t0, probe_data
#ifdef SSNPM_TAGGED
#ifdef SSNPM_PMLEN7
    li      t1, 0xfe00000000000000       /* ignored bits 63:57, VA bit 56 remains zero */
#else
    li      t1, 0xfe00000000000000       /* unmasked control must fault on this tagged VA */
#endif
    or      t0, t0, t1
#endif
#ifdef SSNPM_EXPECT_TRAP
    ld      t2, 0(t0)
    j       failed                       /* unmasked tagged access must not reach data */
#else
    ld      t2, 0(t0)
    li      t3, 0x1234
    bne     t2, t3, failed
    li      t3, 0x5678
    sd      t3, 0(t0)
    ld      t2, 0(t0)
    bne     t2, t3, failed
    lr.d    t2, (t0)
    bne     t2, t3, failed
    li      t3, 0x9abc
    sc.d    t4, t3, (t0)
    bnez    t4, failed
    ld      t2, 0(t0)
    bne     t2, t3, failed
    li      t3, 1
    amoadd.d t2, t3, (t0)
    li      t4, 0x9abc
    bne     t2, t4, failed
    ld      t2, 0(t0)
    li      t4, 0x9abd
    bne     t2, t4, failed
#endif
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b
machine_trap:
#ifdef SSNPM_EXPECT_TRAP
    csrr    t0, mcause
    li      t1, 5                         /* load access fault from unmasked tagged VA */
    bne     t0, t1, failed
    li      a0, 0
    j       good_trap
#else
    j       failed
#endif
failed:
    li      a0, 1
    .word   0x0005006b
    .section .data, "aw", @progbits
    .align  3
probe_data:
    .dword  0x1234
