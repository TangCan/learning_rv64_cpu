---
title: '综合双核发现并完成学习日志导航'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'dispatch'
baseline_commit: '2c9de8b4572b2be698b771e8c42fa2f104c584bb'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epic-1-context.md'
  - '{project-root}/_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/learning-record-conventions.md'
  - '{project-root}/_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** LD、SD 和 Sv39 fault 的双核学习单元及过程日志已完成，但读者还缺一篇跨主题总结，且日志首页没有清晰指出综合工作、已完成历史与后续计划的关系。

**Approach:** 新增一篇日期日志，综合两核各自路径、架构共同点、提交/可见性边界和证据缺口，所有比较链接到当前技术单元与证据。更新学习日志首页与学习计划的状态和导航；README 已链接到首页，核对入口有效即可。既有六阶段历史只按现存材料呈现，不能还原的过程继续标为待回顾。

## Boundaries & Constraints

**Always:** 以当前活动版本 `load-v2.md`、`store-v1.md`、`sv39-load-fault-v3.md` 和 trace matrix 为技术结论依据；每项比较都有双侧证据或明确标为 partial/unknown/unverified；日志将证据类型与验证状态分开写；历史回顾如实说明来自既有记录。

**Never:** 不修改不可变学习单元或上游 checkout；不把源码静态路径说成已运行；不推断 DRAM 可见性、未观察 fault 结果或 RVA23 整体符合性；不虚构旧阶段对话和时间线细节；不引入博客服务、生成器或 CPU 测试/构建/仿真。

</frozen-after-approval>

## Code Map

- `learning-journal/2026-10-15-ld-path-review.md`、`2026-10-15-sd-commit-write-boundary.md`、`2026-10-15-sv39-noncanonical-ld-fault.md`、`2026-10-15-three-case-evidence-audit.md` — 已完成过程及证据边界；综合日志引用它们而不重写细节。
- `notes/units/load-v2.md`、`store-v1.md`、`sv39-load-fault-v3.md` — 当前学习单元和活动证据 ID；此前版本只作历史参考。
- `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 六条双侧路径、证据 ID、固定快照和验证状态。
- `learning-journal/index.md`、`plan.md` — 首页时间线及已完成/当前/计划状态；根 `README.md` 已有日志首页链接。

## Tasks & Acceptance

**Execution:**
- [x] `learning-journal/2026-10-15-load-store-fault-synthesis.md` — 写日期、问题、查阅来源/动作、比较发现、证据类型/状态、当前单元链接及下一步；准确综合 LD 写回/退休、SD 接受与 DRAM 可见性、fault 检测与 trap 路径。
- [x] `learning-journal/index.md` — 添加综合日志；明确已完成的本次访存阶段、仍待整理的旧历程和计划中的后续主题；保留历史未知状态。
- [x] `learning-journal/plan.md` — 将综合阶段标完成，摘要双核差异及未验证边界，指出可执行的下一步。
- [x] `README.md` — 核对并在需要时修正日志首页入口，使新读者可到达时间线。

**Acceptance Criteria:**
- Given 三类当前学习单元与矩阵，when 阅读综合日志，then LD/SD/fault 的共同架构目标、Kunminghu/Heliodor 主要路径差异和证据边界均有引用支撑，缺侧明确标出。
- Given SD 与 fault 结论，when 阅读总结，then store commit、buffer/request 接受、DRAM 可见性彼此区分；fault 静态推导不冒充动态观察；RVA23 不作整体符合性结论。
- Given README、日志首页和计划，when 按导航浏览，then 首页可达，已完成/current/planned 状态明确，目标存在；旧阶段未回顾项保留 pending。
- Given 既有材料无法重建完整探索过程，when 描述历史，then 仅陈述来源能证实的事实，不编造过程细节。

## Implementation Notes

- 新增综合过程日志，汇总双核 LD、SD 和 Sv39 fault 路径并逐项链接活动证据；明确静态结论、测试材料和未运行边界。
- 更新日志首页与学习计划，标记本轮静态整理完成；保留六阶段历史待回顾状态。README 已有有效日志首页链接，无需修改。
- 文档链接检查与 `git diff --check` 通过；未运行 CPU 测试、构建或仿真。

## Spec Change Log

## Review Triage Log

| Finding | Verdict and evidence | Route / result |
| --- | --- | --- |
| LD comparison omitted shared case assumptions | `patch`：load-v2 的案例使用自然对齐 8-byte、M-mode Bare、无异常、DCache hit、无更老重叠 store；综合日志现链接该 tuple 并标出未证实前提。 | 已修复 |
| SD comparison omitted selected tuple | `patch`：store-v1 固定 `SD x11,0(x10)`、`x10=0x80004000`、`x11=0x1122334455667788`、M-mode Bare、8-byte 对齐；日志已直链并注明 assumption/unverified。 | 已修复 |
| Kunminghu PMA claim lacked a direct evidence pointer | `patch`：SD1-E3 支持 Kunminghu 默认 PMA 分类，SD1-E7 支持 Heliodor 地址分类；日志已逐项引用并保留运行时未验证说明。 | 已修复 |
| Fault row omitted precise exception behavior | `patch`：SF1-E4/E5 与 SF1-E8/E9 支持故障 load 被标记并在 head 以异常路径提交；日志现明确它不作为正常 load retirement。 | 已修复 |
| Broad evidence ranges did not map key claims precisely | `patch`：日志现将 LD 两侧写回/退休 gate、SD 两侧接受 endpoint、fault cause/delegation selection 分别关联到具体活动 evidence IDs。 | 已修复 |

## Verification

**Commands:**
- `python3 scripts/check_doc_links.py README.md learning-journal/index.md learning-journal/plan.md learning-journal/2026-10-15-load-store-fault-synthesis.md` — 支持的本地链接和锚点均存在。
- `git diff --check` — 无空白错误。

**Manual checks:**
- 对照当前学习单元、过程日志、trace matrix 与来源快照，确认所有综合断言有可达证据，旧版本和未回顾历史未被覆盖或虚构。
- 不运行 CPU 测试、构建或仿真。
