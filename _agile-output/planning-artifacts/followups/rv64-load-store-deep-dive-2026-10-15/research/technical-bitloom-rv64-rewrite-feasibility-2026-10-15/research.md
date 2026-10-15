---
title: 'technical research: Bitloom RV64 rewrite feasibility'
type: technical
topic: 'Bitloom RV64 rewrite feasibility'
decision: 'Assess whether Bitloom is a viable framework to rewrite the Kunminghu and Heliodor RV64 CPUs, and recommend a minimal pilot.'
source: native-run
status: complete
preset: standard
validation: normal
created: 2026-10-15
updated: 2026-10-15
claims_verified: 1
claims_unverified: 5
---

# technical research: Bitloom RV64 rewrite feasibility

**Decision this research serves:** Assess whether Bitloom is a viable framework to rewrite the Kunminghu and Heliodor RV64 CPUs, and recommend a minimal pilot.

## Executive summary

**Recommendation: do not commit to a full rewrite of either CPU yet.** Bitloom is an RTL design framework that elaborates Rust design crates and emits Verilog, with FIRRTL interop and cycle-level simulation. Its published CPU material is a pair of RV32 teaching cores; it does not establish RV64/RVA23 core-scale readiness. A rewrite is technically plausible, but compatibility, timing, and verification effort remain unproven. [1][2][3][4]

Kunminghu and Heliodor are far beyond those examples. Their documented designs include out-of-order execution, vector processing, MMU and caches, privileged/hypervisor functions, and multicore or SoC integration. Kunminghu uses Chisel/Scala; Heliodor uses Veryl. Bitloom can import a documented subset of FIRRTL, but explicitly does not parse Chisel Scala. No direct Veryl input path was found. [5][6][7][8][9]

Treat Bitloom as a **third, experimental implementation** for learning and comparison, not as a replacement source of the existing cores. First prove a representative vertical slice: RV64 integer pipeline and load/store behavior, 128-bit vector datapath, memory interface, generated Verilog, and differential simulation against a selected reference. Expand only if that slice is maintainable and passes compliance, equivalence, synthesis, and timing gates. Confidence: **medium**; no full-core Bitloom port was implemented or independently tested in this research.

## Findings

### Bitloom capabilities and maturity

The crate layout matters: `bitloom` is the CLI; designs use `bitloom-prelude`; `bitloom-sim` is a separate simulation dependency. The exact docs.rs package page and GitHub releases show version 1.2.4, released October 15, 2026. The README packaged in that release still said 1.2.2 as of October 14, and an unversioned docs.rs `bitloom/latest` page surfaced older 1.0.0 docs during verification. Use versioned crate pages and pin every dependency before starting. [1][2][10]

The documented design surface includes parameterized hardware widths, modules, state, memories, and CDC; the toolchain elaborates into a frozen representation and emits Verilog/FIRRTL. The simulation crate supports cycle ticks. A memory-init helper documents a 64-bit word-width ceiling; that alone says nothing about the supported width of all datapath signals or a full RAM/cache implementation. [2][3]

Bitloom's `.fir` import is useful for inspecting or simulating some Chisel-generated designs: run Chisel/firtool, import compatible FIRRTL into Bitloom, then emit or tick it. The project explicitly says it does not parse Chisel Scala source. Therefore this is not an automatic source rewrite, and compatibility with Kunminghu's actual FIRRTL constructs would need a pilot. [4]

Its public CPU tutorials are RV32I: a trimmed single-cycle core and a five-stage core with forwarding, load-use handling, and branch flush. The tutorials explicitly leave cache, MMU, Linux, dynamic branch prediction, full privileged support, and architectural test compliance out of scope. This is meaningful evidence for learning-scale CPUs, but does not establish the framework's readiness for either target. [5]

The project is active: GitHub showed 593 commits and release tags through 1.2.4, while the public repository showed one star and zero forks at access time. These are only ecosystem snapshots; they do not prove quality, bus factor, or support longevity. A notable gap is lack of independent RV64/RVA23 CPU-scale usage evidence. [1][5][10]

### Target-core migration scope

Kunminghu V2R2 documentation describes an RV64 core with RVV 1.0, MMU, L1/L2 caches, TileLink and partial CHI support, AIA/IMSIC, timers, and debug features. The upstream V3 branch README identifies its sources under `src/main/scala`, generates SystemVerilog, and runs Verilator-based emulation. It warns that V3 is evolving quickly and recommends V2 when stability is important. [6][7]

Heliodor's upstream README describes a Veryl-based, out-of-order RVA23 core with vector and hypervisor extensions, virtual memory, caches, peripherals, and 1–8-hart SMP; it reports ACT4, directed tests, Linux boots, and guest-Linux validation. The Veryl project's own article independently identifies Heliodor as a large real-scale design used to stress the Veryl compiler/simulator and describes its RVA23 validation. [8][9]

**Migration inference:** a complete rewrite means re-expressing the CPU RTL and bringing forward or replacing each design's build, simulation, compliance, and system-test paths. Even if Bitloom can express the logic, generated RTL quality and matching behavior are unverified. Kunminghu's FIRRTL may provide an import route for comparison, but not a Rust source translation; Heliodor would need a new design implementation or an independently built conversion path. [4][6][7][8]

### Cross-dimension insight

