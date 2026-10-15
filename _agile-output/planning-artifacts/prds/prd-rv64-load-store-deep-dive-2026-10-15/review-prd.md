# PRD Review — RV64 双核访存微架构学习与日志

## Re-review delta — revised PRD

**Verdict: Pass for architecture and story planning; no remaining blocker among the five reviewed findings.** The revision binds the `LD` scenario, requires the `SD` story to record its shared scenario and evidence-supported endpoint, fixes the fault address and required trap fields, limits counted source evidence to `sources.lock` SHAs, separates evidence type from validation status, defines required journal fields and link checks, and makes a new trace harness a separately approved scope change.

One small implementation note remains: use the PRD’s two-field evidence model consistently when updating learning records; the linked learning plan still describes labels compactly as one list. The existing learning-record convention already defines type and status separately, so this is a reconciliation note, not a planning blocker. Existing test harness use is not prohibited; only new isolated trace infrastructure is out of scope absent a scope change.

The initial-review findings below describe the earlier revision and are retained as audit history. For current triage, this delta supersedes their original disposition.

- **Reviewed artifact:** `prd.md`
- **Review scope:** PRD rubric (7 dimensions), adversarial, edge-case, structure, and prose lenses. Verification-gap was not run because this is a document, not code.
- **Audience/purpose read:** This document helps an independent learner plan and record a source-grounded comparison of load/store/fault paths in two fixed RV64 CPU snapshots.
- **Size:** 2,653 words. No target length was provided.

## Gate verdict

**Conditional pass for follow-up architecture/story planning; revise before treating the PRD as a complete, implementation-ready acceptance contract.** The thesis and scope are coherent, the evidence boundary is unusually explicit, and the seven FRs have observable outcomes. The main risk is that “successful case,” “actual write path,” and “every observable stage” still leave enough discretion that separate stories could produce incomparable or differently bounded results. The snapshot-mismatch rule also weakens the stated fixed-snapshot constraint.

## PRD Quality Review

### Overall verdict

This is a coherent, appropriately bounded learning-stage PRD: it connects the chronological journal to durable knowledge units, fixes the two source snapshots, and explicitly rejects an RVA23 conformance claim. It is usable for planning, but not yet a precise acceptance contract for the three technical cases: case preconditions and completion boundaries remain open, and the status vocabulary combines evidence type, outcome, and workflow state. Resolve those points in the PRD or make the story-level decisions explicit and binding before implementation.

### Decision-readiness — adequate

The central choice is clear: a Markdown learning journal plus source-grounded technical units, with static traceability sufficient for completion (§§1, 5, 6). The trade-off against a deployed blog and mandatory runtime tracing is stated. The unresolved `SD` input/configuration and visibility boundary (§8, item 1) can reasonably be settled during story feasibility work, but the PRD should say which resulting boundary counts as completion so that it does not become a scope change by accident.

#### Findings

- **[medium] Freeze the `SD` completion boundary (§§4.2 FR-4, 8 item 1)** — The PRD requires a path “到实际写入通路” and distinguishes lower-layer visibility, but defers the exact address/configuration and success boundary. *Fix:* require the story to name an observable endpoint and scenario preconditions, then record that decision as the acceptance boundary for FR-4 (for example, the earliest evidenced accepted write and any later visibility that can actually be established). Do not imply DRAM persistence if the evidence only reaches a cache/buffer.
- **[low] Clarify the effect of the optional runtime-trace question (§8 item 2)** — It says a future trace request triggers a separate decision evaluation, but does not say whether that would change this PRD’s completion status. *Fix:* state that it is a future scope change and does not reopen the current stage unless separately approved.

### Substance over theater — adequate

The vision is specific to comparing two CPU implementations and preserving evidence, rather than generic learning-product language (§1). The single UJ is plausible as a concise reader path, though a named protagonist adds little for this solo technical study; its strongest value is showing how journal, evidence, and knowledge unit connect (§2.2). No boilerplate NFR section is present.

