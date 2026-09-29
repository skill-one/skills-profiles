---
name: dashboarding
description: 通过 HTTP API 以 JSON 格式构建、修改和发布 Grafana 仪表板——支持各种面板类型（时序图 / 统计图 / 指针图 / 表格 / 热力图 / 日志 / 跟踪 / 节点图）、`gridPos` 24 列布局、单位、阈值、模板 + 数据源 + 链式变量、转换（`organize` / `calculateField` / `filterByValue`）、面板 + 仪表板链接（使用 `${__field.labels.x}` / `${__from}`）以及 Loki/Prometheus 注释。适用于以下场景：脚本化仪表板创建、为新增服务编写仪表板 JSON、添加 `$job` 下拉变量、通过转换计算 "错误 %" 列、将部署信息作为注释叠加、或通过 `POST /api/dashboards/db` 推送仪表板——即使用户说 "为这个指标创建仪表板"、"添加服务下拉"、"将错误显示为百分比"、"叠加我们的部署" 或 "导出仪表板 JSON" 而未提及 API 或架构。每次 API 推送后，请通过返回的 `version` 并对仪表板 UID 进行 GET 请求进行验证。
---

# Grafana 仪表板编写

> **文档**: https://grafana.com/docs/grafana/latest/dashboards/

仪表板是 JSON 格式。一次编写，通过 API 推送，通过 `uid` 共享。

## 前置条件

- 从您的机器可访问 Grafana 堆栈（OSS、企业版或云版）
- 具有 `dashboards:write` 权限的 API 令牌（`Authorization: Bearer <token>`）
- 用于检查响应的 `jq`
- [`references/json-schema.md`](references/json-schema.md) 中的 JSON-schema 摘要表

## 常见工作流程

### 1. 通过 API 推送新仪表板并验证

```bash
# 1. 构建负载——封装仪表板 JSON，设置文件夹，标记覆盖
cat > /tmp/dash.json <<'JSON'
{
  "dashboard": {
    "uid": "demo-svc-v1",
    "title": "Demo Service",
    "schemaVersion": 41,
    "tags": ["demo"],
    "time": { "from": "now-1h", "to": "now" },
    "templating": { "list": [] },
    "panels": [{
      "id": 1, "type": "timeseries", "title": "Request Rate",
      "gridPos": { "x": 0, "y": 0, "w": 24, "h": 8 },
      "datasource": { "type": "prometheus", "uid": "prometheus" },
      "targets": [{
        "expr": "sum(rate(http_requests_total[5m])) by (status_code)",
        "legendFormat": "{{status_code}}", "refId": "A"
      }],
      "fieldConfig": { "defaults": { "unit": "reqps" }, "overrides": [] }
    }]
  },
  "folderUid": "",
  "overwrite": true,
  "message": "initial push"
}
JSON

# 2. 在发送之前验证 JSON（捕获尾随逗号错误）
jq empty /tmp/dash.json && echo "json ok"

# 3. POST
RESP=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  "$GRAFANA/api/dashboards/db" -d @/tmp/dash.json)
echo "$RESP" | jq '{status, uid, url, version}'
# 预期：status="success", url="/d/demo-svc-v1/...", version=1（每次推送时递增）

# 4. 验证往返过程——读取并确认一个面板 + 预期的标题
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/demo-svc-v1" \
  | jq '{title: .dashboard.title, panels: (.dashboard.panels | length)}'
# 预期：{"title":"Demo Service","panels":1}

# 5. 在浏览器中打开仪表板——确认面板使用数据渲染。
```

### 2. 向现有仪表板添加 `$job` 模板变量

```bash
# 1. 获取现有仪表板
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/demo-svc-v1" > /tmp/dash.json

# 2. 编辑 templating.list — 追加：
#   { "name":"job", "type":"query",
#     "datasource":{"type":"prometheus","uid":"prometheus"},
#     "query":{"query":"label_values(up, job)","refId":"A"},
#     "refresh":2, "includeAll":true, "multi":true, "label":"Service" }
#  (使用 jq、编辑器或 Grafana UI —— schema 在 references/json-schema.md 中。)

# 3. 将面板 expr 更新为使用变量：rate(http_requests_total{job=~"$job"}[5m])

# 4. 使用 overwrite: true 将其 POST 回去。验证变量出现在 UI 下拉列表中。
```

### 3. 使用转换计算 "Error %" 列

```json
{
  "id": "calculateField",
  "options": {
    "alias": "Error %", "mode": "reduceRow",
    "reduce": { "reducer": "last" },
    "binary": { "left": "errors", "right": "total", "operator": "/" }
  }
}
```

将其添加到面板的 `transformations: []`。在 UI 面板检查器中验证——新字段应出现并随变量选择更新。

完整 schema（面板、单位、所有转换、注释、链接）：[`references/json-schema.md`](references/json-schema.md)。

## API 参考

```bash
# 获取
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/dashboards/uid/<uid>" | jq '.dashboard'

# 搜索
curl -s -H "Authorization: Bearer $TOKEN" \
  "$GRAFANA/api/search?query=kubernetes&type=dash-db" | jq '.[] | {uid,title,folderTitle}'

# 创建文件夹
curl -s -X POST -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" "$GRAFANA/api/folders" \
  -d '{"uid":"platform-team","title":"Platform Team"}'
```

对于嵌入在应用插件中的仪表板，使用 `@grafana/scenes`（技能 `grafana-o11y:grafana-scenes`）。

## 资源

- [Dashboard JSON 模型](https://grafana.com/docs/grafana/latest/dashboards/build-dashboards/view-dashboard-json-model/)
- [HTTP API — 仪表板](https://grafana.com/docs/grafana/latest/developers/http_api/dashboard/)
- [面板类型](https://grafana.com/docs/grafana/latest/panels-visualizations/)
- [变量](https://grafana.com/docs/grafana/latest/dashboards/variables/)
- [转换](https://grafana.com/docs/grafana/latest/panels-visualizations/query-transform-data/transform-data/)
