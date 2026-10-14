---
title: 'Story 6.5：运行 Sstc S/VS comparator 与陷阱对照'
type: 'feature'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
review_loop_iteration: 1
baseline_commit: 'f82e83749997c555cf2354ec1cd3ac8f9c3a7fd7'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-5-3-compare-sstc-timers.md'
  - '{project-root}/notes/units/rva23s64-sstc-v1.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — Epic 6 scope authorized; preserve Story 6.5 acceptance boundary">

## Intent

**Problem：** Sstc 的比较器、访问门控和 S/VS 中断交付已有静态对照，但欠缺对 comparator 边界与定时器陷阱的可复现 CPU 观察。

**Approach：** 在锁定的 Kunminghu 与 Heliodor 配置上运行可执行的 S/VS timer 案例，独立记录 `<`、`==`、`>`、STCE/TM 门控、guest time offset、pending、委派和陷阱。无法执行或观察的项目保留具体 blocker，不从源码推断运行结果。

**Always：** 沿用 Epic 6 锁定快照、单 hart 配置与证据 manifest；比较异步 pending 时只要求规范承诺的 eventual 行为，不臆造精确周期延迟；将 S-mode 与 VS-mode 结果分开。

**Never：** 不修改 `sources/` 上游 checkout；不把静态 RTL、已有测试源码或软件写入 pending 当成硬件观察；不声称 Sstc 或 RVA23S64 完整符合性。

| 场景 | 输入 / 状态 | 预期结果 | 错误处理 |
|---|---|---|---|
| S comparator | STCE 开/关；`stimecmp` 分别低于、等于、高于可见 `time` | 记录比较状态、STIP/pending、交付模式、cause 与退出 marker | 缺少控制或观察能力则记 `blocked`，指出具体缺项 |
| VS comparator | 非零 `htimedelta`；`vstimecmp` 与 guest time 的三种关系；逐级改变 STCE/TM 和委派 | 分别记录 guest time、VSTIP、HS/VS 路由与 cause | 不把零 offset 或单一 gate 结果外推到其他组合 |
| 异步传播 | 比较器或 gate 改变 | 等待有界预算内 pending/陷阱最终可见，不要求固定 cycle | 超预算时区分 CPU 已启动的行为失败与未观察启动 |

</frozen-after-approval>

## Code Map

- `notes/units/rva23s64-sstc-v1.md`：Sstc v1.0 与 RVA23S64 要求、上一轮静态路径、既有测试覆盖和明确未验证矩阵；沿用其术语，但把本故事新增动态结果分开记录。
- `experiments/kunminghu-smoke/run.py`：锁定检查、RV64 镜像构建、Kunminghu 单 hart emulator/NEMU、good-trap 分类及 manifest 归档；runner 当前针对通用 fixture/Zifencei，扩展前须保持原两条路径兼容。
- `sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/{SupervisorLevel,VirtualSupervisorLevel,CSRPermitModule,SstcInterruptGen,Unprivileged,NewCSR}.scala`：活动 `NewCSR` 路径的 comparator、time/htimedelta、pending 与 CSR 权限门；`MachineLevel.scala` 和 `TrapHandleModule.scala` 连接 pending 与陷阱。`src/test` 没有已发现的 Sstc 定向案例。
- `experiments/heliodor-smoke/run.py`：锁定 checkout 和临时 harness 变换；`transform_arch_harness()` 可截取单一命名 arch target，并对 DRAM 初始化添加局部 allow。增加 Sstc target 时应保留目标自己的 fixture 路径和结果 label。
- `sources/heliodor/src/core/csr.veryl:441-475,529-613,620-712,859-886,1022-1144`：S/VS comparator、`time+htimedelta`、STIP/VSTIP 与 trap 路由。`alu_wrap.veryl:446-466` 通用 CSR 检查未见 STCE/TM 专用 gate，须作为待验证项，不得宣称已证实。
- `sources/heliodor/test/sstc/sstc_test.S`、`test/hsstc/hsstc_test.S` 及 `tb/test_arch_common.veryl` 对应的 `test_arch_sstc_stimecmp` / `test_arch_hsstc` 是现有候选；分别只有单侧门控/零 offset 覆盖。Veryl 0.22.0 直接测试曾被 `$readmemh` 的 `invalid_initial_assign` 阻断；应在隔离副本中复用 Story 6.3 workaround 后重试。
- `notes/units/evidence/cpu-validation-toolchain-v1.yaml`：记录来源 revision、输入、配置、工具、启动分类、退出码、日志与哈希；运行记录追加后执行其 validator。

## Tasks & Acceptance

