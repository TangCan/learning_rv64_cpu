CC      = riscv64-unknown-elf-gcc
OBJCOPY = riscv64-unknown-elf-objcopy
ELF2HEX = ../../sources/heliodor/test/c/bin2hex.py
CFLAGS  = -march=rv64imafdc_zicsr -mabi=lp64d -nostdlib -nostartfiles -ffreestanding

all: ssstateen_probe.hex ssstateen_probe_s.hex ssstateen_probe_s_gates.hex ssstateen_probe_s_gates_v2.hex ssstateen_probe_s_gates_v3.hex ssstateen_probe_vs.hex ssstateen_probe_vs_v2.hex ssstateen_probe_vu.hex ssstateen_probe_vu_fcsr.hex

ssstateen_probe.elf: ssstateen_probe.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe.hex: ssstateen_probe.elf
	$(OBJCOPY) -O binary $< ssstateen_probe.bin
	python3 $(ELF2HEX) ssstateen_probe.bin $@

ssstateen_probe_s.elf: ssstateen_probe_s.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_s.hex: ssstateen_probe_s.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_s.bin
	python3 $(ELF2HEX) ssstateen_probe_s.bin $@

ssstateen_probe_s_gates.elf: ssstateen_probe_s_gates.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_s_gates.hex: ssstateen_probe_s_gates.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_s_gates.bin
	python3 $(ELF2HEX) ssstateen_probe_s_gates.bin $@

ssstateen_probe_s_gates_v2.elf: ssstateen_probe_s_gates_v2.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_s_gates_v2.hex: ssstateen_probe_s_gates_v2.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_s_gates_v2.bin
	python3 $(ELF2HEX) ssstateen_probe_s_gates_v2.bin $@

ssstateen_probe_s_gates_v3.elf: ssstateen_probe_s_gates_v3.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_s_gates_v3.hex: ssstateen_probe_s_gates_v3.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_s_gates_v3.bin
	python3 $(ELF2HEX) ssstateen_probe_s_gates_v3.bin $@

ssstateen_probe_vs.elf: ssstateen_probe_vs.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_vs.hex: ssstateen_probe_vs.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_vs.bin
	python3 $(ELF2HEX) ssstateen_probe_vs.bin $@

ssstateen_probe_vu.elf: ssstateen_probe_vu.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_vu.hex: ssstateen_probe_vu.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_vu.bin
	python3 $(ELF2HEX) ssstateen_probe_vu.bin $@

ssstateen_probe_vu_fcsr.elf: ssstateen_probe_vu_fcsr.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_vu_fcsr.hex: ssstateen_probe_vu_fcsr.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_vu_fcsr.bin
	python3 $(ELF2HEX) ssstateen_probe_vu_fcsr.bin $@

ssstateen_probe_vs_v2.elf: ssstateen_probe_vs_v2.S ssstateen_probe.ld
	$(CC) $(CFLAGS) -T ssstateen_probe.ld -o $@ $<

ssstateen_probe_vs_v2.hex: ssstateen_probe_vs_v2.elf
	$(OBJCOPY) -O binary $< ssstateen_probe_vs_v2.bin
	python3 $(ELF2HEX) ssstateen_probe_vs_v2.bin $@

clean:
	rm -f ssstateen_probe.elf ssstateen_probe.bin ssstateen_probe.hex ssstateen_probe_s.elf ssstateen_probe_s.bin ssstateen_probe_s.hex ssstateen_probe_s_gates.elf ssstateen_probe_s_gates.bin ssstateen_probe_s_gates.hex ssstateen_probe_s_gates_v2.elf ssstateen_probe_s_gates_v2.bin ssstateen_probe_s_gates_v2.hex ssstateen_probe_s_gates_v3.elf ssstateen_probe_s_gates_v3.bin ssstateen_probe_s_gates_v3.hex ssstateen_probe_vs.elf ssstateen_probe_vs.bin ssstateen_probe_vs.hex ssstateen_probe_vs_v2.elf ssstateen_probe_vs_v2.bin ssstateen_probe_vs_v2.hex ssstateen_probe_vu.elf ssstateen_probe_vu.bin ssstateen_probe_vu.hex ssstateen_probe_vu_fcsr.elf ssstateen_probe_vu_fcsr.bin ssstateen_probe_vu_fcsr.hex

.PHONY: all clean
