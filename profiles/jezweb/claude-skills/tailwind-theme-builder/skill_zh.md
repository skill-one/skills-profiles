# Tailwind 主题构建器

使用暗黑模式设置完整的 Tailwind v4 + shadcn/ui 主题项目。生成配置好的 CSS、主题提供者和可用的组件库。

## 架构：四步模式

Tailwind v4 需要特定的架构来实现基于 CSS 变量的主题化。此模式是**强制要求**的——跳过或修改步骤会破坏主题。

### 工作原理

```
CSS 变量定义 --> @theme 内联映射 --> Tailwind 实用类
--background           --> --color-background     --> bg-background
（使用 hsl() 包装）      （引用变量）     （生成的类）
```

暗黑模式切换：
```
ThemeProvider 在 <html> 上切换 .dark 类
  --> CSS 变量自动更新 (.dark 覆盖 :root)
  --> Tailwind 实用类引用更新后的变量
  --> UI 无需重新渲染更新
```

### 最佳实践

- **语义化名称：** 使用 `--primary` 而不是 `--blue-500`
- **前景色配对：** 每个背景色都需要一个前景色 (`--primary` + `--primary-foreground`)
- **WCAG 对比度：** 普通文本 4.5:1，大文本 3:1，UI 组件 3:1
- **图表颜色：** 使用 `@theme inline` 映射的单独变量，在样式属性中通过 `var(--chart-1)` 引用

---

## 工作流程

### 第 1 步：安装依赖项

```bash
pnpm add tailwindcss @tailwindcss/vite
pnpm add -D @types/node tw-animate-css
pnpm dlx shadcn@latest init

# 如果存在，则删除 v3 配置
rm -f tailwind.config.ts
```

### 第 2 步：配置 Vite

复制 `assets/vite.config.ts` 或添加 Tailwind 插件：

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

### 第 3 步：四步 CSS 架构（强制要求）

必须按此顺序执行。跳过步骤会破坏主题。

**src/index.css:**

```css
@import "tailwindcss";
@import "tw-animate-css";

/* 1. 在根级别定义 CSS 变量（不能在 @layer base 内部） */
:root {
  --background: hsl(0 0% 100%);
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  --primary-foreground: hsl(210 40% 98%);
  /* ... 所有语义化令牌 */
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  --primary-foreground: hsl(222.2 47.4% 11.2%);
}

/* 2. 将变量映射到 Tailwind 实用类 */
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}

/* 3. 应用基本样式（此处不使用 hsl() 包装） */
@layer base {
  body {
    background-color: var(--background);
    color: var(--foreground);
  }
}
```

**结果：** `bg-background`, `text-primary` 等自动生效。暗黑模式通过 `.dark` 类切换——无需 `dark:` 变体即可实现语义化颜色。

### 第 4 步：设置暗黑模式

将 `assets/theme-provider.tsx` 复制到您的组件目录，然后包裹您的应用：

```typescript
import { ThemeProvider } from '@/components/theme-provider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
    <App />
  </ThemeProvider>
)
```

添加主题切换——安装下拉菜单后使用下面的 ModeToggle 组件：

```bash
pnpm dlx shadcn@latest add dropdown-menu
```

