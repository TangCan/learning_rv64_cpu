---
title: 'Story 4.1: 建立官方 RVA23 必选项清单'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '0cfb321cfb33a24217c18a5b7b33c04409c2b940'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/planning-artifacts/epics.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 项目尚无权威、可逐项追踪的 RVA23U64 与 RVA23S64 强制要求目录，后续双核映射可能遗漏继承要求或将可选项误列为强制项。

**Approach:** 以 RISC-V International ratified RVA23 Profile v1.0 为规范基线，在 `notes/rva23-coverage.md` 建立完整的学习清单，记录要求的稳定身份、规范内容、继承关系、分类及后续双实现映射所需字段。

## Boundaries & Constraints

**Always:** 纳入 U64 与 S64 mandatory base、mandatory extensions 及 profile 明确规定的行为条件；将 S64 继承的 U64 要求显式列出并关联其规范行；将 mandatory、localized/development/expansion/transitory options、recommendations、profile notes 和上游自述分开；记录 profile 版本及 ratification 状态；逐行给出 profile、版本和规范要求标识符；为 Kunminghu 与 Heliodor 分别预留状态、实现位置或范围决定、理由、子案例和证据 ID 字段；状态只用 `not-studied`、`partially-studied`、`studied-unverified`、`evidence-observed`、`not-present`、`out-of-scope`。

**Never:** 不把未调查解释为不存在；不以项目声明或单项测试证明符合性；不宣称认证或完整符合性；不在本故事填充实现覆盖结论或改动上游源码。

</frozen-after-approval>

## Code Map

- 官方基线：[RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)，分别列出 U64/S64 mandatory base、mandatory/unprivileged/privileged requirements、继承关系、选项及建议。其逐项扩展定义可链接到独立 ISA 规范；本清单记录 profile 要求及其限制条件，不复制扩展手册全文。
- `_agile-output/implementation-artifacts/epic-4-context.md` 与 `_agile-output/planning-artifacts/epics.md`：固定后续映射字段和 Story 4.2–4.10 的领域边界。
- `_agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md`：AD-2/AD-4 证据分类及按规范要求逐项映射约束。
- `sources.lock`：两侧固定快照标识；本故事仅建立目录，不据此推断任何实现状态。
- 新建 `notes/rva23-coverage.md`；复用 `notes/units/index.md` 的文档索引惯例（如需索引，保持其只引用稳定路径）。不修改上游源码或既有学习单元。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 建立版本化要求目录、清晰分类、稳定键、U64/S64 继承关联、双实现映射字段和证据规则。
- [x] `notes/units/index.md` — 若该索引承载项目学习资产入口，则添加覆盖图谱链接。

**Acceptance Criteria:**
- Given 官方 ratified RVA23 Profile v1.0，when 清单建立，then 包含 U64 与 S64 的 mandatory base、所有 mandatory unprivileged/privileged requirement 和 profile 规定的行为条件，并记录版本与 ratification 状态。
- Given S64 继承 U64 强制项，when 清单呈现继承，then 每个继承项可见、可追溯到 U64 原始稳定键，汇总时不会被当成两项不同规范要求重复计数。
- Given profile 列出的强制项、不同类型可选项、建议和说明，when 清单分类，then 分类彼此可辨，强制项记录规范行为与适用条件而非仅列扩展名。
- Given 后续需要比较 Kunminghu 与 Heliodor，when 查看任一强制项，then 两个实现各自有独立字段记录状态、位置或范围决定、理由、子案例及证据 ID；缺证据不等于 `not-present`。
- Given 清单中的来源声明，when 描述实现或验证，then 区分规范、文档、源码、测试检查、实际运行与上游自述，不将学习映射表述成认证结论。

## Implementation Notes

官方资料将 RVA23 Profile 标为 v1.0；该 profile 已 ratified。清单采用官方 profile 小节及 requirement 名称组成稳定键，并为 profile 定义的独立行为条件使用有意义的子标识。S64 继承行保留 profile 维度并引用对应 U64 行，目录统计需同时报告 profile 行数与去重规范要求数。

## Verification

**Commands:**
- `git diff --check` — 文档与索引变更无空白错误。

**Manual checks:**
- 与官方 v1.0 §3.1 逐节核对两种 profile 的 mandatory base、扩展、行为条件、继承、options、recommendations；检查所有 mandatory 行双侧字段齐全且初始状态不暗示未经调查的实现结果。

## Review Triage Log

- false — 盲审认为 M/A/V/Zfhmin/Zfa 等条目应加入各扩展的完整操作语义。官方 RVA23 Profile v1.0 §3.1.1.2 本身仅将这些扩展列为必选项并给出简短描述；本清单逐项收录 profile 要求及 profile 给出的限制，扩展手册的细节由后续领域故事追踪。该意见超出本清单要求。route: reject.
- low — 盲审指出 Zimop/Zcmop 的“may-be”措辞易被误读为扩展可选。已明确两扩展本身是 U64 必选项，并描述未重定义时各自默认行为及 ratified ISA 来源。证据：[Unprivileged ISA v20260120 §9.1](https://docs.riscv.org/reference/isa/v20260120/unpriv/zimop.html)。route: patch.
- false — 盲审认为 Ziccif/Ziccrse/Ziccamoa/Zicclsm 未限定主存范围。复查四条表项均明确写有“主存区域”，并限定同时具有可缓存性与一致性 PMA 的区域。route: reject.
- low — 盲审指出“所有实现行”混淆要求行与两侧实现映射。已改为说明每个要求行的 Kunminghu 与 Heliodor 映射状态均初始化为 `not-studied`。route: patch.
- low — 盲审指出覆盖行的实现状态可能与证据记录状态混淆。已说明覆盖行采用 AD-4 实现状态，证据 ID 链接到学习记录模板中独立的 Kind/Status 字段。证据：`notes/templates/learning-record.md` 的“证据表”。route: patch.
- low — 盲审指出证据类型与状态缺少关系说明。已列出模板中的类型和状态词汇，并明确两列分别表示证据类型与证据状态、没有固定的一对一对应。证据：`notes/templates/learning-record.md` 的证据表及 AD-2。route: patch.
- low — 盲审指出 ratification 声明缺少直接来源。已加入 RISC-V International 官方 ratification 公告链接。route: patch.
- low — 盲审指出目录总数难以复算。已补充 U64、S64 继承/特有项与去重后的算式，并说明 Sha 作为 8 个组成项的组合名称不另计一行。证据：逐项键计数与继承关联结构检查。route: patch.
- false — 边界审查未发现未覆盖路径；无需修订。
- false — 验证缺口审查未发现缺口；清单为文档资产，已核验官方章节、条目数、继承关联、双侧状态字段及 Markdown 空白格式。
