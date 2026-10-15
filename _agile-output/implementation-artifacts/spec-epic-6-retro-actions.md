---
title: '落实 Epic 6 回顾行动项'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '93bd409f6b375e683fca04cc4e70637ec7144b55'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md'
  - '{project-root}/_agile-output/implementation-artifacts/sprint-status.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 6 已验收并发布，但回顾留下 runner 结果分类、dispatch/case 测试、证据矩阵完整性和归档维护 5 项 open actions。当前 runner 可能把 testbench 输出误作目标执行，Ssstateen case 映射未逐项贯通，矩阵约束依赖人工复核。

**Approach:** 以最小改动完成五项行动：严格区分 CPU 观察、CPU 断言失败和运行完整性阻塞；为 runner 分派及 Ssstateen case 建立映射测试；为既有矩阵和 operation records 增加显式 completeness 检查；量化归档并决定可验证的保留/压缩策略。

**Scope decision:** 用户选择保留五项完整行动范围。规格约 2,283 个 cl100k_base tokens，超过 1,600-token 建议线；为保留彼此关联的证据分类、矩阵校验及归档工作流，按完整范围规划。

**Archive decision:** 用户选择保留可直接阅读的日志路径，只量化归档、区分可重建与独有证据并记录保留/压缩建议；本轮不做 gzip 路径迁移，不删除或重写 manifest 引用文件。对当前 manifest 运行完整性校验。

**Boundaries & Constraints**

**Always:** 保持 sources.lock 固定快照；只在真实 DUT 断言不匹配时记 `run-fail`；保留已有运行证据与 manifest 可验证性；把失败、blocked、unverified 和 not-applicable 分开；复用现有 Python/pytest 与 manifest 格式。

**Never:** 不修改上游 RTL；不因测试缺项把既有 CPU 结果改成 pass；不删除任何 manifest 引用证据；不把结构性矩阵校验表述为 RVA23 符合性验证。

**I/O & Edge-Case Matrix**

| 场景 | 输入/状态 | 预期 | 错误处理 |
|---|---|---|---|
| Arch marker 但 tohost=0 | testbench 固定时钟后打印 marker | 无目标执行证据，结果为 blocked | 保留 marker 和退出信息，不能记 CPU run-fail |
| Fixture 写入失败 marker | 目标已写入非零失败值且断言不匹配 | CPU started、run-fail | 保存观察值与失败阶段 |
| CPU 运行后输入/源码完整性错误 | 运行器发现 post-run hash 不一致 | infrastructure blocked，不标 assertion failure | 保存 blocker、哈希和 CPU-start 观察 |
| 合法 Ssstateen case | case 到 fixture/harness 映射存在 | 生成对应检查并可验证映射 | 未知 case 明确拒绝，不静默回退 |

</frozen-after-approval>

## Code Map

