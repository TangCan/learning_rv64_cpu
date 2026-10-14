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
| Kunminghu 仿真器工具 | 本机 Verilator 5.020 (2024-01-01) 与 GCC 13.3.0。5.020 缺少源码引用的 `VerilatedTraceBaseC`；必须选用与这份 XiangShan 快照及其 C++ harness 匹配的 Verilator 版本。上游 CI 配置提及 5.048/5.050+，但本次尚未用这些版本复验兼容性。 |
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

## 范围决定

Epic 5 的学习交付继续保持其原验收边界；本记录和 Epic 6 不表示两个实现符合 RVA23。Epic 6 是新增的动态验证 backlog，而不是把五专题未运行/失败案例追认为 Epic 5 的通过项。所有故事在各自实现前都要维持 fixed SHA 和可复查元数据。
