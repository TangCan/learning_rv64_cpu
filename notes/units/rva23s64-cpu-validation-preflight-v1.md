---
unit_id: "rva23s64-cpu-validation-preflight"
stage_id: "Epic 5 retrospective action 11 / proposed Epic 6"
scope: "记录两份固定快照的 CPU 行为验证环境 preflight、实际构建阻塞、Ssstateen 失败根因和可执行后续故事；不修改上游快照。"
source_snapshots:
  - project: "Kunminghu V2"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

# CPU 行为验证 preflight 与后续故事

## 前置条件和记录约定

| 类别 | 已核实值 / 要求 |
|---|---|
| Kunminghu snapshot | `sources.lock` 中 SHA `c098f996bf4d301b88693b20315486d31e93bc9d`；Mill 项目版本 `.mill-version=0.12.3`；Java 17.0.20.1。 |
| Heliodor snapshot | `sources.lock` 中 SHA `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；Veryl 0.22.0 (`967e477`, 2026-10-02)。 |
| Kunminghu 仿真器工具 | Verilator 5.020 (2024-01-01) 缺少源码引用的 `VerilatedTraceBaseC`；使用上游 Verilator v5.050 tag（commit `0a24d49771fa57c36ff667272bf7b5c6705e4df0`）后 simulator 编译和 CoreMark smoke 通过。Simulator C++ 使用 GCC/G++ 13.3.0；Verilator 自身在 Ubuntu 22.04 容器内用 GCC/G++ 11.4.0 构建。 |
| Heliodor 共享测试台 | 原仓库多个未实例化测试台也会在 Veryl check 阶段触发 `$readmemh`/`dram` `invalid_initial_assign`。当前受控方法把源码复制到临时目录，排除未实例化 debug harness，并只在临时副本中给普通 DRAM 初始化加 `allow(initial_assign)`；锁定 checkout 保持只读。 |
| 统一每次运行元数据 | 必须记录：快照 revision、输入/fixture SHA-256、配置与 hart 数、精确命令及 cwd、Mill/Veryl/Verilator/compiler 版本、退出码、CPU 是否启动、完整 stdout/stderr 路径及其 SHA-256、生成产物路径。源码快照、机器码输入、构建/运行日志分开归档；任何启动前错误标 `blocked`，只有 CPU 运行且断言不符才标 `run-fail`。 |

推荐的本项目运行记录模板：

```yaml
snapshot_sha: "<40-hex>"
input_sha256: "<64-hex>"
configuration: "<config / privilege / control registers>"
command: "<exact command>"
working_directory: "<repo-relative or isolated path>"
tools: {mill: "...", veryl: "...", verilator: "...", compiler: "..."}
exit_code: 0
cpu_started: true
result: run-pass | run-fail | blocked
output: "<durable artifact path>"
output_sha256: "<64-hex>"
artifacts: ["<generated hex/elf/RTL/simulator>" ]
```

## Kunminghu：本机 preflight 实测

| 步骤 | 命令/输入 | 输出与结论 |
|---|---|---|
| 获取 Mill | XiangShan `.mill-version=0.12.3`；临时 `/tmp/mill-dist-0.12.3-assembly.jar`，通过 `java -cp ... mill.runner.MillMain` 封装；`mill --version` 为 0.12.3。 | 上游 Maven Central 的 `.12.3-mill.sh` URL 返回 404；assembly JAR launcher 可工作。临时 wrapper 未进入 checkout。 |
| 初始化依赖 | 在 `sources/xiangshan` 执行 `git submodule update --init`，并按直接 gitlink 初始化被 build 引用的 `rocket-chip` 和 `openLLC` 子模块。 | 完成后 XiangShan 直接 gitlink 与锁定 SHA 一致；checkout 无源码差异。没有递归初始化所有无关下游子模块。 |
| 第一轮 build | `MILL_WORKSPACE_ROOT="$PWD" PATH=/tmp:$PATH make emu CONFIG=KunminghuV2Config NUM_CORES=1` | 编译/chisel elaboration 因 `NOOP_HOME` 未进入 Java 子进程失败；不是 DUT 运行。 |
| RTL 生成和 simulator build | `NOOP_HOME="$PWD" MILL_WORKSPACE_ROOT="$PWD" PATH=/tmp:$PATH make emu CONFIG=KunminghuV2Config NUM_CORES=1` | 生成 `build/rtl/SimTop.fir`（约 1.4 GiB）和约 2,001 个 `.sv` 文件；之后 GCC 拒绝 `-fno-slp-vectorize`，退出 2。 |
| GCC 等效开关重试 | `NOOP_HOME="$PWD" MILL_WORKSPACE_ROOT="$PWD" PATH=/tmp:$PATH make emu CONFIG=KunminghuV2Config NUM_CORES=1 OPT_FAST='-O3 -fno-tree-slp-vectorize'` | GCC 编译推进后失败于 `VerilatedTraceBaseC` 未声明，退出 2。该类型不在本机 Verilator 5.020 头文件中；需要兼容的更新版 Verilator。模拟器未生成、CPU 未启动。 |

硬件 elaboration 成功日志保存在 [Kunminghu runMain 日志](evidence/kunminghu-runmain-2026-10-14.log)。可复核失败摘要保存在 [Kunminghu preflight 摘要](evidence/kunminghu-preflight-2026-10-14.txt)。本次输入源为锁定的 Kunminghu checkout；生成文件均在 `sources/xiangshan/build/` 忽略路径内，没有修改上游工作树。该结果关闭了“Mill 不存在”这个单点问题，但没有关闭 Verilator/C++ simulator preflight，也没有运行任何指令案例。

## Heliodor：harness 阻塞和 Ssstateen 失败定位

| 项目 | 实测与证据 |
|---|---|
| 测试台阻塞 | 原始共享 arch test harness 在 Veryl 0.22.0 check 阶段被 `test_arch_common.veryl` 的 DRAM `$readmemh` `invalid_initial_assign` 阻断，CPU 未启动。Story 5.6 的 `run_isolated.py` 生成临时副本，删除仅供 debug 的未实例化测试台片段并局部 allow DRAM 初始化后可执行。这个 workaround 是受限测试台兼容层，不宣称已验证其对五专题所有内存/地址语义通用。 |
| Fixture 来源 | revision `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；fixture `experiments/ssstateen/ssstateen_probe.hex`；SHA-256 `65391f26edfcd03fe56182e53b393e99b8a2500c49e8599f97fbaed49104c789`。 |
| 运行命令 | `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_ssstateen`；隔离目录 `/tmp/heliodor-ssstateen-isolated-4x06fqcp`；Veryl 0.22.0。 |
| 结果 | 退出 1、`0 passed, 1 failed`；tohost `0x02`，仅记录 HS ecall cause 9 / operation ID 21；20 个预期 gate traps 未出现；stateen 写全 1 后读回仍为 0。完整输出 SHA-256 `bdc6e32a9e694e95827d5da1dfe51f6104b0ccb7aad03721b9c4fe3884278d5c`；见 [Ssstateen 运行日志](evidence/heliodor-ssstateen-run-2026-10-14.log)。 |
| 根因定位 | 在固定快照 [CSR read case](../../sources/heliodor/src/core/csr.veryl#L494) 与 [CSR write case](../../sources/heliodor/src/core/csr.veryl#L1047) 中没有 `sstateen0–3`/`hstateen0–3` 映射；未匹配读路径 default 为 `64'd0`，写路径 default 不保存状态。[`csr_illegal` 权限逻辑](../../sources/heliodor/src/core/alu_wrap.veryl#L446) 只检查只读写入、CSR 最低特权级和 RV64 奇数 PMPCFG 未实现项，没有 stateen/ENVCFG gate。故 M-mode 对未实现地址读零/写忽略、HS 操作未被 stateen 规则拦截，与观测一致。结论是此 SHA 的可复现功能缺口，不归咎于 testbench；没有修改锁定源码。 |

## 可直接进入 sprint 的后续故事

这些故事组成 proposed **Epic 6：验证 RVA23S64 五专题的 CPU 行为**，全部明确以实际观察而非上游支持声明为验收证据。Epic 6 保持 `backlog`，所有故事有依赖次序；在 preflight 未通过前不得把目标 CPU 结果记作失败或通过。

1. **6.1 固定两边 CPU 验证工具链和结果归档格式。** 验收：为 Kunminghu 固定可复现的 Mill/Java/Verilator/C++ compiler 组合，解释 Mill launcher 与 `MILL_WORKSPACE_ROOT`/`NOOP_HOME` 环境要求；为 Heliodor 固定 Veryl/toolchain 版本；在临时/ignored 输出目录各跑一个 smoke target；提交环境 manifest、命令模板和元数据记录样例。每个失败均有工具版本、输入哈希、完整日志和“CPU 是否启动”字段。
2. **6.2 建立 Kunminghu 单元测试加载和结果采集适配器。** 验收：固定 gitlinks 不漂移；生成 simulator 并从受控 fixture 加载代码；可以读取 pass/fail/tohost 或等价 marker；一个 no-op/已知短测试完成加载、至少执行一条指令并退出。缺少 NEMU/ready-to-run 依赖时明确记录最低 fixture bundle，不假定通用 `make emu` 自动支持故事测试。
3. **6.3 建立可复用 Heliodor 普通 arch harness 兼容 runner。** 验收：从锁定副本重建临时目录；只排除未实例化 debug harness 并限定 Veryl 0.22.0 所需 lint allow；能对一个普通 arch target 完成 compile/check/run；核对上游 checkout 无 diff，manifest 对源文件和 fixture 做 SHA-256，并逐专题复查这个 workaround 的适用性。
4. **6.4 验证 Zifencei。** 验收：两边各加载自修改代码 fixture；验证旧指令/新指令与 `FENCE.I` 前后观测；覆盖 `funct12/rs1/rd` ignored/reserved 编码；记录缓存/代理隔离、hart 数、fixture 哈希、预期及观察值。多 hart 可作为清晰拆分的后续案例。
5. **6.5 验证 Sstc。** 验收：分别覆盖 `stimecmp <, ==, > time`、STCE/TM gates、pending/陷阱；VS `vstimecmp`、非零 `htimedelta`、两级 STCE、delegation/delivery/VSTIP；无实现路径或不可注入中断时记录阻塞，不以静态读取代替运行。
6. **6.6 验证 Sscofpmf。** 验收：由实现支持的硬件事件驱动 HPM overflow，检查 `mhpmevent.OF`、`scountovf`、cause 13、IE/pending、clear/re-arm 和 MINH/SINH/UINH/VSINH/VUINH 过滤/权限组合；Sail/ACT4 分别记录版本与工具支持，不将软件写计数器误作硬件事件验证。
7. **6.7 验证 Ssnpm。** 验收：测试 PMLEN 0/7、enabled/disabled、canonical/tag address boundaries；分列 S/U 与 VS/VU；对 load/store、atomic、FP、compressed、CMO、vector、hypervisor 显式访问族逐一给出运行结果或具体阻塞。
8. **6.8 验证 Ssstateen。** 验收：两边核对 M/H/S/VS/VU 访问门、八个 CSR 的定义位 reset/readback/WARL 与 ENVCFG gate；复现现有 Heliodor M/HS fail 并保持结果日志；对 Kunminghu 执行相同受控矩阵；若本地快照缺实现，结果标为实际 `run-fail` 并链接到精确源路径，不擅自改写固定快照。

## Story 6.1 固定工具链与 smoke 归档（2026-10-14）

固定组合、源 checkout 和 Kunminghu 所有 11 个直接 gitlink SHA、安装/重建来源、工具哈希与运行记录见 [工具链 manifest](evidence/cpu-validation-toolchain-v1.yaml)。记录校验器为 [`scripts/run_cpu_smoke.py`](../../scripts/run_cpu_smoke.py)，回归用例为 [`test_run_cpu_smoke.py`](../../scripts/tests/test_run_cpu_smoke.py)。Manifest 使用 JSON 语法（它也是有效 YAML），因此校验器可在无 PyYAML 的 `uv run --no-cache` 环境读取；其中明确标注旧日志是合并的 stdout/stderr transcript，避免声称恢复出原始分流日志。校验器还要求两份锁定 checkout 齐全、运行 revision 与所属快照一致、run ID 唯一，并从输出日志核对成功 marker 与持久生成物 SHA-256。

复现/校验命令：

```sh
uv run --no-cache pytest -q scripts/tests/test_run_cpu_smoke.py
uv run --no-cache python scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml
python3 scripts/check_doc_links.py
```

Kunminghu 固定为 `KunminghuV2Config`、单 hart；Mill 0.12.3 / OpenJDK 17.0.20.1、Verilator 5.050、GCC/G++ 13.3.0。上游 Verilator 5.050 在固定 Ubuntu 22.04 image digest 中从 tag 构建，锁定 SHA 与二进制 hash 见 manifest。重新生成的 simulator 通过 C++ 编译；随后 CoreMark 2-iteration 在 NEMU difftest 下完成，第一条指令已提交并命中 `HIT GOOD TRAP`，`instrCnt=663,692`。完整分流日志：[stdout](evidence/smoke/kunminghu-coremark-2026-10-14.stdout.log)、[stderr](evidence/smoke/kunminghu-coremark-2026-10-14.stderr.log)。历史 Verilator 5.020 阻塞和缺环境变量/GCC flag 的失败仍保留在 manifest 与摘要中。

Heliodor 固定为 Veryl 0.22.0（`967e477`）、Verilator 5.020 和 G++ 13.3.0。Story 6.3 runner [`experiments/heliodor-smoke/run.py`](../../experiments/heliodor-smoke/run.py) 从锁定 revision 创建临时副本，保留普通 1 MiB arch harness 并仅选取 `test_arch_rv64ui_add`；隔离变换排除未实例化 64K debug harness 和其他 arch tests，并分别对 test_smoke 的 imem 与普通 harness 的 DRAM 声明加局部 `allow(initial_assign)`。最终验收运行 `heliodor-core-20261014T054447Z-2477026` 为 `run-pass`：base smoke 观察 x10=7、x11=11、x12=77、x13=11 和 `[test_smoke] PASS`；普通 arch target 观察 `tohost=1/pass=1` 和 `v4 rv64ui-add PASS`，退出码 0。工具版本与 Veryl 二进制 SHA、两份 fixture 摘要、源码/变换后 harness、归档 runner、日志及产物 SHA-256 均记录在 manifest 和 [归档目录](evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261014T054447Z-2477026/)；分流日志见 [stdout](evidence/smoke/heliodor-core-20261014T054447Z-2477026.stdout.log) 和 [stderr](evidence/smoke/heliodor-core-20261014T054447Z-2477026.stderr.log)。此前 `test_arch_ssstateen` 在隔离机制下执行 CPU 但观察到不符合预期的 marker，仍归类 `run-fail`；普通 arch add 不覆盖该专题结果。上述运行均不构成 RVA23 符合性结论。

Story 6.1 两侧 CPU-start/marker 验收已通过；Kunminghu 的可重建 Verilator 5.050 环境与 Heliodor 的隔离 Veryl runner 可供后续故事复用。Story 6.3 的普通 arch harness 入口和基础 smoke 均在锁定工具链下实际运行。专题级 Ssstateen 的 `run-fail` 是独立的硬件行为发现，必须由 Story 6.8 处理，不改变基础 arch harness 入口结论。

## Story 6.2 Kunminghu fixture 加载与模拟器入口（2026-10-14）

`experiments/kunminghu-smoke/` 提供 RV64I 算术自检 fixture、链接脚本和复现说明；`run.py` 复用 Story 6.1 锁定的单 hart emulator/NEMU，不会构建或写入 `sources/`。fixture 的 `_start` 位于 `0x80000000`，并以 `7 + 11 == 18` 决定 NEMU custom trap 的 `a0` 成功/失败值。runner 要求仿真器报告预期 raw image 路径、首条提交、提交轨迹中的链接入口 PC、与 map 中 `good_trap` 地址一致的 good-trap PC、无 BADTRAP/ABORT/critical-error、退出码为零；未达到这些条件不分类为 `run-pass`。它在执行后再次验证锁定源码、gitlink 和既有 manifest，并以加锁的原子替换方式写入并发运行记录。

复现命令：

```sh
python3 experiments/kunminghu-smoke/run.py --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml
```

运行 `kunminghu-fixture-20261014T043211Z` 在 `KunminghuV2Config`、`NUM_CORES=1` 下通过；仿真器 flash reset stub 的提交轨迹从 `0x10000000` 跳转到 fixture `_start=0x80000000`，`good_trap` 映射和观察 PC 均为 `0x80000010`。完整 stdout/stderr、合并校验 transcript、ELF、map、raw image、命令、工具版本和 SHA-256 保存在 [运行证据目录](evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261014T043211Z/)。对应的机器可校验记录追加在工具链 manifest 的 Kunminghu `runs` 列表中。回归测试为 [`test_kunminghu_smoke.py`](../../scripts/tests/test_kunminghu_smoke.py)。本 smoke 只证明该 fixture 在固定快照和单 hart 配置下正确加载、提交并退出，不构成任何 RVA23 专题或 profile 符合性结论。

之后保留的 `kunminghu-fixture-20261014T043935Z`、`kunminghu-fixture-20261014T044428Z`、`kunminghu-fixture-20261014T044458Z`、`kunminghu-fixture-20261014T044927Z` 和 `kunminghu-fixture-20261014T045142Z` 是实现审查后的复跑。第十轮审查补充了 linker script 的运行前后 SHA-256 校验和加锁追加前复核、模拟器文件在 hash 期间消失时的结构化失败记录，以及错误 image-path 的 runner 级测试。最终复跑 `kunminghu-fixture-20261014T051436Z-3e81181d1d02` 同样从 `0x80000000` 提交，在 `0x80000010` 命中 good trap，退出码为零；源码 SHA-256 为 `55de02149639dc04d311b153d30ee8082f480d608472488863f9e36b85fcd2ed`，链接脚本 SHA-256 为 `1a09d98e3c1ba4c22c1ecd2c16e5f4d8cad65fc6944efe0a0ccd8b3149d4a412`。manifest 还保存模拟器/NEMU 二进制摘要、资源快照和日志/工件摘要。此前各轮六条成功记录仍保留，最终回归真实运行了正确与错误算术 fixture，分别命中 good trap 和 bad trap。

## 范围决定

Epic 5 的学习交付继续保持其原验收边界；本记录和 Epic 6 不表示两个实现符合 RVA23。Epic 6 是新增的动态验证 backlog，而不是把五专题未运行/失败案例追认为 Epic 5 的通过项。所有故事在各自实现前都要维持 fixed SHA 和可复查元数据。
