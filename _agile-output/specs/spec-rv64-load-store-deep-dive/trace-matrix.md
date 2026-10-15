# 访存路径追踪矩阵

每个阶段在 Kunminghu 与 Heliodor 栏分别记录来源、证据类型和验证状态。证据类型与验证状态是独立字段；实现阶段可以不同，不以相同术语制造虚假的一一对应。

| 观察点 | Kunminghu V2 | Heliodor | 学习记录要求 |
| --- | --- | --- | --- |
| 指令入口 | 已有 LD 学习记录；SD 入口待故事整理 | 有 RV64UI LD/SD 测试入口源码 | 固定 `sources.lock`；测试存在不等于运行通过 |
| 译码与派发 | LoadUnit/StoreUnit 路径；按选定普通标量操作追踪 | decoder / AGU 路径 | 记录操作类型、宽度、立即数/数据与控制信号 |
| 执行与地址生成 | LD 已记录；StoreUnit S0 形成 `rs1 + imm` | LD 已记录；store 地址/数据由 core/ROB 路径保留 | 来源分别见 `load-v1.md` 与 `feasibility.md`；内部阶段不强行对应 |
| 地址转换与保护 | LD/fault 路径已记录；成功 SD 的配置和保护条件尚未运行确认 | LD/fault 路径已记录；成功 SD bare DRAM 路径条件需按源码确认 | 分离源码条件与动态配置观察 |
| 数据访问与响应 | LD 已记录；SD 需区分 StoreQueue head/pending、uncache handshake、response/writeback 与 retirement | LD 已记录；SD 有 commit-store fast/slow 分支 | StoreUnit 的 tag probe 不是实际数据写入；不把 commit 自动等同缓存/内存可见 |
| 提交与架构状态 | LD retirement 静态路径已记录；Kunminghu uncached/MMIO 请求在 ROB head/pending 阶段发出，response/writeback 后才 retirement | LD retirement 静态路径已记录；SD 写入由 ROB head commit 驱动 | 本阶段不预设动态运行 |
| 异常路径 | Sv39 非规范 LD 至 page fault/ROB/CSR 有既有静态记录 | Sv39 非规范 LD 至 page fault/ROB/CSR 有既有静态记录 | 选 cause 13 load page fault；两侧动态均未验证 |

## 案例集合

- 一个成功的标量 load。
- 一个成功的标量 store。
- 一个两侧可比较的同步访存 fault：S-mode、V=0、Sv39 下非规范 VA 的普通 `LD`（cause 13）；具体寄存器/trap 配置仍在故事中列为假设。

## 证据类型与验证状态

- 类型：`spec`、`design-doc`、`source`、`test-inspected`、`test-run`、`experiment`。
- 状态：`inspected`、`run-pass`、`run-fail`、`blocked`、`unverified`、`not-applicable`。
- 示例：源码推导为 `source` + `inspected`；检查了测试代码为 `test-inspected` + `inspected`；实际测试通过为 `test-run` + `run-pass`。
- `test-inspected` 不表示测试已运行。`test-run` 的结论仅适用于记录的输入和配置；`blocked` 说明环境/工具阻止推进，`unverified` 表示缺少该行为的证据。

不得由日志中的启动标记推断某个内部阶段已发生；内部路径只有在源码或可解释 trace 明确支持时才记为已追踪。当前勘察只证明源码路径可追踪，不证明任何新案例已运行。

## Story 1.1：LD 路径记录

共同案例：RV64I `LD`、自然 8 字节对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store。这些场景条件均未由本次运行确认，作为 `assumption` 保留；实际命中、结果与退休状态为 `unverified`。终点是源码支持的写回及退休条件，不表示本案例动态到达该终点。

