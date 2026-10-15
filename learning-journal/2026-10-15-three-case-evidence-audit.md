# 三类访存案例证据与快照审计（2026-10-15）

## 本次问题

统一核对 `LD`、`SD`、Sv39 非规范 `LD` fault 的六条双核路径、结论到证据的闭合关系、证据 ID/type/status，以及 `sources.lock` 快照与 checkout HEAD。只审计当前索引版本；历史版本保留为历史记录，不混用其局部编号。

## 查阅来源与动作

- 对照 [`sources.lock`](../sources.lock) 和两个只读 checkout：Kunminghu HEAD 为 `c098f996bf4d301b88693b20315486d31e93bc9d`，Heliodor HEAD 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，均与锁定完整 SHA 一致。
- 逐项核查 [LD](../notes/units/load-v2.md#证据表) `LD2-E1`–`LD2-E15`、[SD](../notes/units/store-v1.md#证据表) `SD1-E1`–`SD1-E8`、[fault](../notes/units/sv39-load-fault-v3.md#证据表) `SF1-E1`–`SF1-E12` 及[追踪矩阵](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md)。按 `LD2-E1`–`LD2-E15`、`SD1-E1`–`SD1-E8`、`SF1-E1`–`SF1-E12` 三个活动范围逐项检查定义行，跨三段重复检测未发现重复 ID；源码行号对照锁定 checkout。
- 保留 LD v2、SD v1、fault v1/v2 不变。fault v2 的 C3 将 Heliodor ACT README 一般材料列为比较结论，但 Kunminghu 缺少对应测试材料；发布 [fault v3](../notes/units/sv39-load-fault-v3.md)，明确 C3 为 `partial`，缺侧为 `unverified`，并更新矩阵与索引。

## 发现

| 发现 | 证据类型 | 状态 |
| --- | --- | --- |
| 六条路径均从选定指令/TLB request 起始，追到各自有源码支持的终点，并链接活动证据 ID、源码位置、锁定快照。 | `source` | `inspected` |
| LD 两侧终点是写回及退休条件；SD 两侧终点分别为 Kunminghu uncached request handshake 和 Heliodor committed store-buffer `sb_push`。终点只代表源码条件，不代表本例运行或 DRAM 可见。 | `source` | `inspected` |
| Sv39 两侧静态 fault 到 M-mode trap 逻辑可追踪。 | `source` | `inspected` |
| Heliodor ACT README 含一般标签/修复文字，但不能证明本案例输入或断言；底层测试产物未检查。 | `test-inspected` | `inspected` |
| Kunminghu 对应测试材料是否存在/适用未核实。C3 因此仅是可用测试材料的 `partial` 比较，不能代表本案例覆盖。 | `test-inspected` | `unverified` |
| 六个 LD/SD/fault 动态案例均没有本次运行产物；未声称 `run-pass`、实际运行或硬件观察。LD 命中/退休、SD 接受/可见性、fault cause/CSR/redirect 仍为 `unverified`。 | `test-run` | `unverified` |
| 活动 ID 范围为 `LD2-E1`–`LD2-E15`、`SD1-E1`–`SD1-E8`、`SF1-E1`–`SF1-E12`；逐行检查三段定义，跨段重复检测未发现重复 ID。历史 v1/v2 的局部引用不纳入活动集合。 | `source` | `inspected` |

## 知识沉淀与边界

- 当前索引：[学习单元索引](../notes/units/index.md)；过程导航：[学习日志首页](index.md) 与[学习计划](plan.md)；路径细节见[追踪矩阵](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md)。
- 未运行 CPU 测试、构建或仿真；未修改 `sources.lock` 或任何上游 checkout。没有运行产物可支持动态结论。该审计不扩大为 RVA23 整体符合性结论。
