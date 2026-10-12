# Adversarial Review — Final Architecture Spine

**Verdict: Conditional pass.** The spine supports two ordinary instruction units without a direct contradiction, but leaves a contract ambiguity around where stage-level self-checks live and how one canonical topic file handles repeated or version-specific units. Clarify these before generating templates/stories.

## Compliance attack: two units

I instantiated the contract twice, without adding implementation-specific assumptions.

### Unit A: `ADD` (stage 1)

- Frontmatter: `unit_id: ADD`, `stage_id: 1`, scope = integer register-register addition, exclusions = compressed encoding and RV32, spec refs = unprivileged ISA, source IDs = pinned Kunminghu and Heliodor snapshots.
- Required sections in order: stage self-check; architectural behavior and enumerated cases; Kunminghu path; Heliodor path; comparison claims; evidence table; learner summary; open questions.
- Evidence rows separately identify spec behavior, source inspection, and relevant tests. Comparison claim links to evidence IDs for both implementations. An unrun test is `unverified`.
- Stage self-check includes prompt, learner answer, check type, and evidence ID.

This is representable under AD-1/2/4. It can cite the RVA23 requirement separately from its ISA behavior, avoiding a false claim that one `ADD` test proves profile coverage.

### Unit B: `BEQ` (stage 1)

- Frontmatter: `unit_id: BEQ`, `stage_id: 1`, scope = conditional branch decision and redirect, exclusions = prediction accuracy and other branch forms, same pinned source IDs, relevant spec refs.
- It uses the same ordered sections and independent evidence IDs. Its comparison describes the architectural redirect and separately traces each implementation's prediction/redirect/recovery path.
- Stage self-check includes its answer and evidence, with any not-yet-covered behavior named.

This is also representable. AD-1's explicit subcase and omission requirements prevent an apparently complete `BEQ` note from silently omitting cases; AD-2 prevents source-inspection evidence from being presented as a run.

## Findings

### 1. Stage-check ownership is ambiguous (medium)

AD-1 requires a full “stage self-check (prompt, learner answer, check type and evidence ID)” in **every learning-unit record**. Yet the consistency table says stage completion is met when the “route record” contains answers to every self-check. The PRD says each stage has self-check questions and retained answers, without saying whether the answer is in every unit, a single route record, or both. For `ADD` and `BEQ`, this permits either duplicated stage answers in each note or a separate stage-level record; both could satisfy the prose, so later template/story authors can make incompatible choices.

**Resolution:** choose one canonical owner. Recommended: each unit carries only the self-check(s) for that unit; a stage route record indexes unit answers and records stage completion. Say explicitly that the index does not replace unit-level answers. Alternatively, move all stage checks to the route record and remove them from AD-1's required per-unit section list.

### 2. Unit identity and file naming conflict for revisions or multiple units per topic (medium)

AD-1 says one record per learning unit and requires `unit_id`; the seed says one file per topic and the convention gives stable feature names such as `ADD.md`. The PRD expressly allows route changes and later additions. If an `ADD` pilot is revisited against a new snapshot, or a later unit narrows scope to a particular `ADD` subcase, “one file per topic” points to the same path while “one record per unit” implies separate records. AD-2 allows a deliberate snapshot deviation but does not say whether that creates a new unit, a new version of the old unit, or an edit that invalidates its historical conclusions.

**Resolution:** define whether a unit is mutable/current or immutable/versioned. For a current-note model, require a dated change log and preserve old snapshot-specific claims. For an immutable model, include the unit ID/version in the filename, e.g. `ADD-v1.md`, and let an index identify the current record. This is a convention decision, not a reason to block the learning plan.

### 3. RVA23 mapping status has a narrow-but-resolvable interpretation (low)

AD-4's status list permits “not-studied,” “partially-studied,” “studied-unverified,” “evidence-observed,” “not-present,” and “out-of-scope.” A requirement with no evidence because a repository cannot be accessed could be labeled either `not-studied` or `out-of-scope`; rationale is required, but the distinction is not defined. That can yield inconsistent coverage summaries. The per-project status requirement is valuable and the explicit scope/unavailability decision handles the case semantically.

**Resolution:** define `not-studied` as in intended project scope but not yet investigated; reserve `out-of-scope` for an explicit learner decision with rationale; use `not-present` only when inspected evidence supports absence. “Evidence-observed” should remain explicitly non-certifying as currently written.

## Compatibility result

No hard contradiction was found between the central invariants and the PRD in the two instantiated units. The spine correctly separates inspection from execution, requires two-sided evidence for comparison claims, and makes RVA23 mapping independent from implementation claims. The remaining issues concern record ownership/lifecycle and a status definition; they should be resolved before the canonical template and record-index structure are authored.
