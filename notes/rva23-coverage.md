# RVA23 必选项覆盖图谱

> 本文件是项目学习映射的规范目录，不是认证或符合性结论。Story 4.2 已填写 RV64I、M、C、B 及标量控制等范围；Story 4.3 已填写 F、D、Zfhmin、Zfa。向量、内存/缓存属性及 S64 特权等其他领域仍待后续故事调查。每项状态只概括对应学习单元中所列的静态证据和边界。

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
| `RVA23U64/v1.0/§3.1.1.2/A` | 原子指令。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：DecodeUnit/MainPipe/AMOALU 有 W/D AMO、LR/SC 局部路径；完整操作语义、异常与 PMA 区域未验证。子案例：译码线索含 LR.W/D、SC.W/D 和 AMOADD/SWAP/XOR/AND/OR/MIN/MAX/MINU/MAXU.W/D；这些仅为译码观察，全部语义未验证；AMOCAS 属可选 Zacas。证据：[E1–E5](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：局部原子 RTL、ACT 配置/历史说明及 LR/SC 测试源码已检查；未运行且未覆盖完整 A 集合及 PMA 条件。子案例：LR.W/D、SC.W/D、AMOADD/SWAP/XOR/AND/OR/MIN/MAX/MINU/MAXU.W/D 的实现语义未逐项验证；Zacas/Zabha 属选项边界。证据：[E1/E6–E9](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/F` | 单精度浮点指令。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：标量译码、执行 wrapper、FCSR/FS 控制路径及测试材料已静态检查，未运行；子案例：S arithmetic/compare/classify/move/load-store/convert/divide-sqrt/FMA 路径线索，完整指令与异常组合未穷尽；证据 ID：[E1–E4](units/rva23u64-floating-point-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：标量 FPU decode/execute/CSR 路径及 rv64uf 测试 harness/hex 已检查，未运行；子案例：已定位 fadd/fclass/fcmp/fcvt/fdiv/fmadd/fmin/ldst/move/recoding 材料，不能据此认定完整覆盖；证据 ID：[E5–E7](units/rva23u64-floating-point-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/D` | 双精度浮点指令。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：标量 D译码和 FALU/FMA/FCVT/FDivSqrt wrapper 路径已静态检查，未运行；子案例：D arithmetic/compare/classify/move/load-store/convert/divide-sqrt/FMA 路径线索，舍入和异常边界未验证；证据 ID：[E1–E4](units/rva23u64-floating-point-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：标量 D 路径及 rv64ud harness/hex 已检查，未运行；子案例：已定位与 rv64uf 类似的具名测试材料及 structural case，未覆盖全部舍入、NaN、异常组合；证据 ID：[E5–E7](units/rva23u64-floating-point-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/C` | 压缩指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：定位到 RVCExpander/RVCDecoder 包装及 PreDecode 压缩长度路径；未审阅完整展开映射；子案例：仅确认压缩指令识别/长度路径，具体 C 指令集合未穷举；证据：E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：c_expander 检查到部分 C ALU 展开及 Zcb 子集，测试材料未运行；子案例：仅含已定位的 ALU/Zcb 展开，完整 C 编码集合未穷举；证据：E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/B` | 位操作指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：DecodeUnit 覆盖部分 B 子扩展；不等于完整 B；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：decoder/ALU 显式含部分 Zba/Zbb/Zbs 案例；完整 B 范围未核验；子案例：见证据 E4；证据 ID：[E4](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicsr` | CSR 指令；因包含 F 而隐含要求。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：DecodeUnit CSR 指令分发与 NewCSR CSRPermit/寄存器路径；访问语义未运行；子案例：见证据 E1/E2；证据 ID：[E1/E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder CSR 类别和 csr 读写路径已检查，未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicntr` | 基础计数器与计时器。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：NewCSR 有 mcycle/minstret 与用户别名；TIME 实现及计数器可见性/TODO 边界未证明完整；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr 有 mcycle/minstret、time 读口与用户别名；未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihpm` | 硬件性能计数器。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：MachineLevel 定义 mhpmcounter3..31 与事件计数路径；配置/全部事件行为未运行；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr event bus、mhpmcounter 路径及 HPM 定向测试材料已检查，未运行；子案例：见证据 E4/E6；证据 ID：[E4/E6](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccif` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持取指；自然对齐且大小为 2 的幂、最大为 min(ILEN, XLEN)（RVA23 中为 32 位）的取指操作必须是原子的。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：IFU/ICache 路径及参数可定位，但自然对齐、2次幂且最大32-bit取指原子性、跨代理行为未证。子案例：短/32-bit、cache-line/page边界及coherent writer未运行。证据：[E1–E3](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：ICache有32-bit取数、跨界拼接和coherence线索；未证指定PMA区域取指原子性。子案例：2/4-byte、straddle和多代理交错未运行。证据：[E1/E6/E10](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccrse` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 RsrvEventual。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：MainPipe/Probe有LR/SC reservation及probe延迟线索，不是RsrvEventual证明。子案例：无争用、竞争、远端持续冲突均未验证。证据：[E1/E3/E5](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：reservation、DCache事件及测试源码已检查；未运行，不能证明RsrvEventual。子案例：仅针对无争用SC.W重排缺陷。证据：[E1/E6/E7/E9](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Ziccamoa` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持 A 扩展的全部原子操作。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：DecodeUnit/DCache MainPipe/AMOALU有局部路径；无完整A操作集在指定主存区域的系统保证。子案例：W/D AMO、LR/SC、异常和代理/PMA交互未穷尽；不含Ziccamoc选项。证据：[E1–E3](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：原子RMW路径、ACT配置及历史报告已检查；本轮未运行，未证全部A操作和适用区域。子案例：历史测试不替代完整PMA/代理矩阵；Zacas/Zabha分开。证据：[E1/E6–E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicclsm` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持非对齐 load 与 store。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：Load/StoreMisalignBuffer显示最多两片段；PMA、跨line/page、异常优先级及所有宽度行为未覆盖。子案例：LB/LH/LW/LD、SB/SH/SW/SD局部线索，未运行。证据：[E1/E4](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：DCache路径、MISALIGNED_LDST=true参数及历史报告已检查；未运行且未证明所有PMA区。子案例：部分suite有历史报告，跨页/行组合未验证。证据：[E1/E6–E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Za64rs` | 保留集必须连续、自然对齐，且最大为 64 字节。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：MainPipe用get_block_addr跟踪reservation，DCache默认blockBytes=64；粒度线索存在，配置实例和连续/自然对齐不变量未验证。子案例：跨64B边界、W/D LR/SC未验证。证据：[E3](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：reservation RTL与ACT“精确覆盖访问宽度”(XLEN size)参数已检查；实现状态及对齐边界未证。子案例：W/D、synonym、remote writes未全测。证据：[E6/E7/E9](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihintpause` | 暂停提示指令。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：PAUSE 解码为 fence 提示路径；微架构停顿效果未证明；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder 将 PAUSE 作为 NOP 处理；提示 bundle 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zic64b` | 缓存块大小为 64 字节，且在地址空间中自然对齐。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：DCache默认blockBytes=64，DTS导出参数化I/D cache block size；实际平台所有cache参数和地址空间未核。子案例：I/D实例、自然对齐未验证。证据：[E3](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：I-cache RTL为64B line，ACT CACHE_BLOCK_SIZE=64且README有缓存说明；配置/说明不证明全部系统实例。子案例：I/D/L2代理、对齐/alias未测。证据：[E7/E10](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicbom` | 缓存块管理指令。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：DecodeUnit有CBO_CLEAN/FLUSH/INVAL及DCache CMO请求接口；各操作权限、代理和PMA语义未核完。子案例：clean/flush/inval有路由线索，未运行；CBO_ZERO归Zicboz。证据：[E2/E3/E5](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：decoder clean/inval/flush 路由、coherent no-op/inval升级flush配置和历史报告已检查；未运行。子案例：clean/flush/inval及PMP历史子集，系统范围有限；zero归Zicboz。证据：[E6–E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicbop` | 缓存块预取指令。 | 状态：`partially-studied`；位置/范围：见内存缓存学习单元；理由：DecodeUnit追踪到soft-prefetch的r/w/i操作标签及DCache prefetch agent；未追踪它们与Zicbop的CBO指令逐变体映射，不能据此声明支持。子案例：r/w/i标签已见；CBO prefetch.r/w/i译码和语义均未逐项验证。证据：[E2/E5](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：ACT配置声明Zicbop且README有历史suite报告；未发现逐变体RTL追踪，本轮未运行。子案例：CBO prefetch.r/w/i三种变体均未逐项追踪；历史suite不能证明具体变体支持。证据：[E7/E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicboz` | 缓存块清零指令。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：DecodeUnit CBO_ZERO及LSU/DCache线索已检查；整块清零、对齐、权限/可见性未运行。子案例：block边界和共享可见性未验证。证据：[E2/E3](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：decoder cbo.zero路由、core 64B fill-zero及ACT参数已检查；历史报告1项，本轮未运行。子案例：整块效果、权限和PMA/代理交互未验证。证据：[E6–E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zfhmin` | 半精度最小浮点：仅要求半精度 load/store、寄存器间搬运，以及 H↔S/D 转换，不包含 H 算术。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：译码显式含 H 运算（例如 `FADD_H`）、转换、FALU 等路径，但这宽于 Zfhmin 最小要求，材料和运行证据不足；子案例：确认 decode/wrapper 有 H 路径线索；Zfhmin 所需搬运/转换/访存逐项正确性未验证，H 算术不计入 Zfhmin；证据 ID：[E1–E4](units/rva23u64-floating-point-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见浮点学习单元；理由：源码具有 H 操作路径且有定向源码、hex 与 harness，但均未执行；子案例：材料自述覆盖 FLH/FSH、FMV.X.H/H.X、FCVT.S.H/H.S、FCVT.D.H/H.D，含少量舍入/NaN-box/flags case；不涵盖完整边界验证；证据 ID：[E5–E7](units/rva23u64-floating-point-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zkt` | 与数据无关的执行时延。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：译码/执行源代码不能证明数据无关时延属性；未提供本次侧信道/时序证据；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：已有标量功能 RTL/测试材料不能证明数据无关时延；未见本次时序证据；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/V` | 向量扩展；参数/行为按 V v1.0，局部证据不等于完整指令覆盖。 | 状态：`partially-studied`；位置/范围：`DecodeUnit.scala` 接入 `VecDecoder.table`；默认 VLEN=128、ELEN=64 且可参数化；VSET/VADD/VRGATHER 及内部 VLD/VST load/store 路由标签（不是 ISA 助记符）与 vtype/vlenb/VLSU 路径线索；理由：已检查源码和 VSET harness/VsetRef（固定 VLEN=128、ELEN=64），未运行；子案例：E1 源码；E3 对 vill/vta/vma/vsew/vlmul、函数、AVL、oldVL 做组合输入，以 VsetRef 期望比较 vill/vta/vma/vsew/vlmul/vl 输出；参数全集、指令全集、异常/重启、mask/tail 全组合未核验；证据 ID：[E1/E3](units/rva23u64-vector-v1.md#证据表)。 | 状态：`partially-studied`；位置/范围：`decoder.veryl` OP_V、`heliodor_core.veryl` VRF/VU 派发、`vector_unit.veryl`、`vector_pkg.veryl`、`vrf.veryl`、`csr.veryl`；固定 VLEN=128、ELEN=64；理由：已检查实现子集和定向测试材料，未运行；子案例：E2 源码；vadd/vsetvl 见 E4–E5；vmem 的 unit-stride/masked store、vseg 的 segment 顺序、vleff 的 vl 截断分别见 E6a–E6c；完整 opcode、参数、异常重启与所有 mask/tail 组合未验证；历史 PASS 仅 E7；证据 ID：[E2/E4–E6c/E7](units/rva23u64-vector-v1.md#证据表)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvfhmin` | 向量最小半精度浮点：V v1.0 §30.18.4，仅使 `SEW=16` 下 `vfwcvt.f.f.v`（binary16→binary32）和 `vfncvt.f.f.w`（binary32→binary16）有定义；依赖 `Zve32f`，不要求 Zvfh 的 H 算术/归约/搬移全集。 | 状态：`partially-studied`；位置/范围：`VecDecoder.scala` 有向量 FP widening/narrowing 路由与 `FCVT_H_S`/`FCVT_S_H` 等标量路由，另见 `VFWCVT_F_F_V`/`VFNCVT_F_F_W` 向量转换 decoder 路由；`FPDecoder.scala` 的 FP16 / `VSew.e16` 控制线索仍不能证明这些向量路由在 SEW=16 正确；`Parameters.scala` 声明 `zvfhmin`。路由/名称不证明运行时 SEW=16 的两条最小转换语义；`scripts/xiangshan.py` 列出的向量 FP 镜像属于 `Zvfh`，不能替代 Zvfhmin。子案例：E1–E3；`SEW=16`、binary16/binary32 窄化/宽化转换数值、标志/舍入、完整 Zvfh 不在已核验范围；证据 ID：[E1–E3](units/rva23u64-vector-security-and-half.md#证据表)。 | 状态：`partially-studied`；位置/范围：`vector_unit.veryl` 有向量 FP 窄化/宽化路径和 SEW=16 整数向量几何线索；`test/act/config/heliodor/sail.json` 报告 Zvfhmin unsupported。已检查 `test/vfarith` 的单/双精度转换与 `test/vnarrow` 的整数窄化材料，不是 binary16 Zvfhmin 案例；不存在仅凭这些材料断言实现缺失。子案例：E4–E6；目标转换与全 SEW/异常边界未核验；证据 ID：[E4–E6](units/rva23u64-vector-security-and-half.md#证据表)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvbb` | 向量基础位操作集合：`vandn.[vv,vx]`、`vbrev.v`、`vbrev8.v`、`vrev8.v`、`vclz.v`、`vctz.v`、`vcpop.v`、`vrol.[vv,vx]`、`vror.[vv,vx,vi]`、`vwsll.[vv,vx,vi]`；依 V Crypto v1.0 §32.1.2.1，EEW=8/16/32（Zve32x）及 EEW=64（Zve64x）。不以标量 Zbb 或基础 V 操作作为该集合证据。 | 状态：`partially-studied`；位置/范围：`Instructions.scala` 定义 Zvbb 的多个 BitPat；`VecDecoder.scala` 将已列部分 opcode 路由到 `vialuF`/`vipu`，包含向量/标量/立即数形式。opcode pattern/译码映射不证明执行单元所有行为和合法 EEW；未逐项确认集合闭合。子案例：E1、E2；所有 Zvbb 指令形式、SEW/EEW 和边界未验；证据 ID：[E1–E2](units/rva23u64-vector-security-and-half.md#证据表)。 | 状态：`partially-studied`；位置/范围：`vector_unit.veryl` 可见基础 V 的 mask population 路径，但它不是 Zvbb 的 vector-element `vcpop.v`，也不是 Zvbb 全集合逐指令实现核对；ACT `sail.json` 将 Zvbb 标为 unsupported。预构建 `rv64uzbb` 是标量 Zbb 测试镜像，不是 Zvbb 向量证据；当前检查到的向量 ALU/FP 测试材料未包含 Zvbb 指令刺激。子案例：E3–E5；列表其余操作、EEW 与功能行为未核验；证据 ID：[E3–E5](units/rva23u64-vector-security-and-half.md#证据表)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zvkt` | 向量数据无关执行时延（DIEL）：Vector Crypto v1.0 §32.1.2.15 要求所有已实现的列举指令满足 DIEL，约束按操作数及明确豁免定义；不包括所有存储/浮点操作、`vcpop.m` 等列明排除项。 | 状态：`partially-studied`；位置/范围：检查 `VecDecoder.scala`、`Instructions.scala` 及 XiangShan `src/test/scala`；源码与功能译码/测试材料无法证明 DIEL，未发现本轮时序/形式属性证据。搜索未命中不等于证明不存在；具体已实现 DIEL 指令集合也未穷尽。子案例：E1、E2；未证明任何 DIEL 契约；证据 ID：[E1–E2](units/rva23u64-vector-security-and-half.md#证据表)。 | 状态：`partially-studied`；位置/范围：检查 `vector_unit.veryl`、`sail.json` 以及测试/断言材料；ACT 配置将 Zvkt 标为 unsupported，只支持该配置声明事实。功能 RTL、配置和普通功能测试均不能证明 DIEL；本轮未找到能证明数据无关时延的测量或形式化证据。子案例：E3–E5；列举指令的每数据操作数时延契约未验证；证据 ID：[E3–E5](units/rva23u64-vector-security-and-half.md#证据表)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zihintntl` | 非时间局部性提示。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：在指定译码/测试搜索范围未定位到可确认的 NTL 处理；不能据此判断缺失；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：test_arch_hint 覆盖 bundle 注释提及 NTL，但未定位到独立刺激/断言及 decoder 路径；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zicond` | 整数条件操作。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：DecodeUnit 有 czero.eqz/nez 两条映射；ALU 路径尚无本故事运行结果；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder/ALU 有 czero.eqz/nez；Zicond 专用 hex/harness 已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zimop` | RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。按 ratified [Zimop ISA 定义](https://docs.riscv.org/reference/isa/v20260120/unpriv/zimop.html)，未被重新定义时 MOP 指令将零写入 `rd`。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：DecodeUnit 有 MOP.R/RR pattern 和 isZimop 后处理线索；所有索引编码及最终默认结果需进一步核对；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：decoder 显式识别 MOP.R/RR 并令 rd=0；hint bundle 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zcmop` | RVA23U64 必选扩展；may-be 描述指令可由后续扩展重新定义的行为。按 ratified [Zcmop ISA 定义](https://docs.riscv.org/reference/isa/v20260120/unpriv/zimop.html)，未被重新定义时 C.MOP 指令不写任何寄存器。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：未在已定位的香山压缩展开路径中确认 C.MOP 全部合法编码；不能据搜索缺失判不存在；子案例：见证据 E1/E3；证据 ID：[E1/E3](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：c_expander 将所检查的 C.MOP 保留编码扩为 NOP；hint 测试材料已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zcb` | 附加压缩指令。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：指定 PreDecode 路径未能逐项确认 Zcb 扩展解码；不能据搜索缺失判不存在；子案例：见证据 E1；证据 ID：[E1](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：c_expander 明确包含 c.mul 与 zext/sext 子集；专用 Zcb harness 已检查，未运行；子案例：见证据 E4/E5；证据 ID：[E4/E5](units/rva23u64-scalar-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zfa` | 附加浮点指令；RVA23U64 新增必选扩展。 | 状态：`studied-unverified`；位置/范围：`FPDecoder.scala`/`DecodeUnit.scala` 可见部分 Zfa pattern；执行由既有浮点单元分发；`fudian/`、`yunsuan/` 快照目录为空，内部单元无法从本快照检查；子案例：本次观察子集为 FLEQ/FLTQ、FMINM/FMAXM、FROUND/FROUNDNX、FCVTMOD.W.D；该子集的语义、异常/flags 及完整 Zfa 指令集合均未验证；证据 ID：[E1–E4](units/rva23u64-floating-point-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：decoder/fpu_wrap 含部分 Zfa opcode 与执行分支，测试源码和输入文件存在但 ignored，未执行；子案例：zfa_s1–s4 材料分别涉及比较/minmax、round、FCVTMOD.W.D 等可见案例；无完整指令矩阵及实际运行证据；证据 ID：[E5–E7](units/rva23u64-floating-point-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Zawrs` | 等待保留集指令。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：DecodeUnit分别有WRS_NTO/WRS_STO路由，xiangshan.py列workload；入口不证明等待/唤醒语义，本轮未运行。子案例：NTO、STO分别有译码线索；等待、唤醒、提前终止及reservation event语义未验证。证据：[E2/E5](units/rva23u64-memory-cache-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见内存缓存学习单元；理由：decoder分别注释WRS.NTO/WRS.STO可立即结束为NOP；README有历史声明，本轮未运行。子案例：NTO、STO分别有译码线索；两者等待/唤醒行为及权限/中断/event组合未验证。证据：[E6/E8](units/rva23u64-memory-cache-v1.md#evidence-table)。 |
| `RVA23U64/v1.0/§3.1.1.2/Supm` | 指针屏蔽；执行环境至少须提供选择 PMLEN=0 与 PMLEN=7 的方式。 | 状态：`partially-studied`；位置/范围：见标量学习单元；理由：EnvPMM 枚举含 Disable 与 PMLEN7，但须核验配置寄存器/执行环境暴露选择及变址路径；子案例：见证据 E2；证据 ID：[E2](units/rva23u64-scalar-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：见标量学习单元；理由：csr/alu_wrap 有 PMLEN=0/7 地址屏蔽路径线索；对所有访问类与模式的行为未运行；子案例：见证据 E4；证据 ID：[E4](units/rva23u64-scalar-v1.md#evidence-table)。 |

### RVA23S64 §3.1.2 — 必选基础、继承项与特权扩展

Sha 是 profile 定义的增强型 Hypervisor 要求组合；本清单将其展开为 H 与 7 个配套扩展要求行，分别追踪，不为组合名称重复增加一条覆盖计数。

| 稳定键（profile/v1.0/section/ID） | 要求及适用条件 / 继承关系 | Kunminghu：状态；位置/范围；理由；子案例；证据 ID | Heliodor：状态；位置/范围；理由；子案例；证据 ID |
|---|---|---|---|
| `RVA23S64/v1.0/§3.1.2.1/RV64I` | 必选基础 ISA 为 RV64I，采用小端序；U-mode 中的 ECALL 触发到 S-mode 的受控陷阱，S-mode 中的 ECALL 触发向执行环境请求的陷阱。 | 状态：`partially-studied`；位置/范围：[CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1254)、[TrapHandleModule.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/TrapHandleModule.scala:51)；理由：源码区分 U/S ECALL cause、medeleg/mideleg 路由及 S trap target，并更新 S trap 状态；未验证全部 RV64I、端序、委托组合或运行行为。子案例：U cause 8、S cause 9、U→S 委托、S→M 环境请求、M/SIE 与中断优先级；Ecall 具体路由仍未动态验证。证据：[E1–E3](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：[heliodor_core.veryl](../sources/heliodor/src/core/heliodor_core.veryl:4647)、[csr.veryl](../sources/heliodor/src/core/csr.veryl:900)；理由：源码区分 U/S cause、委托目标和 S/M trap-entry 更新；未验证全部 RV64I 与 S-mode ECALL 端到端环境服务。子案例：已有 U ECALL 测试源码与 S-mode timer/PLIC 测试源码；未运行，S ECALL 与所有委托组合未证。证据：[E1、E3–E5](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
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
| `RVA23S64/v1.0/§3.1.2.2/Ss1p13` | Supervisor 架构版本 1.13。 | 状态：`partially-studied`；位置/范围：[SupervisorLevel.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SupervisorLevel.scala:63)、[TrapHandleModule.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/TrapHandleModule.scala:51)、既有 [CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1254)；理由：已定位 S CSR、陷阱路由/进入/返回路径；未完整审计 Privileged Architecture v1.13，也无本轮运行证据。子案例：委托异常/中断、sstatus、sepc/scause/stval、SRET 有源码线索；其他 S 语义未检查。证据：[E1–E2](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：[heliodor_core.veryl](../sources/heliodor/src/core/heliodor_core.veryl:4647)、[csr.veryl](../sources/heliodor/src/core/csr.veryl:900)；理由：已定位核心 S trap entry/return 与 supervisor CSR 路径；不是完整 1.13 映射。子案例：U/S cause、delegation、SRET、S CSR 写入有源码线索；更多特权架构行为未核验。证据：[E1、E3](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
| `RVA23S64/v1.0/§3.1.2.2/Svbare` | 必须支持 satp 的 Bare 模式。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sv39` | 基于页的 39 位虚拟内存系统。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svade` | 访问 A=0 的页或写入 D=0 的页时，必须触发 page-fault 异常。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssccptr` | 在同时具有可缓存性与一致性 PMA 的主存区域中，必须支持硬件读取页表。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstvecd` | stvec.MODE 必须能够取值 0（Direct）；在 Direct 模式下，stvec.BASE 必须能够保存任意有效的四字节对齐地址。 | 状态：`partially-studied`；位置/范围：[CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:457)、[TrapHandleModule.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/TrapHandleModule.scala:88)；理由：stvec WARL mask `~0x2` 只清 bit 1，读写 map 保留高位 BASE 和 bit 0；trap target 按低位对齐并在 vectored interrupt 时加 cause。静态掩码仍不能证明任意有效 BASE 的端到端能力。子案例：MODE=Direct、MODE=Vectored 的 interrupt/exceptions、BASE 多个四字节对齐值与边界写读未动态测。证据：[E2](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：[csr.veryl](../sources/heliodor/src/core/csr.veryl:253)、[heliodor_core.veryl](../sources/heliodor/src/core/heliodor_core.veryl:4937)；理由：stvec 有独立存储，trap target 以低两位清零；未观察多个任意合法 BASE 的写读/跳转。子案例：Direct、Vectored 同步异常/中断 target 公式有源码线索；所有合法 BASE 与非法 MODE 行为未测。证据：[E3–E4](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstvala` | 发生 load、store、取指 page-fault、access-fault 或非对齐异常时，stval 必须写入故障虚拟地址；断点异常也须写入该地址，但由 EBREAK/C.EBREAK 指令引起的断点除外。发生 virtual-instruction 或 illegal-instruction 异常时，stval 必须写入故障指令。 | 状态：`partially-studied`；位置/范围：[CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1364)、[CSR.scala trap update](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:1516)；理由：可追踪延迟 tval 更新与 S entry 写入/清零，但各异常值来源及 breakpoint 例外未逐项验证。子案例：load/store/fetch page fault、access fault、misaligned、非 EBREAK breakpoint 地址、EBREAK/C.EBREAK 例外、virtual-instruction 与 illegal-instruction 编码；全部运行结果未验证。证据：[E1–E2](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`partially-studied`；位置/范围：[heliodor_core.veryl](../sources/heliodor/src/core/heliodor_core.veryl:4775)、[csr.veryl](../sources/heliodor/src/core/csr.veryl:900)；理由：可追踪 tval 进入 S trap CSR 的通道；trap 输入对 load/store/fetch fault 与 illegal instruction 有选择线索，但源码排除 `commit_virt_instr` 的指令编码路径，该虚拟化边界不作为符合性证据；breakpoint 等来源未穷举。子案例：load/store/fetch page/access/misaligned, breakpoint excluding EBREAK/C.EBREAK, virtual-instruction, illegal-instruction；无本轮运行证据。证据：[E1、E3–E4](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
| `RVA23S64/v1.0/§3.1.2.2/Sscounterenw` | 对于每个非只读零值的 hpmcounter，其对应的 scounteren 位必须可写。 | 状态：`partially-studied`；位置/范围：[CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:470)、[CSR.scala scounteren mapping](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:796)；理由：源码声明 scounteren 存储，但写 mask 为零且代码注释指出不支持用户计数器；已有 Zihpm 路径使“非只读零值”的具体集合需单独界定，不能将此映射判为满足或缺失。子案例：每个 implemented HPM counter 对应 bit writable；计数器实现与访问矩阵未运行。证据：[E2](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：[csr.veryl](../sources/heliodor/src/core/csr.veryl:360)、[csr.veryl read/write](../sources/heliodor/src/core/csr.veryl:519)；理由：scounteren 为 CSR state，常规 S-mode write 路径写入全部位；HPM counter 3..31 计数路径有源码线索，但没有逐位写读运行验证。子案例：每个非只读零值 hpmcounter 对应使能位、只读零值 counter exclusion、权限/读写检查未运行。证据：[E3](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
| `RVA23S64/v1.0/§3.1.2.2/Svpbmt` | 基于页的内存类型。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svinval` | 细粒度地址转换缓存失效。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Svnapot` | NAPOT 地址转换连续性。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sstc` | Supervisor 模式计时器中断。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Sscofpmf` | 计数器溢出与基于特权模式的过滤。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssnpm` | 指针屏蔽；senvcfg.PME 与 henvcfg.PME 至少须支持 PMLEN=0 和 PMLEN=7。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 | 状态：`not-studied`；位置/范围：待填；理由：待填；子案例：待填；证据 ID：待填。 |
| `RVA23S64/v1.0/§3.1.2.2/Ssu64xl` | sstatus.UXL 必须能够取值 2（UXLEN=64）。 | 状态：`partially-studied`；位置/范围：[CSR.scala](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:384)、[CSR.scala SSTATUS mask](../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala:424)；理由：源码将 UXL 列为只读字段并定义掩码，注释显示 RV64 约束；本轮未做 CSR 读写验证。子案例：读 UXL=2、写入不改变值；未运行。证据：[E1–E2](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 | 状态：`studied-unverified`；位置/范围：[csr.veryl](../sources/heliodor/src/core/csr.veryl:426)、[sstatus read](../sources/heliodor/src/core/csr.veryl:519)；理由：SSTATUS_XL_RO 将 UXL 位读为 2，S status read 路径合成该常量；未运行 CSR 检查。子案例：UXL=2 readback、写入保持只读；未运行。证据：[E1、E3](units/rva23s64-supervisor-traps-v1.md#evidence-table)。 |
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
