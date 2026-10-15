# 双核 LD 路径复核（2026-10-15）

## 本次问题

`load-v1.md` 将 Heliodor architectural RAT 与 `arch_regs` 调试镜像的更新概括到同一提交描述中。本次复核固定 Kunminghu V2 与 Heliodor 快照，区分二者门控，并确认 LD 路径与证据边界。

## 查阅来源与动作

- 对照 [`sources.lock`](../sources.lock)，检查 `sources/xiangshan` 与 `sources/heliodor` 的 HEAD；两者分别匹配锁定 SHA `c098f996bf4d301b88693b20315486d31e93bc9d` 和 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- 复核 Kunminghu `LoadUnit.scala`、`LoadPipe.scala`、`Rob.scala`、`RenameTable.scala`，以及 Heliodor decoder、core、LSU、DCache、MMU、ROB、RAT 源码；具体位置与逐项证据见 [load-v2](../notes/units/load-v2.md#证据表)。
- 检查 load-v1、学习记录约定及现有访存追踪矩阵；没有运行 LD 测试或仿真。

## 发现

| 发现 | 证据类型 | 状态 |
| --- | --- | --- |
| 两个快照源码都能静态追踪 LD 地址形成、转换/直通、DCache hit 数据路径、结果写回和 ROB 退休条件。 | `source` | `inspected` |
| Heliodor architectural RAT `rat_arch` 更新受 `rob_commit_ack` 经 `rat_commit_en` 门控；`arch_regs` 调试/cosim 镜像独立受 `rob_commit_valid` 门控。 | `source` | `inspected` |
| M-mode Bare、自然对齐、无异常、DCache hit、无更老重叠 store 是共同案例假设；源码未固定本次案例配置。 | `source` | `inspected` |
| 本次未运行 LD 案例，实际命中、结果值及退休均未观察。 | `experiment` | `unverified` |

## 知识沉淀与证据

- 新版 [load-v2](../notes/units/load-v2.md) 保留 v1 基线并使用唯一 evidence ID `LD2-E1`–`LD2-E15`；版本索引见[学习单元索引](../notes/units/index.md)。
- [追踪矩阵](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md)增加两核 LD 行，分列 `type` 与 `status`。
- [load-v1](../notes/units/load-v1.md) 未修改。源码证据仅为 `source` + `inspected`；案例运行状态为 `unverified`。

## 下一步

按计划继续普通 DRAM `SD` 路径；LD 的实际命中、结果值和退休仍需单独运行证据才能验证。
