---
title: 'Story 5.3：比较 Sstc 与 S/VS timer'
type: 'feature'
created: '2026-10-13'
status: 'in-progress'
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
- `notes/rva23-coverage.md`：要求键 `RVA23S64/v1.0/§3.1.2.2/Sstc`；两侧当前为 `not-studied`。完成后按实际证据更新状态并链接本单元。
- Kunminghu 活动路径：`wrapper/CSR.scala:65` 实例化 `NewCSR`（`EXT_SSTC=true`）；检查 `SupervisorLevel.scala:131-193`、`VirtualSupervisorLevel.scala:191-265`、`CSRPermitModule.scala:225-228,443-445,616-619`、`SstcInterruptGen.scala:33-35`、`Unprivileged.scala:151-166` 与 `NewCSR.scala:532-606,710-717`，再追踪 MachineLevel 的 pending/委托。旧 `backend/fu/CSR.scala` 不是活动证据。未发现 Sstc 定向测试。
- Heliodor：`src/core/csr.veryl:362-475,529-620,640-715,859-886,1022-1144`；`alu_wrap.veryl:446-466` 通用 CSR 权限检查。测试入口：`test/sstc/sstc_test.S` + `tb/test_arch_common.veryl:4557-4583`；`test/hsstc/hsstc_test.S` + `:5876-5902`，均启用 `MTIME_EN`、100000 cycles。候选命令为 `veryl test --test test_arch_sstc_stimecmp` 和 `veryl test --test test_arch_hsstc`。本地缺 PATH 中 Veryl；Story 5.2 的 Veryl 0.22.0 调用在 testbench check 遇 `$readmemh`/`dram` `invalid_initial_assign` 退出 1，本故事须重试并记录。
- 规范：[Sstc v1.0](https://docs.riscv.org/reference/isa/v20250508/priv/sstc.html)、[RVA23 v1.0](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)。Kunminghu 未发现定向仿真用例或 fixture runner。

## Tasks & Acceptance

**Execution：**
- [ ] `notes/units/rva23s64-sstc-v1.md` — 新建双核学习单元，记录 S/VS 行为、实现路径、证据、自检和边界。
- [ ] `notes/rva23-coverage.md` — 更新 Sstc 两侧状态、理由、子案例和证据链接，保留动态验证边界。
- [ ] `notes/units/index.md` — 登记单元和实际验证/阻塞状态。
- [ ] Heliodor 定向目标 — 运行 S/VS 命令并记录工具、输入、期望、观察/阻塞与日志；核对比较阈值和门控覆盖，缺项标未验证。
- [ ] Kunminghu — 查明可执行 CSR/interrupt harness；可运行时验证比较与门控，否则记录缺失项及阻塞。

**Acceptance Criteria：**
- Given Sstc v1.0 与 RVA23S64 要求，when 界定案例，then 覆盖 `stimecmp`、`vstimecmp`、两级 STCE、pending 与委托/可见性。
- Given 两侧锁定配置，when 追踪 S/VS timer，then 记录 CSR 访问、time/guest time（含 `htimedelta`）、比较器、pending 和中断交付；未知配置或连线明确标注。
- Given 有可执行的比较器案例，when 检查阈值行为，then 覆盖小于、等于、大于比较值及启用/禁用门控；记录实际观察。无法执行的用例保留具体 blocker 和未验证标记。
- Given Heliodor VS 路径，when 检查 guest timer，then 独立追踪 `vstimecmp`、`henvcfg.STCE`、guest offset 与 VSTIP；未运行不得推断通过。
- Given 异步中断结果，when 比较观察与规范，then 依据规范有界评估要求，不附加无依据的 cycle-exact 延迟要求。
- Given 单元完成，when 学习者复核，then 可解释两条路径、实现差异和未测试边界；运行结论均有命令、配置、输入和观察证据。

## Implementation Notes

## Spec Change Log

## Review Triage Log

## Verification

**Commands：**
- `git -C sources/xiangshan rev-parse HEAD`、`git -C sources/heliodor rev-parse HEAD` — 与锁定 SHA 一致。
- `cd sources/heliodor && veryl test --test test_arch_sstc_stimecmp` 与 `veryl test --test test_arch_hsstc` — 记录真实退出状态、观察与产物；本地 PATH 当前找不到 `veryl`，需按实现时可用工具重试，不将候选命令算作测试结果。
- `git diff --check` — 文档与单元索引无空白错误。

**Manual checks：**
- 对照规范核对 CSR 可访问条件、比较条件及异步 timer interrupt 有界评估；确认 S、VS 路径和证据状态分别记录。
