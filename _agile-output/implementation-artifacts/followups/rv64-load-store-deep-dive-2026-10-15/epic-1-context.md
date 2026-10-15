# Epic 1 Context: 完成可回顾、可复查的双核访存学习阶段

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

建立一套可按时间回顾、又能按主题复习的双核 RV64 访存学习记录：用 Kunminghu V2 与 Heliodor 的固定源码快照，对照普通 `LD`、DRAM `SD` 和 Sv39 非规范地址 load page fault 的实现路径。技术结论、探索日志与原始运行产物各有归属并互相链接；每项主张都标明证据及其验证边界，使未知和未运行部分保持明确，而不影响静态源码路径学习目标。

## Stories

- Story 1.1: 复核并记录双核 `LD` 路径
- Story 1.2: 追踪普通 DRAM `SD` 的提交与写入边界
- Story 1.3: 追踪 Sv39 非规范地址 `LD` fault
- Story 1.4: 核验三类案例的证据与快照
- Story 1.5: 综合双核发现并完成学习日志导航

## Requirements & Constraints

- 覆盖三类案例在两个实现上的路径；比较同一架构场景，但按各自微架构术语描述，不强行对齐内部阶段。LD 从译码/发射到写回和退休；SD 到证据支持的写入接受终点；fault 到证据支持的 trap 状态更新。六条路径在追踪矩阵中各占一行，缺失阶段或证据保留为 `unknown`、`blocked` 或 `unverified`。
- 每项实现主张使用锁定快照及 `sources.lock` 中稳定 ID 和完整 SHA。证据类型与验证状态分别记录；比较缺一侧则标为 `partial`，不能据此声称两侧等价。实际运行结论必须能追溯输入、命令、配置、输出和产物位置；检查过测试源码不代表执行过测试。
- 学习单元是技术结论的唯一正式归属，已发布版本不可原地修改；修订生成新版本并更新 `notes/units/index.md`。日期日志记录问题、查阅来源/动作、发现及状态、相关链接和下一步，不复制大段结论，也不补造无法还原的历史。
- 使用中文 Markdown、现有 Git 与仓库链接；无需部署博客或增加生成服务。不得修改上游 RTL，不扩大为 RVA23 符合性证明；动态运行不是本阶段必需门槛。Follow-up 产物与已完成的 RVA23 阶段保持隔离。

## Technical Decisions

- 固定比较对象为 `sources.lock` 中的 Kunminghu V2、Heliodor 快照；快照变化时记录新基线并重核受影响主张。
- LD 共用场景为 RV64I、自然 8 字节对齐、M-mode Bare、无异常、DCache hit、无更老重叠 store。无法从来源或配置确认的条件标作 assumption。
- SD 使用自然对齐的普通 DRAM 目标；在解释路径前，先在故事与决策日志中确定两侧共用 tuple 及来源可支持的写入接受终点。明确区分指令提交、缓存/缓冲接受和更低层可见性；不能由 commit 单独推断 DRAM 可见或持久。
- Fault 共用场景为 S-mode、V=0、`satp.MODE=Sv39`、普通 RV64I `LD`、VA `0x0000008000000000`、`medeleg[13]=0`。追踪 cause 13、故障 PC/`mepc`、`mtval`、M-mode trap target 和有来源支持的状态更新；实现选择不明时保留未知。
- `notes/units/` 保存版本化技术单元，`learning-journal/` 保存时间线，原始运行产物位于 `notes/units/evidence/`，追踪矩阵连接两侧案例与证据。遵循现有学习记录约定中的证据类型/状态词汇。

## Cross-Story Dependencies

- Story 1.1–1.3 产出三类路径、技术单元及日志，并更新追踪矩阵对应行；Story 1.2 必须先完成 SD tuple/终点决策。
- Story 1.4 审核前述六行路径、证据标识和快照 SHA；Story 1.5 综合前三类发现并检查索引/README 导航及已发布链接。Story 1.5 对历史只做可由留存材料支持的回顾。
