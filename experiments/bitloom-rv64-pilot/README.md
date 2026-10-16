# Bitloom RV64 pilot

独立的 Bitloom 教学试点，用来验证一个可运行、可比较的 RV64 学习切片。它不修改或替换 Kunminghu、Heliodor，也不声称实现完整 RV64I、RVA23 或产品级 CPU。

## 工具链

- Rust/Cargo：1.98.1（执行前检查版本；当前仓库未锁定 Rust 工具链）
- Bitloom CLI、`bitloom-prelude`、`bitloom-sim`：1.2.4
- Icarus Verilog：12.0
- `bitloom-sim` 使用 `u64` 信号值，128 位向量结果必须通过生成 Verilog 的外部 HDL 仿真验证。

## 运行与导出

从仓库根目录执行；以下命令使用忽略的 `target/` 作为构建输出，CLI 安装在隔离目录：

```sh
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo fmt --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml -- --check
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml
cargo install --locked --root target/bitloom-cli --version 1.2.4 bitloom
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo install --list --root target/bitloom-cli
CARGO_TARGET_DIR=target/bitloom-rv64-pilot PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build \
  --package bitloom_rv64_pilot \
  --manifest-dir experiments/bitloom-rv64-pilot \
  --out-dir "$PWD/target/bitloom-out"
```

## Story 1.1：工具链最小闭环

8 位计数器 tick 测试通过；Bitloom CLI 1.2.4 成功生成 Verilog。导出保留 64/128 位端口和同步存储器声明，但没有存储器读写事务，也没有通过 `bitloom-sim` 验证 128 位数据。命令输出、工具版本、生成 RTL 和哈希保存在 [`minimal-2026-10-15`](../../notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/)；RTL SHA-256 为 `c5d6053d5536183f9ea3f6bff58c77a90412c82726df7c5f5c8d57557eac179f`。

## Story 1.2：RV64I 有序执行切片

Bitloom HIR 实现 IF、ID、EX、WB 四阶段、64 位 x0–x31 架构寄存器、ALU、PC 和分支重定向。外部每周期根据 `fetch_pc` 驱动 `instruction_in`；写回通过 `wb_valid/wb_pc/wb_rd/wb_data` 观察，`debug_reg_addr/debug_reg_data` 提供寄存器检查口。

本 Story 支持以下 RV64I 指令：

| 指令 | 行为 |
| --- | --- |
| `LUI`、`AUIPC` | 立即数装载、PC 相对立即数 |
| `JAL` | 写回 `PC+4` 并跳转 |
| `BEQ`、`BNE` | 相等/不等条件分支 |
| `ADDI`、`ADD`、`SUB` | 64 位加减与立即数加法 |
| `AND`、`OR`、`XOR` | 64 位按位运算 |

其余编码均令 `unsupported_instruction` 拉高，不产生写回；当前不提供 trap/CSR 行为。x0 恒为零。没有数据前递或停顿逻辑，相关测试在依赖指令间插入 NOP；分支和 JAL 会清除两条年轻指令。load/store 由后续 Story 1.3 处理。

确定性输入程序与期望结果放在 [`tests/smoke.rs`](tests/smoke.rs)：覆盖 ADDI 的符号扩展边界、ADD/SUB/AND/OR/XOR、x0、BEQ/BNE 的跳转与顺序路径、正负分支/JAL 偏移、错误路径 flush、LUI/AUIPC 结果及非法 opcode/funct 编码告警。所有结果来自 Bitloom 周期仿真；尚未与 Kunminghu 或 Heliodor 做参考差分。
