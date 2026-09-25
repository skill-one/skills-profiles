# 生成式 UI 技能

此技能包含 Claude 内置 `show_widget` 工具的完整设计系统——即 Claude.ai 对话中内联渲染交互式 HTML/SVG 小部件的生成式 UI 功能。以下指南是 Anthropic "Imagine — 视觉创作套件" 的实际设计规则，已提取出来，以便您可以直接生成高质量的小部件，而无需 `read_me` 设置调用。

**工作原理**：在 claude.ai 上，Claude 可以访问 `show_widget` 工具，该工具在对话中内联渲染原始 HTML/SVG 片段。此技能提供设计系统、模板和模式，以便您能够很好地使用它。

---

## 第 1 步：选择正确的视觉类型

根据 **动词** 而不是 **名词** 进行路由。同一主题，根据提问内容不同，视觉呈现方式也不同：

| 用户说 | 类型 | 格式 |
|---|---|---|
| "X 是如何工作的" | 插图式图表 | SVG |
| "X 架构" | 结构式图表 | SVG |
| "步骤是什么" | 流程图 | SVG |
| "解释复利" | 交互式解释器 | HTML |
| "比较这些选项" | 比较网格 | HTML |
| "显示收入图表" | Chart.js 图表 | HTML |
| "创建联系卡" | 数据记录 | HTML |
| "画一个日落" | 艺术/插图 | SVG |

---

## 第 2 步：构建小部件

### 结构（严格顺序）

```
<style>  →  HTML 内容  →  <script>
```

输出以逐个 token 的方式流式传输。样式必须存在于它们所指向的元素之前，而脚本必须在 DOM 准备就绪后运行。

### 哲学

- **无缝**：用户不应注意到主机 UI 哪里结束，而您的小部件开始
- **扁平**：没有渐变、网格背景、噪点纹理或装饰效果。干净的扁平表面
- **紧凑**：显示必要的内联内容。其余的解释以文本形式呈现
- **文本放在您的响应中，视觉放在工具中**——所有解释性文本、描述和摘要都必须作为正常响应文本放在工具调用外部。工具输出应仅包含视觉元素

### 核心规则

- 无 `<!-- 注释 -->` 或 `/* 注释 */`（浪费 token，破坏流式传输）
- 无小于 11px 的字体大小
- 无表情符号——使用 CSS 形状或 SVG 路径
- 无渐变、阴影、模糊、发光或霓虹效果
- 外部容器无深色/彩色背景（仅透明——主机提供背景）
- **排版**：仅两种字重：400 常规、500 中等。从不使用 600 或 700。标题：h1=22px，h2=18px，h3=16px——所有字重均为 500。正文=16px，字重 400，行高 1.7
- **句子大小写**始终。从不使用 Title Case，从不使用 ALL CAPS
- 无句子中的居中加粗——实体名称放在 `code style` 中，而不是 **加粗**
- 无 `<!DOCTYPE>`、`<html>`、`<head>` 或 `<body>`——仅内容片段
- 无 `position: fixed`——使用常规流布局
- 无制表符、轮播或 `display: none` 部分在流式传输期间
- 无嵌套滚动——自动适应高度
- 角落：`border-radius: var(--border-radius-lg)` 用于卡片，`var(--border-radius-md)` 用于元素
- 无单边边框的圆角（border-left、border-top）
- **四舍五入所有显示的数字**——使用 `Math.round()`、`.toFixed(n)` 或 `Intl.NumberFormat`

### CDN 允许列表（CSP 强制执行）

外部资源只能从以下位置加载：
- `cdnjs.cloudflare.com`
- `cdn.jsdelivr.net`
- `unpkg.com`
- `esm.sh`

所有其他来源都被阻止——请求将静默失败。

### CSS 变量

