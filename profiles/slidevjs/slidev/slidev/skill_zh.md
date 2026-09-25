# Slidev - 开发者演示文稿

基于 Vite、Vue 和 Markdown 构建的网页版演示文稿制作工具。

## 使用场景

- 技术演示或带实时代码示例的幻灯片
- 带动画的语法高亮代码片段
- 交互式演示（Monaco 编辑器、可运行代码）
- 数学公式（LaTeX）或图表（Mermaid、PlantUML）
- 录制带演讲者笔记的演示
- 导出为 PDF、PPTX 或作为 SPA 托管
- 开发者讲座或工作坊的代码演示

## 快速入门

```bash
pnpm create slidev    # 创建项目
pnpm run dev          # 启动开发服务器（打开 http://localhost:3030）
pnpm run build        # 构建静态 SPA
pnpm run export       # 导出为 PDF（需要 playwright-chromium）
```

**验证**：执行 `pnpm run dev` 后，确认幻灯片加载在 `http://localhost:3030`。执行 `pnpm run export` 后，检查项目根目录下是否存在输出 PDF。

## 基本语法

```md
---
theme: default
title: 我的演示
---

# 第一张幻灯片

内容在此处

---

# 第二张幻灯片

更多内容

<!--
演讲者笔记在此处
-->
```

- `---` 分隔幻灯片
- 第一个 frontmatter = headmatter（演示文稿配置）
- HTML 注释 = 演讲者笔记

## 核心参考

| 主题 | 描述 | 参考 |
|------|------|------|
| Markdown 语法 | 幻灯片分隔符、frontmatter、笔记、代码块 | [core-syntax](references/core-syntax.md) |
| 动画 | v-click、v-clicks、motion、过渡 | [core-animations](references/core-animations.md) |
| headmatter | 全局配置选项 | [core-headmatter](references/core-headmatter.md) |
| frontmatter | 每张幻灯片配置选项 | [core-frontmatter](references/core-frontmatter.md) |
| CLI 命令 | 开发、构建、导出、主题命令 | [core-cli](references/core-cli.md) |
| 组件 | 内置 Vue 组件 | [core-components](references/core-components.md) |
| 布局 | 内置幻灯片布局 | [core-layouts](references/core-layouts.md) |
| 导出 | PDF、PPTX、PNG 导出选项 | [core-exporting](references/core-exporting.md) |
| 托管 | 构建和部署到各种平台 | [core-hosting](references/core-hosting.md) |
| 全局上下文 | $nav、$slidev、composables API | [core-global-context](references/core-global-context.md) |

## 功能参考

### 代码与编辑器

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 行高亮 | `` ```ts {2,3} `` | [code-line-highlighting](references/code-line-highlighting.md) |
| 点击高亮 | `` ```ts {1\|2-3\|all} `` | [code-line-highlighting](references/code-line-highlighting.md) |
| 行号 | `lineNumbers: true` 或 `{lines:true}` | [code-line-numbers](references/code-line-numbers.md) |
| 可滚动代码 | `{maxHeight:'100px'}` | [code-max-height](references/code-max-height.md) |
| 代码标签 | `::code-group`（需要 `comark: true`） | [code-groups](references/code-groups.md) |
| Monaco 编辑器 | `` ```ts {monaco} `` | [editor-monaco](references/editor-monaco.md) |
| 运行代码 | `` ```ts {monaco-run} `` | [editor-monaco-run](references/editor-monaco-run.md) |
| 编辑文件 | `<<< ./file.ts {monaco-write}` | [editor-monaco-write](references/editor-monaco-write.md) |
| 代码动画 | `` ````md magic-move `` | [code-magic-move](references/code-magic-move.md) |
| TypeScript 类型 | `` ```ts twoslash `` | [code-twoslash](references/code-twoslash.md) |
| 导入代码 | `<<< @/snippets/file.js` | [code-import-snippet](references/code-import-snippet.md) |

### 图表与数学

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| Mermaid 图表 | `` ```mermaid `` | [diagram-mermaid](references/diagram-mermaid.md) |
| PlantUML 图表 | `` ```plantuml `` | [diagram-plantuml](references/diagram-plantuml.md) |
| LaTeX 数学 | `$inline$` 或 `$$block$$` | [diagram-latex](references/diagram-latex.md) |

### 布局与样式

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 画布尺寸 | `canvasWidth`, `aspectRatio` | [layout-canvas-size](references/layout-canvas-size.md) |
| 缩放幻灯片 | `zoom: 0.8` | [layout-zoom](references/layout-zoom.md) |
| 缩放元素 | `<Transform :scale="0.5">` | [layout-transform](references/layout-transform.md) |
| 布局插槽 | `::right::`, `::default::` | [layout-slots](references/layout-slots.md) |
| 作用域 CSS | `<style>` 在幻灯片中 | [style-scoped](references/style-scoped.md) |
| 全局层 | `global-top.vue`, `global-bottom.vue` | [layout-global-layers](references/layout-global-layers.md) |
| 可拖动元素 | `v-drag`, `<v-drag>` | [layout-draggable](references/layout-draggable.md) |
| 图标 | `<mdi-icon-name />` | [style-icons](references/style-icons.md) |

### 动画与交互

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 点击动画 | `v-click`, `<v-clicks>` | [core-animations](references/core-animations.md) |
| 粗略标记 | `v-mark.underline`, `v-mark.circle` | [animation-rough-marker](references/animation-rough-marker.md) |
| 绘图模式 | 按 `C` 或配置 `drawings:` | [animation-drawing](references/animation-drawing.md) |
| 方向样式 | `forward:delay-300` | [style-direction](references/style-direction.md) |
| 笔记高亮 | `[click]` 在笔记中 | [animation-click-marker](references/animation-click-marker.md) |

### 语法扩展

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| Comark 语法 | `comark: true` + `{style="color:red"}` | [syntax-comark](references/syntax-comark.md) |
| 块 frontmatter | `` ```yaml `` 而不是 `---` | [syntax-block-frontmatter](references/syntax-block-frontmatter.md) |
| 导入幻灯片 | `src: ./other.md` | [syntax-importing-slides](references/syntax-importing-slides.md) |
| 合并 frontmatter | 主入口优先 | [syntax-frontmatter-merging](references/syntax-frontmatter-merging.md) |