```typescript
// src/components/mode-toggle.tsx
import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { useTheme } from "@/components/theme-provider"

export function ModeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">切换主题</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>浅色</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>深色</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>系统</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

### 第 5 步：配置 components.json

```json
{
  "tailwind": {
    "config": "",
    "css": "src/index.css",
    "baseColor": "slate",
    "cssVariables": true
  }
}
```

`"config": ""` 至关重要——v4 不使用 `tailwind.config.ts`。

---

## 严格规则

**必须：**
- 在 `:root`/`.dark` 中用 `hsl()` 包装颜色
- 使用 `@theme inline` 映射所有 CSS 变量
- 使用 `@tailwindcss/vite` 插件（不是 PostCSS）
- 如果存在，则删除 `tailwind.config.ts`

**禁止：**
- 将 `:root`/`.dark` 放在 `@layer base` 内
- 使用 `.dark { @theme { } }`（v4 不支持嵌套 @theme）
- 双重包装：`hsl(var(--background))`
- 使用 `@apply` 与 `@layer base` 类（使用 `@utility` 代替）

---

## 所有 18 个常见问题

### 快速诊断

| # | 症状 | 原因 | 解决方法 |
|---|-------|-------|-----|
| 1 | 变量被忽略/主题破坏 | `:root` 在 `@layer base` 内 | 将 `:root` 和 `.dark` 移到根级别 |
| 2 | 暗黑模式颜色不切换 | `.dark { @theme { } }` | 使用 CSS 变量 + 单个 `@theme inline` |
| 3 | 颜色全为黑/白 | 双重 `hsl()` 包装 | 使用 `var(--background)` 而不是 `hsl(var(...))` |
| 4 | `bg-primary` 未生成 | `tailwind.config.ts` 中的颜色 | 删除配置文件，使用 `@theme inline` |
| 5 | 缺少 `bg-background` 类 | 没有 `@theme inline` 块 | 添加 `@theme inline` 映射变量 |
| 6 | shadcn 组件失效 | `components.json` 有配置路径 | 设置 `"config": ""`（空字符串） |
| 7 | Tailwind 未处理 | 使用 PostCSS 插件 | 切换到 `@tailwindcss/vite` 插件 |
| 8 | `@/` 导入失败 | 缺少路径别名 | 在 `tsconfig.app.json` 中添加 `paths` |
| 9 | 重复的 `dark:` 变体 | 使用 `dark:bg-primary-dark` | 直接使用 `bg-primary`——变量会处理它 |
| 10 | 处处硬编码颜色 | 使用 `bg-blue-600 dark:bg-blue-400` | 使用语义化令牌：`bg-primary` |
| 11 | 类合并问题 | 类名的字符串拼接 | 使用 `cn()` 从 `@/lib/utils` |
| 12 | Radix Select 失效 | 空字符串值 `value=""` | 使用 `value="placeholder"` |
| 13 | 错误的 Tailwind 版本 | 安装了 `tailwindcss@^3` | 安装 `tailwindcss@^4.1.0` + `@tailwindcss/vite` |
| 14 | 缺少依赖项 | 仅安装了 `tailwindcss` | 还需安装 `clsx`, `tailwind-merge`, `@types/node` |
| 15 | 暗黑模式下失效 | 仅测试了浅色模式 | 测试浅色、暗黑、系统和切换过渡 |
| 16 | 对比度不满足 WCAG | 视觉上看起来正常 | 检查比例：普通文本 4.5:1，大文本/UI 3:1 |
| 17 | 动画导入构建失败 | 使用 `tailwindcss-animate`（已弃用） | 使用 `tw-animate-css` 或原生 CSS 动画 |
| 18 | CSS 优先级问题 | `@layer base` 在 shadcn init 后重复 | 合并到单个 `@layer base` 块 |

### 常见问题详细说明及代码示例

**#1 -- :root 在 @layer base 内**

Tailwind v4 会移除 `@theme`/`@layer` 外的 CSS，但 `:root` 必须在根级别以持久化。这是最常见的配置错误。

错误：
```css
@layer base {
  :root { --background: hsl(0 0% 100%); }
}
```

正确：
```css
:root { --background: hsl(0 0% 100%); }
@layer base {
  body { background-color: var(--background); }
}
```

**#2 -- 嵌套 @theme**

Tailwind v4 不支持在选择器内使用 `@theme`。使用 CSS 变量在 `:root`/`.dark` 中，并使用单个 `@theme inline` 块。

错误：
```css
@theme { --color-primary: hsl(0 0% 0%); }
.dark { @theme { --color-primary: hsl(0 0% 100%); } }
```

正确：
```css
:root { --primary: hsl(0 0% 0%); }
.dark { --primary: hsl(0 0% 100%); }
@theme inline { --color-primary: var(--primary); }
```

**#3 -- 双重 hsl() 包装**

变量已经包含 `hsl()`。双重包装会创建 `hsl(hsl(...))`。

错误：`background-color: hsl(var(--background));`
正确：`background-color: var(--background);`

**#4 -- tailwind.config.ts 中的颜色**

Tailwind v4 完全忽略 `theme.extend.colors`。删除文件或保持为空。在 `components.json` 中设置 `"config": ""`。

**#5 -- 缺少 @theme inline**

没有 `@theme inline`，Tailwind 无法知道您的 CSS 变量。实用类如 `bg-background` 将不会生成。

错误：
```css
:root { --background: hsl(0 0% 100%); }
/* 没有 @theme inline 块——bg-background 不会存在 */
```

正确：
```css
:root { --background: hsl(0 0% 100%); }
@theme inline { --color-background: var(--background); }
```

**#7 -- PostCSS 与 Vite 插件**

错误：
```typescript
export default defineConfig({
  css: { postcss: './postcss.config.js' }  // 旧的 v3 方法
})
```

正确：
```typescript
import tailwindcss from '@tailwindcss/vite'
export default defineConfig({
  plugins: [react(), tailwindcss()]  // v4 方法
})
```

**#8 -- 路径别名**

在 `tsconfig.app.json` 中添加：
```json
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": { "@/*": ["./src/*"] }
  }
}
```

**#11 -- cn() 用于类合并**

错误：`` className={`base ${isActive && 'active'}`} ``
正确：`className={cn("base", isActive && "active")}`

`cn()` 从 `@/lib/utils` 正确合并和去重 Tailwind 类。

**#12 -- Radix Select 空值**

Radix UI Select 不允许空字符串值。使用 `value="placeholder"` 而不是 `value=""`。

**#14 -- 必要的依赖项**

```json
{
  "dependencies": {
    "tailwindcss": "^4.1.0",
    "@tailwindcss/vite": "^4.1.0",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.3.1"
  },
  "devDependencies": {
    "@types/node": "^24.0.0"
  }
}
```

**#17 -- tw-animate-css**

`tailwindcss-animate` 在 Tailwind v4 中已弃用。shadcn/ui 文档可能仍会引用它。会导致构建失败和导入错误。使用 `tw-animate-css` 或 `@tailwindcss/motion` 代替。

**#18 -- 重复的 @layer base**

`shadcn init` 会添加自己的 `@layer base` 块。运行 init 后立即检查 `src/index.css` 并将任何重复块合并为一个。

错误：
```css
@layer base { body { background-color: var(--background); } }
@layer base { * { border-color: hsl(var(--border)); } }  /* 来自 shadcn 的重复 */
```

正确：
```css
@layer base {
  * { border-color: var(--border); }
  body { background-color: var(--background); color: var(--foreground); }
}
```

### 预防检查清单

- [ ] 没有 `tailwind.config.ts` 文件（或为空）
- [ ] `components.json` 有 `"config": ""`
- [ ] 所有颜色在 `:root` 中有 `hsl()` 包装
- [ ] `@theme inline` 映射所有变量
- [ ] `@layer base` 不包含 `:root`
- [ ] 主题提供者包裹应用
- [ ] 测试了浅色、暗黑和系统模式
- [ ] 所有文本具有足够对比度

---

## 暗黑模式测试清单

- [ ] 浅色模式显示正常
- [ ] 暗黑模式显示正常
- [ ] 系统模式尊重系统设置
- [ ] 主题在页面刷新后保持
- [ ] 切换组件显示当前状态
- [ ] 所有文本具有适当对比度
- [ ] 加载时不会出现错误的主题闪烁
- [ ] 无痕模式下正常工作（优雅回退）

---

## 资源文件

从 `assets/` 目录复制：
- `index.css` -- 完整的 CSS，包含所有颜色变量
- `components.json` -- shadcn/ui v4 配置
- `vite.config.ts` -- Vite + Tailwind 插件
- `theme-provider.tsx` -- 暗黑模式提供者
- `utils.ts` -- `cn()` 工具

## 参考文件

- `references/migration-guide.md` -- v3 到 v4 迁移指南

## 官方文档

- shadcn/ui Tailwind v4 指南：https://ui.shadcn.com/docs/tailwind-v4
- shadcn/ui 暗黑模式（Vite）：https://ui.shadcn.com/docs/dark-mode/vite
- shadcn/ui 主题化：https://ui.shadcn.com/docs/theming
- Tailwind v4 文档：https://tailwindcss.com/docs
- Tailwind 暗黑模式：https://tailwindcss.com/docs/dark-mode
