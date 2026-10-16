---
unit_id: "load"
stage_id: "阶段 3"
scope: "在 M-mode Bare、自然对齐、无异常、DCache hit 且不存在更老重叠 store 的前提下，追踪 RV64I `LD rd, imm(rs1)` 从有效地址、LSU 请求到 64 位寄存器结果和 ROB retirement；比较 Kunminghu V2 与 Heliodor 固定快照。"
exclusions:
  - "DCache miss/refill、replay、store-to-load forwarding、未对齐访问。"
  - "页表转换配置、PMP/PMA 拒绝、异常及非 Bare 特权状态。M-mode Bare 是案例前提，具体缓存与权限配置未从 sources.lock 验证。"
  - "不从单条 load 推断性能/周期、所有访存顺序行为或 RVA23 整体符合性。"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual, RV64I Base Integer Instruction Set"
    edition: "v20260120; RV64I version 2.1"
    section: "§3.1.3 Load and Store Instructions"
  - name: "RISC-V Unprivileged ISA Manual, RV32I Base Integer Instruction Set"
    edition: "v20260120; RV32I version 2.1"
    section: "§2.6 Load and Store Instructions"
version: 2
evidence_namespace: "LD2-E1–LD2-E15"
source_snapshots:
  - project: "Kunminghu V2"
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

## 单元自检

- **问题：** 这条 `LD` 如何从 `rs1 + imm` 得到 `rd` 并退休？源码检查和现有测试能证明哪些内容，哪些边界仍未验证？
- **学习者答案：** 架构上，`LD` 访问地址 `EA = x[rs1] + sign_extend(imm[11:0])`，把该地址的 64 位值写入 `rd`。自然对齐意味着 `EA[2:0]=0`。两侧已分别运行通过字节相同的冷加载 fixture（LD2-E19）：Kunminghu native commit trace 在 PC `0x80000008` 记录 `ld t1,0(t0)`，由已提交 x5 恢复 EA=`0x80000050`，观察到 x6=`0x123456789abcdef0`；Heliodor retirement port 在同一 PC 观察到一次 x6 写回及相同数据。后续 Heliodor 隔离探针还确认目标 PC safe hit（LD2-E20、E21）；Kunminghu 的 cache hit 仍未观察。两侧源码分别显示其 load、cache、ROB 和 architectural map 路径（LD2-E2–E15），`rat_arch` 由 `rob_commit_ack` 经 `rat_commit_en` 门控更新，`arch_regs` 调试镜像由 `rob_commit_valid` 门控更新，二者门控不同。同输入独立运行通过不证明同步或微架构等价。
- **检查类型：** explanation + source-location
- **证据 ID：** LD2-E1–LD2-E21；两侧共享镜像运行证据为 LD2-E19

## 架构行为与子案例

- **可观察行为：** 对 `LD rd, imm(rs1)`，有效地址为 `EA = x[rs1] + sign_extend(imm[11:0])`；RV64I `LD` 从 EA 读取 64 位值并写入 `rd`。本例再限定 EA 自然 8 字节对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store。规范规定可见结果，不规定本文两种微架构的内部流水线。
- **规范依据：** [RV64I §3.1.3，Unprivileged ISA v20260120](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html)；[RV32I §2.6，同版本](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html)。RV64I 章节建立在 RV32I 上并只列差异，需合读；RV64I 明确 `LD` 将 64 位内存值装入 `rd`。这不是 RVA23 整体符合性判断。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| `LD`, XLEN=64，EA[2:0]=0 | covered | 64 位加载语义由 LD2-E1 支持；实现数据路径见 LD2-E2–LD2-E11。 |
| Heliodor 目标 PC DCache safe hit | covered | 预热 fixture 在目标 PC 观察到 hit=1、miss=0（LD2-E21）；这是 DCache safe-hit 信号，不是原始 tag 比较。 |
| Kunminghu 目标 DCache hit、两边 M-mode Bare、无异常、无更老重叠 store | unconfirmed | Kunminghu 预热 fixture 的汇总计数没有 hit 事件，且无 PC 标签；权限/模式配置和旧 store 条件也未由运行记录完整确认。 |
| DCache miss/refill 与 replay | partially observed | Heliodor 冷加载目标 PC 观察到 fill-start 和 safe-hit（LD2-E20）；没有追踪 fill 完成、两者时序或 replay 延迟。 |
| 更老 store 重叠、forwarding、store-load 次序 | excluded | 无相关旧 store 是前提；不覆盖 forwarding 或内存顺序验证。 |
| 未对齐、地址转换、权限拒绝及异常 | excluded | 不从本案例推及这些子案例。 |

