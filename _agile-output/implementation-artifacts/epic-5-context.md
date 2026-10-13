# Epic 5 Context: 完成 RVA23S64 双实现深度学习与结项审计

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

在 Epic 4 的 RVA23U64/RVA23S64 必选项图谱基础上，深入比较 Zifencei、Sstc、Sscofpmf、Ssnpm 和 Ssstateen 在 Kunminghu V2 与 Heliodor 中的规范行为、实现路径和验证证据，并审计五个学习单元的证据链。允许结论为已验证、静态证据、未实现、未验证或受阻；明确剩余边界后可判断本项目的学习目标是否完成，但不得据此声称 CPU 符合 RVA23 或获得认证。

## Stories

- Story 5.1: 确认活动实现路径与验证就绪度
- Story 5.2: 比较 Zifencei 与 `FENCE.I`
- Story 5.3: 比较 Sstc 与 S/VS timer
- Story 5.4: 比较 Sscofpmf 计数溢出和模式过滤
- Story 5.5: 比较 Ssnpm 指针屏蔽
- Story 5.6: 比较 Ssstateen 状态访问门控
- Story 5.7: 审计 RVA23S64 覆盖与学习结项证据

## Requirements & Constraints

- 五个主题均须分别对照两边固定源码快照，引用适用规范版本，从架构行为追踪到实现并提供自检答案和证据；具体子案例与验收范围由各故事规格定义。
- RVA23 必选项图谱与五个深度学习单元是不同交付物。深度单元须关联 Epic 4 的精确要求 ID、规范版本和映射状态，不可替代完整图谱，也不可将局部测试或上游声明作为完整符合性证明。
- 区分配置中活动的实现路径、静态源码检查、已检查测试材料和实际运行结果。未运行测试不得记为通过；未知、未实现或受阻项须注明依据、阻塞和证据边界。
- 运行记录应能复现，包含命令、配置、输入/案例、预期与观察结果及产物位置。每个故事计划运行的可运行案例须有结果；无法运行时记录具体原因。
- 学习说明使用中文，扩展名、ISA 符号和源码路径保留上游拼写。学习结项只代表本项目学习范围，不代表 Kunminghu、Heliodor 或本项目获得 RVA23 认证。

## Technical Decisions

- 使用项目 `sources.lock` 中的稳定快照 ID 和完整 commit SHA；偏离锁定快照时说明原因及其对跨单元比较的影响。规划研究记录的基线为 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，实施时仍须以当前锁文件及实际 checkout 核实为准。
- 每个学习单元单独保存版本化记录，包含范围、排除项、规范引用、快照、自检、架构行为及子案例、两边实现路径、比较结论、证据表、总结和未决问题；索引指向当前版本。每项比较结论关联两边证据 ID。
- 证据类型区分规范、设计文档、源码、检查过的测试、运行过的测试和实验；状态区分 `inspected`、`run-pass`、`run-fail`、`unverified`、`not-applicable`。`run-pass` 必须有观察到的运行输出。
- 不在上游源码中直接修改或实验。学习者编写的 harness/实验放在 `experiments/<unit>/`，并记录快照、输入、步骤和观察结果。
- Kunminghu 的源码存在不能证明所选目标启用了该路径；先核对活动 CSR/configuration 路径。Heliodor 的有界源码搜索未找到明确 Ssstateen RTL 路径，搜索结果不能单独证明未实现；须依故事要求检查通用访问路径并界定结论。
- Ssnpm 记录须保留 profile 文档的 `PME` 与指针屏蔽规范/源码的 `PMM` 引用；只有核实后才能说明映射，不能静默统一术语。

## Cross-Story Dependencies

- Epic 5 依赖 Epic 4 完成 RVA23U64/RVA23S64 必选项图谱；五个深度单元须沿用该图谱的要求 ID 与状态。
- Story 5.1 是 Epic 5 的准备门：先核验快照、活动路径、测试入口及工具/用例就绪情况，再按顺序推进 Stories 5.2–5.6。
- Story 5.7 在五个主题单元完成后审计其映射、证据、自检、子案例和检查器结果，并记录剩余限制与学习结项判断。
