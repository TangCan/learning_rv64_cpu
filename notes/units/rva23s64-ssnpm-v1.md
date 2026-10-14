# RVA23S64 `Ssnpm` 指针屏蔽双核对照（v1）

## 范围与结论

本单元比较 `sources.lock` 固定的 Kunminghu V2 (`xiangshan-kunminghu-v2-20261012`, `c098f996bf4d301b88693b20315486d31e93bc9d`) 与 Heliodor (`heliodor-master-20261012`, `94e9c5821c24a8941c3ddc3b76daddc7124a855a`) 对 RVA23S64 v1.0 §3.1.2.2 `Ssnpm` 的地址路径。Kunminghu 四格 PMLEN/tagged U-mode 运行中，PMLEN0 canonical/tagged 和 PMLEN7 canonical 通过；PMLEN7 tagged 的普通 load/store 断言通过，但 LR.D 在该 tagged 地址触发 load access fault，NEMU difftest 随后因模式状态不一致中止。Heliodor 的 PMLEN0 canonical、PMLEN7 canonical/tagged 与 bit56-set case 到达 pass marker；PMLEN0 tagged 修正版因 high-address load 被 low-bit DRAM alias 满足而 run-fail。旧 E15 来自未拒绝 unexpected success 的早期 fixture，由 E21 取代。Kunminghu 与 Heliodor 的轻量内存模型按低地址位索引，故 tagged high-address 成功结果不能证明 raw 与 masked effective address 的差异。其余访问族/模式仍分开列为静态、未验证或运行失败。本学习记录不是符合性或认证结论。

## 规范定义与 PME/PMM 术语

