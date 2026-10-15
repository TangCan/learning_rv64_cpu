# Spec-to-Architecture Reconciliation

**Inputs:**
- `_agile-output/specs/spec-rv64-load-store-deep-dive/SPEC.md`
- `_agile-output/planning-artifacts/architecture/architecture-rv64-load-store-deep-dive-2026-10-15/ARCHITECTURE-SPINE.md`

**Verdict: revise before downstream story planning.** The spine captures the broad artifact pipeline, locked-source provenance, evidence labeling, architectural equivalence, and separation from the completed RVA23 phase. It does not yet preserve several acceptance-level details and learning-journal requirements from the Spec/PRD. No contradictory implementation choice was found, but these omissions could let stories silently weaken scope.

## Findings

### 1. Journal content and historical reconstruction requirements are underspecified — Major

The Spec requires a navigable index that distinguishes completed history, current work, and planned topics; unpublished retrospectives must be marked pending, and historical detail not recoverable from retained material must not be invented. Each post needs date, question, sources/actions, findings with evidence type/status, links, and next step, with explicit `none`/`unknown`/`not applicable` rather than unexplained blanks (PRD FR-1/FR-2). The spine says posts are dated chronology, links to units/evidence, and planned entries are plain text, but does not bind the distinction among history/current/planned, the no-invention rule, or the required post fields.

**Risk:** Stories could implement a browsable index but publish reconstructed history as factual, or produce posts without enough context to resume learning.

**Reconciliation:** Add these as journal conventions or an AD bound to FR-1/FR-2; explicitly state that historical posts are evidence-based retrospective summaries and unresolved historical details remain unknown/pending.

### 2. LD's required common case tuple is not preserved — Major

The PRD FR-3 requires both implementations to use the same tuple: RV64I `LD`, naturally aligned 8-byte access, M-mode Bare, no exception, DCache hit, and no older overlapping store. Unknown configuration/runtime premises must be labeled assumptions. The spine's “same architectural case tuple” rule and generic case-boundary convention do not enumerate these acceptance conditions.

**Risk:** The two LD paths may be documented for materially different translation/cache/store-order conditions while appearing comparable.

**Reconciliation:** Bind the tuple explicitly in the spine or retain a direct pointer to FR-3 as the normative case definition; require unsupported premises to remain assumptions, never runtime observations.

### 3. Fault case and required architectural state are reduced to a generic Sv39 fault — Major

The PRD FR-5 fixes S-mode, V=0, Sv39, ordinary RV64I `LD`, VA `0x0000008000000000`, and `medeleg[13]=0`, and requires tracing fault detection, exception retention, cause 13, fault PC/`mepc`, `mtval`, M-mode trap target, and related state updates. It also requires unknown `mtval` implementation choices to stay unknown. The spine names the Sv39 fault family and says to compare endpoints, but does not retain this tuple or the named state obligations.

**Risk:** A story could choose another fault input, omit delegation/trap state, or report “page fault” without tracing the requested precise-exception boundary.

**Reconciliation:** Record the fixed tuple and required state fields, while keeping any implementation-specific `mtval` representation unknown unless supported by evidence.

### 4. SD write endpoint boundary is not fully explicit — Moderate

The spine appropriately defers the exact SD tuple and endpoint to the SD story. However, the PRD requires separating instruction commit, cache/buffer acceptance, and lower-level visibility, and explicitly forbids inferring DRAM persistence/visibility without evidence. The spine defers the endpoint and says exact configuration is deferred, but does not state that commit is not automatically visibility or that DRAM persistence must not be inferred.

**Risk:** Story completion might treat ROB/StoreQueue commit as proof of a cache/DRAM write.

**Reconciliation:** Add the non-inference rule to AD-4 or case-boundary conventions; require the story to record its evidence-supported acceptance endpoint and mark any lower-level visibility unknown absent evidence.

### 5. Comparison evidence must be bilateral, with partial status — Minor

AD-3 says a missing side is `partial`/`unverified`, and the capability map references comparison evidence. This substantially preserves the Spec/PRD rule that each comparative conclusion must link both sides or explicitly identify missing evidence. The wording “a missing side is `partial`/`unverified`” could be made more precise because these are claim-level states, while `partial` is not included in the shared validation-state enum.

**Risk:** `partial` may be entered as a `status` despite not being an allowed status, or evidence rows may be marked partial instead of the comparison claim.

**Reconciliation:** State that `partial` describes comparison coverage/claim completeness (not evidence-row status); use `unverified` as the status field where required by the conventions.

## Preserved without material conflict

- Independent follow-up scope and protection of completed RVA23 artifacts (Spec constraints/Open Question; AD-6).
- Locked snapshot IDs/full SHA, revalidation after baseline changes, and no cross-version evidence mixing (Spec constraints; AD-2).
- Evidence type separate from validation status, with runtime claims tied to exact inputs/commands/configuration/output/artifact location (Spec constraints and PRD FR-6; AD-3).
- Different microarchitectural stage names and evidence-supported endpoints rather than forced phase alignment (Spec CAP-1/constraints; AD-4).
- Static source-path completion is allowed; runtime is optional, and a trace harness is deferred pending story feasibility/scope change (Spec Open Questions; Deferred).
- Markdown/GitHub surface and no deployed blog runtime (PRD non-goals; Environment and Operations).
- Stable technical-unit ownership and journal links rather than duplicated explanations (PRD vision/FR-2; AD-1/AD-5).

## Quiet additions to confirm downstream

The spine introduces immutable published unit versions, `notes/units/index.md`, and a dated baseline-change record. These are consistent with the existing learning-record conventions (immutable versioned units and index) and source-lock convention (dated change record), so they do not conflict with the Spec. Ensure stories reuse the existing conventions rather than create a second versioning or snapshot-change mechanism.

## Open question coverage

The Spec's unresolved harness question is appropriately preserved as deferred; the spine correctly does not decide to build a harness. The second Spec question—protecting follow-up planning outputs from overwriting the original completion artifacts—is converted into AD-6. The Spec's representative-case selection assumption is mostly preserved: SD tuple/endpoint are deferred; LD and fault tuples should remain fixed rather than be reopened as story choices.
