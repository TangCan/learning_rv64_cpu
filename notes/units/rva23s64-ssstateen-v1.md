---
unit_id: "rva23s64-ssstateen"
stage_id: "Epic 5 / Story 5.6"
scope: "RVA23S64/v1.0/§3.1.2.2/Ssstateen；对照固定 Kunminghu V2 与 Heliodor 快照中的 sstateen0–3、hstateen0–3、SE0/ENVCFG 分层访问和 CSR 异常路径。"
exclusions:
  - "不宣称 RVA23S64 符合性或认证。"
  - "不把 Heliodor ACT 配置、搜索缺项或一次读零单独作为实现缺失证据；结论限于本次检查的 CSR RTL 路径。"
  - "Kunminghu 没有 CPU 运行观察；Heliodor 仅运行 M/HS 隔离 fixture。所有 WARL、reset 可见值和异常结论都区分已观察结果与尚未逐项验证内容。"
  - "不将 M-level mstateen0–3 本身计作 RVA23S64 Ssstateen 要求；只把它们当成门控控制寄存器。"
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0 ratified"
    section: "§3.1.2.2/Sha/Ssstateen"
    url: "https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html"
    profile_category: "mandatory"
  - name: "Smstateen/Ssstateen"
    edition: "v1.0"
    section: "§3.1.1–3.1.3"
    url: "https://docs.riscv.org/reference/isa/v20260120/priv/smstateen.html"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

## 范围与结论

RVA23S64 v1.0 §3.1.2.2 在 `Sha` 组合项中明确要求 `Ssstateen`：必须提供 supervisor-mode `sstateen0–3` 和 hypervisor-mode `hstateen0–3`。Smstateen/Ssstateen v1.0 定义了这些 CSR 的分层访问关系、字段约束与 WARL/RO-zero 规则。此单元核对八个 CSR、M/HS/S/VS/VU 的可适用控制路径，并区分结构路径与 CPU 运行观察。

**结论按证据范围限定：** Kunminghu 活动 `NewCSR` 路径中有八个 CSR、字段/读写状态和 SE0 门控的静态路径，当前分类为 `studied-unverified`；没有本轮 Kunminghu CPU 运行观察。Heliodor `csr.veryl` CSR read/write 主路径未保存 stateen 状态；相关地址落入默认读零/写忽略分支，通用权限检查也没有 SE0/ENVCFG 条件。隔离的 Heliodor CPU 用例实际观察到写入无读回、预期阻止阶段没有 stateen trap，支持这条固定 CSR 路径的静态缺失判断，故覆盖表记 `not-present`。该结果不扩大成其他项目集成或完整 RVA23 合规性结论。ACT `sail.json` 中 `Ssstateen.supported=false` 仅作附加配置线索，不作为该判定依据。

## 规范契约与字段清单

`Ssstateen` 本身包括 `sstateen*` 与 `hstateen*`；`mstateen*` 是 `Smstateen`，不是本 profile 行的直接 CSR 要求，但 M-level 对相同位的控制决定低层访问和只读掩码。

| CSR | RV64 地址 | 规范/实现字段 | 规范约束与本轮观察状态 |
|---|---:|---|---|
| `sstateen0` | `0x10C` | bit 2 `JVT`、bit 1 `FCSR`、bit 0 `C`；其余位保留 | 每个标准定义字段 WARL；未实现扩展/保留位 RO-zero。Kunminghu 将 JVT/FCSR 定义为 RO-zero、C 为 RW，CSR 宽度 32 bit；无运行写读回。Heliodor 主 CSR 路径无存储，地址读零、写忽略。 |
| `sstateen1` | `0x10D` | bit 31:0 保留 | Kunminghu 明确全字段 RO-zero；无运行写读回。Heliodor 主路径为默认读零/写忽略。 |
| `sstateen2` | `0x10E` | bit 31:0 保留 | 同 `sstateen1`。 |
| `sstateen3` | `0x10F` | bit 31:0 保留 | 同 `sstateen1`。 |
| `hstateen0` | `0x60C` | bit 63 `SE0`、62 `ENVCFG`、60 `CSRIND`、59 `AIA`、58 `IMSIC`、57 `CONTEXT`、56 `P1P13`，低位继承 `JVT/FCSR/C` | `P1P13`、未实现功能位及保留位按实现约束 RO-zero；`SE0`、`ENVCFG` 等受支持字段 WARL。Kunminghu 有字段与 M-level 对应位读掩码；无运行 WARL 观察。 |
| `hstateen1` | `0x60D` | bit 63 `SE`；其余位保留 | `SE` 控制对应 slot 的 `sstateen` CSR 访问；M 对应位为 0 时 H/S 视图 RO-zero。Kunminghu 静态定义；该 CSR 自身字段未声明 reset，读值又受 M 对应位掩码。 |
| `hstateen2` | `0x60E` | bit 63 `SE`；其余位保留 | 同 `hstateen1`。 |
| `hstateen3` | `0x60F` | bit 63 `SE`；其余位保留 | 同 `hstateen1`。 |

