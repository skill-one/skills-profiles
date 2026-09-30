---
name: web-design-guidelines
description: Web 平台设计与无障碍准则。在构建 Web 界面、进行无障碍审计、实现响应式布局或审查 Web UI 代码时使用。当任务涉及 HTML、CSS、Web 组件、WCAG 合规性、响应式设计或 Web 性能时触发。
---

# Web 平台设计指南

跨框架规则，用于创建可访问、高性能、响应式的 Web 界面。基于 WCAG 2.2、MDN Web 文档和现代 Web 平台 API。

---

## 1. 可访问性 / WCAG [关键]

可访问性不是可选项。本节中的大多数规则映射到 WCAG 2.2 成功标准中的 A 级或 AA 级。少量最佳实践规则（内联注释说明）针对 AAA 级或超出 WCAG。

### 1.1 使用语义 HTML 元素

根据其预期用途使用元素。语义结构提供免费的可访问性、SEO 和阅读模式支持。

| 元素 | 用途 |
|------|------|
| `<main>` | 主要页面内容（每个页面一个） |
| `<nav>` | 导航块 |
| `<header>` | 导入内容或导航辅助 |
| `<footer>` | 最近分区内容的页脚 |
| `<article>` | 自包含、可独立分发的内容 |
| `<section>` | 带标题的主题分组 |
| `<aside>` | 旁支相关内容（侧边栏、提示框） |
| `<figure>` / `<figcaption>` | 插图、图表、代码列表 |
| `<details>` / `<summary>` | 可展开/可折叠的披露小部件 |
| `<dialog>` | 模态或非模态对话框 |
| `<time>` | 机器可读的日期/时间 |
| `<mark>` | 高亮/引用文本 |
| `<address>` | 最近文章/主体的联系信息 |

```html
<!-- 良好 -->
<main>
  <article>
    <h1>文章标题</h1>
    <p>内容...</p>
  </article>
  <aside>相关链接</aside>
</main>

<!-- 不好：div 汤碗 -->
<div class="main">
  <div class="article">
    <div class="title">文章标题</div>
    <div class="content">内容...</div>
  </div>
</div>
```

**反模式**：使用 `<div>` 或 `<span>` 作为交互元素。当存在 `<button>` 时，永远不要写 `<div onclick>`。

### 1.2 交互元素的 ARIA 标签

每个交互元素必须有可访问的名称。优先使用可见文本；仅在可见文本不足时使用 `aria-label` 或 `aria-labelledby`（SC 4.1.2）。

```html
<!-- 仅图标按钮：需要 aria-label -->
<button aria-label="关闭对话框">
  <svg aria-hidden="true">...</svg>
</button>

<!-- 通过 labelledby 链接 -->
<h2 id="section-title">通知</h2>
<ul aria-labelledby="section-title">...</ul>

<!-- 重复：可见文本足够 -->
<button>保存更改</button> <!-- 无需 aria-label -->
```

### 1.3 键盘导航

所有交互元素必须可通过键盘访问和操作（SC 2.1.1）。

- 使用原生交互元素（`<button>`、`<a href>`、`<input>`、`<select>`），它们默认可通过键盘访问。
- 自定义小部件需要 `tabindex="0"` 进入 Tab 顺序并使用 keydown 处理器激活。
- 永远不要使用大于 0 的 `tabindex` 值。
- 在模态中捕获焦点；关闭时返回焦点。

```js
// 模态的焦点捕获
dialog.addEventListener('keydown', (e) => {
  if (e.key === 'Tab') {
    const focusable = dialog.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
});
```

### 1.4 可见焦点指示器

除非提供可见替代方案，否则永远不要移除焦点轮廓（SC 2.4.7，增强 SC 2.4.11 (AA) 和 SC 2.4.12 (AAA) 在 WCAG 2.2 中）。

```css
/* 良好：自定义焦点指示器 */
:focus-visible {
  outline: 3px solid var(--focus-color, #4A90D9);
  outline-offset: 2px;
}

/* 仅当 :focus-visible 受支持时移除默认值 */
:focus:not(:focus-visible) {
  outline: none;
}

/* 不好：移除所有焦点样式 */
/* *:focus { outline: none; } */
```

WCAG 2.2 要求焦点指示器具有组件周长两倍的最小面积，与相邻颜色对比度为 3:1。

### 1.5 跳过导航链接

提供跳过重复内容块的机制（SC 2.4.1）。

```html
<body>
  <a href="#main-content" class="skip-link">跳转到主要内容</a>
  <nav>...</nav>
  <main id="main-content">...</main>
</body>
```

```css
.skip-link {
  position: absolute;
  top: -100%;
  left: 0;
  z-index: 1000;
  padding: 0.75rem 1.5rem;
  background: var(--color-primary);
  color: var(--color-on-primary);
}
.skip-link:focus {
  top: 0;
}
```

### 1.6 图像的替代文本

每个 `<img>` 必须有 `alt` 属性（SC 1.1.1）。

- **信息性图像**：描述内容和功能。`alt="条形图显示 Q4 销售额翻倍"`.
- **装饰性图像**：使用 `alt=""`（空字符串），使屏幕阅读器跳过它们。
- **功能性图像**（在链接/按钮内）：描述操作。`alt="搜索"`.
- **复杂图像**：使用 `alt` 进行简短描述，链接到长描述或使用 `<figcaption>`。

