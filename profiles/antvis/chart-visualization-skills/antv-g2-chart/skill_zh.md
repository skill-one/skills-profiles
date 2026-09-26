# G2 v5 图表可视化

## 概述

G2 v5 是 AntV 的图形语法图表库。它使用 **Spec 模式** — 一种声明式的 JSON 类配置风格。生成的示例应从完整的 spec 开始；运行时可后续通过 `chart.options()` 合并本地更新。

```javascript
import { Chart } from '@antv/g2';

const chart = new Chart({ container: 'container', autoFit: true });
chart.options({
  type: 'interval',
  data: [{ genre: 'Sports', sold: 275 }],
  encode: { x: 'genre', y: 'sold' },
});
chart.render();
```

### CDN 使用

```html
<script src="https://unpkg.com/@antv/g2@5/dist/g2.min.js"></script>
<script>
  const chart = new G2.Chart({ container: 'container', autoFit: true });
  chart.options({
    type: 'interval',
    data: [{ genre: 'Sports', sold: 275 }],
    encode: { x: 'genre', y: 'sold' },
  });
  chart.render();
</script>
```

## 内容检索服务

在使用 AntV G2 进行数据可视化时，如果您需要了解 G2 v5 的概念、用法、API、示例及其他方面，可以使用提供的内容检索服务。使用该技能时，内容通过 antv HTTP API 服务器使用 GET 请求检索。

- 主机：`https://sive.antv.antgroup.com`
- 端点：`/api/v1/context/retrieve`
- 方法：`GET`
- 参数：`query`, `library`, `topK`, `content`, `maxTokens`

通过查询检索参考文档（混合搜索 = FTS + 向量 + RRF 融合）。

| 参数 | 类型 | 必填 | 描述 |
|---|---|---|---|
| `query` | string | ✅ | 搜索关键词，例如 `bar chart interval` |
| `library` | string | ✅ | 库名称：`g2`, `g6`, `x6` |
| `topK` | number | | 返回结果数量（默认：5） |
| `content` | boolean | | 返回完整参考文档 markdown（默认：true） |
| `maxTokens` | number | | 每个结果的最大 token 数量（默认：无限制） |

```bash
curl "https://sive.antv.antgroup.com/api/v1/context/retrieve?query=bar+chart+stacked&library=g2"
```

## 严格规则

### 必须仅使用 V5 Spec 模式

```javascript
// ❌ 错误 — V4 链式 API（已弃用，不会渲染）
chart.interval()
  .data([...])
  .encode('x', 'genre')
  .encode('y', 'sold')
  .style({ radius: 4 });

// ✅ 正确 — V5 Spec 模式
chart.options({
  type: 'interval',
  data: [...],
  encode: { x: 'genre', y: 'sold' },
  style: { radius: 4 },
});
```

### 多标记叠加使用 `view + children`

`chart.options()` 支持增量深度合并更新，这对于运行时交互很有用。对于生成的单次代码，提供完整的初始 spec。要创建独立的叠加标记，使用一个 `type: 'view'` 并带有 `children`；顺序更改根 `type` 不会创建叠加效果。

```javascript
// ❌ 错误 — 这会改变一个根标记从线到点；它不会叠加它们
chart.options({ type: 'line', data, encode: { x: 'date', y: 'value' } });
chart.options({ type: 'point', data, encode: { x: 'date', y: 'value' } });

// ✅ 正确 — 多标记的 children 数组
chart.options({
  type: 'view',
  data,
  children: [
    { type: 'line',  encode: { x: 'date', y: 'value' } },
    { type: 'point', encode: { x: 'date', y: 'value' } },
  ],
});
```

### 必须有 `container`，`chart.render()` 在最后

```javascript
// ❌ 错误 — 没有容器，没有渲染
const chart = new Chart();
chart.options({ type: 'interval', data });

// ✅ 正确
const chart = new Chart({ container: 'container', autoFit: true });
chart.options({ type: 'interval', data, encode: { x: 'genre', y: 'sold' } });
chart.render();
```

### 必须使用正确的标记类型

