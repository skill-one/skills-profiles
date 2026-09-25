# Shopify Liquid主题的CSS、JS和HTML标准

## 核心原则

1. **渐进增强** — 语义化HTML优先，其次是CSS，最后是JS
2. **无外部依赖** — JavaScript仅使用原生浏览器API
3. **设计令牌** — 永远不要硬编码颜色、间距或字体
4. **BEM命名** — 全局一致的类命名
5. **防御性CSS** — 优雅处理边缘情况

## Liquid主题中的CSS

### CSS存放位置

| 位置 | Liquid? | 用途 |
|------|---------|---------|
| `{% stylesheet %}` | 否 | 组件级样式（每个文件一个） |
| `{% style %}` | 是 | 需要Liquid的动态值（例如，颜色设置） |
| `assets/*.css` | 否 | 共享/全局样式 |

**关键点：** `{% stylesheet %}` 不会处理Liquid。使用内联 `style` 属性处理动态值：

```liquid
{%- comment -%} 做法正确：内联变量 {%- endcomment -%}
<div
  class="hero"
  style="--bg-color: {{ section.settings.bg_color }}; --padding: {{ section.settings.padding }}px;"
>

{%- comment -%} 错误做法：Liquid在stylesheet内 {%- endcomment -%}
{% stylesheet %}
  .hero { background: {{ section.settings.bg_color }}; } /* 不会生效 */
{% endstylesheet %}
```

### BEM命名规范

```
.block                      → 组件根：.product-card
.block__element             → 子元素：.product-card__title
.block--modifier            → 变体：.product-card--featured
.block__element--modifier   → 元素变体：.product-card__title--large
```

**规则：**
- 使用连字符分隔单词：`.product-card`，不要`.productCard`
- 单一元素级别：`.block__element`，不要`.block__el1__el2`
- 修饰符必须与基础类配对：`class="btn btn--primary"`，不要单独`class="btn--primary"`
- 当子元素可独立存在时，开始新的BEM作用域

```html
<!-- 正确：单一元素级别 -->
<div class="product-card">
  <h3 class="product-card__title">{{ product.title }}</h3>
  <span class="product-card__button-label">{{ 'add_to_cart' | t }}</span>
</div>

<!-- 正确：新的BEM作用域用于独立组件 -->
<div class="product-card">
  <button class="button button--primary">
    <span class="button__label">{{ 'add_to_cart' | t }}</span>
  </button>
</div>
```

### 特异性

- 尽可能使用 `0 1 0`（单个类）
- 复杂的父子级使用最大 `0 4 0`
- **永远**不要使用ID选择器
- **永远**不要使用`!important`（如果绝对必要，请注释原因）
- 避免元素选择器，使用类选择器

### CSS嵌套

```css
/* 正确：媒体查询在选择器内 */
.header {
  width: 100%;

  @media screen and (min-width: 750px) {
    width: auto;
  }
}

/* 正确：状态修饰符使用& */
.button {
  background: var(--color-primary);

  &:hover { background: var(--color-primary-hover); }
  &:focus-visible { outline: 2px solid var(--color-focus); }
  &[disabled] { opacity: 0.5; }
}

/* 正确：父级修饰符影响子元素（单级） */
.card--featured {
  .card__title { font-size: var(--font-size-xl); }
}

/* 错误：嵌套超过第一级 */
.parent {
  .child {
    .grandchild { } /* 太深 */
  }
}
```

### 设计令牌

使用CSS自定义属性表示所有值 — 永远不要硬编码颜色、间距或字体。定义一致的量表并在所有地方引用。

**示例量表**（根据主题需求调整）：

```css
:root {
  /* 间距 — 使用一致的量表 */
  --space-2xs: 0.5rem;    --space-xs: 0.75rem;   --space-sm: 1rem;
  --space-md: 1.5rem;     --space-lg: 2rem;       --space-xl: 3rem;

  /* 字体 — 相对单位 */
  --font-size-sm: 0.875rem;  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;  --font-size-xl: 1.25rem;  --font-size-2xl: 1.5rem;
}
```