```html
<img src="chart.png" alt="收入图表：Q1 $2M，Q2 $2.4M，Q3 $3.1M，Q4 $4.5M">
<img src="decorative-wave.svg" alt="">
```

### 1.7 色彩对比度

保持最小对比度比率（SC 1.4.3，1.4.6，1.4.11）。

| 内容 | 最小比率 |
|------|---------|
| 普通文本（<24px / <18.66px 粗体） | 4.5:1 |
| 大文本（>=24px / >=18.66px 粗体） | 3:1 |
| UI 组件和图形对象 | 3:1 |

不要仅依赖颜色来传达信息（SC 1.4.1）。将颜色与图标、文本或图案搭配使用。

```css
/* 检查这些 token 的对比度 */
:root {
  --text-primary: #1a1a2e;    /* 背景为白色：~16:1 */
  --text-secondary: #555770;  /* 背景为白色：~6.5:1 */
  --text-disabled: #767693;   /* 背景为白色：~4.5:1，边缘值 */
}
```

### 1.8 表单标签

每个表单输入必须有程序上关联的标签（SC 1.3.1，3.3.2）。

```html
<!-- 显式标签（首选） -->
<label for="email">电子邮件地址</label>
<input id="email" type="email" autocomplete="email">

<!-- 隐式标签（可接受） -->
<label>
  电子邮件地址
  <input type="email" autocomplete="email">
</label>

<!-- 永远不要：仅使用占位符作为标签 -->
<!-- <input placeholder="电子邮件"> -->
```

### 1.9 错误识别

在文本中识别和描述错误（SC 3.3.1）。使用 `aria-describedby` 或 `aria-errormessage` 将错误消息链接到输入。

```html
<label for="email">电子邮件</label>
<input id="email" type="email" aria-describedby="email-error" aria-invalid="true">
<p id="email-error" role="alert">输入有效的电子邮件地址，例如 name@example.com</p>
```

### 1.10 ARIA Live Regions

向屏幕阅读器宣布动态内容变化（SC 4.1.3）。

```html
<!-- 闲时宣布：用户空闲时宣布 -->
<div aria-live="polite" aria-atomic="true">
  找到 3 个结果
</div>

<!-- 强制：打断当前语音 -->
<div role="alert">
  您的会话将在 2 分钟后过期。
</div>

<!-- 状态消息 -->
<div role="status">
  文件上传成功。
</div>
```

默认使用 `aria-live="polite"`。保留 `role="alert"` / `aria-live="assertive"` 用于时间敏感的警告。

### 1.11 ARIA 角色快速参考

| 角色 | 用途 | 原生等效元素 |
|------|------|-------------|
| `button` | 可点击操作 | `<button>` |
| `link` | 导航 | `<a href>` |
| `tab` / `tablist` / `tabpanel` | Tab 界面 | 无 |
| `dialog` | 模态 | `<dialog>` |
| `alert` | 强制性实时区域 | 无 |
| `status` | 闲时实时区域 | `<output>` |
| `navigation` | 导航地标 | `<nav>` |
| `main` | 主要地标 | `<main>` |
| `complementary` | 旁支地标 | `<aside>` |
| `search` | 搜索地标 | `<search>`（HTML5） |
| `img` | 图像 | `<img>` |
| `list` / `listitem` | 列表 | `<ul>/<li>` |
| `heading` | 标题（带 `aria-level`） | `<h1>`-`<h6>` |
| `menu` / `menuitem` | 菜单小部件 | 无 |
| `tree` / `treeitem` | 树视图 | 无 |
| `grid` / `row` / `gridcell` | 数据网格 | `<table>` |
| `progressbar` | 进度 | `<progress>` |
| `slider` | 范围输入 | `<input type="range">` |
| `switch` | 开关 | `<input type="checkbox">` |

**规则**：优先使用原生 HTML，仅在模式不存在时使用 ARIA。

### 1.12 名称中的标签（WCAG 2.5.3 级 A）

当交互元素有可见文本时，其可访问名称必须包含该可见文本作为子字符串（SC 2.5.3）。语音控制用户（Dragon NaturallySpeaking、macOS 语音控制）通过可见标签激活控件。如果 `aria-label` 替代或与可见文本矛盾，语音命令将失败。

```html
<!-- 正确：aria-label 包含可见文本作为子字符串 -->
<button aria-label="从购物车删除项目">删除</button>

<!-- 正确：无需 aria-label — 可见文本是可访问名称 -->
<button>保存更改</button>

<!-- 正确：图标按钮 — 无可见文本，aria-label 很好 -->
<button aria-label="关闭对话框">
  <svg aria-hidden="true">...</svg>
</button>
```

```html
<!-- 错误：aria-label 使用与可见文本不同的文本替代 -->
<button aria-label="移除">删除</button>

<!-- 错误：aria-label 不包含可见的 "提交" -->
<button aria-label="进入下一步">提交</button>
```

