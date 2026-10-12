---
title: 'Story 3.2: 对照原子内存操作'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'dispatch'
baseline_commit: '071a7005a904c382080de467d0eedc8f1ea348a5'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-3-context.md'
  - '{project-root}/notes/templates/learning-record.md'
  - '{project-root}/notes/units/index.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 当前双核学习记录尚未解释原子读改写与普通 load/store 的架构差异，也没有比较两种实现如何维护原子性并返回旧值。

**Approach:** 选择两边源码均支持的 RV64A `AMOADD.D`，从译码和操作数开始，追踪内存端的原子读改写、旧值返回及 ROB 退休；以固定源码证据比较实现，并标明未运行验证的边界。

## Boundaries & Constraints

**Always:** 使用 `sources.lock` 固定快照和规范版本；解释 `AMOADD.D` 的旧内存值返回、64 位加法及原子读改写语义；每项双核实现比较都关联双方证据；尝试运行 Heliodor 已有的 `test_arch_rv64ua_amoadd_d`；若工具链在测试执行前阻止运行，记录命令、版本和错误，并将动态行为标为未验证；明确 Kunminghu 未定位到对应专门测试，只能提供静态源码证据；区分源码、测试检查和实际运行，不把源码条件描述成运行观察。

**Never:** 不新增测试或修改上游源码；不把 Heliodor 的测试结果外推为 Kunminghu 测试结果，不推断周期或断言竞争下的实现正确性；不外推到 LR/SC、其他 AMO 操作、`.W`、未对齐地址、异常权限路径、非缓存设备内存或 RVA23 整体符合性。

</frozen-after-approval>

## Code Map

