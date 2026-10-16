# Story 1.5: Verilog export and stage decision

## Reproduction

From the repository root, the final designs were generated with the isolated Bitloom CLI 1.2.4:

```sh
CARGO_TARGET_DIR=target/bitloom-rv64-pilot PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build --package bitloom_rv64_pilot --manifest-dir experiments/bitloom-rv64-pilot --out-dir "$PWD/target/bitloom-final-out"
CARGO_TARGET_DIR=target/bitloom-vector-case PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build --package bitloom_vector_case --manifest-dir experiments/bitloom-vector-case --out-dir "$PWD/target/bitloom-vector-out"
iverilog -g2012 -tnull target/bitloom-final-out/BitloomRv64Pilot.v
iverilog -g2012 -tnull target/bitloom-vector-out/BitloomVectorCase.v
yosys -p 'read_verilog target/bitloom-final-out/BitloomRv64Pilot.v; hierarchy -check -top BitloomRv64Pilot; proc; opt; check; synth -top BitloomRv64Pilot; stat'
yosys -p 'read_verilog target/bitloom-vector-out/BitloomVectorCase.v; hierarchy -check -top BitloomVectorCase; proc; opt; check; synth -top BitloomVectorCase; stat'
```

Both builds, both Icarus elaborations, and both Yosys runs exited 0. Generated outputs and full logs are in this directory; exact versions and SHA-256 values are in `toolchain.txt` and `sha256.txt`. `core-host-Cargo.lock` and `vector-host-Cargo.lock` preserve the CLI-generated shim dependency resolutions. The vector HDL behavioral test is separately captured in the Story 1.4 evidence directory.

Yosys 0.33 reports zero `check` problems, then synthesizes generic logic: 16,349 cells for the RV64 pilot module and 1,274 cells for the vector module. No target library or timing constraints were provided. These results do not establish target area, frequency, power or PPA.

## Decision

Stop the Bitloom pilot after this bounded self-check. The RV64I subset, LD/SD case and 128-bit `vadd.vv` case pass their local checks and exports. The locked reference runners cannot accept these custom cases, so cross-core memory/vector equivalence remains unverified. Do not expand into a complete core rewrite or broader ISA/RVV support based on these results. A later comparison should first provide fixed, reviewable LD/SD and vector fixtures for the reference flows.
