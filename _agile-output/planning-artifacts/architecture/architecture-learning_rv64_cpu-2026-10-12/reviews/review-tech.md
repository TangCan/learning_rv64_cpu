# Technical validity review

Reviewed: 2026-10-12  
Target: `ARCHITECTURE-SPINE.md`  
Verdict: **technically sound as a learning architecture draft; upstream references and the source pinning rule are appropriate.** No blocking defect found. The main caveat is to keep profile requirements separate from implementation and compliance claims, and record that upstream branch tips move.

## Findings

### 1. Kunminghu V2 is the appropriate XiangShan study line

**Status: Confirmed, with naming precision recommended.** The XiangShan repository's current branch-maintenance table lists `kunminghu-v2` as maintained, and explicitly recommends prioritizing it for research, verification, or downstream use over rapidly evolving V3. Direct `git ls-remote` inspection on the review date found `kunminghu-v2` at `c098f996bf4d301b88693b20315486d31e93bc9d`. The official user guide identifies the documented implementation as **Kunminghu V2R2** and says V2's goal is to refine functionality against the RVA23 profile and server SoC spec. For notes, use “Kunminghu V2 (V2R2 documentation/configuration)” to distinguish the branch/family name from the documentation's release designation.

Sources: [XiangShan repository and branch status](https://github.com/OpenXiangShan/XiangShan) (last updated 2026-06-30 per repository page); [Kunminghu V2 user guide](https://docs.xiangshan.cc/projects/user-guide/en/kunminghu-v2/introduction/).

### 2. Heliodor's default branch and language description

**Status: Confirmed.** GitHub identifies `master` as Heliodor's default branch. `git ls-remote` found its current tip at `94e9c5821c24a8941c3ddc3b76daddc7124a855a`. The upstream README describes Heliodor as an RV64 application-processor core written in Veryl and self-reports complete RVA23-profile implementation, ACT4 compliance results, and Linux boot results. The spine correctly treats the source as a moving default branch and requires per-unit SHA pins. Preserve the distinction between upstream's claims/results and what this learning project has independently inspected or run; AD-2 and AD-4 already require that distinction.

Source: [Heliodor repository README](https://github.com/dalance/heliodor).

### 3. Architecture implementation languages are useful context, not adopted project tooling

**Status: Confirmed; no stack change required.** XiangShan's primary source tree is Scala/Chisel (repository tree documents `src/main/scala` and generation of SystemVerilog RTL); Heliodor's source is Veryl. These are the languages learners will encounter when tracing implementation. They are **upstream implementation languages**, not a requirement that this notes-and-experiments repository adopt either language or install both toolchains up front. The spine's decision to defer toolchain versions and commands until a concrete source snapshot and experiment are selected is sound. A later onboarding note should explain the contrast and identify when each toolchain is needed.

Sources: [XiangShan repository structure/build guidance](https://github.com/OpenXiangShan/XiangShan); [Heliodor README](https://github.com/dalance/heliodor).

### 4. RVA23 coverage mapping is correctly framed, but should be treated as a profile matrix

**Status: Confirmed, scope caveat.** The current RISC-V profile specification defines both `RVA23U64` and `RVA23S64`; S64 incorporates the mandatory U64 user-mode extensions and adds supervisor requirements. Therefore the spine's requirement to map mandatory items from both profiles is valid. The mapping must include more than instruction mnemonics: profile-defined memory-model/PMA properties and privileged behavior also matter. Keep mandatory, localized/development/expansion options, and project-reported support in distinct statuses. An upstream's “complete RVA23” wording or a subset of compliance tests is not, by itself, proof of every profile requirement. The current rule already calls for a specification reference, implementation path, and evidence status, so this is an execution note rather than a defect.

Source: [RISC-V RVA23 Profiles, v1.0](https://docs.riscv.org/reference/rva23/rva23-profiles.html).

### 5. Versions and snapshot policy

**Status: Sound.** `Markdown / GitHub Flavored Markdown — No runtime version` is a format convention, not a runtime dependency. `Git 2.43.0` matches `git --version` in the current planning environment; labeling it as an environment observation rather than a project-wide minimum is correct. The branch names in the stack are moving references, but AD-2 explicitly says to save the full commit SHA per learning unit and never use a moving branch as the only locator. The observed branch tips above are review-time evidence only and should not be mistaken for permanently adopted pins.

## Overall assessment

The technical choices are current and internally consistent for a comparative study: use the maintained Kunminghu V2 branch and Heliodor's default branch, cite the profile specification, and pin exact source commits in each record. The architecture spine need not be edited based on this review. When the project creates source checkout/tooling instructions, use branch-tip checksums as dated observations and identify Scala/Chisel versus Veryl as upstream languages; select and pin actual tool versions only for a reproducible build or test exercise.
