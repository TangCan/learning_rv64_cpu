---
title: 'Story 6.4：运行 Zifencei 自修改代码对照'
type: 'feature'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '32d2a1664cbeba17865204276183fdd33aa621f0'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-6-3-heliodor-arch-harness-isolated-runner.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 两个锁定 RV64 核心都缺少可复现的 Zifencei CPU 运行对照；现有输入没有分别覆盖 FENCE.I 的三个保留字段。

**Approach:** 在 Kunminghu 与 Heliodor 各自固定的单 hart 配置上运行同一组自修改指令案例，逐条记录 FENCE.I 前后的返回值、保留字段编码的 trap/结果以及可追溯证据。结论只代表实际测试的 hart 和配置。

## Boundaries & Constraints

**Always:** 使用 `sources.lock` 固定的源代码快照与各自已记录的工具链；每个案例明确输入 SHA、编码、期望/观察值、工具、配置、日志和 CPU 是否启动；基准案例先返回旧值 1，再写入返回 42 的新指令，并在 FENCE.I 后重新取指；`funct12`、`rs1`、`rd` 各自单独置非零；两个核使用相同语义和期望值。

**Never:** 不修改上游核心快照；不把编译成功、静态 RTL 或汇编/反汇编结果说成 CPU 观察；不把这些有限案例说成 RVA23 符合性证明；本故事不声称覆盖跨 hart 发布/同步。

## I/O & Edge-Case Matrix

| 场景 | 输入 / 状态 | 期望行为 | 错误处理 |
|---|---|---|---|
| 标准 FENCE.I | 固定自修改程序，单 hart | 修改前返回 1，修改并同步后返回 42，成功 marker | CPU 未启动记 blocked；启动后结果不符记 run-fail |
| 非零 funct12 | 仅 FENCE.I bits[31:20] 为 1 | 基础实现忽略保留字段，仍观察到 1 后 42，且不因该字段 trap | 同上，记录实际 trap 或结果 |
| 非零 rs1 | 仅 FENCE.I rs1 为 x1 | 同上 | 同上 |
| 非零 rd | 仅 FENCE.I rd 为 x1 | 同上 | 同上 |
| 多 hart 不可用 | 两个 runner 均固定单 hart | 限定结论为 hart-local；远端 hart 同步未覆盖 | 清楚记录 hart 数及限制 |

</frozen-after-approval>

## Code Map

- `experiments/kunminghu-smoke/run.py` 与 `fixture.S` / `fixture.ld` -- 已验证的 Kunminghu 装载、链接、仿真和 NEMU good-trap 观察路径；runner 当前固定一个算术 fixture，应复用其隔离、证据和 manifest 约定。
- `experiments/heliodor-smoke/run.py` -- 已验证的临时副本和普通 arch harness 变换；目前将镜像、测试目标及 tohost marker 固定为 add，需要扩展为可选择本故事镜像和目标。
- `sources/heliodor/tb/test_arch_common.veryl:10-18,200-203,300-318,1065-1089` -- 普通 DRAM 位于 0x80000000，tohost word 位于 0x80001000；现有 fence_i arch target使用 300000 周期并报告 tohost/pass。
- `sources/heliodor/src/core/decoder.veryl:630-635` -- FENCE.I 按 MISC_MEM 与 funct3=001 解码；这是静态线索，不是行为证据。
- `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:229` 与 `frontend/icache/ICache.scala:379` -- Kunminghu 的 FENCE.I 解码/取指缓存线索，仅用于解释，不替代运行观察。
- `experiments/rva23s64-zifencei/kunminghu-self-modifying.S` -- 既有汇编输入已实现旧值检查、自修改及 FENCE.I，但需要适配 runner 的 trap 终止约定，并补齐三个独立编码案例。
- `notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- 两个核心的源 SHA、工具链和运行记录格式；遵守已有 manifest 校验和归档语义。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/rva23s64-zifencei/` -- 提供四个固定、可复现的 RV64 镜像：标准 FENCE.I 和三个各自仅修改一个保留字段的变体；保存源码及链接布局并可从镜像复核指令字。
- [x] `experiments/kunminghu-smoke/` -- 增加本专题 runner 路径，沿用锁定检查、工具记录、隔离运行和证据归档；每个镜像由 pinned emulator 执行并观察 NEMU good trap 或明确失败。
- [x] `experiments/heliodor-smoke/` -- 扩展隔离 runner 支持四个专题镜像/目标，维持既有 harness workaround 边界并对每次运行记录 tohost、pass、CPU 启动与完整日志。
- [x] `scripts/tests/` -- 添加 runner 单元覆盖，验证四种独立编码、结果分类（未启动为 blocked、启动后错误为 run-fail）及输入完整性检查。
- [x] `experiments/rva23s64-zifencei/README.md` 和 `notes/units/` -- 记录命令、配置、所有预期/观察值、证据路径与 SHA、各核结果、静态解释及单 hart 限制；同步 manifest 的完整运行记录。

