---
unit_id: "rva23s64-zifencei"
stage_id: "Epic 5 / Story 5.2"
scope: "RVA23S64/v1.0/§3.1.2.2/Zifencei；对比锁定 Kunminghu V2 与 Heliodor 快照上的 FENCE.I 本地 hart 同步路径及可观察自修改代码测试材料。"
exclusions:
  - "不宣称 RVA23S64 符合性或认证。"
  - "FENCE.I 只提供执行它的 hart 的本地同步；远端 hart 必须各自执行 FENCE.I，并由软件/运行时协调。"
  - "不覆盖非一致性设备写入、所有缓存层/内存属性组合、并发写入竞态或多 hart 发布协议。"
  - "测试未运行的编码字段、边界和行为均保持未验证。"
spec_refs:
  - name: "Zifencei"
    edition: "v2.0, ratified"
    section: "FENCE.I instruction"
    url: "https://docs.riscv.org/reference/isa/v20240411/unpriv/zifencei.html"
    profile_category: "RVA23S64 mandatory extension"
  - name: "RVA23 Profile"
    edition: "v1.0, ratified"
    section: "§3.1.2.2/Zifencei; §3.1.2 note N2"
    url: "https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html"
    profile_category: "mandatory"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

## 规范契约与范围

Zifencei v2.0 定义 `FENCE.I`：在同一 hart 上，指令保证此前该 hart 可见的数据存储，对该 hart 后续的指令取指可见。RVA23S64 v1.0 §3.1.2.2 要求 Zifencei，并在 N2 说明它是 profile 中支持指令缓存一致性的标准机制。执行 `FENCE.I` 不会向其他 hart 广播指令缓存失效；跨 hart 发布代码还需要写入 hart 执行数据 `FENCE`、通知远端 hart，并让每个可能执行新代码的远端 hart 自行执行 `FENCE.I`。

本记录把证据分为规范、静态 RTL、检查过的测试/机器码和实际运行。RTL 路径只能支持静态映射；测试文件和反汇编不能替代仿真结果。

## Kunminghu V2 路径

锁定目标是 `sources.lock` 中 `xiangshan-kunminghu-v2-20261012`，实测 HEAD 为 `c098f996bf4d301b88693b20315486d31e93bc9d`。`DecodeUnit.scala` 将 `FENCE_I` 译为 `FuType.fence/FenceOpType.fencei`，并设置 `noSpec`、`blockBack`、`flushPipe`。`FuConfig.scala` 的 Fence 配置为非流水且 `flushPipe=true`。

`Fence.scala` 在 `s_idle` 接收操作后请求 store-buffer flush，在 `s_wait` 等待 `sbIsEmpty`；`FENCE.I` 随后进入 `s_icache`，使 `fencei` 拉高一个周期。`XSCore.scala` 将此信号送至 frontend；`Frontend.scala` 用 `RegNext` 传给 I-cache。`ICache.scala` 的 `metaArray.io.flushAll` 清除缓存有效状态，并把 fencei 传给 miss unit。静态代码可见 `ICacheMissUnit.scala` 在失效期间抑制新请求/唤醒，返回 SRAM 写使能也受 fencei/flush 条件抑制；这些接线本身不能证明已发起 miss/fill 的时序竞态都正确收敛。具体重取时序和在途 miss/fill 的竞争结果尚未运行验证。

在锁定 checkout 的 `src/test/scala` 有界检索未定位到定向 `FENCE.I` 自修改代码用例。因此本地新增 [Kunminghu 汇编 fixture](../../experiments/rva23s64-zifencei/kunminghu-self-modifying.S) 和运行说明；它是待接入该目标仿真 harness 的测试输入，不是已运行结果。使用 `.option norvc` 固定补丁函数布局，避免压缩指令改变被覆写区域。

## Heliodor 路径

锁定目标 `heliodor-master-20261012` 的实测 HEAD 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。`decoder.veryl` 在 `MISC_MEM` 且 `funct3=001` 时置 `is_fence_i`；core 将该位写入 ROB，ROB 只允许它在头部提交。core 串行化条件包含 `c_is_fence_i`，提交确认且 store buffer 空后产生 `commit_fence_i_pulse`。当 `COHERENT_IFETCH==0` 时还有 D-cache 写回/失效路径；I-cache 收到 pulse 后清所有 way 的 valid，并在被打断的 fill 完成时不写入有效 tag/data。提交还触发 redirect 到 `c_pc+4`，清理年轻指令并重新取指。代码注释解释这是为避免 fence 后续指令已被旧代码提前取入 fetch buffer/ROB。

