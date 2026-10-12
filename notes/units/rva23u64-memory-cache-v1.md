---
unit_id: "rva23u64-memory-cache"
stage_id: "Epic 4 / Story 4.6"
scope: "RVA23U64 mandatory A, Ziccif, Ziccrse, Ziccamoa, Zicclsm, Za64rs, Zic64b, Zicbom, Zicbop, Zicboz, Zawrs and evidence boundaries for two fixed RTL snapshots."
exclusions:
  - "S64 inheritance rows; separately tracked requirements are unchanged."
  - "Optional/development Zama16b, Zabha, Zacas, Ziccamoc requirements beyond their relevance to distinguishing scope."
  - "Platform PMA maps, complete ISA conformance, proof of global progress, and unrun tests."
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0"
    section: "§3.1.1.2 (mandatory memory/cache requirements)"
    profile_category: "mandatory"
  - name: "A Extension"
    edition: "v2.1 ratified"
    section: "LR/SC, AMO, reservation sets"
    profile_category: "mandatory"
  - name: "CMO Extension"
    edition: "v1.0 ratified"
    section: "cache-block management, prefetch, and zero operations"
    profile_category: "mandatory"
  - name: "Zawrs"
    edition: "v1.01 ratified"
    section: "WRS.NTO and WRS.STO"
    profile_category: "mandatory"
source_snapshots:
  - project: "Kunminghu"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    repository: "https://github.com/OpenXiangShan/XiangShan.git"
    branch: "kunminghu-v2"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    repository: "https://github.com/dalance/heliodor.git"
    branch: "master"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

<!-- 本单元只记录固定快照里可复查的证据。静态检查及上游历史报告不代表本轮运行或合规认证。 -->

## 单元自检

- **问题：** 为什么 `LR/SC`/AMO、cache-block 和 misaligned 证据都不能单独说明 RVA23 所要求的所有主存区域属性？
- **学习者答案：** 这些证据只覆盖局部 RTL、配置或选定案例。Profile 对 Ziccif、Ziccrse、Ziccamoa、Zicclsm 明确限定在同时具有 cacheability 与 coherence PMA 的主存区域；本次未找到两项目标平台的完整 PMA 区域表，也未运行覆盖所有代理和区域的测试。因此保留区域条件，将平台保证标为未验证。
- **检查类型：** explanation
- **证据 ID：** E1–E10

## 架构行为与子案例

