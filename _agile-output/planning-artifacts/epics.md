---
status: final
stepsCompleted: [1, 2, 3, 4]
updated: 2026-10-13
inputDocuments:
  - _agile-output/planning-artifacts/prds/prd-learning_rv64_cpu-2026-10-12/prd.md
  - _agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md
  - _agile-output/planning-artifacts/research/technical-rv64-cpu-learning-completion-plan-for-re-2026-10-13/research.md
---

# learning_rv64_cpu - RV64 Learning Plan

## Overview

本文件把《RV64 CPU 双项目学习计划》的需求和架构约束整理为后续史诗与故事拆分的输入。项目通过对照香山 Kunminghu V2 与 Heliodor 学习 RV64 CPU；学习笔记和可复查证据是主要成果。

## Requirements Inventory

### Functional Requirements

- **FR-1：记录来源快照。** 每份对照记录注明两边仓库链接、分支和所读 commit；版本更新时可识别记录所依据的版本。
- **FR-2：引用规范与验证证据。** 每份对照记录指向适用 ISA/profile 规范和实现测试或验证证据；缺少证据时明确标为未验证。
- **FR-3：从架构行为追踪到实现。** 从规范描述或指令行为追踪至两边实现的关键阶段和结果，不止记录文件名或复制代码片段。
- **FR-4：总结差异及依据。** 每份记录至少说明一项有源码、设计文档或验证依据的实现差异；若实现方式相同，也记录结论依据。
- **FR-5：完成首轮对照并通过阶段门。** ADD 试点复盘必须给出 `ready`、`adjust` 或 `defer`；`ready` 须列明获准启动的史诗 2–5 子集并确认其范围与节奏。
- **FR-6：逐步覆盖核心主题。** 按阶段学习来源与环境、指令路径、乱序处理器、内存与特权、RVA23 扩展及 RVA23S64 深度对照；每阶段记录规范行为、两边源码路径、验证依据和自检答案，并按先修条件推进。
- **FR-7：对照 RVA23 要求。** 将 `RVA23U64` 与 `RVA23S64` 全部必选要求映射到实现对照或明确范围决定，注明规范依据、实现位置和验证状态；不把 README 声明当作完整符合证明，也不以官方认证为目标。
- **FR-8：记录可复习的学习成果。** 每个完成单元包含中文总结、来源快照、可复查引用和未解问题；如有实验，记录运行条件和观察结果。
- **FR-9：使用证据检查理解。** 每阶段至少通过解释、源码定位或测试/仿真检查理解；未运行的测试不能记为通过。
- **FR-10：完成 RVA23S64 深度对照单元。** 完成 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen 五个主题的双实现记录，分别追溯固定快照、规范行为、源码路径、测试证据和验证状态；可运行案例须运行，受阻或未实现项须保留具体边界。
- **FR-11：审计最终结项证据。** 将五个深度单元关联到必选项映射，检查证据链、自检答案和范围内子案例状态，记录检查器结果、剩余限制及复盘决定；学习结项不等于 CPU 获得 RVA23 符合性或认证。

### NonFunctional Requirements

PRD 没有单列编号的 NFR。以下为从 PRD 的质量目标和约束归纳的 NFR，供确认：

- **NFR-1（可追溯性）：** 学习结论能回链到规范版本、上游仓库和固定 commit，以及相关源码、测试或实验材料。
- **NFR-2（可复现与证据准确）：** 运行证据记录命令、配置、输入、预期与观察结果；代码检查与实际运行明确区分，不把未运行的测试标记为通过。
- **NFR-3（可复习性）：** 学习解释使用中文，ISA 名称、扩展名、符号和源码路径保留上游原文；记录结构稳定，支持不同实现横向比较。
- **NFR-4（来源边界）：** 不在上游源码中直接做学习实验，不复制或重新分发上游源码；自建实验与学习记录分开放置。
- **NFR-5（声明边界）：** RVA23 必选映射、上游项目自述和本项目实际观察的证据分开表达；不宣称本项目或上游获得官方认证。
- **NFR-6（状态和术语准确）：** 活动配置、源码静态检查、测试文件检查、实际运行结果和阻塞状态分别记录；规范版本或字段命名不一致时先核实对应关系，不将不确定项表述为通过。

### Additional Requirements

- 建立项目级 `sources.lock`，为 Kunminghu V2（V2R2 文档/配置）与 Heliodor 固定 commit；每个学习单元引用快照 ID。快照变更需留下日期记录；有意偏离基线时注明原因和跨单元比较限制。
- 使用统一的学习单元模板和稳定字段；一个单元一份不可变版本记录，文件名为 `<unit_id>-vN.md`，索引指向当前版本。记录范围、排除项、规范引用、参数化子案例、两边实现路径、比较结论、证据表、总结和问题。
- 每项比较结论关联两边证据 ID。证据类型包括规范、设计文档、源码、检查过的测试、运行过的测试和实验；证据状态要区分已检查、运行通过、运行失败、未验证和不适用。
- RVA23 覆盖表按官方必选要求的精确 ID 和规范版本逐项列出，对 Kunminghu 和 Heliodor 分别记录状态、实现位置或范围决定、理由、覆盖子案例和证据 ID；必选项、可选项和上游自述分开。
- 单元记录保存本单元自检问题和答案；阶段路线索引这些答案并记录阶段完成。阶段完成还需至少一项带证据的解释、源码定位或测试/仿真检查。
- 不修改上游源码。学习者编写的 harness 或实验放在 `experiments/<unit>/`，记录源码快照、输入、过程和观察结果。
- 环境阶段记录主机 OS、可用磁盘/内存、隔离方式、工具链版本和配置、生成物位置、安装/清理步骤、确切命令和保留的输出；如果不能运行，记录阻塞原因并仅使用源码/规范检查证据。
- 架构将上游 checkout 位置暂定为 Git 忽略的 `sources/`，需在克隆前确认仓库体量、磁盘空间和工作区。工具链及测试命令在选定快照与主机后确定。
- 项目当前不以完整 CPU 实现、性能测量、穷举可选扩展、公开发布或官方认证为范围；公开笔记前检查许可证和引用。
- Epic 5 开始前确认两边源码快照、Kunminghu 活动 CSR/配置路径、Heliodor 的测试入口与 Ssstateen 行为边界，以及 ACT4/Sail、编译器和仿真工具版本；前置条件若无法满足，须记录阻塞和影响范围。
- RVA23S64 的五个深度主题为 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen。必选项图谱与深度学习记录是不同产物；单个源码入口或测试通过不能替代扩展行为覆盖。

### UX Design Requirements

无 UX 设计文档；本项目当前是个人学习记录，不包含 UI 设计交付物。

