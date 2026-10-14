---
title: 'Story 6.1: 固定 CPU 验证工具链与结果归档'
type: 'feature'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '4394eb9c626c6405a1ae1a354fdd2a79da92ad30'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/notes/units/rva23s64-cpu-validation-preflight-v1.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 5 的前置调查证明 Kunminghu 可生成 RTL，但本机 GCC 13.3/Verilator 5.020 无法完成 simulator 编译；Heliodor 可用 Veryl 0.22.0 在隔离副本运行，但工具链和结果归档尚未固化为可复用入口。后续专题需要可比较、可复现的运行边界。

**Approach:** 为两份锁定快照记录固定工具版本、配置、依赖 gitlink、环境变量和命令，并建立统一机器可读运行记录模板。使用隔离工具环境尝试并运行两边最小 smoke 输入；每个结果附源 SHA、fixture SHA-256、完整日志与哈希、CPU 是否启动及产物位置。

## Boundaries & Constraints

**Always:** 保持 `sources.lock` 两个 SHA 和源 checkout 不变；记录工具、输入、命令、cwd、配置/hart 数、退出码、CPU 启动标志、结果分类、输出 SHA 和生成物。CPU 启动前失败为 `blocked`；只有运行后的预期不符才是 `run-fail`。隔离环境和可重建步骤需可供后续故事复用。

**Never:** 不把 RTL elaboration/编译称为 CPU 运行；不把上游支持声明或软件强制状态称作硬件行为；不修改 `sources/` 来适配本机工具链；不把有限 smoke 结果表述为 RVA23 符合性。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Toolchain ready | 锁定快照、配置与最小 smoke fixture | 两侧精确版本和命令可复现；运行结果含全部元数据 | 缺工具或版本不兼容时记录首个失败阶段并归类 blocked |
| CPU execution mismatch | 可加载 smoke 输入，CPU 已启动 | 保留预期/观察值和完整日志，分类 run-fail | 不将断言失败归为环境阻塞 |
| Source/dependency drift | 上游 checkout 与锁定 SHA/gitlink 比较 | SHA 一致且源工作树干净 | 不一致即停止使用该结果并定位漂移 |

</frozen-after-approval>

## Code Map