| ❌ 虚构（来自 ECharts/Vega） | ✅ G2 正确替换 |
|---|---|
| `type: 'ruleX'` | `type: 'lineX'` |
| `type: 'ruleY'` | `type: 'lineY'` |
| `type: 'regionX'` | `type: 'rangeX'` |
| `type: 'regionY'` | `type: 'rangeY'` |
| `type: 'venn'` | `type: 'path'` + transform |

**G2 正确标记**：`interval`, `line`, `area`, `point`, `rect`, `cell`, `text`, `image`, `path`, `polygon`, `shape`, `link`, `connector`, `vector`, `lineX`, `lineY`, `rangeX`, `rangeY`, `range`, `box`, `boxplot`, `density`, `heatmap`, `beeswarm`, `treemap`, `pack`, `partition`, `tree`, `sankey`, `chord`, `wordCloud`, `gauge`, `liquid`。`sunburst` 需要 `@antv/g2-extension-plot`。

### `encode` 是对象，`transform` 是数组

```javascript
// ❌ 错误
.encode('x', 'genre')
.transform: { type: 'stackY' }

// ✅ 正确
encode: { x: 'genre', y: 'sold' }
transform: [{ type: 'stackY' }]
```

### `labels` 是复数；范围编码使用标记适当的通道

```javascript
// ❌ 错误
label: { text: 'sold' }

// ✅ 正确
labels: [{ text: 'sold' }]
// Interval / link 范围可以使用两字段数组或 y + y1。
encode: { y: ['start', 'end'] }
// RangeY 明确使用 y + y1。
encode: { y: 'start', y1: 'end' }
```

### 用户代码中不能使用 d3

```javascript
// ❌ 错误 — d3 没有在用户作用域中暴露
const total = d3.sum(data, d => d.value);

// ✅ 正确 — 使用原生 JS 或 G2 内置转换
const total = data.reduce((sum, d) => sum + d.value, 0);
```

### 不能使用白色/近白色填充，不能使用 `padding` 作为数组

```javascript
// ❌ 错误
style: { fill: '#fff' }       // 在白色背景上不可见
padding: [40, 30, 40, 50]     // 在 G2 v5 中无效

// ✅ 正确
encode: { color: 'group' }    // 让 G2 分配颜色
padding: 40                   // 单个数字或 'auto'
```

### 转置是转换，不是坐标类型

```javascript
// ❌ 错误
coordinate: { type: 'transpose' }

// ✅ 正确
coordinate: { transform: [{ type: 'transpose' }] }
```

## 默认美学 / 默认视觉基线

目标是默认清晰、克制、可读，而不是给每张图添加相同装饰。先遵守以下决策，再按需检索 `default+aesthetics+design` 获取完整示例。

> 注意区分两种“默认”。G2 引擎默认（`theme/create.ts`）是 `line.lineWidth: 1`、`area.fillOpacity: 0.85`、矩形 `radius` 无圆角；本节标记基线里的 `radius: 4` / `lineWidth: 2` / `fillOpacity: 0.5~0.6` 是本技能的**约定值**，用来覆写引擎默认让生成示例更好看，必须显式写在 `style` 里，不是省略即生效。

