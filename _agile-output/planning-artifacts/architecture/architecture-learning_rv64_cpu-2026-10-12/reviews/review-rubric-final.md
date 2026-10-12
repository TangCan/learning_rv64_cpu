# Final Architecture Spine Rubric Review

**Verdict: Conditional pass; the spine is strong and ready for downstream planning after two small consistency fixes.** It names the learning paradigm, defines enforceable evidence and comparison records, accounts for the complete mandatory RVA23 mapping, and explicitly defers the host/toolchain/operations choices. It aligns closely with PRD FR-1 through FR-9 and SM-1 through SM-3.

## Checklist findings

### 1. Does the spine fix real divergence points at this altitude?

**Pass.** Independent learning units could otherwise choose inconsistent evidence standards, source revisions, experiment boundaries, or coverage claims. AD-1 through AD-4 establish common contracts at the initiative level while leaving exact unit content to the learning records.

### 2. Is each AD rule enforceable and does it prevent its stated divergence?

**Pass, with one wording edge.** AD-1 has required frontmatter, section order, subcase accounting, and evidence-backed stage self-checks. AD-2 distinguishes source inspection from execution and provides concrete run evidence fields. AD-3 prevents upstream edits and isolates learner experiments. AD-4 establishes a row for every mandatory profile requirement and requires explicit rationale/status and evidence for each implementation.

AD-4's `out-of-scope` status should always require an explicit scope decision and rationale, as the rule already says; its status vocabulary alone does not encode that constraint. Treating the accompanying implementation-location-or-decision and rationale fields as mandatory makes it enforceable. The language is adequate, but a template should make these fields required.

### 3. Could Deferred allow two units to diverge?

**Pass.** The only outstanding decisions are repository checkout location, actual host/resources and operations, toolchain/test invocations, pacing and later topic selection, and external publication/license review. The snapshot lock and evidence rules apply regardless of checkout placement. Host and execution details are explicitly assigned to the environment stage rather than left silent.

### 4. Are named technologies verified-current?

**Minor issue.** Markdown/GFM is a format choice rather than a versioned runtime. Git 2.43.0 is described as the version in the planning environment, not as a required project baseline, so it need not be upgraded. Consider labeling it `Observed Git version (planning host)` to avoid downstream readers interpreting it as a selected minimum. Kunminghu and Heliodor are intentionally pinned by exact commit in the project lock, so moving upstream branch names are not the only evidence locator.

### 5. Does it ratify the existing codebase?

**Not applicable / pass.** This is a new learning repository; the two upstream projects are subjects of study, not the repository's own brownfield implementation. The proposed `sources/` checkout tree is expressly seed and is deferred pending size and disk review.

### 6. Does it cover the driving PRD?

**Pass.** The capability map binds all nine FRs and three SMs. The record contract supports FR-1 to FR-5 and FR-8; route and stage completion conventions support FR-6/FR-9; AD-4 maps every mandatory RVA23U64 and RVA23S64 requirement per implementation, covering FR-7 and SM-3. Explicit `not-studied`/partial/unverified/absent/out-of-scope states prevent coverage overclaim. The MVP ADD pilot is compatible with the unit contract.

One alignment issue should be corrected: AD-2 says the snapshot lock assigns stable IDs to selected source commits, while the Stack row says to “pin commit per study unit” for Heliodor. The latter could be read as allowing a different Heliodor SHA in every unit without changing the shared lock. Make the Stack row say the Heliodor commit is pinned in the shared lock and referenced by each unit; deviations follow AD-2. This matches PRD FR-1 and keeps comparisons reproducible.

### 7. Are inherited invariants weakened or contradicted?

**Not applicable.** There is no parent architecture spine.

### 8. Are all owned dimensions decided, deferred, or open?

**Pass.** The evidence and record model, comparison boundary, source versioning, experiments, documentation language, stage completion, and RVA23 coverage are decided. Checkout/storage, host environment and operations, toolchain specifics, pace, and release are explicitly deferred. That is appropriate for a learning-notes repository and avoids inventing a deployment architecture.

## Recommended disposition

Apply the small Heliodor shared-lock wording correction and optionally clarify the Git row as an observed environment fact. No substantive architecture decision is missing. AD-4's required rationale/decision fields should be reflected in the eventual coverage-table template.
