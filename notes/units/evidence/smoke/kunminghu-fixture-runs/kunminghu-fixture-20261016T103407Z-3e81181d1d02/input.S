.option norvc
.section .text.init,"ax",@progbits
.globl _start
_start:
    la t0, ld_data
    ld t6, 0(t0)          # Populate DCache before the measured load.
    li t5, 0x123456789abcdef0
    bne t6, t5, fail      # Wait for the refill before issuing ld_target.
.globl ld_target
ld_target:
    ld t1, 0(t0)
    li t2, 0x123456789abcdef0
    bne t1, t2, fail
    la t3, tohost
    li t4, 1
    sw t4, 0(t3)
.globl good_trap
good_trap:
    .word 0x0005006b
fail:
    li a0, 1
    .word 0x0005006b
.section .rodata,"a",@progbits
.balign 8
.globl ld_data
ld_data:
    .dword 0x123456789abcdef0
.section .tohost,"aw",@progbits
.balign 8
.globl tohost
tohost:
    .word 0
