# Reality and evidence review

**Target:** `ARCHITECTURE-SPINE.md`
**Lens:** Check whether adopted technical and tooling decisions are grounded in repository reality or verifiable evidence, rather than assumed from general knowledge.
**Verdict:** Pass with one documentation consistency issue to reconcile before downstream stories treat the evidence vocabulary as normative.

## Findings

### Minor — Evidence status vocabulary differs across the architecture, plan, and base convention

The spine's AD-3 calls for separate `type` and `status`, and says missing sides are `partial`/`unverified`; it also allows `blocked`/`unverified` for unobserved stages in AD-4. The current plan's evidence rules include `blocked`, while the referenced base convention (`_agile-output/specs/spec-learning_rv64_cpu/learning-record-conventions.md`) lists `inspected`, `run-pass`, `run-fail`, `unverified`, and `not-applicable`, without `blocked` or `partial`. This is a concrete in-repository mismatch, not a concern about the underlying evidence model. Clarify whether `blocked` and `partial` are valid status values and update the convention or constrain the spine before stories copy the schema.

## Decision checks

- **AD-1, canonical technical owner:** Grounded in the existing repository: `notes/units/` contains versioned learning records and `learning-journal/index.md` explicitly says logs describe process while technical details and evidence remain in linked unit/evidence records. The rule is consistent with the stated learning workflow.
- **AD-2, locked source snapshots:** Grounded and verified. `sources.lock` records full commit SHAs for Kunminghu and Heliodor; both ignored source checkouts currently resolve to those exact SHAs and have clean detached checkouts. `.gitignore` excludes `/sources/`, consistent with the lock's role as provenance rather than committed upstream code.
- **AD-3, evidence typing and claim limits:** The separation of evidence kind from validation state is grounded in the repository convention and plan. Runtime evidence fields match that convention. The status-name mismatch is the sole issue above.
- **AD-4, compare architectural cases without equating pipelines:** Fits the dual-core objective in the Spec/PRD and avoids asserting implementation details without source evidence. The two locked checkouts and the feasibility/PRD artifacts provide the appropriate basis for later path tracing; no current claim about particular pipeline stages is asserted here.
- **AD-5, one-way ownership and journal index:** Grounded in the existing journal scaffold and learning-record convention. The current index distinguishes existing retrospective materials from posts still to be written and says historical process will not be invented. The prescribed Markdown layout matches the repository.
- **AD-6, follow-up isolation:** The Spec and PRD identify this as a separate post-closeout stage. Its distinct follow-up Spec/PRD/architecture paths exist; keeping the old RVA23 completion record untouched is consistent with that boundary.
- **Markdown/Git as storage and GitHub as reading surface:** Reality-checked against the actual repository: artifacts are Markdown, this is a Git working tree, and there is no generator, deployed service, runtime, provider, or infrastructure in the described feature. This is an accurate scope decision for the current artifact-only stage.
- **Deferred harness and SD case details:** These are correctly deferred by the PRD and feasibility work rather than presented as settled technical facts. No new toolchain or evolving external technology claim is embedded in the spine.

## Scope and evidence limits

This review checked the spine against the follow-up Spec and PRD, learning-journal plan/index, learning-record convention, `sources.lock`, `.gitignore`, and current locked checkout SHAs/status. It did not independently re-audit upstream RTL or execute CPU tests; the spine makes no new RTL behavior claim requiring that verification.
