.option norvc
.section .text.init,"ax",@progbits
.globl _start
_start:
    la t0, ld_data
.globl ld_target
ld_target:
    ld t1, 0(t0)
    li t2, 0x123456789abcdef0
    bne t1, t2, fail
    la t3, tohost
    li t4, 1
    sw t4, 0(t3)
1:  j 1b
fail:
    la t3, tohost
    li t4, 2
    sw t4, 0(t3)
2:  j 2b
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