### FR Coverage Map

FR-1: Epic 1 — 建立两边来源快照记录方式。
FR-2: Epics 1–5 — 每个单元关联适用规范和验证证据，缺失时标明未验证。
FR-3: Epics 1–5 — 从架构行为追踪到实现；Epic 4 对 profile 要求追踪到实现或范围决定。
FR-4: Epics 1–5 — 给出有依据的实现差异或相同点结论。
FR-5: Epic 1 — 完成 ADD 对照试点并复核方法；`ready` 仅授权列明的 Epics 2–5。
FR-6: Epics 1–5 — 按来源环境、指令路径、乱序、内存特权、RVA23 图谱和深度对照路线分阶段学习。
FR-7: Epics 4–5 — Epic 4 建立 RVA23U64 与 RVA23S64 必选项图谱；Epic 5 深入检查五个 RVA23S64 主题。
FR-8: Epics 1–5 — 每个完成单元保存总结、快照、引用和问题；有实验时记录条件与结果。
FR-9: Epics 1–5 — 每阶段通过带证据的解释、源码定位或测试/仿真检查。
FR-10: Epic 5 — 完成五个 RVA23S64 深度对照单元，计划内可运行案例有运行结果或具体阻塞。
FR-11: Epic 5 — 审计证据链和学习闭环；整体完成声明不代表符合性或认证。

## Workstream Summary

史诗 2–5 是候选 backlog，不代表已批准启动。Epic 1 Story 1.3 的 ADD 试点复盘必须记录 `ready`、`adjust` 或 `defer`。`ready` 须确认记录方法、获准启动的史诗范围和学习节奏，并只授权复盘中列明的史诗；`adjust` 先更新 PRD、史诗和路线，修订后仍须记录 `ready` 才能启动；`defer` 暂停后续史诗，直到复盘另行决定。复盘还须确认是否加入 `BEQ`、`LD/SD` 以及后续主题范围和节奏。Epic 5 另须在 Epic 4 图谱完成后通过源码活动路径与工具可用性前置门。

### Epic 1: 完成双核 ADD 对照试点
学习者熟悉两个源码仓库和版本快照，按统一方法完成首份对照记录，并检查记录方法是否适合后续学习。
**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6 (阶段 0–1), FR-8, FR-9

### Epic 2: 追踪乱序处理器中的依赖与恢复
学习者能够解释重命名、发射、执行、提交及分支恢复路径，并形成有证据的双实现比较记录。
**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 2), FR-8, FR-9

### Epic 3: 解释内存与特权行为
学习者能够追踪访存、异常或地址转换路径，比较两边实现并记录验证边界。
**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 3), FR-8, FR-9

### Epic 4: 建立 RVA23 必选项对照图谱
学习者能够逐项映射 RVA23U64 与 RVA23S64 必选要求，分别记录 Kunminghu 与 Heliodor 的实现位置、学习状态和证据。
**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8, FR-9

### Epic 5: 完成 RVA23S64 双实现深度学习与结项审计
学习者能够深入对照 Zifencei、Sstc、Sscofpmf、Ssnpm 和 Ssstateen 的规范行为与 Kunminghu/Heliodor 实现，记录测试与验证边界，并审计整体学习证据。对于未实现、未验证或环境受阻项，学习者给出明确结论和证据边界；学习结项不代表 CPU 获得 RVA23 符合性或认证。
**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 5), FR-7, FR-8, FR-9, FR-10, FR-11

每个获准启动的史诗须交付可独立复习的阶段成果，并复用统一的来源和证据规则。

## Epic 1: 完成双核 ADD 对照试点

学习者熟悉两个源码仓库和版本快照，按统一方法完成首份对照记录，并检查记录方法是否适合后续学习。

### Story 1.1: 建立源码与环境基线

**FRs covered:** FR-1, FR-6 (阶段 0), FR-8, FR-9

As a learner,
I want to pin the Kunminghu and Heliodor source versions and record source navigation and environment information,
So that later ADD comparisons can be traced to explicit evidence.

**Acceptance Criteria:**

**Given** the two selected upstream repositories, **When** I establish the source baseline, **Then** I create or update the project-level `sources.lock` with each repository URL, branch, full commit SHA, and stable snapshot ID and record a dated snapshot-change event when the lock changes.

**Given** the two pinned snapshots, **When** I complete the initial source survey, **Then** I record each project's hardware description language, core source locations, and existing test entry points with the relevant commit.

**Given** the current learning host, **When** I document the environment, **Then** I record the OS, available disk and memory, toolchains, and test execution conditions; anything that cannot yet run has a blocker recorded and is not described as an observed run.

**Given** repository size and host resources, **When** I choose a checkout location, **Then** I record the selected local or sibling location and reason; if using a project-local checkout, I place it under Git-ignored `sources/`; if cloning is deferred, I record why and the condition that will trigger the decision.

**Given** the source/environment stage, **When** I complete its self-check, **Then** I save an answer identifying the core source and test locations in both projects and cite the source-location evidence.

### Story 1.2: 建立统一的学习记录模板

**FRs covered:** FR-2, FR-8

As a learner,
I want to use a consistent comparative learning-record template,
So that each unit can compare both implementations in the same structure and trace its supporting evidence.

**Acceptance Criteria:**

**Given** the agreed architecture rules, **When** I create the learning-record template, **Then** it includes `unit_id`, `stage_id`, scope, exclusions, specification references, source snapshot IDs, and ordered sections for self-check, architectural behavior and subcases, both implementation paths, comparison claims, evidence, learner summary, and open questions.

**Given** a comparison claim, **When** I record it, **Then** it links to evidence IDs for both implementations, and the evidence table distinguishes specification, design document, source, inspected test, executed test, and experiment evidence, using statuses `inspected`, `run-pass`, `run-fail`, `unverified`, and `not-applicable`.

**Given** a test or experiment run, **When** I record its evidence, **Then** I include the command, configuration, input, expected result, observed result, and artifact path; an unexecuted item is never labeled as a passing run.

**Given** a Chinese learning record, **When** I use the template, **Then** ISA names, extension names, symbols, and source paths retain upstream spelling, and uncovered parameterized subcases are explicitly listed.

### Story 1.3: 完成 ADD 双核对照试点

**FRs covered:** FR-2, FR-3, FR-4, FR-5, FR-6 (阶段 1), FR-8, FR-9

As a learner,
I want to trace ADD from its architectural behavior to both Kunminghu and Heliodor implementations,
So that I can validate the comparative learning method with an evidence-backed example.

**Acceptance Criteria:**

**Given** the pinned source snapshots and learning-record template, **When** I complete the ADD learning record, **Then** I describe its observable architectural behavior and applicable specification and trace the key decode, execution, and result writeback paths in both implementations.

