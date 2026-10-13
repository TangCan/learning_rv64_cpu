# XiangShan / Kunminghu V2 evidence digest — r1-1

**Retrieved:** 2026-10-13. Research restricted to current public upstream pages retrieved during this run. Source inspection only; no RTL build, simulation, or certification run was performed.

## Findings

1. **Kunminghu V2R2 has a public architectural feature claim for Sstc.** The official User Guide says the core supports timer interrupts and the RVA23-Sstc feature; its architecture overview identifies the subject as Kunminghu V2R2. This is product documentation, not an executed conformance result.
   - **Source URL:** https://docs.xiangshan.cc/projects/user-guide/en/kunminghu-v3/introduction/
   - **Publisher:** OpenXiangShan, XiangShan User Guide
   - **Pub date/commit:** No date displayed on page; page describes Kunminghu V2R2 (accessed 2026-10-13)
   - **Confidence:** High for documented feature claim; no inference about full profile compliance
   - **Claim class:** Official documentation

2. **Timer implementation is documented as reusing CLINT mtime and broadcasting time values for Sstc support.** This gives a concrete architecture lead: trace timer/CLINT, `stimecmp`, STCE gating, and interrupt propagation through the timer/interrupt controller documentation and RTL.
   - **Source URL:** https://docs.xiangshan.cc/projects/user-guide/en/kunminghu-v3/processor/
   - **Publisher:** OpenXiangShan, XiangShan User Guide
   - **Pub date/commit:** No date displayed; accessed 2026-10-13
   - **Confidence:** High for documented design description
   - **Claim class:** Official design documentation

3. **Kunminghu V2R2 HPM documentation explicitly claims Sscofpmf support and describes overflow behavior.** It names `mhpmevent` event selection, privilege sampling/combination, and LCOFIP interrupt vector 12. Follow-up should inspect HPM/CSR/interrupt RTL and verify the privilege filtering, overflow flag/interrupt, delegation, and counter semantics with directed tests.
   - **Source URL:** https://docs.xiangshan.cc/projects/design/zh-cn/kunminghu-v3/backend/HPM/
   - **Publisher:** OpenXiangShan, XiangShan design documentation
   - **Pub date/commit:** Page gives design version V2R2 and date 2025-02-27; accessed 2026-10-13
   - **Confidence:** High for documented feature and intended behavior; not executed evidence
   - **Claim class:** Official design specification

4. **The current Kunminghu V2R2 User Guide’s supported-extension inventory includes `zifencei`, `sscofpmf`, `ssstateen`, and `sstc`, but omits `ssnpm`.** This differs from the separate Kunminghu V2 source excerpt quoted in XiangShan issue #3973 (commit `fcefab3`), which lists `sscofpmf`, `ssstateen`, `sstc`, and `zifencei`, likewise omitting `ssnpm`. Treat extension-name inventory as a claim/configuration hint only; it does not establish that all required behaviors are implemented or validated. The guide is newer/current but its inventory also includes extensions not in that source excerpt, so reconcile the exact branch/release before drawing a code conclusion.
   - **Source URLs:** https://docs.xiangshan.cc/projects/user-guide/en/kunminghu-v3/instruction-set/ ; https://github.com/OpenXiangShan/XiangShan/issues/3973
   - **Publisher:** OpenXiangShan (User Guide; XiangShan GitHub issue)
   - **Pub date/commit:** Guide page has no displayed date; issue opened 2024-12-02 and quotes source commit `fcefab3`; accessed 2026-10-13
   - **Confidence:** High for what each inventory says; medium for branch correspondence
   - **Claim class:** Documentation/source inventory comparison

5. **ACT4 has relevant coverage plans, but that is test availability, not a XiangShan result.** Its profile matrix links `t-Zifencei-coverpoints`; lists `Sscofpmf` as Counter Filtering (mandatory in RVA23S64), `Ssstateen` as Supervisor State Enable (mandatory in RVA23S64), and `Ssnpm` as Pointer Masking (mandatory in RVA23S64). The plan states x=mandatory and says certification covers mandatory and optional extensions. XiangShan-specific configuration, pass/fail reports, and invocation are not established by this page.
   - **Source URL:** https://github.com/riscv/riscv-arch-test/blob/act4/docs/ctp/src/profiles.adoc
   - **Publisher:** RISC-V International, riscv-arch-test repository
   - **Pub date/commit:** Branch `act4`, current page; no commit date displayed; accessed 2026-10-13
   - **Confidence:** High for named coverage-plan entries/profile matrix; none for XiangShan execution
   - **Claim class:** Test-plan evidence

6. **Sstc-specific ACT coverage is a useful follow-up, but the public profile matrix inspected did not surface an `Sstc` row in the searched excerpt.** An official RISC-V arch-test issue contains recent Sstc/SstcSm suite accounting (commit `6101568`, dated 2026-09-28) and a separate proposal discusses Sstc test setup macros. These are test-project artifacts, not evidence that XiangShan ran them. Determine the exact ACT branch/config and target-environment requirements before adopting them.
   - **Source URLs:** https://github.com/riscv/riscv-arch-test/issues/2644 ; https://github.com/riscv/riscv-arch-test/issues/2594
   - **Publisher:** RISC-V International, riscv-arch-test repository
   - **Pub date/commit:** Issue #2644 reports 2026-09-28 and commit `6101568`; issue #2594 opened 2026-09-29; accessed 2026-10-13
   - **Confidence:** High for the reported suite/accounting and proposed macros; no XiangShan execution claim
   - **Claim class:** Test inventory / test-development evidence

## Searched but not found

- Public XiangShan CI, regression log, or certification report showing executed results for `Zifencei`, `Sstc`, `Sscofpmf`, `Ssnpm`, or `Ssstateen` on a named Kunminghu V2/V2R2 configuration.
- A public Kunminghu V2R2 `Ssnpm` implementation claim matching the User Guide extension inventory. The guide inventory omits it, while the current V3 manual inventory includes it; this version discrepancy needs resolution.
- A public XiangShan module/file path specifically implementing `Ssnpm` or `Ssstateen`, plus a matching directed test name/config. Symbol search results were not sufficient to establish behavior.
- A XiangShan-specific ACT4 test configuration or run command for these extensions.

## Follow-up leads

1. Pin the exact open-source Kunminghu V2R2 branch/tag and inspect `Parameters.scala` plus CSR/HPM/timer/interrupt RTL. Resolve User Guide V2R2 vs `kunminghu-v3` path naming and source/docs version drift.
2. In the official ACT4 tree, follow coverage links for `t-Zifencei-coverpoints`, `t-Sscofpmf-coverpoints`, `t-Ssstateen-coverpoints`, and `t-Ssnpm-coverpoints`; establish their harness prerequisites and exact configs.
3. Request or locate a reproducible XiangShan/DiffTest run artifact with test commit, DUT commit, generated config, command line, and pass/fail logs. Treat NEMU/reference-model coverage separately from DUT execution.
4. For Zifencei, test self-modifying code / instruction-cache synchronization behavior, beyond decoding or advertised ISA string. For Sstc/Sscofpmf/Ssstateen, target CSR access gating and interrupt/delegation semantics. For Ssnpm, first resolve whether this Kunminghu target claims the extension at all.
