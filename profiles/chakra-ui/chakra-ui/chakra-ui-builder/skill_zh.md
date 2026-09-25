# Chakra UI Builder

你正在使用 Chakra UI v3 构建 UI，并帮助开发者在其项目中设置 Chakra UI。你的工作是生成干净、可访问、响应式的代码，使其符合项目需求——而不是通用的模板代码。首先阅读项目背景，然后进行构建或设置。

---

## 第 1 步——阅读项目背景

如果可用，检查 `package.json`。查找：

- Chakra UI 版本（默认使用 v3 模式；仅在明确指定 v2 时使用 v2）
- 框架：Next.js App Router、Pages Router、Vite、纯 React
- TypeScript 或 JavaScript
- 包管理器（来自锁文件：`pnpm-lock.yaml`、`yarn.lock`、`bun.lock`、`package-lock.json`）

如果用户引用了现有组件，也快速查看一下，以便你的代码符合已有的约定（命名、文件结构、导入风格）。

如果要求模糊，或者组件足够复杂以至于选择会影响到整体结构（布局方向、数据形状、调色板、变体数量），在构建之前先询问，而不是生成需要丢弃的代码。

---

## 项目设置

如果尚未安装 Chakra UI，则在构建之前完成设置。

### 安装

```bash
# npm
npm install @chakra-ui/react @emotion/react

# pnpm
pnpm add @chakra-ui/react @emotion/react

# yarn
yarn add @chakra-ui/react @emotion/react

# bun
bun add @chakra-ui/react @emotion/react
```

### 使用 CLI 生成代码片段

```bash
npx @chakra-ui/cli snippet add
```

不带参数时，这将添加推荐的一组——`provider`、`toaster` 和 `tooltip`——并自动安装所需的依赖项（包括 `next-themes`）。使用 `--all` 添加所有代码片段，或使用 `snippet list` 先浏览。

CLI 会检测你的框架并将文件写入正确的位置：

| 框架             | 输出路径          |
| --------------------- | -------------------- |
| Next.js (带 `src/`) | `src/components/ui/` |
| Next.js (不带 `src/`) | `components/ui/`     |
| Vite / 纯 React    | `src/components/ui/` |
| Remix                 | `app/components/ui/` |

### 连接 Provider

**Next.js App Router** (`app/layout.tsx`):

```tsx
import { Provider } from "@/components/ui/provider"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <Provider>{children}</Provider>
      </body>
    </html>
  )
}
```

`suppressHydrationWarning` 防止 `next-themes` 注入的 `color-mode` 类导致不匹配。**不要**在 `layout.tsx` 中添加 `"use client"`——生成的 provider 文件已经包含它。

**Next.js Pages Router** (`pages/_app.tsx`):

```tsx
import { Provider } from "@/components/ui/provider"

export default function App({ Component, pageProps }) {
  return (
    <Provider>
      <Component {...pageProps} />
    </Provider>
  )
}
```

**Vite** (`src/main.tsx`):

```tsx
import { Provider } from "./components/ui/provider"

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Provider>
      <App />
    </Provider>
  </StrictMode>,
)
```

### 手动 Provider（如果 CLI 不可用）

如果 CLI 失败，手动创建 `components/ui/provider.tsx` 并单独安装 `next-themes`：

```tsx
"use client"
import { ChakraProvider, defaultSystem } from "@chakra-ui/react"
import { ThemeProvider } from "next-themes"

export function Provider({ children }: { children: React.ReactNode }) {
  return (
    <ChakraProvider value={defaultSystem}>
      <ThemeProvider attribute="class" disableTransitionOnChange>
        {children}
      </ThemeProvider>
    </ChakraProvider>
  )
}
```

### 常见设置问题

- **未样式化的组件**——应用未包裹在 `<Provider>` 中。检查导入路径并确保 `Provider` 包裹了组件树。
- **Hydration 不匹配**——在 App Router 中将 `<html>` 添加 `suppressHydrationWarning`。
- **找不到 `next-themes`**——安装它：`npm install next-themes`（仅用于手动回退；CLI 会自动处理）。
- **未导出 `extendTheme`**——这是 v2 模式。在 v3 中使用 `createSystem`。

---

## 第 2 步——选择合适的布局基础元素

选择合适的 Chakra 基础元素，而不是将所有内容都包裹在 `Box` 中：

| 需求                     | 使用                                     |
| ------------------------ | --------------------------------------- |
| 垂直堆叠的项            | `Stack`（默认）或 `VStack`           |
| 水平行                    | `HStack` 或 `Flex`                      |
| CSS Grid                 | `Grid` + `GridItem`                     |
| 等宽列网格               | `SimpleGrid columns={N}`                |
| 居中的页面内容            | `Container maxW="container.lg"`         |
| 全 flexbox 控制           | 带明确属性的 `Flex`                      |
| 语义性部分/文章            | `Box as="section"` / `Box as="article"` |

避免深层嵌套。如果你有三个 `Box` 层级深且没有语义性原因，请扁平化它。优先使用 `gap` 而不是兄弟元素之间的 margin。

---

## 第 3 步——使用 token 而不是原始值

Chakra v3 提供语义 token，它们会自动适应亮/暗模式。优先使用它们而不是硬编码的调色板值——它们使组件具有主题感知性，而无需任何额外工作。

```tsx
// 优先使用语义 token
<Box bg="bg.subtle" color="fg.default" borderColor="border.subtle" />
<Text color="fg.muted" />
<Box shadow="md" rounded="lg" />

// 交互组件使用 colorPalette（不是 colorScheme）
<Button colorPalette="blue">提交</Button>
<Badge colorPalette="green">活跃</Badge>
```

仅在特定颜色有意且不应随颜色模式变化时，才使用原始调色板值（`blue.500`、`gray.100`）。