**Given** both implementation paths, **When** I compare their designs, **Then** I record at least one difference supported by evidence from both sides, or record the evidence supporting a conclusion that their implementations are alike.

**Given** available tests or verification materials, **When** I include them in the learning record, **Then** I distinguish inspected materials from tests actually run and record the relevant evidence; tests not run are marked unverified.

**Given** this learning unit, **When** I complete its self-check, **Then** I save an explanation of ADD behavior, source locations in both implementations, and one evidence-backed understanding check.

**Given** the pilot record is complete, **When** I review the method, **Then** I document reusable parts of the template, gaps encountered, and recommended changes, save the ADD record as a versioned file, and point the unit index to the current version.

**Given** the ADD record and method review, **When** I decide whether to continue, **Then** I record exactly one gate outcome: `ready` (confirm the method, name the Epics among 2–5 authorized to start, and confirm scope/cadence), `adjust` (revise the PRD, epics, and route, then record a new `ready` before starting), or `defer` (pause them until a later review); no later epic starts without an explicit `ready` that names it.

**Given** I create a learner-authored harness or experiment during the pilot, **When** I save it, **Then** I keep it under `experiments/ADD/`, record its source snapshot, inputs, procedure, and observed result, and do not edit upstream source in place; if no experiment is needed, I record that none was created.

## Epic 2: 追踪乱序处理器中的依赖与恢复

候选史诗；仅在 Story 1.3 复盘明确给出 `ready`、列出本史诗并确认其范围后启动。

学习者能够解释重命名、发射、执行、提交及分支恢复路径，并形成有证据的双实现比较记录。

### Story 2.1: 追踪依赖指令的乱序执行与提交

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 2), FR-8, FR-9

As a learner,
I want to trace a set of data-dependent instructions through both out-of-order processors,
So that I can understand the key state and control paths from rename through commit.

**Acceptance Criteria:**

**Given** the pinned source snapshots for both implementations, **When** I create the dependency learning record, **Then** I select a bounded producer/consumer instruction example and explain its architectural result.

**Given** the instruction dependency, **When** I trace Kunminghu and Heliodor, **Then** I record applicable rename, issue, execution, and commit paths and key state changes; any inapplicable or unconfirmed stage is identified explicitly.

**Given** both implementation paths, **When** I compare them, **Then** each comparison claim links to evidence IDs from both sides and distinguishes source inspection from tests actually run.

**Given** the learning unit is complete, **When** I save it, **Then** I use an immutable `<unit_id>-vN.md` filename and update the unit index to identify the current revision.

**Given** the completed record, **When** I answer its stage self-check, **Then** I can explain how the dependency preserves correctness and locate at least one key structure and relevant verification boundary in each implementation.

### Story 2.2: 追踪分支冲刷与恢复

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 2), FR-8, FR-9

As a learner,
I want to trace a recovery path after a branch prediction error,
So that I can compare how both processors discard wrong-path work and resume correct execution.

**Acceptance Criteria:**

**Given** the pinned source snapshots for both implementations, **When** I create the branch recovery learning record, **Then** I describe the selected branch behavior, recovery scenario, and scope; if an actual test or configuration cannot be confirmed, I mark it unverified.

**Given** the recovery scenario, **When** I trace both implementations, **Then** I record branch outcome determination, wrong-path detection, squash scope, and key state or control-flow changes after recovery, with source locations.

**Given** both recovery paths, **When** I compare them, **Then** each claim links to evidence IDs from both sides and distinguishes source inspection, inspected tests, and actual run results.

**Given** the learning unit is complete, **When** I save it, **Then** I use an immutable `<unit_id>-vN.md` filename and update the unit index to identify the current revision.

**Given** the completed record, **When** I answer the stage self-check, **Then** I explain how recovery prevents wrong-path instructions from committing and identify at least one verification boundary or unverified case.

## Epic 3: 解释内存与特权行为

候选史诗；仅在 Story 1.3 复盘明确给出 `ready`、列出本史诗并确认其范围后启动。

学习者能够追踪访存、原子操作以及异常或地址转换路径，比较两边实现并记录验证边界。

### Story 3.1: 追踪普通访存路径

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 3), FR-8, FR-9

As a learner,
I want to trace a load or store from its architectural behavior through both LSU and cache paths,
So that I can understand how a memory access is processed and produces an observable result.

**Acceptance Criteria:**

**Given** the pinned source snapshots for both implementations, **When** I select a bounded load or store case, **Then** I record its architectural behavior, applicable specification, and excluded subcases.

**Given** the selected memory access, **When** I trace both implementations, **Then** I record applicable address generation, LSU request, cache or downstream interaction, and response or write path, with source locations.

**Given** both memory paths, **When** I compare them, **Then** each claim links to evidence IDs from both sides and identifies whether tests were inspected, run, or remain unverified.

**Given** the learning unit is complete, **When** I save it, **Then** I use an immutable `<unit_id>-vN.md` filename and update the unit index to identify the current revision.

**Given** the learning record, **When** I complete its stage self-check, **Then** I explain the key path for this access and identify at least one relevant verification boundary.

### Story 3.2: 对照原子内存操作

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 3), FR-8, FR-9

As a learner,
I want to trace one class of atomic memory operation through both implementations,
So that I can understand its architectural guarantees and how it differs from ordinary memory access.

**Acceptance Criteria:**

**Given** the pinned source snapshots for both implementations, **When** I select an atomic operation class supported by source evidence, such as an AMO or LR/SC, **Then** I record its architectural behavior, applicable specification, scope, and excluded subcases.

**Given** the selected operation, **When** I trace both implementations, **Then** I record how the request enters the memory subsystem, how atomicity is maintained, and how the result or state is returned; any unsupported conclusion is marked unverified.

**Given** both implementation paths, **When** I compare them, **Then** each claim links to evidence IDs from both sides and distinguishes inspected tests from tests actually run.

**Given** the learning unit is complete, **When** I save it, **Then** I use an immutable `<unit_id>-vN.md` filename and update the unit index to identify the current revision.

**Given** the completed record, **When** I answer its stage self-check, **Then** I explain the selected operation's architectural difference from ordinary load/store and identify a relevant verification boundary.

### Story 3.3: 追踪异常或地址转换路径

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 3), FR-8, FR-9

As a learner,
I want to trace one exception-handling or address-translation event,
So that I can understand how privileged state affects a memory result or control flow.

**Acceptance Criteria:**

**Given** the pinned source snapshots for both implementations, **When** I select an exception or address-translation event supported by source evidence, **Then** I record its trigger condition, relevant privilege mode, architectural result, and scope.

