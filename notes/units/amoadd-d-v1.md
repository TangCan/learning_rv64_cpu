---
unit_id: "amoadd-d"
stage_id: "阶段 3"
scope: "在 M-mode Bare、自然 8 字节对齐、可缓存主存、无访问异常的场景，比较 RV64A `AMOADD.D` 的译码、原子读改写、旧值返回和退休路径；证据限于 sources.lock 固定的 Kunminghu V2 与 Heliodor 源码。"
exclusions:
  - "LR/SC、其他 AMO、`.W`、`aq`/`rl` 排序子案例及 RVA23 整体符合性。"
  - "未对齐地址、转换/权限拒绝及异常路径；只注明其为独立路径，不推断处理细节。"
  - "非缓存设备内存、具体多核交错、周期、竞争正确性及动态执行结果。"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual, A extension"
    edition: "v20260120"
    section: "§12.1 AMO instructions; Zaamo"
    profile_category: "not-profile-specific"
source_snapshots:
  - project: "Kunminghu V2"
    snapshot_id: "xiangshan-kunminghu-v2-20261012"
    repository: "https://github.com/OpenXiangShan/XiangShan.git"
    branch: "kunminghu-v2"
    commit: "c098f996bf4d301b88693b20315486d31e93bc9d"
  - project: "Heliodor"
    snapshot_id: "heliodor-master-20261012"
    repository: "https://github.com/dalance/heliodor.git"
    branch: "master"
    commit: "94e9c5821c24a8941c3ddc3b76daddc7124a855a"
---

## 单元自检

- **问题：** `AMOADD.D` 与普通 `LD` 后接 `SD` 在架构上有什么区别？旧值和新值分别流向哪里？本记录的实现路径和验证结论有哪些边界？
- **学习者答案：** `AMOADD.D rd, rs2, (rs1)` 对自然对齐的 64 位内存位置执行不可分割的读改写：先取得旧值 `old`，内存更新为 `(old + x[rs2]) mod 2^64`，而 `rd` 得到 `old`。普通 `LD` 和 `SD` 是两条独立架构操作，中间允许其他观察者介入；不能仅因软件把它们相邻发出就获得 AMO 的原子性。Kunminghu 的译码把该指令标为 MOU/AMO，序列化相关执行，并在 `AtomicsUnit` 准备 DCache AMO 请求；DCache 的 AMOALU 计算加法并通过 AMO 响应返回旧数据，AtomicsUnit 将结果作为 `FuType.mou` writeback 经 `MemBlock` 送入 OoO writeback 接口，ROB 再按通用完成/提交条件退休（E2–E8）。Heliodor 在 head 执行 AMO 读，ALU 用读到的旧值形成 CDB/ROB 结果，再在退休时发出本地缓存写；目录失效/行离开会 poison 并触发 replay（E9–E15）。这是对固定源码的静态追踪，不证明实现对所有竞争交错都正确。Heliodor 有 `amoadd_d` 测试入口，Kunminghu 的测试树未检出专用入口；Heliodor 测试虽尝试运行，但在测试启动前因编译错误退出，因此没有 pass 结论，动态行为未验证（E16–E18）。未对齐和访问拒绝仅作为排除边界，不推断其异常细节。
- **检查类型：** explanation + source-location
- **证据 ID：** E1–E18；测试命令尝试运行但测试未启动

## 架构行为与子案例

