# HeroUI v3 React 开发指南

HeroUI v3 是基于 **Tailwind CSS v4** 和 **React Aria Components** 构建的组件库，为 React 应用程序提供可访问、可定制的 UI 组件。

---

## 安装

```bash
curl -fsSL https://heroui.com/install | bash -s heroui-react
```

---

## 关键提示：仅限 v3 - 忽略 v2 知识

**本指南仅适用于 HeroUI v3。** 请勿使用 v2 模式——提供者、样式和组件 API 全部已更改：

| 功能       | v2（勿使用）                   | v3（使用此模式）                               |
| ------------- | --------------------------------- | ------------------------------------------- |
| 提供      | 需要 `<HeroUIProvider>`       | **无需提供者**                      |
| 动画      | `framer-motion` 包           | CSS 基础，无需额外依赖                    |
| 组件 API | 扁平属性：`<Card title="x">`    | 复合：`<Card><Card.Header>`             |
| 样式       | Tailwind v3 + `@heroui/theme`     | Tailwind v4 + `@heroui/styles`         	  |
| 包        | `@heroui/system`, `@heroui/theme` | `@heroui/react`, `@heroui/styles` 		  |

```tsx
// 勿这样做 - v2 模式
import { HeroUIProvider } from "@heroui/react";
import { motion } from "framer-motion";

<HeroUIProvider>
	<Card title="Product" description="A great product" />
</HeroUIProvider>;
```

### 正确（v3 模式）

```tsx
// 这样做 - v3 模式（无需提供者，复合组件）
import { Card } from "@heroui/react";

<Card>
	<Card.Header>
		<Card.Title>Product</Card.Title>
		<Card.Description>A great product</Card.Description>
	</Card.Header>
</Card>;
```

**实施前始终获取 v3 文档。**

---

## 核心原则

- 语义变体（`primary`、`secondary`、`tertiary`）优于视觉描述
- 组合优于配置（复合组件）
- 基于 CSS 变量的主题化，使用 `oklch` 色彩空间
- 使用 BEM 命名约定以实现可预测的样式

---

## 访问文档和组件信息

**对于组件的详细信息、示例、属性和实现模式，始终获取文档：**

### 使用脚本

```bash
# 列出所有可用组件
node scripts/list_components.mjs

# 获取组件文档（MDX）
node scripts/get_component_docs.mjs Button
node scripts/get_component_docs.mjs Button Card TextField

# 获取组件源代码
node scripts/get_source.mjs Button

# 获取组件 CSS 样式（BEM 类）
node scripts/get_styles.mjs Button

# 获取主题变量
node scripts/get_theme.mjs

# 获取非组件文档（指南、发布）
node scripts/get_docs.mjs /docs/react/getting-started/theming
```

### 直接 MDX URL

组件文档：使用具体的 kebab-case 斜杠路径获取 `.mdx`。当路径未知时，运行 `node scripts/list_components.mjs`，并始终避免获取包含占位符的 URL。

示例：

- 按钮：`https://heroui.com/docs/react/components/button.mdx`
- 模态框：`https://heroui.com/docs/react/components/modal.mdx`
- 表单：`https://heroui.com/docs/react/components/form.mdx`

入门指南：使用具体的主题 URL，例如 `https://heroui.com/docs/react/getting-started/quick-start.mdx`。

**重要提示：** 实施前始终获取组件文档。MDX 文档包含完整的示例、属性、结构和 API 参考。

---

## 安装要点

### 快速安装

```bash
npm i @heroui/styles @heroui/react tailwind-variants
```

### 框架设置（Next.js App Router - 推荐）

1. **安装依赖项：**

```bash
npm i @heroui/styles @heroui/react tailwind-variants tailwindcss @tailwindcss/postcss postcss
```

2. **创建/更新 `app/globals.css`：**

```css
/* Tailwind CSS v4 - 必须首先 */
@import "tailwindcss";

/* HeroUI v3 样式 - 必须在 Tailwind 之后 */
@import "@heroui/styles";
```

3. **在 `app/layout.tsx` 中导入：**

```tsx
import "./globals.css";

export default function RootLayout({
	children,
}: {
	children: React.ReactNode;
}) {
	return (
		<html lang="en" suppressHydrationWarning>
			<body>
				{/* HeroUI v3 中无需提供者！ */}
				{children}
			</body>
		</html>
	);
}
```

4. **配置 PostCSS (`postcss.config.mjs`)：**

```js
export default {
	plugins: {
		"@tailwindcss/postcss": {},
	},
};
```

### 关键设置要求

1. **必须使用 Tailwind CSS v4** - HeroUI v3 无法与 Tailwind CSS v3 一起工作
2. **使用复合组件** - 组件使用复合结构（例如，`Card.Header`、`Card.Content`）
3. **使用 onPress 而不是 onClick** - 为更好的可访问性，使用 `onPress` 事件处理程序
4. **导入顺序很重要** - 始终在 HeroUI 样式之前导入 Tailwind CSS

---

## 组件模式

所有组件都使用上述的**复合模式**（如 `Card.Header`、`Card.Content` 这样的点表示法子组件）。不要扁平化为属性——始终使用子组件进行组合。获取组件文档以获取完整的结构和示例。

---

## 语义变体

HeroUI 使用语义命名来传达功能意图：

| 变体     | 目的                           | 使用          |
| ----------- | --------------------------------- | -------------- |
| `primary`   | 主要操作以继续前进       | 每个上下文 1 个 |
| `secondary` | 替代操作               | 多个       |
| `tertiary`  | 否定操作（取消、跳过） | 稀疏      |
| `danger`    | 破坏性操作               | 当需要时    |
| `ghost`     | 低强调操作              | 最小权重    |
| `outline`   | 替代操作                 | 边框样式    |

**不要使用原始颜色** - 语义变体会根据主题和可访问性进行调整。

---

## 主题化

HeroUI v3 使用 `oklch` 色彩空间的 CSS 变量：

```css
:root {
	--accent: oklch(0.6204 0.195 253.83);
	--accent-foreground: var(--snow);
	--background: oklch(0.9702 0 0);
	--foreground: var(--eclipse);
}
```

**获取当前主题变量：**

```bash
node scripts/get_theme.mjs
```

**颜色命名：**

- 无后缀 = 背景（例如，`--accent`）
- 带 `-foreground` = 文本颜色（例如，`--accent-foreground`）

**主题切换：**

```html
<html class="dark" data-theme="dark"></html>
```

对于详细的主题化，获取：`https://heroui.com/docs/react/getting-started/theming.mdx`
