# Stage 3 回顾：访存、原子操作与地址异常

回顾日期：2026-10-15

> 本文根据 Git 历史、故事规格、学习单元、Epic 复盘和后续学习记录事后整理，不是 2026-10-12 当时的连续会话记录。提交记录能定位对应材料进入版本历史的时间，不能还原未记录的探索过程。

## 本次问题

Stage 3 从三类行为观察两颗乱序核心的状态边界：普通 `LD` 如何返回并退休，`AMOADD.D` 如何同时返回旧值并更新内存，Sv39 非规范地址如何形成精确异常。后来增加的 `SD` 对照进一步追踪了 store 提交与写入路径接受之间的边界。本文把原 Epic 3 交付与这项后续扩展分开记录。

## 可追溯的学习过程

- **2026-10-12 15:46 +08:00：普通 load。** `071a7005a904c382080de467d0eedc8f1ea348a5` 加入 `load-v1.md`。案例在 M-mode Bare、自然对齐、无异常、DCache hit、没有更老重叠 store 等前提下，静态追踪 `LD` 从地址生成、TLB/cache 到结果和 ROB 退休路径。
- **2026-10-12 16:04 +08:00：原子读改写。** `1fc59cc46eba869e4e84c272e88e10971fc29621` 加入 `amoadd-d-v1.md`，比较固定快照中 `AMOADD.D` 的读改写路径及旧值返回。Heliodor 测试尝试在测试执行前被 Veryl 编译阶段阻断；这不是目标断言失败，也不是测试通过。
- **2026-10-12 16:15 +08:00：共同 fault。** `0cfb321cfb33a24217c18a5b7b33c04409c2b940` 加入 `sv39-load-fault-v1.md`，追踪 S-mode、Sv39 下非规范 load 地址至 load page fault 和 M-mode trap 的静态路径。
- **2026-10-13：Epic 复盘。** `e3a5474bbe867a83da21b8fb7c8c8ced48f9f1dc` 才提交 Epic 3 回顾文件。判定为 `accepted-with-open-items`：三项学习记录符合已声明范围，但未动态验证目标行为；复盘也记录了启动下一 Epic 前未先完成前一 Epic 回顾的节奏问题，以及 Story 3.3 中过期的待核实文字。复盘文件名中的 10-12 是其所回顾 Epic 的日期，不是回顾文档的提交日期。
- **2026-10-13–14：复盘后续闭环。** `9ef6b5ab25eee00febb76a6b7c5d946f260217bf` 更新复盘行动项；`4394eb9c626c6405a1ae1a354fdd2a79da92ad30` 记录后续核验：后续 Epic 启动门要求前序回顾完成，Story 3.3 规格补足了静态源码证据并保留未动态验证边界。这些后续约束没有改变当时曾跳过复盘门的历史事实。
- **2026-10-15：学习计划中的后续扩展。** `c600d9c6455646e08862bef9c3a16a4f447ae89d` 复核 LD 并形成 `load-v2.md`；`6efb7d5142054232e715437f8c8decc11bdff14c` 新增普通 `SD` 提交与接受边界；`528edce4960c7a86ee382916e6cf189ec8ba4acc` 复核 Sv39 fault 并发布 v3；`2c9de8b4572b2be698b771e8c42fa2f104c584bb` 审计三类案例证据，随后 `a7a7f1ece857523919dd1e80c876c7019886f47d` 完成访存路径综合。这是原项目结项后的独立静态学习扩展；`SD` 不属于 Epic 3 原先三个 Story 的差异范围。

这些时间均为 Git 作者时间（`%aI`，+08:00）；可用完整 SHA 运行 `git show -s --format='%H %aI %s' <完整 SHA>` 复核。三个原始单元和后续复核都引用 `sources.lock` 固定的 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。

## 发现与验证边界

| 主题 | 可支持的结论 | 不能据此声称 |
| --- | --- | --- |
| `LD` | 固定源码中可追踪从地址生成、缓存 hit 数据到写回/退休的路径；后续 LD v2 复核了 Heliodor commit ack 与架构状态更新门控。 | M-mode Bare、hit 等前提没有由本例运行确认；未观察本例实际数据、写回或退休。Heliodor LD/DCache 测试源码未运行，DCache 单测也不等于端到端核心执行。 |
| `SD`（后续扩展） | Kunminghu 在默认 PMA 前提下经 StoreQueue uncached/MMIO 请求握手接受 store；Heliodor 在 ROB 提交端满足 eligibility 条件后由 `sb_push` 接受进入 committed store buffer。两者都只是各自记录所选的接受终点，不等于下游事务或 DRAM 可见。 | 固定 tuple 未动态执行；两侧实际接受、DCache drain 和 DRAM 可见性未验证。详细输入与边界见[SD 单元](../notes/units/store-v1.md)。 |
| `AMOADD.D` | 两侧源码有原子读改写路径；架构结果包含旧值写入 `rd` 和内存更新，不能简化成互不相关的 `LD`/`SD`。 | 不能由静态路径推出竞争交错正确性或实际返回值；Heliodor 测试因编译错误在运行前受阻，Kunminghu 未找到专用测试入口。 |
| Sv39 非规范 `LD` fault | 固定非法 VA 的规范预期是 load page fault（cause 13）；静态源码可追踪异常保留、CSR/trap 与 redirect 路径。v3 将 ACT 测试比较标为 partial。 | 未观测实际 cause、CSR、`mtval` 或 redirect。Heliodor 的两项 MMU 测试通过的是页表遍历 happy path，不是本 fault；ACT 标签不证明该固定 tuple 已运行。 |

Epic 3 的 `accepted-with-open-items` 是对学习交付的验收判断，不表示 CPU 行为通过。其时序复盘问题后来落实为后续启动门；静态研究仍不能替代动态行为验证或 RVA23 符合性证明。

## 知识沉淀

- 原始 Epic 3 单元：[LD v1](../notes/units/load-v1.md)、[AMOADD.D](../notes/units/amoadd-d-v1.md)、[Sv39 fault v1](../notes/units/sv39-load-fault-v1.md)。当前使用的 LD 复核为 [v2](../notes/units/load-v2.md)，fault 审计修订为 [v3](../notes/units/sv39-load-fault-v3.md)；历史版本保留。
- 后续 `SD` 追踪见 [store-v1.md](../notes/units/store-v1.md)；具体访存过程见 [LD 路径复核](2026-10-15-ld-path-review.md)、[SD 接受边界](2026-10-15-sd-commit-write-boundary.md)、[fault 复核](2026-10-15-sv39-noncanonical-ld-fault.md)、[证据审计](2026-10-15-three-case-evidence-audit.md)和[综合日志](2026-10-15-load-store-fault-synthesis.md)。
- [Epic 3 回顾](../_agile-output/implementation-artifacts/epic-3-retro-2026-10-12.md)记录原验收、遗留事项与后续闭环。

## 下一步

日志计划的下一个历史阶段是 Stage 4：建立 RVA23 必选项映射和覆盖边界。回顾时应区分规范要求目录、固定源码检查和符合性结论；既有资料明确不构成整体 RVA23 符合性证明。
