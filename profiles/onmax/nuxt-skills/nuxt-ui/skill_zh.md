# Nuxt UI

基于 [Reka UI](https://reka-ui.com/) + [Tailwind CSS](https://tailwindcss.com/) + [Tailwind Variants](https://www.tailwind-variants.org/) 构建的 Vue 组件库。可与 Nuxt、Vue (Vite)、Laravel (Vite + Inertia) 和 AdonisJS (Vite + Inertia) 一起使用。

## MCP 服务器

对于组件 API 细节（属性、插槽、事件、完整文档、示例），请使用 [Nuxt UI MCP 服务器](https://ui.nuxt.com/docs/getting-started/ai/mcp)。如果尚未配置，请添加：

**Cursor** — `.cursor/mcp.json`:

```json
{ "mcpServers": { "nuxt-ui": { "type": "http", "url": "https://ui.nuxt.com/mcp" } } }
```

**Claude Code**:

```bash
claude mcp add --transport http nuxt-ui https://ui.nuxt.com/mcp
```

主要的 MCP 工具：

- `search-components` — 按名称、类别或意图查找组件（无参数 = 列出所有）
- `search-composables` — 按名称或描述查找可组合项（无参数 = 列出所有）
- `search-icons` — 搜索 Iconify 图标（默认为 `lucide`），返回 `i-{prefix}-{name}` 名称
- `get-component` — 带使用示例的完整组件文档
- `get-component-metadata` — 属性、插槽、事件（轻量级，无文档内容）
- `get-example` — 真实世界的代码示例

当您需要了解 **组件接受什么** 或 **其 API 如何工作** 时，请使用 MCP。这项技能教您 **何时使用哪个组件** 以及 **如何构建良好**。

## 核心规则（始终适用）

1. **始终用 `UApp` 包裹应用** — 这对于 toast、工具提示和程序化覆盖是必需的。接受 `locale` 属性用于 i18n。
2. **始终使用语义化颜色** — `text-default`、`bg-elevated`、`border-muted` 等。切勿使用原始 Tailwind 调色板颜色，如 `text-gray-500`。
3. **读取生成的主题文件以获取插槽名称** — Nuxt: `.nuxt/ui/<component>.ts`，Vue: `node_modules/.nuxt-ui/ui/<component>.ts`。这些文件显示任何组件的每个插槽、变体和默认类。
4. **覆盖优先级**（最高者胜出）: `ui` 属性 / `class` 属性 → 全局配置 → 主题默认值。
5. **图标使用 `i-{collection}-{name}` 格式** — `lucide` 是默认集合。使用 MCP 的 `search-icons` 工具查找图标，或浏览 [icones.js.org](https://icones.js.org)。

## 如何使用这项技能

根据任务，在编写任何代码之前加载相关的参考文件。不要加载所有内容 — 仅加载所需内容。

### 参考文件

**指南** — 设计决策和约定：

- [design-system](references/guidelines/design-system.md) — 语义化颜色、主题、品牌定制、变体、`ui` 属性
- [component-selection](references/guidelines/component-selection.md) — 决策矩阵：何时使用 Modal vs Slideover，Select vs SelectMenu，Toast vs Alert 等
- [conventions](references/guidelines/conventions.md) — 编码模式、插槽命名、项数组、可组合项、键盘快捷键
- [forms](references/guidelines/forms.md) — 表单验证、字段布局、错误处理、标准模式

**布局** — 全页结构模式：

- [landing](references/layouts/landing.md) — 登录页面、博客、版本日志、定价
- [dashboard](references/layouts/dashboard.md) — 带侧边栏和面板的 admin UI
- [docs](references/layouts/docs.md) — 带导航和目录的文档站点
- [chat](references/layouts/chat.md) — 使用 Vercel AI SDK 的 AI 聊天
- [editor](references/layouts/editor.md) — 带工具栏的富文本编辑器

**配方** — 常见任务的完整模式：

- [data-tables](references/recipes/data-tables.md) — 带过滤、分页、排序、选择的表格
- [auth](references/recipes/auth.md) — 登录、注册、忘记密码表单
- [overlays](references/recipes/overlays.md) — 模态框、滑出框、抽屉、命令面板
- [navigation](references/recipes/navigation.md) — 头部、侧边栏、面包屑、选项卡

**快速参考**：

- [components](references/components.md) — 分类组件索引，用于查找正确的组件名称

### 路由表

| 任务                              | 加载这些参考文件                         |
| --------------------------------- | --------------------------------------------- |
| 构建登录页面              | design-system, conventions, landing           |
| 构建仪表板 / admin UI      | conventions, component-selection, dashboard   |
| 添加设置页面               | conventions, forms                            |
| 创建登录 / 注册表单      | conventions, forms, auth                      |
| 在表格中显示数据           | conventions, component-selection, data-tables |
| 定制主题 / 品牌颜色    | design-system                                 |
| 添加聊天界面              | conventions, chat                             |
| 添加模态框、滑出框或抽屉 | conventions, component-selection, overlays    |
| 构建站点导航             | conventions, component-selection, navigation  |
| 构建文档站点        | conventions, docs                             |
| 渲染 markdown                   | component-selection, components, docs         |
| 添加富文本编辑器            | conventions, editor                           |
| 一般 UI 工作                   | conventions, component-selection              |

## 安装

### Nuxt

```bash
pnpm add @nuxt/ui tailwindcss
```

```ts
// nuxt.config.ts
export default defineNuxtConfig({
  modules: ['@nuxt/ui'],
  css: ['~/assets/css/main.css']
})
```

```css
/* app/assets/css/main.css */
@import "tailwindcss";
@import "@nuxt/ui";
```

```vue
<!-- app.vue -->
<template>
  <UApp>
    <NuxtPage />
  </UApp>
</template>
```

### Vue (Vite)

```bash
pnpm add @nuxt/ui tailwindcss
```

```ts
// vite.config.ts
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import ui from '@nuxt-ui/vite'

export default defineConfig({
  plugins: [
    vue(),
    ui()
  ]
})
```

```ts
// src/main.ts
import './assets/css/main.css'
import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ui from '@nuxt-ui/vue-plugin'
import App from './App.vue'

const app = createApp(App)
const router = createRouter({
  routes: [],
  history: createWebHistory()
})

app.use(router)
app.use(ui)
app.mount('#app')
```

```css
/* src/assets/css/main.css */
@import "tailwindcss";
@import "@nuxt/ui";
```

```vue
<!-- src/App.vue -->
<template>
  <UApp>
    <RouterView />
  </UApp>
</template>
```

> 在 `index.html` 中的根 `<div id="app">` 添加 `class="isolate"`。
> 对于 Inertia: 在 `vite.config.ts` 中使用 `ui({ router: 'inertia' })`。
