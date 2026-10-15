---
title: 'Story 6.8：运行 Ssstateen 八 CSR 与层级访问门对照'
type: 'feature'
created: '2026-10-14'
status: 'done'
baseline_commit: '2107400a5b1122131dea0cd865f9739bbf7ed65c'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-5-6-compare-ssstateen.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-6-7-run-ssnpm-pmlen-access-families.md'
  - '{project-root}/notes/units/rva23s64-ssstateen-v1.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** Story 5.6 已有静态路径和 Heliodor M/HS 失败观察，但 Kunminghu 尚无 CPU 运行结果，VS/VU、逐 CSR/WARL 和层级门控证据也不完整；Heliodor 旧运行需要用稳定输入摘要重新核对。

**Approach：** 在锁定的 Kunminghu 与 Heliodor 快照上执行可复查的 Ssstateen 对照，逐操作记录模式、操作 ID、规范预期、实际读回值或 trap，并分别报告运行、阻塞与未验证范围；用 fixture SHA 将 Heliodor 新运行与耐久基线比较。

**Always：** 覆盖 `sstateen0–3`、`hstateen0–3` 的规范定义 reset 可见值、读写/WARL 位及 M/H/S/VS/VU 可适用访问路径与 gates clear/set。每个实际执行的 CSR 操作记录 operation ID、预期与观察值或 trap cause、执行模式；报告每个模式/门控组合的状态。保存源快照、fixture SHA、工具版本、精确命令、CPU-start 判定、退出码、日志和产物摘要。Kunminghu 与 Heliodor 结论独立呈现。只有 CPU 已启动且断言观察到语义不符，才报告 CPU `run-fail`；harness、构建或 preflight 阻塞另行分类。

**Never：** 不修改 `sources/` 锁定快照；不把构建/启动前阻塞称为 CPU 失败，不以测试框架退出码代替架构结果，不把未执行模式或 WARL 位标为通过；不将两个核的结果合并推断，不宣称 RVA23 符合性或认证，不缩减八 CSR 与 M/H/S/VS/VU 的已批准故事范围。

## I/O & Edge-Case Matrix

| 场景 | 输入/状态 | 预期/观察 | 失败处理 |
|---|---|---|---|
| CSR reset 与 WARL | 八 CSR；按规范区分 reset 可见值、RW、RO-zero、WARL/保留位 | 记录逐 CSR 读回和写后读回，不预设规范未定义值 | 按字段限定预期；无法执行则标具体 blocker/unverified |
| M/HS/S gate | M `SE0/SE`、`ENVCFG` 清零/置位及适用 CSR 操作 | 每个操作记录 ID、mode、预期与读回/异常 | trap cause 和 faulting operation 必须可关联；CPU 未启动标 blocked |
| VS/VU gate | H `SE0/SE` 与适用 virtual CSR / 受控扩展状态访问 | 区分 virtual-instruction、illegal-instruction、读写结果及各模式覆盖 | 未能进入 guest 或缺少 fixture 时列明前置阻塞，不外推为通过 |
| Heliodor 基线复跑 | 锁定快照、fixture SHA、隔离 harness 与耐久日志 | fixture SHA 相同后对照稳定架构观察字段；按实际断言报告状态 | SHA 不同不得作同输入行为比较；意外结果保留并分类 |
| Kunminghu 矩阵 | 固定快照与 matching preflight/runner | 独立记录 CPU-start、各访问案例和 assertion 观察 | preflight/build 失败不计 CPU run-fail；仅运行断言不符才计 run-fail |

</frozen-after-approval>

## Code Map