**Given** the selected event, **When** I trace both implementations, **Then** I record event detection, relevant state updates where applicable, and subsequent control flow or translation result, with source locations.

**Given** both implementation paths and available verification materials, **When** I compare them, **Then** each claim links to evidence IDs from both sides and distinguishes source inspection, inspected tests, and actual run results.

**Given** the learning unit is complete, **When** I save it, **Then** I use an immutable `<unit_id>-vN.md` filename and update the unit index to identify the current revision.

**Given** the completed record, **When** I answer its stage self-check, **Then** I explain how the event affects memory access or privileged control flow and identify a verification boundary or unverified portion.

## Epic 4: 建立 RVA23 必选项对照图谱

候选史诗；仅在 Story 1.3 复盘明确给出 `ready`、列出本史诗并确认其范围后启动。

学习者能够逐项映射 RVA23U64 与 RVA23S64 必选要求，分别记录 Kunminghu 与 Heliodor 的实现位置、学习状态和证据。

### Story 4.1: 建立官方必选项清单

**FRs covered:** FR-7

As a learner,
I want to create a complete checklist of mandatory requirements from the official RVA23 specification with stable identifiers,
So that I can compare both implementations item by item without omitting inherited requirements or misclassifying optional items.

**Acceptance Criteria:**

**Given** the official RVA23 Profile specification, **When** I create the inventory, **Then** I record its version and ratification status and assign each mandatory RVA23U64 and RVA23S64 requirement a stable key containing profile, specification version, and requirement identifier.

**Given** RVA23S64 includes mandatory unprivileged requirements from RVA23U64, **When** I represent this inheritance, **Then** the inventory marks inherited requirements explicitly without omitting them or claiming coverage twice.

**Given** mandatory requirements, optional items, recommendations, and upstream implementation claims, **When** I organize the inventory, **Then** I identify them separately and include normative behavioral requirements, not only extension names.

**Given** each inventory item, **When** later stories map the implementations, **Then** separate fields are available for Kunminghu and Heliodor status, implementation location or scope decision, rationale, subcases, and evidence IDs.

**Given** each implementation status, **When** I classify an inventory row, **Then** I use `not-studied` (in scope but not investigated), `partially-studied`, `studied-unverified`, `evidence-observed` (project evidence only, not certification), `not-present` (absence supported by inspected evidence), or `out-of-scope` (explicit learner decision with rationale); unavailable evidence is not silently treated as absence.

### Story 4.2: 映射 RVA23U64 基础整数与标量要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map the RVA23U64 base integer and non-floating-point, non-vector scalar requirements item by item,
So that I can identify each implementation location and current evidence status.

**Acceptance Criteria:**

**Given** the official inventory from Story 4.1, **When** I map the base integer and scalar requirements, **Then** I cover RV64I and applicable integer, compressed, bit-manipulation, CSR/counter, hint, conditional, may-be operation, pointer-masking (`Supm`), and data-independent execution latency (`Zkt`) requirements; floating-point, vector, memory-attribute, and S64 privileged requirements are handled in later stories.

**Given** each applicable requirement, **When** I inspect Kunminghu and Heliodor, **Then** I record status, specific source location or scope decision, rationale, covered subcases, and evidence IDs separately for each implementation.

**Given** a requirement with test or verification material, **When** I record the evidence, **Then** I distinguish source inspection, inspected tests, and actual run results; items not run are not marked run-pass.

**Given** the completed scalar mapping, **When** I update the coverage table, **Then** I preserve a separate row per normative requirement ID and version instead of using an extension name or single test as a proxy for the whole requirement.

### Story 4.3: 映射 RVA23U64 浮点要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map the RVA23U64 scalar floating-point mandatory requirements item by item,
So that I can compare floating-point implementation locations, behavior scope, and evidence status in both processors.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map floating-point requirements, **Then** I cover single precision, double precision, minimal half precision, and the additional floating-point requirements listed by the profile, with applicable specification IDs and versions.

**Given** each floating-point requirement, **When** I inspect Kunminghu and Heliodor, **Then** I record implementation location, status, covered behavioral subcases, and evidence IDs separately for each; unconfirmed behavior is marked unverified or another appropriate status with its rationale.

**Given** available tests or verification materials, **When** I record evidence, **Then** I distinguish source inspection, inspected tests, and actual run results and do not infer full extension coverage from one test.

**Given** the floating-point mapping, **When** I review the coverage table, **Then** I can identify each implementation's status and evidence by requirement ID without conflating scalar and vector floating-point requirements.

### Story 4.4: 映射 RVA23U64 的基础向量要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to trace the mandatory V extension implementation and configuration in both processors,
So that I can identify the coverage and evidence status of vector base requirements.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map the V requirements, **Then** I record the vector base capabilities and related implementation parameters required by the specification, keyed by specification ID and version, without treating the extension name alone as proof of complete coverage.

**Given** both vector implementations, **When** I inspect source and verification materials, **Then** I record relevant decode, vector execution, vector state/register, and vector memory locations where applicable, with evidence status.

**Given** vector operations have parameterized behavior, **When** I record coverage, **Then** I explicitly list examined subcases such as element widths, masks, tail handling, or exceptions, and leave uncovered items explicit.

**Given** the Kunminghu and Heliodor findings, **When** I update the coverage table, **Then** I record each implementation's status, location, rationale, and evidence IDs separately and distinguish inspection from actual execution.

### Story 4.5: 映射 RVA23U64 的其他向量必选项

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to inspect Zvfhmin, Zvbb, and Zvkt item by item,
So that I can identify the implementation status of vector half-precision, bit-manipulation, and data-independent execution latency requirements in both processors.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map the additional vector requirements, **Then** I create separate entries for Zvfhmin, Zvbb, and Zvkt and cite their specification IDs and versions.

**Given** each vector requirement, **When** I inspect Kunminghu and Heliodor, **Then** I separately record status, source locations, covered subcases, rationale, and evidence IDs.

**Given** available tests or verification materials, **When** I record evidence, **Then** I distinguish source inspection, inspected tests, and actual run results and identify behavior that remains unverified.

**Given** the updated coverage table, **When** I review each result, **Then** I do not treat evidence for the base V extension as automatic evidence for these additional requirements.

### Story 4.6: 映射 RVA23U64 的内存与缓存要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map RVA23U64 requirements for main memory, atomic behavior, and cache-block operations item by item,
So that profile behavior that cannot be proven by instruction implementation locations alone is covered.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map memory and cache requirements, **Then** I cover applicable instruction-fetch atomicity, reservation events, atomic operations, misaligned accesses, reservation sets, cache-block size, and cache-block management, prefetch, and zeroing requirements.

