CC      = riscv64-unknown-elf-gcc
OBJCOPY = riscv64-unknown-elf-objcopy
ELF2HEX = ../../sources/heliodor/test/c/bin2hex.py
CFLAGS  = -march=rv64imafdc_zicsr -mabi=lp64d -nostdlib -nostartfiles -ffreestanding

all: ssstateen_probe.hex

ssstateen_probe.elf: ssstateen_probe.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe.hex: ssstateen_probe.elf
	$(OBJCOPY) -O binary $< ssstateen_probe.bin
	python3 $(ELF2HEX) ssstateen_probe.bin $@

clean:
	rm -f ssstateen_probe.elf ssstateen_probe.bin ssstateen_probe.hex

.PHONY: all clean
