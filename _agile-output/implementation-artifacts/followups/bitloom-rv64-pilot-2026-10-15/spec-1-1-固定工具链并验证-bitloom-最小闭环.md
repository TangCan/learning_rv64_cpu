---
title: Story 1.1 — 固定工具链并验证 Bitloom 最小闭环
type: feature
created: '2026-10-15'
status: review
route: oneshot
review_loop_iteration: 0
context:
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/prd.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/ARCHITECTURE-SPINE.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epics.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

在 `experiments/bitloom-rv64-pilot/` 建立最小外部 Cargo 项目，精确固定 Bitloom 1.2.4。设计仅依赖 `bitloom-prelude`，`bitloom-sim` 仅作开发依赖；用 8 位计数器验证 tick 状态变化，并以隔离安装的 `cargo bitloom` 生成 Verilog。另 probe 64/128 位信号和同步存储器的表达/导出能力；失败时记录首个阻塞且不升级依赖。记录工具链、命令、结果和产物 SHA-256，不修改上游 RTL。`bitloom-sim` 信号值限 `u64`，128 位只以生成 Verilog 和宽度足够的 HDL 仿真验证，不能声称由 Bitloom 周期仿真验证。

</frozen-after-approval>

## Implementation Notes

项目没有现成 Rust 工作区；本机 Rust/Cargo 1.98.1、Icarus Verilog 12.0。CLI 和 crate 1.2.4 可在独立 consumer 使用。`cargo bitloom new` 的 hyphen 包名在 host shim 中映射为 underscore 后无法解析，改成 underscore 包名解决。仓库未固定 Rust 工具链，README 明确版本前置条件并记录本机可执行文件版本。

实现文件：`.gitignore`、`experiments/bitloom-rv64-pilot/{Cargo.toml, Cargo.lock, README.md, src/lib.rs, tests/smoke.rs}`。测试 1 passed；CLI 生成的 Verilog SHA-256 为 `91404af9cbeb3271c06d7e00c23ef64682ea22bde426931cb15b4f8f6150205b`，包含 64/128 位端口和 64 位 SyncReadMem。该 memory 仅声明，未验证读写时序；`bitloom-sim` 仍不支持对大于 64 位信号给出完整仿真值。原始 RTL、测试日志、CLI 构建日志及工具版本/哈希已归档于 `notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/`。旧访存阶段状态未改。

## Review Triage Log

- 归档生成 RTL 与测试/构建日志：已解决；证据目录包含原始 Verilog 和两份命令日志。
- Rust 工具链可复现性：已解决到本故事要求的记录级别；README 要求并提示核对 Rust/Cargo 1.98.1，工具可执行路径与完整版本记录在 `toolchain.txt`。仓库没有强制安装/锁定 Rust 工具链。
- CLI 版本可核对性：已解决；安装清单记录 `bitloom v1.2.4`，并记录 CLI 可执行文件 SHA-256。
- 重复的 AD-8：已解决；删除重复决策，AD-6 保留宽度验证约束。