**Given** each profile-defined memory property or behavior, **When** I inspect both implementations and available platform material, **Then** I separately record locatable implementation or platform evidence; if no evidence can be located, I record a scope decision, rationale, and unverified status.

**Given** a requirement that applies only under specified memory-region or PMA conditions, **When** I record its applicability, **Then** I state those conditions and do not generalize local RTL or one test result into complete platform coverage.

**Given** available verification materials, **When** I update the coverage table, **Then** I link evidence IDs separately for Kunminghu and Heliodor and distinguish source inspection, inspected tests, and actual run results.

### Story 4.7: 映射 RVA23S64 的监督模式与陷阱要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map the RVA23S64 supervisor, trap, and related state requirements item by item,
So that I can inspect how both processors support the supervisor behavior required by the profile.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map supervisor requirements, **Then** I cover applicable Zifencei, Ss1p13, trap-vector and stval behavior, counter permissions, supervisor timer, counter-overflow filtering, pointer masking including the required `senvcfg.PME` settings, and UXL=64 requirements.

**Given** each supervisor requirement, **When** I inspect Kunminghu and Heliodor, **Then** I separately record its specification ID, implementation location, status, applicable subcases, rationale, and evidence IDs.

**Given** a requirement depends on trap cause, privilege, or CSR state, **When** I record the mapping, **Then** I state its applicability conditions and observed state updates; unconfirmed behavior remains unverified.

**Given** available source and test materials, **When** I update the coverage table, **Then** I distinguish source inspection, inspected tests, and actual run results and do not use one trap case as evidence for all requirements.

### Story 4.8: 映射 RVA23S64 的地址转换与页表要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map RVA23S64 address-translation and page-table requirements item by item,
So that I can compare both virtual-memory paths and their verification evidence.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map address-translation requirements, **Then** I cover applicable Svbare, Sv39, Svade, hardware page-table reads, Svpbmt, Svinval, and Svnapot requirements.

**Given** each address-translation requirement, **When** I inspect both implementations, **Then** I separately record mode or conditions, implementation location, status, covered subcases, and evidence IDs.

**Given** a requirement involving page-table walks, page faults, translation-cache invalidation, or memory types, **When** I record its implementation evidence, **Then** I state applicability conditions and unverified behavior and do not generalize one page mode or test to all modes.

**Given** the completed mapping, **When** I review the coverage table, **Then** I can inspect each requirement ID and the status, rationale, and evidence for Kunminghu and Heliodor separately.

### Story 4.9: 映射 RVA23S64 的 Hypervisor 必选要求

**FRs covered:** FR-2, FR-6 (阶段 4), FR-7, FR-8

As a learner,
I want to map the Hypervisor and companion requirements included in Sha item by item,
So that I can identify the evidence for each processor's virtualization implementation.

**Acceptance Criteria:**

**Given** the official mandatory-requirement inventory, **When** I map Sha, **Then** I cover H and its listed Ssstateen, Shcounterenw, Shvstvala, Shtvala, Shvstvecd, Shvsatpa, and Shgatpa requirements, including `henvcfg.PME` behavior required by Ssnpm where applicable.

**Given** each Hypervisor requirement, **When** I inspect Kunminghu and Heliodor, **Then** I separately record implementation location, status, applicable virtualization or translation modes, relevant subcases, and evidence IDs.

**Given** a requirement depends on guest/host state, trap information, or vsatp/hgatp modes, **When** I record the mapping, **Then** I state applicability conditions, mode correspondence, and any unverified behavior.

**Given** an upstream project claim or test result, **When** I record it as evidence, **Then** I preserve its source and evidence type and do not treat a claim or partial test as verification of the entire mandatory requirement.

### Story 4.10: 核对 RVA23 必选项映射完整性

**FRs covered:** FR-7, FR-8

As a learner,
I want to reconcile the completed coverage table against the official RVA23 mandatory checklist,
So that I can find omissions, blank statuses, or conclusions that could be mistaken for verified behavior.

**Acceptance Criteria:**

**Given** the official RVA23 Profile v1.0 mandatory checklist, **When** I reconcile the project coverage table, **Then** every RVA23U64 and RVA23S64 mandatory item, inherited item, and normative behavioral requirement has a corresponding entry.

**Given** each mandatory requirement entry, **When** I inspect both implementation mappings, **Then** Kunminghu and Heliodor each have an explicit status; no status is blank, and out-of-scope or unverified items include a rationale.

**Given** the coverage evidence and statuses, **When** I produce the summary, **Then** I report status counts by profile and implementation, distinguish mandatory items from optional items and upstream claims, and list unresolved items.

**Given** the completed comparison map, **When** I write its summary, **Then** I identify it as this project's learning map of specification and implementation evidence and do not claim certification or use partial tests as proof of complete compliance.

## Epic 5: 完成 RVA23S64 双实现深度学习与结项审计

Epic 5 在 Epic 4 的 profile 必选项图谱基础上，完成五个 RVA23S64 主题的深入比较，并审计证据链。Epic 5 开始前须完成 Story 5.1 的准备门；主题故事依次推进，每项允许以“已验证、静态证据、未实现或受阻”等证据状态结束，不得把未知记为通过。

### Story 5.1: 确认活动实现路径与验证就绪度

**FRs covered:** FR-1, FR-2, FR-6 (阶段 5), FR-7, FR-8, FR-9, FR-10; NFR-1, NFR-2, NFR-6

As a learner,
I want to establish the active implementation paths and validation readiness for the five RVA23S64 topics,
So that I can plan each comparison against the selected source snapshots, configurations, and runnable evidence.

**Acceptance Criteria:**

**Given** the project `sources.lock`, **When** I prepare Epic 5, **Then** I record and verify the full commit SHA for Kunminghu and Heliodor; any mismatch is resolved or recorded as a blocked prerequisite before using evidence from that checkout.

**Given** the selected Kunminghu target and configuration, **When** I trace its CSR wrapper and configuration, **Then** I record which CSR implementation path is active for Sstc, Sscofpmf, Ssnpm, and Ssstateen, plus the relevant feature controls; code presence alone is not treated as proof that the selected target enables a feature.

**Given** the Heliodor snapshot, **When** I inspect the FENCE.I, Sstc, Sscofpmf, pointer-masking and Ssstateen source/test entry points, **Then** I record each test’s build command, harness, expected observation, parameters and whether it has only been inspected, built, or actually run.

**Given** the five study topics and the available ACT4/Sail and local toolchains, **When** I create the requirement-to-case readiness matrix, **Then** each topic has its applicable spec version, case list, candidate test source, dependency/tool version and current status; unsupported or uncertain cases are marked explicitly.

**Given** the profile PDF and pointer-masking specification/source use different PME/PMM spellings, **When** I record the Ssnpm requirement, **Then** I preserve both source references and document the verified mapping or leave it explicitly unresolved; I do not silently normalize the terminology.

