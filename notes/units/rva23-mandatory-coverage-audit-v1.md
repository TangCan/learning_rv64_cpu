---
unit_id: "rva23-mandatory-coverage-audit"
stage_id: "Epic 4 / Story 4.10"
scope: "按 RVA23 Profile v1.0 官方 §3.1 清单核对项目必选项目录的行完整性、双核状态、范围说明、证据链接与计数；不重新认证或独立复核此前故事的全部源码结论。"
exclusions:
  - "不把本次目录审计当作实现符合性认证，也不将继承关联重复计为新规范要求。"
  - "不因 not-studied 或搜索缺失推断扩展不支持。"
  - "不将测试材料、单个测试结果或上游项目自述视为完整 profile 验证。"
spec_refs:
  - name: "RISC-V RVA23 Profile"
    edition: "v1.0 ratified"
    section: "§3.1.1 RVA23U64; §3.1.2 RVA23S64"
    profile_category: "mandatory inventory"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    repository: "https://github.com/OpenXiangShan/XiangShan.git"
    branch: "kunminghu-v2"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    repository: "https://github.com/dalance/heliodor.git"
    branch: "master"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

## 单元自检

- **问题：** 92 条 profile 行的状态计数能否证明两个实现满足 RVA23？
- **学习者答案：** 不能。计数表达目录中调查状态的分布；部分状态基于有边界的静态证据，未调查项和未运行的子案例仍是开放问题。认证需要覆盖规范行为的完整验证证据。
- **检查类型：** traceability
- **证据 ID：** E1–E3

## 审计方法与结论

官方规范基线为 [RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)。规范清单按 profile 和 section 定义必选键；可复查的固定键 manifest 位于 [`scripts/check_rva23_coverage.py`](../../scripts/check_rva23_coverage.py) 的 `U64_IDS`、`S64_IDS`。目录计数为 U64 34 行、S64 58 行、合计 92 个 profile 行。S64 的 33 个继承扩展行均指向同 ID 的 U64 原始要求，因此去重总数为 59（34 个 U64 原始要求、S64 的独立基础要求 1 项、S64 特有要求 24 项）。Sha 作为 8 个组成要求展开，没有额外重复行。

每条行都有 Kunminghu 和 Heliodor 状态格，使用目录允许的状态词。链接审计仅检查本目录引用的本地文件与 evidence-table 锚点是否存在；此前专题中的源码位置、证据内容与技术结论均未在本次独立复核。原有 33 条 S64 继承行此前留有空白模板；本次改为沿用对应 U64 原始行状态、位置范围、子案例和证据链接，并明确说明未新增独立调查。Story 4.10 审计时，四条 S64 特有项 Zifencei、Sstc、Sscofpmf、Ssnpm 在两侧均为 `not-studied`；Stories 5.2–5.4 随后将 Zifencei、Sstc、Sscofpmf 两侧更新为 `studied-unverified`。当前仍为 `not-studied` 的三个实现侧是 Kunminghu/Heliodor 的 Ssnpm，以及 Heliodor 的 Ssstateen；Kunminghu 的 Ssstateen 有局部静态映射。Ssnpm 中的 `henvcfg.PME` 也不能由 U64 Supm 映射替代。当前三个未调查实现侧仍需后续专题调查；Story 4.10 原始审计只记录当时的状态与边界，不计作完成调查。

| Profile | 实现 | partially-studied | studied-unverified | not-studied | evidence-observed | not-present | out-of-scope | 行数 |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| RVA23U64 | Kunminghu | 21 | 13 | 0 | 0 | 0 | 0 | 34 |
| RVA23U64 | Heliodor | 14 | 20 | 0 | 0 | 0 | 0 | 34 |
| RVA23S64 | Kunminghu | 37 | 20 | 1 | 0 | 0 | 0 | 58 |
| RVA23S64 | Heliodor | 26 | 28 | 2 | 2 | 0 | 0 | 58 |

统计单位是 profile 行的实现侧状态格，一格计一次；继承行在各 profile 统计中保留，但在去重规范要求数中不重复。覆盖表状态与证据表 Kind/Status 是不同维度。非强制选项、建议项和上游自述均独立列出，不进入 mandatory 状态计数。

**未解决项：** Story 4.10 时 S64 的 Zifencei、Sstc、Sscofpmf、Ssnpm 两侧均未做专题调查；Stories 5.2、5.3、5.4 已将 Zifencei、Sstc、Sscofpmf 两侧更新为 `studied-unverified`。当前 Ssnpm 两侧仍未调查；Ssstateen 的 Heliodor 侧也未调查（Kunminghu 侧只有局部静态映射）。Story 5.4 的两个 Sscofpmf 单元分别为静态证据与 testbench 阻塞，均不是运行通过；当前三个未调查实现侧仍需后续专题调查；其余 `partially-studied` 与 `studied-unverified` 行仍列有未穷尽子案例或未运行验证。目录不声明完整实现覆盖、认证或符合性。

## 证据表

<a id="evidence-table"></a>

| ID | 支持的结论 | Kind | Status | 范围 / 输入 | 结果 / 限制 |
| --- | --- | --- | --- | --- | --- |
| E1 | 官方必选清单与键 manifest | spec | inspected | RISC-V RVA23 Profile v1.0 §3.1.1–§3.1.2；固定键分别列于 checker 的 `U64_IDS` 与 `S64_IDS` | 官方强制目录基线为 U64 34 项、S64 58 项；继承项在各 profile 中单列，去重结构为 34+1+24=59。Checker 会逐项将文档行键与此 manifest 比较。 |
| E2 | 行级状态、理由和证据回链 | source | inspected | 审阅 `notes/rva23-coverage.md` 全部 mandatory rows；检查每行两侧状态格、继承来源、局部证据链接和本地锚点 | 发现并修复 33 个继承行的模板占位；发现并修复 Zifencei、Sstc、Sscofpmf、Ssnpm 的范围占位。合法状态计数见本记录；旧证据保持各原学习单元的来源和验证类型。 |
| E3 | 状态提取与汇总边界 | source | inspected | 计数命令 `uv run --no-project python scripts/check_rva23_coverage.py` 从已通过 inventory 检查的 92 行逐行提取状态；检查两侧状态格数量、允许词汇、继承源键及预期计数 | 命令输出 184 个状态格和四组 profile/实现计数；checker 对 malformed row、缺失/额外/重复 inventory key、缺失/非法状态、继承源键不符及统计漂移均以非零退出拒绝。选项、自述未计入 mandatory，计数也不作符合性声明。 |

## 比较与学习结论

U64 两侧均已有逐项学习记录，但仍存在未验证子案例。Story 4.10 时 S64 的 Zifencei、Sstc、Sscofpmf 尚未调查；Stories 5.2–5.4 随后分别补充了双核学习单元，因此当前目录计数把这三项两侧状态记为 `studied-unverified`。Sscofpmf 的动态运行仍被 Heliodor testbench blocker 阻断，Kunminghu harness 未定位；Ssnpm 两侧和 Heliodor Ssstateen 仍属当前未调查项。S64 Heliodor 的两个 `evidence-observed` 格保持原始单元定义和证据链接；这个覆盖状态仅表示目录所列证据观察，不能替代完整要求验证。详见 [`notes/rva23-coverage.md`](../rva23-coverage.md) 中的完整逐项映射与未解决项。

<a id="rva23-mandatory-coverage-audit-v1-self-check"></a>