Profile 中 Ziccif 要求适用区域取指，且自然对齐、大小为 2 的幂且不超过 min(ILEN, XLEN) 的取指是原子的（RVA23 为 32 位）；Ziccrse 要求 RsrvEventual；Ziccamoa 要求 A 全部原子操作；Zicclsm 要求适用区域支持非对齐 load/store。Za64rs 将 reservation set 限为连续、自然对齐且最多 64 字节。Zic64b 要求自然对齐的 64 字节 cache block。Zicbom、Zicbop、Zicboz 分别涉及 cache-block 管理、预取、清零指令。Zawrs 提供 WRS.NTO/WRS.STO 等待提示。A 与各 ratified 扩展的具体操作语义以所列规范为准；本单元不将译码或单一案例等同完整架构行为。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 同时具有 cacheability + coherence PMA 的主存区域 | unconfirmed | 两项目标快照的相关 RTL/ACT 配置未给出可审计的完整物理区域 PMA 地图；涉及 Ziccif、Ziccrse、Ziccamoa、Zicclsm。E1、E7、E10。 |
| 指令取指支持及最大 32 位取指原子性 | unconfirmed | 两侧可见取指/缓存结构线索；未检查跨代理指令写入与取指原子性端到端证据。E2、E6、E10。 |
| A 全操作集合：LR.W/D、SC.W/D；AMOADD、AMOSWAP、AMOXOR、AMOAND、AMOOR、AMOMIN、AMOMAX、AMOMINU、AMOMAXU 各自的 .W/.D 形式 | unconfirmed | 两侧译码/局部数据路径观察不等于语义核验；以上每种操作和宽度的结果、异常及内存类型均未逐项验证。AMOCAS 属可选 Zacas，不计入本集合。Heliodor 历史 ACT 报告不在本轮重跑。E2、E5–E8。 |
| LR/SC 保留集连续、自然对齐且不超过 64B | unconfirmed | Kunminghu 以 cache block 地址跟踪；Heliodor Sail 配置写明精确覆盖访问宽度（XLEN size），但实现与平台级保证未形式验证。E3、E7、E9。 |
| RsrvEventual / 无争用 LR/SC 进展 | unconfirmed | 有局部倒计时或定向回归源码；没有本轮活性证明/运行结果，也不覆盖所有竞争情形。E3、E6、E9。 |
| 非对齐 load/store：宽度、拆分、跨 dword/line、异常与 PMA | unconfirmed | 两侧 RTL/配置有拆分线索；缺少端到端运行矩阵，且 Heliodor ACT 参数并不证明所有平台区域。E4、E7、E8。 |
| 64B cache block 与地址对齐 | unconfirmed | Kunminghu D-cache 参数默认 64B 且 DTS 导出 cache size 属性；Heliodor cache RTL/平台说明使用 64B line。仍需核实具体配置实例和系统完整地址空间。E3、E10。 |
| Zicbom clean/flush/inval 与权限/内存区域边界；Zicboz zero 单列 | unconfirmed | 有指令/请求路由和 ACT 配置/历史报告；逐项架构语义、系统代理交互和全部权限区域未在本轮执行。Heliodor 的 inval 配置按 coherent write-back 实现升级为 flush。CBO_ZERO/cbo.zero 仅归 Zicboz。E2、E5、E7、E8。 |
| Zicbop 的 CBO prefetch.r、prefetch.w、prefetch.i 各变体 | unconfirmed | Kunminghu 只追踪到 soft-prefetch r/w/i 内部操作标签，未建立它们与三条 CBO 指令的逐变体对应；Heliodor 仅见 ACT 扩展声明和汇总历史套件，未逐变体追踪。三种 CBO 变体均未确认实现/行为。E2、E5、E7、E8。 |
| WRS.NTO 与 WRS.STO 等待行为（分别考察） | unconfirmed | 两者分别有译码线索；实现注释允许提示立即结束，但 NTO/STO 的等待与唤醒行为均未验证。不据译码声明推断进展或功耗行为。E2、E6、E8。 |

### 规范子语义与证据边界

