# Claude 代码插件的 MCP 集成

## 概述

模型上下文协议（MCP）通过提供结构化工具访问，使 Claude 代码插件能够与外部服务和 API 集成。使用 MCP 集成将外部服务功能作为工具在 Claude 代码中暴露。

**主要功能：**
- 连接到外部服务（数据库、API、文件系统）
- 从单个服务提供 10 个以上的相关工具
- 处理 OAuth 和复杂认证流程
- 将 MCP 服务器与插件捆绑以实现自动设置

## MCP 服务器配置方法

插件可以通过两种方式捆绑 MCP 服务器：

### 方法 1：专用 .mcp.json（推荐）

在插件根目录创建 .mcp.json：

```json
{
  "database-tools": {
    "command": "${CLAUDE_PLUGIN_ROOT}/servers/db-server",
    "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
    "env": {
      "DB_URL": "${DB_URL}"
    }
  }
}
```

**优点：**
- 关系明确
- 更易于维护
- 更适合多个服务器

### 方法 2：在 plugin.json 中内联

向 plugin.json 添加 mcpServers 字段：

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

**优点：**
- 单一配置文件
- 适合简单的单服务器插件

## MCP 服务器类型

### stdio（本地进程）

将本地 MCP 服务器作为子进程执行。最适合本地工具和自定义服务器。

**配置：**
```json
{
  "filesystem": {
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-filesystem", "/allowed/path"],
    "env": {
      "LOG_LEVEL": "debug"
    }
  }
}
```

**用例：**
- 文件系统访问
- 本地数据库连接
- 自定义 MCP 服务器
- NPM 打包的 MCP 服务器

**进程管理：**
- Claude 代码启动和管理进程
- 通过 stdin/stdout 通信
- 当 Claude 代码退出时终止

### SSE（服务器发送事件）

连接到支持 OAuth 的托管 MCP 服务器。最适合云服务。

**配置：**
```json
{
  "hosted-service": {
    "type": "sse",
    "url": "https://mcp.example.com/sse"
  }
}
```

**用例：**
- 官方托管 MCP 服务器（Asana、GitHub 等）
- 具有 MCP 端点的云服务
- OAuth 基于的认证
- 无需本地安装

**认证：**
- Claude 代码自动处理 OAuth 流程
- 首次使用时用户在浏览器中认证
- 令牌由 Claude 代码管理

### HTTP（REST API）

连接到具有令牌认证的 RESTful MCP 服务器。

**配置：**
```json
{
  "api-service": {
    "type": "http",
    "url": "https://api.example.com/mcp",
    "headers": {
      "Authorization": "Bearer ${API_TOKEN}",
      "X-Custom-Header": "value"
    }
  }
}
```

**用例：**
- 基于 REST API 的 MCP 服务器
- 令牌认证
- 自定义 API 后端
- 状态无关交互

### WebSocket（实时）

连接到 WebSocket MCP 服务器以实现实时双向通信。

**配置：**
```json
{
  "realtime-service": {
    "type": "ws",
    "url": "wss://mcp.example.com/ws",
    "headers": {
      "Authorization": "Bearer ${TOKEN}"
    }
  }
}
```

**用例：**
- 实时数据流
- 持久连接
- 服务器推送通知
- 低延迟需求

## 环境变量扩展

所有 MCP 配置都支持环境变量替换：

**${CLAUDE_PLUGIN_ROOT}** - 插件目录（始终用于可移植性）：
```json
{
  "command": "${CLAUDE_PLUGIN_ROOT}/servers/my-server"
}
```

**用户环境变量** - 来自用户 shell：
```json
{
  "env": {
    "API_KEY": "${MY_API_KEY}",
    "DATABASE_URL": "${DB_URL}"
  }
}
```

**最佳实践：** 在插件 README 中记录所有必需的环境变量。

## MCP 工具命名

当 MCP 服务器提供工具时，它们会自动添加前缀：

**格式：** `mcp__plugin_<plugin-name>_<server-name>__<tool-name>`

**示例：**
- 插件：`asana`
- 服务器：`asana`
- 工具：`create_task`
- **完整名称：** `mcp__plugin_asana_asana__asana_create_task`

### 在命令中使用 MCP 工具

在命令 frontmatter 中预允许特定 MCP 工具：

```markdown
---
allowed-tools: [
  "mcp__plugin_asana_asana__asana_create_task",
  "mcp__plugin_asana_asana__asana_search_tasks"
]
---
```

