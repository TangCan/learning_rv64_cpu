---
unit_id: "rva23s64-ssstateen"
stage_id: "Epic 5 / Story 5.6"
scope: "RVA23S64/v1.0/§3.1.2.2/Ssstateen；对照固定 Kunminghu V2 与 Heliodor 快照中的 sstateen0–3、hstateen0–3、SE0/ENVCFG 分层访问和 CSR 异常路径。"
exclusions:
  - "不宣称 RVA23S64 符合性或认证。"
  - "不把 Heliodor ACT 配置、搜索缺项或一次读零单独作为实现缺失证据；结论限于本次检查的 CSR RTL 路径。"
  - "Kunminghu M/HS、S、VS 的适用 gate 路径和 M/H/S 全 1 WARL 掩码已有动态观察；VU FCSR 可用性已观测，未发现可用于隔离 VU stateen gate 的已实现 user-custom CSR。"
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

**结论按证据范围限定：** Kunminghu 的 M/HS 主矩阵最新差分运行 `kunminghu-fixture-20261014T155020Z-3e81181d1d02` 已通过 GOODTRAP 自检并以 `run-pass` 结束；全 1 写后的 M/H/S stateen 字段掩码及 21 个实现可写字段（含 `sstateen0.C`）均有精确读回自检。之前的 `kunminghu-fixture-20261014T123122Z-069b00f3c8db` 失败源于 fixture 未配置 PMP，M trap 返回 HS 代码时触发取指访问故障，并非 stateen gate 行为差异。独立 fixture 进一步观察到 S 对四个 `sstateen` 槽位的读写、M.SE0–3 各自清零时相应 CSR 访问 cause 2，以及恢复后读回；VS 对四个 `sstateen` 槽位在 H.SE 开启时的读写也均提交，VS 对 H.SE0 清零及 H.SE1–3 清零分别观察到 cause 22，恢复后完成写读回；另对 H.ENVCFG 清零访问 VS `senvcfg` 观察到 cause 22，恢复后读回 `0xf0`。VU fixture 动态读到 MISA.F=1，M/H/S 的 FCSR stateen 字段为 0，VU `fflags` 访问提交。VU 结果证明进入 VU 并观察到可用 FCSR，不构成 gate-clear/set 对照，因为这些 FCSR 字段在该实现中为 RO-zero。Kunminghu M/S/VS 适用门控路径和八 CSR 全 1 WARL/RO-zero 读回已运行；FCSR gate 在 `misa.F=1` 时按规范 RO-zero，不适用作 gate 测试。自定义 VU CSR 探针因 `0x800` 未实现且 CSR 权限逻辑优先 illegal-instruction，保留为 unverified。规范未定义的 S/H reset 位只记录观察。Heliodor `csr.veryl` CSR read/write 主路径未保存 stateen 状态；相关地址落入默认读零/写忽略分支，通用权限检查也没有 SE0/ENVCFG 条件。隔离的 Heliodor CPU 用例实际观察到写入无读回、预期阻止阶段没有 stateen trap，支持这条固定 CSR 路径的静态缺失判断，故覆盖表记 `not-present`。该结果不扩大成其他项目集成或完整 RVA23 合规性结论。ACT `sail.json` 中 `Ssstateen.supported=false` 仅作附加配置线索，不作为该判定依据。

## 规范契约与字段清单

`Ssstateen` 本身包括 `sstateen*` 与 `hstateen*`；`mstateen*` 是 `Smstateen`，不是本 profile 行的直接 CSR 要求，但 M-level 对相同位的控制决定低层访问和只读掩码。