- `notes/units/rva23s64-cpu-validation-preflight-v1.md` — 已有 Kunminghu 三轮构建记录、Heliodor 隔离 runner 观察和必需元数据字段；需增补 Story 6.1 的最终固定组合及 smoke 结果，不删除历史失败。
- `notes/units/evidence/kunminghu-preflight-2026-10-14.txt`、`kunminghu-runmain-2026-10-14.log`、`heliodor-ssstateen-run-2026-10-14.log` — 已归档日志，可复核前置阻塞和 Heliodor CPU 运行结果。
- `sources.lock`、`sources/xiangshan/.mill-version`、`sources/xiangshan/.github/workflows/emu.yml`、`sources/xiangshan/Makefile`、`sources/xiangshan/build.sc` — 固定 snapshot、Mill 0.12.3、Verilator CI 版本范围、`NOOP_HOME` 与 `MILL_WORKSPACE_ROOT` 用法。
- `experiments/ssstateen/run_isolated.py`、`experiments/ssstateen/README.md`、`sources/heliodor/Veryl.toml`、`Veryl.lock` — 可复用 Heliodor 临时 harness 修补边界、Veryl 入口和锁文件；fixture 需从独立目录复制并摘要。
- `sources/xiangshan/build/` — 先前 ignored build 已生成约 1.4 GiB FIR 与 2,001 个 SystemVerilog 源文件；禁止把其存在误认为 simulator 或 CPU 已运行。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/evidence/cpu-validation-toolchain-v1.yaml` — 固定两边工具链、依赖 revisions、目标配置、环境变量、安装/重建来源与哈希；注明本机当前工具和兼容性结论。
- [x] `scripts/run_cpu_smoke.py` 与 `scripts/tests/test_run_cpu_smoke.py` — 定义统一 run manifest 校验/摘要及严格结果分类，确保缺字段、启动前失败和运行后 assertion failure 不会混淆。
- [x] `experiments/` 与 `notes/units/evidence/` — 为每边选取最小已知输入并完成实际运行；保存完整可用命令、fixture SHA、工具版本、退出码、CPU 启动证据、完整分流日志 SHA 和生成物路径。Kunminghu 使用固定 Verilator 5.050 构建 emulator 并通过 CoreMark/NEMU；Heliodor base-core smoke 通过，Ssstateen 专题失败另记 `run-fail`。
- [x] `notes/units/rva23s64-cpu-validation-preflight-v1.md` — 链接环境 manifest、复现命令、smoke 运行记录和适用边界，保持历史 preflight 观察可追溯。

**Acceptance Criteria:**
- Given 锁定快照，when 工具链准备完成，then manifest 列出准确 Mill/Java/Verilator/C++ compiler 与 Veryl 版本、所需环境变量、所有被选目标依赖 gitlink SHA 和配置，且两边源工作树仍干净。
- Given 两边可调用的 smoke 入口，when 输入最小已知程序，then 运行记录同时证明 CPU 开始执行并观察到预期 marker；若入口因先决能力缺失无法运行，记录完整 blocker，Story 不得标为 done。
- Given 任一失败，when 生成运行摘要，then schema 强制保留 snapshot SHA、input SHA-256、命令/cwd、配置、工具版本、退出码、cpu_started、result、日志路径/hash 和 artifacts；CPU 未启动不能归为 run-fail。
- Given 所有记录生成，when 校验工具链和 manifest，then 源 SHA/gitlink 检查、日志哈希校验、schema 测试和文档链接检查通过。

## Implementation Notes

- Kunminghu 使用 Verilator 上游 v5.050 tag 构建 emulator；刷新旧的 `VSimTop.mk` 后头文件路径指向新工具，C++ 编译和运行均通过。CoreMark 输出及 NEMU good trap 证据已分流归档。
- Heliodor 基础 smoke 通过；runner 只在临时副本增加 Veryl 0.22.0 所需 ROM `$readmemh` lint allow，源码 checkout 保持未修改。Ssstateen 功能 probe 仍为真实 `run-fail`，不掩盖该差异。
- 两份锁定 checkout 的 HEAD 与 `sources.lock` 一致且干净；工具版本、依赖 gitlinks、输入和日志哈希均由 manifest validator 核对。CPU-start 与预期 marker 的两侧 smoke 验收现已满足。

## Spec Change Log

## Review Triage Log

| # | Finding | Verdict / route | Evidence |
|---|---|---|---|
| 1 | Review diff accidentally included generated Python bytecode. | `low` / `patch` | Added Python cache patterns to `.gitignore`; final diff excludes cache artifacts. |
| 2 | Manifest accepted snapshots with no run records. | `medium` / `patch` | `validate_manifest` now requires a non-empty `runs` list; regression test covers empty list. |
| 3 | Tool maps accepted missing or non-string version values. | `medium` / `patch` | Record and snapshot tool maps require non-empty string values; exact unknowns must be stated explicitly. |
| 4 | String values such as `"false"` were truth-coerced for result classification. | `medium` / `patch` | Classification now uses validated booleans; malformed types are rejected. |
| 5 | Fixture path was optional, preventing independent input digest verification. | `medium` / `patch` | `input` is required, must resolve to a file, and its SHA-256 is checked. |
| 6 | Artifact paths were not checked. | `medium` / `patch` | Artifact files/directories and path patterns must resolve; manifest validation covers current outputs. |
| 7 | Omitted direct gitlinks could evade source drift checks. | `medium` / `patch` | Manifest gitlink keys must equal direct gitlinks in the source tree; each parent and child revision is checked. |
| 8 | Lock SHA lookup was not tied to the matching checkout. | `medium` / `patch` | `sources.lock` is parsed into checkout-to-commit pairs and compared against the selected checkout. |
| 9 | Heliodor run evidence referenced a temporary directory and lacked reproducible setup details. | `low` / `patch` | Durable isolated runner already exists; provisioning now documents official Veryl tool installer commands, pinned version/hash, and runner invocation. The temp run directory is identified as ephemeral. |
| 10 | Heliodor tool versions were missing in the original archived run. | `medium` / `patch` | Re-ran the smoke and recorded exact Veryl, Verilator, and G++ versions with separate stdout/stderr logs. |
| 11 | An empty `runs` list bypassed smoke-record validation. | `medium` / `patch` | Same root cause as finding 2; the explicit non-empty-list guard and regression test close it. |
| 12 | Unhashable `result` values could raise `TypeError`. | `low` / `patch` | Result type is checked before enum membership; malformed-result test verifies clean rejection. |
| 13 | `runs: null` could raise `TypeError`. | `low` / `patch` | All non-list and empty run values now produce validation errors. |
| 14 | Missing run records bypassed required metadata checks. | `medium` / `patch` | Covered by the non-empty-list guard and its manifest regression test. |
| 15 | Log hash mismatch had no regression test. | `medium` / `patch` | Added a focused tampered-transcript test; it verifies output/stdout/stderr hash mismatches are reported. |
| 16 | Manifest could omit either locked CPU checkout. | `medium` / `patch` | Validator requires exactly `sources/xiangshan` and `sources/heliodor`; regression test removes one snapshot and expects rejection. |
| 17 | A run revision could be attributed to the wrong enclosing snapshot. | `medium` / `patch` | Every run `snapshot_sha` must match its parent; regression covers mismatch. |
| 18 | Run IDs could be missing or duplicated. | `low` / `patch` | Non-empty string IDs are required and unique across snapshots. |
| 19 | `run-pass` could be asserted without its marker appearing in captured output. | `high` / `patch` | Each run names an expected marker; passing runs must contain it in the hashed output transcript, covered by a tampered-output test. |
| 20 | Artifact existence alone did not prove the captured artifact content. | `medium` / `patch` | Durable file artifacts now require SHA-256 entries and the validator recomputes them; regression covers tampering. |
| 21 | Blocked records could omit the actual blocker explanation. | `medium` / `patch` | All records have a typed blocker field; blocked records require a non-empty explanation and first failed stage. |
| 22 | Snapshot configuration/environment shape was only truth-tested. | `low` / `patch` | Configuration must be a non-empty string; environment must be a non-empty mapping of non-empty strings. |
| 23 | Heliodor smoke logs omitted runner invocation context. | `low` / `patch` | Runner writes source revision/tree digest, command, working directory and exit code into archived stdout, with stderr separately captured. |
| 24 | Temporary Heliodor transformation could not be independently inspected. | `medium` / `patch` | The exact transformed testbench and copied fixture are retained under `heliodor-core-smoke-inputs`, alongside hashed metadata. |
| 25 | Heliodor copied source tree lacked a durable digest. | `medium` / `patch` | Runner metadata records the locked commit and deterministic SHA-256 over the isolated working tree; metadata and transformed inputs are archived and hashed in the run manifest. |
| 26 | The edge-case reviewer returned no findings, so that review layer did not produce a usable report. | `process` / `failed layer` | Recorded as a failed layer; blind hunter, verification-gap and full-spec acceptance reviewers returned usable results. Do not treat the empty edge report as a clean review. |
| 27 | Heliodor's recorded replay command omitted required `--archive-dir`. | `medium` / `patch` | Manifest command now includes the archive argument; reran that exact runner invocation successfully and refreshed captured logs and hashes. |
| 28 | Kunminghu snapshot summary contradicted the later CoreMark CPU pass. | `medium` / `patch` | Snapshot configuration now describes the successful CoreMark/NEMU run; the earlier Verilator 5.020 failure remains a separate blocked record. |
| 29 | Malformed `blocker` values and checkout paths outside the repository raised exceptions instead of validation errors. | `medium` / `patch` | Validator guards blocker type and repository containment; regression tests cover null/list blocker values and an external checkout. |
| 30 | NUL-containing or symlink-loop checkout paths could still make `Path.resolve()` raise. | `low` / `patch` | Checkout path resolution now converts `OSError`, `RuntimeError`, and `ValueError` into manifest diagnostics; regression covers an embedded NUL. |

The final review round also confirmed the blind-hunter findings were either patched as above or superseded by stronger manifest checks. The verification-gap layer found no gaps, and the acceptance auditor found all four acceptance criteria evidenced. The edge-case layer returned an empty payload and is recorded as failed rather than passed.

## Verification

**Commands:**
- `uv run --no-cache pytest -q scripts/tests/test_run_cpu_smoke.py` — expected: all schema/classification regression tests pass.
- `uv run --no-cache python scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` — expected: valid manifest and all referenced fixture/log hashes match.
- `python3 scripts/check_doc_links.py` — expected: all supported local links and anchors resolve.
- `git -C sources/xiangshan status --short` and `git -C sources/heliodor status --short` — expected: no source checkout modifications.

Executed results: the latest schema suite passed 19 tests; manifest validation reported valid; `check_doc_links.py` validated 38 documents; both source checkout status commands were empty; `git diff --check` passed. The validator checks source revisions, direct gitlinks, fixture, log and durable artifact hashes; passing markers are verified in captured outputs. Heliodor Ssstateen remains a separate `run-fail`; the base-core smoke on both snapshots is `run-pass`.
