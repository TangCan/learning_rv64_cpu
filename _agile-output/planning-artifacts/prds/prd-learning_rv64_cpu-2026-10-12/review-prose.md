# Editorial prose review

Purpose and audience: these documents help Richard plan and carry out a paired RV64 CPU learning project; the PRD defines the requirements baseline and the epic breakdown turns it into learning tasks.

The concise, formal Chinese technical voice and use of `ready`, `adjust`, `defer`, and RISC-V terminology are intentional and should be preserved.

| Pass | Original Text | Revised Text | Changes |
| --- | --- | --- | --- |
| prose | PRD §4.3 distinguishes “stages 2–4”; other passages refer to Epics 2–4. The gate used “pause” and “defer” inconsistently, and `adjust` did not explicitly require a new `ready`. | Clarify that phases 2–4 correspond to candidate Epics 2–4; make `ready` name authorized epics, require a new `ready` after `adjust`, and define `defer` as pausing until a later review. | Removes ambiguity between phase and epic numbers and clarifies authorization after revisions. |
| prose | PRD FR-5, Epic List, and Story 1.3 used different descriptions of what `ready` authorizes; Story 1.3 used an English parenthetical. | Unify around `ready` confirming the method, named authorized epic subset, scope, and cadence. | Makes the gate's decision record consistent and prevents implied authorization for unnamed epics. |

Both recommendations were applied in the final wording.
