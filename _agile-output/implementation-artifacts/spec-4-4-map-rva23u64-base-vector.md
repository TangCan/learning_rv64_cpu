---
title: 'Story 4.4: 映射 RVA23U64 基础向量要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '716b3c08ed633e33b0bea97a8b0cf4b54fbf4b8d'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-3-map-rva23u64-floating-point.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23U64 将基础向量扩展 V 列为必选项，但覆盖目录尚未说明两套 CPU 的向量参数、状态、指令路径和证据边界。

**Approach:** 按 RVA23 Profile v1.0 的 V 稳定键追踪固定快照中代表性的译码、执行、寄存器/状态及访存路径，记录 V 的实现参数和检查过的验证材料，并保留未核验行为。

## Boundaries & Constraints

**Always:** 分别记录 Kunminghu 与 Heliodor 的源码、可见子案例、参数和证据；明确区分检查过的材料、历史记录与本轮实际运行；不得将部分 opcode、默认配置或上游历史 PASS 写成 RVA23 完整覆盖证明。

**Never:** 不修改上游快照；不把 `Zvfhmin`、`Zvbb`、`Zvkt` 的专属覆盖并入基础 V 结论；不宣称完整指令矩阵、所有参数组合或符合性已经验证。

## Code Map

- `notes/rva23-coverage.md`：只填 RVA23U64/V 一行；同一 V 项在 RVA23S64 继承行暂留后续特权域故事处理。
- `notes/units/rva23u64-floating-point-v1.md`：承接标量与向量浮点边界；向量 VFU/VFPU 证据不能代替标量 F/D 证据。
- `notes/templates/learning-record.md` 与 `notes/units/index.md`：复用证据字段、快照和索引约定。
- 规范：RVA23 Profile v1.0 §3.1.1.2/V；RISC-V V Extension v1.0，以官方 V v1.0 定义核对基础 V 的参数约束和架构状态；重点关注 VLEN/ELEN、SEW/LMUL、vtype/vl/vstart、mask/tail、异常与向量访存等适用行为，不复制规范全文。对未逐项审阅的指令族明确写出范围。
- Kunminghu 固定快照：`sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala` 的 `VecDecoder.table` 接入；`backend/decode/VecDecoder.scala` 的 VSET、VLD/VST、VADD 与 VRGATHER 示例；`Parameters.scala` 的默认 VLEN/ELEN；`backend/fu/vector/Bundles.scala` 的 vtype 字段；`backend/fu/NewCSR/Unprivileged.scala` 的 vlenb；`mem/vector/` 的 VLSU 接口。测试材料：`src/test/scala/xiangshan/backend/fu/VsetTop.scala`、`VsetModuleMain.scala`；核对 harness 输入、参考模型比较和已有结果，不将 VSET 单测外推为完整 V 验证。
- Heliodor 固定快照：`src/core/decoder.veryl` 的 OP_V 路径；`heliodor_core.veryl` 的 VRF/VU 实例化与 FIFO dispatch；`vector_unit.veryl` 的配置状态、向量访存与执行路径；`vector_pkg.veryl`、`vrf.veryl` 的固定参数/寄存器结构；`csr.veryl` 的向量 CSR。定向材料见 `test/vadd`、`test/vsetvl`、`test/vmem`、`test/vseg`、`test/vleff` 等；文档 `doc/phase12_v0_sim_segfault.md` 及其它计划/README 中的 PASS 仅作为上游历史记录。核实测试材料的配置、刺激与断言，并避免将有限案例外推。
- 快照由 `sources.lock` 固定；不得把历史文档中的仿真结果记为本轮实测。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 填写 V 行两侧状态、参数、范围理由、已观察子案例和证据链接；保持 Zvfhmin/Zvbb/Zvkt 行不变。
- [x] `notes/units/rva23u64-vector-v1.md` — 新建学习单元，记录规范范围、参数、代表性译码/执行/状态/访存路径、掩码与 tail、异常/访存子案例、测试材料和未核验边界。
- [x] `notes/units/index.md` — 增加 V 学习单元入口并准确说明本轮验证状态。

**Acceptance Criteria:**
- Given RVA23U64/V，when 查看覆盖目录，then 可分别定位两种实现的状态、参数、实现路径、行为子案例和对应证据 ID。
- Given VLEN/ELEN、SEW/LMUL、mask/tail、向量状态及访存路径，when 阅读学习单元，then 明确哪些仅有源码线索、哪些检查过测试材料、哪些未覆盖或未验证。
- Given 上游记录或 PASS 断言，when 总结测试证据，then 保留其历史/材料属性，不称为本轮运行结果或完整 V 覆盖。

</frozen-after-approval>

## Implementation Notes

调查基于固定快照。Kunminghu 默认 VLEN=128、ELEN=64，且 VLEN 可参数化；Heliodor 固定 VLEN=128、ELEN=64。它们是配置证据，不代表已覆盖所有规范允许的组合或 profile 行为。测试运行范围根据当前环境中可用的既有定向入口确定；结果只记录本轮实际观察，历史报告仍单独标识。

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Finding floor arithmetic used 1 KiB = 1,024 bytes and concluded N=5. | false | The prompt specifies kB; using decimal kB, 25,262 bytes = 25.262 kB and floor(sqrt(25.262)+1)=6, so the requested floor was met. |
| V Extension link pointed to a live page while the record identified v1.0. | low / patch | Replaced it with the official standalone V v1.0 PDF and identified the checked clauses in E8. |
| Kunminghu VLD/VST internal labels could be read as architectural mnemonics. | low / patch | The unit and evidence now identify them as internal decode/FU load/store routing labels and contrast them with architectural mnemonics. |
| Kunminghu VSET evidence did not say which behaviors the harness checks. | low / patch | Coverage row now names vill/vta/vma/vsew/vlmul, function/AVL/oldVL inputs and the output fields compared against VsetRef. |
| Heliodor E6 grouped multiple memory tests without mapping behaviors to files. | low / patch | Split the evidence into E6a–E6c for vmem, vseg and vleff, with the associated checked comparisons and fail branches. |
| E8 did not identify the official clauses supporting its V specification claims. | low / patch | E8 now cites the V v1.0 standalone PDF and enumerates the checked sections for parameters, state, configuration, masking, exceptions and memory. |

Blind Hunter returned six findings; Edge Case Hunter returned no findings; Verification Gap Reviewer found no gaps. No findings were deferred.