- **可观察行为：** 对 `AMOADD.D rd, rs2, (rs1)`，地址为 `x[rs1]`，该地址必须自然 8 字节对齐。对内存中的旧 64 位值 `old`，原子地写入 `old + x[rs2]`（模 `2^64`），并将 `old` 写入 `rd`。`rd=x0` 时丢弃寄存器结果，但内存更新语义不变。规范定义 AMO 相对普通 load/store 的原子读改写行为；内部执行与退休阶段由各实现决定。
- **规范依据：** [RISC-V Unprivileged ISA A extension §12.1、Zaamo，v20260120](https://docs.riscv.org/reference/isa/v20260120/unpriv/a-st-ext.html)。本记录只讨论 RV64 `AMOADD.D`，不作 RVA23 profile 完整性判断。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| RV64 `AMOADD.D`，自然 8 字节对齐，M-mode Bare、可缓存主存、无访问异常 | covered | 架构结果由 E1 支持；双边实现路径见 E2–E15。配置与结果均未运行观察。 |
| 旧值写入 `rd`，新值写入内存 | covered | 规范见 E1；Kunminghu 数据路径见 E5–E7；Heliodor 见 E11–E13。 |
| 未对齐地址 | excluded | 本例只取自然对齐地址；不描述实现或异常处理。 |
| 地址转换/权限拒绝 | excluded | 属于独立异常路径；本记录不推断其细节。 |
| `.W`、其他 AMO、LR/SC、`aq`/`rl`、设备内存 | excluded | 不从本例外推。 |
| 多核竞争下原子性、时序和完整 profile 符合性 | unconfirmed | 静态源码路径不构成竞争验证或整体符合性证据。 |

## Kunminghu 路径

- **阶段与状态变化：** `DecodeUnit` 将 `AMOADD_D` 解为两个寄存器源、整数目的寄存器写使能、MOU 功能单元和 `amoadd_d` 操作；解码同时识别 AMO 类型（E2）。Dispatch 侧以 ROB head AMO 未完成作为阻塞条件；`MemBlock` 拦截 AMO store issue，屏蔽普通 store 路径并送入 `AtomicsUnit`，等待原子单元完成后恢复普通状态（E3）。`AtomicsUnit` 收集 `rs2` 数据和 `rs1` 地址/目的寄存器身份，等待 TLB 响应、检查对齐及访问条件，并等待 store buffer 清空；本案例假设地址对齐、Bare 且权限通过，因此只描述请求路径（E4）。其 AMO 请求命令映射为 `M_XA_ADD`，携带地址、64 位操作数和 mask；DCache AMOALU 选择加法路径，计算旧 cache 数据加 `rs2`，而读响应数据被保存在 `resp_data` 并作为 AtomicsUnit 输出数据送往目的物理寄存器（E5–E7）。DCacheWrapper 将 atomic response 注册后返回 LSU。AtomicsUnit 的响应以 `FuType.mou` 和目的物理寄存器号输出，经 `MemBlock` 的 atomic writeback override 并入 `writebackLda` 到 OoO 后端；ROB 证据只展示通用完成及提交门控，不单独证明 AMO 的动态退休（E7–E8）。
- **源码位置：** 固定快照 `sources/xiangshan`：译码 `backend/decode/DecodeUnit.scala:249,946-954`；dispatch/head 阻塞 `backend/dispatch/NewDispatch.scala:814-820,890-898`；串行 AMO 路由 `mem/MemBlock.scala:1802-1835,1847`；地址、源数据、权限与结果选择 `mem/pipeline/AtomicsUnit.scala:84-97,137-178,238-313,357-399,474-495`；AMO 命令/数据字段 `mem/pipeline/AtomicsUnit.scala:491-537`；DCache 运算 `cache/dcache/mainpipe/AMOALU.scala:39-49,73-80`；response `cache/dcache/DCacheWrapper.scala:1467-1472`；ROB commit 条件 `backend/rob/Rob.scala:784-801`（通用 commit-valid 门控，不特指 AMO）。
- **相关验证：** Kunminghu `src/test` 搜索未定位专门的 `AMOADD.D` 测试入口；`src/test/scala/xiangshan/DecodeTest.scala:38-49` 是译码 smoke test，不能证明 AMO 行为。本单元未运行构建或仿真；Heliodor 既有测试命令已尝试两次，但 stable 与 nightly 均在测试执行前编译失败，Kunminghu 没有专门测试入口可运行（E16、E18）。

## Heliodor 路径

- **阶段与状态变化：** decoder 对 AMO 编码设置 `rs1` 地址源、`rs2` 数据源、目的寄存器写使能，并把普通 AMO 标为同时读/写内存、以 MEM 选择旧内存值写回（E9）。整数 IQ 将 AMO 标志和 funct5 保存到队列项，且只让 AMO 在 ROB head 发射，形成源码中的串行化约束（E10）。ALU wrapper 从 `i_load_data` 选出旧 dword；`AMOADD` funct5 `00000` 对旧值与 `rs2` 做 64 位加法形成待写新值，`amo_wb` 仍选旧值供 CDB，CDB 同时携带目的寄存器、ROB index、地址和新 store data（E11）。源码注释和信号路径表明 AMO 读取得当前缓存行所有权，并在 head 退休时走本地缓存写；AMO read issue 时记录 PA 与 ROB index；同周期匹配 invalidate/eviction，或 watch 窗口内匹配 invalidate、缓存行缺席会置 poison。被 watch 的 AMO 到 ROB head 且 poison 时，`commit_amo_replay` 抑制 `rob_commit_ack` 并触发 redirect/replay（E12–E13）。ROB 仅允许有效 head 且结果已写回时提交；core 的 commit ack 还受 replay 与存储条件门控，ack 后更新 architectural RAT（E14–E15）。以上是固定源码所示控制和数据路径，不推导跨核竞争正确性。
- **源码位置：** 固定快照 `sources/heliodor`：AMO decode `src/core/decoder.veryl:606-628`；源/目的操作数标记 `src/core/decode.veryl:190-211,257-260`；head 发射与 AMO 元数据 `src/core/iq_int.veryl:420-430,940-948`；旧值/新值分流、CDB `src/core/alu_wrap.veryl:266-287,312-363,358-363,400-438`；ALU 输入与旧 load data `src/core/heliodor_core.veryl:3023-3057`；AMO poison/replay `src/core/heliodor_core.veryl:4004-4007,4062-4072,5796-5811,5870-5889`；退休写路径 `src/core/heliodor_core.veryl:4062-4072,7489-7525,7553-7556`；ROB head 完成/ack `src/core/rob.veryl:560-578,1520-1534`；架构映射提交 `src/core/heliodor_core.veryl:4416-4420`。
- **相关验证：** `tb/test_arch_common.veryl:2499-2523` 定义 `test_arch_rv64ua_amoadd_d` 测试入口和 pass assertion，关联 `test/riscv-arch-test/build/rv64ua/amoadd_d.hex`。测试源码有入口（E17）。执行 `veryl test --test test_arch_rv64ua_amoadd_d` 时，Veryl 0.22.0 stable 和 `0.22.0-nightly (c3bf469 2026-10-12)` 都在 `tb/test_arch_common.veryl:440` 因 `invalid_initial_assign` 退出，测试未启动；日志在 `/tmp/story32-amoadd-nightly.log`（E18）。因此结果未验证，不能称为通过。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 两边源码均将 `AMOADD.D` 识别为同时涉及内存读写并产生整数目的寄存器结果的原子操作；其架构结果是内存写入旧值加 `rs2`，`rd` 返回旧值。 | E2,E5–E7 | E9,E11 |
| C2 | Kunminghu 将原子请求交给 AtomicsUnit/DCache AMO 命令处理；Heliodor 在 head 读取并计算，再在退休路径本地缓存写，同时保留失效 poison/replay 条件。机制不同；静态源码不证明任意多核交错下的正确性。 | E3–E7 | E10–E13 |
| C3 | 两边都存在从结果到 ROB 退休的源码条件路径；Kunminghu 结果由 atomic response 输出，Heliodor 旧值进入 CDB/ROB，commit ack 才允许架构映射更新。没有本案例运行观察。 | E7–E8 | E11,E14–E15 |
| C4 | Heliodor 提供专门 `amoadd_d` 测试源码入口；Kunminghu 本次源码树检索未定位专门入口。两边均未在本故事运行测试，因此不能报告通过。 | E16 | E17 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | ISA 行为、自检 | spec | inspected | RISC-V Unprivileged ISA v20260120 | A extension §12.1、Zaamo；规范链接见上文 | not-run | 不适用 | 自然对齐 RV64 `AMOADD.D` | 原子写 `old + rs2` 并返回 `old` | 已检查规范章节；不规定微架构路径 | none |
| E2 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:249,946-954` | not-run | sources.lock 快照 | `AMOADD.D` decode | MOU/AMO、两个寄存器源、整数 rd 写使能 | 源码 decode table 与 AMO 分类已检查；未运行 | none |
| E3 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/dispatch/NewDispatch.scala:814-820,890-898`; `mem/MemBlock.scala:1802-1835,1847` | not-run | sources.lock 快照 | ROB head AMO、原子 store issue | 普通 store 被屏蔽，AMO 送 AtomicsUnit，完成后返回 normal | 检查到静态阻塞与接线条件；未运行 | none |
| E4 | C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `mem/pipeline/AtomicsUnit.scala:84-97,137-178,238-313,474-495` | not-run | 对齐、Bare、可缓存、无异常为场景假设 | `rs1`, `rs2`, `rd` 与 TLB/PMP 状态 | 地址转换/条件允许后等待数据并进入 cache request | 静态状态和数据收集路径已检查；假设未运行验证 | none |
| E5 | C1–C2 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `mem/pipeline/AtomicsUnit.scala:491-537` | not-run | 自然对齐 `.D` 案例 | `amoadd_d` | DCache 请求命令 `M_XA_ADD`，含 rs2 和 mask | 源码映射及请求字段已检查；未运行 | none |
| E6 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `cache/dcache/mainpipe/AMOALU.scala:39-49,68-80` | not-run | operandBits 由实现参数决定；案例为 64 位 | AMO add | add 运算输出旧值与右操作数之和，新结果按 mask 写回 | 静态 ALU 表达式已检查；未观察实际数据 | none |
| E7 | C1,C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `mem/pipeline/AtomicsUnit.scala:357-399,479-489`; `mem/MemBlock.scala:520-529,552`; `cache/dcache/DCacheWrapper.scala:1467-1472` | not-run | hit/无异常为案例假设 | DCache AMO response | cache 读数据格式化后进入 atomic 输出；DCacheWrapper 注册 atomic response | 源码显示 old response 数据与 output identity/data 连接；未运行 | none |
| E8 | C3 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/rob/Rob.scala:784-801`（通用 commit-valid 门控，不特指 AMO） | not-run | sources.lock 快照 | 已完成 ROB head | 通用 commit valid 受 commit-ready 与阻塞条件控制；非 AMO 专属，也无动态退休观察 | 检查到静态 commit 条件；无本例动态退休观察 | none |
| E9 | C1 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/decoder.veryl:606-628`; `src/core/decode.veryl:190-211,257-260` | not-run | sources.lock 快照 | AMO funct5 00000, funct3 011 | 读写内存并以旧内存值选择目的寄存器写回 | decoder 与 operand flags 已检查；未运行 | none |
| E10 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/iq_int.veryl:420-430,940-948` | not-run | 无特定配置观察 | AMO 发射条件 | AMO 仅 head 发射并携带 AMO 标志/funct5 | 静态 IQ 选择条件已检查；未运行 | none |
| E11 | C1,C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/alu_wrap.veryl:266-287,312-363,358-363,400-438`; `src/core/heliodor_core.veryl:3023-3057` | not-run | 64-bit `.D`，自然对齐场景 | 旧 dcache data、rs2、AMOADD | 新值为 64 位加法结果；`amo_wb`/CDB data 为旧值，store_data 为新值 | 数据选择和 CDB 字段已检查；未运行 | none |
| E12 | C2 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:5788-5811,5859-5908` | not-run | 失效事件/配置未运行观察 | AMO 读到的缓存行在退休前离开 | watch poison；源码条件使 poisoned AMO replay | 静态 watch/poison 逻辑已检查，不是竞争验证 | none |
| E13 | C2–C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:3994-4007,4062-4072,7489-7525,7553-7556` | not-run | M-mode Bare/可缓存主存为场景假设 | AMO head commit，line ownership 保持 | clean path commit 写；poison 抑制写并 replay；commit 写使用读时地址 | 源码注释、ack 和 dcache write enable 已检查；未运行 | none |
| E14 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/rob.veryl:560-578,1520-1534` | not-run | sources.lock 快照 | 已写回的有效 head | commit valid 后经 ack 移出 head | 检查到静态 ROB 条件；无动态退休观察 | none |
| E15 | C3 | source | inspected | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:4416-4420` | not-run | sources.lock 快照 | commit ack 与整数目的寄存器 | architectural RAT/free-list 更新由 commit ack 控制 | 静态架构映射接线已检查；未运行 | none |
| E16 | C4 | test-inspected | unverified | Kunminghu / `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/test`；`src/test/scala/xiangshan/DecodeTest.scala:38-49` | `rg -ni 'amoadd_d|amoadd\.d|amoadd-d' sources/xiangshan/src/test` | 不适用 | 专门 `AMOADD.D` 测试入口 | 应能定位名称/助记符命中 | 搜索范围 `sources/xiangshan/src/test` 未命中；DecodeTest 是译码 smoke test，不证明 AMO 语义 | none |
| E17 | C4、自检 | test-inspected | unverified | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_arch_common.veryl:2499-2523` | 源码检查 | Veryl harness | RV64UA `amoadd_d.hex` | harness assertion 要求 pass | 已检查测试入口与 assertion；入口不代表执行通过 | none |
| E18 | C4、自检 | test-run-attempt | blocked-before-test | Heliodor / `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `tb/test_arch_common.veryl:440` | `veryl test --test test_arch_rv64ua_amoadd_d`，在 `sources/heliodor` | Veryl 0.22.0 stable；`0.22.0-nightly (c3bf469 2026-10-12)` | 执行既有 RV64UA AMOADD.D case | 若启动，harness 应执行 AMOADD.D ISA 用例并报告 assertion 结果 | 同一命令分别用 stable 与 nightly 尝试；两个版本均 exit 1；编译阶段 `invalid_initial_assign`，提示 `dram` initial `$readmemh` 赋值；测试未启动，行为未验证 | `/tmp/story32-amoadd-nightly.log`（nightly） |

- `inspected` 表示规范或固定快照源码已检查；`unverified` 表示测试入口检查过但没有运行。有一次测试命令的双版本运行尝试记录（E18），状态为 `blocked-before-test`，不是 `run-pass` 或测试断言失败；测试未实际运行。
- 源码中的条件与注释不等于本案例运行观察，也不证明任意跨核交错下的正确性。地址对齐、M-mode Bare、缓存属性及无访问异常是选定案例前提。

## 学习者总结

`AMOADD.D` 在单条架构操作中原子地读取旧 64 位值、写入旧值加 `rs2`，并将旧值返回到 `rd`；普通 `LD` 后接 `SD` 不提供这种单操作原子读改写保证。Kunminghu 译码后串行路由到 AtomicsUnit 和 DCache 的 AMO 加法通路，响应旧值并送往目的寄存器，ROB 负责退休。Heliodor 将 AMO 限制在 ROB head 执行，ALU/CDB 将旧值作为寄存器结果、将新值作为待提交写数据，并在提交时执行本地缓存写；源码也显示失效 poison/replay 条件。以上为静态源码证据；Heliodor 有测试入口，Kunminghu 此次未检出专门入口，Kunminghu 专用测试未定位；Heliodor 测试在工具链编译阶段失败、未启动。未验证竞争交错、异常权限路径、未对齐访问或其他原子指令。

## 未解问题

- 两边实际输入、旧值、新值、返回 `rd` 值和退休均未动态观察。
- 两边在多核竞争下的原子性没有由本单元验证；Heliodor poison/replay 源码机制不构成竞争正确性结论。
- Kunminghu 专门 AMOADD.D 测试可能位于本次搜索范围以外；没有从未定位入口推断其全仓库不存在。
