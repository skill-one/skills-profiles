# OpenTelemetry与Grafana

> **文档**: https://grafana.com/docs/opentelemetry/

供应商中立的instrumentation（探针）管道。应用程序通过OTLP → Alloy（或直接）→ Grafana Cloud（Mimir / Loki / Tempo / Pyroscope）。

## 后端

| 信号 | 后端 |
|------|------|
| 指标 | Grafana Mimir |
| 日志 | Grafana Loki |
| 跟踪 | Grafana Tempo |
| 配置文件 | Grafana Pyroscope |

## 前置条件

- Grafana Cloud堆栈 或 自托管Mimir / Loki / Tempo
- 云端OTLP端点: `https://otlp-gateway-<region>.grafana.net/otlp`
- 基本认证凭据：数字实例ID + API令牌，包含 `MetricsPublisher` + `LogsPublisher` + `TracesPublisher`
- 一个需要instrument的应用程序

## 常见工作流

### 1. 认证到Grafana Cloud的OTLP端点

```bash
# 1. 构建认证头部
INSTANCE_ID=123456
API_KEY="glc_eyJ..."
export OTEL_EXPORTER_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic $(echo -n "${INSTANCE_ID}:${API_KEY}" | base64)"
export OTEL_RESOURCE_ATTRIBUTES="service.name=myapp,service.namespace=myteam,deployment.environment=prod"

# 2. 使用curl POST对OTLP跟踪端点进行smoke测试（空体）
curl -s -o /dev/null -w "%{http_code}\n" \
  -X POST -H "Content-Type: application/x-protobuf" \
  -H "Authorization: Basic $(echo -n "${INSTANCE_ID}:${API_KEY}" | base64)" \
  "$OTEL_EXPORTER_OTLP_ENDPOINT/v1/traces" --data-binary '\n'
# 预期400（无效负载）— 不是401（认证）或404（错误端点）。
```

### 2. 自动instrument Java应用程序 + 验证

```bash
# 1. 下载Grafana JVM代理（单个jar）
curl -sLO https://github.com/grafana/grafana-opentelemetry-java/releases/latest/download/grafana-opentelemetry-java.jar

# 2. 使用代理和步骤1中的环境变量运行
java -javaagent:./grafana-opentelemetry-java.jar -jar myapp.jar

# 3. 生成流量，然后在Grafana → 探索 → Tempo中验证：
#    TraceQL: { resource.service.name = "myapp" }
#    预期在约30秒内出现span。也验证指标：
#    PromQL: count by (service_name)({service_name="myapp"})
```

### 3. 自动instrument Python应用程序

```bash
pip install "opentelemetry-distro[otlp]"
opentelemetry-bootstrap -a install

# 与步骤1相同的环境变量，然后：
opentelemetry-instrument python app.py

# 以相同方式验证 — 探索 → 跟踪过滤器 service.name=myapp。
```

### 4. 添加Alloy作为缓冲/采样收集器

```bash
# 应用程序指向本地Alloy（gRPC最快）
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc

# 转发到云端的Alloy环境
export GRAFANA_CLOUD_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
export GRAFANA_CLOUD_INSTANCE_ID=$INSTANCE_ID
export GRAFANA_CLOUD_API_KEY=$API_KEY
alloy run /etc/alloy/config.alloy

# 验证Alloy接收并转发
curl -s http://localhost:12345/metrics | grep otelcol_exporter_sent_spans
```

完整的Alloy配置 + 尾部采样块 + OTel Collector YAML + K8s Operator安装：[`references/collector-config.md`](references/collector-config.md)。

语言SDK细节（Go完整代码，Node手动设置，.NET ASP.NET Core，所有环境变量怪癖）：[`references/instrumentation.md`](references/instrumentation.md)。

### 5. Kubernetes — 通过Operator自动注入

```yaml
apiVersion: opentelemetry.io/v1alpha1
kind: Instrumentation
metadata: { name: my-instrumentation }
spec:
  exporter: { endpoint: http://otelcol:4317 }
  propagators: [tracecontext, baggage]
  java:
    image: us-docker.pkg.dev/grafanalabs-global/docker-grafana-opentelemetry-java-prod/grafana-opentelemetry-java:2.3.0-beta.1
  nodejs: {}
  python: {}
```

然后标注Pod：

```yaml
metadata:
  annotations:
    instrumentation.opentelemetry.io/inject-java: "true"
    # 或: inject-nodejs, inject-python, inject-dotnet
```

```bash
# 验证Operator注入了代理
kubectl describe pod <pod> | grep -A2 'opentelemetry-auto-instrumentation'
# 然后运行相同的Grafana Explore检查。
```

## 采样 — 何时选择哪个

```bash
# 头部采样（便宜，在开始时决定；可能丢失罕见错误）
export OTEL_TRACES_SAMPLER=parentbased_traceidratio
export OTEL_TRACES_SAMPLER_ARG=0.1   # 10%
```

尾部采样（在看到整个跟踪后决定 — 保留错误 + 采样其余部分）需要一个Alloy / OTel-Collector `tail_sampling` 处理器；完整块在 [`references/collector-config.md`](references/collector-config.md)。

## 关键环境变量

| 变量 | 示例 |
|------|------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | `https://otlp-gateway-prod-us-east-0.grafana.net/otlp` |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc` 或 `http/protobuf` |
| `OTEL_EXPORTER_OTLP_HEADERS` | `Authorization=Basic <base64>` |
| `OTEL_RESOURCE_ATTRIBUTES` | `service.name=app,service.namespace=team,deployment.environment=prod` |
| `OTEL_SERVICE_NAME` | `service.name`的缩写 |
| `OTEL_TRACES_SAMPLER` / `_ARG` | `parentbased_traceidratio` / `0.1` |

## 故障排除

- 从OTLP网关返回401 → 实例ID不是数字，或API密钥缺少发布者角色
- 404 → 端点URL错误（必须以`/otlp`结尾）
- Span丢失 → 检查 `OTEL_EXPORTER_OTLP_PROTOCOL` 是否与传输匹配（云端OTLP网关 = `http/protobuf`，本地Alloy = `grpc`）
- Node.js自动instrumentation在打包后损坏 → 打包器如 `@vercel/ncc` 会禁用require钩子
- Gunicorn / uWSGI下的Python显示没有span → 在post-fork钩子中重新初始化OTel提供者

## 资源

- [Grafana OTel文档](https://grafana.com/docs/opentelemetry/)
- [Grafana Cloud OTLP](https://grafana.com/docs/grafana-cloud/send-data/otlp/)
- [Grafana JVM代理](https://github.com/grafana/grafana-opentelemetry-java)
- [Grafana .NET SDK](https://github.com/grafana/grafana-opentelemetry-dotnet)
- [OTel Operator](https://opentelemetry.io/docs/kubernetes/operator/)
