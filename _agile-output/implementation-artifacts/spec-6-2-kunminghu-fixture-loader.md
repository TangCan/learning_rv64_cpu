---
title: 'Story 6.2: 建立 Kunminghu fixture 加载与模拟器入口'
type: 'feature'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
review_loop_iteration: 10
baseline_commit: '32e7bfd524e62aff167af7ec2d4fbd2f35d36568'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-6-1-pin-cpu-validation-toolchains.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 5 留下的 Kunminghu 专题 fixture 尚无链接地址、可复现的二进制加载步骤和明确的仿真结果采集方式。仅完成 `make emu` 或复用 CoreMark 不能证明后续小型定向程序已从预期入口执行并正常结束。

**Approach:** 为锁定的 Kunminghu 单 hart 配置建立一个小型裸机 fixture、链接/镜像生成步骤和可重复 runner。runner 使用已有 Verilator 仿真器和 NEMU difftest，记录源码/输入/工具/命令/日志哈希，要求看到首条提交和预期 good-trap marker；不触碰 `sources/`。

## Boundaries & Constraints

**Always:** 验证 XiangShan HEAD 与 `sources.lock` 一致、相关依赖 gitlink 与 manifest 一致；fixture 用显式 `_start` 和 `0x80000000` 链接/加载基址；将 ELF、map、raw image、日志和元数据保存在项目证据目录；CPU 未启动、超时、good-trap 未出现均不得报 `run-pass`；完成运行后重新确认上游源树干净。

**Never:** 不修改或提交上游源码、生成的 116MB emulator、子模块内容或 ignored build；不把仿真器构建成功当成 CPU 运行成功；不把本 smoke 描述为任何专题或 RVA23 符合性证据。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 可执行路径 | 锁定单 hart 配置、fixture 源码、Verilator emulator 与 NEMU 库 | 编译为加载地址明确的镜像；首指令提交且命中 good trap；保存分流日志与摘要 | 退出码/marker 不符时失败关闭并保存证据 |
| 构建或依赖缺失 | emulator、交叉编译器、NEMU 或工具版本不可用 | 不宣称 CPU 已启动 | 记录首个阻塞阶段、命令、工具版本、输出及哈希 |
| 非预期终止 | 镜像无效、仿真超时、BADTRAP/ABORT 或无提交证据 | 结果不是 `run-pass` | 保存完整输出；区分启动前 `blocked` 与启动后 `run-fail` |

</frozen-after-approval>

## Code Map