| CSR | RV64 地址 | 规范/实现字段 | 规范约束与本轮观察状态 |
|---|---:|---|---|
| `sstateen0` | `0x10C` | bit 2 `JVT`、bit 1 `FCSR`、bit 0 `C` | JVT/FCSR 按扩展支持情况只读零；C 为 WARL。Kunminghu reset `0`、全 1 写后读回 `1`，one-hot C 写后读回 `1`（run `155020Z`）；M.SE0 clear 时 HS 访问 cause 2，恢复后读写完成。Heliodor 主路径默认读零/写忽略；S clear/set 与 VS clear/set 尝试均未观察到 gate trap，H.SE/ M.SE 写 1 仍读回 0；VU direct CSR cause 2 是特权检查，不是 stateen gate。 |
| `sstateen1` | `0x10D` | bit 31:0 保留 | Kunminghu all-ones readback `0`，全 RO-zero；M.SE1 clear gate cause 2，opened access完成。Heliodor CSR 主路径默认读零/写忽略。 |
| `sstateen2` | `0x10E` | bit 31:0 保留 | 同 `sstateen1`，对应 M.SE2。 |
| `sstateen3` | `0x10F` | bit 31:0 保留 | 同 `sstateen1`，对应 M.SE3。 |
| `hstateen0` | `0x60C` | bit 63 `SE0`、62 `ENVCFG`、60 `CSRIND`、59 `AIA`、58 `IMSIC`、57 `CONTEXT`、56 `P1P13`，低位继承 `JVT/FCSR/C` | `P1P13`、未实现功能位及保留位按实现约束 RO-zero；Kunminghu all-ones readback `0xde00000000000001`，六个实现控制字段及 C 分别 one-hot 写读回匹配（run `155020Z`）；SE0/ENVCFG gate 动态证据见下文。Heliodor 主路径读回 0、写忽略；H.SE0 写 1 仍读回 0，故 gate-open 未观察到。 |
| `hstateen1` | `0x60D` | bit 63 `SE`；其余位保留 | `SE` 控制对应 slot 的 `sstateen` CSR 访问；Kunminghu one-hot 和 all-ones readback 均为 bit 63，reset 仅记录。Heliodor 主路径默认读零/写忽略，set 尝试读回 0。 |
| `hstateen2` | `0x60E` | bit 63 `SE`；其余位保留 | 同 `hstateen1`，对应 VS/S slot 2。 |
| `hstateen3` | `0x60F` | bit 63 `SE`；其余位保留 | 同 `hstateen1`，对应 VS/S slot 3。 |

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
| Heliodor 隔离 controlled input | `python3 experiments/ssstateen/run_isolated.py`; 隔离 copy 内执行 Veryl target | build/check 成功，CPU 仿真完成。tohost=`0x02`；trap count 1、唯一 cause 9，唯一操作 ID 21（HS ecall），hstateen0.SE0=0；预期为 20 个 gate trap（cause 2，操作 ID 1–20）+ ecall（cause 9、ID21）且 SE0=1，故 marker 应为 `0x2B`，实际 `0x02`，行为结果 run-fail。测试逐项断言 cause 与操作 ID 顺序，并检查 hstateen0–3 的定义 SE 位；sstateen0 JVT/FCSR 与 sstateen1–3 的 RO-zero 字段也有断言。Story 6.8 复核时纠正了旧 harness 曾把 bit63 错当成全部八 CSR 的 SE 位这一断言错误。未知/WARL 保留位只输出 trace，不假定完整寄存器全值。当前运行以总 trap count 断言先失败，原始完整日志为 `/tmp/ssstateen-story-5-6-review-final.log`。该 Story 5.6 运行本身只测 M/HS，VS/VU 后续证据见 E13–E15。 |

