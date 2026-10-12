# Adversarial review — Architecture Spine

**Artifact:** `ARCHITECTURE-SPINE.md`  
**Review mode:** Constructive adversarial test of downstream consistency  
**Verdict:** Revise before treating the spine as a reusable template contract.

## Summary

The spine states useful principles, but most are outcome-oriented and leave the record format and evidence semantics unconstrained. Two contributors can follow every AD and still produce records that cannot be compared consistently or aggregated into the RVA23 map. The central gap is that AD-1 names required *content*, not a canonical schema; AD-2 and AD-4 require evidence and status labels without defining their meaning, scope, or linkage to claims.

## Adversarial pair

### Unit A: `ADD` (RV64I integer arithmetic)

A learner creates `notes/units/ADD.md`, pins one Kunminghu V2 SHA and one Heliodor SHA, cites the unprivileged ISA operation, and traces decode → execute → writeback. The note has sections called “范围”, “规范行为”, “香山路径”, “Heliodor 路径”, “证据”, “比较”, “总结”, and “问题”. In its evidence section, it lists a decoder unit test as “inspected” and an arithmetic test as “run”, with observed pass output. It records an integer arithmetic difference supported by source links.

This meets AD-1 through AD-3. AD-4 is met by separately marking the ADD-related profile row as mapped/not studied or not applicable, while preserving the full mapping elsewhere.

### Unit B: `Vector load` (RVV vector memory operations)

A second learner creates `notes/units/vector-load.md`, pins both repository SHAs, cites the vector ISA chapter and relevant RVA23 rows, and traces vector decode → LSU request → response/writeback. It scopes the unit to unit-stride loads across supported element widths, masks, and tail behavior, explicitly listing those subcases. It uses the same required prose content, but organizes evidence as a matrix by element width and mask mode. It lists a directed test as “inspected”, a simulator run as “run”, and a configuration where evidence is unavailable as “unverified”. It supports a design-difference conclusion with RTL and test references.

This also meets AD-1 through AD-3. Its RVA23 mapping can meet AD-4 by listing the vector requirements, implementation locations, and the three locally chosen status labels.

### Incompatibility despite compliance

Both records contain all the named AD-1 sections in substance, yet ADD has one architectural operation and a few test artifacts while vector load has a subcase matrix. There is no required canonical table or field model, so a reader cannot reliably compare “evidence” or determine whether a conclusion is supported by equivalent evidence. The spine permits “run” to mean a smoke test, a directed test, or a full architectural test; it also does not require command, configuration, input, expected result, observed result, or a link from a particular claim to the evidence that supports it. A future summary or RVA23 coverage report cannot aggregate these records mechanically or even consistently by hand.

The source snapshots can also drift silently between units. AD-2 asks each note for a branch and SHA, but does not define a project baseline or require the two units to use the same snapshot pair. The ADD comparison could use Kunminghu `K1`/Heliodor `H1`, while vector load uses `K2`/`H2`; both satisfy AD-2, but apparent differences across notes may come from source changes rather than feature differences. The spine does not require that this change be disclosed as a comparability break.

Finally, AD-4 says to map every mandatory `RVA23U64` and `RVA23S64` requirement, but does not specify stable requirement identifiers, one-row-per-requirement cardinality, or whether the status applies independently to each implementation. A learner can mark one combined “vector support” row as mapped and report “verified” based on one load test. Another can split each requirement and mark status separately for Kunminghu and Heliodor. Both can claim to have a mapping, but their coverage cannot be reconciled and the first overstates what its evidence establishes.

## Concrete holes and enforceable rule changes

1. **AD-1 — Define a canonical record schema and unit boundary.** Require a checked-in template with mandatory headings and a small frontmatter schema: stable `unit_id`; exact scope and exclusions; architectural operation/subcases; spec references; source snapshot IDs; implementation paths; comparison claims; learner summary; open questions. Require subcases to be enumerated when a unit covers parameterized behavior (such as element widths, masks, exceptions, or privilege modes). A record is not conformant merely because required topics appear somewhere in prose.

2. **AD-2 — Normalize evidence and make claims traceable.** Require an evidence table with stable IDs and fields: claim ID(s) supported, evidence kind (`spec`, `design-doc`, `source`, `test-inspected`, `test-run`, `experiment`), repository/snapshot, path or artifact, exact command and configuration when run, input/case, expected result, observed result, and a controlled status (`inspected`, `run-pass`, `run-fail`, `unverified`, `not-applicable`). Define that `run-pass` requires recorded observed output and that inspection never implies execution. Each comparison claim must cite at least one evidence ID per side when it makes a two-implementation assertion.

3. **AD-2 — Establish snapshot comparability.** Add a project-level lock file assigning stable IDs to the current Kunminghu and Heliodor snapshots. Each unit must reference those IDs, or declare an intentional deviation with reason and mark cross-unit comparisons as not directly comparable. Update the lock only through a documented snapshot-change event so a SHA change does not silently alter the basis of later notes.

4. **AD-4 — Specify requirement-map shape and per-implementation status.** Require one row per official mandatory requirement, keyed by the exact stable identifier and specification revision, with separate Kunminghu and Heliodor implementation location and evidence-status fields. Use a controlled status vocabulary (for example `mapped-unverified`, `source-inspected`, `test-run-pass`, `test-run-fail`, `unsupported`, `not-studied`) and disallow promoting a requirement to passed based only on a nearby feature test. Every status above `mapped-unverified` must link to evidence IDs whose scope actually covers that requirement.

5. **AD-1 / AD-4 — Define comparison criteria for asymmetric coverage.** Require each unit to state whether both implementations cover the same architectural subcases. Where support or available evidence differs, mark the comparison partial and list unmatched subcases rather than presenting a single unqualified “difference”. This matters especially for vector operations and privilege/virtualization behavior, where configurations and subcases affect what an observed result proves.

## Acceptance checks for a revised spine

- A new learner can create both adversarial records from one template without inventing headings, status meanings, or evidence-table columns.
- A reviewer can identify which exact claims are supported by source inspection versus executed tests, and reproduce a run from the record.
- A report can determine whether two units use the same source baseline and whether each mandatory RVA23 requirement has evidence for each implementation.
- A partial subcase comparison cannot be represented as complete coverage without an explicit exception.
