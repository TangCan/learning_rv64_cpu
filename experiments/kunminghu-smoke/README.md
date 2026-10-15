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