`run_isolated.py` 将固定 Heliodor `src/` 复制到 `tempfile.mkdtemp(prefix="heliodor-ssstateen-isolated-")` 创建的唯一临时路径（本轮：`/tmp/heliodor-ssstateen-isolated-l_jpp8h2`），沿用公共 1 MiB arch harness 的 CPU、memory bus 与输入，不触碰 `sources/`；只省略未实例化、会触发 check 错误的 debug harness，并在私有副本的 DRAM declaration 上加 `#[allow(initial_assign)]`，使 Veryl 0.22.0 能执行原有 `$readmemh`。隔离 target 输出报告区：`trace[0..7]` 是八 CSR 初值，`trace[8..11]` 是 M stateen 控制写零后的读回，`trace[12..19]` 是 M 对八 CSR 写全 1 后的读回，`trace[24..31]` 是 HS 开启后的写读回，`trace[32..33]` 是 `henvcfg/senvcfg` 写读回，`trace[34]` 是 trap count，`trace[35..98]` 是按序 `mcause`，`trace[100..163]` 是每次 trap 前设置的操作 ID；每个 ID 对应一个被门控 CSR 读/写或最后的 ecall。报告缓冲区容量 1536 字节，最多保存 64 个 cause/ID 条目；溢出保护只跳过超量记录、仍更新总计数。

实际观察：`trace[0..31]` 全 0；`trace[32]=trace[33]=0xffff_ffff_ffff_ffff`；`trace[34]=1`，`trace[35]=9`，`trace[100]=21`，其余 cause/operation-ID 槽为 0。即 M 对 stateen CSR 写全 1 后读回零；M 控制清零阶段的 20 次 HS CSR 读/写都没有触发 stateen trap；只有 HS `ecall` 触发 cause 9/operation ID 21；hstateen0.SE0 写全 1 后仍读 0。程序将 `(trap_count << 1) | hstateen0.SE0` 写入 tohost，实际 `0x02`；按规范预期的输入控制应产生 20 个 CSR trap + 1 个 ecall，且 SE0=1，即 `0x2B`。改进后的测试逐条要求 operation ID 1–20 对应 cause 2、ID21 对应 cause 9；当前只看到 ID21/cause9。M/HS 对 hstateen0–3 写入后的定义 SE0/SE bit63 分别断言为 1；sstateen CSR 不存在 bit63 SE 字段。S/H reset 值和完整读写值留在 trace 中，但不对未限定 reset 的 S/H 状态或 WARL 位预设全值。Veryl 的通过状态与架构观察分开记录；当前 runner 用 `$assert` 检查总数、cause、操作 ID 和定义 SE0 位，运行因预期 gate 观察缺失而 exit 1，功能结果为 `run-fail`。

## 层级覆盖与证据状态

`supported` / `absent` / `unresolved` 在下表仅描述已检查静态路径；不等同于 CPU 运行通过。

