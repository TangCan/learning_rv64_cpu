# Sprint change proposal: Heliodor PMP access-span enforcement

**Status:** draft for scope review  
**Basis:** LD2-E41, LD2-E48–E57; locked Heliodor snapshot `94e9c5821c24a8941c3ddc3b76daddc7124a855a`

## Why change course

Dynamic evidence shows an aligned S-mode `LD` that starts in a permitted TOR entry and crosses into the next entry retires without the expected access fault (E41, E53). The same behavior occurs for 8-byte Sv39 PTE reads (E48–E50, E52). Denied-first controls fault as expected (E51, E54), and a fully contained `LD` succeeds (E55).

Static inspection (E57) confirms the likely cause: `pmp_check` receives an address and access type but no access length, then selects an entry using only `i_addr[55:2]`. The final data path does not provide a length either.

## Proposed objective

In a separate working branch derived from the locked Heliodor snapshot, enforce PMP coverage for the complete architectural access span across every `pmp_check` caller. Keep `sources/heliodor` detached and byte-for-byte unchanged as the evidence baseline. The existing untracked LD-validation SPEC remains untouched; this proposal supplies the scope amendment for a follow-up implementation.

## Scope

- Extend the checker so it identifies the lowest-numbered PMP entry intersecting any byte of an access, requires that entry to cover the complete span, and then applies the existing permission and privilege rules.
- Propagate the actual access span through all 14 call sites: final loads/stores and AMOs, instruction fetch, PTW PTE reads and A/D writes, slot-1 loads, fast stores, SC/AMO commit checks, and CBO checks.
- Preserve existing translation, fault-cause, privilege, and no-match behavior for accesses wholly contained in one entry.
- Add focused checker-level cases and Heliodor fixtures for cross-entry deny, denied-first, same-permission cross-entry, and single-entry success.

## Decisions required during implementation

- Establish where each caller gets its architectural width. `dmem_mmu` currently has store strobes but no load width; fetch must account for compressed instructions; PTE traffic is 8 bytes; CBO maintenance covers its block; atomics use the decoded operation width.
- Handle address-end arithmetic at the physical-address limit without wraparound creating a false in-range result.
- Decide whether the unaligned-access behavior can be exercised in this core; do not use it as a substitute for the aligned cases already reproduced.

## Acceptance criteria

1. Cross-entry accesses fault if the first entry does not cover the entire span, even when the next entry grants the same permission.
2. A denied first byte faults; a fully contained access with permission succeeds.
3. PTE reads and A/D writes use the 8-byte span; instruction, scalar, atomic, and CBO callers use their actual operation span.
4. Existing PMP priority, M-mode unlocked-entry bypass, locked-entry enforcement, and no-match behavior remain unchanged for covered cases.
5. Focused tests pass, and the original `sources/heliodor` checkout still resolves to the locked commit with no modifications.

## Out of scope

- Changes to Kunminghu or its 4 KiB PMP grain; E42 remains a configuration blocker for a naturally aligned 8-byte cross-boundary LD there.
- Generic tracing infrastructure, broad ISA compliance claims, and unrelated MMU or cache changes.

## Work sequence

1. Map and supply the correct length at each caller before changing checker behavior.
2. Implement span matching in the isolated Heliodor branch.
3. Add checker-level cases, then run the focused architectural fixtures against the isolated build.
4. Compare baseline and candidate behavior, record hashes and logs, and review the full diff before deciding whether to merge or upstream the fix.
