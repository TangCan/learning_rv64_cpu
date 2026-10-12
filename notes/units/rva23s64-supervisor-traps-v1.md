---
unit_id: "rva23s64-supervisor-traps"
stage_id: "Epic 4 / Story 4.7"
scope: "RVA23S64 RV64I 的 U/S ECALL 与陷阱路由，以及 Ss1p13、Sstvecd、Sstvala、Sscounterenw、Ssu64xl 的双核静态证据和测试边界。"
exclusions:
  - "完整 RV64I/端序符合性及完整 Privileged Architecture v1.13 行为审计。"
  - "Sstvala 子案例的端到端动态验证；所有委托、中断优先级和 S-mode ECALL 环境服务组合。"
  - "H/VS、页表 walk、page-fault A/D 与地址转换机制；仅对源码中的虚拟化分支作边界说明。"
  - "Debug Module、profile 建议和本故事范围外的 S64 特权扩展。"
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0"
    section: "§3.1.2.1、§3.1.2.2: RV64I, Ss1p13, Sstvecd, Sstvala, Sscounterenw, Ssu64xl"
    profile_category: "mandatory"
  - name: "RISC-V Privileged Architecture"
    edition: "v1.13"
    section: "Machine §§2.1.8, 2.3.1–2.3.2; Supervisor §§9.1.1.1–9.1.1.2, 9.1.1.5, 9.1.1.9"
    url: "https://docs.riscv.org/reference/isa/v20240411/priv/supervisor.html (Supervisor); https://docs.riscv.org/reference/isa/v20240411/priv/machine.html (Machine)"
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

<!-- 本单元记录有限学习映射，不作为符合性认证。 -->

## 单元自检

- **问题：** U-mode ECALL 与 S-mode ECALL 的 cause 是否相同？陷阱必然到 S-mode 吗？
- **学习者答案：** cause 按发起 ECALL 时的特权级区分：U 为 8，S 为 9。U-mode 的异常可在允许委托时进入 S-mode；委托不能把 S 来源异常降到 S-mode。S-mode ECALL cause 9 在非 H 执行环境下进入 M-mode，VS-mode cause 10 属于 H 扩展的独立情形。当前证据只说明两侧局部路径；测试未验证环境服务处理。
- **检查类型：** explanation
- **证据 ID：** E1–E4

## 架构行为与子案例

