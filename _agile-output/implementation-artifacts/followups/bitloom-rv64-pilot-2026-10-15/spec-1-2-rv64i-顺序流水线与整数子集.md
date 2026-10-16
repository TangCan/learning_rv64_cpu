---
title: Story 1.2 — 建立 RV64I 顺序流水线与整数子集
type: feature
created: '2026-10-16'
status: done
route: oneshot
review_loop_iteration: 0
context:
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/prd.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/ARCHITECTURE-SPINE.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epics.md
---

## Intent

在 Bitloom 1.2.4 中建立可周期仿真的 RV64I 教学核心切片，明确指令范围和不支持行为。通过确定性程序观察 PC、分支目标和架构寄存器写回，为后续访存和参考差分故事提供基础。

## 实现范围

- 四阶段 IF/ID/EX/WB 顺序流水线；通过 `fetch_pc` 和 `instruction_in` 与测试侧指令源交互。
- 64 位 x0–x31 架构寄存器、ALU、PC、写回观测口和分支 flush。
- 指令：`LUI`、`AUIPC`、`JAL`、`BEQ`、`BNE`、`ADDI`、`ADD`、`SUB`、`AND`、`OR`、`XOR`。其他编码报告为 `unsupported_instruction` 且不写回。
- 不含数据前递、停顿、异常/trap、CSR、load/store；有 RAW 依赖的程序需由调用者插入 NOP。

## 验收标准

- Given 支持指令编码，when 程序被逐周期输入，then 立即数、ALU 和 link 结果按 64 位架构语义写回。
- Given BEQ/BNE/JAL，when 分支或跳转在 EX 阶段生效，then fetch PC 指向目标且两条年轻指令不会提交。
- Given x0 或不支持的编码，when 读取或执行，then x0 保持零，非法指令输出有效且不发生寄存器写回。
- 测试源码内保存输入程序和精确期望值；运行结果仅代表 Bitloom 周期仿真，不宣称与参考 CPU 等价。

## 验证

- `cargo fmt --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml -- --check`
- `cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml`
- Bitloom CLI 1.2.4 `cargo bitloom build` 用于提前确认流水线 HIR 可导出；综合与参考差分留待对应故事。

## 实施记录

- 通过 Bitloom Builder HIR 实现 IF/ID、ID/EX、EX/WB 寄存器和展开的 32 项寄存器文件。
- `tests/smoke.rs` 覆盖整数写回、ADDI 符号扩展边界、所有已实现 ALU 运算、x0、BEQ/BNE taken/fall-through、正负分支/JAL 偏移、flush、LUI/AUIPC 和非法 opcode/funct 编码。
- 固定版本下 `cargo test` 为 5 passed，Bitloom CLI 导出成功，Icarus Verilog elaboration 检查退出码 0；运行记录位于 `notes/units/evidence/bitloom-rv64-pilot/rv64i-subset-2026-10-16/`。
- 暂不支持数据冒险的前递/停顿以及 trap/CSR；覆盖边界详见 `experiments/bitloom-rv64-pilot/README.md`。

## Review Triage Log

| Finding | Disposition | Evidence |
| --- | --- | --- |
| SUB/AND/OR/XOR 没有执行结果断言 | patched | `tests/smoke.rs::addi_and_add_write_back_64_bit_registers` 断言四种结果。 |
| BEQ/BNE 缺少 not-taken 覆盖 | patched | `tests/smoke.rs::conditional_branches_redirect_and_flush_wrong_path` 检查顺序路径写回。 |
| B 型负偏移未覆盖 | patched | `tests/smoke.rs::negative_branch_and_jal_offsets_redirect_to_previous_pc` 检查 PC 8 目标。 |
| J 型负偏移未覆盖 | patched | 同一用例检查 PC 4 目标和 link 写回。 |
| ADDI 立即数边界未覆盖 | patched | 测试断言 2047 和 -2048 的 64 位结果。 |
| 非法 opcode/funct 编码覆盖不足 | patched | 非法 opcode 与不支持的 R-type funct3 均检查告警，且无效指令不产生 `wb_valid`。 |
| `wb_valid` 对非写回指令误报 | patched | `ex_wb_valid` 现由 `wb_we_next` 驱动；分支与非法指令不会报告写回。 |
| 缺少生成 RTL 的周期仿真 | deferred | Story 1.2 的验收范围为 Bitloom 周期仿真和 RTL elaboration；独立 HDL 运行属于后续导出/验证工作。本 Story 已通过 Icarus elaboration，不宣称等价性。 |
