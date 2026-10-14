---
title: 'Story 6.3: 建立 Heliodor arch harness 隔离运行入口'
type: 'feature'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7aa4e7a5427445f5e4c1b1a7af3f15b16e844089'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/planning-artifacts/epics.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
  - '{project-root}/experiments/heliodor-smoke/run.py'
  - '{project-root}/_agile-output/implementation-artifacts/spec-6-2-kunminghu-fixture-loader.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Heliodor 的 Veryl arch 测试入口会被共享的、未实例化 debug harness 检查问题阻塞；直接在锁定 checkout 上编辑会破坏可复现基线。现有 `experiments/heliodor-smoke/run.py` 已有临时副本和 `test_smoke` 的初步运行路径，但没有充分的失败分层、超时保护、运行前后源校验或结构化证据检查。

**Approach:** 将该路径收敛为可重复的隔离 runner：从 `sources.lock` 固定 revision 复制必要源、只应用已验证的 debug-harness 排除与局部 `allow(initial_assign)`，再运行普通 `test_smoke`。保存输入、变换、工具、命令、完整输出与摘要，并明确区分 CPU 启动前阻塞和 CPU 已启动后的断言失败。

## Boundaries & Constraints

**Always:** 使用 Story 6.1 固定的 Heliodor commit `94e9c5821c24a8941c3ddc3b76daddc7124a855a` 和 Veryl 0.22.0；临时副本必须新建，记录源树及变换后测试/fixture 的 SHA-256；普通 `test_smoke` 必须实际执行并观察启动、寄存器结果和 PASS；保留完整 stdout/stderr、退出码、工具版本、工作目录与归档元数据；运行前后验证锁定源码 revision、gitlink 与工作树清洁。

**Never:** 修改 `sources/heliodor` 或锁定快照；把临时 workaround 视为对所有测试语义透明；将 compile/check 通过等同于 CPU 已启动；将此基础 smoke 当作任何 RVA23 专题符合性证据；在本故事扩展到 Zifencei、Sstc、Sscofpmf、Ssnpm 或 Ssstateen 的专题结论。

## I/O & Edge-Case Matrix

| 场景 | 输入/状态 | 预期行为 | 错误处理 |
|---|---|---|---|
| 固定工具与源可用 | 锁定 Heliodor、Veryl 0.22.0、test_smoke 与 RV64UI `add` arch target | 隔离构建和运行，观察 `cy`/commit、x10–x13、tohost/pass 与两个 PASS marker，归档哈希 | 任一 target 失败时保留日志并报告首个失败阶段 |
| 工具缺失/版本不符 | Veryl 不存在或不符合锁定版本/hash | 不启动构建，结果为 blocked | 给出精确缺失项和下一步环境动作 |
| 构建或运行超时/源变更 | 阶段超时或校验前后源状态不一致 | 不得报告 run-pass；保存部分输出和失败记录 | 区分 CPU 启动前 blocked 与启动后 run-fail |

</frozen-after-approval>

## Code Map