- `sources.lock` — Kunminghu 基线 SHA；`notes/units/evidence/cpu-validation-toolchain-v1.yaml` — 版本、gitlink 与 Story 6.1 记录规则。只读并复用其 manifest schema。
- `sources/xiangshan/Makefile` — `make emu CONFIG=KunminghuV2Config NUM_CORES=1` 生成仿真器；该命令本身不运行 CPU。忽略目录 `sources/xiangshan/build/verilator-compile/emu` 已有可复用构建产物。
- `sources/xiangshan/difftest/src/test/csrc/common/args.cpp` — `-i/--image`、`--diff`、`--max-cycles` 和 `--max-instr` 参数；`difftest/src/test/csrc/emu/emu.cpp` — RAM 装载、指令提交、good/bad trap 输出。
- `sources/xiangshan/ready-to-run/coremark-2-iteration.bin` — Story 6.1 已证明 raw image 可由 `-i` 加载，但规模大且依赖 NEMU；`experiments/rva23s64-zifencei/kunminghu-self-modifying.S` — 专题输入可复用其裸机编码风格，现有 `.tohost` + 无限循环没有 loader/结束 marker，不直接作为本故事 smoke。
- `notes/units/evidence/smoke/` — 永久归档日志约定；`scripts/run_cpu_smoke.py` — 已有快照、日志、marker 和 artifact 哈希校验器，扩展以保持一致。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/kunminghu-smoke/` — 增加最小 RV64 汇编、链接脚本及 README；入口设在 `0x80000000`，执行几条可由 NEMU 对照的指令和结果检查，再以 good-trap 约定正常结束。
- [x] `experiments/kunminghu-smoke/run.py` — 校验 locked SHA/clean checkout、工具和目标文件；编译、链接、objcopy、运行；设置有界 timeout；分流并归档命令、工具版本、fixture/image 摘要、CPU-start/提交/trap 观察和产物哈希；调用既有 manifest 校验规则。
- [x] `experiments/kunminghu-smoke/run.py` — 在阻塞记录中采集可用磁盘、可用内存、逻辑 CPU 数及阶段 timeout，并按首个失败阶段给出下一项具体环境调整。
- [x] `scripts/tests/test_kunminghu_smoke.py` — 覆盖成功分类、缺工具/仿真器、超时、缺少首条提交或 good marker、BADTRAP 和日志/artifact 摘要不符。
- [x] `notes/units/evidence/cpu-validation-toolchain-v1.yaml`、`notes/units/evidence/smoke/`、`notes/units/rva23s64-cpu-validation-preflight-v1.md` — 追加实际 smoke 记录和可复查生成物/运行日志，不覆盖 6.1 历史 CoreMark 或构建失败记录。

**Acceptance Criteria:**
- Given Story 6.1 的工具版本和固定 Kunminghu checkout，when runner 准备依赖并生成 fixture，then top-level SHA 和所需 gitlink 都与锁定值一致，且源 checkout 不被修改。
- Given 编译出的最小 raw image，when 单 hart emulator 以受控命令加载并运行，then 输出证明镜像已加载、至少一条指令已提交并命中预期 good-trap marker，且进程正常退出。
- Given 仿真器、工具、镜像、timeout 或 CPU 结果任一失败，when runner 汇总，then 记录首个失败阶段、CPU 是否启动、退出码、分流输出及 SHA，并且无成功 marker 时不能分类为 `run-pass`。
- Given 运行记录和生成物，when 执行回归、manifest validator、文档链接检查和 source cleanliness 检查，then 全部通过，且 manifest 哈希能复算。

### Review Findings

- [x] [Review][Patch] Recheck the locked checkout after the emulator run [experiments/kunminghu-smoke/run.py:242] — added a post-run manifest/source integrity check; a dirty checkout downgrades an apparent pass to `run-fail` and is covered by a runner-level regression.
- [x] [Review][Patch] Keep suffixed evidence directory IDs unique in the manifest [experiments/kunminghu-smoke/run.py:277] — the record ID now comes from `run_dir.name`; a fixed-clock test verifies two same-second invocations append distinct IDs matching their evidence directories.
- [x] [Review][Patch] Preserve argument boundaries in recorded commands [experiments/kunminghu-smoke/run.py:217] — use `shlex.join`; the runner integration test uses an evidence path containing spaces and validates the emitted record.
- [x] [Review][Patch] Reject unbounded or nonpositive emulator timeouts [experiments/kunminghu-smoke/run.py:140] — finite positive values are required before evidence directories or run records are created; a regression covers `inf`.
- [x] [Review][Patch] Preserve a structured record when the manifest cannot be appended [experiments/kunminghu-smoke/run.py:328] — append failure now writes `run-record.json` beside the captured output; a missing-manifest regression verifies the standalone blocked record.
- [x] [Review][Patch] Verify the runner-to-manifest write path [scripts/tests/test_kunminghu_smoke.py:178] — a controlled runner invocation asserts manifest append, unique record IDs, command quoting, valid artifact hashes and `validate_record` acceptance.
- [x] [Review][Patch] Preserve evidence when the lockfile cannot be read [experiments/kunminghu-smoke/run.py:315] — cache the locked SHA during preflight and write a standalone failure record if no schema-valid snapshot SHA is available.
- [x] [Review][Patch] Preserve evidence when the fixture source is missing [experiments/kunminghu-smoke/run.py:242] — detect the missing input before build, save a standalone blocked record, and avoid appending a malformed hash to the manifest.
- [x] [Review][Patch] Serialize concurrent manifest appends [experiments/kunminghu-smoke/run.py:127] — use a process lock plus fsync and atomic replacement; a concurrent append regression verifies no run records are lost.
- [x] [Review][Patch] Match the loaded image path to the generated fixture [experiments/kunminghu-smoke/run.py:43] — success classification now requires the exact raw image path passed to the emulator; tests reject another path and a missing load message.
- [x] [Review][Patch] Reject ABORT even when the good-trap text is also present [experiments/kunminghu-smoke/run.py:67] — the pinned simulator's ABORT message is a failure signal; a mixed-output regression ensures it cannot pass.
- [x] [Review][Patch] Keep NEMU difftest in the runner invocation [scripts/tests/test_kunminghu_smoke.py:214] — the controlled runner test asserts `--diff` and the locked NEMU path are present in the recorded command.
- [x] [Review][Patch] Cover nonzero exit after a good-trap message [scripts/tests/test_kunminghu_smoke.py:291] — regression asserts `run-fail` and `expected_observed=false`.
- [x] [Review][Patch] Document every retained successful fixture run [notes/units/rva23s64-cpu-validation-preflight-v1.md:106] — explain the successive runs and identify which runner changes the final pass exercises.
- [x] [Review][Patch] Reserve evidence directories atomically [experiments/kunminghu-smoke/run.py:184] — same-second concurrent starts now retry after `mkdir` collisions; a threaded test confirms each run gets a unique directory.
- [x] [Review][Patch] Execute the real fixture in regression coverage [scripts/tests/test_kunminghu_smoke.py:377] — when the locked toolchain is available, run the actual assembly through emulator/NEMU, require the correct sum to reach good trap, and require a deliberately wrong sum to reach bad trap.
- [x] [Review][Patch] Revalidate the manifest under the append lock [experiments/kunminghu-smoke/run.py:140] — the locked append rechecks source/manifest integrity immediately before replacing the file; a simulated pre-append change converts the standalone result to `run-fail`.
- [x] [Review][Patch] Record expected outputs that a failed build did not produce [experiments/kunminghu-smoke/run.py:354] — records now distinguish expected, produced, and missing artifact paths; compiler failure regression verifies ELF/map/raw absence is explicit.
- [x] [Review][Patch] Document bounded build-stage timeouts [experiments/kunminghu-smoke/README.md:26] — README states the 120-second compile/link and objcopy limits separately from the configurable emulator timeout.
- [x] [Review][Patch] Persist the manifest directory entry after atomic replacement [experiments/kunminghu-smoke/run.py:149] — fsync the parent directory after `os.replace` to make the durable append sequence complete.
- [x] [Review][Patch] Preserve same-second evidence under concurrent starts [experiments/kunminghu-smoke/run.py:160] — evidence directory creation now reserves names atomically and retries collisions.
- [x] [Review][Patch] Protect the arithmetic assertion against fixture drift [scripts/tests/test_kunminghu_smoke.py:377] — actual emulator/NEMU runs require the correct sum to hit good trap and a deliberately wrong sum to hit bad trap.
- [x] [Review][Patch] Close the source/manifest validation-to-append window [experiments/kunminghu-smoke/run.py:139] — revalidate under the process lock; if integrity changed, preserve a standalone `run-fail` record with updated transcript hash.
- [x] [Review][Patch] Reject evidence directories outside the project root [experiments/kunminghu-smoke/run.py:209] — fail clearly before creating a run directory; a regression covers absolute paths outside the repository.
- [x] [Review][Patch] Exercise build-stage timeout recording end to end [scripts/tests/test_kunminghu_smoke.py:307] — verify partial stdout/stderr, missing artifacts, failed stage, valid blocked record, and that objcopy/emulator do not run.
- [x] [Review][Patch] Detect fixture edits during a smoke run [experiments/kunminghu-smoke/run.py:320] — record the pre-build source hash and downgrade the run if the fixture changes or disappears before evidence is recorded.
- [x] [Review][Patch] Mark manifest append failures in standalone records [experiments/kunminghu-smoke/run.py:434] — retain the CPU result while recording `manifest_persisted=false` and the append error; README describes the fallback file and interpretation.
- [x] [Review][Patch] Document standalone evidence fallback [experiments/kunminghu-smoke/README.md:23] — describe where to find `run-record.json` and which fields identify a failed manifest append.
- [x] [Review][Patch] Make the runner's pass claim match the evidence it checks [experiments/kunminghu-smoke/run.py:404] — describe image, entry commit and good trap; arithmetic correctness is established by the required emulator-backed regression.
- [x] [Review][Patch] Require the arithmetic integration test's dependencies [scripts/tests/test_kunminghu_smoke.py:507] — missing locked tools now fail with provisioning instructions instead of silently skipping the only execution test.
- [x] [Review][Patch] Preserve child output with invalid UTF-8 [experiments/kunminghu-smoke/run.py:97] — decode subprocess streams with replacement so malformed output cannot interrupt evidence capture.
- [x] [Review][Patch] Recheck input and artifact hashes under the manifest lock [experiments/kunminghu-smoke/run.py:142] — changed evidence becomes a failed standalone record before it can be appended as a pass.
- [x] [Review][Patch] Preserve all integrity diagnostics alongside an existing CPU failure [experiments/kunminghu-smoke/run.py:359] — a BADTRAP or other execution failure no longer hides a simultaneous source/manifest integrity error.
- [x] [Review][Patch] Record and recheck simulator binary identities [experiments/kunminghu-smoke/run.py:279] — emulator and NEMU SHA-256 values are included in tool metadata; changed binaries downgrade the run.
- [x] [Review][Patch] Keep run IDs unique across evidence directories [experiments/kunminghu-smoke/run.py:302] — include an evidence-directory key in the timestamp ID, seed suffix selection from existing manifest IDs, and reject duplicates under the append lock; regressions cover separate directories and duplicate appends.
- [x] [Review][Patch] Recheck all three log hashes under the append lock [experiments/kunminghu-smoke/run.py:159] — a log changed after initial hashing now fails closed and is kept as standalone evidence.
- [x] [Review][Patch] Report post-replacement directory-sync failure accurately [experiments/kunminghu-smoke/run.py:181] — distinguish a manifest record already installed by `os.replace` from an append that never happened; standalone metadata records persistence and durability separately.
- [x] [Review][Patch] Record resource context and next environment action for blockers [experiments/kunminghu-smoke/run.py:215] — blocked records include disk/memory/CPU/time limits and a stage-specific remediation; compiler-blocker regression verifies both.
- [x] [Review][Patch] Bind the linker script to the pre-build input identity [experiments/kunminghu-smoke/run.py:354] — record its initial SHA-256, detect mutation/disappearance after execution, and recheck it under the manifest lock; a regression verifies mutation fails closed.
- [x] [Review][Patch] Preserve structured failure evidence when simulator hashing races with file removal [experiments/kunminghu-smoke/run.py:378] — catch initial and post-run hash `OSError`s and classify the run as failed; regression covers removal during initial hashing.
- [x] [Review][Patch] Verify mismatched loaded-image output through the full runner [scripts/tests/test_kunminghu_smoke.py:258] — an otherwise successful CPU trace reporting a different image now has runner-level coverage and is recorded as `run-fail`.

**Rejected**

- `false` — The first-commit phrase comes from XiangShan's Difftest instruction checker when core 0's first instruction commits (`sources/xiangshan/difftest/src/test/csrc/difftest/checkers/instructions.cpp:31`); success additionally requires the expected `_start` PC in commit trace and the map-matched good-trap PC. The phrase is not an unrelated-output success condition.
- `false` — A later failed stage cannot leave `expected_observed` true: the failure branch clears it when converting a pass to `run-fail`, and the classifier's expected-observation predicate includes successful exit and no timeout. The predicate now also requires the first-commit signal, keeping blocked records consistent with the manifest validator.
- `false` — The runner does check direct gitlinks through its call to `validate_manifest`; that validator compares the exact direct-gitlink set and SHA values against `sources.lock` and checks each initialized gitlink checkout for dirt (`scripts/run_cpu_smoke.py:265-286`).
- `false` — The reported absolute `nvme_data1/...` paths came from the temporary review diff's `git diff --no-index /dev/null <absolute-path>` formatting. `git status --short` confirms all additions exist at the intended repository-relative `experiments/`, `scripts/`, `_agile-output/`, and `notes/` paths.
- `false` — The first-commit message is emitted by the pinned Difftest checker on an actual core-0 commit; production pass classification separately requires a commit at the linked entry PC. The message alone can at most affect `blocked` versus `run-fail`, never satisfy the success predicate.
- `false` — Tool version probes may explicitly record `unavailable`; this is the manifest's supported unknown-value convention, while the locked manifest retains the build environment's compiler/Verilator/toolchain versions. A run does not claim an unobserved version.
- `false` — The fixture does not need a hard-coded approved source hash to establish its arithmetic behavior: the integration regression runs the checked-in fixture against the actual CPU and also runs a wrong-sum variant, requiring good and bad traps respectively.
- `low` — A concurrent edit to generated ELF/map/raw artifacts in the short interval between hashing and manifest append is possible, but normal runs do not mutate their reserved evidence directory; subsequent manifest validation detects a changed artifact. Adding cross-process locks around every evidence artifact would add complexity without preventing later edits, so this was rejected as a low-likelihood hardening item.
- `false` — A version-probe timeout returns code 124 and empty output from `_run`; `_version`'s success-and-output condition falls through to `unavailable`, so it does not index an empty line or prevent evidence capture.
- `false` — Existing but unusable emulator/NEMU paths cannot yield `run-pass`: version probing reports `unavailable` on `OSError`, and execution-stage `OSError` is caught and recorded as a failed stage.
- `false` — A link-map inspection failure breaks before the emulator stage; per-run output buffers start empty and contain no CPU-start marker from a previous invocation, so stale output cannot make the classifier claim CPU start.
- `false` — Preflight diagnostics are included in the `blocker` field, which is written both to the transcript and structured record; the full stage error is therefore retained.

## Implementation Notes


## Spec Change Log

## Review Triage Log

Ten independent review iterations used Blind Hunter, Edge Case Hunter, Verification Gap Reviewer and Acceptance Auditor. The first iteration's six patch findings, second iteration's nine patch findings, third iteration's six distinct patch findings, fourth iteration's five patch findings, fifth iteration's four patch findings, sixth iteration's two patch findings, seventh iteration's one patch finding, eighth iteration's three patch findings, ninth iteration's run-ID and acceptance findings, and tenth iteration's linker identity, simulator-hash race, and end-to-end image-path findings were addressed and verified. The tenth acceptance audit found no blocking issues. The runner's pass claim is limited to the signals it checks; the required emulator-backed regression verifies correct and deliberately incorrect arithmetic. Invalid subprocess output, append-time input/artifact/log/linker mutation, simultaneous integrity and CPU failures, simulator binary identity and hash races, manifest-global run-ID uniqueness, post-replacement durability reporting, and blocker resource/remediation context now preserve fail-closed evidence. Earlier false findings were rejected after tracing the Difftest start signal, timeout wrapper, manifest validator's direct-gitlink checks, failure classifier, and temporary diff path formatting. Duplicate findings were grouped. No decision-needed or deferred items remain.

## Design Notes

good trap 使用仿真器已有的 Difftest/NEMU 终止协议，避免自造一个当前 simulator 无法读取的 `.tohost` 通道。fixture 作为 ELF 调试与 raw image 加载两种工件保存；仿真器实际输入为 raw image，入口/地址由链接 map 与首次提交 PC 交叉核对。

## Verification

**Commands:**
- `uv run --no-cache pytest -q scripts/tests/test_kunminghu_smoke.py scripts/tests/test_run_cpu_smoke.py` — 61 项测试通过，包括锁定工具可用时真实运行正确 fixture 和错误算术 fixture。
- `python3 experiments/kunminghu-smoke/run.py --help` — 展示参数和固定默认值。
- `python3 experiments/kunminghu-smoke/run.py --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml --timeout 120` — final `kunminghu-fixture-20261014T051436Z-3e81181d1d02` 为 `run-pass`；首条提交 PC 为 `0x80000000`，good-trap PC 为 `0x80000010`，退出码为 0。fixture source SHA-256 为 `55de02149639dc04d311b153d30ee8082f480d608472488863f9e36b85fcd2ed`；linker script SHA-256 为 `1a09d98e3c1ba4c22c1ecd2c16e5f4d8cad65fc6944efe0a0ccd8b3149d4a412`；emulator SHA-256 为 `21f0700203205870403df50eadf2afd182e33573afdeee9a264a49b328f9e897`；NEMU SHA-256 为 `3e9d63c31d2cd68ec68d55fa9df56ec990ce9a9fd3a8e59709ecb92f21176c40`。资源快照与所有输出/生成物 hash 见对应 manifest 记录和 [运行证据目录](../../notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T051436Z-3e81181d1d02/)。
- `uv run --no-cache python scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` — 快照/gitlink、运行字段、日志与工件 hash 通过。
- `python3 scripts/check_doc_links.py`；`git -C sources/xiangshan status --short` — 文档链接有效且上游源码干净。
