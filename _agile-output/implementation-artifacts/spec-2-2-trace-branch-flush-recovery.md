---
title: 'Story 2.2: 追踪分支冲刷与恢复'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: '73b166ce75aba10b0e76c4749221b3b63282829c'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 阶段 2 的记录还没有说明分支方向预测错误后，错误路径工作如何被丢弃、架构状态如何恢复，以及两种处理器的恢复边界有何不同。

**Approach:** 以“条件分支预测不跳转、实际结果跳转”为有界情景，基于 sources.lock 固定快照追踪错预测确认、年轻指令冲刷、保留分支及控制流恢复；比较 Kunminghu 与 Heliodor 的状态路径和验证边界。

## Boundaries & Constraints

**Always:** 引用完整快照 SHA 与稳定源码位置；每项比较结论链接双方证据 ID；区分规范、源码检查、测试源码检查和实际运行；配置或专用恢复测试无法确认时标为未验证；新增不可变版本记录并更新索引。

**Never:** 不修改上游源码；不猜测预测配置、周期或运行结果；不混入陷阱、load replay 等情景，也不以局部机制证明整体正确性。

</frozen-after-approval>

## Code Map

- `sources.lock` 固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。规范：RISC-V Unprivileged ISA v20260120 RV32I §1.1.5.2、RV64I §3.1；只界定架构分支行为。
- Kunminghu：`backend/fu/Branch.scala:42-50` 判方向错预测；`BranchUnit.scala:32-68` 产生 `flushAfter`；`CtrlBlock.scala:192-211,331-349` 选择/转发；`rob/RobBundles.scala:210-215`、`Rob.scala:955-982` 冲刷年轻 ROB 项；`rename/RenameTable.scala:119-141`、`rename/Snapshot.scala:43-75`、`rename/Rename.scala:176-184,603-628` 恢复映射/快照。测试树检索未发现专用恢复测试。
- Heliodor：`src/core/heliodor_core.veryl:8352-8423` 检查 live control op 的预测/实际 next-PC；`:3389-3406,3617-3622,3719-3729,4307-4314` 接 checkpoint restore 与 IQ/ROB squash；`src/core/rob.veryl:356-374,1536-1565` 保留分支及更老项；`src/core/rat.veryl:137-154` 恢复 RAT。`test/test_arch_common.veryl:715-739,1038-1062` 的 BEQ/BNE 测试不证明早期恢复。
- 复用学习记录模板和索引，新建 `notes/units/branch-recovery-v1.md`。注明 RAS 恢复近似及 commit-time backstop。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/branch-recovery-v1.md` — 记录 ISA 场景、两边错预测判定/冲刷/恢复路径、双边证据、测试边界、自检答案和未确认项。
- [x] `notes/units/index.md` — 链接新不可变版本，保留既有条目。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` — Story 2.2 与 Epic 2 已为 `in-progress`；无需变更。

**Acceptance Criteria:**
- Given sources.lock 固定快照，when 记录预测不跳转而实际跳转的条件分支，then 说明架构行为、情景范围及未确认配置。
- Given 错预测已确认，when 追踪两边实现，then 定位判定、错误路径识别、年轻指令冲刷、保留/恢复状态及重定向路径。
- Given 比较结论，when 汇总证据，then 每项引用双方证据 ID，且不将检查源码或测试源码表述为运行通过。
- Given 学习单元交付，when 更新记录，then 使用新的 `<unit_id>-vN.md` 文件并更新索引。
- Given 阶段自检，when 回答问题，then 解释为何错误路径不能提交，并指出至少一个验证边界。

## Implementation Notes

计划事实：未指定运行配置，标记未验证；只修改文档、索引、规格和 sprint 元数据，无外部副作用。Epic 2 context 有效；沿用 Story 2.1 的快照、证据分类与版本约束。

## Spec Change Log

## Review Triage Log

- `low / patch` — Blind Hunter found sprint Story 2.2 remained `in-progress` while its spec had entered `in-review`; synchronized sprint status to `review` before completing review.
- `low / patch` — Blind Hunter found the Heliodor BEQ/BNE test paragraph cited source evidence E13; corrected the paragraph to cite test-inspected evidence E14.
- `false` — Blind Hunter found an inconsistent test path between the spec Code Map and the learning record. The changed learning record now points to the confirmed `sources/heliodor/tb/test_arch_common.veryl`; the review workflow disallows fixing findings whose remedy is to edit this build spec.
- `medium / patch` — Blind Hunter found the self-check did not cite direct ROB commit eligibility evidence; added Kunminghu E15 and Heliodor E16 to the answer, comparison and evidence table.
- `false` — Blind Hunter found the implementation note said Story 2.2 was already `in-progress` despite the baseline showing `backlog`. The note records the state at implementation handoff, after the coordinator had synchronized the story to `in-progress`; the implementer correctly made no further status change.
- `low / patch` — Verification Gap Reviewer independently found the Heliodor BEQ/BNE paragraph cited E13 rather than E14; same source reference corrected above.
- `false` — Edge Case Hunter independently found the same status-note/diff mismatch as Blind Hunter. The note describes the implementation handoff state after the coordinator's pre-dispatch transition; no inconsistent state was present at handoff.

## Verification

**Commands:**
- 文档核查：检查 frontmatter、证据双边引用、索引目标与 sprint 状态一致性；不运行 CPU 构建、仿真或测试。

**Manual checks:**
- 抽查所有源码路径/行号与固定快照；确认“未运行”边界清晰，且未从局部案例推断 RVA23 符合性。
