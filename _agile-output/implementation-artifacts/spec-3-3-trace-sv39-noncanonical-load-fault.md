---
title: 'Story 3.3: 追踪 Sv39 非规范 load 地址异常'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '1fc59cc46eba869e4e84c272e88e10971fc29621'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 学习记录尚未比较地址转换错误如何从内存请求转为架构异常，也未说明异常如何影响控制流与特权状态。

**Approach:** 选取 S-mode、单阶段 Sv39 下普通 RV64 `LD` 使用非规范虚拟地址而产生 load page fault 的事件，追踪两边的检测、异常传递与 trap 入口，并与规范结果核对。

## Boundaries & Constraints

**Always:** 固定使用 `sources.lock` 中的源码快照和 RISC-V Privileged Architecture v20260120；限定 `i_virt=0`、`satp.MODE=Sv39`、S-mode 普通标量 load，故障原因为 VA[63:39] 不等于 VA[38] 的符号扩展；案例令 `medeleg[13]=0`、`mtvec` 有效，使 load page fault（cause 13）进入 M-mode trap；记录 faulting VA、load PC、异常原因及控制流变化；区分规范、静态源码、已检查测试和实际运行结果；检查并尝试运行现有 Heliodor page-fault 与 Sv39 MMU 测试；区分测试源码、未匹配过滤器、运行通过但不覆盖本事件的测试及真实覆盖。

**Never:** 不新增测试、不修改上游源码；不外推至 Sv39 page-table walk/PTE 权限、A/D 更新、TLB miss/hit 行为、superpage、Sv48/Sv57、虚拟化/G-stage、访问异常、非规范 store/取指或 RVA23 整体符合性；不把静态路径或测试源码描述成动态观察。

</frozen-after-approval>

## Code Map

