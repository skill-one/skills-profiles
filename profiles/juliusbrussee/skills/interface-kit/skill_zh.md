# 接口套件：卓越界面的实现指南

> 如果在项目根目录存在 DESIGN.md 文件，其标记和规范将覆盖本技能中所有默认设置。本技能为不存在设计系统时提供合理的默认值，并提供适用于所有情况的实现指导。

> 欲深入了解任何部分，请参阅本技能 `references/` 目录中的参考文件。

---

## 1. 核心理念

品味是后天培养而非天生具备的。研究为什么优秀的界面感觉是正确的。解构你欣赏的应用程序——间距、时机、阴影的重量。从“不错”到“卓越”之间的差距是由用户能感受到但从未有意识地注意到的数百个微观决策累积而成的。

**细节会累积。** 单个圆角、单个缓动过渡、单个精心选择的阴影——单独看都不重要。它们一起成为“成千上万几乎听不到的声音和谐歌唱”。累积效应是区分匠艺与产出物的关键。

**美感是杠杆。** 光泽不是虚荣。良好的默认值、考量的排版和有意为之的动效是真正的差异化因素。用户信任那些感觉被精心呵护的界面。投资者会注意到。竞争对手难以轻易复制品味。

**意图重于强度。** 大胆的极简主义和精致的极简主义都有效——失败的是缺乏明确的观点。每个视觉决策都应追溯到一个明确的理念方向。如果你无法说明为什么做出某个选择，就重新考虑它。

**选择一个方向并精确执行。** 不要在风格之间犹豫。一个完全投入的 brutalist 页面永远比一个“包含所有元素”的页面表现更好。投入，然后完善。

**永远不要产出“AI烂大街”的审美风格。** 不要在白色背景上使用花哨的渐变。不要使用带有库存插图的通用英雄区域。不要使用安全、易忘的布局，任何产品都可能使用。每个界面都应有独特的观点使其易于识别。

---

## 2. 优先级堆栈

在实现 UI 时，按顺序处理这些优先级。高优先级是不可协商的；低优先级是累积质量的润色。

| 优先级 | 级别 | 含义 |
|--------|------|------|
| **可访问性** | 关键 | 对比度 4.5:1，键盘导航，ARIA 语义，可见焦点环。不要发布任何排除用户的内容。 |
| **性能** | 高 | WebP/AVIF 图片，折叠区域以下的懒加载，CLS < 0.1，合成器线程上的纯变换动画。 |
| **排版** | 高 | 字体平滑，文本换行平衡/美观，数据使用 tabular-nums，最大行长 65ch。 |
| **布局与空间** | 高 | 4/8px 网格，同心边框半径，光学对齐优先于几何对齐。 |
| **颜色与主题** | 中 | HSL 自定义属性，语义标记，单独测试暗黑模式配对。 |
| **动效与交互** | 中 | 基于频率的动画决策，150-300ms 持续时间，默认 ease-out。 |
| **润色与细节** | 低 | 边框上的分层阴影，按钮上的按压力反馈，交错进入动画。 |

永远不要为了追求低优先级而跳过关键/高优先级项。一个动画精美的按钮但无法进行键盘导航，会带来负面影响。

---

## 3. 审美方向

在编写任何 CSS 代码之前，坚定选择一个大胆的审美方向。AI 生成的 UI 最常见的失败模式是收敛于相同的安全、易忘的样式。

### 选择基调

选择一个并完全投入：

- **残酷极简**——充足的空白，等宽字体，鲜明的对比度，几乎零装饰
- **极繁混沌**——分层纹理，冲突的字体比例，密集的信息，有意为之的视觉噪音
- **复古未来**——CRT 发光效果，等宽终端，扫描线，暗黑背景上的霓虹灯
- **有机/自然**——大地色调，圆润形状，纸张纹理，手绘装饰
- **奢华/精致**——衬线标题，柔和调色板，充足的负空间，微妙的金色或奶油色点缀
- **编辑/杂志**——戏剧性层级，满版图片，打破网格的布局
- **俏皮/大胆**——明亮原色，粗犷边框，夸张阴影，弹跳动效

### 根据愿景匹配复杂度

极繁设计需要复杂的代码——分层背景，复杂的网格结构，多个字体堆栈。极简设计需要手术般的精确——当没有需要隐藏的内容时，每个像素的间距都更加重要。

