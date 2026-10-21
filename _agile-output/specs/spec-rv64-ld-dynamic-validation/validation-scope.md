# 验证范围与可行性门槛

## 已知基线

- 固定快照：Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，均以 `sources.lock` 为准。
- [`load-v2.md`](../../../notes/units/load-v2.md) 已静态追踪 `LD` 地址生成、数据路径和退休条件；其 M-mode Bare、自然对齐、无异常、DCache hit、无更老重叠 store 是场景边界，尚非运行观察。
- [`feasibility.md`](../spec-rv64-load-store-deep-dive/feasibility.md) 记录初始可行性结果；后续同一输入双核运行见本文同一镜像记录与 LD2-E19。

## 最小案例

选择一个普通 RV64I `LD rd, imm(rs1)`，EA 自然 8 字节对齐，读入已知 64 位值，排除异常和更老重叠 store。优先沿用已有测试入口；若该输入不能确保或观察指定值，记录为何不能复用后再选择最小替代。M-mode Bare、DCache hit 只在配置和运行证据能证实时作为结论；否则明确保持未验证。

## 每侧必须记录

| 项目 | 证据要求 |
|---|---|
| 输入 | 测试源或 ELF/hex 的来源、关键指令与寄存器/内存初值；标明同一输入或语义等价输入 |
| 环境 | 固定快照、构建/仿真入口及必要配置 |
| 命令 | 可复现的实际命令和退出状态；未运行时写明原因 |
| 结果 | 预期与实际 `rd` 值、通过断言或等价架构状态观察 |
| 退休 | 退休事件/PC 的实际观察；若接口不提供，记录为不可观察，不能从源码条件推断已退休 |
| 状态 | 按项目证据约定区分源码检查、测试源码检查、实际运行、阻塞和未验证 |

## 决策门槛

- **继续双核动态验证：** 两侧都有可复现入口，能检查预期 `rd` 值，并能观察退休，或已对“无退休可见性”的替代证据取得明确决定；实际运行日志与输入一并保存。
- **调整输入或入口：** 现有测试不覆盖可控已知值，但可用现有工具通过最小输入调整解决；先记录具体改动与理由。
- **停止或暂缓：** 任一侧无安全可复现入口、不能观察关键架构结果，或必须改上游 RTL/构建通用 trace 设施才能推进。列明阻塞证据，不记为通过。
- 不因静态路径完整、测试标签存在或另一个实现通过而推断另一侧运行通过；未实际确认 cache hit 时不得声称 hit。

## 2026-10-16 可行性复核与后续同输入验证

状态：**两侧已在各自锁定环境中运行同一字节镜像并观察目标 LD 结果；cache hit 仍未观察。**

| 实现 | 已有入口与可观察点 | 当前阻塞 / 缺口 |
|---|---|---|
| Heliodor | `experiments/heliodor-smoke/run.py --topic ld-probe` 在临时 harness 副本从现有 retirement debug port 捕获目标 PC、rd 和数据；Veryl 0.22.0 位于 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl`。 | 同一共享镜像已通过；接口不提供本 probe 的 EA 或 cache hit。 |
| Kunminghu V2 | `experiments/kunminghu-smoke/run.py --topic ld` 用 native commit trace 和 linker map 检查提交 PC、指令、EA、rd 和值。 | 同一共享镜像已通过；trace 不暴露 DCache hit。 |

### 初步判断

两边分别构建相同源和 linker，实测输出的 4104-byte raw image 字节完全一致（SHA-256 `f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`）。两次运行均通过；Kunminghu 观察 EA=`0x80000050`，Heliodor 观察 PC=`0x80000008` 恰好退休一次、rd=x6 与预期数据。此结果证明相同程序镜像在各自环境中通过，不证明同步执行或微架构等价。DCache hit 两侧仍未动态观察。

### Kunminghu 先行单条 LD 运行记录

- 命令：`python3 experiments/kunminghu-smoke/run.py --topic ld --timeout 120`
- 结果：`run-pass`；锁定 Kunminghu V2 revision `c098f996bf4d301b88693b20315486d31e93bc9d`；native commit trace 在 `ld_target` 对应 PC `0x80000008` 提交 `ld t1,0(t0)`（`0x0002b303`），由已提交 x5 恢复 EA=`0x80000040`，观察到 x6=`0x123456789abcdef0`，随后 fixture 检查到达 NEMU good trap。
- 输入：历史独立 fixture `experiments/kunminghu-smoke/ld.S`；该源只含一条 LD，没有更老 store；data 地址 8 字节对齐。运行记录将 M-mode/SATP reset 写为选定配置，未独立采样 privilege CSR。
- 归档：`notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T075949Z-3e81181d1d02/`，manifest 记录工具、仿真器/参考库哈希、输入与 trace。
- 限制：native trace 未暴露 DCache hit；不能据此声称 hit。此 fixture 与 Heliodor `rv64ui/ld.hex` suite 不同，不构成双核对照。

### Heliodor suite 运行记录

- 命令：`PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld --timeout 180`
- 结果：`run-pass`，退出码 0；锁定 Heliodor revision `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；`test_smoke` 期望寄存器检查通过，LD 目标报告 `tohost=1/pass=1` 和 `v4 rv64ui-ld PASS`。
- 归档：`notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T055817Z-2342121/`；输入 hex SHA-256 `1c601bb6078882605a72d07e68babdfdea8ef18e3505111cab312b7d603401b4`；完整命令、工具版本和输出哈希见 `notes/units/evidence/cpu-validation-toolchain-v1.yaml` 的对应 run 记录。
- 限制：没有观测单条 LD 的退休 PC、`rd` 值或 cache hit；Kunminghu 运行使用另一份受控 fixture，因此不构成双核等价证据。

### Heliodor 先行单条 LD 退休记录

- 命令：`PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 180`
- 结果：`run-pass`；退出码 0；PC=`0x80000008` 恰好退休一次，`rd_valid=1`、`rd=x6`、数据=`0x123456789abcdef0`，随后自检 `tohost=1/pass=1`。
- 归档：`notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T081240Z-4160381/`；输入由先行 fixture 与固定哈希工具链构建，linker map 确认目标地址。
- 方法边界：只在 runner 创建的临时普通 harness 中增加目标 PC 匹配的 retirement capture；未改动锁定 Heliodor RTL。该 capture 不观测有效地址或 cache hit。

### 同一镜像双核运行记录

- 共享输入：`experiments/rv64-ld-probe/ld.S` 与 `experiments/rv64-ld-probe/fixture.ld`。两侧分别用各自 runner 构建；Kunminghu `fixture.bin` 与 Heliodor `ld-probe.hex` 按 little-endian 32-bit words 解码后均为 4104 bytes，SHA-256 同为 `f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`。
- Kunminghu：`python3 experiments/kunminghu-smoke/run.py --topic ld --timeout 120`；run-pass，目标 PC=`0x80000008`，指令=`0x0002b303`，EA=`0x80000050`，x6=`0x123456789abcdef0`，NEMU GOODTRAP 通过。归档 `notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T101307Z-3e81181d1d02/`。
- Heliodor：`PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 180`；run-pass，目标 PC=`0x80000008` 恰好退休一次，rd=x6、data=`0x123456789abcdef0`，`tohost=1/pass=1`。归档 `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T102111Z-1965619/`。
- 限制：fixture 同一，但两边独立构建和运行；EA 只在 Kunminghu trace 中观察。两侧 DCache hit 均未观察，也未形成同步对照或等价性结论。