**规则**：当可见文本存在时，`aria-label` 必须包含该可见文本（逐字，不区分大小写）。在可见文本足够时，优先不使用 `aria-label`。

---

## 2. 响应式设计 [关键]

### 2.1 移动优先方法

为最小视口编写基本样式。使用 `min-width` 媒体查询分层复杂性。

```css
/* 基础：移动端 */
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* 平板 */
@media (min-width: 48rem) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 桌面 */
@media (min-width: 64rem) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 2.2 使用现代 CSS 函数的流体布局

使用 `clamp()`、`min()` 和 `max()` 进行无断点的流体尺寸。

```css
/* 流体排版 */
h1 {
  font-size: clamp(1.75rem, 1.2rem + 2vw, 3rem);
}

/* 流体间距 */
.section {
  padding: clamp(1.5rem, 4vw, 4rem);
}

/* 流体容器 */
.container {
  width: min(90%, 72rem);
  margin-inline: auto;
}
```

### 2.3 容器查询

根据其容器而不是视口调整组件尺寸。

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container card (min-width: 700px) {
  .card {
    grid-template-columns: 300px 1fr;
    gap: 2rem;
  }
}
```

### 2.4 基于内容的断点

在内容断开处设置断点，而不是设备宽度。常见起点：

```css
/* 基于内容，不是 "iPhone" 或 "iPad" */
@media (min-width: 30rem)  { /* ~480px：单列变得拥挤 */ }
@media (min-width: 48rem)  { /* ~768px：有空间放置两列 */ }
@media (min-width: 64rem)  { /* ~1024px：有空间放置侧边栏+内容 */ }
@media (min-width: 80rem)  { /* ~1280px：宽多列 */ }
```

### 2.5 触摸目标

触摸目标最小 44x44 CSS 像素（WCAG SC 2.5.5 AAA；SC 2.5.8 仅要求 AA 级时 24x24px）。相邻目标之间至少提供 24px 间距。

```css
button, a, input, select, textarea {
  min-height: 44px;
  min-width: 44px;
}

/* 扩大点击区域而不改变视觉大小 */
.icon-button {
  position: relative;
  width: 24px;
  height: 24px;
}
.icon-button::after {
  content: "";
  position: absolute;
  inset: -10px; /* 扩展可点击区域 */
}
```

### 2.6 视口元标签

始终在文档 `<head>` 中包含：

```html
<meta name="viewport" content="width=device-width, initial-scale=1">
```

永远不要使用 `maximum-scale=1` 或 `user-scalable=no` —— 这些会破坏捏合缩放的可访问性（SC 1.4.4）。

### 2.7 无水平滚动

内容必须在 320px 宽度下重新流式而不水平滚动（SC 1.4.10）。

```css
/* 防止溢出 */
img, video, iframe, svg {
  max-width: 100%;
  height: auto;
}

/* 包含长单词/URL */
.prose {
  overflow-wrap: break-word;
}

/* 表格：滚动容器，不是页面 */
.table-wrapper {
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}
```

---

## 3. 表单 [高]

### 3.1 每个输入都有标签

每个输入都需要可见、程序上关联的标签。见第 1.8 节。

### 3.2 自动填充属性

使用 `autocomplete` 为常见字段启用浏览器自动填充（SC 1.3.5）。

```html
<input type="text" autocomplete="name" name="full-name">
<input type="email" autocomplete="email" name="email">
<input type="tel" autocomplete="tel" name="phone">
<input type="text" autocomplete="street-address" name="address">
<input type="text" autocomplete="postal-code" name="zip">
<input type="text" autocomplete="cc-name" name="card-name">
<input type="text" autocomplete="cc-number" name="card-number">
<input type="password" autocomplete="new-password" name="password">
<input type="password" autocomplete="current-password" name="current-pw">
```

### 3.3 正确的输入类型

使用正确的 `type` 触发适当的移动键盘和原生验证。

| 类型 | 用于 |
|------|------|
| `email` | 电子邮件地址 |
| `tel` | 电话号码 |
| `url` | URL |
| `number` | 带旋转器的数值（不用于电话、邮编、卡号） |
| `search` | 搜索字段（显示清除按钮） |
| `date` / `time` / `datetime-local` | 时间值 |
| `password` | 密码（触发密码管理器） |
| `text` with `inputmode="numeric"` | 无旋转器的数值数据（PIN、邮编） |

```html
<input type="tel" inputmode="numeric" pattern="[0-9]*" autocomplete="one-time-code">
```

### 3.4 内联验证

在 `blur`（而不是每个按键）时验证。显示成功和错误状态。

```html
<div class="field" data-state="error">
  <label for="username">用户名</label>
  <input id="username" type="text" aria-describedby="username-hint username-error" aria-invalid="true">
  <p id="username-hint" class="hint">3-20 个字符，仅限字母和数字</p>
  <p id="username-error" class="error" role="alert">用户名至少需要 3 个字符</p>
</div>
```

```css
.field[data-state="error"] input {
  border-color: var(--color-error);
  box-shadow: 0 0 0 1px var(--color-error);
}
.field[data-state="error"] .error { display: block; }
.field:not([data-state="error"]) .error { display: none; }
```

### 3.5 Fieldset 和 Legend 用于分组

