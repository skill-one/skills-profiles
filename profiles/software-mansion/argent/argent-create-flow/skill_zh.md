# 创建一个 Argent 流

Argent 流是存储在 `.argent/flows/<name>.yaml` 中的可重播序列。

对于已保存的问答测试用例、工单或验收标准，首先加载 `argent-qa-flows`。它添加了确定性设置、验收证据和两遍证明。

## 阅读相关参考

- 在创建或修改流之前，请完整阅读 [实时编写](references/live-authoring.md)。
- 在优化、组合或手动审查 YAML 时，请阅读 [流 YAML](references/flow-yaml.md)。对于 Vega，在录制远程或键盘工具之前，请先阅读其平台限制。
- 流在物理 iPhone 上运行（一个 iOS `list-devices` 条目，类型为 `"device"`），但重播永远不会自动绑定一个，即使没有启动模拟器：将手机的 udid 作为 `device`（CLI `--device`），并且只有 `connected` 的手机才能运行。在硬件上，流树是 `describe` 树：相同的 id 和角色，没有 UIView 层级。有关硬件契约，请参阅 `argent-ios-device-interact`。
- 在捕获警告、原始坐标、不可用树、时机不当的过渡、覆盖层或重播失败时，请阅读 [可靠性和恢复](references/reliability-and-recovery.md)。

## 不可协商的规则

1. **记录第一次演练。** 在第一次启动或应用内操作之前启动记录器。不要重建排练的路径。
2. **在其状态出现时记录检查。** 记录 `await-ui-element` 实时，然后在优化期间将其转换。回声记录意图或诊断上下文，而不是应用行为或判断。截图是人类证据，而不是可执行的判断。对于缺失，记录与 `visible` 相同的选择器，执行移除操作，然后将其记录为 `hidden`。
3. **使用语义目标。** 优先选择严格的 id，然后是稳定的文本或可访问性标签。使用 `scroll-to` 来定位屏幕外的元素。立即通过 [坐标回退门](references/reliability-and-recovery.md#coordinate-fallback-gate) 解决每个原始点警告。
4. **证明每个屏幕更改。** 记录仅目的地的身份检查。在优化期间，跟随它使用 `await: { idle: true }`。静止并不能证明身份，并且 `idle` 可以带警告通过。
5. **仅优化已执行的行为。** 转换记录的步骤而不改变其含义。实时记录任何缺失的操作或结构检查。唯一未记录的插入是计划的 `snapshot:`、导航 `await: { idle: true }` 和文档化的 Chromium 打包 `launch:`。
6. **仅在用户请求时使用脚本。** 阅读 [流 YAML：本地脚本](references/flow-yaml.md#local-scripts)，然后使用 `flow-add-script` 记录每个脚本。
7. **端到端重播最终的 YAML。** 正常流需要一个不间断的完整遍历。`argent-qa-flows` 需要两次连续的遍历。

### 稳定选择器

稳定选择器由应用代码固定，并且可以支持流的所有帐户、数据、时间、计数、顺序以及所有区域设置和环境。优先选择如 `settings-screen` 的 id。不要基于值（如 `Today`、`Item 4`、用户名、计数器或时间戳）来设置门。

### 仅限流的 选择器作用域

在优化期间，使用 `within`、`after` 和 `next` 来消除重复元素歧义。阅读 [流 YAML：关系作用域](references/flow-yaml.md#relational-scopes) 了解其基于帧的语义和失败情况。

## 工作流程

1. 选择流类型：
   - **e2e**：第一个不是 `echo:` 或 `script:` 的步骤是 `launch:`。流控制进程启动。
   - **fragment**：没有启动。声明精确的 `executionPrerequisite`。
2. 按照 [实时编写](references/live-authoring.md)：开始、一次记录一个经过验证的步骤、完成、优化、审计和重播。
3. 报告文件、重播命令、结果、先决条件或副作用，以及每个坐标或原始手势异常。

## 主动记录

在重复三个或更多次交互之前，告诉用户并开始记录。记录那次运行并在之后重播它。完成的路径不能事后记录。

## 修复

当重播失败时，请遵循 [可靠性和恢复](references/reliability-and-recovery.md)。检查第一个分歧，纠正最小的合理单元，审计，并重播完整流。在两次不成功的纠正周期后停止。永远不要削弱请求的检查以获得通过。