- `sources.lock` 固定 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。规范依据为 [Unprivileged ISA v20260120 A extension §12.1、Zaamo 子节](https://docs.riscv.org/reference/isa/v20260120/unpriv/a-st-ext.html)；RV64 `AMOADD.D` 仅对自然对齐的 doubleword 操作。本记录不判断 RVA23 profile 完整性。
- Kunminghu decode：`src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:249,946-954`；执行分类与序列化：`backend/dispatch/NewDispatch.scala:814-820,896`、`mem/MemBlock.scala:1802-1835`；AMO 数据/权限/缓冲器路径：`mem/pipeline/AtomicsUnit.scala:84-92,137-178,238-335,357-399,479-537`；DCache 运算：`cache/dcache/mainpipe/AMOALU.scala:39-49,73-80`；响应和退休：`cache/dcache/DCacheWrapper.scala:1467-1472`、`backend/rob/Rob.scala:785-801`。不修改上游。
- Heliodor decode 与操作数：`src/core/decoder.veryl:606-628`、`src/core/decode.veryl:190-211,257-260`；head 序列化：`src/core/iq_int.veryl:426-428,945-947`；AMO 执行/旧值 CDB/新值提交：`src/core/alu_wrap.veryl:274-287,316-363,400-438`；目录失效 poison/replay：`src/core/heliodor_core.veryl:5788-5811,5859-5908`；提交 DCache 写及 ROB ack：`:4062-4072,7495-7503,7525-7556`；架构映射更新：`:4416-4420`。
- Heliodor `tb/test_arch_common.veryl:2499-2523` 提供 AMOADD.D 测试入口。本次 Kunminghu 源码搜索未定位到专门的 AMOADD.D 测试；`DecodeTest.scala:38-49` 是译码 smoke test，不证明 AMO 语义。测试入口存在不表示执行过。复用学习记录模板和索引，新增 `notes/units/amoadd-d-v1.md`。

## Tasks & Acceptance

**Execution:**
- [x] `notes/units/amoadd-d-v1.md` — 说明 ISA 行为、适用边界、双核原子性路径、旧值结果/退休、证据及验证限制。
- [x] `notes/units/index.md` — 链接新的不可变学习记录。
- [x] `_agile-output/implementation-artifacts/sprint-status.yaml` — 完成审查后将 Story 3.2 标记为 done，并保持 Epic 3 处于进行中。

**Acceptance Criteria:**
- Given 固定快照，when 解释对齐 `AMOADD.D`，then 记录旧值返回、加法更新、原子读改写语义及规范出处。
- Given 两边实现，when 追踪指令，then 记录请求、原子性维护、结果返回与退休的关键控制和数据路径，并以稳定证据 ID 支持。
- Given 源码或测试入口，when 形成比较结论，then 区分静态源码、已检查测试与未运行测试，不宣称测试通过或竞争正确性。
- Given 学习记录完成，when 保存修订，then 使用新的 `<unit_id>-vN.md` 并更新索引。
- Given 阶段自检，when 回答，then 解释 AMO 与普通 load/store 的架构差异并指出至少一个验证边界。

## Implementation Notes

范围选择：`AMOADD.D` 在两个固定快照中均有译码、执行及返回路径，较 LR/SC 更适合作为一个原子操作案例；aq/rl 排序变化作为未展开子案例。用户授权运行现有测试并调整范围后，尝试运行 Heliodor 已有测试；稳定版与 nightly 均在测试执行前因同一 testbench 编译错误失败。因此本记录保留双核静态路径比较和测试入口证据，将所有动态行为标为未验证，并移除无法满足“测试通过”审计的 I/O 矩阵。没有新增测试或修改上游代码。修改面限于学习记录、索引、spec 与 sprint 元数据；无新增被软件调用的 API。

## Spec Change Log

- 2026-10-12：用户授权运行现有测试并调整范围。Heliodor `test_arch_rv64ua_amoadd_d` 在 Veryl 0.22.0 stable 与同日 nightly 均于测试启动前因 `tb/test_arch_common.veryl:440` 的 `invalid_initial_assign` 编译错误中止；据此将 Always 改为尝试运行并如实记录阻塞，将矩阵删除，避免把未运行行为当作通过验收。双核源码路径比较保留；测试结果及动态行为保持未验证。

## Review Triage Log

- low — 盲审指出 E18 以双版本尝试计为一次命令尝试，原记录措辞不够清楚，且未列稳定版日志；核对后 `/tmp` 仅保留 nightly 日志，E18 已明确为同一命令分别用 stable/nightly 执行，保存的日志路径标为 nightly。证据：执行记录和 `/tmp/story32-amoadd-nightly.log`。route: patch（记录澄清）。
- low — 盲审指出 E16 搜索范围不可复现；已记录精确 `rg -ni 'amoadd_d|amoadd\.d|amoadd-d' sources/xiangshan/src/test` 命令及搜索范围。证据：源码树搜索无命中。route: patch。
- low — 盲审指出 Kunminghu 原子响应到目的寄存器的连接缺少证据；已补 AtomicsUnit 输出 `pdest`/`data`、MemBlock atomic writeback override 与 `writebackLda` 接线，且没有扩张为 PRF 内部更新的断言。证据：`AtomicsUnit.scala:479-489`、`MemBlock.scala:520-529,552`。route: patch。
- low — 盲审指出 E8 通用 ROB 条件可能被读成 AMO 专属退休证据；已将其明确限定为通用 commit-valid 门控，并标注没有 AMO 动态退休观察。证据：`Rob.scala:784-801`。route: patch。
- low — 盲审指出 Heliodor poison/replay 缺少触发和门控条件；已补记录 PA/ROB index、同周期及 watch 窗口内 invalidate/eviction/presence 条件，以及 `commit_amo_replay` 对 ack 和 redirect 的门控。证据：`heliodor_core.veryl:4004-4007,4062-4072,5796-5811,5870-5889`。route: patch。
- low — 盲审指出 E18 的 Expected 应描述用例断言，而非“测试应启动”；已将 Expected 改为若启动则执行 AMOADD.D ISA 用例并报告断言结果，启动失败仅留在 Observed。证据：测试入口 `tb/test_arch_common.veryl:2499-2523` 和编译错误日志。route: patch。
- false — 边界审查未报告未处理路径；无需修订。
- false — 验证缺口审查未发现缺口；本故事仅产出静态学习材料，且测试未启动与证据表状态一致。

## Design Notes

- AMO 指令产生的整数结果是原子更新之前读出的旧内存值，内存写入值则是 `old + rs2`。学习记录应把这两条数据流分别跟到目的寄存器和内存更新，避免把返回旧值误写成新值。
- Kunminghu 通过 AtomicsUnit/DCache AMO 请求和 AMOALU 处理；Heliodor 将旧值送 CDB/ROB，并在退休路径实施本地缓存写入，同时保留失效后的 poison/replay 条件。只比较这些可见源码机制，不推导同一周期行为或覆盖所有多核交错。

## Verification

**Commands:**
- `git diff --check` — 文档改动无空白错误。
- 在 `sources/heliodor` 执行 `veryl test --test test_arch_rv64ua_amoadd_d`，Veryl 0.22.0 stable 与 `0.22.0-nightly (c3bf469 2026-10-12)` 均 exit 1；测试未启动。编译器在 `tb/test_arch_common.veryl:440` 报 `invalid_initial_assign`（`dram` 在 initial 块由 `$readmemh` 赋值）。日志：`/tmp/story32-amoadd-nightly.log`。

**Manual checks:**
- 核对来源 checkout SHA 与 `sources.lock`、源码证据路径、规范链接、证据 ID 双边性、索引目标及测试是否运行；测试执行被工具链编译错误阻止，AMOADD.D 的动态行为未验证；不据此报告通过。