**Execution：**
- [x] `experiments/sstc/` 与 `experiments/heliodor-smoke/run.py`：提供可复现的 S/VS timer 输入与单目标隔离执行；逐项运行并归档以下矩阵：
  - S 比较器在 STCE=1、TM=1 下覆盖 `<`、`==`、`>`；分别独立关闭 STCE、TM，并确认 stimecmp 访问异常 cause=2；记录比较器写入前后的 pending 观察。
  - VS 比较器以非零 `htimedelta` 覆盖 `<`、`==`、`>`，每个允许访问案例显式记录 `menvcfg.STCE`、`henvcfg.STCE`、`mcounteren.TM`、`hcounteren.TM`。
  - VS 访问门分别独立关闭 M STCE、H STCE、M TM、H TM，并观察规范要求的 cause 2 或 cause 22；不得让更早的 time/vstimecmp 读取截断目标访问。
  - VS 路由分别验证 VSTIP 委派到 VS cause 5、未委派到 HS cause 6；成功路径必须在 VS/HS handler 中核对 cause、pending 与重设比较器后的清除。
  - Kunminghu 对可运行的 S 比较器与门控输入逐项运行；若运行环境仍不能到达目标断言，保留带实际 PC/cause/权限原因的 `blocked` 证据，不用 BADTRAP 或泛化结论替代。
- [x] `experiments/kunminghu-smoke/run.py`：支持 Sstc fixture 的构建与运行归档，先为 S-mode 代码建立 PMP 可执行权限，保留通用 fixture、Zifencei 路径行为。
- [x] `scripts/tests/`：增加 Sstc 参数矩阵、仓库外 fixture 路径、CPU 启动/结果分类与陷阱 cause 断言；测试须实际执行并通过。
- [x] `notes/units/rva23s64-sstc-v1.md`、`notes/rva23-coverage.md`、`notes/units/index.md`：追加逐项实际运行结果、显式控制值、输入哈希、pending/trap 观察与 blocker；coverage 保持 `studied-unverified`。
- [x] `_agile-output/implementation-artifacts/spec-6-5-sstc-s-vs-timer-evidence.md` 与 `sprint-status.yaml`：记录复验、审查 triage，并在审查完成后同步故事状态。

**Acceptance Criteria：**
- Given 锁定的 Kunminghu 与 Heliodor 配置，when 追踪 Sstc 路径，then 记录 `stimecmp`、`vstimecmp`、裸时间和 guest `time+htimedelta`、STCE/TM gate、pending 与委派端点；未证实部分标为 unknown。
- Given 可运行的 S-mode fixture，when 对 `time < stimecmp`、`time == stimecmp`、`time > stimecmp` 分别测试 STCE/TM 启用和禁用，then 保存 pending 转变、陷阱是否交付、cause、目标特权模式与观察预算。
- Given 可运行的 VS fixture，when 使用非零 `htimedelta` 并独立改变两级 STCE/TM、委派和 VSTIP 路由，then 分别保存每阶段控制值、guest time、pending 与 HS/VS 结果。
- Given 某项输入无法注入或结果不可观察，when 运行器收敛结果，then 记录具体 blocker 和 `blocked`；仅在 CPU 已启动且期望断言失败时记 `run-fail`。
- Given 异步计时器中断，when 比较实测延迟，then 以 Sstc eventual-pending 要求评估，不添加规范未规定的周期精确期望。

## Implementation Notes

本 spec 曾有一轮不完整实现；其代码已在 BMAD bad-spec loopback 中撤回。以下运行记录只作为诊断历史，不作为当前实现或验收证据。旧运行日志临时保存在 `/tmp/learning-rv64-6-5-loopback-evidence/`，重做时必须重新生成并更新 manifest。

- 历史实现曾尝试 Heliodor Sstc target 和项目自有 S/VS fixture；不完整代码已撤回，版本化输入快照的做法可保留。
- 历史 Kunminghu fixture 未设置 PMP；锁定单核 emulator 因 PMP 拒绝 S-mode PC `0x8000006c` 而报 instruction access fault cause 1/BADTRAP。新实现应先配置有效 PMP，再复验；若仍无法到达目标断言，完整记录观察到的 PMP/异常状态。
- 历史运行曾出现 S boundary、TM gate 与 VS cause 5 的 pass marker；审查发现等值时序、VS 目标 CSR 先后顺序、TM 控制值和 cause 元数据存在问题，因此不得复用作验收结论。
- VS successful delivery fixture checks cause 5 in VS `scause`/`vscause` and only emits pass after guest timer handling and M-mode completion. S successful delivery checks cause 5 in S `scause`; the negative `<` pending check is sampled in M-mode before S entry.
- 新实现必须完成 S/VS 的完整验收矩阵；VS `<`/`==`/`>`、独立 M/H STCE 与 TM 门控、两种可观察路由均不可删减。
- 早期 manifest 中 `kunminghu-fixture-20261014T064944Z-3e81181d1d02` 的 common source 原快照缺失，SHA 差异未被覆盖；旧结果保留来源缺口说明，不作为验收结果。复验使用版本化输入和不可变副本。

