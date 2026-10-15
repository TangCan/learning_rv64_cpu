---
title: '追踪双核 Sv39 非规范地址 LD fault'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'f864178c86c93b4a9b4f3794e58f23031c6c4d9e'
context:
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epic-1-context.md'
  - '{project-root}/notes/units/sv39-load-fault-v1.md'
  - '{project-root}/_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/learning-record-conventions.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 现有 fault 知识单元已记录双核静态路径，但没有将 Epic 固定的非规范地址作为同一案例贯穿证据；Kunminghu 的 CSR 集成路径和 Heliodor 额外的通用 ACT 覆盖也需要按锁定源码重新核对。

**Approach:** 保留已发布的 v1，按两个 `sources.lock` 快照审查并发布 v2，固定 S-mode、V=0、Sv39、`LD`、VA `0x0000008000000000`、`medeleg[13]=0`，追踪 load page fault 到 M-mode trap 更新。更新过程日志、学习导航和矩阵；严格区分规范预期、静态源码、测试材料与本案例未运行状态。

## Boundaries & Constraints

**Always:** 使用固定完整 SHA；说明 VA bit 38/39 使该值在 Sv39 下非规范；区分 fault 检测、ROB 精确异常、cause 13、故障 PC/`mepc`、`mtval` 规则与 trap redirect；引用可复查源码位置；既有 v1 不可修改。

**Never:** 不修改上游 RTL；不把通用 ACT 测试或历史测试摘要写成本案例执行结果；不声称观察到本案例 trap、CSR 值或周期；不扩大为页表遍历、access fault、完整 profile 符合性结论。

</frozen-after-approval>

## Code Map

- `notes/units/sv39-load-fault-v1.md` 是已发布基线；保留它，审查其中条件、测试边界和证据归属，必要时在 v2 纠正但不改写历史版本。学习记录格式见 `learning-record-conventions.md`。
- Kunminghu `TLB.scala:139-175,216-267,470-541` — Sv39 `pf39`、full-VA pre-fault、load page-fault response 与 fault VA；`LoadUnit.scala:391-392,1009-1048,1209-1221,1417-1426,1804-1813` — 普通 load 检查请求、异常传播与写回抑制；`ExceptionGen.scala:77-145`、`Rob.scala:576-680` — 精确异常到 ROB head。CSR 集成用 `fu/wrapper/CSR.scala:65,125-137`、`NewCSR/TrapHandleModule.scala:22-75,104-110`、`NewCSR/NewCSR.scala:420-438,801-820,1032-1034,1124-1139`、`NewCSR/CSREvents/TrapEntryMEvent.scala:20-145` 核实 ROB exception 输入、delegation 与 M trap event；不要把旧 `CSR.scala` 路径误写成当前 wrapper 的活动路径。
- Heliodor `mmu/mmu.veryl:194-206,1224-1289`、`mmu/dmem_mmu.veryl:249-263` — 非规范地址直接 fault 并阻止 walk；`core/heliodor_core.veryl:3047-3050,4580-4604,4671-4728,4773-4812`、`core/alu_wrap.veryl:467-494`、`core/rob.veryl:1344-1368`、`core/csr.veryl:899-950` — load fault 身份/VA、commit cause/delegation、CSR 更新和 redirect。
- `sources/heliodor/test/act/README.md:112-125` 说明一般 Sv39 非规范地址 ACT 案例；`test/act/Makefile` 和生成配置说明运行机制。只检查锁定 checkout 中现存材料，不能推断该套件含有本例精确 VA、特权和 delegation 配置。
- `sources.lock` 锁定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。不得改动两处来源。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/sv39-load-fault-v2.md` — 审核 v1 后发布新版本，记录固定输入、非规范性推导、两侧检测/精确异常/陷入路径、M-mode CSR 更新边界、测试材料和未验证项；用单元内唯一的 `SF1-E1` 起始证据 ID。保留 v1。
- [x] `learning-journal/2026-10-15-sv39-noncanonical-ld-fault.md` — 记录本次源码复核过程、发现及证据限制，链接 v2。
- [x] `notes/units/index.md`、`learning-journal/index.md`、`learning-journal/plan.md` — 指向 fault v2 和日志，标记本阶段静态复核完成、动态案例仍未验证。
- [x] `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 增加 Kunminghu、Heliodor fault 两行，写明同一输入、源码支持终点、固定 SHA、证据类型/状态和未知项。

