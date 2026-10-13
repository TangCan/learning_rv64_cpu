---
title: 'RV64 CPU 学习最终结项所需未调查 RVA23S64 项的技术调研'
type: technical
topic: 'RV64 CPU 学习最终结项所需的未调查 RVA23S64 项'
decision: '如何安排并验收剩余调查与验证，使双实现学习达到可审计的整体结项标准'
source: native web research + pinned upstream snapshots
status: complete
preset: standard
validation: normal
created: '2026-10-13'
updated: '2026-10-13'
claims_verified: 8
claims_unverified: 2
---

# RV64 CPU 学习最终结项计划

**决策：** 用一组有限、可追溯的学习单元关闭 RVA23S64 中尚未调查的主题；先解决源码活动配置和测试可用性，再追踪规范行为、两边实现与验证结果。结项代表学习目标和证据记录完整，不代表两颗上游 CPU 均符合 RVA23，也不等于官方认证。

## 执行摘要

RVA23S64 明确要求 Zifencei、Sstc、Sscofpmf、Ssnpm，并通过 Sha 要求 `sstateen0–3` 和 `hstateen0–3`。这是规范学习范围，不是对任何一个实现的支持结论。[1][2]

固定的两份源码快照显示，工作不必从零开始：Heliodor 有 FENCE.I、Sstc、Sscofpmf 和 Supm/Ssnpm 的源码及定向测试入口；Kunminghu 的 NewCSR 源码中也能找到 Sstc、Sscofpmf、PMM 和 stateen 路径。但静态代码和测试文件都不是运行通过的证据；Kunminghu 还存在新旧 CSR 路径并行，需先确认配置实际选用哪条路径。[12][13][14]

ACT4/CTP 可作为架构测试入口：其 profile matrix 列出这些测试套件，但 CTP 当前是草案；ACT 文档也明确其不是完整的处理器验证。特别是 Sscofpmf 测试仍有依赖 Sail 支持的在途工作。因此先盘点 suite/coverpoint 的完成状态，选择可运行案例，再用设计自己的定向测试补缺。[8][9][10]

建议新增 **Epic 5：完成 RVA23S64 未调查主题的双核学习与证据闭环**，拆成 5 个比较单元：Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen。前四个每份记录均比较 Kunminghu 与 Heliodor；Ssstateen 同样调查两侧，其中 Heliodor 作为待确认的潜在实现空缺处理。按约 20–28 个 60–90 分钟学习时段估算；若建立/修复仿真环境遇到工具链障碍，需另行调整时间。

## 研究发现

### 1. 必选范围和要检查的架构行为

| 主题 | 必须掌握的行为 | 学习记录应覆盖的案例 |
| --- | --- | --- |
| Zifencei | `FENCE.I` 使同一 hart 在此之前可见的数据存储，对此后取指可见；它本身不保证其他 hart 的取指可见。未使用字段需符合规范忽略规则。[2][3] | 对指令内存做写入、执行 `FENCE.I`、确认后续取到新指令；检查保留字段；如做多 hart 案例，写 hart 和执行 hart 的协调机制必须分别说明。 |
| Sstc | S-mode `stimecmp` 和 VS-mode `vstimecmp` 形成计时器中断；`menvcfg.STCE` / `henvcfg.STCE` 控制相应 CSR 可访问性和中断来源。[4] | `time < stimecmp`、`==`、`>`；STCE 关闭时访问陷阱及 pending 行为；STCE 打开后的委托/可见性；VS 时间偏移和 `henvcfg.STCE`。 |
| Sscofpmf | `mhpmevent` 的 OF 与模式抑制位、硬件计数溢出、LCOFI bit 13、`scountovf` 只读状态及访问门控共同构成要求。[5] | 仅硬件递增溢出、OF 置位/清除与重新 arm；MINH/SINH/UINH/VSINH/VUINH；`scountovf` 与 `mcounteren`/`hcounteren`；LCOFIP/LCOFIE、委托和异常 cause。 |
| Ssnpm | RVA23 profile PDF 将控制项写为 `senvcfg.PME` / `henvcfg.PME`，而 Pointer Masking 扩展规范及两份源码使用 `PMM` 字段名；需先核对这一命名差异，再确认至少支持 PMLEN=0 和 PMLEN=7。[1][6] | 掩码启用/关闭时的 U/VU 指针地址变换；S/HS 配置与 guest 配置控制关系；规范列出的 load/store、原子、浮点、压缩、cache、vector 和 hypervisor 显式内存访问类别中，本快照实现支持的子集；PMLEN 边界及异常地址。 |
| Ssstateen | Sha 要求提供 `sstateen0–3` 与 `hstateen0–3`；state-enable 还决定较低特权态访问扩展状态时的门控和陷阱。[1][7] | CSR 存在/读写、WARL/只读零规则、reset 值；M→S/HS→VS/VU 的门控与异常类型；若 Heliodor 确无实现，完整记录检索范围和“未实现/未发现”的证据边界。 |

