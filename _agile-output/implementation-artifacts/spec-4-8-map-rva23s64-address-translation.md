---
title: 'Story 4.8: 映射 RVA23S64 地址转换与页表要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '80f0501a48f70483812914f6f15f902b5fa19ce6'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-7-map-rva23s64-supervisor-traps.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23S64 的地址转换必选要求尚未映射到两套固定 CPU 快照，satp 模式、页表 walk、A/D fault、内存类型与地址转换缓存失效的支持范围和验证边界尚不清楚。

**Approach:** 依据 RVA23 Profile v1.0 及相关特权/虚拟内存扩展规范，逐项检查七个地址转换要求，记录两侧实现路径、适用条件、测试材料和未验证行为，更新覆盖目录并新增学习单元。

## Boundaries & Constraints

**Always:** 分别映射 `Svbare`、`Sv39`、`Svade`、`Ssccptr`、`Svpbmt`、`Svinval`、`Svnapot`；保留满足 cacheability 与 coherence PMA 的主存区域条件；区分静态源码、测试源码和本轮实际测试结果。Sv48/Sv57 和 Svadu 属于 profile expansion options，不作为本故事必选项；若源码涉及，只作范围说明。

**Never:** 不修改上游快照；不将某一种模式、单条测试或局部 RTL 推广为整体符合性；不将 Hypervisor 的 VS/G-stage 映射、A/D 硬件更新选项或其他 S64 领域扩展到本故事结论中。

</frozen-after-approval>

## Code Map

- `notes/rva23-coverage.md`：只更新 `RVA23S64/v1.0/§3.1.2.2/{Svbare,Sv39,Svade,Ssccptr,Svpbmt,Svinval,Svnapot}` 七行。
- Kunminghu 固定快照：`backend/fu/NewCSR/SupervisorLevel.scala`、`CSRDefines.scala` 的 satp WARL 模式；`cache/mmu/{MMUConst,TLB,PageTableWalker,TLBStorage,L2TLB}.scala` 的模式识别、翻译层级、A/D 与失效；`backend/fu/{Fence,PMP}.scala`、`MemBlock.scala` 的 fence、PMP/PMA 和页表内存访问。需核实配置实际实例化的 CSR 路径，避免把旧/替代实现混作活动配置。
- Heliodor 固定快照：`src/mmu/mmu.veryl`、`dmem_mmu.veryl`、`imem_mmu.veryl` 的 Bare/Sv39、页表 walk、TLB、PTE 权限与 A/D；`pmp_check.veryl` 的物理访问权限；`src/core/decoder.veryl` 的 fence 指令路径。
- 既有验证材料：Heliodor `tb/test_mmu.veryl`（Bare/Sv39 与 ASID/选择性失效）及 `tb/test_arch_common.veryl` 中 Svade 相关测试；核实实际 runner 并按用户授权尝试可运行的现有目标测试。Kunminghu 测试需先定位已有 MMU/PTW/TLB 入口。
- 规范：[RVA23 Profile v1.0 §3.1.2.2–3.1.2.3.3](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)；相关特权架构与 Sv39、Svpbmt、Svinval、Svnapot ratified 文本按实际映射条款补充版本和链接。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 为七项地址转换必选要求补全两侧状态、路径或范围决定、适用条件、子案例和学习单元证据链接。
- [x] `notes/units/rva23s64-address-translation-v1.md` — 记录规范行为、Kunminghu/Heliodor 路径、测试证据、差异及未解问题；不把非必选扩展记作本故事验收项。
- [x] `notes/units/index.md` — 登记学习单元并如实说明验证状态。
- [x] 核查并尝试现有目标测试入口；记录工具版本、命令和实际结果。Heliodor Bare/Sv39 与 ASID tests 通过；Svnapot 架构 harness 在 check 阶段被现有 testbench 错误阻断；Kunminghu 未找到合适的 MMU 定向测试入口。

