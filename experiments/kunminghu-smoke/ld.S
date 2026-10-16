/* One aligned RV64I LD with an observable retirement result. */
    .section .text.init, "ax", @progbits
    .globl _start
    .type _start, @function
_start:
    la t0, ld_data
    .globl ld_target
ld_target:
    ld t1, 0(t0)
    li t2, 0x123456789abcdef0
    bne t1, t2, .Lbad
    addi a0, zero, 0
    .globl good_trap
good_trap:
    .word 0x0005006b
.Lbad:
    addi a0, zero, 1
    .word 0x0005006b
    .size _start, .-_start

    .section .rodata, "a", @progbits
    .balign 8
    .globl ld_data
ld_data:
    .dword 0x123456789abcdef0
