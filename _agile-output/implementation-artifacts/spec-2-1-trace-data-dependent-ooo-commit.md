---
title: 'Story 2.1: 追踪依赖指令的乱序执行与提交'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: '4a61d6cbd735daeffb7c20c543237d4a74838e4c'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 学习记录尚未说明乱序处理器如何保持数据依赖指令的架构结果，也没有比较两个固定实现中从重命名到提交的状态路径。

**Approach:** 以 `addi x5,x0,10; addi x6,x5,1` 为有界 RAW 依赖例子，按 sources.lock 固定快照追踪物理寄存器分配、等待/唤醒、执行、ROB 写回与提交，并记录两边差异和验证边界。预期架构结果为 `x5=10`、`x6=11`。

## Boundaries & Constraints

**Always:** 使用 sources.lock 中完整快照 SHA；用官方规范版本和章节说明 ADDI 的架构行为；每项比较结论链接双方证据 ID；区分源码检查、测试源码检查和实际运行结果；记录未确认路径；使用不可变版本文件名并更新索引。

**Never:** 不修改上游源码；不把 RTL 生成入口当成运行验证；不推断实际周期数、调度次序或特定配置行为，除非证据直接支持；不从一个依赖案例推断整体乱序正确性或 RVA23 符合性。

</frozen-after-approval>

## Code Map

- `sources.lock` 固定 Kunminghu `xiangshan-kunminghu-v2-20261012` / `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `heliodor-master-20261012` / `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- `notes/templates/learning-record.md` 与 `notes/units/index.md` 定义记录结构和索引规则；新增 `dependency-v1.md`，保留 ADD 记录。
- RISC-V Unprivileged ISA Manual v20260120 RV32I §1.1.4、§1.1.4.1 说明 XLEN、ADDI/ADD 结果与异常边界（RV32I commentary 亦适用于 RV64I；https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html）。
- Kunminghu: `backend/decode/DecodeUnit.scala:147,154` 译码；`backend/rename/RenameTable.scala:105-149`、`Rename.scala:391-415,518-584` 映射及旁路；`backend/issue/EntryBundles.scala:39-45,240-301` 就绪/唤醒；`backend/datapath/DataPath.scala:447+` 读寄存器；`backend/fu/Alu.scala:196-202,286-291` 执行；`backend/rob/Rob.scala:528-549,788-805` 写回/提交。`IssueQueueMain` 仅生成 RTL。
- Heliodor: `heliodor_core.veryl:2418,2507-2517,3408-3473`、`rat.veryl:119-190` 重命名/提交映射；`iq_int.veryl:429-467,763-790,902-975` 就绪、发射、CDB 唤醒；`heliodor_core.veryl:3023-3065,3342-3368` 执行、读寄存器、PRF 写回；`rob.veryl:560-599,1400-1428` 完成/提交。检查测试覆盖，不推断周期安排。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/dependency-v1.md` — 基于模板记录依赖例子的 ISA 结果、两边 rename→issue/wakeup→execute→ROB/commit 状态路径、双边比较证据、自检答案、未确认边界与验证记录。
- [x] `notes/units/index.md` — 增加 `dependency` 当前版本链接和阶段状态，保留既有 ADD 项。

**Acceptance Criteria:**
- Given sources.lock 中的固定快照，when 记录依赖单元，then 用有界 producer/consumer 指令例子说明输入及架构结果，并引用适用规范。
- Given 该数据依赖，when 追踪两种实现，then 分别说明适用的重命名、发射/等待/唤醒、执行和提交路径及关键状态变化；不适用或未确认的阶段明确标注。
- Given 两条实现路径，when 进行比较，then 每项结论有双方证据 ID，且源码检查与测试运行证据分开。
- Given 单元记录完成，when 保存版本，then 使用新的不可变 `<unit_id>-vN.md` 文件并将索引指向该版本。
- Given 阶段自检，when 回答，then 解释依赖如何维持正确性，并定位两边关键结构与验证边界。

## Implementation Notes

## Spec Change Log

## Review Triage Log

- `low / patch` — C4 originally cited Heliodor evidence E13 in the Kunminghu column. The evidence table identifies E13 as Heliodor; corrected C4 to cite Kunminghu E18 and Heliodor E17.
- `low / patch` — E1 initially cited only RV32I for the RV64I scenario. The official RV64I chapter says it builds on RV32I and presents only differences; added the RV64I companion citation and the read-together rationale.
- `medium / patch` — The self-check implied a consumer wakes only after producer writeback. `EntryBundles.scala:337-362` accepts both IQ and writeback wakeups and selects bypass data on IQ wakeup; the record now describes both and leaves the case-specific route unconfirmed.
- `low / patch` — The Kunminghu data path was described as a direct physical-register read. `DataPath.scala:447-485,507-523,680-712` and `EntryBundles.scala:337-362` show PRF/RC data and bypass/source selection; the record now names both and does not assert which this case selects.
- `low / patch` — E18 originally presented two test-tree entrypoints as behavior-test evidence. `IssueQueueMain` invokes RTL generation and `MultiWakeupQueueMain` has its generation body commented out; E18 is now `source / inspected` and explicitly says neither establishes behavior coverage.

## Verification

**Commands:**
- 不运行 CPU 构建、仿真或测试；仅依据验收范围作固定快照源码和现有测试覆盖检查，不产生 `run-pass` 证据。

**Manual checks:**
- 核对快照、规范引用、关键路径行号、双边证据 ID、未运行边界及新版本索引。