1. **通用**：`container`、完整的初始 `chart.options()` spec、`chart.render()` 是必须项；普通嵌入式图优先 `autoFit: true`、`theme: 'classic'` 与 `padding: 'auto'`。`classic` 是为稳定视觉显式选择的浅色预设，不是引擎默认主题（引擎默认推断为 `light`）；深色容器使用 `classicDark`。两者共用同一套 `category10` 色板（首选 `#5B8FF9`），因此稳定主色在浅/深主题下都可用。
2. **颜色表达语义**：仅当颜色表示独立的系列、状态或分组时使用 `encode.color` 和图例。单指标分类比较使用稳定单色（如 `style.fill: '#5B8FF9'`，作为样式值是合法的）并关闭颜色图例，避免彩虹柱和冗余图例。禁止的是把 hex 字符串存进数据后作为 `encode.color` 的类别字段编码。
3. **标记基线**（约定值，覆写引擎默认）：interval 用 `radius: 4`（引擎默认无圆角）；line 用 `lineWidth: 2`（引擎默认 `1`）；area 用 `fillOpacity: 0.5~0.6`（引擎默认 `0.85`，偏实，降下来更透气）。这些值都需显式写在 `style` 里，不是省略即生效；不需要渐变、阴影或自定义动画。
4. **文本只用已知语义**：字段/单位/来源明确时，添加语义化轴标题、tooltip 名称和 formatter；报告语境或用户提供标题时添加顶层 `title`。信息未知时省略，不编造单位、来源或副标题。
5. **标签按密度选择**：少量且需精确读取的数据可加标签；密集散点、多系列折线、类别很多时默认依赖 tooltip。inside 标签用 `contrastReverse`，发生碰撞时使用 `overlapHide` / `overlapDodgeY` / `overflowHide`；`dx` / `dy` 只用于避让后的细微调整。
6. **特殊图**：饼/环图的少量类别优先外置标签，类别较多时改用 legend；不要默认同时重复两者。气泡图保持 G2 默认 sqrt size 映射，按数据范围设置 `size.range`，仅在 size legend 无助理解时隐藏它。

渐变、阴影、滑块、滚动条、自定义动画和 3D 气泡都属于用户明确要求“报告级 / 精致”时的增强项；添加前必须确认不会掩盖数据或降低标签对比度。

## 快速参考

| 用户意图 | 检索查询 |
|---|---|
| 图表初始化、容器、autoFit | `GET /api/v1/context/retrieve?query=chart+init&library=g2` |
| 条形图 / 柱状图 | `GET /api/v1/context/retrieve?query=bar+chart+interval&library=g2` |
| 折线图 / 面积图 | `GET /api/v1/context/retrieve?query=line+area+chart&library=g2` |
| 饼图 / 环图 / 玫瑰图 | `GET /api/v1/context/retrieve?query=pie+chart+theta&library=g2` |
| 散点图 / 气泡图 | `GET /api/v1/context/retrieve?query=scatter+point+bubble&library=g2` |
| 树图 / 太阳图 / 打包图 | `GET /api/v1/context/retrieve?query=treemap+sunburst+pack&library=g2` |
| 热力图 / 密度图 / 箱线图 | `GET /api/v1/context/retrieve?query=heatmap+density+boxplot&library=g2` |
| 漏斗图 / 指标图 / 词云图 | `GET /api/v1/context/retrieve?query=funnel+gauge+wordcloud&library=g2` |
| 编码通道（x, y, color, size） | `GET /api/v1/context/retrieve?query=encode+channel&library=g2` |
| 缩放 / 调色板 / 颜色范围 | `GET /api/v1/context/retrieve?query=scale+palette+color&library=g2` |
| 坐标系（极坐标、theta、转置） | `GET /api/v1/context/retrieve?query=coordinate+polar+theta+transpose&library=g2` |
| 转换（堆叠、归一化、排序） | `GET /api/v1/context/retrieve?query=transform+stack+normalize&library=g2` |
| 轴 / 图例 / tooltip / 标签 | `GET /api/v1/context/retrieve?query=axis+legend+tooltip+label&library=g2` |
| 交互（刷选、高亮、下钻） | `GET /api/v1/context/retrieve?query=interaction+brush+highlight&library=g2` |
| 主题 / 深色模式 | `GET /api/v1/context/retrieve?query=theme+dark+classicDark&library=g2` |
| 默认美学 / 视觉基线 | `GET /api/v1/context/retrieve?query=default+aesthetics+design&library=g2` |
| 动画 | `GET /api/v1/context/retrieve?query=animation+animate&library=g2` |
| 数据获取 / 过滤 / 排序 | `GET /api/v1/context/retrieve?query=data+fetch+filter+sort&library=g2` |
| 分面 / 视图组合 | `GET /api/v1/context/retrieve?query=facet+view+composition&library=g2` |
| 图表类型选择指南 | `GET /api/v1/context/retrieve?query=chart+type+selection&library=g2` |
| 渲染故障排除 | `GET /api/v1/context/retrieve?query=rendering+troubleshoot+debug&library=g2` |

## 依赖项

- `@antv/g2` — G2 v5 图表引擎
