# Dynatrace 笔记本技能

## 概述

Dynatrace 笔记本是以 JSON 格式存储在文档存储中的文档，包含一个有序的**部分**数组——用于叙述的 markdown 块和用于 DQL 查询并带有可视化的 `dql` 块。部分按数组顺序从上到下渲染。

**使用场景：** 创建、修改、查询或分析笔记本。

## 笔记本 JSON 结构

```json
{
  "name": "我的笔记本",
  "type": "notebook",
  "content": {
    "version": "7",
    "defaultTimeframe": { "from": "now()-2h", "to": "now()" },
    "sections": [
      { "id": "1", "type": "markdown", "markdown": "# 标题" },
      {
        "id": "2", "type": "dql", "title": "查询部分", "showInput": true,
        "state": {
          "input": { "value": "fetch logs | summarize count()" },
          "visualization": "table",
          "visualizationSettings": { "autoSelectVisualization": true, "chartSettings": {} },
          "querySettings": {
            "maxResultRecords": 1000, "defaultScanLimitGbytes": 500,
            "maxResultMegaBytes": 1, "defaultSamplingRatio": 10, "enableSampling": false
          }
        }
      }
    ]
  }
}
```

- 部分按数组顺序渲染。
- 部分类型：`markdown`、`dql`。（`function` 存在但很少使用。）
- 使用字符串-整数 ID（`"1"`、`"2"`、…）；UUID 也被接受。
- `content.defaultTimeframe` 设置默认时间范围；每个部分可以通过 `section.state.input.timeframe` 覆盖。DQL 中允许硬编码时间过滤器。

**可选内容属性：** `defaultSegments`。

## 读取与分析

使用 `dtctl get notebook <id> -o json`（`describe` 仅返回元数据）获取完整内容，然后检查 JSON 以发现其可用属性。在分析前，请仔细阅读 [references/analyzing.md](references/analyzing.md)。

## 创建/更新工作流（必须按顺序）

仔细遵循 [references/create-update.md](references/create-update.md) 中描述的工作流。

**关键规则：**
- 在生成查询之前加载领域技能——不要编造 DQL。
- 在添加到笔记本之前验证所有部分查询。
- 部署前设置 `name`。
- **在 `visualizationSettings` 中优先使用 `autoSelectVisualization: true`**，除非用户请求了特定的可视化类型——当 `false` 时，必须显式设置 `state.visualization`。
- **更新——始终先读取当前状态：** `dtctl get notebook <id> -o json`，将其保存为 `notebook.json`，修改该文件，然后部署。切勿从零开始重建 JSON 或手动注入 `id`——两者都会静默覆盖用户上次部署以来所做的 UI 编辑。
- **使用 `dtctl apply` 部署**——验证将自动运行。如果失败，请修复所有报告的错误后再重新应用。

## 可视化类型

笔记本支持 Dynatrace 可视化的一部分：

- **时间序列**（需要 `timeseries`/`makeTimeseries`）：`lineChart`、`areaChart`、`barChart`、`bandChart`
- **分类**（`summarize ... by:{field}`）：`categoricalBarChart`、`pieChart`、`donutChart`
- **单个值/仪表/计量器**：`singleValue`、`meterBar`、`gauge`
- **表格**（任何数据形状）：`table`、`raw`、`recordView`
- **分布/状态**：`histogram`、`honeycomb`
- **地理地图**：`choropleth`、`dotMap`、`connectionMap`、`bubbleMap`
- **矩阵/相关性**：`heatmap`、`scatterplot`

每个可视化所需的字段类型：[references/sections.md](references/sections.md)。

## 参考

| 文件 | 加载时机 |
|------|-------------|
| [create-update.md](references/create-update.md) | 创建/更新笔记本 |
| [sections.md](references/sections.md) | 部分类型、可视化字段要求、设置 |
| [analyzing.md](references/analyzing.md) | 读取笔记本、提取查询、目的识别 |