静态检查到 testbench `test_arch_rv64ui_fence_i` 将 `HEX_FILE` 设为并加载 `test/riscv-arch-test/build/rv64ui/fence_i.hex`，运行预算为 300000 clocks，输出 `tohost` 并断言 pass。该 hex 在锁定 Heliodor checkout 中为已跟踪文件，SHA-256：`ec1cd95a76b513a5f68aae6bc12d18c64deff877231dc11ae1a43e8c904d85f3`。checkout 不含生成此 hex 的源测试或 build provenance，故无法确认它的生成过程/来源子案例。对该 hex 按每行 little-endian 32-bit 指令静态反汇编（临时转换文件 `/tmp/fence_i.bin`，不属于仓库产物）：在 `0x2004/0x2006` 写入两段指令后，偏移 `0x1d0` 的 `FENCE.I` 编码为 `0x0000100f`；随后间接跳转并检查 `a3==444`。第二轮在 `0x200c/0x200e` 写入，偏移 `0x20c` 的 `FENCE.I` 编码同为 `0x0000100f`，再间接跳转并检查 `a3==777`。444 与 777 是输入机器码中的期望/检查值，不是本次 CPU 观察值。

## 编码字段覆盖

标准 `FENCE.I` 的 `imm[11:0]`、`rs1`、`rd` 字段保留；软件应写零，基础实现必须忽略这些字段。Heliodor 输入中偏移 `0x1d0`、`0x20c` 的机器码均为 `0x0000100f`（`imm[11:0]=0, rs1=0, rd=0`）。Kunminghu fixture 的对象反汇编在偏移 `0x20` 显示 `0x0000100f`，三个字段也均为零。此类静态检查仅证明所检查的输入编码；两侧的非零保留字段覆盖均未验证。译码 RTL 对 opcode/funct3 分类的静态观察不能代替非零字段测试。

## 双核比较

Kunminghu 显式走独立 Fence 单元，先请求 store-buffer flush，再拉高前端 fencei；Heliodor 在 ROB 提交点串行化，等待 store buffer 排空，触发 I-cache flush 和后继 PC redirect。两者均有本地存储排序与取指失效/重取线索。Heliodor 的已检查 hex 包含两轮自修改代码及 444/777 检查值；这些不是 CPU 观察结果。Kunminghu 没有已定位的现成用例，新增 fixture 尚未接入/运行。现有静态比较不能证明两侧均通过自修改代码，也不能证明跨 hart 发布。

## 证据与结果