**背景**：`--color-background-primary`（白色）、`-secondary`（表面）、`-tertiary`（页面背景）、`-info`、`-danger`、`-success`、`-warning`
**文本**：`--color-text-primary`（黑色）、`-secondary`（柔和）、`-tertiary`（提示）、`-info`、`-danger`、`-success`、`-warning`
**边框**：`--color-border-tertiary`（0.15α，默认）、`-secondary`（0.3α，悬停）、`-primary`（0.4α）、语义 `-info/-danger/-success/-warning`
**排版**：`--font-sans`、`--font-serif`、`--font-mono`
**布局**：`--border-radius-md`（8px）、`--border-radius-lg`（12px）、`--border-radius-xl`（16px）

所有自动适应亮/暗模式。

**必须使用暗模式**——每种颜色都必须在这两种模式下工作：
- 在 HTML 中：始终使用 CSS 变量作为文本。从不硬编码颜色，如 `color: #333`
- 在 SVG 中：使用预构建的颜色类（`c-blue`、`c-teal` 等）——它们会自动处理亮/暗模式
- 心理测试：如果背景接近黑色，每个文本元素是否仍然可读？

### `sendPrompt(text)`

一个全局函数，将消息发送到聊天，就像用户输入的一样。当用户下一步需要 Claude 思考时使用它。在 JS 中处理过滤、排序、切换和计算。

---

## 第 3 步：使用 `show_widget` 渲染

`show_widget` 工具已内置在 claude.ai 中——无需激活。直接传递您的小部件代码：

```json
{
  "title": "snake_case_widget_name",
  "widget_code": "<style>...</style>\n<div>...</div>\n<script>...</script>"
}
```

| 参数 | 类型 | 是否必需 | 描述 |
|---|---|---|---|
| `title` | string | 是 | 小部件的蛇形标识符 |
| `widget_code` | string | 是 | HTML 或 SVG 代码。对于 SVG：以 `<svg>` 开头。对于 HTML：内容片段 |

对于 SVG 输出：以 `<svg` 开头 `widget_code`——它将被自动检测并适当包装。

---

## 第 4 步：Chart.js 模板

对于图表，使用 `onload` 回调模式处理脚本加载顺序：

```html
<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px;">
  <div style="background: var(--color-background-secondary); border-radius: var(--border-radius-md); padding: 1rem;">
    <div style="font-size: 13px; color: var(--color-text-secondary);">标签</div>
    <div style="font-size: 24px; font-weight: 500;" id="stat1">—</div>
  </div>
</div>

<div style="position: relative; width: 100%; height: 300px; margin-top: 1rem;">
  <canvas id="myChart"></canvas>
</div>

<div style="display: flex; align-items: center; gap: 12px; margin-top: 1rem;">
  <label style="font-size: 14px; color: var(--color-text-secondary);">参数</label>
  <input type="range" min="0" max="100" value="50" id="param" step="1" style="flex: 1;" />
  <span style="font-size: 14px; font-weight: 500; min-width: 32px;" id="param-out">50</span>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.js" onload="initChart()"></script>
<script>
function initChart() {
  const slider = document.getElementById('param');
  const out = document.getElementById('param-out');
  let chart = null;

  function update() {
    const val = parseFloat(slider.value);
    out.textContent = val;
    document.getElementById('stat1').textContent = val.toFixed(1);

    const labels = [], data = [];
    for (let x = 0; x <= 100; x++) {
      labels.push(x);
      data.push(x * val / 100);
    }

    if (chart) chart.destroy();
    chart = new Chart(document.getElementById('myChart'), {
      type: 'line',
      data: { labels, datasets: [{ data, borderColor: '#7F77DD', borderWidth: 2, pointRadius: 0, fill: false }] },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { x: { grid: { display: false } } }
      }
    });
  }

  slider.addEventListener('input', update);
  update();
}
if (window.Chart) initChart();
</script>
```

**Chart.js 规则**：
- Canvas 无法解析 CSS 变量——使用硬编码的十六进制值
- 仅在包装 div 上设置高度，绝不设置 canvas 本身
- 始终 `responsive: true, maintainAspectRatio: false`
- 始终禁用默认图例，构建自定义 HTML 图例
- 数字格式化：`-$5M` 而不是 `$-5M`（负号在货币符号之前）
- 使用 `onload="initChart()"` 在 CDN 脚本标签上 + `if (window.Chart) initChart();` 作为后备

