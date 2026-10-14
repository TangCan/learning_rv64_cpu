---
title: 'Story 5.6：比较 Ssstateen 状态访问门控'
type: 'feature'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '03a1141739e788ea9bfe76f644eac5aa6c7453df'
context: ['{project-root}/_agile-output/implementation-artifacts/epic-5-context.md', '{project-root}/sources.lock']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** RVA23S64 要求 `sstateen0–3` 与 `hstateen0–3`；当前仅有 Kunminghu 局部静态线索和 Heliodor 有限负搜索，双核行为未核实。

**Approach：** 对照固定快照和规范追踪八 CSR、权限/陷阱，以 `SE0`、`ENVCFG` 检查允许/阻止行为。

**Always：** 覆盖八 CSR、M/H 控制及适用特权层；记录 reset/WARL/RO-zero，不外推代表位。

**Never：** 不改 `sources/`；不以负搜索、ACT 配置、源码存在或读零单独判定支持/缺失；不声称符合性或认证。

## I/O & Edge-Case Matrix

| 场景 | 输入 | 预期记录 |
|---|---|---|
| CSR 读写 | M/H/S/VS/VU 访问八个 CSR | 初值、读回、写回、trap cause；区分 illegal/virtual-instruction，读零不视为支持 |
| 门控 | 设置/清除 SE0、ENVCFG | 记录预期/观察；未到达模式标未决 |
| WARL/RO-zero | 写字段及保留位 | 逐 CSR 记录读回和未测阻塞 |

</frozen-after-approval>

## Code Map

