---
unit_id: "add"
stage_id: "阶段 1：指令路径"
scope: "RV64I 基础整数寄存器-寄存器指令 ADD：从 rs1、rs2 读取 XLEN=64 操作数，将和的低 64 位写入 rd；追踪固定快照中的译码、执行及结果写回路径。"
exclusions:
  - "不覆盖 ADDI 的立即数译码和运算路径。"
  - "不覆盖 ADDW 的低 32 位运算及符号扩展路径。"
  - "不验证所有操作数值、rd=x0、压缩指令别名、流水线冲刷/异常交互或完整指令集/profile 符合性。"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual"
    edition: "Version 20260120 (official release)"
    section: "RV32I §1.1.4.2（寄存器-寄存器运算；RV32I commentary 亦适用于 RV64I）；RV64I §3.1.1、§3.1.2.2"
    profile_category: "not-profile-specific"
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

<!-- 比较结论引用双方证据 ID；源码检查不代表运行验证。 -->

## 单元自检

- **问题：** RV64I `ADD` 对两个寄存器操作数执行什么架构行为？它与 `ADDW`、`ADDI` 的边界是什么？两边各如何把结果送入整数寄存器写回？现有测试能证明什么？
- **学习者答案：** RV64I 的 XLEN 为 64。`ADD rd, rs1, rs2` 将 `rs1` 与 `rs2` 的 64 位值相加，结果按模 2^64 保留低 64 位写入 `rd`；算术溢出被忽略，不产生算术溢出异常。`ADDW` 是独立的 32 位结果并符号扩展变体；`ADDI` 使用立即数，二者的完整实现比较不在本单元范围。Kunminghu 将 ADD 译码为双寄存器输入及 ALU add 操作，ALU 输出经执行单元结果选择和写回路径传递；Heliodor 解码 `Opcode::OP` 的 `funct7=0`、`funct3=0` 为 `AluOp::ADD`，ALU 结果经 CDB 送入整数 PRF 写端口。源码表明两边采用的组织不同，但都实现寄存器加法结果路径；未运行测试，因此不声称运行验证通过。**[E1–E10]**
- **检查类型：** explanation + source-location
- **证据 ID：** E1–E10（静态检查；没有运行证据）

## 架构行为与子案例

