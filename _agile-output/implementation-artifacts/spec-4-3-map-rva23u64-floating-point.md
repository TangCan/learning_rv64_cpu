---
title: 'Story 4.3: 映射 RVA23U64 浮点要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '8d69385e357c98f13a7d97af37d5069de9bf8c9c'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-2-map-rva23u64-integer-scalar.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23U64 的 F、D、Zfhmin、Zfa 强制项尚未映射到两套 CPU 的标量浮点路径及证据，难以区分源码实现和未验证边界。

**Approach:** 按 RVA23 Profile v1.0 四个稳定键检查固定快照中的译码、执行、状态控制和现有测试材料，更新覆盖目录并新增双核学习单元。

## Boundaries & Constraints

**Always:** 分别记录两侧状态、实现位置、子案例和证据 ID；区分标量与向量 FP；说明测试是否运行；未核实的舍入、异常和格式组合明确标记未验证。

**Never:** 不把译码或测试材料存在写成通过；不修改上游源码；不宣称 IEEE 全覆盖或 RVA23 符合性。

## Code Map

- `notes/rva23-coverage.md`：只填 U64 的 F、D、Zfhmin、Zfa 四行。`notes/units/rva23u64-scalar-v1.md` 和 `notes/templates/learning-record.md`：复用快照与证据表结构；索引为 `notes/units/index.md`。
- `sources.lock` 固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- 规范：RVA23 Profile v1.0 §3.1.1.2；[F v2.2](https://docs.riscv.org/reference/isa/unpriv/f-st-ext.html)、[D v2.2](https://docs.riscv.org/reference/isa/unpriv/d-st-ext.html)、[Zfhmin v1.0](https://docs.riscv.org/reference/isa/unpriv/zfh.html)、[Zfa v1.0](https://docs.riscv.org/reference/isa/unpriv/zfa.html)（RISC-V Ratified Specifications Library）。
- Kunminghu：`backend/decode/FPDecoder.scala`、`DecodeUnit.scala`；`backend/fu/wrapper/{FALU,FMA,FCVT,FDivSqrt}.scala`；`backend/fu/NewCSR/{Unprivileged,NewCSR}.scala`。`fudian/`、`yunsuan/` 快照目录为空；`DecodeTest.scala` 须核实测试刺激与断言。
- Heliodor：`src/core/{decoder,fpu_wrap,lsu,alu_wrap,csr}.veryl`、`src/pkg/fpu_pkg.veryl`。测试材料：`tb/test_arch_fp.veryl`、`tb/test_fp_*.veryl`、`test/{zfhmin,zfa,riscv-arch-test/build/rv64uf,riscv-arch-test/build/rv64ud}`；检查 ignored harness 和测试是否运行。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 填四项两侧映射、子案例和证据链接。
- [x] `notes/units/rva23u64-floating-point-v1.md` — 记录规范、路径比较、证据及未验证边界。
- [x] `notes/units/index.md` — 添加入口及验证状态。

**Acceptance Criteria:**
- Given 四项浮点强制要求，when 查看目录，then F、D、Zfhmin、Zfa 各有独立稳定键和两侧映射字段。
- Given 实现及测试材料，when 比较，then 区分 S/D/H 指令族与标量/向量通路，并分别记录源码、检查过的材料和实测结果。
- Given 未核验的舍入、NaN-box、异常 flag、FS 状态或格式组合，when 总结，then 保留明确边界；未运行材料不得表示通过。

</frozen-after-approval>

## Implementation Notes

本故事将 F、D、Zfhmin、Zfa 分开记载。RISC-V 手册对 Zfhmin 将半精度范围限制为搬运与转换指令；Zfa 增加多类浮点指令。Kunminghu 外部 Fudian/Yunsuan 目录在该快照不可用；Heliodor 有较详细的独立架构测试 harness，但全部先按未执行材料记录。

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Sprint status remained `in-progress` while this spec was `in-review` and unit index called it complete. | false | The build workflow keeps sprint status active during review and changes it to `review` in Step 5; the current state is the expected pre-presentation transition. |
| Coverage overview did not distinguish Story 4.2 mapped areas from areas pending investigation. | low / patch | The prior wording said only “其他领域仍待后续故事调查”; updated the overview to name Story 4.2 and Story 4.3 mapped areas and list pending areas. |
| Zfhmin row said H decode exceeded its minimum but gave no concrete opcode. | low / patch | `FPDecoder.scala` lists `FADD_H` (observed at source line 261 in the fixed snapshot); the row now names it and explicitly excludes H arithmetic from Zfhmin. |
| Zfa row did not make clear that evidence was a subset rather than a full inventory. | false | The row already enumerated FLEQ/FLTQ, FMINM/FMAXM, FROUND/FROUNDNX, FCVTMOD.W.D as observed decode clues and stated that the complete set was unverified; revised wording makes the subset explicit. |
| F/D overview wording could imply every listed family had been individually inspected. | false | Both rows call the listed items “路径线索” and explicitly state that complete instructions or boundary behavior were not verified. |
| E6 ignored-file command omitted its working directory. | low / patch | E6 now says `git check-ignore` runs from the project repository root containing `sources/heliodor/`, making the command context reproducible. |

Blind Hunter returned six findings; Edge Case Hunter returned no findings; Verification Gap Reviewer found no gaps. No findings were deferred.
