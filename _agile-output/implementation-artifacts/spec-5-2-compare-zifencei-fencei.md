---
title: 'Story 5.2：比较 Zifencei 与 FENCE.I'
type: 'feature'
created: '2026-10-13'
status: 'done'
baseline_commit: '990ee743d8db2c6d11a56ce87d53be924d68d483'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-context.md'
  - '{project-root}/notes/units/rva23s64-deep-dive-readiness-v1.md'
  - '{project-root}/sources.lock'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** RVA23S64 要求 Zifencei，但译码命中或缓存 flush 信号本身不足以证明本地 hart 上先前代码写入会被后续取指观察，也不能推导多 hart 远程同步。

**Approach：** 基于锁定快照追踪 Kunminghu V2 与 Heliodor 的 `FENCE.I` 从译码、排序/失效到重取指路径，并用可观察的自修改代码案例记录测试输入、结果和边界。

**Always：** 采用 Zifencei v2.0 和 RVA23S64 v1.0 的要求键；区分静态 RTL、测试源码/机器码检查和实际仿真；报告本地 hart 保证，不将 `FENCE.I` 描述为远端 hart 广播；记录测试覆盖的 `funct12`、`rs1`、`rd` 忽略字段及其未覆盖情况。

**Never：** 不修改 `sources/` 上游 checkout；不把源码或 riscv-tests 的自述当作本次运行通过；不宣称多 hart 发布完成或 RVA23 认证；不因缺少工具而静默跳过运行条件，若不可运行则记录具体阻塞并标为未验证。

</frozen-after-approval>

## Code Map

