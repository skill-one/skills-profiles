# Tailwind CSS

> 该技能基于 Tailwind CSS v4.1.18 版本，生成于 2026-01-28。

Tailwind CSS 是一个以工具类优先的 CSS 框架，用于快速构建自定义用户界面。您无需编写自定义 CSS，而是直接在您的标记中使用工具类来组合设计。Tailwind v4 引入了 CSS 优先配置和主题变量，使自定义设计系统更加容易。

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| 安装 | Vite、PostCSS、CLI 和 CDN 设置 | [core-installation](references/core-installation.md) |
| 工具类 | 理解 Tailwind 的工具类优先方法以及元素样式 | [core-utility-classes](references/core-utility-classes.md) |
| 主题变量 | 设计令牌、自定义主题和主题变量命名空间 | [core-theme](references/core-theme.md) |
| 响应式设计 | 移动优先断点、响应式变体和容器查询 | [core-responsive](references/core-responsive.md) |
| 变体 | 使用状态、伪类和媒体查询变体条件性地应用工具类 | [core-variants](references/core-variants.md) |
| 预设样式 | Tailwind 的基础样式以及如何扩展或禁用它们 | [core-preflight](references/core-preflight.md) |

## 布局

### 显示 & Flexbox & Grid

| 主题 | 描述 | 参考 |
|------|------|------|
| 显示 | flex、grid、block、inline、hidden、sr-only、flow-root、contents | [layout-display](references/layout-display.md) |
| Flexbox | flex-direction、justify、items、gap、grow、shrink、wrap、order | [layout-flexbox](references/layout-flexbox.md) |
| Grid | grid-cols、grid-rows、gap、place-items、col-span、row-span、subgrid | [layout-grid](references/layout-grid.md) |
| 宽高比 | 控制元素的宽高比以适应响应式媒体 | [layout-aspect-ratio](references/layout-aspect-ratio.md) |
| 列 | 多列布局，适用于杂志风格或马赛克布局 | [layout-columns](references/layout-columns.md) |

### 定位

| 主题 | 描述 | 参考 |
|------|------|------|
| 定位 | 使用 static、relative、absolute、fixed 和 sticky 控制元素定位 | [layout-position](references/layout-position.md) |
| 插入值 | 使用 top、right、bottom、left 和 inset 工具类控制定位元素的放置 | [layout-inset](references/layout-inset.md) |

### 尺寸

| 主题 | 描述 | 参考 |
|------|------|------|
| 宽度 | 使用间距比例、分数、容器尺寸和视口单位设置元素宽度 | [layout-width](references/layout-width.md) |
| 高度 | 使用间距比例、分数、视口单位和基于内容的尺寸设置元素高度 | [layout-height](references/layout-height.md) |
| 最小 & 最大尺寸 | min-width、max-width、min-height、max-height 约束 | [layout-min-max-sizing](references/layout-min-max-sizing.md) |

### 间距

| 主题 | 描述 | 参考 |
|------|------|------|
| 外边距 | 使用间距比例、负值、逻辑属性和空间工具类控制元素外边距 | [layout-margin](references/layout-margin.md) |
| 内边距 | 使用间距比例、逻辑属性和方向工具类控制元素内边距 | [layout-padding](references/layout-padding.md) |

### 溢出

| 主题 | 描述 | 参考 |
|------|------|------|
| 溢出 | 控制元素如何处理超出其容器的内容 | [layout-overflow](references/layout-overflow.md) |

### 图片 & 替换元素

| 主题 | 描述 | 参考 |
|------|------|------|
| 对象拟合 & 定位 | 控制图片和视频的缩放和定位方式 | [layout-object-fit-position](references/layout-object-fit-position.md) |

### 表格

| 主题 | 描述 | 参考 |
|------|------|------|
| 表格布局 | border-collapse、table-auto、table-fixed | [layout-tables](references/layout-tables.md) |

## 变换