- RVA23 Profile v1.0 §3.1.2.2 的正式发布 PDF 第 7 页 `Ssnpm` 行逐字写 `senvcfg.PME`、`henvcfg.PME`，最低支持 PMLEN=0/7；同节也将 S64 的 `Sspm`（S-mode 自身支持）列为可选项。本故事追踪强制 `Ssnpm`，不是 `Sspm`。参见 [Profile v1.0 PDF](https://docs.riscv.org/reference/rva23/v1.0/_attachments/rva23-profile.pdf)。
- Pointer Masking Extensions v1.0.0 §17.1.2.4–.8 使用 `PMM` 字段名：RV64 `00`=PMLEN0/disabled、`10`=PMLEN7、`11`=PMLEN16、`01` reserved；实现对未支持设置须遵守 WARL。§17.1.2.7 定义 `Ssnpm` 控制下一级 U，以及 H 存在时 VS/VU。参见 [Pointer Masking v1.0.0](https://docs.riscv.org/reference/isa/v20260120/priv/zpm.html#pointer-masking-extensions-version-1-0-0)。
- 因而本记录保留 Profile 发布 PDF 的 `PME` 与 Privileged/Pointer-Masking 规范和 RTL 的 `PMM`。RVA23 profile 上游归档仓库快照 `e030b70992447784ad9081045d47ce6e278f381e` 在 `src/rva23-profile.adoc:402` 使用 `PMM`，见[固定提交源码](https://github.com/riscv/riscv-profiles/blob/e030b70992447784ad9081045d47ce6e278f381e/src/rva23-profile.adoc#L402)（仓库于 2026-07-24 归档）；结合 Zpm 中该控制的定义，这支持将 PDF 的 PME 视作同一 PMM 控制要求的文本拼写差异，不能把它另解为独立 CSR 字段。按要求仍分别保留各来源原始拼写。
- §17.1.2.2、.6：VA 的高 PMLEN 位以 bit `XLEN-PMLEN-1` 符号扩展，PA（包括 Bare 与 guest-physical address）则以零填充；显式访存适用，instruction fetch 和 page-table walk 等隐式访问不适用。适用显式访问族见下表。`MXR` 在有效特权级生效时会抑制 pointer masking；MPRV/SPVP 会影响有效特权级选择。

## 活动路径与实现证据

### Kunminghu

当前 HEAD 与锁定 SHA 相符。活动 NewCSR 的 `EnvCfg.PMM[33:32]` 默认 `00`，合法枚举为 Disable/PMLEN7/PMLEN16；`Hstatus.HUPMM[49:48]` 亦默认 Disable。`NewCSR.scala` 将 mseccfg、menvcfg、henvcfg、hstatus.HUPMM、senvcfg PMM 注册后传给 TLB。普通访问按有效模式选择：M 用 mseccfg，HS/S 用 menvcfg，VS 用 henvcfg，U/VU 用 senvcfg。规范另规定 HLV/HSV 访问如同 VS 时用 henvcfg；如同 VU 时，在 U 执行用 hstatus.HUPMM，在 HS/M 执行用 senvcfg。`TLB.scala:167-195` 的 `hyperinst`/`imode` 条件分支与这些控制相对应：普通 VS→henvcfg，VU→senvcfg，HLV/HSV-as-VS→henvcfg，HLV/HSV-as-VU 按 imode 选 HUPMM 或 senvcfg；`182-187` 中 fetch/HLVX 和有效 MXR 分支禁用 mask。`198-213` 随后令 VA 截取 bit 56:0 / 47:0 并符号扩展，PA 则零扩展。该块还处理屏蔽后的 atomic/misaligned access 检查。静态路径：[`CSRBundles.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRBundles.scala#L62)、[`CSRDefines.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRDefines.scala#L194)、[`NewCSR.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala#L1469)、[`HypervisorLevel.scala`](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/HypervisorLevel.scala#L243)、[`TLB.scala`](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala#L178)。访存入口在 `LoadUnit.scala`、`StoreUnit.scala`、`AtomicsUnit.scala`；`rg -ni 'PMM|Ssnpm|pointer.mask' sources/xiangshan/src/test` 未定位专题测试。新增 `experiments/kunminghu-smoke/ssnpm.S` 由 M-mode 设置并读回 `senvcfg.PMM`、开放 PMP 后进入 U-mode。canonical 案例对 load/store/LR.D/SC.D/AMOADD.D 作值断言；tagged 案例按读回控制执行相同探针，PMLEN0 tagged 在 load fault handler 检查 cause 5。四次基础矩阵见 E10–E13；修正后的 PMLEN0 tagged exact trap assertion 见 E20。bit56-set 的额外运行见 E18。PMLEN7 tagged 的 load/store 成功，但 LR.D 触发 cause 5，随后的 NEMU difftest 以 privilege-state mismatch / ABORT 结束；SC/AMO tagged 未到达，故不能标为已验证。

### Heliodor

当前 HEAD 与锁定 SHA 相符。`csr.veryl:794-797` 将 mseccfg、menvcfg、senvcfg 的 `[33:32]` 分别输出为 M/S/U PMM；`henvcfg` 是单独存储的可读写 H CSR（声明 `:391`，读 `:546`、写 `:1130`），复位为零（`:876`）。CSR 可访问不表示字段已接入地址生成选择器。`heliodor_core.veryl:554-565` 按数据访问有效 privilege 从 M/S/U 三路选 PMM；主 load/AMO AGU 在 `:5283-5290` 变换地址，第二 load AGU 在 `:5313-5319` 重复同一变换。`alu_wrap.veryl:191-203` 对标量 AGU 也有 PMLEN 转换。新建 `experiments/ssnpm/build_heliodor_fixtures.py` 生成四个 PMLEN/tagged 与一个 bit56 boundary 的 isolated M-setup/U-access fixtures；每次断言 `senvcfg.PMM` readback，U-mode 对 probe pointer 执行 `sd`/`ld`，并将结果写至 testbench `tohost`。E14、E16、E17 的 pass marker来自四格初次运行；E15 的旧 pass marker无效，因为初版 fixture未拒绝 unexpected successful load。修正版 E21 观察到 PMLEN0 tagged load 成功且以 `tohost=0x12` 报错，表明该测试 harness 的低位 DRAM alias 不能实现预期 access fault。E19 bit56-set case 到 pass marker，但地址观察仍受同一 alias 限制。运行入口和日志归档于 manifest。随后在 `sources/heliodor/src/core/{csr,heliodor_core,alu_wrap}.veryl` 上执行 `rg -ni 'henvcfg\.PMM|hstatus\.HUPMM|csr_pmm_h|HUPMM|PMM'`；该有界检索只定位 M/S/U PMM 输出/selector 和 `alu_wrap.i_pm_mode`，未定位 `henvcfg.PMM` / `hstatus.HUPMM` 到 VS/VU mask selector 的路径；CSR 可读写性不构成该路径的证据。规范要求普通 VS 用 henvcfg、VU 用 senvcfg；HLV/HSV-as-VS 用 henvcfg；HLV/HSV-as-VU 在 U 执行时用 hstatus.HUPMM、在 HS/M 执行时用 senvcfg。该为所检查路径的缺口，不据此断言整个 Heliodor 完全不支持 H guest pointer masking。证据 E3/E4。

## 访问族矩阵

状态限定为本轮锁定源码/测试检查，不表示该族已运行通过。`static path` 表示追踪到共用 mask 后地址路径；`not located` 表示在上述有界路径未定位到相应变换，不能单独作为不支持结论。

| 显式访存族（Zpm v1.0.0 §17.1.2.6） | Kunminghu | Heliodor | 边界 |
|---|---|---|---|
| Integer load/store | U-mode canonical：PMLEN0/7 下 `ld`/`sd` 值断言通过；PMLEN7 tagged 的 `ld`/`sd` 断言在 LR 前通过但不能区分 pointer mask 与高地址别名；bit56=1 load 产生 cause 5 run-fail；PMLEN0 tagged 检查 cause 5（E10–E13、E18、E20） | U-mode canonical、PMLEN7 tagged 和 bit56=1 cases 到 pass marker（E14、E16、E17、E19）；PMLEN0 tagged 修正版观察到 alias load 成功并 run-fail（E21）；所有高地址成功结果受 DRAM harness 低位别名限制 | Kunminghu 与 Heliodor 的 tagged high-address 成功结果都可能是 memory-model low-bit alias，内部有效地址未采样；Kunminghu bit56=1 load cause 5，Heliodor bit56=1 仍受 alias 限制 |
| Atomic（LR/SC/AMO） | canonical PMLEN0/7 的 LR.D/SC.D/AMOADD.D 随 fixture 通过；PMLEN7 tagged 在 LR.D 触发 cause 5，NEMU difftest 因模式状态差异 ABORT，SC/AMO 未到达 | RTL 有 issue AMO/LR/SC 路径并使用 `agu_addr_iss`；当前 U fixture未执行 atomic | tagged atomic 明确 `run-fail` / `unverified`，不是通过；Heliodor atomic 仅静态检查 |
| Floating-point load/store | `DecodeUnit.scala:398-399` 将 FLW/FLD 解码至普通 `FuType.ldu`；无 tagged FP fixture或 Ssnpm 专题测试运行 | `custom/fp_smoke.S` 存在 FLD/FLW 测试入口；该 fixture 不设置 `senvcfg.PMM`，不构成 Ssnpm 运行证据 | 共用 load-unit 静态入口不等于 FP tagged runtime 覆盖 |
| Compressed load/store | `DecodeUnitComp.scala` 有压缩整数 load/store 解码；无 tagged compressed fixture或 Ssnpm 专题运行 | RV64 compressed 指令进入标量整数 load/store 路径；现有 `test_arch` 是普通模式 ISA case，不设置 Ssnpm 控制 | 仅路径/入口检查；没有逐压缩指令地址观察 |
| Cache management operations | DecodeUnit/StoreQueue 有 CBO decode/提交处理；未定位 Ssnpm tagged-address 专题入口，未运行 | `test/cmo/cmo_test.S` 有 CBO 测试入口；本轮未将其改为 U-mode PMM fixture；CMO MMU 权限路由并非已证实的 PMM mask 路径 | 存在测试入口但不是 Ssnpm 用例；不能写作 blocked build 或 tested |
| Vector load/store | Vector LSU 与 vector TLB/DTLB 路径存在；未证明本轮 fixture 对 vector element address 的 PMM 边界，未运行 | `test/vmem/vmem_test.S`、`vperm` 等有 vector memory 入口；独立 VectorUnit element address 路径未在 U-mode PMM case 中运行 | 静态不能从 scalar AGU 推断向量元素地址行为；dynamic unverified |
| Hypervisor HLV/HSV and VS/VU | NewCSR/TLB 有 VS/VU/HUPMM selector 源码路径；无 VS/VU/HV explicit-access tagged 运行 | `test/hlv/hlv_test.S` 有 HLV/HLVX/HSV 构建入口，但不设置 PMM controls；固定 Ssnpm core path未定位 henvcfg/HUPMM selector | 现有 HLVX 明确免 mask；HLV/HSV/VS/VU 不能由 M/U scalar case 外推 |
| Zicfiss shadow-stack explicit accesses | 未确认配置支持或 PMM 路由，未运行 | 未确认配置支持或 PMM 路由，未运行 | feature support 与具体地址入口都未建立 |
| `FENCE` / `FENCE.I` unused address fields | `not-applicable`：当前编码不产生显式内存访问 | `not-applicable`：当前编码不产生显式内存访问 | 规范仅在这些字段未来启用时适用 |
| Instruction fetch and implicit accesses | `not-applicable`：规范排除取指与页表遍历 | `not-applicable`：规范排除取指与页表遍历 | HLVX 也明确免于 pointer masking |

### 逐核、逐模式状态

下表将普通 U、guest VS/VU 与 HLV/HSV hypervisor explicit-access 分开。`tested` 只指列出的 U fixture；`run-fail` 保留失败观察；`static/unverified` 表示有实现或测试入口线索但没有本模式 Ssnpm runtime；`not-applicable` 表示该访问族本身不是 HLV/HSV 指令。

| 访问族 | Kunminghu U | Kunminghu VS/VU | Kunminghu HLV/HSV | Heliodor U | Heliodor VS/VU | Heliodor HLV/HSV |
|---|---|---|---|---|---|---|
| Integer load/store | `tested` PMLEN0/7 canonical；PMLEN0 tagged cause 5；PMLEN7 tagged load/store到达但 alias-limited；bit56=1 load cause 5 run-fail | `unverified`：selector有静态路径、无运行 | `not-applicable`（此行是普通 load/store） | `tested` 四个 PMLEN/tag 组合及 bit56=1；所有高地址 store/load 结果受 low-bit DRAM alias 限制 | `unverified`：guest selector未定位、无运行 | `not-applicable`（普通 load/store） |
| Atomic LR/SC/AMO | canonical全序列 `tested`；PMLEN7 tagged LR.D `run-fail` cause 5，SC/AMO未到达 | `unverified`：selector有静态路径、无运行 | `not-applicable` | `unverified`：有 AGU issue/reservation路径，无 U-mode atomic fixture | `unverified`：selector未定位 | `not-applicable` |
| FP load/store | `unverified`：FLW/FLD解码至普通 LDU；无 tagged FP fixture | `unverified`：无 VS/VU FP Ssnpm fixture | `not-applicable` | `unverified`：有 `fp_smoke.S`，未设置 Ssnpm controls | `unverified`：无 guest FP Ssnpm fixture | `not-applicable` |
| Compressed load/store | `unverified`：普通压缩 load/store decode路径，未运行 tagged fixture | `unverified`：无 guest压缩 Ssnpm fixture | `not-applicable` | `unverified`：普通 RV64C ISA cases不设 PMM | `unverified`：无 guest压缩 Ssnpm fixture | `not-applicable` |
| Cache management | `unverified`：CBO decode/StoreQueue路径，不是 Ssnpm运行 | `unverified`：无 guest CMO运行 | `not-applicable` | `unverified`：`test/cmo/cmo_test.S` 不设 PMM | `unverified`：无 guest CMO运行 | `not-applicable` |
| Vector load/store | `unverified`：vector LSU/DTLB线索，无 tagged element地址观察 | `unverified`：无 VS/VU vector PMM运行 | `not-applicable` | `unverified`：有 `test/vmem/vmem_test.S`，无 PMM控制 | `unverified`：无 guest vector PMM运行 | `not-applicable` |
| Hypervisor access family | `not-applicable`：U普通访问不是 HLV/HSV | `unverified`：VS/VU有效地址路径有静态 selector，无运行 | `unverified`：HLV/HSV-as-VS/VU未运行 | `not-applicable`：U普通访问不是 HLV/HSV | `unverified`：selector未定位 | `unverified`：有 `test/hlv/hlv_test.S` 入口但无 PMM控制 |
| Zicfiss shadow-stack access | `unverified`：扩展支持和地址路由未建立 | `unverified` | `not-applicable` | `unverified`：扩展支持和地址路由未建立 | `unverified` | `not-applicable` |

## Heliodor 案例与验证记录

本轮尝试执行现有 `test/supm/supm_test.S` 与 checkout 中已跟踪的 `test/supm/supm_test.hex`（SHA-256 `aef6f4f1a8073b27fa1dd25051647a64b8803bdd8c0dcc92e5cb7abf844a7690`）及 `tb/test_arch_common.veryl` 的 `test_arch_supm`，没有执行成功。测试程序集覆盖 Bare M-mode `mseccfg.PMM=11` 的 tagged LD、LR/SC alias，`PMM=10` 的 tagged LR/SC alias，以及 `PMM=0` clean LR/SC；其注释指出 flat DRAM 与 Sv39 MMU 会让 tagged LD/SD alias 在禁用时也可能可观察为同一位置，故 LR/SC 才是 discriminator。检查 ID 与输入期望：41 为 PMLEN16 tagged LD 读取初始化值 `0x1111`（源码注释说明该 load 单独不能区分 mask 是否启用）；42/43 为 PMLEN16 tagged SC 成功且 clean 地址读取 `0x2222`；44/45 为 PMLEN7 tagged SC 成功且 clean 地址读取 `0x3333`；46/47 为 PMM=0 clean SC 成功且读取 `0x4444`。这些是汇编中的检查分支/期望值，不是运行观察。HEX 的哈希固定了实际输入身份，但锁定 checkout 缺生成 provenance，故不能证明它由当前 `.S` 生成。它没有写 `senvcfg` / `henvcfg`，不覆盖 S/U/VS/VU profile Ssnpm 要求。

- 命令 `cd sources/heliodor && make -C test/supm`：exit 0，输出 `Nothing to be done for 'all'`；现有 `test/supm/supm_test.hex` 已存在，本次未重建输入。
- 命令 `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl --version`：Veryl `0.22.0 (967e477 2026-10-02)`。
- 命令 `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_supm`：exit 1，testbench check 阶段报 `invalid_initial_assign`，定位 `tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)`；仿真没有启动。还有 missing_port warnings，但本次确切阻塞为 `dram` 初始化错误。没有把该结果记为 pointer-masking 运行失败。
- Story 6.7 isolated runner 以 `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ssnpm --timeout 180` 重试已有 `test_arch_supm`，通过局部 `allow(initial_assign)` 隔离变换后 CPU-start=true、exit 0，观察 `supm tohost=1` / `supm PASS`（E9）。这只说明 M-mode Supm prerequisite 在该变换下可运行；它不测试 `senvcfg`、`henvcfg`、S/U/VS/VU Ssnpm 行为，故记录 topic 为 `supm-prerequisite`，不作为 Ssnpm run-pass。原始未变换 testbench 的 `$readmemh` blocker 仍由 E6 精确记录。
- 新增的 Ssnpm-only U-mode fixture 不复用 Supm 先决运行：M-mode 设置并读回 senvcfg.PMM，设置 PMP、`mret` 至 U，再执行 scalar `sd`/`ld`。canonical 与可预期 tagged cases 已启动；Heliodor PMLEN0 tagged 修正版观察到 alias load 成功、按预期标为 harness-limited run-fail（E21）。bit56-set fixture 在 Heliodor 到 pass marker 但地址受 alias 限制（E19），在 Kunminghu 于 U-mode load 产生 cause 5（E18）。PMM=0 tagged 通过的实际限制是 testbench 对 DRAM 只用地址低位作索引；该 case不声称裸高地址合法或被 mask。VS/VU/HLV/HSV 仍无有效 selector 证据或 Ssnpm runtime。
- bounded entry search: Heliodor `test/cmo/cmo_test.S`, `test/vmem/vmem_test.S`, `test/hlv/hlv_test.S`, `test/riscv-arch-test/custom/fp_smoke.S` 存在对应非-Ssnpm测试入口；这些源未设置 Ssnpm PMM/进入目标模式。Kunminghu fixed source 的 `DecodeUnit.scala`、`DecodeUnitComp.scala`、LoadUnit/StoreUnit/AtomicsUnit 和 vector/CMO paths 有普通执行入口，但 `rg -ni 'PMM|Ssnpm|pointer.mask' sources/xiangshan/src/test` 无专题 test；本轮仅建立 scalar load/store/atomic fixture。各未测项按矩阵保留 `inspected only` 或 `unverified`，不把普通入口当成 Ssnpm build blocker。

## Kunminghu U-mode PMLEN 运行记录

runner：`experiments/kunminghu-smoke/run.py --topic ssnpm --ssnpm-case <case>`；fixture `experiments/kunminghu-smoke/ssnpm.S`，锁定 Kunminghu SHA `c098f996bf4d301b88693b20315486d31e93bc9d`，KunminghuV2Config、单 hart、NEMU difftest。run IDs、命令、控制读回、输入/输出哈希和日志在 manifest 中。`pmlen0-tagged` 和两个 canonical case pass；PMLEN7 tagged 执行到 LR.D 时触发访问异常并被 NEMU difftest 判为 ABORT，不应将 SC/AMO写成已运行。新增 bit56=1 probe 于 PC `0x80000064` 发生 load access fault cause 5；模拟器 PMP 日志记录 raw `vaddr/paddr=0x01000000800000e0`，其 DUT/参考模型归因未确定。

| case | 控制/模式 | 指令及预期 | 观察 |
|---|---|---|---|
| `pmlen0-canonical` | M 写 senvcfg.PMM=00、读回00、mret U | `ld/sd/lr.d/sc.d/amoadd.d` 验证 0x1234→0x5678→0x9abc→0x9abd | run-pass；全断言通过 |
| `pmlen0-tagged` | PMM=00、mret U | tagged load 预期 access fault cause 5 | run-pass；异常 handler 观察 cause 5 |
| `pmlen7-canonical` | PMM=10、读回10、mret U | 同 canonical 访存族序列 | run-pass；全断言通过 |
| `pmlen7-tagged` | PMM=10、读回10、mret U | tagged `ld/sd` 后 LR.D/SC.D/AMOADD.D 应使用同有效地址 | run-fail；load/store断言到达；LR.D 于 PC `0x80000088` 产生 cause 5、mtval=`0xfe000000800000e0`，NEMU difftest报告 privilege-state mismatch 并 ABORT；SC/AMO未到达 |
| `pmlen7-bit56` | PMM=10、读回10、mret U；输入指针 bit56=1 | mask 应符号扩展 bit56 后执行 `ld/sd` | run-fail；PC `0x80000064` load cause 5；PMP 日志记 raw `vaddr/paddr=0x01000000800000e0`；根因尚未判定 |

上述 PMLEN7-tagged 地址来自异常 `mtval`，fixture 未采样内部 masked-address 总线。仅记录实现运行，不将 PMLEN7 tagged atomic 路径认定为通过。

## 证据表
<a id="evidence-table"></a>

| ID | 类型 | 状态 | 固定来源/位置 | 支持的结论与限制 |
|---|---|---|---|---|
| E1 | spec | inspected | RVA23 Profile v1.0 §3.1.2.2 (`Ssnpm`)，发布 PDF p.7；归档 profile 源提交 `e030b70992447784ad9081045d47ce6e278f381e`, `src/rva23-profile.adoc:402` | 发布件 `PME`、固定源文本 `PMM` 的拼写差异及 PMLEN0/7 最低要求；PMM 架构定义另见 E2 |
| E2 | spec | inspected | Pointer Masking v1.0.0 §§17.1.2.2–.8；H v1.0 §14.1.2.1 | `PMM` 编码、地址变换、模式、访问族及 HLV/HSV-as-VS/VU 控制规则 |
| E3 | source | inspected | Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；`backend/fu/wrapper/CSR.scala`、`backend/fu/NewCSR/CSRBundles.scala:67-74`、`backend/fu/NewCSR/CSRDefines.scala:194-200`、`backend/fu/NewCSR/NewCSR.scala:1469-1473`、`backend/fu/NewCSR/HypervisorLevel.scala:243`、`cache/mmu/TLB.scala:178-214` | PMM 定义、传递、模式选择和地址变换静态路径；无 Ssnpm run |
| E4 | source | inspected | Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；`src/core/csr.veryl:129-134,391,546,794-797,876,1130`；`src/core/heliodor_core.veryl:452-454,554-565,5283-5290,5312-5319,5581-5590,6114-6123`；`src/core/alu_wrap.veryl:191-203` | M/S/U PMM、henvcfg CSR 可读写性、两条 issue AGU、scalar `alu_wrap` AGU mask 以及 AMO/LR/SC issue/reservation/SC-PMP 使用 `agu_addr_iss`；此处不声称完整提交写回地址已追踪。guest selector 的检索范围和命令见 Heliodor 路径段。 |
| E5 | test-inspected | inspected | Heliodor `test/supm/supm_test.S`, `test/supm/supm_test.hex` (SHA-256 `aef6f4f1a8073b27fa1dd25051647a64b8803bdd8c0dcc92e5cb7abf844a7690`), `tb/test_arch_common.veryl:6055-6080` | 仅检查 M-mode Supm 测试材料；不是 Ssnpm 验证 |
| E6 | test-run | run-fail | Heliodor `make -C test/supm`; Veryl 0.22.0 `test --test test_arch_supm`; `tb/test_arch_common.veryl:440` | build 目标无需更新；testbench check 因 `$readmemh`/`dram` 初始化错误退出1，仿真未启动 |
| E9 | prerequisite-run | run-pass | Heliodor isolated runner `heliodor-core-20261014T105323Z-112299`; existing `test_arch_supm` | M-mode Supm `tohost=1` only; explicitly not Ssnpm evidence. |
| E10 | CPU-run | run-fail | Kunminghu `kunminghu-fixture-20261014T111942Z-3e81181d1d02` | PMLEN7 tagged reached load/store then LR.D access fault; emulator recorded NEMU difftest ABORT, cause 5, tagged mtval. |
| E11 | CPU-run | run-pass | Kunminghu `kunminghu-fixture-20261014T112020Z-3e81181d1d02` | PMLEN0 canonical U-mode load/store/LR.D/SC.D/AMOADD.D assertions pass. |
| E12 | CPU-run | run-pass | Kunminghu `kunminghu-fixture-20261014T112039Z-3e81181d1d02` | PMLEN7 canonical U-mode load/store/LR.D/SC.D/AMOADD.D assertions pass. |
| E13 | CPU-run | run-pass | Kunminghu `kunminghu-fixture-20261014T112206Z-3e81181d1d02` | PMLEN0 tagged U-mode observes expected load access fault cause 5. |
| E14 | CPU-run | run-pass | Heliodor `heliodor-core-20261014T111658Z-736615`; PMLEN0 canonical | U-mode senvcfg readback and canonical store/load pass. |
| E15 | CPU-run | run-pass (fixture false-positive) | Heliodor `heliodor-core-20261014T111741Z-736615`; initial PMLEN0 tagged fixture | Fixture accepted the unexpected successful high-address load; this run is not valid evidence for the expected fault and is superseded by E21. |
| E16 | CPU-run | run-pass | Heliodor `heliodor-core-20261014T111818Z-736615`; PMLEN7 canonical | U-mode senvcfg readback and canonical store/load pass. |
| E17 | CPU-run | run-pass | Heliodor `heliodor-core-20261014T111847Z-736615`; PMLEN7 tagged | U-mode senvcfg readback and tagged store/load pass; success is harness-alias-limited. |
| E18 | CPU-run | run-fail | Kunminghu `kunminghu-fixture-20261014T113722Z-3e81181d1d02`; PMLEN7 bit56-set | U-mode load PC `0x80000064` raises cause 5; emulator PMP log records raw `vaddr/paddr=0x01000000800000e0`; root cause vs reference behavior unresolved. |
| E19 | CPU-run | run-pass | Heliodor `heliodor-core-20261014T113806Z-1249945`; PMLEN7 bit56-set | U-mode senvcfg readback and store/load assertions pass; effective address is not externally sampled, so this is harness-limited evidence. |
| E20 | CPU-run | run-pass | Kunminghu `kunminghu-fixture-20261014T114139Z-3e81181d1d02`; repaired PMLEN0 tagged fixture | Cause 5, `mepc=tagged_load`, and `mtval` match assertions all pass. |
| E21 | CPU-run | run-fail | Heliodor `heliodor-core-20261014T114158Z-1350679`; repaired PMLEN0 tagged fixture | CPU starts; high-address load reaches DRAM via low-bit alias, fixture reports `tohost=0x12` because expected cause 5 did not occur. This is a harness limitation, not a CPU defect claim; supersedes flawed E15 interpretation. |

## 自检

1. **禁用与 PMLEN7 有何差别？** `00` 不变换地址；`10` 保留低 57 位，VA 用 bit56 扩展符号，PA 将高 7 位清零。规范示例 VA `0xABFFFFFF12345678` 经 PMLEN7 变为 `0xFFFFFFFF12345678`；同位串作为 PA 时变为 `0x01FFFFFF12345678`。地址变换不替代权限检查。
2. **哪些位是边界？** RV64 PMLEN7 的边界源位 bit56、PMLEN16 的 bit47。每种当前定义 PMLEN 对应固定边界，不依 translation mode 动态变化；超出受支持虚拟/物理地址区域的合法性仍由既有地址翻译/权限机制判断。
3. **已检查与未验证是什么？** Kunminghu scalar integer canonical load/store 与 atomic 全序列通过；PMLEN7 tagged atomic 在 LR.D 失败并产生 difftest ABORT；Kunminghu bit56=1 load产生cause 5。Heliodor scalar U的四格与bit56=1 case都到pass marker，但高地址受harness别名限制。PMLEN0 tagged亦受Heliodor harness别名限制。FP/compressed、CMO、vector、VS/VU/HLV/HSV 都有来源入口或静态路径描述，但没有该 Ssnpm 控制下的运行，不外推。

## 未决项

Profile PDF 的 `PME` 与源码/架构规范 `PMM` 是文档拼写差异。未运行 S-mode control、VS/VU/HLV/HSV、MXR/MPRV/SPVP、跨页、FP/compressed tagged、CMO 或 vector tagged 案例。Kunminghu PMLEN7 tagged LR.D 观察到 cause 5/difftest ABORT；SC/AMO tagged 尚未到达。所有 Kunminghu/Heliodor tagged high-address load/store 成功都受各自 memory model 地址别名限制，未直接观察 masked effective address。Heliodor 的 H guest selector 路径仍未定位。
