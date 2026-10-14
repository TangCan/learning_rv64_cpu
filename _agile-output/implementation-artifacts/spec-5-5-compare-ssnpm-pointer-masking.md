---
title: 'Story 5.5：比较 Ssnpm 指针屏蔽'
type: 'feature'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'c72b1686d352fe39969bae5e9d5968c4f5a89b48'
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem：** RVA23S64 要求 Ssnpm 至少能选择 PMLEN=0 与 PMLEN=7，但 profile 文本、架构字段名与两核实现路径并不完全一致；旧记录尚未验证 S-mode 控制、H/VS 路径或访问族覆盖。

**Approach：** 以锁定的 Kunminghu V2 和 Heliodor 快照，对照官方 profile 与指针屏蔽规范，追踪 PMM 配置、有效地址变换和显式访存路径，并运行可执行的代表性案例。逐项记录不支持、未运行或尚未解决的边界，不据此声称符合性。

**Always：** 记录 profile 的 `PME` 拼写及其版本/源码依据，并与架构规范和 RTL 的 `PMM` 字段名分开；列出适用的 PMLEN、M/S/U/VS/VU 控制和地址访问族；区分源码、测试材料与实际运行观察；每项结论可追溯到两侧证据。

**Never：** 不修改 `sources/` 上游 checkout；不把 U64 Supm/M-mode 结果当作 S64 Ssnpm 验证；不把一次 load 结果外推到其他访问族或虚拟化模式；不把学习记录表述为认证或完整符合性结论。

</frozen-after-approval>

## Code Map

- 锁定 SHA：Kunminghu `c098f996bf4d301b88693b20315486d31e93bc9d`；Heliodor `94e9c5821c24a8941c3ddc3b76daddc7124a855a`（实施时核实）。Profile v1.0 §3.1.2.2 发布文本写 PME；Zpm v1.0.0 §§17.1.2.4–.7 定义 PMM，RV64 编码 `00`=PMLEN0、`10`=7、`11`=16、`01` 保留。profile PDF 与当前 profile 源文有拼写差异，记录版本/引用。
- Kunminghu：活动 CSR 经 `backend/fu/wrapper/CSR.scala` 到 `NewCSR`；`NewCSR/CSRBundles.scala:67-74,CSRDefines.scala:194-200,NewCSR.scala:1469-1473,HypervisorLevel.scala:243` 定义、传递 PMM/HUPMM；`cache/mmu/TLB.scala:178-214` 选模式并屏蔽地址。Load/store/atomic 入口见 `mem/pipeline/{LoadUnit.scala,StoreUnit.scala,AtomicsUnit.scala}`。有界测试搜索无 Ssnpm 专题用例。
- Heliodor：`core/csr.veryl:129-134,794-797` 取 M/S/U PMM；`heliodor_core.veryl:554-565` 选模式；`alu_wrap.veryl:191-203` 与 `heliodor_core.veryl:5283-5290,5312-5319` 屏蔽标量地址。向量地址 `vector_unit.veryl:1976-1985,2569` 未见 PMM 变换，需检查实际路径。现有 `test/supm/supm_test.S` / `tb/test_arch_common.veryl:6055-6080` 只查 M-mode PMLEN16/7 LR/SC alias 与禁用基线。此前 Veryl 0.22.0 被公共 testbench `dram` `$readmemh` `invalid_initial_assign` 阻断；本故事仍须尝试。ACT4/Sail `test/act/config/heliodor/sail.json:712-725` 无可运行入口。
- readiness 单元尚未解决 PME/PMM 术语；coverage 的 Ssnpm 两侧为 `not-studied`。更新状态与索引，不改既有版本记录。

## Tasks & Acceptance

**Execution：**
- [x] `notes/units/rva23s64-ssnpm-v1.md` — 新增双核版本化学习单元，记录规范、控制/地址路径、证据、自检及访存族矩阵，逐核标状态并注明未验证边界。
- [x] Heliodor Ssnpm 案例 — 复核现有 `test_arch_supm` 并记录 make/Veryl 命令、输入和阻塞；Veryl 在共享 testbench 的 `dram` `$readmemh` check 失败，仿真未启动，故未改上游或增加无法执行的 guest 实验。
- [x] `notes/rva23-coverage.md`、`notes/units/index.md` — 将 Ssnpm 两侧更新为 `studied-unverified` 并链接证据。
- [x] 覆盖审计、计数检查器及测试 — 同步两侧状态计数和审计文本。

**Acceptance Criteria：**
- Given RVA23 Profile v1.0 与 Pointer-Masking v1.0.0，when 定义要求，then 引用 PME 与 PMM 的原始版本/位置，并说明已验证映射或差异。
- Given 锁定目标配置，when 追踪两核实现，then 分别说明 senvcfg/henvcfg/HUPMM、PMLEN 选择、适用模式及地址变换在生成/翻译路径中的位置。
- Given 可运行的代表案例，when 验证 PMLEN=0/7 与 tagged address，then 记录指令、模式、CSR 状态、预期、观察、命令和产物；不能运行的案例标明具体阻塞。
- Given 规范定义的显式访存族，when 完成矩阵，then 每类每核都有基于源码/测试/运行证据的状态，且不从某一类推定另一类。
- Given 本单元完成，when 学习者复核，then 能说明禁用与 PMLEN=7 的地址效果、地址边界及已覆盖和未覆盖族，并可回链到两边证据。