| 访问层 | Kunminghu | Heliodor | 运行状态/证据边界 |
|---|---|---|---|
| M 对八个 CSR 的读写 | `supported` 静态：CSR 定义/map/read/write 可见；门控不阻止 M。 | `absent`：M 写全 1 后八 CSR 读回全零；主路径默认写忽略。 | Heliodor reset 初值和写读回已实际观察；Kunminghu run `123122Z` 观察到 M reset 与全 1 写回；差分随后在后续 gate 操作中止。 |
| HS/S 对八个 CSR，`SE0/SE=0` 与 `1` | `supported` 静态：M `SE0/SE` 对低层访问生成 illegal permit。 | `absent`：M 控制清零时 16 次 CSR read/write 没有 trap；开启后访问也没有 stateen CSR 读回。 | Heliodor E12 逐槽读回确认 M.SE0–3 清零为 0、写 SE=1 后仍为 0；S 对 `sstateen0–3` 的 clear 状态读取均完成、无 cause 2、读回 0。设置阶段没有有效 gate-open 状态；HS E9 的 gate 尝试也未出现 cause 2。Kunminghu run `132002Z` 观察到 S 对四个 sstateen CSR 逐槽 M.SE clear cause 2、恢复后读回；HS/H CSR 全矩阵仍未完成。 |
| VS 对 `sstateen0–3`，`hstateen.SE0/SE=0` 与 `1` | `supported` 静态：H 对应位 gate 生成 virtual-level permit。 | `partial`: run `132255Z` 对 slot 0–3 均观察到 H.SE clear 时 VS read 引发 cause 22、handler 恢复 gate 后 write/readback 和 ecall cause 10；slot 1–3 的 `hstateen.SE` 先读回 `0x8000000000000000`。字段 WARL/reset 仍未逐项验证。 | `partial`: E13/E14 已进入 VS；clear 与尝试打开 H.SE 后，四个 `sstateen` 读取均完成且没有 cause 22。H.SE 写入仍读回 0，因此 gate-open 尚不能验证。 |
| U/VU 对 `sstateen` 控制的扩展 state | `partial`: run `130304Z` 进入 VU；MISA=`0x80000000003411af`（F=1），M/H/S FCSR 字段读 0，VU `fflags` 读提交。FCSR 字段为 RO-zero，不能形成 gate-open 对照；此记录不算 gate 通过。 | `unresolved`: 未运行 U/VU 受控扩展状态 gate 对照；固定 CSR 路径缺少 stateen storage。 | E15 进入 Heliodor VU；对 `sstateen0–3` 的直接 CSR 访问按 supervisor 特权级产生 cause 2，终止 ecall cause 8 到达 HS。E16 在 FS=Initial 下读写 `fflags` 并读回 1，无 FCSR trap；但 H.FCSR 设 1 仍读回 0，所以不能作 gate clear/set 对照。VU 受控扩展 state 可用性已观察，gate 比较仍未形成。 |
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
| E9 | test-run | run-fail | Heliodor 隔离 Veryl target，M/HS fixture；Veryl 0.22.0；日志 `/tmp/ssstateen-story-5-6-review-final.log`；隔离目录 `/tmp/heliodor-ssstateen-isolated-l_jpp8h2` | GCC rebuild 后 Veryl 编译/仿真启动，exit 1，`0 passed / 1 failed`；断言 expected 20 gate traps + ecall 失败。trace 记录全 192 项；trap count=1，唯一 cause=9，唯一 operation ID=21，IDs 1–20 未出现；stateen 读回为 0，tohost `0x02` 对比预期 `0x2B`。该动态失败范围仅为 M/HS fixture；该 E9 运行本身只测 M/HS；后续 VS/VU 证据见 E13–E16，未指定 WARL 位仍未验证。 |
| E10 | test-run | run-fail | Heliodor 隔离 `test_arch_ssstateen`、独立 `ssstateen_probe_s_gates.S`；[完整输出](evidence/smoke/heliodor-ssstateen-s-gates-20261014/output.log)；[manifest 记录](evidence/cpu-validation-toolchain-v1.yaml) | CPU started，tohost `0x0a`，exit 1。fixture 请求 M 清 `M.SE0` 和设置 `M.SE0=1`，但未读回控制位，不能证明 set 阶段成立。S-mode operation 43 在 clear 阶段读取 `sstateen0` 未产生 cause-2 trap且读回 `0x0`；operation 44 也完成并读回 `0x0`。E11 补充控制位读回并限定 gate-open 阶段无效。 |
| E11 | test-run | run-fail | Heliodor `ssstateen_probe_s_gates_v2.S` with M.SE0 readback; [full log](evidence/smoke/heliodor-ssstateen-s-gates-readback-20261014/output.log); [manifest record](evidence/cpu-validation-toolchain-v1.yaml) | CPU started, `tohost=0x0a`, exit 1. M.SE0 clear readback is 0; S operation 43 completes with value 0 and no cause-2 trap. M then writes bit 63 to set SE0, but readback remains 0; operation 44 also completes with value 0, so this is not a valid gate-open test. Trap count=5; recorded traps are only ecall causes at IDs 21/22/23/24/42. The fixture reaches both labeled S reads; only the clear state is verified. |
| E12 | test-run | run-fail | Heliodor all-slot fixture `ssstateen_probe_s_gates_v3.S`; [full log](evidence/smoke/heliodor-ssstateen-s-gates-all-slots-20261014/output.log); [manifest record](evidence/cpu-validation-toolchain-v1.yaml) | CPU started, `tohost=0x0a`, exit 1. M.SE0–3 clear readbacks are all 0; S operations 43–46 read `sstateen0–3`, all complete with value 0 and no cause-2 trap. Attempts to set each M.SE bit read back 0; S operations 47–50 also complete with value 0, so no gate-open state was reached. Trap count 5 contains only ecall causes 9 at IDs 21/22/23/24/42. Per-operation expectations and observations are individually recorded; E12 supersedes E11 for S-slot coverage. |
| E13 | test-run | run-fail | Heliodor VS fixture `ssstateen_probe_vs.S`; [log](evidence/smoke/heliodor-ssstateen-vs-20261014/output.log); [manifest](evidence/cpu-validation-toolchain-v1.yaml) | VS guest entry is confirmed by completion markers and terminal ecall. With H.SE clear, all four VS sstateen reads complete as zero without expected cause 22. CPU-started `run-fail`; this does not establish gate-open behavior. |
| E14 | test-run | run-fail | Heliodor VS fixture `ssstateen_probe_vs_v2.S`; [log](evidence/smoke/heliodor-ssstateen-vs-set-20261014/output.log); [manifest](evidence/cpu-validation-toolchain-v1.yaml) | Attempts to set H.SE=1 for all hstateen0–3 read back zero. A second VS read phase completes without cause 22, so no valid gate-open state was achieved. CPU-started `run-fail`; VU privilege-path evidence is recorded separately in E15; WARL/reset fields remain unverified. |
| E15 | test-run | run-pass | Heliodor VU fixture `ssstateen_probe_vu.S`; [log](evidence/smoke/heliodor-ssstateen-vu-20261014/output.log); [manifest](evidence/cpu-validation-toolchain-v1.yaml) | VU reaches its terminal ecall; direct reads of supervisor-privilege `sstateen0–3` each trap with cause 2 and resume through HS; VU ecall reaches HS with cause 8. This verifies privilege classification and trap return only, not an H.SE gate or a VU controlled-extension path. |
| E16 | test-run | run-pass | Heliodor VU FCSR fixture `ssstateen_probe_vu_fcsr.S`; [log](evidence/smoke/heliodor-ssstateen-vu-fcsr-20261014/output.log); [manifest](evidence/cpu-validation-toolchain-v1.yaml) | With FS=Initial, VU reads `fflags` as 0, writes 1 and reads back 1 without a trap; terminal ecall cause 8 reaches HS. H.FCSR set attempt reads back 0, so this confirms controlled state availability but not a clear/set gate comparison. |

