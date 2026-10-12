---
title: 'Story 4.10: 核对 RVA23 必选项映射完整性'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f2a6809d022cd58ef2a2e7e20381a5b57022af57'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/planning-artifacts/epics.md'
  - '{project-root}/notes/rva23-coverage.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="Story 4.10 acceptance criteria and user-authorized continuation">

## Intent

**Problem:** RVA23U64/S64 强制要求目录虽已随着专题故事增长，但继承要求仍有空白模板，S64 部分专有要求也没有明确调查范围；当前缺少按 profile 和实现可复查的完整性统计。

**Approach:** 对照 RVA23 Profile v1.0 §3.1 清单，修复缺少的范围映射，保留未调查状态及理由，统计两核各 profile 的状态，并明确 mandatory、可选项、上游自述与符合性声明边界。

## Boundaries & Constraints

**Always:** 保留固定源码快照与证据链；继承行链接 U64 原始要求并避免去重计数；状态只表述目录的证据调查程度。

**Never:** 不根据搜索缺失推断实现不存在；不把单项测试或源码局部线索表述为完整符合性；不把选项、建议或项目自述算作必选要求。

</frozen-after-approval>

## Code Map

- `notes/rva23-coverage.md` -- 92 条 mandatory 行、状态规则、非强制分类、规范声明与目录计数；本故事主要审计和更新目标。
- `notes/units/rva23u64-scalar-v1.md` 等 Epic 4 学习单元 -- 继承行需要复用的实现范围、状态和证据表。
- `notes/units/rva23-mandatory-coverage-audit-v1.md` -- 本故事新增的审计方法、状态汇总和未决清单。
- `notes/units/index.md` -- 学习单元当前版本索引。
- `_agile-output/implementation-artifacts/sprint-status.yaml` -- Story 4.10 状态。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` -- 对照官方清单核对 profile 行、补齐继承与专有项范围、加入状态统计和未决清单。
- [x] `notes/units/rva23-mandatory-coverage-audit-v1.md` -- 记录审计口径、去重方法、逐侧计数与证据边界。
- [x] `notes/units/index.md` -- 登记 Story 4.10 审计单元。
- [x] `scripts/check_rva23_coverage.py` -- 固定官方必选键集合，校验遗漏/多项、状态格和状态统计可复现。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` -- 验证审查结果后将 Story 4.10 状态设为 done。

**Acceptance Criteria:**
- Given RVA23 Profile v1.0 §3.1 官方强制清单，when 对照目录，then U64/S64 的每项基础、扩展、继承及行为要求均有对应 profile 行。
- Given 每条 mandatory 行，when 检查双核映射，then 两侧均有明确状态；未调查或未验证范围带有理由和可追溯证据。
- Given 各行状态与分类，when 阅读汇总，then 可按 profile/实现核对状态数，选项和上游声明分开，未决项明确列出。
- Given 学习目录，when 阅读结论，then 明确其为规范与实现证据学习图谱，不宣称认证，局部测试不被扩大成完整证明。

## Implementation Notes

- 目录审计找出 33 条 S64 继承行的 66 个实现侧模板占位；继承映射复用对应 U64 行的状态和证据，并注明没有新增独立调查。
- 四项 S64 专有要求 Zifencei、Sstc、Sscofpmf、Ssnpm 保留 `not-studied`，已记录调查范围和理由。
- 计数按每条 profile 行的两个状态格分别统计；S64 的继承行纳入 profile 行数，但不重复计算去重规范要求数。

## Spec Change Log

## Review Triage Log

| Blind review: evidence-observed summary said zero despite two S64 Heliodor cells | low / patch | The count table and unit body show two such cells. Corrected the summary to say two; it now matches the data. |
| Blind review: count verification named a placeholder command and no reproducible script | low / patch | Added `scripts/check_rva23_coverage.py`, documented its exact command and observed output in this spec and E3. |
| Blind review: official inventory comparison lacked a checkable item manifest | low / patch | Added the fixed U64/S64 ID sets to the checker, sourced to Profile v1.0 §§3.1.1–3.1.2; it compares exact sets and reports missing/extra keys. |
| Blind review: E1 and E3 overlapped on row totals | low / patch | E1 now records the normative inventory baseline; E3 records status extraction and reproducible summary validation. |
| Blind review: scope caveat conflicted with evidence-link audit wording | low / patch | Clarified that local targets/anchors were checked, while source-content conclusions were not independently re-reviewed. |
| Blind review: Kunminghu reasons for four S64-only items were generic | low / patch | Added the corresponding instruction-fetch, timer, counter-overflow/filtering, and PME/PMLEN scope to each cell. |
| Blind review: index called Zifencei a privilege-only requirement | low / patch | Changed the label to S64-specific requirements and explicitly noted Zifencei. |
| Blind review: 15 remaining S64 requirements were not enumerated | low / patch | Listed the 15 requirement IDs in the summary so the 25 unique S64 requirements can be reconciled. |
| Blind review: verification section had placeholders and no observed results | low / patch | Replaced placeholders with exact runnable commands and recorded checker/validator/diff-check outcomes. |
| Blind review: status count process did not document how missing/invalid cells fail | low / patch | Checker rejects malformed table rows, missing/extra/duplicate keys, missing/invalid statuses, and template placeholders before printing counts. |

## Verification

**Commands:**
- `uv run --no-project python scripts/check_rva23_coverage.py` -- exit 0; observed output:

  ```text
  valid: true
  profile_rows: U64=34 S64=58 total=92
  implementation_status_cells: 184
  deduplicated_requirements: 59
  S64 Heliodor: evidence-observed=2, not-studied=5, partially-studied=26, studied-unverified=25
  S64 Kunminghu: not-studied=4, partially-studied=37, studied-unverified=17
  U64 Heliodor: partially-studied=14, studied-unverified=20
  U64 Kunminghu: partially-studied=21, studied-unverified=13
  ```

- Checker rejection probe (temporary fixtures passed through the checker's `--coverage` option): missing status → `expected two legal implementation statuses`; invalid status → same rejection; malformed key → `malformed mandatory inventory key`; mismatched inherited source → `missing or mismatched U64 inherited source link`. All four invocations exited nonzero.
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` -- observed: valid after Story 4.10 transitioned to done.
- `git diff --check` -- observed: no whitespace errors.
