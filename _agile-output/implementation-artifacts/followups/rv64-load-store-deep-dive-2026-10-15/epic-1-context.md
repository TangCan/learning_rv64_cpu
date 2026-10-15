# Epic 1 Context: 完成可回顾、可复查的双核访存学习阶段

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

建立可按时间回顾的学习日志，并完成 Kunminghu V2 与 Heliodor 的标量 `LD`、`SD` 和 Sv39 非规范地址 fault 对照。每项技术结论都应能追溯到固定源码快照、测试材料或运行产物，并明确证据覆盖范围；无法确认的阶段和历史信息保留为未知。本规划目录未包含独立 PRD、架构、产品简报或学习计划文件，以下约束依据 epics 与现有 SD 决策记录整理。

## Stories

- Story 1.1: 复核并记录双核 `LD` 路径
- Story 1.2: 追踪普通 DRAM `SD` 的提交与写入边界
- Story 1.3: 追踪 Sv39 非规范地址 `LD` fault
- Story 1.4: 核验三类案例的证据与快照
- Story 1.5: 综合双核发现并完成学习日志导航

## Requirements & Constraints

- `LD` 两侧采用相同场景：自然对齐 8 字节访问、M-mode Bare、无异常、DCache hit、无更老重叠 store。追踪译码/发射至地址生成、转换、缓存响应、写回和退休；假设和未确认阶段要明确标注。
- `SD` 两侧采用同一自然对齐普通 DRAM 场景，并说明指令提交、缓存/缓冲接受和更低层可见性之间的区别。不得仅凭 commit、StoreQueue drain 或早期 tag probe 推断 DRAM 可见或持久。
- fault 案例固定为 S-mode、V=0、Sv39、RV64I `LD`、VA `0x0000008000000000`、`medeleg[13]=0`。追踪检测、异常保留、cause 13、故障 PC/`mepc`、`mtval`、M-mode trap target 及有证据支持的状态更新。
- 比较结论须有两侧证据；缺侧时明确标记 `partial`，并将缺失部分标为 `unverified`、`blocked` 或 `unknown`。证据 `type` 与验证 `status` 分列；源码检查或测试条目不代表实际运行。
- 运行结论需保留精确输入、命令、配置、输出和产物路径。源码证据须使用 `sources.lock` 中的稳定 snapshot ID 与完整 SHA；快照不匹配的证据不计入验收，基线变化后重查受影响结论。
- 已发布学习单元保持不可变；修订创建新版本并更新单元索引。日志记录日期、问题、来源/动作、带证据类型和状态的发现、学习单元/证据链接及下一步。不得补写无法还原的历史细节。
- 不要求动态运行或新增 trace harness；不修改上游 RTL，不作 RVA23 一致性声明。中文 Markdown 通过本地 Git/GitHub 阅读，不引入博客服务或生成器。

## Technical Decisions

- 技术结论归 `notes/units/`，探索时间线归 `learning-journal/`，原始运行产物归 `notes/units/evidence/`。
- 两个实现按各自源码阶段名称描述；只比较等价架构场景，不强行对齐微架构阶段。
- 追踪矩阵覆盖 LD、SD、fault 在两核上的六条路径行。每行记录起点、证据支持的终点、证据引用，或明确标出 `unknown`/`blocked`。
- SD 共同 tuple 为 `SD x11, 0(x10)`，`x10=0x80004000`、`x11=0x1122334455667788`、M-mode Bare、8 字节对齐；这些输入和配置属于 assumption/unverified，非运行观察。Kunminghu 终点为 uncached/MMIO request handshake；Heliodor 终点为 eligible store 进入 committed store buffer (`sb_push`)。两个终点时序不同，均不证明 DRAM 可见或持久。

## Cross-Story Dependencies

- Story 1.2 的 SD tuple 与接受终点由其决策记录固定，路径记录应遵循该边界。
- Story 1.4 核验 Story 1.1–1.3 建立的六条路径、证据字段和快照一致性；Story 1.5 汇总三类案例并完成日志索引/README 导航，依赖前述学习单元、日志和追踪矩阵。
