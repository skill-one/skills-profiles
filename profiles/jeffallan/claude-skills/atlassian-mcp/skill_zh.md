# Atlassian MCP 专家

## 何时使用此技能

- 使用 JQL 过滤器查询 Jira 问题
- 搜索或创建 Confluence 页面
- 自动化冲刺工作流和看板管理
- 设置 MCP 服务器认证（OAuth/API 令牌）
- 将会议记录同步到 Jira 问题
- 从问题数据生成文档
- 调试 Atlassian API 集成问题
- 在官方和开源 MCP 服务器之间进行选择

## 核心工作流

1. **选择服务器** - 选择官方云、开源或自托管 MCP 服务器
2. **认证** - 配置 OAuth 2.1、API 令牌或 PAT 凭证
3. **设计查询** - 编写 Jira 的 JQL、Confluence 的 CQL；在完整执行前使用 `maxResults=1` 进行验证
4. **实现工作流** - 构建工具调用、处理分页、错误恢复
5. **验证权限** - 在任何写入或批量操作前，使用只读探测确认所需范围
6. **部署** - 配置 IDE 集成、测试权限、监控速率限制

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|------|
| 服务器设置 | `references/mcp-server-setup.md` | 安装、选择服务器、配置 |
| Jira 操作 | `references/jira-queries.md` | JQL 语法、问题 CRUD、冲刺、看板、问题链接 |
| Confluence 操作 | `references/confluence-operations.md` | CQL 搜索、页面创建、空间、评论 |
| 认证 | `references/authentication-patterns.md` | OAuth 2.0、API 令牌、权限范围 |
| 常见工作流 | `references/common-workflows.md` | 问题分派、文档同步、冲刺自动化 |

## 快速入门示例

### JQL 查询示例
```
# 当前用户在冲刺中分配的未关闭问题
project = PROJ AND status = "In Progress" AND assignee = currentUser() ORDER BY priority DESC

# 过去 7 天创建的未解决 Bug
project = PROJ AND issuetype = Bug AND status != Done AND created >= -7d ORDER BY created DESC

# 批量操作前验证：先用 maxResults=1 测试
project = PROJ AND sprint in openSprints() AND status = Open ORDER BY created DESC
```

### CQL 查询示例
```
# 最近在特定空间中更新的页面
space = "ENG" AND type = page AND lastModified >= "2024-01-01" ORDER BY lastModified DESC

# 搜索页面文本中的关键词
space = "ENG" AND type = page AND text ~ "deployment runbook"
```

### 最小 MCP 服务器配置
```json
{
  "mcpServers": {
    "atlassian": {
      "command": "npx",
      "args": ["-y", "@sooperset/mcp-atlassian"],
      "env": {
        "JIRA_URL": "https://your-domain.atlassian.net",
        "JIRA_EMAIL": "user@example.com",
        "JIRA_API_TOKEN": "${JIRA_API_TOKEN}",
        "CONFLUENCE_URL": "https://your-domain.atlassian.net/wiki",
        "CONFLUENCE_EMAIL": "user@example.com",
        "CONFLUENCE_API_TOKEN": "${CONFLUENCE_API_TOKEN}"
      }
    }
  }
}
```
> **注意：** 始终从环境变量或密钥管理器加载 `JIRA_API_TOKEN` 和 `CONFLUENCE_API_TOKEN` — 绝不硬编码凭证。

## 限制

### 必须做
- 尊重用户权限和工作区访问控制
- 在执行前验证 JQL/CQL 查询（先用 `maxResults=1` 探测）
- 使用指数退避处理速率限制
- 对大结果集使用分页（每页 50-100 条项）
- 实现网络故障的错误恢复
- 记录 API 调用以供调试和审计追踪
- 首先使用只读操作进行测试
- 记录所需的权限范围
- 在对生产数据进行任何写入或批量操作前确认

### 绝不能做
- 在代码中硬编码 API 令牌或 OAuth 密钥
- 忽略 Atlassian API 的速率限制头信息
- 在未验证必填字段的情况下创建问题
- 对用户提供的查询字符串跳过输入清理
- 在未测试权限边界的情况下部署
- 在未确认提示的情况下更新生产数据
- 在同一会话中混合不同的认证方法
- 在日志或错误消息中暴露敏感问题数据

## 输出模板

在实现 Atlassian MCP 功能时，提供：
1. MCP 服务器配置（JSON/环境变量）
2. 查询示例（带解释的 JQL/CQL）
3. 带错误处理的工具调用实现
4. 认证设置说明
5. 权限要求的简要说明

[文档](https://jeffallan.github.io/claude-skills/skills/platform/atlassian-mcp/)
