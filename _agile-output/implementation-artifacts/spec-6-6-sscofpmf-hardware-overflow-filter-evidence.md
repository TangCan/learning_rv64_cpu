---
title: 'Story 6.6：运行 Sscofpmf 硬件计数器溢出与过滤对照'
type: 'feature'
created: '2026-10-14'
status: 'done'
baseline_commit: 'db2dd7a4961d217285c060c53967e5379fbfe66a'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-5-4-compare-sscofpmf-overflow-filter.md'
  - '{project-root}/notes/units/rva23s64-sscofpmf-v1.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** 静态 RTL 和软件写入 CSR 不能证明硬件性能事件导致的计数器溢出、过滤、`scountovf` 可见性以及 LCOFI 中断交付真实发生。Epic 5 已列出双核路径和未覆盖项；本故事要在固定快照上运行并给出边界明确的 CPU 观察证据。

**Approach：** 扩展现有 Kunminghu fixture runner 和 Heliodor 隔离 arch harness，使用已确认可触发的硬件事件、明确的 counter/event/模式配置，记录从事件计数到 OF、pending、trap 的逐项观察。对不能运行或实现未支持的组合保留精确阻塞理由，并将结果回写 Sscofpmf 学习单元和覆盖目录。

**Always：** 每项证据记录 locked revision、fixture/隔离输入摘要、配置、事件选择器、counter 预载值、特权模式、命令、工具版本、退出码、CPU-start、输出路径与哈希。区分构建阻塞、CPU 已启动的断言失败和通过；OF 必须由硬件事件增量产生。分别记录 OF 清除/re-arm、`scountovf`、LCOFIP、使能/委托和 cause 13，不将这些阶段混作一个结论。保留 MINH、SINH、UINH、VSINH、VUINH 全部模式的覆盖项；未支持或不可达也须有证据。

**Never：** 不改动 `sources/` 上游快照，不把软件写 counter 后回绕算作硬件溢出，不把 ACT4/Sail 配置当 DUT 运行证据，也不宣称 RVA23 符合性或认证。工具或 harness blocker 不得标作 CPU `run-fail`。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 硬件事件触发 wrap | 选择可观察事件；counter 预载到最大值附近；启用计数 | 记录计数变化、OF、scountovf、pending/trap 顺序和 cause | 首条失败阶段及是否已首条指令提交都写入归档 |
| 过滤/清除重布防 | 五种 xINH 模式逐项配置，包含 OF clear 与再次硬件 wrap | 每项记录 counter/OF/LCOFI 的期望与观察；不支持项列出实现证据 | 不可达模式标为 blocked/unverified，禁止从静态实现推断运行结果 |
| 模型工具对照 | ACT4、Sail 的固定配置及可用 coverpoint | 单列工具版本、生成输入和模型结果，与 DUT 结果分开 | 缺少模型/工具时记环境 blocker，不影响 CPU 结果分类 |

</frozen-after-approval>

## Code Map

- `experiments/kunminghu-smoke/run.py`、`fixture.S`、`fixture.ld`：复用固定配置模拟器启动、输入编译和归档模式；增加可选 Sscofpmf 定向用例/结果解析，不改变已有 smoke/Sstc 行为。
- `experiments/heliodor-smoke/run.py`：复用隔离源码副本、工具清单校验和结果归档；将 Sscofpmf arch harness 的测试台变换限定在副本中，并保留原始输入哈希。
- `sources/heliodor/test/sscofpmf/sscofpmf_test.S`、`sources/heliodor/tb/test_arch_common.veryl`：现有 counter 3/event 5 样例与 200000-cycle 入口；只能作为只读 fixture 来源，针对测试台问题在临时副本实施变换。
- `notes/units/rva23s64-sscofpmf-v1.md`：规范边界、活动实现路径、历史静态证据和本轮 CPU 运行矩阵；新增运行结果，不抹除历史“未运行”语境。
- `notes/rva23-coverage.md`、`scripts/check_rva23_coverage.py` 及测试：同步两侧学习状态、证据链接和派生计数。
- `notes/units/evidence/cpu-validation-toolchain-v1.yaml` 与 `scripts/run_cpu_smoke.py`：工具 pin、manifest schema 和公共归档验证。

## Tasks & Acceptance

