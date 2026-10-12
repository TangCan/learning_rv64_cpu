---
unit_id: "rva23u64-vector-security-and-half"
stage_id: "Epic 4 / Story 4.5"
scope: "RVA23U64 必选 Zvfhmin、Zvbb、Zvkt 的规范范围及两套固定快照中已检查的源码、配置和定向验证材料；不代表完整覆盖或符合性验证。"
exclusions:
  - "不把基础 V 的参数/测试、标量 Zfhmin/Zbb/Zkt 或 Zvfh 算术证据替代三个向量要求。"
  - "未运行本单元所列测试；未执行全指令、全 SEW/EEW 或异常边界矩阵。"
  - "未发现 DIEL 形式/时序证据不等于证明实现中不存在此类证据，也不据此作符合性判断。"
spec_refs:
  - name: "RISC-V RVA23 Profile"
    edition: "v1.0, ratified"
    section: "§3.1.1.2 / Zvfhmin, Zvbb, Zvkt"
    profile_category: "mandatory"
  - name: "RISC-V V Standard Extension for Vector Operations"
    edition: "v1.0, ratified"
    section: "§30.18.4 / Zvfhmin"
    profile_category: "not-profile-specific"
  - name: "RISC-V Cryptography Extensions: Vector Instructions"
    edition: "v1.0, ratified"
    section: "§§31.2.1, 31.2.15 / Zvbb, Zvkt"
    profile_category: "not-profile-specific"
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

<!-- 本学习单元是范围有限的静态映射；证据 ID 与覆盖目录互相引用。 -->

## 单元自检

- **问题：** 为什么 Kunminghu 的 `FCVT_H_S`/`FCVT_S_H` 或 `rv64uzvfh` 测试清单不能单独证明 Zvfhmin？为什么功能测试也不能验证 Zvkt？
- **学习者答案：** Zvfhmin 的向量最小要求是 V v1.0 §30.18.4 中 `SEW=16` 的 `vfwcvt.f.f.v` 与 `vfncvt.f.f.w`；标量转换与 `Zvfh` 下更大的向量 H 算术范围是不同案例。功能测试只检查执行结果，不能证明列明指令的时延对数据操作数不变；Zvkt 需要有针对 DIEL 的形式化或时序证据。
- **检查类型：** explanation
- **证据 ID：** E2、E3、E6–E8

## 架构行为与子案例

