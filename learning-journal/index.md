# RV64 CPU 学习日志

这里按时间记录学习问题如何提出、如何查证，以及结论如何沉淀成可复习的知识单元。日志讲学习过程；技术细节和证据仍以链接的 `notes/units/` 记录及证据文件为准。

- [学习计划](plan.md)：既有学习历程归档和后续访存微架构学习路线。
- [学习单元索引](../notes/units/index.md)：已整理的主题知识记录。
- [记录与证据约定](../_agile-output/specs/spec-learning_rv64_cpu/learning-record-conventions.md)：快照、证据类型和运行记录规则。

## 已完成学习历程（待整理为日志文章）

以下时间线先根据已有学习记录和规划整理；日志文章尚未撰写，不补造当时的对话或过程细节。

| 顺序 | 学习阶段 | 已有知识记录 | 日志状态 |
| --- | --- | --- | --- |
| 1 | 建立双核源码基线与学习记录方法，以 `ADD` 作为试点 | [`add-v1.md`](../notes/units/add-v1.md)、[`add-pilot-retrospective.md`](../notes/units/add-pilot-retrospective.md) | 待根据现有记录回顾 |
| 2 | 学习乱序依赖和分支错预测恢复 | [`dependency-v1.md`](../notes/units/dependency-v1.md)、[`branch-recovery-v1.md`](../notes/units/branch-recovery-v1.md) | 待根据现有记录回顾 |
| 3 | 比较普通访存、原子操作和地址异常 | [`load-v2.md`](../notes/units/load-v2.md)、[`store-v1.md`](../notes/units/store-v1.md)、[`amoadd-d-v1.md`](../notes/units/amoadd-d-v1.md)、[`sv39-load-fault-v2.md`](../notes/units/sv39-load-fault-v2.md)（历史版 [`v1`](../notes/units/sv39-load-fault-v1.md)） | 静态记录已完成；各案例运行边界见单元记录 |
| 4 | 建立 RVA23 必选项映射和覆盖边界 | [`rva23-mandatory-coverage-audit-v1.md`](../notes/units/rva23-mandatory-coverage-audit-v1.md) 及 RVA23 专题记录 | 待根据现有记录回顾 |
| 5 | 深入比较 RVA23S64 专题与学习交付证据 | [`rva23s64-closeout-audit-v1.md`](../notes/units/rva23s64-closeout-audit-v1.md) | 待根据现有记录回顾 |
| 6 | 增加固定快照上的代表性 CPU 运行验证 | 各 RVA23S64 专题记录及 `notes/units/evidence/` | 待根据运行证据回顾 |

## 后续学习

| 状态 | 主题 | 过程日志 | 知识记录 |
| --- | --- | --- | --- |
| 已完成前置勘察 | Kunminghu 与 Heliodor 的 load/store/fault 案例可行性 | [访存案例可行性勘察](../_agile-output/specs/spec-rv64-load-store-deep-dive/feasibility.md) | [后续阶段 Spec](../_agile-output/specs/spec-rv64-load-store-deep-dive/SPEC.md) |
| 已完成本次复核 | `LD` 微架构路径复习与补充 | [双核 LD 路径复核](2026-10-15-ld-path-review.md) | [`load-v2.md`](../notes/units/load-v2.md)；基线 [`load-v1.md`](../notes/units/load-v1.md) 保留 |
| 已完成本次静态追踪 | `SD` 从派发到提交及写入接受边界 | [双核 SD 提交与写入边界](2026-10-15-sd-commit-write-boundary.md) | [`store-v1.md`](../notes/units/store-v1.md)；DRAM 可见性未验证 |
| 已完成静态复核 | Sv39 非规范 `LD` fault 双核路径 | [Sv39 非规范地址 LD fault](2026-10-15-sv39-noncanonical-ld-fault.md) | [`sv39-load-fault-v2.md`](../notes/units/sv39-load-fault-v2.md)；[历史版 v1](../notes/units/sv39-load-fault-v1.md) 保留；固定案例动态行为未验证 |
| 计划中 | 双核访存路径综合比较 | 待写 | 后续对照记录待定 |

新日志按 `YYYY-MM-DD-主题.md` 命名，并从本页按时间顺序添加。先写已有证据支持的回顾；如果历史材料不能还原过程，就明确写“基于现有记录回顾”，不虚构当时的探索细节。