**Acceptance Criteria:**
- Given 锁定的工具链与干净核心 checkout, when 四个镜像在每个核心的固定单 hart 配置执行, then 每次运行均归档 revision、输入 SHA、命令、工作目录、工具版本、退出码、CPU 启动、观察值和日志哈希。
- Given 标准镜像, when CPU 执行测试, then 日志显示 FENCE.I 前返回值为 1、修改后返回值为 42，成功终止 marker 与退出状态匹配。
- Given 三个保留字段变体, when 每个核心分别执行, then 每个字段独立非零，记录确切指令字；预期为忽略字段、无非法指令 trap 且新指令返回 42，并逐核报告是否满足。
- Given 仿真无法启动或观察失败, when runner 分类结果, then CPU 启动前为 `blocked`，启动后行为不符为 `run-fail`，不得用静态分析填充观察结果。
- Given 单 hart 验证, when 汇总故事结论, then 明确远端 hart 发布/同步未覆盖，且不作 RVA23 合规或认证声明。

## Implementation Notes

四份镜像由 `build_images.py` 调用锁定交叉工具重建，并核验 FENCE.I 位于 byte offset `0x20`。Kunminghu runner 以 `--topic zifencei` 分别编译、运行四份源码；Heliodor runner 复用实际锁定的 `test_arch_rv64ui_fence_i` harness，在临时副本将 HEX_FILE 指向对应固定镜像。


## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | Evidence |
|---|---|---|
| Passed runs populated `observed_values` with constants without exposing how the values were established (Blind Hunter, Edge Hunter x2). | medium / patch — fixed | The fixture executes `a0==1` before patch and `a0==42` after FENCE.I; each manifest record now names those executed comparisons and the successful trap/tohost marker required to reach completion. It no longer implies register values were parsed from output. |
| Heliodor success predicate lacked a positive test for the new FENCE.I marker (Verification Gap). | medium / patch — fixed | Added a complete passing `v4 rv64ui-fence_i` observation case; the targeted suite passed. |
| Kunminghu ignored `--case` without the topic flag (Blind Hunter). | low / patch — fixed | CLI now rejects `--case` outside `--topic zifencei`; regression case passes. |
| Kunminghu accepted unsupported fixture stems and failed later during manifest encoding lookup (Edge Hunter). | medium / patch — fixed | CLI now validates case/file agreement before creating evidence or running the emulator; regression cases pass. |
| Fixture images could differ in length while the byte-difference test silently truncated comparison via `zip` (Blind Hunter). | medium / patch — fixed | Test asserts all image lengths match before comparing; a dedicated mismatched-length case is covered. |
| Reported image offset lacked an explicit base/load mapping assertion (Blind Hunter). | low / patch — fixed | Tests assert the fixture linker script base is `0x80000000`; docs state Kunminghu raw-image and Heliodor RESET_PC mapping. |
| Heliodor might start the CPU but exit before its completion markers, causing the runner to classify missing evidence as blocked (Blind Hunter). | false | `cpu_started` means a CPU progress/result marker was observed. Without any CPU marker the available evidence cannot establish that execution began; classifying the run as blocked is consistent with Epic 6's evidence-based rule. |
| Image builder could accept unrelated mutations in the FENCE.I word (Blind Hunter). | false | `build_images.py` checks each full word at offset `0x20` against the exact expected encoding before comparing image bytes. |
| Test result lacked a separate pytest output archive (Blind Hunter). | false | The verification command is recorded in this spec and was rerun with the pinned Veryl path; it completed with 95 passing tests. A separate log artifact is not required by the story. |
| Results lacked links to individual manifest records (Blind Hunter). | false | The report table contains each exact run ID and input/output SHA; those IDs are keys in the manifest, so the evidence is directly traceable. |

## Design Notes