**Given** these checks are complete, **When** I assess the Epic 5 gate, **Then** each feature has a known active path or a specific blocker, and each planned test is classified as available, needs setup, unsupported, or blocked with its reason; this story does not claim any CPU feature passed verification.

### Story 5.2: 比较 Zifencei 与 `FENCE.I`

**FRs covered:** FR-2, FR-3, FR-4, FR-6 (阶段 5), FR-7, FR-8, FR-9, FR-10; NFR-1, NFR-2, NFR-3, NFR-5, NFR-6

As a learner,
I want to trace `FENCE.I` from its architectural contract through both cores,
So that I can explain how each implementation makes prior code stores visible to later instruction fetches on the same hart.

**Acceptance Criteria:**

**Given** the applicable ratified Zifencei specification and pinned snapshots, **When** I write the unit’s scope, **Then** I state that `FENCE.I` synchronizes instruction fetch on the executing hart and does not by itself guarantee instruction visibility on another hart.

**Given** Kunminghu and Heliodor’s selected implementations, **When** I trace `FENCE.I`, **Then** I record each path from decode through serialization/invalidation to subsequent fetch, or mark any unconfirmed path as unverified.

**Given** the Heliodor FENCE.I test entry and a matching Kunminghu test or harness, **When** the case can run, **Then** I execute a bounded self-modifying-code case that writes a new instruction, executes `FENCE.I`, and observes the new result; I record the command, configuration, expected and observed result, and artifact path. If it cannot run, I record the specific blocker and keep it unverified.

**Given** the selected test checks the instruction encoding, **When** I review its operands and ignored/reserved fields, **Then** I record whether those cases are covered or leave them explicitly unverified.

**Given** the unit is complete, **When** I compare the two implementations, **Then** I provide source and test evidence for each claim, answer how the local-hart guarantee is met, and list uncovered multi-hart coordination cases separately.

### Story 5.3: 比较 Sstc 与 S/VS timer

**FRs covered:** FR-2–FR-4, FR-6–FR-10; NFR-1–NFR-3, NFR-5, NFR-6

As a learner,
I want to trace supervisor and virtual-supervisor timer interrupts in both cores,
So that I can explain the compare state, access gates and interrupt delivery in S-mode and VS-mode.

**Acceptance Criteria:**

**Given** the ratified Sstc specification and pinned snapshots, **When** I define the unit’s cases, **Then** I cover `stimecmp`, `vstimecmp`, `menvcfg.STCE`, `henvcfg.STCE`, timer pending state and the applicable delegation/visibility rules.

**Given** each selected Kunminghu and Heliodor configuration, **When** I trace the timer path, **Then** I record compare-register access and state, the source of `time` or guest-visible time including `htimedelta`, pending-bit generation, and interrupt delivery; unconfirmed configuration or path details remain marked unknown.

**Given** a test can run, **When** I exercise the comparator, **Then** I check `time < stimecmp`, `time == stimecmp`, and `time > stimecmp`, as well as STCE-enabled and disabled behavior and the resulting pending/access-trap behavior. I record observed values and trap/interrupt causes; unavailable cases retain a specific blocker.

**Given** the selected target supports the guest timer path, **When** I test VS-mode behavior, **Then** I verify `vstimecmp`, `henvcfg.STCE`, guest time offset and VSTIP delivery independently of the S-mode case; if the path cannot be exercised, I document the exact gap.

**Given** timer interrupts are asynchronous, **When** I assess delivery timing, **Then** I compare observations against the specification’s bounded-evaluation requirements and do not impose an unsupported cycle-exact latency expectation.

**Given** the unit is complete, **When** I compare the two implementations, **Then** I provide the two source paths, command/configuration/result evidence for executed cases, self-check answers for S-mode and VS-mode, and an explicit list of untested boundaries.

### Story 5.4: 比较 Sscofpmf 计数溢出和模式过滤

**FRs covered:** FR-2–FR-4, FR-6–FR-10; NFR-1–NFR-3, NFR-5, NFR-6

As a learner,
I want to trace hardware performance-counter overflow and privilege-mode filtering,
So that I can explain how overflow state, `scountovf`, and local counter-overflow interrupts interact.

**Acceptance Criteria:**

**Given** the ratified Sscofpmf specification and the selected implementation configurations, **When** I choose a bounded HPM counter case, **Then** I record the counter, supported event, counter width or preload mechanism, applicable mode filters, and relevant access controls.

**Given** a selected hardware event that increments the counter, **When** I exercise overflow, **Then** I verify the event’s `OF` state, `scountovf` visibility, and local counter-overflow interrupt pending state; software writes that wrap a counter are not accepted as evidence of hardware overflow.

**Given** the counter’s overflow flag is set, **When** I test clearing and re-arming, **Then** I record the architectural operation that clears `OF`, the condition for a subsequent overflow, and the observed interrupt/pending behavior; unsupported or non-deterministic mechanisms are marked as blockers.

**Given** the event and mode configuration are supported, **When** I test privilege filtering, **Then** I cover `MINH`, `SINH`, `UINH`, `VSINH`, and `VUINH` for the selected event, or identify the specific unsupported mode/case and its evidence boundary.

**Given** the `scountovf` read path and local interrupt path are available, **When** I test access and delivery, **Then** I check the applicable `mcounteren`/`hcounteren` gates, LCOFIP/LCOFIE, delegation, and observed trap cause separately; unavailable combinations remain explicitly unverified.

**Given** ACT4/Sail tests are available for the chosen configuration, **When** I run them, **Then** I record their exact version, generated test, command, configuration and result separately from the directed case; a missing Sail model or coverpoint is recorded as a blocker, not a DUT failure.

**Given** the unit is complete, **When** I compare both processors, **Then** I provide the source paths and evidence for overflow, filtering, access, and interrupt behavior, answer the self-check, and list uncovered combinations.

### Story 5.5: 比较 Ssnpm 指针屏蔽

**FRs covered:** FR-2–FR-4, FR-6–FR-10; NFR-1–NFR-3, NFR-5, NFR-6

As a learner,
I want to trace supervisor-controlled pointer masking and its memory-access scope in both cores,
So that I can explain the required PMLEN settings, privilege controls, address transformation, and uncovered access families.

**Acceptance Criteria:**

**Given** the RVA23S64 profile and ratified Pointer Masking specification versions, **When** I define the Ssnpm requirement, **Then** I document the profile PDF’s `PME` spelling and the specification/source `PMM` spelling with their exact references, and record a verified mapping or an explicit unresolved discrepancy.

