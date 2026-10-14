/* Generated Heliodor Sstc fixture: s-lt; STCE=1, TM=2. */
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0,m_trap
    csrw mtvec,t0
    li t0,1
    slli t0,t0,63
    csrw 0x30a,t0
    li t0,2
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
    csrr t0,sip
    andi t0,t0,32
    bnez t0,fail
.Lsample_time:
    csrr t0,time
    .rept 256
    nop
    .endr
    csrr t1,time
    beq t0,t1,.Lsample_time
    mv t0,t1
    li t1,8
    add t1,t0,t1
    csrw 0x14d,t1
    csrr t3,time
    li t4,0x80001004
    sw t0,0(t4)                 /* sampled time */
    sw t1,4(t4)                 /* programmed comparator */
    sw t3,8(t4)                 /* time immediately after comparator write */
#if defined(CASE_S_LT)
    bgeu t3,t1,fail
#elif defined(CASE_S_GT)
    bltu t3,t1,fail
#endif
    li t2,10000
1:  csrr t3,sip
    andi t3,t3,32
    bnez t3,2f
    addi t2,t2,-1
    bnez t2,1b
    j fail
2:  li t0,32
    csrs sie,t0
    li t0,2
    csrs sstatus,t0
3:  j 3b

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
