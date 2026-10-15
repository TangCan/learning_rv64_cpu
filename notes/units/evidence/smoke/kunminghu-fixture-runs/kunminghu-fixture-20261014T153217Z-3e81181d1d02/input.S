/* VU user-custom CSR probes distinguish H.C, S.C, and an unimplemented CSR. */
    .option norvc
    .section .text.init
    .globl _start
_start:
    li      t0, -1
    csrw    pmpaddr0, t0
    li      t0, 0x1f
    csrw    pmpcfg0, t0
    la      sp, stack_top
    li      t0, -1
    li      t6, 5101
    csrw    0x30c, t0              /* M.SE0 and M.C */
    li      t6, 5102
    csrw    0x10c, t0              /* S.C */
    li      t6, 5103
    csrw    0x60c, t0              /* H.SE0 and H.C */
    li      t0, (1 << 2) | (1 << 8)
    csrw    medeleg, t0            /* delegate illegal instruction and U ecall to HS */
    la      t0, m_trap
    csrw    mtvec, t0
    la      t0, hs_stage
    csrw    mepc, t0
    li      t0, 0x800
    csrw    mstatus, t0
    mret

hs_stage:
    li      s1, 0                  /* expected virtual-instruction traps */
    li      s2, 0                  /* expected unimplemented-CSR trap */
    li      t4, 1
    slli    t4, t4, 63             /* H.SE0 open, H.C clear */
    li      t6, 5104
    csrw    0x60c, t4
    li      t6, 5105
    csrr    t2, 0x10c              /* S.C remains set */
    la      t0, hs_trap
    csrw    stvec, t0
    csrw    hedeleg, zero
    csrw    sstatus, zero          /* SPP=0 selects VU on sret */
    li      t0, 0x80               /* SPV=1, SPVP=0: sret to VU */
    csrw    hstatus, t0
    la      t0, vu_stage
    csrw    sepc, t0
    sret

vu_stage:
    li      t6, 5001
    csrr    t2, 0x800              /* H.C clear: expected virtual-instruction */
    li      t6, 5002
    csrr    t2, 0x800              /* S.C clear: expected virtual-instruction */
    li      t6, 5003
    csrr    t2, 0x800              /* gates open; CSR itself is unimplemented */
    li      t6, 5004
    ecall

m_trap:
    j       bad_trap

hs_trap:
    csrr    t0, scause
    li      t1, 22
    beq     t0, t1, handle_virtual
    li      t1, 2
    beq     t0, t1, handle_illegal
    li      t1, 8
    bne     t0, t1, bad_trap
    li      t1, 5004
    bne     t6, t1, bad_trap
    li      t1, 2
    bne     s1, t1, bad_trap
    li      t1, 1
    bne     s2, t1, bad_trap
    li      a0, 0
    .globl good_trap
good_trap:
    .word   0x0005006b

handle_virtual:
    addi    s1, s1, 1
    li      t1, 5001
    beq     t6, t1, open_hcustom
    li      t1, 5002
    beq     t6, t1, open_scustom
    j       bad_trap

handle_illegal:
    li      t1, 5003
    bne     t6, t1, bad_trap
    addi    s2, s2, 1
    j       resume_guest

open_hcustom:
    li      t4, 1
    slli    t4, t4, 63
    ori     t4, t4, 1
    li      t6, 5201
    csrw    0x60c, t4              /* open H.C, retain H.SE0 */
    li      t6, 5202
    csrw    0x10c, zero            /* clear S.C */
    j       resume_guest

open_scustom:
    li      t6, 5203
    csrw    0x10c, 1               /* open S.C */
resume_guest:
    csrr    t0, sepc
    addi    t0, t0, 4
    csrw    sepc, t0
    sret

bad_trap:
    li      a0, 1
    .word   0x0005006b

    .section .bss
    .align  4
stack:
    .space  256
stack_top:
