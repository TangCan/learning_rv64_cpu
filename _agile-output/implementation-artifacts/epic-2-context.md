# Epic 2 Context: 追踪乱序处理器中的依赖与恢复

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

解释并比较 Kunminghu V2 与 Heliodor 中乱序处理的依赖和恢复路径：从重命名、发射、执行到提交追踪依赖指令，另以分支预测错误为例追踪错误路径指令的冲刷与正确执行恢复。产出可复查的双实现学习记录，帮助学习者理解关键状态变化及其正确性边界。Epic 2 是候选范围；只有 Epic 1 的 ADD 试点复盘明确给出 `ready`、授权 Epic 2 并确认范围与节奏后才启动。

## Stories

- Story 2.1: 追踪依赖指令的乱序执行与提交
- Story 2.2: 追踪分支冲刷与恢复

## Requirements & Constraints

- 每个学习单元从架构行为出发，追踪两种实现并形成一份可比较记录；说明适用规范、范围和明确列出的参数化子案例，未覆盖或未确认部分要标出。
- 每项比较结论都要链接到两边实现的证据。区分规范、设计文档、源码、检查过的测试、实际运行的测试和实验；代码检查不等于测试运行，未运行项目不得记为通过。
- 记录来源仓库、分支及完整 commit 快照 ID，使用稳定源码路径；每次单元记录引用对应快照。阶段自检须保存答案和证据，阶段完成还需至少一项有证据的解释、源码定位或测试/仿真检查。
- 单元记录使用中文；ISA 助记符、扩展名、符号和源码路径保留上游原文。记录以不可变的 `<unit_id>-vN.md` 保存，索引指向当前版本。
- 不在上游源码中做学习实验。若需要自建 harness 或实验，放在 `experiments/<unit>/` 并记录快照、输入、过程和观察结果。

## Technical Decisions

- 采用统一学习单元结构：必需 frontmatter 包含 `unit_id`、`stage_id`、`scope`、`exclusions`、`spec_refs` 和来源快照 ID；正文依次记录自检、架构行为与子案例、Kunminghu 路径、Heliodor 路径、比较结论、证据表、学习总结和未解问题。
- 每个证据条目标明类型（`spec`、`design-doc`、`source`、`test-inspected`、`test-run` 或 `experiment`）及状态（`inspected`、`run-pass`、`run-fail`、`unverified` 或 `not-applicable`）。运行证据需记录命令、配置、输入/案例、预期与观察结果及产物路径；只有观察到结果才能标记 `run-pass`。
- 以选定的有界依赖指令案例及分支恢复场景组织追踪；比较重命名、发射、执行、提交、分支结果判定、错误路径识别、冲刷范围和恢复后的状态/控制流。某阶段不适用或无法确认时明确说明，不推断缺失实现或验证结果。

## Cross-Story Dependencies

- Epic 2 启动依赖 Epic 1 Story 1.3 的明确 `ready` 决定，且决定必须点名授权本史诗并确认范围和节奏。
- Story 2.1 与 Story 2.2 均依赖已固定的两边来源快照及统一记录模板（Epic 1 的基础交付）；两者各自形成独立的版本化单元记录。阶段路线索引两份记录的自检答案，并据此记录阶段完成。