**通配符（谨慎使用）：**
```markdown
---
allowed-tools: ["mcp__plugin_asana_asana__*"]
---
```

**最佳实践：** 预允许特定工具，而不是通配符，以确保安全。

## 生命周期管理

**自动启动：**
- 插件启用时 MCP 服务器启动
- 在首次使用工具前建立连接
- 配置更改需要重启

**生命周期：**
1. 插件加载
2. 解析 MCP 配置
3. 启动服务器进程（stdio）或建立连接（SSE/HTTP/WS）
4. 发现并注册工具
5. 工具作为 `mcp__plugin_...__...` 可用

**查看服务器：**
使用 `/mcp` 命令查看所有服务器，包括插件提供的服务器。

## 认证模式

### OAuth（SSE/HTTP）

Claude 代码自动处理 OAuth：

```json
{
  "type": "sse",
  "url": "https://mcp.example.com/sse"
}
```

用户在首次使用时在浏览器中认证。无需额外配置。

### 令牌认证（Headers）

静态或环境变量令牌：

```json
{
  "type": "http",
  "url": "https://api.example.com",
  "headers": {
    "Authorization": "Bearer ${API_TOKEN}"
  }
}
```

在 README 中记录所需环境变量。

### 环境变量（stdio）

将配置传递给 MCP 服务器：

```json
{
  "command": "python",
  "args": ["-m", "my_mcp_server"],
  "env": {
    "DATABASE_URL": "${DB_URL}",
    "API_KEY": "${API_KEY}",
    "LOG_LEVEL": "info"
  }
}
```

## 集成模式

### 模式 1：简单工具包装器

命令使用 MCP 工具并涉及用户交互：

```markdown
# 命令：create-item.md
---
allowed-tools: ["mcp__plugin_name_server__create_item"]
---

步骤：
1. 从用户收集项目详情
2. 使用 mcp__plugin_name_server__create_item
3. 确认创建
```

**用于：** 在 MCP 调用之前添加验证或预处理。

### 模式 2：自主代理

代理自主使用 MCP 工具：

```markdown
# 代理：data-analyzer.md

分析过程：
1. 通过 mcp__plugin_db_server__query 查询数据
2. 处理和分析结果
3. 生成洞察报告
```

**用于：** 无需用户交互的多步 MCP 工作流。

### 模式 3：多服务器插件

集成多个 MCP 服务器：

```json
{
  "github": {
    "type": "sse",
    "url": "https://mcp.github.com/sse"
  },
  "jira": {
    "type": "sse",
    "url": "https://mcp.jira.com/sse"
  }
}
```

**用于：** 跨多个服务的流程。

## 安全最佳实践

### 使用 HTTPS/WSS

始终使用安全连接：

```json
✅ "url": "https://mcp.example.com/sse"
❌ "url": "http://mcp.example.com/sse"
```

### 令牌管理

**DO:**
- ✅ 使用环境变量存储令牌
- ✅ 在 README 中记录所需环境变量
- ✅ 让 OAuth 流程处理认证

**DON'T:**
- ❌ 在配置中硬编码令牌
- ❌ 将令牌提交到 git
- ❌ 在文档中共享令牌

### 权限范围

预允许必要的 MCP 工具：

```markdown
✅ allowed-tools: [
  "mcp__plugin_api_server__read_data",
  "mcp__plugin_api_server__create_item"
]

❌ allowed-tools: ["mcp__plugin_api_server__*"]
```

## 错误处理

### 连接失败

处理 MCP 服务器不可用：
- 在命令中提供回退行为
- 告知用户连接问题
- 检查服务器 URL 和配置

### 工具调用错误

处理失败的 MCP 操作：
- 在调用 MCP 工具前验证输入
- 提供清晰的错误消息
- 检查速率限制和配额

### 配置错误

验证 MCP 配置：
- 开发过程中测试服务器连接
- 验证 JSON 语法
- 检查所需环境变量

## 性能考虑

### 懒加载

MCP 服务器按需连接：
- 并非所有服务器在启动时连接
- 首次使用工具时触发连接
- 连接池自动管理

### 批处理

尽可能批量处理类似请求：

```
# 良好：带过滤器的单个查询
tasks = search_tasks(project="X", assignee="me", limit=50)

# 避免：许多单个查询
for id in task_ids:
    task = get_task(id)
```

