# Kunminghu first-issue DCache hit probe (LD2-E26)

This isolated C++ probe observes a successful target `LD` whose first issue hits in the DCache. The tracked fixture `experiments/rv64-ld-probe/ld-first-hit.S` performs one preheat `LD`, checks its value, waits 256 NOPs, then executes `ld_target`. It has no older overlapping store. The archived map places the target at PC `0x80000430` and data at `0x80000480`.

## Result

- Target stage 1, cycle 4235, lane 2: PC `0x80000430`, address `0x80000480`, `miss=0`, `tag=1`, `perm=1`.
- Target stage 2, cycle 4236, lane 2: PC `0x80000430`, PADDR `0x80000480`, `hit=1`, `first=1`.
- Commit trace: target instruction `0x0002b303` commits at PC `0x80000430`, writes x6=`0x123456789abcdef0`.
- NEMU reports GOOD TRAP; emulator exit code is 0. The fixture runner separately reports `run-pass` (run ID `kunminghu-fixture-20261019T031556Z-0b04a6183011`).

The preheat LD itself first missed and replayed. The evidence claim is limited to the target LD's first issue. It does not independently establish M-mode/Bare, absence of exceptions, or privilege/PMP/PMA configuration.

## Build and observation integrity

The locked Kunminghu sources remain at `c098f996bf4d301b88693b20315486d31e93bc9d`, and the nested difftest sources at `3729300ae233816d332d057f170472ebe35147b0`. No RTL was regenerated or changed. The temporary observer was built with Verilator v5.050 headers/configuration and linked against the unchanged generated-model archive and runtime objects from the locked build; only the C++ emulator/Verilator driver objects were instrumented. `observer.patch.gz` records the temporary sampling changes.

`input.S`, `fixture.bin`, `fixture.map`, `runner.log`, and `run.log` preserve the input and relevant results. `sha256.txt` contains their hashes.

## Reproduce the fixture run

```sh
cp notes/units/evidence/cpu-validation-toolchain-v1.yaml /tmp/ld-first-hit-manifest.yaml
python3 experiments/kunminghu-smoke/run.py \
  --topic ld \
  --ld-source experiments/rv64-ld-probe/ld-first-hit.S \
  --timeout 180 \
  --manifest /tmp/ld-first-hit-manifest.yaml \
  --evidence-dir experiments/kunminghu-smoke/.ld-first-hit-runs
```
