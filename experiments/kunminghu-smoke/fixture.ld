OUTPUT_ARCH(riscv)
ENTRY(_start)

SECTIONS
{
  . = 0x80000000;
  .text : ALIGN(4) {
    KEEP(*(.text.init))
    *(.text .text.*)
  }
  .rodata : ALIGN(16) { *(.rodata .rodata.*) }
  .data : ALIGN(16) { *(.data .data.*) }
  .bss : ALIGN(16) { *(.bss .bss.*) *(COMMON) }
  /DISCARD/ : { *(.comment) *(.eh_frame*) }
}
