---
title: Story 1.1 — 固定工具链并验证 Bitloom 最小闭环
type: feature
created: '2026-10-15'
status: done
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

实现文件：`.gitignore`、`experiments/bitloom-rv64-pilot/{Cargo.toml, Cargo.lock, README.md, src/lib.rs, tests/smoke.rs}`。测试 1 passed；CLI 生成的 Verilog SHA-256 为 `c5d6053d5536183f9ea3f6bff58c77a90412c82726df7c5f5c8d57557eac179f`，包含 64/128 位端口和 64 位 SyncReadMem。该 memory 仅声明，未验证读写时序；`bitloom-sim` 仍不支持对大于 64 位信号给出完整仿真值。原始 RTL、测试日志、CLI 构建日志及工具版本/哈希已归档于 `notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/`。旧访存阶段状态未改。

## Review Triage Log

- medium / patch — README 与本 Story 记录的 RTL SHA 与归档 Verilog 不符（实际值见 `sha256.txt`）；已同步为实测哈希并归档命令输出。
- false — `rust-version = 1.97.1` 是 manifest 最低版本声明，不代表实际验证版本；README 和 `toolchain.txt` 明确记录本次使用 Rust/Cargo 1.98.1。
- false — smoke 未覆盖 reset，不违反 Story 1.1 的最小状态 tick 验收；故事没有要求验证 reset 行为。
- false — 测试未断言 memory 节点不等于未探测；归档 Verilog 直接包含 `reg [63:0] memory [0:15] /* SyncReadMem */`，README 也限定未验证读写时序。
- false — 归档 CLI 构建日志与生成 RTL 证明本次导出成功；Story 1.1 要求一次性 smoke 证据，没有要求自动化 CLI 回归。
- false — 构建日志中的绝对路径是本次运行环境记录，不影响命令复现说明或验收；README 给出从仓库根目录运行的命令。
- false — Edge Case Hunter 指出的 128 位 HDL 仿真缺失已在 README 明示，且属于 Story 1.4 的验收范围，不是 Story 1.1 的遗漏。

- 归档生成 RTL 与测试/构建日志：已解决；证据目录包含原始 Verilog 和两份命令日志。
- Rust 工具链可复现性：已解决到本故事要求的记录级别；README 要求并提示核对 Rust/Cargo 1.98.1，工具可执行路径与完整版本记录在 `toolchain.txt`。仓库没有强制安装/锁定 Rust 工具链。
- CLI 版本可核对性：已解决；安装清单记录 `bitloom v1.2.4`，并记录 CLI 可执行文件 SHA-256。
- 重复的 AD-8：已解决；删除重复决策，AD-6 保留宽度验证约束。
- 复核归档 RTL SHA：原记录与文件不符；以 `sha256sum` 重新计算并同步 README/本 Story，输出保存在 `notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/sha256.txt`。
- Rust `rust-version` floor、reset 测试、内存导出断言、自动化 CLI 导出与绝对路径日志：不改变本 Story 的验收结论；固定版本、实际 tick、Verilog 导出及其原始产物/日志均已有直接证据，这些建议属于额外回归或可移植性改进。
- 128 位 HDL 仿真：Story 1.1 只要求探测 128 位导出；lane 级 HDL 仿真属于 Story 1.4，README 已明确此次未运行。
