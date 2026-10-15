---
title: '追踪双核普通 DRAM SD 的提交与写入边界'
type: 'feature'
created: '2026-10-15'
status: 'in-progress'
route: 'dispatch'
baseline_commit: 'a010badd67ec8d1c98b279c0bf6fdecfd4f24d20'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/epic-1-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/spec-1-1-dual-core-ld-path.md'
  - '{project-root}/_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/learning-record-conventions.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 现有学习材料尚未解释普通对齐 `SD` 在 Kunminghu 与 Heliodor 中何时提交、何时被后续写入路径接受，以及源码证据能否支持 DRAM 可见性结论。

**Approach:** 对照 `sources.lock` 中的两个固定快照，为同一 RV64I `SD` 场景选择并记录共享地址/数据 tuple 和各自有证据支持的接受终点。发布不可变 `store-v1.md` 与过程日志，更新索引和 trace matrix，清楚标记两侧配置差异、静态证据和未观察的下层可见性。

## Boundaries & Constraints

**Always:** 使用锁定快照；区分 ROB 指令提交、store queue/store buffer/uncache request 接受以及更低层 DRAM 可见性；按各自微架构术语描述；把未经运行确认的配置与行为保留为 assumption 或 unverified；每条结论有证据 ID、type、status 和源码位置。

**Never:** 不修改上游 RTL 或锁定来源；不把 commit、队列出队、缓存接收或 buffer drain 单独表述为 DRAM 已可见/持久；不运行或声称运行 SD 测试/仿真；不扩大为 RVA23 符合性结论。

</frozen-after-approval>

## Code Map

