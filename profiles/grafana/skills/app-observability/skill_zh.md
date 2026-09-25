# Grafana Cloud 应用可观测性

> **文档**: https://grafana.com/docs/grafana-cloud/monitor-applications/

三个共享相同 OTLP + Mimir / Loki / Tempo / Pyroscope 管道的产物：

1. **应用可观测性** — 基于 OTel spanmetrics 的 APM
2. **前端可观测性** — Faro Web SDK，RUM + 会话回放
3. **AI 可观测性** — 通过 OpenLIT 进行 LLM / 向量数据库监控

## 前置条件

- Grafana Cloud 堆栈 + OTLP 端点 + 数字实例 ID + 具备 `MetricsPublisher` + `LogsPublisher` + `TracesPublisher` 权限的 API 密钥
- 对于 APM：使用 OTel SDK 仪器化的应用；对于前端：一个 Web 应用 + Faro 应用密钥；对于 AI：Python ≥ 3.10
- 使用 Grafana Alloy 作为本地 OTLP 接收器（推荐）

## 常见工作流

### 1. 部署 APM — Alloy 接收器 → Grafana Cloud + 验证

```bash
# 1. 设置 Cloud 凭证 + 使用 references/apm.md 中的配置启动 Alloy
export GRAFANA_CLOUD_OTLP_ENDPOINT=https://otlp-gateway-prod-us-east-0.grafana.net/otlp
export GRAFANA_CLOUD_INSTANCE_ID=123456
export GRAFANA_CLOUD_API_KEY=glc_eyJ...
alloy fmt /etc/alloy/config.alloy   # 语法检查
alloy run /etc/alloy/config.alloy

# 2. 验证 Alloy 是否接收并转发
curl -s http://localhost:12345/api/v0/web/components \
  | jq '.[] | select(.id|test("otelcol\\.exporter\\.otlphttp"))
        | {id, health:.health.state}'
# 预期 health.state == "healthy"
curl -s http://localhost:12345/metrics \
  | grep -E 'otelcol_(receiver_accepted_spans|exporter_sent_spans)'

# 3. 将您的应用指向 Alloy（带必要的属性！）
export OTEL_SERVICE_NAME="my-api"
export OTEL_RESOURCE_ATTRIBUTES="service.namespace=myteam,deployment.environment=production"
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export OTEL_EXPORTER_OTLP_PROTOCOL=grpc

# 4. 验证跟踪已到达 Tempo + 生成了 spanmetrics
#    Tempo (TraceQL):  { resource.service.name = "my-api" }
#    Mimir (PromQL):   sum by (job) (rate(traces_spanmetrics_calls_total{service_name="my-api"}[5m]))
#    预期在约 1 分钟内 > 0。

# 5. 验证是否连接到应用可观测性
#    Grafana → 应用 → 服务清单："my-api" 应以 RED 指标出现
#    点击进入 → 服务图边可见（需要出站调用上的 span.kind）
```

完整的 Alloy 块 + 所需资源属性 + spanmetric 名称 + 关联链接: [`references/apm.md`](references/apm.md)。

### 2. 使用 Faro 仪器化 React 前端

```bash
# 1. 安装
npm install @grafana/faro-react @grafana/faro-web-tracing
```

```javascript
// 2. 使用 TracingInstrumentation + ReactIntegration 初始化 Faro（见 references/faro.md）
//    推送一个 smoke test 事件，以便我们有已知的信号：
faro.api.pushEvent('faro_smoketest', { ts: Date.now().toString() });
```

```bash
# 3. 在 DevTools Network 中验证 — POST 到 /collect 返回 202
#    (401 → 错误的应用密钥；404 → URL 区域错误)

# 4. 在 Grafana Cloud 中验证
#    - 前端可观测性 → 您的应用 → 会话：您的会话出现
#    - Loki 上的 LogQL：{kind="event"} |= "faro_smoketest"
#    - 使用 TracingInstrumentation：打开会话 → 跟踪 ID 链接到 Tempo
```