使用 `<fieldset>` 组合相关输入，并使用 `<legend>` 标记组。

```html
<fieldset>
  <legend>收货地址</legend>
  <label for="street">街道</label>
  <input id="street" type="text" autocomplete="street-address">
  <!-- ... -->
</fieldset>

<fieldset>
  <legend>首选联系方式</legend>
  <label><input type="radio" name="contact" value="email"> 电子邮件</label>
  <label><input type="radio" name="contact" value="phone"> 电话</label>
</fieldset>
```

### 3.6 必填字段指示

视觉和程序上指示必填字段。使用 `required` 属性和可见标记。

```html
<label for="name">
  全名 <span aria-hidden="true">*</span>
  <span class="sr-only">(必填)</span>
</label>
<input id="name" type="text" required autocomplete="name">
```

如果大多数字段都是必填的，则指示哪些是可选的。

### 3.7 提交按钮状态

不要禁用提交按钮。相反，在提交时验证并显示错误。

```html
<!-- 良好：始终启用，提交时验证 -->
<button type="submit">创建账户</button>

<!-- 不好：禁用按钮且无解释 -->
<!-- <button type="submit" disabled>创建账户</button> -->
```

禁用按钮无法传达用户无法继续的原因。如果您必须禁用，请提供可见解释。

### 3.8 将说明保持在字段附近

通过提示和错误文本将格式示例、约束和恢复文本放置在相关字段旁边。永远不要仅在介绍性文本中解释要求，并期望用户记住它们。

---

## 4. 字体排印 [高]

### 4.1 字体堆栈

使用系统字体堆栈以提高性能，或使用具有适当回退功能的网络字体。

```css
/* 系统字体堆栈 */
body {
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

/* 等宽字体堆栈 */
code, pre, kbd {
  font-family: ui-monospace, "Cascadia Code", "Source Code Pro", Menlo, Consolas, monospace;
}

/* 带回退和尺寸调整的网络字体 */
@font-face {
  font-family: "CustomFont";
  src: url("/fonts/custom.woff2") format("woff2");
  font-display: swap;
  font-weight: 100 900;
}
body {
  font-family: "CustomFont", system-ui, sans-serif;
}
```

### 4.2 相对单位

使用 `rem` 设置字体大小和间距。使用 `em` 设置组件相对尺寸。

```css
html {
  font-size: 100%; /* = 16px 默认，尊重用户偏好 */
}

body {
  font-size: 1rem;       /* 16px */
}

h1 { font-size: 2.5rem; }  /* 40px */
h2 { font-size: 2rem; }    /* 32px */
h3 { font-size: 1.5rem; }  /* 24px */
small { font-size: 0.875rem; } /* 14px */

/* 永远不要：font-size: 16px; （忽略用户缩放设置） */
```

### 4.3 行高和间距

正文文本行高至少为 1.5（SC 1.4.12）。段落间距至少为字体大小的 2 倍。

```css
body {
  line-height: 1.6;
}

h1, h2, h3 {
  line-height: 1.2;
}

p + p {
  margin-top: 1em;
}
```

### 4.4 最大行长度

将行长度限制在约 75 个字符，以提高可读性。

```css
.prose {
  max-width: 75ch;
}

/* 或用于内容列 */
.content {
  max-width: 40rem; /* 大约 65-75ch，取决于字体 */
  margin-inline: auto;
}
```

### 4.5 排版细节

使用真实引号、正确连字符和表格数字来表示数据。

```css
/* 智能引号 */
q { quotes: "\201C" "\201D" "\2018" "\2019"; } /* 弯曲双引号然后单引号 */

/* 表格数字用于对齐数据 */
.data-table td {
  font-variant-numeric: tabular-nums;
}

/* 旧式数字用于运行文本（可选） */
.prose {
  font-variant-numeric: oldstyle-nums;
}

/* 正确的列表标记器 */
ul { list-style-type: disc; }
ol { list-style-type: decimal; }
```

### 4.6 标题层级

按顺序使用 `h1` 到 `h6`。永远不要跳过层级。每页一个 `h1`。

```html
<!-- 良好 -->
<h1>页面标题</h1>
  <h2>章节</h2>
    <h3>子章节</h3>
  <h2>另一个章节</h2>

<!-- 不好：跳过 h2 -->
<h1>页面标题</h1>
  <h3>子章节</h3> <!-- h2 在哪里？ -->
```

如果需要与层级不同的视觉样式，请使用 CSS 类：

```html
<h2 class="text-lg">视觉上更小但语义上是 h2</h2>
```

---

## 5. 性能 [HIGH]

### 5.1 懒加载折叠以下图像

对初始加载时不可见的图像使用原生懒加载。

```html
<!-- 折叠以上：立即加载，添加 fetchpriority -->
<img src="hero.webp" alt="英雄图像" fetchpriority="high" width="1200" height="600">

<!-- 折叠以下：懒加载 -->
<img src="feature.webp" alt="功能图像" loading="lazy" width="600" height="400">
```

### 5.2 显式图像尺寸

始终指定 `width` 和 `height` 以防止布局偏移（CLS）。

```html
<img src="photo.webp" alt="描述" width="800" height="600">
```