RVA23U64 v1.0 §3.1.1.2 将 Zvfhmin、Zvbb、Zvkt 列为新增必选扩展。V v1.0 §30.18.4 的 Zvfhmin 定义只在 `SEW=16` 时启用 `vfwcvt.f.f.v`（binary16 转 binary32）及 `vfncvt.f.f.w`（binary32 转 binary16），并依赖 Zve32f；更完整的 `Zvfh` 才使多类浮点运算、归约和搬移可在 SEW=16 使用。Vector Crypto v1.0 §31.2.1 列出 Zvbb 的十类助记符/形式；§31.2.15.1 将所有 Zvbb 指令纳入 Zvkt 的 DIEL 要求。§31.1.4 说明向量密码指令 EEW=SEW；§31.2 总览规定 Zvbb 在 Zve32x 下支持 EEW 8/16/32，在 Zve64x 下另支持 EEW=64。Zvkt 也涵盖 §31.2.15.2–.14 所列的 Zvbc、整数加减与进位、比较、复制、扩展、逻辑、乘法/乘加、merge、permute、移位和 slide 指令。控制用途的 vrgather 索引及 vslide 位移豁免 DIEL；`vl`、`vtype`、mask、编码常量不属于数据操作数。存储、浮点、饱和加减、clip、compress、除法、average、mask 操作（含 `vcpop.m`）、min/max、multiply-saturate、reduce、shift-round、vset 明确不受 Zvkt 约束。本单元列明规范范围，不据此推断实现时延。官方来源：[RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)、[V v1.0 §30.18.4](https://docs.riscv.org/reference/isa/unpriv/v-st-ext)、[Vector Crypto v1.0 §§31.1.4、31.2、31.2.1、31.2.15](https://docs.riscv.org/reference/isa/v20250508/unpriv/vector-crypto.html)。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| Zvfhmin 转换集合 | unconfirmed | 需要 `SEW=16` 的 binary16↔binary32 两个转换；当前只见 Kunminghu 路由线索，Heliodor 的 FP 定向材料主要是 SEW=32/64，未验证目标 binary16 向量行为（E2、E5–E6）。 |
| Zvfh H 运算与 Zvfhmin 边界 | excluded | `Zvfh` 扩展额外包含 H 算术/归约/搬移；`scripts/xiangshan.py` 中 `rv64uzvfh-*` 镜像不作为 Zvfhmin 必需转换的测试结论（E3）。标量 Zfhmin 文件也不属于向量证据（E4）。 |
| Zvbb 指令集合 | unconfirmed | 规范列出 vandn、vbrev、vbrev8、vrev8、vclz、vctz、vcpop、vrol、vror、vwsll 及其形式；源码出现部分 BitPat/ALU 分支和 ACT unsupported 配置不能证明集合完整或语义正确（E1、E2、E4）。 |
| Zvbb EEW / SEW | unconfirmed | Vector Crypto §31.1.4 对所述向量密码指令规定 EEW=SEW；§31.2 的 Zvbb 概述允许 Zve32x 使用 EEW 8/16/32，Zve64x 另支持 EEW=64。两侧尚未逐项核验每条指令的译码、SEW/EEW 和全部配置（E1、E2、E7）。 |
| Zvkt DIEL 适用指令 | unconfirmed | 对已实现的列举指令要求 DIEL；部分控制值/指令字段、`vl`、`vtype`、掩码等按规范豁免，且某些操作（如所有存储与浮点、`vcpop.m`）明确不受其约束。Zvbb DIEL 集合为 vandn.v[vx]、vclz.v、vcpop.v、vctz.v、vbrev.v、vbrev8.v、vrev8.v、vrol.v[vx]、vror.v[vxi]、vwsll.[vv,vx,vi]；此外还包括规范列出的基础 V 整数操作。`vl`、`vtype`、mask 与指令编码常量不属于数据操作数，vrgather 的索引和 vslide 的位移还按条款豁免；存储、浮点、`vcpop.m` 等不受 Zvkt 约束。完整范围见 §31.2.15；译码/功能结果不证明时延属性（E1、E7）。 |
| DIEL 证据 | unconfirmed | 未检查到能建立输入数据与执行延迟无关性的本轮形式化或时序证据；ACT 配置及普通功能断言仅支持其配置/功能测试声明（E4、E7）。 |
| 本轮测试运行 | excluded | 本轮只静态检查源码、配置和测试文件；所有上游定向测试均未运行，无 `run-pass`/`run-fail` 证据（E3–E6）。 |

## Kunminghu 路径

- **阶段与状态变化：** `Parameters.scala` 的 ISA 名称列表包含 `zvbb`、`zvfh`、`zvfhmin`、`zvkt`；这是名称声明。`Instructions.scala` 的 `object Zvbb` 定义一组编码 BitPat。`VecDecoder.scala` 在 OPIVV/OPIVX/OPIVI/OPMVV 等表中可见 VANDN、旋转、VWSLL、VBREV、VCLZ、VCTZ、VCPOP 等代表性 Zvbb 分派至 vector ALU/整数单元。浮点 decoder 中可见 widening/narrowing 转换路径及对 H 标量 FP 的 `VSew.e16` 控制线索。以上只证明已观察到的参数名、译码模式和控制线索，不证明每个 Zvbb 操作端到端实现，也不验证 SEW=16 的 Zvfhmin 转换结果或任何 DIEL 属性（E1–E2）。
- **源码位置：** 固定快照 `src/main/scala/xiangshan/Parameters.scala`、`backend/decode/Instructions.scala`、`backend/decode/VecDecoder.scala`、`backend/decode/FPDecoder.scala`（E1–E2）。
- **相关验证：** `scripts/xiangshan.py` 的镜像列表含大量 `rv64uzvfh-*` 向量 FP 文件，但它们标记为 Zvfh 并涉及更广 H 功能，不能直接当作 Zvfhmin 测试已通过或本轮运行（E3）。已检查 `src/test/scala` 中向量测试文件名/相关入口；本次未定位专门的 Zvbb/Zvfhmin 语义测试。对全树 DIEL/constant-time/formal/latency 搜索未发现对应契约证据；搜索范围结果不证明不存在（E7）。

## Heliodor 路径

- **阶段与状态变化：** `vector_unit.veryl` 含向量执行的半字节/元素布局、SEW=16 整数向量算术和一般 FP widening/narrowing 运算单元线索。FP 路径测试/注释所示主要例子是 SEW=32/64；这些不能确认 IEEE binary16 `SEW=16` `vfwcvt.f.f.v`/`vfncvt.f.f.w`。执行单元可见 `vcpop.m` 等路径，但它是基础 V 的 mask 归约，不等于 Zvbb 的 vector-element `vcpop.v`，也不代表完整 bitmanip 集合。`sail.json` 分别将 Zvfhmin、Zvbb、Zvkt 的 `supported` 置为 false；这只陈述 ACT 配置元数据，不单独判定实际 RTL 的存在或合规性（E4–E5）。
- **源码位置：** 固定快照 `src/core/vector_unit.veryl`；配置 `test/act/config/heliodor/sail.json`（E4–E5）。
- **相关验证：** 检查 `test/vfarith/vfarith_test.S` 的 FP 算术和 SEW=32/64 转换案例、`test/vnarrow/vnarrow_test.S` 的整数 `vnsrl`/`vnsra` 窄化案例；未见这些材料测试 Zvfhmin 的 binary16↔binary32 转换。ACT 中 `rv64uzbb` 预构建镜像是标量 Zbb，不能作为 Zvbb；本轮未发现 Zvbb 定向程序。现有 `vfarith` 的 `vcpop.m` 也不是 Zvbb `vcpop.v`。材料均未执行（E6）。全树搜索未发现 DIEL 断言、形式模型或时序验证材料；这不是实现不存在的证明（E7）。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧可观察到不同强度的半精度/向量操作源码线索；Kunminghu 有 decoder/ISA 名称和 FP16 控制线索，Heliodor 有一般向量 FP 逻辑，但 ACT 把 Zvfhmin 配置为 unsupported。两者均未提供本轮 Zvfhmin 转换运行结果。 | E1–E3 | E4–E6 |
| C2 | Kunminghu 明确列出多种 Zvbb BitPat 和 decoder 路由；Heliodor 有有限位操作/向量路径及 ACT unsupported 元数据。局部译码/执行或标量 Zbb 材料都不能代表完整 Zvbb。 | E1–E2 | E4–E6 |
| C3 | 没有证据支撑两边的 Zvkt DIEL 契约。配置、译码存在、功能正确性测试与普通流水线延迟描述均不能替代对数据操作数的时序或形式证明。 | E2、E7 | E4、E7 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/main/scala/xiangshan/backend/decode/Instructions.scala` 的 `Zvbb` BitPat；`VecDecoder.scala` Zvbb 注释及 OPIVV/OPIVX/OPIVI/OPMVV 表；`Parameters.scala` ISA 名称声明 | not-run | 固定 sources.lock 快照 | BitPat 定义包含 vandn.vv/vx、vbrev.v、vbrev8.v、vrev8.v、vclz.v、vctz.v、vcpop.v、vrol.vv/vx、vror.vi/vv/vx、vwsll.vi/vv/vx；VecDecoder 可见部分 vv/vx/vi 路由（不据此称完整端到端实现） | 源码能确认具体 pattern/route | 已检查静态源码；未验证完整集合及执行语义 | none |
| E2 | C1、自检 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `VecDecoder.scala` 的 `VFWCVT_F_F_V`/`VFNCVT_F_F_W` 向量转换 decoder routes；`FPDecoder.scala` FP16、SEW e16 控制及 `FCVT_H_S`/`FCVT_S_H` 等标量路由；`Parameters.scala` 扩展名 | not-run | 固定 sources.lock 快照 | half-FP 转换 decoder 线索及向量/标量路径边界 | 区分路由线索与 Zvfhmin 架构所需两个向量转换 | 只观察到路由/控制线索；没有本轮行为结果或 DIEL 证据 | none |
| E3 | C1、自检 | test-inspected | unverified | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `scripts/xiangshan.py` lines 442–510 的 `rv64uzvfh-p-vfncvtff.bin`、`rv64uzvfh-p-vfwcvtff.bin` 镜像名称（不等同 Zvfhmin）；`ByteMaskTailGenTest` 与 `VsetModuleMain` 只作为基础向量 mask/tail 与 vtype 行为的测试材料，不是 Zvbb/Zvfhmin 专项测试 | not-run | 上游镜像条目 | 镜像名称含 `zvfh`，并含广泛 vector FP 案例 | 只按清单识别测试域，不将 Zvfh 镜像等同 Zvfhmin 案例 | 清单/测试材料已检查；无本轮运行结果，亦未定位专门 Zvfhmin/Zvbb 测试入口 | none |
| E4 | C1–C3 | source | inspected | Heliodor / `heliodor-master-20261012` | `src/core/vector_unit.veryl` 的 FP、SEW/ALU 路径（含 `h_is_vcpop`/`vcpop.m` mask reduction） | not-run | 固定 sources.lock 快照 | 一般向量 FP、有限位操作；区分 `vcpop.m` 与 `vcpop.v` | 只记录可见源码子集 | 静态检查源码路径；没有逐指令完整范围或时延证明 | none |
| E5 | C1–C3 | source | inspected | Heliodor / `heliodor-master-20261012` | `test/act/config/heliodor/sail.json:647-679` 的 `Zvfhmin`、`Zvbb`、`Zvkt` 配置项（ACT 使用的 Sail 参考模型能力声明，字段 `supported: false`） | not-run | ACT Sail config | 三项各 `supported: false` | 作为 ACT 元数据记录 | 已检查配置字段；不据此单独推断 RTL 缺失/不合规 | none |
| E6 | C1–C2、自检 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vfarith/vfarith_test.S` §V3j（SEW=32→64 widen convert）及 §V4h（SEW=64→32 narrow convert）；`test/vnarrow/vnarrow_test.S` 的 SEW=16 `vnsrl/vnsra` 整数案例；`test/riscv-arch-test/build/rv64uzbb/binvi.hex` | not-run | 定向 FP 测试 / ACT 已构建镜像 | vfarith §V3j/V4h 为单/双 FP 转换，vnarrow 为 32→16 位整数窄化；rv64uzbb/binvi 为标量 Zbb | 只说明检查过的不同测试域 | 不是 Zvfhmin binary16 转换、Zvbb vector cases 或本轮通过结果 | none |
| E7 | C3、自检 | source | inspected | 两项目 / 对应 `sources.lock` snapshot | `rg -n` 文本搜索 `sources/xiangshan/src/main/scala`、`src/test/scala`、`sources/heliodor/src/core`、`test`，词组 `zvfhmin|zvbb|zvkt|data.independent|constant.time|DIEL|formal|assert|cover|latency|timing`；另检查 `sail.json` 配置 | not-run | 固定源码快照 | 查找可证明数据操作数不影响执行时延的证据 | 需要可复查的时序/形式证据；译码/功能测试不充分 | 未发现可证明数据操作数时延无关的实现证据；该全树搜索只能说明本次搜索未命中，不能证明其不存在 | none |
| E8 | 规范边界、自检 | spec | inspected | RISC-V RVA23 v1.0、V v1.0、Vector Crypto v1.0 | RVA23 §3.1.1.2；V §30.18.4；Vector Crypto §§31.1.4、31.2、31.2.1、31.2.15 | not-run | 已 ratify 规范文本 | 必选项、binary16 conversions、Zvbb 列表/EEW 与 Zvkt DIEL 范围/豁免 | 各结论按指定条款限定 | 已检查规范定义；这不是实现验证 | none |

## 学习者总结

RVA23U64 把 Zvfhmin、Zvbb、Zvkt 分别列为必选项，但它们的证据类型和架构范围不同。Zvfhmin 只把两条向量 FP 转换扩展到 SEW=16；`Zvfh` 的 H 算术不是其最小要求。Zvbb 有一份明确的 vector bitmanip 指令集合及 EEW 条件；只看标量 Zbb 或部分 V decoder 不足以证明集合齐备。Zvkt 对其列表中已实现操作数施加 DIEL 要求，并定义控制值豁免和明确排除项，因此功能结果、配置支持声明或存在固定延迟的局部代码都不能代替时序/形式验证。Kunminghu 有较多静态 decoder 线索；Heliodor ACT 配置把三项标为 unsupported，并有一般向量 FP/位操作测试材料，但这些材料未在本轮运行。三个扩展在两侧都没有本轮端到端验证或 DIEL 证明。

## 未解问题

- 未逐条核验 Kunminghu Zvbb BitPat、Vector ALU 数据路径与各 EEW/SEW 合法编码的对应关系。
- 未确认 Kunminghu 半精度转换的 FP datapath 在 SEW=16 时是否支持所需 binary16 向量案例；ISA 名称和 decoder 控制路径只是线索。
- 未检查 Heliodor 更广 RTL/生成配置对 ACT unsupported 的覆盖含义；配置声明不可扩写为完整 RTL 结论。
- 未找到或运行两侧 Zvfhmin/Zvbb 专项验证，也未获得 Zvkt DIEL 时序或形式证明。
