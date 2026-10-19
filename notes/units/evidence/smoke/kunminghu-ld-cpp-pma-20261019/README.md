# Kunminghu target load runtime PMA attribute probe (LD2-E32)

This extends the LD2-E27 observer for the LD2-E26 first-issue hit fixture. On the target stage-2 sample it captures the LoadUnit's `s2_mmio`, `s2_actually_uncache`, and `s2_uncache` values alongside privilege, SATP mode, exception summary, and DCache hit.

## Result

- Cycle 4236, lane 2, target PC `0x80000430`, PADDR `0x80000480`: `hit=1`, `first=1`, `satp_mode=0`, `priv_imode=3`, `exception=0`, `mmio=0`, `actually_uncache=0`, `uncache=0`.
- The target committed x6=`0x123456789abcdef0`; NEMU reported GOOD TRAP and the emulator exited 0.

This observes the effective non-MMIO and non-uncached classification for this request. It does not expose the raw matched PMA/PMP entry or cover a denied access.

## Build integrity

Sources were Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` and nested difftest `3729300ae233816d332d057f170472ebe35147b0`. The observer patch was applied to a temporary difftest worktree. Only `emu.o` and `verilator.o` were rebuilt with GCC 13.3 and Verilator v5.050 headers; the locked generated model archive and existing runtime objects were linked unchanged. The original checkout and RTL build were not modified. `observer.patch` is the complete temporary C++ diff.

`input.S`, `fixture.bin`, `fixture.map`, `run.stdout`, `run.stderr`, and `sha256.txt` preserve the fixture and run evidence.