## 自检

1. **`sstateen0–3` 与 `hstateen0–3` 的标准要求是否包含 M CSR？** 不包含。RVA23 的 `Ssstateen` profile 行要求 S/H 两组八 CSR；`mstateen0–3` 属于配套 `Smstateen` 功能。本单元检查 M CSR 是为了验证 SE0/ENVCFG 的上层控制链，不把 M 行扩成 profile 要求。
2. **`sstateen0` 读 0 能证明不支持吗？** 不能。零可能来自 RO-zero WARL、上层 mask、reset 状态或未实现路径。Heliodor 的有限缺失判断结合了固定 CSR 路径无状态、写全 1 后读零、清零控制期间未观察到预期陷阱；不只依赖一次读零。E13/E14 的 VS 观察进一步表明 clear 状态访问没有预期 cause 22，但 H.SE 写 1 未生效，因此仍没有 gate-open 对照。
3. **为什么不把 `not-present` 当成整体不符合认证？** 目录状态标记的是这条要求在固定实现路径的证据判断；Heliodor CSR 状态路径和隔离运行都缺少预期行为。E13/E14 只观察到 VS clear 与 set-attempt，E15 只观察 VU privilege faults；完整 VS/VU H-gate、受控扩展状态和 profile 语义仍不完整，更不等价于完整 RVA23 认证结论。

## 未决项

