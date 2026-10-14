# Zifencei 自修改代码对照

使用 SHA-256 和版本双重核验的 GCC 15.1.0 / GNU binutils 2.44 交叉工具重建并验证四镜像：`python3 experiments/rva23s64-zifencei/build_images.py`。构建器核验 `_start` 与 ELF 入口映射基址、FENCE.I 符号偏移、镜像长度及字段差异。四个固定 RV64 单 hart 镜像与逐核运行证据见 [Zifencei 运行记录](../../notes/units/rva23s64-zifencei-v1.md)。

复现 Kunminghu 四案：

```sh
python3 experiments/kunminghu-smoke/run.py --topic zifencei --timeout 120
```

复现 Heliodor 四案：

```sh
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" \
  python3 experiments/heliodor-smoke/run.py --topic zifencei --timeout 180
```

源文件 `{standard,funct12,rs1,rd}.S` 共用 `fixture.ld`；链接脚本将 ELF `_start` 放在 `0x80000000`；Kunminghu emulator 将 raw binary 装载到 `0x80000000`，Heliodor harness 的 `RESET_PC` 也是 `0x80000000`，因此同名 `.hex` 按该地址映射为 DRAM 32-bit word image。每个镜像的 FENCE.I 位于偏移 0x20，四种编码只有 funct12、rs1、rd 中指定的一项分别置 1。镜像 SHA、运行命令、固定快照与配置、工具版本、退出码、CPU 启动状态、tohost/NEMU 观察、日志及其 SHA-256 记在 `notes/units/evidence/cpu-validation-toolchain-v1.yaml`；报告表中的 run ID 对应 manifest 逐次运行记录。

每个程序均先检查旧指令返回 1，再写入 `addi a0, zero, 42`，执行对应 FENCE.I 并重新取指，检查返回 42。比较成功才设置成功终止 marker；失败路径设置失败 tohost 或 NEMU trap。此处结果仅覆盖所记录的单 hart 配置，不代表远端 hart 同步或完整 profile 符合性。
