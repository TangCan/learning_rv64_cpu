---
unit_id: "sv39-load-fault"
stage_id: "阶段 3"
scope: "S-mode、V=0、satp.MODE=Sv39 时，普通 RV64 LD 的非规范虚拟地址触发 load page fault，并在 medeleg[13]=0 时进入 M-mode trap。"
exclusions:
  - "Sv39 page-table walk、PTE 权限及 A/D 更新、TLB miss/hit 行为、superpage。"
  - "Sv48/Sv57、虚拟化/G-stage、access fault、非规范 store/取指及 RVA23 整体符合性。"
spec_refs:
  - name: "RISC-V Privileged Architecture"
    edition: "v20260120 (2026-01-20)"
    section: "12.4.1 Sv39 Addressing and Memory Protection; 12.1.1 Supervisor Cause register; 3.1.7 mtvec; 3.1.14 mepc; 3.1.15 mcause; 3.1.16 mtval; 3.1.6 mstatus"
    profile_category: "not-profile-specific"
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

<!-- 每条结论以 E 编号引用下方证据；源码引用固定到 sources.lock 的提交。 -->

## 单元自检

- **问题：** S-mode 执行 `LD` 时，Sv39 非规范 VA 如何从地址检查变成 M-mode load page fault？控制流及特权状态发生什么变化？
- **学习者答案：** 令 `LD` 位于 `PC_LD`，其有效地址为 `VA_FAULT`，且 `VA_FAULT[63:39] != {25{VA_FAULT[38]}}`。Sv39 将这种地址定义为 page fault；这是地址规范性故障，不需要先归因于 PTE 权限或物理访问保护。load page fault 的 cause 是 13。若 `medeleg[13]=0`，S-mode 的异常进入 M-mode：`mepc=PC_LD`，`mcause=13`，`mstatus.MPP=S`、`MPIE` 保存旧 `MIE`、`MIE=0`，当前特权级改为 M。`mtvec` 给出 trap entry；同步异常即使在 vectored 模式下也进入 `BASE`。`mepc` 保存故障指令 PC，handler 可用 `MRET` 返回该 PC。`mtval` 可为零；若非零，则按架构规则报告 faulting VA；若该非法 VA 无法由 `mtval` 表示，WARL 实现可将其转换为另一个可表示的非法地址。源码路径显示这条异常链；本机没有观测到该指令实际执行。 **E1–E12**
- **检查类型：** explanation + source-location
- **证据 ID：** E1–E12

## 架构行为与子案例

