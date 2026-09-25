# Superwall 订阅墙编辑器

订阅墙在浏览器编辑器中构建，其工具通过认证中继器暴露。该技能驱动与 MCP 网关相同的界面，因此每个工具都在用户打开的实时浏览器会话中运行。

## 使用场景

- 用户想要构建、编辑或审阅 Superwall 订阅墙、引导流程或 Web2app 流程。
- 用户粘贴了配对码并要求您接管编辑。
- 用户询问“您现在能运行哪些工具？”通过浏览器来发现，而不是凭记忆。

## 从这里开始：先附加，再发现

不要从记忆中假设工具名称或签名。浏览器是真相来源，其工具集在各个版本中会发生变化。

首选的 API 启动流程：

1. 创建自动暴露 URL：`scripts/sw-editor.sh expose --application-id <id> --paywall-id <id> --agent-name <agent> --open --wait`
2. 如果提示，请要求用户完成浏览器授权。编辑器自动暴露；不要让他们点击暴露按钮。
3. 发现当前可用的工具：`scripts/sw-editor.sh tools`
4. 调用工具：`scripts/sw-editor.sh call <tool-name> --args '<json>'`

备用手动流程：

1. 请求用户提供编辑器 UI 中显示的**配对码**。
2. 附加：`scripts/sw-editor.sh attach <pairing-code>`
3. 继续 `tools` 和 `call`。

完整的 CLI 参考：[references/cli.md](references/cli.md)。

## 如何构建和编辑

- 工作流程、构建顺序以及何时使用哪个工具：[references/workflow.md](references/workflow.md)
- 本地 `sw-*` 元素（多选、指示器、抽屉、选择器、Lottie、导航）：[references/native-elements.md](references/native-elements.md)
- 设计标准、审阅检查点、排版和转换原则：[references/design.md](references/design.md)

## 协调规则

- 在编辑前始终建立附加关系。在可能的情况下使用 `expose --open --wait`，否则使用 `attach <pairing-code>`。`tools`、`call`、`status`、`release` 都需要附加的会话。
- 当您有 `SUPERWALL_API_KEY`、应用程序 ID 和订阅墙 ID 时，优先使用 `expose --open --wait`。它使用与手动配对相同的转发器，但去除了人工配对码步骤。
- 在调用您在此会话中未使用过的工具之前，运行 `tools` 以确认其存在并读取当前参数模式。工具定义在浏览器包中，因此更新后的编辑器可以推送新的或重命名的工具，而无需更改此技能。
- 每隔两到三次修改使用 `get_screenshot`（如果工具列表中存在）进行验证。不要盲目操作。
- 优先使用语义工具（`update_styles`、`set_text_content`、`set_dynamic_value`、`move_nodes`）而不是在现有结构上重新运行 `write_html`。参见 `references/workflow.md`。
- 优先使用本地 `sw-*` 元素而不是手写的 `<div>` 重建，只要 UI 表示语义控件。参见 `references/native-elements.md`。
- 解析 CLI 输出时使用 `jq`，而不是 Python。示例：`sw-editor.sh call get_subtree --args '...' | jq -r '.content[0].text'`
- 用户完成时发布：`scripts/sw-editor.sh release`。

## 当出现问题时

- `session_not_ready`：浏览器断开连接或重新加载。要求用户将编辑器标签页恢复，然后重新附加。配对码会旋转，因此他们必须提供新的配对码。
- `session_locked`：另一个客户端已经附加。用户可能从另一个 MCP 客户端附加，或者之前的 CLI 附加未释放。他们可以从编辑器 UI 中断开连接，然后您可以重试。
- `unauthorized`：控制器令牌已过期。使用新的配对码重新附加。
- `attach_failed: provide a valid current pairingCode`：配对码在约 10 分钟后过期，并在断开连接时旋转。要求用户向您展示当前的配对码。