- **可观察行为：** 读取两个 XLEN 位整数寄存器值，执行加法，将低 XLEN 位写回目的寄存器；溢出不触发算术溢出异常。
- **规范依据：** RISC-V Unprivileged ISA Manual Version 20260120。RV32I §1.1.4.2 说明 ADD 对 rs1、rs2 求和，忽略溢出并写入结果低 XLEN 位，且 RV32I commentary 也适用于 RV64I；RV64I §3.1.1 定义 XLEN=64，§3.1.2.2 说明普通整数计算指令操作 XLEN 位值，`W` 后缀指令则忽略高 32 位并将 32 位有符号结果符号扩展至 64 位。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 64 位寄存器-寄存器 ADD；结果低 64 位 | covered（规范与源码检查） | 规范行为；未用运行测试验证。E1–E4 |
| 有符号/无符号解释及进位溢出 | covered（规范边界） | 加法对位模式执行；溢出被忽略，保留低 64 位。未穷举数值边界。E1 |
| `rd=x0` 的架构可见结果 | unconfirmed | 未在此试点专项追踪零寄存器丢弃写入的实现或运行验证。 |
| `ADDW` | excluded | 32 位加法后符号扩展，与 ADD 语义不同；这里只检查对照边界。E2、E5、E7 |
| `ADDI` | excluded | 寄存器-立即数指令，不属于本单元的双寄存器 ADD 路径。E3、E5、E6 |
| 全操作数组合、流水线恢复及异常交互 | excluded | 超出单指令静态追踪范围；未运行。 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit` 的 `ADD` 项选择 `SrcType.reg`、`SrcType.reg`、`FuType.alu`、`ALUOpType.add` 并置整数写使能。ALU 的 `AddModule` 对两路 XLEN 输入求和；结果选择器将 add 结果送到 `io.result`。ALU wrapper 将输入源值和功能码交给数据模块并输出结果。执行单元从有效功能单元选择结果数据与整数写使能；`Backend` 将整数执行单元输出接入 `wbDataPath`。
- **源码位置：** `DecodeUnit.scala:154`（E3）；`Alu.scala:25-35, 370-380`（E4）；wrapper `Alu.scala:8-22`（E5）；`ExeUnit.scala:328-374`（E6）；`Backend.scala:667-680`（E6）。
- **相关验证：** `DecodeTest.scala:38-49` 的 `DecodeUnitTest` 只对 DecodeUnit 时钟步进 10 次，没有断言 ADD 译码语义或算术结果。入口 `Makefile.test:10-12` 提供 `test-DecodeUnit`，但未运行。E8 为检查过的测试源码；E9 为入口检查；E15 单独记录未运行状态。

## Heliodor 路径

- **阶段与状态变化：** `decoder.veryl` 对 `Opcode::OP` 选择寄存器 A/B 和整数寄存器写使能；在 `funct7=0000000` 分支下，以 `funct3=000` 选择 `AluOp::ADD`。`alu.veryl` 直接计算 `i_a + i_b`。`alu_wrap.veryl` 选择寄存器操作数、调用 ALU，并将普通 ALU 情况的 `alu_out` 作为 `wb_data`；有效 CDB 项携带 `has_rd`、目的物理寄存器和数据。核心将有效 CDB 的目的及数据接到整数 PRF 写端口。
- **源码位置：** `decoder.veryl:410-428`（E10）；`alu.veryl:143-155`（E11）；`alu_wrap.veryl:121-132, 400-421`（E12）；`heliodor_core.veryl:3362-3368`（E13）。
- **相关验证：** `tb/test_alu.veryl:33-45` 有 ADD 输入向量 10+20、期望 30。native testbench 运行 29 次时钟迭代后只断言一次 `pass`，没有等待 `done` 或检查 `tc`；因此静态源码不能确认最终断言对应哪个案例，也不能证明 ADD 或 DIV 被断言。本机未运行 `veryl test`。文件注释提到早先案例由 riscv-tests arch tests 覆盖，但该说法未在本试点核实。E14 为检查过的测试源码；E16 单独记录未运行状态。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边的静态源码路径都把 ADD 的两个寄存器操作数送入加法运算，并提供整数目的写回路径；该观察支持路径层面的相同点，不构成运行验证或完整 ISA 合规结论。 | E3、E4、E5、E6 | E10、E11、E12、E13 |
| C2 | 源码组织存在差异：Kunminghu 通过独立 `AddModule`、ALU 结果选择及执行/写回模块连接；Heliodor 由 Veryl ALU wrapper 选择操作数、计算并形成 CDB 项，再接 PRF 写端口。此为微架构组织差异，不是 ISA 行为差异。 | E4、E5、E6 | E11、E12、E13 |
| C3 | 检查过的测试材料都不足以形成 ADD 运行通过证据：Kunminghu 定向测试只步进译码模块；Heliodor 有 ADD 向量和一次总体断言，但因未等待 `done` 或检查 `tc`，无法从源码确认断言案例。两边测试均未运行。 | E8、E9、E15 | E14、E16 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 自检、ADD 规范行为 | spec | inspected | RISC-V Unprivileged ISA Manual v20260120 | [RV32I §1.1.4.2](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html) | not-run | 不适用 | 两寄存器加法与溢出语义 | 低 XLEN 位写回，溢出忽略 | 规范文字已检查；无执行观察 | none |
| E2 | 自检、ADD/ADDW 边界 | spec | inspected | RISC-V Unprivileged ISA Manual v20260120 | [RV64I §3.1.1、§3.1.2.2](https://docs.riscv.org/reference/isa/unpriv/rv64.html) | not-run | 不适用 | XLEN 与 W 后缀边界 | XLEN=64；W 结果符号扩展 | 规范文字已检查；无执行观察 | none |
| E3 | C1、Kunminghu 译码 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:154` | not-run | 锁定 snapshot | ADD decode table entry | 两个寄存器源、ALU add、整数写使能 | 源码静态检查确认映射 | none |
| E4 | C1、C2、Kunminghu 运算/选择 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/main/scala/xiangshan/backend/fu/Alu.scala:25-35,370-380` | not-run | 锁定 snapshot | XLEN 两输入加法及 ALU 结果选择 | add 结果作为 ALU result | 源码静态检查确认连接 | none |
| E5 | C1、C2、Kunminghu wrapper | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/Alu.scala:8-22` | not-run | 锁定 snapshot | 输入操作数/功能码与结果 | wrapper 传递输入并输出结果 | 源码静态检查确认连接 | none |
| E6 | C1、C2、Kunminghu execution/writeback | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `ExeUnit.scala:328-374`; `Backend.scala:667-680` | not-run | 锁定 snapshot | 功能单元结果与整数写使能 | 选择执行结果并接入写回路径 | 源码静态检查确认连接 | none |
| E7 | ADD 与 ADDW 源码边界 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `DecodeUnit.scala:154,173,178`; `Alu.scala:25-35,360-368` | not-run | 锁定 snapshot | ADD 与 ADDW 操作类型 | 分别映射 `add`、`addw` 路径 | 源码静态检查确认独立操作码/路径 | none |
| E8 | C3、Kunminghu 测试检查 | test-inspected | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/test/scala/xiangshan/DecodeTest.scala:38-49` | not-run | `DecodeUnitTest` / Verilator 注解 | DecodeUnit 时钟步进 10 周期 | 若要证明 ADD，需检查 ADD decode/output | 仅检查到步进，无 ADD 断言；未运行 | none |
| E9 | C3、Kunminghu 测试入口 | test-inspected | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/Makefile.test:10-12` | not-run | Mill target `test-DecodeUnit` | `DecodeUnitTest` | 定向入口可调用测试 | 只检查 Makefile；Mill 不可用，未运行 | none |
| E10 | C1、Heliodor 译码 | source | inspected | Heliodor / `heliodor-master-20261012` | `sources/heliodor/src/core/decoder.veryl:410-428` | not-run | 锁定 snapshot | `Opcode::OP`, `funct7=0`, `funct3=0` | `AluOp::ADD` 与寄存器源 | 源码静态检查确认映射 | none |
| E11 | C1、C2、Heliodor 运算 | source | inspected | Heliodor / `heliodor-master-20261012` | `sources/heliodor/src/core/alu.veryl:143-155` | not-run | 锁定 snapshot | `AluOp::ADD` | `i_a+i_b` 的 64 位结果 | 源码静态检查确认表达式 | none |
| E12 | C1、C2、Heliodor wrapper/CDB | source | inspected | Heliodor / `heliodor-master-20261012` | `sources/heliodor/src/core/alu_wrap.veryl:121-132,400-421` | not-run | 锁定 snapshot | issue operands、ALU result、CDB | 普通 ALU 结果作为 CDB data 携带目的寄存器 | 源码静态检查确认连接 | none |
| E13 | C1、C2、Heliodor 整数 PRF 写回 | source | inspected | Heliodor / `heliodor-master-20261012` | `sources/heliodor/src/core/heliodor_core.veryl:3362-3368` | not-run | 锁定 snapshot | CDB valid/has_rd/pdst/data | 有效整数结果接到 PRF 写端口 | 源码静态检查确认连接 | none |
| E14 | C3、Heliodor testbench 断言范围 | test-inspected | inspected | Heliodor / `heliodor-master-20261012` | `sources/heliodor/tb/test_alu.veryl:33-45,223-249` | not-run | 默认 Veryl testbench；29 次时钟迭代后一次 `pass` 断言 | 含 ADD 10+20 期望 30 的向量 | 需确认断言时的 `tc`/案例才能判断覆盖 | 未等待 `done` 或检查 `tc`；源码无法确认最终断言对应案例，不能证明 ADD 或 DIV 已断言。见 E16 | none |
| E15 | C3、Kunminghu 测试运行状态 | test-run | unverified | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/Makefile.test:10-12` | `mill -i XiangShan.test.testOnly xiangshan.DecodeUnitTest`（未运行） | 定向 DecodeUnitTest / Verilator | ADD decode/output assertion | 需实际运行并观察 ADD 行为 | 未运行；Mill 当前不可用 | none |
| E16 | C3、Heliodor 测试运行状态 | test-run | unverified | Heliodor / `heliodor-master-20261012` | `sources/heliodor/tb/test_alu.veryl` | `veryl test`（未运行） | 默认 Veryl testbench | ADD 向量的独立 assertion/观察 | 需实际运行并观察 ADD 行为 | 未运行；Veryl 当前不可用 | none |

## 学习者总结

RV64I `ADD` 是 XLEN 位寄存器加法，在本单元 XLEN=64，因此结果是两数之和的低 64 位，溢出被忽略。`ADDW` 会先形成低 32 位结果再符号扩展，`ADDI` 的第二操作数则来自立即数，均不能与 ADD 混作同一条完整实现路径。Kunminghu 将加法器、结果选择、执行结果选择和后端写回分层连接；Heliodor 将 ALU wrapper/CDB 与 PRF 写端口连接。源码检查显示了行为路径和组织差异，但没有执行 ADD 专项测试；尤其不能把 Heliodor 测试文件中存在 ADD 向量当作 ADD 已通过，也不能从本单元推断 RVA23 整体符合性。

## 未解问题

- 本机没有运行 Kunminghu 或 Heliodor 测试；ADD 的实际运行结果未验证。
- 尚未追踪 `rd=x0` 丢弃写入、异常/冲刷流水线交互及各种溢出边界的实现细节。
- Heliodor testbench 的单次断言实际对应哪个案例、ADD 是否由其他 arch test 覆盖，仍需检查相应测试实现并实际运行后确认。
