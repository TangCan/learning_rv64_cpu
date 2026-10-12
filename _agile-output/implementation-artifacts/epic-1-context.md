# Epic 1 Context: 完成双核 ADD 对照试点

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

建立 Kunminghu V2 与 Heliodor 的可追溯源码和环境基线，并用共同记录方法完成 ADD 的双实现对照试点。该阶段验证如何把架构行为连到两边源码及验证证据，为后续学习提供可复查、可复习的基础；ADD 复盘还将决定后续哪些候选史诗获准启动。

## Stories

- Story 1.1: 建立源码与环境基线
- Story 1.2: 建立统一的学习记录模板
- Story 1.3: 完成 ADD 双核对照试点

## Requirements & Constraints

- 为两边来源记录仓库 URL、分支、完整 commit SHA 和稳定快照 ID；快照变化需有日期事件。学习结论应关联规范及两边的源码、设计或验证证据。
- 盘点两边 HDL、核心源码位置、已有测试入口，并记录所依据的 commit。记录主机 OS、可用磁盘和内存、工具链及测试运行条件；无法运行的项目记录阻塞，不得描述为已观察到的运行结果。
- 学习记录使用中文，保留 ISA 名称、符号和源码路径的上游拼写。结论要从架构行为追踪到两边实现，并以双方证据支持差异或相同结论；区分检查过的材料和实际运行过的测试。未运行测试不得标为通过。
- 单元记录采用不可变版本文件和索引；实验如有，放在 `experiments/<unit>/`，记录快照、输入、步骤和结果。不得原地修改上游源码，也不得复制或重新分发上游源码。
- ADD 试点复盘必须记录一个 `ready`、`adjust` 或 `defer` 结果。只有 `ready` 明确列出获准启动的史诗并确认范围与节奏时，才可开始相应后续工作；`adjust` 后需修订规划并重新得到 `ready`。

## Technical Decisions

- 比较采用同一学习单元记录两边实现，并关联固定来源快照、规范版本与证据 ID。运行证据需保留命令、配置、输入、预期和观察结果及产物位置。
- Story 1.1 已依据仓库体量与主机资源选择 Git 忽略的 `sources/`，以浅克隆固定 Kunminghu `kunminghu-v2` 与 Heliodor `master` 快照；精确 SHA 与 snapshot ID 见项目根目录 `sources.lock`。子模块和工具链仍未初始化/安装，CPU 测试尚未运行。
- 不要求必须运行测试；若当前环境不支持，使用源码/规范检查并明确记录运行阻塞和证据边界。

## Cross-Story Dependencies

Story 1.1 固定来源快照并记录源码、测试及环境基线，供 Story 1.2 的记录规范和 Story 1.3 的 ADD 对照引用。Story 1.3 依赖前两项完成；其复盘门槛控制后续候选史诗的启动。