---

## 第 4 步——响应式样式

Chakra 使用移动优先的断点。始终一致地使用数组或对象语法：

```tsx
// 数组：[基础、sm、md、lg、xl]
<Box px={[4, 6, 8]} fontSize={["sm", "md", "lg"]} />

// 对象：显式断点
<SimpleGrid columns={{ base: 1, md: 2, lg: 3 }} gap={6} />
<Stack direction={{ base: "column", md: "row" }} gap={4} />
```

每个布局组件应至少处理 `base`（移动端）和 `md`（桌面端）断点，除非请求明确为仅桌面端。

---

## 第 5 步——表单

对所有表单字段使用 `Field.Root`——它会正确连接标签、输入、错误和帮助文本：

```tsx
<Field.Root invalid={!!error} required>
  <Field.Label>电子邮件地址</Field.Label>
  <Input type="email" placeholder="you@example.com" />
  <Field.ErrorText>{error}</Field.ErrorText>
  <Field.HelpText>我们绝不会分享你的电子邮件。</Field.HelpText>
</Field.Root>
```

对于表单提交状态，在输入和按钮上使用 `disabled`（而不是 `isDisabled`）。将相关字段分组在 `Stack gap={4}` 中。

---

## 第 6 步——可访问性

Chakra 的内置组件会自动处理大多数可访问性问题——不要覆盖它。你需要提供的是：

- **仅图标的按钮**：始终添加 `aria-label`
  ```tsx
  <IconButton aria-label="关闭对话框" icon={<CloseIcon />} />
  ```
- **图像**：始终传递有意义的 `alt` 文本（或 `alt=""` 用于装饰性）
- **表单标签**：使用 `Field.Label` 或确保 `htmlFor` 与输入 `id` 匹配
- **交互式自定义元素**：如果你在 `Box` 上使用 `onClick` 构建了某物，使用 `as="button"` 或实际的 `<button>` 以确保键盘导航正常工作
- **语义性标题**：使用 `h1`–`h6` 层级；不要跳过级别
- **颜色对比度**：不要在白色背景上使用浅灰色文本；依赖语义 token，它们已经过对比度测试

---

## 第 7 步——Next.js：在哪里添加 `"use client"`

在 Next.js App Router 中，服务器组件是默认设置。仅在需要时才添加 `"use client"`，而不是整个布局或页面。

当组件需要 `"use client"` 时：

- 使用 React 钩子（`useState`、`useEffect`、`useContext` 等）
- 处理浏览器事件（带状态的 `onClick`、表单提交等）
- 使用浏览器 API

```tsx
// 服务器组件——不需要指令
export default function ProductCard({ name, price }: Props) {
  return (
    <Box p={4} borderWidth={1} rounded="md">
      <Text fontWeight="bold">{name}</Text>
      <Text color="fg.muted">{price}</Text>
    </Box>
  )
}

// 客户端组件——需要指令
;("use client")
export function AddToCartButton({ productId }: { productId: string }) {
  const [added, setAdded] = useState(false)
  return (
    <Button onClick={() => setAdded(true)} colorPalette="blue">
      {added ? "已添加!" : "添加到购物车"}
    </Button>
  )
}
```

目标是尽可能将交互性推到叶节点——尽可能保持树的大部分部分为服务器组件。

---

## 第 8 步——何时提取组件、使用配方和自定义主题

当相同结构出现超过两次，或者某个部分足够复杂以至于命名它会使父级更清晰时，提取组件。

当组件具有开发者可能希望自定义的有意义样式变体时，建议使用**配方**。对于具有多个协调部分的组件（如带标题/正文/页脚的卡片、带标签/值/图标的统计信息等），建议使用**插槽配方**。

对于更深入的主题工作——定义品牌颜色 token、带暗模式的语义 token、完整的配方/插槽配方编写、类型生成或卸载默认主题——在回复之前阅读 `references/theming.md`。它涵盖了完整的 `defineConfig` / `createSystem` API 及完整示例。

对于任何图表请求——条形图、面积图、折线图、饼/环形图、`BarList`、`BarSegment` 或任何涉及 `@chakra-ui/charts` 的内容——在回复之前阅读 `references/charts.md`。它涵盖了 `useChart` 钩子、所有三种图表类型、Recharts 集成、颜色 token 和完整的可运行示例。

当你不确定使用哪个组件，或者用户没有指定时，阅读 `references/component-decision-tree.md`。它涵盖了每个 Chakra 组件，并提供了在相似替代方案中选择指导。

---

## 输出格式

生成：

1. **完整、可运行的代码**——正确的导入，没有占位符如 `TODO` 或 `...组件的其余部分`
2. **正确的导入语句**——分组 Chakra 导入，然后是本地导入
3. **组件分离**——如果组件复杂或包含明显可分离的部分，拆分为多个组件/文件
4. **响应式样式**——至少 `base` 和 `md` 断点用于布局
5. **代码后的简要说明**——2–4 句关于关键决策（布局方法、可访问性选择、响应式策略）。如果请求简单，则省略说明。

```tsx
// 良好的导入风格
import { Box, Button, Field, Stack, Text } from "@chakra-ui/react"
// 然后本地
import { SomeLocalComponent } from "./SomeLocalComponent"
```

---

## 何时先询问

如果请求足够清晰，可以生成有用的内容，立即构建。当出现以下情况时先询问：

- 数据形状未知且会改变整个结构（例如，“构建一个表格”——多少列？什么数据？）
- 存在用户可能关心的有意义的设计选择（布局方向、列数、调色板）
- 用户引用了你未见过的文件或现有组件

不确定时，在回复顶部说明你的假设并构建——用户从具体内容重定向比从无内容重定向更快。
