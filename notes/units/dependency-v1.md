---
unit_id: "dependency"
stage_id: "阶段 2"
scope: "追踪 RV64I 两条相邻整数 ADDI 的寄存器 RAW 依赖，从重命名到整数执行结果写回 ROB 并按序提交；比较 Kunminghu V2 与 Heliodor 固定快照的结构路径。"
exclusions:
  - "不确定发射/执行/提交周期数、两条指令的具体调度顺序或任何未固定配置下的行为。"
  - "不覆盖 WAW/WAR、多源/多生产者、异常、分支恢复、访存依赖及所有参数化配置。"
  - "不以单一指令对证明整体乱序正确性、性能或 RVA23 符合性。"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual, RV64I Base Integer Instruction Set"
    edition: "v20260120; RV64I version 2.1"
    section: "§3.1.2 Integer Computational Instructions; §3.1.2.1 Integer Register-Immediate Instructions"
    profile_category: "mandatory"
  - name: "RISC-V Unprivileged ISA Manual, RV32I Base Integer Instruction Set"
    edition: "v20260120; RV32I version 2.1"
    section: "§1.1.4 Integer Computational Instructions; §1.1.4.1 Integer Register-Immediate Instructions"
    profile_category: "mandatory"
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

- **问题：** 当 `addi x6,x5,1` 在 `addi x5,x0,10` 之后被重命名时，为什么它不能直接把 `x5` 的旧值当成操作数？两边分别用什么状态保持这一依赖？
- **学习者答案：** 第二条指令的源必须指向第一条指令新分配的物理目的寄存器，而不是重命名前 `x5` 所映射的物理寄存器。重命名建立这个标签关联；若源尚未就绪，发射队列保持依赖。Kunminghu 可由 IQ wakeup 提前唤醒并选择 forward/bypass 数据路径，也可由写回唤醒后从 PRF、寄存器缓存或其他选择路径取得数据；这条指令对实际采用哪条路未确认。结果写入各自 ROB 项，ROB 按程序顺序提交，使架构寄存器应为 `x5=10`、`x6=11`。源码说明这些结构关系，但本文未运行程序验证最终值。
- **检查类型：** explanation + source-location
- **证据 ID：** E2–E12；未运行，见 E17–E18

## 架构行为与子案例

