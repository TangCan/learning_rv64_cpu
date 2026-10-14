# Zifencei 本地汇编 fixture（仅测试输入）

此文件提供汇编与静态布局检查说明，不是完整可运行的 CPU 测试。fixture 尚无链接脚本、内存映射、镜像装载、入口设置或 `tohost` 采集 runner。

`kunminghu-self-modifying.S` 是本地 RV64 汇编 fixture。它先调用 `patched`
并检查旧指令返回 1，然后把该指令改为 `addi a0,zero,42`，执行 `fence.i`
后再次调用并检查新值 42；两个检查都通过时向 `tohost` 写入 `0x600d`，
否则写入 1。这里的数值是测试期望/检查值；本机没有 CPU 执行观察值。

## Kunminghu 路线与运行限制

锁定源码的 `Makefile` 将 `CONFIG` 传给 Verilog 仿真生成目标，默认
`NUM_CORES=1`；项目 README 给出的可用目标形式是 `make emu CONFIG=...`。
因此目标构建命令为：

```sh
cd sources/xiangshan
make emu CONFIG=KunminghuV2Config NUM_CORES=1
```

这条命令构建 `build/emu`，不会自动加载或执行本 fixture。当前环境缺少
`mill`，所以构建在生成仿真器前置阶段不可用；Verilator、Docker 与交叉
GCC 可用。对锁定 checkout 的 `src/test/scala` 执行 `rg -ni 'fence\.i|fence_i|fencei|zifencei|self.?modif' sources/xiangshan/src/test/scala`（退出码 1，无匹配）；这是有界文本检索，不排除其他路径或间接用例。仓库没有将本 fixture 接入 Kunminghu 测试目标，也没有为它提供
链接脚本/内存映射、加载与入口参数、`.tohost` 结果采集脚本及运行日志
流程。因此本地不能给出 CPU 运行命令或观察值。未来 runner 还需定义 `.tohost` section 的链接地址、镜像装载地址以及成功 `0x600d`/失败 `1` 的采集约定；当前源码中的 section 声明本身不定义这些平台约定。不能把该源码或对象文件称为
已运行的 Kunminghu harness；后续需补齐这些输入和观测步骤后才能运行。

Assembly layout check (not a CPU test):

```sh
out_obj=$(mktemp /tmp/kunminghu-fencei-XXXXXX.o)
riscv64-unknown-elf-gcc -march=rv64imac_zifencei -mabi=lp64 -nostdlib -c ../../experiments/rva23s64-zifencei/kunminghu-self-modifying.S -o "$out_obj"
riscv64-unknown-elf-objdump -dr "$out_obj"
```

fixture 使用 `.option norvc`。反汇编确认旧函数是 32-bit `addi a0,zero,1`
加 `ret`；store 写入 `0x02a00513` (`addi a0,zero,42`)，随后位于 `.text`
偏移 `0x20` 的 `fence.i` 编码为 `0x0000100f`。它使用
`riscv64-unknown-elf-gcc` 15.1.0 汇编到 `/tmp` 临时对象；没有 CPU 执行。

Heliodor candidate command from `sources/heliodor`:

```sh
veryl test --test test_arch_rv64ui_fence_i
```

Heliodor testbench 将 `HEX_FILE` 明确设为
`test/riscv-arch-test/build/rv64ui/fence_i.hex` 并加载该路径。此文件在锁定
checkout 中为已跟踪文件，SHA-256 为
`ec1cd95a76b513a5f68aae6bc12d18c64deff877231dc11ae1a43e8c904d85f3`；本
checkout 不含生成该 hex 的源测试与 build provenance，不能据文件名推断其
生成过程或上游子案例来源。

该定向命令于 2026-10-13 使用本机 Veryl
`0.22.0 (967e477 2026-10-02)` 尝试。testbench check 停在
`tb/test_arch_common.veryl:440`（`invalid_initial_assign`：
`$readmemh(HEX_FILE, dram)`），退出码 1，仿真未启动。PATH 中的 `veryl`
调用退出 127。未修改上游文件，也未安装工具。