RISC-V Zifencei 2.0 规定 funct12、rs1、rd 保留给未来更细粒度 fence；为向前兼容，基础实现应忽略这些字段，标准软件应将其置零。因此三个变体分别只改一个字段，便于将 trap 或取指结果归因到单一字段。规范也限定 FENCE.I 只同步执行它的 hart；本故事使用单 hart，不能据此推断远端 hart 行为。

**镜像设计：** 每个镜像先执行旧 `patched` 指令并检查 a0=1，再用 32 位 store 写入 `addi a0, zero, 42`；在对应 FENCE.I 后再次调用并检查 a0=42。Kunminghu 以 NEMU good-trap 结束；Heliodor 以架构 harness 的 tohost=1 结束。字段变体只替换 FENCE.I 编码，其余程序字节保持一致。

## Verification

**Commands:**
- `python3 experiments/rva23s64-zifencei/build_images.py` -- 重建并验证四种编码。
- `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" uv run --no-cache pytest -q scripts/tests/test_zifencei_self_modifying.py scripts/tests/test_heliodor_smoke.py scripts/tests/test_run_cpu_smoke.py scripts/tests/test_kunminghu_smoke.py` -- 99 项通过（包含本次独立审查修复）。
- `python3 experiments/kunminghu-smoke/run.py --topic zifencei --timeout 120` -- 四例均 run-pass，CPU 启动并到达正确 PC 的 NEMU good trap。
- `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic zifencei --timeout 180` -- 四例均 run-pass，CPU 启动，tohost=1/pass=1。
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- manifest 有效。

运行 ID、输入与日志 SHA-256 在 manifest 与 `notes/units/rva23s64-zifencei-v1.md` 中列出。之前的 Heliodor standard 探跑使用的是还未修正失败终止分支的镜像；该记录未保留在 manifest，最终标准记录来自与另外三例相同的最终四例批次。

## Review Findings

| Finding | Triage | Evidence |
|---|---|---|
| Cross GCC/binutils were selected from `PATH` without confirming the captured versions or binary identity. | **patch** | `build_images.py` now requires the manifest-captured GCC 15.1.0 and objcopy 2.44 version strings and checks SHA-256 for GCC, objcopy, and nm before building. |
| `zip` comparison could ignore trailing bytes when image lengths differed. | **patch** | The builder requires exactly `0x1008` bytes for each image and explicitly compares lengths before byte differences. Existing test also rejects unequal image lengths. |
| A correct word at offset `0x20` did not prove `_start` and the fixture layout were correct. | **patch** | Builder invokes pinned `nm`, requires `_start == 0x80000000` and `fence_i_instruction == 0x80000020`; linker script declares `ENTRY(_start)`. |
| Heliodor changed module-global `ARCH_FIXTURE`, so later same-process runs depended on call order. | **patch** | Fixture path is local to `run()` and is passed to input hashing, transformation, and copy operations. |
| Harness transformation did not require a unique `HEX_FILE` path anchor. | **patch** | Transformation now rejects zero or multiple matches. Regression cases cover missing and duplicate anchors. |
| A generic smoke marker could be mistaken for startup of the separately invoked Zifencei target; a missing target result marker left target startup unobserved. | **patch** | Zifencei classification now uses its own arch result marker. Without it, startup is explicitly unobserved and the run remains `blocked`; an observed failing tohost marker is `run-fail`. |
| `reserved_field_trap: not observed` did not state whether the harness exposes trap cause. | **patch** | Passing records say no trap prevented the pass marker and that trap-cause telemetry is unavailable; non-passing records direct readers to the log and state the telemetry limit. |
| Old/new values were described as observed although they were inferred from the fixture reaching its pass marker. | **patch** | Report now says the values are established by successful in-program equality checks and are not printed register observations. Manifest records name this evidence method. |
| “双核” could imply a dual-hart run. | **patch** | Report title and opening specify a comparison of two core implementations, one hart per run; scope limits remain explicit. |
| Results table did not itself list all per-run startup, exit, and marker fields. | **patch** | Table run IDs are explicitly identified as keys for manifest records containing startup, exit code, marker, and full-log path. |
| Blind review emitted an isolated `kB`/`N` calculation without a code or acceptance-criteria location. | **reject** | No finding or proposed guard maps to Story 6.4 artifacts or behavior; it is unrelated reviewer output. |

Acceptance Auditor found no acceptance-criteria violations. Verification-gap review found no additional gaps. Edge Case review's startup-classification concern is resolved by the Zifencei-specific classification above.
