# 访存路径追踪矩阵

每个阶段在 Kunminghu 与 Heliodor 栏分别记录来源、证据类型和验证状态。证据类型与验证状态是独立字段；实现阶段可以不同，不以相同术语制造虚假的一一对应。

| 观察点 | Kunminghu V2 | Heliodor | 学习记录要求 |
| --- | --- | --- | --- |
| 指令入口 | 已有 LD 学习记录；SD 入口待故事整理 | 有 RV64UI LD/SD 测试入口源码 | 固定 `sources.lock`；测试存在不等于运行通过 |
| 译码与派发 | LoadUnit/StoreUnit 路径；按选定普通标量操作追踪 | decoder / AGU 路径 | 记录操作类型、宽度、立即数/数据与控制信号 |
| 执行与地址生成 | LD 已记录；StoreUnit S0 形成 `rs1 + imm` | LD 已记录；store 地址/数据由 core/ROB 路径保留 | 来源分别见 `load-v1.md` 与 `feasibility.md`；内部阶段不强行对应 |
| 地址转换与保护 | LD/fault 路径已记录；成功 SD 的配置和保护条件尚未运行确认 | LD/fault 路径已记录；成功 SD bare DRAM 路径条件需按源码确认 | 分离源码条件与动态配置观察 |
| 数据访问与响应 | LD 已记录；SD 从 StoreQueue commit/drain 到实际写口仍需故事补全 | LD 已记录；SD 有 commit-store fast/slow 分支 | StoreUnit 的 tag probe 不是实际数据写入；不把 commit 自动等同缓存/内存可见 |
| 提交与架构状态 | LD retirement 静态路径已记录；SD commit 后进入 StoreQueue | LD retirement 静态路径已记录；SD 写入由 ROB head commit 驱动 | 本阶段不预设动态运行 |
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
