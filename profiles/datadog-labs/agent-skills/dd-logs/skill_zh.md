# Datadog 日志

进行日志搜索、处理和归档，并具备成本意识。

## 前置条件

Datadog Pup 应该已经安装。如果没有，请参考 [设置 Pup](https://github.com/datadog-labs/agent-skills/tree/main?tab=readme-ov-file#setup-pup)。

## 命令执行顺序（高效用 token）

对于作用域命令，请使用以下顺序：

1. 首先检查上下文（先前的输出、对话、保存的值）。
2. 如果必需的值缺失，请先运行发现命令。
3. 如果仍然不明确，请要求用户确认。
4. 然后运行目标命令。
5. 避免可能失败的推测性命令。

## 快速入门

```bash
pup auth login
```

## 搜索日志

```bash
# 基本搜索
pup logs search --query="status:error" --from="1h"

# 带过滤条件
pup logs search --query="service:api status:error" --from="1h" --limit 100

# JSON 输出
pup logs search --query="@http.status_code:>=500" --from="1h"
```

### 搜索语法

| 查询 | 含义 |
|-------|---------|
| `error` | 全文搜索 |
| `status:error` | 标签等于 |
| `@http.status_code:500` | 属性等于 |
| `@http.status_code:>=400` | 数值范围 |
| `service:api AND env:prod` | 布尔运算 |
| `@message:*timeout*` | 通配符 |

## 配置 API

pup 0.42.0 中可用的日志配置命令：

```bash
# 列出日志归档
pup logs archives list

# 列出日志限制查询
pup logs restriction-queries list

# 列出自定义日志目的地
pup logs custom-destinations list
```

### 常见处理器

```json
{
  "name": "API 日志",
  "filter": {"query": "service:api"},
  "processors": [
    {
      "type": "grok-parser",
      "name": "解析 nginx",
      "source": "message",
      "grok": {"match_rules": "%{IPORHOST:client_ip} %{DATA:method} %{DATA:path} %{NUMBER:status}"}
    },
    {
      "type": "status-remapper",
      "name": "设置严重性",
      "sources": ["level", "severity"]
    },
    {
      "type": "attribute-remapper",
      "name": "重映射 user_id",
      "sources": ["user_id"],
      "target": "usr.id"
    }
  ]
}
```

## 排除过滤器（成本控制）

**仅索引重要内容：**

```json
{
  "name": "丢弃 debug 日志",
  "filter": {"query": "status:debug"},
  "is_enabled": true
}
```

### 高量级排除

```bash
# 查找最嘈杂的日志源
pup logs search --query="*" --from="1h" | jq 'group_by(.service) | map({service: .[0].service, count: length}) | sort_by(-.count)[:10]'
```

| 排除 | 查询 |
|---------|-------|
| 健康检查 | `@http.url:"/health" OR @http.url:"/ready"` |
| debug 日志 | `status:debug` |
| 静态资源 | `@http.url:*.css OR @http.url:*.js` |
| 心跳 | `@message:*heartbeat*` |

## 归档

以低成本存储日志以符合合规要求：

```bash
# 列出归档
pup logs archives list

# 归档配置（S3 示例）
{
  "name": "compliance-archive",
  "query": "*",
  "destination": {
    "type": "s3",
    "bucket": "my-logs-archive",
    "path": "/datadog"
  },
  "rehydration_tags": ["team:platform"]
}
```

### 恢复（还原）

```bash
# pup 0.42.0 中没有 `pup logs rehydrate` 命令。
# 使用 Datadog UI/API 进行恢复工作流。
```

## 基于日志的指标

从日志创建指标（比索引更便宜）：

```bash
# 列出基于日志的指标
pup logs metrics list

# 通过 ID 获取一个指标
pup logs metrics get api.errors.count
```

**基数警告：** 仅对有界值进行分组。

## 敏感数据

### 清理规则

```json
{
  "type": "hash-remapper",
  "name": "哈希电子邮件",
  "sources": ["email", "@user.email"]
}
```

### 永不记录

```python
# 在您的应用中 - 发送前进行清理
import re

def sanitize_log(message: str) -> str:
    # 移除信用卡信息
    message = re.sub(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[REDACTED]', message)
    # 移除 SSN
    message = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED]', message)
    return message
```

## 故障排除

| 问题 | 解决方法 |
|---------|-----|
| 日志未出现 | 检查代理、管道过滤器 |
| 成本过高 | 添加排除过滤器 |
| 搜索缓慢 | 缩小时间范围，使用索引 |
| 属性缺失 | 检查 grok 解析器 |

## 参考/文档

- [日志搜索语法](https://docs.datadoghq.com/logs/explorer/search_syntax/)
- [管道](https://docs.datadoghq.com/logs/log_configuration/pipelines/)
- [排除过滤器](https://docs.datadoghq.com/logs/indexes/#exclusion-filters)
- [归档](https://docs.datadoghq.com/logs/archives/)
