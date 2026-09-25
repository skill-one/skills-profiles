# Shopify 主题的辅助功能

## 核心原则

每个交互组件必须能在仅使用键盘、屏幕阅读器和减少动画效果的情况下正常工作。从语义化的 HTML 开始——仅在原生语义不足时才添加 ARIA 属性。

## 决策表：选择哪种模式？

| 组件 | HTML 元素 | ARIA 模式 | 参考 |
|-------|----------|----------|------|
| 可展开内容 | `<details>/<summary>` | 无需 | [手风琴](#accordion) |
| 模态/对话框 | `<dialog>` | `aria-modal="true"` | [模态](#modal) |
| 提示/弹出 | `[popover]` 属性 | `role="tooltip"` 降级 | [提示](#tooltip) |
| 下拉菜单 | `<nav>` + `<ul>` | 触发器上 `aria-expanded` | [导航](#dropdown-navigation) |
| 标签界面 | `<div>` | `role="tablist/tab/tabpanel"` | [标签](#tabs) |
| 轮播/滑块 | `<div>` | `role="region"` + `aria-roledescription` | [轮播](#carousel) |
| 产品卡片 | `<article>` | `aria-labelledby` | [产品卡片](#product-card) |
| 表单 | `<form>` | `aria-invalid`, `aria-describedby` | [表单](#forms) |
| 购物车抽屉 | `<dialog>` | 聚焦陷阱 | [购物车抽屉](#cart-drawer) |
| 价格显示 | `<span>` | `aria-label` 用于上下文 | [价格显示](#price-display) |
| 筛选器 | `<form>` + `<fieldset>` | `aria-expanded` 用于披露 | [筛选器](#product-filters) |

## 页面结构

### 地标

```html
<body>
  <a href="#main-content" class="skip-link">{{ 'accessibility.skip_to_content' | t }}</a>
  <header role="banner">
    <nav aria-label="{{ 'accessibility.main_navigation' | t }}">...</nav>
  </header>
  <main id="main-content">
    <!-- 页面所有内容位于 main 内 -->
  </main>
  <footer role="contentinfo">
    <nav aria-label="{{ 'accessibility.footer_navigation' | t }}">...</nav>
  </footer>
</body>
```

- 每页仅使用一个 `<header>`, `<main>`, `<footer>`
- 多个 `<nav>` 元素必须具有不同的 `aria-label`
- 所有内容必须位于地标内

### 跳过链接

```css
.skip-link {
  position: absolute;
  inset-inline-start: -999px;
  z-index: 999;
}
.skip-link:focus {
  position: fixed;
  inset-block-start: 0;
  inset-inline-start: 0;
  padding: 1rem;
  background: var(--color-background);
  color: var(--color-foreground);
}
```

### 标题

- 每页仅使用一个 `<h1>`, 从不跳过级别 (h1 → h3)
- 使用真实的标题元素，而不是样式化的 div
- 模板: `<h1>` 通常是页面/产品标题

## 聚焦管理

### 聚焦指示器

```css
/* 所有交互元素 */
:focus-visible {
  outline: 2px solid rgb(var(--color-focus));
  outline-offset: 2px;
}

/* 高对比度模式 */
@media (forced-colors: active) {
  :focus-visible {
    outline: 3px solid LinkText;
  }
}
```

- 聚焦指示器最小 3:1 对比度
- 使用 `:focus-visible` (而不是 `:focus`) 以避免在点击时显示
- 永远不要 `outline: none` 而没有可见的替代方案

### 聚焦陷阱（模态/抽屉）

- 在模态、抽屉和对话框内设置聚焦陷阱
- 关闭时返回到触发元素
- 打开时第一个可聚焦元素获得焦点
- 查询所有可聚焦元素: `a[href], button:not([disabled]), input:not([disabled]), select, textarea, [tabindex]:not([tabindex="-1"])`

参见 [聚焦和键盘模式](references/focus-and-keyboard.md) 获取完整的 FocusTrap 实现。

## 组件模式

### 产品卡片

```html
<article class="product-card" aria-labelledby="ProductTitle-{{ product.id }}">
  <a href="{{ product.url }}" class="product-card__link" aria-labelledby="ProductTitle-{{ product.id }}">
    <img
      src="{{ product.featured_image | image_url: width: 400 }}"
      alt="{{ product.featured_image.alt | escape }}"
      loading="lazy"
      width="{{ product.featured_image.width }}"
      height="{{ product.featured_image.height }}"
    >
  </a>
  <h3 id="ProductTitle-{{ product.id }}">
    <a href="{{ product.url }}">{{ product.title }}</a>
  </h3>
  <div class="product-card__price" aria-label="{{ 'products.price_label' | t: price: product.price | money }}">
    {{ product.price | money }}
  </div>
  <button
    class="product-card__quick-add"
    tabindex="-1"
    aria-label="{{ 'products.quick_add' | t: title: product.title }}"
  >
    {{ 'products.add_to_cart' | t }}
  </button>
</article>
```

**规则:**
- 每个卡片只有一个 tab 停靠点（主链接）
- 鼠标独占快捷方式上使用 `tabindex="-1"`（快速添加）
- `<article>` 上使用 `aria-labelledby` 指向标题
- 图片使用描述性 alt 文本；装饰性图片使用 `alt=""`

### 轮播

```html
<div
  role="region"
  aria-roledescription="carousel"
  aria-label="{{ section.settings.heading | escape }}"
>
  <div class="carousel__controls">
    <button
      aria-label="{{ 'accessibility.previous_slide' | t }}"
      aria-controls="CarouselSlides-{{ section.id }}"
    >{% render 'icon-chevron-left' %}</button>
    <button
      aria-label="{{ 'accessibility.next_slide' | t }}"
      aria-controls="CarouselSlides-{{ section.id }}"
    >{% render 'icon-chevron-right' %}</button>
    <button
      aria-label="{{ 'accessibility.pause_slideshow' | t }}"
      aria-pressed="false"
    >{% render 'icon-pause' %}</button>
  </div>

  <div id="CarouselSlides-{{ section.id }}" aria-live="polite">
    {% for slide in section.blocks %}
      <div
        role="group"
        aria-roledescription="slide"
        aria-label="{{ 'accessibility.slide_n_of_total' | t: n: forloop.index, total: forloop.length }}"
        {% unless forloop.first %}aria-hidden="true"{% endunless %}
      >
        {{ slide.settings.content }}
      </div>
    {% endfor %}
  </div>
</div>
```

**规则:**
- 自动旋转最小 5 秒，鼠标悬停/聚焦时暂停
- 自动旋转轮播需要播放/暂停按钮
- 滑块容器上使用 `aria-live="polite"`（自动旋转期间设置为 `"off"`）
- 不活跃的滑块上使用 `aria-hidden="true"`
- 每个滑块: `role="group"` + `aria-roledescription="slide"`

### 模态

```html
<dialog
  id="Modal-{{ section.id }}"
  aria-labelledby="ModalTitle-{{ section.id }}"
  aria-modal="true"
>
  <div class="modal__header">
    <h2 id="ModalTitle-{{ section.id }}">{{ title }}</h2>
    <button
      type="button"
      aria-label="{{ 'accessibility.close' | t }}"
      on:click="/closeModal"
    >{% render 'icon-close' %}</button>
  </div>
  <div class="modal__content">
    <!-- 内容 -->
  </div>
</dialog>
```

**规则:**
- 使用原生 `<dialog>` 元素
- `aria-labelledby` 指向标题
- 按 Escape 键关闭（原生 `<dialog>` 支持）
- 打开时聚焦第一个交互元素
- 关闭时返回到触发元素

### 购物车抽屉

与模态模式相同，但需额外:
- 用于购物车数量更新的活区域: `<span aria-live="polite" aria-atomic="true">`
- 清晰的"移除商品"按钮，使用 `aria-label="{{ 'cart.remove_item' | t: title: item.title }}"`
- 带关联标签的数量输入框

### 表单

```html
<form action="{{ routes.cart_url }}" method="post">
  <div class="form__field">
    <label for="Email-{{ section.id }}">{{ 'forms.email' | t }}</label>
    <input
      type="email"
      id="Email-{{ section.id }}"
      name="email"
      required
      aria-required="true"
      autocomplete="email"
      aria-describedby="EmailError-{{ section.id }}"
    >
    <p
      id="EmailError-{{ section.id }}"
      class="form__error"
      role="alert"
      hidden
    >{{ 'forms.email_required' | t }}</p>
  </div>
</form>
```

**规则:**
- 每个输入框都有可见的 `<label>` 与匹配的 `for`/`id`
- 使用 `<fieldset>/<legend>` 对单选/复选框组
- 错误消息: `role="alert"` + `aria-describedby` 链接到输入框
- `aria-invalid="true"` 在无效输入上
- 常见字段使用 `autocomplete` 属性
- 必填字段: `required` + `aria-required="true"` + 视觉指示器

### 产品筛选器

```html
<form class="facets">
  <div class="facets__group">
    <button
      type="button"
      aria-expanded="false"
      aria-controls="FilterColor-{{ section.id }}"
    >{{ 'filters.color' | t }}</button>
    <fieldset id="FilterColor-{{ section.id }}" hidden>
      <legend class="visually-hidden">{{ 'filters.filter_by_color' | t }}</legend>
      {% for color in colors %}
        <label>
          <input type="checkbox" name="filter.color" value="{{ color }}">
          {{ color }}
        </label>
      {% endfor %}
    </fieldset>
  </div>
  <div aria-live="polite" aria-atomic="true">
    {{ 'filters.results_count' | t: count: results.size }}
  </div>
</form>
```

### 价格显示

```html
{% if product.compare_at_price > product.price %}
  <div class="price" aria-label="{{ 'products.sale_price_label' | t: sale_price: product.price | money, original_price: product.compare_at_price | money }}">
    <s aria-hidden="true">{{ product.compare_at_price | money }}</s>
    <span>{{ product.price | money }}</span>
  </div>
{% else %}
  <div class="price">{{ product.price | money }}</div>
{% endif %}
```

- 使用 `aria-label` 提供完整价格上下文（折扣与原价）
- `aria-hidden="true"` 在视觉删除线中以避免重复阅读

### 手风琴

```html
<details>
  <summary>{{ block.settings.heading }}</summary>
  <div class="accordion__content">
    {{ block.settings.content }}
  </div>
</details>
```

原生 `<details>/<summary>` 自动提供键盘和屏幕阅读器支持。

### 标签

```html
<div role="tablist" aria-label="{{ 'accessibility.product_tabs' | t }}">
  {% for tab in tabs %}
    <button
      role="tab"
      id="Tab-{{ tab.id }}"
      aria-selected="{% if forloop.first %}true{% else %}false{% endif %}"
      aria-controls="Panel-{{ tab.id }}"
      tabindex="{% if forloop.first %}0{% else %}-1{% endif %}"
    >{{ tab.title }}</button>
  {% endfor %}
</div>
{% for tab in tabs %}
  <div
    role="tabpanel"
    id="Panel-{{ tab.id }}"
    aria-labelledby="Tab-{{ tab.id }}"
    {% unless forloop.first %}hidden{% endunless %}
    tabindex="0"
  >{{ tab.content }}</div>
{% endfor %}
```

- 箭头键在标签间导航（左/右）
- 只有活动标签有 `tabindex="0"`，其他为 `-1`

### 下拉导航

```html
<nav aria-label="{{ 'accessibility.main_navigation' | t }}">
  <ul role="list">
    {% for link in linklists.main-menu.links %}
      <li>
        {% if link.links.size > 0 %}
          <button aria-expanded="false" aria-controls="Submenu-{{ forloop.index }}">
            {{ link.title }}
          </button>
          <ul id="Submenu-{{ forloop.index }}" hidden role="list">
            {% for child in link.links %}
              <li><a href="{{ child.url }}">{{ child.title }}</a></li>
            {% endfor %}
          </ul>
        {% else %}
          <a href="{{ link.url }}">{{ link.title }}</a>
        {% endif %}
      </li>
    {% endfor %}
  </ul>
</nav>
```

### 提示

```html
<button aria-describedby="Tooltip-{{ block.id }}">
  {{ 'labels.info' | t }}
</button>
<div id="Tooltip-{{ block.id }}" role="tooltip" popover>
  {{ block.settings.tooltip_text }}
</div>
```

## 移动端辅助功能

- **触摸目标:** 最小 44x44px，目标间 8px 间距
- **不锁定方向:** 永远不要限制为横屏/竖屏
- **无仅悬停内容:** 所有内容均可通过点击访问
- 使用 `dvh` 而不是 `vh` 作为移动视口单位

## 动画与动画效果

```css
/* 始终提供减少动画效果 */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

- 闪光频率不超过每秒 3 次
- 自动播放的动画需要暂停/停止控制
- 只有有意义的动画——不要为装饰而动画

## 视觉隐藏实用工具

```css
.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

用于屏幕阅读器专用的内容，如标签和描述。

## 颜色对比度

| 元素 | 最小比例 |
|------|----------|
| 普通文本 (<18px / <14px 粗体) | 4.5:1 |
| 大文本 (≥18px / ≥14px 粗体) | 3:1 |
| UI 组件与图形 | 3:1 |
| 聚焦指示器 | 3:1 |

永远不要仅依赖颜色来传达信息——始终与文本、图标或模式配合使用。

## 参考

- [组件辅助功能模式](references/component-patterns.md)
- [聚焦和键盘模式](references/focus-and-keyboard.md)