### 禁用清单（当不存在 DESIGN.md 时）

在没有现有设计系统的情况下构建时，避免使用这些过时的默认值，这些默认值表明是“AI 生成”的：

- **字体**：Inter, Roboto, Arial, system-ui 作为显示字体，Space Grotesk
- **颜色**：白色背景上的紫色到蓝色渐变
- **模式**：居中文本 + CTA + 库存插图的通用英雄区域

在浅色和暗黑主题之间变化，使用不同的字体配对，选择不同的审美方向。永远不要在项目之间收敛于相同的选项。

### 视觉纹理

通过：渐变网格，噪声/颗粒叠加（`filter: url(#noise)`），分层透明度，微妙的背景图案，双色调图片处理添加深度。

**DESIGN.md 覆盖本节所有内容。** 如果 DESIGN.md 指定 Inter，则使用 Inter。如果它指定紫色渐变，则使用它们。禁用清单仅适用于不存在设计系统且你正在从头开始做审美选择时。

---

## 4. 排版要点

排版是单一最高杠杆的设计元素。正确设置，即使平庸的布局仍然感觉良好。设置错误，其他任何东西都无法挽救。

### 根设置

```css
html {
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-rendering: optimizeLegibility;
}
```

在根布局中应用字体平滑。在 macOS 上，默认的子像素渲染使文本看起来比设计师预期的更重。

### 文本换行

```css
h1, h2, h3, h4, h5, h6 {
  text-wrap: balance;
}

p, li, dd, blockquote {
  text-wrap: pretty;
}
```

`balance` 将标题行均匀分布。`pretty` 避免正文文本中的孤零词。

### 数字显示

```css
.data-value, .price, .counter, [data-numeric] {
  font-variant-numeric: tabular-nums;
}
```

对于任何动态更新的数字——价格、计数器、表格列——使用 `tabular-nums`。没有它，布局会在数字宽度变化时发生偏移。

### 尺寸与节奏

- **基础尺寸**：正文文本的最小尺寸为 16px。正文内容的任何可读内容都不要低于 14px。
- **行高**：正文文本 1.5-1.75，大标题 1.1-1.3。
- **最大行长**：正文文本 `max-width: 65ch`。长行会破坏可读性。
- **字体尺寸**：选择一个一致的尺寸并坚持使用：12 / 14 / 16 / 18 / 24 / 32 / 48 / 64。

### 字体配对

将一个具有个性的显示字体与一个精致的正文字体配对。显示字体承载个性；正文字体承载可读性。在家族内部使用 `font-weight` 进行层级：

- **标题**：600-700（半粗到粗）
- **正文**：400（常规）
- **标签/UI**：500（中等）

始终包含字体堆栈回退：

```css
--font-display: "Instrument Serif", "Georgia", serif;
--font-body: "Söhne", "Helvetica Neue", sans-serif;
--font-mono: "JetBrains Mono", "Fira Code", monospace;
```

---

## 5. 颜色与主题

### HSL 自定义属性（shadcn 模式）

```css
:root {
  --background: 0 0% 100%;
  --foreground: 222.2 84% 4.9%;
  --primary: 222.2 47.4% 11.2%;
  --primary-foreground: 210 40% 98%;
  --secondary: 210 40% 96.1%;
  --secondary-foreground: 222.2 47.4% 11.2%;
  --muted: 210 40% 96.1%;
  --muted-foreground: 215.4 16.3% 46.9%;
  --accent: 210 40% 96.1%;
  --accent-foreground: 222.2 47.4% 11.2%;
  --destructive: 0 84.2% 60.2%;
  --destructive-foreground: 210 40% 98%;
  --border: 214.3 31.8% 91.4%;
  --ring: 222.2 84% 4.9%;
  --radius: 0.5rem;
}
```

定义语义标记：主要、次要、破坏性、减弱、强调、背景、前景。通过语义名称引用颜色——组件中永远不要硬编码十六进制值。

### 暗黑模式

```css
.dark {
  --background: 222.2 84% 4.9%;
  --foreground: 210 40% 98%;
  /* ... 灰度、更浅的色调变体——不是简单反转 ... */
}
```

