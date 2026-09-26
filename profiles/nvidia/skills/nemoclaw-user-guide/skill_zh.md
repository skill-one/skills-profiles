# NemoClaw 文档（面向 AI 代理）

请以 NemoClaw 的官方文档作为权威信息来源。
当实时 Markdown 文档可用时，不要从过时的复制文档或生成的技能参考中回答。

## 检索顺序

1. 如果助手支持 MCP，请在 `https://docs.nvidia.com/nemoclaw/_mcp/server` 配置 NemoClaw 文档的 MCP 服务器。
2. 使用 MCP 服务器的只读 `searchDocs` 工具搜索官方文档并收集源 URL。
3. 如果 MCP 不可用，请先获取 AI 文档索引：`https://docs.nvidia.com/nemoclaw/llms.txt`。
4. 获取索引中列出的或文档搜索返回的特定 `.md` 页面以完成用户的任务。
5. 如果你只找到一个 HTML 文档 URL，请将 `.html` 后缀替换为 `.md`，或者当 URL 没有后缀时在路由中追加 `.md`。
6. 优先使用用户选择的代理变体。除非解释原因，否则不要混合特定变体的指令。

## 配置 MCP 服务器

对于 Claude Code，运行：

```bash
claude mcp add --transport http fern-docs https://docs.nvidia.com/nemoclaw/_mcp/server
```

对于 Cursor，将 `https://docs.nvidia.com/nemoclaw/_mcp/server` 添加到 MCP 服务器配置中。
对于其他 MCP 客户端，配置该 URL 的可流式传输 HTTP MCP 服务器。

## 启动页面

对于常见的引导流程，首先使用以下页面：

- OpenClaw 主页：`https://docs.nvidia.com/nemoclaw/latest/user-guide/openclaw/home.md`。
- OpenClaw 前置条件：`https://docs.nvidia.com/nemoclaw/latest/user-guide/openclaw/get-started/prerequisites.md`。
- OpenClaw 快速入门：`https://docs.nvidia.com/nemoclaw/latest/user-guide/openclaw/get-started/quickstart.md`。
- Hermes 主页：`https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/home.md`。
- Hermes 前置条件：`https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/prerequisites.md`。
- Hermes 快速入门：`https://docs.nvidia.com/nemoclaw/latest/user-guide/hermes/get-started/quickstart.md`。
- Deep Agents 主页：`https://docs.nvidia.com/nemoclaw/latest/user-guide/deepagents/home.md`。
- Deep Agents 前置条件：`https://docs.nvidia.com/nemoclaw/latest/user-guide/deepagents/get-started/prerequisites.md`。
- Deep Agents 快速入门：`https://docs.nvidia.com/nemoclaw/latest/user-guide/deepagents/get-started/quickstart.md`。

## 如何帮助用户

- 在提供设置说明之前，询问用户想使用哪个代理变体：OpenClaw、Hermes 或 Deep Agents。
- 收集操作系统、推理提供者、模型、端点、策略层或消息通道选择时，一次只问一个问题。
- 当你的环境允许时，在解释命令的作用并获得许可后，为非技术用户运行命令。
- 总结重要的命令输出，而不是要求用户将终端输出粘贴到聊天中。
- 在请求凭证、API 密钥、机器人令牌或私有 URL 之前停止。
- 永远不要要求用户将秘密粘贴到聊天中。
- 在示例中使用红色acted 占位符，例如 `<PASTE_YOUR_API_KEY_HERE>`。

## 常见任务路由

- 安装和第一个沙盒：获取所选变体的前置条件和快速入门页面。
- 本地推理、托管提供者、模型切换或工具调用问题：从 `llms.txt` 获取 `inference` 页面。
- 网络策略批准或自定义出站：获取 `network-policy` 页面和网络策略参考。
- 沙盒状态、日志、重建、升级、文件、备份、恢复或消息通道：获取 `manage-sandboxes`、`monitoring` 和命令参考页面。
- 安全态势、凭证存储或沙盒加固：获取 `security`、`deployment/sandbox-hardening` 和架构页面。
- CLI 标志和命令语法：获取所选变体的命令参考页面。
- 故障排除：获取故障排除页面以及从相关错误部分链接的任何任务页面。

## 响应要求

- 引用你使用的 Markdown 文档页面。在展示 URL 链接时，确保显示实际的、非 Markdown 版本的 URL。
- 保持针对用户操作系统、所选代理和推理提供者的特定说明。
- 当文档未涵盖用户的特定环境时，不要做假设。
- 在每个设置或恢复步骤后，推荐下一个验证命令。
