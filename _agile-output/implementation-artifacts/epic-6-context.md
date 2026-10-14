# Epic 6 Context: 验证 RVA23S64 五专题的 CPU 行为

<!-- Compiled from planning artifacts. Edit freely. Regenerate with compile-epic-context if planning docs change. -->

## Goal

在固定 Kunminghu 与 Heliodor 快照上建立可重复、可观察的 CPU 仿真入口，并用代表性架构案例验证 RVA23S64 五个专题。记录必须能区分工具/构建阻塞、测试台阻塞和 CPU 行为结果，以实际运行证据支持结论；有限案例不构成整个 RVA23 Profile 的符合性声明或认证。

## Stories

- Story 6.1: 固定 CPU 验证工具链与结果归档
- Story 6.2: 建立 Kunminghu fixture 加载与模拟器入口
- Story 6.3: 建立 Heliodor arch harness 隔离运行入口
- Story 6.4: 运行 Zifencei 自修改代码对照
- Story 6.5: 运行 Sstc S/VS comparator 与陷阱对照
- Story 6.6: 运行 Sscofpmf 硬件计数器溢出与过滤对照
- Story 6.7: 运行 Ssnpm PMLEN 与访问族对照
- Story 6.8: 运行 Ssstateen 八 CSR 与层级访问门对照

## Requirements & Constraints

- 保持两个已锁定源码快照及其 gitlink 版本不变；将生成物、临时 harness 变换和运行输出放在忽略目录或临时副本中。
- 每次运行记录源码 revision、fixture SHA-256、配置/hart 数、命令与工作目录、工具版本、退出码、CPU 是否启动、完整日志路径与哈希及生成产物路径。
- 任何 CPU 启动前的失败标记为 `blocked`，注明首个失败阶段及工具；只有 CPU 已启动且观察到断言不匹配才标记 `run-fail`。
- 专题结论限定于已运行的输入、模式、配置和 hart 数；未运行的访问族、模式或工具能力应明确列为阻塞或未覆盖，不能由静态源码推断为运行结果。
- Story 6.1 的工具链、fixture 输入和归档约定是专题故事的依赖门。Kunminghu 专题需等待 Story 6.2 的可加载、可观察入口；Heliodor 专题需等待 Story 6.3 的普通 arch harness 入口，并逐专题评估隔离变换是否影响语义。

## Technical Decisions

- 以 `sources.lock` 中的 Kunminghu、Heliodor SHA 为实验基线；不为通过案例修改上游快照。
- 运行记录统一包含 `snapshot_sha`、`input_sha256`、`configuration`、`command`、`working_directory`、`tools`、`exit_code`、`cpu_started`、`result`、`output`、`output_sha256` 与 `artifacts`。
- 工具版本及本机依赖是结果的一部分。若工具不兼容，先记录精确版本和失败点，再调整隔离环境；不可把生成 RTL 或编译推进当作 simulator 已启动。
- Heliodor 的 Veryl 兼容 workaround 必须在新临时副本上进行，只排除触发问题的未实例化 debug harness，并记录局部 lint allow；不能把该变换默认视为对所有专题语义透明。
- Zifencei、Sstc、Sscofpmf、Ssnpm 和 Ssstateen 分别用可控制输入及可观测架构结果验证；按专题保存期望值、观察值、输入哈希和日志，模型或软件写入状态不能替代硬件行为证据。

## Cross-Story Dependencies

- 6.1 是所有专题运行的前置门；先固定可复现工具链、输入约定和结果归档格式。
- 6.2 与 6.3 分别建立 Kunminghu 和 Heliodor 的运行入口；每个专题只在对应入口已证明能加载输入并观察 CPU 进展后开始。
- 6.4–6.8 共用 6.1 的记录约定，且分别依赖所测核心对应的 6.2/6.3 入口。Heliodor 专题需附带其隔离 harness 变换适用性说明。
