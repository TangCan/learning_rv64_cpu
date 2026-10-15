- source_spec: `_agile-output/implementation-artifacts/spec-6-6-sscofpmf-hardware-overflow-filter-evidence.md`
  summary: 评估或压缩/清理 Story 6.6 exploratory artifacts，并同步更新 manifest hashes 与完整性校验。
  evidence: 当前 Kunminghu fixture evidence 子树约 620 MB，包含 manifest 哈希绑定的诊断日志和运行产物；清理会破坏现有证据校验。本故事保留这些文件，后续需评估压缩或清理方案，当前带来克隆与仓库存储风险但不阻止已验收的 CPU 证据。
- source_spec: `_agile-output/implementation-artifacts/spec-6-8-run-ssstateen-eight-csrs-mode-gates.md`
  summary: 为 Heliodor `mode-filters` 增加贯通 runner 的测试，验证选中的 HEX、manifest case 与延长后的 cycle budget。
  evidence: 当前单测分别覆盖观察值筛选、fixture 内容和 cycle budget，但没有从 runner 的 `mode-filters` dispatch 一路核对三者；该路径属于既有 Story 6.6 SSCOFPMF runner，Story 6.8 的 stateen 变更未引入此缺口。
- source_spec: `_agile-output/implementation-artifacts/spec-epic-6-retro-actions.md`
  summary: 保留 smoke 归档原路径，完成体积/重复项盘点并记录保留与后续压缩建议。
  evidence: 2026-10-15 盘点 2,410 files / 1,099,348,447 bytes；910 个日志占 1,082,119,920 bytes；发现 852 个重复副本（164,760,860 bytes）。298-run manifest 的 2,133 个 smoke 路径校验有效。本轮未迁移、压缩、改写或删除证据；后续压缩/去重需单独验证 manifest 引用兼容。
