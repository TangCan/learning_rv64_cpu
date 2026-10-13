---
unit_id: "rva23s64-sscofpmf"
stage_id: "Epic 5 / Story 5.4"
scope: "RVA23S64/v1.0/§3.1.2.2/Sscofpmf；对照锁定 Kunminghu V2 与 Heliodor 的 HPM 硬件溢出、OF/scountovf、模式过滤及 LCOFI 路由。"
exclusions:
  - "不宣称 RVA23S64 符合性或认证。"
  - "只把硬件事件计数增量导致的回绕作为 overflow；软件写入计数器后的回绕不算证据。"
  - "未运行的 CSR 门控、过滤、pending 清除和陷阱组合保持未验证。"
spec_refs:
  - name: "Sscofpmf"
    edition: "v1.0"
    section: "§13.1.1–13.1.2"
    url: "https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html"
  - name: "RVA23 Profile"
    edition: "v1.0"
    section: "§3.1.2.2/Sscofpmf"
    url: "https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html"
    profile_category: "mandatory"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

## 规范契约与范围

Sscofpmf v1.0 §§13.1.1–13.1.2 为性能计数器提供事件过滤与溢出状态。对 `mhpmevent3..31`，`OF` 是每计数器的 sticky overflow 标志；计数器因硬件事件递增而从最大值回绕时置位。软件写 counter 不能制造架构意义上的 overflow。软件可通过写 `mhpmevent` 的 `OF=0` 清除状态；再次硬件回绕可重新置位。

`scountovf` 的每位是对应 `mhpmevent` OF 的只读影子，其读访问矩阵与相应 `hpmcounter` 的 S/VS 访问矩阵相同：M-mode 总是可读；S/HS-mode 在 `mcounteren[X]=1` 时可读，否则读零；VS-mode 需要 `mcounteren[X]=1` 且 `hcounteren[X]=1`，否则读零。该规则只说明 `scountovf` 的读取，不等同于 `hpmcounter` CSR 自身访问陷阱的完整行为。过滤字段分别为 `MINH`、`SINH`、`UINH`、`VSINH`、`VUINH`，分别抑制 M、HS、HU、VS、VU 模式的计数。不能从一个模式的测试推定其他模式覆盖。LCOFI 是独立的本地计数器溢出中断（cause 13）：OF sticky、`scountovf` 可见、`mip/sip.LCOFIP` pending、`mideleg` 委托和实际 trap 是不同观察点。Profile 将 Sscofpmf 列为 RVA23S64 必选项。

过滤字段分别为 `MINH`、`SINH`、`UINH`、`VSINH`、`VUINH`，分别抑制 M、HS、HU、VS、VU 模式的计数。不能从一个模式的测试推定其他模式覆盖。LCOFI 是独立的本地计数器溢出中断（cause 13）：OF sticky、`scountovf` 可见、`mip/sip.LCOFIP` pending、`mideleg` 委托和实际 trap 是不同观察点。Profile 将 Sscofpmf 列为 RVA23S64 必选项。

## Kunminghu V2 活动路径

目标配置沿用 readiness 记录确认的单核 `KunminghuV2Config`；活动 CSR 经 `backend/fu/wrapper/CSR.scala` 实例化 `NewCSR`。快照 HEAD 为 `c098f996bf4d301b88693b20315486d31e93bc9d`，与锁一致。

- `MachineLevel.scala` 为事件 3–31 建立 `mhpmevent`。OF 写入优先于硬件置位，源码的 `when(wen) reg.OF := wdata.OF` 表明 CSR 写清除/置位可控；是否存在同拍竞争语义仍需运行核验。
- `mhpmcounter` 由 `perf.value` 增加。`reg.ALL +& perf.value` 的高位产生 carry，且代码注释明确 overflow 只来自硬件计数增量、不来自 `mhpmcounter`/`mhpmevent` 软件写入。counter 宽度为 64 位；预载全 1 后至少发生一次有效硬件事件是可构造的候选案例。
- `NewCSR.scala` 汇总 OF 向量给 `scountovf` 路径，结合 `mcounteren`/`hcounteren` 与当前 privilege 形成可见值；`lcofiReqVec` 由硬件 carry 且旧 OF 为 0 产生，随后进入 mip 的请求路径。
- `countingEn` 对五个模式分别检查 `MINH/SINH/UINH/VSINH/VUINH`。这是静态接线，不证明每个模式下 event 输入、计数更新或配置可访问性都正确。
- `MachineLevel.scala` 的 LCOFIP 状态具有软件写、S/VS 写视图及硬件 request hold 路径；S `scountovf` 定义位也有读取接线。中断使能、`mideleg`、陷阱 cause 与实际 delivery 尚未通过本故事的 Kunminghu 动态案例观察。

