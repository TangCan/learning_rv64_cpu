# Kunminghu Sv39 L1 PTE PMP denial for LD (LD2-E44)

This fixture runs on locked Kunminghu V2 revision `c098f996bf4d301b88693b20315486d31e93bc9d`. M-mode maps its S-mode code through an allowed root[2] / L1 leaf. The target VA `0x40402000` uses root[1], which points to L1 table page `0x80006000`; PMP entry 0 denies that 4 KiB page, while entry 1 allows the rest of DRAM. PMP CSR readbacks are checked before SATP is enabled.

The target LD at PC `0x800000f8` raises cause 5. The emulator/NEMU diagnostic reports VA `0x40402000`, denied L1 PTE PA `0x80006010`, length 8, and S-mode. The delegated S-mode handler checks `scause=5`, `sepc=ld_target`, and `stval=0x40402000`, then reaches GOOD TRAP at `0x80000138`; exit code is 0. This confirms one Sv39 L1 PTE-read PMP denial path on this snapshot. The denied PTE address is reported by the differential model, not captured independently from the DUT walker; other walk levels remain untested.

## Reproduce

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles -ffreestanding \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf \
  experiments/rv64-ld-probe/ld-kunminghu-pmp-l1-ptw-fault.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

`run.stdout` preserves the commit trace, PMP diagnostic, handler checks, and terminal marker. Simulator stderr contained performance counters and was omitted.
