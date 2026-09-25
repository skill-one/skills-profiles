# Tailwind CSS & shadcn/ui 设计系统

## 概述

使用 Tailwind CSS (v4.1+) 和 shadcn/ui 创建和管理集中式设计系统的专家指南。此技能提供结构化的工作流程，用于定义设计令牌、使用 CSS 变量配置主题，并基于 shadcn/ui 基础元素构建一致的 UI 组件库。

**与其他技能的关系：**
- **tailwind-css-patterns** 涵盖实用优先样式、响应式设计和一般 Tailwind CSS 使用方法
- **shadcn-ui** 涵盖单个组件的安装、配置和实现
- **此技能** 专注于系统级的编排：设计令牌、主题基础设施、组件封装模式，并确保整个应用程序的一致性

## 何时使用

- 使用 Tailwind CSS 和 shadcn/ui 从零开始设置新的设计系统
- 将设计令牌（颜色、排版、间距、圆角、阴影）定义为 CSS 变量
- 使用集中式主题系统配置 `globals.css`（亮色/暗色模式）
- 将 shadcn/ui 组件封装为具有强制约束的设计系统基础元素
- 构建基于令牌的一致 UI 组件库
- 从基于 JavaScript 的 Tailwind 配置迁移到 CSS 优先配置（v4.1+）
- 使用 oklch 格式建立具有感知均匀性的调色板
- 创建超越亮色/暗色的多主题支持（例如，品牌主题）

## 说明

### 第 1 步：初始化设计系统配置

运行以下命令设置项目：

```bash
# 检查 Tailwind 是否已安装
npx tailwindcss --version

# 对于 Tailwind v4（推荐）
npx @tailwindcss/vite@latest init   # 或: npm install -D tailwindcss @tailwindcss/vite

# 初始化 shadcn/ui CLI
npx shadcn@latest init

# 安装核心 shadcn/ui 组件
npx shadcn@latest add button card input -y
```

**验证检查点**：设置后，验证：
```bash
ls src/components/ui/        # 应列出已安装的组件
cat src/app/globals.css       # 应包含 @tailwind 指令
```

### 第 2 步：定义设计令牌

创建 `src/app/globals.css` 并包含您的设计令牌：

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    /* 品牌颜色 */
    --primary: oklch(0.55 0.18 250);
    --primary-foreground: oklch(0.985 0 0);

    /* 语义颜色 */
    --background: oklch(0.99 0 0);
    --foreground: oklch(0.15 0 0);
    --secondary: oklch(0.96 0.01 250);
    --secondary-foreground: oklch(0.20 0 0);

    /* 验证：所有颜色必须有前景色配对 */
    --destructive: oklch(0.55 0.22 25);
    --destructive-foreground: oklch(0.985 0 0);
  }

  .dark {
    --primary: oklch(0.65 0.20 250);
    --background: oklch(0.14 0 0);
    --foreground: oklch(0.97 0 0);
    --secondary: oklch(0.25 0.02 250);
  }
}
```

**验证检查点**：验证令牌是否为有效的 CSS：
```bash
grep -E "^[[:space:]]*--[a-z-]+:" src/app/globals.css | wc -l
# 应返回定义的令牌数量（例如，10+）
```

### 第 3 步：配置主题基础设施

将 CSS 变量桥接到 Tailwind 工具（Tailwind v4.1+）：

```css
@theme inline {
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
  --color-background: var(--background);
  --color-foreground: var(--foreground);
}
```

在 `components/providers/theme-provider.tsx` 中添加暗色模式类切换：
```tsx
import { useEffect } from "react";
export function ThemeProvider({ children }: { children: React.ReactNode }) {
  useEffect(() => {
    const isDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    document.documentElement.classList.toggle("dark", isDark);
  }, []);
  return <>{children}</>;
}
```

**验证检查点**：测试暗色模式：
```bash
document.documentElement.classList.contains("dark") // 在浏览器控制台中
```

### 第 4 步：封装 shadcn/ui 组件

创建 `src/components/ds/Button.tsx`：
```tsx
import { Button as ShadcnButton } from "@/components/ui/button";

type DSVariant = "primary" | "secondary" | "destructive" | "ghost";
const variantMap: Record<DSVariant, "default" | "secondary" | "destructive" | "ghost"> = {
  primary: "default", secondary: "secondary",
  destructive: "destructive", ghost: "ghost",
};

export function Button({ variant = "primary", ...props }: { variant?: DSVariant } & React.ComponentProps<typeof ShadcnButton>) {
  return <ShadcnButton variant={variantMap[variant]} {...props} />;
}
```

**验证检查点**：验证构建是否通过：
```bash
npx tsc --noEmit src/components/ds/Button.tsx
```

### 第 5 步：验证和文档化

运行令牌验证脚本：
```bash
REQUIRED=("primary" "primary-foreground" "background" "foreground" "secondary" "secondary-foreground")
for token in "${REQUIRED[@]}"; do
  grep -q "$token:" src/app/globals.css || echo "MISSING: --$token"