| 要求 | 必须区分的子案例 | 本单元检查结果 / 仍未证明 |
| --- | --- | --- |
| A：LR/SC 与 AMO | LR.W/LR.D、SC.W/SC.D 自然对齐；LR.W/AMO.W 结果按 XLEN 符号扩展；SC 成功写 0、失败写非零；未匹配 reservation 的 SC 失败；LR/SC 访问不匹配或被其他 agent 写入时的失效。RsrvEventual 只对满足 Zalrsc 约束、位于支持该属性区域的 constrained loop 生效；超出约束不据此推断进展。 | 两侧已见部分译码/状态路径，未逐项验证指令语义、异常或无争用/争用活性。自然对齐要求不同于 Zicclsm 的普通非对齐 load/store。E2–E9。 |
| Ziccif：取指原子性 | 规范上限 min(ILEN,XLEN)=32 bit；按 `min(ILEN, XLEN)=32 bits` 展开 8/16/32-bit 自然对齐取指粒度（分别按 1/2/4-byte 对齐）；RISC-V 指令 parcel 最小 16 bits，因此 8-bit 项作为取指访问粒度的边界条件单独核实，不能当作完整指令长度。32-bit 指令若从 2 mod 4 地址跨界拼接，则另记为非自然对齐的 instruction case，不从自然对齐 32-bit 原子性条款外推出保证。 | RTL 有跨界拼接路径，但没有适用 PMA 区域、多 agent 写入时取指原子性的端到端证据。E1、E10–E11。 |
| Zicbom：CBO.INVAL/CLEAN/FLUSH | 三者均作用于由有效地址选中的 cache block；CLEAN 将脏数据传播到一致性点，FLUSH 等价于 clean 后失效；INVAL 使缓存副本失效，但单独对脏副本执行可能让内存暴露旧值。CBCFE/CBIE 及地址访问权限/PMA 决定是否可执行或如何处理 inval；不把译码等同缓存代理已观察到效果。 | 只看到命令路由或 Heliodor 历史配置/报告；未验证寄存器许可、共享代理可见性及所有地址区域。E2–E3、E6–E8。 |
| Zicboz：CBO.ZERO | 将选定 cache block 的所有字节写为零；在可写且 Zicboz supported-access-type PMA 允许的区域适用。操作可逐字节、任意顺序和粒度完成，规范不要求整块原子可见；CBO 操作数选择 block，Zic64b 要求系统 block 64-byte 且自然对齐。 | 两边存在 opcode/zero-fill 路由线索，Heliodor 有 64-byte 参数/历史单项报告；没有跨代理可见性、异常边界或本轮行为验证。E2–E3、E6–E8。 |
| Zicbop：PREFETCH.I/R/W | 三种分别提示未来 instruction fetch、data read、data write；属于 HINT，可被实现忽略。若目标地址无 load/store/fetch 权限，则不抛异常且不得访问缓存或内存；不能把软件 prefetch pipeline 当作每种 ISA hint 均已实现。 | Kunminghu 有 Zicbop decode comment 与处理入口；Heliodor 目前主要是 ACT/历史报告声明，未确认三种指令端到端效果。E2、E5–E8。 |
| Ziccrse、Za64rs | 仅对 profile 限定 PMA 区域谈 RsrvEventual；reservation set 必须连续、自然对齐、最大 64 bytes。 | cache-line 地址跟踪或 ACT reservation 配置只是微架构/模型线索，不能代替全系统属性证明。E1、E3、E6–E9。 |

## 要求到证据索引

下表直接回链覆盖目录各状态与理由所依赖的证据；“未证”表示静态材料不足，不暗示实现缺失。

