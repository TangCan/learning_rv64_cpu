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

## Kunminghu V2 活动路径

目标配置沿用 readiness 记录确认的单核 `KunminghuV2Config`；活动 CSR 经 `backend/fu/wrapper/CSR.scala` 实例化 `NewCSR`。快照 HEAD 为 `c098f996bf4d301b88693b20315486d31e93bc9d`，与锁一致。

- `MachineLevel.scala` 为事件 3–31 建立 `mhpmevent`。OF 写入优先于硬件置位，源码的 `when(wen) reg.OF := wdata.OF` 表明 CSR 写清除/置位可控；是否存在同拍竞争语义仍需运行核验。
- `mhpmcounter` 由 `perf.value` 增加。`reg.ALL +& perf.value` 的高位产生 carry，且代码注释明确 overflow 只来自硬件计数增量、不来自 `mhpmcounter`/`mhpmevent` 软件写入。counter 宽度为 64 位；预载全 1 后至少发生一次有效硬件事件是可构造的候选案例。
- `NewCSR.scala` 汇总 OF 向量给 `scountovf` 路径，结合 `mcounteren`/`hcounteren` 与当前 privilege 形成可见值；`lcofiReqVec` 由硬件 carry 且旧 OF 为 0 产生，随后进入 mip 的请求路径。
- `countingEn` 对五个模式分别检查 `MINH/SINH/UINH/VSINH/VUINH`。这是静态接线，不证明每个模式下 event 输入、计数更新或配置可访问性都正确。
- `MachineLevel.scala` 的 LCOFIP 状态具有软件写、S/VS 写视图及硬件 request hold 路径；S `scountovf` 定义位也有读取接线。E10 的 Kunminghu 补充 fixture 已观察 `mideleg` 委托及 S-mode cause-13 trap；同拍清除/溢出竞争仍未运行。

Kunminghu `src/test/` 有界搜索和 readiness 记录未找到该专题的定向 CPU harness；Story 6.6 使用独立 smoke runner，以 E9/E10 记录有限 CPU 运行。

## Heliodor 活动路径

活动 CSR/HPM 状态在 `sources/heliodor/src/core/csr.veryl`；核心计数事件接线在 `heliodor_core.veryl`。快照 HEAD 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，与锁一致。

- `mhpmcounter[3..31]`、`mhpmevent[3..31]` 为 64 位状态。计数器在所选 event 有效时增加；对旧值全 1 的硬件增量，RTL 同拍置 `mhpmevent[n][63]`（OF）和 `hpm_ovf_pend[n]`。实现使用 64 位 counter。
- 写 `mhpmcounter` 与写 `mhpmevent` 是独立 CSR 写操作；源码有 OF bit 写清除路径。但 RTL 的软件写回绕不构成本记录的溢出证据。LCOFIP 由硬件 pending 汇总并 sticky 到 `mip[13]`，另有软件写 mip 路径；OF 与 pending 的清除/re-arm 时序尚未运行验证。
- `scountovf_val[n]` 当前是 `mhpmevent[n][63] && mcounteren[n]`，且同一 read value 用于所有可达模式。本次所查实现未将 M-mode “always readable” 特例或 VS 所需的 `hcounteren` 合入该表达式。与规范的 M/HS/VS 可见性矩阵相比，这是需要动态和权限路径复核的静态差异，不能只因测试设置了 `mcounteren[3]` 就视为覆盖。
- 过滤静态逻辑仅检查 `MINH`、`SINH`、`UINH` 对应 M/S/U 模式；代码注释标明 VS/VU 位 unused，未见 `VSINH`/`VUINH` 在计数 enable 中生效。故 VSINH、VUINH 明确记录为静态缺口；不能推定覆盖，也不能据此单独给出合规判决。
- RTL 注释定义事件 5 为 mem-port-busy，已有汇编案例选择 counter 3/event 5，并把 counter3 预载全 1；M-mode `ld` 触发硬件 mem-busy 事件。测试源期望检查 cause 13、OF 和 `scountovf[3]`。这些是测试输入/断言，不是运行观察。另一个静态核查点：RTL 的硬件 wrap 分支在 `will_wrap && !e_wr` 时产生 `hpm_ovf_pend`，未显式检查原 OF 是否已为 1；规范规定 OF=1 时不再产生新的 overflow interrupt request。需复核实际状态更新/中断语义，现记为潜在差异而非运行失败结论。
- `mideleg`/中断选择逻辑将 cause 13 纳入 M/S cause 选择；`LCOFIE`、`LCOFIP`、delegation 与 trap 分别存在静态路径。E10 在 Kunminghu 实测 S 委托；Heliodor 的现有 fixture 仍只覆盖 M-mode 中断。Kunminghu E9 分别观察 pending 清除、重布防和再次 trap。

