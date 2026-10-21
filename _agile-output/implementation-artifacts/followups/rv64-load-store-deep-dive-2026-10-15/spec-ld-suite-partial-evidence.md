---
title: '隔离运行 Heliodor RV64UI LD suite 并归档部分证据'
type: 'feature'
created: '2026-10-16'
status: 'complete'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/specs/spec-rv64-ld-dynamic-validation/SPEC.md'
  - '{project-root}/_agile-output/specs/spec-rv64-ld-dynamic-validation/validation-scope.md'
  - '{project-root}/experiments/heliodor-smoke/README.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Heliodor 已有锁定快照的 `test_arch_rv64ui_ld` 和 LD hex，但当前隔离 runner 只支持其他目标，无法在不改上游 checkout 的前提下运行并归档该 suite。用户接受 suite 级 `tohost/pass` 作为部分证据。

**Approach:** 扩展既有 Heliodor 隔离 runner 选择并运行 LD arch target，沿用固定 Veryl、源快照校验、输入哈希、超时和 manifest 归档。结果只表述该 LD suite 自检通过；不声称观测到某条 LD 的退休 PC/rd 值，也不声称 Kunminghu 等价。

**Boundaries & Constraints:** 只修改项目 runner、对应测试和 README；不得修改 `sources/heliodor`。保留既有基础 smoke 与锁定工具/源校验。测试失败或未观察到 LD target 的 `tohost=1/pass=1` 与 PASS marker 时，不得记录 `run-pass`。

**Never:** 不新增通用 trace harness，不把 suite 级结果扩大为逐条 LD 结果、双核比较或 RVA23 符合性结论。

</frozen-after-approval>

## Implementation Notes

- Added `--topic ld` to the existing isolated Heliodor runner, selecting the locked `test_arch_rv64ui_ld` target and `rv64ui/ld.hex`; source checkout remains untouched.
- Archived successful run `heliodor-core-20261016T055817Z-2342121`: both base smoke and LD suite markers passed; suite reports `tohost=1/pass=1`.
- Added runner tests and README usage/limits. `PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 -m pytest -q scripts/tests/test_heliodor_smoke.py` passed: 45 tests.
- Evidence is suite-level only. Per-instruction retirement/rd, cache-hit observation, Kunminghu LD run, and dual-core equivalence remain unverified.