- 固定来源：Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，见 `sources.lock`。规范候选为 [Privileged Architecture v20260120 §12.4 Sv39](https://docs.riscv.org/reference/isa/priv/supervisor.html)（Sv39 地址格式/有效性）与 §12.1.1（load page fault cause 13）；核对异常值与 trap 语义，不推导 profile 合规性。
- Kunminghu：`cache/mmu/TLB.scala:221-260` 生成 39 位规范性检查 `pf39` 并保存异常 VA；`:470-555` 区分 load 与 store/page fault 并生成 TLB response。`mem/pipeline/LoadUnit.scala:1028-1048,1209-1219` 将 TLB fault 写入 load exception vector，并抑制 fault 后不可靠的 PMP/PMA 响应。沿 `backend/rob/Rob.scala:620-680,1311+`、`backend/fu/CSR.scala:1311-1410`、`backend/CtrlBlock.scala` 追踪异常队列、trap cause/tval 与 redirect；实现时核实具体行号和 CSR 更新顺序。
- Heliodor：`mmu/mmu.veryl:194-206` 启用条件与非规范 VA 检测，`:1234-1271` 产生即时 fault 并区别 access fault；`mmu/dmem_mmu.veryl:251-263` 传递 load page fault。`core/alu_wrap.veryl:467-494` 选择 load fault 类型，`core/rob.veryl:1486-1500` 登记 fault 所属 ROB 指令和 VA，`core/heliodor_core.veryl:4671-4812` 计算委托、cause/tval、CSR trap 输入，`:5085-5096` 处理 trap redirect。已有 `test/c/smode_pgfault_test.S` 含 cause 13 handler 分支，但实际触发的是 cause 15 store fault；修复 PTE 后的 `LD` 正常完成，不覆盖本案例。`tb/test_mmu.veryl` 是可运行的成功翻译测试，不覆盖 page fault。
- 复用 `notes/templates/learning-record.md` 和 `notes/units/index.md`；新增不可变 `notes/units/sv39-load-fault-v1.md`。只改学习资料、索引、spec 与 sprint 元数据。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/sv39-load-fault-v1.md` — 记录规范语义、固定快照下双边检测到 M-mode trap 路径、证据 ID、自检及未验证边界。
- [x] `notes/units/index.md` — 将新版本加入单元索引。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` — 完成审查后将 Story 3.3 与已完成全部子故事的 Epic 3 标记为 done。

**Acceptance Criteria:**
- Given 固定规范与快照，when 解释选定非规范地址，then 记录其 load page fault 架构结果、cause 与适用边界。
- Given 两边实现，when 追踪一次 load fault，then 记录地址检查、异常传递、ROB/提交 trap 与 redirect 路径，并用双侧证据 ID 支持比较结论。
- Given 既有测试材料，when 汇报验证，then 区分测试入口、已检查测试与实际运行结果，不声称未观察的执行通过。
- Given 单元记录完成，when 更新学习索引，then 使用新的不可变 `<unit_id>-vN.md` 文件并链接索引。
- Given 阶段自检，when 回答，then 说明地址转换异常如何改变控制流/特权状态并指出至少一项未验证边界。

## Implementation Notes

已运行现有 Heliodor `test_mmu`，它验证 Sv39 page-table walk 的成功路径；未找到匹配 `test_smode_pgfault` 的 Veryl test module。对应的 S-mode 汇编用例涵盖 cause 15 store fault，修表后的 load 是正常路径。没有新增测试或修改上游源码。

规划选择：非规范 Sv39 load VA 在两边都有明确的检查点，能将同一架构 fault 从地址有效性检测追踪至 trap；避开未锁定的 page-table walker 子实现差异。预期修改仅为文档及 sprint 状态，没有不可逆操作、外部副作用或新增软件 API。

## Spec Change Log

## Review Triage Log

- low — 盲审指出“handler 返回地址由 `mtvec` 给出”混淆入口和返回 PC；已修正为 `mtvec.BASE` 提供同步 trap 入口、`mepc` 保存故障指令 PC 并供 MRET 返回。证据：Privileged Architecture v20260120 §3.1.7、§3.1.14 及单元记录。route: patch。
- low — 盲审指出子案例的 `covered` 可能表示动态覆盖；已将配置与 `mtval` 项标记为 `documented (static)`，明确未动态观察。证据：本单元只运行了不同的 MMU happy-path 测试。route: patch。
- low — 盲审指出 vectored `mtvec` 下同步异常入口未说明；已注明同步异常仍跳转到 `BASE`，偏移仅用于中断。证据：Privileged Architecture v20260120 Machine-Level ISA §3.1.7。route: patch。
- low — 盲审指出非法 VA 的 WARL 转换边界不清楚；已分开陈述规范要求与实现行为：若 `mtval` 非零，其值指向 fault VA，但无法表示的非法地址可转换为实现可表示的另一个非法地址。证据：Privileged Architecture v20260120 §3.1.16。route: patch。
- low — 盲审指出源码路径文字易被读为运行观察；已在两侧路径摘要与学习者总结明确标注为规范预期或源码静态推导，并说明未动态观察。证据：本故事测试仅运行普通 Sv39 翻译 happy path。route: patch。
- false — 边界审查未报告未处理路径；无需修订。
- false — 验证缺口审查未发现缺口；测试边界与记录的动态验证范围一致。

## Design Notes

本案例固定 S-mode、V=0，且 `medeleg[13]=0`，因此不需在 S/M 委托两种 trap 目标间泛化；异常发生后同步 trap 至 M-mode。需区分“Sv39 的非规范地址 page fault”与“PMP/PMA access fault”，并依据来源分别说明故障 VA 的携带与 `mtval` 更新。

## Verification

**Commands:**
- `git diff --check` — 文档改动无空白错误。
- 在 `sources/heliodor` 运行 `/tmp/rv64cpu-story32-toolchain/bin/veryl test --test test_mmu`，Veryl 0.22.0-nightly；输出 `2 passed, 0 failed, 29 ignored`；filter 同时匹配 test_mmu_asid。仅验证已有 Sv39 翻译 happy path，不覆盖本故事的异常场景。

**Manual checks:**
- 核对固定 SHA、规范条款、故障条件、trap delegation/cause/tval/redirect 路径、证据 ID、测试边界和索引目标。非规范 load fault 未动态验证；一般 Sv39 翻译测试通过不外推为该异常路径通过。
