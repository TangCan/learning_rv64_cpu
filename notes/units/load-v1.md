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
- **学习者答案：** 架构上，`LD` 访问地址 `EA = x[rs1] + sign_extend(imm[11:0])`，把该地址的 64 位内存值写入 `rd`。自然对齐意味着 `EA[2:0]=0`。Kunminghu 的整数 load issue 源计算 base 加符号扩展立即数，经 DTLB 响应物理地址后发 DCache 请求；hit 数据从 load pipe 返回，选出 64 位结果并写回 load 输出，load queue 同时记录状态（E2–E6）；源码还显示 ROB 可提交头项退休、commit 时更新整数 architectural map（E14）。Heliodor 从 PRF/立即数形成 AGU 地址，M-mode Bare 下 MMU 直通，再由 LSU Stage A 锁存、Stage B 发 DCache 读；hit 数据经 LSU 选择 `LD` 结果、CDB、PRF 和 ROB，head 完成并获 ack 后退休且更新 architectural state（E7–E11、E15）。这些都是固定源码的静态结构证据，没有动态观察本案例到达提交。Heliodor 有 RV64UI LD 测试入口及独立 DCache hit 测试源码，但本单元未运行；DCache 测试不等同于核心端到端指令测试（E12–E13）。缓存 hit、无重叠旧 store、Bare/权限配置均是案例假设，未由运行结果验证。
- **检查类型：** explanation + source-location
- **证据 ID：** E1–E15；未运行测试

## 架构行为与子案例

- **可观察行为：** 对 `LD rd, imm(rs1)`，有效地址为 `EA = x[rs1] + sign_extend(imm[11:0])`；RV64I `LD` 从 EA 读取 64 位值并写入 `rd`。本例再限定 EA 自然 8 字节对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store。规范规定可见结果，不规定本文两种微架构的内部流水线。
- **规范依据：** [RV64I §3.1.3，Unprivileged ISA v20260120](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html)；[RV32I §2.6，同版本](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html)。RV64I 章节建立在 RV32I 上并只列差异，需合读；RV64I 明确 `LD` 将 64 位内存值装入 `rd`。这不是 RVA23 整体符合性判断。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| `LD`, XLEN=64，EA[2:0]=0 | covered | 64 位加载语义由 E1 支持；实现数据路径见 E2–E11。 |
| M-mode Bare、DCache hit、无异常、无更老重叠 store | unconfirmed | 这是边界前提，不是本机运行观察；两边配置未由 sources.lock 固定。 |
| DCache miss/refill 与 replay | excluded | 本记录只描述 hit 返回路径，不推断 miss/refill。 |
| 更老 store 重叠、forwarding、store-load 次序 | excluded | 无相关旧 store 是前提；不覆盖 forwarding 或内存顺序验证。 |
| 未对齐、地址转换、权限拒绝及异常 | excluded | 不从本案例推及这些子案例。 |

## Kunminghu 路径

- **阶段与状态变化：** 整数 load issue 用 `src(0) + SignExt(imm(11,0), VAddrBits)` 形成地址，并为 TLB 保留完整虚拟地址；请求标为读和 load queue index。DTLB 返回物理地址后，DCache 请求使用 `M_XRD`、地址、mask 与 LQ index。DCache load pipe 用物理 tag/权限判断 hit，读取 banked data；本例假定 hit，因此返回数据而不进入 miss/refill。load pipe 将 DCache 响应数据送入 `LoadUnit`，与本例不适用的转发通道合并后按地址偏移选取自然 dword，再由 `rdataHelper` 按操作宽度整理；`LD` 结果送到 `ldout.data`，随目的物理寄存器和 ROB 元数据进入后续写回。LoadQueue 连接接收 load 单元的 load 状态/数据记录（E6）。`Rob.scala` 由可提交头项形成 `commitValid`，在 `isCommit` 时退休；`RenameTableWrapper` 仅在 `isCommit && commitValid && rfWen` 时更新整数 architectural map（E14）。这些是固定源码描述的结构条件，未动态观察本例到达 ROB 头部或发生提交。
- **源码位置：** 有效地址、TLB 与 DCache 请求、DTLB 物理地址响应和 kill 条件 E2–E3；hit 判定、bank read 与响应数据 E4；load pipe 数据选择和 `ldout` E5；load queue 接线 E6。
- **相关验证：** 没有运行 Kunminghu 构建、仿真或测试。该单元不把其他路径入口当作本案例的行为通过证据。

## Heliodor 路径

