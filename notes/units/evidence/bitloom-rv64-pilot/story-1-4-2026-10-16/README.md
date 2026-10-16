# Story 1.4: restricted 128-bit `vadd.vv` evidence

The independent `BitloomVectorCase` design fixes VLEN=128, SEW=32, LMUL=1, VL=4. `vector_init` loads v1/v2 and clears v3; a valid `vadd_enable` writes the four independent 32-bit sums to v3 at the next rising edge. Invalid VL/SEW/LMUL raises `vector_unsupported`, suppresses writeback, and preserves v3.

## Commands and outcomes

Run from the repository root:

```sh
cargo fmt --manifest-path experiments/bitloom-vector-case/Cargo.toml -- --check
cargo check --locked --manifest-path experiments/bitloom-vector-case/Cargo.toml
CARGO_TARGET_DIR=target/bitloom-vector-case PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build --package bitloom_vector_case --manifest-dir experiments/bitloom-vector-case --out-dir "$PWD/target/bitloom-vector-out"
iverilog -g2012 -s vector_case_tb -o /tmp/bitloom-vector-case.vvp notes/units/evidence/bitloom-rv64-pilot/story-1-4-2026-10-16/BitloomVectorCase.v experiments/bitloom-vector-case/tests/vector_case_tb.sv
vvp /tmp/bitloom-vector-case.vvp
yosys -p 'read_verilog notes/units/evidence/bitloom-rv64-pilot/story-1-4-2026-10-16/BitloomVectorCase.v; hierarchy -check -top BitloomVectorCase; proc; opt; check; synth -top BitloomVectorCase; stat'
```

Formatting, crate check, generation, Icarus compile/runtime, and Yosys synthesis all exited 0. The HDL test checks these two lane-ordered examples (`lane3` is the most significant word):

| v1 `[3:0]` | v2 `[3:0]` | v3 `[3:0]` |
|---|---|---|
| `00000000,7fffffff,00000001,ffffffff` | `ffffffff,00000001,ffffffff,00000001` | `ffffffff,80000000,00000000,00000000` |
| `7fffffff,ffffffff,80000000,00000000` | `00000001,00000001,80000000,ffffffff` | `80000000,00000000,00000000,ffffffff` |

The testbench also tries VL=3, SEW=16, and LMUL=2 independently; each is rejected and leaves v3 unchanged. Icarus output is in `iverilog-run.log`.

Yosys 0.33 reports zero `check` problems and 1,274 generic cells after `synth`. This confirms generic synthesis only. No target library, constraints, timing, area, or physical PPA are implied.

The locked Kunminghu runner does not offer a vector topic and rejected `--topic vector-case` at argparse validation (exit 2). The Heliodor runner rejects the same topic at its argument validation (exit 2). Neither CPU started; the lane results are self-checks and not cross-core differential evidence. Logs are `kunminghu-attempt.log` and `heliodor-attempt.log`.

`BitloomVectorCase.v` is the generated RTL. `vector_case_tb.sv` is the testbench copy. The crate lock and generated host-shim lock are `vector-Cargo.lock` and `vector-host-Cargo.lock`; SHA-256 values are in `sha256.txt`, and tool versions are in `toolchain.txt`.
