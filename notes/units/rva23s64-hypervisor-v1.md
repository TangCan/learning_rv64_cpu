---
unit_id: "rva23s64-hypervisor"
stage_id: "Epic 4 / Story 4.9"
scope: "RVA23S64/v1.0/§3.1.2.2 中 Sha 的八个组成要求 H、Ssstateen、Shcounterenw、Shvstvala、Shtvala、Shvstvecd、Shvsatpa、Shgatpa；固定 Kunminghu V2 与 Heliodor 快照的有限源码、测试材料和测试运行映射。"
exclusions:
  - "不表示完整 H 扩展、Sha 或 RVA23S64 符合性；只映射八项强制组成要求。"
  - "宿主 RVA23S64 的 profile 要求不等于 guest VM 必须实现同一 profile。"
  - "H 的其他可选行为、G-stage 扩展、AIA、debug、全部 trap 优先级及完整系统交互不在本轮结论内。"
  - "Kunminghu 同时存在旧 CSR 实现与 NewCSR 组合；部署/选择关系未完全闭合时只记录各路径，不将替代路径当成已活动路径。"
  - "未执行的子案例保持未验证；搜索未定位的状态寄存器不据此判为不存在。"
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0, ratified 2024-10-17"
    section: "§3.1.2.2 mandatory extensions; Sha comprises H and seven named supporting requirements"
    url: "https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-2-rva23s64-mandatory-extensions"
    profile_category: "mandatory"
  - name: "RISC-V Privileged Architecture, H extension"
    edition: "v1.13 base; H v1.0 ratified"
    section: "Chapter 14: H CSRs, traps, VS/G-stage translation; §14.1.10 htval and §14.1.11 vstval"
    url: "https://docs.riscv.org/reference/isa/v20240411/priv/hypervisor"
    profile_category: "ratified normative architecture"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    repository: "https://github.com/OpenXiangShan/XiangShan.git"
    branch: "kunminghu-v2"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    repository: "https://github.com/dalance/heliodor.git"
    branch: "master"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

<!-- Sha 按八个组成要求分别追踪；Sha 这个组合名不增加第九项。 -->

## 要求语义和验证边界

RVA23S64 v1.0 §3.1.2.2 将 Sha 定义为增强型 Hypervisor 要求组合。该组合由 H、Ssstateen、Shcounterenw、Shvstvala、Shtvala、Shvstvecd、Shvsatpa、Shgatpa 构成。目录按八个稳定键逐项追踪，组合名不重复计数。`Shvstvala` 继承 [`RVA23S64/v1.0/§3.1.2.2/Sstvala` 覆盖行](../rva23-coverage.md)，适用 `Sstvala` 所列的 `stval` 情形；其宿主 profile 义务适用于宿主实现，不自动要求被管理的 guest VM 声明 RVA23S64。

| 要求 | 规范行为 | 本轮子案例边界 |
| --- | --- | --- |
| H | Hypervisor 扩展 v1.0：HS/VS 状态、虚拟 CSR、陷阱与两阶段地址转换等架构规定行为。 | 只考察与本组合其他要求直接相关的 CSR、陷阱值、VS vector 和翻译模式线索；不穷举 H 指令及所有架构行为。 |
| Ssstateen | 提供 `sstateen0–3` 和 `hstateen0–3`。 | 寄存器定义、字段、可访问性和权限链分别检查；源码定义不等于运行时 CSR 权限矩阵。 |
| Shcounterenw | 对每个不是只读零值的 `hpmcounter`，对应 `hcounteren` 位可写。 | 必须先确认实际实现的 counter 集合及 RO-zero 属性，再逐位验证写读；本轮未完成此矩阵。 |
| Shvstvala | 在 [`Sstvala` 覆盖行](../rva23-coverage.md)适用的全部情形下，VS trap 将相应值写入 `vstval`。 | 继承的具体类别为 load/store/fetch page fault、access fault、misaligned、breakpoint（EBREAK/C.EBREAK 除外）、virtual-instruction 和 illegal-instruction；未逐类验证 trap 输入。 |
| Shtvala | 在 H 规范允许的所有情形下，`htval` 保存 guest physical fault address 的架构规定编码。 | guest-page fault 的 fetch/load/store、VS 页表遍历中的 G-stage fault 和例外/零值条件未穷尽。 |
| Shvstvecd | `vstvec.MODE` 可取 Direct=0；Direct 下 BASE 能保存任何有效四字节对齐地址。 | 需多地址写读及实际 trap target；仅有寄存器/路由源码线索。 |
| Shvsatpa | `vsatp` 支持 `satp` 支持的全部翻译模式。 | 按各实现的宿主 `satp` WARL 集合比较；扩展选项模式不外推为必选。 |
| Shgatpa | 对 `satp` 支持的每种 SvNN，`hgatp` 支持对应 SvNNx4，并支持 Bare。 | 需比对宿主 mode 集合、WARL 写读及实际 G-stage walk；本轮只有局部源码和测试材料。 |

