# Kunminghu Sv39 L2 root-PTE PMP denial for LD (LD2-E45)

This fixture runs on locked Kunminghu V2 revision `c098f996bf4d301b88693b20315486d31e93bc9d`. It prepares Sv39 mappings and configures PMP to deny the 4 KiB root page at physical address `0x80003000`, while leaving the remaining DRAM allowed. M-mode code sets SATP and executes the target LD with `MPRV=1, MPP=S`; instruction fetch remains M-mode, while the data access and its page-table walk use S-mode translation and PMP permissions.

The target LD at PC `0x800000f4` raises machine load access fault cause 5. The emulator/NEMU diagnostic reports VA `0x80202000`, denied root PTE PA `0x80003010`, length 8, and effective S-mode. The M-mode handler checks `mcause=5`, `mepc=ld_target`, and `mtval=0x80202000`, then reaches GOOD TRAP at `0x8000013c`; simulator exit code is 0. This confirms one Sv39 L2 root-PTE read denial case using MPRV. The denied PTE PA comes from the differential model rather than an independent DUT walker capture.

## Reproduce

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles -ffreestanding \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf \
  experiments/rv64-ld-probe/ld-kunminghu-pmp-l2-ptw-fault.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

`run.stdout` preserves the commit trace, PMP diagnostic, handler checks, and terminal marker. Simulator stderr contained performance counters and was omitted.
