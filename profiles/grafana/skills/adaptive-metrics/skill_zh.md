# Grafana Cloud 自适应指标

> **文档**: https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/metrics-costs/adaptive-metrics.md

在存储前预先缩减高基数指标的聚合规则——直接降低活动序列计费。

## 前置条件

- Grafana Cloud 指标计划（任何付费层级）
- 具有指标写入权限 (`metrics:write`) 的 API 密钥（用于自适应指标 API — `adaptive-metrics.grafana.net`，使用 Bearer 认证）
- 用于验证查询：指标查询端点 (`prometheus-prod-XX.grafana.net`) 使用 HTTP 基本认证——`<metrics_user>`（数字堆栈/实例 ID）加上具有 `metrics:read` 权限的令牌——不是 Bearer 密钥
- 可访问 Cloud 控制台中的 **首页 → 自适应指标**

## 常见工作流程

### 1. 审核并应用自动推荐

```bash
# 1. 拉取推荐列表（按序列缩减影响排序）
curl -s -H "Authorization: Bearer <KEY>" \
  "https://adaptive-metrics.grafana.net/api/v1/recommendations" \
  | jq '.recommendations[] | {metric_name, current_series, projected_series, estimated_reduction_percent}'

# 2. 捕获目标指标的基线序列数量
#    （指标查询端点 = 基本认证，不是 Bearer 密钥）
curl -s -u "<metrics_user>:<metrics_token>" \
  "https://prometheus-prod-XX.grafana.net/api/prom/api/v1/query?query=count({__name__=\"process_cpu_seconds_total\"})" \
  | jq '.data.result[0].value[1]'   # → 例如 "12480"

# 3. 应用推荐（或点击 UI 中的应用）
curl -s -X POST -H "Authorization: Bearer <KEY>" \
  "https://adaptive-metrics.grafana.net/api/v1/recommendations/<ID>/apply"

# 4. 等待 ~5 分钟。验证——重新运行计数查询；预期大幅下降。
#    同时检查节省指标：
#      grafanacloud_instance_active_series_dropped_by_aggregation_rules
```

**回滚**——删除规则：

```bash
curl -s -H "Authorization: Bearer <KEY>" \
  "https://adaptive-metrics.grafana.net/api/v1/rules" | jq '.rules[] | {id, metric_name}'
curl -s -X DELETE -H "Authorization: Bearer <KEY>" \
  "https://adaptive-metrics.grafana.net/api/v1/rules/<RULE_ID>"
# 或在 UI 中：规则 → 行 → 禁用
```

### 2. 手动编写自定义规则

```bash
# 1. 检查指标是否未在仪表板/告警中使用该标签
grep -r 'process_cpu_seconds_total' dashboards/ alerts/ | grep -E 'version|go_version'
# 预期无匹配项 → 可安全删除。

# 2. 创建规则
curl -s -X POST -H "Authorization: Bearer <KEY>" -H "Content-Type: application/json" \
  "https://adaptive-metrics.grafana.net/api/v1/rules" \
  -d '{"rules":[{"metric_name":"process_cpu_seconds_total","match_type":"MATCH_TYPE_EXACT",
                 "drop_labels":["version","go_version"],
                 "aggregations":[{"type":"AGGREGATION_TYPE_SUM"}]}]}'

# 3. 验证——与上述相同的 count() 查询；序列数量应在 5 分钟内下降。
```

完整负载（正则匹配、聚合类型、所有注意事项）：[`references/api.md`](references/api.md)。

### 3. 完全删除未使用的指标

```bash
# 1. 列出未使用的指标
curl -s -H "Authorization: Bearer <KEY>" \
  "https://adaptive-metrics.grafana.net/api/v1/usage-analysis?filter=unused" | \
  jq '.metrics[] | {metric_name, series_count, last_queried}'

# 2. 确认未在仪表板 / 告警 / 记录规则中引用
grep -r '<METRIC_NAME>' dashboards/ alerts/ recording-rules/

# 3. 在 Alloy 中添加 write_relabel_config 删除（完整块在 references/api.md）
#    重新加载 Alloy: curl -X POST http://localhost:12345/-/reload

# 4. 验证——指标应在 ~10 分钟后不再出现在序列计数中
curl -s -u "<metrics_user>:<metrics_token>" \
  'https://prometheus-prod-XX.grafana.net/api/prom/api/v1/label/__name__/values' | jq '.data | index("<METRIC_NAME>")'  # → null
```

## 评估影响

```promql
# 总活动序列（计费单位）
grafanacloud_instance_active_series

# 特定由自适应指标规则删除的序列
grafanacloud_instance_active_series_dropped_by_aggregation_rules
```

规则在 ~5 分钟内生效；完整计费影响在 1 小时内出现。原始高基数样本仍在流动，但被删除的标签不再计入计费。

## 资源

- [自适应指标文档](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/metrics-costs/adaptive-metrics/)
- [自适应日志文档](https://grafana.com/docs/grafana-cloud/cost-management-and-billing/reduce-costs/logs-costs/adaptive-logs/)
- [Prometheus 中的基数](https://grafana.com/docs/grafana-cloud/send-data/metrics/cardinality/)
