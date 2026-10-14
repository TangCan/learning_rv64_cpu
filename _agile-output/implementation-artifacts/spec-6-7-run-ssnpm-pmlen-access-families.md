---
title: 'Story 6.7：运行 Ssnpm PMLEN 与访问族对照'
type: 'feature'
created: '2026-10-14'
status: 'done'
baseline_commit: '545630e5c47ce89437b1da3be4567a653f0e9d28'
route: 'dispatch'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-6-context.md'
  - '{project-root}/_agile-output/implementation-artifacts/spec-5-5-compare-ssnpm-pointer-masking.md'
  - '{project-root}/notes/units/rva23s64-ssnpm-v1.md'
  - '{project-root}/notes/units/evidence/cpu-validation-toolchain-v1.yaml'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** 现有 Ssnpm 学习记录主要是静态路径；Story 5.5 的 Heliodor M-mode Supm 尝试在 CPU 启动前被 testbench 阻断，不能证明 S-mode PMLEN=0/7、地址变换或访存族行为。

**Approach：** 在固定 Kunminghu 与 Heliodor 快照上验证可运行的 Ssnpm 代表案例，覆盖控制状态、PMLEN、tagged/canonical 边界地址、适用模式和显式访存族；为每族每侧记录运行、源码检查、阻塞或未验证状态，并更新学习单元及覆盖索引。

**Always：** PMLEN=0 与 7、使能/禁用及地址边界用例须记录控制 CSR、有效模式、指令、预期和观察地址或 trap cause。逐项列出 integer load/store、atomic、FP、compressed、cache management、vector、hypervisor explicit-memory 各族及适用模式；仅将真实运行标成 tested，不从标量案例外推。记录锁定 SHA、输入/构建哈希、命令、工具、CPU-start、退出码、日志和产物。无法运行时写明首个 blocker 与未覆盖范围。

**Never：** 不修改 `sources/` 固定快照；M-mode Supm 或单一访问族不能作为 Ssnpm 证据；不把 harness/build blocker 写成 CPU `run-fail`，不宣称 RVA23 符合性或认证。不得用静态检查推断未观察到的运行结果，也不静默缩减 Epic 6.7 的访问族范围。

## I/O & Edge-Case Matrix

| 场景 | 输入/状态 | 预期/观察 | 失败处理 |
|---|---|---|---|
| PMLEN 配置与边界 | PMLEN=0/7、mask on/off、tagged/canonical VA | 记录有效地址变化或架构 trap、控制 CSR 读回 | 区分 WARL 不支持、CPU 未启动与断言失败 |
| 显式访问族 | S/U 与可用 VS/VU；按族选代表指令 | 每族/模式独立列结果与证据 | 缺入口、构建或观察条件时标具体 blocked/unverified |
| Heliodor guest 路径 | 固定 harness 与 guest 控制 | 仅在实际 selector/变换被观察时标 tested | 不以 henvcfg CSR 可读写替代 guest 地址变换证据 |

</frozen-after-approval>

## Code Map

- `experiments/kunminghu-smoke/run.py`、`fixture.ld`：复用 ELF 构建、锁定 emulator/NEMU、CPU-start 与 trap 分类、manifest 归档；当前没有 Ssnpm topic。参考 `scripts/tests/test_kunminghu_smoke.py` 中临时 manifest/evidence 的 opt-in CPU 检查，避免污染正式 evidence。
- `experiments/heliodor-smoke/run.py`：复用隔离源码副本、输入树摘要和测试结果分类；当前没有 Ssnpm topic。Veryl testbench `$readmemh`/`dram` 阻塞见 Story 5.5 与 E5/E8，不改上游 checkout。
- `sources/xiangshan/src/main/scala/xiangshan/backend/fu/NewCSR/{CSRDefines.scala,NewCSR.scala,HypervisorLevel.scala}` 与 `sources/xiangshan/src/main/scala/xiangshan/cache/mmu/TLB.scala:178–214`：PMLEN 枚举、控制传输、模式 selector 与 VA/PA 变换；固定 Kunminghu SHA 为 `c098f996bf4d301b88693b20315486d31e93bc9d`。
- `sources/heliodor/src/core/{csr,heliodor_core,alu_wrap}.veryl`：M/S/U PMM、scalar/issue AGU 路径；`csr.veryl:794–797`、`heliodor_core.veryl:554–565,5283–5319`、`alu_wrap.veryl:191–203`。VS/VU selector 在 Story 5.5 的有界搜索中未定位；固定 Heliodor SHA 为 `94e9c5821c24a8941c3ddc3b76daddc7124a855a`。
- `notes/units/rva23s64-ssnpm-v1.md` 已含规范边界与两侧访问族初始矩阵；将新增运行 evidence 而不把 `inspected only` 改写成运行通过。同步 `notes/rva23-coverage.md`、`notes/units/index.md` 与 `notes/units/evidence/cpu-validation-toolchain-v1.yaml`。
- `sources/heliodor/test/supm/` 与 `sources/heliodor/tb/test_arch_common.veryl:6055–6080` 仅是 M-mode Supm 测试源；`test_arch_supm` 曾在 `tb/test_arch_common.veryl:440` 的 `$readmemh` semantic check 阻断，不能作为 Ssnpm 验收。

