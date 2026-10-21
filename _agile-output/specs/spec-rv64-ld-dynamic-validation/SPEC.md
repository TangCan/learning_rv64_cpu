---
id: SPEC-rv64-ld-dynamic-validation
companions:
  - validation-scope.md
  - ../../../notes/units/load-v2.md
  - ../spec-rv64-load-store-deep-dive/feasibility.md
sources: []
---

# 成功标量 LD 双核动态验证可行性

## Why

现有 Kunminghu 与 Heliodor 固定快照已有成功标量 `LD` 的静态路径记录，但没有对应的双核运行时证据。先确认现有 runner 能否运行一个边界明确的案例并观察架构结果，避免在可行性未知时建设新验证设施。

## Capabilities

- **CAP-1**
  - **intent:** 学习者能够判断并说明在两套固定快照中运行一个成功标量 `LD` 案例所需的输入、现有执行入口和结果观察能力。
  - **success:** 对每个实现记录候选输入、可复现命令、runner 结果或具体阻塞原因，以及能否观察预期 `rd` 值和退休；据此给出继续、调整或停止的明确结论，不把静态源码推断写成动态证据。

## Constraints

- 使用 `sources.lock` 中的 Kunminghu V2 与 Heliodor 固定快照；先复用现有测试和 runner。
- 案例限于 RV64I 自然对齐、无异常的单条标量 `LD`；M-mode Bare、DCache hit、无更老重叠 store 是现有学习记录的候选边界，需由可行性检查确认是否能建立和观察。
- 不修改上游 RTL。只有现有入口不能提供必要观察且可行性结论支持时，才可另行提出隔离探针；本规范不授权通用 trace harness。
- 同一二进制若无法用于两侧，可评估语义等价的独立输入，并记录差异；不得预设输入或运行环境兼容。

## Non-goals

- 初始可行性阶段不建设新的 runner、探针或通用 trace harness；后续获用户明确同意后，只新增了使用现有 runner 和 Heliodor 现有 debug retirement port 的局部 LD fixture/capture。
- 不覆盖 `SD`、异常、向量、cache miss/refill、转发、性能/PPA、完整 ISA 符合性或上游 RTL 修改。
- 可行性结果不代表双核等价或整体符合性。

## Success signal

一份可审查的可行性记录对两侧分别给出输入、命令、观察点和证据状态，并以明确门槛决定是否值得开展后续动态验证。若现有入口可用，应以实际运行证据确认预期 `rd` 值和退休；若不可用，应定位具体阻塞，不将缺失证据记为通过。

## Assumptions

- 本工作先做可行性判断；是否进入双核运行验证或新增隔离探针，由结果和后续决策决定。

## Recorded Decision

- 用户接受 Heliodor 锁定 RV64UI LD suite 的 `tohost/pass` 作为**部分证据**，可先复用现有隔离 runner 运行。该结果不满足逐条退休/rd 观察，也不代表 Kunminghu 证据或双核等价；这些缺口仍需单独处理。
- Kunminghu 已有单条受控 fixture 的动态证据：目标 LD 在 commit trace 中退休，EA 与 rd 值匹配预期；DCache hit 未观察。其输入不同于 Heliodor suite，不构成双核等价。
- Veryl 与 NEMU 参考库经路径/文件类型复核均已存在；先前记录的缺失是检查方式造成的误判，详见 companion feasibility 更新。
- 后续在同一隔离案例中使用共享源 `experiments/rv64-ld-probe/ld.S` 与 linker，分别构建并运行两侧；Kunminghu raw image 与 Heliodor HEX 解码结果均为 4104 bytes，SHA-256 `f19127caaf66f2101b299459c2c10355a15f9b12a26490e4a3ff2d1f9701f50f`。两侧目标 LD 都通过，Kunminghu 观察 EA，Heliodor 观察 retirement PC/rd/data。详见 companion validation-scope 与 LD2-E19。
