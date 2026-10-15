---
unit_id: "store"
stage_id: "阶段 3"
scope: "在 RV64I M-mode Bare 场景中追踪自然对齐的普通 `SD`，从解码、地址/数据形成到 Kunminghu StoreQueue uncached request handshake 与 Heliodor committed store buffer 接受条件。"
exclusions:
  - "未对齐、向量/原子 store，以及本案例默认 PMA uncached/MMIO 之外的其他显式 uncached 变体。默认 PMA 的 uncached/MMIO 路径属于本记录范围。"
  - "不推断 DCache drain、下游总线事务、其他观察者可见性或 DRAM 持久性。"
  - "不从单条 SD 推断内存顺序、性能或 RVA23 整体符合性。"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual, RV64I Base Integer Instruction Set"
    edition: "v20260120; RV64I version 2.1"
    section: "§3.1.3 Load and Store Instructions"
version: 1
evidence_namespace: "SD1-E1–SD1-E8"
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

- **问题：** 对共同案例 `SD x11, 0(x10)`（`x10=0x80004000`、`x11=0x1122334455667788`），提交、写入接受和 DRAM 可见性分别能从源码确认到哪里？
- **学习者答案：** 架构语义是把 `rs2` 的 64-bit 值写到 `rs1 + sign_extend(S-imm)` 指向的内存；本例地址自然 8-byte 对齐。两快照静态源码显示 Kunminghu 的 SD 进入 StoreUnit / StoreQueue；若用默认 PMA，DRAM 范围读写开放但 `c=false`，因此从 StoreQueue uncached/MMIO request handshake 作为接受终点：请求在 ROB head/pending 阶段发出，位于 response、writeback 与 retirement 之前。Heliodor 在 ROB head 产生 commit-store 条件，计算 `SD` 的 `0xff` byte strobe；该 PA 属于 DRAM 且避开 tohost 页，满足普通 fast-store 条件时由 `sb_push` 接受进入 committed store buffer。DCache drain 在此之后。源码仅支持这些条件路径；案例输入、默认配置实际使用、提交和接受均未运行观察。握手和 buffer push 都不证明 DRAM 可见或持久。
- **检查类型：** explanation + source-location
- **证据 ID：** SD1-E1–SD1-E8；未运行 SD 测试/仿真

## 架构行为与子案例

`SD rs2, imm(rs1)` 以 `EA=x[rs1]+sign_extend(S-imm)` 写入 8 字节。本例固定 `SD x11, 0(x10)`、`x10=0x80004000`、`x11=0x1122334455667788`、M-mode Bare；设定 PA=VA，目标 8-byte 自然对齐，Heliodor 的 tohost 区间以外。以上寄存器值和运行配置是案例 assumption，实际行为 unverified。

| 子案例 | 覆盖状态 | 说明 |
| --- | --- | --- |
| RV64I `SD`，8-byte 对齐，mask `0xff` | covered statically | ISA 语义及两侧宽度/掩码形成路径见 SD1-E1、E2、E5、E6。 |
| M-mode Bare，目标地址及寄存器值 | assumption | 固定比较 tuple，不代表执行记录。 |
| 两侧 ROB commit 条件和写入接受条件 | covered statically | 分别见 Kunminghu StoreQueue 提交/uncache 请求和 Heliodor commit-store/`sb_push`。 |
| 实际配置、commit、请求接受、DCache/DRAM 更新 | unverified | 没有运行本案例。 |
| 下游写事务、其他观察者可见、DRAM 持久 | unknown | 静态路径和所选 endpoint 均不足以证明。 |

## Kunminghu 路径

`DecodeUnit` 将 `SD` 解码到 StoreUnit，选择 S 型立即数。StoreUnit 用 `src(0)+SignExt(imm[11:0])` 形成地址，`src(1)` 携带写数据；S 型 store 的数据宽度形成 mask，本案例对齐 SD 对应 8 个有效 byte。DTLB response 提供 PA 与 PMA 属性；StoreUnit 的 tag probe 只是检查 tag/meta，不是实际写入。StoreQueue 记录地址、数据、mask 和异常状态；普通 cacheable store 的 committed/dequeue 条件与本例 `mmio` 特例不同，不能把普通 drain 路径套到本例。

