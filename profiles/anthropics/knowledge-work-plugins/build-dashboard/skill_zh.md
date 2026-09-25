# /build-dashboard - 构建交互式仪表板

> 如果你看到不熟悉的占位符或需要检查已连接的哪些工具，请参阅 [CONNECTORS.md](../../CONNECTORS.md)。

构建一个自包含的交互式 HTML 仪表板，包含图表、过滤器、表格和专业的样式。直接在浏览器中打开——无需服务器或依赖项。

## 使用方法

```
/build-dashboard 仪表板的描述 [数据源]
```

## 工作流程

### 1. 理解仪表板需求

确定：

- **目的**：高管概览、运营监控、深入分析、团队报告
- **受众**：谁将使用此仪表板？
- **关键指标**：哪些数字最重要？
- **维度**：用户应该能够按什么进行过滤或切片？
- **数据源**：实时查询、粘贴的数据、CSV 文件或示例数据

### 2. 收集数据

**如果已连接数据仓库：**
1. 查询所需数据
2. 将结果作为 JSON 嵌入 HTML 文件中

**如果数据已粘贴或上传：**
1. 解析和清理数据
2. 嵌入仪表板中的 JSON

**如果从描述开始而没有数据：**
1. 创建一个符合描述模式的真实示例数据集
2. 在仪表板中注明它使用的是示例数据
3. 提供用于替换真实数据的说明

### 3. 设计仪表板布局

遵循标准的仪表板布局模式：

```
┌──────────────────────────────────────────────────┐
│  仪表板标题                    [过滤器 ▼]  │
├────────────┬────────────┬────────────┬───────────┤
│  KPI 卡  │  KPI 卡  │  KPI 卡  │ KPI 卡  │
├────────────┴────────────┼────────────┴───────────┤
│                         │                        │
│    主要图表        │   次要图表      │
│    (最大面积)       │                        │
│                         │                        │
├─────────────────────────┴────────────────────────┤
│                                                  │
│    详细表格 (可排序、可滚动)           │
│                                                  │
└──────────────────────────────────────────────────┘
```

**根据内容调整布局：**
- 顶部放置 2-4 个 KPI 卡，用于显示主要数字
- 中间部分放置 1-3 个图表，用于显示趋势和细分
- 可选在底部放置详细表格，用于深入分析数据
- 根据复杂程度，在页眉或侧边栏中放置过滤器

### 4. 构建 HTML 仪表板

使用以下基础模板生成一个自包含的 HTML 文件。该文件包含：

**结构 (HTML)：**
- 语义化的 HTML5 布局
- 使用 CSS Grid 或 Flexbox 的响应式网格
- 过滤器控件（下拉菜单、日期选择器、开关）
- 带值和标签的 KPI 卡
- 图表容器
- 可排序的标题数据表格

**样式 (CSS)：**
- 专业的配色方案（干净的白色、灰色，以及用于数据的强调色）
- 基于卡的布局，带有微妙的阴影
- 一致的排版（使用系统字体以加快加载速度）
- 响应式设计，可在不同屏幕尺寸上工作
- 适用于打印的样式

**交互性 (JavaScript)：**
- 使用 Chart.js 进行交互式图表（通过 CDN 包含）
- 过滤器下拉菜单，可同时更新所有图表和表格
- 可排序的表格列
- 图表上的悬停工具提示
- 数字格式化（逗号、货币、百分比）

**数据 (嵌入的 JSON)：**
- 所有数据直接作为 JavaScript 变量嵌入 HTML 中
- 无需外部数据获取
- 仪表板完全离线工作

### 5. 实现图表类型

使用 Chart.js 用于所有图表。常见的仪表板图表模式：

- **折线图**：时间序列趋势
- **柱状图**：类别比较
- **环形图**：组成（当类别少于 6 个时）
- **堆叠柱状图**：随时间变化的组成
- **混合（柱状图 + 折线图）**：叠加率与数量

使用以下 Chart.js 集成模式为每种图表类型实现。

### 6. 添加交互性

使用以下过滤器交互性实现模式，用于下拉过滤器、日期范围过滤器、组合过滤器逻辑、可排序表格和图表更新。

