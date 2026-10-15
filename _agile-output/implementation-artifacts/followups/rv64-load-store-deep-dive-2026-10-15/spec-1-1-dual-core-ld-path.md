---
title: '复核并记录双核 LD 路径'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'dispatch'
baseline_commit: '88e35857de1d1e90b66c643443a15c819d50793f'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epic-1-context.md'
  - '{project-root}/_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epics.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 现有 `load-v1.md` 已记录 Kunminghu V2 与 Heliodor 的静态 `LD` 路径，但 Heliodor 的说明把 architectural RAT 与 `arch_regs` 调试镜像的更新时机合并描述，未体现两者门控不同。

**Approach:** 复核两个锁定快照的源码路径，新增不可变 `load-v2.md` 修正退休状态说明，并发布一篇中文探索日志。更新学习单元索引、日志索引和追踪矩阵，使路径、证据类型、验证状态、来源快照与未验证前提可以互相追溯。

## Boundaries & Constraints

**Always:** 使用 `sources.lock` 中的 Kunminghu SHA `c098f996bf4d301b88693b20315486d31e93bc9d` 和 Heliodor SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；按各自术语描述路径；区分 evidence type 与 validation status；保持 `load-v1.md` 不变；自然对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store 中无法观察的前提继续标为 assumption，静态源码不得写成动态运行观察。

**Never:** 不修改上游 RTL，不运行或声称运行 LD 测试，不声称观察到本案例实际 hit、写回或退休，不扩大为 RVA23 符合性结论。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/load-v2.md` — 从现有 LD 单元建立下一不可变版本，唯一化本版本 evidence ID，并分别说明 Heliodor `rat_arch` 的 ack 门控和 `arch_regs` 调试镜像的 commit-valid 门控。
- [x] `notes/units/index.md` — 将 `load` 当前版本指向 v2，保留 v1 文件。
- [x] `learning-journal/2026-10-15-ld-path-review.md` — 记录日期、问题、查阅来源/动作、发现与 evidence type/status、知识单元及证据链接、下一步。
- [x] `learning-journal/index.md` — 发布该日志链接，并将 LD 主题从计划中更新为已完成本次复核。
- [x] `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 增加 Kunminghu 与 Heliodor 两条 LD 路径记录，列出起点、证据支持终点、锁定快照、证据 ID、type/status 与假设边界。

**Acceptance Criteria:**
- Given `sources.lock` 中的两个 checkout，when 复核 LD 路径，then HEAD 与锁定 SHA 一致，地址生成、转换、DCache hit 条件、结果写回和退休条件均引用具体源码位置，并使用各自阶段术语。
- Given Heliodor 的提交路径，when 描述架构状态，then `rat_arch` 更新明确受 `rob_commit_ack` 门控，`arch_regs` 调试镜像更新明确受 `rob_commit_valid` 门控，两者不混称为同一个架构状态。
- Given Bare、DCache hit、无异常、无更老重叠 store 等条件没有运行证据，when 记录路径，then 标为 assumption；源码证据为 `source` + `inspected`，案例运行状态为 `unverified`。
- Given 日志与矩阵完成，when 检查产物，then v1 未改、索引指向 v2、v2 evidence ID 引用一致、日志可达，且矩阵有两条分列 type/status 的 LD 行；不声称运行测试。

</frozen-after-approval>

## Code Map

- `notes/units/load-v1.md` — 已有路径、E1–E15 与边界；作为 v2 基线，保持不变。
- `sources/xiangshan/src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala`, `sources/xiangshan/src/main/scala/xiangshan/cache/dcache/loadpipe/LoadPipe.scala`, `sources/xiangshan/src/main/scala/xiangshan/backend/rob/Rob.scala`, `sources/xiangshan/src/main/scala/xiangshan/backend/rename/RenameTable.scala` — 地址、hit、写回和退休路径；SHA `c098f996bf4d301b88693b20315486d31e93bc9d`。
- `sources/heliodor/src/core/decoder.veryl`, `heliodor_core.veryl`, `lsu.veryl`, `rob.veryl`, `rat.veryl`, `sources/heliodor/src/cache/dcache.veryl`, `sources/heliodor/src/mmu/dmem_mmu.veryl` — decode 至退休；区分位于 `heliodor_core.veryl:4062-4069,4416-4418,5179-5185`；SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- `notes/units/index.md`、`learning-journal/{index.md,plan.md}`、`_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md`、`_agile-output/specs/spec-learning_rv64_cpu/learning-record-conventions.md`、`sources.lock` — 现有导航、矩阵、证据规则及快照边界。README 已链接日志首页。

## Implementation Notes

- 新建 `load-v2.md`，将 Heliodor `rat_arch` 的 ack 门控与 `arch_regs` 调试镜像的 commit-valid 门控分开记录；E1–E15 以 `LD2-E1`–`LD2-E15` 命名，未改动 v1。
- 新增 2026-10-15 学习日志，更新两个索引、学习计划和 trace matrix。链接检查发现并修正一处标题锚点不匹配。
- 测试源码证据使用 `test-inspected` + `inspected`；案例运行仍为 `unverified`。
- Kunminghu 和 Heliodor HEAD 均匹配 `sources.lock`。本故事按静态路径范围完成，未运行 LD 测试或仿真。
- 审查后将比较 claim 补齐为连续编号，并补充 Kunminghu load writeback 连线、LoadQueue bundle 字段及 Heliodor HEX 内容未检查的限定；v1 保持不变。

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| 比较结论从 C3 跳到 C5 | low | 表中没有 C4，读者会误以为缺少比较项；将 C5 统一改为 C4，并同步更新 E14/E15 claim 引用。`patch` |
| LD2-E12 对 `rv64ui/ld.hex` 的内容与覆盖范围说明不足 | low | harness 只证明配置指向该文件且有 pass assertion，未检查 HEX 内容也未运行；已明确这一边界并收窄 Observed。`patch` |
| LD2-E6 的 LoadQueue 数据/状态字段依据不充分 | low | `LqWriteBundle` 继承的 `LsPipelineBundle` 定义了 uop、地址、data 和状态字段，LoadQueue 的 `ldin` 接入该 bundle；已补列定义与接线位置。`patch` |
| Kunminghu `ldout` 到 backend writeback 的中间连线未列 | low | MemBlock 将 load 输出送入 `writebackLda`，XSCore 再接到 backend；已将两个连接位置加入 E5 并补充矩阵叙述。`patch` |
| 未提供具体地址、寄存器初值和可重放输入 | false | Story 定义的是有明确对齐、特权和 hit 前提的抽象路径比较，不要求一组可运行输入；记录已将实际 EA/值标为未观察，无误导性的复现声明。 |
| 矩阵的 `source`/`inspected` 可能被误读为案例已经验证 | false | 矩阵在 Story 1.1 标题下明示场景是 assumption、实际 hit/结果/退休为 unverified，且列说明类型与状态独立；日志也单列 experiment/unverified。 |
| 矩阵证据 ID 没有直达证据表的链接 | false | 两条矩阵记录的证据 ID 均已链接到 `load-v2.md#证据表`，链接检查验证该锚点存在。 |

## Verification

**Manual checks:**
- 核对两个 checkout 的 HEAD 与 `sources.lock` 完整 SHA 一致。
- 检查 v1 未修改、v2 evidence ID 引用一致、索引/日志/矩阵链接可达，并确认两条矩阵行没有把静态源码标为已运行。
- `python3 scripts/check_doc_links.py` 检查 7 份文档；BMAD sprint status validate 通过；`git diff --check` 通过。
- 未运行 RTL、CPU 构建、仿真或 LD 测试，符合本故事边界。