对选定地址，Kunminghu 默认 Pmem 范围是 `[0x80000000,0x80000000000)`；默认 PMA 的该段 `r/w` 开放且 `c=false`，而 `pma_check` 把 `!c` 映射为 `mmio`。因此在默认配置前提下走 StoreQueue uncached/MMIO 状态机：当 store 到达 ROB head/pending-store 且地址/数据有效、无异常后发请求，`io.uncache.req.fire` 是请求接受 endpoint。该请求的地址、数据、mask 分别来自 `paddrModule.io.rdata(0)`、`shiftDataToLow(..., dataModule.io.rdata(0).data)`、`shiftMaskToLow(..., dataModule.io.rdata(0).mask)`（StoreQueue.scala:908-911）；对本案例对应目标地址、64-bit store data 与 8-byte mask。该 handshake 只表示 Uncache 接受请求，不是成功写入。之后 response 若 `denied`，记录 store access fault；若 `corrupt && !denied`，记录 hardware error，状态转入 writeback；`mmioStout` 再携带异常到 ROB（StoreQueue.scala:868-895）。正常 response 也在 writeback 后才允许 retirement。默认配置是否用于任何实际运行没有验证；任何响应结果都不证明 DRAM 持久。

## Heliodor 路径

Decoder 将 STORE 解码为寄存器 base 加 S 型立即数。AGU 计算地址，执行结果把地址、`rs2` 数据和 `funct3` 写入 ROB；ROB head 输出相应 store 字段。commit-store firing 受 `rob_commit_valid`、store 类型、异常/权限及 replay 条件门控。`funct3=011` 产生 `0xff` 的 SD mask；本例 byte offset 为零，故数据未移位。

