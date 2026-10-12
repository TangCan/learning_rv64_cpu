---
unit_id: "rva23u64-floating-point"
stage_id: "Epic 4 / Story 4.3"
scope: "RVA23U64/v1.0 §3.1.1.2 的 F、D、Zfhmin、Zfa 标量浮点要求；对照固定快照的译码、执行、状态控制和已有验证材料。"
exclusions:
  - "向量浮点路径与 Zvfhmin 不属于本单元；源码中出现向量浮点操作不作为标量覆盖证据。"
  - "不声称 IEEE 754 全覆盖或 RVA23 符合性；测试材料均只做静态检查，没有运行。"
  - "舍入模式的全组合、NaN-box、异常 flag、FS 状态及跨格式组合正确性尚未完整验证。"
spec_refs:
  - name: "RISC-V RVA23 Profile"
    edition: "v1.0 ratified"
    section: "§3.1.1.2 F、D、Zfhmin、Zfa"
    profile_category: "mandatory"
  - name: "RISC-V F Extension"
    edition: "v2.2"
    section: "F single-precision floating-point"
    profile_category: "mandatory"
  - name: "RISC-V D Extension"
    edition: "v2.2"
    section: "D double-precision floating-point"
    profile_category: "mandatory"
  - name: "RISC-V Zfhmin Extension"
    edition: "v1.0"
    section: "Zfhmin minimal half-precision floating-point"
    profile_category: "mandatory"
  - name: "RISC-V Zfa Extension"
    edition: "v1.0"
    section: "Zfa additional floating-point instructions"
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

<!-- 只记录固定快照中可见的路径和已检查材料；不存在 run-pass 证据。 -->

## 单元自检

- **问题：** 源码列出 S/D/H opcode，并能找到架构测试输入，能否据此说 F/D/Zfhmin/Zfa 已通过？
- **学习者答案：** 不能。译码表说明指令可能进入某条实现路径，测试源码和输入说明存在待执行的检查；只有运行并观察断言结果才能记为运行通过，而且局部案例不能证明完整扩展覆盖。
- **检查类型：** source-location
- **证据 ID：** E1–E7

## 架构行为与子案例

