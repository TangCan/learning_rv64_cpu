---
unit_id: "rva23s64-sstc"
stage_id: "Epic 5 / Story 5.3"
scope: "RVA23S64/v1.0/§3.1.2.2/Sstc；对照锁定 Kunminghu V2 与 Heliodor 快照的 stimecmp/vstimecmp、STCE、time/guest time、pending 和 S/VS 中断路径。"
exclusions:
  - "不宣称 RVA23S64 符合性或认证。"
  - "不要求或推断 cycle-exact pending 延迟；规范只保证状态变化最终反映。"
  - "不覆盖 RV32 的 stimecmph/vstimecmph 分段访问、计时器频率/时间单调性或完整异步中断时序。"
  - "未运行的比较边界、门控和委托行为均保持未验证。"
spec_refs:
  - name: "Sstc"
    edition: "v1.0, ratified"
    section: "§12.1–12.3"
    url: "https://docs.riscv.org/reference/isa/v20250508/priv/sstc.html"
  - name: "RVA23 Profile"
    edition: "v1.0, ratified"
    section: "§3.1.2.2/Sstc"
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

Sstc v1.0 增加 S 级 `stimecmp`（CSR `0x14D`）和 H 扩展下的 VS 级 `vstimecmp`（`0x24D`）。比较按无符号数进行：当 `time >= stimecmp` 时 STIP pending；当截断为 64 位的 `time + htimedelta >= vstimecmp` 时 VSTIP pending。严格小于时相应硬件 pending 为低，等于和大于时为高。比较状态发生变化后，规范保证 STIP/VSTIP **最终**反映变化，但不保证立即；中断实际陷入还受标准中断使能、当前特权态和委托规则控制，因此允许有限范围的异步传播时间，不要求周期精确延迟。

Sstc CSR 访问权限按当前特权模式区分：HS/S 访问 `stimecmp` 受 `mcounteren.TM` 和 `menvcfg.STCE` 控制；VS 访问 `vstimecmp`（或 `stimecmp` alias）还受 `hcounteren.TM` 与 `henvcfg.STCE` 控制，并同时受 `mcounteren.TM` 和 M 级 `menvcfg.STCE` 约束。对应关闭时，低于 M 的访问触发 illegal-instruction，VS 在上层 STCE 允许而 `henvcfg.STCE=0` 时触发 virtual-instruction；`menvcfg.STCE=0` 时，非 M 对这些 CSR 的访问也触发 illegal-instruction，STIP 退回未实现 Sstc 时的软件控制语义。若 M 级 STCE 为 1 而 `henvcfg.STCE=0`，VS 对 `stimecmp`（即 `vstimecmp` 别名）的访问触发 virtual-instruction，VSTIP 退回未实现此功能时的语义。RVA23S64 v1.0 §3.1.2.2 将 Sstc 列为必选扩展。

## Kunminghu V2 活动路径

目标配置是 readiness 记录确认的单核 `KunminghuV2Config`，活动 CSR 由 `wrapper/CSR.scala` 实例化 `NewCSR`，配置 `EXT_SSTC=true`。以下结论来自锁定 checkout 的静态追踪。

- `SupervisorLevel.scala` 将 `stimecmp` 定义为 64 位 RW CSR，复位为全 1；`VirtualSupervisorLevel.scala` 对 `vstimecmp` 做同样定义。S CSR 地址在 V=1 时映射到 VS CSR 地址。
- `CSRPermitModule.scala` 检查非 M 访问的 `mcounteren.TM`，并检查 `menvcfg.STCE`；VS 特有检查还检查 `hcounteren.TM` 与 `henvcfg.STCE`。`HypervisorLevel.scala` 在 `menvcfg.STCE=0` 时将读出的 `henvcfg.STCE` 约束为 0。
- `time` 的裸值来自 CLINT；`vstime` 使用 `time + htimedelta`。`SstcInterruptGen.scala` 以 `>=` 生成 STIP/VSTIP，并在时间、比较值或配置写入时更新寄存器化结果；输入 valid/更新寄存器意味着源码没有承诺精确周期延迟。
- `NewCSR.scala` 将生成的 STIP/VSTIP 接到 `platformIRP`。`MachineLevel.scala` 在 STCE 开启时以硬件 STIP 替换软件 mip.STIP，并组合 `hvip.VSTIP` 与硬件 VSTIP；Hypervisor/interrupt 路径再结合 `mideleg`、`hideleg` 和对应使能决定可见性/陷入路由。
- 源码仍有边界需动态核验：MachineLevel 有关于 STIP 写行为的 TODO 注释；Sstc 定向测试未发现；读出的静态接线不能证明所有竞争、权限与委托组合正确。

