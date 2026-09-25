# 图表 — 基于项目的交互式图表

使用 Apache ECharts 生成交互式图表页面。每个图表都位于 `output/chart-html/` 下独立的专有项目文件夹中，便于复用和迭代。

## 使用场景

任何需要可视化图表的场景：价格图表、对比图、仪表盘、商业分析等。

## 架构

- **ECharts** (CDN) 用于渲染
- **ECharts 原生导出 (`getDataURL`) + canvas 合并** 用于可靠的 PNG 输出
- **基于项目的存储**：每个图表项目一个文件夹
- **无画廊模式**：所有文件都保留在项目文件夹中

## 项目结构（必填）

每个图表项目应遵循以下结构：

```
output/chart-html/
  <项目名称>/
    index.html        # 图表页面
    generate.py       # 生成脚本（用于可重复性）
    README.md         # 标题 / 描述 / 数据源说明
    data.json         # 数据快照
    screenshot.png    # 保存的图片
```

示例文件夹名称：`btc-90d-20260401`

## 工作流程

### 第 1 步：选择模板或自定义布局

可用模板：

| 模板 | 适用于 |
|---|---|
| `line.html` | 时间序列趋势、多序列对比 |
| `bar.html` | 类别对比、排名 |
| `pie.html` | 构成 / 比例分解 |
| `candlestick.html` | OHLCV 价格图表 |
| `scatter.html` | 相关性、分布 |
| `dashboard.html` | KPI 卡片 + 2×2 多图表网格 |
| `radar.html` | 多维度评分 |
| `heatmap.html` | 矩阵 / 日历强度 |
| `dual-axis.html` | 两个不同刻度的序列（例如市值 vs 稳定币供应）— 左右 Y 轴，每个轴有自己的标签颜色 |
| `multi-panel.html` | 堆叠面板共享一个 X 轴（例如价格 + 量 + RSI）— 单个 ECharts 实例，工具提示/缩放跨所有面板同步 |
| `waterfall.html` | 增量贡献分解（例如 P&L 归因、预算差异）— 正负条形图堆叠在浮动基座上 |

### 第 2 步：创建项目文件夹

使用 `create_project(name, description, data_sources)` 从 `scripts/build_chart.py` 中创建。

### 第 3 步：构建并保存图表页面

使用以下任一方式：
- `build_chart(template_name, ...)`
- `build_chart_custom(...`

然后保存为项目文件夹中的 `index.html`：
- `save_chart(html, project_dir=project_dir)`

### 第 4 步：保存可重复的资产

同时保存：
- `save_generate_script(script_content, project_dir)` → `generate.py`
- `save_data(data, project_dir)` → `data.json`
- 项目 README 由 `create_project(...)` 创建

### 第 5 步：预览服务

使用项目根目录服务（推荐）：

```python
preview_serve(
  title="图表预览",
  dir="skills/chart/scripts",
  command="python3 chart_server.py /data/workspace/output/chart-html 7860",
  port=7860
)
```

然后打开：`/preview/<id>/<项目名称>/index.html`

v3.0.1 的重要行为：
- `chart_server.py` 现在在内部重写预览前缀的静态路径（`/preview/<id>/...` → `/...`）然后再进行文件系统查找。
- 这确保预览 iframe 解析真实的 `index.html` 而不是回退到根目录列表。
- 保持项目页面在 `output/chart-html/<项目>/index.html` 下（不要直接使用 `output/chart-html` 作为静态预览，除非有 `chart_server.py`）。

### 第 6 步：导出图片

两种模式：
1. **用户需要网页 + 图片**：点击页面工具栏中的 "💾 保存图片"，保存到当前项目为 `screenshot.png`
2. **用户只需要图片**：调用 `screenshot_chart(project_dir)`（Playwright）并将 `screenshot.png` 直接发送

## 工具栏要求

每个图表页面必须包含以下按钮：

```html
<div class="actions">
  <button onclick="downloadPNG(this)">📥 下载 PNG</button>
  <button onclick="copyToClipboard(this)">📋 复制图片</button>
  <button onclick="saveToProject(this)">💾 保存图片</button>
</div>
```

不要包含画廊条目。

## 关键文件

| 文件 | 目的 |
|------|---------|
| `skills/chart/scripts/base-styles.css` | 基础暗色主题 CSS |
| `skills/chart/scripts/base-export.js` | 导出辅助：下载/复制/保存到项目 |
| `skills/chart/scripts/build_chart.py` | 项目创建、HTML 构建、数据/脚本保存、截图 |
| `skills/chart/scripts/chart_server.py` | 静态服务器 + `/save-chart` API |
| `skills/chart/templates/*.html` | 可复用的图表模板 |
| `output/chart-html/<项目>/*` | 所有生成的图表文件 |

## 注意事项

- 直接在 HTML 中嵌入数据（`const DATA = ...`）以避免 iframe CORS 问题。
- 对于多图表页面，在 `window.CHART_INSTANCES` 中注册所有图表实例。
- 使用有意义的项目名称（`topic-range-date`）以便于查找。