### 控制层

- `mstateen0.SE0` 控制非 M 模式对全部对应 `sstateen0` / `hstateen0` 的访问；`mstateen1–3.SE` 分别控制对应 slot。`hstateen0.SE0` 及 `hstateen1–3.SE` 控制 VS/VU 层对对应 `sstateen` CSR 的访问。
- `mstateen0.ENVCFG` 控制低于 M 的 `henvcfg` / `senvcfg` 访问；`hstateen0.ENVCFG` 控制 VS 对 `senvcfg` 的访问。`ENVCFG` 是受控目标 CSR 的门控字段，本单元用其访问来检查位 62 的开/关结果。
- 当 stateen 阻止某模式访问受控状态时，规范要求相应指令抛出 illegal-instruction；若执行在 VS/VU 且符合虚拟化陷阱条件，则抛出 virtual-instruction。被保护状态的访问权限与 CSR 自身的读写/特权级权限是不同检查。
- 规范要求 reset 时 `mstateen` 可写位为 0；software 负责在改变 M 对应位后初始化匹配的 H/S 位。`hstateen0.SE0` 规范上始终可写；标准定义位 WARL，未实现功能和保留位 RO-zero。不要把每个 `hstateen` 内部寄存器的硬件 reset 都假设为 0。

## Kunminghu V2 活动路径