## Kunminghu 路径

- **阶段与状态变化：** 整数 load issue 用 `src(0) + SignExt(imm(11,0), VAddrBits)` 形成地址，并为 TLB 保留完整虚拟地址；请求标为读和 load queue index。DTLB 返回物理地址后，DCache 请求使用 `M_XRD`、地址、mask 与 LQ index。DCache load pipe 用物理 tag/权限判断 hit，读取 banked data；本例假定 hit，因此返回数据而不进入 miss/refill。load pipe 将 DCache 响应数据送入 `LoadUnit`，与本例不适用的转发通道合并后按地址偏移选取自然 dword，再由 `rdataHelper` 按操作宽度整理；`LD` 结果送到 `ldout.data`，随目的物理寄存器和 ROB 元数据进入后续写回。LoadQueue 连接接收 load 单元的 load 状态/数据记录（LD2-E6）。`Rob.scala` 由可提交头项形成 `commitValid`，在 `isCommit` 时退休；`RenameTableWrapper` 仅在 `isCommit && commitValid && rfWen` 时更新整数 architectural map（LD2-E14）。这些是固定源码描述的结构条件，未动态观察本例到达 ROB 头部或发生提交。
- **源码位置：** 有效地址、TLB 与 DCache 请求、DTLB 物理地址响应和 kill 条件 LD2-E2–LD2-E3；hit 判定、bank read 与响应数据 LD2-E4；load pipe 数据选择和 `ldout` LD2-E5；load queue 接线 LD2-E6。
- **相关验证：** LD2-E16、E19 通过锁定 Kunminghu runner 构建并运行独立 fixture；manifest 记录 commit trace、自检 marker、工具与二进制哈希。动态观察覆盖目标 `LD` 的提交 PC、机器码、有效地址、目的寄存器和数据。预热变体的汇总 DCache 计数报告 2 次 first-issue real miss、0 次 load hit，但计数没有 PC 标签（LD2-E22），因此目标 hit 仍未观察。

## Heliodor 路径

