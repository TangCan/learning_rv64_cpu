- source_spec: `_agile-output/implementation-artifacts/spec-6-6-sscofpmf-hardware-overflow-filter-evidence.md`
  summary: 评估 Kunminghu Story 6.6 exploratory artifacts（约 620 MB）能否安全压缩或清理；确认来源和 manifest 引用兼容前保留原文件。
  evidence: 2026-10-15 全量 smoke 归档盘点为 2,410 files / 1,099,348,447 bytes，其中 910 个日志占 1,082,119,920 bytes，发现 852 个重复副本（164,760,860 bytes）；298-run manifest 的 2,133 个 smoke 路径校验有效。归档盘点与保留决定已完成，但 `.hex/.bin/.elf/.map` 可重建性尚未逐类验证，故未压缩、改写或删除任何证据。后续若实施压缩/去重，需单独确认来源并验证 manifest 引用兼容。