---

## 第 5 步：SVG 图表模板

对于流程图和图表，使用带有预构建类的 SVG：

```svg
<svg width="100%" viewBox="0 0 680 H">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
    </marker>
  </defs>

  <!-- 单行节点（44px 高） -->
  <g class="node c-blue" onclick="sendPrompt('Tell me more about this')">
    <rect x="250" y="40" width="180" height="44" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="62" text-anchor="middle" dominant-baseline="central">第一步</text>
  </g>

  <!-- 连接箭头 -->
  <line x1="340" y1="84" x2="340" y2="120" class="arr" marker-end="url(#arrow)"/>

  <!-- 两行节点（56px 高） -->
  <g class="node c-teal" onclick="sendPrompt('Explain this step')">
    <rect x="230" y="120" width="220" height="56" rx="8" stroke-width="0.5"/>
    <text class="th" x="340" y="140" text-anchor="middle" dominant-baseline="central">第二步</text>
    <text class="ts" x="340" y="158" text-anchor="middle" dominant-baseline="central">处理输入</text>
  </g>
</svg>
```

**SVG 规则**：
- ViewBox 始终 680px 宽 (`viewBox="0 0 680 H"`)。设置 H 以适应内容 + 40px 的填充
- 安全区域：x=40 到 x=640，y=40 到 y=(H-40)
- 预构建类：`t`（14px）、`ts`（12px 次要）、`th`（14px 中等 500）、`box`、`node`、`arr`、`c-{颜色}`
- 每个 `<text>` 元素必须包含类（`t`、`ts` 或 `th`）
- 使用 `dominant-baseline="central"` 进行垂直文本居中
- 连接器路径需要 `fill="none"`（SVG 默认 `fill: black`）
- 线宽：0.5px 用于边框和边缘
- 使所有节点可点击：`onclick="sendPrompt('...')"`

---

## 第 6 步：交互式解释器模板

对于交互式解释器（滑块、实时计算、内联 SVG）：

```html
<div style="display: flex; align-items: center; gap: 12px; margin: 0 0 1.5rem;">
  <label style="font-size: 14px; color: var(--color-text-secondary);">年数</label>
  <input type="range" min="1" max="40" value="20" id="years" style="flex: 1;" />
  <span style="font-size: 14px; font-weight: 500; min-width: 24px;" id="years-out">20</span>
</div>

<div style="display: flex; align-items: baseline; gap: 8px; margin: 0 0 1.5rem;">
  <span style="font-size: 14px; color: var(--color-text-secondary);">$1,000 →</span>
  <span style="font-size: 24px; font-weight: 500;" id="result">$3,870</span>
</div>

<div style="margin: 2rem 0; position: relative; height: 240px;">
  <canvas id="chart"></canvas>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.5.1/chart.umd.js" onload="initChart()"></script>
<script>
function initChart() {
  // 滑块逻辑、图表渲染、使用 sendPrompt() 进行后续操作
}
if (window.Chart) initChart();
</script>
```

使用 `sendPrompt()` 让用户进行后续提问：`sendPrompt('What if I increase the rate to 10%?')`

---

## 第 7 步：回复用户

渲染小部件后，简要解释：
1. 小部件显示的内容
2. 如何与之交互（哪些控件的作用）
3. 数据的一个关键见解

保持简洁——小部件会为自己代言。

---

## 参考文件

- `references/design_system.md` — 完整的调色板（9 个渐变 × 7 个节点）、CSS 变量、UI 组件模式、度量卡片、布局规则
- `references/svg_and_diagrams.md` — SVG ViewBox 设置、字体校准、预构建类、流程图/结构图/插图图表模式及示例
- `references/chart_js.md` — Chart.js 配置、脚本加载顺序、canvas 尺寸、图例模式、仪表板布局

需要特定设计 token、SVG 坐标数学或 Chart.js 配置详情时，请阅读相关的参考文件。
