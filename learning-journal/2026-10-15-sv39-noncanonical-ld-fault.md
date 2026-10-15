# Sv39 非规范地址 LD fault：双核静态路径复核

日期：2026-10-15

## 本次问题

固定同一案例，复核 S-mode、V=0、Sv39、RV64I 普通 `LD`、VA `0x0000008000000000`、`medeleg[13]=0` 时，非规范地址如何成为精确 load page fault，并进入 M-mode trap。既有 [`sv39-load-fault-v1.md`](../notes/units/sv39-load-fault-v1.md) 保留为不可变历史版本；本次建立 [`sv39-load-fault-v2.md`](../notes/units/sv39-load-fault-v2.md) 补入固定输入并复核活动路径。

## 探索过程

- 依 `sources.lock` 检查两个 checkout 的 HEAD 与完整 SHA；均与锁定条目一致。源码均只读。
- 按 Privileged Architecture v20260120 §12.4.1 推导 VA：它等于 `1<<39`，bit 38=0、bit 39=1，故 `[63:39]` 不是 bit 38 的 25 位符号扩展。此为输入分类，不是运行结果。
- 复查 Kunminghu TLB `pf39`、LoadUnit 异常向量、ROB precise exception，以及后端 CSR wrapper。发现活动 wrapper 实例化 `NewCSR`，其 `TrapHandleModule` 处理 delegation，`TrapEntryMEvent` 处理 M-mode CSR/target；v1 中旧 CSR 文件导航不代表当前 wrapper 集成，v2 记录了校正而未改 v1。
- 复查 Heliodor `va_noncanonical`、`dmem_mmu`、ALU wrapper、ROB commit 和 CSR 更新。源逻辑显示普通 load fault 的 cause 选择、fault PC/VA 输入与 delegation 条件；没有据此声称实际 CSR 值或 trap redirect 已观测。
- 检查 Heliodor ACT README 的一般 Sv39 `sv39_canonical` 材料及 Makefile pin/运行机制。README 给出的是通用套件历史摘要；没有确认精确 VA、S-mode、LD 与 `medeleg[13]` tuple，因此不当作本案例测试结果。

## 发现

| 发现 | 证据类型 | 状态 | 说明 |
| --- | --- | --- | --- |
| 固定 VA 不满足 Sv39 canonical 条件；规范预期普通 load 触发 cause 13。 | `spec` | `inspected` | 位值静态推导，非 hart 观察。 |
| Kunminghu 路径由 TLB full-VA pre-fault 到 LoadUnit/ROB，再由当前 CSR wrapper 接入 NewCSR。 | `source` | `inspected` | delegation=0 的选择逻辑和 trap event 可静态追踪；未观察执行或寄存器。 |
| Heliodor 路径由 MMU request 检查进入 load fault/VA 保存、ROB commit，再到 CSR trap 选择。 | `source` | `inspected` | 固定条件下源码选择 M-mode；未观察执行或寄存器。 |
| Heliodor ACT 文档提到一般非规范 Sv39 案例，但 tuple 不明。 | `test-inspected` | `inspected` | 不能称作本案例覆盖；本次没有运行 ACT、构建或仿真。 |
| 固定案例的 cause、`PC_LD`、`mepc`、`mtval`、trap target 和时序。 | `test-run` | `unverified` | 本次没有动态案例运行或观察。 |

具体行级证据与源码位置见 v2 的 `SF1-E1`–`SF1-E12` 证据表。

## 知识沉淀

- 当前单元版本：[sv39-load-fault-v2.md](../notes/units/sv39-load-fault-v2.md#单元自检)
- 保留的历史版本：[sv39-load-fault-v1.md](../notes/units/sv39-load-fault-v1.md)
- [固定快照](../sources.lock)：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`
- [追踪矩阵](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md#story-13sv39-非规范-ld-fault)：记录两侧静态终点与动态未知项。

## 下一步

访存案例的双核静态记录已覆盖 `LD`、`SD` 与该 fault。后续综合检查可核对三组路径的证据字段、快照和导航；本记录不启动额外运行验证，也不推断 RVA23 整体符合性。
