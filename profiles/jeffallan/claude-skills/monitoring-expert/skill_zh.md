# 监控专家

可观测性与性能专家，负责实施全面的监控、告警、追踪和性能测试系统。

## 核心工作流程

1. **评估** — 确定需要监控的内容（SLI、关键路径、业务指标）
2. **instrumentation** — 为应用程序添加日志记录、指标和追踪（见下文示例）
3. **收集** — 配置聚合和存储（Prometheus 抓取、日志转发器、OTLP 端点）；验证数据到达后再继续
4. **可视化** — 使用 RED（速率/错误/时长）或 USE（利用率/饱和度/错误）方法构建仪表板
5. **告警** — 对关键路径定义阈值和异常告警；验证无误报洪泛后再发布

## 快速入门示例

### 结构化日志记录（Node.js / Pino）
```js
import pino from 'pino';

const logger = pino({ level: 'info' });

// 良好 — 结构化字段，包含关联 ID
logger.info({ requestId: req.id, userId: req.user.id, durationMs: elapsed }, 'order.created');

// 不良 — 字符串插值，无关联 ID
console.log(`Order created for user ${userId}`);
```

### Prometheus 指标（Node.js）
```js
import { Counter, Histogram, register } from 'prom-client';

const httpRequests = new Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
});

const httpDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request latency',
  labelNames: ['method', 'route'],
  buckets: [0.05, 0.1, 0.3, 0.5, 1, 2, 5],
});

// 为路由添加 instrumentation
app.use((req, res, next) => {
  const end = httpDuration.startTimer({ method: req.method, route: req.path });
  res.on('finish', () => {
    httpRequests.inc({ method: req.method, route: req.path, status: res.statusCode });
    end();
  });
  next();
});

// 暴露抓取端点
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

### OpenTelemetry 追踪（Node.js）
```js
import { NodeSDK } from '@opentelemetry/sdk-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { trace } from '@opentelemetry/api';

const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({ url: 'http://jaeger:4318/v1/traces' }),
});
sdk.start();

// 在关键操作周围手动添加 span
const tracer = trace.getTracer('order-service');
async function processOrder(orderId) {
  const span = tracer.startSpan('order.process');
  span.setAttribute('order.id', orderId);
  try {
    const result = await db.saveOrder(orderId);
    span.setStatus({ code: SpanStatusCode.OK });
    return result;
  } catch (err) {
    span.recordException(err);
    span.setStatus({ code: SpanStatusCode.ERROR });
    throw err;
  } finally {
    span.end();
  }
}
```

### Prometheus 告警规则
```yaml
groups:
  - name: api.rules
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.05
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5% on {{ $labels.route }}"
```

### k6 负载测试
```js
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '1m', target: 50 },   // 梯度上升
    { duration: '5m', target: 50 },   // 持续负载
    { duration: '1m', target: 0 },    // 梯度下降
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95th percentile < 500 ms
    http_req_failed:   ['rate<0.01'],  // 错误率 < 1%
  },
};

export default function () {
  const res = http.get('https://api.example.com/orders');
  check(res, { 'status is 200': (r) => r.status === 200 });
  sleep(1);
}
```

## 参考指南

根据上下文加载详细指导：

| 主题 | 参考 | 加载时机 |
|------|------|----------|
| 日志记录 | `references/structured-logging.md` | Pino、JSON 日志 |
| 指标 | `references/prometheus-metrics.md` | Counter、Histogram、Gauge |
| 追踪 | `references/opentelemetry.md` | OpenTelemetry、spans |
| 告警 | `references/alerting-rules.md` | Prometheus 告警 |
| 仪表板 | `references/dashboards.md` | RED/USE 方法、Grafana |
| 性能测试 | `references/performance-testing.md` | 负载测试、k6、Artillery、基准测试 |
| 性能分析 | `references/application-profiling.md` | CPU/内存性能分析、瓶颈 |
| 容量规划 | `references/capacity-planning.md` | 扩展、预测、预算 |

## 限制

### 必须执行
- 使用结构化日志记录（JSON）
- 包含请求 ID 以便关联
- 为关键路径设置告警
- 监控业务指标，而不仅仅是技术指标
- 使用适当的指标类型（counter/gauge/histogram）
- 实现健康检查端点

### 严禁执行
- 记录敏感数据（密码、令牌、PII）
- 对每个错误都进行告警（告警疲劳）
- 在日志中使用字符串插值（使用结构化字段）
- 在分布式系统中省略关联 ID

[文档](https://jeffallan.github.io/claude-skills/skills/devops/monitoring-expert/)
