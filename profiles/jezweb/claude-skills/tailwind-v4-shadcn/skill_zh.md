# Tailwind v4 + shadcn/ui 生产环境堆栈

**生产环境测试**: WordPress 审计器 (https://wordpress-auditor.webfonts.workers.dev)
**最后更新**: 2026-01-20
**版本**: tailwindcss@4.1.18, @tailwindcss/vite@4.1.18
**状态**: 生产就绪 ✅

---

## 快速入门（请按此顺序操作）

```bash
# 1. 安装依赖项
pnpm add tailwindcss @tailwindcss/vite
pnpm add -D @types/node tw-animate-css
pnpm dlx shadcn@latest init

# 2. 如果存在，删除 v3 配置
rm tailwind.config.ts  # v4 不使用此文件
```

**vite.config.ts**:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { '@': path.resolve(__dirname, './src') } }
})
```

**components.json** (关键):
```json
{
  "tailwind": {
    "config": "",              // ← v4 空值
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  }
}
```

---

## 四步架构（强制执行）

跳过步骤将导致您的主题损坏。请严格遵循：

### 第 1 步：在根目录定义 CSS 变量

```css
/* src/index.css */
@import "tailwindcss";
@import "tw-animate-css";  /* shadcn/ui 动画所需 */

:root {
  --background: hsl(0 0% 100%);      /* ← hsl() 包装器必需 */
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  /* ... 所有浅色模式颜色 */
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  /* ... 所有深色模式颜色 */
}
```

**关键**: 在根级别定义（不在 `@layer base` 内）。使用 `hsl()` 包装器。

### 第 2 步：将变量映射到 Tailwind 工具

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ... 映射所有 CSS 变量 */
}
```

**原因**: 生成工具类 (`bg-background`, `text-primary`)。没有这个，工具将不存在。

### 第 3 步：应用基础样式

```css
@layer base {
  body {
    background-color: var(--background);  /* 这里不需要 hsl() 包装器 */
    color: var(--foreground);
  }
}
```

**关键**: 直接引用变量。永远不要双重包装：`hsl(var(--background))`。

### 第 4 步：结果 - 自动深色模式

```tsx
<div className="bg-background text-foreground">
  {/* 无需 dark 变体 - 主题自动切换 */}
</div>
```

---

## 深色模式设置

**1. 创建 ThemeProvider**（参考 `templates/theme-provider.tsx`）

**2. 包裹应用**:
```typescript
// src/main.tsx
import { ThemeProvider } from '@/components/theme-provider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
    <App />
  </ThemeProvider>
)
```

**3. 添加主题切换**:
```bash
pnpm dlx shadcn@latest add dropdown-menu
```

参考 `reference/dark-mode.md` 中的 ModeToggle 组件。

---

## 关键规则

### ✅ 始终执行：

1. 在 `:root`/`.dark` 中用 `hsl()` 包装颜色：`--bg: hsl(0 0% 100%);`
2. 使用 `@theme inline` 映射所有 CSS 变量
3. 在 components.json 中设置 `"tailwind.config": ""`
4. 如果存在，删除 `tailwind.config.ts`
5. 使用 `@tailwindcss/vite` 插件（不是 PostCSS）

### ❌ 永远不要：

