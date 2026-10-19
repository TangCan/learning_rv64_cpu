# Kunminghu locked PMP denied-load probe (LD2-E34)

This M-mode fixture programs `pmpaddr0` for the 4 KiB NAPOT page `0x80002000..0x80003000`, then locks entry 0 with `pmpcfg0=0x98` (NAPOT, no read/write/execute permissions). It loads from `0x80002000`. The trap handler checks `mcause=5`, `mepc=ld_target`, and `mtval=0x80002000`, then signals the good-trap marker. The linker keeps code and `tohost` outside the denied page.

## Result

- DUT commit trace: exception at PC `0x80000038`, instruction `0x0002b303`, cause `5`.
- NEMU reports `isa pmp check failed`, VA=PA=`0x80002000`, length 8, access type 1, M-mode.
- The handler's cause, PC, and `mtval` checks pass; simulation ends at `HIT GOOD TRAP`.

This confirms the locked PMP read-denial path for this Kunminghu fixture. It does not expose the hardware's raw matched PMP entry or cover Heliodor denial.

## Reproduce

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf experiments/rv64-ld-probe/ld-pmp-fault.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

The binary, ELF, map, source copy, logs, and SHA-256 hashes are archived here. The locked Kunminghu and NEMU revisions are recorded in `sources.lock`.