| ID | Claim | Kind | Status | 快照/位置 | 命令、配置或观察 |
|---|---|---|---|---|---|
| E1 | Zifencei 本地契约、profile 必选项与远端边界 | spec | inspected | Zifencei v2.0；RVA23S64 v1.0 §3.1.2.2/N2 | 规范材料；无运行 |
| E2 | Kunminghu 译码、排序、I-cache失效与 miss 请求抑制接线 | source | inspected | DecodeUnit.scala、FuConfig.scala、Fence.scala、XSCore.scala、Frontend.scala、icache/ICache.scala、ICacheMissUnit.scala | 静态可见 valid 清除及失效期间请求/唤醒和返回 SRAM 写使能抑制条件；在途 miss/fill 竞态的实际收敛时序未验证 |
| E3 | Heliodor 译码、ROB提交、store drain、缓存失效、redirect重取 | source | inspected | decoder.veryl、decode.veryl、rob.veryl、heliodor_core.veryl、cache/icache.veryl | 锁定源码静态追踪；动态结果未验证 |
| E4 | Heliodor 自修改代码输入及检查值 | test-inspected | inspected | `tb/test_arch_common.veryl:test_arch_rv64ui_fence_i` 加载 `test/riscv-arch-test/build/rv64ui/fence_i.hex`；该文件在 checkout 中已跟踪，生成 provenance 不可得；SHA-256 `ec1cd95a76b513a5f68aae6bc12d18c64deff877231dc11ae1a43e8c904d85f3` | 静态反汇编：`0x1d0`、`0x20c` 均为 `0x0000100f`；两轮 store + FENCE.I + indirect execution 的检查值分别为 444/777，不是 CPU 观察值 |
| E5 | Kunminghu 本地自修改代码 fixture | experiment | unverified | `experiments/rva23s64-zifencei/kunminghu-self-modifying.S` | `riscv64-unknown-elf-gcc` 15.1.0 以 `-march=rv64imac_zifencei -mabi=lp64 -nostdlib -c` 汇编；对象反汇编的偏移 `0x20` 是 `0x0000100f` (`fence.i`)；store 写入 `0x02a00513`，目标函数为 32-bit `addi a0,zero,1` + `ret`。旧/新检查值为 1/42，成功 `tohost` 值为 `0x600d`，这些是期望检查值，无 CPU 观察值；未接入可运行 harness |
| E6 | Heliodor 定向运行尝试 | test-run | run-fail | Heliodor 锁定 checkout；Veryl `0.22.0 (967e477 2026-10-02)`；`Veryl.toml` 默认 test simulator=`verilator` | cwd `sources/heliodor`；`/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_rv64ui_fence_i`，输入为检入 `test/riscv-arch-test/build/rv64ui/fence_i.hex`；Veryl check 在 `tb/test_arch_common.veryl:440` 因 `$readmemh(HEX_FILE, dram)` 的 `invalid_initial_assign` 退出 1，测试体未启动。CLI 输出只在本次终端返回，未保存日志文件；无仿真产物。裸 `veryl` PATH 调用也返回 127。 |
| E7 | 保留字段覆盖 | test-inspected | unverified | E4/E5 机器码 | Heliodor 偏移 `0x1d0`、`0x20c` 均为 `0x0000100f`；fixture 偏移 `0x20` 为 `0x0000100f`；每处 `funct12=0, rs1=0, rd=0`。非零 `funct12/rs1/rd` 均无测试覆盖 |

## 验证状态与未决问题

- 两个 checkout HEAD 与 `sources.lock` 完全一致。
- PATH 中没有 `veryl`；通过本机安装路径取得 Veryl `0.22.0 (967e477 2026-10-02)` 并执行定向命令。Veryl 在 testbench check 阶段以 `invalid_initial_assign` 阻断：`tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)`；退出码 1，仿真测试体未启动。本轮未修改上游文件，未安装工具；此目标不是运行通过。
- Kunminghu `make emu CONFIG=KunminghuV2Config NUM_CORES=1` 是源码 Makefile/README 支持的构建路线，但它只构建通用 `build/emu`；当前缺 `mill`，且本仓库没有该 fixture 的链接脚本/映像装载配置与 `tohost` 采集流程，故无法运行此案例。
- Kunminghu fixture 已用交叉编译器汇编并静态检查布局；对象写入临时目录。该检查仅证明输入编码/布局，不是 CPU 执行结果。
- 所有动态自修改代码结果、非零保留字段、在途 fill 竞争、错误/边界访问及实际前端重取时序未验证。
- 多 hart 远端失效与代码发布协议不在 `FENCE.I` 单指令保证内，须由软件分别协调并在每个 hart 执行本地同步。

## 单元自检

1. 本地保证是什么？hart 执行 `FENCE.I` 后，它后续取指能观察到此前该 hart 可见的数据写入；不自动使别的 hart 的 I-cache 同步。
2. 两侧代码路径相同吗？否。Kunminghu 使用 Fence 状态机请求 store-buffer flush 后通知 frontend；Heliodor 从 ROB 提交点等待 store drain，清 I-cache 并 redirect 后继 PC 重取。
3. 哪些证据能说明自修改测试通过？本轮没有运行结果。Heliodor hex 只被静态反汇编，Kunminghu 仅有本地 fixture。
4. 非零保留字段是否覆盖？否；检查的机器码与 fixture 的 `funct12`、`rs1`、`rd` 均为零，非零行为保持未验证。

## 后续验证

先在可用环境运行 Heliodor `veryl test --test test_arch_rv64ui_fence_i` 并保存实际退出状态、tohost/assert 输出与日志位置；再将 Kunminghu fixture 接入锁定单核配置的现有 test harness，记录构建配置、输入、结果和日志。若需测试忽略保留字段，另生成 `funct12`、`rs1`、`rd` 各自非零且其余编码有效的用例，并观察是否按规范执行。