**关键原则：**
- 使用`rem`表示间距和字体（尊重用户字体大小偏好）
- 语义化命名令牌：`--space-sm`，不要`--space-16`
- 在`:root`中定义全局令牌，在组件根上定义作用域令牌

### CSS变量作用域

**全局** — 在`:root`中定义主题级值
**组件级** — 在组件根上，命名空间化：

```css
/* 正确：命名空间化 */
.facets {
  --facets-padding: var(--space-md);
  --facets-z-index: 3;
}

/* 错误：通用名称可能冲突 */
.facets {
  --padding: var(--space-md);
  --z-index: 3;
}
```

**通过内联样式覆盖**用于部分/块设置：

```liquid
<section
  class="hero"
  style="
    --hero-bg: {{ section.settings.bg_color }};
    --hero-padding: {{ section.settings.padding }}px;
  "
>
```

### CSS属性顺序

1. **布局** — `position`，`display`，`flex-direction`，`grid-template-columns`
2. **盒模型** — `width`，`margin`，`padding`，`border`
3. **排版** — `font-family`，`font-size`，`line-height`，`color`
4. **视觉效果** — `background`，`opacity`，`border-radius`
5. **动画** — `transition`，`animation`

### 逻辑属性（支持RTL）

```css
/* 正确：逻辑属性 */
padding-inline: 2rem;
padding-block: 1rem;
margin-inline: auto;
border-inline-end: 1px solid var(--color-border);
text-align: start;
inset: 0;

/* 错误：物理属性 */
padding-left: 2rem;
text-align: left;
top: 0; right: 0; bottom: 0; left: 0;
```

### 防御性CSS

```css
.component {
  overflow-wrap: break-word;        /* 防止文本溢出 */
  min-width: 0;                     /* 允许flex项收缩 */
  max-width: 100%;                  /* 限制图片/媒体 */
  isolation: isolate;               /* 创建堆叠上下文 */
}

.image-container {
  aspect-ratio: 4 / 3;             /* 防止布局偏移 */
  background: var(--color-surface); /* 缺失图片的回退 */
}
```

### 现代CSS特性

```css
/* 容器查询用于响应式组件 */
.product-grid { container-type: inline-size; }
@container (min-width: 400px) {
  .product-card { grid-template-columns: 1fr 1fr; }
}

/* 流体间距 */
.section { padding: clamp(1rem, 4vw, 3rem); }

/* 内在尺寸 */
.content { width: min(100%, 800px); }
```

### 性能

- 仅动画`transform`和`opacity`（永远不要布局属性）
- 少量使用`will-change` — 动画后移除
- 使用`contain: content`进行隔离渲染
- 在移动端使用`dvh`代替`vh`

### 减少动画

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## Liquid主题中的JavaScript

### JavaScript存放位置

| 位置 | Liquid? | 用途 |
|------|---------|---------|
| `{% javascript %}` | 否 | 组件特定脚本（每个文件一个） |
| `assets/*.js` | 否 | 共享工具，Web组件 |

### Web组件模式

```javascript
class ProductCard extends HTMLElement {
  connectedCallback() {
    this.button = this.querySelector('[data-add-to-cart]');
    this.button?.addEventListener('click', this.#handleClick.bind(this));
  }

  disconnectedCallback() {
    // 清理事件监听器，中止控制器
  }

  async #handleClick(event) {
    event.preventDefault();
    this.button.disabled = true;

    try {
      const formData = new FormData();
      formData.append('id', this.dataset.variantId);
      formData.append('quantity', '1');

      const response = await fetch('/cart/add.js', {
        method: 'POST',
        body: formData
      });

      if (!response.ok) throw new Error('Failed');

      this.dispatchEvent(new CustomEvent('cart:item-added', {
        detail: await response.json(),
        bubbles: true
      }));
    } catch (error) {
      console.error('Add to cart error:', error);
    } finally {
      this.button.disabled = false;
    }
  }
}

customElements.define('product-card', ProductCard);
```

