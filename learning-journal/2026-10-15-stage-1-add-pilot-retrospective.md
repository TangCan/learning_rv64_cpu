# Stage 1 回顾：从源码基线到 ADD 双核试点

回顾日期：2026-10-15

> 本文是依据现存 Git 历史、Story 规格、学习单元和复盘整理的事后回顾，不是 2026-10-12 当时的会话记录。没有材料支持的操作顺序和对话不作补写。

## 本次问题

Stage 1 要回答的不只是“ADD 在两颗 CPU 中怎么实现”，也要验证一套学习方法能否把架构行为、两边固定源码和验证证据连在一起。第一个对照选了范围较小的 RV64I `ADD`，并以试点结果决定后续学习阶段的启动顺序。

## 可还原的时间线

- **2026-10-12 12:06：项目起点材料。** `e799110ca8bbf5dcef04b65fdff5d019ed60fdbc` 加入双核 RV64/RVA23 学习指南。该提交建立了学习方向，但不能单独证明 CPU 研究已经开始。
- **14:08：学习计划。** `5d57f1660b57f7e30e7ed9cdcb9983b1d797feae` 加入项目计划；随后 `f061d32db7bdc96de7ccb9d71ac3ef75e5b63482` 在 14:24 建立源码与环境基线。项目锁定 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。Story 1.1 记录了源码位置、测试入口和本机工具条件；Mill、Veryl 等运行依赖不可用，因此没有构建或运行 CPU 测试。
- **14:51–14:54：完成基线并建立记录方法。** `40749e01f45ff594b3509b92dab6545b3036437b` 标记 Story 1.1 完成，`71381ce44ede0e26477e091716de7942572335b5` 加入统一学习记录模板。模板要求固定快照、说明场景与排除项、分别追踪两边路径、关联比较证据，并区分检查过的测试源码和实际运行结果。
- **15:04：ADD 试点交付。** `4a61d6cbd735daeffb7c20c543237d4a74838e4c` 加入 `add-v1.md` 和试点复盘。记录依据 RV64I 规范追踪两侧从译码、运算到整数写回的静态路径，也说明了 `ADDW`、`ADDI` 的边界。Heliodor 测试源码包含 ADD 向量，但无法确认总体断言对应哪个案例；两边测试、构建和仿真均未运行。
- **阶段门：** 试点复盘判定 `ready`，只按顺序授权 Epic 2 的 Stories 2.1–2.2、Epic 3 的 Stories 3.1–3.3、Epic 4 的 Stories 4.1–4.10。该决定是继续学习的阶段门，不是 ADD 的动态验证结果，也没有授权表列范围以外的新史诗；详细决策见[ADD 试点复盘](../notes/units/add-pilot-retrospective.md)。
- **2026-10-13–14：后续修订与确认。** `e3a5474bbe867a83da21b8fb7c8c8ced48f9f1dc` 完成各 Epic 回顾，`9ef6b5ab25eee00febb76a6b7c5d946f260217bf` 关闭回顾行动项。Epic 1 回顾在 10 月 14 日记录了 ADD 自检答案的 Heliodor 写回证据、版本化 RV64I 链接、测试源码与运行结果的区分，以及失败 SHA 检查的复现步骤，见 [Epic 1 retrospective follow-through](../_agile-output/implementation-artifacts/epic-1-retro-2026-10-12.md)。这些是后续归档修订，不应误写成试点当天已完成的工作。

上述时间来自项目 Git 提交时间。可复制任一上列完整 SHA 运行 `git show -s --format='%H %aI %s' <完整 SHA>` 复核；技术细节以链接的原始记录为准。

## 发现

| 发现 | 证据类型 | 状态 | 边界 |
| --- | --- | --- | --- |
| 规范定义 `ADD` 对 XLEN 位寄存器求和并忽略溢出；本例 XLEN=64。两份固定源码都能静态追踪到整数写回路径。 | `spec` + `source` | `inspected` | 这是规范与源码检查，不是运行观察。 |
| 两种设计的实现组织不同：Kunminghu 分层连接加法器、结果选择和写回；Heliodor 由 ALU wrapper/CDB 传到整数 PRF。 | `source` | `inspected` | 不据此推断性能或完整 ISA 符合性。 |
| 测试入口和测试源码不能证明本例已通过。Kunminghu 的定向测试没有 ADD 断言；Heliodor 的测试断言与 ADD 向量对应关系不明。 | `test-inspected` | `inspected` | 两边 ADD 行为的实际执行结果仍为 `test-run` / `unverified`。 |

试点的价值在于验证了“规范行为 → 双边源码路径 → 有界测试证据 → 未解问题”的记录结构。它也暴露出需要明确记录证据类型、状态和测试断言覆盖范围，避免将测试源码误写成运行结果。

## 知识沉淀

- 技术路径、自检答案和未覆盖边界见 [ADD 双核学习单元](../notes/units/add-v1.md)。
- 模板复用经验、试点缺口与 `ready` 阶段门见 [ADD 试点复盘](../notes/units/add-pilot-retrospective.md)。
- 快照、主机条件和未运行的工具入口见[源码与环境基线](../notes/source-environment-baseline.md)及 [`sources.lock`](../sources.lock)。
- Story 规格：[基线](../_agile-output/implementation-artifacts/spec-1-1-establish-source-and-environment-baseline.md)、[记录模板](../_agile-output/implementation-artifacts/spec-1-2-establish-learning-record-template.md)、[ADD 试点](../_agile-output/implementation-artifacts/spec-1-3-add-dual-core-pilot.md)。

## 下一步

既定阶段门授权按顺序学习乱序依赖与分支恢复。学习日志计划的下一篇历史回顾是 Stage 2；应继续以现有记录还原，不补造不可追溯的过程。
