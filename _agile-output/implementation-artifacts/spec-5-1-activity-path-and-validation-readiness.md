---
title: 'Story 5.1：确认活动实现路径与验证就绪度'
type: 'feature'
created: '2026-10-13'
status: 'done'
baseline_commit: 'd2c680aa07ebef63aea1c80bae86eb7263220cbf'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** Epic 5 的五个 RVA23S64 深度主题必须依据锁定快照和实际活动路径规划；仅看到 CSR 名称、上游声明或测试文件，无法判断目标配置启用了什么，也不能说明测试能否运行。

**Approach：** 建立一份带来源和证据边界的双核就绪矩阵，逐项记录规范版本、Kunminghu/Heliodor 路径、候选测试、依赖工具和状态，作为 Story 5.2–5.6 的输入。

**Always：** 以 `sources.lock` 和实测 HEAD SHA 为快照权威；Kunminghu 目标采用上游 CI 中的单核 `KunminghuV2Config`，Heliodor 以 `heliodor_core` 为核心测试对象；区分活动路径、静态检查、测试源码存在、构建和实际运行；保留 PME/PMM 原引用与未决边界；学习记录用中文，符号和路径保留上游拼写。

**Never：** 不修改两个上游 checkout；不把 README 声明或测试存在写成运行通过/符合性结论；本故事只盘点工具和测试就绪度，不安装工具、不运行 CPU 测试，也不宣称 RVA23 认证。

## I/O & Edge-Case Matrix

| 情形 | 输入/状态 | 预期输出 | 处理 |
|---|---|---|---|
| 快照匹配 | 两个 checkout HEAD 与锁一致 | 矩阵引用对应 snapshot ID/SHA | 可继续静态映射 |
| 快照不匹配 | 任一 HEAD 与锁不同 | 标记 `blocked`，不得引用该 checkout 得出结论 | 记录 SHA 与恢复前置条件 |
| 仅找到通用路径 | 有 CSR/权限逻辑但无专题测试 | 分别写明静态证据与候选 harness | 状态为 `needs setup`/`unverified`，不推断行为 |
| 未找到显式实现 | 有界搜索无专题符号 | 记录搜索范围及通用访问路径检查要求 | 标记 `unresolved`，不得仅凭搜索判定缺失 |

</frozen-after-approval>

## Code Map

