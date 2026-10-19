# Kunminghu C++ cache probe (LD2-E24)

This is exploratory evidence for the settled fixture's target load at PC `0x80000030`, physical address `0x80000080`. A temporary observer was added only in `/tmp/xiangshan-difftest-cpp` and sampled generated DCache stage-2 `valid`, `paddr`, `_s2_hit_T_2`, `s2_req_isFirstIssue`, alongside the matching LoadUnit stage-2 PC. Source defines `s2_hit` at `LoadPipe.scala:415` as tag match, permission, coherence-state match, and no WPU prediction failure; the generated `_s2_hit_T_2` is the hit condition used in the built model.

Observed lines:

- cycle 4178, lane 2: PC `0x80000030`, PADDR `0x80000080`, `first=1`, `hit=0`.
- cycle 4188, lane 1: PC `0x80000030`, PADDR `0x80000080`, `first=0`, `hit=0`.

The simulator printed NEMU `HIT GOOD TRAP` at PC `0x80000068` and saved its database, but exited with SIGSEGV (139) during shutdown. The isolated C++ objects were compiled with installed Verilator 5.020 headers while the generated model objects came from the original Verilator 5.050 build. This mixed toolchain is a material integrity limitation; the observation suggests the target request missed, but does not close the hit/miss question as verified evidence. Existing Kunminghu and Heliodor fixture results remain as previously recorded.

Run command (from the repository root; outputs shown are archived here):

```sh
/tmp/xiangshan-cpp-probe/build/verilator-compile/emu \
  -i notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T105705Z-3e81181d1d02/fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace \
  --cst-file=notes/units/evidence/smoke/kunminghu-chisel-db-probe-20261016/constantin.cst \
  --dump-select-db='LoadMissDB0 LoadAccessDB0' \
  --db-path=/tmp/ld-cpp-probe.sqlite
```

The temporary worktrees are not part of the repository. `sha256.txt` records the original generated model header/archive, reference model, and fixture hashes. The observer patch is not retained in the locked source checkout.
