# Kunminghu C++ cache hit probe (LD2-E25)

This run isolates the stage-1 cache lookup timing and then samples stage 2 for a target load. The fixture at `input.S` performs one preheat `LD`, checks its value, waits 64 NOP cycles for refill, and executes `ld_target`. The archived linker map places `ld_target` at PC `0x80000130` and data at `0x80000180`.

The temporary observer patch samples DCache stage 1 after the falling-edge evaluation and stage 2 after the rising-edge evaluation. For the target:

- First stage-1 attempt, cycle 4184, lane 2: PC `0x80000130`, address `0x80000180`, `miss=1`, `tag=0`, `perm=0`.
- Replay stage-1 lookup, cycle 4192, lane 1: same PC/address, `miss=0`, `tag=1`, `perm=1`.
- Stage 2, cycle 4193, lane 1: same PC/PADDR, `hit=1`, `first=0`.
- Target instruction commits with x6=`0x123456789abcdef0`; emulator exit code 0 and NEMU GOOD TRAP at `0x80000168`.

This verifies a target-PC DCache hit on replay after the initial miss. The fixture passed its data check. It does not imply the first issue was a hit, and does not independently establish M-mode/Bare, exception absence, or older-store conditions.

The observer was compiled in an isolated difftest worktree with Verilator v5.050 headers/configuration and GCC 13.3, then linked against unchanged generated model/runtime objects from the locked Kunminghu build. The model was not regenerated and both locked source trees remained clean. `observer.patch`, exact input, linker map, image, relevant run output and `sha256.txt` are archived here. The stderr log omits unrelated simulator performance counters.

Fixture run record: `kunminghu-fixture-20261019T025734Z-b6169dcf8d23` (run-pass).

To rebuild the fixture without changing the tracked evidence manifest:

```sh
cp notes/units/evidence/cpu-validation-toolchain-v1.yaml /tmp/ld-probe-manifest.yaml
python3 experiments/kunminghu-smoke/run.py \
  --topic ld \
  --ld-source experiments/rv64-ld-probe/ld-hit-wait.S \
  --timeout 180 \
  --manifest /tmp/ld-probe-manifest.yaml \
  --evidence-dir experiments/kunminghu-smoke/.ld-probe-runs
```

The instrumented emulator invocation uses the temporary C++ observer patch archived here, the generated `fixture.bin`, and the same options as LD2-E24; its output database was `/tmp/ld-wait-final.sqlite`.
