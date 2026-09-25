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

# 3. 验证标签是否到达 Grafana Cloud
#    在 Explore 中运行： count by (team, project) ({__name__=~".+"})
#    然后访问成本管理 → 按 `team` / `project` 分组
```

有关完整的 Alloy 代码片段，请参阅 [`references/adaptive-signals.md`](references/adaptive-signals.md)。

### 2. 使用 Adaptive Metrics 降低指标基数

```bash
# 1. 拉取建议
curl https://<stack>.grafana.net/api/plugins/grafana-adaptive-metrics-app/resources/v1/recommendations \
  -H "Authorization: Bearer <token>" | jq '.recommendations | length'

# 2. 在 UI 中：Grafana Cloud → Adaptive Metrics → 查看按系列减少影响排序的规则
# 3. 在 "预览" 模式下测试后再应用
# 4. 应用（5 分钟内生效）

# 5. 验证 — 受影响的指标上的系列数量应减少
#    应用前捕获基线：
#      count({__name__="http_request_duration_seconds_bucket"})
#    应用后等待 10 分钟，再次运行 — 高基数指标的预期减少 10 倍以上。

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

有关可粘贴的规则（`MetricsUsageHigh`, `LogsIngestionHigh`），请参阅 [`references/alerts-and-queries.md`](references/alerts-and-queries.md)。

## 优化清单

- [ ] 应用 Adaptive Metrics 建议一一通常可减少系列 40-60%
- [ ] 在 Alloy 中丢弃 health/readiness 探针日志
- [ ] 将跟踪尾采样至 5-10% + 保留错误 / 慢 span
- [ ] 将 `team` + `project` 外部标签添加到每个 Alloy 配置
- [ ] 在配额 80% 时设置使用警报
- [ ] 用录制规则替换昂贵的临时查询

## 参考

- [`references/adaptive-signals.md`](references/adaptive-signals.md) — Adaptive Metrics / Logs / Traces 配置；成本归因标签
- [`references/alerts-and-queries.md`](references/alerts-and-queries.md) — 使用警报规则、成本查找 PromQL、计费单元表

## 资源

- [成本管理文档](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/)
- [Adaptive Metrics](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/metrics-costs/adaptive-metrics/)
- [Adaptive Logs](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/logs-costs/)