#### Findings

- **[low] Avoid treating “page” as a product surface (§2.2 UJ-1)** — The UJ says the page explicitly shows evidence status, while the product is Markdown in a Git repository (§§5, 6). *Fix:* use “日志或学习单元” / “记录” unless a rendered web page is an actual requirement.

### Strategic coherence — strong

The PRD has one thesis: compare equivalent architectural behavior through each implementation’s own microarchitecture, and retain the learning trail separately from the stable explanation and raw evidence (§§1, 4.2–4.3). The three selected cases serve that thesis. Non-goals and the reverse metric keep the work from drifting into conformance claims, exhaustive testing, or activity-count optimization (§§5, 7).

#### Findings

No material finding.

### Done-ness clarity — thin

FR-1 through FR-7 each have outcomes, and the technical features generally constrain the subject well (§4). However, terms such as “成功,” “普通,” “路径,” and “可证实观察阶段” still leave the actual scenarios and stopping points open. The success signals restate deliverables without specifying a reproducible acceptance checklist. This is the dimension most likely to cause inconsistent story completion.

#### Findings

- **[high] Define scenario preconditions for success `LD` (§4.2 FR-3)** — “一条普通标量 `LD`” does not fix privilege/translation mode, address mapping, cache response condition, or interference such as an older overlapping store; different implementations could be traced under materially different conditions. *Fix:* state a small common architectural scenario or require the story to record a binding scenario tuple for both snapshots (instruction width/semantics, privilege and translation assumptions, address mapping, and relevant memory/order conditions). If the intent is source-only, mark unobservable runtime preconditions as assumptions rather than implying a common run.
- **[high] Define the completion endpoint for fault tracing (§4.2 FR-5, SM-1)** — “fault 检测、异常保留、cause 和 trap 状态路径” does not say which trap state fields/target are required, or where the static trace may stop. `medeleg[13]=0` fixes delegation but not the complete recorded state. *Fix:* list the required architectural outputs (at minimum cause, faulting address value where implemented/required, exception PC, privilege/trap target and relevant status update) and allow “not established from source” explicitly for unavailable details.
- **[medium] Bound “每个可证实观察阶段” (§7 SM-1)** — The countable unit “每个阶段” is undefined, while §4.2 intentionally avoids aligning unlike internal stage names. *Fix:* define the deliverable as a per-core path table whose rows are source-supported transitions from the named start event to the specified endpoint; completion means every row has a source citation or an explicit unknown marker.
- **[medium] Make the evidence-status vocabulary orthogonal (§3, §4.3 FR-6)** — `source`/`test-inspected` describe evidence kind, `run-pass`/`run-fail` outcomes, and `blocked`/`unverified` state. A single “status” field cannot express these reliably. *Fix:* define separate fields for evidence kind and validation state, or state that these labels are independent tags and define combinations and precedence.
- **[medium] Give FR-2 a checkable minimum log schema (§4.1 FR-2)** — “统一结构” names content categories but not required headings or how an absent next question/evidence is represented. *Fix:* specify the minimum fields (question, actions/sources, findings with status, links to durable unit/evidence, next question; `unknown/not applicable` where needed) or link a canonical template.
- **[low] Make success signals auditable (§7 SM-1–SM-2)** — “一份交付覆盖” and “能够区分/跳转” describe outcomes but do not identify the exact artifact set or a simple check. *Fix:* name the expected index, case records, trace matrix and unit files, then verify link targets and required case fields with a manual checklist or link check.

### Scope honesty — strong

Non-goals explicitly reject upper-source RTL changes, conformance claims, exhaustive case coverage, mandatory dynamic execution, and a standalone blog (§5). The MVP and assumptions align with those limits (§§6, 9). Open questions are visible and, for a hobby/solo learning project, proportionate.

#### Findings

