# Kunminghu default PMA denied-load probe (LD2-E33)

This fixture executes `ld t1, 0(t0)` in M-mode with `t0=0x39002000`. It installs a machine trap handler that checks `mcause=5` (load access fault), `mepc=ld_target`, and `mtval=0x39002000`, then signals the good-trap marker. It does not program PMP CSRs. In the locked default PMA map, the address is in the denied TOR window `0x39002000..0x3a000000`.

## Result

- DUT commit trace: exception at PC `0x80000010`, instruction `0x0002b303`, cause `5`.
- NEMU reports `pma check failed`, VA=PA=`0x39002000`, length 8, access type 1, M-mode.
- The handler's cause, PC, and `mtval` checks pass; simulation ends at `HIT GOOD TRAP`.

This demonstrates the default Kunminghu M-mode load PMA-denial path for this address. It does not test a PMP denial, expose the hardware's raw matched PMA CSR entry, or cover Heliodor.

## Reproduce

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf experiments/rv64-ld-probe/ld-pma-fault.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

`fixture.bin`, `fixture.elf`, `fixture.map`, stdout, stderr, and their SHA-256 hashes are archived here. The locked Kunminghu and NEMU revisions are recorded in `sources.lock`.
