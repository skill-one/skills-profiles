# Datadog 文档

使用此技能查找 Datadog 文档和限制。

## LLM 友好型文档

Datadog 提供了一个针对 LLM 优化的文档索引，位于：

```
https://docs.datadoghq.com/llms.txt
```

该文件包含：
- 按用例组织的所有 Datadog 产品的概述
- 带有 URL 和描述的文档页面完整列表
- 直接链接到 Markdown 源代码（将 `.md` 添加到 URL）

### 如何使用 llms.txt

1. **获取索引**以了解可用的文档：
   ```bash
   curl -s https://docs.datadoghq.com/llms.txt | head -100
   ```

2. **搜索特定主题**：

示例：

   ```bash
   curl -s https://docs.datadoghq.com/llms.txt | grep -i "monitors"
   curl -s https://docs.datadoghq.com/llms.txt | grep -i "apm"
   curl -s https://docs.datadoghq.com/llms.txt | grep -i "logs"
   ```

3. **获取特定文档页面**（将 `.md` 添加到大多数 Datadog Docs URL 以获取原始内容）：
   ```bash
   curl -s https://docs.datadoghq.com/monitors.md
   curl -s https://docs.datadoghq.com/tracing.md
   ```

### 主要文档部分

| 主题 | URL |
|-------|-----|
| APM/追踪 | https://docs.datadoghq.com/tracing/ |
| 日志 | https://docs.datadoghq.com/logs/ |
| 指标 | https://docs.datadoghq.com/metrics/ |
| 监控 | https://docs.datadoghq.com/monitors/ |
| 仪表板 | https://docs.datadoghq.com/dashboards/ |
| 安全 | https://docs.datadoghq.com/security/ |
| 合成测试 | https://docs.datadoghq.com/synthetics/ |
| RUM | https://docs.datadoghq.com/real_user_monitoring/ |
| 事件 | https://docs.datadoghq.com/service_management/incident_management/ |
| API 参考 | https://docs.datadoghq.com/api/ |

## 范围限制

- 使用 llms.txt 进行文档查找
- 对于功能可用性和限制，请参考官方文档

## 故障处理

- 如果无法访问 docs.datadoghq.com，请检查网络连接
- 对于区域特定文档，请使用相应的站点（datadoghq.eu 等）
