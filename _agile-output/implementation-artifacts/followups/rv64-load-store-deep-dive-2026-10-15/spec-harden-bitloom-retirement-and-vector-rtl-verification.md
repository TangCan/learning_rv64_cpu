---
title: '补强 Bitloom 退休观察与向量 RTL 验证入口'
type: 'bugfix'
created: '2026-10-16'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: '2cda518db72fdcc8eff1a8bfb93f571a3b94fbcb'
context:
  - /nvme_data1/richard/learning_rv64_cpu/experiments/bitloom-rv64-pilot/README.md
  - /nvme_data1/richard/learning_rv64_cpu/experiments/bitloom-vector-case/tests/vector_case_tb.sv
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/implementation-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epic-1-retro-2026-10-16.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Bitloom RV64 的 smoke tests 没有明确断言 SD 紧邻普通指令时的退休 PC 顺序；回顾中的审阅报告提出了可能的 PC 覆盖，但现有流水线时序尚未通过 directed case 单独确认。向量 testbench 已覆盖生成 RTL 的算术及配置拒绝行为，却只能按归档命令手动运行，缺少从当前源码重新生成 RTL 并运行它的标准入口。

**Approach:** 增加 SD 后立即跟随普通指令的退休顺序回归用例；若该用例暴露真实丢失，再以最小改动修复退休仲裁。为独立向量 crate 增加可重复的 Icarus 验证 target，并在 README 记录依赖与调用方式。

## Boundaries & Constraints

**Always:** 使用当前源码生成的 `BitloomVectorCase.v`；保留现有 testbench 作为唯一向量断言源；失败必须以非零退出码结束。退休验证断言每条应退休指令的 PC 和顺序。

**Never:** 不扩大指令/向量范围，不依赖归档快照 RTL 代替当前源码构建，不更改 Kunminghu/Heliodor runner 或泛化 CPU 架构。

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| SD 后普通指令 | 程序含 SD@0 后紧接 ADDI@4 | `retire_pc` 依序观察到 0、4，各一次；若失败则修复共用时序逻辑 | Regression test 失败时非零退出 |
| 向量 HDL 验证 | crate 源码、Bitloom CLI 1.2.4、Icarus | 生成 RTL、编译 testbench 并输出 PASS | 工具缺失、生成/编译错误或 `$fatal` 均令 target 失败 |

</frozen-after-approval>

## Code Map

- `experiments/bitloom-rv64-pilot/src/lib.rs` -- `retire_ex_next`、`store_valid_reg`、`ex_retire_valid` 和退休输出组合逻辑。代码审查发现 store 与 EX retirement 都由 ID/EX 元数据注册，SD 排除 EX retirement；SD 后紧邻普通指令的覆盖结论需由 directed 仿真核实。只在用例失败时改动逻辑。
- `experiments/bitloom-rv64-pilot/tests/smoke.rs` -- 复用 `reset`、`addi`、`sd` 和逐周期驱动方式，新增退休序列断言。
- `experiments/bitloom-vector-case/tests/vector_case_tb.sv` -- 现有唯一 HDL testbench，不复制、不弱化断言。
- `experiments/bitloom-vector-case/Cargo.toml` -- crate/包名 `bitloom_vector_case`；Bitloom CLI 插件与依赖固定为 1.2.4。
- `experiments/bitloom-vector-case/Makefile` -- 新增本 crate 的 `test-icarus` 入口；参考 `experiments/ssstateen/Makefile` 的 Make 约定。由目标源码构建到忽略的 `target/`，再调用 `iverilog` 和 `vvp`。
- `experiments/bitloom-rv64-pilot/README.md` -- 核心 Cargo 测试的既有命令/版本前置条件参考；不要改动该 crate 的行为范围。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/bitloom-rv64-pilot/tests/smoke.rs` -- 增加 SD@0 紧接 ADDI@4 的定向测试，逐周期收集退休 PC 并断言顺序、唯一性；若失败，再在 `src/lib.rs` 做最小修复。
- [x] `experiments/bitloom-vector-case/Makefile` -- 从当前 crate 生成 RTL，运行既有 Icarus testbench，输出仅读忽略的 `target/`。
- [x] `experiments/bitloom-vector-case/README.md` -- 记录 make 命令及 Bitloom CLI/Icarus 前置条件。

**Acceptance Criteria:**
- Given 一条 SD 后立即跟随独立 ADDI，when 仿真观察退休输出，then SD 与 ADDI 的 PC 依序各出现一次；其余访存/执行回归继续通过。
- Given Bitloom CLI 1.2.4 和 Icarus 已安装，when 在仓库根执行 `make -C experiments/bitloom-vector-case test-icarus`，then 从当前 RTL 生成开始完整通过现有 HDL testbench。
- Given CLI 或 Icarus 缺失/失败，when 执行 `test-icarus`，then 目标明确失败并返回非零状态。

## Implementation Notes

Investigation: initial code inspection indicates the specifically alleged SD→non-memory PC loss may be a false positive: SD sets `store_valid_reg`, while the younger instruction's `ex_retire_valid` is registered on the following edge. Add a direct test before changing RTL. A separate store/load-response overlap has not been established and is outside this fix unless the directed timing evidence shows it is caused by this path.

The repeatable vector target should use the installed pinned CLI from `target/bitloom-cli/bin` through PATH and write generated RTL/simulation binaries under ignored `target/`. It must build current sources instead of using archived output. No dependency additions are expected.

Implementation result: the new directed regression passed with unchanged retirement logic, confirming the reported SD→ADDI PC-loss finding was a false positive for this scenario. No RTL change was needed. The vector Make target builds the current crate source and runs the checked-in testbench; generated artifacts remain under the ignored crate `target/`.

## Spec Change Log

## Review Triage Log

| Reviewer finding | Verdict | Evidence / disposition |
|---|---|---|
| Blind Hunter: retirement test does not require PC 0 and PC 4 to be consecutive. | false | The frozen acceptance requires each PC once and in order; it does not require adjacency in the full retirement stream. The test checks both counts and their order. |
| Blind Hunter: Make target may use a Bitloom CLI other than 1.2.4. | medium — patch | Verified: PATH selection alone did not enforce the installed package version. Added a preflight using `cargo install --list --root target/bitloom-cli`; it requires `bitloom v1.2.4` and emits an explicit error otherwise. |
| Blind Hunter: missing Icarus tools may not be clearly reported. | false | The make recipe invokes `iverilog` and `vvp` directly; a missing executable produces the shell's `command not found` and a nonzero make result, satisfying the frozen acceptance. |
| Blind Hunter: generated target files may dirty the checkout. | false | `git check-ignore -v` confirmed `.gitignore:9` pattern `target/` covers both generated RTL and simulation output under this crate. |
| Edge Case Hunter | no findings | No additional boundary issue reported. |
| Verification Gap Reviewer | no findings | No additional verification gap reported. |

## Verification

**Commands:**
- `cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml` -- expected: all smoke tests pass, including the directed retirement-order case.
- `make -C experiments/bitloom-vector-case test-icarus` -- expected: current RTL builds, Icarus compiles/runs the testbench, and it prints PASS.

Results: Cargo ran 10 smoke tests, all passed; the new `store_then_addi_retire_in_pc_order_once_each` passed. The Make target requires the installed CLI to report v1.2.4, rebuilt `BitloomVectorCase.v` from current sources, and Icarus printed `PASS: VLEN=128 SEW=32 LMUL=1 VL=4 vadd.vv lanes and rejects`. A stub reporting CLI v9.9.9 was rejected with nonzero exit; a failing `iverilog` stub propagated a nonzero make result.