**Acceptance Criteria:**
- Given 固定案例与两个锁定快照，when 检查 fault 路径，then 两侧均有可追溯证据从非规范检查到 load page fault、PC/VA 保留和 trap 状态选择；Kunminghu 采用 wrapper 所接 NewCSR 路径。
- Given `VA=0x0000008000000000`，when 按 Sv39 检验，then 明确 bit 38 为 0、bit 39 为 1，因而不满足 `[63:39]` 对 bit 38 的符号扩展；这只是输入分类，不是运行观察。
- Given S-mode 且 `medeleg[13]=0`，when 说明目标 trap，then 分开列出架构条件和来源逻辑；cause 13、故障 PC、`mtval` 的实现选择/WARL 限制及 M-mode target 不混为实测寄存器结果。
- Given Heliodor ACT 文档提及一般非规范 Sv39 案例，when 总结测试证据，then 标为测试材料/历史摘要；未确认确切 tuple 时不称其覆盖本案例，且不运行测试、构建或仿真。
- Given 新版交付，when 检查导航和来源，then v1 未改、证据 ID 在 v2 内唯一、所有链接锚点有效、源码 checkout HEAD 与 `sources.lock` 一致、矩阵两侧均明确标注本案例未动态验证。

## Implementation Notes

- 新增 fault-v2、日期日志和两侧矩阵行；审查旧版时确认当前 Kunminghu wrapper 实例化 NewCSR，纠正活动 trap 路径，v1 保持不变。Heliodor ACT README 仅作通用测试材料，未将其历史摘要当作本例测试。链接检查通过；两份上游快照匹配 sources.lock；本例未运行测试、构建或仿真。

## Spec Change Log


## Review Triage Log

- Blind Hunter 1 / Verification Gap 1 — medium / patch — 已将 sprint 状态与实现完成阶段对齐为 `review`，并更新本地时间戳；两位审查者指出的旧 `in-progress` 状态会误报当前工作阶段。
- Blind Hunter 2 / Verification Gap 2 — medium / patch — 将规范入口固定到 v20260120 edition-pinned 索引，并记录该官方 PDF 的 SHA-256；此前滚动页面不能独立复现声明版本。
- Blind Hunter 3 — medium / patch — 将 `sv39_canonical` 限定为 README 中可见的标签，并明确 README 修复文字及标签不足以证明测试输入/断言；没有从命名推断覆盖范围。
- Blind Hunter 4 — medium / patch — 补充 Kunminghu `Backend.scala` 的 ROB 异常/VA 接口到 CSR wrapper `fromRob.trap`/`fromMem.excpVA` 的信号连接；原叙述缺少 PC/cause 传递接口证据。
- Blind Hunter 5 — medium / patch — Heliodor 矩阵现分别引用 README 检查 SF1-E11 和精确未运行 tuple SF1-E12；此前把源码/README 已检查与 tuple 未验证压在同一证据状态中。
- Blind Hunter 6 — low / patch — 自检证据范围扩到 SF1-E11，使 ACT 材料边界也被答案引用；这是直接的证据引用修正。
- Blind Hunter 7 — false — 评审开始时 triage log 按工作流尚待填写；该项是评审流程阶段状态，不是交付遗漏，且本日志已按流程记录全部结论。
- Verification Gap 1 — medium / patch — 与 Blind Hunter 1 同一状态缺陷，以上已修复；实际 sprint 文件由 `in-progress` 改为 `review`。
- Verification Gap 2 — medium / patch — 与 Blind Hunter 2 同一版本固定缺陷，以上已修复；当前版本索引和不可变 PDF 哈希可复查。


## Design Notes

保留 v1 的理由：原记录和其检查历史有复查价值；v2 只负责新增固定 tuple 并校正活动 CSR 集成/测试覆盖边界，避免静默改写已发布结论。

## Verification

**Commands:**
- `python3 scripts/check_doc_links.py ...` — 新增及更新文档的本地链接和锚点有效。
- `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/sprint-status.yaml` — sprint 状态合法。
- `git diff --check` — 无空白错误。

**Manual checks:**
- 核对两 checkout HEAD、VA 位条件、NewCSR TrapHandle delegation 选择、Heliodor ACT 文档范围和证据 ID；确认 fault v1 未修改。
- 不运行 fault 测试、构建或仿真；动态 cause、trap CSR、`mtval` 表现与执行时序保持未验证。
