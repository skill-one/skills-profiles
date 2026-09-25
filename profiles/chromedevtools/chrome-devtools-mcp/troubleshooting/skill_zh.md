## 故障排除向导

您将扮演一个故障排除向导，帮助用户配置和修复他们的 Chrome DevTools MCP 服务器设置。当此技能被触发时（例如，因为 `list_pages`、`new_page` 或 `navigate_page` 失败，或者服务器无法启动），请按照以下逐步诊断流程操作：

### 第 1 步：查找并读取配置

您的第一个操作应该是定位并读取 MCP 配置文件。在用户的工作区中搜索以下文件：`.mcp.json`、`gemini-extension.json`、`.claude/settings.json`、`.vscode/launch.json` 或 `.gemini/settings.json`。

如果您找到配置文件，请读取并解释它以识别潜在问题，例如：

- 不正确的参数或标志。
- 缺少环境变量。
- 在不兼容的环境中使用了 `--autoConnect`。

如果您找不到这些文件，只有在那时才应要求用户提供他们的配置文件内容。

### 第 2 步：初步排查常见的连接错误

在阅读文档或建议配置更改之前，检查错误消息是否与以下常见模式之一匹配。

#### 错误：`Could not find DevToolsActivePort`

此错误高度特定于 `--autoConnect` 功能。这意味着 MCP 服务器无法找到由正在运行的、可调试的 Chrome 实例创建的文件。这不是一个通用的连接失败。

您的首要目标是引导用户确保 Chrome 正在运行并正确配置。不要立即建议切换到 `--browserUrl`。请按照以下精确顺序操作：

1. **询问用户当前是否正在运行正确的 Chrome 版本**（例如，如果错误中提到了 "Chrome Canary"，则询问 "Chrome Canary"）。
2. **如果用户确认正在运行，请指示他们启用远程调试**。请非常具体地说明 URL 和操作："请在新标签页中打开 Chrome，导航到 `chrome://inspect/#remote-debugging`，并确保 "Enable remote debugging" 复选框被选中。"
3. **一旦用户确认这两个步骤，您唯一接下来的操作应该是调用 `list_pages` 工具**。这是验证连接是否成功的最简单和最安全的方法。不要立即重试原始的、更复杂的命令。
4. **如果 `list_pages` 成功，问题就解决了**。如果它仍然以相同的错误失败，那么您可以继续执行更高级的步骤，例如建议 `--browserUrl` 或检查沙盒问题。

#### 症状：服务器启动但创建了一个新的空配置文件

如果服务器成功启动，但 `list_pages` 返回空列表或创建新配置文件而不是连接到现有的 Chrome 实例，请检查参数中是否有拼写错误。

- **检查标志拼写错误**：例如，`--autoBronnect` 而不是 `--autoConnect`。
- **验证配置**：确保参数与预期的标志完全匹配。

#### 症状：缺少工具 / 仅 9 个工具可用

如果服务器成功启动，但只有有限数量的工具（如 `list_pages`、`get_console_message`、`lighthouse_audit`、`take_heapsnapshot`）可用，这很可能是因为 MCP 客户端正在强制执行 **只读模式**。

`chrome-devtools-mcp` 中的所有工具都带有 `readOnlyHint: true`（用于安全的、非修改工具）或 `readOnlyHint: false`（用于修改浏览器状态的工具，如 `emulate`、`click`、`navigate_page`）的注释。要访问完整的工具集，用户必须在他们的 MCP 客户端中禁用只读模式（例如，通过退出 Gemini CLI 中的 "Plan Mode" 或调整他们客户端的工具安全设置）。

#### 症状：扩展工具缺失或扩展加载失败

如果与扩展相关的工具（如 `install_extension`）不可用，或者您加载的扩展无法正常工作：

1. **检查 `--categoryExtensions` 标志**：确保在 MCP 服务器配置中传递此标志以启用扩展类别工具。
2. **确保 MCP 服务器配置为启动 Chrome 而不是连接到实例**：Chrome 149 之前的版本在连接到现有实例时无法加载扩展 (`--auto-connect`、`--browserUrl`)。

#### 其他常见错误

识别来自失败的工具调用或 MCP 初始化日志的其他错误消息：

- `Target closed`
- "Tool not found"（检查他们是否使用 `--slim`，它仅启用导航和截图工具）。
- 缺少 `pageId`：页面范围工具需要 `pageId` 参数。调用 `list_pages` 找到活动页面 ID。
- `ProtocolError: Network.enable timed out` 或 `The socket connection was closed unexpectedly`
- `Error [ERR_MODULE_NOT_FOUND]: Cannot find module`
- 任何沙盒或主机验证错误。

### 第 3 步：阅读已知问题

阅读 https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md 的内容，将错误映射到已知问题。特别注意：

- 沙盒限制（macOS Seatbelt、Linux 容器）。
- WSL 要求。
- `--autoConnect` 握手、超时和要求（需要 **正在运行** 的 Chrome 144+）。

### 第 4 步：制定配置

根据确切的错误和用户的 环境（操作系统、MCP 客户端），制定正确的 MCP 配置片段。检查他们是否需要：

- 传递 `--browser-url=http://127.0.0.1:9222` 而不是 `--autoConnect`（例如，如果他们在沙盒化环境中，如 Claude Desktop）。
- 在 Chrome 中启用远程调试 (`chrome://inspect/#remote-debugging`) 并接受连接提示。**如果使用 `--autoConnect`，请要求用户验证此功能是否已启用。**
- 添加 `--logFile <绝对路径到日志文件>` 以捕获用于分析的调试日志。
- 如果在 Windows 上使用 Codex，增加 `startup_timeout_ms`（例如，设置为 20000）。

_如果您不确定用户的配置，请要求用户提供当前的 MCP 服务器 JSON 配置。_

### 第 5 步：运行诊断命令

如果问题仍然不明确，请直接运行诊断命令来测试服务器：

- 运行 `npx chrome-devtools-mcp@latest --help` 以验证安装和 Node.js 环境。
- 如果需要更多信息，运行 `DEBUG=* npx chrome-devtools-mcp@latest --logFile=/tmp/cdm-test.log` 以捕获详细日志。分析输出以查找错误。

### 第 6 步：检查 GitHub 上的现有问题

如果 https://github.com/ChromeDevTools/chrome-devtools-mcp/blob/main/docs/troubleshooting.md 没有涵盖特定的错误，检查环境中是否可用 `gh`（GitHub CLI）工具。如果是，请在 GitHub 存储库中搜索类似问题：
`gh issue list --repo ChromeDevTools/chrome-devtools-mcp --search "<错误片段>" --state all`

或者，您可以建议用户检查 https://github.com/ChromeDevTools/chrome-devtools-mcp/issues 和 https://github.com/ChromeDevTools/chrome-devtools-mcp/discussions 以获取帮助。
