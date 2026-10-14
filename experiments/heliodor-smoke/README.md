# Heliodor base-core smoke

`run.py` copies the locked Heliodor source snapshot into a unique temporary
directory, keeps only the focused `test_smoke` testbench, and runs it with the
pinned Veryl/Verilator toolchain. The upstream test is marked ignored, so the
runner explicitly uses `--include-ignored`. Veryl 0.22.0 requires an explicit
`allow(initial_assign)` on the testbench's ROM initialized with `$readmemh`; the
runner applies that lint-only workaround to the isolated copy. It never edits
`sources/heliodor`.

Example from the repository root:

```sh
PATH="$VERYl_TOOLCHAIN/bin:$PATH" \
  python3 experiments/heliodor-smoke/run.py \
    --stdout notes/units/evidence/smoke/heliodor-core-smoke.stdout.log \
    --stderr notes/units/evidence/smoke/heliodor-core-smoke.stderr.log \
    --archive-dir notes/units/evidence/smoke/heliodor-core-smoke-inputs
```

The archive directory preserves the transformed testbench, copied fixture,
their digests, the locked source revision, and runner metadata. The stdout log
also begins with the invocation metadata and ends with the runner exit code.

The test proves the small base-core instruction/retirement smoke only. It does
not establish RVA23 compliance or the behavior of the separate architectural
extension probes.
