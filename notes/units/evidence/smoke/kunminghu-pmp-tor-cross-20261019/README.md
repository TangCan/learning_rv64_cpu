# Kunminghu PMP TOR cross-boundary LD attempt (blocked)

This attempt reused `experiments/rv64-ld-probe/ld-heliodor-pmp-cross-boundary.S` on the locked Kunminghu V2 snapshot (`c098f996bf4d301b88693b20315486d31e93bc9d`) to check whether the Heliodor TOR-span failure could be compared on Kunminghu.

The fixture requests a 4-byte TOR boundary at `0x80002004`. The DUT reads `pmpaddr0` back as `0x20000800` after writing `0x20000801`, then branches to BAD TRAP at PC `0x80000108`. The target LD at `ld_target` is never reached. This is a blocked setup, not evidence of correct or incorrect cross-boundary enforcement.

The locked source sets `PlatformGrain` to `log2Ceil(4*1024)` (4 KiB) in `sources/xiangshan/src/main/scala/xiangshan/PMParameters.scala`; the PMP CSR readback also demonstrates that the requested 4-byte TOR boundary is not representable in this configuration. An aligned 8-byte LD cannot straddle a 4 KiB-aligned boundary, so this exact naturally aligned LD case is not available on this snapshot without changing the granularity or using an out-of-scope unaligned access.

## Reproduction

```sh
riscv64-unknown-elf-gcc -march=rv64imac_zicsr -mabi=lp64 -nostdlib -nostartfiles -ffreestanding \
  -Wl,--build-id=none -Wl,-T,experiments/rv64-ld-probe/fixture.ld \
  -Wl,-Map,fixture.map -o fixture.elf \
  experiments/rv64-ld-probe/ld-heliodor-pmp-cross-boundary.S
riscv64-unknown-elf-objcopy -O binary fixture.elf fixture.bin
sources/xiangshan/build/verilator-compile/emu -i fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace
```

The captured stdout is `run.stdout`; it shows the CSR write/readback sequence and BAD TRAP. No target retirement or PMP access-fault result was observed. Simulator stderr contained only performance counters and was omitted.
