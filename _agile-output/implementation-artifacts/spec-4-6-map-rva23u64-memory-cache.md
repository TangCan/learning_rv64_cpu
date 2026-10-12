---
title: 'Story 4.6: 映射 RVA23U64 的内存与缓存要求'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '861a3df2cab456232bf0ffa478a5723e93c93267'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-4-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-4-5-map-rva23u64-additional-vector.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** RVA23U64 的内存与缓存必选项不仅要求指令存在，也规定适用主存区域上的取指原子性、LR/SC 进展、原子与非对齐访问、reservation set 以及 cache block 属性；覆盖目录尚未映射这些条件和两套实现的证据。

**Approach:** 依据 RVA23 Profile v1.0 及 A、CMO、Zawrs ratified 规范，逐项调查 Kunminghu 与 Heliodor 的 RTL、配置、平台说明和现有验证材料，更新对应覆盖行并建立一份限定结论与未验证边界的学习单元。

## Boundaries & Constraints

**Always:** 对 A、Ziccif、Ziccrse、Ziccamoa、Zicclsm、Za64rs、Zic64b、Zicbom、Zicbop、Zicboz、Zawrs 分别记录两侧证据和子案例。凡要求限定于同时具有 cacheability 与 coherence PMA 的主存区域，须保留此适用条件；区分局部 RTL、配置/平台声明、测试材料和实际运行结果。遇到证据缺失时记录 `partially-studied` 或 `studied-unverified`，不得推断实现不存在或平台满足要求。

**Never:** 不修改上游快照；不把指令译码当作架构行为或平台保证；不把单个 LR/SC、AMO、非对齐访问或 CBO 案例推广到所有地址区域和系统代理；不将可选/开发选项 Zama16b、Zabha、Zacas、Ziccamoc 混为本故事的 U64 必选项。

## Code Map

