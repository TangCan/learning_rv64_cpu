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
| `LD`、`SD` | 自然对齐 64 位访问；LD 使用同步读，SD 在执行级写入 |

其余编码、非 8 字节对齐地址及内存范围外访问均令 `unsupported_instruction` 拉高且不提交该访存操作；当前不提供 trap/CSR 行为。x0 恒为零。数据前递和通用相关停顿尚未实现，相关测试在依赖指令间插入 NOP；每条有效 LD 会暂停取指/译码三个周期，以便同步读响应独占退休口。分支和 JAL 会清除两条年轻指令。

## Story 1.3：同步内存访存切片

数据内存为 8 个 64 位字，地址以字节计，映射 `0x00`–`0x3f`；自然对齐的 LD/SD 地址低三位必须为零。初始字为 `mem[0]=0x1122334455667788`、`mem[1]=0x8877665544332211`，其余为零。Bitloom 同步读在采样地址后一拍将数据送入读寄存器；读响应的 valid、PC 和 rd 经过对应两级元数据寄存器配对。SD 在 EX 所在时钟沿写入，读写同址按读先于写处理。测试通过 SD 后 LD 回读验证内存写入。

`wb_valid/wb_pc/wb_rd/wb_data` 用于观察寄存器写回；`retire_valid/retire_pc` 观察本切片的提交 PC，`store_valid/store_pc/store_addr/store_data` 观察存储事务。依赖访存结果的程序必须自行插入 NOP；本切片不处理转发、停顿或访存异常。

确定性输入程序与期望结果放在 [`tests/smoke.rs`](tests/smoke.rs)：覆盖 ADDI 的符号扩展边界、ADD/SUB/AND/OR/XOR、x0、BEQ/BNE 的跳转与顺序路径、正负分支/JAL 偏移、错误路径 flush、LUI/AUIPC 结果及非法 opcode/funct 编码告警。所有结果来自 Bitloom 周期仿真；Kunminghu 和 Heliodor 的固定流程拒绝自定义输入，因此参考差分仍未验证。