## 测试 MCP 集成

### 本地测试

1. 在 .mcp.json 中配置 MCP 服务器
2. 本地安装插件（.claude-plugin/）
3. 运行 `/mcp` 以验证服务器出现
4. 在命令中测试工具调用
5. 查看 `claude --debug` 日志以检查连接问题

### 验证清单

- [ ] MCP 配置是有效的 JSON
- [ ] 服务器 URL 正确且可访问
- [ ] 记录所需环境变量
- [ ] 工具出现在 `/mcp` 输出中
- [ ] 认证工作（OAuth 或令牌）
- [ ] 命令中的工具调用成功
- [ ] 优雅处理错误情况

## 调试

### 启用调试日志

```bash
claude --debug
```

查找：
- MCP 服务器连接尝试
- 工具发现日志
- 认证流程
- 工具调用错误

### 常见问题

**服务器无法连接：**
- 检查 URL 是否正确
- 验证服务器正在运行（stdio）
- 检查网络连接
- 审查认证配置

**工具不可用：**
- 验证服务器连接成功
- 检查工具名称是否完全匹配
- 运行 `/mcp` 查看可用工具
- 配置更改后重启 Claude 代码

**认证失败：**
- 清除缓存的认证令牌
- 重新认证
- 检查令牌范围和权限
- 验证环境变量设置

## 快速参考

### MCP 服务器类型

| 类型 | 传输 | 最适合 | 认证 |
|------|------|--------|------|
| stdio | 进程 | 本地工具、自定义服务器 | 环境变量 |
| SSE | HTTP | 托管服务、云 API | OAuth |
| HTTP | REST | API 后端、令牌认证 | 令牌 |
| ws | WebSocket | 实时、流 | 令牌 |

### 配置清单

- [ ] 指定服务器类型（stdio/SSE/HTTP/ws）
- [ ] 完成类型特定字段（command 或 url）
- [ ] 配置认证
- [ ] 记录环境变量
- [ ] 使用 HTTPS/WSS（不使用 HTTP/WS）
- [ ] 使用 ${CLAUDE_PLUGIN_ROOT} 路径

### 最佳实践

**DO:**
- ✅ 使用 ${CLAUDE_PLUGIN_ROOT} 用于可移植路径
- ✅ 记录所需环境变量
- ✅ 使用安全连接（HTTPS/WSS）
- ✅ 在命令中预允许特定 MCP 工具
- ✅ 发布前测试 MCP 集成
- ✅ 优雅处理连接和工具错误

**DON'T:**
- ❌ 硬编码绝对路径
- ❌ 将凭证提交到 git
- ❌ 使用 HTTP 而不是 HTTPS
- ❌ 使用通配符预允许所有工具
- ❌ 忽略错误处理
- ❌ 忘记记录设置

## 额外资源

### 参考文件

有关详细信息，请参阅：

- **`references/server-types.md`** - 深入探讨每种服务器类型
- **`references/authentication.md`** - 认证模式和 OAuth
- **`references/tool-usage.md`** - 在命令和代理中使用 MCP 工具

### 示例配置

`examples/` 中的工作示例：

- **`stdio-server.json`** - 本地 stdio MCP 服务器
- **`sse-server.json`** - 带有 OAuth 的托管 SSE 服务器
- **`http-server.json`** - 带令牌认证的 REST API

### 外部资源

- **官方 MCP 文档**：https://modelcontextprotocol.io/
- **Claude 代码 MCP 文档**：https://docs.claude.com/en/docs/claude-code/mcp
- **MCP SDK**：@modelcontextprotocol/sdk
- **测试**：使用 `claude --debug` 和 `/mcp` 命令

## 实现工作流

向插件添加 MCP 集成：

1. 选择 MCP 服务器类型（stdio、SSE、HTTP、ws）
2. 在插件根目录创建 .mcp.json 配置
3. 使用 ${CLAUDE_PLUGIN_ROOT} 引用所有文件
4. 在 README 中记录所需环境变量
5. 使用 `/mcp` 命令本地测试
6. 在相关命令中预允许 MCP 工具
7. 处理认证（OAuth 或令牌）
8. 测试错误情况（连接失败、认证错误）
9. 在插件 README 中记录 MCP 集成

专注于 stdio 用于自定义/本地服务器，SSE 用于带 OAuth 的托管服务。
