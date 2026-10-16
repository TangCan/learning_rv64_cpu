# Kunminghu fixture smoke

This minimal RV64I fixture checks `7 + 11 == 18` and exits through the
locked XiangShan NEMU custom trap instruction (`0x0005006b`, with `a0=0`).
The emulator's reset flash stub transfers control to RAM at `_start`, which is linked at
`0x80000000`, the Kunminghu RAM load base. The runner retains the ELF, link
map, raw image, exact commands, tool versions, split logs, and a manifest run
record under `notes/units/evidence/smoke/`.

From the repository root, run:

```sh
python3 experiments/kunminghu-smoke/run.py \
  --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml
```

The `ld` topic builds the shared `experiments/rv64-ld-probe/ld.S` fixture with
the Heliodor probe's linker script. It checks the native commit trace against
the linked target PC, instruction, effective address, `rd`, and expected 64-bit
value, then requires the fixture's self-checking NEMU good trap:

```sh
python3 experiments/kunminghu-smoke/run.py --topic ld \
  --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml
```

The same assembly source and linker produce the byte-identical raw image used
by Heliodor's `--topic ld-probe` (4104 bytes; SHA-256
`f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`); the two
runners execute it independently under different simulators. The runner does
not expose a target-PC DCache response, so cache-hit status remains unverified.
For an alternate prewarmed fixture, `--ld-source` selects another project-local
assembly file:

```sh
python3 experiments/kunminghu-smoke/run.py --topic ld \
  --ld-source experiments/rv64-ld-probe/ld-hit-settled.S --timeout 180
```

The run record preserves aggregate L1 DCache/load-unit counters, but they are
not tagged with a PC. This two-load settled fixture reported two first-issue
real misses and zero load hits; that aggregate result does not identify which
request missed and does not establish a target hit. This is not an RVA23
profile result.

The runner requires the locked `sources/xiangshan` checkout and direct
gitlinks, the existing single-hart `KunminghuV2Config` emulator, its NEMU
reference library, and `riscv64-unknown-elf-gcc`/`objcopy`. It does not rebuild
or write into `sources/`; use Story 6.1's documented toolchain provisioning
steps when these ignored simulator artifacts or tools are absent. Compile/link
and raw-image generation each have a fixed 120-second timeout; `--timeout`
controls the emulator's wall time and must be finite and positive. A passing
smoke only passes when the expected raw image path is reported, the linked entry
is committed, the simulator reaches the map-matched good trap, and the process
exits successfully without BADTRAP, ABORT, or a critical error. The manifest
append is serialized and atomic so concurrent runs retain every record. Run
metadata records the emulator and NEMU binary SHA-256 values as well as reported
tool versions, and records and rechecks the fixture source and linker script hashes
from before compilation. A smoke only proves this fixture ran under the locked configuration; it is not RVA23
profile evidence. If a run cannot be appended to the manifest, the runner exits
with an error and writes `run-record.json` in that run's evidence directory;
check `manifest_persisted`, `manifest_durable`, and any associated error field
before treating the result as fully recorded. The regression suite also requires the locked
toolchain, emulator and NEMU library so its arithmetic test cannot silently skip;
provision them using Story 6.1 before running `pytest`.

`--max-instr` sets a positive simulator instruction limit (default `10000`).
The runner records the selected value in the manifest command. A larger limit
does not make a run pass without the fixture's terminal marker and assertions.