### 2. 固定源码快照的实现和测试线索

- **Heliodor (`94e9c5821c24a8941c3ddc3b76daddc7124a855a`)：** README 声明 Zifencei、Sstc、Sscofpmf 和 Supm/Ssnpm；`tb/test_arch_common.veryl` 有 FENCE.I、Sstc、Sscofpmf 和 pointer-masking 定向测试，且 `test/sstc`、`test/sscofpmf`、`test/supm` 下有独立汇编测试。[14] 这些是已检查的实现/测试入口，不是本机运行记录。对 Ssstateen 的固定快照仓库搜索只找到 ACT Sail 配置中的名字，未找到 RTL CSR 路径；仍应先检查通用 CSR decode/别名后，才可下“未实现”结论。[15]
- **Kunminghu V2 (`c098f996bf4d301b88693b20315486d31e93bc9d`)：** NewCSR 路径有 `stimecmp`/`vstimecmp` 和定时器生成器、`scountovf` 与溢出/过滤逻辑、PMM 到 TLB 的路径，以及 stateen CSR 和访问权限代码。[12][13] 但树中同时保留旧 CSR 实现；例如一处旧路径仍带有 Sstc TODO。每个主题在写结论前必须沿 `wrapper/CSR` 与配置追到活动实现，不能把目录中存在 NewCSR 代码当作该配置实际启用它的证明。[12]
- **测试资源：** ACT4 CTP matrix 已列 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen 等 RVA23S64 案例/套件；这是测试计划证据而非目标核通过证据。ACT4 生成 ELF 后仍需 DUT 自己的 testbench/config 执行，ACT 也不替代微架构验证。[8][9] 公开 issue 中 Sscofpmf 测试工作仍标注需要 Sail 支持；另一份 ACT4 review issue 报告了 Ssstateen 测试生成器/coverpoint 问题。因此运行前要核对分支、coverpoint、生成的测试和预期陷阱，不能只依据 suite 名称推断覆盖质量。[10][11]

### 3. 核心建议与信心

1. **新增五个学习单元，不先改上游 RTL。** 每个单元的结论允许是“实现并已运行验证”“源码有实现线索但尚未运行”“未实现/证据不足”。对学习型项目，准确识别缺口也能完成学习目标；不得把缺口改写成通过。[1][9] **信心：高**（规范和仓库入口明确；对结果保持待验证）。
2. **先做 Kunminghu 活动配置辨析和 ACT4 成熟度检查。** 这是动态验证范围与学习计划工期的主要不确定因素。[8][10][12] **信心：高**。
3. **分层使用验证证据：** 规范逐条矩阵 → 静态源码跟踪 → 上游已有定向测试 → 可用 ACT4 子集 → 缺口定向仿真。报告逐项标明实际运行与否。ACT 通过不能被描述为完整微架构验证或认证。[8][9] **信心：高**。
4. **Ssnpm 与 Ssstateen 设为风险最高的两个单元。** 前者需确定两份快照对 pointer-masking 名称、字段和实际地址路径的映射；后者的 Heliodor RTL 线索目前没有找到，且 state-enable 正确性依赖特权组合而非 CSR 名称。[6][7][15] **信心：中**（静态搜索有边界；需按计划复核）。

## 建议的后续 Epic 5 计划

### Epic 目标

完成 RVA23S64 未调查主题的双实现学习记录，让每条结论能回到固定规范、两个源快照以及明确的测试/验证证据；将上游没有实现或当前无法运行验证的地方作为明示结果保留。

