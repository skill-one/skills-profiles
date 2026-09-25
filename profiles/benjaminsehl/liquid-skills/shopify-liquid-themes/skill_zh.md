# Shopify 主题 Liquid

## 主题架构

```
.
├── sections/    # 全宽页面模块，使用 {% schema %} — 英雄模块、产品网格、客户评价
├── blocks/      # 可嵌套组件，使用 {% schema %} — 幻灯片、功能项、文本块
├── snippets/    # 可重用片段，使用 {% render %} — 按钮、图标、图片辅助工具
├── layout/      # 页面包装器 (必须包含 {{ content_for_header }} 和 {{ content_for_layout }})
├── templates/   # 定义每种页面类型显示哪些片段的 JSON 文件
├── config/      # 全局主题设置 (settings_schema.json, settings_data.json)
├── locales/     # 翻译文件 (en.default.json, fr.json, 等)
└── assets/      # 静态 CSS、JS、图片 (优先使用 {% stylesheet %}/{% javascript %} 而不是)
```

### 何时使用什么

| 需求 | 使用 | 原因 |
|------|-----|-----|
| 全宽可定制模块 | **片段** | 有 `{% schema %}`，出现在编辑器中，渲染块 |
| 小型可嵌套组件，带编辑器设置 | **块** | 有 `{% schema %}`，可以嵌套在片段/块内 |
| 可重用逻辑，商家不可编辑 | **片段** | 无 schema，通过 `{% render %}` 渲染，可接收参数 |
| 跨块/片段共享的逻辑 | **片段** | 块不能 `{% render %}` 其他块 |

## Liquid 语法

### 分隔符

- `{{ ... }}` — 输出 (打印值)
- `{{- ... -}}` — 输出，去除空白
- `{% ... %}` — 逻辑标签 (if, for, assign) — 不打印任何内容
- `{%- ... -%}` — 逻辑标签，去除空白

### 运算符

**比较:** `==`, `!=`, `>`, `<`, `>=`, `<=`
**逻辑:** `and`, `or`, `contains`

### 关键注意事项

1. **条件中无括号** — 使用嵌套 `{% if %}` 代替
2. **无三元运算符** — 始终使用 `{% if cond %}value{% else %}other{% endif %}`
3. **`for` 循环最大 50 次迭代** — 大数组使用 `{% paginate %}`
4. **`contains` 仅适用于字符串** — 不能检查数组中的对象
5. **`{% stylesheet %}`/`{% javascript %}` 不渲染 Liquid** — 这些标签内不能有 Liquid
6. **片段不能访问外部作用域变量** — 通过 render 参数传递
7. **`include` 已弃用** — 始终使用 `{% render 'snippet_name' %}`
8. **`{% liquid %}` 标签** — 多行逻辑，无分隔符；输出使用 `echo`

### 变量

```liquid
{% assign my_var = 'value' %}
{% capture my_var %}computed {{ value }}{% endcapture %}
{% increment counter %}
{% decrement counter %}
```

## 过滤器快速参考

过滤器使用 `|` 链接。一个过滤器的输出类型作为下一个过滤器的输入。

**数组:** `compact`, `concat`, `find`, `find_index`, `first`, `has`, `join`, `last`, `map`, `reject`, `reverse`, `size`, `sort`, `sort_natural`, `sum`, `uniq`, `where`
**字符串:** `append`, `capitalize`, `downcase`, `escape`, `handleize`, `lstrip`, `newline_to_br`, `prepend`, `remove`, `replace`, `rstrip`, `slice`, `split`, `strip`, `strip_html`, `truncate`, `truncatewords`, `upcase`, `url_decode`, `url_encode`
**数学:** `abs`, `at_least`, `at_most`, `ceil`, `divided_by`, `floor`, `minus`, `modulo`, `plus`, `round`, `times`
**货币:** `money`, `money_with_currency`, `money_without_currency`, `money_without_trailing_zeros`
**颜色:** `color_brightness`, `color_darken`, `color_lighten`, `color_mix`, `color_modify`, `color_saturate`, `color_desaturate`, `color_to_hex`, `color_to_hsl`, `color_to_rgb`
**媒体:** `image_url`, `image_tag`, `video_tag`, `external_video_tag`, `media_tag`, `model_viewer_tag`
**URL:** `asset_url`, `asset_img_url`, `file_url`, `shopify_asset_url`
**HTML:** `link_to`, `script_tag`, `stylesheet_tag`, `time_tag`, `placeholder_svg_tag`
**本地化:** `t` (翻译), `format_address`, `currency_selector`
**其他:** `date`, `default`, `json`, `structured_data`, `font_face`, `font_url`, `payment_button`