1. 将 `:root`/`.dark` 放在 `@layer base` 内（会导致级联问题）
2. 使用 `.dark { @theme { } }` 模式（v4 不支持嵌套 @theme）
3. 双重包装颜色：`hsl(var(--background))`
4. 使用 `tailwind.config.ts` 进行主题设置（v4 会忽略它）
5. 使用 `@apply` 指令（v4 中已弃用，参考错误 #7）
6. 使用 `dark:` 变体进行语义颜色（自动处理）
7. 使用 `@apply` 与 `@layer base` 或 `@layer components` 类一起（v4 的破坏性变更 - 使用 `@utility` 代替） | [来源](https://github.com/tailwindlabs/tailwindcss/discussions/17082)
8. 在不理解 CSS 层级顺序的情况下，将任何样式包裹在 `@layer base` 中（参考错误 #8） | [来源](https://github.com/tailwindlabs/tailwindcss/discussions/16002)

---

## 常见错误及解决方案

此技能可防止 **8 个已记录的错误**。

### 1. ❌ tw-animate-css 导入错误

**错误**: "找不到模块 'tailwindcss-animate'"

**原因**: shadcn/ui 已弃用 v4 的 `tailwindcss-animate`。

**解决方案**:
```bash
# ✅ 做
pnpm add -D tw-animate-css

# 添加到 src/index.css:
@import "tailwindcss";
@import "tw-animate-css";

# ❌ 不要
npm install tailwindcss-animate  # 仅限 v3
```

---

### 2. ❌ 颜色无效

**错误**: `bg-primary` 没有应用样式

**原因**: 缺少 `@theme inline` 映射

**解决方案**:
```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ... 映射所有 CSS 变量 */
}
```

---

### 3. ❌ 深色模式未切换

**错误**: 主题保持为浅色/深色

**原因**: 缺少 ThemeProvider

**解决方案**:
1. 创建 ThemeProvider（参考 `templates/theme-provider.tsx`）
2. 在 `main.tsx` 中包裹应用
3. 验证 `<html>` 元素上的 `.dark` 类切换

---

### 4. ❌ 重复 @layer base

**错误**: 控制台显示 "Duplicate @layer base"

**原因**: shadcn init 添加了 `@layer base` - 不要再添加

**解决方案**:
```css
/* ✅ 正确 - 单个 @layer base */
@import "tailwindcss";

:root { --background: hsl(0 0% 100%); }

@theme inline { --color-background: var(--background); }

@layer base { body { background-color: var(--background); } }
```

---

### 5. ❌ 使用 tailwind.config.ts 导致构建失败

**错误**: "意外的配置文件"

**原因**: v4 不使用 `tailwind.config.ts`（v3 遗留）

**解决方案**:
```bash
rm tailwind.config.ts
```

v4 配置发生在 `src/index.css` 中，使用 `@theme` 指令。

---

### 6. ❌ @theme inline 在多主题设置中破坏深色模式

**错误**: 使用 `@theme inline` 和自定义变体（例如 `data-mode="dark"`）时，深色模式不会切换
**来源**: [GitHub 讨论 #18560](https://github.com/tailwindlabs/tailwindcss/discussions/18560)

**原因**: `@theme inline` 在构建时将变量值嵌入工具中。当深色模式更改底层 CSS 变量时，工具不会更新，因为它们引用的是硬编码值，而不是变量。

**发生原因**:
- `@theme inline` 在构建时内联值：`bg-primary` → `background-color: oklch(...)`
- 深色模式覆盖会更改 CSS 变量，但工具已有内联值
- CSS 特异性链中断

**解决方案**: 对于多主题场景，使用 `@theme`（不带 inline）:

```css
/* ✅ 正确 - 使用 @theme 不带 inline */
@custom-variant dark (&:where([data-mode=dark], [data-mode=dark] *));

@theme {
  --color-text-primary: var(--color-slate-900);
  --color-bg-primary: var(--color-white);
}

@layer theme {
  [data-mode="dark"] {
    --color-text-primary: var(--color-white);
    --color-bg-primary: var(--color-slate-900);
  }
}
```

**何时使用 inline**:
- 单主题 + 深色模式切换（如 shadcn/ui 默认） ✅
- 引用其他不会更改的 CSS 变量 ✅

**何时不用 inline**:
- 多主题系统（data-theme="blue" | "green" | 等） ❌
- 超出浅色/深色范围的自定义主题切换 ❌

**维护者指南**（Adam Wathan）:
> "在 v4 中，让生成的 CSS 直接引用您的主题变量更符合规范。我个人只会在没有它的情况下才使用 inline。"

---

### 7. ❌ @apply 与 @layer base/components（v4 破坏性变更）

**错误**: "无法应用未知的工具类: custom-button"
**来源**: [GitHub 讨论 #17082](https://github.com/tailwindlabs/tailwindcss/discussions/17082)

**原因**: 在 v3 中，`@layer base` 和 `@layer components` 中定义的类可以与 `@apply` 一起使用。在 v4 中，这是破坏性架构变更。

**发生原因**: v4 不再“劫持”原生 CSS `@layer` at-rule。只有使用 `@utility` 定义的类才能用于 `@apply`。

**迁移**:
```css
/* ❌ v3 模式（有效） */
@layer components {
  .custom-button {
    @apply px-4 py-2 bg-blue-500;
  }
}

/* ✅ v4 模式（必需） */
@utility custom-button {
  @apply px-4 py-2 bg-blue-500;
}

/* 或使用原生 CSS */
@layer base {
  .custom-button {
    padding: 1rem 0.5rem;
    background-color: theme(colors.blue.500);
  }
}
```

**注意**: 此技能已建议避免使用 `@apply`。此错误主要针对从 v3 迁移的用户。

---

### 8. ❌ @layer base 样式未应用

**错误**: 在 `@layer base` 中定义的样式似乎被忽略
**来源**: [GitHub 讨论 #16002](https://github.com/tailwindlabs/tailwindcss/discussions/16002) | [讨论 #18123](https://github.com/tailwindlabs/tailwindcss/discussions/18123)

**原因**: v4 使用原生 CSS 层级。如果层级的顺序不明确，基础样式可能会因 CSS 级联而被工具层级的样式覆盖。

**发生原因**:
- v3: Tailwind 特殊处理 `@layer base/components/utilities` 并进行特殊处理
- v4: 使用原生 CSS 层级 - 如果您不按正确的顺序导入层级，优先级会中断
- 样式确实被应用，但工具覆盖了它们

**解决方案选项 1**: 明确定义层级:
```css
@import "tailwindcss/theme.css" layer(theme);
@import "tailwindcss/base.css" layer(base);
@import "tailwindcss/components.css" layer(components);
@import "tailwindcss/utilities.css" layer(utilities);

@layer base {
  body {
    background-color: var(--background);
  }
}
```

**解决方案选项 2**（推荐）: 不要使用 `@layer base` - 在根级别定义样式:
```css
@import "tailwindcss";

:root {
  --background: hsl(0 0% 100%);
}

body {
  background-color: var(--background); /* 不需要 @layer */
}
```

**适用范围**: 所有基础样式，而不仅仅是颜色变量。除非您理解 CSS 层级顺序，否则避免将任何样式包裹在 `@layer base` 中。

---

## 快速参考

| 症状 | 原因 | 修复 |
|------|------|------|
| `bg-primary` 无效 | 缺少 `@theme inline` | 添加 `@theme inline` 块 |
| 颜色全部为黑色/白色 | 双重 `hsl()` 包装 | 使用 `var(--color)` 而不是 `hsl(var(--color))` |
| 深色模式未切换 | 缺少 ThemeProvider | 在 `<ThemeProvider>` 中包裹应用 |
| 构建失败 | 存在 `tailwind.config.ts` | 删除文件 |
| 动画错误 | 使用 `tailwindcss-animate` | 安装 `tw-animate-css` |

---

## Tailwind v4 新功能

### OKLCH 颜色空间（2024 年 12 月）

Tailwind v4.0 用 OKLCH 替换了整个默认颜色面板，这是一种感知均匀的颜色空间。
**来源**: [Tailwind v4.0 发布](https://tailwindcss.com/blog/tailwindcss-v4) | [OKLCH 迁移指南](https://andy-cinquin.com/blog/migration-oklch-tailwind-css-4-0)

**为什么使用 OKLCH**:
- **感知一致性**: HSL 的 "50% 亮度" 在不同色相上视觉上不一致（黄色比蓝色在相同亮度下更亮）
- **更好的渐变**: 平滑过渡，没有模糊的中间颜色
- **更广的色域**: 支持现代显示器上 sRGB 以外的颜色
- **更鲜艳的颜色**: 眼睛吸引人的、饱和的颜色以前受 sRGB 限制

**浏览器支持**（2026 年 1 月）:
- Chrome 111+、Firefox 113+、Safari 15.4+、Edge 111+
- 全球覆盖率: 93.1%

**自动回退**: Tailwind 为旧版浏览器生成 sRGB 回退:
```css
.bg-blue-500 {
  background-color: #3b82f6; /* sRGB 回退 */
  background-color: oklch(0.6 0.24 264); /* 现代浏览器 */
}
```

**自定义颜色**: 定义自定义颜色时，现在更推荐使用 OKLCH:
```css
@theme {
  /* 现代方法（推荐） */
  --color-brand: oklch(0.7 0.15 250);

  /* 遗留方法（仍然有效） */
  --color-brand: hsl(240 80% 60%);
}
```

**迁移**: 无破坏性变更 - Tailwind 自动生成回退。对于新项目，使用 OKLCH 兼容的工具来定义自定义颜色。

### 内置功能（无需插件）

**容器查询**（自 v4.0 作为内置功能）:
```tsx
<div className="@container">
  <div className="@md:text-lg @lg:grid-cols-2">
    内容响应容器宽度，而不是视口
  </div>
</div>
```

**行截断**（自 v3.3 作为内置功能）:
```tsx
<p className="line-clamp-3">截断为 3 行并显示省略号...</p>
<p className="line-clamp-[8]">支持任意值</p>
<p className="line-clamp-(--teaser-lines)">支持 CSS 变量</p>
```

**已移除的插件**:
- `@tailwindcss/container-queries` - 现在是内置的
- `@tailwindcss/line-clamp` - 自 v3.3 起内置

---

## Tailwind v4 插件

使用 `@plugin` 指令（不是 `require()` 或 `@import`）:

**排版**（用于 Markdown/CMS 内容）:
```bash
pnpm add -D @tailwindcss/typography
```
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```
```html
<article class="prose dark:prose-invert">{{ content }}</article>
```

**表单**（跨浏览器表单样式）:
```bash
pnpm add -D @tailwindcss/forms
```
```css
@import "tailwindcss";
@plugin "@tailwindcss/forms";
```

**容器查询**（内置，无需插件）:
```tsx
<div className="@container">
  <div className="@md:text-lg">响应容器宽度</div>
</div>
```

**常见插件错误**:
```css
/* ❌ 错误 - v3 语法 */
@import "@tailwindcss/typography";

/* ✅ 正确 - v4 语法 */
@plugin "@tailwindcss/typography";
```

---

## 设置清单

- [ ] 安装 `@tailwindcss/vite`（不是 postcss）
- [ ] `vite.config.ts` 使用 `tailwindcss()` 插件
- [ ] `components.json` 设置 `"config": ""`
- [ ] 不存在 `tailwind.config.ts`
- [ ] `src/index.css` 遵循 4 步模式:
  - [ ] `:root`/`.dark` 在根级别（不在 @layer 内）
  - [ ] 颜色用 `hsl()` 包装
  - [ ] `@theme inline` 映射所有变量
  - [ ] `@layer base` 使用未包装的变量
- [ ] ThemeProvider 包裹应用
- [ ] 主题切换正常工作

---

## 文件模板

可在 `templates/` 目录中找到:

- **index.css** - 包含所有颜色变量的完整 CSS
- **components.json** - shadcn/ui v4 配置
- **vite.config.ts** - Vite + Tailwind 插件
- **theme-provider.tsx** - 深色模式提供者
- **utils.ts** - `cn()` 工具

---

## 从 v3 迁移

参考 `reference/migration-guide.md` 获取完整指南。

**关键变更**:
- 删除 `tailwind.config.ts`
- 将主题移动到 CSS 中，使用 `@theme inline`
- 替换 `@tailwindcss/line-clamp`（现在内置: `line-clamp-*`）
- 替换 `tailwindcss-animate` 为 `tw-animate-css`
- 更新插件: `require()` → `@plugin`

### 额外迁移注意事项

#### 自动迁移工具可能失败

**警告**: `@tailwindcss/upgrade` 工具经常无法迁移配置。
**来源**: [社区报告](https://medium.com/better-dev-nextjs-react/tailwind-v4-migration-from-javascript-config-to-css-first-in-2025-ff3f59b215ca) | [GitHub 讨论 #16642](https://github.com/tailwindlabs/tailwindcss/discussions/16642)

**常见失败**:
- 排版插件配置
- 复杂的主题扩展
- 自定义插件设置

**建议**: 不要依赖自动迁移。按照迁移指南中的手动步骤操作。

#### 默认元素样式已移除

Tailwind v4 对 Preflight 采取更精简的方法，移除了标题、列表和按钮的默认样式。
**来源**: [GitHub 讨论 #16517](https://github.com/tailwindlabs/tailwindcss/discussions/16517) | [Medium: 迁移问题](https://medium.com/better-dev-nextjs-react/tailwind-v4-migration-from-javascript-config-to-css-first-in-2025-ff3f59b215ca)

**影响**:
- 所有标题 (`<h1>` 到 `<h6>`) 渲染为相同大小
- 列表失去默认填充
- 现有项目的视觉回归

**解决方案**:

**选项 1: 使用 @tailwindcss/typography 为内容页面添加样式**:
```bash
pnpm add -D @tailwindcss/typography
```
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
```
```tsx
<article className="prose dark:prose-invert">
  {/* 所有元素自动样式 */}
</article>
```

**选项 2: 添加自定义基础样式**:
```css
@layer base {
  h1 { @apply text-4xl font-bold mb-4; }
  h2 { @apply text-3xl font-bold mb-3; }
  h3 { @apply text-2xl font-bold mb-2; }
  ul { @apply list-disc pl-6 mb-4; }
  ol { @apply list-decimal pl-6 mb-4; }
}
```

#### PostCSS 设置复杂性

**建议**: 对于 Vite 项目，使用 `@tailwindcss/vite` 插件而不是 PostCSS。
**来源**: [Medium: 迁移问题](https://medium.com/better-dev-nextjs-react/tailwind-v4-migration-from-javascript-config-to-css-first-in-2025-ff3f59b215ca) | [GitHub 讨论 #15764](https://github.com/tailwindlabs/tailwindcss/discussions/15764)

**为什么 Vite 插件更好**:
```typescript
// ✅ Vite 插件 - 一行，无需 PostCSS 配置
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
})

// ❌ PostCSS - 多步骤，插件兼容性问题
// 1. 安装 @tailwindcss/postcss
// 2. 配置 postcss.config.js
// 3. 管理插件顺序
// 4. 调试插件冲突
```

**PostCSS 问题报告**:
- 错误: "看起来您正在尝试直接使用 tailwindcss 作为 PostCSS 插件"
- 需要多个 PostCSS 插件: `postcss-import`, `postcss-advanced-variables`, `tailwindcss/nesting`
- v4 PostCSS 插件是单独的包: `@tailwindcss/postcss`

**官方指南**: 对于 Vite 项目，建议使用 Vite 插件。PostCSS 适用于遗留设置或非 Vite 环境。

#### 视觉变化

**环宽度默认**: 从 3px 改为 1px
**来源**: [Medium: 迁移指南](https://medium.com/better-dev-nextjs-react/tailwind-v4-migration-from-javascript-config-to-css-first-in-2025-ff3f59b215ca)

- `ring` 类现在更细
- 使用 `ring-3` 匹配 v3 外观

```tsx
// v3: 3px ring
<button className="ring">按钮</button>

// v4: 1px ring (更细)
<button className="ring">按钮</button>

// 匹配 v3 外观
<button className="ring-3">按钮</button>
```

---

## 参考文档

- **architecture.md** - 深入探讨 4 步模式
- **dark-mode.md** - 完整深色模式实现
- **common-gotchas.md** - 故障排除指南
- **migration-guide.md** - v3 → v4 迁移

---

## 官方文档

- **shadcn/ui Vite 设置**: https://ui.shadcn.com/docs/installation/vite
- **shadcn/ui Tailwind v4**: https://ui.shadcn.com/docs/tailwind-v4
- **Tailwind v4 文档**: https://tailwindcss.com/docs

---

**最后更新**: 2026-01-20
**技能版本**: 3.0.0
**Tailwind v4**: 4.1.18 (最新)
**生产**: WordPress 审计器 (https://wordpress-auditor.webfonts.workers.dev)

**变更日志**:
- v3.0.0 (2026-01-20): 主要研究更新 - 添加 3 个 TIER 1 错误 (#6-8), 扩展迁移指南与社区发现（TIER 2），添加 OKLCH 颜色空间部分、PostCSS 复杂性警告和迁移工具限制
- v2.0.1 (2026-01-03): 生产验证
- v2.0.0: 初始发布，包含 5 个已记录的错误