Profile v1.0 §3.1.2.1 将 U/S ECALL 行为列入 RVA23S64 RV64I 必选基础要求；§3.1.2.2 列出 Ss1p13、Sstvecd、Sstvala、Sscounterenw、Ssu64xl。S64 继承的 U64 扩展仍由原 U64 行去重计数，本单元不重复评定。规范依据为 [RVA23 Profile v1.0 §3.1.2.1–3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html) 与 [Privileged Architecture v1.13](https://docs.riscv.org/reference/isa/priv/priv-intro.html)，其中 Sstvala 的 breakpoint 例外可直接核对 [Privileged Architecture v1.13 §12.1.9](https://docs.riscv.org/reference/isa/priv/priv-intro.html) 的 Supervisor Trap Value 条款，并与 Profile 明确列出的 EBREAK/C.EBREAK 例外共同阅读。

下表中的 `unconfirmed` 表示该子案例未获得完整或动态验证；它与覆盖目录的实现研究状态（如 `partially-studied`、`studied-unverified`）处于不同层级。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| RV64I 小端序 | unconfirmed | profile 要求 little-endian；本轮没有检查两侧端序配置或运行环境，保持未验证。E1–E3 |
| U-mode ECALL：cause、medeleg 与 S trap target | unconfirmed | 两侧 RTL 有 cause/delegation/target 线索；Heliodor 有 U ECALL 测试源码，未运行。E2–E4 |
| S-mode ECALL：cause 与执行环境请求目标 | unconfirmed | RTL 有 cause 9 路径；非 H 执行环境下该 S 来源异常进入 M-mode，不能向 S 委托；本轮没有端到端验证其环境服务处理。E2–E4 |
| 委托与中断使能 | unconfirmed | 检查了 medeleg/mideleg、sie/sstatus.SIE 与 trap routing 线索；未覆盖所有同步/异步组合、优先级和特权级边界。E2–E3 |
| S trap entry / SRET | unconfirmed | sepc/scause/stval 与 S 状态写入以及 SRET 返回路径可定位；未对 SPIE/SIE/SPP 状态组合逐项运行。E2–E3 |
| stvec Direct 与任意合法四字节对齐 BASE | unconfirmed | Kunminghu 的 `stvecMask = ~(0x2)` 只清除 bit 1，`MaskedRegMap(Stvec, ...)` 用该 mask 写入且读出；因此静态掩码保留 BASE 的高位及 MODE bit 0，但没有多个有效 BASE 的读回和跳转测试。某个 handler 地址不能证明任意地址。E2–E3 |
| stvec vectored 中断/同步异常 | unconfirmed | RTL 有 vectored interrupt 加 cause、同步异常取 BASE 的公式；未运行。E2–E3 |
| stval：load/store/fetch page fault、access fault、misaligned | unconfirmed | profile 要求故障虚拟地址；Kunminghu 的延迟更新从异常 PC 或 memExceptionVAddr 选择 tval，Heliodor 分别为 page fault、store/load fault 与非法指令选择输入；breakpoint 及各异常来源尚未全部逐项核验。静态线索不等于逐类别验证。E1–E3 |
| stval：breakpoint（EBREAK/C.EBREAK 除外） | unconfirmed | profile 明确保留 EBREAK/C.EBREAK 例外；本轮没有相应对照测试。E1、E4 |
| stval：virtual-instruction、illegal-instruction | unconfirmed | profile 要求故障指令；Heliodor H/VS 源码作为边界线索，不扩展为本故事的 H 符合性结论。E1、E3 |
| scounteren writable bits | unconfirmed | Kunminghu 的 FuConfig 实例化旧版 `backend.fu.CSR`，其实现有 HPM counter 状态；另有 `wrapper.CSR` 使用 NewCSR，不能把该未证实的替代路径 TODO 当作当前配置结论。`scounterenMask=0` 与 profile 对非只读零 HPM counter 的条件存在潜在冲突，须确认实际被实现的 counter 集合及其只读属性。Heliodor S CSR 写路径和 HPM 计数器存在源码线索。没有逐位运行验证。E2–E3 |
| Ssu64xl：sstatus.UXL=2 | unconfirmed | Heliodor 明确读出 RV64 UXL 常量 2；Kunminghu SSTATUS mask/XL 位定义可查。此处是静态线索，未运行 CSR 写读。E2–E3 |

## Kunminghu 路径

- **阶段与状态变化：** `CSR.scala` 将 ECALL 按 M、S、U 来源分别置入异常向量；异常号与中断号合成 cause，再用 `medeleg`/`mideleg` 和当前 privilege 决定 S 或 M 路由。`TrapHandleModule` 选出异常并按委托选择 `stvec` 或 `mtvec`；CSR 更新 `sepc/scause/stval`，并调整 SIE/SPIE/SPP 等状态。SRET 路径以 `sepc` 为返回目标。S-source ECALL cause 9、U-source cause 8 是静态来源观察，不能代表每种配置下的运行结果。E2。
- **源码位置：** [FuConfig CSR 绑定](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/FuConfig.scala:302) 实例化 `backend.fu.CSR`；[CSR.scala ECALL 分类](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1254)、[delegation 与 trap vector](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1427)、[S trap CSR 更新](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1516)。Sstvecd 的 `stvecMask`、Sstvala 的延迟 tval 写入/清零、`scounterenMask=0` 及 UXL 位定义在 [CSR.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:457)。`wrapper.CSR` 中另实例化 NewCSR，但本次配置路径证据未显示它被 FuConfig 选用；NewCSR 的 TODO 只作为非活动候选路径，不作为当前配置缺口证据。E2。
- **相关验证：** 本轮检查了相关源码位置，没有报告本轮运行的 Kunminghu S-mode trap 测试。`CSR.scala` 的实现位置不等同动态验证。E2、E5。

## Heliodor 路径

- **阶段与状态变化：** `heliodor_core.veryl` 在 commit trap 处按陷阱来源产生 cause（U=8、HS/S=9、M=11），用 `medeleg` 和当前 privilege 选择 S/M 路径，并以 `stvec`/`mtvec` 计算 trap target；`csr.veryl` 在 `i_trap_fire` 时写 S-level `sepc/scause/stval` 并更新 S 状态，SRET 分支恢复状态。虚拟化下 VS 分支存在独立的 VS trap CSR，这里只作为范围边界。`stval` 的输入 `i_trap_tval` 路由存在，但其所有异常类别是否传入规范要求的 VA 或指令值没有逐项验证。E3。
- **源码位置：** [cause 与 delegation](../../sources/heliodor/src/core/heliodor_core.veryl:4647)、[trap target](../../sources/heliodor/src/core/heliodor_core.veryl:4937)、[S trap entry](../../sources/heliodor/src/core/csr.veryl:900)、[SRET 更新](../../sources/heliodor/src/core/csr.veryl:1002)、[sstatus UXL 常量](../../sources/heliodor/src/core/csr.veryl:426)。E3。
- **相关验证：** 已检查 [smode_umode_test.S](../../sources/heliodor/test/c/smode_umode_test.S:1)：源码包含 U ECALL→S handler、cause 8 检查和返回 U-mode；[smode_timer_test.S](../../sources/heliodor/test/c/smode_timer_test.S:1)：委托 STIP 并在 S handler 检查中断；[smode_plic_test.veryl](../../sources/heliodor/tb/test_smode_plic.veryl:1)：其 `#[test(test_smode_plic)]` 注册项运行 harness，并从 `test/hex/smode_plic_test.hex` 载入程序；`test/c/smode_plic_test.S` 是该 HEX 的源码。命令 `veryl test --test test_smode_plic` 只针对这个 harness；README 称默认 `veryl test` 包含 directed tests。`smode_umode_test.S`、`smode_timer_test.S` 与 `smode_minikernel_test.S` 对应的 runner/harness 关系本轮未逐个追踪。这些属于已检查测试材料，不等于已执行或覆盖本单元所有要求。项目 README 推荐 `veryl test`；显式调用本机 latest/nightly 工具也未能通过 check，故 PLIC 测试未启动。E4–E5。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧源码均区分 S/U ECALL cause 并提供委托与 S trap 状态路径；U ECALL 定向测试源码只在 Heliodor 侧定位，且未运行。 | E2 | E3–E5 |
| C2 | 两侧可定位 stvec、trap target 和 stval 通路，但尚未证明任意有效 Direct BASE 写入能力或 Sstvala 的所有类别值。 | E2 | E3–E4 |
| C3 | scounteren 的静态线索不同：FuConfig 绑定的 Kunminghu CSR 中写 mask 为零且可见 HPM counter 状态；profile 条件要求针对非只读零 counter，当前仍需确认实际 counter 集合与 RO 状态，故不能判定满足与否。Heliodor 提供寄存器写路径，但没有逐位运行验证。 | E2 | E3 |
| C4 | Heliodor 的 sstatus UXL 常量为 2；Kunminghu 有对应状态字段定义。静态常量/掩码没有替代 CSR 读写测试。 | E2 | E3 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Profile 与特权架构行为基线 | spec | inspected | RVA23 Profile v1.0；Privileged Architecture v1.13 | [RVA23 §3.1.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html); Privileged Architecture §12.1.9（Supervisor Trap Value，EBREAK/C.EBREAK 边界） | not-run | 不适用 | RV64I ECALL、Ss1p13、Sstvecd、Sstvala、Sscounterenw、Ssu64xl | 依据正式文本分别记录要求与条件 | 已检查 profile 要求和相关架构条款；不将规范要求当作实现证据 | none |
| E2 | Kunminghu CSR、ECALL 分类、delegation、trap vector/entry/return、stval、scounteren 与 UXL 线索 | source | inspected | xiangshan-kunminghu-v2-20261012 | `CSR.scala:402–474, 795–805, 1105–1165, 1254–1257, 1364–1403, 1497–1522`; `NewCSR/SupervisorLevel.scala:63–83`; `NewCSR/TrapHandleModule.scala:51–110` | not-run | 固定快照；RTL 静态检查 | U/S ECALL、委托、中断、S entry/return、stvec/stval/scounteren/UXL | 静态定位不适用于运行通过 | 观察到代码路径；未运行行为测试，部分要求仍未逐案例核验 | none |
| E3 | Heliodor cause/delegation/target、S CSR、trap/SRET 状态和 UXL 路径 | source | inspected | heliodor-master-20261012 | `heliodor_core.veryl:4647–4730, 4775–4804, 4937–4950, 5091–5096`; `csr.veryl:253–254, 360–362, 426–428, 519–526, 900–937, 1011–1014, 1091–1101` | not-run | 固定快照；RTL 静态检查 | ECALL cause、medeleg target、trap state, SRET, stvec, stval, scounteren, UXL | 静态定位不适用于运行通过 | 观察到局部路径；未证明每个架构子案例 | none |
| E4 | Heliodor 已有 S-mode 测试源码材料（runner 关系未全部确认） | test-inspected | unverified | heliodor-master-20261012 | `test/c/smode_umode_test.S`; `test/c/smode_timer_test.S`; `test/c/smode_plic_test.S`; `test/c/smode_minikernel_test.S`; `tb/test_smode_plic.veryl` | not-run | README 默认 Veryl 测试工程；仅 PLIC harness 注册已确认，其他汇编源到 runner 的关系未追踪 | U ECALL、delegated STIP、S external interrupt、mini-kernel | 各源码检查点不等同已连线/可运行 harness；不是 profile 全集 | 已检查源码；本轮没有这些源码用例的运行输出；没有 S-mode ECALL/全部 stval 子案例覆盖结论 | none |
| E5 | 本轮目标测试运行尝试及工具/快照不兼容阻断 | test-run | unverified | heliodor-master-20261012 | `tb/test_smode_plic.veryl:73,172,203–238`; project test harness | `veryl test --test test_smode_plic`; explicit latest/nightly toolchain paths | Veryl 0.22.0 (`967e477`) 与 `0.22.0-nightly` (`c3bf469`) | 核查并尝试既有 S-mode PLIC harness | 若兼容且运行，应由 test assertion 判断通过 | PATH 中没有 `veryl`；显式工具在 check 阶段失败，报 test harness `invalid_initial_assign`，并伴随端口不匹配告警；测试未启动，不记 run-pass | `/tmp/story47-smode-plic-nightly.log` |

## 学习者总结

追踪 S-mode trap 时，应先区分异常来源、cause 编码和目标特权级，再看 trap CSRs 与状态寄存器如何在 entry/return 更新。两套快照都有 U/S ECALL 分类、delegation、S trap vector 及 CSR 更新的源码线索；Heliodor 还提供 U ECALL 与定时器/PLIC 测试源码。源码位置、测试源码和本轮运行输出是三类不同证据。PATH 中没有 Veryl CLI；显式指定本机工具后，因现有 harness 在 check 阶段失败，故测试未运行；任意 Direct BASE、所有 Sstvala 值及 Sscounterenw 条件都保持未验证。

## 未解问题

- 更新 Heliodor 固定快照所需的兼容 Veryl 工具链后，U ECALL、timer、PLIC 和 mini-kernel harness 分别能否运行通过？对应运行结果及配置是什么？
- Kunminghu 当前配置中哪些 HPM counter 是非只读零值；`scounterenMask=0` 与 profile 条件如何对应？
- 两侧是否有对 S-mode ECALL 环境请求路径、多个 Direct BASE 写读/跳转、全部 Sstvala 类别值的针对性测试？
- Heliodor 各 fault cause 生成路径向 `i_trap_tval` 提供何种值，能否逐项映射到 Sstvala 的 VA/指令要求？