- `experiments/heliodor-smoke/run.py` -- 现有基础路径：复制 `src/`、manifest、锁文件，变换 `tb/test_smoke.veryl`，调用 Veryl 并归档测试和 hex 输入；当前直接将输出写入日志，缺少有界超时、结构化失败记录及源状态完整性闭环。
- `sources/heliodor/tb/test_arch_common.veryl` -- 普通 arch harness 位于文件前部，debug harness 从 `ARCH_DEBUG_MARKER` 开始；选取 `test_arch_rv64ui_add` 模块和 `test/riscv-arch-test/build/rv64ui/add.hex`，截取边界必须唯一且精确。
- `experiments/ssstateen/run_isolated.py` -- 专题 runner 的已有隔离经验；复用临时 `src/`、排除未实例化 debug harness 和局部 DRAM lint allow 的具体边界，不复制 Ssstateen 专题逻辑。
- `notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- 锁定 Veryl 版本/hash、Heliodor revision、已知 smoke 输出和归档字段；运行证据应追加到该 manifest。
- `notes/units/evidence/smoke/heliodor-core-smoke-inputs/` -- 现有变换后 `test_smoke.veryl` 与 `v4_smoke.hex` 的 SHA 基线；核对实际变换与既有语义一致。
- `scripts/run_cpu_smoke.py` -- `validate_manifest` 校验 sources.lock、gitlinks 和 clean checkout；采用该校验而不是自建不完整的源干净性规则。
- `experiments/kunminghu-smoke/run.py` 与其测试 -- Story 6.2 的分阶段失败、超时、记录、哈希和故障注入风格；共享约定，不共享架构专属判定。
- `sources/heliodor/tb/test_smoke.veryl` -- 上游输入，只读取并逐字核对 workaround 插入点；禁止写回。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/heliodor-smoke/run.py` -- 校验锁定 revision、Veryl 版本与二进制摘要；隔离生成副本，保留普通 harness 并仅选择 `test_arch_rv64ui_add`；对 `test_smoke` 与 arch target 加超时；将输出与启动/结果断言整理为可解析的运行记录 -- 避免不完整输出被误报为通过。
- [x] `scripts/tests/test_heliodor_smoke.py` -- 覆盖缺工具、版本/hash 错误、源/fixture 变化、超时、CPU 未启动、错误寄存器值和错误成功 marker；以真实仿真运行两个 target，隔离故障不触碰源 checkout。
- [x] `experiments/heliodor-smoke/README.md` -- 记录复现命令、普通 harness 与 debug harness 的隔离边界、局部 lint allow、归档结构和 smoke 结论限制。
- [x] `notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- 追加最终运行记录及源、fixture、变换测试、工具、日志和产物 SHA-256。
- [x] `notes/units/rva23s64-cpu-validation-preflight-v1.md` -- 记录 Story 6.3 的最终 smoke 证据与 workaround 适用性限制。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` -- 所有验收与验证通过后将 Story 6.3 置为 `review`，独立审查通过后更新为 `done`。

**Acceptance Criteria:**
- Given sources.lock 指定的 Heliodor checkout，when runner 启动，then 它验证 commit 和 clean state，在全新临时副本上仅复制执行 `test_smoke` 所需文件，并且不改变上游 checkout。
- Given 固定 Veryl 0.22.0，when 隔离副本构建/检查/仿真，then 输出证明各阶段成功，CPU 启动可观察，x10、x11、x12、x13 与既有 smoke 的期望相符，并出现 PASS marker。
- Given 普通 arch harness 的 `test_arch_rv64ui_add` 与固定 `add.hex`，when runner 执行该 target，then 日志证明 harness 实际运行、`tohost=1`、`pass=1` 并出现其 PASS marker；变换仅移除未实例化 debug harness 和无关 arch test modules，并对 DRAM 初始化应用局部 lint allow。
- Given 工具不匹配、阶段超时、源或输入哈希变化、日志缺失或结果断言失败，when 生成运行结果，then 保留首个失败阶段、退出码、部分日志、输入/工具信息及资源和后续环境动作；CPU 未启动标为 blocked，启动后断言失败标为 run-fail，均不能伪装成 run-pass。
- Given runner 已完成，when 验证 manifest、日志哈希、文档链接和源 checkout，then 所有记录可复算且上游源码与 gitlink 均干净。
- Given 后续专题使用此 runner，when 涉及 memory、translation、interrupt 或 timing，then 该专题单独审查并记录 workaround 对其语义的适用性，本故事不替专题背书。

## Implementation Notes

实现过程中对照 `_agile-output/planning-artifacts/epics.md` 的原始 Story 6.3 验收，确认还必须实际运行普通 arch harness target。为保留冻结意图中的基础 `test_smoke` 验收，同时补足 Epic 原始范围，runner 将执行基础 smoke 与 `test_arch_rv64ui_add`；两者分别有 CPU 结果门控。

## Spec Change Log

- 对照 Epic 6.3 原始 AC 发现普通 arch target 是显式门槛；在不修改冻结意图的情况下，Execution/Acceptance 增加 `test_arch_rv64ui_add` 及其 tohost/PASS 证据，并保留 `test_smoke` 基础 smoke 要求。

## Review Triage Log