- 规范：[Profile §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html) 要求 S/H CSR；[Smstateen/Ssstateen v1.0](https://docs.riscv.org/reference/isa/v20260120/priv/smstateen.html) 定义 WARL/RO-zero、reset 与分层控制。
- 快照（实施前核对）：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a` (`sources.lock`)。
- Kunminghu 活动链：`wrapper/CSR.scala:65` → `NewCSR.scala:100-115`。八 CSR 定义于 Machine/Supervisor/HypervisorLevel；字段在 `StateEnBundle.scala:8-49`，SE0/ENVCFG 门控在 `CSRPermitModule.scala:238-252,452-466`，陷阱输出在 `NewCSR.scala:1106-1114`。
- Heliodor ACT `sail.json:746-750` 标 unsupported；CSR 通用权限/读写/陷阱：`src/core/{alu_wrap.veryl:446-466,csr.veryl:497-592,1047-1161,rob.veryl:1339-1343,heliodor_core.veryl:4397-4458}`。Harness `tb/test_arch_common.veryl:10-22`；负搜索不证明缺失。
- 工具：Veryl `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl`，GCC 可用。Veryl 0.22.0 的 `test_arch_hvscsr` 在 `tb/test_arch_common.veryl:440` 因 `$readmemh`/`dram` check 退出 1，仿真未启动；实验须用隔离 harness。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-ssstateen-v1.md` — 八 CSR、位/门控、层级、双核差异、自检和证据边界。
- [x] `experiments/ssstateen/` — 保存受控访问用例、输入及构建/运行记录，不改上游。
- [x] `notes/rva23-coverage.md`、`notes/units/index.md`、`notes/units/rva23-mandatory-coverage-audit-v1.md` — 同步要求状态和证据链接。

**Acceptance Criteria：**
- Given 规范，when 建清单，then 列出八 CSR、字段、reset、WARL/RO-zero 读写结果或逐项阻塞，并区分静态/运行证据。
- Given Kunminghu 配置，when 追踪八 CSR，then 记录活动路径、读写/位映射及权限结果。
- Given Heliodor，when 检查 CSR/通用路径，then 记录搜索范围及受控访问，并按证据标 supported/absent/unresolved；负搜索不作缺失证明。
- Given 可运行路径，when 测 SE0/ENVCFG，then 记录适用 M/HS/S/VS/VU 层级的允许/阻止、预期/实际 trap、控制值、命令和产物；未测项说明原因。
- Given 单元完成，when 复习，then 能解释双核差异且覆盖表链接证据。

## Verification

- 核对两边 checkout SHA；为 KunminghuV2Config 尝试现有 CSR 仿真入口，记录工具、命令和阻塞/结果。
- GCC 构建 Heliodor 用例；运行 Veryl `test --test test_arch_ssstateen`，区分 build、check、simulation 阶段结果。
- `python3 scripts/check_rva23_coverage.py`、`python3 -m pytest -q scripts/tests/test_check_rva23_coverage.py`、`git diff --check`。

## Implementation Notes

- 对照 `sources.lock` 核实 Kunminghu、Heliodor 固定 SHA。Kunminghu `make emu` 因缺 `mill` 未进入构建；Heliodor 原有 hvscsr test 在 Veryl check 阶段因公共 testbench `$readmemh`/`dram` 初始化错误未启动。以隔离副本运行自建 M/HS 用例，实际观察为 run-fail：stateen 读回为零、20 项预期 gate trap 未发生、仅有 HS ecall cause 9；VS/VU 未测。
- GCC fixture 构建、Veryl 隔离测试和覆盖检查结果见 [`notes/units/rva23s64-ssstateen-v1.md`](../../notes/units/rva23s64-ssstateen-v1.md) 与 [`experiments/ssstateen/README.md`](../../experiments/ssstateen/README.md)。未改 `sources/`。

## Spec Change Log

### Review Findings

- [x] Review/Patch 为每次 stateen/ENVCFG gate trap 检查 `mcause`，区分非法指令与 ecall [experiments/ssstateen/run_isolated.py]
- [x] Review/Patch 为 20 次受控访问写入独立 operation ID，输出 trap 对应操作位置 [experiments/ssstateen/ssstateen_probe.S]
- [x] Review/Patch 断言 M/HS 对八个 stateen CSR 写回后的定义 SE0 bit63，同时保留 reset/WARL trace [experiments/ssstateen/run_isolated.py]
- [x] Review/Patch 断言明确的总 trap 数、cause 顺序、操作编号与功能 marker [experiments/ssstateen/run_isolated.py]
- [x] Review/Patch 在 cause/operation-ID 记录前增加容量保护，并扩大报告区避免数组覆盖 stack [experiments/ssstateen/ssstateen_probe.S]
- [x] Review/Patch 更新单元证据说明，反映唯一临时目录、assert、最终输入与实际 run-fail 日志 [notes/units/rva23s64-ssstateen-v1.md]
- [x] Review/Patch 重建 fixture 并记录添加逐项断言后的 Veryl exit 1 和 0 passed/1 failed [experiments/ssstateen/README.md]

Rejected:
- Blind Hunter 4 (false): `henvcfg`/`senvcfg` 原始读回仍完整保存在 trace；此 story 的断言针对 stateen gate 与已定义 SE0，而不对各自 WARL/保留位的全值作无规范依据的预设。
- Blind Hunter 6 (false): 添加逐项断言后已重新运行隔离 target，保存 exit 1 及确切 assertion failure 和观察 trace。

## Review Triage Log

| Verdict | Finding and evidence |
|---|---|
| false | Blind Hunter claimed repository links resolve from root only if files are relocated. The links in `notes/units/rva23s64-ssstateen-v1.md` are relative to that note (for example `../../sources/...`) and resolve correctly from `notes/units/`; the spec and experiment paths are existing repository paths. |
| medium — patch | Blind Hunter found `run_isolated.py` recursively deleting the predictable `/tmp/heliodor-ssstateen-isolated` path. This could remove unrelated or retained evidence at that location; changed to allocate a unique temporary directory and README now consumes the printed path. |
| low — patch | Blind Hunter found E8 mixed a Kunminghu build blocker, Heliodor pre-run blockers, and an isolated runtime failure under one `run-fail` label. Split into E8 `blocked` build/check evidence and E9 `run-fail` runtime evidence so the coverage table does not imply blocked attempts ran. |
| false | Blind Hunter questioned the two `evidence-observed` cells alongside the new `not-present` cell. The checker counts implementation status cells independently; the Ssstateen classification is `not-present`, and the unit note scopes that label to the checked static path plus its M/HS fixture. |
| false | Blind Hunter asked to change the approved mode criterion or add VS/VU runs. The frozen matrix explicitly says to mark unreachable modes unresolved with a reason; VS/VU remain unresolved in the unit note, and no claim of complete runtime coverage is made. Editing the approved spec is not an allowed fix in this review. |
| false | Blind Hunter said the aggregate trap trace cannot identify whether individual gate operations trapped. The fixture records a total trap count of one and the sole cause as HS `ecall` cause 9; together these show none of the 20 gate operations trapped, while per-CSR readback slots are separately recorded. |
| medium — patch | Verification Gap Reviewer found the generated test could finish successfully without asserting the normative expected marker. Added an assertion for `tohost == 0x2B` after trace printing; isolated Veryl run now exits 1 with the expected assertion failure for the observed `0x02`, making run-fail machine-visible while preserving trace output. |
| false | Blind Hunter asked for more static evidence in the Heliodor M CSR table cell. The cell records the observed all-zero M writes/readbacks and the surrounding Heliodor section explicitly documents missing read/write cases and default read-zero/write-ignore behavior; the conclusion is bounded to the checked path. |
| false | Blind Hunter said field constraints could be mistaken for runtime WARL verification. The table distinguishes static field definitions from absent runtime write/read observations, and the unit's unresolved list explicitly leaves per-field WARL/reset behavior unverified. |
| low — patch | Blind Hunter found harness-source `.replace(..., 1)` calls could silently miss an anchor after upstream source drift. Added `replace_once` checks that require exactly one match and abort otherwise, preventing generation of an incomplete trace harness. |
| medium — patch | Verification Gap Reviewer found the Veryl test runner could report a passed test despite a failed functional observation because the module had no assertions. This is the same root cause as the blind review's missing-assertion finding; the new expected-marker assertion makes the functional failure produce a nonzero test result. |

The two missing-assertion findings are retained as separate findings above and grouped under one patch root cause: the generated test did not make its functional outcome affect the test result.