```css
/* 响应式图像，保留宽高比 */
img {
  max-width: 100%;
  height: auto;
}
```

### 5.3 资源提示

使用 `preconnect` 预连接第三方来源，使用 `preload` 预加载关键资源。

```html
<head>
  <!-- 预连接到关键的第三方来源 -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://cdn.example.com" crossorigin>

  <!-- 预加载关键资源 -->
  <link rel="preload" href="/fonts/main.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="/css/critical.css" as="style">

  <!-- DNS 预取非关键来源 -->
  <link rel="dns-prefetch" href="https://analytics.example.com">
</head>
```

### 5.4 代码拆分

仅在需要时加载 JavaScript。使用动态 `import()` 进行基于路由和基于组件的拆分。

```js
// 基于路由的拆分
const routes = {
  '/dashboard': () => import('./pages/dashboard.js'),
  '/settings':  () => import('./pages/settings.js'),
};

// 基于交互的拆分
button.addEventListener('click', async () => {
  const { openEditor } = await import('./editor.js');
  openEditor();
});
```

### 5.5 虚拟化长列表

对于超过几百项的列表，仅渲染可视行。

```js
// 概念：虚拟滚动
// 仅渲染视口内的项 + 缓冲区
const visibleStart = Math.floor(scrollTop / itemHeight);
const visibleEnd = visibleStart + Math.ceil(containerHeight / itemHeight);
const buffer = 5;
const renderStart = Math.max(0, visibleStart - buffer);
const renderEnd = Math.min(totalItems, visibleEnd + buffer);
```

### 5.6 避免 布局闪烁

批量读取和写入 DOM。永远不要交错它们。

```js
// 不好：读写读写（强制同步布局）
elements.forEach(el => {
  const height = el.offsetHeight;     // 读取
  el.style.height = height + 10 + 'px'; // 写入
});

// 好：批量读取，然后批量写入
const heights = elements.map(el => el.offsetHeight); // 所有读取
elements.forEach((el, i) => {
  el.style.height = heights[i] + 10 + 'px'; // 所有写入
});
```

### 5.7 适当地使用 `will-change`

仅将 `will-change` 应用于将要动画的元素，并在动画完成后移除它。

```css
/* 好：作用域和临时 */
.card:hover {
  will-change: transform;
}
.card.animating {
  will-change: transform, opacity;
}

/* 不好：全局 will-change */
/* * { will-change: transform; } */
```

### 5.8 及时暴露等待状态

在用户操作后，立即确认新状态。如果工作无法在短时间内完成，请显示进度、骨架屏、乐观 UI 或 `aria-busy` 反馈，而不是让界面保持不变。

---

## 6. 动画和运动 [MEDIUM]

### 6.1 尊重 prefers-reduced-motion

始终提供一个减少运动的替代方案（SC 2.3.3，级别 AAA）。

```css
/* 正常定义动画 */
.fade-in {
  animation: fadeIn 300ms ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* 移除或减少用户偏好减少运动 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

```js
// JavaScript 中检查
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
```

### 6.2 合成器友好的动画

仅动画 `transform` 和 `opacity` 以实现平滑的 60fps 动画。这些在 GPU 合成器线程上运行。

```css
/* 好：仅合成器属性 */
.slide-in {
  transition: transform 200ms ease-out, opacity 200ms ease-out;
}

/* 不好：触发布局/绘制 */
.slide-in-bad {
  transition: left 200ms, width 200ms, height 200ms;
}
```

### 6.3 无闪烁内容

内容闪烁频率永远不要超过每秒 3 次（SC 2.3.1）。这可能会引发癫痫。

### 6.4 状态变化的过渡

使用过渡为悬停、焦点、打开/关闭和其他状态变化提供连续性。

```css
.dropdown {
  opacity: 0;
  transform: translateY(-4px);
  transition: opacity 150ms ease-out, transform 150ms ease-out;
  pointer-events: none;
}
.dropdown.open {
  opacity: 1;
  transform: translateY(0);
  pointer-events: auto;
}
```

### 6.5 仅有意义运动

动画应传达状态、引导注意力或显示空间关系。永远不要仅为了装饰而动画。

---

## 7. 深色模式和主题 [MEDIUM]

### 7.1 系统偏好检测

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0f0f17;
    --text: #e4e4ef;
    --surface: #1c1c2e;
    --border: #2e2e44;
  }
}
```

### 7.2 CSS 自定义属性用于主题

将所有主题值定义为自定义属性。通过更改属性值切换主题。

```css
:root {
  color-scheme: light dark;

  /* 浅色主题（默认） */
  --color-bg: #ffffff;
  --color-surface: #f5f5f7;
  --color-text-primary: #1a1a2e;
  --color-text-secondary: #555770;
  --color-border: #d1d1e0;
  --color-primary: #2563eb;
  --color-primary-text: #ffffff;
  --color-error: #dc2626;
  --color-success: #16a34a;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-bg: #0f0f17;
    --color-surface: #1c1c2e;
    --color-text-primary: #e4e4ef;
    --color-text-secondary: #a0a0b8;
    --color-border: #2e2e44;
    --color-primary: #60a5fa;
    --color-primary-text: #0f0f17;
    --color-error: #f87171;
    --color-success: #4ade80;
  }
}
```

