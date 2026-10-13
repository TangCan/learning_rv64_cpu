---
title: 'Story 5.4：比较 Sscofpmf 计数溢出与模式过滤'
type: 'feature'
created: '2026-10-13'
status: 'done'
baseline_commit: 'fcf9b68245e7ca6662a944da978c3f956352c31f'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/notes/units/rva23s64-deep-dive-readiness-v1.md'
  - '{project-root}/notes/units/rva23s64-sstc-v1.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** RVA23S64 要求 Sscofpmf，但仅有 `mhpmevent`、`scountovf` 或中断寄存器不能证明硬件计数器溢出、溢出状态清除、特权模式过滤与 LCOFI 交付按架构要求协同。

**Approach：** 对照固定 Kunminghu V2 与 Heliodor 快照，追踪一个可复现的 HPM 硬件事件从过滤/计数到 OF、`scountovf`、LCOFIP 和陷阱；核验已有定向测试及 ACT4/Sail 可用性，并把未覆盖行为保留为明确边界。

**Always：** 使用 Sscofpmf v1.0 与 RVA23S64 v1.0 §3.1.2.2；只把硬件事件导致的计数器回绕视为溢出证据，记录 counter、event、实现宽度/预载值、模式、门控和观察；分别检查 `MINH`、`SINH`、`UINH`、`VSINH`、`VUINH`，未知或未支持的模式不得推定已覆盖；测试日志须区分源码、输入检查和实际运行。

**Never：** 不修改 `sources/` 上游 checkout；不把直接软件写入 counter 后的回绕当硬件 overflow；不把 `OF` sticky、`scountovf` 可见、LCOFIP 清除、`mideleg` 和 trap cause 混为一项结果；不因缺少 ACT4/Sail 模型或工具而声称 DUT 失败或通过；不宣称符合性或认证。

</frozen-after-approval>

## Code Map