- **[medium] Reconcile the snapshot-mismatch exception with the fixed-snapshot rule (§§3, 4.2, 4.3 FR-7)** — The glossary defines snapshot from `sources.lock`, while FR-7 permits using a mismatched checkout after recording a boundary. That can turn an out-of-lock tree into evidence for the same deliverable. *Fix:* say either (a) stop/restore the lock before drawing in-scope conclusions, or (b) label any changed-checkout analysis as a separate, explicitly non-comparable appendix that cannot satisfy the locked-snapshot FRs.

### Downstream usability — adequate

The glossary is useful, FR/UJ/SM IDs are unique and sequential, and FRs can be extracted into stories. The PRD also names important sources and prior units (§§0, 3–4). Story authors still need to infer the concrete artifact paths, per-case evidence fields, and how unresolved scenario choices are approved. Because this is a chain-top PRD, those are worth fixing before story generation.

#### Findings

- **[medium] Name the expected artifact locations or a location-selection rule (§§4.1, 6.1)** — FRs refer to “日志首页,” “访存追踪矩阵,” and learning units but specify no canonical paths; only `learning-journal/plan.md` appears in the input list. *Fix:* identify the expected destination files/directories or require story planning to record them once in a location map and use that map consistently.
- **[low] State whether FR-6 applies per claim or per learning unit (§4.3 FR-6)** — “为主张标明” suggests per-claim traceability, but “每个比较结论” may mean only summary conclusions. *Fix:* specify the smallest tracked claim unit (for example, each row/assertion in the comparison table) and permit grouped citations only when they unambiguously cover all rows.

### Shape fit — adequate

For a solo learning stage, the capability-spec shape is suitable and no standalone personas are needed. The UJ is short and connects the reading flow to the central need, so it does not materially burden the document. The seven FRs, two success signals, non-goals, and assumption index are more formal than a personal notebook needs, but they serve downstream story planning and are not empty template sections.

#### Findings

No material finding.

### Mechanical notes

- **Glossary:** `fault` and `load page fault` are used informally beside the architectural phrase `cause 13`; consider defining “非规范地址” and clarifying the chosen Sv39 address category in the glossary or case contract.
- **IDs:** FR-1–FR-7, UJ-1, SM-1–SM-2 are contiguous and unique; no unresolved internal ID references found.
- **Assumption roundtrip:** Four inline `[ASSUMPTION]` entries appear in the index; no orphaned assumptions found.
- **Cross-references:** The three relative links in §0 resolve by path calculation from the PRD directory to the Spec, feasibility report, and learning plan. FR-3’s relative `load-v1.md` link resolves to `notes/units/load-v1.md`.
- **Required shape:** Purpose, vision, learner/tasks, glossary, FRs, non-goals, MVP, success signals, open questions, and assumptions are present.

## BMad Review Lenses

### Adversarial

The following are concrete improvement points; some overlap the rubric findings because the same ambiguity affects both acceptance and downstream planning.

