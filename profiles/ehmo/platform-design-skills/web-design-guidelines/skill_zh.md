# Web Platform Design Guidelines

跨框架的规则，用于可访问、高性能、响应式的 Web 界面。基于 WCAG 2.2、MDN Web 文档和现代 Web 平台 API。

---

## 1. 可访问性 / WCAG [关键]

可访问性不是可选项。本节中的大多数规则都映射到 WCAG 2.2 成功标准中的 A 级或 AA 级。少量最佳实践规则（内联注释中注明）针对 AAA 级或超出 WCAG。

### 1.1 使用语义 HTML 元素

按其预期用途使用元素。语义结构提供免费的可访问性、SEO 和阅读模式支持。

| 元素 | 用途 |
|------|------|
| `<main>` | 主要页面内容（每个页面一个） |
| `<nav>` | 导航块 |
| `<header>` | 导入内容或导航辅助 |
| `<footer>` | 最近分区内容的页脚 |
| `<article>` | 自包含、可独立分发的内容 |
| `<section>` | 带标题的主题分组 |
| `<aside>` | 旁支相关内容（侧边栏、调用卡） |
| `<figure>` / `<figcaption>` | 插图、图表、代码列表 |
| `<details>` / `<summary>` | 可展开/可折叠的披露小部件 |
| `<dialog>` | 模态或非模态对话框 |
| `<time>` | 机器可读的日期/时间 |
| `<mark>` | 高亮/引用的文本 |
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

<!-- 不好：div 汤姆 |
<div class="main">
  <div class="article">
    <div class="title">文章标题</div>
    <div class="content">内容...</div>
  </div>
</div>
```

**反模式**：使用 `<div>` 或 `<span>` 作为交互元素。当存在 `<button>` 时，永远不要写 `<div onclick>`。

### 1.2 交互元素上的 ARIA 标签

每个交互元素都必须具有可访问的名称。优先使用可见文本；仅在可见文本不足时使用 `aria-label` 或 `aria-labelledby`（SC 4.1.2）。

```html
<!-- 仅图标按钮：需要 aria-label |
<button aria-label="关闭对话框">
  <svg aria-hidden="true">...</svg>
</button>

<!-- 通过 labelledby 链接 |
<h2 id="section-title">通知</h2>
<ul aria-labelledby="section-title">...</ul>