- **阶段与状态变化：** decoder 将 `LOAD` 解码为 base+立即数、memory writeback 和寄存器写使能。AGU 将 PRF `rs1` 与立即数相加；M-mode Bare 下 `dmem_mmu` 对地址直通。普通 load Stage A 在翻译/PMP 阶段结束后把 VA、PA、`pdst`、ROB index 和 funct3 锁存到 LSR 并从 IQ 接收；Stage B 独占 DCache 读端口。DCache 以有效位/tag 比较决定 hit，hit 时返回选中 cache data。LSU 将 `LD` 的 64 位 `ld_merged` 选为 `load_data_sel`，形成 CDB 数据；普通无异常非 FP load 经 CDB lane 1 写整数 PRF，并由 ROB 按 ROB index 记录结果和 `result_written`。之后 ROB 仅在 head 有效且 `result_written` 时拉高 `o_commit_valid`，core 的 commit ack 移除 head；commit 路径更新 `rat_arch` 和 architectural register mirror（E15）。这些是源码可追踪的静态状态条件，不声称本案例动态运行到提交。
- **源码位置：** LOAD 译码、AGU 地址及两阶段请求/LSR E7–E8；Bare passthrough 与 hit/data E9；LSU 64-bit LD 选择/CDB、PRF 与 ROB 结果记录 E10–E11。
- **相关验证：** `test_arch_rv64ui_ld` 指向 RV64UI LD hex 并包含 pass assertion；`test_dcache` 源码包含同线 hit 场景。这里只检查测试源码，未运行；DCache 单元测试不覆盖核心完整 load 路径（E12–E13）。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边都从整数源与立即数形成 load 地址，并在 load 路径中携带目的寄存器及操作身份；本单元未观察某个动态 `EA`。 | E2 | E7 |
| C2 | 在本案例的 Bare 假设下，地址到物理访存地址的路径分别经过 DTLB 响应和 Heliodor MMU 直通；两者最终都由 DCache 接收读请求。Bare 配置本身未运行验证。 | E3 | E8–E9 |
| C3 | hit 数据都被整理为 `LD` 的 64 位结果并关联写回身份；Kunminghu 经 load pipe 输出，Heliodor 经 LSU CDB lane/PRF/ROB 记录。 | E4–E6 | E10–E11 |
| C5 | 两边源码都给出 load 结果到 ROB retirement 的条件路径及架构映射更新；这些是静态结构证据，不是本案例动态到达提交的观察。 | E14 | E15 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 架构行为、自检 | spec | inspected | RISC-V Unprivileged ISA v20260120 | RV64I §3.1.3；RV32I §2.6；规范链接见上文 | not-run | 不适用 | 自然对齐 RV64I `LD` | 将 EA 处 64 位值写入 `rd` | 已检查规范章节；规范不规定微架构路径 | none |
| E2 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:383-423,625-645,693-718,736-745` | not-run | sources.lock 快照 | 整数 load issue | base+sign-extended imm 形成 VA，形成 load DCache 请求 | 源码显示地址、TLB 请求及 `M_XRD` 请求字段 | none |
| E3 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:903-960,1009-1017` | not-run | Bare 为案例假设；未运行配置 | TLB response 到 DCache | 使用返回 PA，异常/miss 会 kill DCache 请求 | 源码显示 PA 连接与 kill 条件；Bare 假设未观察 | none |
| E4 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/cache/dcache/loadpipe/LoadPipe.scala:179-199,304-317,328-355,417-423,452-479` | not-run | hit 为案例假设 | 自然对齐 load 的 DCache hit | 返回所选 cache 数据 | 源码有 hit、bank data response 和 resp 数据路径；未观察动态 hit | none |
| E5 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/pipeline/LoadUnit.scala:1635-1645,1748-1809` | not-run | 无异常为案例假设 | DCache hit load response | 选择/格式化数据后以 `ldout.data`、pdest/ROB 元数据输出 | 源码显示合并/偏移选择和 load writeback 输出 | none |
| E6 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/mem/lsqueue/LoadQueue.scala:248-258` | not-run | 不适用 | load 单元返回状态 | LoadQueue 接收 load 状态/数据流 | 检查到 VirtualLoadQueue `ldin` 接线；未运行 | none |
| E7 | C1 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/decoder.veryl:334-343`; `src/core/heliodor_core.veryl:5283-5293` | not-run | sources.lock 快照 | RV64I LOAD | decoder 选 base+imm；AGU 计算 EA | 源码显示 LOAD decode 与 AGU 求和 | none |
| E8 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:6410-6416,6644-6652,7406-7425,7895-7912` | not-run | M-mode Bare 为案例假设 | Stage A/Stage B plain load | Stage A 驱动转换请求；Bare 时地址直通；Stage B 锁存并读 cache | 源码注释和连线说明两阶段；未观察运行配置 | none |
| E9 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/mmu/dmem_mmu.veryl:1-5,212-232`; `src/cache/dcache.veryl:375-383,642-645,2624-2626` | not-run | Bare/hit 为案例假设 | PA load cache lookup | Bare passthrough；有效 tag hit 时 `o_rdata` 选缓存数据 | 源码描述直通、hit 判定和 hit data mux；未动态验证 | none |
| E10 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/lsu.veryl:64-106`; `src/core/heliodor_core.veryl:3292-3302,3365-3368` | not-run | 无异常、非 FP load 为案例 | `funct3=011` 的 LD 响应 | 64-bit `ld_d` 成为 load result 并输出 CDB | 源码选择 `ld_d=ld_merged` 并接 CDB 数据 | none |
| E11 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:7850-7855,7862-7874,4173-4181`; `src/core/rob.veryl:1416-1422` | not-run | 无异常为案例假设 | plain load 完成 | CDB lane 1 写 integer PRF；ROB 记录结果与完成状态 | 源码显示 lane mux、PRF 写端口和 ROB CDB2 记录 | none |
| E12 | Heliodor 相关验证 | test-inspected | unverified | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_arch_common.veryl:1173-1197` | not-run | 测试配置未确认 | RV64UI LD HEX harness | assertion 要求 pass | 只检查到 test entrypoint 和 assertion；未运行，不代表本案例通过 | none |
| E13 | Heliodor 相关验证 | test-inspected | unverified | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_dcache.veryl:117-165` | not-run | 单独 DCache 测试 | 冷 miss 后重读 hit、同 line hit、写后读 | 源码定义缓存测试输入/比较；不是核心 LD 端到端测试，未运行 | none |
| E14 | C5、自检 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/backend/rob/Rob.scala:785-801,839-846`; `src/main/scala/xiangshan/backend/rename/RenameTable.scala:151-160,260-265` | not-run | sources.lock 快照 | 已完成 load 结果位于可退休 ROB 项 | ROB 对可提交头项形成 `commitValid`，统计/标记 LOAD commit；commit 更新整数 architectural map | 静态源码条件已检查；无本例动态提交观察 | none |
| E15 | C5、自检 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/rob.veryl:560-571,1308-1314,1416-1422,1523-1532`; `src/core/heliodor_core.veryl:4062-4068,4416-4420,5173-5195`; `src/core/rat.veryl:177-190` | not-run | sources.lock 快照 | 已完成 load 结果位于 ROB head | head 有效且写回完成后允许 commit ack；ack 移除 head 并更新 architectural RAT/register mirror | 静态源码条件已检查；无本例动态提交观察 | none |

