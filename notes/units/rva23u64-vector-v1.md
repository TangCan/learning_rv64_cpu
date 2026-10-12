---
unit_id: "rva23u64-vector"
stage_id: "Epic 4 / Story 4.4"
scope: "RVA23U64 必选 V 的参数、代表性译码/执行/状态/访存线索及已检查定向材料；不作为完整指令或符合性验证。"
exclusions:
  - "未逐条检查 V v1.0 指令全集、所有 SEW/LMUL/VLEN/ELEN 组合及全部异常、访存排序和重启行为。"
  - "Zvfhmin、Zvbb、Zvkt 专属要求不计入本单元；向量浮点路径也不替代标量 F/D 证据。"
  - "本轮未运行下列上游测试；历史文档中的仿真 PASS 不视为本轮实测。"
spec_refs:
  - name: "RISC-V RVA23 Profile"
    edition: "v1.0, ratified"
    section: "§3.1.1.2 / V"
    profile_category: "mandatory"
  - name: "RISC-V V Standard Extension for Vector Operations"
    edition: "v1.0, ratified"
    section: "Standalone V v1.0 PDF §§2, 3.1–3.7, 4.5, 5.3–5.4, 6.1–6.3, 7.4, 7.7–7.8, 8–9, 17.1"
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

## 单元自检

- **问题：** VLEN=128、SEW=32、LMUL=1 时 VLMAX 是多少？仓库中的定向检查能说明哪些结论？
- **学习者答案：** VLMAX = LMUL × VLEN / SEW = 4。现有 vsetvl/vadd 定向材料可检查其特定配置与算术结果的断言设计；由于没有在本轮运行，它们不能证明该结果已通过，更不能证明全部参数与 V 指令均满足规范。
- **检查类型：** explanation
- **证据 ID：** E1、E2、E5、E6a–E6c

## 架构行为与子案例

RVA23U64 v1.0 §3.1.1.2 将 V 列为必选扩展。RISC-V V v1.0 standalone PDF §2 规定实现参数约束（ELEN 至少 8、为 2 的幂；VLEN 至少 ELEN、为 2 的幂且不超过 2^16）；本次还核对 §§3.1–3.7（寄存器、状态、vtype、vl、vlenb、vstart）、§4.5（mask 布局）、§5.3–5.4（mask 与元素类别/tail）、§6.1–6.3（配置指令与 vl 约束）、§7.4/§7.7/§7.8（unit-stride、fault-only-first、segment 访存）、§8–9（对齐/一致性）及 §17.1（precise traps）。这些是定向规范范围，不代表逐条检查了全部 V 指令语义。

