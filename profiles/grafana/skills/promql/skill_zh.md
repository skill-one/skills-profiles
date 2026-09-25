# PromQL 查询模式

> **文档**: https://prometheus.io/docs/prometheus/latest/querying/basics/

PromQL 返回**瞬时向量**、**范围向量**或**标量**。

**黄金法则**: `rate()` / `increase()` 需要 ≥ 4× 扫描间隔的范围向量。60秒扫描 → 至少使用 `[5m]`。

## 前置条件

- 用于查询的 Prometheus / Mimir / Grafana Cloud 端点 (`/api/v1/query` 或通过 Grafana Explore)
- PromQL 模式库位于 [`references/patterns.md`](references/patterns.md)

## 常见工作流程

### 1. 编写并验证查询

```bash
# 0. 指向你的 Prometheus/Mimir。对于 Grafana Cloud，使用指标端点并添加基本认证 (-u "<metrics_user>:<token>") 到以下每个 curl 命令。
PROM=http://localhost:9090   # 或 https://prometheus-prod-XX.grafana.net/api/prom

# 1. 绘制查询 — 对于 "每个服务的 5xx 错误率":
EXPR='sum(rate(http_requests_total{status_code=~"5.."}[5m])) by (service)'

# 2. 验证语法 + 指标/标签是否存在
curl -sG --data-urlencode "query=${EXPR}" \
  "$PROM/api/v1/query" | jq '.status, (.data.result|length)'
# 预期: "success" 和结果计数 > 0。如果为 0 — 检查标签拼写和扫描活动:
curl -sG --data-urlencode "match[]=http_requests_total" "$PROM/api/v1/series" | jq '.data | length'

# 3. 检查数值合理性 — 打开 Grafana Explore，粘贴表达式,
#    确认数值与已知基准值（k6 运行、日志计数等）相符。
```

### 2. 常用模式复制

**按状态请求率**（聚合在 `rate()` 之后）:

```promql
sum(rate(http_requests_total{job="api"}[5m])) by (status_code)
```

**p95 延迟**（必须保留内部聚合中的 `le`）:

```promql
histogram_quantile(0.95,
  sum(rate(http_request_duration_seconds_bucket[5m])) by (le, service))
```

**带除零保护的错误率**:

```promql
sum(rate(http_requests_total{status_code=~"5.."}[5m]))
  / (sum(rate(http_requests_total[5m])) > 0)
```

完整库（记录规则、SLO 燃尽率、偏移量、基数搜索、原生直方图）: [`references/patterns.md`](references/patterns.md)。

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

- `histogram_quantile` 返回 NaN → 内部聚合中遗漏 `by (le)`
- "无数据" → 检查指标存在 (`/api/v1/series`) 和窗口 ≥ 4× 扫描间隔
- 错误的率数值 → 计数器在 `rate()` 之前被聚合（始终先 `rate()`）
- 查询超时 → 系列数量过高；使用 `topk(...)` + 记录规则 + 丢弃高基数标签（参见 [`references/patterns.md`](references/patterns.md)）

## 资源

- [PromQL 基础](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [操作符](https://prometheus.io/docs/prometheus/latest/querying/operators/)
- [函数](https://prometheus.io/docs/prometheus/latest/querying/functions/)
- [Grafana Mimir](https://grafana.com/docs/mimir/latest/)
