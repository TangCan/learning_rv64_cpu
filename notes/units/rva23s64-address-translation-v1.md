---
unit_id: "rva23s64-address-translation"
stage_id: "Epic 4 / Story 4.8"
scope: "RVA23S64/v1.0/§3.1.2.2 的 Svbare、Sv39、Svade、Ssccptr、Svpbmt、Svinval、Svnapot 地址转换要求；固定 Kunminghu/Heliodor 快照的有限静态映射与目标测试证据。"
exclusions:
  - "Sv48、Sv57 与 Svadu 是 RVA23S64 expansion options，不是本单元必选验收项；只作范围线索。"
  - "Hypervisor VS/G-stage 翻译与 HFENCE 不纳入结论，即使源码/共享路径提及。"
  - "不证明完整符合性；页表主存区域必须同时满足 cacheability 和 coherence PMA，本轮未验证平台 PMA 映射。"
  - "所有未明确运行的页表权限、PMA、NAPOT 与失效组合均保持未验证。"
spec_refs:
  - name: "RVA23 Profile"
    edition: "v1.0"
    section: "§3.1.2.2 mandatory extensions; §3.1.2.3.3 expansion options"
    url: "https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-2-rva23s64-mandatory-extensions"
    profile_category: "mandatory (Sv48/Sv57/Svadu are expansion options)"
  - name: "RISC-V Privileged Architecture"
    edition: "v1.13 modules; ratified extensions v1.0"
    section: "§§12.1.10 (satp), 12.3 (Sv39), 12.3.2 (PTE), 12.3.3 (translation algorithm), 12.3.4 (A/D), chapters 10.1 Svnapot, 11.1 Svpbmt, 12.1 Svinval"
    url: "https://docs.riscv.org/reference/isa/v20240411/priv/supervisor.html; https://docs.riscv.org/reference/isa/v20240411/priv/svnapot.html; https://docs.riscv.org/reference/isa/v20240411/priv/svpbmt.html; https://docs.riscv.org/reference/isa/v20240411/priv/svinval.html"
    profile_category: "ratified normative architecture"
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

<!-- 有限学习映射，不构成符合性认证。 -->

## 架构行为与子案例

| 要求 | 规范行为与适用条件 | 本轮子案例边界 |
| --- | --- | --- |
| Svbare | satp.MODE=0 必须可用；关闭翻译。 | Bare 下取指/读写及与 Sv39 切换；不能只凭读数据测试推出全部访存。 |
| Sv39 | satp.MODE=8 的 39-bit 分页；3 级 9-bit VPN 索引，4 KiB 页及合法 superpage，规范 VA 符号扩展、权限与 page/access fault。 | 非规范 VA、权限矩阵、superpage、ASID/global、取指/读/写分别未穷尽。 |
| Svade | A=0 的访问及 D=0 的写入必须 page fault；不进行硬件 A/D 更新。Svadu 是可选扩展。 | A/D 两位、取指/读/写组合和 fault cause/value 未由本轮测试穷尽；Heliodor test_mmu 的 PTE 已预置 A=D=1。 |
| Ssccptr | 同时具 cacheability 与 coherence PMA 的主存区域，硬件必须可读页表。 | PTW PTE 隐式读路径可追踪；尚未验证平台对所有合格主存区域的 PMA 属性、故障注入及一致性可见性。 |
| Svpbmt | `menvcfg.PBMTE` 控制扩展；PTE PBMT[1:0]：0=PMA、1=NC、2=IO、3=reserved。 | 编码及 PBMTE on/off 未完整运行验证；实现字段响应不等于已验证最终访存属性。 |
| Svinval | 支持 SINVAL.VMA 与 SFENCE.W.INVAL / SFENCE.INVAL.IR 的细粒度失效和顺序语义。 | U-mode 执行 SINVAL.VMA 与两个 ordering fences 应 illegal；S-mode 的 SINVAL.VMA 受 TVM 控制，ordering fences 在 M/S 为 NOP；VS/VU 路径另受虚拟化控制且未验证。全局/VA/ASID 选择、in-flight walk、排序均未运行。SFENCE.VMA 测试不作为 Svinval 证据。 |
| Svnapot | Sv39 支持规范定义的 NAPOT 连续映射（64 KiB）；N=1 仅适用于规范允许的 leaf 情况。 | 合法/非法 PTE、每个 4 KiB 子页命中与边界覆盖未运行验证。 |

