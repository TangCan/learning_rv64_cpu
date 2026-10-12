# 学习单元索引

本索引指向每个学习单元当前的不可变版本文件。新修订应新建 `<unit_id>-vN.md`，完成检查后再更新对应行；不要覆盖已有版本。来源快照 ID 必须引用 `sources.lock` 中的条目。阶段自检答案保存在单元记录内，阶段路线记录可索引答案但不能代替答案本身。

| unit_id | stage_id | 学习单元 | 当前版本文件（`<unit_id>-vN.md`） | 状态 |
| --- | --- | --- | --- | --- |
| `add` | 阶段 1 | RV64I `ADD` 双核对照 | [`notes/units/add-v1.md`](add-v1.md) | 试点完成 |
| `dependency` | 阶段 2 | RV64I `ADDI` RAW 依赖双核对照 | [`notes/units/dependency-v1.md`](dependency-v1.md) | 单元记录完成；未运行验证 |
| `branch-recovery` | 阶段 2 | 条件分支错预测冲刷与恢复双核对照 | [`notes/units/branch-recovery-v1.md`](branch-recovery-v1.md) | 单元记录完成；未运行验证 |