## Kunminghu 路径

- **CSR 路径边界：** `FuConfig.CsrCfg` 构造 `backend.fu.CSR`，而 `backend.fu.wrapper.CSR` 包装 `NewCSR`。因此同时记录两者，不能把 `NewCSR` 的完整 state-enable 实现不加条件地当作所有配置的活动 CSR 路径。旧 CSR 可见 H/VS 状态、CSR map 与权限/翻译控制；NewCSR 的 `HypervisorLevel`、`VirtualSupervisorLevel`、`SupervisorLevel` 有更细的 H/VS CSR 组合和 state-enable 定义。
- **H / traps / translation：** 旧 CSR 路径定义 `htval`、`hgatp`、`hcounteren`、`vstvec`、`vstval`、`vsatp`；`NewCSR` 连接 CSRPermitModule、trap events 与 V 状态的 MMU mode 输出。HSEvent 有 GPA 到 `htval` 的选择和 `>>2` 编码线索，VSEvent 把异常值送入 `vstval`。MMU 与 trap code 定义 HS/VS fault 路由；完整指令/CSR/异常矩阵未查完。
- **Ssstateen：** NewCSR 定义 `sstateen0–3` 和 `hstateen0–3`。字段 bundle 含读写/只读位，权限模块有 HS/VS 的 stateen 检查线索。状态不覆盖旧 CSR 配置是否选择该组合，也不覆盖所有字段的读写行为。
- **Shcounterenw：** 旧 CSR 路径的 `hcounterenMask` 是零；NewCSR 路径使用 `Counteren` 并在 VS counter 权限计算中与 `mcounteren` 组合。活动配置与非 RO-zero 的实际 HPM counter 集合需要统一确认，因此不据单一路径直接判符合或不符合。
- **Mode pair：** 旧路径的 satp mode 合法检查只接受 Bare/Sv39，`vsatp` 使用 satp mask；NewCSR 存在 VSatp WARL 以及 Bare/Sv39x4/Sv48x4 mode 条件。Sv48/Sv48x4 只作范围线索；未验证从寄存器写入到完整 walk 的模式配对。

## Heliodor 路径

- `csr.veryl` 有 HS/VS CSR 状态变量、读写路由和 V=1 的 S-CSR alias；`heliodor_core.veryl` 连接陷阱信息与 `vstvec` target；`mmu.veryl` 接收 `vsatp`、`hgatp` 并执行 VS/G-stage walk。
- G-stage guest-page fault 可由 MMU 输出 fault GPA；core 形成 `htval` 输入（GPA>>2），CSR trap entry 对 guest-page fault cause 20/21/23 写 `htval`。现有注释/测试材料表明该路径集中于已实现的 fault case；规范允许的所有情形尚未覆盖。
- VS trap 分支写 `vstval=i_trap_tval`；`vstvec` 进入 delegated VS trap target 选择。输入值生成、MODE WARL 与全部合法 BASE 均未逐项证明。
- `hcounteren` 有状态、read/write map；HPM counter 3–31 地址范围存在。缺少本轮逐位读写和 RO-zero 条件验证。所检查的 CSR 范围未定位 `sstateen` / `hstateen`，但搜索未发现不构成不存在的证据，保持 `not-studied`。
- MMU code 展示 VS Sv39 walk 与 G-stage Sv39x4；Bare 分支也可见。未完整审计 `satp` 与 `vsatp` 的支持集合、CSR WARL、所有合法 `hgatp` 配对及异常响应。

## 测试材料和比较结论

