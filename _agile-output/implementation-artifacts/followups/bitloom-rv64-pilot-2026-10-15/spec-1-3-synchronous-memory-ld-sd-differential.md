---
title: 'Story 1.3 — 同步访存及 RV64I LD/SD 对照'
type: feature
created: '2026-10-16'
status: done
route: dispatch
review_loop_iteration: 0
baseline_commit: 85f462b8ee98a4c78c0ed255604e14b98086c8a2
context:
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/prd.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/ARCHITECTURE-SPINE.md
  - /nvme_data1/richard/learning_rv64_cpu/_agile-output/planning-artifacts/followups/bitloom-rv64-pilot-2026-10-15/epics.md
---

## Intent

实现自然对齐的 RV64I `LD`/`SD`，使用 Bitloom 1.2.4 同步读存储器，并对固定程序的可观察架构结果进行验证。记录 Kunminghu 与 Heliodor 固定参考流程各自的实际结果；若当前流程不能执行相同案例或环境阻塞，准确保存尝试、命令和未验证原因。

## Boundaries & Constraints

**Always:** 数据内存以 64 位字为单位，地址为字节地址且只覆盖自然对齐访问；确定初态、读延迟、读写碰撞约定和不支持行为。按架构效果比较，不对齐不同核心的周期数。所有参考结论须由真实运行日志支撑。

**Never:** 不实现字节/半字访问、非对齐访问、异常、缓存、地址转换或超出故事要求的微架构；不把静态代码/测试入口检查写成运行通过；不因单侧成功推断双侧等价。

## Code Map

