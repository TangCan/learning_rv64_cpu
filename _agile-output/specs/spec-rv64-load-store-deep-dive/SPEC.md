---
id: SPEC-rv64-load-store-deep-dive
companions:
  - trace-matrix.md
  - feasibility.md
  - ../spec-learning_rv64_cpu/learning-record-conventions.md
  - ../../planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/architecture/architecture-rv64-load-store-deep-dive-2026-10-15/ARCHITECTURE-SPINE.md
  - ../../planning-artifacts/prds/prd-rv64-load-store-deep-dive-2026-10-15/prd.md
sources: []
---

# RV64 双核 load/store 微架构深度学习

## Why

已完成的学习项目建立了规范、实现路径和代表性运行证据之间的联系；后续学习需要把同一架构访存行为继续追踪到两个 CPU 各自的微架构阶段。该阶段独立于已结项的 RVA23 学习交付，面向希望理解访存数据流和精确异常边界的学习者。

## Capabilities

- **CAP-1**
  - **intent:** 学习者能够对照 Kunminghu 与 Heliodor 解释标量 load/store 从指令译码到结果提交或异常记录的实现路径。
  - **success:** 学习记录分别追踪两侧成功 load、成功 store 和一个共同架构 fault 案例，覆盖可从证据确认的译码、执行/地址生成、地址转换、访存响应、提交或异常状态；每个阶段引用源码、测试或运行证据，未观察项标为 `blocked` 或 `unverified`。

## Constraints

- 使用 `sources.lock` 中固定的 Kunminghu V2 和 Heliodor 快照；若后续快照改变，先明确比较边界。
- 两侧微架构阶段可以不同；按各自源码命名追踪，不强行建立阶段一一对应。
- 不修改上游 RTL。若现有测试和 trace 无法暴露阶段信息，是否新增隔离学习探针须在故事可行性检查后决定。
- 证据类型与验证状态分别记录；严格区分源码检查、测试源码检查、真实运行观察和未验证结果，沿用学习记录约定中的类型/状态字段。
- 沿用项目学习记录约定，不将本阶段描述为 RVA23 全量行为验证或符合性证明。

## Non-goals

- 穷举所有访存宽度、对齐情况、原子/向量访问、缓存一致性协议或页表组合。
- 性能基准、RTL 改造、SoC 集成、CPU 认证或上游代码修改。
- 预设某个具体 page/access fault 一定能在两个快照中运行。

## Success signal

一份双核学习记录能从同类成功访存和一个共同架构 fault 案例追到各自可证实的实现/观察点，解释两侧路径差异，并将不可观察或未运行的部分明确留为未知。是否运行测试不决定静态路径记录能否完成，但任何运行结论都必须有对应日志和输入证据。

## Assumptions

- 本阶段以源码可追溯比较为核心；现有动态测试或 trace 可用时用于补充，环境阻塞不推断为通过。
- 代表案例由第一项故事通过两侧源码与测试可行性勘察后选定。

## Open Questions

- 本阶段以源码路径追踪为验收，现有动态证据不足的内部阶段标为 `unverified`；若要把逐阶段运行观察提升为验收要求，应另行决定是否新增隔离 trace harness。
- BMM 的 PRD、架构、epics 与 sprint 输出必须落在独立 follow-up 目录；需在创建规划文档前确认不会覆盖原项目结项 artifacts。
