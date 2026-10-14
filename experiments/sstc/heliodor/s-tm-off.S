/* Generated Heliodor Sstc fixture: s-tm-off; STCE=1, TM=0. */
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0,m_trap
    csrw mtvec,t0
    li t0,1
    slli t0,t0,63
    csrw 0x30a,t0
    li t0,0
    csrw 0x306,t0
    li t0,-1
    csrw 0x14d,t0
    li t0,32
    csrw 0x303,t0
    la t0,s_trap
    csrw stvec,t0
    li t0,32
    csrw sie,t0
    li t0,0x800
    csrs mstatus,t0
    la t0,s_entry
    csrw mepc,t0
    mret
s_entry:
target_access:
    csrw 0x14d,zero             /* no earlier time access */
    li t0,0x210                 /* expected trap did not occur */
    li t1,0x80001000
    sw t0,0(t1)
8:  j 8b

    .balign 4
s_trap:
    csrr t0,scause
    li t1,0x8000000000000005
    bne t0,t1,fail
    csrr t0,sip
    andi t0,t0,32
    beqz t0,fail
    li t0,-1
    csrw 0x14d,t0
4:  csrr t0,sip
    andi t0,t0,32
    bnez t0,4b
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
5:  j 5b
    .balign 4
m_trap:
    csrr t0,mcause
    li t1,2
    beq t0,t1,8f
    csrr t1,mepc
    la t2,target_access
    sub t1,t1,t2
    slli t0,t0,16
    or t0,t0,t1
    li t1,0x80001000
    sw t0,0(t1)
9:  j 9b
8:  la t1,target_access
    csrr t0,mepc
    bne t0,t1,fail
    li t0,1
    li t1,0x80001000
    sw t0,0(t1)
6:  j 6b
fail:
    li t0,3
    li t1,0x80001000
    sw t0,0(t1)
7:  j 7b
    .section .tohost,"aw",@progbits
    .align 6
    .globl tohost
tohost: .dword 0
