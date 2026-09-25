## 何时使用

- 用户需要访问或与外部应用交互（如 Gmail、Slack、GitHub、Notion 等）
- 用户希望通过外部服务自动化任务（发送邮件、创建问题、发布消息）
- 构建与外部工具集成的 AI 代理或应用
- 需要为每个用户连接外部服务的多用户应用

## 设置

检查 CLI 是否已安装；若未安装，请安装：
```bash
curl -fsSL https://composio.dev/install | bash
```

安装完成后，重启终端或源代码配置文件，然后进行身份验证：
```bash
composio login       # OAuth；交互式组织/项目选择器（使用 -y 跳过）
composio whoami      # 验证 org_id、project_id、user_id
```
对于没有直接浏览器访问权限的代理：`composio login --no-wait | jq` 获取 URL/密钥，与用户共享 URL，然后在他们完成登录后使用 `composio login --key <cli_key> --no-wait`。

---

### 1. 通过 Composio CLI 使用应用

**使用场景：** 用户需要直接对外部应用执行操作——无需编写代码。代理使用 CLI 搜索、连接并代表用户执行工具。

关键命令（新的顶级别名）：
- `composio search "<query>"` — 按用例查找工具
- `composio execute "<TOOL_SLUG>" -d '{...<输入参数>}'` — 执行工具
- `composio link [toolkit]` — 将用户账户连接到应用（代理：在非交互模式下始终使用 `--no-wait`）
- `composio listen` — 监听实时触发事件

典型工作流程：**搜索 → 连接（如果需要）→ 执行**

> 完整参考：[Composio CLI 指南](rules/composio-cli.md)

---

### 2. 使用 Composio 构建应用和代理

**使用场景：** 编写代码——一个 AI 代理、应用或后端服务，通过 Composio SDK 与外部工具集成。

首先在项目目录内运行以下命令以设置 API 密钥：
```bash
composio init
```

> 完整参考：[使用 Composio 构建](rules/building-with-composio.md)
