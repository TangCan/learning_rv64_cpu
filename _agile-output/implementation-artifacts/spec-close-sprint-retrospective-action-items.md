---
title: '关闭所有 sprint retrospective action items'
type: 'maintenance'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e3a5474bbe867a83da21b8fb7c8c8ced48f9f1dc'
context:
  - '{project-root}/_agile-output/implementation-artifacts/sprint-status.yaml'
  - '{project-root}/_agile-output/implementation-artifacts/epic-1-retro-2026-10-12.md'
  - '{project-root}/_agile-output/implementation-artifacts/epic-2-retro-2026-10-12.md'
  - '{project-root}/_agile-output/implementation-artifacts/epic-3-retro-2026-10-12.md'
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-retro-2026-10-12.md'
  - '{project-root}/scripts/check_rva23_coverage.py'
---

## Intent

**Problem:** sprint-status.yaml 中有 8 项 retro action items 未关闭，涉及证据可追溯性、流程门槛、覆盖审计脚本和摘要一致性。

**Approach:** 逐条完成全部 8 项，补充自动化回归测试；只有在实现与证据验证完成后才通过 retrospective 状态工具标记 done。

## Boundaries & Constraints

**Always:** 保留固定上游快照及“不代表认证/动态行为未验证”等边界；状态计数由目录行数据推导并与发布摘要核对；测试直接覆盖列出的解析/链接/汇总故障。

**Never:** 不修改上游 `sources/`；不将静态证据描述为运行验证；不手工编辑 sprint action 状态（使用 sprint_status.py）。

## Code Map

- `notes/units/add-v1.md`、`notes/units/add-pilot-retrospective.md`：ADD 自检、RV64I 章节链接、29 周期测试源码表述。
- `notes/source-environment-baseline.md` 与 Story 1.1 spec：补足隔离复现错误 SHA fetch 的最小命令与输入。
- `notes/units/index.md`、`notes/units/dependency-v1.md`：Epic 2 自检锚点、profile 分类和同一 rename bundle 的适用边界。
- `.agents/skills/bmad-sprint-planning/scripts/sprint_plan.py`、其测试及 `.agents/skills/bmad-build/sync-sprint-status.md`：故事进入 in-progress 的上一 Epic retrospective 门槛；`optional` 表示可跳过，与 pilot 顺序门冲突时应由门控规则消歧。
- `spec-3-3-trace-sv39-noncanonical-load-fault.md`、`notes/units/sv39-load-fault-v1.md`：清除已解决的源码核实提示并保留静态/未动态验证边界。
- `scripts/check_rva23_coverage.py`：目录解析、状态计数及继承键校验；新增 `scripts/tests/test_check_rva23_coverage.py` 覆盖畸形输入、本地证据链接/锚点/ID及两份摘要漂移。
- `notes/rva23-coverage.md`、`notes/units/rva23-mandatory-coverage-audit-v1.md`、Epic 4 context/index：校验和同步派生计数、59 项去重关系、五项 S64 未调查事项及后续调查范围。

## Tasks & Acceptance

- [x] 修正 ADD 自检证据至 E13、固定 RV64I v20260120 链接、明确 29 次时钟迭代是测试源码行为；为负 SHA fetch 添加可复制命令和精确输入。
- [x] Epic 2 两个单元索引直接链接 `#单元自检`。
- [x] dependency 的通用 ISA profile 标为 `not-profile-specific`，并将分析明确限定于同一 rename bundle。
- [x] 新故事进入 in-progress 前，强制前一 Epic retrospective 为 done；使 optional 定义/生命周期与 pilot 顺序一致，并对门控添加测试。
- [x] 清除 Story 3.3 过期核实提示，链接静态证据并保留未动态验证边界。
- [x] 覆盖解析器逐个实现格验证恰有一个合法状态，并规范处理行首空白；自动测试覆盖重复键、同格多状态、错误 section、缺项、非法状态。
- [x] 从解析数据导出状态计数、profile 行数、总格数和去重要求数；与两处 Markdown 摘要逐值比较，验证本地 evidence 文件、锚点及 ID；测试每类漂移/损坏。
- [x] 摘要逐项列出四个 S64 双侧未调查项与 Heliodor-only Ssstateen，并明确五项都纳入后续调查规划，不算作当前已调查。
- [x] 运行覆盖校验、其新增测试及 sprint-planning 测试；所有 8 项完成后用官方状态脚本标记 done。

## Verification

- `uv run --no-cache pytest -q scripts/tests/test_check_rva23_coverage.py .agents/skills/bmad-sprint-planning/scripts/tests/test_sprint_plan.py` — 59 passed.
- `uv run --no-cache python scripts/check_rva23_coverage.py` — valid; 92 profile rows, 184 cells, 59 deduplicated requirements; both summaries and local evidence links validated.
- `uv run --no-cache --with ruamel.yaml python .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — valid, no problems.
- `git diff --check` — passed.
- Negative SHA reproduction: fetching the all-zero SHA from the isolated local bare remote returned 128; refs were unchanged and HEAD remained `refs/heads/master`.
- Official retrospective status updater reported `action_items_updated: 8`; subsequent sprint validation passed.

## Review Triage Log

| Finding | Verdict | Resolution / evidence |
|---|---|---|
| Retrospective missing or invalid status could yield a misleading next-story recommendation | Patch | Status recommendation now prioritizes the prerequisite retrospective; regression tests cover missing/invalid status. |
| Previous Epic lookup assumed consecutive numeric Epic IDs | Patch | Gate now selects the previous configured Epic; a skipped-number test covers it. |
| `#evidence_table` anchor alias was accepted but not checked against the file | Patch | Both hyphen and underscore anchor forms are validated; tests cover the alias. |
| Evidence ID ranges with suffixed IDs could be expanded incorrectly | Patch | Range expansion handles suffixes; suffixed range regression test passes. |
| Indented summary table rows lacked direct parser coverage | Patch | Added an indented summary table test. |
| No integration test exercised the complete coverage validation path | Patch | Added `validate_all` integration coverage. |
| Local evidence links with no E-ID label could be skipped | Patch | Evidence anchor links are now validated independent of label; regression test covers a no-ID label. |
| SHA reproduction could print results without failing on unexpected ref changes | Patch | Reproduction command now asserts fetch failure, unchanged refs, and unchanged symbolic HEAD; rerun succeeded. |
| Epic 1 exemption was unclear in the gate documentation | Patch | Sprint template, workflow instructions, and current sprint notes clarify there is no predecessor gate for Epic 1. |
| Existing non-story keys could pass the already-started gate path | Patch | Story-key validation now precedes resume logic; regression test covers non-story key rejection. |
| Edge review repeated the evidence-anchor alias inconsistency | Patch | Same anchor validation fix; underscore-alias regression test passes. |
| Story with an unknown status could pass the start gate when its previous Epic retrospective was done | Medium | The gate now rejects missing or unknown story statuses before resume or predecessor checks; a regression test covers unknown status with a satisfied predecessor gate. |
