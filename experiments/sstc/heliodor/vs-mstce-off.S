/* vs-mstce-off; htimedelta=0x10000; M/H STCE=0/1, TM=2/2. */
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0,m_trap
    csrw mtvec,t0
    li t0,0x400004
    csrw medeleg,t0
    csrw 0x602,zero
    li t0,0
    slli t0,t0,63
    csrw 0x30a,t0
    li t0,1
    slli t0,t0,63
    csrw 0x60a,t0
    li t0,2
    csrw 0x306,t0
    li t0,2
    csrw 0x606,t0
    li t0,64
    csrw 0x603,t0
    li t0,0
    csrw 0x604,t0
    li t0,0x10000
    csrw 0x605,t0
    csrw 0x280,zero
    li t0,-1
    csrw 0x24d,t0               /* keep VSTIP clear before entering VS */
    csrw 0x680,zero             /* hgatp bare */
    la t0,hs_trap
    csrw stvec,t0
    la t0,vs_trap
    csrw 0x205,t0
    li t0,0x8000000802
    csrs mstatus,t0
    la t0,vs_entry
    csrw mepc,t0
    mret
vs_entry:
target_access:
    csrw 0x14d,zero          /* first VS CSR access */
    li t0,0x210                /* expected trap did not occur */
    j report_trap
    .balign 4
vs_trap:
    csrr t0,scause
    li t1,0x8000000000000005
    bne t0,t1,vs_bad_cause
    csrr t0,sip
    andi t0,t0,32
    beqz t0,vs_no_pending
    li t0,-1
    csrw 0x14d,t0
    li t2,100000
vs_pending_poll:
    csrr t0,sip
    andi t0,t0,32
    beqz t0,vs_pending_cleared
    addi t2,t2,-1
    bnez t2,vs_pending_poll
    j vs_pending_not_cleared
vs_pending_cleared:
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
4:  j 4b
    .balign 4
vs_bad_cause:
    csrr t1,sepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
vs_no_pending:
    li t0,0x302
    j report_trap
vs_pending_not_cleared:
    li t0,0x212
    j report_trap
    .balign 4
hs_trap:
    csrr t0,scause
    li t1,2
    bnez t1,hs_gate_check
    li t1,0x8000000000000006
    bne t0,t1,hs_bad_cause
    csrr t0,0x644
    andi t0,t0,64
    beqz t0,hs_no_pending
    li t0,-1
    csrw 0x24d,t0
    li t2,100000
hs_pending_poll:
    csrr t0,0x644
    andi t0,t0,64
    beqz t0,hs_pending_cleared
    addi t2,t2,-1
    bnez t2,hs_pending_poll
    j hs_pending_not_cleared
hs_pending_cleared:
    j hs_pass
hs_gate_check:
    bne t0,t1,hs_bad_cause
    csrr t0,sepc
    la t1,target_access
    bne t0,t1,hs_bad_pc
    j hs_pass
hs_bad_cause:
    csrr t1,sepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
hs_no_pending:
    li t0,0x402
    j report_trap
hs_bad_pc:
    li t0,0x403
    j report_trap
hs_pending_not_cleared:
    li t0,0x412
    j report_trap
hs_pass:
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
5:  j 5b
    .balign 4
m_trap:
    csrr t0,mcause
    li t1,2
    beqz t1,m_bad_cause
    bne t0,t1,m_bad_cause
    csrr t0,mepc
    la t1,target_access
    bne t0,t1,m_bad_pc
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
6:  j 6b
m_bad_cause:
    csrr t1,mepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    j report_trap
m_bad_pc:
    li t0,0x403
    j report_trap
report_trap:
    li t1,0x80001000
    sw t0,0(t1)
    j 7f
fail:
    li t0,3
    li t1,0x80001000
    sw t0,0(t1)
7:  j 7b
    .section .tohost,"aw",@progbits
    .align 6
    .globl tohost
tohost: .dword 0
