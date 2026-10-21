# 项目最终交付

## 交付定义

本项目交付的是一套可复习、可追溯的 RV64 CPU 双实现学习档案：以固定版本的 Kunminghu V2 与 Heliodor 为参照，从 RISC-V 架构要求追踪到源码路径和验证证据，并明确哪些结论来自静态检查、哪些来自实际运行、哪些仍失败或未验证。

它不是一颗新的 CPU，也不是对 Kunminghu 或 Heliodor 的产品化修复，更不表示 RVA23 符合性或认证。

## 交付内容

- [学习计划与历程索引](../learning-journal/index.md)：六阶段学习回顾，以及 LD、SD、Sv39 fault 的后续静态学习路径。
- [学习单元索引](../notes/units/index.md)：架构行为、两侧源码路径、比较结论、自检答案和证据状态。
- [RVA23 必选项映射](../notes/rva23-coverage.md)及[完整性审计](../notes/units/rva23-mandatory-coverage-audit-v1.md)：列出两侧已研究、部分研究、未验证或未调查的范围。
- [RVA23S64 结项审计](../notes/units/rva23s64-closeout-audit-v1.md)：覆盖 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen 五个深度主题，并保留运行失败、阻塞与未验证边界。
- [`sources.lock`](../sources.lock)：记录学习结论所依据的上游源码快照。
- [验证证据索引](../notes/units/evidence/README.md)：说明保留的运行记录、hash 和仓库外原始日志归档。

## 已结束的独立试点

- **Bitloom RV64 pilot**：完成有界 RV64I、同步 LD/SD 和受限向量试点后停止；结果不扩展为完整核心实现或目标 PPA 结论。见 [试点记录](../experiments/bitloom-rv64-pilot/README.md)。
- **LD 动态观察**：Kunminghu 与 Heliodor 的受控 LD 运行已留下对应证据；每项观察仅支持记录中的输入、快照和观察点，不代表两核微架构等价。见 [LD 学习记录](../notes/units/load-v2.md)。
- **PMP access-span 隔离修复**：是从 LD/PTE 边界现象延伸出的独立验证/实现工作，位于 `sources/heliodor` 下的独立 linked worktree，不属于顶层学习档案的核心交付，也不因其定向用例通过而声称覆盖所有 PMP 路径。

## 结项边界

原学习范围已完成结项审计。今后只有在出现一个能对应到学习目标的明确问题、验收标准和证据边界时，才启动新的专题；继续添加测试或归档运行日志本身不构成项目目标。任何重新开始的 RTL 修复、工具链开发或 profile 验证都应作为单独计划，并说明它与本学习档案的关系。

本项目记录了实际运行失败和未验证项，不把源码存在、测试文件存在或 checker 成功表述为 CPU 行为通过。想复查所有已移出的原始日志和每次运行源码快照，可按[证据索引](../notes/units/evidence/README.md)中的外部归档说明恢复。
