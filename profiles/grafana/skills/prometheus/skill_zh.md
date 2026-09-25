# 使用 Prometheus 和 Grafana 进行指标监控

> **文档**: https://prometheus.io/docs/ | **Grafana Cloud 指标**: https://grafana.com/docs/grafana-cloud/send-data/metrics/

## PromQL 快速参考

### 即时向量选择器

```promql
# 通过指标名称
http_requests_total

# 标签过滤
http_requests_total{job="api-server"}

# 多个标签 (AND)
http_requests_total{job="api-server", method="GET"}

# 正则表达式
http_requests_total{job=~"api.*", status=~"5.."}

# 否定
http_requests_total{status!="200"}
```

### 范围向量和速率

```promql
# 5 分钟内的每秒速率
rate(http_requests_total[5m])

# 区间内的增量
increase(http_requests_total[1h])

# 即时速率 (最后两个样本)
irate(http_requests_total[5m])

# 偏移 (5 分钟前)
rate(http_requests_total[5m] offset 5m)
```

### 聚合

```promql
# 按标签求和
sum by (job) (rate(http_requests_total[5m]))

# 平均值
avg by (instance) (node_cpu_seconds_total)

# Top-K
topk(5, rate(http_requests_total[5m]))

# 直方图分位数
histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))

# 唯一计数
count(up{job="api"})
```

### 常见模式

```promql
# 错误率百分比
sum(rate(http_requests_total{status=~"5.."}[5m]))
  / sum(rate(http_requests_total[5m])) * 100

# 饱和度 (CPU 使用率 %)
100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100)

# 内存使用
node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes

# 预测磁盘满 (线性外推)
predict_linear(node_filesystem_free_bytes[6h], 24*3600) < 0
```

## 告警规则

### Prometheus 告警规则

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
            / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "高 5xx 错误率 ({{ $value | humanizePercentage }})"
```

### Alertmanager 路由

```yaml
# alertmanager.yml
route:
  receiver: default
  group_by: [alertname, job]
  group_wait: 30s
  group_interval: 5m
  routes:
    - match:
        severity: critical
      receiver: pagerduty
    - match:
        severity: warning
      receiver: slack

receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: "<key>"
  - name: slack
    slack_configs:
      - channel: "#alerts"
        api_url: "<webhook_url>"
  - name: default
    email_configs:
      - to: "oncall@example.com"
```

### 验证告警配置

```bash
promtool check rules rules.yml
amtool check-config alertmanager.yml
amtool config routes test --config.file=alertmanager.yml severity=critical
```

## 录制规则

预计算昂贵的 PromQL 以提升仪表盘性能：

```yaml
groups:
  - name: api_rules
    interval: 1m
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job) (rate(http_requests_total[5m]))
      - record: job:http_request_duration_seconds:p99
        expr: histogram_quantile(0.99, sum by (job, le) (rate(http_request_duration_seconds_bucket[5m])))
```

### 部署并验证录制规则

```bash
# 1. 验证规则语法
promtool check rules rules/recording.yml

# 2. 重新加载 Prometheus (添加到 prometheus.yml 中的 rule_files 后)
curl -X POST http://localhost:9090/-/reload

# 3. 验证规则是否激活
curl -s http://localhost:9090/api/v1/rules | jq '.data.groups[].rules[] | {name, health}'
```

## 指标下钻 (Grafana 12+)

无需编写 PromQL 即可探索 Prometheus 指标。导航至 **Explore > Metrics Drilldown** 或使用 `<grafana-url>/a/grafana-metricsdrilldown-app`。
提供指标搜索与标签分解、智能分段用于异常检测、自动可视化以及从指标到相关日志和追踪的遥测数据旋转。

## 资源

- [PromQL 参考](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [Grafana Cloud 指标](https://grafana.com/docs/grafana-cloud/send-data/metrics/)
- [指标下钻应用](https://github.com/grafana/metrics-drilldown)
- [Grafana 告警](https://grafana.com/docs/grafana/latest/alerting/)
- [Grafana Mimir](https://grafana.com/docs/mimir/latest/)