**Acceptance Criteria:**
- Given 七个 profile 要求键，when 查看覆盖目录，then 两个实现各自都有状态、证据范围、条件、子案例和可追溯证据 ID。
- Given Bare/Sv39、A/D page-fault、页表隐式读取、PBMT、细粒度失效和 NAPOT，when 阅读学习单元，then 可区分架构要求、实现路径、适用 PMA/模式条件和未验证行为。
- Given Sv48、Sv57、Svadu 或 Hypervisor 相关源码线索，when 查看本单元结论，then 它们不会被误标为 RVA23S64 本故事的必选要求或本故事范围内的完整支持结论。
- Given 本轮检查的测试，when 阅读证据表，then 已检查源码、测试材料和实际运行结果分开记录，未执行项不标为通过。

## Implementation Notes

已完成七项映射和单元记录。Kunminghu 活动 CSR 路径仅接受 satp.MODE=0/8；Sv48/Sv57 与 Svadu 明确限定为 expansion-option 范围。PMA 区域、A/D faults、PBMT 细节、完整 Svinval 顺序和 NAPOT 子页行为未验证。Heliodor test_mmu 测试项本轮通过；架构 Svnapot harness 受 testbench 编译错误阻断。

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Blind Hunter: Kunminghu Svade evidence omitted D=0 store faults | low / patch | Checked `TLB.scala:487–489, 517, 548–550`; `stUpdate` raises the store page-fault path for A=0 or D=0. Added exact static path and kept runtime status unverified. |
| Blind Hunter: Bare/Sv39 test result did not explain separate mode setup | low / patch | Checked `tb/test_mmu.veryl:113–140, 176`; the harness reads in M/Bare, changes satp to Sv39 and S-mode, repeats the VA read, then asserts both values match the marker. Added phases and assertion condition. |
| Blind Hunter: SFENCE.VMA test could be mistaken for Svinval evidence | low / patch | `test_mmu_asid` executes SFENCE.VMA selective invalidation. Removed it as Svinval execution evidence and labeled its actual scope; SINVAL.VMA and ordering-fence behavior remain unverified dynamically. |
| Blind Hunter: PBMT mapping lacked encoding and control detail and overstated the final path | low / patch | Checked the ratified Svpbmt table and source field paths. Added `menvcfg.PBMTE`, encodings 0=PMA/1=NC/2=IO/3=reserved, and limited implementation evidence to field checks/response while leaving final memory attributes unverified. |
| Blind Hunter: Heliodor Svinval mapping omitted privilege conditions | low / patch | Checked decoder and commit-time checks at `heliodor_core.veryl:4339, 4385–4396`; documented U illegal, S TVM behavior, M/S ordering-fence NOP path, and left VS/VU behavior unverified. |
| Blind Hunter: Profile/extension references were not section-specific | low / patch | Added direct links to the Profile mandatory and expansion sections and ratified Svpbmt v1.0, Svinval v1.0, and Svnapot v1.0 chapters. |
| Blind Hunter: MMU/SFENCE run evidence was not scoped to the phases and extension tested | low / patch | Added the M/Bare and S/Sv39 phases and marker assertion for `test_mmu`; explicitly says the additional ASID case tests SFENCE.VMA only. Removed that run as Svnapot evidence. |

## Verification

**Commands:**
- `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl --version` — `veryl 0.22.0 (967e477 2026-10-02)`。
- `veryl test --test test_mmu`（cwd `sources/heliodor`）— 2 passed, 0 failed, 29 ignored；观察到 Bare/Sv39 和 ASID selective SFENCE 案例。
- `veryl test --test test_arch_svnapot`（cwd `sources/heliodor`）— check 阶段失败：`test_arch_common.veryl:440 invalid_initial_assign`（`$readmemh` 对 dram 的 initial assignment）；testbench 同时有缺端口 warnings；测试未启动。
- Kunminghu MMU/PTW/TLB 测试入口搜索：未找到对应定向测试，因此未运行。
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — 实际结果：`valid: true`。
- `git diff --check` — expected: no whitespace errors。

**Manual checks:** 对照 profile 条目逐项核对七个键、PMAs、模式条件、证据链接及状态边界。