完整的 React 示例，CDN 设置，会话配置: [`references/faro.md`](references/faro.md)。

### 3. 添加 AI / LLM 可观测性

```bash
pip install openlit==1.42.0
```

```python
# 应用启动时
import openlit
openlit.init(application_name="my-ai-app", environment="production")
# 您现有的 OpenAI / Anthropic / Cohere 调用现在会发出 OTel 跟踪 + 指标。
```

```bash
# 环境（与 APM 相同的 OTLP 端点）
export OTEL_SERVICE_NAME="my-ai-app"
export OTEL_EXPORTER_OTLP_ENDPOINT="https://otlp-gateway-<region>.grafana.net/otlp"
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Basic $(echo -n $ID:$KEY | base64)"

# 几次 LLM 调用后验证：
#   PromQL: sum by (gen_ai_request_model) (rate(gen_ai_usage_input_tokens_total[5m]))
#   仪表板：Grafana → AI 可观测性 → "GenAI Observability" 自动填充
```

完整的 OpenLIT 安装，evals/guards，GenAI 指标列表，仪表板名称: [`references/ai-observability.md`](references/ai-observability.md)。

## 全栈关联速查表

| 信号 | 产物 | 存储 | 查询 |
|---|---|---|---|
| RED 指标 | 应用可观测性 | Mimir | PromQL |
| 跟踪 | Tempo | Tempo | TraceQL |
| 日志 | Loki | Loki | LogQL |
| 配置文件 | Pyroscope | Pyroscope | ProfileQL |
| 浏览器 RUM | 前端可观测性 | Loki + Tempo | LogQL / TraceQL |
| LLM 指标 | AI 可观测性 | Mimir | PromQL |

关联键：`service.name` 将所有信号连接起来；跟踪示例嵌入跟踪 ID 在指标点中；`traceID` 在日志中，`traceparent` 由 Faro 注入用于前端 → 后端链接。

## 故障排除

- 服务在服务清单中缺失 → 缺少 `service.namespace`（作业标签）或 `deployment.environment` 资源属性
- 服务图边缺失 → `span.kind` 在出站调用上未设置（必须是 CLIENT）或在入站（SERVER）
- Faro `/collect` 返回 401 → 错误的应用密钥；404 → URL 中的区域与 Faro 应用不匹配
- 没有GenAI指标 → 确认 OpenLIT 版本与 Cloud 预期的 OTel 语义-conv 版本匹配；使用工作流 #3 中的 curl 验证认证

## 参考

- [`references/apm.md`](references/apm.md) — APM 基础：RED 指标如何生成，所需的 OTel 资源属性，Alloy 配置，关联链接
- [`references/apm-setup.md`](references/apm-setup.md) — 深入探讨：每种语言的完整 OTel SDK 设置（Node / Python / Java / Go），span-metrics 选项，完整的 Alloy 配置
- [`references/faro.md`](references/faro.md) — Faro 基础：SDK 初始化，仪器化，会话回放
- [`references/frontend-observability.md`](references/frontend-observability.md) — 深入探讨：完整的 Faro SDK 参考，React/Vue/Angular 集成，自定义事件，源映射
- [`references/ai-observability.md`](references/ai-observability.md) — OpenLIT 自动仪器化 OpenAI / Anthropic / Bedrock / Vertex AI

## 资源

- [应用可观测性文档](https://grafana.com/docs/grafana-cloud/monitor-applications/application-observability/)
- [前端可观测性文档](https://grafana.com/docs/grafana-cloud/monitor-applications/frontend-observability/)
- [Faro Web SDK](https://github.com/grafana/faro-web-sdk)
- [AI 可观测性文档](https://grafana.com/docs/grafana-cloud/monitor-applications/ai-observability/)
- [OpenLIT](https://openlit.io/)