| # | Finding | Verdict / route | Evidence |
|---|---|---|---|
| 1 | 归档目录遇到 run ID 冲突时，默认 stdout/stderr 路径仍使用未加后缀的 ID。 | `low` / `patch` | 默认日志路径移到唯一 ID 决定之后；碰撞回归检查 `-2` 归档和日志路径。 |
| 2 | arch target 超时诊断固定写成 `test_smoke`。 | `low` / `patch` | 超时消息现在使用命令中的目标名；定向超时测试断言 `test_arch_rv64ui_add`。 |
| 3 | 对合并输出全局扫描寄存器和 marker 会把不同 target 的数据配对。 | `false` | runner 仅依次运行两个固定 target，smoke 寄存器与带 target 名的 arch `tohost`/marker 各有唯一来源；真实集成测试校验了两组观察。 |
| 4 | `source_tree_sha256` 包含 Heliodor `.git` 元数据。 | `medium` / `patch` | 源树摘要跳过 `.git` 路径；回归确认增加 Git 本地配置不会改变摘要。 |
| 5 | 运行后只校验测试与 fixture，隔离副本中的 RTL/config/lock 变化可能未被发现。 | `medium` / `patch` | 新增固定输入集合摘要，覆盖 `src/`、Veryl 配置/锁、两个 harness 与两份 fixture，并在运行后比较；测试注入 RTL 修改可触发失败。 |
| 6 | `output.log` 将所有 stdout 放在 stderr 前，丢失跨流时间顺序。 | `false` | 两条原始流分别保留并独立计算哈希，命令数组保留 target 顺序；验收要求完整分流日志，不依赖跨流时序。 |
| 7 | 日志落盘错误会逃出结构化结果生成。 | `medium` / `patch` | 自定义日志路径失败时改写到归档目录并把警告写入记录；故障注入测试确认 manifest 仍保存完整日志路径。 |
| 8 | 截取 arch target 未验证模块结束边界。 | `false` | 输入 revision 和 harness marker 均固定；Veryl 实际 check/test 解析变换后模块，漂移时源 revision 或选择锚点会拒绝运行。 |
| 9 | 运行会记录但不强制匹配 manifest 中的 Verilator/C++ 版本。 | `medium` / `patch` | runner 现在比较两项版本与 Heliodor snapshot 工具表；测试覆盖 Verilator 漂移，真实双 target 运行通过。 |
| 10 | Code Map/首个 AC 与新增 arch target 要求存在文档范围漂移。 | `false` | Code Map 描述进入本故事时的基础 runner；后续 AC、Implementation Notes 和 Spec Change Log 明确新增 arch target，二者描述先前状态与本次扩展。 |
| 11 | smoke 已启动后 arch 编译失败会被错误覆盖为 `cpu-assertions`。 | `medium` / `patch` | 仅在 target 命令退出成功但结果断言不符时使用 `cpu-assertions`；故障注入测试验证 arch 编译失败仍报告 `test_arch_rv64ui_add`。 |
| 12 | 指定 stdout/stderr 路径写入失败时缺少结构化结果。 | `medium` / `patch` | 与 finding 7 同属日志持久化问题；归档 fallback 和故障注入测试覆盖此路径。 |
| 13 | manifest 持久化测试没有验证已有 Heliodor run records 会被保留。 | `medium` / `patch` | 新回归先写入历史记录，再运行并断言旧记录及新记录都保留；25 项 runner 测试通过。 |

## Design Notes

共享 runner 要保留“复制哪些 harness 文件、删除哪个 debug target、在哪个 DRAM 声明处增加 lint allow”的显式白名单和基线检查。这样将来调整隔离方式时可以发现上游 harness 漂移，而不是静默扩展变换范围。

## Verification

**Commands:**
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests/test_heliodor_smoke.py scripts/tests/test_run_cpu_smoke.py` -- 审查修复后的全部回归通过，包含实际 Veryl 双 target 运行。
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH python3 experiments/heliodor-smoke/run.py --timeout 180` -- `heliodor-core-20261014T054447Z-2477026` 的 `test_smoke` 和 `test_arch_rv64ui_add` 均实际启动并通过；结果为 x10=7、x11=11、x12=77、x13=11，且 arch target `tohost=1/pass=1`。
- `uv run --no-cache python scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml`、`python3 scripts/check_doc_links.py`、`git -C sources/heliodor status --short` -- manifest 有效、链接有效、源 checkout 清洁。