> 详细信息：[语言过滤器](references/filters-language.md), [HTML/媒体过滤器](references/filters-html-media.md), [商业过滤器](references/filters-commerce.md)

## 标签快速参考

| 分类 | 标签 |
|------|------|
| **主题** | `content_for`, `layout`, `section`, `sections`, `schema`, `stylesheet`, `javascript`, `style` |
| **控制** | `if`, `elsif`, `else`, `unless`, `case`, `when` |
| **迭代** | `for`, `break`, `continue`, `cycle`, `tablerow`, `paginate` |
| **变量** | `assign`, `capture`, `increment`, `decrement`, `echo` |
| **HTML** | `form`, `render`, `raw`, `comment`, `liquid` |
| **文档** | `doc` |

> 详细信息及语法和参数：[标签参考](references/tags.md)

## 对象快速参考

### 全局对象 (任何地方可用)

`cart`, `collections`, `customer`, `localization`, `pages`, `request`, `routes`, `settings`, `shop`, `template`, `theme`, `linklists`, `images`, `blogs`, `articles`, `all_products`, `metaobjects`, `canonical_url`, `content_for_header`, `content_for_layout`, `page_title`, `page_description`, `handle`, `current_page`

### 页面特定对象

| 模板 | 对象 |
|------|------|
| `/product` | `product`, `remote_product` |
| `/collection` | `collection`, `current_tags` |
| `/cart` | `cart` |
| `/article` | `article`, `blog` |
| `/blog` | `blog`, `current_tags` |
| `/page` | `page` |
| `/search` | `search` |
| `/customers/*` | `customer`, `order` |

> 完整参考：[商业对象](references/objects-commerce.md), [内容对象](references/objects-content.md), [二级](references/objects-tier2.md), [三级](references/objects-tier3.md)

## Schema 标签

片段和块需要 `{% schema %}`，包含有效的 JSON 对象。片段使用 `section.settings.*`，块使用 `block.settings.*`。

### 片段 schema 结构

```json
{
  "name": "t:sections.hero.name",
  "tag": "section",
  "class": "hero-section",
  "limit": 1,
  "settings": [],
  "max_blocks": 16,
  "blocks": [{ "type": "@theme" }],
  "presets": [{ "name": "t:sections.hero.name" }],
  "enabled_on": { "templates": ["index"] },
  "disabled_on": { "templates": ["password"] }
}
```

### 块 schema 结构

```json
{
  "name": "t:blocks.slide.name",
  "tag": "div",
  "class": "slide",
  "settings": [],
  "blocks": [{ "type": "@theme" }],
  "presets": [{ "name": "t:blocks.slide.name" }]
}
```

### 设置类型决策表

| 需求 | 设置类型 | 关键字段 |
|------|----------|----------|
| 开关切换 | `checkbox` | `default: true/false` |
| 短文本 | `text` | `placeholder` |
| 长文本 | `textarea` | `placeholder` |
| 富文本 (带 `<p>`) | `richtext` | — |
| 内联富文本 (无 `<p>`) | `inline_richtext` | — |
| 数字输入 | `number` | `placeholder` |
| 滑块 | `range` | `min`, `max`, `default` (全部必需), `step`, `unit` |
| 下拉/分段 | `select` | `options: [{value, label}]` |
| 单选按钮 | `radio` | `options: [{value, label}]` |
| 文本对齐 | `text_alignment` | `default: "left"/"center"/"right"` |
| 颜色选择器 | `color` | `default: "#000000"` |
| 图片上传 | `image_picker` | — |
| 视频上传 | `video` | — |
| 外部视频 URL | `video_url` | `accept: ["youtube", "vimeo"]` |
| 产品选择器 | `product` | — |
| 分类选择器 | `collection` | — |
| 页面选择器 | `page` | — |
| 博客选择器 | `blog` | — |
| 文章选择器 | `article` | — |
| URL 输入 | `url` | — |
| 菜单选择器 | `link_list` | — |
| 字体选择器 | `font_picker` | `default` (必需) |
| 编辑器标题 | `header` | `content` (无需 `id`) |
| 编辑器描述 | `paragraph` | `content` (无需 `id`) |

