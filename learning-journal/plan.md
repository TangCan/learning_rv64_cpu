---
title: RV64 双核访存微架构学习计划
status: in-progress
created: 2026-10-15
updated: 2026-10-15
---

# RV64 双核访存微架构学习计划

## 学习目标

对照 `sources.lock` 固定的 Kunminghu V2 与 Heliodor 快照，理解普通 RV64 标量 load、store 和一个共同访存 fault 如何经过各自微架构，直至结果提交或精确异常状态。学习记录要让读者既能按时间回顾探索过程，也能直接查阅整理后的技术结论。

本计划是原 RVA23 学习项目结项后的独立后续学习，不重开原 Epic/sprint，不修改上游 RTL，也不构成 RVA23 全量验证或 CPU 符合性证明。

## 学习顺序

| 阶段 | 主题与问题 | 学习活动 | 过程日志 | 知识沉淀 | 完成门槛 |
| --- | --- | --- | --- | --- | --- |
| A | 回顾已完成的六阶段学习历程 | 依据已有 Epic 记录、单元笔记、复盘和运行证据整理时间线；不虚构缺少依据的过程细节 | [Stage 1](2026-10-15-stage-1-add-pilot-retrospective.md)、[Stage 2](2026-10-15-stage-2-ooo-and-branch-retrospective.md) 回顾已完成；Stage 3–6 待回顾 | 既有 `notes/units/` 记录与 `notes/units/evidence/` | 每篇回顾都链接现有资料，并区分历史事实与事后总结 |
| B | 建立日志规则和路线导航 | 使用首页按阶段/时间组织文章；约定文章结构、证据状态和链接方式 | `learning-journal/index.md` 已建 | 沿用[学习记录与证据约定](../_agile-output/specs/spec-learning_rv64_cpu/learning-record-conventions.md) | 日志能链接到知识单元、固定快照和证据文件；计划/进行中/完成状态清楚 |
| 1 | `LD`：数据如何从指令到达目的寄存器并退休？ | 已复核两侧译码、地址生成、地址转换、缓存响应、写回与退休路径；区分源码结构和未观察状态 | [双核 LD 路径复核](2026-10-15-ld-path-review.md) | [`load-v2.md`](../notes/units/load-v2.md)，保留 [`load-v1.md`](../notes/units/load-v1.md) | 本次静态源码复核完成；案例运行仍未验证 |
| 2 | `SD`：何时提交，何时被写入路径接受？ | 已对照 StoreUnit/StoreQueue/ROB 与 Heliodor commit-store 路径，追踪普通对齐 DRAM `SD`；DRAM 可见性边界仍未验证 | [双核 SD 提交与写入边界](2026-10-15-sd-commit-write-boundary.md) | [`store-v1.md`](../notes/units/store-v1.md) | 本次静态路径追踪完成；案例未运行，未声称下游可见 |
| 3 | 共同 fault：Sv39 非规范地址 `LD` 如何成为精确异常？ | 已固定 S-mode、V=0、Sv39、VA `0x0000008000000000` 的普通 `LD`，静态追踪 fault 检测、ROB 保留、cause 与 trap 更新 | [Sv39 非规范地址 LD fault](2026-10-15-sv39-noncanonical-ld-fault.md) | [`sv39-load-fault-v3.md`](../notes/units/sv39-load-fault-v3.md)；保留 [`v2`](../notes/units/sv39-load-fault-v2.md) 与 [`v1`](../notes/units/sv39-load-fault-v1.md) | 本次静态路径复核完成；ACT 比较为 partial（Kunminghu 测试材料 unverified）；两侧动态 cause/CSR/redirect 未验证 |
| 4 | 总结：相同架构行为为何有不同实现路径？ | 已汇总阶段日志和知识单元，比较两种设计的路径、接受/提交边界和证据缺口 | [双核 LD、SD 与 Sv39 fault 综合](2026-10-15-load-store-fault-synthesis.md) | [`trace-matrix.md`](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md)、当前 [`notes/units/`](../notes/units/index.md) | 静态比较与导航完成；遗留动态边界和旧历程回顾已标明 |

## 每篇日志的结构

1. **本次问题**：这次想回答什么，为什么接着上次继续。
2. **探索过程**：检查了哪些规范章节、源码路径、测试源码或运行产物。
3. **发现**：分别记录已证实结论、反例/差异和未解问题。
4. **证据链接**：引用固定 snapshot ID、文件路径/行号、精确命令及产物路径（如有）。
5. **知识沉淀**：链接到稳定的 `notes/units/` 记录；博客日志保留过程，不复制整份技术结论。
6. **下一步**：写下自然引出的下一个问题，并链接到计划阶段。

## 证据规则

- 每项证据用两个独立字段记录：证据类型（`spec`、`design-doc`、`source`、`test-inspected`、`test-run`、`experiment`）和验证状态（`inspected`、`run-pass`、`run-fail`、`blocked`、`unverified`、`not-applicable`）。例如实际测试通过写作 `test-run` + `run-pass`；检查测试源码写作 `test-inspected` + `inspected`。
- 不从测试入口存在推断测试通过，不从启动日志推断内部微架构阶段实际发生。
- 记录输入、命令和运行输出到 `notes/units/evidence/`；知识结论保存在学习单元，过程反思保存在日志。
- 所有源码比较引用 [`sources.lock`](../sources.lock) 中的快照。若快照改变，先记录比较边界再继续。
- 只有当静态路径无法回答新的学习问题、且动态观察是必要目标时，才另行评估隔离 trace harness；本计划当前不要求新增 harness。

## 范围外

不穷举所有访存宽度、未对齐访问、原子/向量访问、缓存一致性、性能表现和页表组合；不修改上游 RTL；不把学习记录表述成 RVA23 符合性结论。

## 当前状态

- 计划：已建立草案。
- 历史阶段回顾：Stage 1 ADD 试点和 Stage 2 乱序依赖/分支恢复均已于 2026-10-15 基于现有记录回顾；Stage 3–6 待回顾。
- 前置勘察：已完成，结论见 [`feasibility.md`](../_agile-output/specs/spec-rv64-load-store-deep-dive/feasibility.md)。
- 日志首页和路线导航：已建立；Stage 1–2 历程文章已完成，Stage 3–6 尚待依据现有材料回顾。
- `LD`：已完成本次静态源码复核，日志与 load-v2 已发布；案例未运行。
- `SD`：已完成本次静态源码追踪，日志与 store-v1 已发布；案例未运行，DRAM 可见性未验证。
- `Sv39` 非规范 `LD` fault：已完成固定 tuple 的双核静态复核，审计日志与不可变 v3 已发布，v1/v2 保留；动态案例仍未验证。
- Story 1.4：六条路径、活动 ID、证据状态和固定快照已审计；fault v3 将 ACT 测试比较明确为 partial，见[审计日志](2026-10-15-three-case-evidence-audit.md)。
- 综合阶段：已完成静态综合和导航；双核差异为 LD 写回/退休门控、SD 接受终点及 fault 检测/异常保留路径各有实现，具体证据见[综合日志](2026-10-15-load-store-fault-synthesis.md)。当前未验证边界包括 LD hit/值/退休、SD 实际接受及 DRAM 可见性、fault 的动态 cause/CSR/redirect；fault 测试材料比较为 partial。下一步可依据现存证据回顾一项旧阶段（保留其余阶段 pending），或先规划新主题；如需运行结论，须另行记录固定输入、配置、命令和产物。