### 演讲者与录制

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 录制 | 按 `G` 摄像头 | [presenter-recording](references/presenter-recording.md) |
| 计时器 | `duration: 30min`, `timer: countdown` | [presenter-timer](references/presenter-timer.md) |
| 远程控制 | `slidev --remote` | [presenter-remote](references/presenter-remote.md) |
| Ruby 文本 | `notesAutoRuby:` | [presenter-notes-ruby](references/presenter-notes-ruby.md) |

### 导出与构建

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 导出选项 | `slidev export` | [core-exporting](references/core-exporting.md) |
| 构建 & 部署 | `slidev build` | [core-hosting](references/core-hosting.md) |
| 构建 PDF | `download: true` | [build-pdf](references/build-pdf.md) |
| 缓存图片 | 远程 URL 自动缓存 | [build-remote-assets](references/build-remote-assets.md) |
| OG 图片 | `seoMeta.ogImage` 或 `og-image.png` | [build-og-image](references/build-og-image.md) |
| SEO 标签 | `seoMeta:` | [build-seo-meta](references/build-seo-meta.md) |

**导出前提**：`pnpm add -D playwright-chromium` 是 PDF/PPTX/PNG 导出的必要依赖。如果导出因浏览器错误失败，请先安装此依赖。

### 编辑器与工具

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 侧边编辑器 | 点击编辑图标 | [editor-side](references/editor-side.md) |
| VS Code 扩展 | 安装 `antfu.slidev` | [editor-vscode](references/editor-vscode.md) |
| Prettier | `prettier-plugin-slidev` | [editor-prettier](references/editor-prettier.md) |
| 主题卸载 | `slidev theme eject` | [tool-eject-theme](references/tool-eject-theme.md) |
| MCP 服务器（AI 代理） | `http://localhost:<port>/__mcp` 或 `slidev mcp` | [tool-mcp](references/tool-mcp.md) |

### 生命周期与 API

| 功能 | 使用方式 | 参考 |
|------|----------|------|
| 幻灯片钩子 | `onSlideEnter()`, `onSlideLeave()` | [api-slide-hooks](references/api-slide-hooks.md) |
| 导航 API | `$nav`, `useNav()` | [core-global-context](references/core-global-context.md) |

## 常用布局

| 布局 | 目的 |
|------|------|
| `cover` | 标题/封面幻灯片 |
| `center` | 居中内容 |
| `default` | 标准幻灯片 |
| `two-cols` | 两列（使用 `::right::`） |
| `two-cols-header` | 标题 + 两列 |
| `image` / `image-left` / `image-right` | 图片布局 |
| `iframe` / `iframe-left` / `iframe-right` | 嵌入 URL |
| `quote` | 引用 |
| `section` | 分隔符 |
| `fact` / `statement` | 数据/声明显示 |
| `intro` / `end` | 引言/结束幻灯片 |

## 资源

- 文档：https://sli.dev
- 主题库：https://sli.dev/resources/theme-gallery
- 演示案例：https://sli.dev/resources/showcases
