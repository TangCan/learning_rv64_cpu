---
title: 'Story 1.1: 建立源码与环境基线'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: '5d57f1660b57f7e30e7ed9cdcb9983b1d797feae'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_agile-output/planning-artifacts/epics.md'
  - '{project-root}/_agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 学习记录尚无固定的上游源码快照，也没有记录本机源码位置、工具链和验证入口；后续比较可能落在不同版本上，或把未执行的测试误当作验证结果。

**Approach:** 固定 Kunminghu V2 与 Heliodor 的仓库、分支和完整 commit SHA，在 Git 忽略的 `sources/` 下检出这两个快照。调查核心源码和现有验证入口，并记录本机环境及测试可运行条件，作为 ADD 对照的可追溯起点。

## Boundaries & Constraints

**Always:** 精确记录检出 commit 和快照 ID；区分仓库声明、源码检查和实际运行结果；环境记录注明采集日期及可用资源；检出位置和选择理由可复查。

**Never:** 不修改上游源码；不复制或重新分发上游源文件；不将移动分支名当作唯一版本标识；本故事不安装工具链、不初始化子模块、不构建处理器、不运行测试，也不把测试入口的存在描述成测试通过。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 精确快照检出 | 调查阶段记录的完整 SHA 可从上游获取 | 在 `sources/` 检出 detached HEAD；`sources.lock` 中 SHA 与实际 HEAD 一致 | 任一 SHA 无法获取时停止该仓库检出，记录错误和阻塞，不自动切换到新 HEAD |
| 环境工具缺失 | 本机未安装项目所需工具链 | 记录工具版本或 unavailable、验证命令及当前阻塞 | 不运行依赖命令，不将未运行结果记为通过 |

</frozen-after-approval>

## Code Map

- `README.md` — 确认项目选择的 Kunminghu `kunminghu-v2` 与 Heliodor 上游；保留对照学习目标。
- `_agile-output/planning-artifacts/epics.md` — Story 1.1 的五项验收条件，尤其要求使用完整 SHA、记录 HDL/源码/测试入口和 checkout 位置。
- `_agile-output/implementation-artifacts/epic-1-context.md` — Epic 1 的证据、来源和环境规则。
- `_agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md` — 快照 ID、证据类型/状态和实验隔离约定。
- `.gitignore` — 当前忽略 BMAD 运行产物；增加 `sources/` 忽略规则，避免提交上游 checkout。
- `sources.lock` — 新增两个只读源码基线，记录 URL、分支、完整 SHA、稳定 snapshot ID、采集日期和本地相对路径。
- `notes/source-environment-baseline.md` — 新增中文环境/源码调查记录，记录 OS、磁盘/内存、工具链版本与缺项、HDL、核心源码路径、验证入口、运行条件和未解决阻塞。
- `sources/xiangshan/`、`sources/heliodor/` — 新增 shallow checkout，分别固定到 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；只用于阅读，不提交其内容。

## Tasks & Acceptance

**Execution:**
- [x] 更新 `.gitignore` 并创建 `sources.lock`；使用来源 ID `xiangshan-kunminghu-v2-20261012` 与 `heliodor-master-20261012` 固定上游地址、分支、SHA、检出路径和日期，便于后续记录引用。
- [x] 在 `sources/xiangshan/` 与 `sources/heliodor/` 获取锁定 SHA 的 shallow checkout；逐一核对 `git rev-parse HEAD` 与锁文件，避免分支更新导致基线漂移。
- [x] 新建 `notes/source-environment-baseline.md`，记录本机资源和可用工具版本、两边 HDL/核心源码/测试入口、准确的推荐命令和运行阻塞，便于学习者复查而不夸大验证程度。

