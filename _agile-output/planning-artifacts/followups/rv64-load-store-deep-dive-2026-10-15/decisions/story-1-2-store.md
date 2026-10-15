# Story 1.2 决策：共同 SD 案例与接受终点

## 共同 tuple

- 指令：RV64I `SD x11, 0(x10)`。
- 输入：`x10 = 0x80004000`，`x11 = 0x1122334455667788`；`imm=0`，因此 `VA=0x80004000`。
- 场景：M-mode Bare，故本案例设定 `PA=VA`；8-byte 自然对齐。寄存器初值、特权/地址转换状态及本例实际执行均为 assumption / unverified，不是运行观察。
- byte mask：`0xff`；本文只记录 64-bit 数据 tuple，不声称观察到下游字节写事务。

## 默认分类差异

- Kunminghu 的 `SoCParameters` / `Default.yml` 默认 Pmem range 为 `[0x80000000, 0x80000000000)`，PMA 在 `0x80000000` 配置 `r=true,w=true,c=false`。`PMA.scala` 将 `!c` 映射为 `mmio`；若采用此默认配置，目标属于读写开放的 DRAM 范围，但被分类为 uncached/MMIO 路径。默认配置是否用于某次运行未验证。
- Heliodor 的提交路径把 `PA[63:25]==0x40` 分类为 DRAM。`0x80004000` 满足该条件；它不在 `0x80000000–0x80003fff`（`[31:14]==0x20000`）或 `0x80008000` tohost 排除页。若采用源码逻辑，则符合 fast-store DRAM 路径；实际配置与运行未验证。

## 采用的路径终点

- Kunminghu：终点选 StoreQueue 的 uncached/MMIO request handshake（`io.uncache.req.fire`）。它发生在 store 已到 ROB head 且 pending 后、ROB retirement 前；请求 response 随后触发 writeback，之后才发生 ROB retirement。请求以本例地址/数据/mask 发出（StoreQueue.scala:908-911）；handshake 表示 Uncache 接受请求，随后 response 的 denied/corrupt 可能转成异常并经 writeback（StoreQueue.scala:868-895）。它在 ROB head/pending 后、response/writeback 和 retirement 前，不证明成功写入或 DRAM 可见/持久。
- Heliodor：终点选 eligible store 进入 committed store buffer（`sb_push`）。`sb_push = sb_elig && (sb_merge_ok || !sb_full)`，容量或同 line merge 条件决定接受；它与 head commit-store firing 同周期。之后 DCache drain 另行发生，drain ack 也不单独证明 DRAM 可见或持久。

## 未知边界

本案例没有动态运行证据。未观察实际地址/数据、PMA/DRAM 配置、ROB commit、请求握手、`sb_push`、DCache 更新/写回、下游总线事务、其他观察者可见性或 DRAM 持久性。Kunminghu request handshake 发生在 ROB head/pending 后、response/writeback 与 retirement 前；Heliodor endpoint 是提交 store 的 buffer 接受。它们不是相同的可见性时点。

## 证据索引

证据 ID `SD1-E1`–`SD1-E8` 及结论见 [store-v1 证据表](../../../../../notes/units/store-v1.md#证据表)。