## Tasks & Acceptance

**Execution：**
- [x] `experiments/kunminghu-smoke/`、`experiments/heliodor-smoke/` 与对应 tests -- 为可复现的 Ssnpm 用例增加最小运行入口/检查；验证前后不改固定 source snapshot。
- [x] `notes/units/rva23s64-ssnpm-v1.md` -- 逐 PMLEN、边界、模式和访问族更新输入、预期、观察/阻塞及证据链接。
- [x] `notes/rva23-coverage.md`、`notes/units/index.md`、toolchain manifest -- 同步状态与运行记录，维持 evidence validator 和覆盖计数有效。

**Acceptance Criteria：**
- Given PMLEN=0/7、mask enabled/disabled 与 tagged/canonical boundary cases，when 在目标模式执行，then 每次记录控制 CSR、访存指令、有效地址或 trap cause、命令及可追溯日志；未启动 CPU 的结果为 blocked。
- Given S/U 与目标支持的 VS/VU 模式，when 按 explicit-memory family 逐项验证，then integer load/store、atomic、FP、compressed、cache-management、vector、hypervisor access 均有每核/模式状态；有可运行入口的代表项执行，其他项给出精确 blocker 或未验证依据。
- Given Heliodor 的 guest selector 路径尚未定位或 harness 无法构建，when 故事结项，then 报告实际失败阶段与未覆盖模式；不得将单独 CSR 读写或 M-mode Supm 作为 Ssnpm 通过证据。
- Given 学习单元与运行记录更新，when 运行相关脚本/测试、manifest 与 coverage/link 检查，then 证据链接有效、状态格/计数一致，结论限于已观察案例。

## Implementation Notes

- The PMLEN0/7 × canonical/tagged runtime matrix is implemented on both fixed cores. Kunminghu uses a U-mode fixture with `ld/sd/lr.d/sc.d/amoadd.d` assertions on canonical cases; tagged PMLEN7 reaches `ld/sd`, then LR.D faults with cause 5 at `mepc=0x80000088`, `mtval=0xfe000000800000e0`, after which the pinned NEMU difftest aborts on privilege state mismatch. Tagged SC/AMO remain unobserved. The PMLEN0 tagged fixture now asserts cause, `mepc`, and raw `mtval`; the bit56-set case raises cause 5 at the load, with the simulator logging the raw address. Its DUT/reference attribution remains unresolved.
- Heliodor's U-mode fixtures set/read `senvcfg.PMM` in M, `mret` to U and exercise `sd/ld`. PMLEN0 canonical, PMLEN7 canonical/tagged, and bit56-set cases reach pass markers; every high-address success is limited by the testbench DRAM's low-bit alias. The corrected PMLEN0 tagged fixture requires an access fault at the tagged load with matching `mtval`; instead the high-address load succeeds through the alias and the fixture reports `tohost=0x12` / `run-fail`. The earlier E15 pass marker came from a fixture that incorrectly accepted this unexpected success and is not valid Ssnpm evidence.
- Bounded fixed-source searches found non-Ssnpm entry points on Heliodor for FP (`test/riscv-arch-test/custom/fp_smoke.S`), CMO (`test/cmo/cmo_test.S`), vector (`test/vmem/vmem_test.S`), and HLV/HSV (`test/hlv/hlv_test.S`). These fixtures do not set Ssnpm PMM/enter U or exercise the requested Ssnpm selector; their existence is not treated as Ssnpm evidence. Kunminghu decode/LSU paths exist for compressed, FP, CMO, vector, and hypervisor access; no Ssnpm-specific entries were located under `sources/xiangshan/src/test`. The source/test entry findings and per-family evidence limits are recorded in `notes/units/rva23s64-ssnpm-v1.md`.
- Remaining acceptance gaps are explicit: neither core has U-mode FP/compressed/CMO/vector tagged runtime evidence; Heliodor VS/VU/HUPMM selector and runtime remain unlocated/unverified; Kunminghu VS/VU source selector is not runtime-tested; Kunminghu tagged atomic path fails before SC/AMO. The mode-by-family matrix records each as unverified/not-applicable with the inspected entry and exact evidence limit. MXR/MPRV/SPVP remain untested. Coverage remains `studied-unverified`, not feature-complete or conformance evidence.
- Historical Heliodor `working_directory` fields retain their original `/tmp/...` values. The validator no longer requires ephemeral absolute paths to exist after execution; all run logs and inputs remain hash-checked in evidence archives. Empty `/tmp` placeholders were removed.

