# 访存案例可行性勘察

日期：2026-10-15
范围：只读检查 `sources.lock` 固定快照与仓库已有学习记录/测试源码；本次未运行测试、构建或仿真。

## 快照边界

两个 checkout 的 HEAD 都与 `sources.lock` 一致：

| 实现 | snapshot_id | 固定 commit | checkout HEAD |
| --- | --- | --- | --- |
| Kunminghu V2 | `xiangshan-kunminghu-v2-20261012` | `c098f996bf4d301b88693b20315486d31e93bc9d` | 匹配 |
| Heliodor | `heliodor-master-20261012` | `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | 匹配 |

## 候选案例结论

| 案例 | 静态路径可追踪性 | 已有测试/运行材料 | 建议 |
| --- | --- | --- | --- |
| 成功标量 `LD` | 两侧都有完整源码路径及退休条件；既有 [`load-v1.md`](../../../notes/units/load-v1.md) 已记录阶段与来源 | Heliodor 有 RV64UI LD 测试入口源码；该学习单元没有运行此案例。缺少本阶段同输入的双核运行证据 | 重用既有 LD 记录作为入口，补充/复核源码，不把静态路径写成动态观察 |
| 成功标量 `SD` | Kunminghu `StoreUnit.scala` 形成地址、TLB 请求并把数据/掩码交给 StoreQueue；`StoreQueue.scala` 将 ROB commit 标记为已提交，之后向下层发送写入。Heliodor decoder/ROB 保存 store 地址和数据，提交时 `commit_store_fire` 驱动写入路径 | Heliodor `tb/test_arch_common.veryl` 有 `test_arch_rv64ui_sd` 的汇编测试入口源码；本次未运行。此次限定检索未找到 Kunminghu 对应的单项 SD 架构测试入口；仓库既有实验可另行复核 | 适合作为静态路径故事；将 store “提交”与“对缓存/存储器可见”分开描述 |
| 共同 fault | 已有 [`sv39-load-fault-v1.md`](../../../notes/units/sv39-load-fault-v1.md) 静态追踪两边 Sv39 非规范 VA 的普通 `LD` load page fault（cause 13）至 ROB/提交 trap 路径 | 两边均未动态观察该非规范 load fault。Heliodor 有 page-fault 汇编源码，但当前案例实际是 store page fault (cause 15)，不覆盖 load fault。已有 Heliodor `test_mmu` 是成功翻译测试，不覆盖该异常 | 选择 Sv39 非规范 `LD` 为共同 fault；明确这是源码可比，动态仍 unverified |

## 分阶段路径锚点

- **Kunminghu load：** [`LoadUnit.scala`](../../../sources/xiangshan/src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala)；既有证据表 E2–E6、E14 位于 `notes/units/load-v1.md`。
- **Heliodor load：** `decoder.veryl`、`heliodor_core.veryl`、`lsu.veryl`；既有证据表 E7–E11、E15 位于 `notes/units/load-v1.md`。
- **Kunminghu store：** [`StoreUnit.scala`](../../../sources/xiangshan/src/main/scala/xiangshan/mem/pipeline/StoreUnit.scala)（S0 地址/TLB/store metadata）、[`StoreQueue.scala`](../../../sources/xiangshan/src/main/scala/xiangshan/mem/lsqueue/StoreQueue.scala)（ROB commit、向下层 drain）。需继续检查 `StoreQueue` 到 DCache/store buffer 的精确连接，避免把 StoreUnit 的早期 tag probe 误作实际写入。
- **Heliodor store：** [`decoder.veryl`](../../../sources/heliodor/src/core/decoder.veryl)、[`rob.veryl`](../../../sources/heliodor/src/core/rob.veryl)、[`heliodor_core.veryl`](../../../sources/heliodor/src/core/heliodor_core.veryl)（`commit_store_fire` 与 store-data/strobe 路径）。标量 bare DRAM fast path、慢速/MMIO 路径条件不同；故事应固定普通 DRAM、对齐 SD，并循实际条件选路。
- **Kunminghu fault：** `cache/mmu/TLB.scala` → `mem/pipeline/LoadUnit.scala` → ROB/CSR，既有 `notes/units/sv39-load-fault-v1.md` E2–E5。
- **Heliodor fault：** `mmu/mmu.veryl` → `mmu/dmem_mmu.veryl` → `core/alu_wrap.veryl` → ROB/CSR trap，既有同记录 E6–E10。

## 规划决策建议

1. 可以用三个学习故事组织这阶段：复核/扩展 LD 路径、建立 SD 提交到写入可见路径、整理共同非规范 Sv39 LD fault；它们共同落到一份双核对照学习记录。
2. fault 案例建议固定为 S-mode、V=0、Sv39、非规范 VA 的普通 `LD`，并在架构路径分析中明确 `medeleg[13]=0` 的 trap 目标假设。现有记录已说明它比 access fault 更容易跨实现追踪；不要求动态故障运行。
3. 暂不需要新建 trace harness：当前成功信号允许静态路径记录，并要求未观察阶段标为 `unverified`。只有后续把真实逐阶段运行观察提升为验收要求时，再单独评估隔离探针。
4. 新阶段必须独立存放 PRD/架构/epics/sprint 文件，不能覆盖原 `_agile-output/planning-artifacts/epics.md` 或旧 sprint 状态。BMM CE 的默认输出位置会碰到旧 epics 文件，拆故事前先为本阶段建立独立规划目录/显式输出边界。

## 勘察边界

这是固定源码快照的路径可行性判断。Heliodor 的 SD 和 LD 测试只确认测试入口源码存在，不代表已执行或通过；Kunminghu 的相同输入运行、缓存实际命中、store 对外可见、非规范 LD fault 运行都未在本次验证。没有搜索测试仓库之外的所有外部验证资源。
