# Grafana Alloy

> **文档**: https://grafana.com/docs/alloy/latest/

兼容 OpenTelemetry 的收集器——一个二进制文件即可用于指标 + 日志 + 跟踪 + 配置文件。

## 前置条件

- 已安装 `alloy` 命令行工具 (`brew install grafana/grafana/alloy`, `apt install alloy`, 或 `grafana/alloy` Docker 镜像)
- 一个用于发送数据的端点（Grafana Cloud, Prometheus, Loki, Tempo, Pyroscope）
- 该端点的 API 密钥 + 用户名，作为 `GRAFANA_API_KEY` 等环境变量导出

## 常见工作流程

### 1. 本地编写 + 验证配置

```alloy
// config.alloy — 指标 → Grafana Cloud
prometheus.scrape "app" {
  targets = [{"__address__" = "localhost:9090"}]
  forward_to = [prometheus.remote_write.cloud.receiver]
  scrape_interval = "30s"
}

prometheus.remote_write "cloud" {
  endpoint {
    url = sys.env("PROMETHEUS_URL")
    basic_auth {
      username = sys.env("PROM_USER")
      password = sys.env("GRAFANA_API_KEY")
    }
  }
}
```

```bash
# 1. 格式化 + 语法检查（在运行前捕获拼写错误）
alloy fmt config.alloy
alloy validate config.alloy

# 2. 运行它
alloy run config.alloy
# 或作为服务运行：systemctl restart alloy

# 3. 通过端口 12345 的 UI 验证所有组件是否健康
curl -s http://localhost:12345/api/v0/web/components \
  | jq '.[] | select(.health.state != "healthy") | {id, state:.health.state, msg:.health.message}'
# 预期：空（没有不健康的组件）。否则该行会显示故障组件及原因。

# 4. 验证样本是否正在传输
curl -s http://localhost:12345/metrics \
  | grep -E '^prometheus_remote_storage_(samples_total|enqueue_retries_total)' | head
# samples_total 应该 > 0 且持续上升；retries 应该为 0。
```

### 2. 添加日志传输（文件 → Loki）

```alloy
loki.source.file "app_logs" {
  targets    = [{ __path__ = "/var/log/app/*.log", job = "app" }]
  forward_to = [loki.write.cloud.receiver]
}

loki.write "cloud" {
  endpoint {
    url = sys.env("LOKI_URL")
    basic_auth {
      username = sys.env("LOKI_USER")
      password = sys.env("GRAFANA_API_KEY")
    }
  }
}
```

```bash
# 在 Grafana → Explore → Loki 中验证：
#   {job="app"}
# 预期：行正在传输。如果为空：
#   - 检查 /var/log/app/*.log 是否实际存在 + alloy 用户可读取
#   - http://localhost:12345 → loki.source.file.app_logs → "端点"标签页
```

### 3. 接收 OTLP 跟踪并传输到 Tempo

```alloy
otelcol.receiver.otlp "default" {
  grpc { endpoint = "0.0.0.0:4317" }
  http { endpoint = "0.0.0.0:4318" }
  output { traces = [otelcol.exporter.otlp.tempo.input] }
}

otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo-xxx.grafana.net/tempo:443"
    auth     = otelcol.auth.basic.grafana_cloud.handler
  }
}

otelcol.auth.basic "grafana_cloud" {
  username = sys.env("TEMPO_USER")
  password = sys.env("GRAFANA_API_KEY")
}
```

```bash
# 在 Grafana → Explore → Tempo → service.name = your-service 中验证
# 在 Alloy 层级，监控接收器：
curl -s http://localhost:12345/metrics | grep otelcol_receiver_accepted_spans
```

完整模式集（Kubernetes 发现 + 重新标记，完整的 Cloud 管道用于所有 4 种信号）：[`references/collection-patterns.md`](references/collection-patterns.md)。

## 参考

- [`references/config-syntax.md`](references/config-syntax.md) — 块/属性/表达式语法，`import.*`，`remotecfg`，集群
- [`references/components.md`](references/components.md) — 完整组件目录，包含用途 + 典型参数
- [`references/collection-patterns.md`](references/collection-patterns.md) — 端到端管道（K8s Pod，OTLP，配置文件，日志）

## 故障排除

- `alloy validate` → "组件未找到" → 版本太旧；`alloy --version` 并升级
- UI 显示组件 `unhealthy` → 在 http://localhost:12345 中点击该组件以获取实时错误
- `prometheus_remote_storage_samples_dropped_total` 上升 → 检查 `enqueue_retries_total` 和远程写入端点 URL + 凭证
- 没有跟踪到达 Tempo → 检查 `otelcol_receiver_refused_spans` 和导出器的 `otelcol_exporter_sent_spans` / `otelcol_exporter_send_failed_spans`

## 资源

- [Alloy 文档](https://grafana.com/docs/alloy/latest/)
- [组件参考](https://grafana.com/docs/alloy/latest/reference/components/)
- [从 Grafana Agent 迁移](https://grafana.com/docs/alloy/latest/set-up/migrate/from-agent/)