### 前置门：Epic 5 开始前

1. 再次核对 `sources.lock` 两个 SHA 不变；若更新，建立新 snapshot event，并明确新旧记录不可直接混比的部分。
2. 从官方 RVA23 profile 和 ratified ISA library 建立五个扩展的 requirement-to-case 表；记录标准版本、条款、配置条件和排除项。[1]–[7]
3. Kunminghu：从 Kunminghu V2 配置一路追踪到 active CSR module，记录是否选用 NewCSR；对 Sstc TODO 与 NewCSR 实现并存建立差异说明。[12]
4. Heliodor：核验每个已有 test entry 的 Makefile、编译器、testbench、预期输出和参数；逐个确认 Ssstateen 的全树搜寻、CSR decode 和实际行为路径。[14][15]
5. 再探测两项目运行所需的 Veryl、Mill/Java、RISC-V GCC、ACT4、Sail、UDB/Ruby 版本；将安装步骤和工具版本记入运行证据，不在上游 checkout 修改源文件。

**前置门通过条件：** 需求表覆盖 profile 强制行为；两个实现的活动路径已确定或标为“未知/配置阻塞”；测试计划明确区分已有测试与拟新增测试；依赖工具的版本/阻塞有记录。

### Story 5.1：比较 Zifencei 与 FENCE.I

- **源码追踪：** 两侧从 decode 到 commit/serialization，再到 fetch pipeline/I-cache/cache-coherence；说明每边同步机制和单 hart 边界。[2][3][12][14]
- **验证：** 先尝试 Heliodor 的 `test_arch_rv64ui_fence_i` 和同仓已有 testbench；核查 Kunminghu 是否有可匹配的架构测试。补一个写入代码→FENCE.I→执行新代码的短程序，并单独记录未用编码字段行为；多 hart 案例要求正确区分 local FENCE.I 与远端 I-cache 同步。
- **验收：** 记录精确规范行为，两边路径、微架构差异；测试命令/配置/观察值可复现；未实现/未运行情况逐项标记，不把静态路径写成运行通过。
- **预计：** 2–3 个时段。

### Story 5.2：比较 Sstc 和 S/VS timer

- **源码追踪：** `stimecmp`/`vstimecmp` 状态、STCE gates、`time`/`htimedelta` 选择、STIP/VSTIP 生成、CSR 权限与陷阱/委托。[4][12][14]
- **验证：** 复用 Heliodor Sstc/VS Sstc 测试；Kunminghu 若无同类测试则建立定向仿真。用 `time` 边界三值测试比较器，验证 menvcfg/henvcfg gates、访问异常、S/VS delivery 和 guest time offset；记录中断到达的时序允许范围。
- **验收：** S-mode 与 VS-mode 子案例分别闭合；测试通过/失败/受阻均有日志和源码快照；明确与 M-mode timer 的区别。
- **预计：** 3–4 个时段。

### Story 5.3：比较 Sscofpmf 计数溢出和模式过滤

- **源码追踪：** HPM event/counter 更新、OF sticky state、模式 inhibit 位、`scountovf` read mask、local interrupt pending/enable/delegation。[5][12][14]
- **验证：** 先运行 Heliodor `test/sscofpmf` 与/或 testbench 定向块；检查 ACT4 Sscofpmf suite/SAIL 是否已可用。针对一枚 counter 构造最小 overflow，然后逐项测 OF 清除/重 arm、counter enable、S/U/VS/VU 过滤和 LCOFI delivery。使用小计数宽度或可控 preload 避免长运行；不得把软件写 counter 造成的 wrap 当硬件 overflow。[5][10]
- **验收：** 五个模式 inhibit 位、OF/scountovf、IRQ/delegation/access gating 至少有静态路径或动态结果逐条对照；ACT 依赖未满足时明确记录并保留定向测试证据。
- **预计：** 4–5 个时段。

### Story 5.4：比较 Ssnpm 指针屏蔽

