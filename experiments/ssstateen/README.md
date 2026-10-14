# Ssstateen 隔离访问实验

本目录保存学习者编写的 M/HS CSR 输入，不修改锁定的 `sources/` 上游快照。固定输入探测 `sstateen0–3`、`hstateen0–3` 的 reset 可见值、写读回，以及 M `SE0/SE`、`ENVCFG` 清零/置位前后的 HS 访问。每个 20 项受控 CSR 操作在陷阱路径记录独立操作编号和 `mcause`，测试分别断言数量、顺序、cause 与每个 stateen CSR 的定义 `SE0` 位；未知 WARL 位只保留 trace，不作全值预设。VS/VU 与逐字段 WARL 矩阵不在此 fixture 的覆盖范围。

## 重建与运行

在仓库根目录执行：

```sh
make -C experiments/ssstateen clean all
riscv64-unknown-elf-objdump -dr experiments/ssstateen/ssstateen_probe.elf > experiments/ssstateen/ssstateen_probe.dis
WORK_DIR="$(python3 experiments/ssstateen/run_isolated.py)"
cd "$WORK_DIR"
/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_ssstateen
```

`run_isolated.py` 将 `sources/heliodor/src`、锁文件和公共 arch harness 复制到唯一的 `/tmp/heliodor-ssstateen-isolated-*` 临时目录，避免删除其他运行或用户的数据。它只在副本中省略未实例化的 debug harness，并对公共 DRAM `$readmemh` 初始化添加 Veryl 0.22.0 所需的局部 lint allow。测试输入从本目录复制到隔离树。探针将最多 64 条 `mcause` 与操作 ID 分别记录，超过容量时不写数组但继续计数；报告缓冲区按完整容量分配。脚本会打印生成的目录路径。

## 已记录观察

GCC 15.1.0 构建生成 ELF、BIN、HEX 和反汇编文件；HEX 为 1025 words / 4100 bytes。ELF 链接器报告一个 RWX LOAD segment 警告。构建成功不代表 CPU 功能通过。

Veryl 0.22.0 在隔离树完成 build、check 和 CPU simulation。fixture 打印观测 trace 后断言规范预期 marker `tohost=0x2B`；当前快照实际为 `0x02`；Veryl test exit 1，报告 `Failed test (test_arch_ssstateen): Ssstateen expected 20 gate traps plus one HS ecall`，功能断言失败。复现日志：[归档运行日志](../../notes/units/evidence/heliodor-ssstateen-run-2026-10-14.log)。观测值为：八个 stateen reset 读值及 M 写全 1 后的八个读回值均为 0；M stateen 清零后 HS 对八个 stateen CSR 的 16 次读写及对 `henvcfg`/`senvcfg` 的 4 次读写没有产生预期 stateen trap；HS 开启阶段的状态 CSR 读回仍为 0，而两个 ENVCFG CSR 读回全 1。trap 记录只有 HS `ecall` 的 cause 9、操作编号 21，operation IDs 1–20 均未出现；`hstateen0.SE0` 读回为 0。观察结果与规范预期的 20 次 gate trap、1 次 ecall 且 `SE0=1` 不符，因此功能结果是 **run-fail**，不是 `run-pass`。

原 Heliodor 仓库中的 `veryl test --test test_arch_ssstateen` 匹配 0 个测试；原有 `test_arch_hvscsr` 在 testbench check 阶段因 `$readmemh`/`dram` `invalid_initial_assign` 退出，仿真未启动。隔离运行解决的是此 harness check 阻塞，不改变上游，也不覆盖 VS/VU 行为。

Kunminghu 快照 SHA 与 `sources.lock` 一致；初次 preflight 因 Mill launcher 不存在而失败，后续固定临时 Mill launcher 后推进到 RTL 生成及 Verilator/C++ 编译，仍未启动 CPU。当前 `ssstateen_probe.hex` SHA-256：`65391f26edfcd03fe56182e53b393e99b8a2500c49e8599f97fbaed49104c789`。
