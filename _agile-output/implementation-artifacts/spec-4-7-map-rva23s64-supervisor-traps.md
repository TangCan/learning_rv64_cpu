---
title: 'Story 4.7: 映射 RVA23S64 监督模式与陷阱要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '03d36804a0401739da4e668c735df22220060475'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-6-map-rva23u64-memory-cache.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23S64 的 supervisor 基础模式与陷阱要求尚未映射到两套固定 CPU 快照，特别是 U/S ECALL 路由、S-level trap 状态与向量寄存器行为的可复查证据仍缺失。

**Approach:** 依据 RVA23 Profile v1.0 与特权架构 1.13，追踪 profile 基础 RV64I/ECALL、Ss1p13、Sstvecd、Sstvala、Sscounterenw 和 Ssu64xl，并把 RTL、测试材料、运行结果分层记录在覆盖目录和新学习单元中。

## Boundaries & Constraints

**Always:** 逐项映射六个要求键；保留 S64 对 U64 的继承链接，不重复计算已由前序故事映射的要求。ECALL 按来源特权级、异常委托、S/M 目标分别记录；Sstvecd 核对 Direct 模式及所有有效四字节对齐 BASE 的能力；Sstvala 按故障地址/指令类别拆分。区分源码线索、已检查测试和本轮真实运行。

**Never:** 不修改上游快照；不把局部 CSR/陷阱路径或有限定向测试写成 profile 完整符合性；不把 H/VS、页表 walk、page-fault A/D 与地址转换机制扩张进本故事（留给 4.8/4.9）；不把 Debug Module 或 profile 建议误记为本故事必选项。

</frozen-after-approval>

## Code Map

