# 源码与环境基线

采集日期：2026-10-12（Asia/Shanghai）
用途：Story 1.1 来源、源码导航和可运行条件的基线。源码位置和测试入口是对锁定快照的检查结果；本记录没有执行 CPU 测试、仿真或构建。

## 固定来源

| 项目 | Snapshot ID | 仓库 / 分支 | 完整 commit | 本地 checkout |
| --- | --- | --- | --- | --- |
| Kunminghu V2 | `xiangshan-kunminghu-v2-20261012` | [OpenXiangShan/XiangShan](https://github.com/OpenXiangShan/XiangShan) / `kunminghu-v2` | `c098f996bf4d301b88693b20315486d31e93bc9d` | `sources/xiangshan` |
| Heliodor | `heliodor-master-20261012` | [dalance/heliodor](https://github.com/dalance/heliodor) / `master` | `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `sources/heliodor` |

精确 SHA、快照 ID、日期和路径以项目根目录 [`sources.lock`](../sources.lock) 为锁定记录。后续学习记录在 frontmatter 的 `source_snapshots` 字段逐字引用对应 `snapshot_id`；切换快照时新增 snapshot 条目和带日期的 `snapshot_events` 事件，不覆盖旧条目，并在相关学习记录中说明是否仍可直接比较。两份 checkout 均以 `--depth=1` 获取指定 SHA，并处于 detached HEAD；已检查 `git rev-parse HEAD` 与锁文件相同。未初始化子模块。Git checkout 未做源码修改。

## 主机与资源

采集于项目工作区所在主机：

| 项目 | 观察结果 |
| --- | --- |
| OS / 内核 / 架构 | Ubuntu 24.04.4 LTS；Linux `6.8.0-146-generic`；x86_64 |
| 项目盘可用空间 | 浅克隆前 227 GiB；两个 checkout 完成后 `df -h .` 显示 226 GiB 可用（文件系统总量 1.8 TiB） |
| 内存 | checkout 完成后 `free -h` 显示 190 GiB available（总量 251 GiB） |
| Git | 2.43.0 |
| Verilator | 5.020 (2024-01-01, Debian build) |
| Icarus Verilog | 12.0 |
| RISC-V ELF GCC | `riscv64-unknown-elf-gcc` 15.1.0；Heliodor 锁定工具链说明使用 GCC 16 / binutils 2.43，本机版本不匹配 |
| Make / Python / uv | GNU Make 4.3；Python 3.12.3；uv 0.12.5 |
| Scala / SBT / Mill / Veryl | 未安装或不可从当前 `PATH` 调用；XiangShan 的 `Makefile.test` 直接调用 Mill，运行时还需 Java（本机为 17.0.20.1）；无需单独安装 Scala/SBT 才能调用该目标 |
| RISC-V Linux GNU GCC | `riscv64-unknown-linux-gnu-gcc` 未安装或不可从当前 `PATH` 调用 |
| Sail / Ruby | `sail_riscv_sim` 与 `ruby` 当前不可从 `PATH` 调用；Heliodor ACT4 还需要 Sail RISC-V 与 Ruby/UDB |

容器/虚拟机隔离方式和资源限额未由本故事核实。调查阶段上游 API 给出的仓库规模为 XiangShan 127033 KiB、Heliodor 29078 KiB（仅 API 指标，不是本机 checkout 占用）；本机资源充足，因此选择项目内 Git 忽略的 `sources/` 便于源码导航和引用，并使用浅克隆节省存储与获取时间。克隆后 `du -sh` 显示 XiangShan 与 Heliodor checkout 分别约 12 MiB、273 MiB（包含 `.git`；`.git` 分别约 2.8 MiB、11 MiB）。API 规模和 pack 大小均不等于解包后的工作树占用。`sources/` 规则避免将上游 checkout 放入本项目提交。


关键环境信息可用以下命令复查：

```sh
cat /etc/os-release
uname -srmo
df -h .
free -h
git --version
java -version
verilator --version
iverilog -V
make --version
gcc --version
python3 --version
uv --version
riscv64-unknown-elf-gcc --version
```

通过 `command -v mill scala sbt veryl sail_riscv_sim ruby riscv64-unknown-linux-gnu-gcc` 检查当前 `PATH` 上的关键工具；checkout 占用可用 `du -sh sources/xiangshan sources/heliodor sources/xiangshan/.git sources/heliodor/.git` 查看。

以下命令适用于项目根目录下尚不存在 `sources/xiangshan` 与 `sources/heliodor` 的首次建立；若目录已存在，先核对其是否为本项目登记的 checkout，不要直接覆盖或删除其中内容。两个精确快照的 shallow checkout 使用以下命令建立：

```sh
mkdir -p sources/xiangshan sources/heliodor
git -C sources/xiangshan init
git -C sources/xiangshan remote add origin https://github.com/OpenXiangShan/XiangShan.git
git -C sources/xiangshan fetch --depth=1 origin c098f996bf4d301b88693b20315486d31e93bc9d
git -C sources/xiangshan checkout --detach FETCH_HEAD
git -C sources/heliodor init
git -C sources/heliodor remote add origin https://github.com/dalance/heliodor.git
git -C sources/heliodor fetch --depth=1 origin 94e9c5821c24a8941c3ddc3b76daddc7124a855a
git -C sources/heliodor checkout --detach FETCH_HEAD
```

## 源码与验证入口

下表路径依据对应锁定快照检查。上游 README 中的能力或验证结果是仓库声明；本故事只确认文件、目录和命令入口存在，没有重跑这些验证。

| Snapshot ID | HDL / 核心源码位置 | 已有测试或仿真入口（检查过，未运行） | 本机可运行条件与阻塞 |
| --- | --- | --- | --- |
| `xiangshan-kunminghu-v2-20261012` | Chisel / Scala；核心设计位于 `src/main/scala/xiangshan/`，含 `backend/`、`frontend/`、`mem/` 等；核心模块可从 `src/main/scala/xiangshan/XSCore.scala` 的 `XSCore` 追踪，tile 包装位于 `src/main/scala/xiangshan/XSTile.scala`。 | `Makefile.test` 声明 `test`：`mill -i XiangShan.test.test`；定向入口 `test-DecodeUnit`：`mill -i XiangShan.test.testOnly xiangshan.DecodeUnitTest`。测试源码可见于 `src/test/scala/`。仓库 README 另列仿真入口 `make emu`，需先生成 Verilog/模拟器。 | 需要 Mill 及仓库依赖；Mill 当前不可用。完整 Verilator 仿真需构建和环境配置。本故事不初始化子模块，也不构建、不运行测试。 |
| `heliodor-master-20261012` | Veryl；核心入口为 `src/core/heliodor_core.veryl`（`heliodor_core` 模块），SoC 入口见 `src/core/heliodor_soc.veryl`；其他核心模块包括 `decode.veryl`、`alu.veryl`、`rob.veryl`，共享模块见 `src/cache/`、`src/mmu/`、`src/pkg/`。 | README 的默认测试入口：`veryl test`；另有 `test/` 下分类测试和 `tb/` 下 Veryl testbench。README 给出 ACT4 入口 `make -C test/act`，以及 `test/riscv-arch-test` 的 Makefile。以上均仅检查入口。 | 默认测试需 Veryl；当前不可用。ACT4 需 ELF GCC、Sail、uv 及 Ruby/UDB；uv 已安装，Sail 和系统 Ruby 当前不可用。Linux 镜像构建需 `riscv64-unknown-linux-gnu-gcc`，当前不可用。已有 ELF GCC 15.1.0 与上游说明的 GCC 16 不同。未运行任何测试。 |

文件/命令检查依据：`sources/xiangshan/README.md`、`Makefile.test`、`sources/heliodor/README.md`、`toolchain/README.md`，均来自表中对应 SHA。Heliodor README 中报告的测试通过和启动结果属于上游对自身的声明，不是本机观察结果。

## 自检记录

## Story 1.1 核验结果

| 核验项 | 观察结果 |
| --- | --- |
| Kunminghu HEAD | `c098f996bf4d301b88693b20315486d31e93bc9d`，与 `sources.lock` 一致 |
| Heliodor HEAD | `94e9c5821c24a8941c3ddc3b76daddc7124a855a`，与 `sources.lock` 一致 |
| Git 忽略规则 | `git check-ignore -v` 对两个 checkout 均命中 `/sources/` 规则 |
| Sprint 状态文件 | validator 输出 `{"ok": true, "valid": true, "problems": []}` |
| CPU 测试/仿真/构建 | 未运行；符合故事边界 |


- **问题：** 两边的核心源码目录和至少一个现有测试入口分别在哪里？
- **答案：** `xiangshan-kunminghu-v2-20261012` 的 Chisel 核心位于 `sources/xiangshan/src/main/scala/xiangshan/`；已检查 `sources/xiangshan/Makefile.test` 的 `mill -i XiangShan.test.test` 入口。`heliodor-master-20261012` 的 Veryl 核心位于 `sources/heliodor/src/core/`；已检查其 README 中的 `veryl test` 入口。
- **证据状态：** `inspected`（路径、Makefile/README 命令已检查）；没有 `run-pass` 或 `run-fail` 证据。本机尚不能运行两边默认入口，因为缺 Mill 与 Veryl。

精确 SHA 的错误路径也做了隔离模拟：在临时本地 bare 仓库请求一个不存在的 SHA，`git fetch --depth=1` 返回非零（128），没有创建 HEAD 或 refs；真实来源 checkout 未受影响。真实两份 checkout 的 SHA 已逐字核对 `sources.lock`，均为浅克隆且无工作区改动。

## 尚未完成或待后续确认

- 未验证容器/虚拟机隔离细节、工具链安装方式、生成物位置和清理步骤；本故事按边界不安装工具链。
- `veryl test`、XiangShan Mill 测试、Verilator 仿真及 ACT4 均未运行；不据此推断测试通过或失败。
- 后续如需运行，先依据对应锁定快照补齐工具链并记录完整命令、配置、输入、预期/观察结果和产物位置。
