# 图表可视化技能

该技能提供了一套将数据转化为可视化图表的完整工作流。它涵盖了图表选择、参数提取和图像生成。

## 工作流

要可视化数据，请按照以下步骤操作：

### 1. 智能图表选择
分析用户的数据特征，以确定最合适的图表类型。使用以下指南（并参考 `references/` 目录获取详细规格）：

- **时间序列**：使用 `generate_line_chart`（趋势）或 `generate_area_chart`（累积趋势）。使用 `generate_dual_axes_chart` 用于两个不同的刻度。
- **比较**：使用 `generate_bar_chart`（分类）或 `generate_column_chart`。使用 `generate_histogram_chart` 用于频率分布。
- **部分与整体**：使用 `generate_pie_chart` 或 `generate_treemap_chart`（层次结构）。
- **关系与流程**：使用 `generate_scatter_chart`（相关性）、`generate_sankey_chart`（流程）或 `generate_venn_chart`（重叠）。
- **地图**：使用 `generate_district_map`（区域）、`generate_pin_map`（点）或 `generate_path_map`（路线）。
- **层次结构与树状图**：使用 `generate_organization_chart` 或 `generate_mind_map`。
- **专业图表**：
    - `generate_radar_chart`：多维比较。
    - `generate_funnel_chart`：流程阶段。
    - `generate_liquid_chart`：百分比/进度。
    - `generate_word_cloud_chart`：文本频率。
    - `generate_boxplot_chart` 或 `generate_violin_chart`：统计分布。
    - `generate_network_graph`：复杂的节点-边关系。
    - `generate_fishbone_diagram`：因果分析。
    - `generate_flow_diagram`：流程图。
    - `generate_spreadsheet`：表格数据或数据透视表，用于结构化数据的展示和交叉分析。

### 2. 参数提取
选择图表类型后，读取 `references/` 目录中对应的文件（例如 `references/generate_line_chart.md`），以识别所需和可选字段。
从用户输入中提取数据，并将其映射到预期的 `args` 格式。

### 3. 图表生成
调用 `scripts/generate.js` 脚本，并传入 JSON 负载。

**负载格式：**
```json
{
  "tool": "generate_chart_type_name",
  "args": {
    "data": [...],
    "title": "...",
    "theme": "...",
    "style": { ... }
  }
}
```

**执行命令：**
```bash
node ./scripts/generate.js '<payload_json>'
```

### 4. 结果返回
脚本将输出生成图表图像的 URL。
返回以下内容给用户：
- 图像 URL。
- 生成时使用的完整 `args`（规格）。

## 参考材料
每种图表类型的详细规格位于 `references/` 目录中。查阅这些文件以确保传递给脚本的 `args` 符合预期模式。

## 许可证

该 `SKILL.md` 由 [antvis/chart-visualization-skills](https://github.com/antvis/chart-visualization-skills) 提供。
根据 [MIT 许可证](https://github.com/antvis/chart-visualization-skills/blob/master/LICENSE) 授权。