<!-- 重复：可见文本足够 |
<button>保存更改</button> <!-- 无需 aria-label |
```

### 1.3 键盘导航

所有交互元素都必须可通过键盘访问和操作（SC 2.1.1）。

- 使用原生交互元素（`<button>`、`<a href>`、`<input>`、`<select>`），它们默认可通过键盘访问。
- 自定义小部件需要 `tabindex="0"` 进入 Tab 顺序并使用 keydown 处理程序激活。
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

### 1.4 可见的焦点指示器

永远不要在不提供可见替代的情况下移除焦点轮廓（SC 2.4.7、增强 SC 2.4.11 (AA) 和 SC 2.4.12 (AAA) 在 WCAG 2.2 中）。

```css
/* 良好：自定义焦点指示器 |
:focus-visible {
  outline: 3px solid var(--focus-color, #4A90D9);
  outline-offset: 2px;
}

/* 移除默认值仅当 :focus-visible 受支持时 |
:focus:not(:focus-visible) {
  outline: none;
}

/* 不好：移除所有焦点样式 |
/* *:focus { outline: none; } */
```

WCAG 2.2 要求焦点指示器具有组件周长两倍的最小面积，与相邻颜色对比度至少为 3:1。

### 1.5 跳过导航链接

提供一种机制来跳过重复的内容块（SC 2.4.1）。

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

每个 `<img>` 都必须有 `alt` 属性（SC 1.1.1）。

- **信息性图像**：描述内容和功能。`alt="条形图显示第四季度销售额翻倍"`.
- **装饰性图像**：使用 `alt=""`（空字符串），以便屏幕阅读器跳过它们。
- **功能性图像**（链接/按钮内）：描述操作。`alt="搜索"`.
- **复杂图像**：使用 `alt` 进行简短描述，链接到长描述或使用 `<figcaption>`.

```html
<img src="chart.png" alt="收入图表：第一季度 $2M，第二季度 $2.4M，第三季度 $3.1M，第四季度 $4.5M">
<img src="decorative-wave.svg" alt="">
```

### 1.7 色彩对比度

保持最小对比度比率（SC 1.4.3, 1.4.6, 1.4.11）。

| 内容 | 最小比率 |
|------|----------|
| 正常文本（<24px / <18.66px 粗体） | 4.5:1 |
| 大文本（>=24px / >=18.66px 粗体） | 3:1 |
| UI 组件和图形对象 | 3:1 |

不要仅依赖颜色来传达信息（SC 1.4.1）。将颜色与图标、文本或模式配对。

```css
/* 检查这些 token 的对比度 |
:root {
  --text-primary: #1a1a2e;    /* on white: ~16:1 |
  --text-secondary: #555770;  /* on white: ~6.5:1 |
  --text-disabled: #767693;   /* on white: ~4.5:1, 边缘 |
}
```

### 1.8 表单标签

每个表单输入都必须具有程序关联的标签（SC 1.3.1, 3.3.2）。

```html
<!-- 显式标签（首选） |
<label for="email">电子邮件地址</label>
<input id="email" type="email" autocomplete="email">

<!-- 隐式标签（可接受） |
<label>
  电子邮件地址
  <input type="email" autocomplete="email">
</label>

<!-- 永远不要：占位符作为唯一标签 |
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
<!-- 优雅：用户空闲时宣布 |
<div aria-live="polite" aria-atomic="true">
  3 个结果找到
</div>

<!-- 声明：打断当前语音 |
<div role="alert">
  您的会话将在 2 分钟后过期。
</div>

<!-- 状态消息 |
<div role="status">
  文件上传成功。
</div>
```

默认情况下使用 `aria-live="polite"。保留 `role="alert" / `aria-live="assertive"` 用于时间敏感的警告。

### 1.11 ARIA 角色快速参考

| 角色 | 用途 | 本地等效项 |
|------|------|------------|
| `button` | 可点击操作 | `<button>` |
| `link` | 导航 | `<a href>` |
| `tab` / `tablist` / `tabpanel` | 选项卡界面 | 无 |
| `dialog` | 模态 | `<dialog>` |
| `alert` | 断言性实时区域 | 无 |
| `status` | 优雅的实时区域 | `<output>` |
| `navigation` | 导航地标 | `<nav>` |
| `main` | 主要地标 | `<main>` |
| `complementary` | 旁支地标 | `<aside>` |
| `search` | 搜索地标 | `<search>` (HTML5) |
| `img` | 图像 | `<img>` |
| `list` / `listitem` | 列表 | `<ul>/<li>` |
| `heading` | 标题（带有 `aria-level`） | `<h1>`-`<h6>` |
| `menu` / `menuitem` | 菜单小部件 | 无 |
| `tree` / `treeitem` | 树视图 | 无 |
| `grid` / `row` / `gridcell` | 数据网格 | `<table>` |
| `progressbar` | 进度 | `<progress>` |
| `slider` | 范围输入 | `<input type="range">` |
| `switch` | 切换 | `<input type="checkbox">` |

**规则**：优先使用本地 HTML 而不是 ARIA。仅在不存在本地元素的图案中使用 ARIA。

### 1.12 名称中的标签（WCAG 2.5.3 级 A）

当交互元素具有可见文本时，其可访问名称必须包含该可见文本作为子字符串（SC 2.5.3）。语音控制用户（Dragon NaturallySpeaking、macOS Voice Control）说出可见标签以激活控件。如果 `aria-label` 替换或与可见文本矛盾，语音命令将失败。

```html
<!-- 正确：aria-label 包含可见文本作为子字符串 |
<button aria-label="从购物车中删除项目">删除</button>

<!-- 正确：没有 aria-label 需要的可见文本 |
<button>保存更改</button>

<!-- 正确：图标按钮 - 没有可见文本，aria-label 很好 |
<button aria-label="关闭对话框">
  <svg aria-hidden="true">...</svg>
</button>
```

```html
<!-- 不正确：aria-label 使用不同的文本覆盖可见文本 |
<button aria-label="移除">删除</button>

<!-- 不正确：aria-label 不包含可见 "提交" |
<button aria-label="转到下一步">提交</button>
```

**规则**：当存在可见文本时，`aria-label` 必须包含该可见文本（逐字，不区分大小写）。当可见文本足够时，优先不使用 `aria-label`。

---

## 2. 响应式设计 [关键]

### 2.1 移动优先方法

为最小的视口编写基本样式。使用 `min-width` 媒体查询分层复杂性。

```css
/* 基础：移动端 |
.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

/* 平板电脑 |
@media (min-width: 48rem) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 桌面端 |
@media (min-width: 64rem) {
  .grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 1.2 使用现代 CSS 函数的流式布局

使用 `clamp()`、`min()` 和 `max()` 进行无断点流式尺寸。

```css
/* 流式排版 |
h1 {
  font-size: clamp(1.75rem, 1.2rem + 2vw, 3rem);
}

/* 流式间距 |
.section {
  padding: clamp(1.5rem, 4vw, 4rem);
}

/* 流式容器 |
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

###  </div>
