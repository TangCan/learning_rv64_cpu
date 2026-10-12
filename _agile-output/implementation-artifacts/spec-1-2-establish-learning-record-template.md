---
title: 'Story 1.2: 建立统一的学习记录模板'
type: 'feature'
created: '2026-10-12'
status: 'done'
route: 'oneshot'
baseline_commit: '40749e01f45ff594b3509b92dab6545b3036437b'
review_loop_iteration: 0
context:
  - '{project-root}/_agile-output/implementation-artifacts/epic-1-context.md'
  - '{project-root}/_agile-output/planning-artifacts/epics.md'
  - '{project-root}/_agile-output/planning-artifacts/architecture/architecture-learning_rv64_cpu-2026-10-12/ARCHITECTURE-SPINE.md'
  - '{project-root}/_agile-output/specs/spec-learning_rv64_cpu/learning-record-conventions.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 后续学习单元需要同时比较 Kunminghu 与 Heliodor，并把结论追溯到规范、来源快照和证据；没有统一模板会造成记录结构不一或混淆检查与实际运行结果。

**Approach:** 创建一个可复用的中文学习记录模板和单元索引，固定必需元数据、双实现对照章节、证据字段与版本命名规则，使之后的学习记录可以一致填写和复查。

</frozen-after-approval>

## Implementation Notes

本故事按 architecture spine 的 AD-1/AD-2 和 `learning-record-conventions.md` 建立单一模板及版本索引。模板将 source snapshot ID 与仓库 URL、分支、完整 SHA 一并作为填写字段；比较 claim 分开记录两边证据 ID；运行证据包含命令、配置、输入、预期、观察和产物信息。索引初始为空，尚无 Story 1.3 学习单元可登记。审查后明确了两边实现路径各项的证据 ID 位置、单独的运行产物路径字段，以及索引当前版本栏必须填写版本文件路径。

## Review Triage Log

| Verdict | Finding and evidence | Disposition |
| --- | --- | --- |
| low | Kunminghu/Heliodor 路径的阶段变化、源码位置未分别标明证据 ID 填写位置，虽总注释要求引用，但不便逐项追踪；已在三个路径条目增加证据 ID 提示。 | patch — 已修复 |
| low | 证据表将源码位置和运行产物合在一列，不能清楚表达保留产物的独立路径；已拆分证据位置与产物路径列。 | patch — 已修复 |
| low | 索引的“当前版本”栏没有说明填版本号还是文件名；已明确列头填写 `<unit_id>-vN.md` 版本文件路径。 | patch — 已修复 |
