.option norvc
.option arch,+zicsr
.section .text.init,"ax",@progbits
.globl _start
_start:
    la t0, machine_trap
    csrw mtvec, t0
    li t0, 0x20000800              /* TOR top: 0x80002000 */
    csrw pmpaddr0, t0
    li t0, 0x20001000              /* TOR top: 0x80004000 */
    csrw pmpaddr1, t0
    li t0, 0x00000f0f              /* entry 0 and 1: TOR RWX */
    csrw pmpcfg0, t0
    csrr t1, pmpaddr0
    li t2, 0x20000800
    bne t1, t2, fail
    csrr t1, pmpaddr1
    li t2, 0x20001000
    bne t1, t2, fail
    csrr t1, pmpcfg0
    li t2, 0x00000f0f
    bne t1, t2, fail
    la t0, supervisor_start
    csrw mepc, t0
    li t0, 0x800
    csrw mstatus, t0
    mret

supervisor_start:
    la t0, ld_data
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

machine_trap:
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
