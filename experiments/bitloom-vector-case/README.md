# Bitloom 向量案例

从仓库根目录运行向量 RTL testbench：

```sh
make -C experiments/bitloom-vector-case test-icarus
```

该命令先从当前 crate 源码重新生成 `BitloomVectorCase.v`，再编译并运行已提交的 `tests/vector_case_tb.sv`。需要安装 Bitloom CLI 1.2.4 到 `target/bitloom-cli`（见 pilot [工具链说明](../bitloom-rv64-pilot/README.md#运行与导出)），并确保 Icarus Verilog 的 `iverilog`、`vvp` 在 `PATH` 中。生成 RTL 和仿真文件写入本 crate 被忽略的 `target/` 目录。构建、编译、仿真或 `$fatal` 失败时，make target 会返回非零状态。