- **可观察行为：** 输入指令序列 `addi x5,x0,10; addi x6,x5,1`，初始 `x0=0`。RV64I 中每条 ADDI 将 `rs1` 与符号扩展的 12 位立即数相加，忽略算术溢出并写入 `rd` 的低 XLEN 位；两条指令的架构结果为 `x5=10`、`x6=11`。ADDI 不产生算术异常。RV64I v20260120 §3.1 建立在 RV32I §1.1 上，只列出相对 RV32I 的差异，并要求结合前章阅读；因此 ADDI 的共同规则由 RV32I §1.1.4.1 与 RV64I §3.1.2.1 一起引用。
- **规范依据：** [RV64I §3.1、§3.1.2、§3.1.2.1，官方 Unprivileged ISA v20260120](https://docs.riscv.org/reference/isa/unpriv/rv64.html)；[RV32I §1.1.4、§1.1.4.1，同版本](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html)。这两章规定 ADDI 的架构运算，不规定本文所比较的微架构队列和唤醒实现。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 正立即数 10 与 1、`x0` 源、单一整数 RAW | covered | 规范行为及有界输入见 E1；两边结构路径见 E2–E12。 |
| 负立即数、立即数符号扩展边界及 XLEN 溢出 | excluded | 本例不覆盖这些数值边界；ISA 对 ADDI 的规则见 E1。 |
| 多条生产者、WAW/WAR、异常与恢复 | excluded | 不属于这条 RAW 链，不能由本例推导。 |
| 两个指令的实际发射/执行先后、周期、具体物理寄存器编号 | unconfirmed | 由配置、可用性和当时的队列状态决定；源码检查未运行配置仿真，不指定周期或编号。 |
| 同一周期重命名与唤醒的竞争处理 | unconfirmed | 相关源码具有同周期唤醒处理，但该例是否触发及具体周期行为未运行确认。 |

## Kunminghu 路径

- **阶段与状态变化：** ADDI 解码为整数 ALU 加法操作，源类型为寄存器和立即数，目的寄存器使能。重命名时从 RAT 读取源映射，为目的分配新物理寄存器；当该指令的源映射与前序本 bundle 指令的逻辑目的匹配时，Rename 对后一指令做目的到源旁路，因此本例 consumer 的 `psrc(0)` 指向 producer 新分配的 `pdest`。RAT 同时维护 speculative 与 architectural 映射。发射队列记录源 `srcState`，仅当源均 ready、条目未发射且未阻塞才可发射；匹配的 IQ wakeup 与写回唤醒都可更新源状态。计算发射条件还可纳入 IQ wakeup，选出带 `forward`/`bypass` 元数据的数据路径；另一条路径通过 PRF 或 regcache 读取数据，再由数据源选择逻辑送入执行端。源码同时显示这些路径，但未确认本例实际选中的 wakeup 和数据源。ALU 执行加法；执行单元写回用 ROB index 定位记录结果；ROB 仅允许已完成且符合提交条件的头部提交。Rename 的提交路径更新架构映射并回收旧物理寄存器。这里描述的是结构路径，不断言本例实际采用哪一种唤醒源或确切的周期先后。
- **源码位置：** ADDI 解码 E2；RAT 的 speculative/architectural 映射与读写旁路 E3；重命名分配和 bundle 内 bypass E4；发射队列就绪与 wakeup E5；DataPath 物理寄存器读取 E6；ALU 加法数据路径 E7；ROB 写回和提交就绪门控 E8；提交更新映射和旧物理寄存器回收 E9。
- **相关验证：** 本记录只检查以上固定快照源码。Kunminghu 的 `IssueQueueMain.scala` 只是 RTL 生成入口，`MultiWakeupQueueMain.scala` 中的生成主体被注释；二者是 test tree entrypoint，不是行为测试，也不证明覆盖本例。见 E18。

## Heliodor 路径

- **阶段与状态变化：** core 注释描述 F → D+R → IQ → ALU → C 路径。重命名从 `rat_spec` 读取源物理标签，分配新目的标签并将重命名操作放入 ROB 与 IQ。对同一 rename bundle 内的 RAW，core 明确在 slot-1 源标签旁路 slot-0 新分配的 pdst；本例即要求 `x6` 的 `rs1_pdst` 等于 `x5` producer 的新 pdst。IQ 对源标签采样 `prf_ready`，未就绪项不属于可发射候选；整数 CDB 按 pdst snoop IQ 并设置匹配的源 ready，同时记录 PRF ready/done。入选指令的源从整数 PRF 读取；ALU 接受操作数并产生 CDB。PRF 按 CDB 的目的标签写结果，ROB 对相同 ROB index 标记 `result_written` 并记录结果。ROB 只在头项有效且结果已写回时给出 commit valid；实际提交更新 `rat_arch` 并释放旧 pdst，架构寄存器镜像更新结果。核心允许多个发射/执行通道，本文不推断两条依赖指令是否在同周期被选择或具体顺序。
- **源码位置：** 处理器流水线结构注释 E10；rename bundle 的目的分配、ROB 项创建和 rename 连接 E11；RAT speculative/architectural 表及提交更新 E12；IQ ready、选择、CDB 唤醒 E13；ALU 发射和 PRF 读写连接 E14；ROB CDB 完成与按序提交门控 E15；提交时更新 architectural RAT 和架构寄存器镜像 E16。
- **相关验证：** `tb/test_smoke.veryl` 顶部注释描述 RAW 与一段 ADDI loop，但 harness 实际载入 `test/v4_smoke.hex`；该 ROM 与断言对应 M3 MUL/DIV smoke，注释与实际输入不一致。测试模块带 `#[ignore]`，未运行；故只能记录其测试源码和注释，不能作为本文案例通过证据。E17。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边都通过物理目的标签把 RAW 消歧：重命名后 consumer 引用 producer 的新物理目的，而不是依赖架构寄存器在执行时仍保持某个固定物理映射。 | E3, E4 | E11, E12 |
| C2 | 两边都显式记录源就绪状态，并以物理目的标签匹配 producer 的 wakeup/CDB 完成源就绪；队列未就绪时不会将该 consumer 作为可发射项。 | E5 | E13 |
| C3 | 两边都把执行结果写回与架构提交分开：写回记录 ROB 完成状态，提交则受 ROB 顺序门控；架构映射在提交路径更新。 | E8, E9 | E15, E16 |
| C4 | 本次比较没有两条指令的运行证据：Heliodor smoke 被 ignore 且源码注释与 ROM/断言不一致；Kunminghu 所查两个入口分别只生成 RTL、生成代码被注释，均非行为测试。 | E18 | E17 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 架构行为 | spec | inspected | RISC-V Unprivileged ISA Manual v20260120 | RV64I §3.1.2.1 https://docs.riscv.org/reference/isa/unpriv/rv64.html; RV32I §1.1.4、§1.1.4.1 https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html | not-run | 不适用 | `addi x5,x0,10; addi x6,x5,1` | `x5=10`、`x6=11`（XLEN=64） | RV64I 章说明其建立在 RV32I 之上、需结合阅读；合读后 ADDI 将 sign-extended imm 与 rs1 相加并写低 XLEN 位 | none |
| E2 | Kunminghu ADDI 解码 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:147` | not-run | sources.lock 固定快照 | ADDI | reg + imm，ALU add，IMM_I，xWen | 源码解码表如此标注 | none |
| E3 | Kunminghu RAT | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/rename/RenameTable.scala:105-149,151-169` | not-run | sources.lock 固定快照 | speculative/architectural mapping | 重命名查 spec map，提交更新 arch map；spec 写有旁路 | 源码包含两张表、spec 读旁路及 arch 更新逻辑 | none |
| E4 | Kunminghu producer→consumer rename mapping | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/rename/Rename.scala:391-415,518-584` | not-run | sources.lock 固定快照 | 同一 rename bundle 中前序目的与后序源相同 | consumer psrc 旁路到前序 pdest | 源码按 ldest/lsrc 匹配并选择前序 pdest；具体 bundle/cycle 未验证 | none |
| E5 | Kunminghu 发射等待/唤醒 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/issue/EntryBundles.scala:39-45,240-301,337-362,408-430` | not-run | sources.lock 固定快照 | producer 未 ready 的 RAW source | 源 ready 后方可 issue | `srcReady`、`canIssue` 与 IQ wakeup 状态更新源码已检查 | none |
| E6 | Kunminghu 数据读取 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/datapath/DataPath.scala:341-349,447-485,515-521,675-710`; `src/main/scala/xiangshan/backend/issue/EntryBundles.scala:337-362,408-430` | not-run | sources.lock 固定快照 | 已发射整数操作 | 读取所选物理寄存器源数据 | DataPath 中可见 PRF/RC 读数据、寄存器源选择与 bypass network 接口；IQ 元数据可选择 forward/bypass，但本例实际选中的数据路未确认 | none |
| E7 | Kunminghu 算术执行 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/fu/Alu.scala:196-202,286-291` | not-run | sources.lock 固定快照 | ADDI 选择 add 运算 | 源值与立即数相加 | ALU datapath 将 add 模块输入连接到执行源及立即数路径 | none |
| E8 | Kunminghu ROB writeback/commit | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/rob/Rob.scala:528-549,788-805` | not-run | sources.lock 固定快照 | 执行单元结果到 ROB；head commit | writeback 记录结果；提交 valid 受 ROB 完成和顺序条件限制 | 源码按 ROB index 记录 writeback，并门控 commit valid | none |
| E9 | Kunminghu 提交映射/回收 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/rename/RenameTable.scala:151-169`; `Rename.scala:634-669` | not-run | sources.lock 固定快照 | 已提交目的寄存器 | architectural RAT 更新，旧 pdest 可回收 | arch write 与提交/free list 连接已检查 | none |
| E10 | Heliodor 整体阶段 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/heliodor_core.veryl:1-22` | not-run | sources.lock 固定快照 | F → D+R → IQ → ALU → C | 结果经 CDB、ROB 后提交 | 源码头部注释描述该路径；这是源码说明，不是动态观察 | none |
| E11 | Heliodor rename 与 ROB/IQ 分配 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/heliodor_core.veryl:2418,2507-2517,3408-3473` | not-run | sources.lock 固定快照 | `x5` producer 与 `x6` consumer rename | spec RAT source 标签及新 pdst 进入 RenamedOp/ROB/IQ | 源码连接 rename、ROB、IQ，slot-1 读有同 bundle bypass；未推断分配编号 | none |
| E12 | Heliodor RAT 状态 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/rat.veryl:119-190` | not-run | sources.lock 固定快照 | speculative rename 与 commit | `rat_spec` rename 时更新，`rat_arch` commit 时更新 | 源码直接实现两表及读写；x0 不重命名 | none |
| E13 | Heliodor IQ ready/wakeup | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/iq_int.veryl:429-467,763-790,902-975` | not-run | sources.lock 固定快照 | RAW source 的 ready/select/CDB snoop | 未 ready 不入选；匹配 CDB pdst 后 ready | 源码通过 ready 条件筛选，并在 CDB 标签相等时置 ready | none |
| E14 | Heliodor execute/PRF | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/heliodor_core.veryl:3023-3065,3342-3368` | not-run | sources.lock 固定快照 | 已选 ALU 操作与整数源 | 从 PRF 读源，执行后目的 pdst 写回 | ALU/PRF 连接已检查；无实际执行观察 | none |
| E15 | Heliodor ROB 完成与按序提交 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/rob.veryl:560-599,1308-1318,1400-1428` | not-run | sources.lock 固定快照 | CDB 写回及 ROB head | 写回置 result_written；head 完成才可提交 | 源码包含对应状态写入及 commit valid 条件 | none |
| E16 | Heliodor architectural update | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/heliodor_core.veryl:4412-4418,5170-5213`; `src/core/rat.veryl:177-190` | not-run | sources.lock 固定快照 | 已 ack 的整数目的提交 | architectural RAT 与架构寄存器镜像更新 | 提交使能与 rd/data 写逻辑已检查；未实际观察 x5/x6 | none |
| E17 | Heliodor RAW test coverage | test-inspected | inspected | Heliodor / `heliodor-master-20261012` | `tb/test_smoke.veryl:1-25,220-235,310-311,385-393`; `test/v4_smoke.hex:1-5` | not-run | 未运行；测试声明 `#[ignore]` | 顶部注释所述 ADDI loop；实际 ROM 为 M3 运算序列，非本文精确指令对 | 测试声明 stall+wake 及结果断言 | 检查到注释、ROM 加载路径和 M3 断言；顶部 RAW/loop 注释与实际 ROM/断言不一致，因 ignore 且未运行，不构成通过证据 | none |
| E18 | Kunminghu test-tree entrypoints; no behavior assertion | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/test/scala/xiangshan/backend/issue/IssueQueueMain.scala:1-19`; `MultiWakeupQueueMain.scala:1-22` | not-run | 未运行 | `IssueQueueMain` 调用 Generator 生成 IssueQueue RTL；`MultiWakeupQueueMain` 的 `emitVerilog` 主体已注释 | 不适用 | 二者仅为非行为性 test-tree entrypoint；不构成本例或队列行为覆盖证据 | none |

- `run-pass` 仅用于实际执行且观察到预期结果的证据。本单元无 `test-run` 或 `run-pass` 证据；不运行 CPU 构建、仿真或测试。
- Kunminghu 的 `IssueQueueMain` 是 RTL 生成入口，`MultiWakeupQueueMain` 的生成主体已注释；二者都不是行为覆盖证据。Heliodor smoke 被 `#[ignore]`，也没有运行。

## 学习者总结

这条 RAW 链正确性的结构基础是，重命名把架构名 `x5` 转成指向新生产者结果的物理标签，并让消费者带着该标签进入发射队列。Kunminghu 的 IQ wakeup 可使消费者带着转发源选择就绪，也可由写回唤醒后经 PRF/RC 等路径取得操作数；这条案例的实际来源尚未确认。执行写回 ROB 与按序提交分离，提交才更新架构状态。两边都能从源码定位到这些关键关系，但证据只说明固定快照中的实现结构，未证明本文指令对的实际运行结果、具体调度周期或处理器整体正确性。Heliodor 的 smoke 源码顶部注释与实际 ROM/断言不一致且被忽略；Kunminghu 有队列/唤醒测试入口。二者都不能作为本例的运行通过证据。

## 未解问题

- 本例在所选配置下各指令的真实发射、执行、writeback 与 commit 周期及调度顺序未确认。
- 未运行两边的端到端程序；`x5=10`、`x6=11` 是 ISA 推导的预期值，不是本项目实测观察。
- Kunminghu 的测试入口是否覆盖与本例相同的 RAW 行为、Heliodor 是否存在可直接运行且未忽略的同案例测试，未在本记录中确认。
