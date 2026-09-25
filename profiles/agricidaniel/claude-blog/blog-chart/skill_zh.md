# 博客图表：内置SVG数据可视化

为博客文章生成兼容暗模式的内联SVG图表。由`blog-write`和`blog-rewrite`在识别到值得绘制的数据时内部调用。不是独立面向用户命令。

**样式来源真相：** `skills/blog/references/visual-media.md`

对于支持的图表类型，优先使用确定的CLI命令：

```bash
python3 skills/blog-chart/scripts/generate_chart_svg.py --input chart.json --output chart.html --json
```

## 输入格式

作者或研究人员传递一个图表请求：

```
图表请求：
- 类型：水平条形图
- 标题："按产品划分的季度注册量"
- 数据：产品A 420，产品B 315，产品C 180
- 来源：[已验证来源]，[发布日期]
- 平台：mdx（或html）
```

## 图表类型选择

根据数据模式选择。优先考虑图表类型的多样性，但在可比性或读者理解明显受益时重复类型。

| 数据模式 | 最佳图表类型 |
|-------------|-----------------|
| 前后比较 | 分组条形图 |
| 排名因素 / 相关性 | 蜡烛图 |
| 整体部分 / 市场份额 | 环形图 |
| 随时间变化趋势 | 折线图 |
| 百分比改善 | 水平条形图 |
| 分布 / 范围 | 面积图 |
| 多维评分 | 雷达图 |

## 样式规则（不可协商）

所有图表必须在深色和浅色背景下都能正常工作：

```
文本元素：     fill="currentColor"
网格线：        stroke="currentColor" opacity="0.08"
坐标轴线：        stroke="currentColor" opacity="0.3"
背景：        透明（根SVG上无填充）
副标题文本：     fill="var(--chart-muted, currentColor)"
来源文本：        fill="var(--chart-muted, currentColor)"
标签文本：        fill="currentColor" opacity="0.8"
```

将`--chart-muted`设置为宿主主题中的一个可访问文本标记。如果不存在标记，则在浅色背景上使用`#4b5563`，在深色背景上使用`#d1d5db`。不要依赖低不透明度的来源或副标题文本进行可见的归因。

### 色彩搭配

| 色彩 | 十六进制 | 用途 |
|-------|-----|----------|
| 橙色 | `#f97316` | 主要 / 最高值 |
| 天空蓝 | `#38bdf8` | 次要 / 比较 |
| 紫色 | `#a78bfa` | 三级 / 特殊类别 |
| 绿色 | `#22c55e` | 四级 / 正面指示 |

对于批准的彩色元素内的文本：使用`fill="#111827"`和`fontWeight="800"`。仅在检查对比度至少为该特定填充色4.5:1时才使用白色文本。

不要依赖颜色。添加直接标签、图案、虚线、标记形状或图例文本，以便色盲读者可以区分系列。

## 标准SVG外壳（HTML）

```xml
<svg
  viewBox="0 0 560 380"
  style="max-width: 100%; height: auto; font-family: 'Inter', system-ui, sans-serif"
  role="img"
  aria-labelledby="chart-title chart-desc"
>
  <title id="chart-title">图表标题</title>
  <desc id="chart-desc">为屏幕阅读器提供所有关键数据点和来源的描述</desc>

  <!-- 图表内容 -->

  <text x="280" y="372" text-anchor="middle" font-size="10" fill="var(--chart-muted, currentColor)">
    来源：来源名称 (年份)
  </text>
</svg>
```

## JSX/MDX外壳（camelCase属性）

```jsx
<svg
  viewBox="0 0 560 380"
  style={{maxWidth: '100%', height: 'auto', fontFamily: "'Inter', system-ui, sans-serif"}}
  role="img"
  aria-labelledby="chart-title chart-desc"
>
  <title id="chart-title">图表标题</title>
  <desc id="chart-desc">为屏幕阅读器提供描述</desc>

  {/* 图表内容 */}

  <text x="280" y="372" textAnchor="middle" fontSize="10" fill="var(--chart-muted, currentColor)">
    来源：来源名称 (年份)
  </text>
</svg>
```

## JSX属性转换（MDX必需）

| HTML | JSX |
|------|-----|
| `stroke-width` | `strokeWidth` |
| `stroke-dasharray` | `strokeDasharray` |
| `stroke-linecap` | `strokeLinecap` |
| `text-anchor` | `textAnchor` |
| `font-size` | `fontSize` |
| `font-weight` | `fontWeight` |
| `font-family` | `fontFamily` |
| `class` | `className` |
| `style="..."` | `style={{...}}` |

## 图表类型构建

### 水平条形图

最佳用途：百分比改善、单指标比较。

1. 定义图表区域：x=80，y=40，width=440，height=280
2. 计算条形高度：`chartHeight / dataCount - gap`（gap=8）
3. 计算条形宽度：`(value / maxValue) * chartWidth`
4. 定位条形：`y = chartY + index * (barHeight + gap)`
5. 标签在左侧（右对齐于x=75）：类别名称
6. 值标签在条形末端：百分比或数字
7. 来源文本在底部居中