- **源码追踪：** 对照 profile PDF 的 PME 写法与 Pointer Masking 规范、源码中的 PMM 字段名；核对 PMLEN 选择及地址变换进入 LSU/MMU 的位置，并分清 Ssnpm 与机器/监督模式其他 pointer-masking 组成。[1][6][12][14]
- **验证：** 先做名称/版本对照，避免把 Supm、Smnpm/Smmpm 与 Ssnpm 混同。复用 Heliodor `test/supm` 与 testbench；Kunminghu 需确认配置支持及用例入口。针对 PMLEN=0、7、关闭/开启及地址标签进行 load/store；逐步加入 atomics、压缩访问、vector 和 HLV/HSV 等规范规定或本实现支持的类别。按 Pointer Masking 规范检查 `senvcfg.PMM`、`henvcfg.PMM` 的读写及 U/VS 状态，同时记录它们与 profile PDF 中 PME 写法的对应关系；不能以某条普通 load 通过替代整个规定访问类型清单。[1][6]
- **验收：** 需求矩阵覆盖最小 PMLEN、控制状态、模式、内存指令类别、异常/地址变换；所有未测试类别明确列出并解释本轮是否影响结项。
- **预计：** 4–6 个时段。

### Story 5.5：比较 Ssstateen，确认 Heliodor 状态

- **源码追踪：** 两侧 `sstateen0–3` / `hstateen0–3` 声明、读写表、state enable bit mapping、CSR access permit/trap；追踪 M/H/S/VS/VU gate 的 precedence。[1][7][12][15]
- **验证：** 分层测试存在性、reset/WARL/RO-zero，再选择一个有定义的受控状态比特验证“允许访问”和“阻止访问”的陷阱；分别检查 M 清除、H 清除、S stateen 清除的路径，记录异常 cause。若 Heliodor 源码确无实现，增加最小 CSR 地址访问实验确认 trap/result，给出 bounded search 和实验；记录其为实现缺口，不在本项目中补核心功能。
- **验收：** Kunminghu 活动路径的四个 S/H CSR 有证据；Heliodor 结论基于全仓库搜索加 decode/行为证据；profile mapping、测试覆盖与“实现状态”不混为一谈。
- **预计：** 3–4 个时段。

### 汇总 Story 5.6：RVA23S64 结项审计

1. 逐项更新 coverage 表的学习/证据状态，并对 5 个主题与各子案例建立证据链接。
2. 只要仍有 not-studied 子案例，写明是否留作后续学习以及为何不阻碍本轮结项；不得通过改状态消除未知。
3. 检查每份学习单元：双侧 snapshot、规范版本、源码链路、差异、自检答案、测试证据/边界、未解问题均存在。
4. 运行 coverage checker、两类文档/索引链接检查和 sprint validator；记录工具版本与实际输出。
5. 做一次 Epic retrospective，决定本轮目标“学习完成”的 acceptance 是否满足，并记录被接受的残余限制。

**Epic 5 的整体 Done 条件：** 五个比较单元都完成；RVA23S64 这五个扩展在两侧均有明确状态；每项结果均有规范和源码依据；计划内的可运行案例已运行或有具体阻塞证据；Heliodor Ssstateen 以实现/缺失/待确认之一结论闭环；coverage summary 与 evidence links 校验通过；没有把结果表述为 CPU 获得 RVA23 认证。

## 排序、估算和质量门

| 顺序 | 工作块 | 依赖 | 估算（60–90 分钟时段） | 退出门 |
| --- | --- | --- | ---: | --- |
| 准备 | 前置门：规范矩阵、active CSR、工具/测试可用性 | 无 | 2–3 | 每个需求都知道查哪条路径和哪类证据 |
| Story 5.1 | Zifencei | 前置门 | 2–3 | 单 hart 行为和跨 hart 边界解释清楚 |
| Story 5.2 | Sstc | 前置门；复用中断/特权知识 | 3–4 | S/VS timer、gate、delivery 逐项有证据 |
| Story 5.3 | Sscofpmf | 前置门；需要 HPM/中断 harness | 4–5 | OF/filter/scountovf/LCOFI 形成小矩阵 |
| Story 5.4 | Ssnpm | 前置门；先统一术语与配置 | 4–6 | PMM 0/7 与必需访问类别有明确结果 |
| Story 5.5 | Ssstateen | 前置门；先确定活动 CSR 和 H 模式 | 3–4 | S/H CSR 及权限路径；Heliodor 结论有边界 |
| 收尾 | 最终审计与复盘 | 五个单元完成 | 2–3 | coverage/doc/sprint 审计通过，retrospective 接受 |
| **合计** |  |  | **20–28** | 约 20–42 小时；不含工具链安装和超出计划的环境排障 |