## Spec Change Log

## Review Triage Log

- blind-hunter：`s-comparator.S` 的 `==` 仅使用较早读取的 time 样本，不能证明比较器写入时仍相等；medium，bad_spec（任务计划未定义等值观测的可验证方法，且实现宣称满足 AC）。
- blind-hunter / edge-case-hunter：`vs-htm-off` 在读取/写入 vstimecmp 前先执行 `csrr time`；medium，bad_spec（矩阵计划遗漏了目标访问顺序，hcounteren gate 可能由 time 访问先行触发）。
- blind-hunter / edge-case-hunter：VS comparator `<`、`==`、`>` 没有独立输入；medium，bad_spec（当前计划只实现一个 future comparator，和验收边界不符）。
- blind-hunter / edge-case-hunter：VS M/H STCE、M/H TM 没有分别独立关闭并核对目标异常；medium，bad_spec（矩阵计划未列全四个门控维度）。
- blind-hunter：VS nondelegated HS cause 6 路由无 handler 结果；medium，bad_spec（当前 fixture 仅报告 timeout marker，路由目标未被观测）。
- blind-hunter：Kunminghu 首条 S-mode 指令在未配置 PMP 时触发 instruction access fault；medium，patch（运行日志证明目标程序能从 MRET 到 S PC，但该 fixture 未赋予 S-mode 代码执行权限；加 PMP NAPOT 后复跑可验证 Sstc 断言）。
- blind-hunter：断言 `S-TM-OFF` 是更早 `time` 读取失败；false（`build_heliodor_s_fixtures.py` 在 TM=false 时不定义 `TM`，汇编改为 `li t0, 0`，先行操作只有 `csrw stimecmp`；handler 在写 pass 前检查 mcause=2）。
- blind-hunter：VS offset 元数据称 TM enabled；medium，patch（Heliodor `hcounteren`/`mcounteren` reset 为 0，`vs-offset.S` 未写它们；源控制值必须明确初始化并归档）。
- blind-hunter：CPU-started 且 `tohost=0` 会被错误地一律 `blocked`；false（`heliodor-core-20261014T064644Z-3624007` 的目标结果 marker 明确是 `tohost=0 pass=0`，`observe()` 将此断言失败归类 run-fail）。
- blind-hunter：测试套件有 141 pass/1 fail 的 Zifencei evidence link；medium，defer（既有页面/审计缺陷不由本故事引入；独立在 deferred-work 追踪并于结项前修复）。
- verification-gap：缺少覆盖 repo-local `experiments/...` fixture 选择、manifest input 路径与 hash 的 run-level test；medium，patch（现有测试只测 source transformation，不覆盖 `run()` fixture dispatch）。
- edge-case-hunter：报告 VS cause 22 被 fixture 当作失败；false（`vs-gates.S` 在 `HTM_OFF` 分支显式期望 cause 22，`hs_handler` 比较成功才写 tohost=1；实际问题是 runner 元数据误报 cause 2，已在相邻条目记录）。

- 2026-10-14: 独立审查发现实现计划允许仅跑矩阵子集，与冻结意图和验收条件冲突。保留的实现要点（KEEP）：Heliodor 继续使用隔离复制的单目标测试；Kunminghu 继续使用锁定的单核 emulator/NEMU 与输入哈希归档；每个运行保留版本化源文件快照；不修改 `sources/` 上游；不以静态分析或软件 pending 写入代替硬件比较器观察。
- 2026-10-14: 计划修订为逐项实现 S 3 个比较边界与独立门控，VS 非零 offset 的 3 个边界、4 个独立访问门、VS/HS 两种路由，并为 Kunminghu S-mode fixture 配置 PMP。已知错误状态：当前 S 等值输入不能证明写入时等值；VS hcounteren 案例在目标 CSR 访问前先读 `time`；VS 比较边界和独立 gate 组合缺失；Kunminghu S-mode 受未配置 PMP 阻挡。
- 2026-10-14: 审查 false finding：S TM-off fixture 的构建宏使其不读 `time`，而由 M handler 检查 `stimecmp` CSR 访问的 mcause=2；因此“更早 time read 导致目标误判”不成立，不能作为 S TM-off 缺陷。
- 2026-10-14: 审查 false finding：VS gate 汇编明确在 `HTM_OFF` 分支期望 `scause=22`，该 cause 的 fixture 检查并未把正确异常当作失败。独立问题是运行记录硬编码成 cause 2 且目标 CSR 前读取 `time`，须在重做矩阵时修正。
- 2026-10-14: 审查 false finding：VS HS 路由 `tohost=0/pass=0` 是测试台实际打印的目标结果 marker，runner 因明确 `pass=0` 归类 `run-fail`，并非“没有结果 marker”或无条件 `blocked`。
- 2026-10-14: 完整测试套件 141 passed、1 failed；失败为 Zifencei coverage link 中缺少 E1/E2/E3/E5/E7。该历史缺陷不由 Story 6.5 引入，另记入 deferred work 并在项目结项前修复/复验。