## Kunminghu 路径

活动配置绑定关系和源码仅支持范围判断，不代表全芯片行为已动态确认。`FuConfig` 实际 CSR 路径为 `backend.fu.CSR`；该实现 satp 写入仅接受 MODE=0/8。`MMUConst` 定义 Sv39/Sv48 编码与 PTE 的 N/PBMT 字段；`TLB.scala` 的 `ldUpdate`、`stUpdate`、`instrUpdate`（lines 487–489）分别把读 A=0、写 A=0 或 D=0、取指 A=0 合入 page-fault 输出（lines 517, 548–550）；这是静态源码证据，未有本轮 A/D fault runtime verification。TLB、PageTableWalker、TLBStorage、L2TLB 实现翻译层级、PTE 校验/缓存及 sfence 入口。Sv48 代码受配置控制，profile expansion option，不能作为本故事必选结论。PTW 通过 MMU memory request 做隐式 PTE 读取；物理访问权限/总线侧 PMA 条件需另结合实际平台核查。本轮未找到/未运行 Kunminghu 的 MMU/PTW 定向入口。

## Heliodor 路径

`mmu.veryl` 将 satp MODE、VPN[2:0]、三层 walk、TLB、PTE 权限与 A/D fault 路径连起来；Bare passthrough 在 `dmem_mmu.veryl`、`imem_mmu.veryl`。PTE 请求经 core/cache 的 PTW 接口，`pmp_check.veryl` 负责物理权限；PMA-hole 条件也会影响访问，不能假定任意 PTE 放置位置均适用 Ssccptr。`menvcfg.PBMTE` gating 下，PBMT[1:0] 0=PMA、1=NC、2=IO、3=reserved；Heliodor 源码可追踪字段检查/响应传递，但本单元未确认最终访存属性。commit-time [U-mode illegal check](../../sources/heliodor/src/core/heliodor_core.veryl:4396) 与 [S-mode TVM check](../../sources/heliodor/src/core/heliodor_core.veryl:4339) 覆盖 SINVAL/order-fence illegal 与 SFENCE.VMA/SINVAL.VMA；ordering fences 在 M/S 为 NOP。VS/VU 另走虚拟化控制分支，本轮未验证。Svnapot 的 N=1 64 KiB 处理位于 level-0 leaf，Sv39 较高层 N=1 走 fault 路径。Decoder 识别 SINVAL.VMA 和两个 ordering fence；其 MMU 失效路径是保守整 TLB flush，尚不能据此证明所有精确/并发语义。代码同时包含 H/VS/G-stage、Sv48/Svadu 线索，均排除在本结论范围外。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 | Heliodor 证据 |
| --- | --- | --- | --- |
| C1 Svbare/Sv39 | 两侧都有明确 Bare/Sv39 路径；Heliodor 两个目标单测本轮通过。权限/异常全矩阵未验证。 | E2,E3 | E3,E4,E5 |
| C2 Svade | Kunminghu TLB 静态源码明确：`ldUpdate` 对 A=0 读触发 fault，`stUpdate` 对 A=0 或 D=0 写触发 fault，`instrUpdate` 对 A=0 fetch 触发 fault；Heliodor 有 A/D 检查路径线索。没有这些 A/D fault 的 runtime 验证；test_mmu PTE 为 A=D=1。 | E2 | E3,E4,E5 |
| C3 Ssccptr | 两侧有 PTW 硬件隐式读取线索，但需同时满足 cacheability+coherence PMA；实际平台合格区域尚未核验。 | E2 | E3 |
| C4 Svpbmt | `menvcfg.PBMTE` gating；PBMT 0=PMA、1=NC、2=IO、3=reserved。Kunminghu 可见 PBMTE 的 PTE 检查与 TLB response 字段；Heliodor 可见字段 gating/check 与字段到 TLB response。未验证最终 memory attributes。 | E2 | E3,E4,E5 |
| C5 Svinval | Kunminghu 有源码级 sfence/Svinval 路径；Heliodor decoder 与 [commit-time TVM check](../../sources/heliodor/src/core/heliodor_core.veryl:4339)、[U-mode illegal check](../../sources/heliodor/src/core/heliodor_core.veryl:4396) 源码可见 U-mode illegal、S-mode TVM 对 SFENCE.VMA/SINVAL.VMA 的约束，ordering fences 在 M/S 为 NOP；VS/VU virtual controls 未验证。test_mmu 的 SFENCE.VMA run 不作为 Svinval 执行证据。 | E2 | E3 |
| C6 Svnapot | 两侧源码均有 N 位相关映射；Heliodor 为 64 KiB Sv39 leaf 路径且有定向测试材料，但该架构测试本轮无法启动。 | E2 | E3,E4,E6 |

