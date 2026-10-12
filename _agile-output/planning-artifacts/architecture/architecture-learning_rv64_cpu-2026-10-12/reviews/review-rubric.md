# Independent Rubric Review — Architecture Spine

**Target:** `ARCHITECTURE-SPINE.md`  
**Lens:** BMAD good-spine checklist (independent rubric walker)  
**Date:** 2026-10-12

## Gate verdict

**Conditional pass.** The spine gives the learning artifacts useful evidence and comparison rules, covers the PRD's central learning capabilities, and fits a greenfield learning repository. The mechanical lint is clean. Before treating it as the architecture baseline, close the gaps in stage-level understanding checks and the operating/environmental envelope; clarify how RVA23 items with no implementation location are represented.

## Mechanical check

`uv run .agents/skills/bmad-architecture/scripts/lint_spine.py --workspace _agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12` returned `ok: true`, with zero findings.

## Findings

### Medium — Stage completion checks are not enforced by the record contract

**Evidence:** PRD FR-6 requires each stage record to answer that stage's self-check questions; FR-9 requires at least one explanation, source-location, or test/simulation check per stage. AD-1 defines a learning-unit record, while the capability map assigns stage checks to `README.md` and planning artifacts under AD-1/AD-3. Neither an AD nor a consistency convention requires a stage check, its prompt, or the learner's answer/evidence to be recorded. Thus two records could meet the stated template while the stage is marked complete without satisfying FR-6/FR-9.

**Disposition:** Autofix before handoff. Extend the record/route contract to require a stage identifier and self-check prompt plus answer and evidence/check type; keep stage-level roll-up in the route document. Make sure the PRD requirement remains traceable.

### Medium — Operational and environmental envelope is only partly deferred

**Evidence:** The spine defers checkout location and toolchain versions/commands. It does not decide or defer the host/OS or isolation assumptions, where toolchains and generated artifacts live, how environment setup is reproduced, or what operational evidence is retained when test execution is unavailable. These decisions affect whether the two source trees can be built and whether experiments can be repeated. At initiative altitude, a whole portion of the environment/operations dimension is silent.

**Disposition:** Defer explicitly to the source/environment stage, with an owner and decision trigger. Record the minimum environment facts needed for reproducibility (host/OS, toolchain versions and setup, commands, artifacts/results) and a fallback when execution cannot be performed. No need to prescribe a specific provider or host now.

### Low — RVA23 mapping rule does not cover the PRD's scope-decision path

**Evidence:** PRD FR-7 allows each mandatory requirement to map to an implementation **or an explicit scope decision**. AD-4 says to maintain a mapping for every mandatory item with an implementation location, while its rule for “unavailable evidence” only permits marking it unverified. For an item not provided by the chosen sources or outside the learner's intended scope, there may be no implementation location; the spine does not say how to record that distinction without implying coverage.

**Disposition:** Autofix by allowing each requirement row to record implementation location **or** an explicit scope/unavailability decision, with evidence status and rationale. Preserve the distinction between “not studied,” “unverified,” and “not in scope/not present.”

## Checklist assessment

- **Real divergence points for the level below:** Mostly covered. AD-1 and the conventions prevent incomparable notes; AD-2 anchors claims to source snapshots; AD-3 protects upstream sources; AD-4 addresses profile-coverage overclaiming. Stage completion checks are the notable omission (Medium finding).
- **Rules prevent their stated divergence:** AD-1 through AD-3 have concrete, enforceable rules. AD-4 is enforceable for ordinary mapped items, but its required implementation location does not cover the PRD's explicit scope-decision route (Low finding).
- **Deferred items cannot cause units to diverge:** The listed checkout-location and cadence decisions are appropriately deferred and do not weaken the stable per-record rules. The silent environment/operations choices may produce irreproducible or incomparable evidence (Medium finding).
- **Named technology is verified-current:** The spine names Markdown/GFM and Git 2.43.0 and does not rely on an unpinned runtime stack. Upstream versions are intentionally pinned per study unit. This is acceptable for a draft; verify actual toolchain versions when the environment stage runs.
- **Brownfield ratification:** The repository appears to be a planning/learning scaffold rather than an existing CPU implementation. The proposed record structure is consistent with that greenfield context; `sources/` is explicitly nonbinding.
- **Spec capability coverage:** All PRD FR-1 through FR-9 and SM-1 through SM-3 are listed in `binds` and addressed in the capability map. FR-6/FR-9 are only partially enforced by the record rules (Medium finding); FR-7's scope-decision case needs clarification (Low finding).
- **Inherited parent spine:** No parent spine is listed or present in the document metadata; no inherited decision was available to check.
- **Owned dimensions decided/deferred/open:** Learning records, source evidence, experiment isolation, and RVA23 coverage are decided. Checkout location, toolchain commands/versions, cadence, and publication/licensing are deferred. Environment and operations are only partly deferred (Medium finding).

## Other observations

- The seed tree and capability map are helpful and do not accidentally turn the proposed checkout location into an invariant.
- The source snapshot convention is strong. Consider including the exact specification edition/version in each record as it is cited, even though AD-2 currently names repository branch and commit explicitly.

## Summary

Resolve the two medium findings and clarify the RVA23 row model before finalizing the spine. No structural or lint issues block doing so.