**Given** the selected snapshots and active configurations, **When** I trace pointer masking, **Then** I identify the relevant `senvcfg`/`henvcfg` controls, PMLEN selection, privilege-mode applicability, and address transformation through the address-generation/translation path for Kunminghu and Heliodor separately.

**Given** the selected configurations support the required settings, **When** I test pointer masking, **Then** I exercise PMLEN=0 and PMLEN=7, enabled/disabled behavior, and tagged-address transformation in applicable U-mode and VS/VU cases; unsupported configurations or cases include a concrete reason and evidence boundary.

**Given** the specification defines multiple explicit memory-access families, **When** I build the coverage matrix, **Then** I list applicable load/store, atomic, floating-point, compressed, cache, vector, and hypervisor explicit-memory families, and classify each as tested, inspected only, unsupported, or unverified for each implementation.

**Given** a family is supported by the selected target and a runnable test path exists, **When** I execute a representative case, **Then** I record the exact instruction, privilege/virtualization mode, control settings, expected transformed address or result, observed result, command and artifact; unrun families are not inferred from another family’s passing case.

**Given** the unit is complete, **When** I compare both implementations, **Then** I answer how PMLEN=0 and 7 affect the selected addresses, provide the two source paths and validation evidence, and list all uncovered access families and address-boundary cases.

### Story 5.6: 比较 Ssstateen 状态访问门控

**FRs covered:** FR-2–FR-4, FR-6–FR-11; NFR-1–NFR-3, NFR-5, NFR-6

As a learner,
I want to trace the supervisor and hypervisor state-enable registers and access gates,
So that I can explain how lower-privilege access to extension state is permitted or trapped in both cores.

**Acceptance Criteria:**

**Given** the RVA23S64/Sha requirements and ratified Smstateen/Ssstateen specification, **When** I build the unit’s checklist, **Then** I include `sstateen0–3` and `hstateen0–3`, relevant reset and WARL/read-only-zero behavior, and the state-enable bits used by the selected test.

**Given** the selected Kunminghu configuration, **When** I trace state-enable behavior, **Then** I follow the active CSR path and record each required CSR’s read/write handling, state-bit mapping, privilege gate, and trap/permit decision; inactive or unconfirmed code paths are not treated as evidence for the target.

**Given** Heliodor’s pinned source snapshot, **When** I investigate state-enable support, **Then** I record the bounded source-search scope and inspect generic CSR decode/permission paths; if no explicit implementation is found, I use a controlled CSR or extension-state access to observe the result and label the conclusion as supported, absent, or unresolved with its evidence limits.

**Given** a supported state bit and runnable test path, **When** I check access gating, **Then** I exercise one permitted access and one blocked access across the applicable M/H/S/VS/VU hierarchy, recording the controlling register state, expected and observed trap cause, command, configuration, and artifacts.

**Given** the state-enable test is complete, **When** I review reset and access behavior, **Then** I record observed reset/readback and WARL/RO-zero results for the required CSR set, or list each untested register/condition with its specific blocker.

**Given** the unit is complete, **When** I compare the two implementations, **Then** I answer which gate controls the selected extension state at each tested privilege level, cite both source paths and actual test evidence where available, and distinguish a verified implementation gap from absence of a matching symbol.

### Story 5.7: 审计 RVA23S64 覆盖与学习结项证据

**FRs covered:** FR-2–FR-4, FR-6–FR-11; NFR-1–NFR-3, NFR-5, NFR-6

As a learner,
I want to audit the five RVA23S64 deep-comparison units and the overall learning record,
So that I can confirm conclusions are traceable, unverified boundaries are clear, and decide whether the learning objectives are complete.

**Acceptance Criteria:**

**Given** the Epic 4 RVA23U64/RVA23S64 mandatory-requirement map, **When** I audit Epic 5, **Then** I link Zifencei, Sstc, Sscofpmf, Ssnpm, and Ssstateen to exact requirement IDs and specification versions; uncovered requirements include a reason and scope decision, and deep units are not presented as complete conformance proof.

**Given** the five deep-comparison units, **When** I inspect each topic, **Then** I record Kunminghu and Heliodor status, source snapshots, specification basis, implementation paths, learner self-check questions and answers, planned subcase status, and evidence links; actual runs, static inspection, and upstream claims are distinguished.

**Given** cases planned for execution in the stories, **When** I check validation records, **Then** every runnable case has an actual result, while each unrun case has a specific blocker and evidence boundary; unknown or unsupported conclusions are not marked as passed.

**Given** all units and indexes, **When** I run the project's existing coverage checker, document/index link checker, and sprint status validator, **Then** I record the actual commands, tool versions, and outputs; I fix and rerun findings where possible and document any unresolved finding and its reason.

**Given** the audit results, **When** I review the project learning objectives, **Then** I record which objectives have evidence, which remain blocked or unverified, and whether those residual limits are accepted; the completion statement covers only this project's learning scope and does not claim RVA23 conformance certification for Kunminghu, Heliodor, or this project.

**Given** the audit record, **When** I complete this story, **Then** I provide a reviewable evidence index, checker results, self-check conclusions, and remaining items, and confirm the delivery status of Epic 5.

## Epic 6: 验证 RVA23S64 五专题的 CPU 行为

本 Epic 是 Epic 5 学习结项之后新增的动态验证 backlog。目标是在固定 Kunminghu/Heliodor 快照上，先建立可复现的 CPU 仿真入口，再逐专题运行代表性架构案例；仿真构建失败、testbench 阻塞和 CPU 行为失败必须分开记录。本 Epic 不修改 `sources/` 固定快照，也不将有限测试结果表述为整个 RVA23 Profile 符合性或认证。

**依赖门：** Story 6.1 的工具链、fixture 输入和结果归档约定完成前，不开始专题 CPU 行为故事。Story 6.2/6.3 分别验证两边 simulator/harness 的加载与观察能力；依赖某侧的专题案例必须先有该侧可用的入口。所有运行记录均遵守 `notes/units/rva23s64-cpu-validation-preflight-v1.md` 的版本、输入哈希、命令、工具版本、完整日志和 `cpu_started` 字段。

### Story 6.1: 固定 CPU 验证工具链与结果归档

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to make both simulators reproducible and capture the inputs and outputs of each run,
So that CPU observations can be compared without confusing tool failures with DUT behavior.

**Acceptance Criteria:**

**Given** the locked Kunminghu and Heliodor revisions, **When** I prepare their toolchains, **Then** I record exact Mill/Java/Verilator/compiler and Veryl versions, required environment variables, pinned submodule revisions, and supported target configurations without changing either source snapshot.

**Given** a target-side smoke entry exists, **When** I build and run a minimal known input on each core, **Then** I record the exact command, cwd, configuration, source revision, input SHA-256, tool versions, exit code, whether CPU execution began, output path/hash, and generated artifact paths.