- `sources.lock`：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`、Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`；开始前复核 checkout HEAD。
- `notes/rva23-coverage.md`：精确要求 `RVA23S64/v1.0/§3.1.2.2/Zifencei`；当前两侧 `not-studied`，完成后应更新为证据支持的状态而非 `run-pass`（除非实际运行）。
- Kunminghu：`DecodeUnit.scala:228-231` 把 `FENCE_I` 派发到 `FuType.fence/FenceOpType.fencei`；`FuConfig.scala:350-360` 标记 fence 不流水并 flush pipe；`Fence.scala:47-87` 请求 store buffer flush、等待 `sbEmpty` 后进入 fencei 状态；`XSCore.scala:135-139` 接到 frontend；`Frontend.scala:224` 注册传递到 I-cache；`ICache.scala:379-386,634-636` 清所有 valid；`ICacheMissUnit.scala:140-161,315,394-399` 处理在途 miss。限定搜索 `src/test/scala` 未发现定向 `fencei` 用例；源码路径不是仿真结论。
- Heliodor：`decoder.veryl:630-635,1319` 译码；`heliodor_core.veryl:2488`、`rob.veryl:636,1199` 保存并提交；核心 `:4035-4050,4609-4614` 在提交和先前 store drain 后产生 pulse；`:1931-1937` 接入 I-cache；`icache.veryl:508-545` 清 valid 并抑制被打断的 fill；`:5134-5145,5815` redirect 到后继 PC 并重取。`tb/test_arch_common.veryl:1065-1089` 的 `test_arch_rv64ui_fence_i` 载入现存 `test/riscv-arch-test/build/rv64ui/fence_i.hex`；静态反汇编可见两次写入、`fence.i`、间接执行及 444/777 检查，reserved 字段均为零；这不是运行通过证据。
- Heliodor 候选命令：在 `sources/heliodor` 执行 `veryl test --test test_arch_rv64ui_fence_i`；需 Veryl CLI 与 Verilator，现有 hex 已在锁定 checkout。Veryl 当前不在 PATH。重建 hex 才需 riscv-tests upstream/env、`riscv64-unknown-elf-gcc`、objcopy 和 bin2hex。Kunminghu 无同名定向测试；可运行性以可用 harness/工具实测为准。
- 规范行为依据：[Zifencei v2.0](https://docs.riscv.org/reference/isa/unpriv/zifencei.html)；CTP `A.10.2` 要求自修改代码后执行 `fence.i` 并执行新指令，且覆盖非零保留字段，但计划表不等于本地测试结果。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-zifencei-v1.md` — 新建单元，写规范契约、本地/远端边界、双核活动路径、自修改代码测试观察、reserved-field 覆盖、自检、证据与未决项。
- [x] `notes/rva23-coverage.md` — 将 Zifencei 两侧范围更新为本故事实际达到的证据状态，并链接单元；不得把未运行测试写为通过。
- [x] `notes/units/index.md` — 登记 Zifencei 单元和对应动态验证/阻塞状态。
- [x] `experiments/rva23s64-zifencei/` — Kunminghu 没有可复用的定向自修改代码 fixture，因此保存了本地测试源和运行说明，并完成交叉汇编/反汇编检查。Heliodor Veryl 从 PATH 外的本机安装位置运行；testbench check 因既存 `$readmemh`/`dram` 初始化错误退出 1，未启动仿真。单元记录精确命令、配置/输入现状、阻塞原因和遗留验证状态；未安装工具、未改上游源码。

**Acceptance Criteria：**
- Given Zifencei v2.0 与 RVA23S64 要求，when 描述契约，then 明确本 hart 后续取指可见先前本 hart 可见的数据写入，且远端 hart 需要独立协调。
- Given 两个锁定实现，when 追踪 `FENCE.I`，then 记录译码、串行化/存储排序、I-cache 或取指状态失效、重取路径；无法确认的环节标为未验证。
- Given Heliodor `test_arch_rv64ui_fence_i` 和 Kunminghu 对照案例，when 工具/harness 允许运行，then 执行有界自修改代码测试并记录精确命令、配置、写入指令、`FENCE.I`、新指令结果、观察值和日志/产物路径；否则记录具体 blocker，不标运行通过。
- Given 所选编码和测试，when 检查 `funct12`、`rs1`、`rd`，then 记录非零保留字段是否有测试覆盖；未覆盖则明确为 unverified。
- Given 双核比较完成，when 学习者复核，then 能从证据解释本地 hart 保证、实现差异与未覆盖的多 hart 发布边界。

## Implementation Notes

- Kunminghu fixture 显式使用 `.option norvc`，避免压缩指令造成被覆写函数布局变化。用 `riscv64-unknown-elf-gcc -march=rv64imac_zifencei -mabi=lp64 -nostdlib -c ...` 汇编，并用 `riscv64-unknown-elf-objdump -dr` 检查出入指令；对象只写入 `/tmp`，不代表 CPU 运行。
- Heliodor 的本机 `veryl` 不在 PATH，但在 `/nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl` 找到 0.22.0。定向命令在 testbench check 阶段于 `tb/test_arch_common.veryl:440` 因 `invalid_initial_assign` 退出 1；核心仿真未启动，也没有产生运行日志或 pass/fail 观察。

## Spec Change Log

## Review Triage Log

| Finding | Severity | Evidence / disposition |
|---|---|---|
| Self-modifying fixture did not prove stale-to-new instruction transition | high | Corrected fixture to execute and check old instruction result `1`, patch the instruction, execute `FENCE.I`, then check new result `42`; assembled object confirms the intended sequence. CPU execution remains deferred. |
| Kunminghu fixture lacked a runnable harness and image-loading route | high | README now documents the supported generic emulator build command and explicitly records missing Mill, linker/load/entry and `tohost` harness integration; runtime remains blocked and unverified. |
| Heliodor test input provenance and identity were unclear | medium | Recorded tracked input path and SHA-256; documented that generating source/provenance is absent from the locked checkout. |
| Reserved-field evidence was missing | medium | Recorded the checked `FENCE.I` encodings and offsets in Heliodor input and Kunminghu fixture; all checked reserved fields are zero, nonzero coverage remains unverified. |
| Kunminghu in-flight miss behavior was overclaimed | medium | Narrowed statement to statically visible request/wakeup/write suppression wiring; dynamic miss/fill race convergence remains unverified. |
| Test constants could be mistaken for observed CPU values | medium | Labeled Heliodor `444/777` and Kunminghu `1/42/0x600d` as encoded expectations/check values, with no CPU observation claimed. |
| Coverage status lacked rationale | low | Added explanation that Kunminghu status derives from static path inspection and fixture assembly only; neither implementation has a runtime pass for this story. |

## Design Notes

Heliodor 的预构建 `fence_i.hex` 可以静态反汇编核对它是否包含实际自修改流程；这只确认输入适合该案例，不替代执行。源仓库缺少 riscv-tests 上游源码时，不应从文件名推断具体子案例。

## Verification

**Commands：**
- `git -C sources/xiangshan rev-parse HEAD`、`git -C sources/heliodor rev-parse HEAD` — 与 `sources.lock` 一致。
- `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_rv64ui_fence_i` — expected: 记录真实退出状态；本次退出 1，失败发生于 Veryl testbench check，测试体未运行。
- `riscv64-unknown-elf-gcc -march=rv64imac_zifencei -mabi=lp64 -nostdlib -c experiments/rva23s64-zifencei/kunminghu-self-modifying.S -o /tmp/learning-rv64-zifencei-fixture.o` 和 `riscv64-unknown-elf-objdump -dr /tmp/learning-rv64-zifencei-fixture.o` — expected: 对象中保留 32-bit patched 函数、写入新指令后执行 `fence.i`；本次通过静态检查，不是 CPU 执行。
- `git diff --check` — 文档和索引无空白错误。

**Manual checks：**
- 从 RTL 逐段核验顺序/提交、缓存失效和取指 redirect 接线；机器码检查只记静态证据。
- 确认单元、覆盖目录、索引的状态一致，并将未运行与 reserved-field 未覆盖清楚标出。
