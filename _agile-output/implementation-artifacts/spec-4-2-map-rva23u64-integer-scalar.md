---
title: 'Story 4.2: 映射 RVA23U64 基础整数与标量要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '0589acd76062f2e604720080d09a59737b6326be'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-1-establish-official-rva23-inventory.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23U64 的标量强制项尚未映射到 Kunminghu 与 Heliodor 的实现路径，目录仍无法回答具体要求由哪些译码、执行和控制路径承载，也无法辨别源码线索与行为证据。

**Approach:** 对照固定源码快照，为 RV64I、M、C、B 及标量 CSR/counter、hint、conditional、MOP、Supm 和 Zkt 要求逐项记录两边的源码位置、子案例、现有验证材料和证据状态，并更新覆盖目录与学习单元索引。

## Boundaries & Constraints

**Always:** 逐项使用 RVA23U64/v1.0 稳定键；保留要求行，不以扩展名元数据或单个测试概括整项覆盖；分开记录 Kunminghu 与 Heliodor；区分源码、已检查测试材料和实际运行结果；写出证据能支持的子案例及未证实部分；测试未运行时不得写 run-pass；使用学习映射语气，不作符合性认证结论。

**Never:** 不修改上游快照；不把向量、浮点、原子/缓存/内存属性及 S64 特权要求纳入本故事；不因缺少搜索结果断言实现不存在；不把上游测试报告或 ISA 元数据当作本次运行结果。

## Code Map

- `notes/rva23-coverage.md`：Story 4.1 建立的逐项主目录；本故事只填 RVA23U64 §3.1.1.1/RV64I 与 §3.1.1.2 中标量要求的两侧字段，其他领域行保持原状。
- `notes/templates/learning-record.md`：统一证据表字段与 Kind/Status 词汇；新建标量学习单元时沿用该模板，证据 ID 回链到源码或具体验证材料。
- `sources.lock`：固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a` 快照。
- Kunminghu `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala`、`backend/fu/Alu.scala`、`backend/fu/wrapper/{MulUnit,DivUnit}.scala`、`backend/fu/NewCSR/`：分别定位基础/扩展译码、整数执行、M 运算与 CSR/counter；`frontend/PreDecode.scala` 连接压缩展开。静态测试线索在 `src/test/scala/`，须核实测试是否有刺激及断言。
- Heliodor `sources/heliodor/src/core/{decoder,alu,c_expander,csr,alu_wrap}.veryl`：对应标量译码、整数/M 运算、压缩展开、计数器/CSR 与指针掩码；`tb/test_arch_common.veryl`、`tb/test_alu.veryl`、`tb/test_c_expander.veryl` 和各 `test/` 目录为已有验证材料，未执行不代表通过。
- `notes/units/index.md`：学习单元入口；只增加新单元稳定路径及简短证据状态。

## Tasks & Acceptance

**Execution:**
- [x] `notes/rva23-coverage.md` — 填写标量范围各强制要求的两侧状态、位置、理由、子案例和证据 ID；将 Zawrs 与 A/原子等待路径留给 Story 4.6。
- [x] `notes/units/rva23u64-scalar-v1.md` — 记录 RV64I、标量扩展的规范范围、两侧架构路径、证据表、比较结论与未覆盖子案例。
- [x] `notes/units/index.md` — 链接新单元并标明本次只做静态源码/测试材料检查。

**Acceptance Criteria:**
- Given RVA23U64 的标量必选目录，when 查看映射，then RV64I、M、C、B、Zicsr、Zicntr、Zihpm、Zihintpause、Zihintntl、Zicond、Zimop、Zcmop、Zcb、Supm、Zkt 每一行均保留稳定键并分别填写两种实现。
- Given 一项实现路径或验证材料，when 记录结论，then 源码位置、测试材料与实际运行证据可区分，且只声明证据直接支持的行为子案例。
- Given 未定位到实现或无法证明属性，when 填写状态，then 保留不确定边界，不将搜索不到或未运行转成 `not-present` 或通过结论。
- Given 本故事结束，when 阅读覆盖目录与学习单元，then 能比较两个处理器的标量实现结构，并从每个结论追溯到固定快照中的位置或证据材料。

</frozen-after-approval>

## Implementation Notes

故事领域边界由 Epic 4 定义；A、Zawrs、PMA/缓存行为由 Story 4.6 追踪。标量目录本轮发现香山 CSR 源码有非特权计数器/TIME TODO，MOP 译码线索不完整，Supm 与 Zkt 不能由元数据声明证明；Heliodor 有较多定向/ACT 材料，但未运行，覆盖范围依测试刺激逐项描述。

## Review Triage Log

- low — `notes/units/rva23u64-scalar-v1.md` 的子案例表将覆盖状态写为 `unconfirmed`，而主目录使用 `partially-studied` / `studied-unverified`；模板允许子案例表使用独立的 covered/excluded/unconfirmed 词汇，但缺少解释会让读者误以为状态冲突。route: patch.
- low — Kunminghu 的 C 行标为 `studied-unverified`，但单元只确认 PreDecode 压缩展开入口，没有列出已检查的具体 C 编码子案例；该行需缩小状态/范围表述。route: patch.
- low — Heliodor 的 C 行标为 `studied-unverified`，但单元同时说明未核验完整编码集合；需让行内状态和明确支持的压缩子集一致。route: patch.
- low — E3 作为 Kunminghu 测试材料边界证据并被 C2 引用，但仅写“文件清单”，未写清检索方法与范围；实际检查命令应记录以便复查。route: patch.
- low — E1/E4 的多个源码文件路径使用相对快照根的缩写，与路径章节的仓库根路径格式不同；加入固定快照 checkout 前缀可避免歧义。route: patch.
- low — E3/E5/E6 的测试材料均没有记载定位测试的命令或检索步骤，导致静态材料检查难以复现；补记本轮实际执行的只读检索命令。route: patch.
- false — 盲审称 RV64I 的 little-endian 与 ECALL 行为未明确列为未检查子案例；覆盖目录该行已写明“端序、异常语义未逐项核验”，故该具体遗漏不存在。route: reject.
- low — Kunminghu Zicsr、Zicntr、Zihpm、Supm、Zicond 行误引只支持 divider 测试材料的 E3；已将对应证据限制为直接源码证据。route: patch.
- low — Heliodor M 行引用的 E5 未标明 RV64UM harness 与输入；已补充具名 harness、hex 路径，测试仍标为未运行。route: patch.
- low — E6 的 CSR/instret 测试材料缺少具名 harness、hex 路径和针对性查找命令；已补全。route: patch.
- low — Heliodor Supm 行引用只涉及 CSR/HPM 测试的 E6；已限定为 E4 源码证据。route: patch.
- low — Kunminghu Zicond 行引用只支持 divider 测试的 E3；已限定为 E1 源码证据。route: patch.
- low — Heliodor Zihintpause 行的 E5 原先没有指明 PAUSE 输入和 harness；已补充 `hint_test.S` 的 PAUSE 行和 `test_arch_hint` harness 位置。route: patch.
- low — E1/E4 的 M 路径搜索命令未覆盖乘法器/除法器源码；已明确 Kunminghu MulUnit/DivUnit 直接检查，并将 Heliodor `int_divider.veryl` 加入 E4 路径与检索命令。route: patch.
