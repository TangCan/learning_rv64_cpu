---
title: 'Story 5.3：比较 Sstc 与 S/VS timer'
type: 'feature'
created: '2026-10-13'
status: 'done'
baseline_commit: 'f3b76ba24fe55d936b4f9df01bb4e4c272f16664'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/notes/units/rva23s64-deep-dive-readiness-v1.md'
  - '{project-root}/notes/units/rva23s64-zifencei-v1.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** RVA23S64 要求 Sstc，但仅发现比较 CSR 或 pending 位不能说明访问门控、guest time offset 与 S/VS 中断交付路径。

**Approach：** 对照锁定的 Kunminghu V2 与 Heliodor 快照，追踪规范、比较寄存器、`STCE` 门控、可见时间、pending 与委托；检查现成测试及其可运行性，并记录未验证边界。

**Always：** 使用 Sstc v1.0 与 RVA23S64 v1.0 §3.1.2.2/Sstc；区分静态源码、测试材料和实际运行；检查 `<`、`==`、`>` 比较关系、STCE 门控、VS `htimedelta`，并依据规范有界评估异步中断，不臆定周期精确延迟。

**Never：** 不修改 `sources/` 上游 checkout；不把 test source、注释或源码路径当作运行通过；不将单侧测试推广为符合性结论；工具或 harness 阻塞时记录命令、具体错误与未覆盖范围。

</frozen-after-approval>

## Code Map

