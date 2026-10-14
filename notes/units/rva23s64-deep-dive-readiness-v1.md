# RVA23S64 深度专题：活动路径与验证就绪度

## 范围与边界

本记录是 Epic 5 Stories 5.2–5.6 的准备矩阵，追踪 RVA23S64 v1.0 §3.1.2.2 的 `Zifencei`、`Sstc`、`Sscofpmf`、`Ssnpm`、`Ssstateen` 五项。它只登记活动路径、静态检查范围、候选验证入口和本机前置条件；源码/测试存在不等于已运行，更不代表符合 RVA23。未解决项必须由后续专题故事调查。

要求键：`RVA23S64/v1.0/§3.1.2.2/<extension>`，与 [RVA23 覆盖目录](../rva23-coverage.md)一致。规范基线为 [RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)；对应扩展规范：[Zifencei v2.0](https://docs.riscv.org/reference/isa/v20240411/unpriv/zifencei.html)、[Sstc v1.0 §§12.1–12.3](https://docs.riscv.org/reference/isa/v20250508/priv/sstc.html)、[Sscofpmf v1.0 §§13.1.1–13.1.2](https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html)、[Pointer Masking v1.0.0 §§17.1.2.2–.8](https://docs.riscv.org/reference/isa/v20260120/priv/zpm.html#pointer-masking-extensions-version-1-0-0)、[Smstateen/Ssstateen v1.0](https://docs.riscv.org/reference/isa/v20260120/priv/smstateen.html)。S 特权架构基于 Privileged Architecture 1.13（RVA23 的 `Ss1p13`）。

## 固定快照与活动目标

| 项目 | snapshot ID | sources.lock SHA | 实测 HEAD | 目标/活动选择 |
|---|---|---|---|---|
| Kunminghu V2 | `xiangshan-kunminghu-v2-20261012` | `c098f996bf4d301b88693b20315486d31e93bc9d` | `c098f996bf4d301b88693b20315486d31e93bc9d` | 上游 CI `emu.yml` 的 `--config KunminghuV2Config`，且构造 `new KunminghuV2Config(1)`；调查以此单核配置为准，不以 `DefaultConfig` 代替。其 `CsrCfg` 实例经 `wrapper/CSR.scala` 组合 `NewCSR`；旧 `backend/fu/CSR.scala` 中的同名/替代实现不自动视为本目标的活动路径。 |
| Heliodor | `heliodor-master-20261012` | `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | 固定 `heliodor_core` 的 CSR、decode、地址变换和 `tb/test_arch_common.veryl`；Veryl 测试台是行为入口。 |

两侧 SHA 与 `sources.lock` 相符，本矩阵未发生快照阻塞。若后续开始专题调查时 HEAD 不同，先记录新 SHA 并阻止沿用本表得出源码结论。

## 双侧专题矩阵

| 要求键 / 规范行为 | Kunminghu V2 活动路径与测试就绪度 | Heliodor 活动路径与测试就绪度 |
|---|---|---|
| `.../Zifencei`：`FENCE.I` 同步此前对指令内存的写入与同一 hart 后续取指；RVA23 S64 指定为支持指令缓存一致性的标准机制。 | **静态证据**：`DecodeUnit.scala` 将 `FENCE_I` 派发到 `FenceOpType.fencei`；`Fence.scala` 提供 fence 请求；CI 选定 Kunminghu V2。**定向测试**：下述有界测试源码搜索未定位到 Kunminghu `FENCE.I` 专题用例。**待追踪边界**：从 `Fence.scala` 的 fence 请求继续追到前端/ICache 的失效或同步完成条件，并核对提交/等待后恢复取指的路径；Story 5.2 记录该路径与限制。**状态**：needs setup（专题验证入口未定位）。 | **静态证据**：`decode.veryl` 识别 `is_fence_i`；`test_arch_common.veryl` 中的 `test_arch_sysb` 仅登记为通用系统指令入口，不作为已确认的 Zifencei 候选测试，也不声称覆盖同步语义。**验证门槛**：检查该入口是否包含先写入新指令、执行 `FENCE.I`、再取指并观察新指令行为的用例；若没有，应新增可观察的自修改代码/取指同步案例。**状态**：needs setup。 |
| `.../Sstc`：Supervisor timer compare 与 S/VS timer interrupt；Profile 版本 1.0。 | **静态证据**：活动 `NewCSR` 包含 `stimecmp`、`vstimecmp`、`menvcfg.STCE`/`henvcfg.STCE`，`SstcInterruptGen` 接收比较值、写使能和 enable；`CSRPermitModule` 有访问权限门控。源码线索待专题追踪到 timer/interrupt 输入输出；后续范围限定为 `NewCSR.scala` 的 timer/time 输入和 `platformIRP` 输出、`SstcInterruptGen.scala` 的比较器更新、`MachineLevel.scala` 的 STIP/VSTIP pending 接入，以及 CLINT/`htimedelta` 来源。**定向测试**：未找到本机 Kunminghu Sstc 专题测试。**状态**：needs setup。 | **静态证据/测试源码**：`csr.veryl` 中 `stimecmp`、`vstimecmp`、`STCE` 及 STIP/VSTIP 比较逻辑；`test/sstc/sstc_test.S` 与 `test/hsstc/hsstc_test.S`；testbench 对应 `test_arch_sstc_stimecmp`、`test_arch_hsstc`。**候选命令**：`cd sources/heliodor && veryl test --test test_arch_sstc_stimecmp`；VS 案例为 `veryl test --test test_arch_hsstc`。**状态**：needs setup。 |
| `.../Sscofpmf`：`mhpmevent` 溢出状态/中断与按特权模式过滤计数；版本 1.0。 | **静态证据**：活动 `NewCSR` 中 `MachineLevel.scala` 有 `mhpmevent` 的 `OF/MINH/SINH/UINH/VSINH/VUINH` 字段、计数溢出生成；`NewCSR.scala` 接入计数溢出请求和 privilege filter；`SupervisorLevel.scala` 定义 `scountovf`。**定向测试**：限定检索无 Kunminghu 专题测试入口。**状态**：needs setup。 | **静态证据/测试源码**：`csr.veryl` 包含 `mhpmevent`、`scountovf`、LCOFI cause 13 和 M/S/U 过滤；`test/sscofpmf/sscofpmf_test.S` 检查 OF、MINH 和 scountovf；testbench 有 `test_arch_sscofpmf`。现有案例源码覆盖 M-mode MINH 抑制/恢复计数及硬件回绕后 cause 13、OF、`scountovf` 断言；没有覆盖 OF 写零清除/re-arm、其他四个模式过滤、pending 清除后重触发或 S-mode `mideleg` 委托交付。**候选命令**：`cd sources/heliodor && veryl test --test test_arch_sscofpmf`。**状态**：needs setup。 |
| `.../Ssnpm`：RVA23 Profile v1.0 写明 `senvcfg.PME`、若 H 可用则 `henvcfg.PME` 至少支持 PMLEN=0 和 7；指针屏蔽扩展文本/Priv 1.13 使用 `PMM` 字段。 | **静态证据**：活动 `NewCSR` 的 `MEnvCfg`/`HEnvCfg`/`SEnvCfg` 使用字段名 `PMM`，`NewCSR.scala` 将寄存器值送至 TLB PMM 接口；`HUPMM` 另由 `hstatus` 控制。字段名字和接线可见，profile 所写 PME 与实现 PMM 的映射及 PMLEN=0/7 WARL 值尚未逐项核实。**测试**：未找到 Kunminghu 专题测试。**状态**：needs setup（术语映射 unresolved）。 | **静态证据/测试源码**：`csr.veryl` 与 `alu_wrap.veryl` 用 `PMM` 字段选择 mask；`test/supm/supm_test.S` 和 `test_arch_supm` 检查 M-mode 指针屏蔽，未覆盖 S/VS 的 profile 指定 `senvcfg.PME`/`henvcfg.PME` 与 PMLEN 集合。**候选命令**：`cd sources/heliodor && veryl test --test test_arch_supm`（仅 Supm 子集）。**状态**：needs setup（Ssnpm 核心验证仍未完成）。**术语结论**：Profile 的 `PME` 与扩展/RTL 的 `PMM` 尚无本记录可支持的映射结论，保留 unresolved，不静默统一。 |
| `.../Ssstateen`：须提供 `sstateen0–3` 与 `hstateen0–3` CSR；扩展文本版本 1.0。 | **静态证据**：活动 `SupervisorLevel.scala`/`HypervisorLevel.scala` 定义 S/H 两组 CSR；`StateEnBundle.scala` 定义字段；`CSRPermitModule.scala` 有低特权 CSR 访问门控。`wrapper/CSR.scala` 组合 `NewCSR`，所以这不只是未启用替代模块的声明。逐字段可写性、读回和各权限矩阵尚未运行。**测试**：限定检索未找到定向用例。**状态**：needs setup。 | **有界静态负搜索**：限定在 `sources/heliodor/src/core/csr.veryl`、`src/core/decode.veryl`、`tb/test_arch_common.veryl` 和 `test/` 下，以 `stateen`、`sstateen`、`hstateen` 为字面检索词；CSR 地址/读写、指令译码和现有 testbench 范围均无显式命中。未检索生成 RTL、外围或所有间接 CSR alias，且通用 CSR 访问路径仍待人工追踪；无命中不能证明未实现。**候选测试**：无专题用例；通用入口不能验证门控。**状态**：needs setup（实现路径结论 unresolved）；不标记 unsupported/not present。 |

## 候选命令、依赖与当前机器状态

下列命令是复现候选入口的运行方式，不代表曾经运行或通过。Heliodor directed tests 由 `Veryl.toml` 指定 Verilator runner，且 testbench 引用已生成/提交的 hex。本快照已跟踪 `test/sstc/sstc_test.hex`、`test/hsstc/hsstc_test.hex`、`test/sscofpmf/sscofpmf_test.hex`、`test/supm/supm_test.hex`，所列 Veryl 候选入口可直接使用这些输入；只有 hex 缺失或汇编源变化时才需在 `sources/heliodor` 下运行相应 `make -C test/<case>` 重建，再运行 Veryl 测试；构建用 `riscv64-unknown-elf-gcc`、`objcopy` 和 Python `test/c/bin2hex.py`。完整入口可从 `sources/heliodor/README.md` 的 Build & Test 查阅；README 的测试声明不作为本机结果。

| 工具/依赖 | 本机检查结果（本机 executable/version 查询） | 版本要求/影响 |
|---|---|---|
| Verilator | `verilator --version`：5.020，可用 | `Veryl.toml` 选择 Verilator，但文件未钉版本；本地 5.020 是观察值，不是上游要求版本。 |
| 主机 GCC | `gcc --version`：13.3.0，可用 | 本地查询的主机编译器；不是测试 hex 构建所需的 `riscv64-unknown-elf-gcc`。Spec Code Map 中 15.1 与本机观察不符，按本地 executable/version 查询记录为 13.3.0。 |
| `riscv64-unknown-elf-gcc` / `objcopy` | 不可用；本机版本未检查 | 重建 directed-test hex 所需。Heliodor `toolchain/versions.env` 规定 GCC ≥15，当前 pin 为 GCC 16.1.0 / binutils 2.43；若已有 hex，可不经过重建步骤。 |
| Java | `java -version`：17.0.20.1，可用 | Mill 构建需要 JVM；Mill 不可用，版本未检查。上游没有在本故事材料中钉定 Java/Mill 版本。 |
| Mill | 不在 PATH；版本未检查/不可用 | Kunminghu Mill 构建/测试未就绪；项目要求版本未在本故事材料中找到。 |
| Veryl | 不在 PATH；版本未检查/不可用 | Heliodor `veryl test` 未就绪；Veryl 版本未在 `Veryl.toml` 或列出的 README 中钉定。 |
| Ruby | 不在 PATH；版本未检查/不可用 | Toolchain README 指示 system Ruby ≥3.4；测试入口是否需 Ruby 取决于 ACT/setup 路径。 |
| Sail | 不在 PATH；版本未检查/不可用 | `toolchain/versions.env` pin 为 0.12，用于 ACT golden reference；本故事列出的 directed tests 不依赖 Sail。 |
| `uv` | 版本未检查/不可用 | `toolchain/versions.env` pin 为 0.5.18，用于 ACT framework；本故事列出的 directed tests 不依赖 uv。 |
| Rust/Cargo | `cargo` 命令可用；版本未检查 | 本故事候选入口没有 Rust 依赖。 |

Kunminghu 当前只登记源码调查位置，没有命中五专题的定向 test。此前 bounded search 的路径为 `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala`、`backend/fu/Fence.scala`、`backend/fu/NewCSR/`、`sources/xiangshan/src/test/`；文件类型为 Scala、汇编、Verilog/SystemVerilog。搜索词为 `Ssnpm`、`Ssstateen`、`PME`、`PMM`、`stateen`、`sscofpmf`、`sstc`、`FENCE.I`、`fence_i`。搜索只检查这些实现/测试材料，不能证明其余目录无测试。因无已定位测试，不伪造可运行的 Kunminghu 测试命令。Heliodor 的精确 Veryl 命令是已登记测试的候选启动入口，但本机缺 Veryl CLI，故状态为 `needs setup`，本轮没有运行 CPU 测试。

## Ssstateen 有界搜索的直接入口

Heliodor 的有界负搜索记录和未决边界见 [Ssstateen 对照单元](rva23s64-ssstateen-v1.md) 的验证限制；这里的无命中结论仅限该单元列出的 CSR、decode、testbench 和 `test/` 搜索范围，不代表全仓缺失。

## Ssnpm 术语与证据边界

Profile v1.0 专门用 `PME` 写最低 PMLEN 配置要求；指针屏蔽扩展 1.0.0 与 Supervisor/Hypervisor 规范的 CSR 行为使用 `PMM`。当前上游 RTL 存储/传递字段也叫 `PMM`，Heliodor 注释和寄存器名亦如此。这个对应关系可能是 profile 层命名差异，但本故事未通过逐字段规范映射和合法编码检查证明等价，因此专题状态为 `needs setup`，术语关系仍 unresolved。后续必须检查 `senvcfg`、`henvcfg` 对 PMLEN=0/7 的支持、H 对应模式及有效地址屏蔽，再决定是否建立 PME↔PMM 的映射。

## 单元自检

1. 为什么以 Kunminghu V2 作为目标？上游 CI 明确构建/运行单核 `KunminghuV2Config`；活动 CSR 经 `CsrCfg` 和 wrapper 接至 `NewCSR`，不是依据 `DefaultConfig` 或某个孤立源码声明推断。
2. Heliodor 的 Sstc/Sscofpmf/Supm 入口是否已经通过？没有。仅检查到 Veryl testbench 和 directed 源码；Veryl 不在 PATH，源码存在不是运行结果。
3. 五项中哪些仍有阻塞/未决？Kunminghu 测试入口均未定位；两侧都需要专题行为验证。Heliodor Ssstateen 有界搜索无显式命中但不能断言缺失；Ssnpm 的 profile PME 与实现 PMM 映射仍 unresolved。这两项的工作状态均为 `needs setup`。
4. 为什么不从 Heliodor README 的自述推出符合性？README 是上游说明且本轮没有独立运行结果；本矩阵只记录本次锁定快照上检查到的具体路径与测试入口。

## 证据记录

| ID | 类型/状态 | 证据位置和范围 |
|---|---|---|
| E1 | snapshot / inspected | `sources.lock` 与两侧 `git rev-parse HEAD`；SHA 完全相符。 |
| E2 | source / inspected | `sources/xiangshan/src/main/scala/top/Configs.scala`、`.github/workflows/emu.yml`、`backend/fu/FuConfig.scala`、`backend/fu/wrapper/CSR.scala`：目标配置、CI 选择及 CSR 组合关系。 |
| E3 | source / inspected | `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala`、`backend/fu/Fence.scala`、`backend/fu/NewCSR/{NewCSR,MachineLevel,SupervisorLevel,VirtualSupervisorLevel,HypervisorLevel,CSRPermitModule,StateEnBundle,SstcInterruptGen}.scala`：五专题静态活动入口；不等于动态验证。 |
| E4 | source / inspected | `sources/heliodor/src/core/{csr,decode,alu_wrap}.veryl`：CSR、指令译码和有效地址路径；Ssstateen 仅做有界负搜索。 |
| E5 | test-inspected / unverified | `sources/heliodor/tb/test_arch_common.veryl`、`test/{sstc,hsstc,sscofpmf,supm}`：测试入口与案例源码；没有本轮执行输出。 |
| E6 | environment / inspected | 本机命令版本/PATH 检查；Mill、Veryl、Sail、Ruby 缺失，未尝试安装。 |

## 限制与后续输入

- 没有运行任何 Kunminghu 或 Heliodor CPU 测试；矩阵中不存在 `run-pass`。
- Zifencei 的 Heliodor `test_arch_sysb` 只是通用入口，不是已确认的候选覆盖；需检查它是否含有先写入新指令、执行 `FENCE.I`、再取指并观察新指令行为的测试，没有则添加该案例。Kunminghu 两侧都需追踪写入、提交、取指同步路径。
- `Sstc` 需要分开核验 S-mode timer 与 VS timer、权限和中断委托；`Sscofpmf` 需要 overflow latch/clear、计数 filter、scountovf 可见性及 LCOFI 委托；测试源码只提供候选入口。
- `Ssnpm` 需要 profile PME / architecture PMM 精确字段映射及 PMLEN=0/7；现有 Heliodor Supm 案例只触及 M-mode。
- Heliodor `Ssstateen` 负搜索范围有限，不包括对所有通用 CSR alias、外围或生成 RTL 的穷举检查。

## 来源快照

- Kunminghu V2：`xiangshan-kunminghu-v2-20261012`，`c098f996bf4d301b88693b20315486d31e93bc9d`。
- Heliodor：`heliodor-master-20261012`，`94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
