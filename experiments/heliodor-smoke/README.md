# Heliodor isolated base and arch smoke

The runner checks the locked Heliodor revision, clean checkout, gitlinks, manifest, and the manifest-pinned Veryl, Verilator, and C++ compiler versions. It checks the Veryl 0.22.0 binary identity by SHA-256. It builds a fresh temporary project copy containing the pinned RTL/configuration, the base `test_smoke`, one ordinary arch harness target (`test_arch_rv64ui_add`), and their exact instruction images; it hashes those copied inputs before and after execution.

The shared `tb/test_arch_common.veryl` contains the ordinary 1 MiB harness, an unrelated uninstantiated 64K-word debug harness, and many arch tests. The runner retains only the ordinary harness and `test_arch_rv64ui_add`; it excludes the debug variant and unrelated targets. Its isolated edits add `#[allow(initial_assign)]` to the unique `imem` declaration in `test_smoke` and the unique DRAM declaration in the arch harness. It verifies each transformation anchor and copied input hash, then rechecks the locked source after execution. These harness workarounds do not automatically apply to topic tests involving memory, translation, interrupts, or timing; review semantic applicability per story.

Run from the repository root (the toolchain path shown here is the configured Story 6.1 install):

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --timeout 180
```

Each run gets a unique subdirectory under `notes/units/evidence/smoke/heliodor-core-smoke-inputs/` with the exact runner, transformed test/harness, input images, combined output, and `run-metadata.json`; separate stdout/stderr logs are kept beside it. The run record is appended under a lock using atomic replacement to the Heliodor `runs` list in `notes/units/evidence/cpu-validation-toolchain-v1.yaml`. It records commands, versions, working directory, CPU observations, result registers/tohost, resource context, failure stage, and artifact/log SHA-256 values. Preflight and timeout failures before CPU output are `blocked`; failures after CPU output are `run-fail`.

A passing run requires both targets: `test_smoke` must report x10=7, x11=11, x12=77, x13=11 and `[test_smoke] PASS`; the ordinary RV64UI add target must report `tohost=1`, `pass=1` and `v4 rv64ui-add PASS`. This only establishes a base-core smoke and a single ordinary arch target on the pinned setup. It is not evidence of RVA23 compliance or of the behavior of separate architectural extension probes.
