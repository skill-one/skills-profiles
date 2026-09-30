---
name: tailwindcss
description: 在设计和实现使用 Tailwind CSS 的 UI 时使用（布局、排版、响应式、主题、组件模式）。包含快速配方和规范，以实现干净、一致的网页设计。
---

# Tailwind CSS — Utility-first Styling Skill

## 何时使用
- 使用一致的间距/排版比例快速构建 UI
- 设计系统，组合优先于定制 CSS
- 组件驱动应用（React/Vue/Svelte）、营销页面、原型 → 生产

## 核心概念与模式
- Utility 在 HTML/JSX 中组合：`class="flex gap-4 p-6 bg-zinc-950 text-white"`
- 响应式变体：`sm: md: lg: xl:` 等
- 状态变体：`hover:`, `focus:`, `active:`, `disabled:`, `group-hover:`, `peer-checked:`
- 任意值（谨慎使用）：`w-[42rem]`, `bg-[#0b1220]`, `translate-y-[3px]`
- 暗黑模式模式：`dark:` 与基于类的策略
- 提取重复模式：
  - 优先使用组件（JSX/Vue 组件）
  - 然后使用 `@apply` 处理小型可复用模式（避免过度使用）
- 构建流程：
  - Tailwind 扫描“内容”文件中的类名并生成 CSS（零运行时）

## 常见陷阱
- 类名未在生产环境中生成
  - 确保内容路径包含所有模板/组件。
  - 避免动态构建类名（例如 `"text-" + color`），除非已白名单
- 过度使用 `@apply` 并失去 Utility-first 的优势
- 类名顺序冲突导致样式冲突
- 没有结构的巨大 HTML 类列表
  - 使用组件组合；拆分为子组件；必要时使用 `clsx/cva`。

## 快速示例

### 1) 一个干净的 CTA 按钮
```html
<button class="inline-flex items-center justify-center rounded-xl px-5 py-3
               bg-indigo-600 text-white font-medium
               hover:bg-indigo-500 active:bg-indigo-700
               focus:outline-none focus:ring-2 focus:ring-indigo-400/60">
  Get started
</button>
```

### 2) 响应式英雄布局
```html
<section class="mx-auto max-w-6xl px-6 py-16">
  <div class="grid gap-10 lg:grid-cols-2 lg:items-center">
    <div>
      <h1 class="text-4xl font-semibold tracking-tight sm:text-5xl">
        快速构建美观网站。
      </h1>
      <p class="mt-4 text-zinc-600">
        Tailwind 帮助你快速开发，无需与 CSS 作斗争。
      </p>
    </div>
    <div class="rounded-2xl border border-zinc-200 bg-white p-6 shadow-sm">
      <!-- 媒体 -->
    </div>
  </div>
</section>
```

### 3) 安全处理动态类名
优先使用映射：
```js
const toneClass = {
  success: "bg-emerald-600",
  danger: "bg-rose-600",
  info: "bg-sky-600",
}[tone];
```

## 需要询问用户的问题
- 框架/构建工具（Next/Vite/Remix/Webflow 导出）？
- 我们需要设计系统（令牌、组件库）还是一次性页面？
- 暗黑模式？RTL？无障碍性限制？