- `experiments/heliodor-smoke/run.py` — `observe()` 目前对任何 arch result marker 认定 started；异常处理把 post-run integrity 错误设成 assertion failure；专题 dispatch、归档 run record 和 result 字段在 `run()`。
- `sources/heliodor/tb/test_arch_common.veryl:6043-6051` — Sscofpmf testbench 固定等待后无条件输出 tohost/pass；该行本身不证明 fixture 运行。`scripts/tests/test_heliodor_smoke.py` 已有 runner mock 和组件级检查，可扩展 mode-filters dispatch。
- `scripts/run_cpu_smoke.py` — manifest `classify()`、单条 run/manifest 校验与 SHA 检查；保留既有字段兼容，必要时用可选 infrastructure 状态表示 post-run integrity blocker。
- `experiments/ssstateen/run_isolated.py` — case 条件生成 harness，脚本导入有文件系统副作用；末尾 case-to-HEX 字典与 parser choices 必须一致。`scripts/tests/test_ssstateen_story.py` 已覆盖 trace 解析和部分 fixture，但未验证所有 case 到 HEX/断言映射。
- `notes/units/rva23s64-ssnpm-v1.md`、`notes/units/rva23s64-ssstateen-v1.md` 与 `notes/units/evidence/cpu-validation-toolchain-v1.yaml` — Ssnpm 访问族表、Ssstateen CSR/mode 表和结构化 operation records；现有 coverage checker不负责这些运行矩阵。
- `notes/units/evidence/smoke/` — 约 1.1 GiB、主要为日志；`.git` 对象库约 51 MiB。当前 manifest 校验有效；评估发现应保留被引用和内容独有的失败/诊断证据。
- `_agile-output/implementation-artifacts/deferred-work.md`、`epic-6-retro-2026-10-15.md` — 已承诺行动及结项边界；行动完成证据需回填并由 sprint 状态 updater 更新。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/heliodor-smoke/run.py`, `scripts/run_cpu_smoke.py` — 区分目标执行证据、DUT mismatch 与完整性 blocker；保留已存在 manifest 记录的校验兼容。
- [x] `scripts/tests/test_heliodor_smoke.py` — 补 mode-filters 真实 dispatch mock，联合检查 fixture、target、label/marker、cycle budget 与结果；覆盖 arch marker 不代表 CPU start 及 integrity blocker。
- [x] `experiments/ssstateen/run_isolated.py`, `scripts/tests/test_ssstateen_story.py` — 将纯 case/harness/fixture 选择与副作用隔离，验证全部 parser case 的一一映射和未知 case 拒绝。
- [x] `scripts/tests/` 与两份 RVA23S64 单元 — 定义明确的访问族/模式/CSR 必需集合；校验矩阵条目、operation ID 唯一性、允许状态和证据引用，失败/未验证仍为合法状态。
- [x] `notes/units/evidence/smoke/`, CPU manifest 与归档读取校验 — 量化文件/类别/重复项并区分可重建与独有证据；保留可读路径，不删除证据，验证所有路径/哈希。
- [x] retrospective/sprint status — 每个 action item 只有在对应证据通过后才标为 done，记录验证命令与限制。

**Acceptance Criteria:**
- Given 只有 testbench 输出的 arch marker 且 tohost 为零，when Heliodor runner 分类结果，then 记录为无目标进展证据的 blocked；Given 非零 DUT failure marker，then 按 fixture mismatch 记录 run-fail。
- Given CPU 仿真后 source/input hash 验证失败，when 写入 manifest，then assertion_failed=false，完整性问题单独可见且结果不可冒充 DUT run-fail。
- Given `mode-filters` 或任一已支持 Ssstateen case，when 测试 runner 映射，then fixture、target/harness 断言、marker 和预算一致；未知 case 失败并给出明确错误。
- Given Story 6.7/6.8 证据矩阵，when 运行 completeness 校验，then 所需族/模式/CSR 均有合法状态、引用可解析且 operation ID 无重复；不把 `run-fail`、`unverified` 或 `not-applicable` 当作通过。
- Given 归档策略执行完成，when 校验 manifest，then 所有保留证据字节可复原且路径/hash 校验成功，工作区空间变化有实测记录。

## Implementation Notes

- 可选 manifest 字段 `infrastructure_blocked` 用于区分运行后的完整性错误，同时兼容历史 schema-v1 记录。
- `scripts/check_rva23_run_matrices.py` 检查必需矩阵行、重复行、列数、每个模式格的合法状态、运行结果词表、evidence ID、每次运行内 operation ID 唯一性，以及操作的预期行为/异常和观察值。对缺失 heading 和畸形 YAML 容器返回错误。现有链接和 manifest validator 负责校验引用目标及哈希。
- 本次未改写或移除归档路径；未来压缩/去重须单独审核，并验证 manifest 引用兼容性。
- 归档产物来源复核（2026-10-15）：`.bin/.elf/.map` 共 393 个，其中 Kunminghu 运行归档 377 个、Heliodor Ssstateen 归档 16 个；manifest 有对应源码/链接脚本、构建命令、工具版本和产物 SHA-256。302 个 `.hex` 中有 289 个被 manifest 的 `artifacts` 路径引用，另 13 个未被该字段直接引用；全部保留。四类产物共 695 个、3,111,509 字节，约占归档 1,099,348,447 字节的 0.28%。manifest 校验有效。来源链可追溯不等于逐项 bit-for-bit 重建已验证；结合用户要求保留可读日志及产物占比，本轮不压缩或清理，未产生需要更新的 manifest hash。


## Spec Change Log


## Review Triage Log

| # | 审查发现 | 裁定与证据 | 路由 |
|---:|---|---|---|
| 1 | 合并运行中 smoke 已通过而 arch target `tohost=0` 会被判成 DUT 失败 | **medium**：旧 `failed = cpu_started and not passed` 将 idle arch 结果带入 `run-fail`；现分开计算 smoke 与 arch 断言结果，并有 runner 回归测试。 | patch，已修复 |
| 2 | 缺失矩阵 heading 会在 `_table_rows()` 触发 `IndexError` | **medium**：heading 定位使用无保护的 `split(...)[1]`；现返回带 heading 名的校验错误，负向测试覆盖。 | patch，已修复 |
| 3 | 用集合检查 row label 会漏掉重复必需行 | **medium**：重复行可让表格结构看似完整；现检测并报错，负向测试覆盖。 | patch，已修复 |
| 4 | 必需矩阵格的状态和证据引用不完整仍会通过 | **medium**：原 checker 只检查 row label；现检查 mode matrix 每格状态、运行行 evidence ID，并对 ID/range 解析定义，补了缺状态和未定义 ID 测试。 | patch，已修复 |
| 5 | 畸形 YAML mapping/list 或 operation record 可触发异常退出 | **low**：对新 checker 单独传入 malformed values 会抛异常；现按结构校验并返回说明，负向测试覆盖。 | patch，已修复 |
| 6 | 原 Ssstateen 测试只在源码任意位置搜索 assertion 文本，不能证明 case 使用对应 harness | **medium**：改错 `vs-v2` 分支仍可能通过原测试；现对全部八个 case 执行脚本生成 harness，并核验生成断言与复制 fixture。 | patch，已修复 |
| 7 | Ssnpm 逐核/逐模式矩阵缺少 FENCE 字段和取指/隐式访问行 | **medium**：上游访问族矩阵已列出且规范边界明确为 not-applicable；逐模式矩阵缺行使维度不完整。现补齐两行及状态/边界说明。 | patch，已修复 |
| 8 | `.hex/.bin/.elf/.map` 被称为可重建，但没有逐类来源和构建依据 | **medium**：本轮未验证这些归档产物的生成 provenance；文档现明确标注可重建性未验证，并保留全部文件。 | patch，已修复 |
| 9 | 回顾记录称 integration test 未运行但未给出测试名 | **low**：读者无法确定未覆盖的行为；固定 Veryl 加入 PATH 后该测试已实际通过，回顾和规格最终记录完整聚焦套件 95 项通过。 | patch，已修复 |
| 10 | Edge-case hunter 独立指出缺失 heading 会令 checker 崩溃 | **medium**：核实为与第 2 项相同的 `split()[1]` 根因；现由同一修复和负向测试覆盖。 | patch，已修复 |
| 11 | Edge-case hunter 独立指出状态/引用无效可能仍显示完整 | **medium**：核实旧逻辑未检验状态单元和证据列；现补状态、运行证据 ID 及定义范围校验。 | patch，已修复 |
| 12 | Edge-case hunter 指出 YAML 非字符串状态或不可哈希 operation ID 可能引起 `TypeError` | **low**：运行时检查确认 malformed container 可令 checker 异常退出；现验证类型后再比较/去重。 | patch，已修复 |
| 13 | Edge-case hunter 认为实现说明夸大 checker 对状态/引用的覆盖 | **medium**：原说明与旧代码不符；修复后 checker 和负向测试覆盖逐模式状态及证据定义，说明同步更新。 | patch，已修复 |
| 14 | Verification-gap reviewer 指出没有测试实际生成的 case harness | **medium**：确认错误的 harness 分支会逃过源码文本搜索；现所有 case 均执行生成逻辑并检查断言与 fixture。 | patch，已修复 |
| 15 | Verification-gap reviewer 指出 checker 只有当前仓库正向测试 | **medium**：删除重复 ID/缺失观察值检查不会影响旧正向测试；现补缺行、非法状态、重复 ID、缺预期/观察及畸形容器的负向测试。 | patch，已修复 |
| 16 | 独立复核发现只检查 evidence token 存在仍会接受未定义 ID，例如 `E99` | **medium**：原实现不把 citation 与证据表定义相交；现展开 ID range 并与文档证据定义对照，`E99` 回归测试通过。 | patch，已修复 |
| 17 | 完整聚焦套件指出一个旧测试仍把 smoke 成功但 arch 无目标结果记为 run-fail | **medium**：测试逐项运行确认该输出应是 `blocked`，未证明 DUT assertion mismatch；更新为逐例声明预期 `failed`，另保留真实 smoke assertion 错误为 run-fail。 | patch，已修复 |

## Verification

**Commands:**
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests/test_heliodor_smoke.py scripts/tests/test_run_cpu_smoke.py scripts/tests/test_ssstateen_story.py` — 95 项通过，包括真实 Veryl arch harness 集成测试。
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` — manifest 有效。
- `python3 scripts/check_doc_links.py` — 38 份文档有效。
- `python3 scripts/check_rva23_coverage.py` — 有效；92 行 profile、184 个状态单元格、59 项去重要求。
- `python3 scripts/check_rva23_run_matrices.py` — 必需矩阵、证据 ID/range 和 operation records 完整。
- `git diff --check` — 通过。
