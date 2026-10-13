# 学习单元索引

本索引指向每个学习单元当前的不可变版本文件。新修订应新建 `<unit_id>-vN.md`，完成检查后再更新对应行；不要覆盖已有版本。来源快照 ID 必须引用 `sources.lock` 中的条目。阶段自检答案保存在单元记录内，阶段路线记录可索引答案但不能代替答案本身。

| unit_id | stage_id | 学习单元 | 当前版本文件（`<unit_id>-vN.md`） | 状态 |
| --- | --- | --- | --- | --- |
| `add` | 阶段 1 | RV64I `ADD` 双核对照 | [`notes/units/add-v1.md`](add-v1.md) | 试点完成 |
| `dependency` | 阶段 2 | RV64I `ADDI` RAW 依赖双核对照 | [`notes/units/dependency-v1.md`](dependency-v1.md#单元自检) | 单元记录完成；未运行验证 |
| `branch-recovery` | 阶段 2 | 条件分支错预测冲刷与恢复双核对照 | [`notes/units/branch-recovery-v1.md`](branch-recovery-v1.md#单元自检) | 单元记录完成；未运行验证 |
| `load` | 阶段 3 | RV64I `LD` 普通访存路径双核对照 | [`notes/units/load-v1.md`](load-v1.md) | 单元记录完成；未运行验证 |
| `amoadd-d` | 阶段 3 | RV64A `AMOADD.D` 原子读改写双核对照 | [`notes/units/amoadd-d-v1.md`](amoadd-d-v1.md) | 单元记录完成；测试被工具链阻止，动态行为未验证 |
| `sv39-load-fault` | 阶段 3 | Sv39 非规范 `LD` page fault 与 M-mode trap 双核对照 | [`notes/units/sv39-load-fault-v1.md`](sv39-load-fault-v1.md) | 单元记录完成；源码已检查，动态行为未验证 |
| `rva23u64-scalar` | Epic 4 / Story 4.2 | RVA23U64 基础整数与标量要求双核映射 | [`rva23u64-scalar-v1.md`](rva23u64-scalar-v1.md) | 单元记录完成；本次仅静态源码/测试材料检查，未运行测试 |
| `rva23u64-floating-point` | Epic 4 / Story 4.3 | RVA23U64 F、D、Zfhmin、Zfa 标量浮点要求双核映射 | [`rva23u64-floating-point-v1.md`](rva23u64-floating-point-v1.md) | 单元记录完成；静态源码/测试材料检查，未运行测试；舍入、NaN-box、异常 flags 与 FS 边界未验证 |
| `rva23u64-vector` | Epic 4 / Story 4.4 | RVA23U64 基础向量 V 要求双核映射 | [`rva23u64-vector-v1.md`](rva23u64-vector-v1.md) | 单元记录完成；静态源码/测试材料检查，未运行测试；完整指令、参数组合、异常/重启及 mask/tail 边界未验证 |
| `rva23u64-vector-security-and-half` | Epic 4 / Story 4.5 | RVA23U64 Zvfhmin、Zvbb、Zvkt 向量要求双核映射 | [`rva23u64-vector-security-and-half.md`](rva23u64-vector-security-and-half.md) | 单元记录已建立；静态源码、配置和测试材料已检查，未运行；Zvfhmin 转换与 Zvbb 集合未完整验证；两侧 Zvkt DIEL 均无本轮时序/形式证明 |
| `rva23u64-memory-cache` | Epic 4 / Story 4.6 | RVA23U64 内存与缓存必选要求双核映射 | [`rva23u64-memory-cache-v1.md`](rva23u64-memory-cache-v1.md) | 单元记录已建立；两侧 RTL/配置/测试材料已静态检查，未运行；PMA 区域、取指原子性、完整原子操作与进展边界未验证 |
| `rva23s64-supervisor-traps` | Epic 4 / Story 4.7 | RVA23S64 监督模式与陷阱要求双核映射 | [`rva23s64-supervisor-traps-v1.md`](rva23s64-supervisor-traps-v1.md) | 单元记录已建立；两侧 RTL 与 Heliodor S-mode 测试源码已检查；Veryl CLI 不在 PATH；显式调用本机 latest/nightly 0.22.0 均在 testbench check 阶段失败，本轮测试未启动；ECALL 路由、任意 stvec BASE 与 Sstvala 子案例未验证 |
| `rva23s64-address-translation` | Epic 4 / Story 4.8 | RVA23S64 地址转换与页表要求双核映射 | [`rva23s64-address-translation-v1.md`](rva23s64-address-translation-v1.md) | 单元记录完成；静态源码/测试材料已检查；Heliodor Bare/Sv39 与 ASID 定向目标 2 passed；Svnapot 架构 harness 在 Veryl check 阶段阻断；Kunminghu 未运行；PMA、Svade、完整 PBMT/Svinval/NAPOT 行为未验证 |
| `rva23s64-hypervisor` | Epic 4 / Story 4.9 | RVA23S64 Sha 八个 Hypervisor 组成要求双核映射 | [`rva23s64-hypervisor-v1.md`](rva23s64-hypervisor-v1.md) | 单元记录完成；两侧源码及 Heliodor H 测试材料已检查；`test_arch_hgpf` 在 Veryl testbench check 阶段被现有 `$readmemh`/`dram` 错误阻断；H/Sha 完整行为未验证 |
| `rva23-mandatory-coverage-audit` | Epic 4 / Story 4.10 | RVA23U64/S64 必选项目录完整性审计 | [`rva23-mandatory-coverage-audit-v1.md`](rva23-mandatory-coverage-audit-v1.md) | 单元记录完成；核对 92 行、184 个双核状态格、继承关系与计数；四项 S64 专有要求两侧均未调查，另有 Heliodor Ssstateen 未调查；五个未调查实现侧列入下一阶段规划；不构成符合性结论 |
| `rva23s64-deep-dive-readiness` | Epic 5 / Story 5.1 | RVA23S64 五个深度专题的路径与验证就绪度 | [`rva23s64-deep-dive-readiness-v1.md`](rva23s64-deep-dive-readiness-v1.md) | 就绪矩阵完成；两侧快照 SHA 已核实，活动路径与候选验证入口已登记；本机缺 Mill/Veryl，未运行 CPU 测试；Ssnpm PME/PMM 映射与 Heliodor Ssstateen 仍未决 |
| `rva23s64-zifencei` | Epic 5 / Story 5.2 | Zifencei `FENCE.I` 自修改代码同步双核对照 | [`rva23s64-zifencei-v1.md`](rva23s64-zifencei-v1.md) | 两侧活动 RTL 与 Heliodor 自修改机器码已静态检查；Kunminghu fixture 已保存；Heliodor Veryl check 在 `test_arch_common.veryl:440` 被 `$readmemh`/`dram` 初始赋值错误阻断，仿真未启动；动态行为、非零保留字段及多 hart 发布未验证 |

RVA23 必选项覆盖目录（Epic 4，后续专题更新状态）：[`notes/rva23-coverage.md`](../rva23-coverage.md)。Story 4.2 已填基础整数与标量映射；Story 4.3 已填 F、D、Zfhmin、Zfa；Story 4.4 已填基础 V 的双核静态映射；Story 4.5 已填 Zvfhmin、Zvbb、Zvkt 的有限双核静态映射；Story 4.6 已填 A 与内存/缓存要求；Story 4.7–4.9 已填 S64 trap、地址转换及 Sha 八项的有限映射；Story 4.10 核对目录完整性并汇总各状态；Story 5.2 将 Zifencei 两侧更新为 `studied-unverified`。各单元列出未验证子案例；未调查项在目录中明确标注。
