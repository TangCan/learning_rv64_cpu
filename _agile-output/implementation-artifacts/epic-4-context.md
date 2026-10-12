# Epic 4 Context: 建立 RVA23 必选项对照图谱

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

建立覆盖 RVA23U64 与 RVA23S64 全部必选要求的学习型对照图谱，使每项规范要求都能对应到 Kunminghu 与 Heliodor 的实现位置、明确的范围决定和可复查证据。成果用于理解与追踪，不代表实现符合性认证。

## Stories

- Story 4.1: 建立官方必选项清单
- Story 4.2: 映射 RVA23U64 基础整数与标量要求
- Story 4.3: 映射 RVA23U64 浮点要求
- Story 4.4: 映射 RVA23U64 的基础向量要求
- Story 4.5: 映射 RVA23U64 的其他向量必选项
- Story 4.6: 映射 RVA23U64 的内存与缓存要求
- Story 4.7: 映射 RVA23S64 的监督模式与陷阱要求
- Story 4.8: 映射 RVA23S64 的地址转换与页表要求
- Story 4.9: 映射 RVA23S64 的 Hypervisor 必选要求
- Story 4.10: 核对 RVA23 必选项映射完整性

## Requirements & Constraints

- 以官方 RVA23 Profile 规范为准，记录采用的版本和 ratification 状态；纳入 RVA23U64 与 RVA23S64 的所有必选要求，包括继承项和规范行为要求，不可只列扩展名称。
- 清单中的每项必须有包含 profile、规范版本和要求标识符的稳定键。明确标注 S64 继承的 U64 项，确保继承项可见且不被重复计算。
- 将必选项、可选项、建议和上游项目自述分开。项目自述或单项测试不能作为完整覆盖的证明。
- 对 Kunminghu 和 Heliodor 分别记录状态、实现位置或范围决定、理由、涉及子案例及证据 ID。状态使用 `not-studied`、`partially-studied`、`studied-unverified`、`evidence-observed`、`not-present` 或 `out-of-scope`；缺少证据不能推断为不存在。
- 证据须区分规范、设计文档、源码、已检查测试、实际运行测试和实验；只有观察到运行结果才能记为运行通过。覆盖子案例不完整时须显式列出未覆盖部分。
- 最终核对每个 profile、每个实现均有明确状态，统计状态并列出未解决项；将结果描述为本项目的学习映射，不宣称官方认证或完整符合性。

## Technical Decisions

- 在 `notes/rva23-coverage.md` 维护按规范要求逐项组织的映射；要求标识符和规范版本作为行级身份，不以扩展名或测试用例合并多项要求。
- 每条对照结论链接到两边实现各自的证据 ID。引用固定来源快照和规范版本，记录稳定源码路径；区分源码检查、测试材料检查和真实执行结果。
- RVA23S64 中继承的 RVA23U64 要求在清单中显式标记继承关系，并仍保持每个强制要求可独立追踪。
- 只记录实现/平台证据能支持的结论。内存区域、PMA、特权状态、地址转换模式、向量参数或虚拟化状态等适用条件须随相关映射注明；局部 RTL 或单一案例不能推广为整体覆盖。

## Cross-Story Dependencies

- Story 4.1 先建立权威必选项清单和映射字段；Stories 4.2–4.9 按要求领域填充这份清单；Story 4.10 再对照官方清单核验遗漏、空状态和证据边界。
- 各领域映射都依赖项目已固定的 Kunminghu、Heliodor 来源快照及统一证据规则。RVA23S64 的监督模式、地址转换和 Hypervisor 映射需要与 U64 基础要求区分，同时保留其继承关系。
