---
unit_id: "branch-recovery"
stage_id: "阶段 2"
scope: "条件分支预测不跳转、实际结果跳转：从分支解析到年轻错误路径清除、分支保留、重命名状态恢复和正确目标重定向；比较 Kunminghu V2 与 Heliodor 固定快照源码。"
exclusions:
  - "预测跳转但实际不跳转及目标地址错误的独立追踪"
  - "陷阱、load replay、间接跳转及其他恢复原因"
  - "具体预测器配置、时序周期和性能结论"
  - "RAS 精确恢复行为与 RVA23 整体符合性"
spec_refs:
  - name: "RISC-V Unprivileged ISA Manual"
    edition: "v20260120"
    section: "RV32I §1.1.5.2；RV64I §3.1"
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

- **问题：** 条件分支被预测为不跳转但实际应跳转时，为什么年轻指令不能提交？两边如何恢复控制流和重命名状态？源码检查能证明什么，不能证明什么？
- **学习者答案：** 年轻指令沿错误后继路径取指，它们的寄存器结果和其他推测状态不属于正确架构执行，必须在提交前被清除；解析分支本身及其更老指令仍然有效。Kunminghu 的 `BranchModule` 比较预测方向和实际方向，`BranchUnit` 发出保留分支本身的 `flushAfter` redirect，ROB 清除更年轻条目；清除后的 ROB 有效位为零，而提交资格要求对应队列项有效并有可提交结果（E5、E15）。rename table 选择可用分支快照或架构映射恢复；Heliodor 比较控制指令预测与实际 next-PC，在执行阶段登记恢复，随后恢复分支 checkpoint 并部分冲刷年轻 ROB/IQ 项；其提交输出要求 head 项有效且结果已写回，因此被冲刷项不可提交（E10–E13、E16）。源码只能说明静态连接和逻辑意图；本单元没有运行恢复仿真，专用恢复测试和预测配置均未确认。**[E1–E16]**
- **检查类型：** explanation + source-location
- **证据 ID：** E1–E16

## 架构行为与子案例

- **可观察行为：** 有一条条件分支，预测器给出 not-taken，条件计算结果为 taken。顺序后继地址只是预测路径；实际下一条架构指令地址应为分支目标。错误路径年轻指令不得提交，分支及更老指令保留，处理器从正确目标继续执行。
- **规范依据：** [RV32I §1.1.5.2](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html) 定义条件分支的比较和目标控制流行为；RV64I §3.1 说明 RV64I 基于 RV32I 并列出差异，需结合阅读（[RV64I](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv64.html)）。规范不规定预测、队列冲刷或恢复实现。

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| 预测 not-taken，实际 taken | covered | 本记录限定场景；结果应沿分支目标继续。架构行为由 E1 支持，实现路径见 E2–E9。 |
| 预测 taken，实际 not-taken | excluded | 不在有界情景内；不得从本场景反推其恢复路径。 |
| 预测方向正确但目标错误 | excluded | 作为独立目标预测错误场景排除。 |
| 预测器配置、方向概率及恢复周期 | unconfirmed | sources.lock 不固定运行配置，本单元不推测配置或周期。 |
| 异常、load replay、RAS 精确状态 | excluded / unconfirmed | 恢复原因不纳入；RAS 仅提示其恢复近似边界，未作精确验证。 |

## Kunminghu 路径

- **阶段与状态变化：** `BranchModule` 由分支比较计算 `taken`，以 `pred_taken ^ taken` 得到方向错预测（E2）。对本场景该值为真，`BranchUnit` 生成 `RedirectLevel.flushAfter`，携带本分支 ROB/FTQ 标识和计算出的目标地址（E3）。控制块在写回 redirect 候选中排除已被更老 redirect 冲刷的项，并选择最老有效 redirect；转发级 redirect 到 FTQ 触发前端重定向（E4）。`RobPtr.needFlush` 对 `flushAfter` 不清除 redirect 指向的分支，只清除其后的 ROB 项；ROB 延迟一拍更新年轻项 valid（E5）。rename table 在 redirect 后恢复 `spec_table`：优先选中可用快照，否则回到 `arch_table`；快照按重命名时遇到的控制流指令等条件生成，控制块按 redirect ROB 年龄筛选快照（E6–E7）。这是带快照选择策略的恢复，不代表每条分支都有独立精确 checkpoint。RAS 的源码注释描述误预测 call/return 后重做 push/pop；具体状态一致性未在此验证（E8）。
- **源码位置：** 固定快照 `sources/xiangshan`：`src/main/scala/xiangshan/backend/fu/Branch.scala:42-50`；`backend/fu/wrapper/BranchUnit.scala:29-68`；`backend/CtrlBlock.scala:192-211,331-349,516-563`；`backend/rob/RobBundles.scala:210-215`；`backend/rob/Rob.scala:955-982`；`backend/rename/RenameTable.scala:119-141`；`backend/rename/Snapshot.scala:43-75`；`backend/rename/Rename.scala:603-628`；RAS 注释 `frontend/RAS.scala:268-269`。
- **相关验证：** 检索 Kunminghu 测试树未发现专用分支恢复测试（E9）；没有运行构建、仿真或测试。