<a id="evidence-table"></a>

## 证据表

| ID | 支持的 claim | Kind | Status | 项目 / snapshot | 证据位置 / 测试材料 | Command / configuration | Observed / scope |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | 强制身份、行为与选项范围 | spec | inspected | RVA23 Profile v1.0; Privileged Architecture v1.13 | [RVA23S64 mandatory extensions §3.1.2.2](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-2-rva23s64-mandatory-extensions); [RVA23S64 expansion options §3.1.2.3.3](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html#3-1-2-3-3-expansion-options); [Svpbmt v1.0 §11.1](https://docs.riscv.org/reference/isa/v20240411/priv/svpbmt.html); [Svinval v1.0 §12.1](https://docs.riscv.org/reference/isa/v20240411/priv/svinval.html); [Svnapot v1.0 §10.1](https://docs.riscv.org/reference/isa/v20240411/priv/svnapot.html); [Privileged Supervisor ISA v1.13](https://docs.riscv.org/reference/isa/v20240411/priv/supervisor.html) | not-run | Svbare/Sv39/Svade/Ssccptr/Svpbmt/Svinval/Svnapot 是本单元七项；Sv48/Sv57/Svadu 是 expansion options。 |
| E2 | Kunminghu 静态路径 | source | inspected | `xiangshan-kunminghu-v2-20261012` | [active CSR and satp WARL](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/CSR.scala); [MMU constants](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/MMUConst.scala); [TLB](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala); [PTW](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/PageTableWalker.scala); [TLB storage](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/TLBStorage.scala); [L2 TLB](../../sources/xiangshan/src/main/scala/xiangshan/cache/mmu/L2TLB.scala); [Fence](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/Fence.scala); [PMP](../../sources/xiangshan/src/main/scala/xiangshan/backend/fu/PMP.scala) | static source only | inspected paths include satp 0/8, walk, A/PTE fault checks, N/PBMT fields, selective sfence. Profile-wide PMA and dynamic behavior not established. |
| E3 | Heliodor static paths | source | inspected | `heliodor-master-20261012` | [MMU](../../sources/heliodor/src/mmu/mmu.veryl); [dmem wrapper](../../sources/heliodor/src/mmu/dmem_mmu.veryl); [imem wrapper](../../sources/heliodor/src/mmu/imem_mmu.veryl); [PMP](../../sources/heliodor/src/mmu/pmp_check.veryl); [decoder](../../sources/heliodor/src/core/decoder.veryl); [core PTW integration](../../sources/heliodor/src/core/heliodor_core.veryl) | static source only | confirms code paths and conditions; not a full architectural audit. |
| E4 | Heliodor MMU、Svade、Svpbmt、Svnapot 测试材料检查 | test-inspected | inspected | `heliodor-master-20261012` | [test_mmu Bare/Sv39 + ASID](../../sources/heliodor/tb/test_mmu.veryl); [Svade-related architecture cases](../../sources/heliodor/tb/test_arch_common.veryl:3066); [Svnapot](../../sources/heliodor/tb/test_arch_common.veryl:4782); [Svpbmt](../../sources/heliodor/tb/test_arch_common.veryl:4810) | not-run | Materials identified; Svade material is not part of this run, and the NAPOT/PBMT harness compile did not execute. |
| E5 | Heliodor Bare/Sv39 与 ASID selective SFENCE 定向测试运行 | test-run | run-pass | `heliodor-master-20261012` | [test_mmu](../../sources/heliodor/tb/test_mmu.veryl); includes `test_mmu_asid` | `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_mmu`; `veryl 0.22.0 (967e477)` | 2 passed, 0 failed, 29 ignored。`test_mmu` Phase 1 在 M-mode/satp=0、VA 0x100 读取并保存 `bare_rdata`；Phase 2 写 MODE=8 并切到 S-mode；Phase 3 以同一 VA 触发 Sv39 walk，在 busy 结束后保存 `stored_rdata`。通过条件是两次读值都等于 `64'hDEAD_BEEF_CAFE_BABE`。此外同一 runner 运行 ASID isolation/selective SFENCE.VMA case；这只验证 SFENCE.VMA，不验证 SINVAL.VMA 或 Svinval ordering fences。test_mmu PTE 预置 A=D=1，因此无 Svade 覆盖。 |
| E6 | Svnapot architecture harness compile attempt | test-run | run-fail | `heliodor-master-20261012` | [test_arch_svnapot](../../sources/heliodor/tb/test_arch_common.veryl:4782) | `veryl test --test test_arch_svnapot`; same Veryl tool | Veryl check failed at `test_arch_common.veryl:440 invalid_initial_assign` (`$readmemh` writes dram in initial); stale harness missing-port warnings; test did not execute. |
| E7 | Kunminghu directed MMU tests | test-inspected | unverified | Kunminghu fixed snapshot | Repository test path search for MMU/PTW/TLB-specific test entry | not-run | No suitable existing target identified during this pass; no run result claimed. |

## 验证状态

本轮实际运行了 Heliodor `test_mmu`，其 runner 同时选择 `test_mmu` 和 `test_mmu_asid`，结果 2 passed；这只覆盖给定 Bare/Sv39 数据访问和选择性 ASID fence 案例。另尝试 `test_arch_svnapot`，被 Veryl check 阶段的现有 testbench `$readmemh` initial assignment 错误挡住，测试本体未执行。Kunminghu 本轮未运行测试。源码检查、测试材料检查和实际运行结果已分列；不存在将未执行测试记为通过的情况。

## 学习者总结

分析地址转换时，先判 satp 模式与特权级，再追踪 VPN 索引、PTE 隐式读、leaf 权限/A-D/PBMT/N 属性、TLB 填充和失效。仅在同时具 cacheability、coherence PMA 的主存区域要求 Ssccptr 的页表读取支持。单条 Bare/Sv39 测试并不覆盖所有 fault、PMA 和扩展行为。

## 未解问题

- 两侧平台 PMA 如何精确标记可缓存且一致的主存区域，PTW 对区域边界/访问故障的完整行为。
- Svade A/D fault 的所有取指/读/写组合、fault address/cause；本轮没有有效运行覆盖。
- PBMT 三种编码、禁用控制和 cache/coherence 互操作的动态验证。
- Svnapot 64 KiB 的每个 4 KiB 地址子页、非法 N 编码及边界测试。
- Svinval 指令的完整顺序语义及 in-flight translation 与选择失效组合。
- Kunminghu 无 MMU 目标测试入口的原因和可复现动态验证方法。
