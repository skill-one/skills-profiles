# 向 Grafana Cloud 发送数据

> **文档**: https://grafana.com/docs/grafana-cloud/send-data/

## 快速入门：查找您的凭证

在 Grafana Cloud 控制台 → **我的账户** → **堆栈** → **详情**：

| 信号 | 凭证字段 |
|------|----------|
| 指标 | Prometheus 远程写入 URL、用户名、密码/API 密钥 |
| 日志 | Loki URL、用户名、密码/API 密钥 |
| 跟踪 | Tempo OTLP 端点、用户名、密码/API 密钥 |
| 配置文件 | Pyroscope URL、用户名、密码/API 密钥 |

## Alloy（推荐 — 所有信号）

```alloy
// 指标
prometheus.scrape "app" {
  targets    = [{"__address__" = "localhost:8080"}]
  forward_to = [prometheus.remote_write.cloud.receiver]
}

prometheus.remote_write "cloud" {
  endpoint {
    url = "https://prometheus-prod-xx.grafana.net/api/prom/push"
    basic_auth {
      username = sys.env("PROM_USER")
      password = sys.env("GRAFANA_CLOUD_API_KEY")
    }
  }
}

// 日志
loki.source.file "app" {
  targets = [{__path__ = "/var/log/app/*.log", job = "app"}]
  forward_to = [loki.write.cloud.receiver]
}

loki.write "cloud" {
  endpoint {
    url = "https://logs-prod-xx.grafana.net/loki/api/v1/push"
    basic_auth {
      username = sys.env("LOKI_USER")
      password = sys.env("GRAFANA_CLOUD_API_KEY")
    }
  }
}

// 跟踪（OTLP 接收 → 转发）
otelcol.receiver.otlp "default" {
  grpc { endpoint = "0.0.0.0:4317" }
  http { endpoint = "0.0.0.0:4318" }
  output {
    traces = [otelcol.exporter.otlp.cloud.input]
  }
}

otelcol.exporter.otlp "cloud" {
  client {
    endpoint = "tempo-prod-xx.grafana.net:443"
    auth = otelcol.auth.basic.cloud.handler
  }
}

otelcol.auth.basic "cloud" {
  username = sys.env("TEMPO_USER")
  password = sys.env("GRAFANA_CLOUD_API_KEY")
}
```

## 直接 Prometheus Remote Write

```yaml
# prometheus.yml
remote_write:
  - url: https://prometheus-prod-xx.grafana.net/api/prom/push
    basic_auth:
      username: "123456"
      password: "your-api-key"
    write_relabel_configs:
      - source_labels: [__name__]
        regex: "go_.*"
        action: drop   # 可选：丢弃高基数指标
```

## 直接 Loki Push (curl)

```bash
curl -X POST https://logs-prod-xx.grafana.net/loki/api/v1/push \
  -H "Content-Type: application/json" \
  -u "123456:your-api-key" \
  -d '{
    "streams": [{
      "stream": { "app": "myapp", "env": "prod" },
      "values": [
        ["1706745600000000000", "application started"]
      ]
    }]
  }'
```

## OpenTelemetry SDK → Grafana Cloud

```bash
# OpenTelemetry 导出环境变量
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-prod-xx.grafana.net/otlp"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic $(echo -n '123456:your-api-key' | base64)"
export OTEL_SERVICE_NAME="my-service"
```

Python 示例:
```python
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

provider = TracerProvider()
exporter = OTLPSpanExporter()  # 读取 OTEL_EXPORTER_OTLP_* 环境变量
provider.add_span_processor(BatchSpanProcessor(exporter))
trace.set_tracer_provider(provider)
```

## 云集成

常见基础设施的预构建集成（从 Grafana Cloud UI 或 API 安装）：

```bash
# 列出可用集成
curl https://integrations-api-prod.grafana.net/api/v1/integrations \
  -H "Authorization: Bearer <api-key>"

# 安装 AWS CloudWatch 集成
curl -X POST https://integrations-api-prod.grafana.net/api/v1/integrations/cloudwatch \
  -H "Authorization: Bearer <api-key>" \
  -H "Content-Type: application/json" \
  -d '{"name": "aws-prod", "config": {...}}'
```

热门集成：AWS CloudWatch、Azure Monitor、GCP、Kubernetes、Docker、MySQL、PostgreSQL、Redis、Nginx、Apache、JVM、Node.js、Python、.NET。

## Kubernetes Agent Operator

```yaml
# grafana/k8s-monitoring Helm chart 的 values.yaml
cluster:
  name: production

externalServices:
  prometheus:
    host: https://prometheus-prod-xx.grafana.net
    basicAuth:
      username: "123456"
      password:
        secretName: grafana-cloud-secret
        secretKey: api-key

  loki:
    host: https://logs-prod-xx.grafana.net
    basicAuth:
      username: "234567"
      password:
        secretName: grafana-cloud-secret
        secretKey: api-key

metrics:
  enabled: true
  podMonitors:
    enabled: true
  serviceMonitors:
    enabled: true

logs:
  pod_logs:
    enabled: true

traces:
  enabled: true
```

```bash
helm install k8s-monitoring grafana/k8s-monitoring \
  --version 4.1.4 \
  -n monitoring --create-namespace \
  -f values.yaml
```

## API 密钥管理

```bash
# 通过 Grafana API 创建 API 密钥
curl -X POST https://yourstack.grafana.net/api/auth/keys \
  -H "Content-Type: application/json" \
  -u "admin:adminpassword" \
  -d '{"name": "alloy-writer", "role": "MetricsPublisher", "secondsToLive": 0}'
```

数据摄取角色：`MetricsPublisher`、`LogsPublisher`、`TracesPublisher`、`ProfilesPublisher`
