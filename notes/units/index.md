# 学习单元索引

本索引指向每个学习单元当前的不可变版本文件。新修订应新建 `<unit_id>-vN.md`，完成检查后再更新对应行；不要覆盖已有版本。来源快照 ID 必须引用 `sources.lock` 中的条目。阶段自检答案保存在单元记录内，阶段路线记录可索引答案但不能代替答案本身。

| unit_id | stage_id | 学习单元 | 当前版本文件（`<unit_id>-vN.md`） | 状态 |
| --- | --- | --- | --- | --- |
| `add` | 阶段 1 | RV64I `ADD` 双核对照 | [`notes/units/add-v1.md`](add-v1.md) | 试点完成 |
| `dependency` | 阶段 2 | RV64I `ADDI` RAW 依赖双核对照 | [`notes/units/dependency-v1.md`](dependency-v1.md) | 单元记录完成；未运行验证 |
| `branch-recovery` | 阶段 2 | 条件分支错预测冲刷与恢复双核对照 | [`notes/units/branch-recovery-v1.md`](branch-recovery-v1.md) | 单元记录完成；未运行验证 |
| `load` | 阶段 3 | RV64I `LD` 普通访存路径双核对照 | [`notes/units/load-v1.md`](load-v1.md) | 单元记录完成；未运行验证 |
| `amoadd-d` | 阶段 3 | RV64A `AMOADD.D` 原子读改写双核对照 | [`notes/units/amoadd-d-v1.md`](amoadd-d-v1.md) | 单元记录完成；测试被工具链阻止，动态行为未验证 |
| `sv39-load-fault` | 阶段 3 | Sv39 非规范 `LD` page fault 与 M-mode trap 双核对照 | [`notes/units/sv39-load-fault-v1.md`](sv39-load-fault-v1.md) | 单元记录完成；源码已检查，动态行为未验证 |
| `rva23u64-scalar` | Epic 4 / Story 4.2 | RVA23U64 基础整数与标量要求双核映射 | [`rva23u64-scalar-v1.md`](rva23u64-scalar-v1.md) | 单元记录完成；本次仅静态源码/测试材料检查，未运行测试 |

RVA23 必选项覆盖目录（Epic 4）：[`notes/rva23-coverage.md`](../rva23-coverage.md)。Story 4.2 已填基础整数与标量映射，其余领域由后续故事调查。
