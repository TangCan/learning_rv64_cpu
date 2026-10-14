# RVA23 Profile ID 清单来源

`scripts/check_rva23_coverage.py` 中的 `U64_IDS` 与 `S64_IDS` 是按官方 RVA23 Profile **v1.0** §3.1.1（RVA23U64）和 §3.1.2（RVA23S64）维护的版本化键清单。

- 发布规范：[RVA23 Profile v1.0](https://docs.riscv.org/reference/rva23/v1.0/rva23-profiles.html)
- 上游源文件：[rva23-profile.adoc](https://github.com/riscv/riscv-profiles/blob/e030b70992447784ad9081045d47ce6e278f381e/src/rva23-profile.adoc)，固定提交 `e030b70992447784ad9081045d47ce6e278f381e`
- 来源范围：该文件中的 RVA23U64/RVA23S64 mandatory-extension 表（§3.1.1–§3.1.2）；S64 继承行仍作为 profile 行保留，由 checker 单独验证与同 ID U64 行的关联。
- 更新规则：更换 Profile 版本时，先对照新版本 mandatory-extension 表更新 manifest、目录与 `EXPECTED_COUNTS`，再运行 `scripts/check_rva23_coverage.py` 和对应测试。此清单记录要求 ID，不代表实现或认证状态。
