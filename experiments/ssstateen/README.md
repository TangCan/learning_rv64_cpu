# Ssstateen 隔离访问实验

本目录保存学习者编写的 M/HS 与 S-mode CSR 输入，不修改锁定的 `sources/` 上游快照。`ssstateen_probe.hex` 保留耐久 M/HS 基线；`ssstateen_probe_s.hex` 增加从 HS 切换到 S 后对 `sstateen0–3` 的读、写、读回；`ssstateen_probe_s_gates_v3.hex` 独立对 M.SE0–3 清零/置位读回，并在 S-mode 对应读取四个 `sstateen` CSR。固定 Heliodor 快照的 CPU-started `run-fail` 观察显示：clear 阶段四个读取均未产生预期 cause 2；四个 set 写后控制位读回仍为 0，因此没有 gate-open 观察。完整证据在 `notes/units/evidence/smoke/heliodor-ssstateen-s-gates-all-slots-20261014/` 与 toolchain manifest。E13/E14 已补 VS guest 两阶段四槽读取：HS 将 hstateen0–3 清零后读回 0，VS 读 sstateen0–3 均完成且无 cause 22；HS 尝试设置 H.SE 后四个控制位仍读回 0，第二轮 VS 读取也均完成且无 cause 22。因此 gate-open 仍未验证，E15 已进入 VU 并确认对 supervisor-privilege `sstateen0–3` 的访问分别产生 cause 2，终止 ecall cause 8 到达 HS；这不是 H.SE gate 观察。E16 进一步确认 VU 在 FS=Initial 时 `fflags` 可读写：0 写为 1 后读回 1，无异常；H.FCSR 设 1 的尝试仍读回 0，故 gate clear/set 对照不可用。逐字段 WARL/reset 矩阵仍未覆盖。证据归档于 `notes/units/evidence/smoke/heliodor-ssstateen-vs-20261014/`、`heliodor-ssstateen-vs-set-20261014/` 与 toolchain manifest。

## 重建与运行

在仓库根目录执行：

```sh
make -C experiments/ssstateen clean all
riscv64-unknown-elf-objdump -dr experiments/ssstateen/ssstateen_probe.elf > experiments/ssstateen/ssstateen_probe.dis
riscv64-unknown-elf-objdump -dr experiments/ssstateen/ssstateen_probe_s.elf > experiments/ssstateen/ssstateen_probe_s.dis
WORK_DIR="$(python3 experiments/ssstateen/run_isolated.py)"
cd "$WORK_DIR"
/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_ssstateen
```

重跑带 M.SE0 控制位读回的 S gate fixture 时，使用 `--case s-gates-v3`：

```sh
WORK_DIR="$(python3 experiments/ssstateen/run_isolated.py --case s-gates-v3)"
cd "$WORK_DIR"
/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_ssstateen
```

`run_isolated.py` 将 `sources/heliodor/src`、锁文件和公共 arch harness 复制到唯一的 `/tmp/heliodor-ssstateen-isolated-*` 临时目录，避免删除其他运行或用户的数据。它只在副本中省略未实例化的 debug harness，并对公共 DRAM `$readmemh` 初始化添加 Veryl 0.22.0 所需的局部 lint allow。测试输入从本目录复制到隔离树。探针将最多 64 条 `mcause` 与操作 ID 分别记录，超过容量时不写数组但继续计数；报告缓冲区按完整容量分配。脚本会打印生成的目录路径。

## 已记录观察

GCC 15.1.0 构建生成 ELF、BIN、HEX 和反汇编文件；HEX 为 1025 words / 4100 bytes。ELF 链接器报告一个 RWX LOAD segment 警告。构建成功不代表 CPU 功能通过。

Veryl 0.22.0 在隔离树完成 build、check 和 CPU simulation。fixture 打印观测 trace 后断言规范预期 marker `tohost=0x2B`；当前快照实际为 `0x02`；Veryl test exit 1，报告 `Failed test (test_arch_ssstateen): Ssstateen expected 20 gate traps plus one HS ecall`，功能断言失败。复现日志：[归档运行日志](../../notes/units/evidence/heliodor-ssstateen-run-2026-10-14.log)。观测值为：八个 stateen reset 读值及 M 写全 1 后的八个读回值均为 0；M stateen 清零后 HS 对八个 stateen CSR 的 16 次读写及对 `henvcfg`/`senvcfg` 的 4 次读写没有产生预期 stateen trap；HS 开启阶段的状态 CSR 读回仍为 0，而两个 ENVCFG CSR 读回全 1。trap 记录只有 HS `ecall` 的 cause 9、操作编号 21，operation IDs 1–20 均未出现；`hstateen0.SE0` 读回为 0。观察结果与规范预期的 20 次 gate trap、1 次 ecall 且 `SE0=1` 不符，因此功能结果是 **run-fail**，不是 `run-pass`。

原 Heliodor 仓库中的 `veryl test --test test_arch_ssstateen` 匹配 0 个测试；原有 `test_arch_hvscsr` 在 testbench check 阶段因 `$readmemh`/`dram` `invalid_initial_assign` 退出，仿真未启动。隔离运行解决的是此 harness check 阻塞，不改变上游。VS/VU guest 均已实测进入；E15/E16 记录 VU `sstateen` privilege trap 与 `fflags` 访问。VU FCSR gate clear/set 对照仍未覆盖。

Kunminghu 快照 SHA 与 `sources.lock` 一致；初次 preflight 因 Mill launcher 不存在而失败，后续固定临时 Mill launcher 后推进到 RTL 生成及 Verilator/C++ 编译，仍未启动 CPU。当前 `ssstateen_probe.hex` SHA-256：`65391f26edfcd03fe56182e53b393e99b8a2500c49e8599f97fbaed49104c789`。


Story 6.8 harness 复核修正：旧测试曾错误地对 `sstateen0–3` 也断言 bit 63；现只断言 `hstateen0–3` 的定义 SE 位，并对 `sstateen0.JVT/FCSR`、`sstateen1–3` 的 RO-zero 字段及 `hstateen1–3` 保留字段增加限定断言。

VS 两阶段复现命令：

```sh
make -C experiments/ssstateen ssstateen_probe_vs_v2.hex
python3 experiments/ssstateen/run_isolated.py --case vs-v2
```

VU 特权级 CSR 访问复现命令：

```sh
make -C experiments/ssstateen ssstateen_probe_vu.hex
python3 experiments/ssstateen/run_isolated.py --case vu
```

VU FCSR 状态访问复现命令：

```sh
make -C experiments/ssstateen ssstateen_probe_vu_fcsr.hex
python3 experiments/ssstateen/run_isolated.py --case vu-fcsr
```