done
```

**验证检查点**：确保所有 shadcn 组件使用 DS 令牌：
```bash
grep -r "bg-primary\|text-primary\|bg-background" src/components/ds/
```

## 示例

### 添加自定义令牌

在 `globals.css` 中扩展基础令牌：

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}

.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}

@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

使用：`<div className="bg-warning text-warning-foreground">Warning</div>`

### 将 shadcn/ui 组件封装为设计系统基础元素

参考 `references/component-wrapping.md` 获取完整的示例，包括 Button、Text 和 Stack 基础元素及其完整的 TypeScript 类型。

创建受约束的设计系统组件，强制使用令牌。
内联示例：

```tsx
import { Button as ShadcnButton } from "@/components/ui/button";

export function Button({ variant = "primary", size = "md", ...props }) {
  const variantMap = { primary: "default", secondary: "secondary" };
  const sizeMap = { sm: "sm", md: "default", lg: "lg" };
  return (
    <ShadcnButton
      variant={variantMap[variant]}
      size={sizeMap[size]}
      {...props}
    />
  );
}
```

### 多主题支持

对于需要超越亮色/暗色的多品牌主题的应用程序：

```css
[data-theme="ocean"] {
  --primary: oklch(0.55 0.18 230);
  --primary-foreground: oklch(0.985 0 0);
}

[data-theme="forest"] {
  --primary: oklch(0.50 0.15 145);
  --primary-foreground: oklch(0.985 0 0);
}
```

```tsx
const [theme, setTheme] = useState("light");
useEffect(() => {
  document.documentElement.setAttribute("data-theme", theme);
}, [theme]);
```

### 设计令牌验证

验证所有必需的令牌是否已定义：

```bash
#!/bin/bash
REQUIRED=("--background" "--foreground" "--primary" "--primary-foreground")
for token in "${REQUIRED[@]}"; do
  grep -q "$token:" src/styles/globals.css || echo "Missing: $token"
done
```

## 限制和警告

- **oklch 颜色格式**：使用 oklch 以实现感知均匀性。并非所有浏览器都原生支持 oklch；如果针对旧版浏览器，请检查兼容性
- **令牌命名**：遵循 shadcn/ui 的约定（`--primary`，`--primary-foreground`）以实现无缝集成
- **`@`theme inline vs `@`theme**：当将 CSS 变量桥接到 Tailwind 工具时使用 `@theme inline`；使用 `@theme` 直接定义令牌
- **组件封装**：保持封装组件尽可能轻量。仅添加强制设计系统规则的约束；避免重复 shadcn/ui 逻辑
- **暗色模式**：始终在 `:root` 中定义每个令牌的暗色模式值。缺少暗色令牌会导致视觉回归
- **CSS 变量作用域**：在 `:root` 中定义的令牌是全局的。使用 `[data-theme]` 选择器以避免多主题冲突
- **性能**：避免过多的 CSS 自定义属性链。每个 `var()` 查找会带来微小的非零开销
- **Tailwind v4 vs v3**：`@theme` 指令和 `@theme inline` 是 v4.1+ 功能。对于 v3 项目，使用 `tailwind.config.js` 并使用 `theme.extend`

## 最佳实践

1. **单一事实来源**：所有设计令牌都位于 `globals.css`。组件中切勿硬编码颜色值
2. **语义命名**：使用基于用途的名称（`--primary`，`--destructive`）而不是基于外观的名称（`--blue-500`，`--red-600`）
3. **前景色配对**：每个背景令牌都必须有一个匹配的 `-foreground` 令牌以符合对比度合规性
4. **令牌范围**：为自定义调色板定义完整的范围（50-950）以提供灵活性
5. **组件条目导出**：从单个 `index.ts` 导出所有 DS 组件以实现干净的导入
6. **可访问性**：确保所有令牌对（背景/前景）符合 WCAG AA 对比度（文本 4.5:1，大文本 3:1）
7. **文档化令牌**：为团队维护所有令牌的视觉参考
8. **一致间距**：通过 DS 组件使用 Tailwind 的间距范围（`gap-2`，`gap-4`，`gap-6`）而不是任意值

## 参考

- Tailwind CSS v4 主题配置：https://tailwindcss.com/docs/theme
- Tailwind CSS 函数和指令：https://tailwindcss.com/docs/functions-and-directives
- shadcn/ui 主题指南：https://ui.shadcn.com/docs/theming
- shadcn/ui 手动安装：https://ui.shadcn.com/docs/installation/manual
- oklch 色彩空间：https://oklch.com
