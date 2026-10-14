---
unit_id: "rva23s64-closeout-audit"
stage_id: "Epic 5 / Story 5.7"
scope: "审计 RVA23S64 v1.0 深度单元与 Epic 4 必选项图谱的关联、证据状态、运行边界和本项目学习结项。"
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0 ratified"
    section: "§3.1.1 RVA23U64; §3.1.2 RVA23S64"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

# RVA23S64 深度单元结项证据审计（Story 5.7）

## 学习结项决定与自检

**结项决定：接受本项目的 Epic 5 学习交付，但不接受为 CPU 行为验证完成。** 五个主题均有固定快照、精确 profile 键与规范版本、双边路径或受限的缺失结论、学习者自检问答和案例状态；局部静态证据及一项 Heliodor M/HS 运行失败均能追溯。Stories 5.2–5.6 的受计划 CPU 案例不是全覆盖：多数在 CPU 启动前受阻，Ssstateen 隔离测试实际 run-fail，其他列出的边界未验证。将这些缺口明确保留，是本项目“理解证据与边界”的学习目标交付；它们仍是若未来需要验证实现行为时的未完成事项。

1. **五项规范映射是否覆盖整个 RVA23S64？** 否。它们只映射 S64 的五项深度主题；Epic 4 的 58 行/59 个去重键目录才承载必选项全图谱，目录中其他状态也保留其各自范围。
2. **哪些案例有 CPU 观察？** 只有 Story 5.6 的 Heliodor M/HS 隔离 fixture 实际启动；观察结果为功能 `run-fail`。Zifencei、Sstc、Sscofpmf、Ssnpm 候选测试均未到 CPU 行为结果，Kunminghu 五个专题均无本轮 CPU 运行结果。
3. **结项结论意味着 RVA23 合规吗？** 不意味着。项目学习交付完成不构成两个 CPU 的整体 RVA23 行为验证、符合性声明或认证。

## 审计边界

本审计对照 `sources.lock`、Epic 4 覆盖目录和 Stories 5.1–5.6 学习记录。两份 checkout 的实际 HEAD 与锁定值一致；工作区中的 `sources/` 保持只读。本次不修改上游源码，也不复核全部上游实现或认证 RVA23。

Epic 4 目录当前为 U64 34 行、S64 58 行，共 92 profile 行、184 个实现状态格、59 个去重规范要求。五个深度单元分别只深入一个强制要求，不能替代完整 profile 图谱。覆盖表两侧状态是目录分类；其下的证据类型和状态是另一维度。

## 要求键与规范依据