1. **§0 — Independent-stage boundary:** The PRD says it follows the closed RVA23 project, but does not explicitly say that these deliverables must not change its original completion state. Add a completion-boundary statement to guard against future sprint bookkeeping reopening the old stage.
2. **§1 — Comparison equivalence:** “同一架构行为” does not say how to demonstrate that the two cases have equivalent architectural inputs. Require a compact shared-case definition while preserving each core’s distinct internal path.
3. **§2.2 — Reader state:** The UJ begins from an index and ends at a knowledge unit, but says nothing about how a reader sees the evidence level when a log lacks a runtime artifact. Specify the status/link behavior at that boundary.
4. **§3 — Evidence categories:** The term “证据” groups normative text, design documentation, source, tests, and runs, but does not establish whether citations can support claims at different strengths. Specify which claim types each source class may support.
5. **§4.1 FR-1 — Index discovery:** “仓库入口” could mean README, journal index, or another landing document. Name the canonical entry link to prevent multiple competing starts.
6. **§4.1 FR-2 — Missing data:** A log may have no runtime evidence or no new question. Define explicit `not run`, `unknown`, or `none` behavior so the template does not encourage omission to look like completion.
7. **§4.2 FR-3 — Load case:** “成功 LD” can hide materially different translation, cache, forwarding, and exception paths. Bind a scenario or require all unbound conditions to be declared assumptions in both records.
8. **§4.2 FR-4 — Store visibility:** “实际写入通路” and “更低层可见性” are not a single endpoint. State whether the deliverable follows to a queue acceptance, cache update, bus request, or another source-supported event; keep unobservable memory persistence out of the claim.
9. **§4.2 FR-5 — Fault state:** The case fixes mode and delegation but not an exact noncanonical VA or the required `stval/mtval`, `sepc/mepc`, status, and target fields. Specify the expected record fields or an explicit unknown marker.
10. **§4.3 FR-6 — Tag combinations:** The six labels mix evidence type, result, and status. Define independent tags or a tuple; otherwise the two cores may label equivalent evidence inconsistently.
11. **§4.3 FR-7 — Snapshot exception:** Allowing analysis from a non-lock checkout after recording a boundary can contaminate the locked comparison. Restrict it to separately labeled exploratory notes or require lock restoration.
12. **§5 / §6 — Harness boundary:** The non-goal says no isolated harness unless runtime trace becomes an acceptance criterion, while FR-6 accepts runtime evidence and FR-4 allows a story to determine test capability. Clarify that ordinary existing test harness use is allowed but creating new infrastructure is out of scope without an approved change.
13. **§7 SM-1 — Completion test:** “一份交付” could be one document with missing case details. Name the required records and evidence columns and require both implementations or an explicit missing-evidence marker.
14. **§7 SM-2 — Link validation:** “能够跳转” can be satisfied by a syntactically present but broken or stale link. Require resolving all links in the index and confirming target files exist.
15. **§8 item 1 — Decision owner:** The story may choose SD address/configuration and boundary, but no rule says who approves the choice or where it is recorded. Require a logged story decision before trace conclusions are written.
16. **§9 — Assumption lifecycle:** The assumptions are indexed but the PRD does not define which must be confirmed before architecture/story planning. Mark which are accepted working assumptions and which are phase blockers.

### Edge-case hunter

1. **§4.1 FR-1 / §7 SM-2:** If an index link target is missing or renamed, no handling is specified; require link resolution and an explicit “planned/not yet written” state.
2. **§4.1 FR-2:** If evidence or a next question does not exist for a log entry, required fields have no representation; define `not run`, `unknown`, or `none` rather than leaving status implicit.
3. **§4.2 FR-3:** The successful path has no stated branch for an observed cache miss, translation fault, or older-store interaction; bind conditions or require the record to say which branches are excluded.
4. **§4.2 FR-4:** If source inspection cannot establish any lower-layer visibility point, the acceptance condition is unclear; permit a bounded endpoint plus explicit unknown, rather than forcing an unsupported visibility claim.
5. **§4.2 FR-5:** The Sv39 noncanonical-address case is not fixed to a concrete invalid VA, and exact trap-state recording is unspecified; choose and document the address and required state fields before comparing.
6. **§4.3 FR-7:** If a checkout diverges after verification but before source citations are collected, the PRD gives no revalidation trigger; require recording the SHA used at analysis time and checking it against the lock before claiming in-scope evidence.
7. **§4.3 FR-6:** If one claim has source evidence on one core but no counterpart on the other, the PRD allows a missing-evidence note, but does not state whether the comparative claim is incomplete; require it to remain unverified/partial.

### Editorial Structure

**Chosen model:** Strategic/Context (Pyramid), appropriate for a PRD. Findings below are structural suggestions only; content is not being changed. Word impacts use the measured total of 2,653 words.

