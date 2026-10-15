# Stage 4 回顾：建立 RVA23 必选项映射

回顾日期：2026-10-15

> 本文根据 Git 历史、Story 规格、覆盖目录、审计记录和 Epic 复盘事后整理，不是 2026-10-12 当时的连续会话记录。提交时间可以定位材料进入版本历史的时间，不能还原未记录的操作顺序或对话。

## 本次问题

Stage 4 要把 RVA23U64 与 RVA23S64 的必选要求拆成可追踪的条目，分别关联 Kunminghu、Heliodor 的学习状态、范围说明和证据。这个目录回答“哪些要求已调查、证据到哪里”，不回答“处理器是否已完整符合 RVA23”。

## 可追溯的学习过程

- **2026-10-12 16:29 +08:00：建立规范清单。** `0589acd76062f2e604720080d09a59737b6326be` 引入 RVA23 Profile v1.0 §3.1 的必选项清单和稳定身份键，作为 U64/S64 后续映射的基线。
- **16:46–18:21：按领域填充两侧映射。** 后续提交依次覆盖 U64 标量、浮点、向量、内存/缓存，以及 S64 监督陷阱、地址转换和 Hypervisor 专题。`f2a6809d022cd58ef2a2e7e20381a5b57022af57` 完成最后的 Hypervisor 映射；各子领域的结论仍以各自学习单元的固定快照与证据为准。
- **18:29–18:30：审计并完成 Epic。** `e6672fb5dd9463e5773ab6665e8f04e39e8ccb0c` 加入 Story 4.10 审计，随后 `80547d5badc125dd0dc09a61e4e3e8b45458d1e4` 完成 Epic。该 Epic 的 13 个提交涉及覆盖表、故事规格、学习记录和校验工具，没有修改 CPU RTL。
- **2026-10-13：复盘记录补写。** `e3a5474bbe867a83da21b8fb7c8c8ced48f9f1dc` 提交 Epic 4 回顾，结论为 `accepted-with-open-items`。回顾发现 checker 对某些格式错误的覆盖行校验不足、审计摘要遗漏 Heliodor Ssstateen，以及 Epic 3 的复盘门未能在 Epic 4 开始前生效。文件日期标注 10-12，但该回顾实际在 10-13 进入 Git 历史。
- **10-13–10-14：修复审计与流程待办。** `9ef6b5ab25eee00febb76a6b7c5d946f260217bf` 关闭 Epic 4 行动项 6–8 并加入 checker 回归测试；`4394eb9c626c6405a1ae1a354fdd2a79da92ad30` 的[闭环记录](../_agile-output/implementation-artifacts/epic-4-retro-2026-10-12.md#action-item-follow-through-verified-2026-10-14)核验了 profile 行、实现状态格、摘要计数、去重关系和证据回链，补齐 S64 未调查范围说明，并确认后续 Epic 启动前须完成前序复盘。
- **后续专题阶段：更新目录证据。** Epic 5 学习计划于 2026-10-13 启动（`d3d836a179789829182e5aeebfcd3079328d5ab3`）；Epic 6 CPU 行为对照在 2026-10-15 的 `93bd409f6b375e683fca04cc4e70637ec7144b55` 完成。见 [Epic 5 回顾](../_agile-output/implementation-artifacts/epic-5-retro-2026-10-14.md)和[Epic 6 回顾](../_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md)。这些后续工作更新了当前 [`rva23-coverage.md`](../notes/rva23-coverage.md) 的状态，但不应倒算成 Story 4.10 当时已经做完的调查。

上述时间是 Git 作者时间（`%aI`，+08:00），可用完整 SHA 运行 `git show -s --format='%H %aI %s' <完整 SHA>` 复核。Stage 4 所引用的实现快照固定为 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 和 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。

## 目录结构与关键发现

Story 4.10 按 RVA23 Profile v1.0 §3.1 得到 **92 个 profile 行**：RVA23U64 34 行、RVA23S64 58 行；每行分别记录两个实现，因此有 **184 个状态格**。按继承关系去重后为 **59 项规范要求**：U64 的 34 项，加 S64 独有的 25 项（S64 基础要求 1 项、S64 特有要求 24 项）；S64 的 33 个继承行仍在 S64 表中可见，但不重复计为新要求。Sha 按 8 个组成要求展开，而不是另加一个合并项。

这三个数字计量不同对象。`profile 行`保留 profile/section 身份，`状态格`记录某实现的调查范围，`去重要求`排除继承重复。覆盖状态（如 `partially-studied`、`studied-unverified`、`evidence-observed`、`not-present`）也不等于单条证据的 `Kind`/`Status`，更不是二元的通过/失败。

| 结论 | 证据与边界 |
| --- | --- |
| 覆盖表能逐项列出官方 mandatory 键、继承关系、双方调查状态及证据链接；Story 4.10 校验了清单、行数和链接结构。 | 依据 [RVA23 必选项审计](../notes/units/rva23-mandatory-coverage-audit-v1.md) 和 [当前覆盖图谱](../notes/rva23-coverage.md)。审计没有重新认证或重审每个专题的全部源码结论。 |
| Story 4.10 时，四个 S64 专有主题 Zifencei、Sstc、Sscofpmf、Ssnpm 两侧都尚未做专题调查；审计摘要还漏列 Heliodor Ssstateen 的未调查状态。 | 这是 2026-10-12 的历史截点。Epic 5/6 后续做了有限静态/运行调查；某些案例仍有阻塞、run-fail 或未验证项，必须查看当前目录和对应单元，不能沿用旧计数描述现态。 |
| Epic 4 的 `accepted-with-open-items` 接受的是“学习型对照图谱”交付；审计发现的 checker 边界、摘要完整性和复盘门问题随后有对应闭环记录。 | 后续行动项要求 checker 拒绝重复键、同格多状态、错误 section 等输入，并加入回归测试；这验证目录工具，不等于验证 CPU 行为。 |

因此，92/184/59 是目录结构和审计口径，不是“覆盖了多少百分比”的指标。`not-studied` 不是实现不存在；`not-present` 也只能用于证据限定的实现路径。单项测试、设计声明或局部 RTL 不能推出完整 profile 符合性。

## 知识沉淀

- [RVA23 必选项覆盖图谱](../notes/rva23-coverage.md)：当前逐项映射、状态规则、可选项分区和开放边界。
- [Story 4.10 审计记录](../notes/units/rva23-mandatory-coverage-audit-v1.md)：原始计数、方法和 Story 4.10 状态截点。
- [Epic 4 回顾](../_agile-output/implementation-artifacts/epic-4-retro-2026-10-12.md)：验收结论、审计发现及行动项闭环。
- [RVA23S64 深度学习结项审计](../notes/units/rva23s64-closeout-audit-v1.md)：后续专题调查与运行证据的范围和限制。

## 下一步

日志计划的下一个历史阶段是 Stage 5：深入比较 RVA23S64 专题并检查学习交付证据。回顾应把每个专题的规范要求、源码映射、测试阻塞和实际运行分别呈现，不能用阶段 4 的目录完整性替代行为验证。
