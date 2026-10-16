---
title: 'Story 1.4 — 受限 128 位 vadd.vv 案例'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
context:
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/prd.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/ARCHITECTURE-SPINE.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epics.md
---

## Intent

实现固定 VLEN=128、SEW=32、LMUL=1、VL=4 的 `vadd.vv` 向量寄存器示例。使用生成 Verilog 的 128 位 HDL 仿真验证四个 lane 和 lane 截断；不把 `bitloom-sim` 的 u64 端口观察当作 128 位证据。

## Boundaries

- `vector_init` 把 128 位源向量载入 v1/v2 并清零目的 v3。
- `vadd_enable` 且 VL=4、SEW=32、LMUL=1 时，时钟沿将四个 32 位 lane 和写入 v3。
- 每个 lane 独立截断；不产生跨 lane 进位。
- 其他 VL/SEW/LMUL 配置通过 `vector_unsupported` 显式拒绝，不更新 v3。
- 该独立模块不实现指令译码、其他 RVV 配置、掩码、尾部/掩码策略或异常。

## Implementation

- `experiments/bitloom-vector-case/` -- 固定依赖并独立生成 `BitloomVectorCase`，保持 RV64 核心 Bitloom Sim 的单模块前提。
- `experiments/bitloom-vector-case/tests/vector_case_tb.sv` -- Icarus testbench，检查两组全宽结果、lane overflow 截断及三类不支持配置。
- `notes/units/evidence/bitloom-rv64-pilot/story-1-4-2026-10-16/` -- RTL、测试平台、完整构建/仿真/综合日志、配置和哈希。

## Acceptance

- [x] 四个 32 位 lane 结果均由 Icarus 实际检查，覆盖边界与溢出截断。
- [x] 对 VL、SEW、LMUL 不匹配案例报告 unsupported 且目的向量保持不变。
- [x] 明确向量源寄存器初始化、VLEN/SEW/LMUL/VL 和不支持范围。
- [x] 尝试固定 Kunminghu/Heliodor 流程；两者不含向量入口，结果保留为自检而非双核验证。

## Verification

- `cargo fmt --manifest-path experiments/bitloom-vector-case/Cargo.toml -- --check` -- pass。
- `cargo check --locked --manifest-path experiments/bitloom-vector-case/Cargo.toml` -- pass。
- `cargo bitloom build --package bitloom_vector_case --manifest-dir experiments/bitloom-vector-case --out-dir "$PWD/target/bitloom-vector-out"` -- pass; generated 128-bit ports/data path.
- `iverilog -g2012 -s vector_case_tb ... && vvp ...` -- pass; two arithmetic cases and three unsupported configurations.
- Yosys 0.33 `hierarchy -check; proc; opt; check; synth; stat` -- pass; zero check problems, 1,274 generic cells. No technology library, timing constraints or PPA claim.
- Kunminghu runner rejected unsupported `vector-case` topic at argument validation (exit 2); Heliodor did likewise. Neither CPU started and no vector reference result was produced.

## Review Triage

Code changes were inspected locally against the Story acceptance. Separate package is necessary because Bitloom `Sim` rejects multi-module HIR; adding a second module to the RV64 package would break its existing simulation harness. No separate reference differential exists because the locked runners expose no vector topic/case.