锁定 HEAD 为 `c098f996bf4d301b88693b20315486d31e93bc9d`。配置中的 `CsrCfg` 实例化 `wrapper.CSR`，wrapper 在 [CSR.scala](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/CSR.scala#L22) 内实例化 `NewCSR`，因此本次追踪的是活动新 CSR 实现，不是同仓库 legacy `backend.fu.CSR`。

- `MachineLevel.scala` 定义 `mstateen0–3`；`mstateen0` 的可写字段和 `mstateen1–3.SE` 明确 reset 为 0。
- `SupervisorLevel.scala` 定义 `sstateen0–3` 并放入 supervisor CSR map。`sstateen0` 读视图按 `privState.isVirtual` 选择对应 M 或 H stateen 掩码；`sstateen1–3` 在此实现中为 RO-zero。
- `HypervisorLevel.scala` 定义 `hstateen0–3`；每个 `hstateen` 的读视图与对应 `mstateen` 做按位 AND。`hstateen1–3.SE` 字段没有单独 `.withReset`；CSR bundle 因字段初始化规则进入 reset 时，未声明 init 的字段值以零构造，但设计对其外显值仍以 M 对应位掩码为准。动态 reset 行为未跑。
- `StateEnBundle.scala` 给出本实现字段：`sstateen0` 位 2/1/0 为 `JVT`/`FCSR`/`C`，前两者 RO-zero，`C` RW；H/M stateen0 另有 SE0、ENVCFG、CSRIND、AIA、IMSIC、CONTEXT、P1P13 字段；H/M stateen1–3 只有 `SE[63]`，S stateen1–3 所有实现字段 RO-zero。
- `CSRPermitModule.scala` 对非 M 的八个 stateen 地址按 CSR slot 对应 M `SE0/SE` 做 illegal-instruction permit 检查；VS 的 `sstateen0–3` 访问再按 H `SE0/SE` 检查并进入 virtual-instruction permit。M `ENVCFG` 与 H `ENVCFG` 也分别门控低层 `henvcfg/senvcfg` 与 VS `senvcfg`。
- `CSRPermitModule` 将 permit 分类输出为 `EX_II` / `EX_VI`；`NewCSR.scala` 将两者输出，wrapper 的 exception vector 接到 illegal-instruction 与 virtual-instruction 两类异常。静态连线没有本轮 trap cause 观察。

由以上路径可说 Kunminghu 有可追踪的字段定义、CSR map、层级读掩码和控制逻辑；未证明配置下运行结果、异常 cause、写入 WARL 值或 VU/guest 行为完全符合规范。

## Heliodor 路径与判定边界

锁定 HEAD 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。对 `src/core/csr.veryl`、`alu_wrap.veryl`、`rob.veryl`、`heliodor_core.veryl` 的 CSR 状态、读写 decode、通用权限与 trap 提交路径进行了检查。

- `csr.veryl` 列有 `senvcfg`、`henvcfg` 等 CSR state/read/write case，但没有 `sstateen0–3` / `hstateen0–3` 状态变量、CSR 地址常量、read case 或 write case。未匹配读地址由 `rd_data_w=0` 默认分支处理；未匹配写地址进入 `default {}`，不会储存写入值。V=1 时 CSR read/write 的 S-CSR alias case 也未加入 `sstateen` 地址，因此同样没有对应状态。
- `alu_wrap.veryl` 的通用 checker 只看 CSR 地址只读编码、地址最低特权级和有限的 PMP odd-slot 特例；没有 SE0、ENVCFG 或 stateen 层级控制。对合法 S CSR 地址，generic privilege decode 可接受 M/S 访问；H 地址 `0x60C–0x60F` 在 HS 侧同样没有 stateen-specific storage 或 gate。checker 未显示虚拟 CSR access 的 stateen 专属 virtual-instruction 分支。
- `rob.veryl` 将 `csr_illegal` 记入 ROB illegal 标记。未追踪到 stateen 控制导致的 cause 2 / cause 22 路径，因为 stateen permit 来源不存在于所检查 CSR 路径。
- Heliodor ACT4 的 `test/act/config/heliodor/sail.json` 把 `Stateen.Ssstateen.supported` 设为 false、`C_readonly_zero=true`、`SE0_readonly_zero=false`。这是测试配置声明，不是 RTL 缺失判定的依据。

这里的 `not-present` 限定为“Heliodor 固定快照所检查的主 CSR 状态与访问路径没有提供 stateen 寄存器；通用默认读零/写忽略”。这不依赖负搜索或读零单独推断，也不声称已运行验证；若存在本轮未检查的外部 CSR 扩展路径，仍需另行核实。

## 受控访问用例与运行记录

`experiments/ssstateen/ssstateen_probe.S` 是可重建的 M/HS 输入，不改 `sources/`。启动段在 M 读出八 CSR reset 可见值；将 M 控制位打开后，对八个要求 CSR 执行写读回；再将 M `SE0/SE` 与 `ENVCFG` 清零进入 HS/S 阶段，依次读写 `sstateen0–3`、`hstateen0–3`、`henvcfg`、`senvcfg`，期望访问被阻止而落入 trap handler；HS 执行 `ecall` 后，M trap handler 将 `SE0/SE` 和 `ENVCFG` 置 1，再回到 HS 做第二轮允许访问并记录读回值。输出报告区分初值、M 写读回、清零控制读回、HS 开启后的值、trap cause 列表与结束 marker。这个 fixture 尚不能验证 VS/VU 的 H-level gate，也没有 pass/fail 架构断言；marker 仅表示程序走到末端。

构建记录（工作区 2026-10-13，Heliodor snapshot 未改）：

```sh
cd experiments/ssstateen
make clean && make
riscv64-unknown-elf-objdump -dr ssstateen_probe.elf > ssstateen_probe.dis
```

结果：GCC 15.1.0 成功汇编/链接；`bin2hex.py` 生成 `ssstateen_probe.hex`，输出 `1025 words (4100 bytes)`。ELF linker 有一个 RWX LOAD segment warning。hex SHA-256 为 `638383a6674e95e96f23c604b969d8b0bdb6033b3409db9b12449d7638caa70d`。这只是构建与反汇编检查，不是 CPU 执行。

| 检查/运行 | 命令 | 阶段与结果 |
|---|---|---|
| 两边快照核对 | `git -C sources/xiangshan rev-parse HEAD`; `git -C sources/heliodor rev-parse HEAD` | 两者分别与 `sources.lock` 相同：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`，Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。 |
| Kunminghu 构建/运行入口尝试 | `cd sources/xiangshan && make emu CONFIG=KunminghuV2Config NUM_CORES=1` | Make 生成入口命令后在构建前置阶段退出 2：`time: cannot run mill: No such file or directory`；没有生成/启动仿真器，也无 CSR 运行结果。仓库中未定位可独立运行的 stateen CSR test harness。 |
| Heliodor 原仓库专题 target | `cd sources/heliodor && veryl test --test test_arch_ssstateen` | Veryl `0.22.0 (967e477 2026-10-02)`；退出 0，但输出 `No tests matched filter 'test_arch_ssstateen'`、0 passed/0 failed/29 ignored。原快照没有该 target。 |
| Heliodor 原仓库现有共享 arch test | `cd sources/heliodor && veryl test --test test_arch_hvscsr` | check 阶段因 `tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)` 报 `invalid_initial_assign` 退出 1；仿真未启动。该 target 不测试 Ssstateen。 |
| Heliodor 隔离 controlled input | `python3 experiments/ssstateen/run_isolated.py`; 隔离 copy 内执行 Veryl target | build/check 成功，CPU 仿真完成。tohost=`0x02`；trap count 1、唯一 cause 9，唯一操作 ID 21（HS ecall），hstateen0.SE0=0；预期为 20 个 gate trap（cause 2，操作 ID 1–20）+ ecall（cause 9、ID21）且 SE0=1，故 marker 应为 `0x2B`，实际 `0x02`，行为结果 run-fail。测试现在逐项断言 cause、操作 ID 顺序及八个 stateen CSR 写后读回的定义 SE0 位；未知/WARL 保留位只输出 trace，不假定完整寄存器全值。当前运行以总 trap count 断言先失败，原始完整日志为 `/tmp/ssstateen-story-5-6-review-final.log`。VS/VU 未测。 |

`run_isolated.py` 将固定 Heliodor `src/` 复制到 `tempfile.mkdtemp(prefix="heliodor-ssstateen-isolated-")` 创建的唯一临时路径（本轮：`/tmp/heliodor-ssstateen-isolated-l_jpp8h2`），沿用公共 1 MiB arch harness 的 CPU、memory bus 与输入，不触碰 `sources/`；只省略未实例化、会触发 check 错误的 debug harness，并在私有副本的 DRAM declaration 上加 `#[allow(initial_assign)]`，使 Veryl 0.22.0 能执行原有 `$readmemh`。隔离 target 输出报告区：`trace[0..7]` 是八 CSR 初值，`trace[8..11]` 是 M stateen 控制写零后的读回，`trace[12..19]` 是 M 对八 CSR 写全 1 后的读回，`trace[24..31]` 是 HS 开启后的写读回，`trace[32..33]` 是 `henvcfg/senvcfg` 写读回，`trace[34]` 是 trap count，`trace[35..98]` 是按序 `mcause`，`trace[100..163]` 是每次 trap 前设置的操作 ID；每个 ID 对应一个被门控 CSR 读/写或最后的 ecall。报告缓冲区容量 1536 字节，最多保存 64 个 cause/ID 条目；溢出保护只跳过超量记录、仍更新总计数。