## 五种过滤模式盘点

| 字段 | 规范含义 | Kunminghu 静态路径 | Heliodor 静态路径 | 本故事动态覆盖 |
|---|---|---|---|---|
| `MINH` | 抑制 M | `countingEn` 显式检查 | M 逻辑检查该位 | Kunminghu 验证过滤/解除过滤；Heliodor 验证 M-mode 过滤 |
| `SINH` | 抑制 HS/S | `countingEn` 显式检查 | S 逻辑检查该位 | Kunminghu 验证过滤/解除过滤；Heliodor 未运行 |
| `UINH` | 抑制 HU/U | `countingEn` 显式检查 | U 逻辑检查该位 | Kunminghu 验证过滤/解除过滤；Heliodor 未运行 |
| `VSINH` | 抑制 VS | `countingEn` 显式检查 | 注释称 unused，未见逻辑使用 | Kunminghu 验证过滤/解除过滤；Heliodor 静态缺口 |
| `VUINH` | 抑制 VU | `countingEn` 显式检查 | 注释称 unused，未见逻辑使用 | Kunminghu 验证过滤/解除过滤；Heliodor 静态缺口 |

“静态路径”仅表示源代码中可定位的条件表达式，不代表 event 选取、寄存器授权及架构可见性已动态验证。

## Story 6.6 双核运行矩阵