## Heliodor 路径

- **阶段与状态变化：** ROB 保存每条指令预测的 next-PC；执行完成的控制指令只有在 ROB 项仍 live 且 `redirect_pc != rob_pred_next_pc` 时才计为 early mispredict（E10）。本场景目标地址与预测顺序后继不同，触发 early recovery；恢复时前端取用登记的实际目标 PC（E11）。分支重命名时捕获 RAT 与 free-list checkpoint；恢复使能在下一恢复阶段由 early redirect 驱动，并被同周期 commit redirect 抑制（E12）。ROB 保留 head 到分支项（含分支）并冲刷所有年轻项、把 tail 移到分支后一项；两个 IQ 也清除更年轻项。提交时的 next-PC 比较仍是 backstop：若早恢复已作用，CDB 写回时改写该分支保存的预测 next-PC，避免它之后提交时重复 redirect（E13）。
- **源码位置：** 固定快照 `sources/heliodor`：`src/core/heliodor_core.veryl:8338-8423`（live 条件、方向/目标比较、早恢复选择与登记）；`:1270-1302,1479-1483,1581-1583`（早恢复 PC 转向）；`:3389-3429`（checkpoint 和恢复使能）；`:3617-3622,3719-3729,4307-4314`（IQ/ROB squash 接线）；`src/core/rob.veryl:356-375,1536-1565`（保留分支与年轻项冲刷）；`src/core/rat.veryl:71-77,117-153`（checkpoint 捕获及 RAT 恢复）。
- **相关验证：** `sources/heliodor/tb/test_arch_common.veryl:715-739,1038-1062` 中存在 BEQ/BNE 架构测试 harness（E14），但这些测试源码不证明测试实际运行，也不证明专用早恢复边界；源码注释中的验证叙述不作为本单元运行证据。未运行任何测试。

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | 在本场景下，两边都识别控制流预测与解析结果不一致，并提供到实际目标的控制流恢复路径；Kunminghu 此处直接比较方向，Heliodor 比较预测与实际 next-PC。 | E2–E4 | E10 |
| C2 | 两边都以错分支为边界保留分支并移除年轻错误路径项；两边的提交资格检查也排除已被清除的年轻 ROB 项。Kunminghu 以 `flushAfter` 和 ROB valid/commit-ready 门控实现，Heliodor 显式 age-based partial squash 并以 head valid/result-written 门控提交。 | E3,E5,E15 | E12–E13,E16 |
| C3 | 恢复推测映射时，Kunminghu 可按 redirect 与已有 snapshot 关系选择快照或架构映射；Heliodor 在控制指令重命名时记录以 ROB index 索引的 checkpoint 并恢复该映射。证据仅说明源码机制，不代表实际运行验证。 | E6–E7 | E12–E13 |
| C4 | 验证边界不同于实现证据：Kunminghu 测试树检索未找到专用恢复测试；Heliodor 有 BEQ/BNE 架构测试源码，但其不能单独证明早恢复触发与冲刷，且本单元没有运行测试。 | E9 | E14 |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | ISA 场景 | spec | inspected | RISC-V Unprivileged ISA v20260120 | RV32I §1.1.5.2; RV64I §3.1，官方章节链接见上文 | not-run | 不适用 | 条件分支比较与控制流 | 实际跳转时 PC 指向分支目标 | 已检查规范章节；不规定微架构恢复 | none |
| E2 | C1 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/main/scala/xiangshan/backend/fu/Branch.scala:42-50` | not-run | 未指定 | `pred_taken=0, taken=1` | `mispredict=1` | 源码表达式为预测方向与实际方向异或 | none |
| E3 | C1–C2 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/fu/wrapper/BranchUnit.scala:51-64`; `backend/rob/RobBundles.scala:210-215` | not-run | 未指定 | 分支方向错预测 | 发出 `flushAfter` redirect 并指向分支目标，保留分支 ROB 项 | 已检查源码；未运行 | none |
| E4 | C1 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/CtrlBlock.scala:192-211,331-349` | not-run | 未指定 | 有效执行 redirect | 选择有效最老 redirect 并转发前端 | 已检查源码连线；未观察动态结果 | none |
| E5 | C2 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/rob/Rob.scala:955-982` | not-run | 未指定 | `flushAfter` redirect 的 ROB index | 年轻项 valid 清零，指向分支项保留 | 已检查源码年龄/valid 更新逻辑 | none |
| E6 | C3 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/rename/RenameTable.scala:119-141`; `backend/rename/Snapshot.scala:43-75` | not-run | 未指定 | redirect 与可用快照/无快照 | 恢复 spec map 到快照或 arch map | 已检查源码；具体运行选择未观察 | none |
| E7 | C3 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/CtrlBlock.scala:516-563`; `backend/rename/Rename.scala:603-628` | not-run | 未指定 | 分支 ROB 年龄与 snapshot 关系 | 选择满足边界的快照；snapshot 生成受控制流条件约束 | 已检查源码 | none |
| E8 | 恢复边界 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `frontend/RAS.scala:268-269` | not-run | 未指定 | call/return 误预测 | 源码注释称需重做 push/pop | 注释已检查；未验证完整 RAS 恢复行为 | none |
| E9 | C4 | test-inspected | unverified | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `src/test` 下路径检索；未发现专用分支恢复测试 | `rg --files sources/xiangshan/src/test` + 文件名/内容检索；未运行 | 不适用 | 专用 branch recovery test | 如有应验证该恢复案例 | 检索范围内未发现；不等同于证明仓库没有任何间接验证 | none |
| E10 | C1 | source | inspected | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:8338-8423` | not-run | 未指定 | live control op，resolved next-PC 与预测 next-PC 不同 | 记录 early mispredict 与恢复目标 | 已检查源码比较及触发逻辑；未运行 | none |
| E11 | C1 | source | inspected | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:1270-1302,1479-1483,1581-1583` | not-run | 未指定 | early redirect registered target PC | 前端从解析分支目标重新取指 | 已检查源码消费 early redirect PC；未运行 | none |
| E12 | C2–C3 | source | inspected | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/heliodor_core.veryl:3389-3429`; `src/core/rat.veryl:71-77,117-153` | not-run | 未指定 | 控制指令 rename checkpoint，后续 restore | 从分支 checkpoint 恢复推测 RAT/free-list 状态 | 已检查 capture/restore 接线；未运行 | none |
| E13 | C2–C3 | source | inspected | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/rob.veryl:356-375,1536-1565`; `heliodor_core.veryl:3617-3622,3719-3729,4307-4314,8406-8411` | not-run | 未指定 | early redirect 对应分支及年轻项 | 保留分支和更老项，冲刷年轻 ROB/IQ；改写预测 next-PC 避免重复 commit redirect | 已检查源码；动态行为未观察 | none |
| E14 | C4 | test-inspected | unverified | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `sources/heliodor/tb/test_arch_common.veryl:715-739,1038-1062` | not-run | 测试源码列出 BEQ/BNE HEX harness；运行配置未确认 | RV64UI BEQ/BNE | 测试定义预期 pass 断言 | 仅检查到测试源码；未执行，不能声称 pass 或证明早恢复 | none |
| E15 | C2、自检：年轻错误路径不能提交 | source | inspected | Kunminghu `xiangshan-kunminghu-v2-20261012`; `c098f996bf4d301b88693b20315486d31e93bc9d` | `backend/rob/RobBundles.scala:170-173`; `backend/rob/Rob.scala:752-785,788-801,955-982` | not-run | 未指定 | squash 清除年轻 ROB 项 valid；提交筛选检查队列项和写回状态 | 被冲刷项不进入 commitValid | 已检查 valid 清除与提交资格源码；未运行 | none |
| E16 | C2、自检：年轻错误路径不能提交 | source | inspected | Heliodor `heliodor-master-20261012`; `94e9c5821c24a8941c3ddc3b76daddc7124a855a` | `src/core/rob.veryl:521,560-571,1523-1529,1536-1565` | not-run | 未指定 | squash 清除年轻 entries valid；head 提交条件 | 仅非空、有效且结果写回的 head 可提交；被 squash 项不可提交 | 已检查提交资格、提交和清除源码；未运行 | none |

## 学习者总结

预测为不跳转而实际跳转时，错误路径指令必须在提交前被丢弃，分支自身和更老指令保留，取指转向分支目标。Kunminghu 从方向异或开始，通过 `flushAfter` 及 ROB 年龄清理年轻项，并按 redirect 与 snapshot 状态恢复重命名映射；Heliodor 检查 live 控制指令的预测/实际 next-PC，使用分支 checkpoint、年轻 ROB/IQ partial squash 和 commit-time backstop。两边机制均由固定快照源码检查得到；Kunminghu 没检出专用恢复测试，Heliodor 的 BEQ/BNE 测试源码也未在本单元运行。没有预测配置，未验证周期、运行结果、RAS 精确恢复或 RVA23 符合性。

## 未解问题

- Kunminghu 的分支相关 snapshot 是按控制流指令与 ROB 年龄组织的恢复近似；本单元没有验证所有分支位置、无可用 snapshot 情况及 RAS 状态是否在动态运行中完全一致。
- Heliodor 的分支专用 checkpoint restore、部分冲刷和 commit-time backstop 未由本单元实际运行或专用恢复测试确认。
- 两个快照的预测器配置、方向/目标预测参数、周期和性能影响均未确认。