- `experiments/ssstateen/ssstateen_probe.S`、`run_isolated.py`、`README.md`：现有 Heliodor M/HS fixture、隔离复制和 gate 断言；复核其输入和日志哈希比较能力并扩展必要用例。
- `experiments/kunminghu-smoke/run.py`、`fixture.ld`、`scripts/tests/test_kunminghu_smoke.py`：复用固定快照的 preflight、构建/运行分类及归档入口；目前没有 Ssstateen topic。
- `sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/{StateEnBundle.scala,MachineLevel.scala,SupervisorLevel.scala,HypervisorLevel.scala,CSRPermitModule.scala,NewCSR.scala}`：固定 SHA `c098f996bf4d301b88693b20315486d31e93bc9d` 的八 CSR 字段、映射、读掩码和访问门控静态路径。
- `sources/heliodor/src/core/{csr.veryl,alu_wrap.veryl,heliodor_core.veryl}`：固定 SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a` 的 CSR 状态/权限与隔离 arch harness 路径；不修改上游快照。
- `notes/units/rva23s64-ssstateen-v1.md`、`notes/rva23-coverage.md`、`notes/units/index.md`、`notes/units/evidence/cpu-validation-toolchain-v1.yaml`：需同步分层矩阵、运行状态、证据索引和可复查归档。

## Tasks & Acceptance

**Execution：**
- [x] `experiments/kunminghu-smoke/`、对应 tests 与最小 fixture -- 固定快照的 Ssstateen preflight/运行矩阵按模式和 operation ID 记录期望、读回/陷阱；覆盖 M/HS、S 四槽、VS 四槽及 H.ENVCFG clear/set。run `155020Z` 增加并自检 Kunminghu 全部 21 个实现可写 stateen 字段的 one-hot 写读回。VU FCSR gate 不适用：动态 MISA.F=1 且 FCSR controls 为规范 RO-zero；U-custom CSR `0x800` 未实现，illegal-instruction 优先于 virtual-instruction，故 VU custom-state gate 标记 `unverified` 并给出可复现原因。S/H 未定义 reset 位只记录观察。
- [x] `experiments/ssstateen/`、对应 tests -- 固定 Heliodor SHA 的隔离 fixture 与 durable baseline 已复跑；八个要求 CSR 的 M/HS/S/VS/VU 适用路径有 operation records 和动态观察。Heliodor CSR 主路径没有 stateen 状态/map，M/H/S gate set 写回仍为 0；gate-open 不可达，按规格标明为 `run-fail`/`unverified`，不是 pass。VU direct supervisor CSR cause 2 是权限陷阱；FCSR 使用已测但 H.FCSR 写读 0，因此无 gate 对照。其余未实现/保留字段依据 RTL 默认读零/写忽略路径分类，不外推合规。
- [x] `notes/units/rva23s64-ssstateen-v1.md` -- 更新八 CSR 的逐项、逐模式运行矩阵与证据边界，分别解释两个快照结果。
- [x] toolchain manifest、`notes/rva23-coverage.md`、`notes/units/index.md` -- 归档 inputs/outputs 和命令/工具/快照摘要，同步状态与索引，维持既有验证器一致。

**Acceptance Criteria：**
- Given 八个要求 CSR 及规范定义的 reset/WARL 位，when 执行可用读写案例，then 每个实际 CSR 操作都有唯一 ID、模式、预期与观察值或 trap，未定义/保留位不被错误固定为某个值。
- Given M/H/S/VS/VU 适用的层级门控状态，when 清除与开启对应 gates 并执行访问，then 按模式记录各 CSR 和受控状态访问；未实际运行的组合明确标注原因，不从其他模式推断。
- Given 固定 Heliodor fixture 与 durable baseline，when 使用隔离 harness 重跑，then 输入 SHA 相同才比较稳定观察字段；结果保持 `run-fail`，除非新的架构观察满足预期断言。
- Given 固定 Kunminghu snapshot 与匹配 preflight runner，when 执行同范围矩阵，then 独立报告每案例状态；只有 CPU 已启动且断言观察到行为不符才记 CPU `run-fail`。
- Given 所有规格、脚本、证据索引更新，when 运行相关测试与 coverage/manifest/link/sprint validators，then 结果可复现、证据哈希有效、状态和计数一致，且没有将 harness 通过误报为 CPU 通过。

## Implementation Notes

- `experiments/kunminghu-smoke/run.py` now accepts `--topic ssstateen --ssstateen-case m-hs-gates-diff` and `--topic ssstateen --ssstateen-case m-hs-selfcheck --no-diff`. Both cases use the locked Kunminghu snapshot preflight, build/link inspection, emulator classification, evidence files, and manifest append. The no-diff case skips NEMU as a differential dependency and records `differential_enabled=false`; this emulator build still initializes its reference proxy, so the runner supplies a run-local alias to the pinned ready-to-run library without enabling comparison.
- Runner accepts a positive `--max-instr` value (default `10000`) and records it in the exact command. A 30,000-instruction no-diff rerun still had no fixture terminal marker. Its output contained no commit-trace records, so all 93 operation records correctly say reachability is unavailable rather than claiming operations were not reached; CPU architectural behavior remains unverified.
- A further no-diff run with `--max-instr 100000`, `kunminghu-fixture-20261014T131636Z-cc7bc34a80d2`, also reached its instruction limit without a fixture terminal marker or usable commit trace; its architectural result remains `unverified`.
- Latest official differential run: `kunminghu-fixture-20261014T155020Z-3e81181d1d02` built, started CPU, passed NEMU differential execution, and reached GOODTRAP (`run-pass`). In addition to the prior all-ones mask assertions and 20 ordered cause-2 HS gate traps, the fixture independently writes and reads every implemented M/H writable stateen field and `sstateen0.C`; all 21 one-hot readbacks match their masks. It records 147 unique operation IDs, including the per-field operations; missing source-register values in the native commit trace are explicitly marked unavailable while the fixture's readback assertion is independently checked before GOODTRAP. A previous field-test attempt `154604Z` was a harness setup failure: H.SE0 was written while M.SE0 was cleared, so its field readback was masked; the fixture was corrected to reopen M gates before lower-level CSR field probes. Earlier no-diff runs stopped at instruction limits without a terminal marker or usable commit trace and remain `unverified`.
- Focused HS/VS runner cases add limited mode evidence: `kunminghu-fixture-20261014T125026Z-62f2a67abbe7` recorded the positive HS/VS path; `kunminghu-fixture-20261014T130024Z-b10452454932` recorded VS H.SE0-clear virtual-instruction cause 22, handler restoration of H.SE0 plus C, all-ones VS write source, defined C-bit readback 1, and VS ecall cause 10. Earlier attempts remain archived with their distinct failures/operation mismatches.
- S-mode runner case `kunminghu-fixture-20261014T132002Z-5d65bb90e90c` recorded S-mode reads, writes, and readbacks for `sstateen0–3`; clearing each corresponding M.SE0–3 gate caused its S CSR read to trap with cause 2, then restoring the gate allowed execution to continue and finish with cause-9 ecall. This covers one clear/set path per S slot, not all WARL fields or all mode combinations.
- Extended VS runner case `kunminghu-fixture-20261014T132255Z-b10452454932` observed all four H.SE clear gates produce VS virtual-instruction cause 22; the updated fixture also counts these traps and the H.ENVCFG case before GOODTRAP. Run `kunminghu-fixture-20261014T152653Z-3e81181d1d02` observed H.ENVCFG-clear VS `senvcfg` cause 22 and readback `0xf0` after restoring H.ENVCFG; the HS handler restored each gate and execution continued through VS writes/readbacks and cause-10 ecall. For slots 1–3, HS CSR readbacks before clearing confirmed `SE=1`. The CPU-native trace omits the `t4` shift update, so those initial write-source records are unavailable; the CSR readbacks establish the values. The earlier `130908Z` attempt is retained but its derived source values were stale and is not used as gate-setting evidence.
- VU runner case `kunminghu-fixture-20261014T130304Z-b0efa44f992a` dynamically read MISA=`0x80000000003411af` (F=1), M/H/S FCSR control values 0, committed a VU `fflags` read, and observed VU ecall cause 8. The implementation declares FCSR controls RO-zero, so this reaches VU and samples FCSR availability but cannot provide a gate-clear/set comparison; it is not counted as a stateen-gate pass. The first attempt `kunminghu-fixture-20261014T130220Z-b0efa44f992a` is retained as a failed setup attempt: M.SE0 was not opened before HS read hstateen0, yielding cause 2 and a double trap.
- Heliodor operation records include mode, expected and observed values, expected/observed cause, and cause status. Reset/WARL values not fixed by normative requirements remain observations, not asserted constants. The `t6/x31` fixture labels and their postprocessing are distinguished from native trace fields.
- Heliodor E12 expands the S gate fixture to all four slots. It reads back M.SE0–3 after clear and set writes, and records per-slot S accesses with unique operation IDs. All clear values are 0; S operations 43–46 complete with readback 0 and no cause 2. All set writes still read back 0, so operations 47–50 do not represent a valid gate-open phase. The isolated target exits 1 on the expected gate assertions and is recorded as CPU-started `run-fail`; E12 supersedes E11 for S-slot coverage. Source, HEX, copied harness, logs, and hashes are in manifest record `ssstateen-heliodor-s-gates-all-slots-20261014`.
- Story enters review after passing full repository verification (`190 passed, 1 skipped` on 2026-10-14) and all manifest/coverage/link/sprint validators. Kunminghu M/HS, S slots 0–3, VS slots 0–3, H.ENVCFG, and one-hot readback for every implemented stateen field have passing runtime evidence. Heliodor has verified M.SE0–3-clear S reads and VS guest reads under H.SE clear plus attempted set; the stateen path has no mapped storage, set writes read back zero, and no gate-open state is available. VU FCSR stateen control is inapplicable when misa.F=1; the attempted user-custom CSR probe is unverified because 0x800 is unmapped and CSR legality takes exception priority; S/H reset bits without defined reset values remain observations, not assertions. Heliodor E15 confirms VU entry, expected cause-2 privilege traps for direct `sstateen` CSR reads, and cause-8 ecall return; E16 confirms VU `fflags` 0→1 read/write/readback with FS=Initial, but H.FCSR write still reads back 0, so no gate comparison is available. These finite paths do not establish profile compliance or certification.


## Spec Change Log


## Review Triage Log

| Finding | Verdict / evidence | Route |
|---|---|---|
| blind-hunter: spec path has an `nvme_data1/...` prefix | **false** — the diff header is `a/_agile-output/...` and the file exists at the repository-relative location. | reject |
| blind-hunter: Ssstateen fixtures are under a nested workspace path | **false** — the files are under `experiments/ssstateen/`, matching runner paths; the Kunminghu run consumed them and reached GOODTRAP. | reject |
| blind-hunter: Heliodor Sscofpmf fixtures are under a nested workspace path | **false** — the files are under `experiments/sscofpmf/`, matching `SSCOFPMF_FIXTURES`. | reject |
| blind-hunter: Story test is under a nested workspace path | **false** — `scripts/tests/test_ssstateen_story.py` is in the normal pytest discovery tree and the full suite collected it. | reject |
| blind-hunter: evidence archives are under a nested workspace path | **false** — evidence lives under repository-relative `notes/units/evidence/...`; manifest validation resolves and verifies its hashes. | reject |
| blind-hunter: compiled outputs inflate the change by about 393 MB | **medium** — generated `.bin`/`.elf` files and diagnostic evidence materially increase repository size; cleaning them requires coordinating manifest-bound artifacts. | defer |
| blind-hunter: default Heliodor test has conflicting `trace[34]` assertions | **medium** — the generated default harness asserted both 3 and 23; removed the stale 3 assertion, retaining the 23-trap expectation. | patch |
| blind-hunter: `s-gates-v3` has conflicting `trace[34]` assertions | **medium** — the generated v3 harness asserted both 6 and 9; aligned the earlier check to the four-slot expected count of 9. | patch |
| blind-hunter: importing `run_isolated.py` parses the caller's CLI arguments | **low** — import-time `parse_args()` could exit on unrelated flags; parsing now uses an empty argument list when imported. | patch |
| blind-hunter: completed tasks imply all modes passed despite failed/unverified results | **false** — the execution checklist records evidence collection; its task text and AC explicitly classify Heliodor `run-fail`, VU `unverified`, and gates that cannot open, without calling them passes. | reject |
| verification-gap: Heliodor `mode-filters` lacks a joined runner-path test | **medium** — tests cover components but do not jointly assert selected fixture, manifest case, and cycle budget; this is the existing Story 6.6 runner path and is outside Story 6.8's stateen scope. | defer |


## Verification

**Commands：**
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests` -- expected: all tests pass; report CPU fixture outcomes separately.
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- expected: archived evidence hashes validate.
- `python3 scripts/check_rva23_coverage.py && python3 scripts/check_doc_links.py` -- expected: coverage and local links validate.
- `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` -- expected: sprint status valid.

