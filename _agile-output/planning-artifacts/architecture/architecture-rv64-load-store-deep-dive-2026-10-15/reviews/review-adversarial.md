# Adversarial architecture review

**Verdict: revise before handoff.** The spine states the right high-level boundaries, but two one-level-down records can still obey its rules while disagreeing about evidence states and unit lifecycle. Those differences would make the three case records difficult to compare or maintain uniformly.

## Constructed divergence cases

### Case A: two records encode incomplete comparison differently

- A `LD` unit uses `status: unverified` for a missing Heliodor observation and adds prose `comparison: partial`.
- An `SD` unit uses `status: partial` for the same missing-side condition.

Both follow AD-3's statement that a missing side is `partial`/`unverified`, and both keep `type` separate. However, the existing learning-record convention permits status values `inspected`, `run-pass`, `run-fail`, `unverified`, and `not-applicable` (with PRD FR-6 additionally naming `blocked`); it does not define `partial` as a status. The two records therefore cannot be consumed or reviewed consistently. The spine should distinguish claim/comparison completeness from evidence validation status and name the authoritative allowed values (including how `blocked` is treated).

### Case B: two records resolve an existing unit differently

- The `LD` author edits `notes/units/load-v1.md` in place because PRD FR-3 says it may be “reviewed or cited.”
- The `SD` author creates a new immutable `<unit_id>-v1.md` and adds it to a unit index because AD-1 requires immutable versions and a current-version index.

Both are plausible readings of the documents, but the result violates the intended immutable-history rule for one record and leaves the other linked to an older version. AD-1 needs a single rule for revising existing records (new version, cite-only, or explicitly grandfathered exception), and the seed should name the index location it requires.

## Findings

### High

1. **AD-3 mixes evidence status with comparison completeness.** The `partial`/`unverified` shorthand has no field-level meaning, and `partial` is absent from the learning-record status vocabulary. Define separate fields or an explicit mapping so every unit represents a missing counterpart in the same way.

### Medium

2. **AD-1 does not settle reuse and revision of existing learning units.** The PRD permits review or reuse of `load-v1.md`, while the spine requires immutable versioned units and a current-version index. State whether existing records may be edited, whether a new version is mandatory, and where the authoritative unit index lives.

3. **Stable evidence ID uniqueness is underspecified.** AD-3 requires claim links to evidence IDs, while AD-5 places artifacts under case/run directories. Two records can independently choose the same unqualified ID (for example, `source-kh-ld`) for distinct artifacts, making links ambiguous. Specify that IDs are repository-wide unique or derive them from a stable path/namespace.

## Checks

- **Case tuple and endpoint:** The spine adequately requires each core to use its own source terminology and an evidence-supported endpoint. Deferring the concrete SD tuple/endpoint to its story is consistent with the PRD, provided that story records one common tuple and endpoint decision before analysis.
- **Ownership and organization:** The one-way model is useful, but the version index and evidence ID details above leave room for incompatible implementation choices.
- **Snapshot provenance:** AD-2 gives a clear baseline and change rule; no divergence issue found.
- **Isolation:** AD-6 clearly protects the completed RVA23 artifacts.