### `visible_if` 模式

```json
{
  "visible_if": "{{ block.settings.layout == 'vertical' }}",
  "type": "select",
  "id": "alignment",
  "label": "t:labels.alignment",
  "options": [...]
}
```

根据其他设置值有条件地显示/隐藏编辑器中的设置。

### 块入口类型

- `{ "type": "@theme" }` — 接受任何主题块
- `{ "type": "@app" }` — 接受应用块
- `{ "type": "slide" }` — 仅接受 `slide` 块类型

> 完整 schema 详细信息和所有 33 种设置类型：[schema 和设置参考](references/schema-and-settings.md)

## CSS & JavaScript

### 组件级样式和脚本

在片段、块和片段中使用 `{% stylesheet %}` 和 `{% javascript %}`：

```liquid
{% stylesheet %}
  .my-component { display: flex; }
{% endstylesheet %}

{% javascript %}
  console.log('loaded');
{% endjavascript %}
```

- **每个文件一个标签** — 多个 `{% stylesheet %}` 标签会导致错误
- **标签内无 Liquid** — 这些标签不处理 Liquid；使用 CSS 变量或类代替
- 仅支持在 `sections/`, `blocks/`, 和 `snippets/` 中

### `{% style %}` 标签 (带 Liquid 的 CSS)

用于需要 Liquid 的动态 CSS (例如，在编辑器中实时更新的颜色设置)：

```liquid
{% style %}
  .section-{{ section.id }} {
    background: {{ section.settings.bg_color }};
  }
{% endstyle %}
```

### 设置的 CSS 模式

**单个 CSS 属性** — 使用 CSS 变量：
```liquid
<div style="--gap: {{ block.settings.gap }}px">
```

**多个 CSS 属性** — 使用 CSS 类作为选择值：
```liquid
<div class="{{ block.settings.layout }}">
```

## LiquidDoc (`{% doc %}`)

**必需用于:** 片段 (始终)，块 (当通过 `{% content_for 'block' %}` 静态渲染时)

```liquid
{% doc %}
  简要描述此文件渲染的内容。

  @param {type} name - 必需参数的描述
  @param {type} [name] - 可选参数的描述 (括号 = 可选)

  @example
  {% render 'snippet-name', name: value %}
{% enddoc %}
```

**参数类型:** `string`, `number`, `boolean`, `image`, `object`, `array`

## 翻译

### 所有用户界面字符串必须使用 `t` 过滤器

```liquid
<!-- 正确 -->
<h2>{{ 'sections.hero.heading' | t }}</h2>
<button>{{ 'products.add_to_cart' | t }}</button>

<!-- 错误 — 永远不要硬编码字符串 -->
<h2>Welcome to our store</h2>
```

### 变量插值

```liquid
{{ 'products.price_range' | t: min: product.price_min | money, max: product.price_max | money }}
```

本地化文件：
```json
{
  "products": {
    "price_range": "From {{ min }} to {{ max }}"
  }
}
```

### 本地化文件结构

```
locales/
├── en.default.json          # 英文翻译 (必需)
├── en.default.schema.json   # 编辑器设置翻译 (必需)
├── fr.json                  # 法文翻译
└── fr.schema.json           # 法文编辑器翻译
```

### 键命名约定

- 使用 **snake_case** 和 **分层键** (最多 3 级)
- 使用 **句子大小写** (仅首字母大写)
- Schema 标签使用 `t:` 前缀：`"label": "t:labels.heading"`
- 按组件分组：`sections.hero.heading`, `blocks.slide.title`

## 参考

- 过滤器：[语言](references/filters-language.md) (77), [HTML/媒体](references/filters-html-media.md) (45), [商业](references/filters-commerce.md) (30)
- [标签参考 (30 个标签)](references/tags.md)
- 对象：[商业](references/objects-commerce.md) (5), [内容](references/objects-content.md) (10), [二级](references/objects-tier2.md) (69), [三级](references/objects-tier3.md) (53)
- [Schema & 设置参考 (33 种类型)](references/schema-and-settings.md)
- [完整示例 (片段、块、片段)](references/examples.md)
