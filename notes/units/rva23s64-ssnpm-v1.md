# RVA23S64 `Ssnpm` 指针屏蔽双核对照（v1）

## 范围与结论

本单元比较 `sources.lock` 固定的 Kunminghu V2 (`xiangshan-kunminghu-v2-20261012`, `c098f996bf4d301b88693b20315486d31e93bc9d`) 与 Heliodor (`heliodor-master-20261012`, `94e9c5821c24a8941c3ddc3b76daddc7124a855a`) 对 RVA23S64 v1.0 §3.1.2.2 `Ssnpm` 的静态路径。两边均有 PMM 配置和标量地址变换线索，故覆盖映射为 `studied-unverified`；没有本轮 S-mode/guest 运行通过证据。此学习记录不是符合性或认证结论。

## 规范定义与 PME/PMM 术语

- RVA23 Profile v1.0 §3.1.2.2 的正式发布 PDF 第 7 页 `Ssnpm` 行逐字写 `senvcfg.PME`、`henvcfg.PME`，最低支持 PMLEN=0/7；同节也将 S64 的 `Sspm`（S-mode 自身支持）列为可选项。本故事追踪强制 `Ssnpm`，不是 `Sspm`。参见 [Profile v1.0 PDF](https://docs.riscv.org/reference/rva23/v1.0/_attachments/rva23-profile.pdf)。
- Pointer Masking Extensions v1.0.0 §17.1.2.4–.8 使用 `PMM` 字段名：RV64 `00`=PMLEN0/disabled、`10`=PMLEN7、`11`=PMLEN16、`01` reserved；实现对未支持设置须遵守 WARL。§17.1.2.7 定义 `Ssnpm` 控制下一级 U，以及 H 存在时 VS/VU。参见 [Pointer Masking v1.0.0](https://docs.riscv.org/reference/isa/v20260120/priv/zpm.html#pointer-masking-extensions-version-1-0-0)。
- 因而本记录保留 Profile 发布 PDF 的 `PME` 与 Privileged/Pointer-Masking 规范和 RTL 的 `PMM`。RVA23 profile 上游归档仓库快照 `e030b70992447784ad9081045d47ce6e278f381e` 在 `src/rva23-profile.adoc:402` 使用 `PMM`，见[固定提交源码](https://github.com/riscv/riscv-profiles/blob/e030b70992447784ad9081045d47ce6e278f381e/src/rva23-profile.adoc#L402)（仓库于 2026-07-24 归档）；结合 Zpm 中该控制的定义，这支持将 PDF 的 PME 视作同一 PMM 控制要求的文本拼写差异，不能把它另解为独立 CSR 字段。按要求仍分别保留各来源原始拼写。
- §17.1.2.2、.6：VA 的高 PMLEN 位以 bit `XLEN-PMLEN-1` 符号扩展，PA（包括 Bare 与 guest-physical address）则以零填充；显式访存适用，instruction fetch 和 page-table walk 等隐式访问不适用。适用显式访问族见下表。`MXR` 在有效特权级生效时会抑制 pointer masking；MPRV/SPVP 会影响有效特权级选择。

## 活动路径与实现证据

### Kunminghu

当前 HEAD 与锁定 SHA 相符。活动 NewCSR 的 `EnvCfg.PMM[33:32]` 默认 `00`，合法枚举为 Disable/PMLEN7/PMLEN16；`Hstatus.HUPMM[49:48]` 亦默认 Disable。`NewCSR.scala` 将 mseccfg、menvcfg、henvcfg、hstatus.HUPMM、senvcfg PMM 注册后传给 TLB。普通访问按有效模式选择：M 用 mseccfg，HS/S 用 menvcfg，VS 用 henvcfg，U/VU 用 senvcfg。规范另规定 HLV/HSV 访问如同 VS 时用 henvcfg；如同 VU 时，在 U 执行用 hstatus.HUPMM，在 HS/M 执行用 senvcfg。`TLB.scala` 的 hyperinst/imode 条件分支与这些控制相对应；fetch/HLVX 和有效 MXR 分支禁用 mask。随后 VA 截取 bit 56:0 / 47:0 并符号扩展，PA 则零扩展。该块还处理屏蔽后的 atomic/misaligned access 检查。静态路径：[`CSRBundles.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRBundles.scala#L62)、[`CSRDefines.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRDefines.scala#L194)、[`NewCSR.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala#L1469)、[`HypervisorLevel.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/HypervisorLevel.scala#L243)、[`TLB.scala`](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala#L178)。访存入口在 `LoadUnit.scala`、`StoreUnit.scala`、`AtomicsUnit.scala`；`rg -ni 'PMM|Ssnpm|pointer.mask' sources/xiangshan/src/test` 未定位专题测试。证据 E1/E2。

### Heliodor

当前 HEAD 与锁定 SHA 相符。`csr.veryl:794-797` 将 mseccfg、menvcfg、senvcfg 的 `[33:32]` 分别输出为 M/S/U PMM；`henvcfg` 是单独存储的可读写 H CSR（声明 `:391`，读 `:546`、写 `:1130`），复位为零（`:876`）。CSR 可访问不表示字段已接入地址生成选择器。`heliodor_core.veryl:554-565` 按数据访问有效 privilege 从 M/S/U 三路选 PMM；主 load/AMO AGU 在 `:5283-5290` 变换地址，第二 load AGU 在 `:5313-5319` 重复同一变换。`alu_wrap.veryl:191-203` 对标量 AGU 也有 PMLEN 转换。按 `csr_pmm`、PMM 选择器和 HUPMM 相关符号检索所检查源码，未定位 `henvcfg.PMM` / `hstatus.HUPMM` 到 VS/VU mask selector 的路径；CSR 可读写性不构成该路径的证据。规范要求普通 VS 用 henvcfg、VU 用 senvcfg；HLV/HSV-as-VS 用 henvcfg；HLV/HSV-as-VU 在 U 执行时用 hstatus.HUPMM、在 HS/M 执行时用 senvcfg。该为所检查路径的缺口，不据此断言整个 Heliodor 完全不支持 H guest pointer masking。证据 E3/E4。

## 访问族矩阵

状态限定为本轮锁定源码/测试检查，不表示该族已运行通过。`static path` 表示追踪到共用 mask 后地址路径；`not located` 表示在上述有界路径未定位到相应变换，不能单独作为不支持结论。

| 显式访存族（Zpm v1.0.0 §17.1.2.6） | Kunminghu | Heliodor | 边界 |
|---|---|---|---|
| Integer load/store | `inspected only`：TLB 从标量 Load/Store 请求使用 mask 地址；未运行 | `inspected only`：两 AGU 至 load/store MMU 地址有 mask；未运行 | 仅源码路径，不含运行观察 |
| Atomic（含 LR/SC） | `inspected only`：TLB 将 atomic 纳入同一 effective-address 变换及后续检查；专题测试未定位 | `inspected only`：AGU 地址复用到 AMO/LR/SC 路径；已有 Supm 源码为 M-mode，不是 Ssnpm 证据 | 不外推到全 A 操作、权限或异常行为 |
| Floating-point load/store | `inspected only`：按显式访存共用 Load/Store/TLB 接口追踪；未运行 | `inspected only`：静态路径归入通用 load/store AGU/MMU；未运行 | 未定位独立 FP Ssnpm 用例 |
| Compressed load/store | `inspected only`：解码后访存经通用 Load/Store/TLB 路径；未运行 | `inspected only`：解码后访存进入通用 scalar AGU；未运行 | 未逐条检查压缩编码 |
| Cache management operations | `unverified`：本轮未检查 Zicbom/Zicbop/Zicboz 请求是否进入同一 TLB PMM 路径 | `unverified`：未定位这些 CMO 的 PMM 变换 | 不宣称覆盖；规范要求显式 CMO 受 mask |
| Vector load/store | `unverified`：本轮未追踪向量 LSU 的完整地址入口 | `unverified`：VectorUnit 有独立 element-address 生成；未在该路径定位 PMM | 不从标量 AGU 推断向量行为 |
| Hypervisor HLV/HSV and VS/VU | `inspected only`：普通 VS 用 henvcfg、VU 用 senvcfg；HLV/HSV-as-VS 用 henvcfg；HLV/HSV-as-VU 依调用模式用 HUPMM 或 senvcfg；未动态验证 | `unverified`：已检查路径未发现 henvcfg/HUPMM selector | Heliodor guest/H 路径仍未决；HLVX 免于 masking；不以 M-mode 案例替代 |
| Zicfiss shadow-stack explicit accesses | `unverified`：本轮未追踪 `SSPUSH`/`SSPOPCHK` 等地址是否接入 PMM TLB 路径 | `unverified`：本轮未检查 Zicfiss 支持配置与对应地址入口 | Profile 不强制 Zicfiss；仅在目标实现该扩展时适用 |
| `FENCE` / `FENCE.I` unused address fields | `not-applicable`：规范仅在这些字段未来启用时适用 | `not-applicable`：规范仅在这些字段未来启用时适用 | 当前编码不产生显式内存访问 |
| Instruction fetch and implicit accesses | `not-applicable`：Zpm 明确排除取指与页表遍历 | `not-applicable`：Zpm 明确排除取指与页表遍历 | HLVX 也明确免于 pointer masking |

## Heliodor 案例与验证记录

本轮尝试执行现有 `test/supm/supm_test.S`、对应 `.hex` 及 `tb/test_arch_common.veryl` 的 `test_arch_supm`，没有执行成功。测试程序集覆盖 Bare M-mode `mseccfg.PMM=11` 的 tagged LD、LR/SC alias，`PMM=10` 的 tagged LR/SC alias，以及 `PMM=0` clean LR/SC；其注释指出 flat DRAM 与 Sv39 MMU 会让 tagged LD/SD alias 在禁用时也可能可观察为同一位置，故 LR/SC 才是 discriminator。它没有写 `senvcfg` / `henvcfg`，不覆盖 S/U/VS/VU profile Ssnpm 要求。

- 命令 `cd sources/heliodor && make -C test/supm`：exit 0，输出 `Nothing to be done for 'all'`；现有 `test/supm/supm_test.hex` 已存在，本次未重建输入。
- 命令 `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl --version`：Veryl `0.22.0 (967e477 2026-10-02)`。
- 命令 `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_supm`：exit 1，testbench check 阶段报 `invalid_initial_assign`，定位 `tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)`；仿真没有启动。还有 missing_port warnings，但本次确切阻塞为 `dram` 初始化错误。没有把该结果记为 pointer-masking 运行失败。
- 未新增 guest/S-mode 汇编试验：现有共享 testbench 已在 elaboration/check 阶段阻止 CPU test 启动；改 testbench 会越出本故事的上游只读边界，且尚无已验证的 S/guest 控制驱动方案。故 S-mode PMLEN0/7 tagged access 与 guest `henvcfg` 案例明确为未运行。

## 证据表

| ID | 类型 | 状态 | 固定来源/位置 | 支持的结论与限制 |
|---|---|---|---|---|
| E1 | spec | inspected | RVA23 Profile v1.0 §3.1.2.2 (`Ssnpm`)，发布 PDF p.7；归档 profile 源提交 `e030b70992447784ad9081045d47ce6e278f381e`, `src/rva23-profile.adoc:402` | 发布件 `PME`、固定源文本 `PMM` 的拼写差异及 PMLEN0/7 最低要求；PMM 架构定义另见 E2 |
| E2 | spec | inspected | Pointer Masking v1.0.0 §§17.1.2.2–.8；H v1.0 §14.1.2.1 | `PMM` 编码、地址变换、模式、访问族及 HLV/HSV-as-VS/VU 控制规则 |
| E3 | source | inspected | Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；`backend/fu/wrapper/CSR.scala`、`backend/fu/NewCSR/CSRBundles.scala:67-74`、`backend/fu/NewCSR/CSRDefines.scala:194-200`、`backend/fu/NewCSR/NewCSR.scala:1469-1473`、`backend/fu/NewCSR/HypervisorLevel.scala:243`、`cache/mmu/TLB.scala:178-214` | PMM 定义、传递、模式选择和地址变换静态路径；无 Ssnpm run |
| E4 | source | inspected | Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；`src/core/csr.veryl:129-134,391,546,794-797,876,1130`；`src/core/heliodor_core.veryl:452-454,554-565,5283-5290,5313-5319`；`src/core/alu_wrap.veryl:191-203` | M/S/U PMM、henvcfg CSR 可读写性、两个 load AGU 及 scalar AGU 变换；在所检索路径未定位 guest PMM selector |
| E5 | test-inspected | inspected | Heliodor `test/supm/supm_test.S`, `test/supm/supm_test.hex`, `tb/test_arch_common.veryl:6055-6080` | 仅检查 M-mode Supm 测试材料；不是 Ssnpm 验证 |
| E6 | test-run | run-fail | Heliodor `make -C test/supm`; Veryl 0.22.0 `test --test test_arch_supm`; `tb/test_arch_common.veryl:440` | build 目标无需更新；testbench check 因 `$readmemh`/`dram` 初始化错误退出1，仿真未启动 |

## 自检

1. **禁用与 PMLEN7 有何差别？** `00` 不变换地址；`10` 保留低 57 位，VA 用 bit56 扩展符号，PA 将高 7 位清零。规范示例 VA `0xABFFFFFF12345678` 经 PMLEN7 变为 `0xFFFFFFFF12345678`；同位串作为 PA 时变为 `0x01FFFFFF12345678`。地址变换不替代权限检查。
2. **哪些位是边界？** RV64 PMLEN7 的边界源位 bit56、PMLEN16 的 bit47。每种当前定义 PMLEN 对应固定边界，不依 translation mode 动态变化；超出受支持虚拟/物理地址区域的合法性仍由既有地址翻译/权限机制判断。
3. **已检查与未验证是什么？** 静态映射覆盖标量整数及共用 scalar atomic/FP/compressed 路径（各有范围限定）；Heliodor 原有测试仅 M-mode Supm 且仿真被 testbench 阻断。CMO、vector 及 Heliodor VS/VU/H guest 仍未验证；Kunminghu S/U/H selector 有源码证据但没有运行观察。不得从单次 load 或 M-mode U64 测试推出其他格子的通过。

## 未决项

Kunminghu `EnvCfg.PMM` 与 Heliodor PMM 仅有静态字段/路径证据；Profile PDF 的 `PME` 与源码/架构规范 `PMM` 是文档拼写差异。S-mode control/WARL 写入读回、S/U/VS/VU 上 PMLEN0/7 tagged access、MXR/MPRV/SPVP、地址边界异常和跨页行为均未运行。Heliodor 的 H guest pointer masking 路径、两边 vector/CMO 路径仍待进一步检查。现有 testbench blocker 需在单独的 harness/toolchain 修复工作中解决。