| 核 | 固定快照 | 用例/配置 | 结果 | 已观察边界 |
|---|---|---|---|---|
| Heliodor | `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `test_arch_sscofpmf`，单 DUT；counter3/event5；64-bit 全 1 预载；M-mode；MINH 置位/清除各 64 次 load；200000 arch clocks | `run-pass`，CPU started，exit 0，tohost=1/pass=1 | fixture 断言 MINH 阶段 counter=0、清除后 counter 非零、硬件 event wrap 后 M cause 13、OF=1、scountovf[3]=1。未单独读取 LCOFIP，也未测 OF 清除/re-arm、S/VS 门控、委托或其余过滤模式。隔离 harness 只对副本的 dram 声明加 Veryl `initial_assign` 局部 allow，并排除未实例化 debug harness；原始 fixture 与源哈希归档。见 E8。 |
| Kunminghu V2 | `c098f996bf4d301b88693b20315486d31e93bc9d` | 单核 `KunminghuV2Config`；counter3/event2 (`ifu_req`)；64-bit 全 1 预载；逐项测试五个 xINH；100000 cycle/10000 instruction 上限 | `run-pass`，CPU started，exit 0，good trap | 五种模式均检查抑制时无计数、解除后硬件事件计数；另检查硬件 wrap、cause 13、OF/scountovf set/clear、单独清 LCOFIP、第二次硬件 wrap/trap。S/VS `scountovf` 门控与 S delegation 另见 E10。 |

ACT4/Sail 对照未运行：E7 所记 Heliodor ACT 配置未启用 Sscofpmf、Sail 配置标记 unsupported，且无可用专题 coverpoint；属于模型/工具环境边界，不影响 Heliodor CPU 的 `run-pass` 分类。

## E8 Heliodor fixture assertions 与 raw observation 边界

E8 manifest record 的 `expected_controls` 包含 event5、counter3、64-bit 全 1 preload、M-mode、MINH on/off 和 cause 13；同一 record 还包含 `configuration`、完整 `command`、`tools`、`exit_code`、`cpu_started`、`output`/SHA、归档文件及 SHA。`observed_values` 保存 tohost=1、pass=true 和 fixture assertion 摘要。汇编断言 MINH=1 时 counter=0、MINH 清除后 counter 非零，并在硬件 wrap 后断言 cause 13、OF 和 `scountovf[3]`。日志不逐项打印 counter、cause、OF 或 `scountovf` 的原始 CSR 值；这些是断言结果，不是可从 log 独立读取的 telemetry。见 [完整 E8 metadata](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T093231Z-2273768/run-metadata.json) 与 [E8 log](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T093231Z-2273768/output.log)。

## E9 Kunminghu 五种 xINH 的输入、预期与观察

使用同一个 counter3/event2 (`ifu_req`)、64-bit counter。M-mode 起始阶段先验证 `MINH=1` 时计数为 0，再清除 MINH 并验证计数非零。随后依次进入 S/U/VS/VU，每项以对应 `xINH=1` 执行 64 个 NOP 并预期 counter 保持 0，再清除此位，以相同硬件事件执行另一段 64 个 NOP 并预期 counter 非零。

| 字段 | 输入模式 / 过滤状态 | 预期 | 观察方式 / 归档 |
|---|---|---|---|
| MINH | M，置位 → 清除 | 置位期间无计数；清除后有硬件事件计数 | 汇编分别读取 counter 并分支至失败标记；E9 通过 good-trap 证明断言已通过。输入：[v4 fixture](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/input.S)，输出：[log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。 |
| SINH | S，SINH=1 → SINH=0 | 置位阶段 counter=0；清除后 counter>0 | `FILTER_CASE s_filter` 检查两阶段并累积失败位；同一 v4 输入，见 [E9 input](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/input.S) / [E9 log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。 |
| UINH | U，UINH=1 → UINH=0 | 置位阶段 counter=0；清除后 counter>0 | `FILTER_CASE u_filter` 检查两阶段并累积失败位；同一 v4 输入，见 [E9 input](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/input.S) / [E9 log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。 |
| VSINH | VS，VSINH=1 → VSINH=0 | 置位阶段 counter=0；清除后 counter>0 | `FILTER_CASE vs_filter` 检查两阶段并累积失败位；同一 v4 输入，见 [E9 input](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/input.S) / [E9 log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。 |
| VUINH | VU，VUINH=1 → VUINH=0 | 置位阶段 counter=0；清除后 counter>0 | `FILTER_CASE vu_filter` 检查两阶段并累积失败位；同一 v4 输入，见 [E9 input](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/input.S) / [E9 log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。 |

每项的数值由 fixture 中的 CSR 读取和条件分支检查，不会逐项打印到原始日志。E9 的 `run-pass` / good-trap 只表示所有这些断言均通过；原始值不可从日志重建。完整命令、工具版本和输入/产物哈希见 [manifest E9](evidence/cpu-validation-toolchain-v1.yaml)。

## E10 Kunminghu `scountovf` gate 与 S 委托输入矩阵

OF 先由 event2/counter3 的硬件增量置位。fixture 随后从 M/S/VS 读取 `scountovf`，逐项断言：

| 当前模式 | `mcounteren[3]` | `hcounteren[3]` | 预期 `scountovf[3]` | 断言位置 |
|---|---:|---:|---:|---|
| M | 1 | 1 | 1（M always-readable） | 起始 M 检查 |
| S | 0 | — | 0 | `s_mcounteren_off` |
| S | 1 | — | 1 | `s_mcounteren_on` |
| VS | 1 | 0 | 0 | `vs_hcounteren_off` |
| VS | 0 | 1 | 0 | `vs_mcounteren_off` |
| VS | 1 | 1 | 1 | `vs_both_on` |

随后 fixture 写 `mideleg[13]=1`，设置 delegated `LCOFIE`/SIE，使硬件 overflow interrupt 进入 S handler。handler 断言 `scause` 为 interrupt cause 13、`scountovf[3]=1`、`sip.LCOFIP=1`，再到达 good-trap。表中的每个 CSR 值均由汇编读取后作分支断言，未逐项打印到原始运行日志；日志只有整体启动/结束标记，不能据此列出原始读值。最终输入归档为 [E10 input.S](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T101934Z-3e81181d1d02/input.S)，完整输出为 [E10 log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T101934Z-3e81181d1d02/output.log)，运行记录/哈希见 [manifest E10](evidence/cpu-validation-toolchain-v1.yaml)。

表中六个 E10 测试组合都可达且均已执行，没有 blocked/unreachable 组合；这不是所有模式与两个 counteren 位的完整笛卡尔积（例如 M 的 always-readable 特例无需 gate 关闭矩阵）。

## Heliodor 定向测试与运行记录

Heliodor 入口为 `test/sscofpmf/sscofpmf_test.S` 和 `tb/test_arch_common.veryl` 的 `test_arch_sscofpmf`。该例选择 counter 3/event 5 (`mem-port-busy`)，检查 MINH 过滤/恢复，再以硬件事件回绕检查 M cause 13、OF、`scountovf[3]`。Story 6.6 E8 已运行此有限案例。Kunminghu fixture `experiments/sscofpmf/kunminghu-sscofpmf-complete-v4.S` 使用 selector 2 (`ifu_req`)，逐项检查五个 xINH 的过滤/解除过滤，并检查硬件 overflow、OF/scountovf 清除、LCOFIP 独立清除及第二次硬件 wrap/trap。其运行上限为 100000 cycles/10000 instructions。E10 补充案验证 Kunminghu S/VS `scountovf` 权限组合与 S-mode delegation；Heliodor 未运行这些组合。

Story 5.4 曾在上游 checkout 原样尝试，并因 Veryl 对 `dram` `$readmemh` 的 `invalid_initial_assign` 阻断；该历史结果保留如下。Story 6.6 则在隔离副本应用局部 lint allow 后重新运行。

历史实际运行：

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
| counter 硬件 wrap → OF | 两侧 64-bit counter carry/硬件增量路径；两侧均有定向硬件事件 fixture | Kunminghu event2/counter3 与 Heliodor event5/counter3 均运行；限于指定配置/事件 |
| OF sticky、清除、再次布防 | 两侧有 OF CSR 写路径和硬件置位路径 | Kunminghu 观察清除和第二次硬件 wrap；Heliodor 清除/re-arm、两侧同拍优先级未覆盖 |
| `scountovf` | M 总是可读；S/HS 需 `mcounteren[X]`；VS 需 `mcounteren[X]` 与 `hcounteren[X]` | Kunminghu 已运行 M always、S gate off/on、VS 单 gate off/both on；Heliodor 按 `mcounteren` mask | Kunminghu 的 counter3 组合均通过断言；Heliodor 静态表达式未体现 M always-readable 或 VS 的 `hcounteren` 条件，未运行访问矩阵。此表描述 scountovf 位读取，不替代 counter CSR 访问陷阱分析 |
| LCOFIP/LCOFIE | 两侧均有 pending/enable 静态定义及路径 | Kunminghu 观察首次 pending、软件独立清除、第二次 M cause-13 trap，并在补充案观察 cause-13 S trap 与 `sip.LCOFIP`；Heliodor 清除/重触发及 S delegation 未覆盖 |
| `mideleg` / trap cause | Heliodor test source 检查 M cause 13；两侧源码可追踪中断选择 | Kunminghu 补充运行观察 delegated S cause 13；Heliodor 的 S delegation 与其余路由组合未覆盖 |
| 五个 xINH | Kunminghu 五位均接入；Heliodor 仅见 M/S/U | Kunminghu 五种模式均有动态过滤/解除观察；Heliodor VS/VU 静态缺口，S/U 未运行 |

## 双核比较

Kunminghu 与 Heliodor 均观察到有限硬件事件 overflow 案例通过。Kunminghu 还运行了五种 xINH、OF/scountovf 清除、LCOFIP 独立清除、S/VS `scountovf` 权限组合及 cause-13 S delegation；Heliodor 当前案例只覆盖 MINH 与首次 overflow。Heliodor `scountovf` 静态 mask 只依赖 `mcounteren`，且 VS/VU 过滤位标为 unused；这些差异与未覆盖访问矩阵仍需复核，不据此声称完整支持或失败。

## 证据表

<a id="evidence-table"></a>

| ID | Claim | Kind | Status | 位置/快照或运行记录 |
|---|---|---|---|---|
| E1 | Sscofpmf overflow、OF 清除、模式过滤、scountovf 与 LCOFI 架构要求；RVA23S64 必选 | spec | inspected | [Sscofpmf v1.0 §§13.1.1–13.1.2](https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html)、[RVA23 v1.0 §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html) |
| E2 | Kunminghu 64-bit HPM 硬件 carry、写清除、五模式过滤与请求路径 | source | inspected | SHA `c098f996bf4d301b88693b20315486d31e93bc9d`；`MachineLevel.scala:203–211,365–378,773–786`；`NewCSR.scala:761–769,1300–1332`；`SupervisorLevel.scala:150–162` |
| E3 | Heliodor 64-bit HPM 状态、scountovf mask、M/S/U-only filter、LCOFI/mideleg静态路由 | source | inspected | SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；[csr.veryl:202–261,408–423,483–490,627–695,1202–1239](../../sources/heliodor/src/core/csr.veryl)，VS/VU unused 注释及仅 M/S/U inhibit 条件见 [csr.veryl:1213–1222](../../sources/heliodor/src/core/csr.veryl#L1213)。 |
| E4 | counter3/event5 硬件 overflow 案例的输入与断言 | test-inspected | inspected | `test/sscofpmf/sscofpmf_test.S`；`tb/test_arch_common.veryl:6027–6052`；源码检查，不是运行结果 |
| E5 | Heliodor test_arch_sscofpmf 启动尝试（Story 5.4 历史记录） | test-run | blocked | cwd `sources/heliodor`；Veryl `0.22.0 (967e477 2026-10-02)`，Verilator `5.020`；命令见运行记录；期望 tohost/pass；观察 testbench semantic check 在 `tb/test_arch_common.veryl:440` 因 `$readmemh`/`dram` `invalid_initial_assign` 退出 1，CPU 未启动。这是 harness/tool blocker，不是 CPU run-fail；Story 6.6 的隔离运行另见 E8。 |
| E6 | Kunminghu 专题 CPU harness 搜索与工具就绪度 | environment | inspected | Kunminghu bounded `src/test/` 搜索未定位专题 CPU harness，`mill` 不在 PATH；Story 6.6 使用独立 smoke runner 完成 E9/E10 运行 |
| E7 | Heliodor ACT4/Sail 配置与用例就绪度 | environment / test-inspected | unverified | ACT4 [DUT config](../../sources/heliodor/test/act/config/heliodor/heliodor.yaml#L8) 的 `implemented_extensions` 未列 Sscofpmf；Sail [config](../../sources/heliodor/test/act/config/heliodor/sail.json#L683) 明确 `Sscofpmf.supported=false`。`sources/heliodor/test/act/` 未发现 fetched framework/generated Sscofpmf test。PATH 无 `sail_riscv_sim`、`act4`、`mill`，且配置/coverpoint 不支持该专题，故未生成/运行用例。这是模型/验证入口缺口，不是 DUT 失败或通过 |
| E8 | Heliodor Story 6.6 隔离 Sscofpmf CPU 运行 | test-run | run-pass | ID `heliodor-core-20261014T093231Z-2273768`；snapshot `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；counter3/event5、64-bit preload `0xffffffffffffffff`、M-mode、MINH on/off；Veryl 0.22.0 / Verilator 5.020 / g++ 13.3；CPU started，exit 0，fixture assertions pass，tohost=1；[完整 run metadata](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T093231Z-2273768/run-metadata.json)、[归档目录](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T093231Z-2273768/)（隔离输入/harness SHA、命令和产物哈希）及 [run log](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T093231Z-2273768/output.log)。只证明该有限案例；LCOFIP 独立读取及 clear/re-arm、S/VS access/delegation、其他 xINH 未覆盖。 |
| E9 | Kunminghu Story 6.6 五模式过滤与 overflow/clear/re-arm CPU 运行 | test-run | run-pass | ID `kunminghu-fixture-20261014T095905Z-3e81181d1d02`；snapshot `c098f996bf4d301b88693b20315486d31e93bc9d`；counter3/event2 (`ifu_req`)，64-bit 全 1；五个 xINH 分别检查抑制/解除；硬件 wrap 检查 cause 13、OF、scountovf[3]；清 OF 后独立写 mip 清 LCOFIP、验证清除并观察第二次硬件 wrap/cause 13；CPU started、exit 0、good trap。完整记录在 [toolchain manifest](evidence/cpu-validation-toolchain-v1.yaml)，运行输出见 [run log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T095905Z-3e81181d1d02/output.log)。S/VS gate 与 S delegation 见 E10；同拍 clear/overflow 竞争未覆盖。 |
| E10 | Kunminghu Story 6.6 `scountovf` access matrix 与 S-delegated LCOFI | test-run | run-pass | ID `kunminghu-fixture-20261014T101934Z-3e81181d1d02`；snapshot `c098f996bf4d301b88693b20315486d31e93bc9d`；counter3/event2 (`ifu_req`)，64-bit counter；OF 由硬件事件置位。fixture 检查 M always-visible、S `mcounteren[3]` off/on、VS `hcounteren[3]` off / `mcounteren[3]` off / both on；随后写 `mideleg[13]`、启用 LCOFIE/SIE，并在 S handler 断言 cause 13、`scountovf[3]` 和 `sip.LCOFIP`。GCC 15.1、Verilator 5.050、锁定 emulator/NEMU hashes；CPU started、exit 0、good trap。输入、命令及输出/工件哈希在 [toolchain manifest](evidence/cpu-validation-toolchain-v1.yaml) 与 [run log](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T101934Z-3e81181d1d02/output.log)。仅限该事件和配置。 |