官方文本：[RVA23 Profile v1.0 §3.1](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)；[RISC-V V Extension v1.0 standalone PDF](https://docs.riscv.org/reference/isa/extensions/vector/_attachments/riscv-v-spec.pdf)。规范范围限于前述明确列出的 PDF 条款。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| VLEN/ELEN | unconfirmed | Kunminghu 默认参数 128/64 且由参数传递；Heliodor 固定 128/64。仅检查配置线索，未核对 profile 允许组合全集（E1、E2）。 |
| SEW/LMUL、vtype/vl | unconfirmed | 检查 vset 解码、vtype 字段与 Heliodor VSET 案例；不能外推所有合法/非法设置及 AVL 特殊情况（E1、E2、E5）。 |
| vstart、vlenb 与向量状态 | unconfirmed | 两侧可见相应状态/CSR 线索；没有本轮对陷阱重启、状态使能、所有 CSR 读写语义的验证（E1、E2）。 |
| mask/tail | unconfirmed | Kunminghu 有 vma/vta 字段与访存掩码接口线索；Heliodor 的 vmem 源码材料含 masked store 与 sentinel 断言。tail 的全部 agnostic/undisturbed 组合及算术结果未验证（E1、E2、E6a）。 |
| 指令译码与执行 | unconfirmed | 检查 VSET、VADD、VRGATHER 等代表性路径；非完整 V 指令矩阵，也不包含 Zvfhmin/Zvbb/Zvkt 的专属要求（E1、E2）。 |
| 向量访存 | unconfirmed | 检查 unit-stride/segment/fault-only-first 等接口或测试刺激；stride/indexed/whole-register、对齐、异常优先级、重启等行为未完整检查（E1、E2、E6a–E6c）。 |
| 本轮动态结果 | excluded | 没有执行测试，不存在本轮 run-pass/run-fail 证据。上游历史 PASS 仅作为其原文记录（E7）。 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit.scala` 将 `VecDecoder.table` 并入译码表；`VecDecoder.scala` 给出 VSET、VADD、VRGATHER 等架构操作映射，并使用内部 `VLD`/`VST` decode/FU 标签表示向量 load/store 路由（它们不是 ISA 助记符，架构助记符如 `vle32.v`/`vse32.v`）。`Parameters.scala` 默认 `VLEN=128`、`ELEN=64`，并允许参数化；向量 `Bundles.scala` 表达 `vill/vma/vta/vsew/vlmul`。`Unprivileged.scala` 将只读 `vlenb` 初始化为 `VLEN/8`。`mem/vector/` 中 `VecCommon.scala`、`VecBundle.scala` 等呈现 VLSU 数据、掩码及拆分/合并接口。它们是源码线索，不是逐项架构语义证明（E1）。
- **源码位置：** 固定快照下 `src/main/scala/xiangshan/backend/decode/{DecodeUnit.scala,VecDecoder.scala}`、`Parameters.scala`、`backend/fu/vector/Bundles.scala`、`backend/fu/NewCSR/Unprivileged.scala`、`mem/vector/VecCommon.scala` 与 `VecBundle.scala`（E1）。
- **相关验证：** `src/test/scala/xiangshan/backend/fu/VsetTop.scala` 将输入配置接入 VSET datapath；`VsetModuleMain.scala` 对 `vill/vta/vma/vsew/vlmul`、函数种类、AVL 与 oldVL 做组合输入，调用 `VsetRef.test` 计算期望，并用多个输出 `expect` 比较；`VsetRef.scala` 的模型固定 VLEN=128/ELEN=64。harness 内仍有 oldVType.vill/ratio change 的 TODO，且测试模块不是完整指令级 V 验证。本轮未运行（E3）。

## Heliodor 路径

- **阶段与状态变化：** `decoder.veryl` 的 `OP_V` 分支将配置、整数向量算术等有限子集派发为 `VecOp`，其它编码可能走 illegal 分支；`heliodor_core.veryl` 实例化 VRF/VU 并串接向量派发/提交路径。`vector_pkg.veryl` 固定 VLEN=128、ELEN=64、VLENB=16 及 32 个向量寄存器；`vrf.veryl` 定义 32×VLEN 存储结构。`csr.veryl` 包含 vstart/vxsat/vxrm/vcsr/vl/vtype/vlenb 状态线索。`vector_unit.veryl` 覆盖其实现子集中的配置、算术、访存和提交行为；这些源文件说明实现范围受阶段/子集限制，不代表完整 RVV（E2）。
- **源码位置：** 固定快照下 `src/core/{decoder.veryl,heliodor_core.veryl,vector_unit.veryl,vrf.veryl,csr.veryl}` 与 `src/pkg/vector_pkg.veryl`（E2）。
- **相关验证：** 检查了 `test/vadd`、`test/vsetvl` 的材料见 E4–E5。访存材料按程序分别记录：E6a `test/vmem/vmem_test.S` 中 `vle32.v`/`vse32.v` 后的 loadback 比较检查 unit-stride 数据，fail10–fail13 比较 masked `vse32.v` 后 active 元素写入值与 inactive 元素 sentinel 保留；E6b `test/vseg/vseg_test.S` 中 fail3–fail7 检查 `vlseg2e32.v` 拆分顺序，fail8–fail11 检查 `vsseg2e32.v` 交错顺序，fail12–fail15 检查 `vlseg3e32.v` 字段元素；E6c `test/vleff/vleff_test.S` 中 fail3 检查无故障时 `vl` 保持 16，fail6 检查跨页 element 8 故障后 `vl=8`，fail7–fail9 检查已加载前缀/trim 后范围及 element 8 sentinel 未写，trap handler 以 99 标记非预期陷阱。各目录 Makefile 的构建配置为 `-march=rv64gcv_zicsr -mabi=lp64d`。上述只是已检查的测试刺激/断言，不是运行结果。

## 本轮运行边界

已检查可用的定向入口，但运行器不可用：当前环境的 command -v veryl 与 command -v mill 均无结果，因此无法执行 Heliodor 的 veryl test --test test_arch_vadd 或 Kunminghu 的 mill XiangShan.test.testOnly xiangshan.backend.fu.VsetModuleMain。本轮未安装新工具链；Heliodor Makefile 只生成测试 hex，不会执行设计仿真。故没有本轮动态结果，相关 evidence 保持 unverified。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两侧均有基础 V 参数、状态及操作路径线索；Kunminghu 默认 128/64、可参数化，Heliodor 固定 128/64。参数证据不表示覆盖所有规范允许组合。 | E1 | E2 |
| C2 | Kunminghu 材料聚焦 VSET 模块输入/参考输出比较；Heliodor 定向程序触及算术、配置、掩码和多类访存子案例。两侧材料均未在本轮运行，广度差异也不代表完整覆盖。 | E3 | E4–E6c |
| C3 | 本轮只记录已检查的局部证据；不对完整 opcode、异常/重启、全部掩码与 tail 组合或 RVA23 符合性作结论。 | E1、E3 | E2、E4–E6c、E7 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | C1、C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012` | 上述 DecodeUnit、VecDecoder、Parameters、Bundles、Unprivileged、mem/vector 源码 | not-run | 默认 VLEN=128、ELEN=64；源码参数可配 | VSET/VADD/VRGATHER 映射及内部 VLD/VST load/store 路由标签（非 ISA 助记符）；vtype/vlenb/VLSU 接口 | 源码中可定位这些参数与路径 | 已检查源码定义和连接线索；未生成硬件或执行向量指令 | none |
| E2 | C1、C3 | source | inspected | Heliodor / `heliodor-master-20261012` | 上述 decoder/core/vector_unit/vector_pkg/vrf/csr 源码 | not-run | 固定 VLEN=128、ELEN=64、32 个寄存器 | OP_V、VecOp、CSR、VRF/VU 与向量访存路径 | 源码呈现有限译码/执行和架构状态线索 | 已检查声明和逻辑；未证明完整 V 语义 | none |
| E3 | C2、C3、自检 | test-inspected | unverified | Kunminghu / `xiangshan-kunminghu-v2-20261012` | `src/test/scala/xiangshan/backend/fu/{VsetTop.scala,VsetModuleMain.scala,VsetRef.scala}` | not-run | 组合输入的 VSET 函数、vill/vta/vma/vsew/vlmul、AVL 与 oldVL；参考模型固定 VLEN=128/ELEN=64 | VsetRef 计算期望并由 expect 比较输出字段；保留 oldVType.vill/ratio TODO，不是完整 V 测试 | 输出匹配参考预期 | 仅检查到 harness 刺激与 expect；未运行 | none |
| E4 | C2、自检 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vadd/{Makefile,vadd_test.S}` | not-run；Makefile 定义交叉编译/hex 生成入口 | `-march=rv64gcv_zicsr -mabi=lp64d` | `vsetvli`、vadd.vx/vv/vi、`vmv.x.s`、vl/结果分支比较 | tohost=1 表示程序自述 PASS | 源级断言已检查；没有本轮运行结果 | none |
| E5 | C2、自检 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vsetvl/{Makefile,vsetvl_test.S}` | not-run；Makefile 定义交叉编译/hex 生成入口 | `-march=rv64gcv_zicsr -mabi=lp64d`；注释 VLEN=128 | register vsetvl 的 e16/e32/e64、m1/m2、AVL clamp、vle32 读取 | 各比较通过后 tohost=1 | 源级输入及分支比较已检查；无动态观察 | none |
| E6a | C2、C3 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vmem/vmem_test.S`（unit-stride load/store；fail10–fail13 masked store checks）及 `test/vmem/Makefile` | not-run；Makefile 仅定义交叉编译/hex 生成入口 | `-march=rv64gcv_zicsr -mabi=lp64d` | `vle32.v`/`vse32.v` 的 loadback；active masked store 写入与 inactive 元素 sentinel 保留 | 指定比较不分支到 fail 标签 | 已检查对应指令、loadback 与 fail 分支；未执行 | none |
| E6b | C2、C3 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vseg/vseg_test.S`（fail3–fail7、fail8–fail11、fail12–fail15）及 `test/vseg/Makefile` | not-run；Makefile 仅定义交叉编译/hex 生成入口 | `-march=rv64gcv_zicsr -mabi=lp64d` | `vlseg2e32.v` deinterleave、`vsseg2e32.v` interleave、`vlseg3e32.v` 字段顺序 | 读回值与每个 `bne` 的预期值一致 | 已检查各子测试比较与 fail 分支；未执行 | none |
| E6c | C2、C3 | test-inspected | unverified | Heliodor / `heliodor-master-20261012` | `test/vleff/vleff_test.S`（fail3、fail6–fail9、trap handler）及 `test/vleff/Makefile` | not-run；Makefile 仅定义交叉编译/hex 生成入口 | `-march=rv64gcv_zicsr -mabi=lp64d`；程序配置 Sv39 unmapped page | 无故障时 vl=16；element 8 fault 后 trim 到 vl=8、检查前缀和 sentinel，意外 trap 写 99 | 对应 `bne` 不跳 fail；无意外 trap | 已检查断言/陷阱处理；未执行 | none |
| E7 | C3 | design-doc | inspected | Heliodor / `heliodor-master-20261012` | `doc/phase12_v0_sim_segfault.md`（包括其中记录的历史运行命令与 PASS） | not-run | 上游文档记载的历史环境 | 文档记载 V0 `test_arch_vadd` 在各后端 PASS 及 V=0 回归结果 | 仅按上游文档原意作为历史记录 | 未复跑；不是本轮测试结果，不外推至当前实现或完整 V | none |
| E8 | C1、C3 | spec | inspected | RISC-V RVA23 Profile v1.0；RISC-V V Extension v1.0 standalone PDF | 官方 RVA23 §3.1.1.2/V；V v1.0 PDF §§2, 3.1–3.7, 4.5, 5.3–5.4, 6.1–6.3, 7.4, 7.7–7.8, 8–9, 17.1 | not-run | ratified 规范文本 | V 参数约束及架构状态/行为范围 | RVA23U64 要求 V；V 1.0 定义参数和指令架构行为 | 已检查官方规范内容；非实现验证 | none |

## 学习者总结

RVA23U64 把 V 列为必选扩展，但源码中出现 V 解码、固定参数或某个向量程序，只能支持有边界的映射结论。Kunminghu 给出可参数化的 VLEN/ELEN 默认值、译码/VSET/CSR/VLSU 线索和 VSET 参考比较 harness；Heliodor 采用固定 128/64 参数，并有若干手写测试程序覆盖配置、算术及特定访存行为。现有材料均未在本轮运行，所有动态结果仍未验证。完整 V 指令、所有参数组合、异常与重启细节、掩码/tail 全组合以及符合性仍在未核验范围；Zvfhmin、Zvbb、Zvkt 另行映射。

## 未解问题

- 未确认 Kunminghu 参数化配置实际覆盖范围，以及全部 SEW/LMUL 与非法 vtype 行为。
- 未逐项检查任一实现的全部 V 1.0 指令族、异常优先级、`vstart` 重启/中断行为、访存 ordering 和所有 tail/mask 组合。
- 未运行 Kunminghu VSET harness 或 Heliodor 定向测试，无法给出本轮动态结果。
- V 之外的 Zvfhmin、Zvbb、Zvkt 专属要求由后续独立映射处理。
