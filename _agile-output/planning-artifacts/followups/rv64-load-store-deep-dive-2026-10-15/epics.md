---
status: final
stepsCompleted: [1, 2, 3]
inputDocuments:
  - followup-prd.md
  - followup-architecture.md
  - followup-spec.md
  - feasibility.md
  - trace-matrix.md
  - learning-record-conventions.md
  - learning-plan.md
---

# RV64 load/store deep dive - Epic Breakdown

## Overview

This independent follow-up organizes learning work for Kunminghu V2 and Heliodor. It preserves the completed RVA23 stage and uses the locked source snapshots and evidence rules defined by the follow-up PRD and architecture spine.

## Requirements Inventory

### Functional Requirements

FR-1: Maintain a navigable Markdown learning-journal index that distinguishes completed history, current work, and planned topics; published links resolve, while unwritten historical recaps remain pending.

FR-2: Record each exploration with date, question, sources/actions, findings with evidence type and validation state, links to the canonical learning unit/evidence, and next step. Do not invent unrecoverable historical details.

FR-3: Trace a successful RV64I `LD` on both cores from decode/issue through address generation, translation, cache response, writeback, and retirement. Use the shared tuple: naturally aligned 8-byte access, M-mode Bare, no exception, DCache hit, and no older overlapping store. Mark unconfirmed premises as assumptions and unobserved stages unknown/unverified.

FR-4: Trace an ordinary naturally aligned RV64I `SD` to DRAM on both cores. The story must choose one shared tuple and an evidence-supported write-acceptance endpoint, distinguish instruction commit from cache/buffer acceptance and lower-level visibility, and never infer DRAM visibility from commit alone.

FR-5: Compare the common Sv39 noncanonical-address load page fault: S-mode, V=0, Sv39, ordinary RV64I `LD`, VA `0x0000008000000000`, `medeleg[13]=0`. Trace detection, exception retention, cause 13, fault PC/`mepc`, `mtval`, M-mode trap target, and supported state updates; keep unsupported behavior unknown and unrun behavior unverified.

FR-6: Keep evidence `type` and validation `status` separate. Use the specified vocabularies; link every claim to evidence IDs on both cores or mark comparison coverage partial. Runtime claims include input, command, configuration, output, and artifact path. A test entry is not proof of execution.

FR-7: Identify source evidence by the stable snapshot ID and full SHA in `sources.lock`; mismatched checkouts do not count toward acceptance, and affected claims are rechecked after a baseline change.

### NonFunctional Requirements

NFR-1: Preserve provenance and reproducibility through locked source snapshots, evidence IDs, and exact runtime records.

NFR-2: Preserve history: published learning-unit versions are immutable; revisions create a new version and update `notes/units/index.md`.

NFR-3: Keep materials readable as Chinese Markdown in Git/GitHub; no deployed blog service or generator is required.

NFR-4: Evidence quality must bound each claim; static inspection, inspected tests, and actual execution remain distinct.

### Additional Requirements

- Architecture: `notes/units/` owns technical conclusions; `learning-journal/` owns chronology; raw run artifacts remain under `notes/units/evidence/`.
- Architecture: compare equivalent architectural tuples using each core's own stage names; do not force one-to-one microarchitectural alignment.
- Architecture: the trace matrix contains six case/core path rows, each from required start to selected endpoint with evidence references or explicit `unknown`/`blocked`.
- Architecture: keep this follow-up's spec, PRD, architecture, epics, and sprint outputs in distinct paths; do not alter completed RVA23 artifacts.
- Architecture: no upstream RTL changes, no RVA23 conformance claim, and no mandatory dynamic run. A trace harness requires separate feasibility/scope review.
- Operations: use the existing local Git checkout and Markdown rendering; no service, provider, or infrastructure is introduced.
- UX: no separate UX contract exists; this is a repository-based personal learning workflow.

### UX Design Requirements

None. No UX design contract or separate UI is in scope.

### FR Coverage Map

FR-1: Epic 1 — Maintain a navigable journal index with clear history/current/planned states.
FR-2: Epic 1 — Record explorations with evidence links and preserve historical uncertainty.
FR-3: Epic 1 — Trace successful scalar LD on both locked core snapshots.
FR-4: Epic 1 — Trace ordinary aligned DRAM SD through an evidence-supported write endpoint.
FR-5: Epic 1 — Trace the shared Sv39 noncanonical LD page fault through supported trap state.
FR-6: Epic 1 — Keep evidence type, validation status, comparison completeness, and claim scope explicit.
FR-7: Epic 1 — Preserve source snapshot provenance and revalidation boundaries.

## Epic List

### Epic 1: 完成可回顾、可复查的双核访存学习阶段

