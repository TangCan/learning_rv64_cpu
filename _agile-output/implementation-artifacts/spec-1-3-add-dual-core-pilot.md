---
title: 'Story 1.3: 完成 ADD 双核对照试点'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: '71381ce44ede0e26477e091716de7942572335b5'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-1-1-establish-source-and-environment-baseline.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-1-2-establish-learning-record-template.md'
  - '{project-root}/_agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 项目尚无同时追踪规范行为、两边实现及验证边界的实际学习单元，统一模板也未经真实案例检验，因此无法判断当前记录方法是否足以支撑后续双核学习。

**Approach:** 以 RV64I `ADD` 为首个对照单元，按固定快照完成译码、执行与结果写回追踪，保存双边证据和自检答案；再复盘模板的复用点、缺口和改进建议，并记录一个阶段门结论。

## Boundaries & Constraints

**Always:** 使用 `sources.lock` 中两个固定 snapshot ID 和完整 SHA；引用官方规范及精确版本；区分 `inspected` 与实际 `run-pass`/`run-fail`，测试未运行时标为 `unverified`；每条比较结论关联两边证据 ID；注明 ADD 与 ADDW、ADDI 的语义边界；不得从一个指令推断 RVA23 整体符合性。

**Never:** 不修改或复制上游源码；不将未运行测试写成通过；不把测试入口或包含 ADD 向量的测试源码误报为 ADD 已验证；不在阶段门结论之外启动后续史诗。若无需自建实验，明确记录未创建。

</frozen-after-approval>

## Code Map

- `sources.lock` — 权威来源快照；Kunminghu `xiangshan-kunminghu-v2-20261012` / `c098f996bf4d301b88693b20315486d31e93bc9d`，Heliodor `heliodor-master-20261012` / `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- `notes/templates/learning-record.md`、`notes/units/index.md` — Story 1.2 产物；复用章节顺序、证据字段和版本索引，不另建模板。
- RISC-V Unprivileged ISA Manual 20260120：[RV32I §1.1.4.2](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html) 定义 ADD 为 rs1 与 rs2 相加、溢出忽略并写入低 XLEN 位；[RV64I §3.1.1、§3.1.2.2](https://docs.riscv.org/reference/isa/unpriv/rv64.html) 给出 XLEN=64 与 ADDW 的 32 位/符号扩展边界。该条目是基础整数指令学习，不声称验证 RVA23 profile。
- Kunminghu: `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:154` 将 `ADD` 译码为双寄存器源和 `ALUOpType.add`；`backend/fu/Alu.scala:25-35,370-380` 计算并选择加法结果；`backend/fu/wrapper/Alu.scala:8-22` 传递功能码和结果；`backend/exu/ExeUnit.scala:328-374` 选择执行结果/写使能，`backend/Backend.scala:667-680` 接入写回路径。`src/test/scala/xiangshan/DecodeTest.scala:38-49` 的 `DecodeUnitTest` 不检查 ADD 语义；入口见 `Makefile.test:10-12`。
- Heliodor: `sources/heliodor/src/core/decoder.veryl:413-428` 以 `Opcode::OP`、`funct7=0`、`funct3=0` 选择 `AluOp::ADD`；`src/core/alu.veryl:143-155` 区分 64 位 ADD 与 ADDW；`src/core/alu_wrap.veryl:121-132,400-421` 选操作数并形成 CDB 结果；`src/core/heliodor_core.veryl:3362-3368` 接到整数 PRF 写端口。`tb/test_alu.veryl:33-45,223-249` 含 ADD 向量并在 29 次时钟迭代后执行一次 `pass` 断言，但未等待 `done` 或检查 `tc`；静态源码不能确认断言时对应的案例，因此不能据此证明 ADD 或 DIV 已验证。默认入口 `veryl test` 未运行，Veryl 不在当前 PATH。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/add-v1.md` — 按 Story 1.2 模板记录 RV64I ADD 的规范行为、覆盖/排除子案例、自检答案、两边 decode→execute→writeback 路径、比较结论和证据表；未运行测试保持 `unverified`。
- [x] `notes/units/index.md` — 将 `add` 当前版本指向 `notes/units/add-v1.md`。
- [x] `notes/units/add-pilot-retrospective.md` — 复盘模板可复用部分、实际缺口、建议修订及自建实验是否必要；依据证据只记录一个 `ready`、`adjust` 或 `defer` 阶段门结论。若为 `ready`，按用户目标列出获准启动的 Epic 2、3、4，范围遵循现有 sprint stories，按 story 顺序逐项推进，不设日历周期。

**Acceptance Criteria:**
- Given sources.lock 中的固定快照和官方 RV64I 规范，when ADD 学习记录完成，then 说明 64 位寄存器加法、模 2^64 结果、无算术溢出异常，并明确不覆盖 ADDI/ADDW 的完整实现比较。
- Given 两边实现，when 记录 ADD 路径，then 分别追踪译码、ALU 运算和结果/整数寄存器写回；至少一条比较结论由双方证据支持，且不把微架构组织差异误作 ISA 语义差异。
- Given 现有测试和验证资料，when 记录其证据，then 分清入口、检查过的测试源码和实际运行结果；没有运行的 ADD 测试不得标记通过。
- Given ADD 单元和模板，when 完成试点，then 以 `add-v1.md` 保存自检问题与有来源依据的参考答案，索引指向该版本，并记录未覆盖子案例和未解问题。
- Given 试点记录与方法复盘，when 写阶段门，then 恰有一个 `ready`、`adjust` 或 `defer`；只有 `ready` 才能启动其中明确列出的后续史诗。
- Given 试点过程，when 需要自建实验时，then 仅将学习者编写内容放入 `experiments/ADD/` 并记录快照、输入、步骤和观察；若不需要，复盘明确记为未创建。

## Implementation Notes

## Spec Change Log

## Review Triage Log

- `medium / patch` — `notes/units/add-v1.md:60` 及复盘原第 2 条把 native testbench 描述为在 DIV 案例断言；源码只在固定 29 次时钟迭代后断言一次，未等待 `done` 或检查 `tc`，无法确认所断言案例。已将 spec、学习记录、证据 E14、复盘及未决事项改为只陈述静态源码能支持的范围；ADD 与 DIV 均不视为已断言。

## Design Notes

本故事验证记录方法，不以新增上游实现或证明完整指令符合性为目标。源码检查可支持实现路径和组织差异；只有真实执行并观察到结果的命令才能形成运行证据。ADD 是 RV64I 基础指令，ADDW 是独立的 32 位运算后符号扩展变体。

## Verification

**Commands:**
- 不运行 CPU 构建、仿真或测试：当前 Heliodor Veryl 与 XiangShan Mill 工具链不可用，且本试点验收允许静态源码检查；因此不会产生 `run-pass` 证据。

**Manual checks:**
- 核对所有快照 ID/SHA 与 `sources.lock`，核对规范版本与章节。
- 按源文件路径复查两边 decode、执行、结果/写回的叙述及行号；确保每条比较结论均引用双方证据 ID。
- 核对模板章节顺序、显式子案例、自检参考答案、测试未运行标记、不可变文件名和索引版本。
- 核对复盘恰有一个阶段门结果；`ready` 时其授权史诗、范围与顺序节奏与当前用户目标一致。
