---
name: promql
description: 为 Prometheus / Grafana Mimir / Grafana Cloud Metrics 编写、验证和优化 PromQL。涵盖 `rate` 与 `irate` 与 `increase` 的区别、标签匹配器和正则表达式、`sum / avg / topk / by / without` 聚合、经典与原生 `histogram_quantile`、带除零保护的比率计算、`absent` / `changes` 用于检测数据陈旧、时间偏移和 `predict_linear`、记录规则命名、SLO 与消耗率计算，以及基数查找策略。适用于编写指标查询、修正错误的 p95 值、构建错误预算告警、调试“查询缓慢”、定位导致基数激增的噪声标签，或从仪表板查询迁移到记录规则——即使用户说“计算错误率”、“p99 延迟”、“按服务求和”、“为什么这个查询缓慢”，或“是什么占用了 Mimir”而不提及 PromQL。
---

# PromQL 查询模式

> **文档**: https://prometheus.io/docs/prometheus/latest/querying/basics/

PromQL 返回**瞬时向量**、**范围向量**或**标量**。

**黄金法则**: `rate()` / `increase()` 需要范围向量 ≥ 4× 抓取间隔。60秒抓取 → 使用 `[5m]` 最小值。

## 前置条件

- 用于查询的 Prometheus / Mimir / Grafana Cloud 端点 (`/api/v1/query` 或通过 Grafana Explore)
- PromQL 模式库位于 [`references/patterns.md`](references/patterns.md)

## 常见工作流

### 1. 编写并验证查询

```bash
# 0. 指向你的 Prometheus/Mimir。对于 Grafana Cloud，使用指标端点，并为每个 curl 添加基本认证 (-u "<metrics_user>:<token>")
PROM=http://localhost:9090   # 或 https://prometheus-prod-XX.grafana.net/api/prom

# 1. 构思查询 — 对于 "每个服务的 5xx 错误率":
EXPR='sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (service)'

# 2. 验证语法 + 指标/标签是否存在
curl -sG --data-urlencode "query=${EXPR}" \
  "$PROM/api/v1/query" | jq '.status, (.data.result|length)'
# 预期: "success" 和结果计数 > 0。如果为 0 — 检查标签拼写和抓取活动:
curl -sG --data-urlencode "match[]=http_requests_total" "$PROM/api/v1/series" | jq '.data | length'

# 3. 检查数值合理性 — 打开 Grafana Explore，粘贴表达式,
#    确认数值与已知基准值（k6 运行、日志计数等）相符。
```

### 2. 常用模式复制

**按状态请求率**（聚合在 `rate()` 之后）:

```promql
sum(rate(http_requests_total{job="api"}[5m])) by (status_code)
```

**p95 延迟**（内部聚合必须保留 `le`）:

```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

**带除零保护的错误率**:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
  / (sum(rate(http_requests_total[5m])) > 0)
```

完整库（记录规则、SLO 燃尽率、偏移量、基数搜索、原生直方图）: [`references/patterns.md`](references/patterns.md).

### 3. 将慢速仪表板查询转换为记录规则

```yaml
# 1. 选择慢速表达式，为其分配记录规则名称
groups:
  - name: http_request_rates
    interval: 1m
    rules:
      - record: job:http_request_duration_p95:rate5m
        expr: |
          histogram_quantile(0.95,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le, job))
```

```bash
# 2. 规则加载后，验证新指标是否存在
curl -sG --data-urlencode "query=job:http_request_duration_p95:rate5m" \
  "$PROM/api/v1/query" | jq '.data.result | length'   # → > 0

# 3. 验证它至少在一个样本窗口中与原始表达式匹配
# (两个查询应在同一时间戳产生相同值。)

# 4. 将仪表板面板表达式替换为记录规则指标。
```

## 常见错误

- `histogram_quantile` 返回 NaN → 内部聚合遗漏 `by (le)`
- "无数据" → 检查指标存在 (`/api/v1/series`) 和窗口 ≥ 4× 抓取间隔
- 错误的率数值 → 计数器在 `rate()` 之前被聚合（始终先 `rate()`）
- 查询超时 → 系列数量过高；使用 `topk(...)` + 记录规则 + 丢弃高基数标签（参见 [`references/patterns.md`](references/patterns.md)）

## 资源

- [PromQL 基础](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [操作符](https://prometheus.io/docs/prometheus/latest/querying/operators/)
- [函数](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Grafana Mimir](https://grafana.com/docs/mimir/latest/)