暗黑模式不是“反转颜色”。使用灰度、更浅的色调变体。背景变暗但不是纯黑（`#000`）。文本变亮但不是纯白（`#fff`）。单独测试暗黑模式的对比度——在浅色模式下通过的内容可能在暗色模式下失败。

### 对比度要求

- **WCAG AA 最小值**：正常文本 4.5:1，大文本（18px+ 粗体或 24px+ 常规）3:1
- 永远不要仅通过颜色传递信息——始终与图标、标签或图案配对
- 使用浏览器开发者工具对比度检查器或 axe-core 进行测试

### 颜色信心

主导颜色与锐利强调优于胆怯、均匀分布的调色板。选择一到两个英雄颜色，让其余的调色板退居其次。自信的调色板具有清晰的层级；不确定的调色板会均匀分布颜色并感觉扁平。

---

## 6. 空间设计

### 同心边框半径

这是使嵌套 UI 元素感觉“不对劲”的最常见原因：

```
outer_radius = inner_radius + padding
```

```css
/* 正确：同心 */
.card        { border-radius: 16px; padding: 8px; }
.card-inner  { border-radius: 8px; }  /* 16 - 8 = 8 */

/* 错误：父级和子级使用相同半径 */
.card        { border-radius: 12px; }
.card-inner  { border-radius: 12px; }  /* 看起来臃肿 */
```

当几何中心对齐看起来不对时，进行光学对齐。播放/暂停图标、下拉箭头、非对称符号通常需要 1-2px 的手动调整才能看起来居中。

### 阴影覆盖边框

使用多个透明的 `box-shadow` 值创建自然深度，而不是使用边框：

```css
.elevated {
  box-shadow:
    0 1px 2px rgba(0, 0, 0, 0.04),
    0 2px 4px rgba(0, 0, 0, 0.04),
    0 4px 8px rgba(0, 0, 0, 0.04);
}
```

不同扩散距离的多个阴影模拟光线的运作方式。单一硬阴影看起来不自然。

### 图片轮廓

为图片和媒体添加微妙的内嵌轮廓，以在多种背景下保持一致深度：

```css
img, video {
  outline: 1px solid rgba(0, 0, 0, 0.06);
  outline-offset: -1px;
}
```

### 间距尺度

使用 4px / 8px 基础增量系统。每个间距值应该是 4 的倍数：

`4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 / 128`

### 点击区域

所有交互元素的最小 44x44px。如果视觉元素较小，使用伪元素扩展点击区域：

```css
.small-button::before {
  content: "";
  position: absolute;
  inset: -8px;
}
```

### Z-索引尺度

定义一个分层尺度，永远不要使用任意值：

```css
--z-base: 0;
--z-dropdown: 10;
--z-sticky: 20;
--z-overlay: 40;
--z-modal: 100;
--z-toast: 1000;
```

---

## 7. 动效与交互

### 基于频率的决策框架

这是动画决策最重要的心智模型：

| 频率 | 示例 | 动画 |
|------|------|------|
| **每天 100+ 次** | 键盘快捷键，命令面板操作，选项卡切换 | **无。** 零动画。即时。 |
| **每天几十次** | 悬停效果，列表项导航，切换器 | **移除或大幅减少。** 最大 50-100ms。 |
| **偶尔** | 模态框，抽屉，提示，页面过渡 | **标准动画。** 150-300ms。 |
| **罕见/首次** | 欢迎教程，庆祝，空状态 | **可以增加乐趣。** 300-500ms，更复杂。 |

高频动画感觉迟缓。低频动画无动效会感觉突兀。根据使用频率匹配动画预算。

### 自定义缓动曲线

内置 CSS 缓动（`ease`，`ease-in-out`）太弱。定义自定义曲线：

```css
:root {
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
  --ease-in-out: cubic-bezier(0.77, 0, 0.175, 1);
  --ease-drawer: cubic-bezier(0.32, 0.72, 0, 1);
  --ease-spring: cubic-bezier(0.34, 1.56, 0.64, 1);
}
```

### 持续时间指南

| 元素 | 持续时间 |
|------|----------|
| 按钮，切换器 | 100-160ms |
| 提示 | 125-200ms |
| 下拉菜单，弹出框 | 150-250ms |
| 模态框，抽屉 | 200-500ms |
| 页面过渡 | 250-400ms |

