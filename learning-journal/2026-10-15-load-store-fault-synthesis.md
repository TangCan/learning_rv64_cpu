# 双核 LD、SD 与 Sv39 fault 综合（2026-10-15）

## 本次问题

在完成 `LD`、普通 `SD` 和 Sv39 非规范地址 `LD` fault 的双核静态追踪后，综合两种实现如何满足共同架构目标、各自的微架构路径在哪里分叉，以及现有证据能支持到哪里。本篇依据已有学习记录与当前活动单元回顾，不重写路径细节，也不补造早期探索过程。

## 查阅来源与动作

- 对照 [sources.lock](../sources.lock)、[追踪矩阵](../_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md) 和当前单元：[load-v2](../notes/units/load-v2.md)、[store-v1](../notes/units/store-v1.md)、[sv39-load-fault-v3](../notes/units/sv39-load-fault-v3.md)。矩阵及单元固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；既有审计记录其 checkout HEAD 与锁定 SHA 一致。
- 对照此前过程记录：[LD 复核](2026-10-15-ld-path-review.md)、[SD 边界追踪](2026-10-15-sd-commit-write-boundary.md)、[Sv39 fault 复核](2026-10-15-sv39-noncanonical-ld-fault.md) 和[证据审计](2026-10-15-three-case-evidence-audit.md)。本次未运行 CPU 测试、构建或仿真。

## 综合发现

| 主题 | 双核比较 | 证据类型 | 验证状态 |
| --- | --- | --- | --- |
| `LD` 架构目标 | 共同案例限定为自然对齐 8-byte access、M-mode Bare、无异常、DCache hit、无更老重叠 store（[load-v2 案例边界](../notes/units/load-v2.md#架构行为与子案例)）；这些是未由运行确认的 assumptions。RV64I `LD` 将有效地址处的 64 位值写入目标寄存器，并在无异常时按序退休。Kunminghu 从整数 load issue 经 DTLB 返回 PA、DCache load pipe 和 backend 写回；Heliodor 从 decoder/AGU 经 MMU Bare passthrough、LSU/DCache、CDB/PRF 与 ROB。两边 hit 数据写回的源码证据分别为 `LD2-E4`–`LD2-E6` / `LD2-E10`–`LD2-E11`；退休条件及架构状态门控分别为 Kunminghu `LD2-E14`、Heliodor `LD2-E15`。 | `source`；另有 `spec` 支持架构语义 | `inspected`；场景前提、实际 hit、数据值与退休 `unverified` |
| `SD` 架构目标与接受边界 | 共同 tuple 为 [`store-v1` 所列案例](../notes/units/store-v1.md#架构行为与子案例)：`SD x11, 0(x10)`、`x10=0x80004000`、`x11=0x1122334455667788`、M-mode Bare、8-byte aligned；寄存器值与运行配置是 assumption，实际执行 `unverified`。两侧接受路径不同：Kunminghu 默认 PMA `c=false` 的分类见 `SD1-E3`，其 StoreQueue uncached/MMIO request handshake 终点见 `SD1-E4`；Heliodor 对该地址的 DRAM 分类见 `SD1-E7`，eligible store 进入 committed store buffer 的 `sb_push` 见 `SD1-E6`、`SD1-E8`。默认配置是否实际使用仍未验证。ROB 提交、请求/缓冲接受、后续 DCache drain 和 DRAM 可见性是不同边界。 | `source` | 静态检查 `inspected`；tuple、配置应用、commit、handshake、push 与下层可见性均未运行验证；DRAM 可见性 `unknown` |
| Sv39 非规范 `LD` fault | 固定 VA `0x0000008000000000` 的非规范性由位值静态推导。Kunminghu TLB 检查后，fault 身份经 LoadUnit 和 ROB 保留为精确异常，head exception 接入当前 NewCSR 路径（`SF1-E3`–`SF1-E6`）；Heliodor 的 MMU fault/VA 经 ROB 保存并在 head commit 时选择异常（`SF1-E7`–`SF1-E9`）。该 fault 不作为正常 `LD` 结果退休，而是在精确异常路径到达 head 后进入 trap 处理。给定 S-mode、V=0、Sv39、`medeleg[13]=0`，规范和源码逻辑支持 load page fault cause 13 与 M-mode trap 选择（Kunminghu `SF1-E6`；Heliodor `SF1-E9`–`SF1-E10`）。 | `spec` + `source`；测试材料比较 `partial` (`test-inspected`) | 静态检查为 `inspected`；动态 fault、PC、CSR 值及 redirect `unverified`。Heliodor ACT README 标签不证明本 tuple 的输入/断言，Kunminghu 对应测试材料 `unverified`。 |

各比较的证据 ID 已随关键断言标出：LD 写回/退休分别见表内的 `LD2-E4`–`LD2-E6` / `LD2-E10`–`LD2-E11` 与 `LD2-E14` / `LD2-E15`；SD Kunminghu PMA 分类与请求接受分别为 `SD1-E3` / `SD1-E4`，Heliodor DRAM 分类与 buffer 接受为 `SD1-E7` / `SD1-E6`、`SD1-E8`；fault 精确异常保留与 cause/delegation 选择见 `SF1-E5`–`SF1-E6`、`SF1-E8`–`SF1-E10`。fault 规范输入及位值见 `SF1-E1`–`SF1-E2`，测试材料及动态状态边界见 `SF1-E11`–`SF1-E12`。各 ID 的源码位置、固定 SHA、类型和状态见对应单元证据表及追踪矩阵。

## 知识沉淀与历史边界

本次访存阶段的静态学习交付已包括三份活动单元、四篇过程记录和六条矩阵路径；这不表示三个案例已实际运行。旧学习路线列出的六阶段历史仅按现有单元、复盘和运行材料建立索引。尚无文章的阶段继续标为待依据材料回顾，不能从当前访存追踪反推旧阶段的对话或时间线。

## 下一步

按[学习计划](plan.md)先选有现存材料支撑的一项旧阶段，撰写注明“基于现有记录回顾”的日志；若转向新技术主题，则先定义问题和所需证据。需要运行结论时，另行固定输入、配置、命令与产物，再更新相应单元；在此之前 LD 命中/退休、SD 接受与 DRAM 可见性、fault 运行结果都保持未验证。本总结不作 RVA23 整体符合性判断。