- `notes/rva23-coverage.md`：U64 §3.1.1.2 中 A、Ziccif、Ziccrse、Ziccamoa、Zicclsm、Za64rs、Zic64b、Zicbom、Zicbop、Zicboz、Zawrs 的逐项双侧映射；S64 继承行不在本故事修改。
- `notes/units/amoadd-d-v1.md`：Story 3.2 已追踪 AMOADD.D 局部路径；可作为 A 的既有证据线索，不能替代完整 A 集合、内存区域 PMA 或系统保证。
- Kunminghu 固定快照：`src/main/scala/xiangshan/backend/decode/DecodeUnit.scala` 的 AMO/LRSC/CBO/WRS 解码；`cache/dcache/mainpipe/MainPipe.scala`、`DCacheWrapper.scala`、`Probe.scala` 的 reservation 与一致性事件；`LoadUnit.scala`、`LoadMisalignBuffer.scala`、`StoreMisalignBuffer.scala` 的非对齐访问；`DCacheWrapper.scala`、`XSDts.scala` 的 cache block 参数/设备树输出；`Parameters.scala` 与 `scripts/xiangshan.py` 的配置/工作负载声明。
- Heliodor 固定快照：`src/core/decoder.veryl`、`heliodor_core.veryl`、`dcache.veryl`、`icache.veryl` 的原子、取指拼接、reservation、split access 和 CBO 路径；`test/act/config/heliodor/heliodor.yaml`、`sail.json`、`test/act/README.md` 与 `README.md` 的平台假设、支持声明和测试报告；`tb/test_lrsc_reorder.veryl` 的 LR/SC 定向回归。
- 规范：[RVA23 Profile v1.0 §3.1.1.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)、[A v2.1](https://docs.riscv.org/reference/isa/unpriv/a-st-ext.html)、[CMO v1.0](https://docs.riscv.org/reference/isa/unpriv/cmo.html)、[Zawrs v1.01](https://docs.riscv.org/reference/isa/unpriv/zawrs.html)。
- `notes/templates/learning-record.md`、前序 Epic 4 学习单元及 `notes/units/index.md`：沿用证据表字段、状态词汇和版本索引方式；新建本单元版本，不覆盖历史单元。

## Tasks & Acceptance

**Execution:**
- [ ] `notes/rva23-coverage.md` — 更新上述 11 个 U64 必选项行的两侧状态、位置/范围、条件、子案例和证据链接；保留相关 S64 继承行及其他领域。
- [ ] `notes/units/rva23u64-memory-cache-v1.md` — 按统一模板记录规范行为、两侧源码/平台路径、验证材料、比较结论和未解问题；区分局部实现线索与平台属性。
- [ ] `notes/units/index.md` — 登记本学习单元及实际检查/运行状态。

**Acceptance Criteria:**
- Given 官方必选项目录，when 核对 Story 4.6 范围，then 11 项 U64 键均有两侧独立状态、位置或范围决定、理由、子案例和证据 ID。
- Given 有 cacheability 与 coherence PMA 前提的要求，when 阅读映射，then 可识别其适用内存区域；局部 RTL 或配置不会被写成平台级保证。
- Given LR/SC、AMO、misaligned、取指 atomicity、reservation-set 与 CBO 行为，when 阅读学习单元，then 各自边界和所检查的微架构事件均可复查，证据不足处维持未验证状态。
- Given 测试源码、配置和历史结果，when 记录验证证据，then 明确标记已检查或本轮运行，且没有实际观察输出的测试不标为通过。

</frozen-after-approval>

## Implementation Notes

Epic 4 上下文与 Story 4.5 作为连续性基线。Story 3.2 已记录 AMOADD.D 的路径，但本故事需要追踪整个 profile 要求及 PMA/平台边界。两侧 reconnaissance 已定位局部实现、配置和测试入口；未运行 RTL/ACT 测试。上游快照固定于 `sources.lock`。三个执行任务已完成；覆盖表 11 项证据回链、Sprint validator 与差异格式检查均已核对通过。

## Review Triage Log

| Finding | Verdict | Evidence and disposition |
| --- | --- | --- |
| Blind/edge review: E1’s observed field described only the profile check, leaving A/CMO/Zawrs semantic claims unclear. | low / patch | Verified the official profile and the ratified A, CMO, and Zawrs text; updated E1 to name those checks and separate profile requirements from extension behavior. |
| Blind review: Zicbom lacked operation-level effects and access boundaries. | low / patch | Checked CMO semantics for CBO.INVAL/CLEAN/FLUSH and CBCFE/CBIE/access constraints; added a per-operation case and retained platform visibility as unverified. |
| Blind review: Zicboz did not distinguish whole-block zero semantics, permission/PMA requirements, and atomic visibility. | low / patch | Checked CMO v1.0: all bytes are zeroed at implementation-defined granularity/order, without an atomicity guarantee; added the supported-access PMA and Zic64b block context. |
| Blind review: Zicbop lacked each hint's purpose and may-ignore behavior. | low / patch | Added PREFETCH.I/R/W meanings, HINT/ignore semantics, and the inaccessible-address no-exception/no-access rule from CMO. |
| Blind review: A cases omitted LR/SC alignment, width results, failure, and eventuality constraints. | medium / patch | Added LR/SC natural alignment, W sign-extension/result status, invalid-reservation failure, and constrained-loop-only RsrvEventual scope; full execution semantics remain unverified. |
| Blind review: Ziccif lacked its full fetch-size/alignment cases. | low / patch | Added the 8/16/32-bit fetch-access boundary cases, natural alignment by access size, and called out 32-bit instruction straddling separately from naturally aligned 32-bit atomicity. |
| Blind review: all execution task boxes remained unchecked. | false | The cited boxes are inside `<frozen-after-approval>`; Step 3 makes that block read-only and Step 4 rejects findings whose fix edits this build's spec. Sprint status is the mutable execution tracker and records Story 4.6 as `review`; no frozen text was changed. |
| Blind review: coverage rows did not have a direct claim-to-evidence map. | low / patch | Added an 11-row requirement-to-evidence index that maps both implementations for every requirement without making evidence stronger than its recorded scope. |
| Edge review: extension-specific claims might be mistaken as unchecked because E1's observation was narrow. | low / patch | Same evidence issue as the first finding; after verifying the official sources, expanded E1 to identify the profile and three extension specifications explicitly. |

## Verification

**Commands:**
- `uv run .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — expected: `valid: true`。
- `git diff --check` — expected: no whitespace errors.

**Manual checks:**
- 对照 profile §3.1.1.2 与覆盖目录核实 11 个键及 PMA 条件；逐条检查证据 ID 均能链接到学习单元且不混淆 inspected、unverified 和 run-pass。
