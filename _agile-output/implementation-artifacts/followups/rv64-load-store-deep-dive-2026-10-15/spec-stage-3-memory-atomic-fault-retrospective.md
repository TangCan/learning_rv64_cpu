---
title: '学习日志：回顾 Stage 3 访存、原子操作与地址异常'
type: 'feature'
created: '2026-10-15'
status: 'done'
route: 'oneshot'
review_loop_iteration: 0
context:
  - '{project-root}/learning-journal/plan.md'
  - '{project-root}/learning-journal/index.md'
  - '{project-root}/notes/units/load-v2.md'
  - '{project-root}/notes/units/store-v1.md'
  - '{project-root}/notes/units/amoadd-d-v1.md'
  - '{project-root}/notes/units/sv39-load-fault-v3.md'
  - '{project-root}/_agile-output/implementation-artifacts/epic-3-retro-2026-10-12.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 学习日志首页仍将 Stage 3 标为待回顾，读者需要在普通 load、AMO、Sv39 fault 单元和 Epic 3 复盘之间自行还原学习过程；后来补充的 SD 追踪与证据审计也没有和原始 Epic 交付清楚区分。

**Approach:** 根据完整 Git 历史和现存学习记录撰写中文 Stage 3 事后回顾，并更新日志首页和学习计划。明确区分 Epic 3 最初的 LD、AMOADD.D、Sv39 fault 三项，与后续 LD/SD/fault 静态复核；准确标出测试、阻塞、未验证边界，不补造过程或动态结果。

</frozen-after-approval>

## Implementation Notes

已写入 Stage 3 事后回顾，并更新日志索引与计划。明确原 Epic 3 最初覆盖 LD、AMOADD.D、Sv39 fault；将 10 月 15 日 LD/SD/fault 复核作为后续静态扩展，保留各自运行限制。盲审问题已修复：明确 Git 时间字段为作者时间 `%aI` 并标注 +08:00；补充 Kunminghu StoreQueue uncached/MMIO handshake 与 Heliodor `sb_push` 的具体接受边界。文档链接与差异格式检查通过；未运行 CPU 构建、测试或仿真。

## Review Triage Log

- **low — patch：** 时间线称时间为提交者时间，但命令显示 `%aI` 作者时间；统一改为作者时间，标注 +08:00 并保留可复制命令。
- **low — patch：** `SD` 表格中的接受点过于抽象；按单元证据补充 StoreQueue uncached/MMIO request handshake、Heliodor committed store buffer `sb_push` 与两者不代表 DRAM 可见性的边界。
- **low — patch：** 开篇把 commit date 的证明范围说得过宽；改为说明提交记录能定位材料进入版本历史的时间，但不能还原未记录过程。