```liquid
<product-card data-variant-id="{{ product.selected_or_first_available_variant.id }}">
  <button data-add-to-cart>{{ 'products.add_to_cart' | t }}</button>
</product-card>
```

### JavaScript规则

| 规则 | 做 | 不要 |
|------|-----|-------|
| 循环 | `for (const item of items)` | `items.forEach()` |
| 异步 | `async`/`await` | `.then()`链 |
| 变量 | 默认`const` | `let`除非需要重新赋值 |
| 条件 | 早期返回 | 嵌套`if/else` |
| URL | `new URL()` + `URLSearchParams` | 字符串拼接 |
| 依赖 | 原生浏览器API | 外部库 |
| 私有方法 | `#methodName()` | `_methodName()` |
| 类型 | JSDoc `@typedef`，`@param`，`@returns` | 未定义 |

### Fetch的AbortController

```javascript
class DataLoader extends HTMLElement {
  #controller = null;

  async load(url) {
    this.#controller?.abort();
    this.#controller = new AbortController();

    try {
      const response = await fetch(url, { signal: this.#controller.signal });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (error.name !== 'AbortError') throw error;
      return null;
    }
  }

  disconnectedCallback() {
    this.#controller?.abort();
  }
}
```

### 组件通信

**父级→子级：** 调用公共方法
```javascript
this.querySelector('child-component')?.publicMethod(data);
```

**子级→父级：** 派发自定义事件
```javascript
this.dispatchEvent(new CustomEvent('child:action', {
  detail: { value },
  bubbles: true
}));
```

## HTML标准

### 首选原生元素

| 需求 | 使用 | 不使用 |
|------|-----|-----|
| 可展开 | `<details>/<summary>` | 带JS的自定义手风琴 |
| 对话框/模态框 | `<dialog>` | 自定义覆盖div |
| 提示/弹出 | `popover`属性 | 自定义定位div |
| 搜索表单 | `<search>` | `<div class="search">` |
| 表单结果 | `<output>` | `<span class="result">` |

### 渐进增强

```liquid
{%- comment -%} 无需JS即可工作 {%- endcomment -%}
<details class="accordion">
  <summary>{{ block.settings.heading }}</summary>
  <div class="accordion__content">
    {{ block.settings.content }}
  </div>
</details>

{%- comment -%} 带JS增强 {%- endcomment -%}
{% javascript %}
  // 可选：平滑动画，分析跟踪
{% endjavascript %}
```

### 图片

```liquid
{{ image | image_url: width: 800 | image_tag:
  loading: 'lazy',
  alt: image.alt | escape,
  width: image.width,
  height: image.height
}}
```

- 所有折叠后图片使用`loading="lazy"`
- 始终设置`width`和`height`以防止布局偏移
- 描述性`alt`文本；装饰性图片使用`alt=""`

## JSON模板和配置文件

主题模板（`templates/*.json`）、部分组（`sections/*.json`）和配置文件（`config/settings_data.json`）都是JSON。使用`jq`通过`bash`工具进行手术刀式编辑 — 它比基于字符串的查找替换更安全可靠，适用于结构化数据。

### 常见模式

```bash
# 在模板中添加部分
jq '.sections.new_section = {"type": "hero", "settings": {"heading": "Welcome"}}' templates/index.json > /tmp/out && mv /tmp/out templates/index.json

# 更新设置值
jq '.current.sections.header.settings.logo_width = 200' config/settings_data.json > /tmp/out && mv /tmp/out config/settings_data.json

# 重新排序部分
jq '.order += ["new_section"]' templates/index.json > /tmp/out && mv /tmp/out templates/index.json

# 删除部分
jq 'del(.sections.old_banner) | .order -= ["old_banner"]' templates/index.json > /tmp/out && mv /tmp/out templates/index.json

# 读取嵌套值
jq '.sections.header.settings' templates/index.json
```

**优先使用`jq`而不是`edit`修改任何`.json`文件** — 它验证结构，处理转义，并避免空白/格式问题。

## 参考

- [CSS模式和示例](references/css-patterns.md)
- [JavaScript模式和示例](references/javascript-patterns.md)