- **阶段与状态变化：** decoder 将 `LOAD` 解码为 base+立即数、memory writeback 和寄存器写使能。AGU 将 PRF `rs1` 与立即数相加；M-mode Bare 下 `dmem_mmu` 对地址直通。普通 load Stage A 在翻译/PMP 阶段结束后把 VA、PA、`pdst`、ROB index 和 funct3 锁存到 LSR 并从 IQ 接收；Stage B 独占 DCache 读端口。DCache 以有效位/tag 比较决定 hit，hit 时返回选中 cache data。LSU 将 `LD` 的 64 位 `ld_merged` 选为 `load_data_sel`，形成 CDB 数据；普通无异常非 FP load 经 CDB lane 1 写整数 PRF，并由 ROB 按 ROB index 记录结果和 `result_written`。之后 ROB 仅在 head 有效且 `result_written` 时拉高 `o_commit_valid`（core 信号 `rob_commit_valid`）；core 的 `rob_commit_ack` 才移除 head。`rat_arch` 由 `rat_commit_en`（由 `rob_commit_ack` 与 rd/合法性条件组合）门控更新；`arch_regs` 调试/cosim 镜像由 `rob_commit_valid` 与 rd/合法性条件门控更新（LD2-E15）。这些是源码可追踪的静态状态条件，不声称本案例动态运行到提交。
- **源码位置：** LOAD 译码、AGU 地址及两阶段请求/LSR LD2-E7–LD2-E8；Bare passthrough 与 hit/data LD2-E9；LSU 64-bit LD 选择/CDB、PRF 与 ROB 结果记录 LD2-E10–LD2-E11。
- **相关验证：** `test_arch_rv64ui_ld` 指向 RV64UI LD hex 并包含 pass assertion；该 suite 已由隔离 runner 运行并通过 `tohost/pass`（LD2-E17）。隔离 core 额外加入 PC 限定的 `dc_hit_safe`/`dc_miss_valid` 观察：冷加载在目标 PC 看到 miss 与 hit（LD2-E20），预热访问只看到 safe hit（LD2-E21）。预热 fixture 的 retirement 端口未捕获目标指令，但其 cache 请求 PC 与链接目标 PC 匹配，且 fixture 自检通过。`test_dcache` 源码包含同线 hit 场景，但不是核心完整 load 路径（LD2-E12–E13）。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边都从整数源与立即数形成 load 地址。Kunminghu fixture 动态观察到 `EA=0x80000040`；Heliodor suite 结果不暴露目标 `EA`。 | LD2-E2、LD2-E16 | LD2-E7、LD2-E17 |
| C2 | 在本案例的 Bare 假设下，地址到物理访存地址的路径分别经过 DTLB 响应和 Heliodor MMU 直通；两者最终都由 DCache 接收读请求。Bare 配置本身未运行验证。 | LD2-E3 | LD2-E8–LD2-E9 |
| C3 | Kunminghu 的目标 `LD` 动态写回 x6=`0x123456789abcdef0`；其 hit 未观察。Heliodor 冷加载退休值匹配，预热 fixture 自检通过且目标 PC safe hit 被观察到。 | LD2-E16、LD2-E19 | LD2-E18–LD2-E21 |
| C4 | Kunminghu native commit trace 在目标 PC 观察到该 `LD` 提交；Heliodor 冷加载 retirement 端口捕获目标指令；预热 fixture 只捕获到 PC 限定 cache 请求，未捕获退休记录。RAT 更新门控仍是静态源码证据。 | LD2-E14、LD2-E16 | LD2-E15、LD2-E18、LD2-E20–E21 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| LD2-E1 | 架构行为、自检 | spec | inspected | RISC-V Unprivileged ISA v20260120 | RV64I §3.1.3；RV32I §2.6；规范链接见上文 | not-run | 不适用 | 自然对齐 RV64I `LD` | 将 EA 处 64 位值写入 `rd` | 已检查规范章节；规范不规定微架构路径 | none |
| LD2-E2 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:383-423,625-645,693-718,736-745` | not-run | sources.lock 快照 | 整数 load issue | base+sign-extended imm 形成 VA，形成 load DCache 请求 | 源码显示地址、TLB 请求及 `M_XRD` 请求字段 | none |
| LD2-E3 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:903-960,1009-1017` | not-run | Bare 为案例假设；未运行配置 | TLB response 到 DCache | 使用返回 PA，异常/miss 会 kill DCache 请求 | 源码显示 PA 连接与 kill 条件；Bare 假设未观察 | none |
| LD2-E4 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/cache/dcache/loadpipe/LoadPipe.scala:179-199,304-317,328-355,417-423,452-479` | not-run | hit 为案例假设 | 自然对齐 load 的 DCache hit | 返回所选 cache 数据 | 源码有 hit、bank data response 和 resp 数据路径；未观察动态 hit | none |
| LD2-E5 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:1635-1645,1748-1809`; `src/main/scala/xiangshan/mem/MemBlock.scala:520-552`; `src/main/scala/xiangshan/XSCore.scala:169` | not-run | 无异常为案例假设 | DCache hit load response | 选择/格式化数据后以 `ldout.data`、pdest/ROB 元数据输出，再经 memory writeback 接口送入 backend | 源码显示 load 输出及连接；未观察动态写回 | none |
| LD2-E6 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/Bundles.scala:52-77,161-175`; `src/main/scala/xiangshan/mem/lsqueue/LoadQueue.scala:167,248-258` | not-run | 不适用 | load 单元送出的 load queue bundle | bundle 带有 load pipeline 的 uop、地址、data 和状态字段；LoadQueue 将其接入 VirtualLoadQueue | 检查到 bundle 定义与 `ldin` 接线；未运行 | none |
| LD2-E7 | C1 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/decoder.veryl:334-343`; `src/core/heliodor_core.veryl:5283-5293` | not-run | sources.lock 快照 | RV64I LOAD | decoder 选 base+imm；AGU 计算 EA | 源码显示 LOAD decode 与 AGU 求和 | none |
| LD2-E8 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:6410-6416,6644-6652,7406-7425,7895-7912` | not-run | M-mode Bare 为案例假设 | Stage A/Stage B plain load | Stage A 驱动转换请求；Bare 时地址直通；Stage B 锁存并读 cache | 源码注释和连线说明两阶段；未观察运行配置 | none |
| LD2-E9 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/mmu/dmem_mmu.veryl:1-5,212-232`; `src/cache/dcache.veryl:375-383,642-645,2624-2626` | not-run | Bare/hit 为案例假设 | PA load cache lookup | Bare passthrough；有效 tag hit 时 `o_rdata` 选缓存数据 | 源码描述直通、hit 判定和 hit data mux；未动态验证 | none |
| LD2-E10 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/lsu.veryl:64-106`; `src/core/heliodor_core.veryl:3292-3302,3365-3368` | not-run | 无异常、非 FP load 为案例 | `funct3=011` 的 LD 响应 | 64-bit `ld_d` 成为 load result 并输出 CDB | 源码选择 `ld_d=ld_merged` 并接 CDB 数据 | none |
| LD2-E11 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:7850-7855,7862-7874,4173-4181`; `src/core/rob.veryl:1416-1422` | not-run | 无异常为案例假设 | plain load 完成 | CDB lane 1 写 integer PRF；ROB 记录结果与完成状态 | 源码显示 lane mux、PRF 写端口和 ROB CDB2 记录 | none |
| LD2-E12 | Heliodor 相关验证 | test-inspected | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_arch_common.veryl:1173-1197` | not-run | 测试配置未确认；未检查 hex 文件内容 | RV64UI LD HEX harness | assertion 要求 pass | 只检查到 test entrypoint 配置指向 `rv64ui/ld.hex` 和 pass assertion；hex 内容未检查，测试未运行，不代表本案例通过 | none |
| LD2-E13 | Heliodor 相关验证 | test-inspected | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_dcache.veryl:117-165` | not-run | 单独 DCache 测试 | 冷 miss 后重读 hit、同 line hit、写后读 | 源码定义缓存测试输入/比较；不是核心 LD 端到端测试，未运行 | none |
| LD2-E14 | C4、自检 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/backend/rob/Rob.scala:785-801,839-846`; `src/main/scala/xiangshan/backend/rename/RenameTable.scala:151-160,260-265` | not-run | sources.lock 快照 | 已完成 load 结果位于可退休 ROB 项 | ROB 对可提交头项形成 `commitValid`，统计/标记 LOAD commit；commit 更新整数 architectural map | 静态源码条件已检查；无本例动态提交观察 | none |
| LD2-E15 | C4、自检 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/rob.veryl:560-571,1416-1422`; `src/core/heliodor_core.veryl:4062-4069,4416-4418,5179-5185`; `src/core/rat.veryl:177-190` | not-run | sources.lock 快照 | 已完成 load 结果位于 ROB head | head 有效且写回完成后产生 `rob_commit_valid`；`rob_commit_ack` 移除 head 并经 `rat_commit_en` 更新 architectural RAT；独立的 `arch_regs` 镜像由 `rob_commit_valid` 门控更新 | 静态源码条件已检查；无本例动态提交观察 | none |
| LD2-E16 | Kunminghu 单指令动态结果（先行 fixture） | test-run | run-pass | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | archived `input.S`; runner `experiments/kunminghu-smoke/run.py`; archived native trace and linker map | `python3 experiments/kunminghu-smoke/run.py --topic ld --timeout 120` | KunminghuV2Config，NUM_CORES=1，M-mode 初始状态 / SATP reset，NEMU difftest；DCache hit 未观察 | 单条 `ld t1,0(t0)`，EA=`0x80000040`，已知数据 `0x123456789abcdef0` | 目标 PC=`0x80000008` 的提交记录应是指令 `0x0002b303`，写 x6 为预期值；之后 fixture GOODTRAP | commit trace 匹配目标 PC/编码，x5 推得 EA=`0x80000040`，x6=`0x123456789abcdef0`，EA 八字节对齐，good trap 通过；cache hit 未观察 | `notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T075949Z-3e81181d1d02/` |
| LD2-E17 | Heliodor RV64UI LD suite 部分动态证据 | test-run | run-pass | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `experiments/heliodor-smoke/run.py --topic ld`; manifest run record | `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld --timeout 180` | 锁定 Veryl 0.22.0；隔离单 DUT `test_arch_rv64ui_ld` harness | locked `rv64ui/ld.hex` suite | `test_smoke` pass；LD suite `tohost=1/pass=1` 与 PASS marker | suite 级 pass；自身不暴露目标单条 LD 的退休 PC/rd | `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T055817Z-2342121/` |
| LD2-E18 | Heliodor 单条 LD 退休结果（先行 fixture） | test-run | run-pass | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | archived `ld-probe.S`; `run.py --topic ld-probe`; manifest run record | `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 180` | 锁定 Veryl 0.22.0；隔离普通 harness 从已有 debug retirement port 捕获目标 PC | 单条 `ld t1,0(t0)`，linked PC=`0x80000008`，预期 `rd=x6`, data=`0x123456789abcdef0` | 必须恰好一次目标 PC retirement、rd_valid=1、x6 数据匹配，并有 `tohost=1/pass=1` | 观察到 count=1, PC=`0x80000008`, rd=x6, data=`0x123456789abcdef0`; EA 与 cache hit 未观察 | `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T081240Z-4160381/` |
| LD2-E19 | 同一镜像的 Kunminghu/Heliodor 单条 LD 对照 | test-run | run-pass | Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`; Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `experiments/rv64-ld-probe/ld.S` + `fixture.ld`; 两侧 manifest run records | `python3 experiments/kunminghu-smoke/run.py --topic ld --timeout 120`；`PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 180` | 两个固定快照的单 DUT runner；输出镜像归一后逐字节相同 | 4104-byte binary SHA-256=`f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`；目标 PC=`0x80000008`，EA/data=`0x80000050` | Kunminghu commit 与 Heliodor retirement 均匹配 `rd=x6`, `0x123456789abcdef0`，各自终止自检通过 | 两侧 run-pass；Kunminghu 还观察 EA，Heliodor 观察 count=1/PC/rd/data；两侧 cache hit 未观察 | Kunminghu `notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T101307Z-3e81181d1d02/`；Heliodor `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T102111Z-1965619/` |
| LD2-E20 | Heliodor 冷加载目标 PC 的 DCache 事件观察 | test-run | run-pass | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | archived `heliodor_core.veryl`; manifest run record | `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --timeout 300` | 隔离 core，探针以 `lsr_pc_q == 0x80000008` 限定 | 共享冷加载 fixture，目标 `LD` PC=`0x80000008` | fixture pass；目标 retirement x6/data 匹配；记录 target PC 的 cache hit/miss 信号 | `req=1 hit=1 miss=1`；retirement count=1 且 data=`0x123456789abcdef0`。锁存信号只证明两类事件都出现，不编码先后顺序 | `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T104511Z-2457187/` |
| LD2-E21 | Heliodor 预热目标 PC safe-hit 观察 | test-run | run-pass | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `experiments/rv64-ld-probe/ld-hit-settled.S`; archived transformed core and manifest run record | `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic ld-probe --ld-probe-source experiments/rv64-ld-probe/ld-hit-settled.S --timeout 300` | 隔离 core，探针以 `lsr_pc_q == 0x80000030` 限定 | 先完成同地址预热读取，再执行被测 `LD` | 目标 PC request safe hit，未观察 fill-start；fixture 对加载值自检并通过 tohost/pass | `req=1 hit=1 miss=0`；target-PC retirement capture count=0，因此退休字段不作为此项结论依据 | `notes/units/evidence/smoke/heliodor-core-smoke-inputs/heliodor-core-20261016T104750Z-2510169/` |
| LD2-E22 | Kunminghu settled 预热 fixture 的聚合 cache 计数 | test-run | run-pass | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `experiments/kunminghu-smoke/run.py --ld-source`; manifest run record | `python3 experiments/kunminghu-smoke/run.py --topic ld --ld-source experiments/rv64-ld-probe/ld-hit-settled.S --timeout 180` | KunminghuV2Config 单 hart；两个同地址 LD，第二个为被测 target PC=`0x80000030` | settled 预热源，EA/data=`0x80000080`/`0x123456789abcdef0` | 目标 commit 与 fixture 自检通过；归档 L1 DCache/load-unit counters 供边界分析 | aggregate `real_miss_first_issue=2`, `load_hit=0`, `load_miss=4`, `load_replay=2`；无 PC 标签，不能据此标记目标请求 hit/miss | `notes/units/evidence/smoke/kunminghu-fixture-runs/kunminghu-fixture-20261016T105705Z-3e81181d1d02/` |

- `inspected` 表示源码/规范已检查，`unverified` 表示对应行为仍未验证。LD2-E19 是同一冷加载原始二进制分别在两侧运行的对照；LD2-E20/E21 是 Heliodor 独立冷加载/预热探针；LD2-E22 是 Kunminghu 预热变体。Heliodor safe hit 已按目标 PC 观察；Kunminghu 的聚合计数没有目标 PC，不能确定其目标请求状态，也没有跨实现的同状态 hit 对照。
- M-mode Bare、DCache hit、对齐和无旧重叠 store 是本案例边界，不是实验观察。源码局部证据不证明两边对 miss/refill、forwarding、未对齐访问、异常、地址转换配置或 RVA23 整体符合性。

## 学习者总结

`LD` 的架构结果是 EA 指向的完整 64 位值。两侧现已分别运行并通过同一 4104-byte 冷加载 binary（哈希见 LD2-E19），且目标 PC、rd=x6 与数据一致；Kunminghu trace 还观察到 EA。Heliodor 预热 fixture 的目标-PC 请求观察到 safe hit，冷加载则观察到 hit 与 fill-start。Kunminghu settled 变体的全局计数未记录 hit，且不带 PC，目标请求仍不能分类。两侧是在各自锁定环境中独立运行，不能替代同步或同一微架构配置下的等价证明。

## 未解问题

- Kunminghu 本例 EA、x6 值和目标提交已观察；DCache hit 与访问是否无异常仍不能从独立记录直接断言。
- Kunminghu DCache 计数目前是全局汇总；需要能按目标 PC 关联的运行时观察，才能确定 target LD 的 hit/miss，并与 Heliodor 对照。
- Heliodor 冷加载目标 retirement PC/rd/value 已观察；预热版本的 cache hit 已观察但其 retirement 端口未捕获目标事件。Heliodor 的动态有效地址仍未直接观测。
- 两边具体 M-mode/Bare、PMP/PMA 与 DCache 配置未由 sources.lock 固定；本文只将它们作为选定场景假设。
- 两侧同一镜像已独立运行通过；尚无同步双核执行或微架构等价性结论。