| 主题 | 描述 | 参考 |
|------|------|------|
| 变换基础 | 启用变换、硬件加速和自定义变换值的基变换工具类 | [transform-base](references/transform-base.md) |
| 平移 | 在 x、y 和 z 轴上平移元素，使用间距比例、百分比和自定义值 | [transform-translate](references/transform-translate.md) |
| 旋转 | 在 2D 和 3D 空间中旋转元素，使用度值和自定义旋转 | [transform-rotate](references/transform-rotate.md) |
| 缩放 | 均匀或特定轴缩放元素，使用百分比值 | [transform-scale](references/transform-scale.md) |
| 倾斜 | 在 x 和 y 轴上倾斜元素，使用度值 | [transform-skew](references/transform-skew.md) |

## 字体排版

| 主题 | 描述 | 参考 |
|------|------|------|
| 字体 & 文本 | 字体大小、权重、颜色、行高、字间距、装饰、截断 | [typography-font-text](references/typography-font-text.md) |
| 文本对齐 | 使用 left、center、right、justify 和逻辑属性控制文本对齐 | [typography-text-align](references/typography-text-align.md) |
| 列表样式 | list-style-type、list-style-position 用于项目符号和标记 | [typography-list-style](references/typography-list-style.md) |

## 视觉效果

| 主题 | 描述 | 参考 |
|------|------|------|
| 背景 | 背景颜色、渐变、图片、大小、位置 | [visual-background](references/visual-background.md) |
| 边框 | 边框宽度、颜色、半径、分割、环 | [visual-border](references/visual-border.md) |
| 效果 | 盒阴影、不透明度、混合模式、背景模糊、滤镜 | [visual-effects](references/visual-effects.md) |
| SVG | fill、stroke、stroke-width 用于 SVG 和图标样式 | [visual-svg](references/visual-svg.md) |

## 效果 & 交互

| 主题 | 描述 | 参考 |
|------|------|------|
| 过渡 & 动画 | CSS 过渡、动画关键帧、减少运动 | [effects-transition-animation](references/effects-transition-animation.md) |
| 可见性 & 交互 | 可见性、光标、pointer-events、user-select、z-index | [effects-visibility-interactivity](references/effects-visibility-interactivity.md) |
| 表单控件 | accent-color、appearance、caret-color、resize | [effects-form-controls](references/effects-form-controls.md) |
| 滚动快照 | scroll-snap-type、scroll-snap-align 用于轮播 | [effects-scroll-snap](references/effects-scroll-snap.md) |

## 功能

### 暗黑模式

| 主题 | 描述 | 参考 |
|------|------|------|
| 暗黑模式 | 使用暗黑变体和自定义策略实现暗黑模式 | [features-dark-mode](references/features-dark-mode.md) |

### 迁移

| 主题 | 描述 | 参考 |
|------|------|------|
| 升级指南 | 从 v3 迁移到 v4、破坏性变更、重命名映射 | [features-upgrade](references/features-upgrade.md) |

### 自定义

| 主题 | 描述 | 参考 |
|------|------|------|
| 自定义样式 | 添加自定义样式、工具类、变体以及处理任意值 | [features-custom-styles](references/features-custom-styles.md) |
| 函数 & 指令 | Tailwind 的 CSS 指令和函数，用于处理您的设计系统 | [features-functions-directives](references/features-functions-directives.md) |
| 内容检测 | Tailwind 如何检测类以及如何自定义内容扫描 | [features-content-detection](references/features-content-detection.md) |

## 最佳实践

| 主题 | 描述 | 参考 |
|------|------|------|
| 工具类模式 | 管理重复、冲突、important 修饰符、何时使用组件 | [best-practices-utility-patterns](references/best-practices-utility-patterns.md) |

## 关键建议

- **直接在标记中使用工具类** - 通过组合工具类来组合设计
- **使用主题变量进行自定义** - 使用 `@theme` 指令定义设计令牌
- **移动优先响应式设计** - 使用未加前缀的工具类为移动端，加前缀为断点
- **使用完整类名** - 不要使用字符串插值动态构建类名
- **利用变体** - 堆叠变体以实现复杂的条件样式
- **优先使用 CSS 优先配置** - 使用 `@theme`、`@utility` 和 `@custom-variant` 而不是 JavaScript 配置
