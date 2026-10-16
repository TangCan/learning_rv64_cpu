# Kunminghu ChiselDB probe (LD2-E23)

The settled Kunminghu fixture completed and the emulator printed `saving memdb`, but the archived SQLite database contains no tables. This was not caused by disabled Constantin gates: `constantin.cst` enables `isWriteLoadMissTable0`, `isFirstHitWrite0`, and `isWriteLoadAccessTable0`. The source declares both DCache tables with ChiselDB's default `basicDB=false`; that elaboration emits empty `LoadMissDB0_write`, `LoadAccessDB0_write`, and `init_db_*` stubs. Runtime flags cannot turn those generated no-ops into logging. The database therefore cannot establish whether the target LD at PC `0x80000030` hit or missed.

The source does expose the needed cycle-local signals: `DCacheLoadIO.s2_pc`, `s2_first_hit`, the miss request address, and `debug_robIdx`. A bounded follow-up would need an isolated elaboration with ChiselDB enabled, the DCache table marked `basicDB=true`, and PC added to the record; this changes only the temporary probe build, not the locked checkout. The normal emulator was built without trace support (`VM_TRACE=0`). An isolated `EMU_TRACE=1` Verilator build was attempted but stopped during long RTL parsing before artifacts were generated. The temporary build tree was removed.

Command (run from the repository root):

```sh
sources/xiangshan/build/verilator-compile/emu \
  -i notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T105705Z-3e81181d1d02/fixture.bin \
  --diff sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace \
  --cst-file=notes/units/evidence/smoke/kunminghu-chisel-db-probe-20261016/constantin.cst \
  --dump-select-db='LoadMissDB0 LoadAccessDB0' \
  --db-path=notes/units/evidence/smoke/kunminghu-chisel-db-probe-20261016/chisel-db.sqlite
```

The database has no tables; the emulator run itself reached GOODTRAP. `stdout.log` and `stderr.log` preserve the run output. This is a negative tool-capability probe, not a cache result.