实际观察：`trace[0..31]` 全 0；`trace[32]=trace[33]=0xffff_ffff_ffff_ffff`；`trace[34]=1`，`trace[35]=9`，`trace[100]=21`，其余 cause/operation-ID 槽为 0。即 M 对 stateen CSR 写全 1 后读回零；M 控制清零阶段的 20 次 HS CSR 读/写都没有触发 stateen trap；只有 HS `ecall` 触发 cause 9/operation ID 21；hstateen0.SE0 写全 1 后仍读 0。程序将 `(trap_count << 1) | hstateen0.SE0` 写入 tohost，实际 `0x02`；按规范预期的输入控制应产生 20 个 CSR trap + 1 个 ecall，且 SE0=1，即 `0x2B`。改进后的测试逐条要求 operation ID 1–20 对应 cause 2、ID21 对应 cause 9；当前只看到 ID21/cause9。M/HS 对八个 stateen CSR 写入后的 SE0 bit63 也分别断言为 1；S/H reset 值和完整读写值留在 trace 中，但不对未限定 reset 的 S/H 状态或各 CSR 的 WARL/RO-zero 位预设全值。Veryl 的通过状态与架构观察分开记录；当前 runner 用 `$assert` 检查总数、cause、操作 ID 和定义 SE0 位，运行因预期 gate 观察缺失而 exit 1，功能结果为 `run-fail`。

