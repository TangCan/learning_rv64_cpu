---
title: 'Story 5.7：审计 RVA23S64 覆盖与学习结项证据'
type: 'feature'
created: '2026-10-13'
status: 'done'
route: 'dispatch'
review_loop_iteration: 0
baseline_commit: 'e80d6a7cb6ec3ca8d7a017512537101de958041e'
context: ['{project-root}/_agile-output/implementation-artifacts/epic-5-context.md', '{project-root}/_agile-output/planning-artifacts/epics.md', '{project-root}/sources.lock']
---

<frozen-after-approval reason="human-owned intent — Epic 5 start gate authorizes Story 5.7 scope">

## Intent

**Problem：** Epic 5 的五个 RVA23S64 深度单元、Epic 4 覆盖目录和项目学习目标分散在不同记录中，尚无一次可复查的最终证据审计与结项判断。

**Approach：** 依据锁定源码快照和规范版本，核对五单元的两侧状态、自检、计划子案例、运行/阻塞证据及链接；运行覆盖与 sprint 检查，补上通用本地文档链接检查。产出审计索引，区分已形成学习证据的目标与未验证的 CPU 行为。

**Always：** 记录真实 SHA；区分源码、测试材料、实测、阻塞和上游声明；未运行项目不得记通过；结项判断只覆盖本项目学习范围。

**Never：** 不把局部证据外推为整体 RVA23 符合或认证；不修改 `sources/`；不因工具失败掩盖未知。

## I/O & Edge-Case Matrix

| 输入 / 状态 | 预期审计结果 | 边界处理 |
|---|---|---|
| 五单元、覆盖表、锁文件 | 精确列出规范键/版本、快照、两侧状态、证据、自检和子案例 | 缺项逐项记录，不推断通过 |
| 实测失败、未启动、静态缺失、未验证 | 区分 `run-fail`、阻塞与有界静态结论 | 记录具体原因、证据边界和结项影响 |
| 文档链接和 sprint YAML | 可复跑的检查命令、版本、输出 | 可修问题修复并重跑；其余保留理由 |
</frozen-after-approval>

## Code Map

- `_agile-output/planning-artifacts/epics.md` Story 5.7 AC；PRD FR-11；`epic-5-context.md` 规定快照、证据与结项边界。
- `notes/rva23-coverage.md`、`notes/units/rva23-mandatory-coverage-audit-v1.md`、`notes/units/index.md` 是目录、总审计和学习入口；当前为 92 profile 行、184 状态格、59 去重要求。
- 五单元：`notes/units/rva23s64-{zifencei,sstc,sscofpmf,ssnpm,ssstateen}-v1.md`。仅 Ssstateen Heliodor M/HS fixture 实际运行到 CPU，结果为 `run-fail`。
- `scripts/check_rva23_coverage.py` 校验目录、汇总和目录证据链接，不覆盖全库链接。仓库没有独立文档/索引链接 checker；本 story 增加无依赖的 `scripts/check_doc_links.py` 及测试，只检查约定学习文档中的常规 Markdown inline/reference 链接和 HTML href/src，不是完整 CommonMark 解析器；自动链接、转义定界符及带未转义嵌套括号的 inline destination 不在支持范围内。
- `.agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate` 只校验 sprint YAML。两份上游 checkout 应与 `sources.lock` 匹配并保持干净。

## Tasks & Acceptance

**Execution：**
- [x] `scripts/check_doc_links.py`、`scripts/tests/test_check_doc_links.py`、`scripts/tests/test_closeout_audit.py` — 检查本地链接/锚点，并锁定五项映射及运行/阻塞分类。
- [x] 五单元、Story specs 与 `sources.lock` — 交叉核对状态、快照、规范、证据、自检及计划案例；未发现有证据支持但需要修复的矛盾。
- [x] 覆盖表、审计记录、索引 — 汇总实际验证和未决边界、工具结果及项目学习结项决定。
- [x] Story spec 与 `sprint-status.yaml` — 记录验证结果；实现已完成并交由 BMAD review，Story 5.7 进入 review，Epic 5 保持 in-progress。

**Acceptance Criteria：**
- Given Epic 4 目录和五单元，when 审计，then 每项可追溯到精确规范键、双核状态及证据；缺调查、缺验证、阻塞和运行失败有区别。
- Given 已计划案例，when 核对运行记录，then 每个可运行案例有实际结果，未运行者有具体 blocker 和范围；不把输入期望或 check 阶段退出写成 DUT 结果。
- Given 项目文档和 sprint 状态，when 运行覆盖检查、内链检查、sprint validator，then 记录命令/版本/输出，修复并复跑可修问题，说明余项。
- Given 汇总证据，when 判断学习结项，then 说明有证据的学习目标、未验证行为及是否接受限制，且不声称标准符合性/认证。

## Verification

