# Run the implemented Heliodor SINH/UINH filters in S and U mode.
#define MSTATUS      0x300
#define MTVEC        0x305
#define MCOUNTEREN   0x306
#define MCAUSE       0x342
#define MHPMEVENT3   0x323
#define MHPMCOUNTER3 0xb03
#define HPMCOUNTER3  0xc03

    .section .text.init
    .globl _start
_start:
    li      t0, 0x80001000
    li      t1, 10
    sw      t1, 0(t0)

    la      t0, mtrap
    csrw    MTVEC, t0
    li      s5, 0x80002000
    li      t0, 8
    csrw    MCOUNTEREN, t0          # expose counter3 to S and U
    li      t0, 5
    li      t1, 1
    slli    t1, t1, 61              # SINH
    or      t0, t0, t1
    csrw    MHPMEVENT3, t0
    csrw    MHPMCOUNTER3, zero
    li      t0, 0x800               # MPP=S
    csrw    MSTATUS, t0
    la      t0, s_entry
    csrw    0x341, t0
    mret

s_entry:
    li      t0, 0x80001000
    li      t1, 20
    sw      t1, 0(t0)

    li      t1, 4096
s_inhibited:
    ld      t3, 0(s5)
    addi    t1, t1, -1
    bnez    t1, s_inhibited
    csrr    t0, HPMCOUNTER3
    bnez    t0, fail_s_inhibit

    li      t0, 0x80001000
    li      t1, 21
    sw      t1, 0(t0)
    li      a4, 1
    ecall                           # M clears SINH, then returns to S
    csrr    t0, HPMCOUNTER3
    beqz    t0, fail_s_enabled

    li      t0, 0x80001000
    li      t1, 22
    sw      t1, 0(t0)
    li      a4, 2
    ecall                           # M configures UINH and enters U

u_entry:
    li      t0, 0x80001000
    li      t1, 30
    sw      t1, 0(t0)

    li      t1, 4096
u_inhibited:
    ld      t3, 0(s5)
    addi    t1, t1, -1
    bnez    t1, u_inhibited
    csrr    t0, HPMCOUNTER3
    bnez    t0, fail_u_inhibit

    li      t0, 0x80001000
    li      t1, 31
    sw      t1, 0(t0)
    li      a4, 3
    ecall                           # M clears UINH, then returns to U
    csrr    t0, HPMCOUNTER3
    beqz    t0, fail_u_enabled

    li      t0, 0x80001000
    li      t1, 32
    sw      t1, 0(t0)
    li      a4, 4
    ecall                           # M reports pass

mtrap:
    li      t0, 0x80001000
    li      t1, 25
    sw      t1, 0(t0)
    csrr    t0, MCAUSE
    li      t1, 9
    li      t2, 3
    bltu    a4, t2, check_cause     # phases 1-2 are S ecall; 3-4 are U ecall
    li      t1, 8
check_cause:
    bne     t0, t1, fail_bad_trap
    li      t0, 1
    beq     a4, t0, clear_sinh
    li      t0, 2
    beq     a4, t0, enter_u
    li      t0, 3
    beq     a4, t0, clear_uinh
    li      t0, 4
    beq     a4, t0, pass
    j       fail_bad_trap

clear_sinh:
    li      t0, 5
    csrw    MHPMEVENT3, t0
    csrw    MHPMCOUNTER3, zero
    csrr    t0, 0x341
    addi    t0, t0, 4               # skip the handled S-mode ecall
    csrw    0x341, t0
    li      t0, 0x80001000
    li      t1, 23
    sw      t1, 0(t0)
    mret

enter_u:
    li      t0, 5
    li      t1, 1
    slli    t1, t1, 60              # UINH
    or      t0, t0, t1
    csrw    MHPMEVENT3, t0
    csrw    MHPMCOUNTER3, zero
    li      t1, 0x1800              # clear MPP[12:11] to select U
    csrc    MSTATUS, t1
    la      t0, u_entry
    csrw    0x341, t0
    mret

clear_uinh:
    li      t0, 5
    csrw    MHPMEVENT3, t0
    csrw    MHPMCOUNTER3, zero
    csrr    t0, 0x341
    addi    t0, t0, 4               # skip the handled U-mode ecall
    csrw    0x341, t0
    mret

pass:
    li      t0, 1
    li      t1, 0x80001000
    sw      t0, 0(t1)
1:  j       1b

fail_s_inhibit:
    li      t6, 51
    j       fail
fail_s_enabled:
    li      t6, 52
    j       fail
fail_u_inhibit:
    li      t6, 53
    j       fail
fail_u_enabled:
    li      t6, 54
    j       fail
fail_bad_trap:
    csrr    t6, MCAUSE           # preserve the unexpected trap cause for the run record
fail:
    li      t1, 0x80001000
    sw      t6, 0(t1)
2:  j       2b

    .section .tohost, "aw", @progbits
    .align 6
    .globl tohost
tohost:
    .dword 0