## Heliodor 活动路径

锁定 `heliodor_core` 的 CSR 状态、权限检查和中断交付路径位于 `csr.veryl`、`alu_wrap.veryl` 及 `heliodor_core.veryl`。测试入口由仓库根目录下的 `tb/test_arch_common.veryl` 注册（对应 `sources/heliodor/tb/test_arch_common.veryl`）。

- `csr.veryl` 保存 64 位 `stimecmp` 和 `vstimecmp`，均复位为全 1。Menvcfg/henvcfg 的 bit 63 作为 STCE；STIP 比较 `i_mtime >= stimecmp`，VS 比较 `(i_mtime + htimedelta) >= vstimecmp`。静态源码中的 64 位向量加法输出为 64 位，路径形态对应规范规定的 64 位截断；本轮没有非零 `htimedelta` 溢出/截断运行案例或观察。`henvcfg.STCE` 可写值虽存储，但 guest timer 比较器由 M/H 两级 STCE 同时门控。该比较器门控结论独立于下文的 CSR 访问权限检查结论。
- V=1 时 guest 读 `time` 得 `i_mtime + htimedelta`，写 `stimecmp` 别名更新 `vstimecmp`；HS/M 可通过独立 VS CSR 地址观察/写入状态。STIP 在 STCE 开启时由比较结果驱动，否则回到 `mip.STIP` 软件值。VSTIP 在 guest Sstc 关闭时回到 `hvip.VSTIP`；打开时由比较源与软件注入 pending 组合。`hip.VSTIP`、`vsip.STIP` 和 hideleg/VS 使能的 VS delivery 路径均可静态追踪。
- 已检查的 `alu_wrap.veryl` 通用 CSR permission check 依据 CSR 地址特权级、只读属性和未实现地址判断；该检查片段未显示 `menvcfg.STCE`、`henvcfg.STCE` 或 TM 条件。现有 S/VS 测试也不检查 STCE 关闭时 CSR 访问应触发的异常。因此这里记录为权限门控静态待核项，不能从比较器路径推断访问条件满足规范。

| Heliodor CSR 访问场景 | 此次静态检查可确认 | 尚未由已检查路径/测试确认 |
|---|---|---|
| HS/S-mode 读写 `stimecmp` | 通用 checker 可按 CSR 地址特权级与读写属性处理；S 测试检查比较器门控而非 CSR 访问权限：M-mode 打开 `mie.STIE`/`mstatus.MIE`、令 `stimecmp=0` 并把 `mtvec` 指向失败 handler；只有 timer pending 造成可观察的 M trap 才会失败；另在 `STCE=1` 时走 S interrupt。 | `mcounteren.TM` 与 `menvcfg.STCE` 对 S-mode `stimecmp` 访问异常的专用判定；当前 S 测试未执行 STCE=0 CSR 访问。 |
| VS-mode 读写 `stimecmp` alias / `vstimecmp` | CSR 状态路径可见 V=1 时使用 guest compare state；测试材料为比较器和中断交付同时打开 M/H 两级 STCE 并走 VS delivery。这不验证 CSR 访问权限 gate。 | `hcounteren.TM`、`mcounteren.TM` 与 `henvcfg.STCE` 的独立关闭行为，以及 virtual-instruction / illegal-instruction 的异常类型。 |

## 测试材料与覆盖评估

