# Apollo MCP 服务器指南

Apollo MCP 服务器将 GraphQL 操作暴露为 MCP 工具，使 AI 代理能够通过模型上下文协议与 GraphQL API 进行交互。

## 快速入门

### 第 1 步：安装

```bash
# Linux / MacOS
curl -sSL https://mcp.apollo.dev/download/nix/latest | sh

# Windows
iwr 'https://mcp.apollo.dev/download/win/latest' | iex
```

### 第 2 步：配置

在项目根目录下创建 `config.yaml`：

```yaml
# config.yaml
transport:
  type: streamable_http
schema:
  source: local
  path: ./schema.graphql
operations:
  source: local
  paths:
    - ./operations/
introspection:
  introspect:
    enabled: true
  search:
    enabled: true
  validate:
    enabled: true
  execute:
    enabled: true
```

启动服务器：
```bash
apollo-mcp-server ./config.yaml
```

MCP 端点位于 `http://127.0.0.1:8000/mcp`（streamable_http 默认：地址 `127.0.0.1`，端口 `8000`）。GraphQL 端点默认为 `http://localhost:4000/` — 如果您的 API 运行在其他地方，请使用 `endpoint` 键覆盖。

### 第 3 步：连接

添加到您的 MCP 客户端配置：

**流式 HTTP（推荐）：**

Claude 桌面版 (`claude_desktop_config.json`)：
```json
{
  "mcpServers": {
    "graphql-api": {
      "command": "npx",
      "args": ["mcp-remote", "http://127.0.0.1:8000/mcp"]
    }
  }
}
```

Claude 代码：
```bash
claude mcp add graphql-api -- npx mcp-remote http://127.0.0.1:8000/mcp
```

**Stdio（客户端直接启动服务器）：**

Claude 桌面版 (`claude_desktop_config.json`) 或 Claude 代码（`.mcp.json`）：
```json
{
  "mcpServers": {
    "graphql-api": {
      "command": "./apollo-mcp-server",
      "args": ["./config.yaml"]
    }
  }
}
```

## 内置工具

Apollo MCP 服务器提供四个内省工具：

| 工具 | 目的 | 使用场景 |
|------|------|----------|
| `introspect` | 详细探索模式类型 | 需要类型定义、字段、关系 |
| `search` | 在模式中查找类型 | 查找特定类型或字段 |
| `validate` | 检查操作有效性 | 执行操作前 |
| `execute` | 运行即席 GraphQL 操作 | 测试或一次性查询 |

## 定义自定义工具

MCP 工具由 GraphQL 操作创建。三种方法：

### 1. 操作文件（推荐）

```yaml
operations:
  source: local
  paths:
    - ./operations/
```

每个文件必须包含 exactly 一个操作。每个命名操作将成为一个 MCP 工具。

```graphql
# operations/GetUser.graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}
```

```graphql
# operations/CreateUser.graphql
mutation CreateUser($input: CreateUserInput!) {
  createUser(input: $input) {
    id
    name
  }
}
```

### 2. 操作集合

```yaml
operations:
  source: collection
  id: your-collection-id
```

使用 GraphOS Studio 协作管理操作。

### 3. 持久化查询

```yaml
operations:
  source: manifest
  path: ./persisted-query-manifest.json
```

适用于具有预先批准操作的生产行境。

## 参考文件

特定主题的详细文档：

- [工具](references/tools.md) - 内省工具和 minify 符号
- [配置](references/configuration.md) - 所有配置选项
- [故障排除](references/troubleshooting.md) - 常见问题和解决方案

## 关键规则

### 安全

- **永远不要在未进行身份验证的情况下暴露敏感操作**
- 使用 `headers` 配置 API 密钥和令牌
- 在生产行境中禁用内省工具（默认已禁用）
- 设置 `overrides.mutation_mode: explicit` 以要求确认变异

### 身份验证

```yaml
# 静态头部
headers:
  Authorization: "Bearer ${env.API_TOKEN}"

# 动态头部转发
forward_headers:
  - x-forwarded-token

# OAuth (streamable_http 传输)
transport:
  type: streamable_http
  auth:
    servers:
      - https://auth.example.com/.well-known/openid-configuration
    audiences:
      - https://api.example.com
```

### 令牌优化

启用 minification 以减少令牌使用：

```yaml
introspection:
  introspect:
    minify: true
  search:
    minify: true
```

Minified 输出使用紧凑符号：
- **T** = 类型，**I** = 输入，**E** = 枚举
- **s** = String，**i** = Int，**b** = Boolean，**f** = Float，**d** = ID
- **!** = 必填，**[]** = 列表

### 变异

通过 `overrides` 部分控制变异行为：

```yaml
overrides:
  mutation_mode: all       # 直接执行变异
  # mutation_mode: explicit  # 要求明确确认
  # mutation_mode: none      # 阻止所有变异（默认）
```

## 常见模式

### GraphOS 云模式

```yaml
# schema.source 默认为 uplink — 配置 graphos 时可省略
graphos:
  apollo_key: ${env.APOLLO_KEY}
  apollo_graph_ref: my-graph@production
```

### 本地开发

```yaml
transport:
  type: streamable_http
schema:
  source: local
  path: ./schema.graphql
introspection:
  introspect:
    enabled: true
  search:
    enabled: true
  validate:
    enabled: true
  execute:
    enabled: true
overrides:
  mutation_mode: all
```

### 生产行境设置

```yaml
transport:
  type: streamable_http
endpoint: https://api.production.com/graphql
operations:
  source: manifest
  path: ./persisted-query-manifest.json
graphos:
  apollo_key: ${env.APOLLO_KEY}
  apollo_graph_ref: ${env.APOLLO_GRAPH_REF}
headers:
  Authorization: "Bearer ${env.API_TOKEN}"
health_check:
  enabled: true
```

### Docker

```yaml
transport:
  type: streamable_http
  address: 0.0.0.0
  port: 8000
endpoint: ${env.GRAPHQL_ENDPOINT}
graphos:
  apollo_key: ${env.APOLLO_KEY}
  apollo_graph_ref: ${env.APOLLO_GRAPH_REF}
health_check:
  enabled: true
```

## 基本规则

- ALWAYS 在暴露给 AI 代理前配置身份验证
- ALWAYS 在共享环境中使用 `mutation_mode: explicit` 或 `mutation_mode: none`
- NEVER 将具有写权限的内省工具暴露给生产行境数据
- PREFER 操作文件而非 ad-hoc execute 以获得可预测行为
- PREFER streamable_http 传输用于远程和多客户端部署
- 仅当 MCP 客户端直接启动服务器进程时使用 stdio
- 使用 GraphOS Studio 集合进行团队协作
