---
title: '核验三类案例的证据与快照'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'dispatch'
baseline_commit: '528edce4960c7a86ee382916e6cf189ec8ba4acc'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epic-1-context.md'
  - '{project-root}/_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/learning-record-conventions.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** LD、SD 和 Sv39 fault 已分别形成双侧追踪，但还没有对六条矩阵路径、结论到证据的闭合关系、证据类型/状态及固定源码快照做一次统一审计。个别版本间存在证据引用范围和旧路径表述差异，读者需要知道哪些是当前有效记录、哪些只是历史材料。

**Approach:** 按当前索引的三类学习单元与 trace matrix，核对六条 Kunminghu/Heliodor 路径、claim→证据 ID→源码位置、ID 范围、运行记录字段和两份 `sources.lock` 快照。将已确认缺口修正在新版本或矩阵中，保留不可变旧版，并把剩余 `unknown`、`blocked`、`unverified` 和比较缺侧记录清楚。唯一性按当前三类活动记录及其矩阵引用审计；历史版本中的局部 ID 留作版本内引用，不改写历史。

## Boundaries & Constraints

**Always:** 使用锁定完整 SHA 并核对 checkout HEAD；证据 `type` 与 `status` 分列；静态检查、测试材料和动态观察不可互相替代；实际运行结论须能追到精确输入、命令、配置、输出和产物；已发布学习单元只通过新版本修订，索引指向当前版本。

**Never:** 不修改上游 checkout 或 `sources.lock`；不补跑 CPU 测试、构建或仿真；不把启动标记、测试源码或历史摘要写成运行通过；不扩大结论为 RVA23 整体符合性。

</frozen-after-approval>

## Code Map

- `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 六条 LD/SD/fault 行与各自证据链接、type/status。
- `notes/units/load-v2.md`、`store-v1.md`、`sv39-load-fault-v3.md` — 当前 claim/证据表；ID 前缀 `LD2-E`、`SD1-E`、`SF1-E`。源位置只读核对。
- 对应 `*-v1.md` 是历史版本：LD/fault 有局部 E 编号，且 fault v1 引用旧 CSR 集成；不要原地改写或拿作当前 claim 证据。当前唯一性检查仅包含当前索引版本，不将历史局部别名与活动 ID 混用。
- `sources.lock` 及两个 `sources/` checkout — snapshot/完整 SHA；journal 与 `notes/units/index.md` 遵循现有格式和导航。

## Tasks & Acceptance

**Execution:**
- [x] 逐行审计矩阵六条路径及当前学习单元：起点/终点、claim→ID→源位置、`type`/`status`；fault 比较缺侧在 v3 标记 `partial`/`unverified`，v1/v2 保持不变。
- [x] 核对活动证据 ID、完整 SHA 与 checkout HEAD；35 个活动证据 ID 唯一。两个 checkout HEAD 与 `sources.lock` 一致；没有动态运行产物的结论保持 `unverified`。
- [x] 新增审计日志并更新学习日志、计划和学习单元索引导航，记录结果、未知边界和历史版本处理。

**Acceptance Criteria:**
- Given 三类案例，when 检查矩阵，then 六条路径均有起点、证据终点、ID 和源位置；缺口标 `unknown`/`blocked` 并解释。
- Given 任一比较，when 追查支持，then 两侧有证据，或标 `partial` 并将缺侧标 `unverified`/`blocked`；`partial` 不是证据状态。
- Given 活动证据 ID/源码引用，when 对照来源，then ID 无歧义、snapshot/full SHA 与 checkout HEAD 一致；旧版不得支撑当前 claim。
- Given 运行结论，when 核验记录，then 输入、命令、配置、输出和产物可查；否则不得当作运行观察或标 `run-pass`。
- Given 交付完成，when 查看日志、矩阵和索引，then 静态/动态证据及未知边界清晰，旧单元未原地修改，且未运行测试/构建/仿真。

## Implementation Notes

- 发布 `notes/units/sv39-load-fault-v3.md`，将原 v2 的 ACT 比较修正为 `partial`：Heliodor README 仅为一般测试材料，Kunminghu 对应测试材料标为 `unverified`；v1/v2 均未原地修改。矩阵改指向 v3。
- 独立 diff 检查补齐 v3 自检的 E11 证据引用与 matrix 的 `test-inspected` 类型；当前单元共 35 个前缀化 ID，活动记录之间唯一。
- 新增 `learning-journal/2026-10-15-three-case-evidence-audit.md`，并更新 `learning-journal/index.md`、`learning-journal/plan.md`、`notes/units/index.md`。
- 未修改 `sources.lock` 或上游 checkout；未运行 CPU 测试、构建或仿真。

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence | Route / result |
| --- | --- | --- |
| Kunminghu matrix row incorrectly labeled test-inspected | `patch`：SF1-E3–E6 均为源码静态检查，Kunminghu 测试材料标为 unverified；矩阵已改为 `source`。 | 已修复 |
| Heliodor matrix row status obscured unverified tuple | `patch`：SF1-E11 为 inspected，SF1-E12 为 unverified；矩阵现分别列出 `test-inspected`/`inspected` 与 `test-run`/`unverified`。 | 已修复 |
| Matrix source locations were not inline | `false`：矩阵每行链接到证据 ID，证据 ID 在学习单元证据表对应源码位置；AC 要求路径可追溯，不要求重复内联位置。现已在矩阵说明该关系。 | 驳回；链接关系已明确 |
| SF1-E11 README reference was broad | `patch`：对应内容实际在 README 的 `123–125`，suite 命令在 `131–133`；证据行已精确标注，并说明未检查底层测试产物。 | 已修复 |
| C3 could imply measured coverage | `patch`：现有材料不能确认输入与断言，故不能测量覆盖；已改称“可用测试材料的部分比较”。 | 已修复 |
| Active ID uniqueness claim lacked reproducible scope | `patch`：审计日志现列出 `LD2-E1–E15`、`SD1-E1–E8`、`SF1-E1–E12`，并记录跨集合查重无重复。 | 已修复 |
| Matrix did not make unspecified PC_LD explicit | `patch`：fault 单元将 `PC_LD` 记为未赋值，矩阵现明确此项未赋具体值。 | 已修复 |

## Design Notes

三类活动学习单元已有 `LD2-E`、`SD1-E`、`SF1-E` 前缀；旧版档案仍使用单元局部编号。以当前活动记录为首要核验面，并在范围选择后按不可变学习记录约定处理，不为表面统一而重写历史版本。

## Verification

**Commands:**
- `python3 scripts/check_doc_links.py learning-journal/2026-10-15-three-case-evidence-audit.md learning-journal/index.md learning-journal/plan.md notes/units/index.md notes/units/sv39-load-fault-v3.md _agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 所有受支持的本地链接和锚点均存在。
- `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/sprint-status.yaml` — sprint 状态合法。
- `git diff --check` — 无空白错误。

**Manual checks:**
- 核对六条路径的证据 ID、源码位置、type/status、当前单元版本和来源 SHA；确认旧版本未改。
- 不运行测试/构建/仿真；只报告现有静态证据和既有产物。
