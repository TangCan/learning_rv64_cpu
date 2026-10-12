---
title: 'Story 4.9: 映射 RVA23S64 的 Hypervisor 必选要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'b82613827868cb8a4edeb903bcc0c89db09995be'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-8-map-rva23s64-address-translation.md'
  - '{project-root}/sources.lock'
---

<!-- <frozen-after-approval> 中的目标与边界经人工批准后锁定。 -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23S64 的 Hypervisor 强制要求尚未映射到 Kunminghu 与 Heliodor 固定快照，H 扩展、HS/VS 控制状态、陷阱信息及两阶段地址转换的实现和验证边界不清楚。

**Approach:** 依据 RVA23 Profile v1.0 的 Sha 组合定义，展开检查 H、Ssstateen、Shcounterenw、Shvstvala、Shtvala、Shvstvecd、Shvsatpa、Shgatpa 八项，记录两侧源码路径、测试材料、适用条件和未验证子案例，并更新覆盖目录与学习单元。

## Boundaries & Constraints

**Always:** 保留 Sha 的组合身份并逐项追踪八个组成要求；区分必选项与其他 H 扩展行为、静态源码、测试材料和实际运行结果；将未找到的证据记为未知/未研究，不据搜索缺失判定不支持；继承项（例如 Shvstvala 所引用的 Sstvala）须链接到先前映射。

**Never:** 不修改上游快照；不把 H CSR 存在、测试名称或 Linux 启动线索推广为完整 H/Sha 符合性；不把本轮未覆盖的 Hypervisor 扩展特性加入这八项结论；不将 Guest VM 的 profile 要求与宿主 RVA23S64 要求混为一谈。

</frozen-after-approval>

## Code Map

- `notes/rva23-coverage.md`：只填 RVA23S64/v1.0/§3.1.2.2 的 H、Ssstateen、Shcounterenw、Shvstvala、Shtvala、Shvstvecd、Shvsatpa、Shgatpa 八行；保留 Sha 按组成项去重计数的说明。
- Kunminghu：`backend/fu/NewCSR/{MachineLevel,HypervisorLevel,VirtualSupervisorLevel,StateEnBundle}.scala`、`CSRPermitModule.scala`、`NewCSR.scala`；结合活动 NewCSR 组合、CSR 权限门控与 MMU/陷阱连接判断范围。固定配置为 `sources.lock` 中 Kunminghu V2。
- Heliodor：`src/core/csr.veryl`、`heliodor_core.veryl`、`src/mmu/mmu.veryl`、`imem_mmu.veryl`、`dmem_mmu.veryl`；检查 CSR 读写/陷阱、V 状态控制、VS/G 两阶段 walk 与 fault 元数据。固定快照为 `sources.lock` 中 Heliodor。
- 既有测试：Heliodor `tb/test_arch_common.veryl` 中 H/虚拟化目标及其已检入程序；Kunminghu `src/test/scala` 中 NewCSR/CSR 测试。按用户授权尝试可运行的现有目标，不因构建受阻扩大为上游代码改动。
- 规范基线：[RVA23 Profile v1.0 §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-2-rva23s64-mandatory-extensions)；H 扩展采用 Privileged Architecture v1.13 ratified H v1.0 文本。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 补齐 Sha 八个组成要求的两侧状态、路径/范围、条件、子案例和证据链接。
- [x] `notes/units/rva23s64-hypervisor-v1.md` — 记录要求语义、两侧实现比较、测试证据、未解问题及 Sha/宿主与 guest 边界。
- [x] `notes/units/index.md` — 登记学习单元并摘要验证状态。
- [x] 检查并尝试现有 Hypervisor 定向目标；Veryl test 在共享架构 testbench check 阶段失败，测试体未运行。Kunminghu 定向测试搜索未找到可确认目标，且 Mill 不在 PATH；具体证据/命令见学习单元。不将测试源码当作运行证据。

**Acceptance Criteria:**
- Given Sha 组合及其八项稳定要求键，when 查看覆盖目录，then Kunminghu 和 Heliodor 均有可追溯状态、实现位置或范围决定、适用条件、子案例及证据 ID。
- Given 两阶段翻译、VS/HS 陷阱和配套 CSR，when 阅读学习单元，then 可分辨 profile 要求、局部实现线索、平台/特权条件与未验证行为。
- Given 未发现的 CSR、受限计数器或未执行测试，when 查看结论，then 证据缺口不会被写成已支持或明确不存在。
- Given Sha 强制项与其他 H 能力，when 查看清单和总结，then 只将八项 Sha 组成纳入本故事验收，且不宣称完整符合性。

## Implementation Notes

已按 profile 将 Sha 展开为八行，未增加组合重复计数；`Shvstvala` 链接回先前 `Sstvala` 映射。学习单元分别记录旧 CSR 与 NewCSR 的配置边界，并将 Heliodor 未定位的 state-enable CSR 保持为未知。Heliodor `test_arch_hgpf` 以 Veryl 0.22.0 尝试时，testbench check 在 `test_arch_common.veryl:440` 因 `$readmemh` 对 `dram` 的 initial assignment 失败；测试体未执行。完整 H/Sha 行为、CSR 矩阵及 trap/mode 子案例仍未验证。

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| E2 lacked the MMU/trap integration sources needed to trace its claims | low / patch | Added links to NewCSR translation mode selection, trap handling/events, and the page-table walker; E2 now names those relationships as static evidence only. |
| E2 omitted the wrapper that selects the NewCSR path | low / patch | Added `wrapper/CSR.scala` and retained `FuConfig.CsrCfg` as a separate path; the evidence now explicitly avoids claiming one path is enabled in every complete configuration. |
| E2 referred to an unsupported “M mode feed” claim | low / patch | Removed that phrase; E2 now states only linked permission, trap, translation-mode, and page-walk relationships. |
| C4 combined Shvstvala and Shtvala | low / patch | Split into separate Shvstvala and Shtvala claims; kept the blocked `test_arch_hgpf` run only with Shtvala-related evidence, not vstval evidence. |
| C6 combined Shvsatpa and Shgatpa | low / patch | Split into independent Shvsatpa (`satp`/`vsatp`) and Shgatpa (`satp`/`hgatp` SvNNx4/Bare) conclusions. |
| Inherited Sstvala cases lacked a direct mapping reference | low / patch | Added direct links to the earlier Sstvala coverage row and enumerated its inherited exception categories in the behavior table. |
| Sprint `last_updated` timestamp was earlier than the implementation update | low / patch | Updated `_agile-output/implementation-artifacts/sprint-status.yaml` at the current change time. |

## Verification

**Commands:**
- cwd `sources/heliodor`: `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl --version` — `veryl 0.22.0 (967e477 2026-10-02)`。
- cwd `sources/heliodor`: `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_hgpf` — failed in testbench check at `tb/test_arch_common.veryl:440 invalid_initial_assign`; `$readmemh(HEX_FILE, dram)` assigns `dram` in an initial block. Test did not execute; stale missing-port warnings also appeared.
- Kunminghu: `mill` is not available in `PATH`; `sources/xiangshan/src/test/scala` search did not identify a confirmed H/CSR directed target, so no Kunminghu test was run.
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — expected: `valid: true`。
- `git diff --check` — expected: no whitespace errors。