### 7.3 color-scheme 元标签

告诉浏览器支持的颜色方案，以便原生 UI 元素（滚动条、表单控件）使用。

```html
<meta name="color-scheme" content="light dark">
```

### 7.4 在两种模式下保持对比度

在浅色和深色模式下验证对比度比例。深色模式通常在深色表面上存在低对比度文本。

### 7.5 自适应图像

为浅色和深色上下文提供适当的图像。

```html
<picture>
  <source srcset="logo-dark.svg" media="(prefers-color-scheme: dark)">
  <img src="logo-light.svg" alt="公司标志">
</picture>
```

```css
/* 或在简单情况下使用 CSS 过滤器 */
@media (prefers-color-scheme: dark) {
  .decorative-img {
    filter: brightness(0.9) contrast(1.1);
  }
}
```

### 7.6 尊重 prefers-contrast

使用 `@media (prefers-contrast: more)` 和 `@media (prefers-contrast: forced)` 尊重用户的对比度偏好。`prefers-contrast: more` 响应 macOS/iOS 系统设置中的“增加对比度”；`prefers-contrast: forced` 响应 Windows 高对比度模式——这是一个独特的 OS 功能，完全覆盖颜色。

```css
/* 默认主题 */
:root {
  --color-text: #555770;
  --color-border: #d1d1e0;
  --color-bg: #ffffff;
}

/* 高对比度模式：更强的文本和边框颜色 */
@media (prefers-contrast: more) {
  :root {
    --color-text: #1a1a2e;       /* 更深的文本以获得更高的比例 */
    --color-border: #1a1a2e;     /* 更强的边框 */
    --color-bg: #ffffff;
  }

  /* 确保交互元素有清晰的边界 */
  button, input, select, textarea {
    border: 2px solid currentColor;
  }
}

/* 强制颜色（Windows 高对比度模式） */
@media (prefers-contrast: forced) {
  /* 使用系统颜色关键字以尊重 OS 颜色调色板 */
  :root {
    --color-text: ButtonText;
    --color-bg: ButtonFace;
    --color-border: ButtonBorder;
  }
}
```

---

## 8. 导航和状态 [MEDIUM]

### 8.1 URL 反映状态

每个有意义的视图都应该有一个唯一的 URL。用户应该能够书签、分享和重新加载任何状态。

```js
// 无需全页重新加载地更新 URL
function updateFilters(filters) {
  const params = new URLSearchParams(filters);
  history.pushState(null, '', `?${params}`);
  renderResults(filters);
}

// 在加载时从 URL 恢复状态
const params = new URLSearchParams(location.search);
const initialFilters = Object.fromEntries(params);
```

### 8.2 浏览器后退/前进

处理 `popstate` 以支持浏览器导航。

```js
window.addEventListener('popstate', () => {
  const params = new URLSearchParams(location.search);
  renderResults(Object.fromEntries(params));
});
```

### 8.3 活跃的导航状态

在导航中指示当前页面或章节。使用 `aria-current="page"` 为活动链接。

```html
<nav aria-label="主导航">
  <a href="/" aria-current="page">主页</a>
  <a href="/products">产品</a>
  <a href="/about">关于</a>
</nav>
```

```css
[aria-current="page"] {
  font-weight: 700;
  border-bottom: 2px solid var(--color-primary);
}
```

### 8.4 面包屑导航

为具有深层结构的网站提供面包屑导航。

```html
<nav aria-label="面包屑">
  <ol>
    <li><a href="/">主页</a></li>
    <li><a href="/products">产品</a></li>
    <li><a href="/products/widgets" aria-current="page">小部件</a></li>
  </ol>
</nav>
```

### 8.5 滚动恢复

管理 SPA 导航的滚动位置。

```js
// 禁用浏览器自动恢复以手动控制
if ('scrollRestoration' in history) {
  history.scrollRestoration = 'manual';
}

// 导航前保存滚动位置
function saveScrollPosition() {
  sessionStorage.setItem(`scroll-${location.pathname}`, window.scrollY);
}

// 在后退/前进时恢复
window.addEventListener('popstate', () => {
  const saved = sessionStorage.getItem(`scroll-${location.pathname}`);
  if (saved) {
    requestAnimationFrame(() => window.scrollTo(0, parseInt(saved)));
  }
});
```

---

## 9. 触摸和交互 [MEDIUM]

### 9.1 touch-action 用于滚动控制

使用 `touch-action` 控制交互元素的手势行为。

```css
/* 仅允许垂直滚动（禁用水平滑动和缩放） */
.vertical-scroll {
  touch-action: pan-y;
}

/* 轮播：仅水平滚动 */
.carousel {
  touch-action: pan-x;
}

/* 画布/地图：禁用所有浏览器手势 */
.canvas {
  touch-action: none;
}
```

### 9.2 点击高亮

控制移动 WebKit 浏览器上的点击高亮。

```css
button, a {
  -webkit-tap-highlight-color: transparent;
}
```

### 9.3 悬停和焦点平等

每个悬停交互都必须与键盘焦点配合使用。

