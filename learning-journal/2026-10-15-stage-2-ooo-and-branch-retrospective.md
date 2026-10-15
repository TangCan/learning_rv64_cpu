# Stage 2 回顾：乱序依赖与分支恢复

回顾日期：2026-10-15

> 本文依据 Git 历史、Story 规格、两个学习单元和 Epic 复盘事后整理，不是 2026-10-12 的会话记录。结论限于记录覆盖的固定源码快照，不补写未留存的探索步骤或运行观察。

## 本次问题

Stage 2 用两个案例理解乱序处理器如何维护正确状态：数据依赖如何从重命名延续到提交；分支方向预测错误时，错误路径如何被清除并恢复正确控制流。两例分别对应 Story 2.1 和 2.2，均对照 Kunminghu V2 与 Heliodor。

## 可追溯的学习过程

- **2026-10-12 15:18：依赖案例。** 提交 `73b166ce75aba10b0e76c4749221b3b63282829c` 加入 `dependency-v1.md`。案例限定同一个 rename bundle 内的 `addi x5,x0,10; addi x6,x5,1`，沿物理寄存器重命名、等待与唤醒、执行、ROB 写回和按序提交追踪 RAW 依赖。
- **2026-10-12 15:31：分支恢复案例。** 提交 `b50d796423817dc7dad6d0937d928aa7d8d0e101` 加入 `branch-recovery-v1.md`。案例限定条件分支预测不跳转、实际结果跳转，检查错误路径年轻项的清除、分支保留、重命名状态恢复和目标重定向。
- **2026-10-13：Epic 复盘。** `e3a5474bbe867a83da21b8fb7c8c8ced48f9f1dc` 写入 Epic 回顾，接受两个故事的核心学习交付，同时记录索引可发现性和依赖案例边界等后续事项。复盘不是两个案例的动态验证。
- **2026-10-14：后续闭环记录。** `4394eb9c626c6405a1ae1a354fdd2a79da92ad30` 记录复盘行动项跟进：[`notes/units/index.md`](../notes/units/index.md) 直接链接两份单元的自检答案；[`dependency-v1.md`](../notes/units/dependency-v1.md) 将案例明确为同一 rename bundle，并将通用 ISA 的 profile 分类改为 `not-profile-specific`。Epic 2 复盘的[后续跟进记录](../_agile-output/implementation-artifacts/epic-2-retro-2026-10-12.md#action-item-follow-through-verified-2026-10-14)列出这两项闭环。应将这些视为后续归档修订，而非首轮记录时已经完成的工作。

上述时间来自提交者时间；可用完整 SHA 执行 `git show -s --format='%H %aI %s' <完整 SHA>` 复核。两个单元均引用 `sources.lock` 固定的 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。

## 发现与证据边界

| 案例 | 源码检查所得 | 验证边界 |
| --- | --- | --- |
| ADDI RAW 依赖 | 两边都用 producer 新分配的物理目的标签关联 consumer，并区分结果写回与 ROB 按序提交；Kunminghu 还存在 IQ wakeup/bypass 与写回唤醒后 PRF/RC 等数据路径。 | 指令对的架构预期 `x5=10`、`x6=11` 来自 ISA 推导，不是运行结果；本例实际唤醒和数据选择路径、调度次序与周期均未确认。Heliodor smoke 被 `#[ignore]`，其说明、ROM 与断言不对应本例；Kunminghu 检查到的两个入口也不是本例行为测试。 |
| 条件分支恢复 | 两边源码都呈现错预测识别、保留分支及较老工作、清除年轻错误路径和转向正确目标的路径。Kunminghu 使用 `flushAfter` 与 snapshot/arch map 恢复选择；Heliodor 使用预测/实际 next-PC 比较、分支 checkpoint、partial squash，并有提交阶段 backstop。 | 这些是静态源码结论。Kunminghu 检索范围内未发现专用恢复测试；Heliodor 的 BEQ/BNE 测试源码没有运行，也不证明 early recovery。预测器配置、周期、性能以及完整 RAS 恢复均未验证。 |

Epic 2 复盘判定为 `accepted-with-open-items`，随后记录了相关行动项闭环。这里的“接受”指学习记录满足已声明的范围，不代表两个 CPU 已通过端到端验证，更不是整体乱序正确性或 RVA23 符合性证明。

## 知识沉淀

- [ADDI RAW 依赖单元](../notes/units/dependency-v1.md)记录有界输入、两侧路径、比较证据和自检答案。
- [分支冲刷与恢复单元](../notes/units/branch-recovery-v1.md)记录预测不跳转、实际跳转案例与恢复边界。
- [Epic 2 回顾](../_agile-output/implementation-artifacts/epic-2-retro-2026-10-12.md)记录验收判断、当时的开放项及后续行动项；[Epic 2 Context](../_agile-output/implementation-artifacts/epic-2-context.md)记录阶段目标与跨故事约束。
- [Story 2.1](../_agile-output/implementation-artifacts/spec-2-1-trace-data-dependent-ooo-commit.md)与[Story 2.2](../_agile-output/implementation-artifacts/spec-2-2-trace-branch-flush-recovery.md)保留各案例的原始验收范围。

## 下一步

日志计划中的下一个历史阶段是 Stage 3：普通访存、原子操作与地址异常。应继续分别依据现存记录回顾，并维持源码检查、测试源码检查和实际运行证据之间的区分。
