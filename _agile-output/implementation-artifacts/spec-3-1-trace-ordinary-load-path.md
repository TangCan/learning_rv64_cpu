---
title: 'Story 3.1: 追踪普通访存路径'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: 'b50d796423817dc7dad6d0937d928aa7d8d0e101'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 目前的学习记录尚未把一条普通 RV64I load 从有效地址计算追踪到缓存响应、寄存器结果和提交，因而缺少访存数据路径的双核比较。

**Approach:** 选取 M-mode Bare 下、地址自然对齐且无异常的 `LD rd, imm(rs1)`，以 DCache 命中、无更老重叠 store 为边界，记录 Kunminghu 与 Heliodor 的地址生成、请求、命中数据返回和结果路径。

## Boundaries & Constraints

**Always:** 引用固定快照完整 SHA、适用规范和双方证据；区分源码检查、测试源码检查与实际运行；未验证的缓存/权限/转换前提须明示；使用不可变记录并更新索引。

**Never:** 不改上游源码、不声称运行通过或推断周期；不从本案例推及 miss/refill、forwarding、未对齐、异常、转换配置或 RVA23 整体符合性。

</frozen-after-approval>

## Code Map

- `sources.lock` 固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。规范：RISC-V Unprivileged ISA v20260120 RV32I §2.6、RV64I §3.1.3；官方版本化章节为 `https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html` 和对应 `rv64.html`。
- Kunminghu：`mem/pipeline/LoadUnit.scala:625-645,693-718,736-745` 地址/TLB 输入；`:383-423,903-960,1009-1017` DTLB/DCache 请求与物理地址；`cache/dcache/loadpipe/LoadPipe.scala:179-199,304-317,328-355,452-479,520-522` 命中、读数和响应；`LoadUnit.scala:1748-1809,1635-1645` 结果选择/写回；`mem/lsqueue/LoadQueue.scala:248-258` 接收状态。store forwarding 位于 `LoadUnit.scala:962-987,1397-1408`。
- Heliodor：`core/decoder.veryl:334-343` 译码；`core/heliodor_core.veryl:5283-5293,6410-6416,7406-7425,7895-7912` 地址与 Stage A/B；`mmu/dmem_mmu.veryl:124-128,212-232` Bare 直通；`cache/dcache.veryl:375-383,642-645,2624-2626` 命中/数据；`core/lsu.veryl:64-89,103-116` LD 结果；core `heliodor_core.veryl:7850-7855,7862-7874,3292-3302,3365-3368,4173-4181` CDB/PRF/ROB。load 状态存于 ROB shadow，无独立 LoadQueue。
- `tb/test_arch_common.veryl:1173-1197` 有 RV64UI LD 测试入口；`tb/test_dcache.veryl:117-165` 覆盖缓存测试设计中的冷 miss/同线 hit。不证明本案例运行通过或覆盖核心 LD 全路径。复用模板/索引，新建 `notes/units/load-v1.md`。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/load-v1.md` — 写入 ISA 行为、边界、双边地址到结果路径、证据表、自检答案和验证限制。
- [x] `notes/units/index.md` — 链接新不可变版本并保留既有记录。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` — Story 3.1 与 Epic 3 已处于 `in-progress`；依照状态同步规则保持现状。

**Acceptance Criteria:**
- Given 固定快照，when 选定对齐 `LD`，then 记录有效地址、64 位结果语义、规范依据及排除子案例。
- Given M-mode Bare、DCache 命中且无相关旧 store，when 追踪两边，then 说明地址、LSU 请求、转换/直通、缓存、响应和结果路径并引用源码。
- Given 双边路径，when 比较，then 每项链接双方证据，区分测试源码、运行结果和未验证情景。
- Given 学习记录完成，when 保存修订，then 使用新的 `<unit_id>-vN.md` 文件并更新索引。
- Given 阶段自检，when 回答，then 说明该 `LD` 的数据路径和至少一个验证边界。

## Implementation Notes

计划事实：无待用户决定的问题；快照/规范/源码已限定案例，具体 hit/config 是未验证前提。仅改文档与 sprint 元数据，无不可逆操作或外部副作用。

## Spec Change Log

## Review Triage Log

| Finding | Verdict / route | 核验与处置 |
| --- | --- | --- |
| Blind hunter 1 | false | `notes/units/add-pilot-retrospective.md` 的阶段门为 `ready`，并在授权表中明确列出 Epic 3、Story 3.1 及顺序；启动 Epic 3 有先决证据。 |
| Blind hunter 2 + Edge Case Hunter 1 | medium / patch（同一根因 G1） | 原记录止于 ROB 结果记录，不能满足意图中的提交路径；已补两边 ROB 退休与架构映射静态条件 E14–E15，并明确未观察动态提交。 |
| Blind hunter 3 | low / rejected | 该建议需要改动本次 build 的 spec Code Map；审查规则明确要求拒绝以编辑本 build spec 为修复的 finding。学习记录自身使用锁定上游快照下完整仓库相对路径。 |
| Blind hunter 4 | medium / patch | 已将 RV64I 引用修正为与声明版本一致的 v20260120 版本化链接。 |
| Blind hunter 5 | medium / patch | 原 C4 用 Kunminghu LoadQueue RTL 支持测试覆盖主张；已移除该比较项，只保留 E12–E13 支持 Heliodor 测试源码检查，且明确未运行。 |
| Blind hunter 6 | low / patch | 已删除未提供 profile 依据的 `profile_category: mandatory` 元数据。 |

Verification Gap Reviewer 未报告 finding；本轮没有 defer 项。
## Verification

**Commands:**
- `git diff --check` — 文档改动无空白错误；手工核查快照 SHA、证据 ID 双边性、索引链接和测试状态。
- 不运行 CPU 构建、仿真或测试；本故事只产出源码学习文档，未要求运行验证。