## Verification

**Commands：**
- Heliodor: `cd sources/heliodor && make -C test/supm` — 若依赖可用，应生成 `test/supm/supm_test.hex`。
- Heliodor: `cd sources/heliodor && /nvme_data1/richard/.local/share/veryl/toolchains/latest/veryl test --test test_arch_supm` — 记录完整工具版本、退出码和是否启动仿真；阻塞应精确归类。
- `python3 scripts/check_rva23_coverage.py` 与 `python3 -m pytest -q scripts/tests/test_check_rva23_coverage.py` — 覆盖行/状态格/固定计数一致，测试通过。
- `git diff --check` — 无空白错误。

## Implementation Notes

- 术语核查确认 Profile v1.0 发布 PDF 第 7 页 `Ssnpm` 行保留 `PME` 拼写；Pointer-Masking v1.0.0 定义架构字段 `PMM`。记录原始拼写差异和字段路径，不伪称 profile 文本已修订。
- Kunminghu TLB 有模式选择/地址变换静态路径；Heliodor 的静态输出只追踪到 M/S/U PMM，向量独立地址和 hypervisor 行为保持未验证。现有 Heliodor Supm 目标只覆盖 M-mode，不能代替 Ssnpm。
- `make -C test/supm` 成功但目标已是最新；Veryl `0.22.0 (967e477 2026-10-02)` 执行 `test --test test_arch_supm` 退出 1，`tb/test_arch_common.veryl:440` 的 `$readmemh(HEX_FILE, dram)` 触发 `invalid_initial_assign`，仿真未启动，不是 DUT 结果。
- 依静态证据将 Ssnpm 两侧标为 `studied-unverified`。PMLEN 写回/WARL、S/U/VS/VU tagged access、向量/CMO、guest HLV/HSV、权限/异常边界仍未动态验证。
- `python3 scripts/check_rva23_coverage.py` 通过：92 行、184 个状态格、59 项去重要求；S64 Kunminghu 为 37/21/0，Heliodor 为 26/29/1/2（依次为 partially-studied/studied-unverified/not-studied/evidence-observed）。`python3 -m pytest -q scripts/tests/test_check_rva23_coverage.py` 为 15 passed；`git diff --check` 通过。

## Spec Change Log

### Review Findings

- [x] Review/Patch 固定 Supm HEX 输入哈希，并声明无法证明其由当前汇编源生成 [notes/units/rva23s64-ssnpm-v1.md]
- [x] Review/Patch 为 Kunminghu VS/VU 与 HLV/HSV PMM selector 增加精确 TLB 行范围 [notes/units/rva23s64-ssnpm-v1.md]
- [x] Review/Patch 限定 Heliodor AMO/LR/SC 共享地址的证据和结论范围 [notes/units/rva23s64-ssnpm-v1.md]
- [x] Review/Patch 将未逐项追踪的 FP/compressed 地址族降为 unverified [notes/units/rva23s64-ssnpm-v1.md]
- [x] Review/Patch 记录 Heliodor H guest PMM 负搜索的文件集与精确词项 [notes/units/rva23s64-ssnpm-v1.md]
- [x] Review/Patch 在覆盖矩阵中列明 Heliodor 已检查的两条 issue AGU 与 scalar AGU [notes/rva23-coverage.md]
- [x] Review/Patch 记录 M-mode Supm 测试各检查 ID 的输入和预期结果 [notes/units/rva23s64-ssnpm-v1.md]

Rejected: none.

## Review Triage Log

- **R1 — low / patch：** “Heliodor Ssnpm 案例”容易被读成已完成 Ssnpm 实验；实际只检查并尝试运行 M-mode Supm 既有目标，仿真未启动。已将单元改为明确写成本轮尝试及失败结果，并注明不覆盖 Ssnpm。
- **R2 — low / patch：** PME/PMM 对照引用 profile 仓库可变 `main`，无法从记录复现源码版本。已锁定归档仓库提交 `e030b70992447784ad9081045d47ce6e278f381e` 并链接到固定行。
- **R3 — low / patch：** Heliodor 叙述把 henvcfg CSR 可读写性与 guest mask selector 路径放在同一结论中，容易混淆两者。已给出 CSR 声明/读写/复位位置，并明确 CSR 可访问不证明其 PMM 接入地址选择器。
- **R4 — low / patch：** E4 未给出第二 load AGU、henvcfg CSR 读写及 guest selector 搜索范围的行号，读者无法直接核验。已补充对应固定文件行号和检索范围限定。
- **R5 — false：** 要求在 Heliodor 段重复 HLV/HSV 的规范 selector 规则；该规则已在本单元规范段和访问族矩阵写明，原文没有缺失规范定义。无需重复。
- **R6 — low / patch：** Heliodor 的 guest 未验证状态缺少对照规范规则，单看该段不易判断所需控制。已在 Heliodor 路径说明补列 VS/VU 与 HLV/HSV 的规范 selector，仍明确未定位实现路径。
- **R7 — low / patch：** E3/E4 证据表此前仅以“上述位置”或文件名指向实现，脱离正文无法复核。已为 Kunminghu 与 Heliodor 补充固定 SHA 及文件/行号；该项与 R4 同属证据表定位不足，合并为同一补丁处理。

