# 学习记录与证据约定

## 学习单元记录

每个单元一个不可变 Markdown 版本，文件名为 `<unit_id>-vN.md`；索引指向当前版本。模板 frontmatter 包含 `unit_id`、`stage_id`、范围、排除项、规范引用和源码快照 ID。章节顺序：单元自检问题/答案/检查类型/证据 ID、架构行为及子案例、Kunminghu 路径、Heliodor 路径、比较结论、证据表、学习者总结、未解问题。参数化行为（如宽度、掩码、异常和特权模式）要列出子案例和未覆盖项。

## 源码快照

项目级 `sources.lock` 为 Kunminghu 和 Heliodor 的完整 commit SHA 分配稳定 ID。每份记录引用锁中的 ID。改变锁时留下带日期的快照变更记录；有意偏离基线时说明理由，并标明跨单元结论不能直接比较。工作区 checkout 位置可在确认仓库规模和主机资源后选择；如使用项目内目录，`sources/` 必须在 Git 中忽略。

## 证据表

每项证据含稳定 ID、支持的结论 ID、类型、仓库/快照、源码或材料位置。类型：`spec`、`design-doc`、`source`、`test-inspected`、`test-run`、`experiment`。状态：`inspected`、`run-pass`、`run-fail`、`unverified`、`not-applicable`。运行记录包含精确命令、配置、输入/案例、预期结果、观察结果和产物位置；只有观察到实际输出才能标记 `run-pass`。检查测试不代表执行测试。比较结论必须有两边的证据 ID。

## 阶段检查与实验边界

单元记录拥有自己的自检问题和答案；阶段路线索引这些答案并记录阶段完成。实验仅在需要时创建，放在 `experiments/<unit>/`，记录源码快照、输入、步骤和观察结果，不修改或复制上游源文件。
