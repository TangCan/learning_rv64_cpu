# PRD–Architecture Reconciliation

Date: 2026-10-15
Inputs: `../../prds/prd-rv64-load-store-deep-dive-2026-10-15/prd.md` and `../ARCHITECTURE-SPINE.md`

## Verdict

**Pass with downstream carry-through conditions.** The spine preserves the PRD's central architecture: a separate follow-up learning stage, fixed dual-core snapshots, evidence-bounded architectural-case comparisons, separate ownership for process and technical knowledge, and Markdown/Git as the delivery surface. No direct contradiction was found. The architecture intentionally compresses several acceptance details; story planning must carry the listed PRD details through explicitly rather than treating the spine as a replacement for the PRD.

## Reconciliation

| PRD requirement / boundary | Spine coverage | Finding |
| --- | --- | --- |
| Independent stage after the completed RVA23 stage; do not alter its epic or sprint record (PRD §0, FR-1, SM-2) | AD-6 and structural paths | Preserved. Keep downstream story and sprint outputs in this follow-up workspace too. |
| Chinese, chronological posts explain question, actions, findings, evidence, next step; unknown historical detail must not be invented (FR-1, FR-2) | AD-1/AD-5; conventions specify Chinese/date pattern and links | Partial at architecture altitude. The required post fields and historical-reconstruction caveat are not repeated. Story acceptance criteria must retain all fields and label retrospective/unknown material. |
| Index must distinguish completed history, current work, and planned topics; published links resolve; planned items are plain text (FR-1) | AD-5 and convention that index only links existing posts | Link integrity is preserved, but the three index categories are implicit. Carry the categories and README → index link check into FR-1 story acceptance. |
| Technical conclusions have one canonical owner; published unit versions immutable; index points to current version (FR-2, existing `load-v1.md`) | AD-1 | Preserved and made more precise. Review/reuse `load-v1.md` without editing a published version in place; if changed, publish a new version and update the index. |
| Successful `LD`: RV64I, aligned 8-byte access, M-mode Bare, no exception, DCache hit, no older overlapping store; follow decode/issue through retirement and state assumptions (FR-3) | AD-2/AD-4 and case-boundary convention | Architectural tuple and source-specific endpoint policy preserved generally, but the exact `LD` tuple and the required decode/issue, writeback, retirement milestones are omitted. Include them verbatim in the story. Runtime/configuration uncertainty remains an assumption; locked source inability must yield blocked/unknown, not a fabricated path. |
| `SD`: natural aligned RV64I store to ordinary DRAM; choose a shared exact tuple and evidence-supported write-acceptance endpoint; distinguish retirement, cache/buffer acceptance, and lower visibility (FR-4, open question 1) | AD-4 plus Deferred | Preserved, deliberately unresolved. Story must establish the shared tuple and endpoint in both story and decision log before concluding. Do not claim DRAM persistence/visibility without evidence; do not mix MMIO, misaligned, or atomic behavior. |
| Shared fault: S-mode, V=0, Sv39, ordinary LD, noncanonical VA `0x0000008000000000`, `medeleg[13]=0`; record cause/trap state and unknown `mtval` details (FR-5) | AD-2/AD-4 and case-boundary convention | Only generic fault tuple is present. Story must preserve exact parameters, source-backed `mcause=13`, `mepc`/fault PC, `mtval`, M-mode target, relevant state updates, and unknown implementation-specific details. Static and dynamic evidence must remain distinct. |
| Evidence type and validation status are independent; permitted values; claims bounded by evidence; runtime evidence includes input, command, config, output, artifact path (FR-6) | AD-3 | Preserved substantially, with a small schema omission: `partial` is used for a claim lacking one side but is not listed as an evidence status, correctly avoiding conflation. The unit/claim representation should explain that `partial` qualifies comparison coverage while `type` and `status` remain separate. Retain all exact allowed values and runtime metadata fields. |
| Both cores need evidence for each comparison; missing side means partial/unverified; test source does not prove execution; no unsupported generalization (FR-6) | AD-3 | Preserved. Ensure individual rows/claims identify evidence IDs and core/source side, not just a single aggregate status. |
| Only `sources.lock` IDs/full SHA count; mismatch blocks acceptance; alternate versions only background; recheck before completion (FR-7) | AD-2 | Preserved. Dated baseline-change record and impact recheck are useful additions consistent with provenance requirements. |
| No upstream RTL changes, full RVA23/conformance claim, exhaustive scope, mandatory runtime, deployed blog, or new trace harness by default (Non-goals, assumptions) | Design paradigm, Environment and Operations, Deferred | Preserved. The explicit non-goal list is omitted but the spine does not authorize any excluded work. Keep optional runtime and no-harness default in stories; harness remains a separately assessed scope change. |
| MVP consists of index, three records, trace matrix, and separation of process/explanation/raw evidence; success includes path rows for each core from requested start to selected endpoint (MVP, SM-1/SM-2) | Capability map and structural seed | Main artifacts appear, but the trace matrix is not explicitly located in the structural seed/map and the exact SM-1 row completeness criterion is absent. Add the existing `trace-matrix.md` path and make the three cases × two cores, start-to-selected-endpoint evidence/unknown requirement explicit in stories. |
| Existing evidence and history should be reviewed; no fabricated past process | Inputs/structural shape do not mention feasibility report or learning plan directly; FR-1 responsibilities not in spine | Not a contradiction. Downstream planning should use the PRD and companion conventions, preserve prior six-stage history as evidence-led retrospective, and not create fabricated old posts. |
| Independent learner; no multi-role approval/operational deployment requirement; GitHub Markdown reading sufficient (assumptions) | Environment and Operations | Preserved; no runtime/provider/infrastructure is introduced. |

## Required carry-through in story planning

1. Treat the PRD as the acceptance source; the spine defines shared architecture constraints and does not reduce PRD success criteria.
2. Write one story or clearly bounded acceptance set for each case (`LD`, `SD`, fault), preserving the exact tuples and required milestone/state fields above.
3. Preserve the learning journal post template, index categories, link checks, and historical reconstruction caveat.
4. Include the trace matrix and assert six case/core path rows with explicit start, evidence-supported endpoint, evidence references, or `unknown`/`blocked`.
5. Keep `partial` as comparison coverage metadata, separate from evidence `type` and `status`; identify which core each evidence record supports.
6. In the SD story, record its chosen common tuple and write-acceptance endpoint in both the story and decision log before drawing conclusions.
7. Keep all new planning/status files within the isolated follow-up artifact path; do not modify the completed RVA23 sprint or epic.

No spine edit is necessary for this reconciliation. These are precision requirements for downstream story acceptance, not conflicts in the shared architecture decisions.