```css
/* 始终将 :hover 与 :focus-visible 配对 */
.card:hover,
.card:focus-visible {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}
```

### 9.4 无仅悬停交互

永远不要将基本功能隐藏在悬停后面。触摸设备没有悬停状态。

```css
/* 不好：内容仅在悬停时可见 */
/* .tooltip { display: none; }
   .trigger:hover .tooltip { display: block; } */

/* 好：也适用于焦点和点击 */
.trigger:hover .tooltip,
.trigger:focus-within .tooltip,
.tooltip:focus-within {
  display: block;
}
```

### 9.5 滚动快照用于轮播

使用 CSS 滚动快照为卡片轮播和水平列表。

```css
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  gap: 1rem;
  scroll-padding: 1rem;
}

.carousel > .slide {
  scroll-snap-align: start;
  flex: 0 0 min(85%, 400px);
}
```

---

## 10. 国际化 [MEDIUM]

### 10.1 dir 和 lang 属性

在 `<html>` 元素上设置 `lang`。使用 `dir="auto"` 为用户生成的内容。

```html
<html lang="en" dir="ltr">

<!-- 用户生成的内容：让浏览器检测方向 -->
<p dir="auto">用户提交的文本</p>

<!-- 已知 RTL 内容的显式覆盖 -->
<blockquote lang="ar" dir="rtl">...</blockquote>
```

### 10.2 Intl API 用于格式化

使用 `Intl` API 进行区域感知格式化。永远不要硬编码日期或数字格式。

```js
// 日期
new Intl.DateTimeFormat('en-US', { dateStyle: 'long' }).format(date);
// "January 15, 2026"

// 数字
new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(1234.56);
// "1.234,56 EUR"

// 相对时间
new Intl.RelativeTimeFormat('en', { numeric: 'auto' }).format(-1, 'day');
// "yesterday"

// 列表
new Intl.ListFormat('en', { style: 'long', type: 'conjunction' }).format(['a', 'b', 'c']);
// "a, b, and c"

// 复数
const pr = new Intl.PluralRules('en');
const suffixes = { one: 'st', two: 'nd', few: 'rd', other: 'th' };
function ordinal(n) { return `${n}${suffixes[pr.select(n)]}`; }
```

### 10.3 避免 图像中的文本

图像中的文本无法翻译、调整大小或由屏幕阅读器读取。当需要样式的文本覆盖时，使用 HTML/CSS 文本与背景图像。

### 10.4 CSS 逻辑属性

使用逻辑属性而不是物理属性以支持 LTR 和 RTL 布局。

```css
/* 物理（在从右到左的语言中会断行） */
/* margin-left: 1rem; padding-right: 2rem; border-left: 1px solid; */

/* 逻辑（在从左到右和从右到左的语言中均有效） */
.sidebar {
  margin-inline-start: 1rem;
  padding-inline-end: 2rem;
  border-inline-start: 1px solid var(--color-border);
}

.stack > * + * {
  margin-block-start: 1rem;
}

/* 逻辑简写 */
.box {
  margin-inline: auto;     /* 左 + 右 */
  padding-block: 2rem;     /* 上 + 下 */
  inset-inline-start: 0;   /* 左（在从左到右的语言中），右（在从右到左的语言中） */
  border-start-start-radius: 8px; /* 左上角（在从左到右的语言中），右上角（在从右到左的语言中） */
}
```

| 物理 | 逻辑 |
|------|------|
| `left` / `right` | `inline-start` / `inline-end` |
| `top` / `bottom` | `block-start` / `block-end` |
| `margin-left` | `margin-inline-start` |
| `padding-right` | `padding-inline-end` |
| `border-top-left-radius` | `border-start-start-radius` |
| `width` | `inline-size` |
| `height` | `block-size` |
| `text-align: left` | `text-align: start` |

### 10.5 从右到左的语言布局支持

在从右到左的语言模式下测试布局。Flexbox 和 Grid 使用逻辑属性自动处理从右到左的语言。

```css
/* 此布局在从左到右和从右到左的语言中无需更改即可工作 */
.layout {
  display: flex;
  gap: 1rem;
}

/* 指示方向的图标需要翻转 */
[dir="rtl"] .arrow-icon {
  transform: scaleX(-1);
}
```

---

## 11. 渐进式网络应用 [MEDIUM]

渐进式网络应用允许网络应用被安装并在离线状态下运行。在构建可安装的网络应用时，以下规则确保体验的一致性和可靠性。

### 11.1 提供完整的网络应用清单

在 `<head>` 中通过链接包含 `manifest.json`，其中包含所有可安装性所需字段。缺少字段会静默阻止安装提示。

```html
<link rel="manifest" href="/manifest.json">
```

```json
{
  "name": "我的应用",
  "short_name": "应用",
  "start_url": "/",
  "display": "standalone",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
```

**不正确：**
```json
{
  "name": "我的应用"
  // 缺少 start_url、display 和 icons — 应用不可安装
}
```

### 11.2 设置 theme_color 和 background_color

`theme_color` 调色浏览器的工具栏和操作系统的任务切换器。`background_color` 在应用加载前填充启动画面。两者必须与您的品牌颜色匹配。