Kunminghu `src/test/` 有界搜索和 readiness 记录未找到该专题的定向 CPU harness。通用 Chisel 单测或 `make emu` 不提供本案例的程序加载、单核配置及可观察断言；本轮没有运行 Kunminghu CPU 测试。

## Heliodor 活动路径

活动 CSR/HPM 状态在 `sources/heliodor/src/core/csr.veryl`；核心计数事件接线在 `heliodor_core.veryl`。快照 HEAD 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，与锁一致。

- `mhpmcounter[3..31]`、`mhpmevent[3..31]` 为 64 位状态。计数器在所选 event 有效时增加；对旧值全 1 的硬件增量，RTL 同拍置 `mhpmevent[n][63]`（OF）和 `hpm_ovf_pend[n]`。实现使用 64 位 counter。
- 写 `mhpmcounter` 与写 `mhpmevent` 是独立 CSR 写操作；源码有 OF bit 写清除路径。但 RTL 的软件写回绕不构成本记录的溢出证据。LCOFIP 由硬件 pending 汇总并 sticky 到 `mip[13]`，另有软件写 mip 路径；OF 与 pending 的清除/re-arm 时序尚未运行验证。
- `scountovf_val[n]` 当前是 `mhpmevent[n][63] && mcounteren[n]`，且同一 read value 用于所有可达模式。本次所查实现未将 M-mode “always readable” 特例或 VS 所需的 `hcounteren` 合入该表达式。与规范的 M/HS/VS 可见性矩阵相比，这是需要动态和权限路径复核的静态差异，不能只因测试设置了 `mcounteren[3]` 就视为覆盖。
- 过滤静态逻辑仅检查 `MINH`、`SINH`、`UINH` 对应 M/S/U 模式；代码注释标明 VS/VU 位 unused，未见 `VSINH`/`VUINH` 在计数 enable 中生效。故 VSINH、VUINH 明确记录为静态缺口；不能推定覆盖，也不能据此单独给出合规判决。
- RTL 注释定义事件 5 为 mem-port-busy，已有汇编案例选择 counter 3/event 5，并把 counter3 预载全 1；M-mode `ld` 触发硬件 mem-busy 事件。测试源期望检查 cause 13、OF 和 `scountovf[3]`。这些是测试输入/断言，不是运行观察。另一个静态核查点：RTL 的硬件 wrap 分支在 `will_wrap && !e_wr` 时产生 `hpm_ovf_pend`，未显式检查原 OF 是否已为 1；规范规定 OF=1 时不再产生新的 overflow interrupt request。需复核实际状态更新/中断语义，现记为潜在差异而非运行失败结论。
- `mideleg`/中断选择逻辑将 cause 13 纳入 M/S cause 选择；`LCOFIE`、`LCOFIP`、delegation 与 trap 分别存在静态路径。但现有案例启用 M-mode 中断，未覆盖 S 委托路径，也未分别观察 pending 清除、重布防和再次 trap。

## 五种过滤模式盘点

| 字段 | 规范含义 | Kunminghu 静态路径 | Heliodor 静态路径 | 本故事动态覆盖 |
|---|---|---|---|---|
| `MINH` | 抑制 M | `countingEn` 显式检查 | M 逻辑检查该位 | 测试源码有 M-mode 检查；本轮被 testbench 阻断 |
| `SINH` | 抑制 HS/S | `countingEn` 显式检查 | S 逻辑检查该位 | 未运行/未覆盖 |
| `UINH` | 抑制 HU/U | `countingEn` 显式检查 | U 逻辑检查该位 | 未运行/未覆盖 |
| `VSINH` | 抑制 VS | `countingEn` 显式检查 | 注释称 unused，未见逻辑使用 | 未运行；Heliodor 静态缺口 |
| `VUINH` | 抑制 VU | `countingEn` 显式检查 | 注释称 unused，未见逻辑使用 | 未运行；Heliodor 静态缺口 |