Heliodor 已检入 `test/sstc/sstc_test.S`/`.hex` 和 `test/hsstc/hsstc_test.S`/`.hex`。两个 testbench 目标均开启 `MTIME_EN=1`，配置的测试预算为 100000 clocks；由于语义检查阶段即失败，该预算并未实际运行。比较的是 tohost/pass；这些输入和断言不是本次 CPU 观察。

| 案例 | 输入与期望 | 覆盖及未覆盖 |
|---|---|---|
| `test_arch_sstc_stimecmp` | `stimecmp=0`、M-mode 开 STIE/MIE、`menvcfg.STCE=0`，期望不触发陷阱；随后开 STCE、委托 cause 5，S-mode 设 `stimecmp=time+400`，期望进入 S handler 且 `scause=(interrupt|5)`。 | 第一阶段在 M-mode 运行，打开 `mie.STIE`/`mstatus.MIE`，把比较值设为 0 并将 `mtvec` 指向失败处理器；如果硬件错误地产生 timer pending，预期会进入失败处理器。它检查 STCE=0 的 pending 行为，不检查 S-mode 在 STCE=0 时访问 CSR 的异常。未单独观测 `<`、`==`、`>` 三种阈值，也不测试 `mcounteren.TM`、pending 清除边界或精确延迟。 |
| `test_arch_hsstc` | M-mode 同时设置 `menvcfg.STCE` 与 `henvcfg.STCE`、`htimedelta=0`、`hideleg.VSTIP=1`；VS 读 time 并将 `stimecmp` 设为 guest time 加 `0x400`，期望 VS handler 收到 cause 5，前移比较值后退出 guest。 | 覆盖双级使能同时打开时的 `vstimecmp` 别名、零 offset、VSTIP→VS 委托/陷入链。未覆盖非零 `htimedelta`、两级 STCE 各自关闭、TM 权限、非委托时 HS 接收、`<`/`==`/`>` 分别观测或 V=0 pending 可见性。 |

两份汇编都没有专门设置比较值刚好等于当前时间并单独读取 pending 的子案例。测试目标若能运行，异步中断到达说明该路径最终可交付，不应据此反推固定比较周期或 cycle-exact 延迟。

## 双核比较

Kunminghu 用独立 CSR 模块、带更新条件的比较器和中断 pending bundle，源码显示 S/VS 访问门控及 S/VS 计时器输入；Heliodor 在 CSR combinational view 中形成比较和 alias，并把有效 pending 纳入 HS/VS 中断交付。Kunminghu 的权限路径比 Heliodor 此次追踪到的通用 checker 显式包含 STCE/TM 条件；Heliodor 的专用访问门控尚未从活动路径中定位，属于风险/未决边界。两边源码都包含 Sstc 路径；只凭源码不能判断整体符合性。

## 证据表

<a id="evidence-table"></a>

