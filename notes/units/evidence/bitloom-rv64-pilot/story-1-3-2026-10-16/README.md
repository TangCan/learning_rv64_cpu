# Story 1.3 run evidence

The deterministic case initializes `mem[0]=0x1122334455667788`, `mem[1]=0x8877665544332211`, executes `LD x2,0(x1)`, `SD x2,8(x1)`, then `LD x3,8(x1)`. The captured input description is [`program.S`](program.S), SHA-256 `22f998029280c06e3796d9fcb0908b00832bcd0e658c50b59b597ae67151206d`.

## Bitloom

- Configuration: Bitloom prelude/sim 1.2.4; Rust/Cargo 1.98.1; 8 x 64-bit data words, the two initial values above and six zero words.
- `cargo fmt --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml -- --check` — exit 0 ([log](cargo-fmt.log)).
- `cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml` — exit 0, all 9 tests pass ([log](cargo-test.log)). Tests check initial LD, store PC/address/data, store-then-LD result, consecutive load response association and ordered retirement, boundary addresses, signed S immediate, malformed funct3, and invalid access behavior including unchanged memory after invalid SD.
- `CARGO_TARGET_DIR=target/bitloom-rv64-pilot PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build --package bitloom_rv64_pilot --manifest-dir experiments/bitloom-rv64-pilot --out-dir "$PWD/target/bitloom-out"` — exit 0 ([log](bitloom-build.log)).
- `iverilog -g2012 -tnull target/bitloom-out/BitloomRv64Pilot.v` — exit 0 ([log](iverilog.log)). This checks parsing/elaboration only, not HDL simulation.
- Generated Verilog is [`BitloomRv64Pilot.v`](BitloomRv64Pilot.v), SHA-256 `bc5695f132134b0e5e55362f28cfe7a6dd98e3306de76bad370b332ab10c2f41`; tool versions are in [toolchain.txt](toolchain.txt).

## Kunminghu locked flow

Attempted from the repository root:

```sh
python3 experiments/kunminghu-smoke/run.py --topic zifencei --input notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/program.S --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml --evidence-dir notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/kunminghu
```

Exit 2 at runner argument validation, before tool/source preflight or CPU start: `--input` is restricted to four Story 6.4 assembly paths. The complete command output is [kunminghu-attempt.log](kunminghu-attempt.log). No Kunminghu result or runner manifest record was produced; architecture comparison is unverified.

## Heliodor locked flow

Attempted from the repository root:

```sh
python3 experiments/heliodor-smoke/run.py --topic zifencei --case story-1-3 --archive-dir notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/heliodor
```

Exit 2 at runner argument validation, before source/tool preflight or CPU start: the runner only selects `standard`, `funct12`, `rs1`, or `rd`, and has no custom-input option. The complete output is [heliodor-attempt.log](heliodor-attempt.log). No Heliodor result or runner manifest record was produced; architecture comparison is unverified.
