# Azure Messaging SDK 故障排除

## 快速参考

| 属性 | 值 |
|----------|-------|
| **服务** | Azure Event Hubs, Azure Service Bus |
| **MCP 工具** | `mcp_azure_mcp_eventhubs`, `mcp_azure_mcp_servicebus` |
| **适用场景** | 诊断 SDK 连接、认证和消息处理问题 |

## 何时使用此技能

- SDK 连接失败、认证错误或 AMQP 链接错误
- 空闲超时、连接不活跃或断开连接后缓慢重连
- AMQP 链接分离或强制分离错误
- 消息锁丢失、消息锁过期、锁续期失败或批量锁超时
- 会话锁丢失、会话锁过期或会话接收器错误
- 事件处理器或消息处理器停止处理
- 重复事件或检查点偏移重置
- SDK 配置问题（重试、预取、批量大小、接收批量行为）

## MCP 工具

| 工具 | 命令 | 用途 |
|------|---------|-----|
| `mcp_azure_mcp_eventhubs` | 命名空间/中心操作 | 列出命名空间、中心、消费者组 |
| `mcp_azure_mcp_servicebus` | 队列/主题操作 | 列出命名空间、队列、主题、订阅 |
| `mcp_azure_mcp_monitor` | `logs_query` | 使用 KQL 查询诊断日志 |
| `mcp_azure_mcp_resourcehealth` | `get` | 检查服务健康状态 |
| `mcp_azure_mcp_documentation` | 文档搜索 | 在 Microsoft Learn 中搜索故障排除文档 |

## 诊断工作流

1. **识别 SDK 和版本** — 检查提示中的 SDK 和版本线索；如果未说明，则继续诊断并在需要时询问
2. **检查资源健康** — 使用 `mcp_azure_mcp_resourcehealth` 验证命名空间是否健康
3. **查看错误消息** — 与特定语言的故障排除指南进行匹配
4. **查阅文档** — 使用 `mcp_azure_mcp_documentation` 在 Microsoft Learn 中搜索错误或主题
5. **检查配置** — 验证连接字符串、实体名称、消费者组
6. **推荐修复方案** — 应用修复措施，并引用找到的文档

## 故障排除指南

连接性、SDK 和认证故障排除指南位于 azure-diagnostics 技能的 `troubleshooting/messaging/` 下。

## 参考

- 使用 `mcp_azure_mcp_documentation` 在 Microsoft Learn 中搜索最新指南。