UI 动画应保持在 300ms 以下。永远不要使用 `ease-in` 进行 UI 动画——它会导致暂停前置加载，感觉迟缓。

### 进入/退出非对称性

退出应比进入更柔和、更快。250ms 的进入动画，其退出应在 150-200ms。

### 分裂和交错进入动画

当多个元素进入视口时，按语义块交错它们，延迟约 50-100ms：

```css
.stagger-item {
  animation: fadeSlideIn 300ms var(--ease-out) both;
}
.stagger-item:nth-child(1) { animation-delay: 0ms; }
.stagger-item:nth-child(2) { animation-delay: 60ms; }
.stagger-item:nth-child(3) { animation-delay: 120ms; }
```

### 缩放动画

永远不要从 `scale(0)` 开始。从 `scale(0.9)` 或更高开始，结合不透明度：

```css
@keyframes scaleIn {
  from { opacity: 0; transform: scale(0.95); }
  to   { opacity: 1; transform: scale(1); }
}
```

### 按压力反馈

每个可按元素在 `:active` 上应稍微缩小：

```css
button:active {
  transform: scale(0.97);
}
```

### 可中断性

使用 CSS 过渡（而不是关键帧动画）进行交互状态变化。过渡可以在中途中断；关键帧不能。这对悬停状态、切换器以及用户可能快速交互的任何元素都很重要。

### 弹出框原点

使弹出框感知 `transform-origin`——它们应从触发元素生长，而不是从中心生长。例外：模态框始终从中心原点开始。

### 提示悬停延迟

在后续悬停时跳过提示延迟。如果用户已经等待了一个提示，立即显示下一个提示。

### 减少动效

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

尊重 `prefers-reduced-motion`。减少动画——不要完全消除不透明度和颜色过渡，因为它们提供重要的反馈。

### 悬停门

在媒体查询后门悬停动画，以避免触摸设备触发卡住的悬停状态：

```css
@media (hover: hover) and (pointer: fine) {
  .card:hover { transform: translateY(-2px); }
}
```

> 深入了解弹簧物理、手势驱动动画和复杂编排，请参考 `references/animation-playbook.md`。

---

## 8. 组件工艺

### 基础组件

使用 Radix UI 基础组件，用于可访问性、无样式化基础。使用 CVA（类变体权威）进行类型安全的组件变体：

```tsx
import { cva } from "class-variance-authority";

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        default: "h-10 px-4 py-2",
        lg: "h-11 px-8 text-lg",
      },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);
```

### 按钮

- 按下时缩放（`transform: scale(0.97)` on `:active`）
- 可见焦点环（永远不要 `outline: none` 而没有替代方案）
- 加载状态：使用替换标签的旋转器，保持按钮尺寸
- 禁用状态：`opacity: 0.5`，`pointer-events: none`

### 卡片

- 卡片与内部元素之间的同心边框半径
- 分层阴影（不是边框）用于深度
- 悬停状态：轻微提升变化（`translateY(-1px)` + 阴影增加）

### 对话框/模态框

- 焦点陷阱（键盘无法跳转到后面的元素）
- ESC 关闭，点击遮罩层关闭
- `transform-origin: center`，淡入+缩放进入动画
- `aria-modal="true"`，`role="dialog"`，`aria-labelledby`

### 表单

- 始终显示标签——永远不要仅使用占位符的输入
- 错误消息靠近字段，使用 `aria-live="polite"` 为屏幕阅读器提供
- 逐步显示：仅在需要时显示高级字段
- 使用 React Hook Form + Zod 进行验证

### 主题

使用 shadcn CSS 变量模式（HSL 格式）为所有组件颜色。将客户端交互组件包装在服务器组件中，以兼容 Next.js App Router。

> 参考 `references/component-patterns.md` 获取完整的组件目录，包含可复制粘贴的实现。

---

## 9. 可访问性要点

### 语义 HTML 优先

在使用 `<button>`、`<nav>`、`<main>`、`<header>`、`<footer>`、`<article>`、`<section>` 之前，再考虑 ARIA。`<button>` 免费提供键盘处理、焦点管理和屏幕阅读器语义。`<div onClick>` 则提供这些功能中的任何一项。

