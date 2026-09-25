# Grafana Cloud 人工智能与机器学习

> **文档**: https://grafana.com/docs/grafana-cloud/alerting-and-irm/machine-learning/

在一个 Grafana Cloud 堆栈中，集成了机器学习告警、自动根本原因分析（RCA）和基于大型语言模型（LLM）的助手。

## 前置条件

- Grafana Cloud 堆栈（专业版 / 高级版 — 大部分功能已正式发布，部分功能处于预览阶段）
- 具有对机器学习 / Sift / LLM 插件端点的 `plugins:write` 权限的 API 令牌
- 对于动态告警：您要预测的指标至少需要 14 天（理想情况下为 90 天）的历史数据

## 常见工作流

### 1. 使用动态告警进行预测性告警

```bash
# 1. 创建预测任务（Prophet — 学习每日/每周的季节性）
curl -X POST https://<stack>.grafana.net/api/plugins/grafana-ml-app/resources/ml/v1/forecast \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "cpu-forecast",
    "metric": "avg(rate(node_cpu_seconds_total{mode=\"user\"}[5m]))",
    "datasourceId": 1,
    "interval": 300,
    "trainingWindow": "90d",
    "forecastWindow": "7d",
    "algorithm": { "name": "prophet", "config": {} }
  }'

# 2. 验证任务是否正在生成预测值指标（可能需要几分钟）。
#    <datasourceId> 必须与上面使用的 datasourceId 匹配（通过
#    GET /api/datasources 查找），或者从 Explore 中运行查询。
curl -s -H "Authorization: Bearer <token>" \
  'https://<stack>.grafana.net/api/datasources/proxy/<datasourceId>/api/v1/query?query=ml_forecast_upper{job="cpu-forecast"}' \
  | jq '.data.result | length'
# 预期结果：> 0

# 3. 添加一个告警，当实际值超过上限时触发
# expr:  avg(rate(node_cpu_seconds_total{mode="user"}[5m]))
#         > ml_forecast_upper{job="cpu-forecast"} * 1.1
```

### 2. 异常值告警 — 一个服务与其他服务不同

```bash
# 1. 创建异常值任务（DBSCAN — 将同类分组，标记异常值）
curl -X POST https://<stack>.grafana.net/api/plugins/grafana-ml-app/resources/ml/v1/outlier \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{
    "name": "service-error-outliers",
    "metric": "sum(rate(http_requests_total{status=~\"5..\"}[5m])) by (service)",
    "datasourceId": 1,
    "interval": 300,
    "algorithm": { "name": "dbscan", "sensitivity": 0.5, "config": { "epsilon": 0.5 } }
  }'

# 2. 验证分数指标是否存在（<datasourceId> 必须与上面使用的
#    datasourceId 匹配，或者从 Explore 中运行查询）
curl -s -H "Authorization: Bearer <token>" \
  'https://<stack>.grafana.net/api/datasources/proxy/<datasourceId>/api/v1/query?query=ml_outlier_score{job="service-error-outliers"}' \
  | jq '.data.result | length'

# 3. 当 ml_outlier_score{job="service-error-outliers"} > 0.8 持续 5 分钟时告警
```

### 3. 运行 Sift 调查

```bash
# 1. 从 API 触发（或从 Explore / Incident / OnCall）
curl -X POST https://<stack>.grafana.net/api/plugins/grafana-sift-app/resources/sift/v1/investigations \
  -H "Authorization: Bearer <token>" -H "Content-Type: application/json" \
  -d '{ "name":"checkout-spike","start":"2024-02-01T10:00:00Z","end":"2024-02-01T10:30:00Z",
        "filters":{"service":"checkout","namespace":"production"} }'

# 2. 响应中包含调查 ID — 在 UI 中打开它：
#    https://<stack>.grafana.net/a/grafana-sift-app/investigations/<id>
# 3. 验证分析是否运行 — 每个的 8 个检查都显示 ✔ 或 ✖，并带有相关证据。
```

有关完整的 8 分析表格，请参阅 [`references/sift.md`](references/sift.md)。

### 4. 连接 LLM 插件

```yaml
# 1. 配置（provisioning/plugins/llm.yaml — 参见 references/llm-and-graph.md）
apiVersion: 1
apps:
  - type: grafana-llm-app
    jsonData: { openAIUrl: https://api.openai.com, openAIModel: gpt-4o }
    secureJsonData: { openAIKey: sk-... }
```

```bash
# 2. 重启 Grafana，然后验证健康端点报告配置的提供者
curl -s -H "Authorization: Bearer <token>" \
  https://<stack>.grafana.net/api/plugins/grafana-llm-app/health | jq
# 预期结果：{"status":"ok", ...}

# 3. 在面板中验证 — 打开任何面板，点击助手图标，询问“这个查询做什么？”
```

有关助手功能、知识图谱搜索语法和自适应指标建议，请参阅 [`references/llm-and-graph.md`](references/llm-and-graph.md)。

## 资源

- [机器学习文档](https://grafana.com/docs/grafana-cloud/alerting-and-irm/machine-learning/)
- [Sift](https://grafana.com/docs/grafana-cloud/alerting-and-irm/machine-learning/sift/)
- [Grafana 助手](https://grafana.com/docs/grafana-cloud/visualizations/grafana-assistant/)
- [LLM 插件](https://grafana.com/grafana/plugins/grafana-llm-app/)
