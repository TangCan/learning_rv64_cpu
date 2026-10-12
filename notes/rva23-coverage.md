# RVA23 必选项覆盖图谱

> 本文件是项目学习映射的规范目录，不是认证或符合性结论。Story 4.2 已填写基础整数与标量范围行；其余领域仍保持 `not-studied`。每项状态只概括对应学习单元中所列的静态证据和边界。

## 规范基线

- Profile：RISC-V RVA23 Profile **v1.0**，§3.1（U64 §§3.1.1–3.1.1.4；S64 §§3.1.2–3.1.2.4）。
- 状态：RISC-V International Ratified Specifications Library 将该版本列为已批准（ratified）；[RISC-V International 的 ratification 公告](https://riscv.org/blog/risc-v-announces-ratification-of-the-rva23-profile-standard/)亦确认该状态。此目录仅以该正式文本为规范基线。
- 官方来源：[RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)。下方每个要求行均给出 profile、版本、小节及要求标识符。
- 源码快照（后续映射定位用，不构成实现结论）：`xiangshan-kunminghu-v2-20261012` (`c098f996bf4d301b88693b20315486d31e93bc9d`)；`heliodor-master-20261012` (`94e9c5821c24a8941c3ddc3b76daddc7124a855a`)。

## 身份、计数与状态规则

- 稳定键格式：`<profile>/v1.0/§<profile-section>/<requirement-id>`。行为条件保留在要求描述中；同一规范项的 S64 继承行有 S64 profile 键，并以 `继承自` 指向 U64 原始键。
- 统计同时报告 profile 行数与去重要求数：继承关联不产生新的规范要求；U64 行是规范要求的原始计数项。
- 两个实现分别填写状态、实现位置或范围决定、理由、子案例、证据 ID。初始状态 `not-studied` 表示未调查，绝不表示缺失。仅可使用 `not-studied`、`partially-studied`、`studied-unverified`、`evidence-observed`、`not-present`、`out-of-scope`。缺证据时不能标 `not-present`；`out-of-scope` 必须记录学习范围决定和理由。
- 覆盖表中的实现状态使用 AD-4 词汇；每个证据 ID 则回链到学习记录模板中的证据表，并沿用其独立的 `Kind` 与 `Status` 列。`Kind` 可为 `spec`、`design-doc`、`source`、`test-inspected`、`test-run` 或 `experiment`；`Status` 可为 `inspected`（已检查材料）、`run-pass`/`run-fail`（已运行并观察到结果）、`unverified`（结果未经运行验证）或 `not-applicable`（不适用）。这两列各自描述证据类别和证据状态，不存在固定的一对一对应；`run-pass` 必须包含可复查的命令与观察输出。
- 实现状态描述项目证据，单项测试、局部 RTL 或上游自述不证明整项覆盖，也不构成认证。比较结论必须分别链接两边证据 ID，并列出未检查子案例。

## 强制要求目录

### RVA23U64 §3.1.1 — 必选基础与扩展

| 稳定键（profile/v1.0/section/ID） | 要求及适用条件 | Kunminghu：状态；位置/范围；理由；子案例；证据 ID | Heliodor：状态；位置/范围；理由；子案例；证据 ID |
|---|---|---|---|
| `RVA23U64/v1.0/§3.1.1.1/RV64I` | 必选基础 ISA 为 RV64I，采用小端序；ECALL 触发向执行环境请求的陷阱。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：部分基础译码/ALU 路径；完整 RV64I 与端序、异常语义未逐项核验；子案例：见证据 E1/E2；证据 ID：[E1/E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：解码与 ALU 路径及架构指令测试材料已定位；全指令子案例未穷尽；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/M` | 整数乘法与除法。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：MulUnit/DivUnit 与 decode 路径；边界行为未运行；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：ALU/多周期 int_divider 与 RV64UM 定向测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/A` | 原子指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/F` | 单精度浮点指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/D` | 双精度浮点指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/C` | 压缩指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：定位到 RVCExpander/RVCDecoder 包装及 PreDecode 压缩长度路径；未审阅完整展开映射；子案例：仅确认压缩指令识别/长度路径，具体 C 指令集合未穷举；证据：E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：c_expander 检查到部分 C ALU 展开及 Zcb 子集，测试材料未运行；子案例：仅含已定位的 ALU/Zcb 展开，完整 C 编码集合未穷举；证据：E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/B` | 位操作指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：DecodeUnit 覆盖部分 B 子扩展；不等于完整 B；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：decoder/ALU 显式含部分 Zba/Zbb/Zbs 案例；完整 B 范围未核验；子案例：见证据 E4；证据 ID：[E4](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicsr` | CSR 指令；因包含 F 而隐含要求。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：DecodeUnit CSR 指令分发与 NewCSR CSRPermit/寄存器路径；访问语义未运行；子案例：见证据 E1/E2；证据 ID：[E1/E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder CSR 类别和 csr 读写路径已检查，未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicntr` | 基础计数器与计时器。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：NewCSR 有 mcycle/minstret 与用户别名；TIME 实现及计数器可见性/TODO 边界未证明完整；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr 有 mcycle/minstret、time 读口与用户别名；未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihpm` | 硬件性能计数器。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：MachineLevel 定义 mhpmcounter3..31 与事件计数路径；配置/全部事件行为未运行；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr event bus、mhpmcounter 路径及 HPM 定向测试材料已检查，未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccif` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持取指；自然对齐且大小为 2 的幂、最大为 min(ILEN, XLEN)（RVA23 中为 32 位）的取指操作必须是原子的。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccrse` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 RsrvEventual。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccamoa` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 A 扩展的全部原子操作。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicclsm` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持非对齐 load 与 store。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Za64rs` | 保留集必须连续、自然对齐，且最大为 64 字节。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihintpause` | 暂停提示指令。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：PAUSE 解码为 fence 提示路径；微架构停顿效果未证明；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder 将 PAUSE 作为 NOP 处理；提示 bundle 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zic64b` | 缓存块大小为 64 字节，且在地址空间中自然对齐。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicbom` | 缓存块管理指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicbop` | 缓存块预取指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicboz` | 缓存块清零指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zfhmin` | 半精度浮点。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zkt` | 与数据无关的执行时延。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：译码/执行源代码不能证明数据无关时延属性；未提供本次侧信道/时序证据；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：已有标量功能 RTL/测试材料不能证明数据无关时延；未见本次时序证据；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/V` | 向量扩展。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvfhmin` | 向量最小半精度浮点。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvbb` | 向量基础位操作指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvkt` | 向量操作的与数据无关执行时延。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihintntl` | 非时间局部性提示。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：在指定译码/测试搜索范围未定位到可确认的 NTL 处理；不能据此判断缺失；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：test_arch_hint 覆盖 bundle 注释提及 NTL，但未定位到独立刺激/断言及 decoder 路径；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicond` | 整数条件操作。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：DecodeUnit 有 czero.eqz/nez 两条映射；ALU 路径尚无本故事运行结果；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder/ALU 有 czero.eqz/nez；Zicond 专用 hex/harness 已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zimop` | RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。按 ratified [Zimop ISA 定义](https://docs.riscv.org/reference/isa/v20260120/unpriv/zimop.html)，未被重新定义时 MOP 指令将零写入 `rd`。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：DecodeUnit 有 MOP.R/RR pattern 和 isZimop 后处理线索；所有索引编码及最终默认结果需进一步核对；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder 显式识别 MOP.R/RR 并令 rd=0；hint bundle 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zcmop` | RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。按 ratified [Zcmop ISA 定义](https://docs.riscv.org/reference/isa/v20260120/unpriv/zimop.html)，未被重新定义时 C.MOP 指令不写任何寄存器。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：未在已定位的香山压缩展开路径中确认 C.MOP 全部合法编码；不能据搜索缺失判不存在；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：c_expander 将所检查的 C.MOP 保留编码扩为 NOP；hint 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zcb` | 附加压缩指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：指定 PreDecode 路径未能逐项确认 Zcb 扩展解码；不能据搜索缺失判不存在；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：c_expander 明确包含 c.mul 与 zext/sext 子集；专用 Zcb harness 已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zfa` | 附加浮点指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Zawrs` | 等待保留集指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23U64/v1.0/§3.1.1.2/Supm` | 指针屏蔽；执行环境至少须提供选择 PMLEN=0 与 PMLEN=7 的方式。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：EnvPMM 枚举含 Disable 与 PMLEN7，但须核验配置寄存器/执行环境暴露选择及变址路径；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr/alu_wrap 有 PMLEN=0/7 地址屏蔽路径线索；对所有访问类与模式的行为未运行；子案例：见证据 E4；证据 ID：[E4](units/rva23u64-scalar-v1.md#evidence-table)。 |

### RVA23S64 §3.1.2 — 必选基础、继承项与特权扩展

Sha 是 profile 定义的增强型 Hypervisor 要求组合；本清单将其展开为 H 与 7 个配套扩展要求行，分别追踪，不为组合名称重复增加一条覆盖计数。

| 稳定键（profile/v1.0/section/ID） | 要求及适用条件 / 继承关系 | Kunminghu：状态；位置/范围；理由；子案例；证据 ID | Heliodor：状态；位置/范围；理由；子案例；证据 ID |
|---|---|---|---|
| `RVA23S64/v1.0/§3.1.2.1/RV64I` | 必选基础 ISA 为 RV64I，采用小端序；U-mode 中的 ECALL 触发到 S-mode 的受控陷阱，S-mode 中的 ECALL 触发向执行环境请求的陷阱。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/M` | **继承**：整数乘法与除法。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/M`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/A` | **继承**：原子指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/A`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/F` | **继承**：单精度浮点指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/F`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/D` | **继承**：双精度浮点指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/D`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/C` | **继承**：压缩指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/C`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/B` | **继承**：位操作指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/B`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicsr` | **继承**：CSR 指令；因包含 F 而隐含要求。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicsr`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicntr` | **继承**：基础计数器与计时器。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicntr`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zihpm` | **继承**：硬件性能计数器。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zihpm`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ziccif` | **继承**：在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持取指；自然对齐且大小为 2 的幂、最大为 min(ILEN, XLEN)（RVA23 中为 32 位）的取指操作必须是原子的。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Ziccif`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ziccrse` | **继承**：在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 RsrvEventual。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Ziccrse`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ziccamoa` | **继承**：在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 A 扩展的全部原子操作。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Ziccamoa`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicclsm` | **继承**：在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持非对齐 load 与 store。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicclsm`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Za64rs` | **继承**：保留集必须连续、自然对齐，且最大为 64 字节。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Za64rs`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zihintpause` | **继承**：暂停提示指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zihintpause`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zic64b` | **继承**：缓存块大小为 64 字节，且在地址空间中自然对齐。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zic64b`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicbom` | **继承**：缓存块管理指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicbom`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicbop` | **继承**：缓存块预取指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicbop`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicboz` | **继承**：缓存块清零指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicboz`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zfhmin` | **继承**：半精度浮点。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zfhmin`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zkt` | **继承**：与数据无关的执行时延。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zkt`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/V` | **继承**：向量扩展。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/V`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zvfhmin` | **继承**：向量最小半精度浮点。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zvfhmin`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zvbb` | **继承**：向量基础位操作指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zvbb`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zvkt` | **继承**：向量操作的与数据无关执行时延。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zvkt`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zihintntl` | **继承**：非时间局部性提示。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zihintntl`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zicond` | **继承**：整数条件操作。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zicond`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zimop` | **继承**：RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。未被重新定义时 MOP 指令将零写入 `rd`。关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zimop`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zcmop` | **继承**：RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。未被重新定义时 C.MOP 指令不写任何寄存器。关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zcmop`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zcb` | **继承**：附加压缩指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zcb`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zfa` | **继承**：附加浮点指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zfa`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zawrs` | **继承**：等待保留集指令。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Zawrs`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Supm` | **继承**：指针屏蔽；执行环境至少须提供选择 PMLEN=0 与 PMLEN=7 的方式。 关联原始要求 `RVA23U64/v1.0/§3.1.1.2/Supm`；按原始 U64 键去重计数。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Zifencei` | 指令取指栅栏。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ss1p13` | Supervisor 架构版本 1.13。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svbare` | 必须支持 satp 的 Bare 模式。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sv39` | 基于页的 39 位虚拟内存系统。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svade` | 访问 A=0 的页或写入 D=0 的页时，必须触发 page-fault 异常。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssccptr` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持硬件读取页表。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstvecd` | stvec.MODE 必须能够取值 0（Direct）；在 Direct 模式下，stvec.BASE 必须能够保存任意有效的四字节对齐地址。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstvala` | 发生 load、store、取指 page-fault、access-fault 或非对齐异常时，stval 必须写入故障虚拟地址；断点异常也须写入该地址，但由 EBREAK/C.EBREAK 指令引起的断点除外。发生 virtual-instruction 或 illegal-instruction 异常时，stval 必须写入故障指令。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sscounterenw` | 对于每个非只读零值的 hpmcounter，其对应的 scounteren 位必须可写。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svpbmt` | 基于页的内存类型。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svinval` | 细粒度地址转换缓存失效。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svnapot` | NAPOT 地址转换连续性。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstc` | Supervisor 模式计时器中断。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sscofpmf` | 计数器溢出与基于特权模式的过滤。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssnpm` | 指针屏蔽；senvcfg.PME 与 henvcfg.PME 至少须支持 PMLEN=0 和 PMLEN=7。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssu64xl` | sstatus.UXL 必须能够取值 2（UXLEN=64）。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/H` | Hypervisor 扩展。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssstateen` | 必须提供 Supervisor 模式的 sstateen0-3 和 Hypervisor 模式的 hstateen0-3 state-enable 寄存器。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shcounterenw` | 对于每个非只读零值的 hpmcounter，其对应的 hcounteren 位必须可写。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shvstvala` | 在 Sstvala 所列的全部情形下，vstval 必须写入对应值（见 RVA23S64/v1.0/§3.1.2.2/Sstvala）。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shtvala` | 在 ISA 允许的所有情形下，htval 必须写入发生故障的 guest physical address。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shvstvecd` | vstvec.MODE 必须能够取值 0（Direct）；在 Direct 模式下，vstvec.BASE 必须能够保存任意有效的四字节对齐地址。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shvsatpa` | satp 支持的全部地址转换模式都必须由 vsatp 支持。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Shgatpa` | 对于 satp 支持的每种 SvNN 方案，必须支持对应的 hgatp SvNNx4 模式；也必须支持 hgatp Bare 模式。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |

## 非强制项目（与强制目录分开）

以下类别保留 profile 中的分类；未列入实现映射字段，也不计入必选项覆盖统计。

### RVA23U64 局部选项
- Zvkng — 支持带 GCM 的 NIST 向量密码算法。
- Zvksg — 支持带 GCM 的商用密码向量算法。

### RVA23U64 开发选项
- Zabha — 字节与半字原子内存操作。
- Zacas — Compare-and-Swap 指令。
- Ziccamoc — 在同时具有可缓存性与一致性 PMA 的主存区域中，提供 AMOCASQ 级别的 PMA 支持。
- Zvbc — 向量无进位乘法。
- Zama16b — 未跨越自然对齐 16 字节边界的非对齐 load、store 和 AMO 必须是原子的。

### RVA23U64 扩展选项
- Zfh — 标量半精度浮点。
- Zbc — 标量无进位乘法。
- Zicfilp — Landing Pad（间接跳转目标）保护。
- Zicfiss — 影子栈。
- Zvfh — 向量半精度浮点。
- Zfbfmin — 标量 BF16 转换。
- Zvfbfmin — 向量 BF16 转换。
- Zvfbfwma — 向量 BF16 扩宽乘加。

### RVA23U64 过渡选项
- 规范未列出。

### RVA23S64 特权局部选项
- 规范未列出。

### RVA23S64 特权开发选项
- 规范未列出。

### RVA23S64 特权扩展选项
- Sv48 — 基于页的 48 位虚拟内存系统。
- Sv57 — 基于页的 57 位虚拟内存系统。
- Zkr — 熵 CSR。
- Svadu — 硬件更新 A/D 位。
- Sdtrig — 调试触发器。
- Ssstrict — 标准保留编码行为：执行未实现的标准/保留 opcode 或访问相应 CSR 时，必须受控陷入 Supervisor；该要求不规定自定义编码空间或 CSR。要求适用于声明兼容 RVA23 且包含 H 的执行环境，不适用于其 guest VM。
- Svvptc — 无须显式内存管理 fence，PTE 从无效变为有效的更新须在有界时间内可见。
- Sspm — Supervisor 模式指针屏蔽；执行环境至少须能选择 PMLEN=0 和 PMLEN=7。

### RVA23S64 特权过渡选项
- 规范未列出。

## 建议项

- `RVA23U64/v1.0/§3.1.1.4/illegal-instruction`：强烈建议在执行未实现的 opcode 时触发 illegal-instruction 异常。（建议，不是必选项）
- `RVA23S64/v1.0/§3.1.2.4/illegal-instruction-or-CSR`：强烈建议在执行未实现的 opcode 或访问未实现的 CSR 时触发 illegal-instruction 异常。（建议，不是必选项）

## Profile 说明（非独立必选要求）

| Note ID | 规范说明 |
|---|---|
| `RVA23U64-N1` | U64 关于 illegal-instruction 的建议不是强制要求。 |
| `RVA23U64-N0` | V 在 RVA22U64 中是可选项，在 RVA23U64 中成为必选项。 |
| `RVA23U64-N2` | RVA22 的标量密码 Zkn/Zks 在 RVA23 中不再是选项；profile 说明其方向是转向向量密码。Zbc 属于扩展选项。 |
| `RVA23U64-N3` | Profile 说明：Ziccamoc 是 profile 定义的扩展，要求适用主存区域支持 AMOCASQ；规范称其 PMA 定义将加入特权架构手册。 |
| `RVA23U64-N4` | Profile 说明：Zama16b 对应 Sm1p13 引入的 Misaligned Atomicity Granule 特性；规范称其定义将加入 PMA 章节。 |
| `RVA23S64-N1` | S64 基于特权架构 1.13；Ss1p13 取代 Ss1p12。 |
| `RVA23S64-N2` | 本 profile 将 Zifencei 规定为支持指令缓存一致性的唯一标准机制；Zjid 被描述为仍在开发、未来可能成为选项。 |
| `RVA23S64-N3` | Svnapot、Sstc、Ssu64xl 与增强型 Hypervisor 要求 Sha 在 RVA22 中为可选项，在 RVA23 中为必选项。 |
| `RVA23S64-N4` | Sha 是 profile 对增强型 Hypervisor 要求组合的命名，包含表中 H 及配套特性；规范说明该命名不改变特性集合，定义将加入 Hypervisor 章节。本清单按组成项展开追踪，不另计一条组合覆盖。 |
| `RVA23S64-N5` | Ssstrict 不规定自定义编码空间或 CSR；该 profile 规则适用于声明兼容 RVA23 的执行环境，不适用于 guest VM。 |

## 上游项目自述（非规范要求、非实现证据）

Story 4.1 未收集或采用 Kunminghu、Heliodor 的符合性自述。以后若引用，必须单独记录原始来源、日期、原文范围及证据 ID；不得混入上述规范要求，也不得作为覆盖证明。

## 当前目录计数

- RVA23U64 必选 profile 行：**34**（1 条基础 + 21 个沿自 RVA22 的必选扩展 + 12 个 RVA23 新增必选扩展）。
- RVA23S64 必选 profile 行：**58**（1 条基础 + 33 个继承扩展 + 24 个 S64 特有条目：1 个 Zifencei + 15 个其他必选特权扩展 + 8 个 Sha 组成项）。
- Profile 行总数：**92**。
- 去重规范要求数：**59**（34 个 U64 要求 + 1 个 S64 基础 + 24 个 S64 特有条目；33 个继承项不重复计数。Sha 是 8 个组成项的组合名称，不另设一条要求行）。
- Story 4.2 已填写 RV64I 与本故事标量范围的两侧状态；A 与 Zawrs 明确留给 Story 4.6，其他非本故事领域保持 `not-studied`。单元状态反映静态调查范围，不表达动态通过或完整支持。

## 来源与证据边界

- 规范：仅 RVA23 Profile v1.0 §3.1；扩展手册用于后续解释具体扩展，不在本目录复制全文。
- 文档、源码、测试检查、实际测试运行、实验属于不同证据种类，均须保留具体 ID、固定快照/版本、位置和检查或运行状态。
- 只有观察到运行结果才可记录 `run-pass`；测试材料存在或已阅读不能作为运行通过。项目声明和单项测试均不能证明完整满足 profile 要求。
- 本清单是学习追踪工具，不宣称 Kunminghu、Heliodor 或本项目获得认证，也不宣称已完整符合 RVA23。
