# Kunminghu target load context probe (LD2-E27)

This extends the LD2-E26 observer with the load lane's registered privilege mode, SATP mode, and stage-2 exception summary. It uses the same `ld-first-hit.S` fixture and target PC `0x80000430`.

## Result

- At cycle 4236, lane 2's valid target request had `hit=1`, `first=1`, `satp_mode=0`, `priv_imode=3`, and `exception=0`.
- In this snapshot, `CSRConst.ModeM` is 3, and the registered TLB CSR mode is sourced from the CSR privilege mode. SATP mode 0 is Bare. `LoadUnit.s2_exception` is gated by `s2_vecActive` and summarizes the selected load exceptions and debug trigger; it was 0 for this target request.
- The target committed x6=`0x123456789abcdef0`; NEMU reported GOOD TRAP and the emulator exited 0.

This verifies M-mode, Bare, and a clear stage-2 exception summary for this Kunminghu target request. It does not establish PMP/PMA setup, absence of older overlapping stores beyond the fixture's instruction sequence, or any Heliodor privilege configuration.

## Build integrity

Kunminghu and nested difftest revisions were `c098f996bf4d301b88693b20315486d31e93bc9d` and `3729300ae233816d332d057f170472ebe35147b0`. The observer was compiled in a temporary difftest worktree with Verilator v5.050 headers and runtime objects. It linked against the locked generated-model archive and unchanged non-runtime driver objects. No RTL was regenerated. `observer.patch.gz` captures the temporary observer changes; captured emulator stdout and stderr (stdout trailing spaces normalized), fixture input, image, map, and hashes are included.
