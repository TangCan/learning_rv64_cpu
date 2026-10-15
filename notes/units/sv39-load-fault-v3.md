---
unit_id: "sv39-load-fault"
stage_id: "访存阶段 3：共同 fault"
version: 3
evidence_namespace: "SF1-E1–SF1-E12"
scope: "固定比较 S-mode、V=0、Sv39、RV64I 普通 LD，VA=0x0000008000000000，medeleg[13]=0 时，非规范地址导致 load page fault 并按架构条件进入 M-mode trap 的静态路径。"
exclusions:
  - "页表遍历、PTE 权限、A/D 更新、TLB miss/hit 行为。"
  - "Sv48/Sv57、虚拟化/G-stage、access fault、非规范 store/取指。"
  - "动态 trap/CSR/周期行为、完整 profile 符合性。"
spec_refs:
  - name: "RISC-V Privileged Architecture"
    edition: "v20260120 (2026-01-20)"
    section: "12.4.1 Sv39 Addressing and Memory Protection; 12.1.1 Supervisor Cause register; 3.1.6 mstatus; 3.1.7 mtvec; 3.1.14 mepc; 3.1.15 mcause; 3.1.16 mtval"
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

<!-- 本版本沿用当前活动证据命名空间 SF1-E1–SF1-E12；v1/v2 保留为历史版本。 -->

## 单元自检

- **问题：** 固定 VA 如何被识别为 Sv39 非规范地址？两边如何将普通 `LD` fault 保留到 ROB/commit，并在 `medeleg[13]=0` 时形成 M-mode trap？哪些结果只是规范预期或源码推导？
- **学习者答案：** `VA=0x0000008000000000=2^39`，bit 38=0、bit 39=1，因此高位 `[63:39]` 并非 bit 38 的 25 位符号扩展。Sv39 规范预期该 load 有 page fault，普通 load page fault 的 cause 为 13。Kunminghu 在 TLB full-VA pre-fault 检查生成 load page-fault 响应，LoadUnit 将异常放入 uop，ROB 到最老异常时送出原 PC 与异常向量；当前活动 wrapper 将这一路由到 NewCSR，NewCSR 的 delegation 逻辑在 `medeleg[13]=0` 时保留 M-mode 目标。Heliodor 的 MMU 在请求上检查 `va_noncanonical` 并即时给出 fault；ALU wrapper 携带 fault VA，ROB 保存 fault 类型与地址，commit 选择 cause 13 并依据 `medeleg` 选择 M-mode trap。`mepc`/`mtval` 的取值、CSR 更新和 redirect 均为源码支持的静态路径，不是本例运行观测。 **[SF1-E1–SF1-E11]**
- **检查类型：** explanation + source-location
- **证据 ID：** SF1-E1–SF1-E11

## 架构行为与子案例

