---
unit_id: "rva23u64-scalar"
stage_id: "Epic 4 / Story 4.2"
scope: "RVA23U64 §3.1.1.1 的 RV64I 及 §3.1.1.2 的 M、C、B、Zicsr、Zicntr、Zihpm、Zihintpause、Zihintntl、Zicond、Zimop、Zcmop、Zcb、Supm、Zkt；比较固定源码快照和已有测试材料。"
exclusions:
  - "A 与 Zawrs 的原子/保留等待路径由 Story 4.6 跟踪。"
  - "F/D、向量、缓存/内存属性、浮点、其他 S64 特权功能及全 ISA 符合性不在本单元范围。"
  - "所有测试仅作静态材料检查；未执行任何测试，不得推断 run-pass。"
spec_refs:
  - name: "RISC-V RVA23 Profile"
    edition: "v1.0 ratified"
    section: "§3.1.1.1 RV64I; §3.1.1.2 M/C/B/Zicsr/Zicntr/Zihpm/Zihintpause/Zihintntl/Zicond/Zimop/Zcmop/Zcb/Supm/Zkt"
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

<!-- 结论只在引用的源码和具体验证材料范围内成立；测试均未运行。 -->

## 单元自检

- **问题：** 为什么静态看到扩展译码或定向测试，仍不能写成 profile 要求已通过？
- **学习者答案：** RTL 显示设计路径，测试源显示拟检查的刺激和断言；只有执行并观察结果才能记录运行状态，而且单个子案例不能证明完整扩展或 profile 覆盖。
- **检查类型：** source-location
- **证据 ID：** E1–E6

## 架构行为与子案例

