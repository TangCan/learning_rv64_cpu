# Story 1.3 architectural input; byte-addressed, 64-bit naturally aligned memory.
# Initial memory: [0] = 0x1122334455667788, [1] = 0x8877665544332211.
# The program loads word 0, stores it to word 1, and loads word 1 back.
_start:
    addi x1, x0, 0
    ld   x2, 0(x1)
    nop
    nop
    nop
    nop
    sd   x2, 8(x1)
    nop
    nop
    nop
    ld   x3, 8(x1)
    nop
    nop