## Spec Change Log

## Review Triage Log

| Finding | Verdict | Evidence and route |
|---|---|---|
| Blind Hunter: Heliodor PMLEN0 tagged successful load can report pass. | medium | `build_heliodor_fixtures.py` jumps to `good_trap` after any successful load, while only an actual cause-5 trap should pass; patch fixture and regression assertion. |
| Blind Hunter: Heliodor PMLEN7 tagged result cannot distinguish masked from raw address under low-bit DRAM aliasing. | medium | Harness data indexing discards high address bits and no effective-address telemetry exists; qualify the result as harness-limited and adjust fixture/evidence claims. |
| Blind Hunter: Heliodor PMLEN0 checks only `mcause`. | medium | Its handler accepts any cause-5 trap without checking `mepc`/`mtval`; assert the fault came from the tagged load. |
| Blind Hunter: no bit-56 PMLEN7 boundary input is exercised. | medium | The current tag literal leaves VA bit 56 clear; add a focused bit-56-set boundary probe and record its limit. |
| Blind Hunter: Kunminghu PMLEN0 checks only `mcause`. | medium | `ssnpm.S` accepts any cause-5 trap without checking the faulting instruction/address; assert `mepc`/`mtval`. |
| Blind Hunter: family results are not fully explicit per applicable mode. | medium | The table lists families/core results but several cells do not state U/VS/VU/HLV mode disposition individually; add per-mode statuses, including unverified/not-applicable. |
| Blind Hunter: Heliodor archive omits the referenced linker script. | medium | Builder uses `experiments/rva23s64-zifencei/fixture.ld`, but run archive only copies the builder and assembly; archive/hash the linker input. |
| Blind Hunter: manifest omits nested gcc/objcopy build commands. | medium | The recorded command invokes only the builder, whose exact compiler and objcopy argument vectors are absent from run metadata; record them. |
| Blind Hunter: test suite does not guard against a success-path bypass in Ssnpm fixtures. | medium | Existing checks inspect source strings/fabricated marker output rather than expected-case pass/fail behavior; add focused assertions for the generated expected-fault fixture and runner outcome. |
| Blind Hunter: PMLEN0 tagged fixture can pass after successful load. | medium | Confirmed in builder's `expect_fault` branch; duplicate root cause with the first finding, retain this row and fix once. |
| Edge Case Hunter: successful Heliodor PMLEN0 tagged load reaches pass marker. | medium | Confirmed `assembly()` emits `j good_trap` after `ld`; same root cause as Blind Hunter rows 1 and 10, fix once. |
| Verification Gap: fixture tests do not ensure bad Ssnpm checks fail. | medium | Current tests assert source text and fabricated output only; same testability gap as Blind Hunter row 9, add focused regression assertions. |

## Verification

**Commands：**
- `python3 scripts/run_cpu_smoke.py validate --manifest notes/units/evidence/cpu-validation-toolchain-v1.yaml` -- manifest 与所有输入/输出 hashes 有效。
- `python3 scripts/check_rva23_coverage.py`、`python3 scripts/check_doc_links.py` -- coverage 与本地文档链接有效。
- `PATH=/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH uv run --no-cache pytest -q scripts/tests` -- 156 passed, 1 skipped; Heliodor/Kunminghu CPU fixtures also ran separately and are recorded in the manifest.
- `git diff --check` -- 无空白错误。

**Manual checks：** 逐项核对访问族矩阵与 immutable run records；不得把源码路径或 harness pass 当作 CPU 观察。
