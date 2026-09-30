---
name: cost-management
description: 通过将支出分配给团队并减少遥测数据量来降低您的Grafana Cloud账单。涵盖符合FOCUS标准的计费仪表板、Alloy中的成本归因标签、自适应指标（基数减少）、自适应日志（丢弃/采样）、自适应追踪（尾部采样）、使用量警报以及优化清单。在调查高额Grafana Cloud账单、将可观测性成本归因于团队或服务、减少活动序列/日志字节/追踪跨度，或设置使用量/配额警报时使用——即使用户说“我们的Grafana账单太高了”、“谁消耗了最多的指标”、“丢弃调试日志”、“采样我们的追踪”，或“在超出配额前通知我”，而不提及成本管理。
---

# Grafana Cloud 成本管理

> **文档**: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/

通过自适应信号 + 成本归因标签减少指标 / 日志 / 跟踪支出。

## 前置条件

- 已启用 Adaptive Metrics / Logs / Traces 的 Grafana Cloud 堆栈（可在 **成本管理** 下查看）
- Alloy（或 Grafana Agent）采集遥测数据，API 密钥范围包含 `metrics:write` + `logs:write` (+ `traces:write`）
- 拥有堆栈的管理员权限以应用自适应建议

## 常见工作流

### 1. 将成本归因到团队 / 服务

```alloy
# 1. 在 Alloy 中添加外部标签（指标 + 日志配置）
prometheus.remote_write "cloud" {
  endpoint { url = sys.env("PROMETHEUS_URL") /* ... */ }
  external_labels = { team = "platform", project = "checkout-service" }
}
```

```bash
# 2. 重新加载 Alloy
curl -X POST http://localhost:12345/-/reload

# 3. 验证标签已到达 Grafana Cloud
#    在 Explore 中运行： count by (team, project) ({__name__=~".+"})
#    然后访问成本管理 → 按 `team` / `project` 分组
```

有关完整的 Alloy 代码片段，请参阅 [`references/adaptive-signals.md`](references/adaptive-signals.md)。

### 2. 使用 Adaptive Metrics 降低指标基数

```bash
# 1. 拉取建议
curl https://<stack>.grafana.net/api/plugins/grafana-adaptive-metrics-app/resources/v1/recommendations \
  -H "Authorization: Bearer <token>" | jq '.recommendations | length'

# 2. 在 UI 中：Grafana Cloud → Adaptive Metrics → 查看按 series-reduction 影响排序的规则
# 3. 在应用前在 "预览" 模式下测试
# 4. 应用（5 分钟内生效）

# 5. 验证 — 受影响的指标上的序列数应减少
#    应用前捕获基线：
#      count({__name__="http_request_duration_seconds_bucket"})
#    应用后 10 分钟，再次运行 — 高基数指标应减少 10 倍以上。

# 如需回滚：在 UI 中打开规则 → 禁用，或 DELETE /v1/rules/<id>。
```

### 3. 在 Alloy 中丢弃噪声日志

```alloy
# 1. 添加过滤阶段（有关完整代码块，请参阅 references/adaptive-signals.md）
loki.process "filter_logs" {
  forward_to = [loki.write.cloud.receiver]
  stage.drop { expression = ".*GET /health.*" }
}
```

```bash
# 2. 重新加载 Alloy
curl -X POST http://localhost:12345/-/reload

# 3. 验证过滤器 — health 日志不应出现在 Logs Drilldown 中
#    LogQL 检查（应返回 0）：
#      sum(rate({app="my-app"} |= "GET /health" [5m]))
#    存入字节数也应减少。比较应用前后的 24 小时：
#      sum(increase(loki_ingester_chunk_size_bytes_sum[24h])) by (namespace)
```

### 4. 在达到配额前设置使用警报

有关现成可粘贴的规则（`MetricsUsageHigh`, `LogsIngestionHigh`），请参阅 [`references/alerts-and-queries.md`](references/alerts-and-queries.md)。

## 优化清单

- [ ] 应用 Adaptive Metrics 建议一一通常可减少 40-60% 的序列数
- [ ] 在 Alloy 中丢弃 health/readiness 探针日志
- [ ] 将跟踪尾样本减少到 5-10% + 保留错误 / 慢 span
- [ ] 将 `team` + `project` 外部标签添加到每个 Alloy 配置
- [ ] 在配额的 80% 时设置使用警报
- [ ] 用录制规则替换昂贵的 ad-hoc 查询

## 参考

- [`references/adaptive-signals.md`](references/adaptive-signals.md) — Adaptive Metrics / Logs / Traces 配置；成本归因标签
- [`references/alerts-and-queries.md`](references/alerts-and-queries.md) — 使用警报规则、成本查找 PromQL、计费单元表

## 资源

- [成本管理文档](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/)
- [Adaptive Metrics](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/metrics-costs/adaptive-metrics/)
- [Adaptive Logs](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/logs-costs/)