- **规范预期（非本机运行观察）：** 普通标量 `LD` 从 `PC_LD` 计算 `VA_FAULT`；固定 `i_virt=0`、`satp.MODE=Sv39`、当前 S-mode、且 `VA_FAULT[63:39]` 不是 bit 38 的 25 位符号扩展。依 Privileged Architecture v20260120 §12.4.1，这一地址导致 page-fault exception。§12.1.1 将 load page fault 编为 cause 13。设 `medeleg[13]=0`，异常被送至 M-mode；trap entry 由 `mtvec.BASE` 决定，vectored 模式对同步异常也使用 `BASE`。`mepc` 保存故障指令 PC，供 `MRET` 返回使用。架构允许 `mtval` 为零；若非零报告 page fault，它给出 faulting virtual address。若无效 VA 不能由 `mtval` 表示，WARL 实现可将其转换为另一个可表示的无效地址。
- **规范依据：** [Privileged Architecture v20260120 §12.4.1](https://docs.riscv.org/reference/isa/v20260120/priv/supervisor.html)、§12.1.1、§3.1.6、§3.1.7、§3.1.14–3.1.16。原因号和 trap 状态在源码证据之外仍以该版本规范为准。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 普通 RV64 `LD`，S-mode，V=0 | documented (static) | 本单元固定的规范/源码分析配置；未动态执行。 |
| `satp.MODE=Sv39` 且 VA 非规范 | documented (static) | `[63:39] != {25{[38]}}`，架构预期为 page fault；未动态观察。 |
| `medeleg[13]=0`、`mtvec` 有效 | documented (static) | 规范/源码分析中将 cause 13 定向到 M-mode；未动态观察 trap 入口。 |
| `mtval` | documented (static) | 架构允许零；非零时报告 fault VA；无效 VA 若不能表示，WARL 实现可转换成另一个可表示的无效地址。两边仅检查静态路径，未动态观察。 |
| Sv39 page-table walk、PTE 权限、A/D 更新、TLB 行为 | excluded | 这些不是本案例 fault 原因。 |
| Sv48/Sv57、G-stage、access fault、store、取指 | excluded | 不从本案例外推。 |
| 整体 profile 符合性 | excluded | 本记录不是符合性映射或认证。 |

## Kunminghu 路径

- **阶段与状态变化（静态源码推导，非运行观察）：** TLB 处理 `checkfullva` 请求时按 Sv39 形成 `pf39`，以 VA[38:0] 的符号扩展与完整有效地址比较。错误置位预检测 page fault，并将 fault VA 保存到响应的 `fullva`。LoadUnit 将 TLB 的 load page fault 写入 uop exception vector；故障时 PMP/PMA 响应不可信，因此不以其覆盖 translation fault。ROB 的异常队列保留该指令及异常，直到成为最老可提交异常时输出原指令 PC 和 exception vector。CSR 依据 exception vector 选择 cause 13；在 `medeleg[13]=0` 时不走 S-mode delegation，写入 M-mode trap 状态并从 `mtvec` 形成 trap target。对同步异常，trap entry 是 `mtvec.BASE`；`mepc` 是故障 PC，可供 `MRET` 返回。ROB/CSR 的 trap redirect 将后续取指指向 trap entry。`mtval` 来自 LSU 的 memory exception VA 路径。本机没有观测这条指令执行。 **E2–E5**
- **源码位置：** `TLB.scala:216-267, 237-260` 的 `pf39`、预异常标志与 `resp.fullva`；`LoadUnit.scala:1028-1048, 1209-1221`；`LoadExceptionBuffer.scala:95-100`、`Backend.scala:617`；`Rob.scala:577-680`；`CSR.scala:1310-1328, 1340-1398, 1427-1459, 1525-1541`。以上均固定在 `xiangshan-kunminghu-v2-20261012`。源码行号是检查时定位。
- **相关验证：** 已检查静态源码；未运行 Kunminghu 仿真。**E2–E5**

## Heliodor 路径

- **阶段与状态变化（静态源码推导，非运行观察）：** `mmu.veryl` 以 `!i_virt && satp_mode==Sv39 && i_priv!=M` 定义单阶段翻译使能，直接检查 VA 的 63:39 是否为 bit 38 的符号扩展。非规范地址令 `_fault_out=i_req`，因此即时报告而绕过 TLB hit 与 page walk；相同逻辑在该路径不会将故障改为 access fault。`dmem_mmu` 根据 load/store 类型把 page fault 传出，`alu_wrap` 将普通 load 标为 load fault 并携带 AGU 有效地址。ROB 按 ROB 所属记录 fault 类型及 VA；提交时选择 load page fault cause 13，传入 faulting PC 与 VA。给定 `medeleg[13]=0`，静态逻辑选择 M-mode trap；同步异常的 trap entry 是 `mtvec.BASE`，包括 vectored 模式，`mepc` 保存 fault PC 供 `MRET` 返回。CSR 在 `commit_trap` 时写 `mepc/mcause/mtval` 和 M-mode 状态，提交 redirect 将 PC 切到 trap entry。Heliodor 当前 CSR 路径把 load fault VA 送入 tval；规范允许 `mtval` 采用零值配置，因此这里只能确认实现静态选择，不宣称实际寄存器观测。 **E6–E10**
- **源码位置：** `mmu/mmu.veryl:194-206, 1228-1265`；`mmu/dmem_mmu.veryl:251-263`；`core/alu_wrap.veryl:467-494`；`core/rob.veryl:1486-1514, 640-644`；`core/heliodor_core.veryl:4700-4724, 4759-4812, 4938-4950, 5085-5090`；CSR 状态更新在 `core/csr.veryl:940-965`。均固定在 `heliodor-master-20261012`。
- **相关验证：** 已检查 `test/c/smode_pgfault_test.S`：它实际构造的是 S-mode store 到无效页，handler 处理 cause 15；其后的 `LD` 在页表修复之后成功访问，不覆盖本案例。该汇编没有对应 Veryl test module；`veryl test --test test_smode_pgfault` 返回“无匹配测试”，不能算作执行。已运行现有 `veryl test --test test_mmu`，Sv39 翻译用例通过，但它没有触发 page fault；记录在 E11。非规范 load fault 动态行为仍未验证。 **E10–E12**

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边都有显式 Sv39 非规范 VA 检查，并将普通 load 归类为 load page fault；cause 13 是架构定义。Kunminghu 将规范性检查集成于 TLB full-VA 检查与响应，Heliodor 在单阶段 MMU 入口即时 fault、避免 TLB hit/page walk。此为固定源码路径比较，不是动态行为或符合性证明。 | E2, E3 | E6, E7, E8 |
| C2 | 两侧均保留 fault 指令身份/PC 和 fault VA，提交点再进入 trap 状态更新与控制流重定向；在 `medeleg[13]=0` 的选定配置下目标为 M-mode。Kunminghu 延迟更新 `mtval`；Heliodor 的静态 trap 输入直接选择 load fault VA。 | E4, E5 | E8, E9 |
| C3 | Heliodor 已检查的汇编实际触发 S-mode store page fault（cause 15），不能验证本例的非规范 load fault（cause 13）；XiangShan src/test 的限定关键词搜索未定位专项测试。两侧都没有本例的动态观察。 | E12 | E10,E11 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 自检、C1、架构定义 | spec | inspected | Privileged Architecture v20260120 | §12.4.1、§12.1.1、§3.1.6–3.1.7、§3.1.14–3.1.16；[官方文档](https://docs.riscv.org/reference/isa/v20260120/priv/supervisor.html) | not-run | XLEN=64；S-mode Sv39 | 非规范 load VA、cause 与 trap 状态 | PF；cause 13；按 delegation 进入相应 trap mode | 静态核对规范文本；没有 hart 执行观测 | none |
| E2 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/cache/mmu/TLB.scala:216-267` | not-run | 固定 sources.lock 快照 | `checkfullva` 且 Sv39 | 非规范性检测并保存响应 fault VA | 源码比较 `SignExt(va(38,0))` 与 VA；已检查，未运行 | none |
| E3 | C1、C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:1028-1048,1209-1221`; `src/main/scala/xiangshan/mem/lsqueue/LoadExceptionBuffer.scala:95-100`; `src/main/scala/xiangshan/backend/Backend.scala:617` | not-run | 普通标量 load | TLB PF 传入 uop；异常地址送往 CSR | load page-fault vector 与 VA 保持关联；不将无效 PMP/PMA 响应当故障原因 | 静态源码已检查，未运行 | none |
| E4 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/rob/Rob.scala:577-680,1188-1230` | not-run | 按 ROB 顺序提交 | 含异常的 load | ROB 将最老异常的 PC/vector 送出，抑制正常控制流 | 源码静态路径已检查，未运行 | none |
| E5 | C2、自检 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/fu/CSR.scala:1310-1328,1340-1398,1427-1459,1525-1541`; `src/main/scala/xiangshan/backend/CtrlBlock.scala:112-127,346-349` | not-run | S-mode、`medeleg[13]=0`、有效 `mtvec` | 同步 load PF | cause=13；更新 M trap state；trap target redirect | 静态源码已检查，未运行 | none |
| E6 | C1 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/mmu/mmu.veryl:194-206,1228-1265` | not-run | V=0、Sv39、非 M-mode | `VA[63:39] != {25{VA[38]}}` | 立即 fault，绕过 TLB hit 与 walk | 静态源码已检查，未运行 | none |
| E7 | C1、C2 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/mmu/dmem_mmu.veryl:251-263`; `src/core/alu_wrap.veryl:467-494` | not-run | 普通 load | MMU fault 和 AGU VA | 输出 load fault 类型并携带有效地址 | 静态源码已检查，未运行 | none |
| E8 | C2、自检 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/rob.veryl:1486-1514,640-644`; `src/core/heliodor_core.veryl:4700-4724,4759-4812` | not-run | ROB 提交点 | load fault | 保留 fault VA/PC，选择 cause 13，提供 tval | 静态源码已检查，未运行 | none |
| E9 | C2、自检 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/heliodor_core.veryl:4938-4950,5085-5090`; `src/core/csr.veryl:940-965` | not-run | `medeleg[13]=0`、有效 `mtvec` | 同步 cause 13 | M-mode CSR 更新并 redirect 到 trap target | 静态源码已检查，未运行 | none |
| E10 | C3、验证边界 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/c/smode_pgfault_test.S:85-100,130-163,157-201`；无匹配的 `tb` test module | `make -C sources/heliodor/test/c ../hex/smode_pgfault_test.hex`; `veryl test --test test_smode_pgfault` | 汇编测试配置 S-mode Sv39；源码设置 `medeleg[13]=1` | store 到无效映射触发 cause 15；修复后 load 成功 | cause 15 被处理并返回，后续 load 成功；不覆盖非规范 LD cause 13 | make 表示 hex 已是最新；Veryl filter 命中 0 test，显示 `No tests matched filter`。源码不是本案例的测试 | none |
| E11 | C3、工具链正向校验 | test-run | run-pass | Heliodor / `heliodor-master-20261012` | `tb/test_mmu.veryl:1-176` | `veryl test --test test_mmu`，位于 `sources/heliodor` | Veryl `0.22.0-nightly (c3bf469 2026-10-12)` | 现有 Sv39 page-table walk 测试（filter 还匹配 `test_mmu_asid`） | 两个匹配的 MMU 测试完成且 assertions 通过；不覆盖非规范 fault | `2 passed, 0 failed, 29 ignored`；输出含 `MMU Sv39 page table walk test passed`，但本案例仍未验证 | none |
| E12 | C3、覆盖范围 | test-inspected | unverified | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/test` | `rg -ni 'noncanonical|non-canonical|load.?page.?fault|page.?fault|pgfault' sources/xiangshan/src/test` | 固定来源快照 | 本例非规范 Sv39 load fault 专项测试 | 若覆盖，应有相关测试源码命中 | 此搜索范围无关键词命中；不推断仓库其他目录不存在测试，也没有动态执行 | none |

- `test-inspected` 表示只检查了测试源文件。`unverified` 表示本案例未动态执行；E11 的 run-pass 只覆盖 Sv39 page-table walk happy path，不覆盖本案例 fault；E12 仅反映限定搜索范围的未命中。非规范 load 仍为 unverified。
- 本案例中的 `mtval` 区分架构规则与实现选择：规范允许清零；非零时应给出 fault VA，但若该无效 VA 不能被 `mtval` 表示，WARL 实现可将它转换成另一个可表示的无效地址。Kunminghu 的静态 CSR 路径延迟取 mem exception VA，Heliodor 的静态 trap 输入选择 load fault VA；具体寄存器表示及转换依赖实现，本机没有执行读取。

## 学习者总结

基于规范与源码静态检查，Sv39 的非规范性可在页表翻译前判定；`LD` 的架构预期是 cause 13 load page fault，而不是 PMP/PMA access fault。Kunminghu 在 TLB 的 full-VA 检查中生成 page fault，再由 LoadUnit 和 ROB 维持异常身份及地址，CSR 静态路径在提交异常后更新 trap 状态。Heliodor 在单阶段 MMU 检查非规范 VA 后立即 fault，load 类型和 VA 经 ALU/ROB 到达提交 trap 逻辑。固定为 `medeleg[13]=0` 后，源码路径对应 M-mode trap entry；同步异常位于 `mtvec.BASE`，故障 PC 保存在 `mepc` 供返回使用。上述均为规范预期及源码静态推导，不是本案例的动态观察。Heliodor 的 Sv39 MMU happy-path 测试已运行通过；现有 S-mode store page-fault 材料不覆盖非规范 load fault，后者的动态结果仍未验证。

## 未解问题

- 本机没有可执行的 Heliodor page-fault harness 目标：S-mode 汇编源文件与预生成 hex 存在，但没有对应 test module；`veryl` 不在 PATH。需后续确认是否有独立集成环境可运行该汇编；非规范 Sv39 `LD` 的动态 cause、trap PC、`mtval` 与 redirect 仍未验证。
- Kunminghu load-exception VA 在 ROB/LSQ 读出的精确时序与 fault VA WARL 表现未由本机仿真检查；本记录仅依据源码静态追踪。