| Pass | Original Text | Revised Text | Changes |
|---|---|---|---|
| structure | §0 文档目的 + §1 愿景 (about 278 words) | **MERGE** into a short opening summary that states the approval/decision, scope, and goal; move the provenance links into a one-line “Inputs” note after it. | Front-loads the decision under the Pyramid model; estimated net reduction 20–40 words (0.8–1.5%). |
| structure | §2.1 目标任务 + §2.2 用户旅程 (about 233 words) | **CONDENSE** into one “Learner needs and flow” section; retain the index → evidence → learning-unit sequence and the `unverified/blocked` outcome. | Preserves the only useful journey while reducing overlap; estimated 40–70 words (1.5–2.6%). |
| structure | §5 非目标 + §6 MVP 范围 (about 355 words) | **MERGE** overlapping statements (static evidence acceptable, no deployed blog, selected cases only) and keep the fuller scope boundary once. | Removes repetition across “non-goals” and “not included”; estimated 35–60 words (1.3–2.3%). |
| structure | §§3–9, especially glossary, scope, and success signals | **PRESERVE** the glossary, non-goals, success signals, open questions, and assumptions index. | These may look formal for a solo project, but they directly prevent evidence overclaim and support downstream story extraction; no cut recommended. |

Summary: 3 structural recommendations plus 1 explicit preserve recommendation. If all condensing recommendations are accepted, estimated reduction is 95–170 words (3.6–6.4%); no length target was supplied. The proposed cuts preserve the mental model and evidence boundaries.

### Editorial Prose

The tone is restrained and technically precise; keep Chinese explanatory prose and the established English ISA/status terms. The following small edits remove avoidable ambiguity without changing scope.

| Pass | Original Text | Revised Text | Changes |
|---|---|---|---|
| prose | §2.2 “页面明确显示 `unverified` 或 `blocked`。” | “日志或学习单元明确标记为 `unverified` 或 `blocked`。” | Aligns the noun with the Markdown artifact model. |
| prose | §4.2 “经结果写回到退休的可证实路径。” | “经结果写回直到退休的、由源码或运行证据支持的路径。” | Makes “可证实” concrete and improves the endpoint phrasing. |
| prose | §4.2 “到实际写入通路” | “直到源码能够确认的写入接受点” | Avoids implying DRAM persistence when the implementation evidence may stop earlier. |
| prose | §4.3 “`source`、`test-inspected`、`run-pass`、`run-fail`、`blocked`、`unverified` 含义一致。” | “证据类型和验证状态分别标记；各标签的定义与组合规则保持一致。” | Avoids treating evidence type, result, and state as one category. |
| prose | §4.3 “若 checkout 与锁定快照不一致，先记录比较边界，再使用该 checkout 得出结论。” | Consider: “若 checkout 与锁定快照不一致，记录差异并停止将该 checkout 的结论计入本阶段固定快照比较。” | Removes the conflict with the fixed-snapshot promise; confirm whether out-of-scope exploratory notes are allowed. |

## Consolidated findings for triage

1. **High — Define scenario and endpoint contracts for the three cases** (§§4.2, 7): `LD` preconditions, `SD` write acceptance/visibility, and fault trap-state outputs are too open for consistent completion. Some detail can live in stories, but the PRD should require a binding scenario and explicit stop point.
2. **High — Reconcile the fixed snapshot rule** (§4.3 FR-7): the mismatch exception currently allows non-locked source conclusions to count toward the same learning deliverable.
3. **Medium — Separate evidence kind from outcome/state** (§3, 4.3 FR-6): the status vocabulary mixes incompatible dimensions and lacks combination semantics.
4. **Medium — Define the minimum log schema and artifact/link acceptance checks** (§§4.1, 6.1, 7): requirements currently describe desired behavior without a canonical entry path, target paths, missing-data representation, or auditable link check.
5. **Medium — Remove harness ambiguity** (§§5, 6, 8): clarify use of existing test harnesses versus creating a new trace harness.

**Initial review result (superseded by re-review delta):** Conditional pass for planning; close findings 1–3 before marking the PRD final. Findings 4–5 can be resolved in PRD or explicitly bound during architecture/story planning.
