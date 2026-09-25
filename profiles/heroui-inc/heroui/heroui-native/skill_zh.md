# HeroUI 原生开发指南

HeroUI Native 是基于 **Uniwind (React Native 的 Tailwind CSS)** 和 **React Native** 构建的一个组件库，为移动应用程序提供可访问、可定制的 UI 组件。

---

## 安装

```bash
curl -fsSL https://heroui.com/install | bash -s heroui-native
```

---

## 关键提示：仅限原生 - 请勿使用 Web 模式

**本指南仅适用于 HeroUI Native。** 请勿应用 HeroUI React (Web) 模式——包、样式引擎和颜色格式均不同：

| 功能      | React (Web)          | 原生 (移动)                     |
| --------- | -------------------- | -------------------------------- |
| **样式**  | Tailwind CSS v4      | Uniwind (React Native 的 Tailwind) |
| **颜色**   | oklch 格式         | HSL 格式                          |
| **包**    | `@heroui/react`      | `heroui-native`                  |
| **平台**  | Web 浏览器         | iOS & Android                    |

```tsx
// 正确——原生模式
import { Button } from "heroui-native";

<Button variant="primary" onPress={() => console.log("Pressed!")}>
	Click me
</Button>;
```

**实施前请始终查阅原生文档。**

---

## 核心原则

- 语义变体 (`primary`, `secondary`, `tertiary`) 优先于视觉描述
- 组合优于配置（复合组件）
- 使用 HSL 颜色格式的主题变量
- 使用 Uniwind 工具的 React Native StyleSheet 模式

---

## 访问文档和组件信息

**对于组件的详细信息、示例、属性和实施模式，请始终查阅文档：**

### 使用脚本

```bash
# 列出所有可用组件
node scripts/list_components.mjs

# 获取组件文档 (MDX)
node scripts/get_component_docs.mjs Button
node scripts/get_component_docs.mjs Button Card TextField

# 获取主题变量
node scripts/get_theme.mjs

# 获取非组件文档（指南、发布）
node scripts/get_docs.mjs /docs/native/getting-started/theming
```

### 直接 MDX URL

组件文档：使用具体的 kebab-case 斜杠命名。当 URL 不确定时，运行 `node scripts/list_components.mjs`，并切勿获取仍包含占位符的 URL。

示例：

- 按钮：`https://heroui.com/docs/native/components/button.mdx`
- 对话框：`https://heroui.com/docs/native/components/dialog.mdx`
- 文本字段：`https://heroui.com/docs/native/components/text-field.mdx`

入门指南：使用具体的主题 URL，例如 `https://heroui.com/docs/native/getting-started/quick-start.mdx`。

**重要提示：** 实施前请始终查阅组件文档。MDX 文档包含完整的示例、属性、结构和 API 参考。

---

## 安装要点

### 快速安装

```bash
npm i heroui-native react-native-reanimated react-native-gesture-handler react-native-safe-area-context @gorhom/bottom-sheet react-native-svg react-native-worklets tailwind-merge tailwind-variants
```

### 框架设置（推荐使用 Expo）

1. **安装依赖项：**

```bash
npx create-expo-app MyApp
cd MyApp
npm i heroui-native uniwind tailwindcss
npm i react-native-reanimated react-native-gesture-handler react-native-safe-area-context @gorhom/bottom-sheet react-native-svg react-native-worklets tailwind-merge tailwind-variants
```

2. **创建 `global.css`：**

```css
@import "tailwindcss";
@import "uniwind";
@import "heroui-native/styles";

@source "./node_modules/heroui-native/lib";
```

3. **用提供者包裹应用：**

```tsx
import { GestureHandlerRootView } from "react-native-gesture-handler";
import { HeroUINativeProvider } from "heroui-native";
import "./global.css";

export default function Layout() {
	return (
		<GestureHandlerRootView style={{ flex: 1 }}>
			<HeroUINativeProvider>
				<App />
			</HeroUINativeProvider>
		</GestureHandlerRootView>
	);
}
```

### 关键设置要求

1. **必须使用 Uniwind** - HeroUI Native 使用 Uniwind (React Native 的 Tailwind CSS)
2. **必须使用 HeroUINativeProvider** - 用 `HeroUINativeProvider` 包裹你的应用
3. **必须使用 GestureHandlerRootView** - 用 `GestureHandlerRootView` 从 `react-native-gesture-handler` 包裹
4. **使用复合组件** - 组件使用复合结构（例如，`Card.Header`, `Card.Body`）
5. **使用 onPress 而不是 onClick** - React Native 使用 `onPress` 事件处理器
6. **平台特定代码** - 使用 `Platform.OS` 处理 iOS/Android 差异

---

## 组件模式

HeroUI Native 使用 **复合组件模式**。每个组件都有通过点表示法访问的子组件。

**示例 - 卡片：**

```tsx
<Card>
	<Card.Header>{/* 图标、徽章 */}</Card.Header>
	<Card.Body>
		<Card.Title>Title</Card.Title>
		<Card.Description>Description</Card.Description>
	</Card.Body>
	<Card.Footer>{/* 操作 */}</Card.Footer>
</Card>
```

**要点：**

- 始终使用复合结构——不要展平为属性
- 通过点表示法访问子组件（例如，`Card.Header`）
- 原生卡片使用 `Card.Body`（不是 `Card.Content`）；标题和描述在 Body 内部
- **查阅组件文档以获取完整结构和示例**

---

## 语义变体

HeroUI 使用语义命名来传达功能意图：

| 变体       | 目的                           | 使用方式          |
| ---------- | ------------------------------ | ----------------- |
| `primary`     | 主要操作以推进流程             | 每个上下文 1 个    |
| `secondary`   | 替代操作                       | 多个              |
| `tertiary`    | 否定操作（取消、跳过）         | 谨慎使用          |
| `danger`      | 破坏性操作                     | 按需使用          |
| `danger-soft` | 轻微破坏性操作                 | 较少突出          |
| `ghost`       | 低强调操作                     | 最小权重          |
| `outline`     | 替代操作                       | 边框样式          |

**不要使用原始颜色** - 语义变体会根据主题和可访问性进行调整。

---

## 主题

HeroUI Native 使用 Tailwind/Uniwind 的 CSS 变量进行主题设置。主题颜色定义在 `global.css` 中：

```css
@theme {
	--color-accent: hsl(260, 100%, 70%);
	--color-accent-foreground: hsl(0, 0%, 100%);
}
```

**获取当前主题变量：**

```bash
node scripts/get_theme.mjs
```

**以编程方式访问主题颜色：**

```tsx
import { useThemeColor } from "heroui-native";

const accentColor = useThemeColor("accent");
```

**主题切换（浅色/深色模式）：**

```tsx
import { Uniwind, useUniwind } from "uniwind";

const { theme } = useUniwind();
Uniwind.setTheme(theme === "light" ? "dark" : "light");
```

详细主题设置请查阅：`https://heroui.com/docs/native/getting-started/theming.mdx`