Ssnpm 与 Sscofpmf 各自的硬件语义和环境依赖最多，故安排在 timer 基础之后；Ssstateen 依赖虚拟化特权路径，因此后置。若用户更重视快速先得到闭环，可将 Ssstateen 的有界搜寻提前到 Sstc 之后，以尽早确认 Heliodor 的潜在 profile 差距；其余测试和审计条件不变。

### 主要风险与缓解

| 风险 | 影响 | 缓解 |
| --- | --- | --- |
| Kunminghu 新旧 CSR 实现并存 | 可能沿错误路径学习或验证 | 每个单元先从配置/wrapper 追到活动 module，再选 test target。[12] |
| ACT4 test plan/SAIL 未完整支持某扩展 | suite 缺覆盖或无法生成 | 锁定 ACT4/Sail 版本，核验具体 suite 与 coverpoints；独立 directed test 补缺。[8][10] |
| Heliodor Ssstateen 可能未实现 | 不能按普通支持特性比较 | 用受控 CSR 访问确认，结果可作为准确缺口；不为完成计划而改上游 CPU。[7][15] |
| Ssnpm 跨多类 memory operations | 把一条 load 成功误读为完整覆盖 | 按规范 operation-family checklist，分类记录已测/未测。[6] |
| 工具链和配置随快照变化 | 测试命令复现失败、报告失真 | 每次运行写下 SHA、工具版本、命令、参数、预期/实际、trace/log 位置。 |

## 来源与置信度说明

实现证据固定到项目锁定的两个上游 SHA。标准版本以 RISC-V International 公开规格为准。ACT/CTP 是辅助测试计划；它对架构行为有用，但不是微架构验证替代物。所有本轮源代码搜索均为静态检查，没有重新运行任何 CPU 测试或构建。该区别是结项时不可消除的证据边界。

## 开放问题

1. Kunminghu V2 的具体测试配置是否实例化了 NewCSR，且以何种参数启用 Sstc、PMM、HPM 和 stateen？需要从选定 target 的生成配置与构建路径确认。
2. ACT4 当前分支的每个相关 suite 是否都有完整可生成的测试，以及 Sscofpmf 所需 Sail 实现何时就绪？需在计划启动时重新核查。[8][10]
3. Heliodor 是否有未使用 `sstateen` 字符串的通用 CSR decode/别名行为？固定快照搜索未找到明显 RTL 名称，但应以行为测试结论关闭。[15]
4. 动态验证能覆盖多少案例取决于工具链及两边现有 testbench；若新 harness 超出本计划范围，应作为单独故事而不是降低学习记录验收标准。

## 来源附录