Heliodor `test_arch_common.veryl` 中已检查 H 相关目标材料：`test_arch_hvstrap`、`test_arch_hvirq`、`test_arch_hgpf`、`test_arch_hgpfns`、`test_arch_hvinst`、`test_arch_hvscsr`、`test_arch_hvtvm`；另有 `test_soc_hvlinux`。这些只是已检入测试源码；未运行通过的目标不作运行证据。Kunminghu `src/test/scala` 搜索 H CSR/VM 相关目标时未找到可确认的定向用例，不能据此推断无测试或功能不存在。

| Claim ID | 比较结论 | Kunminghu evidence | Heliodor evidence |
| --- | --- | --- | --- |
| C1 / H | 两侧均有 H/VS CSR、虚拟化状态和 VS/G 两阶段相关静态线索；这不代表完整 H 或 Sha 覆盖。 | E2 | E3–E5 |
| C2 / Ssstateen | NewCSR 源码有 s/h stateen0–3 与权限线索；旧 CSR 配置活动关系仍需确认。Heliodor 相关寄存器在所查范围内未知。 | E2 | E3 |
| C3 / Shcounterenw | Kunminghu 不同 CSR 路径的 hcounteren mask/Counteren 存在差异；Heliodor 有可读写 hcounteren 与 HPM 范围。两侧 counter 集合和逐位矩阵未运行。 | E2 | E3 |
| C4 / Shvstvala | 两侧 VS trap entry 有向 `vstval` 写入异常值的静态路径；继承的 Sstvala 输入类别和委托组合未逐项验证。Guest-page fault test attempt 不作为 vstval-specific run evidence。 | E2 | E3,E6 |
| C5 / Shtvala | 两侧有 GPA 到 `htval` 的静态路径；Heliodor 定向 guest-page fault test 被共享 testbench check 阻断，未执行测试体。完整 ISA-permitted fault 情形未覆盖。 | E2 | E3,E5–E6 |
| C6 / Shvstvecd | 两侧有 vstvec CSR 和 VS trap target 线索；Direct WARL 与任意合法 BASE 未运行验证。 | E2 | E3 |
| C7 / Shvsatpa | 两侧 `vsatp` 有 VS-mode 翻译路径线索；`satp` 与 `vsatp` 所有支持模式的逐模式比较和 WARL 读回未核验。 | E2 | E3,E6 |
| C8 / Shgatpa | 两侧均有 Bare 与 Sv39x4 G-stage 路由线索；每个 satp SvNN 对应的 hgatp SvNNx4 模式、WARL 读回和实际 walk 未全部核验。 | E2 | E3–E6 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim | Kind | Status | 项目 / snapshot | 证据位置 / 测试材料 | Command / configuration | Observed / scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Sha 身份、八项要求语义和继承关系 | spec | inspected | RVA23 Profile v1.0; Privileged Architecture v1.13/H v1.0 | [RVA23S64 mandatory extensions §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-2-rva23s64-mandatory-extensions); [H v1.0 ratified chapter](https://docs.riscv.org/reference/isa/v20240411/priv/hypervisor) | not-run | 仅八个 Sha 组成项；不增加 Sha 汇总行，不把宿主 requirement 泛化到 guest VM。 |
| E2 | Kunminghu 静态 CSR、权限、trap 和 mode 路径 | source | inspected | `xiangshan-kunminghu-v2-20261012` | [legacy CSR](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala); [FuConfig CSR selection](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/FuConfig.scala); [wrapper selecting NewCSR](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/CSR.scala); [NewCSR integration and MMU mode outputs](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala); [HypervisorLevel](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/HypervisorLevel.scala); [VirtualSupervisorLevel](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/VirtualSupervisorLevel.scala); [SupervisorLevel](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SupervisorLevel.scala); [StateEnBundle](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/StateEnBundle.scala); [CSRPermitModule](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRPermitModule.scala); [TrapHandleModule](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/TrapHandleModule.scala); [HS trap event](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSREvents/TrapEntryHSEvent.scala); [VS trap event](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSREvents/TrapEntryVSEvent.scala); [translation event mode selection](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSREvents/CSREvent.scala); [page-table walker](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/PageTableWalker.scala) | static source only | `FuConfig.CsrCfg` and `wrapper.CSR` show distinct CSR construction paths; NewCSR has explicit connections to permission, trap, translation-mode, and page-walk code. The links document code relationships, not which path is enabled in every complete core configuration or runtime behavior. |
| E3 | Heliodor 静态 H/VS CSR、trap 与 MMU paths | source | inspected | `heliodor-master-20261012` | [CSR](../../sources/heliodor/src/core/csr.veryl); [core trap/MMU integration](../../sources/heliodor/src/core/heliodor_core.veryl); [two-stage MMU](../../sources/heliodor/src/mmu/mmu.veryl) | static source only | Includes observed CSR storage/routing, V trap path, guest GPA fault path and Sv39/Sv39x4 walk. Does not establish all required cases. |
| E4 | H architecture test materials and Kunminghu test search | test-inspected | inspected | Both fixed snapshots | Heliodor [`test_arch_common.veryl`](../../sources/heliodor/tb/test_arch_common.veryl) targets `test_arch_hvstrap`, `test_arch_hvirq`, `test_arch_hgpf`, `test_arch_hgpfns`, `test_arch_hvinst`, `test_arch_hvscsr`, `test_arch_hvtvm`; [`test_soc_hvlinux.veryl`](../../sources/heliodor/tb/test_soc_hvlinux.veryl); Kunminghu `src/test/scala` search | not-run | Heliodor files are test material only; Kunminghu search did not identify a confirmed targeted test. |
| E5 | Heliodor guest-page fault target attempt | test-run | run-fail | `heliodor-master-20261012` | [`test_arch_hgpf`](../../sources/heliodor/tb/test_arch_common.veryl) | cwd `sources/heliodor`; `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_hgpf`; Veryl `0.22.0 (967e477 2026-10-02)` | Check failed at `tb/test_arch_common.veryl:440 invalid_initial_assign`: `$readmemh(HEX_FILE, dram)` assigns `dram` in an initial block. Runner also emits stale missing-port warnings. Test body did not execute. |
| E6 | Heliodor H/VS trap and guest translation case material | test-inspected | inspected | `heliodor-master-20261012` | `test_arch_hvstrap` (VS delegation); `test_arch_hvirq` (VS interrupt); `test_arch_hgpf`/`test_arch_hgpfns` (guest-page faults); `test_arch_hvscsr`, `test_arch_hvtvm`; `test_soc_hvlinux` | not-run | Read comments/setup/assertions only. Runtime claims are limited to E5; guest Linux material does not establish profile compliance. |
| E7 | Kunminghu MMU/CSR directed test search | test-inspected | unverified | `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/test/scala` keyword/target search for H, VS, hgatp, vsatp, and CSR | not-run | No confirmed directed target located; do not infer absence or non-support. |

## 验证状态

- Veryl: `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl --version` → `veryl 0.22.0 (967e477 2026-10-02)`。
- Attempt: cwd `sources/heliodor`; `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_hgpf` → check failed before test execution at the existing `dram` `$readmemh` initial assignment (`invalid_initial_assign`, `test_arch_common.veryl:440`); see E5.
- Kunminghu: no confirmed H/CSR directed test was located in the inspected test tree; no test run claimed.
- The attempted Heliodor target is not a pass and proves no test-body behavior. No testbench or upstream snapshot files were modified.

## 学习者总结

Sha 是 profile-defined 的八项集合。先确定某个结论属于 H 本体还是其中一项补充要求，再确认 CSR/trap/mode 线索来自哪条实现路径、V/HS/VS 状态和 privilege 条件是什么，最后区分源码、检入测试与实际运行结果。RVA23S64 宿主 profile 的强制要求不自动定义 guest profile；完整 H 功能、guest 启动线索或单一 fault 测试都不能替代八项逐项验证。

## 未解问题

- Kunminghu `FuConfig.CsrCfg` legacy CSR 与 wrapper `NewCSR` 的部署选择/配置边界需进一步闭合；stateen 和 counteren 的映射会受此影响。
- 两侧 `hpmcounter` 实际非只读零值集合及每个 `hcounteren` bit 的 writable/readback 矩阵。
- Ssstateen CSR 逐项存在性、权限和读回；Heliodor 对应状态在本轮检查范围内未知。
- `vstval` 继承的所有 `Sstvala` trap 类别及 `htval` 所有 ISA-permitted GPA cases。
- `vstvec` Direct MODE 与任意合法 BASE 的 CSR 和 trap target 动态验证。
- 所有 satp/vsatp/hgatp mode 支持集合、WARL behavior、Bare 与 SvNNx4 配对和真实 walk 行为。
- 修复或替代现有 `test_arch_common` harness check 阻断后，重跑 H 定向测试；本轮未修改上游或 testbench。