### 7. 保存和打开

1. 将仪表板保存为具有描述性名称的 HTML 文件（例如，`sales_dashboard.html`）
2. 在用户的默认浏览器中打开它
3. 确认它正确渲染
4. 提供更新数据或自定义的说明

---

## 基础模板

每个仪表板都遵循此结构：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>仪表板标题</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.5.1" integrity="sha384-jb8JQMbMoBUzgWatfe6COACi2ljcDdZQ2OxczGA3bGNeWe+6DChMTBJemed7ZnvJ" crossorigin="anonymous"></script>
    <script src="https://cdn.jsdelivr.net/npm/chartjs-adapter-date-fns@3.0.0" integrity="sha384-cVMg8E3QFwTvGCDuK+ET4PD341jF3W8nO1auiXfuZNQkzbUUiBGLsIQUE+b1mxws" crossorigin="anonymous"></script>
    <style>
        /* 仪表板样式放在这里 */
    </style>
</head>
<body>
    <div class="dashboard-container">
        <header class="dashboard-header">
            <h1>仪表板标题</h1>
            <div class="filters">
                <!-- 过滤器控件 -->
            </div>
        </header>

        <section class="kpi-row">
            <!-- KPI 卡 -->
        </section>

        <section class="chart-row">
            <!-- 图表容器 -->
        </section>

        <section class="table-section">
            <!-- 数据表格 -->
        </section>

        <footer class="dashboard-footer">
            <span>数据更新时间：<span id="data-date"></span></span>
        </footer>
    </div>

    <script>
        // 嵌入数据
        const DATA = [];

        // 仪表板逻辑
        class Dashboard {
            constructor(data) {
                this.rawData = data;
                this.filteredData = data;
                this.charts = {};
                this.init();
            }

            init() {
                this.setupFilters();
                this.renderKPIs();
                this.renderCharts();
                this.renderTable();
            }

            applyFilters() {
                // 过滤逻辑
                this.filteredData = this.rawData.filter(row => {
                    // 应用每个激活的过滤器
                    return true; // 占位符
                });
                this.renderKPIs();
                this.updateCharts();
                this.renderTable();
            }

            // ... 每个部分的方法
        }

        const dashboard = new Dashboard(DATA);
    </script>
</body>
</html>
```

## KPI 卡模式

```html
<div class="kpi-card">
    <div class="kpi-label">总收入</div>
    <div class="kpi-value" id="kpi-revenue">¥0</div>
    <div class="kpi-change positive" id="kpi-revenue-change">+0%</div>
</div>
```

```javascript
function renderKPI(elementId, value, previousValue, format = 'number') {
    const el = document.getElementById(elementId);
    const changeEl = document.getElementById(elementId + '-change');

    // 格式化值
    el.textContent = formatValue(value, format);

    // 计算并显示变化
    if (previousValue && previousValue !== 0) {
        const pctChange = ((value - previousValue) / previousValue) * 100;
        const sign = pctChange >= 0 ? '+' : '';
        changeEl.textContent = `${sign}${pctChange.toFixed(1)}% vs 上期`;
        changeEl.className = `kpi-change ${pctChange >= 0 ? 'positive' : 'negative'}`;
    }
}

