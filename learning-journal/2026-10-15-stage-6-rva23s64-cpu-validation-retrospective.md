# Stage 6 回顾：RVA23S64 五专题 CPU 行为验证

> 本文是根据 Epic 6 复盘、固定快照运行记录和五专题证据表整理的事后回顾；不补造未留存的过程。Stage 5 记录的是专题学习和当时的验证阻塞，本文记录后续建立运行入口后观测到的有限 CPU 行为，两阶段不互相回填。

## 从静态路径走向运行观察

Stage 5 的主要困难不是缺少代码线索，而是缺少能在两份固定 CPU 快照上执行专题输入的入口。Epic 6 因此先锁定工具与输入、建立 Kunminghu fixture runner 和 Heliodor 隔离 arch harness，再为 Zifencei、Sstc、Sscofpmf、Ssnpm、Ssstateen 补入代表性运行案例。两个源码基线仍为 Kunminghu V2 `c098f996bf4d301b88693b20315486d31e93bc9d` 与 Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；运行输入、命令、工具版本、CPU-start 证据及输出摘要可由[CPU 验证 manifest](../notes/units/evidence/cpu-validation-toolchain-v1.yaml)追溯。

下表的日期来自 Git 作者元数据（`%aI`，UTC+08:00），表示这些变更进入版本历史的时间，不是工作会话日志，也不能证明具体操作发生时刻。可用 `git show -s --format='%H %aI %s' <SHA>` 复核：

| 作者时间 | 提交 | 里程碑 |
| --- | --- | --- |
| 10-14 12:21 | `32e7bfd524e62aff167af7ec2d4fbd2f35d36568` | 固定 CPU 工具链与 smoke 证据 |
| 10-14 13:15 / 13:48 | `7aa4e7a5427445f5e4c1b1a7af3f15b16e844089` / `32d2a1664cbeba17865204276183fdd33aa621f0` | Kunminghu fixture runner / Heliodor 隔离 runner |
| 10-14 14:16 | `47ef772d2b0f47c3e24547b9019edcd6a4eb476b` | Zifencei 双核运行证据 |
| 10-14 16:56 / 18:39 / 19:46 | `79c7e47d05845d5148edb2452781a8eefa805108` / `545630e5c47ce89437b1da3be4567a653f0e9d28` / `2107400a5b1122131dea0cd865f9739bbf7ed65c` | Sstc、Sscofpmf、Ssnpm 运行矩阵 |
| 10-15 09:26 / 10:42 | `93bd409f6b375e683fca04cc4e70637ec7144b55` / `333e102489b27d371e75b3bc9944de6720ae6557` | 五专题交付与复盘行动完成 |

Ssstateen 与八个故事的最终验收和具体阶段结论见 [Epic 6 复盘](../_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md)。

## 代表性结果及边界