**Execution：**
- [x] `experiments/kunminghu-smoke/` -- 为 Sscofpmf 增加可选、可解析的 fixture；使用活动 HPM event source，不假设事件编号，分别保留不适用的过滤模式证据。
- [x] `experiments/heliodor-smoke/run.py` -- 加入 `test_arch_sscofpmf` 运行路径；临时 harness workaround 必须可审计，并解析可观察的硬件结果而非只看退出码。
- [x] `experiments/*` runner tests -- 覆盖 CPU 未启动、启动后断言失败、OF 软件预置、filter 不支持和 ACT4/Sail 缺失等边界，确保结果分类不能误报为硬件通过。
- [x] `notes/units/rva23s64-sscofpmf-v1.md`、`notes/rva23-coverage.md` 和覆盖检查器测试 -- 汇总两核 run matrix、阻塞/失败边界、ACT4/Sail 对照和证据引用；更新精确状态计数。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` 与本规格 -- 验收与复审收尾后规格标记 done，sprint story 保持 review 供后续开发评审。

**Acceptance Criteria：**
- Given 已锁定的两份 CPU 快照和可触发的硬件事件，when 运行定向 fixture，then 按核记录 event selector、counter 值/预载、特权模式、OF、`scountovf`、pending/interrupt、trap cause 和观察顺序；未启动 CPU 的运行标为 blocked。
- Given counter 已因硬件事件置 OF，when 测试清除并重新产生溢出，then 记录清除操作及再次触发结果；软件写入 counter 不可满足该条件。
- Given MINH/SINH/UINH/VSINH/VUINH 与访问/委托控制，when 逐项运行可达组合，then 每项有输入、期望、观察和归档；其余组合有具体实现或 harness blocker，不留静默缺项。
- Given ACT4/Sail 不能执行或没有相关 coverpoint，when 汇总结果，then 精确记录工具/模型支持及阻塞，并与 CPU 运行结果分栏。
- Given 故事结项，when 执行覆盖/证据检查和相关脚本测试，then 所有本轮文档链接、证据 ID、状态汇总及计数通过校验，且没有把有限案例外推为 profile 符合性。

## Implementation Notes

- Kunminghu fixture `kunminghu-sscofpmf-complete-v5.S` 在锁定配置上通过硬件 event2/counter3 wrap；逐项断言五种 xINH 抑制/恢复、cause 13、OF/scountovf 置位与清除、独立 LCOFIP 清除及第二次硬件回绕投递。E9 的完整 record 在 toolchain manifest，完整输出另存 run log。
- Heliodor 原始隔离 `test_arch_sscofpmf`（E8）通过 event5/counter3 的 MINH 与首次硬件 wrap/cause13/OF/scountovf 案例；测试台变换只作用于隔离副本。扩展 v2–v4 尝试单独观察 MIP.LCOFIP、OF 清除/re-arm；最新 v4 CPU-started `run-fail`，cause 13 已进入但 OF 断言失败，记录为 E12，不覆盖 E8 的历史 pass。最新 S/U 矩阵 E14 对 event5/counter3 分别运行 S/SINH 与 U/UINH 的置位及清除阶段：两个置位阶段 counter 均为 0，清除阶段仍为 0，两个清除断言失败；这只表明该配置下结果不符合 fixture 预期，不外推至其他事件源。Heliodor 的 S/VS `scountovf` 可见性和 delegation 仍无动态证据。
- 回归测试验证 CPU 未启动、启动后断言不匹配、fixture 未软件预置 OF、Heliodor VS/VU filter 未实现以及 ACT4/Sail 缺少 Sscofpmf 的边界。全量 `scripts/tests` 178 项通过、1 项 opt-in Kunminghu integration skipped；覆盖检查器为 valid，manifest validator 通过，`git diff --check` 通过。
- 所有有限运行结果仅描述所记录快照、配置、事件和访问路径。Kunminghu 已覆盖 counter3 的 S/VS `scountovf` gate 与 S-mode delegation；Heliodor 的对应权限矩阵和 delegation、同拍 clear/overflow 优先级及 ACT4/Sail 专题运行仍未覆盖；不构成 RVA23 符合性或认证结论。

### E9/E10 evidence matrices and reproduction notes

- **E8 metadata and observation boundary:** the archived record includes snapshot/input hash, controls (event5, counter3, width/preload, M-mode, MINH phases, cause 13), configuration, command, tool versions, exit/start state, output hash, and artifact hashes. Observed values contain tohost/pass plus an assertion summary; counter/cause/OF/scountovf are fixture-checked and not individually printed as raw CSR values.
- **E9 Kunminghu xINH matrix:** event2/`ifu_req`, counter3, 64-bit all-ones preload. M `MINH=1` expects no increments and `MINH=0` expects increments; S/SINH, U/UINH, VS/VSINH, VU/VUINH each expect no increments with the bit set and increments after clearing it. Assembly reads counter values and branches on each result; reaching good-trap means all assertions passed. The run does not print each raw CSR value. The unit's E9 matrix links the immutable input, log, and manifest record.
- **E10 Kunminghu access/delegation matrix:** with OF set by hardware, M expects `scountovf[3]=1`; S expects 0/1 with `mcounteren[3]` off/on; VS expects 0 when either `hcounteren[3]` or `mcounteren[3]` is off and 1 when both are on. Then `mideleg[13]`, delegated LCOFIE and SIE are enabled; the S handler asserts interrupt cause 13, `scountovf[3]=1`, and `sip.LCOFIP=1`. These are fixture branch assertions, not per-case raw CSR values printed in the log. The unit links the immutable input, log, and manifest record.
- E8's complete `run-metadata.json`, archive directory, and output log are linked from the unit evidence table. Heliodor's VS/VU static filter gap is at `sources/heliodor/src/core/csr.veryl:1213–1222` (E3); E7 directly links the ACT4 DUT and Sail config files. Manifest validation ran as `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` with Python 3.12.3.
- Kunminghu exploratory access-route runs `101412`, `101612`, `101753`, and `101845` ended in CPU run-fail while diagnosing trap enable and fixture ordering. Their separate fixture inputs/logs remain because manifest records bind their SHA-256 hashes. They are diagnostic history, not acceptance evidence; E10 `101934` and E11 `135231` pass the access-route assertions, including S-visible `sie.LCOFIE`. E9 `complete-v5.S` is the accepted five-filter case; the v5 access-route first compile attempt remains bound to its archived original input, while the corrected v6 fixture passes as E11 and checks S-visible `sie.LCOFIE`. Earlier variants remain immutable where recorded.
- Latest manual reruns: Kunminghu access-route v6 ID `kunminghu-fixture-20261014T135231Z-a88d5b9d673c` is `run-pass`; Heliodor extended v4 ID `heliodor-core-20261014T135548Z-3090096` is `run-fail` at OF readback after cause-13 entry; E13 is an incomplete diagnostic run, superseded for S/U acceptance evidence by E14 ID `heliodor-core-20261014T142410Z-3235815`, a CPU-started `run-fail` with both S/U clear-phase assertions failing (`tohost=0x14`). Its matrix fixture, manifest record and output log are archived. Manifest validation succeeds after restoring the v5 failed-build source hash and pinning the corrected fixture at v6.
- `RUN_KUNMINGHU_SSCOFPMF_REGRESSION=1 uv run --no-cache pytest -q scripts/tests/test_kunminghu_smoke.py -k fixtures_repeatable` runs both `hardware-filter` and `access-route` with a temporary manifest and separate evidence directories under the repository, then removes them. It does not write to the official manifest or evidence directory.

## Spec Change Log

- 2026-10-14：Story 由 `review` 收尾为 `done`。Kunminghu access-route v6 通过并增加 `sie.LCOFIE` 读回断言；Heliodor E12/E14 的 CPU-started 断言失败作为有界行为观察保留，原始 E8 pass 不被覆盖。E14 补齐 S/U inhibit-on/off 动态观察；结项不要求 DUT 通过每个架构预期，但要求失败、未覆盖和工具边界均可追溯，且不外推为符合性结论。

## Review Triage Log

| Finding | Verdict / evidence | Route |
|---|---|---|
| BH1: review diff carries roughly 158 MB of intermediate logs/binaries; current Kunminghu evidence subtree is about 620 MB | **medium** — confirmed by disk inspection. These outputs are individually hash-bound in the manifest and removing them would invalidate diagnostic run records; they add clone/storage cost. Deferred compression/cleanup with manifest-hash and validator updates. | defer |
| BH2: E8 summary omits its control and run metadata fields | **low** — the underlying E8 record does contain preload, privilege, event/counter, command, tools, exit/start, output hash, and artifact hashes; the unit's concise row did not enumerate them. Added a field inventory and linked record. | patch |
| BH3: E9 five-mode filter matrix lacks per-mode expectations, observations, and archives | **medium** — prior summary did not list each xINH phase or its evidence method. Added one row per mode with expected zero/nonzero counter behavior and immutable input/log links. | patch |
| BH4: E10 gate combinations and unreachable boundary are not itemized | **medium** — prior summary omitted the S/VS gate cross-combinations and whether any were blocked. Added the tested combinations and clarified the tested subset. | patch |
| BH5: E8 pass text does not distinguish fixture assertions from raw observed CSR values | **low** — metadata/log show tohost/pass and an assertion summary, not individual counter/cause/OF/scountovf read values. Added that boundary explicitly. | patch |
| BH6: Heliodor VS/VU filter gap lacks precise source citation | **low** — static claim verified at `csr.veryl:1213–1222`; linked this range from E3. | patch |
| BH7: E7 ACT4/Sail blocker lacks direct config links | **low** — linked the ACT DUT YAML and Sail JSON at the relevant lines; config lacks Sscofpmf / marks it unsupported. | patch |
| BH8: validator command and Python runtime are absent | **low** — added the exact manifest validation command and observed Python 3.12.3. | patch |
| BH9: spec and sprint status disagree | **medium** — spec is `in-review` while the sprint story said `in-progress`; changed sprint status to `review`, not `done`. | patch |
| BH10: fixture variants and diagnostic runs lack a retention explanation | **low** — added run IDs, failure purpose, and explanation that fixture input/log hashes are manifest-bound; only E9/E10 passing cases count as acceptance evidence. | patch |
| Edge1: SSCOFPMF expected marker uses generic smoke marker | **low** — current runner record builder used `[test_smoke] PASS` although the arch target emits `sscofpmf PASS`; fixed selection and added a unit test. | patch |
| Verification1: no repeatable Kunminghu CPU fixture regression check | **medium** — source-only tests did not prove either selected case still runs. Added opt-in test that runs both `hardware-filter` and `access-route`, checks each manifest result/case, and cleans its temporary manifest/evidence tree. | patch |
| Acceptance: Heliodor LCOFIP was not independently read and clear/re-arm had no evidence | **bounded run-fail recorded** — local v2–v4 fixtures added MIP checks and a second-wrap path; v4 started the CPU but failed its OF assertion (E12). The evidence task is closed as a documented outcome; this does not claim the extension passed. | done with explicit behavior boundary |
| Acceptance: Heliodor S/U filter paths lacked dynamic evidence | **bounded run-fail recorded** — E14 runs both S/SINH and U/UINH inhibit-on and inhibit-off phases. Both inhibit-on checks observed counter=0; both inhibit-off checks also observed counter=0 and are encoded as failed assertion bits (`tohost=0x14`). E13 remains diagnostic history only. The evidence is limited to event5/counter3 and does not establish behavior for other events. | done with explicit behavior boundary |

## Verification

**Commands：**
- `python3 experiments/kunminghu-smoke/run.py --help` 与 `python3 experiments/heliodor-smoke/run.py --help` -- 新增参数可发现，原参数兼容。
- `python3 scripts/check_rva23_coverage.py` -- 覆盖状态、链接和派生计数一致。
- `uv run --no-cache pytest -q scripts/tests` -- 相关项目脚本测试通过。
- `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" uv run --no-cache pytest -q scripts/tests` -- current result 178 passed, 1 skipped (opt-in Kunminghu CPU integration check).
- Latest manual reruns: Kunminghu access-route v6 ID `kunminghu-fixture-20261014T135231Z-a88d5b9d673c` is `run-pass`; Heliodor extended v4 ID `heliodor-core-20261014T135548Z-3090096` is `run-fail` at OF readback after cause-13 entry; Heliodor S/U matrix E14 ID `heliodor-core-20261014T142410Z-3235815` is CPU-started `run-fail`, `tohost=0x14`, with both clear-phase counter assertions failing. E13 is retained as incomplete diagnostic history. Manifest validation succeeds after restoring the v5 failed-build source hash and pinning the corrected fixture at v6.
- `RUN_KUNMINGHU_SSCOFPMF_REGRESSION=1 PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests/test_kunminghu_smoke.py -k fixtures_repeatable` -- 1 passed, 56 deselected; both fixture cases recorded run-pass in a temporary manifest, whose evidence hashes validated, then the temporary evidence tree was removed.
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- valid, Python 3.12.3.
- `python3 scripts/check_doc_links.py` -- 38 documents valid.
- `python3 scripts/check_rva23_coverage.py` -- valid: 92 profile rows, 184 status cells.
- `git diff --check` -- 无空白错误。

**Manual checks：** 每份 run record 可追溯 revision、输入 hash、工具版本、完整日志和 CPU-start 分类；硬件 wrap 证据包含事件计数路径而不是软件强制 OF。
