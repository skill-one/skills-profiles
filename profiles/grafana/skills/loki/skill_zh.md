# Grafana Loki - 日志聚合

> **文档**: https://grafana.com/docs/loki/latest/

仅索引元数据（标签），不索引完整日志内容——比全文检索系统便宜得多。

## LogQL 快速参考

### 日志流选择器（每个查询都必须使用）

```logql
{app="nginx"}                        # 精确匹配
{app!="nginx"}                       # 不等于
{app=~"nginx|apache"}               # 正则表达式匹配
{app!~"debug.*"}                     # 正则表达式不匹配
{app="nginx", env="prod"}           # AND（多个标签）
```

### 行过滤器（管道阶段 1 - 为性能优先放置）

```logql
{app="nginx"} |= "error"            # 包含字符串
{app="nginx"} != "info"             # 不包含
{app="nginx"} |~ "error|warn"       # 正则表达式匹配
{app="nginx"} !~ "health.*check"    # 正则表达式不匹配
{app="nginx"} |= `"status":5`       # 反引号避免转义
```

### 解析器

```logql
# JSON
{app="api"} | json
{app="api"} | json status="http_status", path="request.path"

# Logfmt
{app="api"} | logfmt
{app="api"} | logfmt --strict
{app="api"} | logfmt --keep-empty

# Pattern（位置参数，_丢弃）
{app="nginx"} | pattern `<ip> - - <_> "<method> <uri> <_>" <status> <bytes>`

# Regexp（命名捕获组）
{app="nginx"} | regexp `(?P<method>\w+) (?P<path>\S+) HTTP/(?P<version>\S+)`

# Unpack（解包 Promtail 打包的标签）
{app="api"} | unpack
```

### 标签过滤器（解析器之后）

```logql
{app="api"} | json | status >= 500
{app="api"} | json | status == 200 and method != "OPTIONS"
{app="api"} | logfmt | duration > 1s
{app="api"} | json | level =~ "error|warn"
{app="api"} | json | bytes > 20MB
{app="api"} | json | path != "/healthz"
```

### 行格式

```logql
{app="api"} | json | line_format "{{.method}} {{.path}} -> {{.status}} ({{.duration}})"
{app="api"} | logfmt | line_format `{{.level | upper}}: {{.msg}}`
```

### 标签格式

```logql
{app="api"} | logfmt | label_format new_name=old_name
{app="api"} | logfmt | label_format severity=level, svc=app
{app="api"} | logfmt | label_format msg=`{{.level}}: {{.message}}`
```

### 丢弃/保留标签

```logql
{app="api"} | json | drop filename, level="debug"
{app="api"} | json | keep level, status, method
```

### 去色

```logql
{app="cli-tool"} | decolorize
```

## 指标查询

### 日志范围聚合

```logql
# 每秒请求次数
rate({app="nginx"}[5m])

# 窗口内的总日志行数
count_over_time({app="nginx"}[1h])

# 每秒字节数
bytes_rate({app="nginx"}[5m])

# 总字节数
bytes_over_time({app="nginx"}[1h])

# 在范围内无日志时返回 1（用于缺失告警）
absent_over_time({app="nginx"}[5m])
```

### 聚合

```logql
# 按服务错误率
sum(rate({env="prod"} |= "error" [5m])) by (app)

# 最活跃的 5 个服务
topk(5, sum(rate({env="prod"}[5m])) by (app))

# 所有服务的总错误数
sum(count_over_time({env="prod"} |= "error" [5m]))
```

### 解包范围聚合（来自日志的数值）

```logql
# 从 logfmt 获取平均请求持续时间
avg_over_time({app="api"} | logfmt | unwrap duration [5m])

# 95% 延迟分位数
quantile_over_time(0.95, {app="api"} | logfmt | unwrap duration [5m]) by (app)

# 从 JSON 日志获取字节总和
sum_over_time({app="api"} | json | unwrap bytes [5m])

# 带转换（持续时间字符串→秒）
avg_over_time({app="api"} | logfmt | unwrap duration | duration_seconds [5m])
```

### 偏移修饰符

```logql
# 比较当前速率与 1 小时前
rate({app="nginx"}[5m]) / rate({app="nginx"}[5m] offset 1h)
```

## 实用示例

### 错误率告警查询
```logql
sum(rate({env="prod"} |= "error" [5m])) by (service)
/
sum(rate({env="prod"}[5m])) by (service)
> 0.05
```

### 慢请求
```logql
{app="api"} | logfmt | duration > 1s | line_format "SLOW: {{.method}} {{.path}} {{.duration}}"
```

### HTTP 5xx 错误及详情
```logql
{app="nginx"} | pattern `<ip> - - <_> "<method> <uri> <_>" <status> <bytes>` | status >= 500
```

### 凭证泄露检测
```logql
{namespace="prod"} |~ `https?://\w+:\w+@`
```

## 发送日志到 Loki

### 通过 Grafana Alloy

```alloy
loki.source.file "app" {
  targets    = [{__path__ = "/var/log/app/*.log", job = "app"}]
  forward_to = [loki.process.parse.receiver]
}

loki.process "parse" {
  forward_to = [loki.write.cloud.receiver]
  stage.json {
    expressions = { level = "level", msg = "message" }
  }
  stage.labels {
    values = { level = "" }
  }
  stage.drop {
    expression = ".*healthcheck.*"
  }
}

loki.write "cloud" {
  endpoint {
    url = "https://logs-xxx.grafana.net/loki/api/v1/push"
    basic_auth {
      username = sys.env("LOKI_USER")
      password = sys.env("GRAFANA_API_KEY")
    }
  }
  external_labels = { cluster = "prod" }
}
```

### 通过 Kubernetes（Alloy DaemonSet）

```alloy
discovery.kubernetes "pods" {
  role = "pod"
}

loki.source.kubernetes "pods" {
  targets    = discovery.kubernetes.pods.targets
  forward_to = [loki.write.cloud.receiver]
}
```

### Loki HTTP 推送 API

```bash
curl -X POST https://logs-xxx.grafana.net/loki/api/v1/push \
  -u "user:apikey" \
  -H 'Content-Type: application/json' \
  -d '{
    "streams": [{
      "stream": { "app": "myapp", "env": "prod" },
      "values": [
        ["1609459200000000000", "log line here"]
      ]
    }]
  }'
```

## 架构

```
推送路径:  客户端 → 分发器 → Ingester（WAL）→ 对象存储（块）
读取路径:  查询 → 查询前端 → Querier → Ingester + 存储（块）
```

**组件:**
- **Distributor**: 验证和哈希传入的日志流
- **Ingester**: 内存缓冲块，刷新到对象存储
- **Querier**: 执行 LogQL 查询
- **Query Frontend**: 缓存、拆分和并行化查询
- **Compactor**: 管理保留和去重

## 参考

- [LogQL 参考](references/logql.md)
- [配置](references/configuration.md)
- [发送数据](references/send-data.md)