**Acceptance Criteria:**
- Given 两个已选上游仓库和调查阶段取得的完整 SHA，when 建立基线，then `sources.lock` 记录各自 URL、分支、完整 SHA、稳定 snapshot ID、日期和 checkout 路径，且两个 checkout 的 HEAD 与记录一致。
- Given 两个锁定的 checkout，when 完成源码调查，then 环境记录注明各自 HDL、核心源码位置及带快照引用的现有测试/仿真入口。
- Given 当前学习主机，when 完成环境盘点，then 记录 OS、可用磁盘和内存、已安装工具及版本、缺失工具和测试执行条件；未运行命令明确标记未运行，不声称测试通过。
- Given 仓库体量和本机可用资源，when 选择 checkout 位置，then 记录选择 `sources/` 的理由、浅克隆方式及不初始化子模块的边界；checkout 内容不会出现在 Git 提交中。
- Given 来源/环境阶段完成，when 回答自检，then 记录能指出两边核心源码目录和各自至少一个现有测试入口，并关联对应 snapshot ID。

## Implementation Notes

调查阶段于 2026-10-12 查询上游：Kunminghu `kunminghu-v2` SHA `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `master` SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。GitHub 仓库 API 的规模指标分别为 127033 KiB 和 29078 KiB，非实测 checkout 占用。本机 Ubuntu 24.04.4，项目盘可用 227 GiB，内存可用 191 GiB；计划使用浅克隆，不运行测试。

已在 `sources/` 完成两个 detached shallow checkout，实际 `HEAD` 与锁文件 SHA 一致；检出目录被 Git 忽略，两个源仓库工作区干净。主机记录更新为 checkout 后的 226 GiB 可用磁盘和 190 GiB available 内存。已检查源代码、Makefile、Veryl 配置和测试入口，未运行 CPU 测试、仿真或构建。环境中 Mill、Veryl、Sail、系统 Ruby 与 Linux RISC-V GCC 不可用；现有 ELF GCC 15.1.0 与 Heliodor 锁定工具链说明中的 GCC 16 不同。不存在的 SHA 获取失败路径在临时本地仓库中模拟，`git fetch` 返回 128，未创建 HEAD 或 refs。

## Spec Change Log

## Review Triage Log

| Verdict | Finding and evidence | Route / disposition |
| --- | --- | --- |
| low | `notes/source-environment-baseline.md` 原 Verification 仅列 expected，没有写实际结果，读者无法从记录复核命令执行状态；本轮已补入 SHA、ignore 和 validator 的观察结果，并标明 CPU 测试未运行。 | patch — 已修复 |
| low | checkout 命令在目录已存在时会因 `git init`/`remote add` 状态不同而失败或混淆；已注明命令适用的空目录前提及不得覆盖既有内容。 | patch — 已修复 |
| false | 核心源码导航被指缺少入口，但已有 `src/main/scala/xiangshan/` 与 Veryl 核心文件例子；实际核查 `XSCore.scala` 定义 `XSCore`，并发现 `heliodor_core.veryl` 定义核心模块，故不成立；为便利补充了精确文件路径。 | reject — 现有路径已满足验收，补充导航信息 |
| false | 被指 XiangShan 测试缺少 Scala/SBT 运行条件；`Makefile.test` 目标直接调用 Mill，本机 Java 17 已记录，目标不要求独立安装 Scala/SBT；Mill 缺失已明确为阻塞。 | reject — 已在工具表解释运行条件 |
| low | 快照规则未说明未来记录如何引用及如何更新；architecture spine 规定变更需有日期事件，而源记录未给操作格式；已补 `source_snapshots` 引用方式和保留旧条目/新增事件的更新规则。 | patch — 已修复 |
| medium | `.gitignore` 中未锚定的 `sources/` 规则会忽略仓库任意子目录里的同名目录和文件；规则已改为 `/sources/`，仅忽略仓库根目录 checkout。 | patch — 已修复 |


## Verification

**Commands:**
- `git -C sources/xiangshan rev-parse HEAD` — expected: 与 `sources.lock` 中 Kunminghu SHA 完全相同。
- `git -C sources/heliodor rev-parse HEAD` — expected: 与 `sources.lock` 中 Heliodor SHA 完全相同。
- `git check-ignore sources/xiangshan sources/heliodor` — expected: 两个 checkout 路径均被 Git 忽略。
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — expected: story status 格式有效。

**Manual checks:**
- 对照 `sources.lock` 和环境记录核实仓库 URL、分支、完整 SHA、采集日期、源码目录、测试入口和工具缺失；只核查测试入口，不执行 CPU 测试。