**Latest output：**
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests` -- `190 passed, 1 skipped` in 112.74s on 2026-10-14 after the one-hot CSR/parser changes; skipped case is opt-in Kunminghu CPU integration.
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- valid after current Epic 6 evidence additions.
- Heliodor E16 `--case vu-fcsr` -- CPU started; VU `fflags` read 0, write 1, readback 1 without a trap; terminal ecall cause 8; H.FCSR set attempt readback 0, so no gate comparison. Manifest record `ssstateen-heliodor-vu-fcsr-20261014`.
- `python3 scripts/check_rva23_coverage.py` -- valid; 92 profile rows, 184 implementation cells, 59 deduplicated requirements.
- `python3 scripts/check_doc_links.py` -- valid; 38 documents.
- `uv run --no-cache --with ruamel.yaml python .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` -- valid with no problems.
- `git diff --check` -- clean.
- Heliodor S gate rerun: `make -C experiments/ssstateen ssstateen_probe_s_gates_v3.hex`; `python3 experiments/ssstateen/run_isolated.py --case s-gates-v3`; `veryl test --test test_arch_ssstateen` -- CPU started, exit 1; `tohost=0x0a`; trap count 5, only explicit ecalls. M.SE0–3 clear readbacks are 0; operations 43–46 complete with readback 0 and no cause-2 traps. Attempts to set each control read back 0; operations 47–50 complete with readback 0 but are not valid gate-open cases. Manifest record `ssstateen-heliodor-s-gates-all-slots-20261014` validates.
- `python3 experiments/kunminghu-smoke/run.py --topic ssstateen --ssstateen-case m-hs-gates-diff --max-instr 10000` -- latest `kunminghu-fixture-20261014T155020Z-3e81181d1d02`; CPU started, NEMU differential and GOODTRAP passed; 147 operations archived, including 21 implemented writable-field one-hot readbacks with exact asserted values. `154604Z` exposed a fixture ordering issue (H.SE0 was masked because M.SE0 remained clear); corrected and passing in `154748Z`/`155020Z`.
- Kunminghu S and VS gates: `m-s-gates` run `kunminghu-fixture-20261014T152629Z-3e81181d1d02` and `hs-vs-gates` run `kunminghu-fixture-20261014T152653Z-3e81181d1d02` both reached GOODTRAP; the S fixture self-checks four M.SE traps, and VS fixture self-checks H.SE0–3 plus H.ENVCFG (five virtual-instruction traps). VS `senvcfg` readback after H.ENVCFG restore was `0xf0`.
- VU custom-state diagnostic run `kunminghu-fixture-20261014T153123Z-3e81181d1d02` is `unverified`: CSR `0x800` is unmapped and CSR legality chooses `EX_II` before `EX_VI`, so its cause-2 observation cannot isolate the VU stateen C gates. The archived attempt is retained for the limitation, not as a CPU conformance failure.
- `python3 experiments/kunminghu-smoke/run.py --topic ssstateen --ssstateen-case m-hs-selfcheck --no-diff --max-instr 30000 ...` -- instruction limit reached at PC `0x8000158e`; no terminal marker or commit trace; all 93 operation reachability fields unavailable; `unverified`, exit code 0.
- `PATH=... uv run --no-cache pytest -q scripts/tests/test_kunminghu_smoke.py -k ssstateen` -- `4 passed, 52 deselected` after adding the instruction limit option.
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests` -- last full run before the max-instruction option/parser fix: `173 passed, 1 skipped in 89.86s` on 2026-10-14, including the latest Story 6.8 tests.
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- valid; final Kunminghu operation trace record and artifact hashes are present.
- `python3 scripts/check_rva23_coverage.py` -- valid; profile U64=34, S64=58, total=92; 184 implementation-status cells.
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- valid after adding the Heliodor S-mode run record.
- `python3 scripts/check_doc_links.py` -- valid; 38 documents.
- `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` -- `valid: true`.
- `git diff --check` -- clean.

- Heliodor S extension: `SSSTATEEN_S_MODE_OBSERVATIONS_PASS`; `trace[150..157]` all zero; three traps are only the expected HS entry, transition, and final S ecall (cause 9; operation IDs 21, 22, 42). The test later fails on the existing M-mode hstateen SE0 assertion, so the overall run remains `run-fail`. Durable evidence: `heliodor-ssstateen-s-rerun-20261014`.
