# 验证证据索引与归档策略

本目录服务于最终学习档案：保留结论所需的来源快照 ID、命令、结果摘要、失败/未验证边界和可追溯链接。专题结论见 [`notes/units/`](../)；运行命令、工具版本、输入与输出 hash 汇总见 [`cpu-validation-toolchain-v1.yaml`](cpu-validation-toolchain-v1.yaml)。

## 当前保留内容

- 小型 `stdout.log`：保留实际提交轨迹、通过 marker 或 GOOD TRAP 等简洁结果。
- 被学习记录明确引用的 `output.log`，以及每种 runner 的代表性输出样本。
- 输入汇编、ELF/HEX/BIN、linker map、fixture 元数据、run manifest 与 SHA-256。
- 项目自己维护的实验源码位于 `experiments/`；固定上游来源和 commit 见 `sources.lock`。

冗长的 `stderr.log`、未被学习记录引用的重复 `output.log`，以及每次隔离运行重复复制的 runner/Veryl 源码快照，已移至仓库外归档。锁定上游 commit、每次运行的 metadata 和 artifact SHA-256 仍在仓库内；上游源码本身可从锁定快照恢复。

## 仓库外原始证据包

- 位置：`../learning_rv64_cpu-evidence-archive-2026-10-21-r1/removed-evidence.tar.zst`
- SHA-256：`5f85d88ca140277e16ae8b631766289680bc086eeefde1bf53291df91b229eec`
- 内容：1,379 个归档原始文件；其中 1,373 个已移出工作树，6 个被专题文档直接引用的日志仍保留，原始总大小 1,056,405,863 bytes；压缩包约 24 MiB。
- 清单：[`archive-manifest-2026-10-21.tsv`](archive-manifest-2026-10-21.tsv)，逐文件记录原路径、大小、SHA-256 和归档原因。

该压缩包不提交到 Git。恢复全部归档文件（从仓库根目录执行）：

```sh
tar --zstd -xf ../learning_rv64_cpu-evidence-archive-2026-10-21-r1/removed-evidence.tar.zst -C .
```

运行结果与 fixture 未被改写；当前仓库只减少冗长日志和重复运行快照。归档在本机仓库旁，不会随 Git clone/push 自动传输，需单独备份或交付。
