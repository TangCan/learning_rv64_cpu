---
title: 'Story 1.5 — Verilog 导出与阶段决策'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
context:
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/prd.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/ARCHITECTURE-SPINE.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epics.md
---

## Intent

Export the fixed RV64I/LD/SD and VLEN=128 vector designs, preserve reproducible tool output and synthesis evidence, and make an explicit stop/continue decision against the PRD stage gates.

## Acceptance

- [x] Generate Verilog with the pinned Bitloom CLI and archive outputs, commands, toolchain and SHA-256.
- [x] Parse both generated designs with Icarus and run generic Yosys synthesis/check.
- [x] Record unavailable reference comparisons and absence of technology-specific PPA evidence accurately.
- [x] Record an explicit stage decision and update Epic/Story status.

## Decision

**Stop the Bitloom pilot after the bounded self-check. Do not start a complete core rewrite or expand ISA/RVV scope.** The fixed RV64I/LD/SD Bitloom tests and restricted 128-bit lane test pass; both designs export to Verilog, pass Icarus parsing, and pass generic Yosys checks/synthesis. The current Kunminghu/Heliodor runners reject the custom memory and vector cases before CPU startup, so no cross-core LD/SD or vector equivalence is established. Generic synthesis has no target cell library or timing constraints, so it provides no physical area or timing result. Any renewed comparison should first add a reviewed fixed fixture path to each reference runner.

This is a bounded pilot stop decision, not an RVA23, full RV64I, full RVV, performance, or product-readiness claim.

## Evidence

The final generated RTL, build logs, Icarus logs, Yosys reports, toolchain versions and hashes are archived at `notes/units/evidence/bitloom-rv64-pilot/story-1-5-2026-10-16/`. Yosys 0.33 reports zero problems after `check` and successful generic synthesis: 16,349 cells for `BitloomRv64Pilot` and 1,274 cells for `BitloomVectorCase`. These counts are generic netlist statistics only; they are not comparable implementation metrics.

## Follow-up boundary

No later Epic is configured in this pilot. `epic-1-retrospective` remains `optional` under the sprint file's rule that permits ending without another Epic.