| ID | Claim | Kind | Status | 位置/快照或运行记录 |
|---|---|---|---|---|
| E1 | Sstc unsigned `>=`、最终 pending、S/VS access gate、`htimedelta` 与标准委托规则；RVA23S64 必选项 | spec | inspected | [Sstc v1.0 §12.1–12.3](https://docs.riscv.org/reference/isa/v20250508/priv/sstc.html)、[RVA23 v1.0 §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html) |
| E2 | Kunminghu S/VS compare CSR、TM/STCE permission check、计时输入及 pending 接线 | source | inspected | 快照 `c098f996bf4d301b88693b20315486d31e93bc9d`；[SupervisorLevel.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SupervisorLevel.scala:131)、[VirtualSupervisorLevel.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/VirtualSupervisorLevel.scala:191)、[CSRPermitModule.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRPermitModule.scala:225)、[SstcInterruptGen.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SstcInterruptGen.scala:33)、[NewCSR.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala:536)、[MachineLevel.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/MachineLevel.scala:260) |
| E3 | Heliodor S/VS compare、guest time、pending alias 和 delivery 静态路径；访问权限待核 | source | inspected | 快照 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；[csr.veryl](../../sources/heliodor/src/core/csr.veryl:441)、[alu_wrap.veryl](../../sources/heliodor/src/core/alu_wrap.veryl:446)；已检查通用 CSR 地址权限逻辑，在本次活动路径范围内未定位 STCE/TM 专用门控 |
| E4 | Heliodor S-mode/VS-mode 测试输入及覆盖边界 | test-inspected | inspected | [sstc_test.S](../../sources/heliodor/test/sstc/sstc_test.S)、[hsstc_test.S](../../sources/heliodor/test/hsstc/hsstc_test.S)、[test_arch_common.veryl](../../sources/heliodor/tb/test_arch_common.veryl:4557)；test sources only |
| E5 | S-mode 定向目标尝试 | test-run | run-fail | cwd `sources/heliodor`；Veryl `0.22.0 (967e477 2026-10-02)`；命令 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_sstc_stimecmp`；Verilator `5.020`；测试输入 `test/sstc/sstc_test.hex`，`MTIME_EN=1`，预算 100000 clocks。期望 tohost/pass；观察：Veryl testbench check 在 `tb/test_arch_common.veryl:440` 因 `$readmemh(HEX_FILE, dram)` 的 `invalid_initial_assign` 退出 1，仿真未启动。完整原始输出 `/tmp/story-5-3-sstc-stimecmp.log`；关键错误摘录见下方“验证状态与未决边界”，无仿真产物。 |
| E6 | VS 定向目标尝试 | test-run | run-fail | cwd `sources/heliodor`；同 E5 工具版本；命令 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_hsstc`；输入 `test/hsstc/hsstc_test.hex`，`MTIME_EN=1`，预算 100000 clocks。期望 tohost/pass；观察：同在 `tb/test_arch_common.veryl:440` 因 `$readmemh(HEX_FILE, dram)` 的 `invalid_initial_assign` 退出 1，仿真未启动。完整原始输出 `/tmp/story-5-3-hsstc.log`；关键错误摘录见下方“验证状态与未决边界”，无仿真产物。 |
| E7 | Kunminghu 测试入口就绪度 | environment / test-inspected | unverified | 快照中 `src/test/` 有界搜索 `sstc`、`stimecmp`、`vstimecmp` 无定向命中；`src/test/scala` 当前是模块/后端单测，不是已定位的 CSR/interrupt CPU harness。`command -v mill` 无路径结果，仓库也无 `mill` wrapper；Makefile 的通用 emu 构建不提供本案例 fixture/加载与观察步骤。本故事未运行 Kunminghu CPU 测试。 |
| E8 | Story 6.5 新增的 S/VS 动态比较、访问门与路由矩阵 | test-run | observed | [动态运行表](#dynamic-sstc-evidence)、不可变输入副本、日志与 SHA-256 见 [toolchain manifest](evidence/cpu-validation-toolchain-v1.yaml)；coverage 仍保持 `studied-unverified`，未宣称合规。 |

## 验证状态与未决边界

> 本节记录 Epic 5 / Story 5.3 的原始静态研究基线和当时阻断；它不是当前动态验证状态。Epic 6 / Story 6.5 后续使用隔离 harness 跑了 S/VS 矩阵，最终结果见本页下方“Story 6.5 动态复验结果”和 manifest。本节的历史命令与早期判断保留作追溯。

- 两侧 HEAD 已复核与 `sources.lock` 完全一致；未改动 `sources/` 上游 checkout。
- Heliodor 两条候选命令均已实际调用。Veryl 成功读入项目源后在 testbench semantic check 阶段失败，具体错误为 `invalid_initial_assign`: `tb/test_arch_common.veryl:440` 对 `dram` 执行 `$readmemh`，退出码 1；CPU 仿真体没有启动。因此没有任何动态 `run-pass` 结果。完整命令输出当时保存在 `/tmp/story-5-3-sstc-stimecmp.log` 与 `/tmp/story-5-3-hsstc.log`；关键错误摘录如下，供脱离原机器复核：

```text
Error: invalid_initial_assign (https://doc.veryl-lang.org/book/07_appendix/02_semantic_error.html#invalid_initial_assign)
  × "dram" is assigned in an initial block
     ╭─[sources/heliodor/tb/test_arch_common.veryl:440:29]
 439 │     initial {
 440 │         $readmemh(HEX_FILE, dram);
     ·                             ──┬─
     ·                               ╰── Error location
 441 │     }
     ╰────
```

- Kunminghu 对锁定 checkout 的 `src/test/` 做了有界文本搜索：`rg -ni 'sstc|stimecmp|vstimecmp' sources/xiangshan/src/test`，无匹配输出。候选 harness 的判定条件是能以 `KunminghuV2Config` 启动 CPU、加载此故事的汇编/二进制输入，并观察 CSR/pending/trap 或 `tohost` 结果；未定位满足条件的入口。该搜索不证明全仓不存在间接或生成测试。虽有通用 `make emu CONFIG=KunminghuV2Config NUM_CORES=1` 路线，本机 `mill` 不在 PATH、checkout 无 wrapper，且没有本故事 fixture/加载/观察适配；故不将通用 emu 构建算作可运行案例。
- `<`、`==`、`>` 阈值分离观测、禁用 STCE 下 S/VS CSR 非法访问、各 TM 控制、VS 非零 offset、两级 STCE 独立关闭、非委托 HS 路径和 pending 清除均未验证。
- Heliodor 通用 CSR permission 片段中未见 Sstc 专用 STCE/TM 判定；这是静态追踪未定位的门控问题，须后续审查/验证，不能据此单独宣告实现缺失或合规。
- 不推断异步 timer interrupt 的 cycle-exact 延迟；规范只给 pending 状态 eventual 反映保证。

## 单元自检

1. `stimecmp` 什么时候使 STIP pending？无符号 `time >= stimecmp`；比较变化最终反映，时间不保证立即一致。小于为低，等于/大于为高。
2. VS 比较器使用什么时间？64 位截断的 `time + htimedelta`，与 `vstimecmp` 做无符号大于等于比较。
3. 哪些配置控制可访问性？低特权访问受 `mcounteren.TM` 和 `menvcfg.STCE` 限制；VS 还受 `hcounteren.TM` 和 `henvcfg.STCE` 限制，关闭时异常类型依规范区分 illegal-instruction 与 virtual-instruction。
4. 两边中断怎么到 S/VS？pending 接入 mip/hip 等视图，再由 enable、delegation 和当前 privilege/V 决定陷入。源码连线不等于运行观察。
5. 原始 Heliodor 测试尝试通过了吗？没有；当时两条候选命令都被 Veryl testbench check 阻断。Story 6.5 后来通过隔离 harness 运行 S/VS 矩阵，最新结果在下方动态证据表。
6. 原始测试源码覆盖哪些边界？未分别检查 `<`、`==`、`>`，也没有非零 `htimedelta` 或逐层 gate 关闭；Story 6.5 的后续矩阵已补测这些场景，Heliodor gate 行为差异如实记录为 `run-fail`。

## 后续验证

上述后续验证建议已由 Epic 6 / Story 6.5 的隔离 runner 实施；Heliodor 原 testbench 的 Veryl 阻断仍是该旧入口的限制。当前矩阵结果只适用于表列的锁定快照、单 hart 与控制组合，不构成 Sstc 或 RVA23S64 合规结论。


<a id="dynamic-sstc-evidence"></a>

## Story 6.5 动态复验结果（2026-10-14）

以下结果来自该故事新增的 CPU runs，旧的未启动/历史记录保留为历史证据，不覆盖本表。Heliodor SSTC 输入采用 run-id 下不可变 `.hex` 副本；完整输入路径、SHA-256、命令及 stdout/stderr 见 [toolchain manifest](evidence/cpu-validation-toolchain-v1.yaml) 与对应 run archive。Kunminghu 使用同样归档的 `input.S`、PMP NAPOT（`pmpaddr0=-1`, `pmpcfg0=0x1f`）和锁定单核 NEMU difftest。Heliodor SSTC harness 将 `MTIME_EN=1`，内部计数器每 harness cycle 加一，连接到 DUT 的 CSR `time` 为 `mtime_ctr >> 8`；架构预算 300000 clocks，比较器观察使用 bounded poll，不作周期精确断言。

| DUT | Case | Run ID | Result | Actual controls | Observed result | Input SHA-256 |
|---|---|---|---|---|---|---|
| Kunminghu V2 | `s-lt` | `kunminghu-fixture-20261014T084338Z-3e81181d1d02` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=time < stimecmp | sample=0x29; cmp=0x31; after=0x29; relation <; fixture pass marker | `58bc6497bfaeef3acd28066af9cf3c638cbb42a69260fe8e9f0ae15841313881` |
| Heliodor | `s-lt` | `heliodor-core-20261014T084321Z-1266742` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=time < stimecmp; delta=8 | sample=0x1; cmp=0x9; after=0x1; fixture pass marker | `ae8b15401dc1fc4701d765d097f414e1feee6551a90c69c781d7de63a4d9d904` |
| Kunminghu V2 | `s-eq` | `kunminghu-fixture-20261014T084352Z-3e81181d1d02` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=time == stimecmp | sample=0x29; cmp=0x29; after=0x29; relation ==; fixture pass marker | `58bc6497bfaeef3acd28066af9cf3c638cbb42a69260fe8e9f0ae15841313881` |
| Heliodor | `s-eq` | `heliodor-core-20261014T084348Z-1266742` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=one sampled time value == stimecmp | sample=0x1; cmp=0x1; after=0x1; fixture pass marker | `c53adad8fd6aa99dc7a639eba49d8ce2e46cf29b65a0f44400973d1c3df3619b` |
| Kunminghu V2 | `s-gt` | `kunminghu-fixture-20261014T084405Z-3e81181d1d02` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=time > stimecmp | sample=0x29; cmp=0x21; after=0x29; relation >; fixture pass marker | `58bc6497bfaeef3acd28066af9cf3c638cbb42a69260fe8e9f0ae15841313881` |
| Heliodor | `s-gt` | `heliodor-core-20261014T084415Z-1266742` | run-pass | menvcfg.STCE=1; mcounteren.TM=1; relation=time > stimecmp; delta=-8 | sample=0x9; cmp=0x1; after=0x9; fixture pass marker | `3b8c039cb1e29749fc0c1885f02f615129fa5fedc368df6f91cca356c45638f7` |
| Kunminghu V2 | `s-stce-off` | `kunminghu-fixture-20261014T084419Z-3e81181d1d02` | run-pass | menvcfg.STCE=0; mcounteren.TM=1; expected_exception=2 | fixture verified cause=2; pass marker | `58bc6497bfaeef3acd28066af9cf3c638cbb42a69260fe8e9f0ae15841313881` |
| Heliodor | `s-stce-off` | `heliodor-core-20261014T084442Z-1266742` | run-fail | menvcfg.STCE=0; mcounteren.TM=1; expected_cause=2 | no trap; S; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `093f33a1a008a1a0361145bfdd6f6cfa059e17e23b47dc1d362b0a9fae53da62` |
| Kunminghu V2 | `s-tm-off` | `kunminghu-fixture-20261014T084433Z-3e81181d1d02` | run-pass | menvcfg.STCE=1; mcounteren.TM=0; expected_exception=2 | fixture verified cause=2; pass marker | `58bc6497bfaeef3acd28066af9cf3c638cbb42a69260fe8e9f0ae15841313881` |
| Heliodor | `s-tm-off` | `heliodor-core-20261014T084509Z-1266742` | run-fail | menvcfg.STCE=1; mcounteren.TM=0; expected_cause=2 | no trap; S; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `cf8bfed4ceef7b9220b050902cb2c06f34b67da16b0ccdff6500fd2ba830fad8` |
| Heliodor | `vs-lt` | `heliodor-core-20261014T084845Z-1425307` | run-pass | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; relation=guest time < vstimecmp; delta=64 | sample=0x10001; cmp=0x10041; after=0x10001; fixture pass marker | `f9b158df5574a18da83f48c68cd155d1f33c2d197145f944ec39d3cba510e56b` |
| Heliodor | `vs-eq` | `heliodor-core-20261014T084919Z-1440267` | run-pass | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; relation=one sampled guest time == vstimecmp; delta=0 | sample=0x10001; cmp=0x10001; after=0x10001; fixture pass marker | `c62dae14af5f564bdbf30832b8dfdf310b1117bbf18e25e3b453f2d990c149a7` |
| Heliodor | `vs-gt` | `heliodor-core-20261014T084946Z-1455938` | run-pass | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; relation=guest time > vstimecmp; delta=-64 | sample=0x10001; cmp=0xffc1; after=0x10001; fixture pass marker | `43cc196f1392a3e6b2eb93bd6d69e9aa0faee25a07d3c478c7e58dea0de38191` |
| Heliodor | `vs-mstce-off` | `heliodor-core-20261014T085012Z-1467848` | run-fail | menvcfg.STCE=0; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; expected_cause=2 | no trap; VS; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `ad05519a8502a1f1e0c7ea4a513ce1e9f5551c0271a3c7715bf8611912700565` |
| Heliodor | `vs-hstce-off` | `heliodor-core-20261014T085039Z-1479859` | run-fail | menvcfg.STCE=1; henvcfg.STCE=0; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; expected_cause=22 | no trap; VS; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `e5f69ad3863514ac89c154bb173f9375abfa233fd4cd7abe633308b3ffc749d3` |
| Heliodor | `vs-mtm-off` | `heliodor-core-20261014T085106Z-1493174` | run-fail | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=0; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; expected_cause=2 | no trap; VS; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `2ee3d674ac5f0c22ff7c0d3a9e50e3eb30df29c110c195d27c878df69d4fe0fc` |
| Heliodor | `vs-htm-off` | `heliodor-core-20261014T085132Z-1506010` | run-fail | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=0; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; expected_cause=22 | no trap; VS; target_access+4; CSR write completed and fallthrough marker executed; tohost=0x210 | `2365464397cb9a2a6831428528f7f88b2b4f3bce02dde319643db72dd21dadd2` |
| Heliodor | `vs-route` | `heliodor-core-20261014T085159Z-1516435` | run-pass | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=1; hie.VSTIE=0; expected_cause=5 | sample=0x10000; cmp=0x10100; after=0x10000; fixture pass marker | `ab225bcfbf06cabc03ee27160add9c5c978e33e933d1fd9623bd384b8c976781` |
| Heliodor | `vs-hs-route` | `heliodor-core-20261014T085226Z-1526513` | run-pass | menvcfg.STCE=1; henvcfg.STCE=1; mcounteren.TM=1; hcounteren.TM=1; htimedelta=0x10000; hideleg.VSTIP=0; hie.VSTIE=1; expected_cause=6 | sample=0x10000; cmp=0x10100; after=0x10000; fixture pass marker | `2d6559cccc4cb3bea4ca876f7a93a80a67719c0c08281c08735557ed6890a0e1` |

Heliodor 六个 access-gate 用例均为 CPU-started `run-fail`：目标 `stimecmp` 写入后执行了 fallthrough marker `tohost=0x210`，没有产生预期异常（S 模式 cause 2；VS 的 M/H 门分别期望 cause 2/22）。VS 正向比较和路由用例在写入前确认 VSTIP 为低；路由 handler 复位 comparator 后以有界轮询确认 pending 清除。这些结果是实现行为观察，不是环境 blocker。静态核对 `alu_wrap.veryl` 的 CSR checker 只检查 CSR privilege encoding、只读与未实现地址，未检查 Sstc STCE/TM 权限；运行结果与该观察一致。VS 用例分别单独关闭 M STCE、H STCE、M TM、H TM，其他门保持开启。

Kunminghu 的五个 S-mode 案例均在锁定单 hart 配置通过。三种比较边界的 commit trace 记录了实际 `time` 样本和 comparator operand；STCE/TM 关闭案例由 fixture 校验 cause 2 后才写入成功 marker。为让这组 Sstc 探针的算术与提交 trace 清晰，构建使用 `RV64IMA_Zicsr`（禁用 C 扩展）；本结果不覆盖 Kunminghu 的压缩指令行为。

两侧运行均只覆盖表中锁定的单 hart 配置和列出的控制组合。该表不是 Sstc 或 RVA23S64 完整符合性结论。