### 键盘导航

- **Tab / Shift+Tab**：在可聚焦元素之间移动
- **Enter / Space**：激活按钮和链接
- **箭头键**：在列表、菜单、选项卡、单选组内导航
- **Escape**：关闭模态框、弹出框、下拉菜单
- **Home / End**：跳转到列表的第一/最后一个项目

### 焦点管理

- 所有交互元素都有可见焦点环——永远不要在未提供替代方案的情况下使用 `outline: none`
- 在模态框内锁定焦点（Tab 在模态框内循环，而不是在它后面）
- 模态框/弹出框关闭时，将焦点恢复到触发元素
- 使用 `focus-visible` 仅对键盘用户显示环，而不是鼠标点击：

```css
:focus-visible {
  outline: 2px solid var(--ring);
  outline-offset: 2px;
}
```

### ARIA 属性

- `aria-label` 用于仅包含图标的按钮：`<button aria-label="关闭菜单">X</button>`
- `aria-labelledby` 将标题与区域关联
- `aria-describedby` 将帮助文本或错误消息链接到输入
- `aria-live="polite"` 用于动态内容更新（提示消息、表单错误）
- `aria-hidden="true"` 用于装饰性元素（文本标签旁边的图标）
- `aria-expanded` 用于可切换元素（下拉菜单、手风琴）

### 颜色和对比度

- WCAG AA 最小值：正常文本 4.5:1，大文本（18px+ 粗体或 24px+ 常规）3:1
- 永远不要仅通过颜色传递信息——始终与图标、文本或图案配对
- 在浅色和暗黑模式下测试

### 图片和媒体

- 有意义的图片使用描述性 `alt` 文本：`alt="显示 23% 收入增长的仪表板"`
- 纯粹装饰性图片使用 `alt=""`
- 视频使用字幕，音频使用文本记录

### 导航辅助

- **跳过链接**：第一个可聚焦元素，聚焦前隐藏：

```html
<a href="#main-content" class="sr-only focus:not-sr-only">
  跳转到主要内容
</a>
```

- **标题层级**：顺序 h1 通过 h6，无级别跳过。每页一个 `<h1>`。

### 触摸目标

- 最小 44x44px 交互区域
- 相邻触摸目标之间最小 8px 间距
- 使用不可见的填充或伪元素扩展小视觉元素

### 测试

- **自动化**：CI 中的 axe-core，Lighthouse 可访问性评分 90+
- **手动**：完整的仅键盘导航测试
- **屏幕阅读器**：使用 VoiceOver（macOS）或 NVDA（Windows）进行测试
- **视觉**：放大到 200%，检查没有破坏或重叠

> 参考 `references/accessibility-checklist.md` 获取完整的审计指南，包含通过/失败标准。

---

## 10. 交付前审查

在考虑任何 UI 实现完成之前，运行此清单：

### 排版
- [ ] 应用字体平滑 (`-webkit-font-smoothing: antialiased`)
- [ ] 标题使用 `text-wrap: balance`
- [ ] 动态数字使用 `font-variant-numeric: tabular-nums`

### 颜色
- [ ] 所有颜色通过语义标记引用，组件中不要硬编码十六进制值
- [ ] 对比度满足 WCAG AA（正常文本 4.5:1，大文本 3:1）
- [ ] 暗黑模式单独测试对比度

### 空间
- [ ] 嵌套圆角元素使用同心边框半径
- [ ] 间距遵循 4px / 8px 尺度一致
- [ ] 交互元素具有 44x44px 最小点击区域
- [ ] 适当使用阴影而不是边框

### 动效
- [ ] 动画频率匹配使用频率（高频操作没有动画）
- [ ] 始终使用特定属性，而不是 `transition: all`
- [ ] 多个元素进入视口时，分割和交错进入动画
- [ ] `prefers-reduced-motion` 受尊重

### 可访问性
- [ ] 所有交互元素可通过键盘访问
- [ ] 键盘导航时焦点环可见（永远不要 `outline: none` 而没有替代方案）
- [ ] 使用语义 HTML 优先于 ARIA
- [ ] 动态内容更新使用 `aria-live="polite"`

> 参考 `references/review-checklist.md` 获取扩展的 30 项清单，包含严重性评级和自动化测试命令。