- **固定输入（案例定义，不是运行记录）：** 当前 S-mode，V=0，`satp.MODE=Sv39`，RV64I `LD`，有效地址 `0x0000008000000000`，`medeleg[13]=0`；故障指令地址记为 `PC_LD`，因未执行而不赋具体值。`mtvec` 假设有效。
- **非规范性推导：** `0x0000008000000000 = 1 << 39`；bit 38 为 0，bit 39 为 1，故 `[63:39]` 不等于 `{25{bit38}}`。这是输入的静态分类，不表示处理器已执行或报告 fault。 **SF1-E2**
- **规范预期：** Privileged Architecture v20260120 §12.4.1 要求 Sv39 有效地址 bit `[63:39]` 全等于 bit 38，否则产生 page-fault exception。普通 load page fault 的 cause 为 13（§12.1.1）。给定 S-mode 且 `medeleg[13]=0`，异常送入 M-mode；M trap 将故障指令地址写入 `mepc`，更新 `mcause` 和 M-mode trap 状态。同步异常即使 `mtvec.MODE=Vectored` 也跳到 `mtvec.BASE`。`mtval` 架构上可写零；非零时报告 faulting VA，且 WARL 实现不必保持所有无效地址，可转换为可表示的无效地址。以上是架构条件，不是寄存器实测。 **SF1-E1**
- **规范依据：** [Privileged Architecture v20260120 的 edition-pinned 索引](https://docs.riscv.org/reference/isa/v20260120/priv/priv-index.html)，其中 Sv39 §12.4.1、Supervisor Cause §12.1.1，以及 Machine-Level ISA 的 `mstatus`、`mtvec`、`mepc`、`mcause`、`mtval` 章节。该 edition 的不可变官方发布构建为 [riscv-isa-manual 官方发布工作流](https://github.com/riscv/riscv-isa-manual/actions/runs/21201436369)，其中 `riscv-privileged-65b7fa8.pdf` 的 SHA-256 为 `9bd53ab5e7b8c024823282a2dbc158f23cfd844097f7fb85f67a2e552fb2198d`；该哈希固定了用于核对规则的 v20260120 PDF。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 固定 VA 的规范性 | documented (static) | bit 38=0、bit 39=1，违反 `[63:39]` 等于 bit 38 符号扩展。SF1-E2 |
| S-mode、V=0、Sv39、普通 RV64 `LD` | assumed / unverified | 对照输入固定；未在任一 hart 动态设置或执行。 |
| load page fault 与 cause 13 | specified + source-inspected | 规范预期和静态源路径；未观察实际 cause。SF1-E1、SF1-E3、SF1-E7 |
| fault PC、`mepc` 与 M-mode redirect | specified + source-inspected | 架构条件与两边源逻辑分别记录；`PC_LD`、CSR 值及 redirect 均未实测。SF1-E5、SF1-E9、SF1-E10 |
| `mtval` | specified + source-inspected | 规范允许零；非零报告 fault VA，无法表示的非法 VA 可被 WARL 转换。两实现源路径选择 fault VA，但无动态 CSR 观察。SF1-E1、SF1-E6、SF1-E10 |
| 页表遍历、PTE 权限、TLB hit/miss、访问 fault | excluded | 本固定 fault 的原因是非规范地址，不追踪这些机制。 |
| RVA23 整体符合性 | excluded | 单一静态案例不能推出 profile 符合性。 |

## Kunminghu 路径

- **阶段与状态变化（源码静态检查）：** `TLB.scala` 在 `checkfullva` 请求上比较 39-bit 符号扩展与完整 VA，产生 `pf39` 并保留 `fullva`；对 `S-mode, V=0, satp.MODE=Sv39`，此路径选择 Sv39 pre-fault。`LoadUnit` 从 TLB response 的 `pf.ld` 形成 `loadPageFault` exception vector。ROB 的异常路径维护异常信息；到 ROB head 可处理异常时，以原 uop PC 和 exception vector 发出异常。此描述不代表本例实际到达这些状态。 **SF1-E3–SF1-E5**
- **活动 CSR 集成与 trap 选择：** 后端把 ROB exception 与 memory exception VA 接至当前 `backend/fu/wrapper/CSR.scala`；该 wrapper 实例化 `NewCSR`，并分别接入 `fromRob.trap`、`fromMem.excpVA`。接口链为 `backend/Backend.scala:615` 的 `ctrlBlock.io.robio.exception → csrio.exception`，再到 `backend/Backend.scala:617-619` 的 exception VA；`backend/fu/wrapper/CSR.scala:129-135` 将 `csrIn.exception.valid/bits.pc/bits.trapVec` 接到 `fromRob.trap`，`CSR.scala:125` 将 `csrIn.memExceptionVAddr` 接到 `fromMem.excpVA`。因此 ROB 的 PC/cause 与 memory exception VA 分别经明确接口进入 NewCSR。`TrapHandleModule` 从 `highestPrioEX` 生成 cause，delegation 向量为 `highestPrioEX & medeleg`；给定同步 load page fault cause 13 且 `medeleg[13]=0`，静态选择为 M-mode。`TrapEntryMEvent` 的 M-mode 输出将特权状态设为 M、MPP 取当前特权状态、MPIE 取旧 MIE、MIE 清零；异常 cause 和 trap PC 用于 `mcause`、`mepc`，内存异常 VA 为 `mtval` 输入，trap target 来自 trap vector 计算。同步 exception 的 vectored 模式地址偏移只对 interrupt 加上，因此异常 target 是 `BASE`。这些是接口/组合逻辑连接结论；未观察任何 CSR 或实际 redirect。**[SF1-E5–SF1-E6]**
- **源码位置：** `cache/mmu/TLB.scala:162-170,216-267,518-534`；`mem/pipeline/LoadUnit.scala:391-397,1027-1048,1209-1221`；`backend/rob/ExceptionGen.scala:88-111,154-167`；`backend/rob/Rob.scala:577-588,651-658`；`backend/Backend.scala:615-619`；`backend/fu/wrapper/CSR.scala:65,125-142`；`backend/fu/NewCSR/TrapHandleModule.scala:39-80,90-111`；`backend/fu/NewCSR/NewCSR.scala:420-440,801-820,849-851,1032-1034,1124-1139`；`backend/fu/NewCSR/CSREvents/TrapEntryMEvent.scala:61-100,120-145`。详见 SF1-E3–SF1-E6。
- **版本修正：** v1 指向旧 `backend/fu/CSR.scala` 的 CSR 处理章节作为 trap 更新路径。该文件不是当前 wrapper 的活动 CSR 集成；v2 依据 wrapper 实例化 `NewCSR` 及其 `TrapHandleModule`/`TrapEntryMEvent` 连接修正，v1 保持不变。 **SF1-E6**

## Heliodor 路径

- **阶段与状态变化（源码静态检查）：** `mmu.veryl` 的 `vm_enabled` 在 V=0、Sv39、非 M-mode 时成立；`va_noncanonical` 检查高位符号扩展。该信号使 fault 在 request 上直接生成，并将 TLB-hit 输出和 walk start 路径屏蔽。`dmem_mmu` 传递 page-fault 标记。`alu_wrap` 将普通 load 归类为 `is_lfault`，并携带 AGU 地址作为 fault VA。ROB 记录 load-fault 身份、fault VA 并清除普通目的寄存器写入；提交时输出 head 的 fault 标志/VA。Core commit 逻辑对非 access fault 的普通 load fault 选 cause 13；faulting PC 选择 `c_pc`，tval 输入选择 ROB 保存的 fault VA。均为源码路径，不是本例执行观察。 **SF1-E7–SF1-E9**
- **Trap 选择及更新：** Core 按 `csr_medeleg_w[excp_cause]` 和前一特权状态计算 S delegation；cause 13、前一状态 S、`medeleg[13]=0` 时 `trap_to_s=0`，CSR trap path 选择 M-mode。CSR 在 trap fire 时将 trap PC、cause、tval 写入 `mepc`、`mcause`、`mtval`；M-mode 更新 `MPIE`、清 `MIE`，MPP 设置为之前的特权。trap target 由 `mtvec` 模式与 base 选择；本例同步异常的规范目标为 BASE。写入的实际值与动态 redirect 未观察。 **SF1-E9–SF1-E10**
- **ACT 材料边界：** 锁定 checkout 的 `test/act/README.md` 将测试标签 `sv39_canonical`（×2）列在其材料中，并记载一项 non-canonical fault handling 修复及历史 suite 摘要。README 能证明这些文字与测试标签存在；单凭标签不能推出测试所断言的地址、非规范输入或断言内容。本文未确认精确输入 VA、S-mode、普通 LD 和 `medeleg[13]` tuple 与本案例一致，因此只将其作为可用测试材料；没有检查 README 指向的底层测试产物，也不把它称为本案例运行结果。未运行 ACT、构建或仿真。 **SF1-E11**
- **源码位置：** `src/mmu/mmu.veryl:194-206,1224-1271,1286-1289`；`src/mmu/dmem_mmu.veryl:249-265`；`src/core/alu_wrap.veryl:467-494`；`src/core/rob.veryl:1344-1355,1488-1515,641-644`；`src/core/heliodor_core.veryl:4583-4604,4671-4728,4773-4812`；`src/core/csr.veryl:895-950,965-975`；ACT `test/act/README.md:123-125`（标签与问题摘要）、`:131-133`（suite 命令；仅 README 检查，未检查底层测试产物）。详见 SF1-E7–SF1-E11。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 对固定非法 VA，两边源码都含 Sv39 高位规范性检查并产生 load page fault 路径；Kunminghu 在 TLB full-VA pre-fault 检查，Heliodor 在 MMU request 入口即时 fault。架构 cause 13 来自规范；两侧运行结果未验证。 | SF1-E3、SF1-E4 | SF1-E7、SF1-E8 |
| C2 | 两边静态路径均保留 fault 指令 PC 与 load fault VA 至精确异常/commit 接口；给定 S-mode 与 `medeleg[13]=0`，源码条件支持 M-mode trap 选择。具体 PC、CSR 值及 redirect 未观察。 | SF1-E5、SF1-E6 | SF1-E9、SF1-E10 |
| C3 | `partial`：Heliodor ACT README 标签不能证明具体输入或断言（SF1-E11）；Kunminghu 对应测试材料 `unverified`，两侧固定 tuple 均未运行（SF1-E12），只能作可用测试材料的 partial 比较，不能据此判断本案例测试覆盖。 | 无对应测试材料：`unverified`；tuple：SF1-E12 | SF1-E11；tuple：SF1-E12 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试材料 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SF1-E1 | 自检、架构行为 | spec | inspected | Privileged Architecture v20260120 | Sv39 §12.4.1、cause §12.1.1、M trap CSR §3.1.6–3.1.16；见规范链接 | not-run | RV64、Sv39、S-mode | 非规范 VA 的 load | page fault；load page fault cause 13；delegation 决定 trap privilege；`mepc`/`mtval` 按规范规则 | 静态阅读规范；无 hart 观察 | none |
| SF1-E2 | 固定输入、规范性推导 | spec | inspected | 案例数学推导（非实现证据） | `0x0000008000000000 = 1<<39` | not-run | 固定位宽 64 | bit38=0、bit39=1、`[63:39]` | 不等于 bit38 的 25 位符号扩展 | 静态位值推导；非运行结果 | none |
| SF1-E3 | C1、自检；Kunminghu pre-fault | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` / `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/cache/mmu/TLB.scala:162-170,216-267,518-534` | not-run | S-mode、V=0、Sv39、`checkfullva`（案例假设） | 固定非法 VA | `pf39` pre-fault，response 保留 fault VA 并抑制 miss 继续路径 | 源码静态检查；本案例未执行 | none |
| SF1-E4 | C1、自检；Kunminghu load exception | source | inspected | Kunminghu / 同 SF1-E3 snapshot | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:391-397,1027-1048,1209-1221` | not-run | 普通 load | TLB `pf.ld` response | `loadPageFault` exception vector 进入 uop；page fault 时不信任尚未生成物理地址的 PMP/PMA response | 源码静态检查；未运行 | none |
| SF1-E5 | C2、自检；Kunminghu precise exception | source | inspected | Kunminghu / 同 SF1-E3 snapshot | `backend/rob/ExceptionGen.scala:88-111,154-167`; `backend/rob/Rob.scala:577-588,651-658`; `backend/Backend.scala:615-619` | not-run | ROB precise exception | 有异常的 load 到 ROB head | 异常身份按 ROB 保留；exception 输出关联 head uop PC/vector，memory exception VA 接 CSR route | 源码静态检查；未观察 PC | none |
| SF1-E6 | C2、自检；Kunminghu active CSR route | source | inspected | Kunminghu / 同 SF1-E3 snapshot | `backend/fu/wrapper/CSR.scala:65,125-142`; `backend/fu/NewCSR/TrapHandleModule.scala:39-80,90-111`; `NewCSR.scala:420-440,801-820,849-851,1032-1034,1124-1139`; `CSREvents/TrapEntryMEvent.scala:61-100,120-145` | not-run | S-mode、cause 13、`medeleg[13]=0`、有效 `mtvec` | load page fault | M-mode event 输入、MPP/MPIE/MIE/mepc/mcause/mtval 和 trap target 逻辑可静态追踪；同步 exception target uses BASE | 静态检查 NewCSR active wrapper path；无 CSR/redirect 观察 | none |
| SF1-E7 | C1、自检；Heliodor detection | source | inspected | Heliodor / `heliodor-master-20261012` / `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/mmu/mmu.veryl:194-206,1224-1271,1286-1289`; `src/mmu/dmem_mmu.veryl:249-265` | not-run | V=0、Sv39、非 M-mode | 固定非法 VA，load request | request 上给 fault；避免 TLB hit 与 walk start；page fault 与 access fault 区分 | 源码静态检查；未执行 | none |
| SF1-E8 | C1、C2；Heliodor fault classification/VA | source | inspected | Heliodor / 同 SF1-E7 snapshot | `src/core/alu_wrap.veryl:467-494`; `src/core/rob.veryl:1344-1355,1488-1515,641-644` | not-run | 普通 `LD` | MMU fault 与 AGU effective VA | load-fault 标志、地址存 ROB，抑制故障 load 的 rd 写回并在 head 输出身份/VA | 源码静态检查；未运行 | none |
| SF1-E9 | C2、自检；Heliodor cause/delegation/PC/tval selection | source | inspected | Heliodor / 同 SF1-E7 snapshot | `src/core/heliodor_core.veryl:4583-4604,4671-4728,4773-4812` | not-run | S-mode、V=0、`medeleg[13]=0` | head load fault | 普通非 access load fault 选 cause 13；trap PC 取 `c_pc`；delegation=0 选择 M；tval 选择 saved fault VA | 静态源码逻辑已检查；无 trap 观测 | none |
| SF1-E10 | C2、自检；Heliodor CSR update | source | inspected | Heliodor / 同 SF1-E7 snapshot | `src/core/csr.veryl:895-950,965-975` | not-run | M-mode trap | cause 13、PC、VA 输入 | trap fire 更新 `mepc/mcause/mtval`、前模式字段及 MIE 状态 | 静态源码检查；无 CSR 读取 | none |
| SF1-E11 | C3；一般 ACT 证据边界 | test-inspected | inspected | Heliodor / 同 SF1-E7 snapshot | `test/act/README.md:123-125,131-133`（仅 README inspection；未检查底层测试产物） | README 提及的 suite 命令未在本次运行 | README 中的 Sv/Sv39 测试材料；精确运行 tuple 未核实 | 标签 `sv39_canonical`（×2）及 README 对 non-canonical fault handling 修复的文字 | 仅证明 README 含此标签和文字；不能据标签判断被测地址或断言内容；没有检查底层测试产物 | README 静态检查；未运行 ACT，不构成本案例运行观察 | none |
| SF1-E12 | C3、比较结论 | test-run | unverified | Kunminghu 与 Heliodor / 两个 sources.lock snapshots | 本案例精确动态 tuple（非规范 `LD` fault） | 未运行 | S-mode、V=0、Sv39、`medeleg[13]=0` | VA `0x0000008000000000` 的普通 `LD` | 实际观察 cause 13 与 M-mode trap | 未验证；本案例没有动态观察 | none |

## 学习者总结

固定 VA 在算术上确属 Sv39 非规范地址；规范预期普通 `LD` 触发 load page fault cause 13。Kunminghu 的可追踪活动链是 TLB pre-fault、LoadUnit exception vector、ROB precise exception，再经当前 wrapper 接入 NewCSR；Heliodor 则在 MMU request 检测后由 load fault/VA 进入 ROB，commit 选择 cause 与 trap CSR 输入。给定 S-mode 且 delegation bit 清零，规范条件和两边静态逻辑都指向 M-mode trap。Heliodor ACT README 列出 `sv39_canonical` 标签并记录 non-canonical fault handling 修复；标签不能证明测试输入或断言内容（SF1-E11）。Kunminghu 对应测试材料未核实，测试侧为 `unverified`；两侧固定 tuple 均未运行（SF1-E12），因此可用测试材料的比较为 `partial`，不能据此判断本案例覆盖。没有运行本案例，`PC_LD`、cause、CSR 内容、`mtval` 表示及 redirect 均未观测；本记录不构成完整 profile 符合性结论。

## 未解问题

- 本记录的可用测试材料比较为 `partial`：Kunminghu 对应测试材料 `unverified`；Heliodor 标签的精确输入/断言也未确认。

- 两侧均未动态执行固定 tuple；实际 cause、`mepc`、`mtval`、trap target 和周期行为未验证。
- Heliodor ACT `sv39_canonical` 的精确生成输入、特权模式、指令及 delegation 配置未确认；只保留为一般测试材料。
- Kunminghu `mtval` 输入受实现 CSR 路径约束，具体无效地址是否被目标寄存器实现转换未动态检查；`mtval` WARL 表示边界仍未知。
- v1 中旧 CSR 路径导航已在本版纠正；v1 本身保留，不覆盖历史记录。