## 验证与复现

Kunminghu 硬件过滤回归可在不改写正式证据目录的情况下运行：`RUN_KUNMINGHU_SSCOFPMF_REGRESSION=1 uv run --no-cache pytest -q scripts/tests/test_kunminghu_smoke.py -k fixtures_repeatable`。它分别运行 hardware-filter/access-route，核对两条 run-pass 记录，使用临时 manifest/evidence 子目录并在结束时清理；本次结果为 1 passed、49 deselected。Manifest 校验命令为 `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml`；执行环境 Python 版本为 3.12.3。

## 单元自检

1. 什么才算本单元中的 overflow 证据？所选硬件事件使硬件递增从最大 counter 值回绕，并分别观察 OF、scountovf、LCOFIP 和 trap；仅软件写 counter 不算。
2. OF 与 LCOFIP 是什么关系？OF 是每 counter sticky 状态；LCOFIP 是中断 pending，可能因 OF 首次硬件置位而请求，但清除/委托/陷阱是独立行为。
3. 哪些模式过滤必须逐项核对？`MINH`、`SINH`、`UINH`、`VSINH`、`VUINH`。Heliodor 此快照静态只见前三个；VS/VU 不可假定覆盖。
4. 两侧 CPU 案例各观察了什么？Kunminghu E9 运行五种 xINH、OF/scountovf/LCOFIP 清除及第二次 trap，E10 运行 S/VS 权限组合与 cause-13 S delegation；Heliodor 运行 MINH 和首次硬件 overflow/cause/OF/scountovf。
5. 仍未验证什么？Heliodor OF 清除/re-arm、scountovf 权限矩阵和 S 委托未运行；Kunminghu 同拍 clear/overflow 竞争未覆盖。Heliodor VS/VU filter 静态实现中未见生效逻辑。

## 总结与限制

完成双核活动路径静态映射和各自有限 CPU 运行。Kunminghu 观察五种 xINH、硬件 wrap、OF/scountovf 清除、LCOFIP 独立清除/重触发、S/VS `scountovf` 权限组合及 cause-13 S delegation；Heliodor 观察 event5/MINH/首次硬件 wrap/cause 13/OF/scountovf。Heliodor VS/VU filter 静态路径未发现，其权限矩阵与 delegation 未运行。结论仅适用于所记录输入，不构成 RVA23 符合性或认证。ACT4/Sail 未运行；现有配置/模型没有该专题的可用对照。
