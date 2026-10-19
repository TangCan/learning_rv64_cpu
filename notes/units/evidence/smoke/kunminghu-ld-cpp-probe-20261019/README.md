# Kunminghu C++ cache probe (LD2-E24)

This run observes the settled fixture's target load at PC `0x80000030`, PADDR `0x80000080`. It uses a temporary C++ observer to sample each DCache load lane's stage-2 `valid`, `paddr`, `_s2_hit_T_2`, and `s2_req_isFirstIssue`, alongside the corresponding LoadUnit stage-2 PC. The archived `observer.patch` is the complete temporary source diff; it was applied only in an isolated difftest worktree.

## Result

- cycle 4178, lane 2: target PC/PADDR, `first=1`, `hit=0`.
- cycle 4188, lane 1: target PC/PADDR, `first=0`, `hit=0` (replayed request).
- The emulator exited 0 and NEMU reported `HIT GOOD TRAP at pc = 0x80000068`.

`LoadPipe.scala:415` defines `s2_hit` as tag match, permission, coherence-state match, and no WPU prediction failure. The generated model's `_s2_hit_T_2` is this stage-2 hit result. Thus this settled fixture's target request missed on its first issue and replay; it does not provide a target hit example. This agrees with the prior aggregate counters (`real_miss_first_issue=2`, `load_hit=0`) but adds PC/PADDR association.

## Build integrity

The locked RTL model was not regenerated. The temporary `emu.o` and `verilator.o` were recompiled with GCC 13.3 and Verilator v5.050 headers/configuration, matching the original generated model and runtime objects. Verilator source tag `v5.050` resolves to commit `848d926ebd4addacacd294dc84e35d9d4ae8078c`; the annotated tag object is `0a24d49771fa57c36ff667272bf7b5c6705e4df0`. The model archive and Verilator runtime objects were copied unchanged from the locked checkout build into the temporary build directory. The first run with mixed 5.020/5.050 C++ objects had SIGSEGV at shutdown and was discarded; this matching-version rerun exits cleanly.

`sha256.txt` records hashes of the persistent model, fixture, NEMU reference and archived logs/patch. No tracked source or original build artifact was modified.

## Command

Run from the repository root with the temporary instrumented emulator:

```sh
/tmp/xiangshan-cpp-probe/build/verilator-compile/emu \
  -i notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T105705Z-3e81181d1d02/fixture.bin \
  --diff=sources/xiangshan/ready-to-run/riscv64-nemu-interpreter-so \
  --max-cycles=10000 --max-instr=1000 --dump-commit-trace \
  --cst-file=notes/units/evidence/smoke/kunminghu-chisel-db-probe-20261016/constantin.cst \
  --dump-select-db='LoadMissDB0 LoadAccessDB0' \
  --db-path=/tmp/ld-cpp-probe-5050.sqlite
```
