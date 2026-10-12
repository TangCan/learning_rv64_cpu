---
id: SPEC-learning_rv64_cpu
companions:
  - learning-route.md
  - learning-record-conventions.md
  - rva23-coverage-rules.md
  - architecture-diagrams.md
  - ../../planning-artifacts/prds/prd-learning_rv64_cpu-2026-10-12/prd.md
  - ../../planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/epics.md
sources: []
---

# RV64 CPU 双项目学习规格

## Why

这是一个以学习机会为出发点的个人项目：通过对照香山 Kunminghu V2 与 Heliodor 对同一架构功能的实现，建立从 RISC-V 规范到高性能 CPU 微架构和源码的连贯理解。两边源码、测试和设计文档提供不同实现的观察证据，官方 RVA23 Profile 为必选能力提供共同基线。

## Capabilities

- **CAP-1**
  - **intent:** 学习者能从架构行为追踪到 Kunminghu 与 Heliodor 的实现并比较设计。
  - **success:** ADD 试点记录有适用规范、两边关键路径、带证据的差异或相同点、自检答案和未解问题；复盘给出 `ready`、`adjust` 或 `defer`，并由 `ready` 明确列出授权启动的 Epics 2–4。
- **CAP-2**
  - **intent:** 学习者能按先修路线逐步理解指令执行、乱序处理、内存/特权和 RVA23 扩展。
  - **success:** 每个阶段都有可复习的学习记录、自检答案，以及至少一项带证据的解释、源码定位或测试/仿真检查。
- **CAP-3**
  - **intent:** 学习者能评估两边实现与 RVA23U64/RVA23S64 必选要求之间的映射。
  - **success:** 每项官方必选要求对两个实现分别有明确状态、位置或范围决定及理由；已有证据关联证据 ID，尚未调查的条目标为 `not-studied`，不虚构证据。
- **CAP-4**
  - **intent:** 学习者能在需要时用隔离实验检查理解。
  - **success:** 学习者自建的每项实验都引用源码快照并记录输入、步骤和观察结果，且与上游源码分开；未运行的验证不会报告为通过。

## Constraints

- 对照对象是 Kunminghu `kunminghu-v2`（V2R2 文档/配置）与 Heliodor 上游；用项目级 `sources.lock` 固定完整 commit SHA 和快照 ID。
- 以官方 RVA23 Profile v1.0 的规范要求为依据。必选项、可选项、建议、上游自述和本项目证据要分别表达；本项目不作认证声明。
- 学习记录使用统一结构，中文解释保留 ISA 名称、扩展名、符号和源码路径的上游写法。比较结论需有两边证据，区分源码检查和实际运行。
- 不在上游源码中直接修改，不复制或重新分发上游源文件。学习者编写的 harness 和实验存放在 `experiments/<unit>/`。
- 首轮先完成来源/环境基线和 ADD 对照试点；复盘必须记录 `ready`、`adjust` 或 `defer`。`ready` 确认记录方法、列明授权启动的 Epic 2–4 子集及节奏；`adjust` 要先修订路线/史诗，之后仍需新 `ready`；`defer` 暂停后续史诗。

## Non-goals

- 实现一颗新的完整 RV64 CPU、流片或追求性能指标。
- 穷举所有可选扩展、SoC 外设或工业实现细节。
- 证明本学习项目或所读实现已获得 RVA23 官方认证。

## Success signal

学习者完成 ADD 双核试点，能从规范定位两边实现并用证据说明结论；随后各阶段都有通过自检的记录。RVA23U64 与 RVA23S64 的每项必选要求最终都有明确状态和理由，已有证据可回查，未调查或未验证的项目不会被误报为已验证。

## Assumptions

- 项目主要由 Richard 个人使用；所需的 Chisel/Scala 与 Veryl 阅读基础可在学习过程中补足。

## Open Questions

- 每周投入时间、学习节奏和完成期限是什么？
- 当前主机是否能运行两个上游项目的仿真/测试工具链？
- 上游仓库克隆到 Git 忽略的 `sources/` 还是同级目录？
- 是否公开发布笔记？若公开，许可证、引用和发布范围如何处理？
- ADD 试点之后是否安排 RTL 修改或其他动手实验？
