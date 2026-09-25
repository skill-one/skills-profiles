# Dynatrace 仪表板技能

## 概述

Dynatrace 仪表板是存储在文档存储中的 JSON 文档，包含组件（内容/可视化）、布局（网格定位）和变量（动态查询参数）。

**使用场景：** 创建、修改、查询或分析仪表板。

## 仪表板 JSON 结构

```json
{
  "name": "我的仪表板",
  "type": "dashboard",
  "content": {
    "version": 21,
    "variables": [],
    "tiles": { "<id>": { "type": "data|markdown", ... } },
    "layouts": { "<id>": { "x": 0, "y": 0, "w": 24, "h": 8 } }
  }
}
```

- `tiles` 中的组件 ID 必须与 `layouts` 中的 ID 匹配
- 网格宽度为 24 个单位。常用宽度：24（全宽）、12（半宽）、6（四分之一宽）
- 两种组件类型：`markdown`（文本内容）和 `data`（DQL 查询 + 可视化）

**可选内容属性：** `settings`、`refreshRate`、`annotations`

## 读取与分析

使用 `dtctl get dashboard <id> -o json` 获取完整内容（`describe` 仅返回元数据），然后检查 JSON 以发现其可用属性。在分析前，请仔细阅读 [references/analyzing.md](references/analyzing.md)。

## 创建/更新工作流（必须按顺序执行）

仔细遵循 [references/create-update.md](references/create-update.md) 中描述的工作流。

**关键规则：**
- 在生成查询前加载领域技能 — 不要自行编写 DQL
- 在添加到仪表板前验证所有查询
- 除非用户明确要求，否则查询中不要有时间范围过滤器
- 部署前设置 `name`
- **更新 — 始终先读取当前状态：** `dtctl get dashboard <id> -o json`，将其保存为 `dashboard.json`，修改该文件，然后部署。切勿从零重新构建 JSON 或手动注入 `id` — 两者都会静默覆盖用户上次部署以来的任何 UI 编辑。
- **使用 `dtctl apply` 部署** — 验证将自动运行。如果失败，请修复所有报告的错误后再重新应用。

## 可视化类型

- **时间序列**（需要 `timeseries`/`makeTimeseries`）：`lineChart`、`areaChart`、`barChart`、`bandChart`
- **分类**（`summarize ... by:{field}`）：`categoricalBarChart`、`pieChart`、`donutChart`
- **单值/仪表盘**（单个数值记录）：`singleValue`、`meterBar`、`gauge`
- **表格**（任何数据形状）：`table`、`raw`、`recordList`
- **分布/状态**：`histogram`、`honeycomb`
- **地图**：`choroplethMap`、`dotMap`、`connectionMap`、`bubbleMap`
- **矩阵**：`heatmap`、`scatterplot`

每种可视化所需的字段类型：[references/tiles.md](references/tiles.md)

## 变量快速参考

```json
{ "version": 2, "key": "Service", "type": "query", "visible": true,
  "editable": true, "input": "smartscapeNodes SERVICE | fields name",
  "multiple": false }
```

- **单选：** `filter service.name == $Service`
- **多选：** `filter in(service.name, array($Service))`
- 类型：`query`（DQL 填充）、`csv`（静态列表）、`text`（自由输入）

完整变量参考：[references/variables.md](references/variables.md)

## 参考

| 文件 | 加载时机 |
|------|-------------|
| [create-update.md](references/create-update.md) | 创建/更新仪表板 |
| [tiles.md](references/tiles.md) | 组件类型、可视化字段要求、设置 |
| [variables.md](references/variables.md) | 变量类型、替换策略、模式 |
| [analyzing.md](references/analyzing.md) | 读取仪表板、提取查询、健康评估 |
