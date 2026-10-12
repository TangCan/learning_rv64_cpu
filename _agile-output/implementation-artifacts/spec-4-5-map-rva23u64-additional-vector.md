---
title: 'Story 4.5: 映射 RVA23U64 其他向量必选项'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '7f06220415280aac786fa4ef1836f4b1df41206e'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-4-map-rva23u64-base-vector.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23U64 将 `Zvfhmin`、`Zvbb` 与 `Zvkt` 列为新增向量必选项，但目录尚未区分半精度最小转换、向量位操作和数据无关延迟三种要求的实现与证据。

**Approach:** 依据 RVA23 Profile v1.0 及各扩展 ratified 文本，分别检查两套固定快照中的源码、配置声明和测试材料，更新三个稳定键并记录已观察子集、未核实内容及测试状态。

## Boundaries & Constraints

**Always:** 分开映射 `Zvfhmin`、`Zvbb`、`Zvkt`，分别记录两侧位置、理由、子案例和证据；标量 Zfhmin/Zbb/Zkt 证据不得替代向量要求；对 constant-time/DIEL 只以时序或形式化证据支撑，配置声明、译码存在和功能测试不构成该证明。

**Never:** 不修改上游快照；不把基础 V 的覆盖外推至三个扩展；不将 `Zvfh` 的半精度算术当作 `Zvfhmin` 必需范围；不因搜索不到某项断言就判实现不存在或不合规。

## Code Map

- `notes/rva23-coverage.md`：只更新 RVA23U64 §3.1.1.2 的 `Zvfhmin`、`Zvbb`、`Zvkt` 三行；保持 V 基础行和其他要求不变。
- `notes/units/rva23u64-vector-v1.md`、`notes/templates/learning-record.md`、`notes/units/index.md`：承接 Epic 4 的证据字段与分层方式；建立本故事独立版本学习单元。
- 规范：[RVA23 Profile v1.0 §3.1.1.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)；[V v1.0 §30.18.4](https://docs.riscv.org/reference/isa/unpriv/v-st-ext)；[Vector Crypto v1.0 §32.1.2.1、§32.1.2.15](https://docs.riscv.org/reference/isa/v20250508/unpriv/vector-crypto.html)。记录 `Zvfhmin` 在 `SEW=16` 定义的窄化/宽化 FP 转换，`Zvbb` 的指令集合及 EEW 条件，`Zvkt` 对所列已实现指令的数据无关执行延迟契约；不等同扩展名到位即证明行为成立。
- Kunminghu 固定快照：`backend/decode/VecDecoder.scala` 的 FP 转换路由与 `Zvbb` opcode，`Instructions.scala` 的指令模式，`FPDecoder.scala` 的 FP16/SEW 线索，`Parameters.scala` 的 ISA 名称声明。检查 `src/test/scala`、`scripts/xiangshan.py` 所列测试镜像和全树形式化/延迟搜索；`Zvfh` 测试材料不得直接代表 `Zvfhmin`。
- Heliodor 固定快照：`src/core/vector_unit.veryl` 的 FP SEW、向量 ALU 与执行子集，`test/act/config/heliodor/sail.json` 的特性配置；检查 vector FP、bitmanip 测试及 assertion/formal/时序材料。标量 ACT 与预构建 `rv64uzbb` 文件不作为 Zvbb 证据。
- 只读快照由 `sources.lock` 固定。上游配置和测试声明只作为对应类型的证据，不视为本轮运行结果。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 独立填写三项 U64 行的双侧状态、位置、理由、子案例和证据；S64 继承行不在本故事修改。
- [x] `notes/units/rva23u64-vector-security-and-half.md` — 记录规范版本、三项的准确范围、两侧实现线索/测试材料、DIEL 证明边界及未覆盖项。
- [x] `notes/units/index.md` — 添加学习单元索引及准确的验证状态。

**Acceptance Criteria:**
- Given RVA23U64 的三个向量必选键，when 查看覆盖目录，then 每项均有独立的两侧状态、路径、子案例和证据链接。
- Given `Zvfhmin`、`Zvbb`、`Zvkt` 的不同语义，when 查看学习单元，then 半精度转换、位操作集合、DIEL 指令适用范围和基础 V/标量扩展边界分别清晰。
- Given 配置文件、译码表、功能测试或历史记录，when 评估实现结论，then 只声明其直接支持的事实；缺少时序/形式证明时，`Zvkt` 保持未验证。
- Given 测试材料，when 更新证据表，then 区分源码检查、上游配置、已检查测试和本轮实际运行，不把未运行材料记为通过。

</frozen-after-approval>

## Implementation Notes

预期证据强度不同：Kunminghu 有部分 `Zvbb`/half-conversion 译码，但缺少本轮动态和 DIEL 属性证明；Heliodor ACT 元数据将三项标为 unsupported，并有标量与向量测试的边界线索。所有状态应严格限定到固定快照中可见材料，不能把 negative search 当作不存在的证明。


## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Spec was `in-review` while sprint status still said `in-progress`. | low / patch | Step 5 transition synchronized `4-5-映射-rva23u64-的其他向量必选项` to `review`; tracker and spec now agree on review readiness. |
| Index wording could imply the story itself was done when only the learning record was complete. | low / patch | Changed the index status to say the unit record is established and separately list its verification gaps. |
| E3/E6 did not identify the exact inspected test cases. | low / patch | Recorded the `rv64uzvfh` conversion image names, `vfarith` V3j/V4h, `vnarrow` SEW=16 integer cases and scalar `rv64uzbb/binvi` boundary. |
| E7 did not make the negative search reproducible. | low / patch | Added the searched source/test directories and representative literal search terms; kept the caveat that no hit does not prove absence. |
| The self-check's cited IDs did not map each half, test, and DIEL claim to its evidence rows. | low / patch | Narrowed the self-check references to E2, E3, E6–E8 and aligned evidence-table self-check labels to the supported claims. |
| Half-FP scalar paths could be mistaken for vector Zvfhmin support. | low / patch | Coverage and E2 now explicitly label `FCVT_H_S`/`FCVT_S_H` as scalar and separately name `VFWCVT_F_F_V`/`VFNCVT_F_F_W` vector decode routes, while keeping SEW=16 behavior unverified. |