Bare 普通 store 的 `fast_store` 分类要求提交 store、非 AMO、非 VM、无跨 dword 高半部、PA 位段属于 DRAM，并非 tohost 页。PA `0x80004000` 满足 DRAM 条件，且避开 `0x80000000–0x80003fff` 与 `0x80008000` 排除页。`sb_elig` 检查访问故障，`sb_push` 在 buffer 有空间或可 merge 时接受；本例的 entry 地址来自 `sb_pa = c_store_eff_pa`，写入数据与 byte strobe 来自 `st_wdata` / `st_wstrb`（heliodor_core.veryl:6707,6851-6852）。在 `PA=0x80004000`、offset=0、`SD` 的条件下，它们对应本例目标、store data 与 `0xff` mask。因此选 eligible store 的 committed store buffer push 作为 endpoint。之后 DCache drain 可先将命中独占行本地合并为 dirty，也可能走其他 cache/writeback 路径；不能将 push 或 drain ack 说成 DRAM 可见。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 | Heliodor 证据 |
| --- | --- | --- | --- |
| C1 | 两侧源码都从 S 型立即数、base 与 `rs2` 数据建立 SD 地址/数据；本例 tuple 是选定输入，不是动态观察。 | SD1-E1–E2 | SD1-E5 |
| C2 | Kunminghu 默认 PMA 对 DRAM 开放 R/W 但 `c=false`，分类到 uncached/MMIO；Heliodor 将本 PA 分类为 DRAM 且非 tohost 页。默认配置是否运行使用均未验证。 | SD1-E3 | SD1-E7 |
| C3 | Kunminghu 的源码接受边界为 store 到达 ROB head/pending 后的 `io.uncache.req.fire`；request response 随后触发 writeback，ROB retirement 再后续发生。 | SD1-E4 | — |
| C4 | Heliodor 的源码接受边界为 commit store 满足 eligibility 与 buffer 容量/merge 条件后的 `sb_push`；后续 DCache drain 独立发生。 | — | SD1-E6、SD1-E8 |
| C5 | 两个 endpoint 均不能单独证明下游写事务、其他观察者可见或 DRAM 持久；本案例全程未运行。 | SD1-E4 | SD1-E8 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 | Command | Configuration / case | Observed | 产物 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SD1-E1 | C1 | source | inspected | Kunminghu / `xiangshan-kunminghu-v2-20261012`, `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/backend/decode/DecodeUnit.scala:167`; `src/main/scala/xiangshan/mem/pipeline/StoreUnit.scala:141-176,200-255` | not-run | locked snapshot | `SD` 选 StoreUnit/S-imm；StoreUnit 形成地址、mask、TLB 请求字段 | none |
| SD1-E2 | C1 | source | inspected | Kunminghu / same snapshot | `src/main/scala/xiangshan/mem/pipeline/StoreUnit.scala:378-422` | not-run | locked snapshot | `rs2` 数据、VA/PA 状态与 LSQ bundle 形成 | none |
| SD1-E3 | C2 | source | inspected | Kunminghu / same snapshot | `src/main/scala/system/SoC.scala:60-65`; `src/main/resources/config/Default.yml:1-8`; `src/main/scala/xiangshan/backend/fu/PMA.scala:42-51,211-218` | not-run | default configuration is an assumption | 默认 Pmem 范围、PMA R/W 与 `c=false` -> `mmio` | none |
| SD1-E4 | C3,C5 | source | inspected | Kunminghu / same snapshot | `src/main/scala/xiangshan/mem/lsqueue/StoreQueue.scala:828-839,868-895,908-911,920-990,1054-1087,1133-1183,1221-1238`; `src/main/scala/xiangshan/mem/MemBlock.scala:1466-1528` | not-run | actual commit/request unverified | commit 条件；uncached/MMIO req valid/fire 与 response/writeback 分离；MemBlock 接入 Uncache | none |
| SD1-E5 | C1 | source | inspected | Heliodor / `heliodor-master-20261012`, `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/decoder.veryl:344-351`; `src/core/alu_wrap.veryl:121-132,425-438`; `src/core/rob.veryl:608-621,1322-1331` | not-run | locked snapshot | STORE S-imm decode, AGU address, ROB store address/data/funct3 | none |
| SD1-E6 | C4 | source | inspected | Heliodor / same snapshot | `src/core/heliodor_core.veryl:5927-5964,5971-5997,6664-6740` | not-run | Bare/M-mode is assumption | ROB commit gate; SD `0xff` mask; DRAM/tohost classification; `sb_elig`/`sb_push` conditions | none |
| SD1-E7 | C2 | source | inspected | Heliodor / same snapshot | `src/core/heliodor_core.veryl:5975-5995` | not-run | source classification only | `0x80004000` meets DRAM predicate and avoids both tohost exclusions | none |
| SD1-E8 | C4,C5 | source | inspected | Heliodor / same snapshot | `src/core/heliodor_core.veryl:6664-6740,6707,6851-6852,7460-7478`; `src/cache/dcache.veryl:1341-1350,1947-2002,2710-2728` | not-run | no runtime observation | `sb_push` acceptance and `sb_pa`/`st_wdata`/`st_wstrb` entry fields; separate drain ack/local dirty merge/writeback path | none |

- Evidence type/status describe static inspection only. No test source was represented as run, and no SD test, build, or simulation was run.
- Kunminghu/Heliodor checkout HEAD match the locked SHAs at review time. M-mode Bare, register contents and default configuration selection are assumptions. Actual commit, request acceptance, buffer push, cache state, bus activity and DRAM visibility remain unverified/unknown.

## 学习者总结

共同的 `SD` 架构输入可以固定为同一地址、数据与宽度，但微架构接受点不同。Kunminghu 默认 PMA 将 DRAM 归类为 uncached/MMIO，因此本例静态路径走 StoreQueue 的 uncache request，response 在后续返回。Heliodor 将该地址视为普通 DRAM fast-store 候选，提交 store 满足资格且 buffer 可接受时通过 `sb_push` 入队。ROB commit、uncache request 接受、store-buffer 接受、DCache drain 与 DRAM 可见性是不同事件；本记录只追到各自源码支持的 endpoint，没有动态运行证据。

## 未解问题

- 默认 SoC/PMA 与 Heliodor DRAM/tohost 设置是否用于具体运行尚未确认。
- 本例是否实际提交、Kunminghu 请求是否握手、Heliodor 是否 `sb_push` 均未运行观察。
- DCache 更新、下游写事务、其他观察者何时可见及 DRAM 持久性均未知。