| 编号 | 支持的结论 | Publisher | Pub date/version | Accessed | Confidence |
| --- | --- | --- | --- | --- | --- |
| [1] | RVA23S64 profile requirements and Sha bundle | [RISC-V International RVA23 Profile](https://docs.riscv.org/reference/rva23/_attachments/rva23-profile.pdf) | v1.0, ratified; page does not expose a publication date | 2026-10-13 | High |
| [2] | Current official ISA library and Zifencei 2.0 semantics | [RISC-V Ratified Specifications Library](https://docs.riscv.org/reference/isa/v20260120/unpriv/zifencei.html) | release v20260120; Zifencei v2.0 | 2026-01-20 | High |
| [3] | Zifencei local-hart and reserved-field behavior | [RISC-V Zifencei specification](https://docs.riscv.org/reference/isa/unpriv/zifencei.html) | v2.0; current ratified ISA library | not displayed | High |
| [4] | Sstc compare, enable gates, and timer interrupt semantics | [RISC-V Sstc specification](https://docs.riscv.org/reference/isa/v20260120/priv/sstc.html) | v1.0.0; library release v20260120 | 2026-01-20 | High |
| [5] | Sscofpmf overflow, filtering, scountovf, and LCOFI semantics | [RISC-V Sscofpmf specification](https://docs.riscv.org/reference/isa/v20260120/priv/sscofpmf.html) | v1.0; library release v20260120 | 2026-01-20 | High |
| [6] | Ratified pointer-masking operations and PMM modes | [RISC-V Pointer Masking specification](https://docs.riscv.org/reference/isa/v20260120/priv/zpm.html) | v1.0.0; library release v20260120 | 2026-01-20 | High |
| [7] | Smstateen/Ssstateen CSR hierarchy and access control | [RISC-V Smstateen/Ssstateen specification](https://docs.riscv.org/reference/isa/v20260120/priv/smstateen.html) | v1.0; library release v20260120 | 2026-01-20 | High |
| [8] | RVA23S64 test-plan suites and coverage matrix | [RISC-V Certification Test Plan](https://riscv.github.io/riscv-arch-test/ctp.html) | CTP v0.0.0 draft, dated 2026-10-12 | 2026-10-13 | High for planned suites; medium for maturity |
| [9] | ACT purpose, limitations, configuration, Sail and DUT testbench workflow | [riscv-arch-test README](https://github.com/riscv/riscv-arch-test) | ACT4 current repository docs; README reports Sail 0.15 support | 2026-10-13 | High |
| [10] | Sscofpmf test development dependency/status | [riscv-arch-test issue #2181](https://github.com/riscv/riscv-arch-test/issues/2181) | opened 2026-08-24; updated 2026-10-12 | 2026-10-13 | Medium |
| [11] | Reported ACT4 Ssstateen suite generator/coverpoint concerns | [riscv-arch-test issue #2146](https://github.com/riscv/riscv-arch-test/issues/2146) | opened 2026-08-20; still a report, not an official disposition | 2026-10-13 | Medium |
| [12] | Kunminghu NewCSR wrapper and legacy CSR coexistence | [CSR wrapper](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/wrapper/CSR.scala), [legacy CSR](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/CSR.scala) | pinned source SHA, 2026-10-12 | 2026-10-13 | High for code presence; active feature config remains to trace |
| [13] | Kunminghu timer, PMM, HPM, and stateen RTL leads | [Sstc generator](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/NewCSR/SstcInterruptGen.scala), [NewCSR](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala), [CSR bundles](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/NewCSR/CSRBundles.scala), [state-enable bundle](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/NewCSR/StateEnBundle.scala), [hypervisor CSR](https://github.com/OpenXiangShan/XiangShan/blob/c098f996bf4d301b88693b20315486d31e93bc9d/src/main/scala/xiangshan/backend/fu/NewCSR/HypervisorLevel.scala) | pinned source SHA, 2026-10-12 | 2026-10-13 | High for static paths |
| [14] | Heliodor README, CSR/address paths, and directed test entries | [README](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/README.md), [CSR](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/src/core/csr.veryl), [address path](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/src/core/alu_wrap.veryl), [directed testbench](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/tb/test_arch_common.veryl), [Sstc test](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/test/sstc/sstc_test.S), [Sscofpmf test](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/test/sscofpmf/sscofpmf_test.S), [pointer-masking test](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/test/supm/supm_test.S) | pinned source SHA, 2026-10-12 | 2026-10-13 | High for files/tests present; no run evidence |
| [15] | Bounded Heliodor Ssstateen source search | [Heliodor CSR decode/state source](https://github.com/dalance/heliodor/blob/94e9c5821c24a8941c3ddc3b76daddc7124a855a/src/core/csr.veryl) | pinned source SHA, 2026-10-12 | 2026-10-13 | Medium; full-tree text search is documented in this report, and absence of a symbol is not by itself proof |

## Staleness map

Recheck time-sensitive source status before starting Epic 5. Ratified semantic requirements are versioned and stable, but the latest library release and test-framework/Sail compatibility can change. The generated staleness map is based on six ledger claims and freshness windows of one month for versions/compatibility and six months for ecosystem status. It reports **1 stale claim** and an earliest check date of **2026-02-20**, already elapsed for the 2026-01-20 ISA library release; reconfirm whether `v20260120` remains current before executing tests. Revisit ACT4 suite readiness by **2026-11-12** because the CTP/test-framework version is actively changing.
