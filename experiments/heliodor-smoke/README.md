# Heliodor isolated base and arch smoke

The runner checks the locked Heliodor revision, clean checkout, gitlinks, manifest, and the manifest-pinned Veryl, Verilator, and C++ compiler versions. It checks the Veryl 0.22.0 binary identity by SHA-256. It builds a fresh temporary project copy containing the pinned RTL/configuration, the base `test_smoke`, one ordinary arch harness target (`test_arch_rv64ui_add`), and their exact instruction images; it hashes those copied inputs before and after execution.

The shared `tb/test_arch_common.veryl` contains the ordinary 1 MiB harness, an unrelated uninstantiated 64K-word debug harness, and many arch tests. The runner retains only the ordinary harness and `test_arch_rv64ui_add`; it excludes the debug variant and unrelated targets. Its isolated edits add `#[allow(initial_assign)]` to the unique `imem` declaration in `test_smoke` and the unique DRAM declaration in the arch harness. It verifies each transformation anchor and copied input hash, then rechecks the locked source after execution. These harness workarounds do not automatically apply to topic tests involving memory, translation, interrupts, or timing; review semantic applicability per story.

Run from the repository root (the toolchain path shown here is the configured Story 6.1 install):

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --timeout 180
```

To run the locked RV64UI LD suite through the same isolated runner:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld --timeout 180
```

To observe the target PC's DCache safe-hit and fill-start signals, run the
self-checking cold-load fixture:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 180
```

The isolated core copy qualifies `dc_hit_safe` and `dc_miss_valid` with the
target LD PC and latches whether either signal was observed. `hit` means a
DCache safe hit, not a raw tag comparison. The default cold-load fixture also
captures its retirement PC, destination, and data. Its current observation is
one target retirement at `0x80000008` (`rd=x6`, value
`0x123456789abcdef0`) and both hit and fill-start signals at that PC.

To validate the arch harness's injected PMA-hole load-fault path with a
self-checking M-mode trap handler:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe \
  --ld-probe-source experiments/rv64-ld-probe/ld-heliodor-pma-fault.S \
  --ld-probe-expect-fault --timeout 300
```

The fixture's handler checks cause 5, the target `mepc`, and the faulting
address in `mtval` before writing `tohost=1`. The runner treats this marker as
the expected result only in the explicit fault mode. The isolated arch harness
sets `PMA_FAULT=1`; this exercises its injected PMA-hole path and does not
establish hardware PMP enforcement or an implementation PMA register map.
The run manifest retains the first pre-mode attempt as `run-fail`: that run
reached the fixture's pass marker, but the success-only probe criteria rejected
the expected exception. Later runs with `--ld-probe-expect-fault` passed.

To validate Heliodor's locked PMP read-denial path on a DRAM address, run:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe \
  --ld-probe-source experiments/rv64-ld-probe/ld-heliodor-pmp-fault.S \
  --ld-probe-expect-fault --timeout 300
```

The fixture reads back `pmpaddr0=0x200009ff` and `pmpcfg0=0x98` before the
target load. Its locked NAPOT entry denies reads from `0x80002000`; that page
is in the harness's DRAM range, which passes the separate `PMA_FAULT` map check.
An earlier fixture revision omitted the CSR readback and did not reach its
pass marker; that blocked run is retained in the run manifest.

To check M-mode bypass of an unlocked matching entry with no permissions:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe \
  --ld-probe-source experiments/rv64-ld-probe/ld-heliodor-pmp-m-bypass.S \
  --timeout 300
```

The fixture warms the DRAM address before programming `pmpcfg0=0x18`, reads
back the entry, then requires a second M-mode load to return the same value.
The target request must also be observed as a DCache hit without an access fault.

To verify S-mode enforcement for an unlocked PMP match while keeping the code
and trap handler accessible through a lower-priority DRAM entry:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe \
  --ld-probe-source experiments/rv64-ld-probe/ld-heliodor-pmp-s-deny.S \
  --ld-probe-expect-fault --timeout 300
```

The fixture reads back both PMP addresses and `pmpcfg0`, delegates load access
fault cause 5 to S-mode, and enters S-mode with `mret`. The handler must observe
`scause=5`, `sepc=ld_target`, and `stval=0x80002000` before it writes
`tohost=1`. The target request faults before the DCache probe; this case does
not cover U-mode or page-table-walk PMP checks.

To run the settled prewarm fixture and check that the target access hits without
a fill start:

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic ld-probe \
  --ld-probe-source experiments/rv64-ld-probe/ld-hit-settled.S --timeout 180
```

This run passed with `req=1 hit=1 miss=0` at target PC `0x80000030`, along with
the fixture checks and `tohost=1/pass=1`. The fixture's retirement port did not
capture that target instruction, so the record leaves `observed_retirement`
empty; the cache request itself is PC-qualified. Kunminghu's `--topic ld` uses
the shared cold-load assembly and linker. Its archived `fixture.bin` and
Heliodor `ld-probe.hex` decode to the same 4104-byte image (SHA-256
`f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`).

Each run gets a unique subdirectory under `notes/units/evidence/smoke/heliodor-core-smoke-inputs/` with the exact runner, transformed test/harness, input images, combined output, and `run-metadata.json`; separate stdout/stderr logs are kept beside it. The run record is appended under a lock using atomic replacement to the Heliodor `runs` list in `notes/units/evidence/cpu-validation-toolchain-v1.yaml`. It records commands, versions, working directory, CPU observations, result registers/tohost, resource context, failure stage, and artifact/log SHA-256 values. Preflight and timeout failures before CPU output are `blocked`; failures after CPU output are `run-fail`.

A passing run requires `test_smoke` to report x10=7, x11=11, x12=77, x13=11 and `[test_smoke] PASS`, plus the selected architecture target's `tohost=1`, `pass=1`, and PASS marker. For `--topic ld`, this establishes only that the locked RV64UI LD suite completed its self-check on one Heliodor DUT. The suite result does not expose an individual LD retirement PC or `rd` value, and does not establish Kunminghu equivalence or RVA23 compliance. For Zifencei and LD runs, startup is established from the arch target's own result marker; a generic smoke marker from the separate invocation does not establish that target's startup. If the target emits no result marker, the runner leaves startup unobserved and records the run as blocked.