- Kunminghu 已运行 M 八 CSR reset/readback、精确 M/H/S 全 1 WARL/RO-zero 掩码自检、S `sstateen0–3` 与 M.SE0–3 clear/set、VS H.SE0–3 clear/set、H.ENVCFG clear/set 与 VU FCSR 可用性；VU 的 FCSR stateen bit 在 `misa.F=1` 时规范要求 RO-zero；测试自定义 VU CSR 的实验因 `0x800` 未实现且 CSR 权限逻辑优先选 illegal-instruction，已归档为 unverified，不作为 gate 失败或通过。S/H 未定义 reset 值仅记录观察。
- Heliodor 隔离 M/HS/S/VS/VU fixtures 已运行；VS H.SE set 尝试读回仍为 0，VU direct `sstateen` CSR 访问 cause 2，VU `fflags` 在 FS=Initial 下可写读回 1。VS gate-open、VU FCSR gate 对照、HS gate 矩阵及逐字段 WARL/reset 仍未验证。
- Heliodor 原仓库共享 testbench 仍在 check 阶段因 `$readmemh`/`dram` 初始化退出；本轮使用隔离副本上的局部 lint 注解来执行普通 arch harness，没有修改上游或锁定快照。扩展 fixture 归档在 `evidence/smoke/heliodor-ssstateen-s-rerun-20261014/`。

## Story 6.8 固定快照运行矩阵 2026-10-14

本节只记录本次 Epic 6 CPU 运行。两边均使用 `sources.lock` 固定 SHA；Heliodor fixture SHA 与 Story 5.6 耐久记录一致（`65391f26edfcd03fe56182e53b393e99b8a2500c49e8599f97fbaed49104c789`）。运行输入、工具版本、命令、CPU-start、退出码、日志及构建产物归档在 [CPU 验证 manifest](evidence/cpu-validation-toolchain-v1.yaml)；可复查新运行的 Heliodor 归档在 `evidence/smoke/heliodor-ssstateen-rerun-20261014/`，Kunminghu 归档在 `evidence/smoke/kunminghu-ssstateen-20261014/`。

### 逐 CSR 与模式状态

`reset` 指启动时在 M 读取 S/H CSR；规范未定义或本实现未声明的 reset 值只记录观察，不作为预期常量。`write/readback` 的全 1 探针记录八个 CSR 的实际实现掩码；GOODTRAP 自检验证 M/H/S 定义字段和 RO-zero 位，不固定未定义位。

