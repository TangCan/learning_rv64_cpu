/* Heliodor U-mode Ssnpm case pmlen0-tagged. */
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
    li t0, 0
    slli t0, t0, 32
    csrw senvcfg, t0
    csrr t1, senvcfg
    srli t1, t1, 32
    andi t1, t1, 3
    li t2, 0
    bne t1, t2, readback_mismatch
    la t0, u_entry
    csrw mepc, t0
    csrw mstatus, zero
    mret
u_entry:
    la t0, probe_data
    li t1, 0xfe00000000000000
    or t0, t0, t1
tagged_load:
    ld t2, 0(t0)
    li t5, 0x12
    j report_fail
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
    csrr t0, mcause
    li t1, 5
    bne t0, t1, trap_failure
    la t2, tagged_load
    csrr t3, mepc
    bne t2, t3, trap_failure
    la t2, probe_data
    li t3, 0xfe00000000000000
    or t2, t2, t3
    csrr t3, mtval
    bne t2, t3, trap_failure
    li t1, 1
    sd t1, 0(t4)
    j trap_halt
trap_failure:
    addi t5, t0, 0x30
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