```json
{
  "theme_color": "#1a73e8",
  "background_color": "#ffffff"
}
```

### 11.3 注册 Service Worker 以支持离线功能

Service Worker 是可安装性和离线功能所必需的。在安装时缓存关键资源；离线时从缓存中响应。

```js
// 在您的主入口点
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');
}
```

```js
// sw.js — 安装时缓存，离线时从缓存中提供
const CACHE = 'v1';
const PRECACHE = ['/', '/index.html', '/app.js', '/app.css'];

self.addEventListener('install', e =>
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)))
);

self.addEventListener('fetch', e =>
  e.respondWith(
    caches.match(e.request).then(hit => hit ?? fetch(e.request))
  )
);
```

### 11.4 满足可安装性标准

要显示浏览器安装提示：应用必须通过 HTTPS 提供，有一个注册的 Service Worker 并带有 `fetch` 处理器，并且包含一个带有 `name`、`icons`、`start_url` 和 `display: standalone`（或 `fullscreen`/`minimal-ui`）的清单。

### 11.5 适当使用显示模式

| 值 | 使用场景 |
|----|----------|
| `standalone` | 应用替换浏览器 UI；最常见的选择 |
| `fullscreen` | 游戏 或 媒体应用需要整个屏幕 |
| `minimal-ui` | 保留最小的浏览器控件（后退、刷新） |
| `browser` | 无安装行为；在浏览器标签中打开 |

---

## 评估清单

在构建或审查网络界面时使用此清单。

### 可访问性
- [ ] 所有图像都有适当的 `alt` 文本
- [ ] 颜色对比度满足 4.5:1（文本）和 3:1（UI 组件）
- [ ] 所有交互元素都可以通过键盘访问
- [ ] 聚焦指示器可见（对比度 3:1，最小周长 2px）
- [ ] 提供跳过导航链接
- [ ] 表单输入有相关联的标签
- [ ] 错误消息链接到它们的输入
- [ ] 动态内容更新使用 ARIA live regions
- [ ] 没有内容每秒闪烁超过 3 次
- [ ] 页面有正确的标题层次结构（h1-h6，无跳过）
- [ ] 使用正确的地标（main、nav、header、footer）

### 响应式
- [ ] 在 320px 宽度下没有水平滚动
- [ ] 触摸目标至少为 44x44px
- [ ] 存在视口元标签（无 user-scalable=no）
- [ ] 布局在手机、平板和桌面设备上均可工作
- [ ] 手机上无需缩放即可阅读文本

### 表单
- [ ] 所有输入都有可见的标签
- [ ] 常见字段设置了 autocomplete 属性
- [ ] 正确的输入类型触发正确的手机键盘
- [ ] 错误消息清晰且具体
- [ ] 标记了必填字段
- [ ] 提交按钮未被禁用

### 性能
- [ ] 超出视口图像使用 `loading="lazy"`
- [ ] 图像有明确的 `width` 和 `height`
- [ ] 关键字体预加载
- [ ] 第三方来源使用 `preconnect`
- [ ] 大型 JS 打包文件进行代码拆分

### 动画和主题
- [ ] 尊重 `prefers-reduced-motion`
- [ ] 动画仅使用 `transform` 和 `opacity`
- [ ] 深色模式保持对比度比例
- [ ] 存在 `color-scheme` 元标签
- [ ] 主题使用 CSS 自定义属性
- [ ] `prefers-contrast: more` 增加文本和边框对比度
- [ ] `prefers-contrast: forced` 使用系统颜色关键字

### 国际化
- [ ] `<html>` 上的 `lang` 属性
- [ ] 使用逻辑属性（不使用物理属性）
- [ ] 使用 Intl API 格式化日期/数字
- [ ] 文本未嵌入图像中
- [ ] 在从右到左的语言模式下测试布局

### 渐进式网络应用
- [ ] 从 `<head>` 链接 Web App Manifest，包含 `name`、`icons`、`start_url` 和 `display`
- [ ] `theme_color` 和 `background_color` 与品牌调色板匹配
- [ ] 注册 Service Worker 并带有 `fetch` 处理器以支持离线功能
- [ ] 应用通过 HTTPS 提供

---

## 常见反模式

| 反模式 | 修复 |
|-------|------|
| `<div onclick="...">` | 使用 `<button>` |
| `outline: none` 而无替代方案 | 使用 `:focus-visible` 并自定义轮廓 |
| `placeholder` 作为标签 | 添加一个 `<label>` 元素 |
| `tabindex="5"` | 使用 `tabindex="0"` 或自然顺序 |
| `user-scalable=no` | 移除它 |
| `font-size: 12px` | 使用 `font-size: 0.75rem` |
| 动画 `width`/`height`/`top`/`left` | 动画 `transform` 和 `opacity` |
| 禁用提交按钮 | 提交时验证，显示错误 |
| 仅使用颜色表示状态 | 添加图标、文本或图案 |
| `margin-left` / `padding-right` | 使用 `margin-inline-start` / `padding-inline-end` |
| `<img>` 缺少尺寸 | 添加 `width` 和 `height` 属性 |
| 仅使用悬停的披露 | 添加 `:focus-within` 和点击处理程序 |