- **可观察行为：** 基础整数和扩展指令由前端展开/译码、整数执行单元和 CSR 子系统承载。覆盖表的 `partially-studied` 等状态描述一项 profile 要求的调查程度；本表的 `unconfirmed` 描述单个子案例是否已由证据确立。`unconfirmed` 表示该子案例尚未确立，不表示实现缺失。
- **规范依据：** RVA23 Profile v1.0 §3.1.1.1、§3.1.1.2；稳定要求键见 [`notes/rva23-coverage.md`](../rva23-coverage.md)。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| RV64I 基本指令路径 | unconfirmed | 定位了基础译码、ALU、分支和访存路径；没有逐项枚举全部 RV64I 指令和异常行为。 |
| M 乘法、除法 | unconfirmed | 找到香山 MulUnit/DivUnit 和 Heliodor ALU/int_divider；Heliodor 有 RV64UM 具名测试，未运行。 |
| C 与 Zcb 压缩展开 | unconfirmed | 香山定位到 RVCExpander/RVCDecoder 包装和 PreDecode 的压缩长度路径，但未审阅完整展开映射；Heliodor 检查到部分 C ALU 与 Zcb 展开操作。测试材料未运行，完整 C 编码集合未核验。 |
| B 位操作 | unconfirmed | 两侧源码含部分位操作映射；子扩展、变体和完整 B 操作集合未穷尽。 |
| CSR、cycle/time/instret 与 HPM | unconfirmed | 找到 CSR 读写和计数器路径；香山有计数器/TIME 待核边界，所有权限、计数配置及事件场景未完成。 |
| Zihintpause | unconfirmed | 两侧有 PAUSE 译码处理；提示对调度/停顿的微架构效果未验证。 |
| Zihintntl | unconfirmed | Heliodor 有 hint bundle 名称线索，未确认独立 NTL 指令刺激与断言；香山指定源码/测试搜索未定位路径。搜索范围有限，不据此断言不存在。 |
| Zicond | unconfirmed | 两侧含 czero.eqz 与 czero.nez 路径，Heliodor 有专用定向 harness；测试未运行。 |
| Zimop 与 Zcmop | unconfirmed | Heliodor 显式写出 MOP 默认零结果和 C.MOP NOP 展开；香山有 Zimop decode/后处理线索，C.MOP 全部合法编码和最终行为未确认。 |
| Supm PMLEN=0 / 7 | unconfirmed | 两侧源码含 Disable/7 位掩码选择线索；所有环境配置、访问类型和模式行为未运行。 |
| Zkt 数据无关时延 | unconfirmed | RTL 功能路径和功能测试不足以证明时序/侧信道属性；本单元没有独立时序证据。 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit` 将基础指令映射到功能单元，并将 CSR、PAUSE、Zicond 和部分 Zimop pattern 接入后端；整数乘除分别走执行 wrapper；`NewCSR` 提供计数器与 EnvPMM。源码只建立路径线索，MOP 和 NTL 仍有待核子案例。
- **源码位置：** 固定快照 `xiangshan-kunminghu-v2-20261012`：`src/main/scala/xiangshan/backend/decode/DecodeUnit.scala`（PAUSE、ZicondDecode、ZimopDecode、isZimop 和最终译码）；`backend/fu/Alu.scala`；`backend/fu/wrapper/MulUnit.scala`、`DivUnit.scala`；`backend/fu/NewCSR/MachineLevel.scala`（mcycle、minstret、mhpmcounter）；`CSRDefines.scala`（EnvPMM Disable/PMLEN7/PMLEN16）；`frontend/PreDecode.scala`。
- **相关验证：** 已检查 `sources/xiangshan/src/test/scala/fu/IntDiv.scala`。`IntDividerTest` 生成随机 64 位 dividend/divisor，驱动 signed divide，并用 `expect` 检查 quotient 与 remainder；它只提供 divider 的这些测试材料，不覆盖乘法或所有 M 子案例，且未运行。其他源码/测试搜索没有据未命中推断实现缺失。

## Heliodor 路径

- **阶段与状态变化：** `decoder.veryl` 识别标量整数/CSR、PAUSE、Zicond 和 MOP.R/RR；`alu.veryl` 含 Zicond 运算；`c_expander.veryl` 将 C/Zcb 操作展开并把被识别 C.MOP 编码转换为 NOP；`csr.veryl` 提供 cycle/time/instret 与 HPM 计数器逻辑；`alu_wrap.veryl` 含 PMLEN 地址掩码路径。
- **源码位置：** 固定快照 `heliodor-master-20261012`：`src/core/decoder.veryl`（Zicond、PAUSE、Zimop）；`src/core/alu.veryl`（CZERO）；`src/core/c_expander.veryl`（Zcb、C.MOP）；`src/core/csr.veryl`（计数器、time、HPM）；`src/core/alu_wrap.veryl`（地址掩码）。
- **相关验证：** 已检查 `tb/test_arch_common.veryl` 中 `test_arch_zicond`、`test_arch_hint`、`test_arch_zcb`、`test_arch_hpm_counter` 及 `test_alu.veryl`、`test_c_expander.veryl` harness；也定位 `test/zicond`、`test/hint`、`test/zcb`、`test/hpm` 输入。测试源有刺激/断言入口，但未执行。具名 M、CSR/计数器和全 ISA 子案例仅覆盖到可见的材料范围。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧都存在标量译码、整数执行与 CSR/计数器的源码路径；路径存在本身不是行为通过结论。 | E1–E3 | E4–E6 |
| C2 | 本次可检查到的 Heliodor 材料更直接提供 Zicond、Zcb、HPM 和 hint 定向 harness；未运行这些 harness，因此仅表示材料更具体，不表示覆盖更好或实现已通过。 | E3 | E5–E6 |
| C3 | Zkt、Zihintntl 与 Supm 的 profile 子案例仍有重要边界；无证据处保持 partial/unconfirmed。 | E1–E3 | E4–E6 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | C1、C3；RV64I/M/C/B/CSR/提示与 Zimop 映射 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala`；`sources/xiangshan/src/main/scala/xiangshan/backend/fu/Alu.scala`；`sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/MulUnit.scala`；`sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/DivUnit.scala`；`sources/xiangshan/src/main/scala/xiangshan/frontend/PreDecode.scala` | 直接源码审阅 Kunminghu `MulUnit.scala` 与 `DivUnit.scala`；`rg -n "RVCExpander|RVCDecoder|currentIsRVC|Zicond|PAUSE|MOP_R|C_MOP|MOP|Zh?pm|cycle|time|instret|PMLEN|PME|Czero|NTL" sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/Alu.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/MulUnit.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/DivUnit.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR sources/xiangshan/src/main/scala/xiangshan/frontend/PreDecode.scala sources/heliodor/src/core/decoder.veryl sources/heliodor/src/core/alu.veryl sources/heliodor/src/core/c_expander.veryl sources/heliodor/src/core/csr.veryl sources/heliodor/src/core/alu_wrap.veryl sources/heliodor/src/core/int_divider.veryl sources/heliodor/tb/test_arch_common.veryl sources/heliodor/tb/test_alu.veryl sources/heliodor/tb/test_c_expander.veryl` | 不适用 | 译码/执行符号与映射 | 对照项需能追溯到路径 | 已检查相关符号；没有执行行为 | none |
| E2 | C1、C3；Zicsr/Zicntr/Zihpm/Supm | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/MachineLevel.scala`；`sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRDefines.scala`；`sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRPermitModule.scala` | `rg -n "TODO|FIXME|mcycle|hpmcounter|instret|cycle|time|PMLEN7|senvcfg.*PME|PAUSE|c\.mop|MOP" sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/MachineLevel.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SupervisorLevel.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRDefines.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/Alu.scala sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala sources/heliodor/tb/test_arch_common.veryl sources/heliodor/tb/test_alu.veryl sources/heliodor/tb/test_c_expander.veryl` | 不适用 | CSR 与计数器/EnvPMM 实现 | 记录源码能直接支持的范围 | 定位 mcycle/minstret/HPM 与 EnvPMM 枚举；完整行为未验证 | none |
| E3 | C1、C2；香山 divider 测试材料 | test-inspected | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `sources/xiangshan/src/test/scala/fu/IntDiv.scala` (`IntDividerTest`: 随机 64 位 signed division，expect quotient/remainder) | `rg -n "NTL|ntl|HINT|MOP|cmop|zicond|PME|PMP" sources/xiangshan/src/main/scala/xiangshan/backend/decode sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR sources/xiangshan/src/test/scala sources/heliodor/tb/test_arch_common.veryl`；`cat sources/xiangshan/src/test/scala/fu/IntDiv.scala` | 不适用 | divider 随机输入；未运行 | quotient/remainder 断言 | 仅确认存在 divider 刺激与断言；只支持所述除法案例，不覆盖乘法/完整 M 扩展 | none |
| E4 | C1、C3；Heliodor 标量 RTL | source | inspected | Heliodor `heliodor-master-20261012` | `sources/heliodor/src/core/decoder.veryl`；`sources/heliodor/src/core/alu.veryl`；`sources/heliodor/src/core/c_expander.veryl`；`sources/heliodor/src/core/csr.veryl`；`sources/heliodor/src/core/alu_wrap.veryl`；`sources/heliodor/src/core/int_divider.veryl` | 直接源码审阅 Heliodor `alu.veryl` 与 `int_divider.veryl`；`rg -n "RVCExpander|RVCDecoder|currentIsRVC|MUL|DIV|REM|Zicond|PAUSE|MOP_R|C_MOP|MOP|Zh?pm|cycle|time|instret|PMLEN|PME|Czero|NTL" sources/heliodor/src/core/decoder.veryl sources/heliodor/src/core/alu.veryl sources/heliodor/src/core/c_expander.veryl sources/heliodor/src/core/csr.veryl sources/heliodor/src/core/alu_wrap.veryl sources/heliodor/src/core/int_divider.veryl` | 不适用 | 解码、ALU、压缩与 CSR 路径 | 记录源码能直接支持的范围 | 已检查相关案例和逻辑注释；行为未运行 | none |
| E5 | C1、C2；Heliodor 定向测试材料 | test-inspected | inspected | Heliodor `heliodor-master-20261012` | `sources/heliodor/tb/test_arch_common.veryl`（`test_arch_rv64um_div/divu/divuw/divw/mul/mulh/mulhsu/mulhu/mulw/rem/remu/remuw/remw`，约 1956–2302 行；`test_arch_hint` 4698–4720 行；`test_arch_zicond`、`test_arch_zcb`、`test_arch_hpm_counter`）；`sources/heliodor/tb/test_alu.veryl`；`sources/heliodor/tb/test_c_expander.veryl`；`sources/heliodor/test/riscv-arch-test/build/rv64um/{div,divu,divuw,divw,mul,mulh,mulhsu,mulhu,mulw,rem,remu,remuw,remw}.hex`；`sources/heliodor/test/hint/hint_test.S:20-21`（PAUSE stimulus）；`sources/heliodor/test/zicond/{zicond_test.S,zicond_test.hex}`；`sources/heliodor/test/hint/{hint_test.S,hint_test.hex}`；`sources/heliodor/test/zcb/{zcb_test.S,zcb_test.hex}`；`sources/heliodor/test/hpm/{hpm_test.S,hpm_test.hex}` | `rg -n "test_arch_rv64um_(div|divu|divuw|divw|mul|mulh|mulhsu|mulhu|mulw|rem|remu|remuw|remw)|test_arch_hint|test_arch_zicond|test_arch_zcb|test_arch_hpm_counter" sources/heliodor/tb/test_arch_common.veryl`；`rg --files sources/heliodor/test/riscv-arch-test/build/rv64um sources/heliodor/test/hint sources/heliodor/test/zicond sources/heliodor/test/zcb sources/heliodor/test/hpm`；`sed -n '20,21p' sources/heliodor/test/hint/hint_test.S` | 未运行 | harness 载入的具名输入程序与断言 | harness 断言通过 | 仅检查测试源和输入文件；没有运行结果 | none |
| E6 | C1、C2；Heliodor CSR/HPM 行为测试材料 | test-inspected | inspected | Heliodor `heliodor-master-20261012` | `sources/heliodor/tb/test_arch_common.veryl`（`test_arch_rv64mi_csr` 2307–2335 行；`test_arch_rv64mi_instret_overflow` 3201–3223 行；`test_arch_hpm_counter` 4586–4608 行）；`sources/heliodor/test/riscv-arch-test/build/rv64mi/{csr,instret_overflow}.hex`；`sources/heliodor/test/hpm/{hpm_test.S,hpm_test.hex}` | `rg -n "test_arch_rv64mi_csr|test_arch_rv64mi_instret_overflow|test_arch_hpm_counter" sources/heliodor/tb/test_arch_common.veryl`；`rg --files sources/heliodor/test/riscv-arch-test/build/rv64mi sources/heliodor/test/hpm` | 未运行 | CSR/计数器具名案例 | harness 断言通过 | 只检查材料，未执行 | none |

- 没有 `test-run`、`experiment` 或 `run-pass` 证据。本轮静态检查不支持动态通过、完整覆盖、Zkt 时序性质或 profile 符合性结论。

## 学习者总结

两侧实现都把标量 ISA 行为拆在译码、执行和 CSR 路径中；Heliodor 的本次快照还配有若干直观的架构测试 harness。可见的源码和测试入口帮助定位行为，但它们不能替代测试运行，也不能代表完整子扩展覆盖。Zihintntl、Zimop/C.MOP 边界、PMLEN 环境选择、计数器细节及 Zkt 属性需要后续更细的逐项核验。本单元是可追踪的学习映射，不是实现认证。

## 未解问题

- 香山 scalar CSR/counter 源码中 TIME/非特权计数器的具体缺口与 `TODO` 边界应由后续 CSR 专题核查；当前仅记录已见位置和不确定性。
- 两侧 `Zihintntl` 指令编码、所有 NTL hint 类别、Zimop/Zcmop 全部保留索引的行为均未穷举。
- Supm 的执行环境如何选择 PMLEN=0/7，以及在不同地址访问路径上的完整屏蔽行为未运行验证。
- Zkt 的数据无关执行时延需独立时序/侧信道方法，当前证据不能回答。
