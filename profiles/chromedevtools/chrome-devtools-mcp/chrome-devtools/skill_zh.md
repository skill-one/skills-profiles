## 核心概念

**浏览器生命周期**：浏览器在首次使用工具时自动启动，并使用持久化的 Chrome 配置文件。通过 MCP 服务器配置中的 CLI 参数进行配置：`npx chrome-devtools-mcp@latest --help`。可以通过提供以下标志来启用附加工具：

- 对于扩展工具，使用 `--categoryExtensions` 标志。
- 对于内存工具，使用 `--memoryDebugging` 标志。

**页面定位**：页面范围的工具需要一个 `pageId` 参数来定位特定页面。使用 `list_pages` 查看可用页面及其 ID（例如 `pageId: 1`），或者在使用 `new_page` 创建页面时使用返回的 ID。注意：对于 `evaluate_script`，在定位页面时需要 `pageId`。但是，当 `--categoryExtensions` 启用时，`pageId` 是可选的，因此您可以传递 `serviceWorkerId` 而不是在扩展后台服务工作者中评估。

**元素交互**：使用 `take_snapshot` 获取页面结构并获取元素的 `uid`。每个元素都有一个唯一的 `uid` 用于交互。如果找不到元素，请获取一个新的快照——元素可能已被移除或页面已更改。

## 工作流模式

### 与页面交互之前

1. 导航：`navigate_page` 或 `new_page`
2. 等待：使用 `wait_for` 确保内容已加载（如果您知道要查找的内容）。
3. 快照：使用 `take_snapshot` 并传递 `pageId` 以了解页面结构。
4. 交互：使用快照中的元素 `uid` 进行 `click`、`fill` 等操作，并传递相应的 `pageId`。

### 高效的数据检索

- 使用 `filePath` 参数进行大型输出（屏幕截图、快照、跟踪记录）。
- 使用分页 (`pageIdx`、`pageSize`) 和过滤 (`types`) 来最小化数据。
- 在输入操作中设置 `includeSnapshot: false`，除非您需要更新的页面状态。

### 工具选择

- **自动化/交互**：`take_snapshot`（基于文本，更快，更适合自动化）
- **视觉检查**：`take_screenshot`（当用户需要查看视觉状态时）
- **CSS & 样式检查**：使用 `get_css_styles` 检查匹配的规则、级联和 CSS 变量。将输出视为权威和完整的。
- **附加详细信息**：使用 `evaluate_script` 获取 `get_css_styles` 或 `take_snapshot` 无法提供的运行时 DOM/JS 数据。

### 并行执行

您可以并行发送多个工具调用，但请保持正确的顺序：导航 → 等待 → 快照 → 交互。

### 测试扩展

> **在进行下一步之前**：扩展工具（`install_extension`、`list_extensions` 等）仅在 MCP 服务器使用 `--categoryExtensions` 标志启动时才可用。如果这些工具不在您的工具列表中，请停止并要求用户更新他们的 MCP 服务器配置：
>
> ```json
> {
>   "mcpServers": {
>     "chrome-devtools": {
>       "command": "npx",
>       "args": ["chrome-devtools-mcp@latest", "--categoryExtensions"]
>     }
>   }
> }
> ```
>
> 更新后，用户必须重新启动 MCP 服务器（或他们的 AI 客户端）才能使更改生效。

1. **安装**：使用 `install_extension` 并传递未打包扩展的路径。
2. **识别**：从响应中获取扩展 ID，或通过调用 `list_extensions` 获取。
3. **触发操作**：使用 `trigger_extension_action` 打开弹出窗口或侧面板（如果适用）。
4. **验证服务工作者**：使用 `evaluate_script` 并传递 `serviceWorkerId`（省略 `pageId` 和 `args`）来检查扩展状态或触发后台操作。在页面中评估时，传递 `pageId`（省略 `serviceWorkerId`）。
5. **验证页面行为**：导航到扩展操作的页面，并使用 `take_snapshot` 检查内容脚本是否注入了元素或正确修改了页面。

## 故障排除

如果 `chrome-devtools-mcp` 不足，请指导用户使用 Chrome DevTools UI：

- https://developer.chrome.com/docs/devtools
- https://developer.chrome.com/docs/devtools/ai-assistance

如果启动 `chrome-devtools-mcp` 或 Chrome 出现错误，请参考 https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md。