- `inspected` 表示源码/规范已检查，`unverified` 表示测试未执行；没有 `test-run`、`run-pass` 或 `run-fail` 证据。没有构建、仿真或测试运行命令及运行产物。
- M-mode Bare、DCache hit、对齐和无旧重叠 store 是本案例边界，不是实验观察。源码局部证据不证明两边对 miss/refill、forwarding、未对齐访问、异常、地址转换配置或 RVA23 整体符合性。

## 学习者总结

`LD` 的架构结果是 EA 指向的完整 64 位值；本案例限定自然对齐、Bare、DCache hit、无异常和无更老重叠 store。Kunminghu 从 load issue 形成地址，接收 DTLB 返回的物理地址并发起 DCache 读，hit 数据经 load pipe 格式化后输出写回；ROB 可提交头项时退休，commit 更新整数 architectural map。Heliodor 先由 AGU 计算地址，M-mode Bare 下 MMU 直通，plain load 经 Stage A/Stage B 到 DCache，再由 LSU 选出 `ld_d`、发送 CDB 并记录到 PRF/ROB；head 完成且得到 ack 后退休，commit 路径更新 `rat_arch` 和寄存器镜像。两边 retirement 路径都是源码所示的静态结构，没有动态观察本案例实际提交。Heliodor 的相关测试只有源码检查证据，没有运行结果；缓存命中和权限/转换配置仍是未验证前提。

## 未解问题

- 两个实现中本例的实际 EA、命中数据、最终 `rd` 值和提交结果均未运行观察。
- 两边具体 M-mode/Bare、PMP/PMA 与 DCache 配置未由 sources.lock 固定；本文只将它们作为选定场景假设。
- Kunminghu 与 Heliodor 在同一端到端 `LD` 输入上的动态测试/仿真未执行。