## 层级覆盖与证据状态

`supported` / `absent` / `unresolved` 在下表仅描述已检查静态路径；不等同于 CPU 运行通过。

| 访问层 | Kunminghu | Heliodor | 运行状态/证据边界 |
|---|---|---|---|
| M 对八个 CSR 的读写 | `supported` 静态：CSR 定义/map/read/write 可见；门控不阻止 M。 | `absent`：M 写全 1 后八 CSR 读回全零；主路径默认写忽略。 | Heliodor reset 初值和写读回已实际观察；Kunminghu 无 CPU 运行。 |
| HS/S 对八个 CSR，`SE0/SE=0` 与 `1` | `supported` 静态：M `SE0/SE` 对低层访问生成 illegal permit。 | `absent`：M 控制清零时 16 次 CSR read/write 没有 trap；开启后访问也没有 stateen CSR 读回。 | Heliodor 另有 `henvcfg/senvcfg` 各 2 次 blocked CSR 操作；实际只有 cause 9 的 HS ecall，未见 stateen gate。Kunminghu 无 CPU 观察。 |
| VS 对 `sstateen0–3`，`hstateen.SE0/SE=0` 与 `1` | `supported` 静态：H 对应位 gate 生成 virtual-level permit。 | `unresolved`：CSR alias path 与 trap virtualization 未运行；不能从 VS CSR 通用默认行为推断完整 guest 处理。 | 未能启动 guest-mode fixture；实际 illegal/virtual-instruction cause 未测。 |
| U/VU 对 `sstateen` 控制的扩展 state | `unresolved`：`sstateen0.C` 自定义 state gate 有静态路径，其余标准字段所控扩展状态不在本案例范围。 | `unresolved`：没有 stateen CSR storage，且本轮未运行 U/VU protected-state 指令。 | 没有扩展状态访问 fixture，不从 U/VU CSR 读零推断结果。 |
| `ENVCFG=0/1` | `supported` 静态：M/H 控制分别 gate `henvcfg/senvcfg` 与 VS `senvcfg`。 | `absent` static gate: CSR addresses exist but checked permission path has no stateen ENVCFG control. | Heliodor 的 `henvcfg/senvcfg` 写读回都是全 1；关闭阶段没有额外 trap。VS `hstateen0.ENVCFG` 未运行。 |

## 证据表

<a id="evidence-table"></a>