- `sources.lock` 固定基线：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；checkout HEAD 已复核一致。
- `notes/rva23-coverage.md`：要求键 `RVA23S64/v1.0/§3.1.2.2/Sstc`；开始本故事时两侧为 `not-studied`，本次完成静态调查后更新为 `studied-unverified` 并链接本单元。
- Kunminghu 活动路径：`wrapper/CSR.scala:65` 实例化 `NewCSR`（`EXT_SSTC=true`）；检查 `SupervisorLevel.scala:131-193`、`VirtualSupervisorLevel.scala:191-265`、`CSRPermitModule.scala:225-228,443-445,616-619`、`SstcInterruptGen.scala:33-35`、`Unprivileged.scala:151-166` 与 `NewCSR.scala:532-606,710-717`，再追踪 MachineLevel 的 pending/委托。旧 `backend/fu/CSR.scala` 不是活动证据。未发现 Sstc 定向测试。
- Heliodor：`src/core/csr.veryl:362-475,529-620,640-715,859-886,1022-1144`；`alu_wrap.veryl:446-466` 通用 CSR 权限检查。测试入口：`test/sstc/sstc_test.S` + `tb/test_arch_common.veryl:4557-4583`；`test/hsstc/hsstc_test.S` + `:5876-5902`，均启用 `MTIME_EN`、100000 cycles。候选命令为 `veryl test --test test_arch_sstc_stimecmp` 和 `veryl test --test test_arch_hsstc`。本地 PATH 中没有 Veryl；本故事已用本机绝对路径的 Veryl 0.22.0 重试，两目标均在 testbench check 因 `$readmemh`/`dram` `invalid_initial_assign` 退出 1，具体结果见 Verification。
- 规范：[Sstc v1.0](https://docs.riscv.org/reference/isa/v20250508/priv/sstc.html)、[RVA23 v1.0](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)。Kunminghu 未发现定向仿真用例或 fixture runner。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-sstc-v1.md` — 新建双核学习单元，记录 S/VS 行为、实现路径、证据、自检和边界。
- [x] `notes/rva23-coverage.md` — 更新 Sstc 两侧状态、理由、子案例和证据链接，保留动态验证边界。
- [x] `notes/units/index.md` — 登记单元和实际验证/阻塞状态。
- [x] Heliodor 定向目标 — 已运行 S/VS 命令并记录工具、输入、期望、观察/阻塞与日志；核对比较阈值和门控覆盖，缺项标未验证。
- [x] Kunminghu — 已查明未定位可执行 CSR/interrupt harness；记录缺失项及工具阻塞。

**Acceptance Criteria：**
- Given Sstc v1.0 与 RVA23S64 要求，when 界定案例，then 覆盖 `stimecmp`、`vstimecmp`、两级 STCE、pending 与委托/可见性。
- Given 两侧锁定配置，when 追踪 S/VS timer，then 记录 CSR 访问、time/guest time（含 `htimedelta`）、比较器、pending 和中断交付；未知配置或连线明确标注。
- Given 有可执行的比较器案例，when 检查阈值行为，then 覆盖小于、等于、大于比较值及启用/禁用门控；记录实际观察。无法执行的用例保留具体 blocker 和未验证标记。
- Given Heliodor VS 路径，when 检查 guest timer，then 独立追踪 `vstimecmp`、`henvcfg.STCE`、guest offset 与 VSTIP；未运行不得推断通过。
- Given 异步中断结果，when 比较观察与规范，then 依据规范有界评估要求，不附加无依据的 cycle-exact 延迟要求。
- Given 单元完成，when 学习者复核，then 可解释两条路径、实现差异和未测试边界；运行结论均有命令、配置、输入和观察证据。

## Implementation Notes

- 新建 [Sstc 双核学习单元](../../notes/units/rva23s64-sstc-v1.md)，记录规范要求、两边 CSR/计时/pending/路由静态路径、测试材料覆盖、自检和未验证边界。Kunminghu 当前没有定位定向 CPU harness；Heliodor 通用 CSR permission 追踪中未找到 STCE/TM 专用访问门控，作为静态待核项呈现。
- `veryl test --test test_arch_sstc_stimecmp` 与 `veryl test --test test_arch_hsstc` 均实际退出 1；两次都因 `tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)` 检查错误 `invalid_initial_assign` 阻断，仿真未启动。完整命令输出保存在本机 `/tmp/story-5-3-sstc-stimecmp.log`、`/tmp/story-5-3-hsstc.log`；关键错误摘录已写入单元验证记录，避免将临时路径当作唯一证据。
- 覆盖目录将两侧 Sstc 从 `not-studied` 改为 `studied-unverified`，状态汇总相应调整；不把测试源码或静态路径写成动态通过。
- Sstc 状态变更后，已同步覆盖检查器的 S64 固定计数，以及 Story 4.10 审计页的当前汇总和时间说明；审计正文保留了 Story 4.10 当时的历史结论。

## Spec Change Log

## Review Triage Log

| Finding | Verdict / evidence | Route |
|---|---|---|
| Blind review：sprint 状态仍为 `in-progress` | low：实现任务已经完成且规格进入 `in-review`；状态定义将 `review` 用于实现完成待审。现已同步 sprint 状态为 `review`。 | patch — 已同步状态 |
| Blind review：Code Map 将 Sstc 描述为当前 `not-studied` | low：该句在实现后已过时，可能让读者误读覆盖目录；现已明确这是开始故事时的状态。 | patch — 已修正文案 |
| Blind review：覆盖计数检查器期望值过期 | medium：运行器实际读到 S64 Kunminghu `37/19/2`、Heliodor `26/27/3/2`；固定期望值仍是 Zifencei 更新前数字，导致本故事覆盖变更后的标准检查失败。 | patch — 已更新当前期望值 |
| Verification-gap review：覆盖计数检查器仍失败（与上一项同根因） | medium：同一运行输出确认 `37/17/4` 与 `37/19/2` 不符；已与上一项一并同步两侧计数。 | patch — 与上一项共同修复 |
| Blind review：运行日志只有临时路径 | low：`/tmp` 在其他工作区不可访问；现已将两次失败的关键 Veryl 错误原文保存在本单元中，并保留运行环境临时完整日志路径作为补充。 | patch — 已补充持久证据摘录 |
| Blind review：Heliodor 专用 CSR gate 的 S/VS 结论不够分明 | low：通用权限检查不显示 `STCE/TM` 门控；现已分列 S-mode 与 VS-mode 读写条件，并标出未被检查路径证明的部分。 | patch — 已补充分层说明 |
| Blind review：S 用例的 `STCE=0` 负向断言条件不清 | low：测试源设置比较值 0、M-mode timer enable、全局 MIE 和失败陷阱向量；现已说明这些输入为何能观察意外 M timer trap。 | patch — 已补充断言条件 |
| Blind review：Kunminghu harness 负搜索不易复现 | low：未记录确切搜索调用和可执行 harness 的判定条件；现已补充路径、命令、无匹配观察与结论边界。 | patch — 已补充搜索证据 |

## Verification

**Commands：**
- `git -C sources/xiangshan rev-parse HEAD` — `c098f996bf4d301b88693b20315486d31e93bc9d`，与 `sources.lock` 一致。
- `git -C sources/heliodor rev-parse HEAD` — `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，与 `sources.lock` 一致。
- Heliodor S：cwd `sources/heliodor`，Veryl `0.22.0 (967e477 2026-10-02)`，命令 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_sstc_stimecmp`，退出 1；testbench check 在 `tb/test_arch_common.veryl:440` 因 `$readmemh`/`dram` `invalid_initial_assign` 失败，测试体未启动，无仿真产物。输入 hex `test/sstc/sstc_test.hex`，预算 100000 clocks；本机完整日志 `/tmp/story-5-3-sstc-stimecmp.log`，关键错误摘录保存在单元验证记录中。
- Heliodor VS：cwd `sources/heliodor`，相同工具版本，命令 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_hsstc`，退出 1；同一 `invalid_initial_assign` 阻断，测试体未启动，无仿真产物。输入 hex `test/hsstc/hsstc_test.hex`，预算 100000 clocks；本机完整日志 `/tmp/story-5-3-hsstc.log`，关键错误摘录保存在单元验证记录中。
- Kunminghu：`command -v mill` 无结果，checkout 无 `mill` wrapper；`src/test/` 下限定检索 `sstc`/`stimecmp`/`vstimecmp` 无定向目标。通用 emu 构建未提供该故事程序的装载和可观察结果，因此没有伪造 CPU 测试命令/结果。
- `git diff --check` — 退出码 0，无输出。
- `python3 scripts/check_rva23_coverage.py` — 退出码 0；92 profile rows、184 状态格、去重 59 项，S64 Kunminghu `37/19/2`、Heliodor `26/27/3/2`。
- `python3 -m pytest -q scripts/tests/test_check_rva23_coverage.py` — 退出码 0，15 passed。

**Manual checks：**
- 已对照 Sstc v1.0 §12.1–12.3 与 RVA23S64 v1.0 §3.1.2.2 核对 STCE/TM、无符号 `>=`、`htimedelta` 的 64 位 guest time 和 eventual pending 约束；学习单元分别记录 S/VS。
- 已核对测试源码：S 用例含 STCE=0 的 M-mode 负向与 STCE=1 的 S interrupt 用例；VS 用例只开两级 STCE、`htimedelta=0` 并委托到 VS。均未单独区分 `<`/`==`/`>`，关闭各门控时的 S/VS CSR 异常、非零 offset 和独立 gate 均标为未验证。
- 覆盖目录两个 Sstc 状态均为 `studied-unverified`；Heliodor 测试退出失败不计作通过，Kunminghu 侧没有运行结果。