**Commands：**
- `python3 scripts/check_rva23_coverage.py` — valid，记录行数、状态格、去重计数。
- `python3 scripts/check_doc_links.py` — 约定学习文档中支持语法的本地链接无未解释缺项；不解析的 Markdown 形式见 Implementation Notes。
- `uv run --no-cache --with ruamel.yaml python .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py validate --status-file _agile-output/implementation-artifacts/sprint-status.yaml` — valid，无问题。
- `python3 -m pytest -q scripts/tests`、`git diff --check` — 全部通过。

## Implementation Notes

- 新增 `scripts/check_doc_links.py`，默认检查 `notes/` 及 Epic 5 的 context、start-gate 和 Stories 5.1–5.7；可传文档/目录参数。只依赖 Python 标准库，检查常规 Markdown inline/reference 链接、HTML href/src、本地 heading/显式 anchor、`file:line` 与 `#Lnn`，按源文档行号报告并在缺项时退出非零。它会忽略 fenced/inline code，但不是完整 CommonMark 解析器；自动链接、转义定界符及带未转义嵌套括号的 inline destination 不受检查。
- 新增 `scripts/tests/test_check_doc_links.py`，测试本地目标、heading/CJK/重复/显式 anchor、缺失目标、行号、外链/inline/fenced code、reference/HTML 链接、CLI 成功/错误退出、非法 UTF-8 和无效 URL。
- 交叉核验五个单元、覆盖目录和锁定 checkout：实际 SHA 均匹配 `sources.lock`。五项 exact key/版本及案例结果汇总于 [结项审计](../../notes/units/rva23s64-closeout-audit-v1.md)；仅 Ssstateen Heliodor M/HS fixture 有 CPU 运行观察，结果 `run-fail`。其他被计划的 CPU 案例分别为启动前阻塞或静态/未验证，不记通过。
- 检查结果：`python3 scripts/check_rva23_coverage.py` 输出 92 profile rows、184 状态格、59 去重要求，valid；`python3 scripts/check_doc_links.py` 输出 36 documents 中所有受支持语法的本地目标和锚点存在；指定 sprint validator 输出 valid=true、problems=[]；`python3 -m pytest -q scripts/tests` 为 29 passed；`git diff --check` 通过。工具版本和完整边界见结项审计。
- 学习结项接受范围仅为本项目的对照记录与证据边界；Epic 5 的 5.1–5.6 仍处 review，本故事实现已交 review，Epic 5 保持 in-progress。无 RVA23 整体符合性/认证结论。

## Spec Change Log

- 2026-10-13：实现 Story 5.7；新增标准库文档链接检查器和回归测试，完成五单元证据审计、结项记录与索引；按实际验证结果标记任务完成。
- 2026-10-13：审查发现链接扫描器边界和错误输入处理不足；明确支持语法范围，修复代码跨度、fence、UTF-8 和非法 URL 处理并补回归测试。

## Review Triage Log

- `medium — patch`（盲审：sprint 未进入 review）：已核实；实现完成却仍是 `in-progress`，与当前交付阶段不符。将 Story 5.7 状态同步为 `review`，Epic 5 保持 `in-progress`。
- `medium — patch`（盲审：inline code 被当成链接）：已核实；`visible_markdown()` 原先只屏蔽 fenced code，行内代码中的 `[...](...)` 会触发错误报告。加入行内代码跨度剔除和回归用例。
- `medium — patch`（盲审：fence 匹配过宽）：已核实；任意同字符 fence 都会结束代码块，且有 info string 的行也会被误认作结束标记。按字符、长度和尾随空白判断闭合，并加入回归用例。
- `medium — patch`（盲审：带括号目的地未说明）：已核实；当前链接正则不支持带未转义嵌套括号的路径，曾未说明该限制。明确 checker 支持语法和不检查的 CommonMark 形式，并限定审计结论范围。
- `false`（盲审：Ssstateen `not-present` 与 run-fail 混淆）：表格分别说明目录 `not-present` 分类和隔离 M/HS fixture 的 `run-fail`；“未决项”还明确分类仅针对固定主路径及本次受控观察，不外推至 guest 或外部集成。
- `false`（盲审：逐个计划案例没有结果/阻塞）：逐项读取 Story 5.2–5.6 spec 和对应证据表；每个启动过的候选 target 有实际运行结果，其余条目明确缺少 harness/入口或未运行边界，符合该 AC 对未运行案例记录 blocker 的要求。
- `low — patch`（盲审：checker 未定义支持的 Markdown 子集）：与带括号目的地问题同属链接语法支持范围未定义；在 spec 和审计结果中明确列出支持的常规 inline/reference/HTML 形式及未覆盖自动链接、转义定界符、嵌套括号形式。
- `low — patch`（边界审查：无效 UTF-8 文档导致 traceback）：已核实；文档读取只捕获 `OSError`，无效 UTF-8 会抛出未处理的 `UnicodeDecodeError`。改为以单条不可读文档错误返回，并加入测试。
- `low — patch`（边界审查：非法 URL 导致 traceback）：已核实；`urlsplit()` 对损坏的 IPv6 URL 会抛出 `ValueError`。现在报告链接行的 invalid target 并继续扫描，加入测试。
