UnoCSS 是一个即时原子 CSS 引擎，设计得灵活且可扩展。其核心是无偏见的——所有 CSS 工具都通过预设提供。它是 Tailwind CSS 的超集，因此你可以重用你的 Tailwind 知识来使用基本语法。

**重要提示：** 在编写 UnoCSS 代码之前，代理应检查项目根目录中的 `uno.config.*` 或 `unocss.config.*` 文件，以了解可用的预设、规则和快捷方式。如果项目设置不明确，请避免使用 attributify 模式和其他高级功能——坚持使用基本的 `class` 使用方式。

> 该技能基于 UnoCSS 66.x 版本，生成于 2026-01-28。

## 核心

| 主题 | 描述 | 参考 |
|------|------|------|
| 配置 | 配置文件设置和所有配置选项 | [core-config](references/core-config.md) |
| 规则 | 用于生成 CSS 工具的静态和动态规则 | [core-rules](references/core-rules.md) |
| 快捷方式 | 将多个规则组合为单个简写 | [core-shortcuts](references/core-shortcuts.md) |
| 主题 | 用于颜色、断点、设计令牌的主题系统 | [core-theme](references/core-theme.md) |
| 变体 | 将 hover:、dark:、responsive 等变化应用于规则 | [core-variants](references/core-variants.md) |
| 提取 | UnoCSS 如何从源代码中提取工具 | [core-extracting](references/core-extracting.md) |
| 安全列表和黑名单 | 强制包含或排除特定工具 | [core-safelist](references/core-safelist.md) |
| 层级和预渲染 | CSS 层级排序和原始 CSS 注入 | [core-layers](references/core-layers.md) |

## 预设

### 主要预设

| 主题 | 描述 | 参考 |
|------|------|------|
| 预设 Wind3 | 兼容 Tailwind CSS v3 / Windi CSS 的预设（最常见） | [preset-wind3](references/preset-wind3.md) |
| 预设 Wind4 | 兼容 Tailwind CSS v4 并具有现代 CSS 功能的预设 | [preset-wind4](references/preset-wind4.md) |
| 预设 Mini | 包含自定义构建所需基本工具的最小预设 | [preset-mini](references/preset-mini.md) |

### 功能预设

| 主题 | 描述 | 参考 |
|------|------|------|
| 预设 Icons | 使用 Iconify 的纯 CSS 图标，支持任何图标集 | [preset-icons](references/preset-icons.md) |
| 预设 Attributify | 将工具分组到 HTML 属性中，而不是 class | [preset-attributify](references/preset-attributify.md) |
| 预设 Typography | 用于默认排版类 | [preset-typography](references/preset-typography.md) |
| 预设 Web Fonts | 轻松集成 Google Fonts 和其他网络字体 | [preset-web-fonts](references/preset-web-fonts.md) |
| 预设 Tagify | 将工具用作 HTML 标签名 | [preset-tagify](references/preset-tagify.md) |
| 预设 Rem to Px | 将 rem 单位转换为 px 用于工具 | [preset-rem-to-px](references/preset-rem-to-px.md) |

## 转换器

| 主题 | 描述 | 参考 |
|------|------|------|
| 变体组 | 具有共同前缀的工具分组简写 | [transformer-variant-group](references/transformer-variant-group.md) |
| 指令 | CSS 指令：@apply、@screen、theme()、icon() | [transformer-directives](references/transformer-directives.md) |
| 编译类 | 将多个类编译为一个哈希类 | [transformer-compile-class](references/transformer-compile-class.md) |
| Attributify JSX | 支持 JSX/TSX 中的无值 attributify | [transformer-attributify-jsx](references/transformer-attributify-jsx.md) |

## 集成

| 主题 | 描述 | 参考 |
|------|------|------|
| Vite 集成 | 使用 Vite 配置 UnoCSS 及特定框架的提示 | [integrations-vite](references/integrations-vite.md) |
| Nuxt 集成 | Nuxt 应用的 UnoCSS 模块 | [integrations-nuxt](references/integrations-nuxt.md) |
