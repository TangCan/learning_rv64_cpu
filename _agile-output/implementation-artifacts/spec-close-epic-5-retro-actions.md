---
title: '关闭 Epic 5 retrospective action items'
type: 'maintenance'
created: '2026-10-14'
status: 'done'
route: 'dispatch'
baseline_commit: '776d2c2'
context:
  - '{project-root}/_agile-output/implementation-artifacts/sprint-status.yaml'
  - '{project-root}/_agile-output/implementation-artifacts/epic-5-retro-2026-10-14.md'
  - '{project-root}/notes/units/rva23s64-closeout-audit-v1.md'
  - '{project-root}/scripts/check_rva23_coverage.py'
  - '{project-root}/scripts/check_doc_links.py'
---

## Intent

**Problem:** Epic 5 有四项 retro action items 仍为 open，涉及结项映射的自动校验、Markdown 链接检查边界、CPU 行为验证后续门和 closeout audit 的决策摘要顺序。

**Approach:** 按四项行动的原文完整处理，修复已复现的 checker 缺陷；CPU 行为验证项形成可复现 preflight、现有失败的诊断结论和按五专题拆分的可执行故事。只有每项均有可复查证据后才通过官方 sprint action 状态工具标记 done。

## Boundaries & Constraints

**Always:** 不修改上游 `sources/`；静态审阅、工具阻塞、仿真功能失败分别表述；运行记录包含 revision、输入摘要、命令、工具版本和输出。

**Never:** 不把 testbench/elaboration 阻塞称为 CPU run-fail；不把隔离失败在根因未定位时归因于 RTL；不声称 RVA23 认证或 CPU 行为验证完成。

## Tasks & Acceptance

- [x] action 9：测试精确五主题 profile key 以及覆盖目录中的 Heliodor/Kunminghu 状态；给硬编码 profile ID 列表补充权威、版本化来源；增加 evidence 链接与 ID 范围解析边界测试。
- [x] action 10：定义 GitHub 仓库 GFM renderer 和检查器支持的 Markdown/HTML 子集；修复或明确拒绝转义反引号、HTML 注释、嵌套括号目标；用 renderer 结果校验 heading anchors。
- [x] action 11：记录环境/harness preflight；诊断 Kunminghu Mill、Heliodor testbench 和 Ssstateen run-fail；给五专题未运行案例建立有验收和结果元数据要求的 executable stories。
- [x] action 12：将学习结项决定移到 closeout audit 开篇，保留后续证据和自检。
- [x] 所有目标测试和审计命令通过；使用官方 sprint 状态脚本将 action 9–12 改为 done；复核整个 sprint-status。

## Verification

- `uv run --no-cache pytest -q scripts/tests/test_closeout_audit.py scripts/tests/test_check_doc_links.py scripts/tests/test_check_rva23_coverage.py`
- `uv run --no-cache python scripts/check_rva23_coverage.py`
- `uv run --no-cache python scripts/check_doc_links.py`
- sprint status validator and `git diff --check`

结果：39 tests passed；coverage checker valid（92 profile rows、184 status cells、59 deduplicated requirements）；文档链接检查 valid（38 documents）；sprint status validator valid；`git diff --check` clean。官方 `sprint_status.py update --epic 5 --set-action-status ...` 将 action 9–12 更新为 `done`。
