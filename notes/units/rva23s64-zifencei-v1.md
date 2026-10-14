# Zifencei 自修改代码运行对照

此记录只覆盖 `sources.lock` 固定快照上的单 hart、机器模式本地 RAM 自修改案例。程序先从 `patched` 读取旧指令返回 1，再写入 `addi a0, zero, 42`；对应 FENCE.I 后再次取指并检查 42。只有两个比较均成功才写入成功 tohost，并走 Kunminghu NEMU good-trap；失败路径使用失败 tohost/NEMU trap。每个变体只改 FENCE.I 指令的一个保留字段。

## 复现命令

```sh
python3 experiments/kunminghu-smoke/run.py --topic zifencei --timeout 120
PATH="/nvme_data1/richard/.local/share/veryl/toolchains/latest:$PATH" python3 experiments/heliodor-smoke/run.py --topic zifencei --timeout 180
```

Kunminghu 使用 `sources/xiangshan` commit `c098f996bf4d301b88693b20315486d31e93bc9d`、`KunminghuV2Config`、`NUM_CORES=1`、锁定 emulator/NEMU 与交叉 GCC 15.1.0 / GNU objcopy 2.44。Heliodor 使用 commit `94e9c5821c24a8941c3ddc3b76daddc7124a855a`、Veryl 0.22.0（SHA-256 `aa57dd31488410769ee61c367f03de6cbf11101be47b510b99bde4ac9155b4c1`）、单 harness/DUT；沿用普通 arch harness 的隔离边界，只选择 `test_arch_rv64ui_fence_i` 并替换其镜像路径。两个 runner 的完整命令、工作目录、工具、输入哈希、退出码、CPU 启动状态、日志及产物哈希均在 `cpu-validation-toolchain-v1.yaml` 对应运行记录中。

## 证据与结果

八次运行均观察到 CPU 启动、成功终止和 run-pass；两核各自的架构测试程序在比较成功后才到达成功 marker，因此观察到旧值 1 和新值 42。Heliodor 同时输出 `tohost=1 pass=1`；Kunminghu 到达与链接 map 中 good-trap PC 相符的 NEMU good trap。三个保留字段变体均未发生非法指令 trap。

| 案例 | FENCE.I 编码 | 字段变化 | 预期/观察返回值 | Kunminghu run ID；输入 SHA-256；日志 SHA-256 | Heliodor run ID；输入 SHA-256；日志 SHA-256 |
|---|---:|---|---|---|---|
| 标准 FENCE.I | `0x0000100f` | 无 | `1 → 42` / 两核 pass | `kunminghu-fixture-20261014T061155Z-3e81181d1d02`<br>`960d13173a27a6c2da0f26ac8e2332afbc8eddfa4abdfabc6a6475e7e3b17039`<br>`26a7c511bb0ca71d59f70b7db4570edc4759f3010b5687fb1429ba094de026bb` | `heliodor-core-20261014T061229Z-2934442`<br>`8c38dc80b0ea216a14de36382d1d7374e2f2011b026a90b8df984d0a0472e669`<br>`993c4cfa08028cfd0a96c5743084373d53a59738baed8456277b3ba7e699fd6b` |
| 仅 funct12 非零 | `0x0010100f` | funct12=1 | `1 → 42` / 两核 pass | `kunminghu-fixture-20261014T061204Z-3e81181d1d02`<br>`4a4766c287ca020a0242d15b945f33150425c626b55294c9e4210b96de27a07a`<br>`fcc22f6b0ae08779b115cc4b5869a696c8d11db2645b82475104e927a9d2877e` | `heliodor-core-20261014T061254Z-2934442`<br>`f5773af3200b1efa03bf815e343eb9fb06ecf11d9850572e148a87f69ec043a8`<br>`8c250a91294ce10a9b359a6051bd966a1a3e100cfa5b4c0bfde2de26182f57d0` |
| 仅 rs1 非零 | `0x0000900f` | rs1=1 | `1 → 42` / 两核 pass | `kunminghu-fixture-20261014T061212Z-3e81181d1d02`<br>`13b76c8668ee518f45aeae2ce0ab0794328093b8b359d7df706be0baf269d63a`<br>`a048504ff70d604eca62de25feef565a1e017c8a84ce92a3546b20feae6a8896` | `heliodor-core-20261014T061318Z-2934442`<br>`5fa6b0cfe0f2377c54b8fe7ba4043156ec71b2ffdb46a7f07b2fe61da4384a12`<br>`f86ca898bc7e10e8630c48f3d5a0238a449570c130c8336605a3f4466a1fbc46` |
| 仅 rd 非零 | `0x0000108f` | rd=1 | `1 → 42` / 两核 pass | `kunminghu-fixture-20261014T061220Z-3e81181d1d02`<br>`b14571531a136adf157657e825546831614c950193c9756f1ecc9b1745c46f58`<br>`91158ac5438d0540a1857ed8e63b28838ebf7d5b2b1e10d7af4a211a19e5c1b1` | `heliodor-core-20261014T061342Z-2934442`<br>`fbcca53c9fb04291cd1bef4400add7c526c4a6aba7f541751f318d8bdcfa73ad`<br>`cdadea7bf5b2ea00a2128b1f7af64bdcd50326b06fac5d95fa851238c409adb9` |

Kunminghu 输出日志路径位于 `notes/units/evidence/smoke/kunminghu-fixture-runs/<run-id>/output.log`；Heliodor 位于 `notes/units/evidence/smoke/heliodor-core-smoke-inputs/<run-id>/output.log`。记录与完整 stdout/stderr 分别哈希，精确路径见 manifest。

镜像由锁定的 riscv64-unknown-elf-gcc 15.1.0 与 GNU objcopy 2.44 生成；使用 `python3 experiments/rva23s64-zifencei/build_images.py` 可重建并检查四个 hex image。

## 镜像与编码核验

`experiments/rva23s64-zifencei/{standard,funct12,rs1,rd}.S` 为四份 RV64 汇编输入，共用 `fixture.ld`。相应 `.hex` 是从链接后 RV64 image 生成的 DRAM word 文件；链接脚本将 `_start` 定位于 `0x80000000`，Kunminghu raw image loader 与 Heliodor `RESET_PC` 均映射到该地址；FENCE.I 指令处于镜像偏移 `0x20`。单测逐字节比较镜像，确认标准编码以外每个变体只有编码内对应字节不同。

`funct12` 变体只置 bit 20；`rs1` 变体只置 bit 15；`rd` 变体只置 bit 7。Heliodor 的隔离 workaround 仅排除未实例化 debug harness，保留普通 arch harness，并在 DRAM 初始化处沿用局部 `allow(initial_assign)`。

## 范围限制

两个 runner 均固定单 hart，因此结论只表示所记录快照、工具链、hart 配置和这四个输入的 hart-local 行为。没有测试一个 hart 发布代码后由远端 hart 执行的同步行为；这些案例不构成 RVA23S64 或 Zifencei 的完整符合性声明。
