---
unit_id: "<stable-unit-id>"
stage_id: "<stage-id>"
scope: "<本单元覆盖的行为与边界>"
exclusions:
  - "<明确列出未覆盖的行为或子案例；没有时写 none>"
spec_refs:
  - name: "<规范名称>"
    edition: "<版本或发布日期>"
    section: "<章节、条款或要求 ID>"
    profile_category: "<mandatory | optional | upstream-claim | not-profile-specific>"
source_snapshots:
  - project: "Kunminghu"
    snapshot_id: "<sources.lock 中的 snapshot_id>"
    repository: "<仓库 URL>"
    branch: "<分支名>"
    commit: "<完整 commit SHA>"
  - project: "Heliodor"
    snapshot_id: "<sources.lock 中的 snapshot_id>"
    repository: "<仓库 URL>"
    branch: "<分支名>"
    commit: "<完整 commit SHA>"
---

<!-- 每条结论以 E 编号引用下方证据；比较结论分别引用两边证据。未执行的测试不能标为通过。 -->

## 单元自检

- **问题：** <学习者需要回答的问题>
- **学习者答案：** <用自己的话解释，不以复制源码代替>
- **检查类型：** <explanation | source-location | test/simulation | other>
- **证据 ID：** <E...；没有适用证据时说明原因>

## 架构行为与子案例

- **可观察行为：** <说明输入、可见结果及适用规则>
- **规范依据：** <引用 frontmatter 中的规范、版本和章节；没有适用规范时说明原因>

| 子案例 | 覆盖状态 | 说明 / 排除原因 |
| --- | --- | --- |
| <参数、宽度、掩码、异常、特权模式等具体子案例> | <covered | excluded | unconfirmed> | <边界及证据 ID；未覆盖项必须说明> |

## Kunminghu 路径

- **阶段与状态变化：** <按行为路径描述关键阶段、信号或状态变化；关联证据 ID，如 E1>
- **源码位置：** <固定 snapshot 下的路径与符号，关联证据 ID；可用时附行号或永久链接>
- **相关验证：** <测试/设计材料及其证据 ID；区分检查与运行>

## Heliodor 路径

- **阶段与状态变化：** <按行为路径描述关键阶段、信号或状态变化；关联证据 ID，如 E1>
- **源码位置：** <固定 snapshot 下的路径与符号，关联证据 ID；可用时附行号或永久链接>
- **相关验证：** <测试/设计材料及其证据 ID；区分检查与运行>

## 比较结论

| Claim ID | 结论 | Kunminghu 证据 ID | Heliodor 证据 ID |
| --- | --- | --- | --- |
| C1 | <写出有边界、可核查的差异或相同点> | <E...> | <E...> |

## 证据表

| ID | 支持的 claim / 自检 | Kind | Status | 项目 / snapshot | 证据位置 / 测试文件 | Command | Configuration | Input / case | Expected | Observed | 产物路径 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| E1 | <C1 或自检> | <spec / design-doc / source / test-inspected / test-run / experiment> | <inspected / run-pass / run-fail / unverified / not-applicable> | <项目及 snapshot_id；规范证据填规范版本> | <源码、规范、测试文件位置及行号/链接> | <运行命令；未运行则填 not-run> | <配置；不适用时说明> | <输入/案例；不适用时说明> | <预期；不适用时说明> | <实测观察；未运行不得写通过> | <保留的运行产物路径；无产物时填 none> |

- `run-pass` 仅用于实际执行且观察到预期结果的证据。未执行测试标为 `unverified`；上游声明须与本项目观察分开。
- 使用 `mandatory`、`optional`、`upstream-claim` 等标签明确区分规范必选、可选和上游自述，不以局部测试推断完整符合性。

## 学习者总结

<用中文概括本单元学到的架构行为、两边实现特点和证据边界；ISA 名称、扩展名、符号及源码路径保留上游拼写。>

## 未解问题

- <尚未解决的问题及其影响；没有时写 none>
