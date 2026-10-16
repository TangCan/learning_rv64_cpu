# Kunminghu ChiselDB probe (LD2-E23)

The settled Kunminghu fixture completed and the emulator printed `saving memdb`, but the archived SQLite database contains no tables. This was not caused by disabled Constantin gates: `constantin.cst` enables `isWriteLoadMissTable0`, `isFirstHitWrite0`, and `isWriteLoadAccessTable0`. Inspection of the locked generated C++ build shows `LoadMissDB0_write`, `LoadAccessDB0_write`, and the corresponding `init_db_*` functions are empty stubs. The database therefore cannot establish whether the target LD at PC `0x80000030` hit or missed.

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