| 核与起点 | 路径及证据支持终点 | 固定快照 | 证据 ID | type | status | 假设与边界 |
| --- | --- | --- | --- | --- | --- | --- |
| Kunminghu V2：整数 load issue | `LoadUnit` 由源操作数和符号扩展立即数形成 VA；DTLB 响应提供 PA 后发 DCache 读请求；`LoadPipe` hit 响应经偏移/宽度选择形成 `ldout.data`，经 MemBlock/XSCore 写回接口进入 backend；load 返回状态进入 LoadQueue。ROB 可提交头项时退休，`RenameTableWrapper` 按 commit 条件更新整数 architectural map。源码终点为写回及退休条件。 | `xiangshan-kunminghu-v2-20261012`，`c098f996bf4d301b88693b20315486d31e93bc9d` | [`LD2-E2`–`LD2-E6`、`LD2-E14`](../../../notes/units/load-v2.md#证据表) | `source` | `inspected` | M-mode Bare、自然对齐、无异常、DCache hit、无更老重叠 store 均为案例假设；没有运行观察实际 hit、值或退休。 |
| Heliodor：`decoder` / AGU 发射路径 | `LOAD` decode 后由 AGU 形成地址；Bare 下 `dmem_mmu` 直通，Stage A 锁存请求，Stage B 读 DCache；hit 数据经 LSU 选为 64-bit `LD` 结果并写 CDB/PRF、记录 ROB。ROB head 完成后产生 `rob_commit_valid`；`rob_commit_ack` 移除 head 并门控 `rat_arch` 更新，`arch_regs` 调试镜像另由 `rob_commit_valid` 门控。源码终点为写回及退休条件。 | `heliodor-master-20261012`，`94e9c5821c24a8941c3ddc3b76daddc7124a855a` | [`LD2-E7`–`LD2-E11`、`LD2-E15`](../../../notes/units/load-v2.md#证据表) | `source` | `inspected` | 同上；`rat_arch` 与 `arch_regs` 是不同状态，分别受 ack 和 commit-valid 门控。没有运行观察本案例实际 hit、值或退休。 |

## Story 1.2：SD 提交与写入接受边界

共同 tuple：RV64I `SD x11, 0(x10)`，`x10=0x80004000`，`x11=0x1122334455667788`，M-mode Bare，PA=VA，8-byte 对齐。Tuple 与默认配置是案例 assumption；没有运行 SD，实际地址、commit、endpoint 接受及 DRAM 可见性均 `unverified`/`unknown`。Kunminghu 默认 PMA 分类与 Heliodor DRAM/tohost 分类是源码结论，不表示运行时确实选用了默认配置。

| 核与起点 | 路径及证据支持终点 | 固定快照 | 证据 ID | type | status | 假设与边界 |
| --- | --- | --- | --- | --- | --- | --- |
| Kunminghu V2：`SD` StoreUnit 输入 | `SD` 译码为 StoreUnit/S-immediate；StoreUnit 形成 base+imm 地址、`rs2` 数据和 mask，DTLB response 提供 PA/PMA 属性。默认配置中该地址落在 Pmem 范围，R/W 开放且 PMA `c=false`，走 StoreQueue uncached/MMIO 分支。store 到达 ROB head/pending 后，StoreQueue 用本例的 PA、`rs2` data、mask 请求 Uncache（`StoreQueue.scala:908-911`），`io.uncache.req.fire` 为接受终点。response 的 denied/corrupt 会记录异常并经 writeback（`StoreQueue.scala:868-895`），之后才 retirement；handshake 不证明成功写入。终点为 request handshake。 | `xiangshan-kunminghu-v2-20261012`，`c098f996bf4d301b88693b20315486d31e93bc9d` | [`SD1-E1`–`SD1-E4`](../../../notes/units/store-v1.md#证据表) | `source` | `inspected` | 默认配置应用、M-mode Bare、寄存器 tuple、实际 commit/handshake 均未验证。Tag probe 不是数据写入；uncache handshake 不证明 DRAM 可见/持久。 |
| Heliodor：decoder / AGU 与 ROB head commit-store | STORE/S-immediate 解码，AGU 形成地址，ROB 保存地址、`rs2` 与 funct3；commit-store 产生 SD `0xff` mask。`0x80004000` 满足 DRAM predicate 且避开 `0x80000000–0x80003fff` 和 `0x80008000` tohost 排除页。eligible head store 在 buffer 可 merge 或未满时 `sb_push`；本例 entry 用 `sb_pa`、`st_wdata`、`st_wstrb`（`heliodor_core.veryl:6707,6851-6852`）保存地址、数据和 mask，作为接受终点；之后的 DCache drain 是另一个阶段。 | `heliodor-master-20261012`，`94e9c5821c24a8941c3ddc3b76daddc7124a855a` | [`SD1-E5`–`SD1-E8`](../../../notes/units/store-v1.md#证据表) | `source` | `inspected` | 地址、Bare/DRAM 配置与 `sb_push` 实际发生均未验证。Buffer push / DCache drain ack 不证明下游事务、他方可见或 DRAM 持久。 |
