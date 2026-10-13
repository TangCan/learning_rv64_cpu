---
date: 2026-10-13
gate: FR-5 ADD pilot follow-up authorization
outcome: ready
authorized_epics: [5]
headless: false
---

# Epic 5 启动阶段门补充决策

## Decision

在原 ADD 试点复盘授权 Epic 2、3、4 的范围上，Richard 于 2026-10-13 明确批准将 Epic 5 加入获准启动范围。本记录是该阶段门的后续授权补充，不改写原复盘当时的授权内容。

**本次新增授权：Epic 5 — 完成 RVA23S64 双实现深度学习与结项审计。** 授权范围限于 `epics.md` 中 Story 5.1–5.7：先确认活动实现路径与验证就绪度，再依次完成五个主题对照，最后审计证据与学习结项。

## Preconditions and execution boundaries

- Epic 4 RVA23U64/RVA23S64 必选项映射及其 retrospective 已完成；当前 `sprint-status.yaml` 将 Epic 4 及其 retrospective 记录为 `done`。
- Epic 5 必须先完成 Story 5.1 的准备门。两边固定快照、Kunminghu 活动路径、Heliodor 测试入口、Ssstateen 行为边界以及 ACT4/Sail、编译器和仿真工具可用性，按 Story 5.1 核实；无法确认的项记录为阻塞或未验证，不得推断为通过。
- 故事按 Epic 5 既定顺序推进；不设日历周期。每个主题以学习记录、来源/证据链和自检为交付。
- 未授权修改上游 CPU 源码，也不以 CPU 实现符合 RVA23 或获得认证为目标。

## Gate assessment

**Ready, conditional on the preconditions above.** Epic 5 is authorized to start from Story 5.1. The story-level readiness result may record blocked or unsupported cases without claiming feature verification; such findings do not silently expand the authorized scope.

## Evidence

- 原授权与范围：`spec-1-3-add-dual-core-pilot.md` 及 `notes/units/add-pilot-retrospective.md`，当时明确授权 Epics 2–4。
- 当前 Epic 5 故事范围：`../planning-artifacts/epics.md`，Story 5.1–5.7。
- Epic 4 前置状态：`sprint-status.yaml` 中 Epic 4 和 `epic-4-retrospective` 均为 `done`。
- 本补充决策：用户于 2026-10-13 明确授权补充阶段门并完成 Sprint Planning。