“静态路径”仅表示源代码中可定位的条件表达式，不代表 event 选取、寄存器授权及架构可见性已动态验证。

## Heliodor 定向测试与运行记录

入口为 `test/sscofpmf/sscofpmf_test.S` 和 `tb/test_arch_common.veryl` 的 `test_arch_sscofpmf`。测试源码先令 counter 3 选择 event 5 (`mem-port-busy`)，设置 `MINH` 并在 M-mode 执行 64 次 load，断言 counter 保持 0；清除 `MINH` 后重置 counter 并重复 load，断言 counter 非零。这覆盖源码预期的抑制与恢复计数两种行为，但本轮没有运行它。之后源码预载 counter 全 1，硬件事件预期产生回绕，并检查 M cause 13、OF、`scountovf[3]`。harness 预算 200000 clocks。样例没有检查 OF 的软件清除/re-arm、S-mode 访问的 `mcounteren/hcounteren` 门控、LCOFIP 清除后再触发或 S-mode `mideleg` 路径。

实际运行：

| 项目 | 观察 |
|---|---|
| 命令 | `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_sscofpmf` |
| 工具 | Veryl `0.22.0 (967e477 2026-10-02)`；Verilator `5.020 2024-01-01 rev (Debian 5.020-1)` |
| 输入 / 预期 | 已检入 `test/sscofpmf/sscofpmf_test.hex`；期望 tohost/pass 及上述断言 |
| 结果 | **未启动仿真。** Veryl semantic check 以退出码 1 报 `invalid_initial_assign`：`tb/test_arch_common.veryl:440` 对 `dram` 执行 `$readmemh(HEX_FILE, dram)`。这属于 testbench/tool 兼容阻塞，不是 DUT 失败或通过。 |
| 输出 | 完整命令输出保存在本机临时文件 `/tmp/story-5-4-sscofpmf.log`；关键错误、退出状态和未启动仿真已记入本记录。临时文件不作为长期可移植证据。 |

未尝试修补上游 testbench，也未安装工具。`veryl` 不在 PATH，故使用上述本机显式路径。

## 访问与中断边界

| 观察项 | 静态线索 | 状态/未决项 |
|---|---|---|
| counter 硬件 wrap → OF | 两侧 64-bit counter carry/硬件增量路径；Heliodor有全 1 + event5 测试源 | Kunminghu 只有静态；Heliodor 测试未运行 |
| OF sticky、清除、再次布防 | 两侧有 OF CSR 写路径和硬件置位路径 | 写 0 清除后的再次事件及同拍优先级未运行验证 |
| `scountovf` | M 总是可读；S/HS 需 `mcounteren[X]`；VS 需 `mcounteren[X]` 与 `hcounteren[X]` | Kunminghu 汇总 OF；Heliodor 按 `mcounteren` mask | Heliodor 静态表达式未体现 M always-readable 或 VS 的 `hcounteren` 条件；完整访问矩阵未运行。此表描述 scountovf 位读取，不替代 counter CSR 访问陷阱分析 |
| LCOFIP/LCOFIE | 两侧均有 pending/enable 静态定义及路径 | pending 清除后的保持/重触发条件未运行验证 |
| `mideleg` / trap cause | Heliodor test source 检查 M cause 13；两侧源码可追踪中断选择 | S 委托、M/S 目标区分、enable/current privilege 组合未完整覆盖 |
| 五个 xINH | Kunminghu 五位均接入；Heliodor 仅见 M/S/U | Heliodor VS/VU 静态缺口；所有模式动态行为未验证 |

## 双核比较

Kunminghu 源码路径明确把硬件计数 carry 与软件 CSR 写区分开，并将五个过滤位都纳入 privilege 计数许可；其定向 CPU 测试入口在本轮未定位。Heliodor 有更直接的汇编案例和 testbench 注册目标，案例本身符合“硬件事件使预载计数器回绕”的证据原则，但 Veryl 检查阻断仿真。Heliodor `scountovf` 静态 mask 只依赖 `mcounteren`，且 VS/VU 过滤位标为 unused；这些差异需要动态/规范逐项复核，不据此声称完整支持或失败。

## 证据表

