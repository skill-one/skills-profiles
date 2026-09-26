# Tailwind CSS — Utility-first Styling Skill

## 何时使用
- 使用一致的间距/排版比例进行快速 UI 构建
- 设计系统，其中组合优于定制 CSS
- 组件驱动型应用（React/Vue/Svelte）、营销页面、原型 → 生产

## 核心概念与模式
- Utility 在 HTML/JSX 中组合：`class="flex gap-4 p-6 bg-zinc-950 text-white"`
- 响应式变体：`sm: md: lg: xl:` 等
- 状态变体：`hover:`, `focus:`, `active:`, `disabled:`, `group-hover:`, `peer-checked:`
- 任意值（谨慎使用）：`w-[42rem]`, `bg-[#0b1220]`, `translate-y-[3px]`
- 暗黑模式模式：`dark:` 与基于类的策略
- 提取重复模式：
  - 优先使用组件（JSX/Vue 组件）
  - 然后使用 `@apply` 处理小的可重用模式（避免过度使用）
- 构建 pipeline：
  - Tailwind 扫描“内容”文件中的类名并生成 CSS（零运行时）

## 常见陷阱
- 类在生产环境中未生成
  - 确保内容路径包含所有模板/组件。
  - 避免动态构建类名（例如 `"text-" + color`），除非已白名单
- 过度使用 `@apply` 并失去 utility-first 的优势
- 由于类名顺序假设导致的样式冲突
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
        快速构建美观的网站。
      </h1>
      <p class="mt-4 text-zinc-600">
        Tailwind 帮助你快速前进，无需与 CSS 作战。
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

## 需要向用户了解的内容
- 框架/构建工具（Next/Vite/Remix/Webflow 导出）？
- 我们需要设计系统（令牌、组件库）还是一次性页面？
- 暗黑模式？RTL？可访问性限制？