学习者能够按时间回顾探索过程，并复习一套有证据支撑的 Kunminghu 与 Heliodor 标量访存路径；每项结论都能追溯到固定源码快照、测试材料或真实运行产物，未证实部分明确保留为未知。

**FRs covered:** FR-1, FR-2, FR-3, FR-4, FR-5, FR-6, FR-7

**Delivery notes:** 在同一学习阶段内按日志与导航、LD、SD、Sv39 fault、证据/快照核对和综合回顾拆分 Stories。具体 SD tuple 与写入接受终点先经可行性检查并记入决策日志；不把动态运行或新增 trace harness 设为默认门槛。

### Story 1.1: 复核并记录双核 `LD` 路径

**FRs covered:** FR-2, FR-3

**NFRs covered:** NFR-2, NFR-4

As a RV64 CPU 学习者,
I want 按同一架构场景追踪 Kunminghu 与 Heliodor 的普通 `LD`,
So that 我能理解数据从译码到退休的双核实现路径及其证据边界。

**Acceptance Criteria:**

**Given** `sources.lock` 中的 Kunminghu V2 与 Heliodor 固定快照，**When** 我复核 RV64I `LD`，**Then** 两侧采用相同 tuple：自然 8 字节对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store；未被来源或运行配置确认的前提标为 assumption。

**Given** 上述共同场景，**When** 我整理两侧路径，**Then** 每侧从译码/发射经过地址生成、地址转换、缓存响应追踪至写回和退休；使用各自源码术语，引用锁定 SHA 与具体源码位置，证据不足处标为 `unknown`、`blocked` 或 `unverified`。

**Given** 现有 `load-v1.md` 已发布，**When** 本次复核完成，**Then** 若其结论足够则引用该版本；若需修改则新建下一不可变版本并更新 `notes/units/index.md`，不得覆盖已发布文件。

**Given** 两侧路径复核完成，**When** 本 Story 交付，**Then** 新增一篇满足学习日志字段约定的 `LD` 探索记录，链接技术单元和证据，并更新日志索引及追踪矩阵中的两侧 `LD` 行；证据 `type`/`status` 分列，测试源码检查不写成测试已运行。

**Given** 本 PRD 允许静态路径记录完成目标，**When** 没有新的运行证据，**Then** 不要求执行测试，且不把源码推导描述为动态运行观察。

### Story 1.2: 追踪普通 DRAM `SD` 的提交与写入边界

**FRs covered:** FR-2, FR-4

**NFRs covered:** NFR-1, NFR-2, NFR-4

As a RV64 CPU 学习者,
I want 追踪 Kunminghu 与 Heliodor 中普通对齐 DRAM `SD` 的写入路径,
So that 我能区分指令提交、缓存/缓冲接受和更低层可见性。

**Acceptance Criteria:**

**Given** `sources.lock` 中的两个固定快照，**When** 开始解释 SD 路径之前，**Then** 依据两侧源码/测试可行性确定同一自然对齐、普通 DRAM 目标的 RV64I `SD` 地址与配置 tuple，并选出证据支持的写入接受终点；将 tuple、终点和未能确认的前提写入本 Story 与 `_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/decisions/story-1-2-store.md` 决策记录。

**Given** 已确定的共同 tuple，**When** 追踪两侧路径，**Then** 分别按 Kunminghu 和 Heliodor 自身术语从译码、地址/数据形成、排队与提交追踪到所选接受终点，记录锁定 SHA、源码位置及必要的测试材料证据；两侧差异不强行映射为相同流水阶段。

**Given** 路径涉及提交、缓存/缓冲写入或更低层存储，**When** 写出比较结论，**Then** 明确区分指令提交、缓存/缓冲接受和下层可见性；若缺少证据，不从 commit、StoreQueue drain 或早期 tag probe 推断 DRAM 可见或持久。

**Given** 两侧静态路径整理完成，**When** 本 Story 交付，**Then** 创建新的不可变 `store` 学习单元版本、符合约定的日期日志，并更新日志索引及追踪矩阵中的两个 SD 行；每个结论链接两侧证据或明确标明 comparison partial，证据 `type` 与 `status` 分列。

**Given** 没有该 tuple 的实际运行证据，**When** 验收静态学习记录，**Then** 测试源码只标为已检查，未观察到的可见性保持 `unknown`/`unverified`；本 Story 不要求运行测试或新增 trace harness。

### Story 1.3: 追踪 Sv39 非规范地址 `LD` fault

**FRs covered:** FR-2, FR-5

**NFRs covered:** NFR-1, NFR-2, NFR-4

As a RV64 CPU 学习者,
I want 对照两核如何处理同一 Sv39 非规范地址 `LD` fault,
So that 我能理解实现如何将地址异常保留为精确的架构 trap 状态。