function formatValue(value, format) {
    switch (format) {
        case 'currency':
            if (value >= 1e6) return `$${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `$${(value / 1e3).toFixed(1)}K`;
            return `$${value.toFixed(0)}`;
        case 'percent':
            return `${value.toFixed(1)}%`;
        case 'number':
            if (value >= 1e6) return `${(value / 1e6).toFixed(1)}M`;
            if (value >= 1e3) return `${(value / 1e3).toFixed(1)}K`;
            return value.toLocaleString();
        default:
            return value.toString();
    }
}
```

## Chart.js 集成

### 图表容器模式

```html
<div class="chart-container">
    <h3 class="chart-title">月度收入趋势</h3>
    <canvas id="revenue-chart"></canvas>
</div>
```

### 折线图

```javascript
function createLineChart(canvasId, labels, datasets) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: datasets.map((ds, i) => ({
                label: ds.label,
                data: ds.data,
                borderColor: COLORS[i % COLORS.length],
                backgroundColor: COLORS[i % COLORS.length] + '20',
                borderWidth: 2,
                fill: ds.fill || false,
                tension: 0.3,
                pointRadius: 3,
                pointHoverRadius: 6,
            }))
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    position: 'top',
                    labels: { usePointStyle: true, padding: 20 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${formatValue(context.parsed.y, 'currency')}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatValue(value, 'currency');
                        }
                    }
                }
            }
        }
    });
}
```

### 柱状图

```javascript
function createBarChart(canvasId, labels, data, options = {}) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    const isHorizontal = options.horizontal || labels.length > 8;

    return new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: options.label || '值',
                data: data,
                backgroundColor: options.colors || COLORS.map(c => c + 'CC'),
                borderColor: options.colors || COLORS,
                borderWidth: 1,
                borderRadius: 4,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: isHorizontal ? 'y' : 'x',
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return formatValue(context.parsed[isHorizontal ? 'x' : 'y'], options.format || 'number');
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    grid: { display: isHorizontal },
                    ticks: isHorizontal ? {
                        callback: function(value) {
                            return formatValue(value, options.format || 'number');
                        }
                    } : {}
                },
                y: {
                    beginAtZero: !isHorizontal,
                    grid: { display: !isHorizontal },
                    ticks: !isHorizontal ? {
                        callback: function(value) {
                            return formatValue(value, options.format || 'number');
                        }
                    } : {}
                }
            }
        }
    });
}
```

### 环形图

```javascript
function createDoughnutChart(canvasId, labels, data) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: COLORS.map(c => c + 'CC'),
                borderColor: '#ffffff',
                borderWidth: 2,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: {
                legend: {
                    position: 'right',
                    labels: { usePointStyle: true, padding: 15 }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const total = context.dataset.data.reduce((a, b) => a + b, 0);
                            const pct = ((context.parsed / total) * 100).toFixed(1);
                            return `${context.label}: ${formatValue(context.parsed, 'number')} (${pct}%)`;
                        }
                    }
                }
            }
        }
    });
}
```

### 过滤器变化时更新图表

```javascript
function updateChart(chart, newLabels, newData) {
    chart.data.labels = newLabels;

    if (Array.isArray(newData[0])) {
        // 多个数据集
        newData.forEach((data, i) => {
            chart.data.datasets[i].data = data;
        });
    } else {
        chart.data.datasets[0].data = newData;
    }

    chart.update('none'); // 'none' 禁用动画以实现即时更新
}
```

## 过滤器和交互性实现

### 下拉过滤器

```html
<div class="filter-group">
    <label for="filter-region">区域</label>
    <select id="filter-region" onchange="dashboard.applyFilters()">
        <option value="all">所有区域</option>
    </select>
</div>
```

```javascript
function populateFilter(selectId, data, field) {
    const select = document.getElementById(selectId);
    const values = [...new Set(data.map(d => d[field]))].sort();

    // 保留 "所有" 选项，添加唯一值
    values.forEach(val => {
        const option = document.createElement('option');
        option.value = val;
        option.textContent = val;
        select.appendChild(option);
    });
}

function getFilterValue(selectId) {
    const val = document.getElementById(selectId).value;
    return val === 'all' ? null : val;
}
```

### 日期范围过滤器

```html
<div class="filter-group">
    <label>日期范围</label>
    <input type="date" id="filter-date-start" onchange="dashboard.applyFilters()">
    <span>至</span>
    <input type="date" id="filter-date-end" onchange="dashboard.applyFilters()">
</div>
```

```javascript
function filterByDateRange(data, dateField, startDate, endDate) {
    return data.filter(row => {
        const rowDate = new Date(row[dateField]);
        if (startDate && rowDate < new Date(startDate)) return false;
        if (endDate && rowDate > new Date(endDate)) return false;
        return true;
    });
}
```

### 组合过滤器逻辑

```javascript
applyFilters() {
    const region = getFilterValue('filter-region');
    const category = getFilterValue('filter-category');
    const startDate = document.getElementById('filter-date-start').value;
    const endDate = document.getElementById('filter-date-end').value;

    this.filteredData = this.rawData.filter(row => {
        if (region && row.region !== region) return false;
        if (category && row.category !== category) return false;
        if (startDate && row.date < startDate) return false;
        if (endDate && row.date > endDate) return false;
        return true;
    });

    this.renderKPIs();
    this.updateCharts();
    this.renderTable();
}
```

### 可排序表格

```javascript
function renderTable(containerId, data, columns) {
    const container = document.getElementById(containerId);
    let sortCol = null;
    let sortDir = 'desc';

    function render(sortedData) {
        let html = '<table class="data-table">';

        // 头部
        html += '<thead><tr>';
        columns.forEach(col => {
            const arrow = sortCol === col.field
                ? (sortDir === 'asc' ? ' ▲' : ' ▼')
                : '';
            html += `<th onclick="sortTable('${col.field}')" style="cursor:pointer">${col.label}${arrow}</th>`;
        });
        html += '</tr></thead>';

        // 身体
        html += '<tbody>';
        sortedData.forEach(row => {
            html += '<tr>';
            columns.forEach(col => {
                const value = col.format ? formatValue(row[col.field], col.format) : row[col.field];
                html += `<td>${value}</td>`;
            });
            html += '</tr>';
        });
        html += '</tbody></table>';

        container.innerHTML = html;
    }

    window.sortTable = function(field) {
        if (sortCol === field) {
            sortDir = sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            sortCol = field;
            sortDir = 'desc';
        }
        const sorted = [...data].sort((a, b) => {
            const aVal = a[field], bVal = b[field];
            const cmp = aVal < bVal ? -1 : aVal > bVal ? 1 : 0;
            return sortDir === 'asc' ? cmp : -cmp;
        });
        render(sorted);
    };

    render(data);
}
```

## 仪表板 CSS 样式

### 配色方案

```css
:root {
    /* 背景层 */
    --bg-primary: #f8f9fa;
    --bg-card: #ffffff;
    --bg-header: #1a1a2e;

    /* 文本 */
    --text-primary: #212529;
    --text-secondary: #6c757d;
    --text-on-dark: #ffffff;

    /* 数据的强调色 */
    --color-1: #4C72B0;
    --color-2: #DD8452;
    --color-3: #55A868;
    --color-4: #C44E52;
    --color-5: #8172B3;
    --color-6: #937860;

    /* 状态颜色 */
    --positive: #28a745;
    --negative: #dc3545;
    --neutral: #6c757d;

    /* 间距 */
    --gap: 16px;
    --radius: 8px;
}
```

### 布局

```css
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.5;
}

.dashboard-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: var(--gap);
}

.dashboard-header {
    background: var(--bg-header);
    color: var(--text-on-dark);
    padding: 20px 24px;
    border-radius: var(--radius);
    margin-bottom: var(--gap);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.dashboard-header h1 {
    font-size: 20px;
    font-weight: 600;
}
```

### KPI 卡

```css
.kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: var(--gap);
    margin-bottom: var(--gap);
}

.kpi-card {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.kpi-label {
    font-size: 13px;
    color: var(--text-secondary);
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 4px;
}

.kpi-change {
    font-size: 13px;
    font-weight: 500;
}

.kpi-change.positive { color: var(--positive); }
.kpi-change.negative { color: var(--negative); }
```

### 图表容器

```css
.chart-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: var(--gap);
    margin-bottom: var(--gap);
}

.chart-container {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.chart-container h3 {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 16px;
}

.chart-container canvas {
    max-height: 300px;
}
```

### 过滤器

```css
.filters {
    display: flex;
    gap: 12px;
    align-items: center;
    flex-wrap: wrap;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 6px;
}

.filter-group label {
    font-size: 12px;
    color: rgba(255, 255, 255, 0.7);
}

.filter-group select,
.filter-group input[type="date"] {
    padding: 6px 10px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.1);
    color: var(--text-on-dark);
    font-size: 13px;
}

.filter-group select option {
    background: var(--bg-header);
    color: var(--text-on-dark);
}
```

### 数据表格

```css
.table-section {
    background: var(--bg-card);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
    overflow-x: auto;
}

.data-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
}

.data-table thead th {
    text-align: left;
    padding: 10px 12px;
    border-bottom: 2px solid #dee2e6;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    white-space: nowrap;
    user-select: none;
}

.data-table thead th:hover {
    color: var(--text-primary);
    background: #f8f9fa;
}

.data-table tbody td {
    padding: 10px 12px;
    border-bottom: 1px solid #f0f0f0;
}

.data-table tbody tr:hover {
    background: #f8f9fa;
}

.data-table tbody tr:last-child td {
    border-bottom: none;
}
```

### 响应式设计

```css
@media (max-width: 768px) {
    .dashboard-header {
        flex-direction: column;
        align-items: flex-start;
    }

    .kpi-row {
        grid-template-columns: repeat(2, 1fr);
    }

    .chart-row {
        grid-template-columns: 1fr;
    }

    .filters {
        flex-direction: column;
        align-items: flex-start;
    }
}

@media print {
    body { background: white; }
    .dashboard-container { max-width: none; }
    .filters { display: none; }
    .chart-container { break-inside: avoid; }
    .kpi-card { border: 1px solid #dee2e6; box-shadow: none; }
}
```

## 性能考虑（大数据集）

### 数据大小指南

| 数据大小 | 方法 |
|---|---|
| <1,000 行 | 直接嵌入 HTML。完全交互式。 |
| 1,000 - 10,000 行 | 嵌入 HTML。可能需要在浏览器中预先聚合。 |
| 10,000 - 100,000 行 | 服务器端预先聚合。仅嵌入聚合数据。 |
| >100,000 行 | 不适合客户端仪表板。使用 BI 工具或分页。 |

### 预先聚合模式

与其嵌入 50,000 行原始数据并在浏览器中聚合：

```javascript
// 不要：嵌入 50,000 行原始数据
const RAW_DATA = [/* 50,000 行 */];

// 要：预先聚合后嵌入
const CHART_DATA = {
    monthly_revenue: [
        { month: '2024-01', revenue: 150000, orders: 1200 },
        { month: '2024-02', revenue: 165000, orders: 1350 },
        // ... 12 行而不是 50,000
    ],
    top_products: [
        { product: 'Widget A', revenue: 45000 },
        // ... 10 行
    ],
    kpis: {
        total_revenue: 1980000,
        total_orders: 15600,
        avg_order_value: 127,
    }
};
```

### 图表性能

- 折线图限制为每个系列 <500 个数据点（如有必要则下采样）
- 柱状图限制为 <50 个类别
- 散点图限制为 1,000 个点（大数据集使用采样）
- 禁用具有许多图表的仪表板的动画：`animation: false` 在 Chart.js 选项中
- 使用 `Chart.update('none')` 而不是 `Chart.update()` 以便过滤器触发更新

### DOM 性能

- 限制数据表格为 100-200 行可见行。更多则添加分页。
- 使用 `requestAnimationFrame` 进行协调的图表更新
- 避免在过滤器更改时重建整个 DOM——仅更新更改的元素

```javascript
// 高效的表格分页
function renderTablePage(data, page, pageSize = 50) {
    const start = page * pageSize;
    const end = Math.min(start + pageSize, data.length);
    const pageData = data.slice(start, end);
    // 仅渲染 pageData
    // 显示分页控件："显示 1-50 of 2,340"
}
```

## 示例

```
/build-dashboard 月度销售仪表板，包含收入趋势、热门产品和区域细分。数据在订单表中。
```

```
/build-dashboard 这里是我们的支持工单数据 [粘贴 CSV]。构建一个仪表板，显示按优先级划分的量、响应时间趋势和解决率。
```

```
/build-dashboard 为 SaaS 公司创建一个模板高管仪表板，显示 MRR、流失率、新客户和 NPS。使用示例数据。
```

## 建议

- 仪表板是完全自包含的 HTML 文件——通过发送文件与任何人分享
- 对于实时仪表板，请考虑连接到 BI 工具。这些仪表板是时间点的快照
- 请求“暗黑模式”或“演示模式”以获得不同的样式
- 您可以请求特定的配色方案以匹配您的品牌
