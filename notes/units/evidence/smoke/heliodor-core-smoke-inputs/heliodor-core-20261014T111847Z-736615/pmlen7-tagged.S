/* Heliodor U-mode Ssnpm case pmlen7-tagged. */
    .option norvc
    .section .text.init,"ax",@progbits
    .globl _start
_start:
    la t0, machine_trap
    csrw mtvec, t0
    /* 8 KiB NAPOT grants linked image/tohost while denying tagged high addresses. */
    li t0, 0x200003ff
    csrw pmpaddr0, t0
    li t0, 0x1f
    csrw pmpcfg0, t0
    li t0, 2
    slli t0, t0, 32
    csrw senvcfg, t0
    csrr t1, senvcfg
    srli t1, t1, 32
    andi t1, t1, 3
    li t2, 2
    bne t1, t2, readback_mismatch
    la t0, u_entry
    csrw mepc, t0
    csrw mstatus, zero
    mret
u_entry:
    la t0, probe_data
    li t1, 0xfe00000000000000
    or t0, t0, t1
    li t3, 0x5678
    sd t3, 0(t0)
    ld t2, 0(t0)
    bne t2, t3, load_mismatch
    li a0, 0
    j good_trap
good_trap:
    la t4, tohost
    li t5, 1
    sd t5, 0(t4)
    j trap_halt
machine_trap:
    la t4, tohost
    ld t5, 0(t4)
    li t1, 1
    beq t5, t1, trap_halt
    li t5, 3
    sd t5, 0(t4)
    j trap_halt
trap_halt:
    j trap_halt
readback_mismatch:
    li t5, 0x11
    j report_fail
load_mismatch:
    li t5, 0x12
    j report_fail
unexpected_trap:
    csrr t0, mcause
    addi t5, t0, 0x20
report_fail:
    la t4, tohost
    sd t5, 0(t4)
    j trap_halt
    .section .data,"aw",@progbits
    .align 3
probe_data:
    .dword 0x1234
    .section .tohost,"aw",@progbits
    .align 6
    .globl tohost
tohost:
    .dword 0
