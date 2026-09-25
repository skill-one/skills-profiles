# Grafana Tempo

> **文档**: https://grafana.com/docs/tempo/latest/

成本效益高的分布式追踪。支持 OTLP / Jaeger / Zipkin / OpenCensus / Kafka。将 Parquet 块存储在 S3/GCS/Azure 中。

## 前置条件

- Docker（快速启动）或 Kubernetes（生产环境）
- 对象存储桶（S3/GCS/Azure）用于分布式部署
- 一个发出 OTLP 的应用程序或 `tempo-cli` 用于合成流量
- 一个带有 Tempo 数据源的 Grafana 堆栈用于查询

## 常见工作流程

### 1. 本地启动 Tempo + 验证摄取

```bash
# 1. 启动官方 Docker Compose 示例
git clone https://github.com/grafana/tempo.git
cd tempo/example/docker-compose/local
mkdir -p tempo-data
docker compose up -d

# 2. 验证就绪状态
curl -sf http://localhost:3200/ready                              # → "ready"

# 3. 发送合成 OTLP 追踪（完整负载在临时终端中）
curl -X POST -H 'Content-Type: application/json' \
  http://localhost:4318/v1/traces \
  -d '{"resourceSpans":[{"resource":{"attributes":[{"key":"service.name","value":{"stringValue":"my-service"}}]},
       "scopeSpans":[{"spans":[{"traceId":"5B8EFFF798038103D269B633813FC700","spanId":"EEE19B7EC3C1B100",
       "name":"my-op","startTimeUnixNano":1689969302000000000,"endTimeUnixNano":1689969302500000000,"kind":2}]}]}]}'

# 4. 验证追踪是否已到达（ingestion-counter > 0 且追踪可检索）
curl -s http://localhost:3200/metrics | grep tempo_distributor_spans_received_total | head
curl -s http://localhost:3200/api/v2/traces/5B8EFFF798038103D269B633813FC700 | jq '.batches | length'
# 预期 > 0。

# 5. 在 Grafana → 探索 → Tempo 中运行 TraceQL: {resource.service.name="my-service"}
```

### 2. 通过 Alloy 从应用程序发送追踪

```alloy
// alloy.river
otelcol.receiver.otlp "default" {
  grpc { endpoint = "0.0.0.0:4317" }
  http { endpoint = "0.0.0.0:4318" }
  output { traces = [otelcol.exporter.otlp.tempo.input] }
}

otelcol.exporter.otlp "tempo" {
  client {
    endpoint = "tempo:4317"
    tls { insecure = true }
  }
}
```

```bash
# 验证 Alloy 成功转发
curl -s http://localhost:12345/metrics | grep otelcol_exporter_sent_spans
# 然后：相同的 Grafana → 探索 → Tempo 检查。
```

### 3. 编写 + 运行 TraceQL

```traceql
# 慢请求来自一个服务
{ resource.service.name = "frontend" && duration > 1s }

# 服务器追踪中存在下游错误（结构化）
{ kind = server } >> { status = error }

# 每个服务的错误率（指标）
{ status = error } | rate() by (resource.service.name)
```

完整的操作员 + 范围速查表、内置函数列表、指标函数：[`references/traceql.md`](references/traceql.md)。

```bash
# 通过 API
curl -sG --data-urlencode 'q={resource.service.name="frontend" && duration > 1s}' \
  --data-urlencode "start=$(date -d '1h ago' +%s)" --data-urlencode "end=$(date +%s)" \
  http://localhost:3200/api/search | jq '.traces | length'
```

### 4. 在 Kubernetes 上部署（Helm）

```bash
helm repo add grafana https://grafana.github.io/helm-charts
helm install tempo grafana/tempo-distributed --version 1.61.3 \
  --set storage.trace.backend=s3 \
  --set storage.trace.s3.bucket=my-tempo-bucket \
  --set storage.trace.s3.region=us-east-1

# 验证每个 Pod 都处于就绪状态（distributor, ingester, querier, query-frontend, compactor）
kubectl get pods -n default -l app.kubernetes.io/instance=tempo
kubectl port-forward svc/tempo-query-frontend 3200:3200 &
curl -sf http://localhost:3200/ready
```

## 多租户

```yaml
multitenancy_enabled: true
# 所有请求都必须包含头部: X-Scope-OrgID: <租户 ID>
```

完整架构、端口、性能调优、metrics-generator 配置、多租户客户端片段、traces-to-logs/metrics/profiles 数据源：[`references/architecture-and-operations.md`](references/architecture-and-operations.md)。

## 故障排除

- `/ready` → 503 → ingester 仍在加入；检查 `tempo_ingester_*` 指标 + 日志
- 推送时 429 → 提高 `max_outstanding_per_tenant` 或每个租户的摄取限制
- "Explore 中没有显示追踪" → 确认 `X-Scope-OrgID` 在写入者和 Grafana 数据源之间匹配
- TraceQL 慢 → 缩小 `start`/`end`，添加 service.name 过滤器，为热属性启用专用 Parquet 列

## 资源

- [Tempo 文档](https://grafana.com/docs/tempo/latest/)
- [TraceQL 参考](https://grafana.com/docs/tempo/latest/traceql/)
- [`references/traceql.md`](references/traceql.md) — 完整 TraceQL 速查表
- [`references/architecture-and-operations.md`](references/architecture-and-operations.md) — 组件、端口、Helm、调优、数据源链接