- `sources/xiangshan/src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:167` — `SD` 解码为 StoreUnit、S 型立即数；`StoreUnit.scala:141-176,200-255,378-422` — 地址、对齐/掩码、`rs2` 数据、DTLB 响应及 LSQ 输入。
- `sources/xiangshan/src/main/scala/xiangshan/mem/lsqueue/StoreQueue.scala:828-839,920-990,1054-1087,1133-1183,1221-1238,1323-1360` — ROB 提交标记、默认 PMA uncached/MMIO 路径、请求/响应与回写，以及 committed store 到 Sbuffer 的条件；`MemBlock.scala:1466-1528` 连接 LSQ Uncache 请求和 Uncache 模块。`system/SoC.scala:60-65`、`src/main/resources/config/Default.yml:1-8` 与 `backend/fu/PMA.scala:42-51,211-218` 说明默认 DRAM 范围、R/W 权限及 `c=false` 对应的 uncached 分类。
- `sources/heliodor/src/core/decoder.veryl:344-351` — STORE/S 型立即数解码；`alu_wrap.veryl:121-132,425-438` 与 `rob.veryl:608-621,1322-1331` — 地址/数据/Funct3 写入 ROB 并在 head 输出。
- `sources/heliodor/src/core/heliodor_core.veryl:5927-5964,5971-5997,6664-6740,7460-7478` — commit、SD 字节选通、DRAM/非 tohost 分类、store-buffer push 与 drain。`src/cache/dcache.veryl:1341-1350,1947-2002,2710-2728` 区分 DCache 本地 dirty merge、write-through 与 memory writeback。
- `sources.lock` 固定 Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；本故事只读这两个 checkout，不编辑其文件。
- `notes/units/load-v2.md`、`learning-journal/2026-10-15-ld-path-review.md`、两个索引、学习计划和 `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 复用既定版本、日志字段、证据词汇和矩阵格式；保持 `load-v1.md` / `load-v2.md` 不变。

## Tasks & Acceptance

**Execution:**
- [x] `_agile-output/planning-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/decisions/story-1-2-store.md` — 记录共同 tuple、两侧实际默认配置差异、接受终点选择及未知边界，便于后续复查路径选择。
- [x] `notes/units/store-v1.md` — 新建不可变 SD 技术记录，包含双侧从译码/地址数据形成到提交及接受终点的证据、比较结论、子案例、证据表和未解问题。
- [x] `notes/units/index.md` — 将 `store` 指向 v1，不改动既有 load/fault 版本。
- [x] `learning-journal/2026-10-15-sd-commit-write-boundary.md` — 按约定记录问题、探索动作、发现、证据边界、知识单元链接和下一步。
- [x] `learning-journal/index.md` 与 `learning-journal/plan.md` — 链接日志，并把 SD 阶段标成已完成本次静态追踪。
- [x] `_agile-output/specs/spec-rv64-load-store-deep-dive/trace-matrix.md` — 添加 Kunminghu 与 Heliodor SD 行，分别列出路径终点、快照、证据链接、type/status 与配置假设。

**Acceptance Criteria:**
- Given 两个锁定源码快照，when 追踪普通 `SD`，then 两侧都从指令和源寄存器开始，引用地址、8-byte mask/data、提交条件及所选接受边界的源码位置；不足处明确标为 unknown/unverified。
- Given 共享案例 `SD x11, 0(x10)`、`x10=0x80004000`、`x11=0x1122334455667788`、M-mode Bare，when 分类该目标，then 记录它落在 Kunminghu 默认 Pmem 范围且 R/W 开放但 PMA `c=false`（uncached 路径），并落在 Heliodor DRAM window 且避开其 tohost 排除页；默认配置是否用于任何实际运行仍是未验证前提。
- Given 两侧写路径不同，when 选择接受终点，then Kunminghu 记录 StoreQueue 的 uncached request handshake，并区分到达 ROB head、request handshake、返回确认与之后的 ROB retirement；Heliodor 记录 eligible store 进入 committed store buffer（`sb_push`），并区分 commit 与之后 DCache drain。
- Given 只有静态源码证据，when 总结结果，then 不声称观察到该 SD 运行、DCache 更新、下游写事务、其他观察者可见或 DRAM 持久；矩阵两侧 evidence type/status 分列，且测试源码（若检查）不写成已运行。
- Given 已有学习单元、日志和矩阵，when 校验交付，then 新增证据 ID 全局唯一，所有链接/锚点有效，LD 文档未改，两个 checkout HEAD 匹配 `sources.lock`；不运行测试、构建或仿真。

## Implementation Notes

- 固定 RTL 显示 Kunminghu 默认 `c=false` 的 MMIO 请求在 ROB head/pending-store 阶段发出，response 后 writeback，随后才 retirement；因此将含混的“先 commit、再握手”收窄为真实状态顺序，frozen intent 未改。Heliodor endpoint 保持 eligible store 的 `sb_push`。
- 新增 `SD1-E1`–`SD1-E8`，发布 decision、store-v1、日期日志和矩阵双侧行；索引与学习计划已更新。

## Spec Change Log

## Review Triage Log

## Design Notes

**案例与终点：**选 PA/VA `0x80004000`，避开 Heliodor 在 `0x80000000–0x80003fff` 与 `0x80008000` 的 tohost 排除区；两边均用 `M-mode Bare`，所以记录的 VA 与 PA 相同。Kunminghu 默认 PMA 把 DRAM 的 `c` 设为 false，其 `mmio` 响应触发 uncached StoreQueue 路径；Heliodor 的同一地址符合 `fast_store` DRAM 条件。该差异是设计比较的一部分，不为追求路径相同而覆盖默认属性。Kunminghu 终点为 request handshake；Heliodor 终点为提交 store buffer push。两个 endpoint 代表各自提交后首个受接收方 ready/容量约束的写入接受点，不代表共同的 cache 或 memory visibility 时点。

## Verification

- `python3 scripts/check_doc_links.py` 检查 7 份新增/更新文档：通过；全局检索确认 `SD1-E1`–`SD1-E8` 仅在本单元、日志、决策及矩阵中使用且编号无重复。
- Kunminghu 与 Heliodor HEAD 分别匹配 `sources.lock`；`load-v1.md`、`load-v2.md` 与既有 LD 日志未修改。
- Sprint status validate 通过；`git diff --check` 通过。验证命令未运行 RTL、构建、SD 测试或仿真。

**Commands:**
- `python3 scripts/check_doc_links.py ...` — 所有新增/更新 Markdown 的支持链接和锚点存在。
- `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/followups/rv64-load-store-deep-dive-2026-10-15/sprint-status.yaml` — sprint 状态合法。
- `git diff --check` — 无空白错误。

**Manual checks:**
- 比较两个 checkout HEAD 与 `sources.lock`；核对源位置支持各自路径、PMA 差异和终点；确认新增 evidence ID 唯一，SD 两侧 matrix 行链接到证据表。
- 不运行 RTL、CPU 构建、SD 测试或仿真；本故事的动态地址、store-buffer 接受和 DRAM 可见性继续标为未验证。