| ID | 类型 | 状态 | 固定来源/位置 | 支持的结论与限制 |
|---|---|---|---|---|
| E1 | spec | inspected | RVA23 Profile v1.0 §3.1.2.2/Sha/Ssstateen；Smstateen/Ssstateen v1.0 §§3.1.1–3.1.3 | profile 要求八 CSR；定义分层控制、WARL/RO-zero、M reset 与软件初始化责任。 |
| E2 | source | inspected | Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；[wrapper CSR](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/wrapper/CSR.scala#L22)、[NewCSR map](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/SupervisorLevel.scala#L164)、[H CSR map](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/HypervisorLevel.scala#L170) | NewCSR 是 wrapper 活动实现；八 CSR 的 CSR map/读路径及 M/H 掩码可见。配置构建未成功、没有运行观察。 |
| E3 | source | inspected | Kunminghu [state fields](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/StateEnBundle.scala#L8)、[M fields](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/MachineLevel.scala#L411)、[CSR module reset](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRModule.scala#L24) | 位映射、显式 reset、RO-zero 字段与 H1–3 读掩码；无本轮逐字段写读回。 |
| E4 | source | inspected | Kunminghu [M/HS/S stateen permit](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRPermitModule.scala#L238)、[VS/VU gate](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/CSRPermitModule.scala#L455)、[exception output](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/NewCSR.scala#L1106) | SE0/SE 与 ENVCFG 的静态权限逻辑及 II/VI 分类；实际 cause 尚未观察。 |
| E5 | source | inspected | Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；[CSR read/default](../../sources/heliodor/src/core/csr.veryl#L508)、[CSR write/default](../../sources/heliodor/src/core/csr.veryl#L1144)、[generic CSR permission](../../sources/heliodor/src/core/alu_wrap.veryl#L446)、[ROB illegal flag](../../sources/heliodor/src/core/rob.veryl#L1339) | 检查路径无 stateen CSR 状态，默认读零/写忽略，checker 无 stateen gates；支持“该路径未提供”的静态判断，不代表运行结果或所有外部集成。 |
| E6 | test-inspected | inspected | Heliodor `test/act/config/heliodor/sail.json:746-752`；`tb/test_arch_common.veryl` target 列表 | ACT4 标 unsupported；仅作配置背景，既不证明 RTL 缺失，也不作为覆盖判定单独依据；没有现存 Ssstateen test target。 |
| E7 | experiment-build | run-pass | `experiments/ssstateen/ssstateen_probe.S`, `.ld`, `Makefile`, `.hex`, `.dis` | GCC 15.1.0 汇编、链接、bin-to-hex 和反汇编检查通过，输入覆盖 M 与 HS 两态、八 CSR、ENVCFG target；这是 fixture build，不是 CPU run。 |
| E8 | build/check-attempt | blocked | Kunminghu `make emu CONFIG=KunminghuV2Config NUM_CORES=1`; Heliodor 原仓库与隔离 Veryl targets | Kunminghu 缺 `mill`，仿真未启动。Heliodor 原仓库无专题 test target，原 shared testbench check 被 `$readmemh` 阻断；隔离副本的 build/check 阶段通过并启动仿真。 |
| E9 | test-run | run-fail | Heliodor 隔离 Veryl target，M/HS fixture；Veryl 0.22.0；日志 `/tmp/ssstateen-story-5-6-review-final.log`；隔离目录 `/tmp/heliodor-ssstateen-isolated-l_jpp8h2` | GCC rebuild 后 Veryl 编译/仿真启动，exit 1，`0 passed / 1 failed`；断言 expected 20 gate traps + ecall 失败。trace 记录全 192 项；trap count=1，唯一 cause=9，唯一 operation ID=21，IDs 1–20 未出现；stateen 读回为 0，tohost `0x02` 对比预期 `0x2B`。该动态失败范围仅为 M/HS fixture；VS/VU 和未指定 WARL 位仍未验证。 |

## 自检

1. **`sstateen0–3` 与 `hstateen0–3` 的标准要求是否包含 M CSR？** 不包含。RVA23 的 `Ssstateen` profile 行要求 S/H 两组八 CSR；`mstateen0–3` 属于配套 `Smstateen` 功能。本单元检查 M CSR 是为了验证 SE0/ENVCFG 的上层控制链，不把 M 行扩成 profile 要求。
2. **`sstateen0` 读 0 能证明不支持吗？** 不能。零可能来自 RO-zero WARL、上层 mask、reset 状态或未实现路径。Heliodor 的有限缺失判断结合了固定 CSR 路径无状态、写全 1 后读零、清零控制期间未观察到预期陷阱；不只依赖一次读零。
3. **为什么不把 `not-present` 当成整体不符合认证？** 目录状态标记的是这条要求在固定实现路径的证据判断；Heliodor CSR 状态路径和隔离运行都缺少预期行为，但没有覆盖其他可能集成方式、VS/VU H-gate、完整 profile 语义，更不等价于完整 RVA23 认证结论。

## 未决项

- Kunminghu 的八 CSR 初值、写读回、WARL/RO-zero、M/HS/S/VS/VU trap cause 和 `SE0/ENVCFG` 开关实际行为未运行。
- Heliodor 隔离 M/HS 运行报告状态读写与 gate 行为不符预期；VS/VU `hstateen` 控制及特权下受控扩展 state 未覆盖。
- Heliodor 原仓库共享 testbench 仍在 check 阶段因 `$readmemh`/`dram` 初始化退出；本轮使用隔离副本上的局部 lint 注解来执行普通 arch harness，没有修改上游或锁定快照。