- `sources.lock`：两个上游仓库、分支、快照 ID 与 SHA；当前 checkout HEAD 已核对一致。
- `sources/xiangshan/src/main/scala/top/Configs.scala`：`KunminghuV2Config`；上游 CI `emu.yml` 使用该目标。`FuConfig.scala`、`backend/fu/wrapper/CSR.scala`、`NewCSR/NewCSR.scala`：CSR 活动接线；`NewCSR/{SstcInterruptGen,CSRPermitModule}.scala`、`SupervisorLevel.scala`、`MachineLevel.scala`、`HypervisorLevel.scala`、`StateEnBundle.scala`：五主题行为入口。
- `sources/heliodor/Veryl.toml`：Veryl 测试源与 Verilator runner；`src/core/{csr,decode,alu_wrap}.veryl`：CSR、FENCE.I 与地址变换路径；`tb/test_arch_common.veryl` 和 `test/{sstc,hsstc,sscofpmf,supm}`：可检查的 directed 测试入口。
- `sources/heliodor/README.md`、`toolchain/README.md`：上游测试命令和依赖声明，只作入口线索，不作本机结果。
- `notes/rva23-coverage.md` 及 `notes/units/rva23s64-{supervisor-traps,hypervisor}-v1.md`：Epic 4 要求 ID、已有边界及 Sha/Ssstateen 范围。
- 当前环境：本机 `gcc --version` 为 GCC 13.3.0，Verilator 5.020、Java 17、Rust/Cargo 可用；Mill、Veryl、Sail、Ruby 不在 PATH。Kunminghu 没有命中专题名的定向测试；Heliodor 测试源码存在，但需 Veryl/setup。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-deep-dive-readiness-v1.md` — 新建就绪矩阵，记录五个主题的规范版本、双侧活动路径/证据、测试入口、命令、依赖工具、状态与阻塞，并附自检问答。
- [x] `notes/units/index.md` — 登记新单元及其就绪/静态证据状态。
- [x] 不改 `sources.lock` 或 `sources/`；若最终 SHA 校验不一致，将矩阵标阻塞并停止使用不匹配 checkout。

**Acceptance Criteria：**
- Given `sources.lock`，when 核验来源，then 记录两个完整 HEAD SHA 和 snapshot ID；不一致项阻止后续分析。
- Given `KunminghuV2Config` 与 `heliodor_core`，when 完成五主题路径调查，then 写出接线/配置证据；区分活动路径与仅存在的替代实现。
- Given 每个候选案例，when 登记验证入口，then 记录规范版本、源码/测试位置、精确命令、依赖版本和 `available`、`needs setup`、`unsupported` 或 `blocked` 状态及依据；未执行案例不得标记通过。
- Given `Ssnpm` 与 `Ssstateen`，when 完成清单，then 并列保留 PME/PMM 的规范来源并记录已核实映射或明确的 unresolved 结论，同时写明 Heliodor Ssstateen 的有界负搜索限制。
- Given 单元完成，when 学习者复核，then 能解释两侧活动路径如何确定、五主题的本机验证门槛及尚未解决的阻塞。

## Implementation Notes

## Spec Change Log

## Review Triage Log

| Finding | Verdict / evidence | Route |
|---|---|---|
| Blind review：GCC 版本与 Code Map 不一致 | medium：就绪矩阵先前记录 13.3.0，规格环境摘要写 15.1，读者可能据此误判本机工具可用性；已按本机查询统一为 13.3.0。 | patch — 已修正文档与本规格摘要 |
| Blind review：`unresolved` 不在验收状态枚举中 | medium：Ssnpm、Ssstateen 先前把调查结论直接写成状态；已将状态统一为 `needs setup`，把 unresolved 留作结论限定。 | patch — 已修正 |
| Blind review：候选测试依赖未记录版本或不可用状态 | medium：Veryl/Mill 版本及测试程序交叉编译器状况会决定入口能否复现；矩阵现在写明已知版本要求和本机未检查/不可用项。 | patch — 已补充 |
| Blind review：`test_arch_sysb` 的 Zifencei 覆盖未经确认 | medium：通用测试入口不能证明 FENCE.I 同步语义；矩阵改为通用入口并列明需确认或新增可观察的自修改代码案例。 | patch — 已修正 |
| Blind review：Kunminghu 负搜索范围不清楚 | medium：无范围的“未找到”可能被误读为全仓不存在；矩阵已登记受检路径、文件类型和搜索词，并限定结论边界。 | patch — 已补充 |
| Edge review：GCC 版本声明冲突（同一问题的独立发现） | medium：复核确认矩阵与规格 Code Map 的 GCC 数值冲突；本机 `gcc --version` 结果已统一到 13.3.0。 | patch — 与首项共同修复 |

## Design Notes

配置选取固定到 Kunminghu V2 的 `KunminghuV2Config`，而不是 Makefile 默认的通用 `DefaultConfig`；Heliodor 以现有 core testbench 为行为目标。此选择由目标项目/上游 CI 源码解决，不构成待用户决定的产品范围。

## Verification

**Commands：**
- `git -C sources/xiangshan rev-parse HEAD` 与 `git -C sources/heliodor rev-parse HEAD` — 输出须与 `sources.lock` 完全相同。
- `git diff --check` — 文档无空白错误。

**Manual checks：**
- 每一矩阵行有两边源码证据或明确的缺失/阻塞边界；README 及测试入口未被误记为实测结果；索引链接可到达新版本。
