# Story 1.2 运行证据

- `cargo-test.log`：固定 Bitloom 1.2.4 consumer 的周期仿真测试输出，5 项通过。
- `bitloom-build.log`：Bitloom CLI 1.2.4 从设计生成 Verilog 的命令输出。
- `hdl-check.log`：Icarus Verilog 12.0 对生成模块的语法/elaboration 检查，退出码 0。
- `hdl-check.log` 仅记录 Icarus 对生成 RTL 的语法与 elaboration 检查，并非周期 HDL 仿真。
- 程序输入与期望值由仓库内 `experiments/bitloom-rv64-pilot/tests/smoke.rs` 保存；本测试没有运行上游参考 CPU。
