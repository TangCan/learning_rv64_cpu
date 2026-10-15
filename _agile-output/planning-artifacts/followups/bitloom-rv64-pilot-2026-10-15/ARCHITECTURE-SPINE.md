# Bitloom RV64 Pilot — Architecture Spine

**Status:** Draft
**Scope:** One isolated learning core and its reference/evidence flow.

## Inherited constraints

- The completed RVA23 study and the completed load/store follow-up remain immutable baselines.
- Kunminghu and Heliodor remain independent reference implementations; this pilot neither replaces nor modifies them.
- Static inspection, test-source inspection, simulation, and synthesis are separate evidence types.

## AD-1 — Use a standalone educational core

- **Decision:** Keep the Bitloom design, simulator, generated RTL, and pilot evidence in a separate pilot workspace.
- **Prevents:** Accidental coupling to either upstream build or interpreting the pilot as an upstream port.

## AD-2 — Use a fixed, sequential design paradigm

- **Decision:** Model an in-order RV64I teaching pipeline with explicit stage state and a deterministic synchronous memory interface.
- **Prevents:** The learning slice from acquiring OoO, cache, MMU, or system behavior that cannot be validated within this pilot.

## AD-3 — Pin the research baseline before implementation

- **Decision:** Start with Bitloom 1.2.4 and record exact versions for Rust, Bitloom design/sim crates, and HDL tools. Verify compile, tick/simulation, and Verilog emission before building the core.
- **Prevents:** Results silently mixing API versions or assuming documented capabilities equal tested compatibility.

## AD-4 — Separate design from execution harness

- **Decision:** Keep hardware description and cycle simulation/test drivers in distinct crates or workspace members, using Bitloom's published boundary where supported.
- **Prevents:** Test-only host logic from being mistaken for synthesizable design logic.

## AD-5 — Compare architectural effects, not pipeline timing

- **Decision:** Compare retirement-visible PC/register/memory effects for the same deterministic instruction and data inputs. Keep each core's own test/build path and report coverage per reference independently.
- **Prevents:** False equivalence claims between different microarchitectures or conflating architectural agreement with cycle-level identity.

## AD-6 — Bound vector support to one explicit RVV case

- **Decision:** Implement only 128-bit VLEN `vadd.vv` with SEW=32, LMUL=1, VL=4 for the pilot. Treat other vector configurations and instructions as unsupported.
- **Prevents:** A single vector demonstration from being generalized into full RVV support.

## AD-7 — Gate Verilog/PPA claims on tool evidence

- **Decision:** Archive generated Verilog and exact tool output. Report synthesis and timing only when the required tools and constraints are available.
- **Prevents:** Treating code generation as proof of synthesizability, physical quality, or performance.

## Deferred

- Whether to attempt Kunminghu FIRRTL import; first establish standalone design behavior.
- Veryl conversion/import; no direct path was identified in the research.
- Broader RV64I/RVV, privileged state, MMU, cache, OoO, SMP, compliance suites, and full-core rewrite.
- Target clock, area, process node, and hard PPA thresholds; no target has been selected.