- **可观察行为：** 标量 FP 指令从标量 decoder 进入算术、乘加、转换或除法/平方根单元，读写浮点寄存器并通过 FCSR/状态控制处理 rounding mode、flags 与 FS。标量浮点与向量 FP decoder、向量执行单元分开；本单元只跟踪标量路径。
- **规范依据：** RVA23 Profile v1.0 §3.1.1.2 将 F、D、Zfhmin 列为强制要求；Zfa 为 RVA23U64 新增强制要求。Zfhmin 的最小半精度范围为 FLH/FSH、FMV.X.H/FMV.H.X 及 FCVT.S.H/FCVT.H.S/FCVT.D.H/FCVT.H.D，不能把完整 H 算术路径误当作其要求。官方来源：[RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)、[F v2.2](https://docs.riscv.org/reference/isa/unpriv/f-st-ext.html)、[D v2.2](https://docs.riscv.org/reference/isa/unpriv/d-st-ext.html)、[Zfhmin v1.0](https://docs.riscv.org/reference/isa/unpriv/zfh.html)、[Zfa v1.0](https://docs.riscv.org/reference/isa/unpriv/zfa.html)。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| F 单精度算术、比较、分类、符号操作、转换、load/store、除法/平方根、FMA | unconfirmed | 两边存在标量 decode/执行路径；Heliodor 有 rv64uf harness 与 hex；均未执行，不推断完整指令或数值语义通过。 |
| D 双精度对应操作 | unconfirmed | 两边存在标量路径；Heliodor 有 rv64ud harness 与 hex；舍入、异常及所有输入类别未验证。 |
| Zfhmin 搬运与格式转换 | unconfirmed | Heliodor Zfhmin 源码注释/测试涉及要求中的搬运、S/H、D/H 转换；未执行。Kunminghu 的 H decode 线索更广，但不能代替逐条正确性证据。 |
| Zfhmin H 算术 | excluded | H 算术超出 Zfhmin 最小扩展要求；即使 decode 表中出现也不用于证明 Zfhmin。 |
| Zfa 比较/minmax、round、转换等指令 | unconfirmed | 两边可见部分 opcode/执行分支；Heliodor 有 zfa_s1–s4 测试材料。完整扩展覆盖及各边界均未核实。 |
| 舍入、NaN-box、异常 flags、FS 状态和跨格式组合 | unconfirmed | 源码可见部分信号和分支不等于规范级组合验证；现有材料未运行且未形成穷举。 |
| 向量 FP / Zvfhmin | excluded | VecDecoder、VFPU 等是独立向量路径，不属于标量 F/D/Zfhmin/Zfa 映射。 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit`/`FPDecoder` 将 S/D/H 标量算术、比较、转换、load/store、FMA、除法/平方根和部分 Zfa opcode 转为功能单元控制；`FALU`、`FMA`、`FCVT`、`FDivSqrt` wrapper 分别连接浮点算术、乘加、转换与除法/平方根子模块。`NewCSR`/`Unprivileged` 有 FCSR、frm、fflags 与 FS 可见的控制和提交路径。源码快照内 `fudian/`、`yunsuan/` 目录为空，因此 wrapper 下游实现不能在本快照中继续核验。`VecDecoder`/VF* 路径单独处理向量操作。
- **源码位置：** 固定 snapshot `xiangshan-kunminghu-v2-20261012`：`sources/xiangshan/src/main/scala/xiangshan/backend/decode/FPDecoder.scala`、`backend/decode/DecodeUnit.scala`；`backend/fu/wrapper/FALU.scala`、`FMA.scala`、`FCVT.scala`、`FDivSqrt.scala`；`backend/fu/NewCSR/Unprivileged.scala`、`NewCSR.scala`。测试线索：`sources/xiangshan/src/test/scala/xiangshan/DecodeTest.scala`。
- **相关验证：** `DecodeTest.scala` 实例化 DecodeUnit 并推进时钟，没有给出 FP instruction stimulus 或结果断言，不能作为 FP 行为测试。指定源码/测试静态搜索没有找到独立标量 FP 定向测试；该搜索范围有限，不据此断言其他位置不存在测试。未运行测试。

## Heliodor 路径

- **阶段与状态变化：** `decoder.veryl` 选择标量 FP opcode；`fpu_wrap.veryl` 按 FpuOp 分发 D/S/H 的运算、转换和部分 Zfa 操作，并输出结果与 fflags；`fpu_pkg.veryl` 定义浮点操作枚举。`csr.veryl` 与 `alu_wrap.veryl` 包含 CSR/状态及标量数据通路连接线索，`lsu.veryl` 提供浮点 load/store 路径。`tb/test_arch_fp.veryl` 将 rv64uf/rv64ud hex 接入具名 harness，`test_arch_common.veryl` 有 Zfhmin harness；`test_arch_fp` 和 `test/` 源文件在仓库 `.gitignore` 下，尽管固定快照工作区能读到，仍需作为 ignored 材料看待。全部未运行。向量操作属于独立路径。
- **源码位置：** 固定 snapshot `heliodor-master-20261012`：`sources/heliodor/src/core/decoder.veryl`、`fpu_wrap.veryl`、`lsu.veryl`、`alu_wrap.veryl`、`csr.veryl`、`src/pkg/fpu_pkg.veryl`。材料：`tb/test_arch_fp.veryl`、`tb/test_arch_common.veryl`、`tb/test_fp_*.veryl`、`test/zfhmin/`、`test/zfa/`、`test/riscv-arch-test/build/rv64uf/`、`test/riscv-arch-test/build/rv64ud/`。
- **相关验证：** `test_arch_fp` 有 rv64uf/rv64ud 的 add、class、compare、convert、divide、FMA、min、load/store、move、recoding、structural harness，并以 pass 断言结束；`test_arch_common` 中可见 Zfhmin harness。Zfa S1–S4 harness 加载对应 hex 并断言 pass；Zfhmin/Zfa 汇编注释和指令可作为刺激材料范围线索。全部均为已检查、未运行材料；PASS 字符串和断言不代表本轮观察到 pass。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧都有标量 FP decode 到算术/转换/状态控制的可见路径；Kunminghu wrapper 下游 fudian/yunsuan 源码在该快照中不可见，Heliodor 的 fpu_wrap 有较多直接实现逻辑；这只是源码可见度差异，不是正确性结论。 | E1–E3 | E5 |
| C2 | Heliodor 快照中存在分立的 rv64uf/rv64ud、Zfhmin、Zfa 测试 harness 和输入；已检查但未执行。Kunminghu DecodeTest 没有 FP 刺激/断言；测试入口差异不能说明设计优劣。 | E4 | E6–E7 |
| C3 | 标量和向量浮点路径有不同的 decoder/功能单元归属；不能使用 VecDecoder/VF* 路径代替标量 F/D/Zfhmin/Zfa 证据。 | E1–E3 | E5 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | C1/C3；Kunminghu 标量与向量 decode 区分 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `FPDecoder.scala`、`DecodeUnit.scala`（F/D/H 与 Zfa pattern；标量/向量 decode） | `rg -n "FADD|FCVT|FMINM|FLEQ|FROUND|FCVTMOD|FPDecoder|FuType\.falu" sources/xiangshan/src/main/scala/xiangshan/backend/decode/FPDecoder.scala sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala` | 不适用 | S/D/H 标量 opcode 与部分 Zfa opcode | 路由线索 | 已检查 pattern；未生成/运行指令 | none |
| E2 | C1；Kunminghu 标量执行 wrapper | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `backend/fu/wrapper/FALU.scala`、`FMA.scala`、`FCVT.scala`、`FDivSqrt.scala`；snapshot `fudian/`、`yunsuan/` 为空 | `rg -n "FloatAdder|FloatFMA|FloatDivider|FpPipedFuncUnit|fflags" sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/FALU.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/FMA.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/FCVT.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/FDivSqrt.scala` | 不适用 | 算术/FMA/转换/div-sqrt wrapper | 路由和接口线索 | wrapper 调用外部模块；外部实现源未随快照提供 | none |
| E3 | C1；Kunminghu FCSR/FS 路径 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `backend/fu/NewCSR/Unprivileged.scala`、`NewCSR.scala` | `rg -n "FCSR|fflags|frm|fpState|ContextStatus\.Off|writeFCSR" sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/Unprivileged.scala sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala` | 不适用 | FCSR/rounding/flags/status 线索 | 路径可定位 | 已检查 CSR 信号和状态控制；未验证完整状态转换/异常行为 | none |
| E4 | C2；Kunminghu FP 测试边界 | test-inspected | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012` | `src/test/scala/xiangshan/DecodeTest.scala` | `sed -n '1,180p' sources/xiangshan/src/test/scala/xiangshan/DecodeTest.scala` | DecodeUnitTest/VerilatorBackendAnnotation | 仅 DecodeUnit 空闲时钟步进 | FP 输入与结果断言（若要作为 FP 行为验证） | 文件没有 FP stimulus 或 FP 结果断言；未运行 | none |
| E5 | C1/C3；Heliodor 标量 FP 与向量区分 | source | inspected | Heliodor `heliodor-master-20261012` | `src/core/decoder.veryl`、`fpu_wrap.veryl`、`lsu.veryl`、`alu_wrap.veryl`、`csr.veryl`、`src/pkg/fpu_pkg.veryl` | `rg -n "FpuOp::FADD|FpuOp::FCVT|FCVTMOD_W_D|FROUND|FLEQ|fflags|o_fflags|FP" sources/heliodor/src/core/decoder.veryl sources/heliodor/src/core/fpu_wrap.veryl sources/heliodor/src/core/lsu.veryl sources/heliodor/src/core/alu_wrap.veryl sources/heliodor/src/core/csr.veryl sources/heliodor/src/pkg/fpu_pkg.veryl` | 不适用 | 标量 S/D/H 与 Zfa 分支 | 源码路径/操作分发 | 已检查源代码；未运行仿真 | none |
| E6 | C2；Heliodor F/D/Zfhmin 测试材料 | test-inspected | unverified | Heliodor `heliodor-master-20261012` | `tb/test_arch_fp.veryl`、`tb/test_arch_common.veryl`、`tb/test_fp_*.veryl`；`test/riscv-arch-test/build/rv64uf/`、`rv64ud/`；`test/zfhmin/` | `rg --files sources/heliodor/tb sources/heliodor/test/riscv-arch-test/build/rv64uf sources/heliodor/test/riscv-arch-test/build/rv64ud sources/heliodor/test/zfhmin | rg 'test_arch_fp|test_arch_common|test_fp_|rv64u[fd]/|zfhmin'`；`rg -n "test_arch_rv64u[fd]_|test_arch_zfhmin|\$assert.*pass" sources/heliodor/tb/test_arch_fp.veryl sources/heliodor/tb/test_arch_common.veryl`；从项目仓库根目录（包含 `sources/heliodor/` 的工作目录）运行：`git check-ignore -v sources/heliodor/tb/test_arch_fp.veryl sources/heliodor/test/zfhmin/zfhmin_test.S` | 未运行 | rv64uf/rv64ud hex；Zfhmin asm/hex | harness 断言通过 | 具名输入/harness 存在且已检查；ignored；没有执行结果 | none |
| E7 | C2；Heliodor Zfa 测试材料 | test-inspected | unverified | Heliodor `heliodor-master-20261012` | `tb/test_arch_fp.veryl` 的 zfa_s1–s4 harness；`test/zfa/zfa_s1.S`…`zfa_s4.S` 与相应 hex | `rg -n "test_arch_zfa_s[1-4]|zfa_s[1-4]\\.hex|FROUND|FCVTMOD|FLEQ|FMINM" sources/heliodor/tb/test_arch_fp.veryl sources/heliodor/test/zfa`；`git check-ignore -v sources/heliodor/tb/test_arch_fp.veryl sources/heliodor/test/zfa/zfa_s1.S` | 未运行 | Zfa S1–S4 已有测试源/hex | harness pass 断言 | 只检查材料；ignored；没有执行结果 | none |

- 本单元没有 `test-run`、`experiment` 或 `run-pass` 证据。未检查/未运行的材料不能作为通过结论；不得据此推导 IEEE 754 全覆盖或 RVA23 符合性。

## 学习者总结

F、D、Zfhmin、Zfa 都有源码路径线索，但证据形态不同：Kunminghu 前端译码和 wrapper 可见，wrapper 指向的外部浮点库源码未包含在固定快照；Heliodor 能看到更多 FPU 分发逻辑，并有 ignored 的架构测试源和 hex 输入。Zfhmin 只要求半精度搬运与转换，不能将 H 算术混入这个要求；F/D/Zfa 的标量路径也不能由向量 FP 路径代证。所有测试材料均未运行，舍入、NaN-box、异常 flags、FS 状态和格式组合仍是明确的未验证边界。

## 未解问题

- Kunminghu wrapper 所调用的 fudian/yunsuan 内部实现不在固定快照中；需另有可信快照或可审阅源码才能继续核验。
- Heliodor ignored harness/输入材料的生成版本、完整刺激清单与运行配置尚未复核；当前只记录可见源码和文件。
- 两侧 F/D/Zfhmin/Zfa 的舍入模式、NaN-box、异常 flags、FS 关闭/脏状态及各格式组合均未系统验证。
- 是否需要运行 Heliodor 已有 harness 属于后续验证工作；本故事没有运行任何测试。