<a id="evidence-table"></a>

| ID | Claim | Kind | Status | 位置/快照或运行记录 |
|---|---|---|---|---|
| E1 | Sscofpmf overflow、OF 清除、模式过滤、scountovf 与 LCOFI 架构要求；RVA23S64 必选 | spec | inspected | [Sscofpmf v1.0 §§13.1.1–13.1.2](https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html)、[RVA23 v1.0 §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html) |
| E2 | Kunminghu 64-bit HPM 硬件 carry、写清除、五模式过滤与请求路径 | source | inspected | SHA `c098f996bf4d301b88693b20315486d31e93bc9d`；`MachineLevel.scala:203–211,365–378,773–786`；`NewCSR.scala:761–769,1300–1332`；`SupervisorLevel.scala:150–162` |
| E3 | Heliodor 64-bit HPM 状态、scountovf mask、M/S/U-only filter、LCOFI/mideleg静态路由 | source | inspected | SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；`src/core/csr.veryl:202–261,408–423,483–490,627–695,1202–1239` |
| E4 | counter3/event5 硬件 overflow 案例的输入与断言 | test-inspected | inspected | `test/sscofpmf/sscofpmf_test.S`；`tb/test_arch_common.veryl:6027–6052`；源码检查，不是运行结果 |
| E5 | Heliodor test_arch_sscofpmf 启动尝试 | test-run | run-fail | cwd `sources/heliodor`；Veryl `0.22.0 (967e477 2026-10-02)`，Verilator `5.020`；命令见运行记录；期望 tohost/pass；观察 testbench semantic check 在 `tb/test_arch_common.veryl:440` 因 `$readmemh`/`dram` `invalid_initial_assign` 退出 1，仿真未开始；不是 DUT 失败/通过 |
| E6 | Kunminghu 专题 CPU harness 搜索与工具就绪度 | environment | unverified | Kunminghu bounded `src/test/` 搜索未定位专题 CPU harness，`mill` 不在 PATH；未运行 Kunminghu CPU 测试 |
| E7 | Heliodor ACT4/Sail 配置与用例就绪度 | environment / test-inspected | unverified | ACT4 DUT 配置 `sources/heliodor/test/act/config/heliodor/heliodor.yaml` 的 `implemented_extensions` 未列 Sscofpmf；同目录 `sail.json` 标记 `Sscofpmf.supported=false`；`sources/heliodor/test/act/` 未发现 fetched framework/generated Sscofpmf test。PATH 无 `sail_riscv_sim`、`act4`、`mill`，虽有 `uv` 与 RISC-V GCC/objcopy，但现配置不支持且无本专题 ACT4 coverpoint，故未生成/运行用例。这是模型/验证入口缺口，不是 DUT 失败或通过 |

## 单元自检

1. 什么才算本单元中的 overflow 证据？所选硬件事件使硬件递增从最大 counter 值回绕，并分别观察 OF、scountovf、LCOFIP 和 trap；仅软件写 counter 不算。
2. OF 与 LCOFIP 是什么关系？OF 是每 counter sticky 状态；LCOFIP 是中断 pending，可能因 OF 首次硬件置位而请求，但清除/委托/陷阱是独立行为。
3. 哪些模式过滤必须逐项核对？`MINH`、`SINH`、`UINH`、`VSINH`、`VUINH`。Heliodor 此快照静态只见前三个；VS/VU 不可假定覆盖。
4. Heliodor 定向测试通过了吗？没有结论。Veryl 在 testbench `dram` `$readmemh` 检查退出，仿真没有启动。
5. 仍未验证什么？OF 清除/re-arm、S/VS `scountovf` 可见性与 mcounteren/hcounteren、LCOFIP 清除/再触发、S 委托路径及五模式实际过滤均未运行观察。

## 总结与限制

完成双核活动路径静态映射和 Heliodor 既有案例的真实启动尝试。Kunminghu 的静态源码显示五位过滤和硬件 carry；Heliodor 有 64 位硬件 wrap 源码及相应测试材料，但当前 Veryl testbench blocker 阻止仿真，且 VS/VU filter 静态路径未发现。任何 overflow、过滤、中断交付或符合性结论均不超出这些边界。ACT4/Sail 本轮未运行；readiness 记录中的工具缺口仍适用。