| Profile requirement | Kunminghu evidence | Heliodor evidence |
| --- | --- | --- |
| A | E2–E5 | E6–E9 |
| Ziccif | E1、E11 | E1、E6、E10 |
| Ziccrse | E1、E3、E5 | E1、E6、E9 |
| Ziccamoa | E1–E3、E5 | E1、E6、E8 |
| Zicclsm | E1、E4 | E1、E6–E8 |
| Za64rs | E1、E3 | E1、E6、E7、E9 |
| Zic64b | E1、E3 | E1、E7、E10 |
| Zicbom | E1–E3、E5 | E1、E6–E8 |
| Zicbop | E1、E2、E5 | E1、E7、E8 |
| Zicboz | E1–E3 | E1、E6–E8 |
| Zawrs | E1、E2、E5 | E1、E6、E8 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit.scala` 将 LR/SC、AMO 与 WRS 操作路由至 LSU/CSR；其中观察到 LR.W/D、SC.W/D 以及 AMOADD/SWAP/XOR/AND/OR/MIN/MAX/MINU/MAXU 的 W/D 译码项，这些仅是译码观察，操作语义和异常均未验证。CBO CLEAN/FLUSH/INVAL 路由至 store LSU；CBO_ZERO 单独归 Zicboz。soft-prefetch 的 r/w/i 标签及 DCache prefetch agent 可见，但未将其映射到 Zicbop 的 CBO prefetch.r/w/i 指令。D-cache MainPipe 有 LR/SC 倒计时、按 cache block 地址匹配及 AMO ALU 更新路径；Probe 会延迟与 reservation block 冲突的 coherence probe，这是局部冲突处理线索，不建立公平性或 RsrvEventual 进展保证。Load/Store MisalignBuffer 有最多两片段的 load/store 对齐数据处理线索。以上均为局部 RTL 证据，不证明 PMA 区域行为或完整代理一致性。E2–E4。
- **源码位置：** [DecodeUnit.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:233)、[MainPipe.scala](../../sources/xiangshan/src/main/scala/xiangshan/cache/dcache/mainpipe/MainPipe.scala:604)、[Probe.scala](../../sources/xiangshan/src/main/scala/xiangshan/cache/dcache/mainpipe/Probe.scala:87)、[LoadMisalignBuffer.scala](../../sources/xiangshan/src/main/scala/xiangshan/mem/lsqueue/LoadMisalignBuffer.scala:39)、[StoreMisalignBuffer.scala](../../sources/xiangshan/src/main/scala/xiangshan/mem/lsqueue/StoreMisalignBuffer.scala:41)。D-cache `blockBytes=64` 为参数默认值；[XSDts.scala](../../sources/xiangshan/src/main/scala/xiangshan/XSDts.scala:39) 导出配置值，[Parameters.scala](../../sources/xiangshan/src/main/scala/xiangshan/Parameters.scala:366) 列出 ISA 名称。E3。
- **相关验证：** [AMOADD.D 既有单元](amoadd-d-v1.md)仅追踪一条 AMO 路径；[xiangshan.py](../../sources/xiangshan/scripts/xiangshan.py:373) 列出预取和 Zawrs 工作负载材料。仅检查了源码/清单；本轮未运行。E5。取指前端的跨页路径见 `IFU.scala:529`，仅作为拼接/异常处理的代码定位；在 `src/main/scala`、测试树和脚本中搜索 atomic fetch、Ziccif 与相关术语未发现可支持本 profile 保证的测试或平台说明。E11。

## Heliodor 路径

- **阶段与状态变化：** `decoder.veryl` 对 WRS.NTO、WRS.STO 各有译码路径，注释允许它们作为立即结束的 NOP；此线索不验证任一提示的等待/唤醒行为。CBO decode 路由 zero 与 cache maintenance。`heliodor_core.veryl` 保存 VA/PA reservation、ROB 年龄与 committed 状态，并以 D-cache presence/invalidation 事件清除/监测；`dcache.veryl` 连接 line-presence、AMO/SC 与 misaligned 访问路径。`icache.veryl` 描述 64B 行、32-bit fetch words 和跨取指拼接。局部 RTL 不证明主存 PMA 属性、原子取指或全局 RsrvEventual。E6。
- **源码位置：** [decoder.veryl](../../sources/heliodor/src/core/decoder.veryl:650)、[heliodor_core.veryl](../../sources/heliodor/src/core/heliodor_core.veryl:2776)、[dcache.veryl](../../sources/heliodor/src/cache/dcache.veryl:220)、[icache.veryl](../../sources/heliodor/src/cache/icache.veryl:1)。ACT config 声明 Ziccif/Ziccrse/Ziccamoa/Zicclsm 等扩展与 XLEN-size reservation、MISALIGNED_LDST 和 CACHE_BLOCK_SIZE 参数；这是参考模型/测试平台配置，不是 RTL 平台保证。E7。
- **相关验证：** [test_lrsc_reorder.veryl](../../sources/heliodor/tb/test_lrsc_reorder.veryl:1) 是单 hart、无争用 SC.W 重排回归的测试源码，本轮未运行。ACT README 记录历史 506/506 结果及 cache-block、misaligned 用例；该文本仅作为已检查的上游历史报告，本轮没有观察到其运行输出。E8、E9。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧都提供原子、CBO 或 misaligned 的局部实现线索；没有证据足以推广到所有同时具 cacheability 与 coherence PMA 的主存区域。 | E1–E5 | E1、E6–E8 |
| C2 | 两侧都显示 64B cache-line 线索；配置/参数和设备树或 README 声明不能单独证明整个平台的 Zic64b 保证。 | E3 | E7、E10 |
| C3 | LR/SC 局部状态/测试不能证明完整 RsrvEventual 或任意争用下进展；Heliodor 单元测试源码只覆盖特定重排故障。 | E3、E5 | E6、E9 |
| C4 | Heliodor 的 ACT 参数明确配置 reservation 精确覆盖访问宽度、非对齐 load/store 支持、64B cache block；它是 Sail/ACT 配置证据，不是 RTL 原子性或 PMA 证明。 | — | E7 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | Profile 要求和扩展语义基线 | spec | inspected | RVA23 Profile v1.0、A v2.1、CMO v1.0、Zawrs v1.01 | [Profile §3.1.1.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#section-rva23u64-mandatory-extensions); [A](https://docs.riscv.org/reference/isa/unpriv/a-st-ext.html); [CMO](https://docs.riscv.org/reference/isa/unpriv/cmo.html); [Zawrs](https://docs.riscv.org/reference/isa/unpriv/zawrs.html) | not-run | 不适用 | PMA 前提、A 指令、CMO 操作类别和权限、WRS 行为 | 按 ratified 文本分开记录 profile 要求及扩展操作语义 | 已阅读上述官方规范的相关章节；没有据此推断 RTL 或平台合规 | none |
| E2 | Kunminghu 指令译码范围 | source | inspected | xiangshan-kunminghu-v2-20261012 | DecodeUnit.scala:233–265, 476–482 | not-run | 固定快照 | WRS、A W/D、CBO clean/flush/inval；另有单独的 CBO_ZERO 路由（归 Zicboz） | 只支持译码路由存在 | 已检查相应 decode table；zero 不计入 Zicbom | none |
| E3 | Kunminghu D-cache 原子/reservation/cache-block 参数与 DTS 声明 | source | inspected | xiangshan-kunminghu-v2-20261012 | MainPipe.scala:604–649, 683–754; Probe.scala:87–96; DCacheWrapper.scala:40–64, 619–622; XSDts.scala:39–50; Parameters.scala:872–876 | not-run | 默认/参数化配置 | LR/SC、AMOALU、Probe block 地址、64B cache block | 不适用于源码检查 | 看到局部机制及参数默认值；未确认生成平台实例与 PMA 区域 | none |
| E4 | Kunminghu misaligned load/store 实现线索 | source | inspected | xiangshan-kunminghu-v2-20261012 | LoadMisalignBuffer.scala:39–80; StoreMisalignBuffer.scala:41–69; LoadUnit.scala | not-run | 固定快照 | 两片段拆分/移位掩码 | 不适用于源码检查 | 已检查入口和局部拆分结构；端到端异常/跨缓存行覆盖未验证 | none |
| E5 | Kunminghu 测试入口 | test-inspected | unverified | xiangshan-kunminghu-v2-20261012 | notes/units/amoadd-d-v1.md; scripts/xiangshan.py:373–378 | not-run | 既有单元与工作负载列表 | AMOADD.D 单路径、softprefetch、Zawrs 列表项 | 若运行需各自验证输出 | 只检查既有记录/列表；本轮未运行 | none |
| E6 | Heliodor 原子、reservation、CBO、取指及 misaligned 局部 RTL | source | inspected | heliodor-master-20261012 | decoder.veryl:616–675, 716–721; alu_wrap.veryl:344–363; heliodor_core.veryl:2776–2809, 5580–5665, 6734–6741, 6839–6840; dcache.veryl:210–242, 637–645; icache.veryl:1–55 | not-run | 固定快照 | A decode/commit, CBO decode/zero, WRS NOP, LR/SC reservation and cache presence, misaligned paths, I-cache fetch | 不适用于源码检查 | 已检查局部路径；未建立 PMA、完整取指原子性或全域进展结论 | none |
| E7 | Heliodor Sail/ACT configuration declarations | design-doc | inspected | heliodor-master-20261012 | test/act/config/heliodor/heliodor.yaml:18–28, 45–47, 62–66, 157–166; sail.json:647–679 | not-run | ACT/Sail reference config | extension flags, XLEN-size reservation, misaligned LD/ST, 64B cache blocks | 不适用于配置检查 | 配置中存在声明；不是 RTL 结论或本轮测试结果 | none |
| E8 | Heliodor 上游历史 ACT 报告 | design-doc | inspected | heliodor-master-20261012 | test/act/README.md:67–82, 210–237; README.md:145–152 | not-run | README 标记历史报告/提交环境 | ACT4 506/506 总计；atomic/compressed/CSR 129/129；Zicbom 3、Zicboz 1、Zicbop 3；PMPZaamo 1/1、PMPZalrsc 1/1、PMPZicbo 4/4；Misalign/MisalignD/MisalignF/MisalignZca 8/2/2/8 | 仅按 README 记载为历史报告数量；atomic 129/129 未细分各 A 指令/宽度，CBO 与 prefetch 计数也未列每条变体 | 已检查 README 历史报告，未观察本轮输出，不记 run-pass | none |
| E9 | Heliodor LR/SC 定向测试源码 | test-inspected | unverified | heliodor-master-20261012 | tb/test_lrsc_reorder.veryl:1–32 | not-run | M-mode, single-hart test image as source comments specify | uncontended SC.W reordered behind younger LR.W | harness assertion expects all SC.W succeed | 已检查源码和预期；未运行 | none |
| E10 | Heliodor cache-line / memory-system 声明及 instruction-fetch design | design-doc | inspected | heliodor-master-20261012 | README.md:99–121, 134; icache.veryl:1–55 | not-run | README platform description | 64B I/D/L2 lines, coherent fetch and cache paths | 不适用于文档检查 | 已检查声明；不代表全部 memory agents/PMA mappings | none |
| E11 | Kunminghu fetch-boundary code and atomicity-evidence search | source | inspected | xiangshan-kunminghu-v2-20261012 | frontend/IFU.scala:529 and frontend fetch code; atomic-fetch/Ziccif term search over source, tests, scripts | not-run | 固定快照 | 跨页 32-bit instruction assembly path; search for profile-level fetch atomicity evidence | 只定位取指边界处理；未命中不能证明行为不存在 | 看到跨界实现代码；未找到适用 PMA 区域原子取指测试/平台说明 | none |

## 学习者总结

两套设计都可以沿着 decode、局部缓存/LSU 状态和测试配置追踪到有意义的实现线索。Kunminghu 的 MainPipe 展示按缓存块地址维护 LR/SC 窗口，Heliodor 把 reservation、提交年龄和缓存行 presence/invalidation 连接起来；两侧都提供了原子、非对齐和 CBO 路径线索。可复查材料仍不足以验证 profile 对 cacheability 与 coherence PMA 区域的系统级条件、全指令集合、取指原子性及进展保证。Heliodor 的 ACT README 提供历史测试报告，Story 4.6 本轮没有运行这些测试；因此所有覆盖映射均保持有限状态，不宣称符合性。

## 未解问题

- 两侧具体平台实现的 PMA 区域图及 coherence/cacheability 属性是什么？
- 哪些端到端测试能分别验证 32 位取指原子性、完整 A 操作集、RsrvEventual，以及 misaligned 访问在适用 PMA 区域内的行为？
- Heliodor `CACHE_BLOCK_SIZE=64` 与 RTL 的所有实例/系统代理参数是否一致？
- 两侧 CBO 权限、共享代理行为及 Zicbop 架构提示覆盖是否可由测试/实现材料逐项追踪？
