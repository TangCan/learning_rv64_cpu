# Bitloom RV64 pilot — Story 1.1 smoke

该小实验只验证独立 consumer 项目能否用 Bitloom 1.2.4 elaborate、tick 和导出 Verilog。8 位计数器不是 RV64 CPU；宽端口与同步存储器仅验证表达/导出，不代表 128 位仿真正确。

## 工具链

- Rust/Cargo：1.98.1（执行前检查 `rustc --version` 和 `cargo --version`；本仓库没有锁定 Rust 工具链）
- Bitloom CLI、`bitloom-prelude`、`bitloom-sim`：1.2.4
- Icarus Verilog：12.0（本 Story 不运行 HDL 仿真）
- Bitloom `bitloom-sim` 使用 `u64` 值；128 位检查只能依据 HIR/生成 Verilog，不使用其 tick 仿真。

## 运行

从仓库根目录执行。以下命令会把编译产物放入仓库忽略的 `target/`，CLI 安装在隔离目录；`cargo install --list` 应显示 `bitloom v1.2.4`：

```sh
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo fmt --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml -- --check
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml
cargo install --locked --root target/bitloom-cli --version 1.2.4 bitloom
CARGO_TARGET_DIR=target/bitloom-rv64-pilot cargo install --list --root target/bitloom-cli
CARGO_TARGET_DIR=target/bitloom-rv64-pilot PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build \
  --package bitloom_rv64_pilot \
  --manifest-dir experiments/bitloom-rv64-pilot \
  --out-dir "$PWD/target/bitloom-out"
cp target/bitloom-out/BitloomRv64Pilot.v notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/
```

## 结果

- `cargo fmt --check`：通过。
- `cargo test`：通过，`counter_ticks_and_wide_ports_elaborate` 1 passed。
- `cargo bitloom build`：Bitloom CLI 1.2.4 成功生成 `target/bitloom-out/BitloomRv64Pilot.v`。
- Verilog 保留 `[63:0]` 和 `[127:0]` 端口，并输出 `reg [63:0] memory [0:15] /* SyncReadMem */`。这只证明表达/导出；内存没有读写事务，未验证同步读延迟。
- 可复核证据（命令输出、工具版本、CLI 哈希、生成 RTL）：[`notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/`](../../notes/units/evidence/bitloom-rv64-pilot/minimal-2026-10-15/)。RTL SHA-256：`91404af9cbeb3271c06d7e00c23ef64682ea22bde426931cb15b4f8f6150205b`。
- 初次 CLI 构建因脚手架包名连字符/下划线映射失败；统一 Cargo 包名为 `bitloom_rv64_pilot` 后成功。没有升级 Bitloom。