| CSR | Kunminghu M | Kunminghu HS/S | Kunminghu VS/VU | Heliodor M | Heliodor HS | Heliodor S/VS/VU |
|---|---|---|---|---|---|---|
| `sstateen0` | reset 观察 0；all-ones readback `1`; gates-clear M read `0` | M.SE0 清除时 S 访问 cause 2；恢复后 S read/write/readback；HS 访问 gate 见主矩阵 | H.SE0 清除 cause 22；恢复后 C 读回 1。VU FCSR 受 FS 控制，FCSR stateen 位 RO-zero | reset 0；写 1 读 0 | M.SE0 clear 时访问无 cause 2；gate-set 写读 0 | S access 无 cause 2；VS access 无 cause 22；H.SE set attempt 读 0 |
| `sstateen1` | reset 观察 0；all-ones readback `0` (RO-zero) | M.SE1 clear 时 S access cause 2；恢复后读写序列完成 | H.SE1 clear cause 22；恢复后访问完成，读回 0；VU direct CSR cause 2 是 CSR 特权异常 | reset 0；写 1 读 0 | M.SE clear access 无 cause 2；gate-set 读 0 | S/VS accesses 完成且无预期 gate trap；VU direct CSR cause 2 是特权异常 |
| `sstateen2` | reset 观察 0；all-ones readback `0` (RO-zero) | M.SE2 clear 时 S access cause 2；恢复后读写序列完成 | H.SE2 clear cause 22；恢复后访问完成，读回 0；VU direct CSR cause 2 是 CSR 特权异常 | reset 0；写 1 读 0 | M.SE clear access 无 cause 2；gate-set 读 0 | S/VS accesses 完成且无预期 gate trap；VU direct CSR cause 2 是特权异常 |
| `sstateen3` | reset 观察 0；all-ones readback `0` (RO-zero) | M.SE3 clear 时 S access cause 2；恢复后读写序列完成 | H.SE3 clear cause 22；恢复后访问完成，读回 0；VU direct CSR cause 2 是 CSR 特权异常 | reset 0；写 1 读 0 | M.SE clear access 无 cause 2；gate-set 读 0 | S/VS accesses 完成且无预期 gate trap；VU direct CSR cause 2 是特权异常 |
| `hstateen0` | reset 观察 0；all-ones readback `0xde00000000000001`; M mask 自检 | M.SE0 clear causes 2 for HS read/write; enabled HS can access and read back | H.SE0 clear blocks VS sstateen0; H.ENVCFG clear blocks VS `senvcfg` (cause 22) | reset 0；write 1 read 0 | M.SE0 clear access no cause 2; write 1 read 0 | H.SE attempts read 0; VS accesses no cause 22 |
| `hstateen1` | reset 观察 0；all-ones readback `0x8000000000000000`; exact SE mask checked | M.SE1 clear causes 2 for HS access; enabled HS read/write recorded | H.SE1 clear causes 22 on VS sstateen1; restore lets access continue | reset 0；write 1 read 0 | M.SE clear access no cause 2; write 1 read 0 | 不适用：VS/VU 不直接访问 hstateen；E14 HS set attempt read 0 |
| `hstateen2` | reset 观察 0；all-ones readback `0x8000000000000000`; exact SE mask checked | M.SE2 clear causes 2 for HS access; enabled HS read/write recorded | H.SE2 clear causes 22 on VS sstateen2; restore lets access continue | reset 0；write 1 read 0 | M.SE clear access no cause 2; write 1 read 0 | 不适用：VS/VU 不直接访问 hstateen；E14 HS set attempt read 0 |
| `hstateen3` | reset 观察 0；all-ones readback `0x8000000000000000`; exact SE mask checked | M.SE3 clear causes 2 for HS access; enabled HS read/write recorded | H.SE3 clear causes 22 on VS sstateen3; restore lets access continue | reset 0；write 1 read 0 | M.SE clear access no cause 2; write 1 read 0 | 不适用：VS/VU 不直接访问 hstateen；E14 HS set attempt read 0 |

Kunminghu 官方 runner 最新差分记录为 `kunminghu-fixture-20261014T155020Z-3e81181d1d02`，CPU 已启动并以 `run-pass` 结束；GOODTRAP 检查 M reset-zero、全 1 WARL/RO-zero 掩码、21 个实现可写 stateen 字段的 one-hot 读回、20 个 cause-2 trap 的 ID 顺序及 cause-9 ecall。147 条 operation records 中 CSR 读值直接来自 native trace；操作 ID 1–21 若 native trace 缺事件则标记为 fixture trap-log 自检断言。one-hot 写操作的写值依赖源代码编码，native trace 未保留源寄存器值时明确标成 unavailable，不使用过期寄存器重建值。更早的 `123122Z` 因未配置 PMP 导致 MRET 取指故障，`154604Z` 因 H.SE0 在 M.SE0 清零时被遮蔽而触发 BADTRAP；两者分别保留为已修复的旧 fixture 尝试。

Heliodor 的 durable run record 除了 fixture trap trace 内嵌的 IDs 1–21，还按源操作顺序为其余 64 个 CSR/control 操作分配唯一归档 ID（1000+）；每条记录保留 mode、CSR、操作、规范约束及 trace observation。源程序本身只把 gate phase 的 IDs 1–21 写入硬件 trap trace，归档 ID 1000+ 是根据 fixture 指令序列与 trace slot 做的后处理标识，并非 CPU 内部 trace。HS gate-clear 的 `henvcfg` write/read IDs 17/18、`senvcfg` write/read IDs 19/20 预期 cause 2，实际未 trap。操作 ID 21 是 HS `ecall`，唯一实际 trap 为 cause 9。HS gate-set 阶段两个 ENVCFG CSR 读回全 1。trace 中 reset 值是 `trace[0..7]`，M 全 1 写回是 `[12..19]`，HS 开启后的写回是 `[24..31]`，ENVCFG 为 `[32..33]`，trap count/cause/ID 是 `[34]`、`[35..]`、`[100..]`。该 fixture 对未 trap 的 HS 读操作没有单独保存读值；它只证明操作未触发 trap，不能据此填入读回值。