Bitloom's biggest advantage for this learning project is that it offers a third RTL authoring model plus a simulation/output path, which can support targeted comparisons. That advantage is strongest for shared blocks or deliberately reduced cores. At full size, both targets' existing ecosystems carry important verification and integration assets; translating only their RTL would lose much of the evidence that currently makes their behavior trustworthy.

## Recommendations

1. **Keep both upstream cores as the reference implementations.** Do not describe a Bitloom port as equivalent until each target's selected tests and traces are reproduced. Confidence: medium, because the recommendation follows from the documented feature gap and verification breadth, without a Bitloom scale experiment. [5][6][8][9]
2. **Run a bounded Bitloom pilot before any rewrite decision.** Pin the published CLI, prelude, and sim crates; implement one shared RV64I pipeline slice with 64-bit ALU/register state, branch and load/store behavior, then a 128-bit vector operation and synchronous memory. Generate Verilog, simulate cycle by cycle, and compare architectural outputs against one reference test set. The 128-bit/memory stage is needed because the Bitloom docs do not yet evidence those exact CPU needs as a validated end-to-end case. [2][3][5]
3. **Gate expansion on evidence:** compile/simulate cleanly; pass selected RV64 instruction tests; match traces on the same stimulus; show generated RTL can be synthesized and mapped to an acceptable timing/area target; establish a workable compliance and regression harness. Then add privileged/MMU/cache or OoO pieces one subsystem at a time. The sources do not support estimating full-rewrite effort or PPA yet. This conclusion remains unverified until the pilot is built and compared. [5][6][8]
4. **Use the Chisel FIRRTL importer only as an optional comparison tool.** First test whether the actual Kunminghu FIRRTL output falls within the documented Bitloom import subset. No equivalent Veryl importer was found in the reviewed public documentation. [4][7][8]

## Verification notes

The exact 1.2.4 registry page and official release tags agree; generic docs.rs entry points and the release README are stale relative to the Oct 15 release. The Chisel/FIRRTL contract is also visible in the published `bitloom-firrtl` docs. Heliodor's language and feature scope is independently described by the Veryl project. Kunminghu V2R2's broad feature scope is documented, while V3's exact scope remains version-sensitive. No independent evidence established full Bitloom CPU-scale readiness. [1][2][4][6][7][8][9][10]

## Open questions

- Does the current published Bitloom subset support the vector widths, operators, and synchronous memory semantics required by the selected CPU blocks?
- Can a representative Kunminghu FIRRTL output import successfully without losing hierarchy or unsupported memory/control constructs?
- What is the cost of reproducing ACT4, Linux, RVWMO, hypervisor, and SMP validation in Bitloom's generated design flow?
- What synthesis, area, and timing results does a Bitloom-generated representative slice achieve versus the existing RTL?
- Is there a public Veryl-to-Bitloom path beyond translating through an intermediate format? None was found in this source pass.

## Source appendix

| Ref | Supports | Publisher | Publication/update | Accessed | Confidence |
|---|---|---|---|---|---|
| [1] | Bitloom published CLI 1.2.4, crate identity, release listing | [docs.rs / crates.io](https://docs.rs/crate/bitloom/1.2.4) | Published 2026-10-15 | 2026-10-15 | High |
| [2] | Design-facing API types and crate boundary | [docs.rs / Bitloom](https://docs.rs/bitloom-prelude/latest/bitloom_prelude/) | Version 1.2.4 | 2026-10-15 | High |
| [3] | Memory-init word-width limit | [docs.rs / Bitloom](https://docs.rs/bitloom-builder/latest/bitloom_builder/) | Version 1.2.4 | 2026-10-15 | High |
| [4] | FIRRTL import path; no direct Chisel Scala parse | [TangCan/Bitloom](https://github.com/TangCan/bitloom/blob/main/docs/fr46-chisel-import.md) | Repository document; no date shown | 2026-10-15 | High for stated contract |
| [5] | RV32 tutorials and explicitly excluded features | [TangCan/Bitloom](https://github.com/TangCan/bitloom) | Repository README; accessed current main | 2026-10-15 | High for stated scope; medium for absence inference |
| [6] | Kunminghu V2R2 feature overview | [XiangShan User Guide](https://docs.xiangshan.cc/projects/user-guide/en/kunminghu-v3/introduction/) | Copyright 2024–2025; page date not stated | 2026-10-15 | High |
| [7] | Kunminghu source language, build/emulation path, V3 maturity warning | [OpenXiangShan/XiangShan](https://github.com/OpenXiangShan/XiangShan/tree/kunminghu-v3) | README last updated 2026-06-30 | 2026-10-15 | High |
| [8] | Heliodor architecture and validation description | [dalance/heliodor](https://github.com/dalance/heliodor) | Repository README; no stable update date shown | 2026-10-15 | High for stated scope |
| [9] | Independent Heliodor/Veryl scale and RVA23 account | [Veryl project](https://veryl-lang.org/blog/heliodor-rva23/) | 2026-06-24 | 2026-10-15 | High |
| [10] | Bitloom 1.2.4 release tags on same date | [TangCan/Bitloom releases](https://github.com/TangCan/bitloom/releases) | 2026-10-15 | 2026-10-15 | High |

## Staleness map

- Crate version and compatibility evidence: re-check by **2026-11-15** (≤1 month).
- Ecosystem activity: re-check by **2027-04-15** (≤6 months).
- Kunminghu / Heliodor architecture and implementation patterns: re-check by **2028-06-24** (≤2 years from the oldest cited target article).
- Earliest re-check: **2026-11-15**.
