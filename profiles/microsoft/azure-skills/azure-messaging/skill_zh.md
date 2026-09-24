# Azure 消息服务 SDK 故障排除

## 快速参考

| 属性 | 值 |
|----------|-------|
| **服务** | Azure Event Hubs, Azure Service Bus |
| **MCP 工具** | `mcp_azure_mcp_eventhubs`, `mcp_azure_mcp_servicebus` |
| **适用于** | 诊断 SDK 连接、认证和消息处理问题 |

## 何时使用本技能

- SDK 连接失败、认证错误或 AMQP 链路错误
- 空闲超时、连接不活跃，或断开后重连缓慢
- AMQP 链路断开或强制断开错误
- 消息锁丢失、消息锁过期、锁续期失败或批锁超时
- 会话锁丢失、会话锁过期或会话接收器错误
- 事件处理器或消息处理器停止处理
- 事件重复或检查点偏移量重置
- SDK 配置问题（重试、预取、批大小、接收批行为）

## MCP 工具

| 工具 | 命令 | 用途 |
|------|---------|-----|
| `mcp_azure_mcp_eventhubs` | 命名空间/枢纽操作 | 列出命名空间、枢纽、消费者组 |
| `mcp_azure_mcp_servicebus` | 队列/主题操作 | 列出命名空间、队列、主题、订阅 |
| `mcp_azure_mcp_monitor` | `logs_query` | 使用 KQL 查询诊断日志 |
| `mcp_azure_mcp_resourcehealth` | `get` | 检查服务健康状态 |
| `mcp_azure_mcp_documentation` | Doc search | 在 Microsoft Learn 中搜索故障排除文档 |

## 诊断工作流程

1. **确定 SDK 及版本** — 检查提示词中是否有 SDK 及版本的线索；如未提及，则继续诊断，如有需要后续再询问
2. **检查资源健康** — 使用 `mcp_azure_mcp_resourcehealth` 验证命名空间是否健康
3. **审查错误信息** — 与语言特定的故障排除指南进行匹配
4. **查阅文档** — 使用 `mcp_azure_mcp_documentation` 在 Microsoft Learn 中搜索该错误或主题
5. **检查配置** — 验证连接字符串、实体名称、消费者组
6. **推荐修复方案** — 应用修复方案，并引用已找到的文档

## 故障排除指南

连接性、SDK 和认证故障排除指南位于 `azure-diagnostics` 技能的 `troubleshooting/messaging/` 目录下。

## 参考资料

- 使用 `mcp_azure_mcp_documentation` 在 Microsoft Learn 中搜索最新指引。