- `notes/rva23-coverage.md`：更新 `RVA23S64/v1.0/§3.1.2.1/RV64I` 与 `§3.1.2.2/{Ss1p13,Sstvecd,Sstvala,Sscounterenw,Ssu64xl}` 六行；其余继承行、分页与 Hypervisor 行不改。
- `notes/units/rva23s64-supervisor-traps-v1.md`、`notes/units/index.md`：按学习记录模板补充规范要求、特权级/异常子案例、比较结论与可追溯证据。
- Kunminghu：固定于 `sources.lock`。检查 `src/main/scala/xiangshan/backend/fu/CSR.scala` 的 ECALL 分类、medeleg/mideleg、中断使能、trap vector、sepc/scause/stval 与 S 状态更新；检查 `backend/fu/NewCSR/SupervisorLevel.scala`、`TrapHandleModule.scala`、trap entry/SRET events。静态实现位置不等同动态验证。
- Heliodor：固定于 `sources.lock`。检查 `src/core/heliodor_core.veryl` 的 ECALL cause/delegation/target、`src/core/csr.veryl` 的 S CSR 与 trap/SRET 更新；检查 `test/c/smode_umode_test.S`、`smode_timer_test.S`、`smode_plic_test.S`、`smode_minikernel_test.S` 等既有用例，并按项目实际 runner 决定可运行范围。H 测试只作边界参考。
- 规范：[RVA23 Profile v1.0 §3.1.2.1–3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)；[RISC-V Privileged Architecture v1.13](https://docs.riscv.org/reference/isa/priv/priv-intro.html)。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 为六个 S64 基础/监督要求补足双侧状态、范围决定、异常子案例与证据回链，保留既有继承关系和其他领域。
- [x] `notes/units/rva23s64-supervisor-traps-v1.md` — 建立学习单元，分别记录 U/S ECALL、委托与中断、trap entry/return、stvec/stval 要求及测试证据边界。
- [x] `notes/units/index.md` — 登记本单元和真实验证状态。
- [x] 检查既有目标测试及其运行入口；尝试运行可用的 S-mode 定向 harness，记录工具版本、命令、输出与阻断原因；本轮已检查并尝试 PLIC harness，但工具在 check 阶段因 testbench 错误退出，测试本体未启动，不计为通过。

**Acceptance Criteria:**
- Given 六个 profile 要求键，when 查看覆盖目录，then 每项均有 Kunminghu 与 Heliodor 独立状态、路径/范围、理由、子案例和学习单元证据 ID。
- Given U/S ECALL、委托、中断、S trap entry/return、Direct stvec 与 Sstvala 的异常类别，when 阅读学习单元，then 每个声明都能追溯到规范条款和各侧静态或测试材料证据，未核实部分明确标为未验证。
- Given 已检查或运行的 S-mode 用例，when 评估覆盖范围，then 测试检查与本轮运行结果分开，个别 case 不作为全部陷阱要求的证明。

## Implementation Notes

覆盖目录已填写六个范围要求键的双侧状态、子案例和学习单元回链；新增单元区分规范、静态源码、已检查测试材料和本轮测试结果。依用户授权调整测试范围：本 story 的验收目标为学习映射而非新增/修改 RTL 或测试，不要求每个架构子案例都由自动化测试覆盖。尝试运行 Heliodor S-mode PLIC harness：PATH 中没有 `veryl`；显式调用本机 Veryl 0.22.0（967e477）和 0.22.0-nightly（c3bf469）均在 Veryl check 阶段失败，报 `test_smode_plic.veryl:172 invalid_initial_assign`，并显示其 testbench 对 Heliodor 当前模块接口有缺失端口告警。测试未启动，不记为通过；固定上游快照保持不变。

## Spec Change Log

- 依用户明确授权“运行现有测试并调整范围”，将原先要求测试启动的子任务调整为核查并尝试现有 harness、准确记录阻断；不把未启动的 harness 当作通过，也不修改固定快照。

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| 内容审查：子案例 `unconfirmed` 与覆盖目录状态词不一致 | low / patch | 在学习单元表前说明 `unconfirmed` 是子案例验证状态，覆盖目录状态是要求层级的研究状态；增加端序子案例并明确未检查。 |
| 内容审查：目标测试任务未完成但 story 已转 review | low / patch | 按用户授权调整任务为“检查并尝试可用 harness”，已完成工具调用及阻断记录并勾选；测试未启动仍明确为未通过。 |
| 内容审查：EBREAK/C.EBREAK 边界缺少直接规范条款 | low / patch | 为学习单元补充 Privileged Architecture §12.1.9 与 RVA23 Profile §3.1.2.2 的直接交叉引用。 |
| 内容审查：RV64I 小端要求没有独立子案例 | low / patch | 增加小端序 `unconfirmed` 子案例，明确本轮没有检查配置或运行环境。 |
| 内容审查：Kunminghu stvec mask 未说明高位范围 | low / patch | 依据 `stvecMask = ~(0x2)` 与 `MaskedRegMap` 写读 map 补充静态判断：只清 bit 1，保留高位 BASE 与 bit 0；任意 BASE 仍未动态验证。 |
| 内容审查：Sstvala 各类 tval 来源证据范围不清 | false | 原文已将所有类别列为 `unconfirmed`，并声明只检查 tval 通道、未逐类确认输入和值；修订补入已检查的 fault 路径线索并保留未验证结论。 |
| 内容审查：PLIC 命令与汇编测试材料关系不清 | low / patch | 补充 harness 的 `#[test]` 注册、`$readmemh` 所载 HEX、汇编源文件关系及本轮命令只选择 PLIC harness 的范围；其他测试的 harness 对应关系仍明确为未追踪。 |
| 内容审查：S-mode ECALL 委托目标表述容易误导 | low / patch | 明确 S 来源异常不能委托降到 S，非 H 环境下 cause 9 进入 M；VS cause 10 留在 H/VS 后续范围。 |
| 内容审查：Kunminghu scounteren 证据未确认活动 CSR 路径 | low / patch | FuConfig 绑定旧版 `backend.fu.CSR`；NewCSR TODO 不作为活动实现结论。覆盖记录将 mask=0 与 HPM counter 集合列为潜在冲突并保持未定。 |
| 验证审查：sprint 测试未锁定单条 story 状态 | defer | 当前通用 sprint-status validator 验证格式；为每个故事状态新增专门测试超出本 story 的学习映射范围。本次已运行 validator 且通过，跟踪文件为有效状态。 |

## Verification

**Commands:**
- Heliodor: `/nvme_data1/richard/.local/share/veryl/toolchains/{latest,nightly}/veryl test --test test_smode_plic` — 两版本都在 check 阶段因现有 harness 报错而退出，测试未启动。
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — 状态文件有效。
- `git diff --check` — 无空白错误。

**Manual checks:** 核对六个键、继承关系、Sstvala 异常类型与证据 ID 回链；不得将 Debug/H、分页和 profile 建议记为本故事必选。