### 两侧运行判定与未覆盖范围

- **Heliodor**：隔离 harness 已启动 CPU；M/HS fixture 对 ID 1–20 的 gate 操作没有产生预期 cause-2 traps。E12 独立 S fixture 逐槽确认 M.SE0–3 清除读回为 0，但设置 SE=1 后仍读回 0；S operations 43–46 在 clear 状态完成读取，均读回 0 且无 cause 2。E13/E14 确认可进入 VS，八次 VS sstateen 读取均完成、没有 cause 22；四个 H.SE 设置尝试仍读回 0，故 gate-open 未验证。E15 已确认 VU guest、cause-2 CSR 特权异常与 cause-8 ecall 路径；VU FCSR 已证实可用，但 H.FCSR 写 1 仍读回 0，gate clear/set 对照无法达成。整体执行仍含 CPU-started `run-fail` 案例。
- **Kunminghu**：CPU first instruction commit 已出现；官方 M/HS 主矩阵记录 `155020Z` 为 `run-pass`，NEMU 差分和 GOODTRAP 自检均完成。夹具显式配置 PMP NAPOT RWX，确保 trap 返回路径可取指；旧的 `123122Z` PMP 配置缺失失败记录保留作历史。主矩阵的 trap 自检检查 20 个 HS gate cause 2 与顺序 ID、最终 cause-9 ecall，以及 21 个可写 stateen 字段的 one-hot 读回；manifest 区分原生 trace、fixture 断言和 unavailable 写源。后续 runner `125026Z` 观察到 HS/VS positive path；`132255Z` 对 VS slot 0–3 均观察到 H.SE clear 时 cause 22、恢复后 all-ones write/readback，并以 cause 10 收尾；slot 1–3 的 H.SE 初始读回均为 `0x8000000000000000`。S runner `132002Z` 对 sstateen0–3 记录 S-mode 读写和 M.SE0–3 各自 clear/set：各自关闭时访问 cause 2，恢复后读回并以 cause 9 ecall 收尾。VU runner `130304Z` 观察到 MISA.F=1、M/H/S FCSR 字段读 0、VU `fflags` 读提交与 ecall cause 8。首次 VU 尝试 `130220Z` 因 M.SE0 未先打开而在 HS CSR read cause 2 后双陷阱，保留为失败 attempt。no-diff selfcheck 的 30,000 与 100,000 指令运行均无 terminal marker 或 commit trace，分别保持 `unverified`。VU FCSR stateen gate 在 `misa.F=1` 时规范规定为 RO-zero；user-custom CSR gate 探针 `153123Z` 因 CSR 未映射且 illegal-instruction 优先于 virtual-instruction 而保持 unverified。规范未定义的 S/H reset 位保持观察值而非断言。
- VS/VU fixture 只覆盖上述具体操作。VU FCSR bit 在锁定 Kunminghu 实现中为 RO-zero，Heliodor 的 H.FCSR 写 1 也读回 0；两侧可观察到 VU fflags 路径，但无法形成独立 FCSR gate clear/set 对照。未实现字段依规范保持 RO-zero；实现字段的 one-hot 与 all-ones 读回已按当前 Kunminghu 定义逐项检查。Heliodor 无 stateen CSR 存储映射，因此其 gate-open 和字段写入路径无法在该快照形成可执行对照。

本节结果不构成 RVA23S64 符合性或认证结论。Kunminghu 与 Heliodor 状态独立；Heliodor 的 `not-present` 仍限定于已经检查的 CSR 主路径。