**Acceptance Criteria:**

**Given** `sources.lock` 中的两个固定快照，**When** 检查共同 fault 案例，**Then** 两侧都使用 S-mode、V=0、`satp.MODE=Sv39`、普通 RV64I `LD`、VA=`0x0000008000000000`、`medeleg[13]=0`；未确认的配置前提明确标为 assumption。

**Given** 该共同输入，**When** 追踪两侧异常路径，**Then** 记录 fault 检测、异常保留、`mcause=13`、故障 PC/`mepc`、`mtval`、M-mode trap target 及来源能确认的相关状态更新，并分别引用锁定 SHA 和源码位置。

**Given** 某项实现选择或 `mtval` 表示无法由锁定来源确认，**When** 写出结论，**Then** 将其列为 `unknown`/`unverified`，不得用架构预期替代实现证据；静态检查与动态运行观察分开记录。

**Given** 既有 `sv39-load-fault-v1.md` 已发布，**When** 本次复核需要修改其结论，**Then** 新建下一不可变版本并更新单元索引；若无需修改则引用现有版本。

**Given** 两侧路径完成静态复核，**When** 本 Story 交付，**Then** 新增符合日志字段约定的 fault 探索文章，更新日志索引及追踪矩阵中的两侧 fault 行；每项比较结论有两侧证据或明确标为 partial/unverified。本 Story 不要求实际运行 fault 测试。

### Story 1.4: 核验三类案例的证据与快照

**FRs covered:** FR-6, FR-7

**NFRs covered:** NFR-1, NFR-4

As a RV64 CPU 学习者,
I want 审核 LD、SD 与 fault 三类案例的双侧证据和来源快照,
So that 我能判断每项比较结论是否可复查、是否超出其证据范围。

**Acceptance Criteria:**

**Given** 三类案例的学习单元和证据表已建立，**When** 核对追踪矩阵，**Then** Kunminghu 与 Heliodor 的 LD、SD、fault 共六条路径行各自列明追踪起点、证据支持的终点、证据 ID 与来源位置，或明确标记 `unknown`/`blocked` 并说明影响。

**Given** 任一双核比较结论，**When** 审核其证据，**Then** 它链接两侧证据，或将比较覆盖标为 `partial` 且缺失侧标为 `unverified`/`blocked`；证据 `type` 和 `status` 使用独立字段，`partial` 不作为 evidence status。

**Given** 所有记录中的证据标识和源码版本，**When** 检查追溯性，**Then** evidence ID 在仓库内唯一；每项源码证据引用 `sources.lock` 中的稳定 snapshot ID 与完整 SHA，且记录使用的 SHA 与锁定值一致。checkout 不匹配时，该证据不计入本阶段比较验收。

**Given** 记录中含实际运行结论，**When** 审核该结论，**Then** 证据包含精确输入、命令、配置、输出和产物路径；没有运行产物时不得标为 `run-pass`，也不得将静态路径泛化为运行观察。

**Given** 固定快照与证据检查完成，**When** 有证据缺口，**Then** 保留 `unknown`、`blocked`、`unverified` 或 `partial` 并描述其边界；本 Story 不要求补跑测试或新增 trace harness。

### Story 1.5: 综合双核发现并完成学习日志导航

**FRs covered:** FR-1, FR-2

**NFRs covered:** NFR-3, NFR-4

As a RV64 CPU 学习者,
I want 汇总 LD、SD 与 fault 的双核发现并通过日志索引回顾整个探索过程,
So that 我能复习两种实现的差异，并追溯每项结论的来源和验证边界。

**Acceptance Criteria:**

**Given** 三类案例的学习单元、过程日志和追踪矩阵已建立，**When** 撰写综合总结，**Then** 解释共同架构行为在 Kunminghu 与 Heliodor 中的主要路径差异；每项比较结论链接两侧证据，或明确标记 partial/unknown，不把未观察内容写成已验证事实。

**Given** 综合总结面向之后继续学习的读者，**When** 发布总结日志，**Then** 记录日期、问题、查阅来源/动作、发现（含证据类型与状态）、学习单元/证据链接和下一步，并链接 LD、SD、fault 学习单元及 trace matrix。

**Given** 学习日志索引与 README 入口已存在，**When** 完成本阶段导航检查，**Then** README 可到达日志首页；首页区分已完成历史、当前工作和计划主题，所有已发布链接目标存在，未撰写的旧阶段回顾仍标为待整理/事后回顾。

**Given** 旧阶段过程不能从现存材料还原，**When** 总结既有历史与本阶段成果，**Then** 不虚构对话或探索细节；无法确认的信息保留为 unknown 或 pending。