### 分组条形图

最佳用途：前后比较、A与B比较。

1. 沿Y轴定义组，每组内的条形
2. 使用2种颜色（主要+次要）表示两个系列
3. 在顶部添加图例：彩色方块+每个系列的标签
4. 组间间隙 > 组内间隙

### 环形图

最佳用途：整体部分、市场份额。

1. 中心：cx=280，cy=180，外半径=140，内半径=80
2. 使用累积角度计算弧段
3. 每个段：`<path d="M... A... L... A... Z" fill="color" />`
4. 中心文本：总计或关键标签
5. 图例在图表下方，带有彩色方块+标签+值

### 折线图

最佳用途：随时间变化趋势。

1. X轴：时间段，均匀分布
2. Y轴：值范围，带有4-5条网格线
3. 绘制网格线：`stroke="currentColor" opacity="0.08"`
4. 绘制数据点：`<circle cx=... cy=... r="4" fill="color" />`
5. 连接：`<polyline points="..." fill="none" stroke="color" strokeWidth="2" />`
6. 可选：线下区域填充，`opacity="0.1"`

### 蜡烛图

最佳用途：排名因素、相关性。

1. 水平方向（类似于条形图，但带有圆形）
2. 从坐标轴到数据点的细线：`stroke="currentColor" opacity="0.15" strokeWidth="1"`
3. 数据点处的圆形：`r="6"`，填充颜色
4. 值标签在圆形旁边
5. Y轴上的类别（左对齐）

### 面积图

最佳用途：分布、累积数据。

1. 与折线图相同，但下方有填充区域
2. 区域填充：`<path d="M... L... L... Z" fill="color" opacity="0.15" />`
3. 顶部的线：`stroke="color" strokeWidth="2" fill="none"`
4. 区域后的网格线

### 雷达图

最佳用途：多维评分（5-7轴）。

1. 中心：cx=280，cy=190
2. 绘制同心多边形作为网格（3-4级）
3. 计算轴端点，角度相等
4. 在每个轴上按值比例绘制数据点
5. 用填充多边形连接数据点：`fill="color" opacity="0.2" stroke="color"`
6. 在外边缘标签每个轴

## 标签规则

- 在单词边界处将长标签包装到`<tspan>`行中。
- 只有在包装会与数据标记冲突时才截断，并将完整标签保留在`<desc>`或相邻的文本中。
- 使用稳定的图表尺寸，带有响应式`max-width: 100%; height: auto`样式，或选择一个更宽的justified viewBox以适应密集标签。
- 检查手机宽度，以确保坐标轴标签、图例和值标签不会重叠。

## 输出格式

将每个图表包装在`<figure>`元素中：

**HTML:**
```html
<figure>
  <svg viewBox="0 0 560 380" style="max-width: 100%; height: auto; font-family: 'Inter', system-ui, sans-serif" role="img" aria-labelledby="chart-title chart-desc">
    <title id="chart-title">[图表标题]</title>
    <desc id="chart-desc">[包含所有数据点的完整描述，用于屏幕阅读器]</desc>
    <!-- 图表内容 -->
    <text x="280" y="372" text-anchor="middle" font-size="10" fill="var(--chart-muted, currentColor)">
      来源：[来源名称] ([年份])
    </text>
  </svg>
  <figcaption>来源：<a href="[来源URL]">[来源名称]</a>，[发布日期]。</figcaption>
</figure>
```

**MDX:**
```mdx
<figure className="chart-container" style={{margin: '2.5rem 0', textAlign: 'center', padding: '1.5rem', borderRadius: '12px'}}>
  <svg viewBox="0 0 560 380" style={{maxWidth: '100%', height: 'auto', fontFamily: "'Inter', system-ui, sans-serif"}} role="img" aria-labelledby="chart-title chart-desc">
    <title id="chart-title">[图表标题]</title>
    <desc id="chart-desc">[完整描述]</desc>
    {/* 带有camelCase属性的图表内容 */}
    <text x="280" y="372" textAnchor="middle" fontSize="10" fill="var(--chart-muted, currentColor)">
      来源：[来源名称] ([年份])
    </text>
  </svg>
  <figcaption>来源：<a href="[来源URL]">[来源名称]</a>，[发布日期]。</figcaption>
</figure>
```

## 质量检查清单（返回前验证）

- [ ] 除了彩色元素内的对比度检查标签外，没有硬编码的文本颜色
- [ ] 没有白色/浅色背景（透明或无）
- [ ] 底部有来源归因文本，并且存在语义`<figcaption>`
- [ ] `<svg>`上存在`role="img"`和`aria-labelledby`
- [ ] `<svg>`内存在`<title id>`和`<desc id>`
- [ ] 图表类型选择支持理解和可比性
- [ ] 如果是MDX：所有属性都是camelCased（属性名中无连字符）
- [ ] 数据值与源数据完全匹配
- [ ] 色彩搭配仅使用批准的颜色
- [ ] ViewBox是`0 0 560 380`（标准）或合理的替代方案
- [ ] 标签、形状、图案或线样式提供了超越颜色的冗余