**Given** a build, harness, or test fails before CPU execution, **When** I classify its result, **Then** it is recorded as `blocked` with the first failing tool/phase and is never labeled a CPU `run-fail`.

### Story 6.2: 建立 Kunminghu fixture 加载与模拟器入口

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want a repeatable Kunminghu simulator entry that loads a small directed program and exposes its result,
So that the five architecture topics can use controlled inputs and observable pass/fail markers.

**Acceptance Criteria:**

**Given** Story 6.1's pinned toolchain, **When** I initialize only dependencies required by the selected target, **Then** every submodule resolves to its parent gitlink SHA and the locked top-level snapshot SHA remains unchanged.

**Given** the simulator build, **When** I load a minimal fixture, **Then** the harness confirms program load, CPU start, instruction retirement or equivalent progress, and a result marker; a simulator build alone does not satisfy this criterion.

**Given** the Makefile, Chisel, Verilator, or C++ toolchain stops before execution, **When** I report the outcome, **Then** the exact first blocker, output excerpt/hash, resources, and next environment change are recorded without modifying upstream files.

### Story 6.3: 建立 Heliodor arch harness 隔离运行入口

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to run the pinned Heliodor architecture harness despite the shared debug-testbench check issue,
So that ordinary architecture tests can produce isolated CPU observations without changing the source checkout.

**Acceptance Criteria:**

**Given** the pinned Heliodor source and Veryl version, **When** I build the isolated runner, **Then** it creates a fresh temporary copy, removes only the uninstantiated debug harness that causes check failure, applies the minimum documented local `allow(initial_assign)`, and copies the exact fixture by recorded SHA.

**Given** the transformed harness, **When** I run one small known test, **Then** the log proves compile/check passed, CPU simulation started, the expected output channel was observed, and the source checkout remained clean.

**Given** a topic uses memory, address translation, interrupt, or timing behavior, **When** I reuse the workaround, **Then** I review and record whether the local harness transformation can affect that case's semantics before treating its result as evidence.

### Story 6.4: 运行 Zifencei 自修改代码对照

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to execute self-modifying instruction cases around `FENCE.I` on both cores,
So that I can distinguish instruction-fetch synchronization from data-store visibility and reserved-field handling.

**Acceptance Criteria:**

**Given** a fixed program image and cache/hart configuration, **When** each core runs the case, **Then** the result distinguishes the old instruction result before synchronization from the newly written instruction result after `FENCE.I`, with exact expected and observed values.

**Given** Zifencei ignored/reserved fields, **When** I execute nonzero `funct12`, `rs1`, and `rd` encodings independently, **Then** each encoding's expected architectural treatment and observed trap/result are recorded per implementation.

**Given** a multi-hart test is unavailable, **When** I close the story, **Then** the conclusion is restricted to the tested hart count and remote-hart publication/synchronization remains an explicit uncovered case.

### Story 6.5: 运行 Sstc S/VS comparator 与陷阱对照

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to exercise supervisor and virtual-supervisor timer comparators and gates,
So that I can explain timer interrupt generation, delegation, and delivery from observed behavior.

**Acceptance Criteria:**

**Given** a runnable S-mode timer fixture, **When** I test `stimecmp < time`, `== time`, and `> time` with STCE/TM enabled and disabled, **Then** pending-bit transitions, trap delivery, cause, privilege and expected cycle relationship are recorded.

**Given** a runnable VS fixture, **When** I test `vstimecmp`, nonzero `htimedelta`, both applicable STCE levels, delegation and VSTIP delivery, **Then** each stage's control state and observed result are reported independently.

**Given** an interrupt cannot be injected or the harness cannot observe virtual time, **When** a case cannot run, **Then** it is `blocked` with the missing capability named; no result is inferred from static CSR paths.

### Story 6.6: 运行 Sscofpmf 硬件计数器溢出与过滤对照

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to cause a hardware performance-counter overflow and observe its filtering and interrupt path,
So that software writes to counter state are not mistaken for hardware event behavior.

**Acceptance Criteria:**

**Given** a selected hardware event and implemented counter, **When** the counter overflows, **Then** the test observes `mhpmevent.OF`, `scountovf`, pending/interrupt state and cause 13, and records the event selector, counter value, privilege and observed sequence.

**Given** implemented privilege filters and access/delegation controls, **When** I vary MINH/SINH/UINH/VSINH/VUINH and clear/re-arm state, **Then** each supported combination has an observed result and unsupported combinations name the exact implementation or harness blocker.

**Given** ACT4 or Sail does not support the requirement, **When** I report directed testing, **Then** model/tool support is recorded separately and software-forced OF is not claimed as hardware-overflow evidence.

### Story 6.7: 运行 Ssnpm PMLEN 与访问族对照

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to test supervisor pointer masking at its required PMLEN settings and applicable privilege levels,
So that I can observe tagged-address transformation and the access families affected by it.

**Acceptance Criteria:**

**Given** PMLEN=0 and PMLEN=7 configurations, **When** I test masking enabled/disabled and canonical/tagged boundary addresses, **Then** each case records the transformed effective address or architectural trap and the controlling `senvcfg`/`henvcfg` state.

**Given** S/U and virtualized modes supported by a target, **When** I execute representative load/store and applicable atomic, FP, compressed, cache, vector and hypervisor explicit-memory accesses, **Then** results are listed by family and mode rather than inferred from one scalar case.

**Given** an access family cannot be built or observed, **When** the story closes, **Then** it has a specific `blocked` reason or an explicit out-of-scope decision; M-mode Supm is not used as Ssnpm evidence.

### Story 6.8: 运行 Ssstateen 八 CSR 与层级访问门对照

**FRs covered:** FR-2–FR-11; NFR-1–NFR-6

As a learner,
I want to check state-enable CSR reset/readback and hierarchical access traps on both cores,
So that I can confirm the existing Heliodor failure and determine Kunminghu's observed behavior.

**Acceptance Criteria:**

**Given** `sstateen0–3` and `hstateen0–3`, **When** I test defined reset/readback/WARL bits and M/H/S/VS/VU access paths with gates clear/set, **Then** every executed CSR operation records its operation ID, expected/observed value, trap cause and mode.

**Given** the existing Heliodor fixture, **When** I rerun it with the isolated harness, **Then** the run is compared against the durable baseline log by fixture SHA and remains `run-fail` unless a new run produces the expected behavior.

**Given** the fixed Kunminghu snapshot and preflight runner, **When** I run the matching matrix, **Then** I report its behavior independently; a missing implementation is a CPU `run-fail` only after the CPU starts and the assertion observes the mismatch.
