# Tailwind v4 + shadcn/ui 生产环境配置栈

**经过生产环境测试**: WordPress 审计工具 (https://wordpress-auditor.webfonts.workers.dev)
**最后更新**: 2025-12-04
**状态**: 生产就绪 ✅

## 目录
1. [开始前须知](#-开始前须知请阅读此部分)
2. [快速入门](#快速入门5分钟---请按此确切顺序操作)
3. [四步架构](#四步架构关键)
4. [暗黑模式设置](#暗黑模式设置)
5. [关键规则](#关键规则必须遵守)
6. [语义颜色标记](#语义颜色标记)
7. [常见问题及修复方法](#常见问题--快速修复方法)
8. [文件模板](#文件模板)
9. [配置清单](#完整配置清单)
10. [高级主题](#高级主题)
11. [依赖项](#依赖项)
12. [Tailwind v4 插件](#tailwind-v4插件)
13. [参考文档](#参考文档)
14. [何时加载参考](#何时加载参考)

---

## ⚠️ 开始前须知 (请阅读此部分!)

**对 AI 代理至关重要**: 如果你正在使用 Claude Code 帮助用户设置 Tailwind v4:

1. **在对话开始时明确声明你正在使用此技能**
2. **参考技能中的模式** 而不是一般知识
3. **防止已知问题** 列表在 `reference/common-gotchas.md` 中
4. **不要猜测** - 如果不确定，请检查技能文档

**用户操作要求**: 告诉 Claude 首先检查此技能!

说: **"我正在设置 Tailwind v4 + shadcn/ui - 首先检查 tailwind-v4-shadcn 技能"**

### 这为何重要 (实际效果)

**未激活技能**:
- ❌ 配置时间: ~5 分钟
- ❌ 遇到错误: 2-3 个 (tw-animate-css, 重复的 @layer base)
- ❌ 需要手动修复: 2+ 提交
- ❌ 令牌使用量: ~65k
- ❌ 用户信心: 需要调试

**已激活技能**:
- ✅ 配置时间: ~1 分钟
- ✅ 遇到错误: 0
- ✅ 需要手动修复: 0
- ✅ 令牌使用量: ~20k (减少 70%)
- ✅ 用户信心: 即时成功

### 此技能防止的已知问题

1. **tw-animate-css 导入错误** (v4 中已弃用)
2. **重复的 @layer base 块** (shadcn init 会添加自己的)
3. **错误模板选择** (vanilla TS vs React)
4. **缺少 post-init 清理** (不兼容的 CSS 规则)
5. **错误的插件语法** (使用 @import 或 require() 而不是 @plugin 指令)

当技能激活时，所有这些问题都会自动处理。

---

## 快速入门 (5 分钟 - 请按此确切顺序操作)

### 1. 安装依赖项

```bash
bun add tailwindcss @tailwindcss/vite
# 或: npm install tailwindcss @tailwindcss/vite

bun add -d @types/node

# 注意: 由于已知的 Bun 兼容性问题，使用 pnpm 进行 shadcn init
# (bunx 有 "Script not found" 和 postinstall/msw 问题)
pnpm dlx shadcn@latest init
```

### 2. 配置 Vite

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import path from 'path'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
```

### 3. 更新 components.json

```json
{
  "tailwind": {
    "config": "",              // ← 关键: v4 为空
    "css": "src/index.css",
    "cssVariables": true
  }
}
```

### 4. 删除 tailwind.config.ts

```bash
rm tailwind.config.ts  # v4 不使用此文件
```

---

## 四步架构 (关键)

此模式是 **强制要求** - 跳过步骤将导致您的主题失效。

### 第 1 步: 在根级别定义 CSS 变量

```css
/* src/index.css */
@import "tailwindcss";

:root {
  --background: hsl(0 0% 100%);      /* ← hsl() 包装器是必需的 */
  --foreground: hsl(222.2 84% 4.9%);
  --primary: hsl(221.2 83.2% 53.3%);
  /* ... 所有浅色模式颜色 */
}

.dark {
  --background: hsl(222.2 84% 4.9%);
  --foreground: hsl(210 40% 98%);
  --primary: hsl(217.2 91.2% 59.8%);
  /* ... 所有暗黑模式颜色 */
}
```

**关键规则**:
- ✅ 在根级别定义 (不在 @layer base 内)
- ✅ 所有颜色值使用 `hsl()` 包装器
- ✅ 使用 `.dark` 表示暗黑模式 (不是 `.dark { @theme { } }`)

### 第 2 步: 将变量映射到 Tailwind 工具

```css
@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  /* ... 映射所有 CSS 变量 */
}
```

**为什么需要这样做**:
- 生成实用类 (`bg-background`, `text-primary`)
- 没有这个，`bg-primary` 等将不存在

### 第 3 步: 应用基础样式

```css
@layer base {
  body {
    background-color: var(--background);  /* 这里不需要 hsl() */
    color: var(--foreground);
  }
}
```

**关键规则**:
- ✅ 直接引用变量: `var(--background)`
- ❌ 不要双重包装: `hsl(var(--background))`

### 第 4 步: 结果 - 自动暗黑模式

```tsx
<div className="bg-background text-foreground">
  {/* 不需要 dark: 变体 - 主题会自动切换 */}
</div>
```

---

## 暗黑模式设置

### 1. 创建 ThemeProvider

查看 `reference/dark-mode.md` 获取完整实现或使用模板:

```typescript
// 从: templates/theme-provider.tsx 复制
```

### 2. 包裹您的 App

```typescript
// src/main.tsx
import { ThemeProvider } from '@/components/theme-provider'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <ThemeProvider defaultTheme="dark" storageKey="vite-ui-theme">
      <App />
    </ThemeProvider>
  </React.StrictMode>,
)
```

### 3. 添加主题切换器

```bash
pnpm dlx shadcn@latest add dropdown-menu
```

查看 `reference/dark-mode.md` 获取 ModeToggle 组件代码。

---

## 关键规则 (必须遵守)

### ✅ 总是做:

1. **在 `:root` 和 `.dark` 中用 `hsl()` 包装颜色值**
   ```css
   --background: hsl(0 0% 100%);  /* ✅ 正确 */
   ```

2. **使用 `@theme inline` 映射所有 CSS 变量**
   ```css
   @theme inline {
     --color-background: var(--background);
   }
   ```

3. **在 components.json 中设置 `"tailwind.config": ""`**
   ```json
   { "tailwind": { "config": "" } }
   ```

4. **如果存在则删除 `tailwind.config.ts`**

5. **使用 `@tailwindcss/vite` 插件 (不是 PostCSS)**

6. **使用 `cn()` 处理条件类**
   ```typescript
   import { cn } from "@/lib/utils"
   <div className={cn("base", isActive && "active")} />
   ```

### ❌ 永远不要做:

1. **将 `:root` 或 `.dark` 放在 `@layer base` 内**
   ```css
   /* 错误 */
   @layer base {
     :root { --background: hsl(...); }
   }
   ```

2. **使用 `.dark { @theme { } }` 模式**
   ```css
   /* 错误 - v4 不支持嵌套 @theme */
   .dark {
     @theme {
       --color-primary: hsl(...);
     }
   }
   ```

3. **双重包装颜色**
   ```css
   /* 错误 */
   body {
     background-color: hsl(var(--background));
   }
   ```

4. **使用 `tailwind.config.ts` 设置主题颜色**
   ```typescript
   /* 错误 - v4 忽略此文件 */
   export default {
     theme: {
       extend: {
         colors: { primary: 'hsl(var(--primary))' }
       }
     }
   }
   ```

5. **使用 `@apply` 指令 (v4 中已弃用)**

6. **使用 `dark:` 变体处理语义颜色**
   ```tsx
   /* 错误 */
   <div className="bg-primary dark:bg-primary-dark" />

   /* 正确 */
   <div className="bg-primary" />
   ```

---

## 语义颜色标记

始终使用语义名称表示颜色:

```css
:root {
  --destructive: hsl(0 84.2% 60.2%);        /* 红色 - 错误、关键 */
  --success: hsl(142.1 76.2% 36.3%);        /* 绿色 - 成功状态 */
  --warning: hsl(38 92% 50%);               /* 黄色 - 警告 */
  --info: hsl(221.2 83.2% 53.3%);           /* 蓝色 - 信息、主要 */
}
```

**使用方法**:
```tsx
<div className="bg-destructive text-destructive-foreground">关键</div>
<div className="bg-success text-success-foreground">成功</div>
<div className="bg-warning text-warning-foreground">警告</div>
<div className="bg-info text-info-foreground">信息</div>
```

---

## 常见问题及快速修复方法

| 症状 | 原因 | 修复 |
|-------|-------|-----|
| `bg-primary` 不工作 | 缺少 `@theme inline` 映射 | 添加 `@theme inline` 块 |
| 颜色全部为黑/白 | 双重 `hsl()` 包装 | 使用 `var(--color)` 而不是 `hsl(var(--color))` |
| 暗黑模式不切换 | 缺少 ThemeProvider | 将 App 包裹在 `<ThemeProvider>` 内 |
| 构建失败 | 存在 `tailwind.config.ts` | 删除该文件 |
| 文本不可见 | 对比度颜色错误 | 检查 `:root`/`.dark` 中的颜色定义 |

查看 `reference/common-gotchas.md` 获取完整的故障排除指南。

---

## 文件模板

所有模板都可在 `templates/` 目录中找到:

- **index.css** - 完整的 CSS 设置，包含所有颜色变量
- **components.json** - shadcn/ui v4 配置
- **vite.config.ts** - Vite + Tailwind 插件设置
- **tsconfig.app.json** - 带路径别名的 TypeScript
- **theme-provider.tsx** - 带 localStorage 的暗黑模式提供器
- **utils.ts** - 用于类合并的 `cn()` 工具

将这些文件复制到您的项目中并根据需要进行自定义。

---

## 完整配置清单

- [ ] 创建了 Vite + React + TypeScript 项目
- [ ] 安装了 `@tailwindcss/vite` (不是 postcss)
- [ ] `vite.config.ts` 使用 `tailwindcss()` 插件
- [ ] `tsconfig.json` 配置了路径别名
- [ ] 存在 `components.json` 且 `"config": ""`
- [ ] 不存在 `tailwind.config.ts` 文件
- [ ] `src/index.css` 遵循 v4 模式:
  - [ ] `:root` 和 `.dark` 在根级别 (不在 @layer 内)
  - [ ] 颜色用 `hsl()` 包装
  - [ ] `@theme inline` 映射所有变量
  - [ ] `@layer base` 使用未包装的变量
- [ ] 安装了主题提供器并包裹 App
- [ ] 创建了暗黑模式切换组件
- [ ] 在浏览器中测试主题切换是否正常工作

---

## 高级主题

加载 `references/advanced-usage.md` 获取高级模式，包括:

- **自定义颜色**: 添加默认调色板之外的语义颜色
- **v3 迁移**: 查看 `references/migration-guide.md` 获取完整指南
- **组件最佳实践**: 语义标记、cn() 工具、组合模式

**快速示例**:
```css
:root { --brand: hsl(280 65% 60%); }
@theme inline { --color-brand: var(--brand); }
```
使用方法: `<div className="bg-brand">品牌化</div>`

有关详细模式和组件组合示例，请加载 `references/advanced-usage.md`。

---

## 依赖项

### ✅ 安装这些

```json
{
  "dependencies": {
    "tailwindcss": "^4.1.17",
    "@tailwindcss/vite": "^4.1.17",
    "clsx": "^2.1.1",
    "tailwind-merge": "^3.3.1",
    "@radix-ui/react-*": "latest",
    "lucide-react": "^0.554.0",
    "react": "^19.2.0",
    "react-dom": "^19.2.0"
  },
  "devDependencies": {
    "@types/node": "^24.10.1",
    "@vitejs/plugin-react": "^5.2.0",
    "vite": "^7.2.4",
    "typescript": "~5.9.3"
  }
}
```

### ❌ 永远不要安装这些 (v4 中已弃用)

```bash
# 这些包会导致构建错误:
bun add tailwindcss-animate  # ❌ 已弃用
# 或: npm install tailwindcss-animate  # ❌ 已弃用

bun add tw-animate-css      # ❌ 不存在
```

**如果您看到这些包的导入错误**，请删除它们，改用原生 CSS 动画或 `@tailwindcss/motion`。

---

## Tailwind v4 插件

Tailwind v4 支持使用 CSS 中的 `@plugin` 指令的官方插件。

**快速示例**:
```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

**常见错误**:
❌ 错误: `@import "@tailwindcss/typography"` (不工作)
✅ 正确: `@plugin "@tailwindcss/typography"` (使用 @plugin 指令)

**内置功能**: 容器查询现在是核心 (不需要 `@tailwindcss/container-queries` 插件)。

加载 `references/plugins-reference.md` 获取完整文档，包括 Typography 插件 (prose 类)、Forms 插件、安装步骤和常见插件错误。

---

## 参考文档

为深入理解，请参阅:

- **common-gotchas.md** - 所有可能导致失败的方... (文档被截断)
