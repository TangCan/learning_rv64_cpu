# Kunminghu Sv39 L0 PTE PMP denial for LD (LD2-E43)

This run reused the Heliodor Sv39 probe on locked Kunminghu V2 revision `c098f996bf4d301b88693b20315486d31e93bc9d`. M-mode builds a Sv39 mapping for code through an allowed 2 MiB leaf, then maps target VA `0x80202000` through an L0 PTE at physical address `0x80005010`. PMP entry 0 denies the 4 KiB L0 table page `0x80005000..0x80005fff`; entry 1 allows the broader DRAM range. PMP CSR readbacks match the fixture before SATP is enabled and execution enters S-mode.

The target instruction at PC `0x80000118` raises load access fault cause 5. The emulator/NEMU output reports target VA `0x80202000`, PTE physical address `0x80005010`, access length 8, and S-mode. The delegated S-mode handler checks `scause=5`, `sepc=ld_target`, and `stval=0x80202000`, then reaches GOOD TRAP at `0x80000160`; simulator exit code is 0. This confirms this single Sv39 L0 PTE-read denial path on the locked Kunminghu build. It does not capture an internal hardware page-walk address independently of the differential model, or cover other walk levels.

## Reproduce

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles -ffreestanding \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf \
  experiments/rv64-ld-probe/ld-heliodor-pmp-ptw-fault.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

`run.stdout` contains the commit trace, exception, NEMU PMP diagnostic, handler checks, and terminal marker. Simulator stderr contained only performance counters and was omitted.