## Design Notes

Sstc comparator 采用无符号 `time >= compare`。等于案例应由同一次读取的时间值写入 compare，之后只断言规范要求的最终 pending，不用相邻 cycle 的延迟作精确判断。VS guest time 为 64 位截断的 `time + htimedelta`；记录实际输入以证明 offset 非零。软件写入 `mip/hvip` 仅用于隔离 legacy 行为，不能计为硬件 comparator 通过。

## Verification

**Commands：**
- `python3 experiments/kunminghu-smoke/run.py --topic sstc ...` -- 每个 run ID 对应完整输入、日志、CPU-start、退出与 trap/pending 结果。
- `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic sstc ...` -- 每个 S/VS target 独立记录输入、工具、结果 marker 与日志。
- `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" uv run --no-cache pytest -q scripts/tests/` -- 相关回归通过。
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- manifest 有效。

**Manual checks：**
- 对照 Sstc v1.0 与 RVA23S64 v1.0 要求，确认测试结论没有超出实际运行的 hart、模式、offset、gate 与委派组合。

## Implementation Progress (2026-10-14)

- 完成 S/VS fixtures、矩阵运行器和不可变逐次输入快照；Kunminghu S-mode 配置 PMP NAPOT。Heliodor VS 用例在进入 VS 前将 `vstimecmp` 置为 `-1`、保持 `hgatp=Bare`，并在 comparator 写入前确认 VSTIP 为低。VS/HS 成功路由 handler 检查 cause 和 pending，复位比较器后用有界轮询确认 pending 清除。
- Heliodor 最新 S/VS 矩阵：S、VS `<`/`==`/`>` 全部 `run-pass`；VS 委派到 VS cause 5 与未委派到 HS cause 6 两种路由均 `run-pass`。S 的 STCE/TM 两门和 VS 的 M/H STCE/TM 四门均 CPU-started `run-fail`，观察到目标 CSR 写后 fallthrough（`tohost=0x210`），没有陷阱；按实现缺陷保留，不标成环境 blocker。
- Kunminghu 最新 S 矩阵五项全部 `run-pass`：`<` sample=41/cmp=49，`==` 41/41，`>` 41/33；STCE-off 与 TM-off 均校验 cause 2。Sstc 探针以 `RV64IMA_Zicsr` 编译，禁用 C 仅为本证据的算术/trace 清晰度，不覆盖压缩指令。
- 独立审查发现并修复 stale VS pending、Kunminghu CSR write operand 取证、异步 pending clear 立即读取以及 VS trap-origin 元数据问题。`mstatus=0x8000000802` 的 MPV/MPP 位复核为有效，原“没有进入 VS”发现判 false。
- Heliodor/Kunminghu 定向 runner tests：74 passed。全量 `scripts/tests/`：145 passed；manifest validator、RVA23 coverage checker、doc-link checker、`py_compile` 与 `git diff --check` 均通过。Sstc coverage 仍为 `studied-unverified`，因为 Heliodor 的 6 个访问门没有按预期陷阱；失败作为核心观察保留，不影响本故事的证据采集验收完成。

## Final Review Triage (2026-10-14)

- 验收审查发现 VS 进入前的 `vstimecmp=0` 可造成 stale VSTIP，Kunminghu parser 把无 rd 的 CSR write `data` 当 comparator；均已修复：初值设为 `-1` 并在写入前检查 pending，trace 从 CSR `rs1` 最近一次提交值还原操作数。
- 验收审查指出路由 handler 不应假设 pending 写后立即清除；VS/HS handler 改为有界轮询，超时写失败 marker，并为最新生成器产物补充运行证据。
- edge review 关于 MPV 未设置的发现为 false；`0x8000000802` 包含 mstatus.MPV(bit 39) 与 MPP=S(bit 12:11)。VS trap marker 未编码起源模式，runner 现记录为 unknown，不再推断为 HS。
- 最新 Kunminghu `s-lt` 为 run-pass（sample=41, comparator=49）；早期 PC `0x80000096` 的 run-fail 是未修复输入/trace 版本的历史记录，不代表最终结果。