- `experiments/bitloom-rv64-pilot/src/lib.rs` -- Story 1.2 IF/ID、ID/EX、EX/WB 数据通路、译码与寄存器写回；扩展 load/store 与同步数据存储器。
- `experiments/bitloom-rv64-pilot/tests/smoke.rs` -- Bitloom `Sim` 的确定性程序构造器、逐周期指令源与寄存器观察；扩展为退休 PC、load/store 和内存回读断言。
- `experiments/bitloom-rv64-pilot/README.md` -- 固定依赖、命令、指令范围和仿真限制。
- `experiments/kunminghu-smoke/run.py`、`experiments/heliodor-smoke/run.py` -- 固定参考工具链入口。当前 Kunminghu `--input` 限定 Zifencei fixture；Heliodor 默认仅选 RV64UI add；两者都不能直接运行共用自定义夹具。
- `notes/units/load-v1.md`、`notes/source-environment-baseline.md` -- LD 架构语义、参考源码路径及固定快照限制；仅作为上下文，不替代本故事运行证据。
- `notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- 两侧 runner 运行记录入口；仅由 runner 写入。

## Tasks & Acceptance

**Execution:**
- [x] `experiments/bitloom-rv64-pilot/src/lib.rs` -- 增加 LD/SD 译码、有效地址、自然对齐 64 位读写、同步内存读数据对齐流水线，并暴露可验证的退休事件。
- [x] `experiments/bitloom-rv64-pilot/tests/smoke.rs` -- 固定初始内存和输入程序；检查初始 LD、SD 后 LD 回读、退休 PC/寄存器/内存结果及不支持情况。
- [x] `experiments/bitloom-rv64-pilot/README.md` -- 说明同步读一拍延迟、内存大小/地址映射、无前递限制和运行方式。
- [x] `experiments/kunminghu-smoke/run.py`、`experiments/heliodor-smoke/run.py` 或独立的 Story 夹具运行入口 -- 分别尝试固定参考流程，保存实际命令、输入哈希、配置、日志、结果或明确阻塞。
- [x] `notes/units/evidence/bitloom-rv64-pilot/` -- 保存 Story 输入、Bitloom 输出与两侧参考运行证据/阻塞记录；更新本 spec 的实施和审查记录及 sprint 状态。

**Acceptance Criteria:**
- Given 固定的 64 位内存初态和自然对齐访问，when 程序执行 LD/SD，then 初始值可加载且 SD 后的 LD 返回新值，PC/寄存器/内存效果可由模拟结果观察。
- Given 同步读取地址在时钟沿采样，when 一个 LD 经过访存级，then 读数据和对应 PC/rd 在写回与退休观察口上保持对应，不错配相邻指令。
- Given 固定 RV64I 程序和初态，when 尝试运行 Kunminghu 与 Heliodor 各自锁定流程，then 分别记录实际架构结果，或记录运行命令、阻塞阶段与未验证状态。
- Given 两边结果均可获得，when 比较案例，then 仅比较架构退休 PC、寄存器和内存效果，不要求周期级相同。

## Implementation Notes

- Bitloom API 已核实：`declare_sync_read_mem_with_init`、`assign_mem_write_en`、`assign_reg_d_mem_read`。锁定版本仿真器在模拟器内有一拍 pending read；同址读写按 read-before-write 处理。集成流水线时必须给读响应配套延迟地址/rd/pc 元数据。
- Bitloom 仿真器公开 `Sim` 接口没有内存检查器；通过 store 后重新 load 同地址验证最终内存效果，避免仅依赖实现内部状态。
- 当前通用参考 runners 的输入入口不支持该自定义程序。实现前需判断扩展 runner 的最小安全边界；每侧失败必须留下独立证据。

## Spec Change Log

- 2026-10-16: 记录实现范围、固定访存案例、两侧 runner 接口阻塞及实际验证结果。

## Review Triage Log

2026-10-16 三位评审的发现逐条处置；相同问题保留为独立记录：

| Reviewer finding | Verdict | Evidence / disposition |
|---|---|---|
| Blind Hunter: 单一退休口可能被 load/普通指令重叠覆盖 | Fixed | 有效 LD 和其两级响应期间暂停 IF/ID，避免多个提交同周期；相邻 LD 后普通写回用例断言两个 PC 均退休。 |
| Blind Hunter: 同周期普通写回与 LD 写回冲突 | Fixed | 同上；相邻 LD、独立 ADDI 验证 load 数据和年轻写回分别可见。 |
| Blind Hunter: 缺少越界 LD 覆盖 | Fixed | `signed_store_offset_accepts_last_word_and_rejects_first_word_past_memory` 验证 0x40 LD 不写寄存器。 |
| Blind Hunter: 非法 SD 未检查内存未变化 | Fixed | 同用例在越界 SD 后读取 mem[0] 并核对初始值。 |
| Blind Hunter: 未覆盖末尾有效地址及首个越界地址 | Fixed | 覆盖 0x38 存取成功、0x40 访存不支持。 |
| Blind Hunter: 未覆盖负 S immediate | Fixed | 以 x1=64 执行 `SD/LD ...,-8(x1)`，实际有效地址 0x38。 |
| Blind Hunter: 未覆盖非法 LD/SD funct3 | Fixed | 非标准 funct3 的 LD、SD 均加入不支持编码用例。 |
| Blind Hunter: 未覆盖非零 base 加负 S immediate | Fixed | x1=64、立即数 -8 的用例直接验证有效地址 56。 |
| Blind Hunter: program.S 与测试硬编码程序可能不一致 | False positive | 两者指令顺序及地址一致：ADDI@0、LD@4、NOP@8/12/16/20、SD@24、NOP@28/32/36、LD@40、NOP@44/48。 |
| Blind Hunter: 未运行生成 Verilog 的 HDL 仿真 | Deferred | 本故事执行 Bitloom 仿真与 Icarus parse/elaboration；HDL runtime 仿真留给 Story 1.5 导出决策，当前未声称通过。 |
| Verification Gap: 缺少越界 LD 覆盖 | Fixed | 与 Blind Hunter 同项，新增用例确认 x5 保持零。 |
| Verification Gap: 非法 SD 后内存未确认 | Fixed | 与 Blind Hunter 同项，LD 回读 mem[0] 等于初始字。 |
| Edge Case Hunter: load 周边提交 PC 可能丢失 | Fixed | LD 停顿保证单提交口按程序顺序输出；专用测试同时检查 LD@20 与 ADDI@24。 |
| Edge Case Hunter: 同 rd 的年轻写回可能被较老 load 覆盖 | Fixed | 停顿期间不允许年轻指令进入 EX；两级读响应完成后才继续。 |

Kunminghu 与 Heliodor 固定流程仍分别在参数校验阶段拒绝该自定义案例，没有启动 CPU；故跨核差分状态保持未验证。

## Design Notes

同步读取以采样地址为起点延迟一拍；实现需将访存指令的 PC、目的寄存器和写使能与响应同步延迟。SD 后的 LD 回读同时检查真实写入结果和同程序的读写顺序。

## Verification

**Commands:**
- `cargo fmt --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml -- --check` -- exit 0。
- `cargo test --manifest-path experiments/bitloom-rv64-pilot/Cargo.toml` -- 9 个测试通过，包括 LD/SD 回读、相邻 load 后退休顺序、边界/负偏移及非法访存检查。
- `CARGO_TARGET_DIR=target/bitloom-rv64-pilot PATH="$PWD/target/bitloom-cli/bin:$PATH" cargo bitloom build --package bitloom_rv64_pilot --manifest-dir experiments/bitloom-rv64-pilot --out-dir "$PWD/target/bitloom-out"` -- exit 0；`iverilog -g2012 -tnull target/bitloom-out/BitloomRv64Pilot.v` -- exit 0，仅证明生成 RTL 可解析/展开。
- Kunminghu: `python3 experiments/kunminghu-smoke/run.py --topic zifencei --input notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/program.S --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml --evidence-dir notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/kunminghu` -- exit 2，runner 限定四个 Story 6.4 源文件，CPU 未启动。
- Heliodor: `python3 experiments/heliodor-smoke/run.py --topic zifencei --case story-1-3 --archive-dir notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/heliodor` -- exit 2，runner 仅接受 `standard/funct12/rs1/rd`，CPU 未启动。
- 输入、日志、工具版本、生成 RTL 和哈希归档于 `notes/units/evidence/bitloom-rv64-pilot/story-1-3-2026-10-16/README.md`。参考差分仍未验证，runner 拒绝发生在参数校验阶段。