| 深度主题 | 精确强制键 | 本单元规范基线 | Kunminghu | Heliodor | 覆盖记录 |
|---|---|---|---|---|---|
| Zifencei | `RVA23S64/v1.0/§3.1.2.2/Zifencei` | Zifencei v2.0 ratified；RVA23 Profile v1.0 §3.1.2.2/N2 | `studied-unverified`；活动 RTL 与 fixture 汇编/反汇编已检查，未在 CPU 上运行 | `studied-unverified`；测试机器码已检查，Veryl 在 testbench check 阶段退出 | [覆盖行](../rva23-coverage.md#L101)；[Story 5.2 单元](rva23s64-zifencei-v1.md#证据与结果) |
| Sstc | `RVA23S64/v1.0/§3.1.2.2/Sstc` | Sstc v1.0 ratified §§12.1–12.3；RVA23 Profile v1.0 §3.1.2.2 | `studied-unverified`；NewCSR、compare/pending 和门控路径静态检查，无定向 CPU harness | `studied-unverified`；S 与 VS 候选目标均在 `$readmemh`/`dram` `invalid_initial_assign` 失败，仿真未开始 | [覆盖行](../rva23-coverage.md#L113)；[Story 5.3 单元](rva23s64-sstc-v1.md#evidence-table) |
| Sscofpmf | `RVA23S64/v1.0/§3.1.2.2/Sscofpmf` | Sscofpmf v1.0 §§13.1.1–13.1.2；RVA23 Profile v1.0 §3.1.2.2 | `studied-unverified`；硬件 carry、OF、过滤和请求路径静态检查，无 CPU 运行入口 | `studied-unverified`；counter3/event5 目标在 testbench check 阶段被同一 `dram` 初始化错误阻断 | [覆盖行](../rva23-coverage.md#L114)；[Story 5.4 单元](rva23s64-sscofpmf-v1.md#evidence-table) |
| Ssnpm | `RVA23S64/v1.0/§3.1.2.2/Ssnpm` | RVA23 Profile v1.0 §3.1.2.2；Pointer Masking v1.0.0 §§17.1.2.2–.8；H v1.0 §14.1.2.1 | `studied-unverified`；PMM/TLB 静态路径已检查，无 S/U/guest 运行 | `studied-unverified`；M-mode Supm 材料不是 Ssnpm 证明，其 target 在 testbench check 阶段失败；VS/VU selector 未定位 | [覆盖行](../rva23-coverage.md#L115)；[Story 5.5 单元](rva23s64-ssnpm-v1.md#证据表) |
| Ssstateen | `RVA23S64/v1.0/§3.1.2.2/Ssstateen`（属于 Sha） | Smstateen/Ssstateen v1.0 §§3.1.1–3.1.3；RVA23 Profile v1.0 §3.1.2.2/Sha | `studied-unverified`；活动 NewCSR 的八 CSR 与 gate 静态可追踪，Kunminghu 构建缺 `mill` 而未运行 | 覆盖目录 `not-present` 只针对已检查的主 CSR 路径；另一个受控 M/HS 隔离用例实际 `run-fail`，非预期 trap 与读回观察已记录 | [覆盖行](../rva23-coverage.md#L118)；[Story 5.6 单元](rva23s64-ssstateen-v1.md#evidence-table) |

## 计划案例、结果与范围

“运行失败”只用于输入确实启动到目标 CPU 并观察到不符结果；构建、编译或 testbench check 阶段退出属于阻塞，不是 DUT 结果。没有任何下列单元产生 `run-pass` 的 CPU 行为证据。

| 故事 / 计划案例 | Kunminghu 结果 | Heliodor 结果 | 当前边界与证据 |
|---|---|---|---|
| 5.2：写入新指令、执行 `FENCE.I`、检查新执行结果；检查 ignored/reserved 字段 | Fixture 已汇编并反汇编，未接入可运行 harness；`mill` 不可用，CPU 行为未验证。 | 定向 `test_arch_rv64ui_fence_i` 在 Veryl testbench check 遇 `invalid_initial_assign` 退出 1，测试体未运行。已有机器码期望值 444/777 不是观察结果；`funct12/rs1/rd` 非零编码未覆盖。 | 多 hart 发布/远端同步仍未验证；见 [5.2 E4–E7](rva23s64-zifencei-v1.md#证据与结果)。 |
| 5.3：S-mode `time <, ==, > stimecmp`、STCE/TM 开关及 pending/trap；VS `vstimecmp`、`htimedelta`、VSTIP | 没有定向 CSR/interrupt CPU harness；比较边界、gate 与 delivery 均未运行。 | S 和 VS 两个候选 target 均在 `$readmemh(HEX_FILE, dram)` 的 testbench check 退出 1；无仿真观察。 | 两边均无运行通过。Heliodor 的静态路径和测试输入不能代替运行；见 [5.3 E2–E7](rva23s64-sstc-v1.md#evidence-table)。 |
| 5.4：硬件 HPM event 递增造成 OF；scountovf、LCOFIP/IE、clear/re-arm、MINH/SINH/UINH/VSINH/VUINH 和 access/delegation；ACT4/Sail | 没有定位可运行的 HPM CPU fixture；硬件事件回绕及所有动态 gate 未验证。 | counter3/event5 用例在 Veryl testbench check 退出 1，CPU 未启动。ACT 配置将 Sscofpmf 标为 unsupported，缺生成测试及可用模型/coverpoint，ACT4/Sail 案例未生成或执行。 | 源码有五个过滤位，但 Heliodor VS/VU 静态标 unused；没有运行观察。不能以软件写计数器回绕作溢出证据；见 [5.4 E2–E7](rva23s64-sscofpmf-v1.md#evidence-table)。 |
| 5.5：PMLEN=0/7、enabled/disabled、tag transform、U 与 VS/VU，以及 load/store、atomic、FP、compressed、cache、vector、hypervisor 显式访问族 | 有限 RTL/地址路径静态检查；案例与地址族未运行。 | 现有 M-mode Supm 与 Ssnpm 不同；`test_arch_supm` 在 testbench check 退出 1，未运行 CPU。 | 所有 S/U/guest 变换观察、vector、CMO、地址边界保持未验证。Profile PDF 的 PME 与架构规范/RTL 的 PMM 原样保留；根据固定 profile 源和 PMM 定义记录为同一控制要求的拼写差异。见 [5.5 E1–E6](rva23s64-ssnpm-v1.md#证据表)。 |
| 5.6：`sstateen0–3`/`hstateen0–3` reset/readback/WARL，M/H/S/VS/VU 允许与阻断访问 | 构建在缺少 `mill` 处退出，未启动 CPU。 | 原仓库无专用 test target；共享 harness check 被 `$readmemh` 阻断。隔离 M/HS harness 实际运行：八个 stateen 写全 1 后读回全零；关闭 gate 时没有预期 20 个 CSR trap；只观察到 HS `ecall` cause 9；tohost `0x02`，预期 `0x2B`，因此 `run-fail`。 | 这是固定 Heliodor 路径的 M/HS 功能失败证据；不扩展到 VS/VU、逐字段 WARL 或其他集成。Kunminghu 实际行为和两边 U/VU protected-state 访问未测；见 [5.6 E7–E9](rva23s64-ssstateen-v1.md#evidence-table)。 |

## 检查器与 sprint 记录

以下命令均在项目根目录执行。Checker 报告目录状态，不判断 CPU 行为。

| 检查 | 实际命令与版本 | 实际输出 / 结果 |
|---|---|---|
| RVA23 inventory | `python3 scripts/check_rva23_coverage.py`；Python 3.12.3 | `valid: true`; `profile_rows: U64=34 S64=58 total=92`; `implementation_status_cells: 184`; `deduplicated_requirements: 59`。S64 Heliodor：partially-studied=26、studied-unverified=29、evidence-observed=2、not-present=1；S64 Kunminghu：36、22；U64 Heliodor：14、20；U64 Kunminghu：21、13。 |
| 本地文档目标/锚点 | `python3 scripts/check_doc_links.py`；Python 3.12.3 | 检查 notes 文档、Epic 5 context/start-gate 和 Story 5.1–5.7；以 GitHub.com 仓库 GFM 渲染为目标，支持简单 inline/full/shortcut reference links、定义式链接、`<a href>`/`<img src>` 属性、HTML 显式 ID、heading anchors、相对目标及 `file:line`/`#Lnn` 源码引用。HTML comments 不参与链接扫描；转义 backtick 不打开 code span；裸目标中的平衡嵌套括号受支持。不是完整 CommonMark/GFM parser；自动链接、复杂 inline label 和任意 HTML 均不承诺检查。 |
| sprint YAML | `uv run --no-cache --with ruamel.yaml python .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml`；uv 0.12.5，Python 3.12.3 | `{"ok": true, "action": "validate", "status_file": "_agile-output/implementation-artifacts/sprint-status.yaml", "valid": true, "problems": [], "legacy_mapped": []}`。故事键为 `5-7-审计-rva23s64-覆盖与学习结项证据`。 |
| checker 回归测试 | `python3 -m pytest -q scripts/tests/test_check_doc_links.py`；pytest 9.1.1 | `13 passed`。涵盖相对链接和 heading anchor、缺目标/缺锚点及行号、explicit/重复/CJK anchor、外链与 inline/fenced code 排除、full/shortcut/undefined reference 与 quoted/unquoted HTML 链接、CLI 成功/错误退出、非法 UTF-8 和无效 URL。 |
| 全脚本测试 | `python3 -m pytest -q scripts/tests`；pytest 9.1.1 | `31 passed`（覆盖目录、链接解析及结项分类检查；Story 5.7 review fixes 后复跑）。 |
| whitespace 检查 | `git diff --check` | 检查通过，无 whitespace error。 |

Story 5.7 开始实施时由 `backlog` 切换为 `in-progress`，交付审查后按 review 结果完成；本审计记录完成时，Epic 5 retrospective 状态为 `optional`。其后已完成正式回顾，见 [Epic 5 retrospective](../../_agile-output/implementation-artifacts/epic-5-retro-2026-10-14.md)；当前 Epic 5 与 Stories 5.1–5.7 均为 `done`。

## 未决项

- 未来若需验证 CPU 行为，应先恢复 Kunminghu Mill 构建入口，修复或隔离 Heliodor testbench 的 Veryl `$readmemh`/`dram` check 阻塞，再运行每个故事列出的输入；当前未产出的动态结果不推断为通过。
- Zifencei 非零 ignored/reserved 字段及远端 hart 协调、Sstc comparator 等值与 delegation、Sscofpmf 模式矩阵和 clear/re-arm、Ssnpm S/VS/VU 与非标量访问族、Ssstateen VS/VU 和逐字段 WARL/reset 仍未运行验证。
- Heliodor Ssstateen `not-present` 只代表已检查固定 CSR 主路径和本次受控 M/HS 观察；外部集成、guest 行为与 profile 其他要求不在该结论内。
- 全局 RVA23 checker、文档链接 checker 和 sprint validator 的成功仅证明清单/文档/YAML检查通过，不是设计验证。
