# Stage 5 回顾：深入比较 RVA23S64 专题与验证证据

> 本文是基于版本历史和现存材料整理的事后回顾。Git 时间均为作者时间（`%aI`，Asia/Shanghai，UTC+08:00）；提交时间能定位记录何时进入版本历史，不能还原未记录的探索过程。

## 本阶段要回答的问题

Stage 4 建立了 RVA23 必选项映射后，下一步是选取对特权态实现影响较大的专题，沿两份固定 CPU 快照理解规范要求、活动实现路径和验证入口。Epic 5 将范围限定为 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen 五项，并允许结论落在静态证据、未验证或受阻；学习结项不等同于 RVA23 符合性验证。

准备门先核对源码快照、活动目标和可用测试入口。[准备矩阵](../notes/units/rva23s64-deep-dive-readiness-v1.md)显示，测试源码或候选命令只是入口线索，必须实际启动目标 CPU 才能标为运行证据。Story 5.1 于 2026-10-13 12:31:03（提交 `990ee743`）记录准备度；五项专题于当日下午至晚间陆续沉淀，随后由 Story 5.7 审计跨单元的要求映射与证据边界。

## 五项专题的证据边界

| 专题 | 静态学习发现 | Epic 5 动态证据与限制 |
| --- | --- | --- |
| Zifencei / `FENCE.I` | 追踪 Kunminghu 的 decode、fence 请求与 Heliodor 的译码/候选测试；区分本 hart 后续取指同步与跨 hart 发布。详见 [Zifencei 单元](../notes/units/rva23s64-zifencei-v1.md#证据与结果)与[结项案例审计](../notes/units/rva23s64-closeout-audit-v1.md#计划案例结果与范围)。 | Fixture 已汇编、反汇编，但 Kunminghu 没有可用定向 CPU 入口；Heliodor 在 testbench check 阶段退出，CPU 未运行。故没有 Epic 5 `run-pass`。 |
| Sstc | 比较 `stimecmp`、`vstimecmp`、`STCE`、timer 比较器和 STIP/VSTIP 接入路径。详见 [Sstc 单元](../notes/units/rva23s64-sstc-v1.md#evidence-table)与[结项案例审计](../notes/units/rva23s64-closeout-audit-v1.md#计划案例结果与范围)。 | 两个 Heliodor 候选 target 都在 testbench check 退出；Kunminghu 缺少定向入口。S/VS 比较边界、门控和中断递送均未观察。 |
| Sscofpmf | 静态追踪 `mhpmevent` 溢出、`scountovf`/LCOFI 及按特权模式过滤的实现线索。详见 [Sscofpmf 单元](../notes/units/rva23s64-sscofpmf-v1.md#evidence-table)与[结项案例审计](../notes/units/rva23s64-closeout-audit-v1.md#计划案例结果与范围)。 | Heliodor 候选用例在 testbench check 退出；Kunminghu 没有已定位的定向 fixture，ACT/Sail 案例也未生成或执行。不能用软件写计数器回绕替代硬件溢出证据。 |
| Ssnpm | 对照指针掩码控制和地址路径，并保留 profile 文档 `PME` 与架构规范/RTL `PMM` 的原始术语差异。详见 [Ssnpm 单元](../notes/units/rva23s64-ssnpm-v1.md#证据表)与[结项案例审计](../notes/units/rva23s64-closeout-audit-v1.md#计划案例结果与范围)。 | 候选 `test_arch_supm` 在 testbench check 退出，CPU 未运行。S/U/guest 变换、非标量访问族与边界情形仍未验证。 |
| Ssstateen | 检查 Kunminghu CSR 路径及 Heliodor 固定 CSR 主路径，限定对“未找到”与“未实现”的推断范围。详见 [Ssstateen 单元](../notes/units/rva23s64-ssstateen-v1.md#evidence-table)与[结项案例审计](../notes/units/rva23s64-closeout-audit-v1.md#计划案例结果与范围)。 | 这是 Epic 5 唯一实际启动的 CPU 案例：隔离 Heliodor M/HS harness 观察到预期 gate trap 未出现，tohost 为 `0x02`，低于预期 `0x2B`，结果为 `run-fail`。结果只适用于该固定路径/模式，不代表 VS/VU 或完整 WARL/reset 矩阵。 |

[结项审计](../notes/units/rva23s64-closeout-audit-v1.md)区分了 testbench/build 阶段阻塞与目标运行后的失败。Epic 5 没有任何 CPU `run-pass`；Kunminghu 的 Mill/Verilator 工具链问题和 Heliodor testbench 检查问题都不能被记成 DUT 通过或失败。五专题详细输入、源码路径、测试子案例和缺口以各单元的证据表为准。

## 阶段结论及后续

Epic 5 的七个故事（Story 5.1–5.7）均完成后，阶段结论为 `accepted-with-open-items`（criteria: profiled；状态和范围见 [Epic 5 复盘](../_agile-output/implementation-artifacts/epic-5-retro-2026-10-14.md)）：它接受的是有边界的专题学习交付，不是五项 CPU 行为验证完成，更不是 RVA23 符合性声明。Epic 5 复盘把 checker 一致性、链接解析范围、CPU 验证准备门和前置结项摘要列为行动；四项行动的具体闭环证据见 [Epic 5 复盘的 Action item completion evidence](../_agile-output/implementation-artifacts/epic-5-retro-2026-10-14.md#action-item-completion-evidence-2026-10-14)。

Epic 6 是后续新增的动态验证阶段，不应回填到本阶段的结果表。例如，Epic 6 的 [Zifencei 代表性案例](../notes/units/rva23s64-zifencei-v1.md)后来有运行通过记录；[Sstc 单元](../notes/units/rva23s64-sstc-v1.md)则保留 Kunminghu 部分案例通过与 Heliodor gate 运行失败等不同结果。汇总结论仍为 `accepted-with-open-items`；完整逐项状态见 [Epic 6 复盘](../_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md)及专题运行记录。这样保留阶段边界，才能看清从“知道代码路径”到“观察 CPU 行为”之间还需要哪些工具、fixture 和结果证据。

下一篇回顾是 Stage 6：说明固定快照上的代表性 CPU 运行验证实际覆盖了什么、哪些结果失败或仍未运行，以及项目级结项结论为何仍有限定范围。