| 专题 | Kunminghu V2 | Heliodor | 可得结论与限制 |
| --- | --- | --- | --- |
| Zifencei / `FENCE.I` | 四个单 hart 自修改代码/编码变体用例运行通过 | 同样四个用例运行通过 | fixture 检查旧指令值 `1` 到新指令值 `42`；不覆盖 hart 间发布与远端取指同步，也不等于全部编码或符合性验证。详见 [Zifencei 运行证据](../notes/units/rva23s64-zifencei-v1.md#evidence-table)。 |
| Sstc | S-mode `<`、`==`、`>` 比较及 STCE/TM 关闭时的访问异常用例通过 | S/VS 比较和中断路由代表用例通过；单独关闭 M/H STCE 或 TM 的若干 gate 用例 CPU 已启动但未产生预期 trap，判为 `run-fail` | 同一专题可同时有通过和失败；Heliodor 的 gate 失败是目标行为观察，不是 Stage 5 的旧 `$readmemh` testbench 阻塞。详见 [Sstc 动态矩阵](../notes/units/rva23s64-sstc-v1.md#dynamic-sstc-evidence)。 |
| Sscofpmf | 硬件计数溢出、五种 xINH 过滤、清除/重触发及部分访问路由案例通过 | 首次硬件溢出主路径通过；扩展 OF 清除/re-arm 运行失败，S/U 过滤结果包含失败和未完成观察 | 不能把一个硬件溢出 pass 扩大为全部过滤、delegation 或模式组合通过。详见 [Sscofpmf 双核矩阵](../notes/units/rva23s64-sscofpmf-v1.md#story-6.6-双核运行矩阵)。 |
| Ssnpm | PMLEN 0/7 canonical 标量和部分 tagged 案例有通过记录；PMLEN7 tagged atomic 在 LR.D 遇 cause 5/difftest ABORT，后续 SC/AMO 未到达 | canonical 和部分 tagged 标量用例有记录；修正后的 PMLEN0 tagged 输入因 DRAM 低位别名意外访问成功，fixture 以 `run-fail` 记录 | Heliodor 的失败是 harness 地址别名限制，不能据此断定 DUT 缺陷；部分运行通过也未直接证明 masked effective address。FP、compressed、CMO、vector、guest 等访问族仍未验证。详见 [Ssnpm 证据表](../notes/units/rva23s64-ssnpm-v1.md#evidence-table)。 |
| Ssstateen | M/HS 主矩阵及部分 S、VS、VU 适用字段和 gate 检查通过 | M/H/S/VS gate 主路径出现 CPU-started `run-fail`；SE 写入读回为 0，无法形成有效 gate-open 对照；VU 特权异常分类和 FCSR 可用性用例通过，但不是 gate 对照 | Kunminghu 的通过和 Heliodor 的受限失败分别适用于实际运行的快照与输入；不能推广到未运行的 custom CSR、WARL/reset 或全部 guest 状态。详见 [Ssstateen 固定快照矩阵](../notes/units/rva23s64-ssstateen-v1.md#story-6.8-固定快照运行矩阵-2026-10-14)。 |

只按 CPU manifest 的 `snapshots[].runs` 中 `result` 字段分组计数，Kunminghu 共 130 条（81 `run-pass`、38 `run-fail`、6 `blocked`、5 `unverified`），Heliodor 共 168 条（57 `run-pass`、81 `run-fail`、30 `blocked`）；这一可复算口径也记录在 [Epic 6 行为验证审计](../_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md#behavior-verification)。这些是累计尝试数，含探索、失败和阻塞，不是通过率。

状态须结合具体 fixture 理解：`run-pass` 表示该输入通过了它声明的断言；`run-fail` 表示 CPU 已启动但运行记录中的预期与观察不一致，若有 alias/harness 限制则不能直接归因于 DUT 缺陷；`blocked` 表示目标 CPU 未启动（例如构建或 testbench 检查阻塞）；`fixture-incomplete` 表示 CPU 已运行但 fixture 未到达完整终结断言，只能保留已观测阶段；`harness-limited` 表示运行观察受仿真内存别名或可见性限制，不能支撑更强结论；`unverified` 表示没有足以回答该项的目标行为观察。专题结果见上述证据表，不能以单一数字代替。

## 复盘、结项与学习所得

Epic 6 的八个故事完成，阶段 verdict 为 `accepted-with-open-items`（criteria: profiled）。它接受的是固定快照上的运行入口、代表性案例和可追溯学习记录，不是完整 RVA23 行为验证或认证。复盘指出 runner 的启动/失败分类、分派集成测试、Ssstateen case 映射、运行矩阵一致性和归档体积需要改进；这些行动随后在 [Epic 6 行动完成记录](../_agile-output/implementation-artifacts/epic-6-retro-2026-10-15.md#行动项实施证据-2026-10-15)中闭环，包含新增分类与矩阵校验、集成测试及归档盘点。

归档盘点记录 smoke evidence 共 2,410 个文件、约 1.02 GiB；重复内容可以识别，但扩展名不足以证明产物可重建，所以本次保留全部文件，没有压缩或删除。行动完成不意味着历史运行目录已精简。

这阶段最重要的学习增量，是能把“源码里有路径”“测试源码覆盖了某条件”“CPU 实际观察到结果”分开表述。通过和失败并存并不矛盾；差异要落到固定版本、模式、输入、控制位和 fixture 观测上。测试矩阵更完整，也不会自动把案例变成 profile 全覆盖。

Stage 1–6 的历史回顾现已齐备。后续若要继续学习访存或扩展 RVA23 行为验证，应另立具体主题和完成门槛；当前阶段日志不承诺开展新的 CPU 实验。
