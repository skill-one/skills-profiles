---
name: vitepress
description: VitePress 是由 Vite 和 Vue 驱动的静态网站生成器。用于构建文档网站、配置主题或使用 Vue 组件编写 Markdown。
---

VitePress 是一个基于 Vite 和 Vue 3 构建的静态网站生成器（SSG）。它将 Markdown 内容应用主题，生成静态 HTML，从而创建一个用于快速导航的单页应用（SPA）。非常适合用于文档、博客和营销网站。

**主要特性：**
- 基于 `.md` 文件进行文件路由
- Vue 组件可直接在 Markdown 中使用
- 快速 HMR，即时更新（<100毫秒）
- 默认主题针对文档进行了优化
- 内置搜索（本地或 Algolia）

**在使用 VitePress 项目之前：**
- 查看 `.vitepress/config.ts` 进行站点配置
- 查看 `.vitepress/theme/` 进行自定义主题扩展
- `public/` 目录包含静态资源，按原样服务

> 本指南基于 VitePress 2.0.0-alpha.20 版本，生成于 2026-09-25。

**VitePress 2 版本注意事项（v1 → v2）：** 使用 `vitepress@next` 安装；需要 Node.js 22+；`defineConfigWithTheme` 已弃用 — 使用 `defineConfig<ThemeConfig>`；原生 RTL 支持通过 `dir` 选项和 CSS 逻辑属性替代旧的 PostCSS 插件方法；内置图标化流程（`icons` 配置，`useIcon`/`VPIcon`，`collection:name` 社交图标）；新增 `assetsBase`（CDN）和 `assetsShards` 构建选项；`metaChunk` 已移除。Markdown `image.lazyLoading` 重命名为 `image.lazyLoad`。

## 核心

| 主题 | 描述 | 参考 |
|------|------|------|
| 配置 | 配置文件设置，`defineConfig`，站点元数据 | [core-config](references/core-config.md) |
| CLI | 命令行界面：开发、构建、预览、初始化 | [core-cli](references/core-cli.md) |
| 路由 | 基于文件的路由，源目录，重写规则 | [core-routing](references/core-routing.md) |
| Markdown | 前置信息，容器，表格，锚点，包含 | [core-markdown](references/core-markdown.md) |

## 功能

### 代码与内容

| 主题 | 描述 | 参考 |
|------|------|------|
| 代码块 | 语法高亮，行高亮，差异，聚焦 | [features-code-blocks](references/features-code-blocks.md) |
| Markdown 中的 Vue | 组件，脚本设置，指令，模板 | [features-vue](references/features-vue.md) |
| 数据加载 | 构建时数据加载器，`createContentLoader` | [features-data-loading](references/features-data-loading.md) |
| 动态路由 | 从数据生成页面，路径加载文件 | [features-dynamic-routes](references/features-dynamic-routes.md) |

## 主题

| 主题 | 描述 | 参考 |
|------|------|------|
| 主题配置 | 导航，侧边栏，搜索，社交链接，页脚 | [theme-config](references/theme-config.md) |
| 自定义 | CSS 变量，插槽，字体，全局组件 | [theme-customization](references/theme-customization.md) |
| 自定义主题 | 从零构建主题，主题接口 | [theme-custom](references/theme-custom.md) |

## 高级

| 主题 | 描述 | 参考 |
|------|------|------|
| 国际化 | 多语言站点，本地化配置 | [advanced-i18n](references/advanced-i18n.md) |
| SSR 兼容性 | 服务器端渲染，`ClientOnly`，动态导入 | [advanced-ssr](references/advanced-ssr.md) |

## 实用技巧

| 主题 | 描述 | 参考 |
|------|------|------|
| 部署 | GitHub Pages，Netlify，Vercel，Cloudflare，Nginx | [recipes-deploy](references/recipes-deploy.md) |