- `sources.lock`：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；当前 checkout HEAD 与锁一致。
- `notes/rva23-coverage.md` 中 `RVA23S64/v1.0/§3.1.2.2/Sscofpmf` 两侧为 `not-studied`；完成后应依证据更新状态，并同步目录计数/检查器的固定期望值。
- Kunminghu 活动 CSR 路径由 `backend/fu/wrapper/CSR.scala:65` 实例化 `NewCSR`，`NewCSR.scala:65` 开启扩展；查 `MachineLevel.scala:203-211,365-378,773-786` 的 HPM 状态、硬件 carry 与 OF 写清除，`NewCSR.scala:761-769,1300-1332` 的 `scountovf` 汇总、模式过滤和请求，`SupervisorLevel.scala:150-162`、`MachineLevel.scala:307-319`、`InterruptBundle.scala:24,118,212,506` 与 trap 代码追踪只读状态及 LCOFI 路由。锁定 `src/test/` 有界搜索未发现该主题的定向测试；通用 Chisel 测试/`make emu` 不是此用例已可运行的 harness。
- Heliodor 活动实现位于 `src/core/csr.veryl`，核心连线在 `heliodor_core.veryl:4752,4885-4886,8475-8491`。`csr.veryl:408-413,483-492,1202-1239` 覆盖 HPM 状态、`scountovf`、event filter、硬件 wrap 与 LCOFIP；`csr.veryl:627-695,1075-1095,1146-1153` 可追踪中断选择和 CSR 写行为。需注意模式 filter 当前静态代码只检查 M/S/U，VS/VU 位注释为 unused；counter access trap 也有未实现注释，不能把这些代码当成已验证的完整门控。
- Heliodor `test/sscofpmf/sscofpmf_test.S` 与 `tb/test_arch_common.veryl:6027-6052` 是已有目标：counter 3 / event 5（mem-port-busy），MINH 检查后由硬件事件使全 1 预载回绕，检查 M cause 13、OF 和 `scountovf[3]`；harness 预算 200000 clocks。候选命令：`cd sources/heliodor && veryl test --test test_arch_sscofpmf`。`veryl` 当前不在 PATH；Story 5.2/5.3 的显式 Veryl 0.22.0 调用被 `dram` `$readmemh` 的 `invalid_initial_assign` 阻断，须按本故事重新尝试并记录。
- 规范依据：[Sscofpmf v1.0](https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html)；RVA23 profile 依据见 [RVA23 v1.0](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)。运行 ACT4/Sail 前先核对工具、模型与 coverpoint；当前 PATH 未发现 `sail`、`act4` 或 `mill`，不可凭空构造运行结论。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-sscofpmf-v1.md` — 新建单元，说明规范要求、双核活动路径、溢出/过滤/访问/中断证据、自检及未决边界。
- [x] `notes/rva23-coverage.md`、`notes/units/index.md` — 更新 Sscofpmf 两侧状态/证据链接与学习索引；同步 `notes/units/rva23-mandatory-coverage-audit-v1.md` 的当前计数语境及 `scripts/check_rva23_coverage.py` / 对应测试的固定计数。
- [x] Heliodor 定向目标 — 实际尝试现有 test；记录工具版本、输入、event/counter、预期、观察或具体阻塞。核对 OF 清除/re-arm、`scountovf` 的 mcounteren/hcounteren 可见性、LCOFIP 清除/再触发及 M/S 委托是否被该例覆盖。
- [x] Kunminghu 与 ACT4/Sail — 查明可运行的 CSR/HPM harness、模型和 coverpoint；确认工具/模型与 harness 阻塞，并记录精确搜索/工具缺口；未安装工具或改上游源码。

**Acceptance Criteria：**
- Given 锁定配置与所选 counter/event，when 定义硬件溢出案例，then 记录实现 counter 宽度、硬件事件、预载方式、过滤状态与访问控制，不把软件写入当作 overflow。
- Given counter 硬件递增越过最大值，when 观察溢出路径，then 分别检查 OF、`scountovf`、LCOFIP 和实际 cause/陷入；未运行的路径不标通过。
- Given OF 已置位，when 检查清除与重新布防，then 记录哪种 CSR 操作清 OF、再次产生 LCOFI 的条件及观察，未覆盖则具体标为 unverified/blocker。
- Given 所选事件与模式可用，when 检查过滤，then 覆盖五个 `xINH` 模式或逐项注明不支持/未验证及证据；Heliodor VS/VU 的静态缺口不得隐去。
- Given `scountovf` 与 LCOFI 的可执行入口，when 检查访问/路由，then 分开核验 mcounteren/hcounteren、LCOFIP/LCOFIE、`mideleg` 和 trap cause；不可运行组合保留边界。
- Given ACT4/Sail 的模型和用例可用，when 执行，then 记录版本、生成测试、配置、命令与结果；工具或 coverpoint 不可用则记为环境阻塞，不记为 DUT 失败。
- Given 单元完成，when 学习者复核，then 能解释 OF/过滤/可见性/中断的关系、两侧实现差异和未覆盖案例；所有比较结论均可回链到两侧证据。

## Implementation Notes

## Spec Change Log

## Review Triage Log

| Finding | Verdict / evidence | Route |
|---|---|---|
| Blind 1: Sscofpmf section numbering conflicts | **patch** — official v1.0 page is Chapter 13; both the unit metadata and evidence now cite §§13.1.1–13.1.2. | Implementation note corrected |
| Blind 2: sprint timestamp moved backward | **patch** — baseline contained the erroneous 15:10 value; local time at this correction is 14:51 Asia/Shanghai, so the timestamp now reflects the actual current time and corrects the inherited future value. | Sprint timestamp corrected |
| Blind 3: verification outcomes absent from Verification section | **false (rejected)** — this finding asks to edit this build's spec, which the review workflow explicitly disallows as a finding fix. Actual command outcomes are present in the unit's implementation evidence and local run record. | Rejected per workflow rule |
| Blind 4: `scountovf` mode access matrix missing | **patch** — normative Sscofpmf §13.1.2 states M always-readable, S/HS gated by `mcounteren`, VS gated by both `mcounteren` and `hcounteren`; the unit now records that matrix and distinguishes it from counter CSR traps. | Unit contract and comparison table corrected |
| Blind 5: generalized visibility statement conflicts with Heliodor analysis | **patch** — same missing per-mode contract caused the ambiguity; the unit now explicitly states the normative matrix before comparing the shared Heliodor expression. | Unit contract clarified |
| Blind 6: ACT4 and Sail claims conflated | **patch** — evidence is now split: E7 records ACT4 extension configuration/test availability and separately records Sail's `Sscofpmf.supported=false`; E6 is limited to Kunminghu harness/tool search. | Evidence table corrected |
| Blind 7: MINH test behavior underspecified | **patch** — test source explicitly checks zero counter increments with MINH set and nonzero increments after clearing it; the unit now describes both expectations and says they were not run. | Test source analysis clarified |
| Verification gap reviewer: no findings | **false** — reviewer reported no verification gaps after inspecting the diff. | No action |
| Edge case reviewer: no findings | **false** — reviewer reported no edge-case findings after tracing the spec and diff. | No action |

## Verification

**Commands：**
- `git -C sources/xiangshan rev-parse HEAD` 与 `git -C sources/heliodor rev-parse HEAD` — 输出 SHA 与 `sources.lock` 一致。
- `cd sources/heliodor && veryl test --test test_arch_sscofpmf` — 若可启动，记录真实运行结果；否则记录 testbench/tool blocker，不将 test source 算作通过。
- `python3 scripts/check_rva23_coverage.py` 与 `python3 -m pytest -q scripts/tests/test_check_rva23_coverage.py` — 覆盖表行数、状态格与固定计数匹配，测试通过。
- `git diff --check` — 无空白错误。
- Heliodor 命令完整输出保存在本机 `/tmp/story-5-4-sscofpmf.log`；可移植失败摘要见单元记录。

**Manual checks：**
- 确认溢出由硬件事件增量产生，OF 清除/re-arm 操作符合规范；逐模式跟踪过滤，并分别检查 `scountovf` 门控、LCOFI pending、enable、delegation 和 trap cause。
