# Chakra UI 迁移：v2 → v3

你正在指导一位开发者将其项目从 Chakra UI v2 迁移到 v3。请按以下步骤依次操作。首先检查项目——切勿猜测包版本或框架。

> **Node 版本要求**：Chakra UI v3 需要 Node >= 20.x。如果环境不确定，请在继续操作前确认。

---

## 第 1 步 — 检查项目

阅读以下文件以了解当前状态：

```
package.json
```

查找：

- 当前 `@chakra-ui/react` 版本（v2.x 与 v3.x）
- 相关包：`@chakra-ui/icons`、`@chakra-ui/hooks`、`@chakra-ui/next-js`、`@emotion/styled`、`framer-motion`
- 框架：Next.js（App Router 或 Pages Router）、Vite、纯 React
- 包管理器（从锁文件中获取：`pnpm-lock.yaml`、`yarn.lock`、`bun.lock`、`package-lock.json`）

在需要时也检查关键文件：

- 提供者/主题设置（`_app.tsx`、`layout.tsx`、`theme.ts`）
- 颜色模式使用（`ColorModeScript`、`useColorMode`、`useColorModeValue`）
- 任何显示重 v2 模式的组件文件

---

## 第 2 步 — 更新包

### 移除仅 v2 依赖的包

```bash
# npm
npm uninstall @chakra-ui/icons @chakra-ui/hooks @chakra-ui/next-js @emotion/styled framer-motion

# pnpm
pnpm remove @chakra-ui/icons @chakra-ui/hooks @chakra-ui/next-js @emotion/styled framer-motion

# yarn
yarn remove @chakra-ui/icons @chakra-ui/hooks @chakra-ui/next-js @emotion/styled framer-motion
```

`@emotion/styled` 和 `framer-motion` 在 v3 中不再需要。

### 安装 v3 核心 包

```bash
# npm
npm install @chakra-ui/react @emotion/react

# pnpm
pnpm add @chakra-ui/react @emotion/react

# yarn
yarn add @chakra-ui/react @emotion/react
```

### 已移除包的替代方案

| 已移除              | 替代方案                                  |
| -------------------- | -------------------------------------------- |
| `@chakra-ui/icons`   | `lucide-react` 或 `react-icons`              |
| `@chakra-ui/hooks`   | `react-use` 或 `usehooks-ts`                 |
| `@chakra-ui/next-js` | `asChild` 属性模式（见 Next.js 部分） |

---

## 第 3 步 — 运行 codemod

官方 codemod 处理大多数机械性变更：组件重命名、属性更新、导入重写和复合组件重构。它不会替代人工审核——计划审核输出。

**先进行干运行（不更改文件）**：

```bash
npx @chakra-ui/codemod upgrade --dry
```

查看其提议。满意后：

```bash
npx @chakra-ui/codemod upgrade
```

codemod 后，在手动编辑前提交更改，以便从干净的 diff 进行工作。

---

## 第 4 步 — 更新提供者

### 旧的 v2 模式

```tsx
// v2
import { ChakraProvider } from "@chakra-ui/react"
import theme from "./theme"

;<ChakraProvider theme={theme}>{children}</ChakraProvider>
```

### 新的 v3 模式（使用 Chakra CLI 代码片段）

生成提供者和组件代码片段：

```bash
npx @chakra-ui/cli snippet add
```

这将创建 `components/ui/provider.tsx`（以及 `toaster` 和 `tooltip` 代码片段），并自动安装所需的 npm 依赖项——包括 `next-themes`。导入并使用它：

```tsx
// v3 — app/layout.tsx（Next.js App Router）
import { Provider } from "@/components/ui/provider"

;<html lang="en" suppressHydrationWarning>
  <body>
    <Provider>{children}</Provider>
  </body>
</html>
```

`Provider` 文件包含 `"use client"`——不要将其添加到 `layout.tsx`。见 Next.js 部分了解 Pages Router 的放置位置。

### v3 中的自定义主题

用 `createSystem` 替换 `extendTheme`：

```ts
// v2
import { extendTheme } from "@chakra-ui/react"
// v3
import { createSystem, defaultConfig, defineConfig } from "@chakra-ui/react"

export const theme = extendTheme({ colors: { brand: { 500: "#2196f3" } } })

const config = defineConfig({
  theme: { tokens: { colors: { brand: { 500: { value: "#2196f3" } } } } },
})
export const system = createSystem(defaultConfig, config)
```

通过 `value={system}` 将 `system` 传递给 `ChakraProvider`。

---

## 第 5 步 — 颜色模式迁移

### 移除所有 v2 颜色模式模式

```tsx
// 移除这些 v2 导入和使用：
import { ColorModeScript } from "@chakra-ui/react"
// ❌
import { useColorMode } from "@chakra-ui/react"
// ❌（使用 next-themes）
import { useColorModeValue } from "@chakra-ui/react"
// ❌（使用 CSS 令牌）
import { DarkMode, LightMode } from "@chakra-ui/react"

// ❌

// 也从 _document.tsx 中移除：
;<ColorModeScript initialColorMode={theme.config.initialColorMode} /> // ❌
```

### v3 颜色模式方法

颜色模式由 `next-themes` 通过生成的 `Provider` 处理。使用语义令牌，它们会自动响应当前的颜色模式：

```tsx
// 使用 Chakra 语义令牌——它们在暗黑模式下自动切换
<Box color="fg.default" bg="bg.subtle">
  ...
</Box>
```

对于颜色模式切换，使用生成的 `components/ui/color-mode.tsx` 代码片段或直接使用 `next-themes` 的 `useColorMode`。

---

## 第 6 步 — 属性重命名

这些布尔值和样式属性在 v3 中被重命名为与 HTML 和现代 React 的一致。codemod 捕获了大部分这些，但之后需要手动验证。

### 布尔值属性

| v2                | v3              |
| ----------------- | --------------- |
| `isOpen`          | `open`          |
| `defaultIsOpen`   | `defaultOpen`   |
| `isDisabled`      | `disabled`      |
| `isInvalid`       | `invalid`       |
| `isRequired`      | `required`      |
| `isReadOnly`      | `readOnly`      |
| `isChecked`       | `checked`       |
| `isLoaded`        | `loaded`        |
| `isIndeterminate` | `indeterminate` |

### 样式和布局属性

| v2                | v3                          |
| ----------------- | --------------------------- |
| `colorScheme`     | `colorPalette`              |
| `noOfLines`       | `lineClamp`                 |
| `truncated`       | `truncate`                  |
| `spacing` (Stack) | `gap`                       |
| `apply`           | `textStyle` 或 `layerStyle` |

### 嵌套样式属性

```tsx
// v2 — sx 嵌套伪选择器
<Box sx={{ "&:hover": { color: "blue.500" } }} />

// v3 — css 属性带 "&" 选择器
<Box css={{ "&:hover": { color: "blue.500" } }} />
```

---

## 第 7 步 — 组件迁移

### 重命名的组件

| v2            | v3                                  |
| ------------- | ----------------------------------- |
| `Modal`       | `Dialog`                            |
| `FormControl` | `Field`                             |
| `Select`      | `NativeSelect`                      |
| `AlertDialog` | `AlertDialog`（复合，见下文） |

`Modal` 是最常见的重命名——每个 `<Modal>`、`<ModalOverlay>`、`<ModalContent>`、`<ModalHeader>`、`<ModalBody>`、`<ModalFooter>` 和 `<ModalCloseButton>` 都变成 `Dialog.*` 复合部分：

```tsx
// v2
<Modal isOpen={open} onClose={onClose}>
  <ModalOverlay />
  <ModalContent>
    <ModalHeader>Title</ModalHeader>
    <ModalBody>Body</ModalBody>
    <ModalFooter><Button onClick={onClose}>Close</Button></ModalFooter>
  </ModalContent>
</Modal>

// v3
<Dialog.Root open={open} onOpenChange={({ open }) => setOpen(open)}>
  <Dialog.Backdrop />
  <Dialog.Positioner>
    <Dialog.Content>
      <Dialog.Header><Dialog.Title>Title</Dialog.Title></Dialog.Header>
      <Dialog.Body>Body</Dialog.Body>
      <Dialog.Footer><Button onClick={() => setOpen(false)}>Close</Button></Dialog.Footer>
      <Dialog.CloseTrigger />
    </Dialog.Content>
  </Dialog.Positioner>
</Dialog.Root>
```

### 复合组件重写

v3 采用了统一的复合组件 API。codemod 处理了许多这些，但复杂的自定义使用需要手动审核。

**Checkbox**

```tsx
// v2
<Checkbox isChecked={val} onChange={fn}>Label</Checkbox>

// v3
<Checkbox.Root checked={val} onCheckedChange={fn}>
  <Checkbox.Control><Checkbox.Indicator /></Checkbox.Control>
  <Checkbox.Label>Label</Checkbox.Label>
</Checkbox.Root>
```

**Progress**

```tsx
// v2
<Progress value={60} colorScheme="blue" />

// v3
<Progress.Root value={60} colorPalette="blue">
  <Progress.Track><Progress.Range /></Progress.Track>
</Progress.Root>
```

**Accordion**

```tsx
// v2
<Accordion><AccordionItem><AccordionButton /><AccordionPanel /></AccordionItem></Accordion>

// v3
<Accordion.Root>
  <Accordion.Item value="item-1">
    <Accordion.ItemTrigger />
    <Accordion.ItemContent />
  </Accordion.Item>
</Accordion.Root>
```

**FormControl → Field**

```tsx
// v2
<FormControl isInvalid={!!error} isRequired>
  <FormLabel>Email</FormLabel>
  <Input type="email" />
  <FormErrorMessage>{error}</FormErrorMessage>
  <FormHelperText>We'll never share your email.</FormHelperText>
</FormControl>

// v3
<Field.Root invalid={!!error} required>
  <Field.Label>Email</Field.Label>
  <Input type="email" />
  <Field.ErrorText>{error}</Field.ErrorText>
  <Field.HelpText>We'll never share your email.</Field.HelpText>
</Field.Root>
```

所有 `FormControl` 子部分映射到 `Field.*`：

- `FormLabel` → `Field.Label`
- `FormErrorMessage` → `Field.ErrorText`
- `FormHelperText` → `Field.HelpText`
- `FormControl` 属性 `isInvalid`、`isRequired`、`isDisabled` → `invalid`、`required`、`disabled`

**Dialog / Drawer / Menu / Tabs** 遵循相同的复合模式：使用 `ComponentName.Root`、`.Trigger`、`.Content`、`.Item` 等。查看 Chakra UI v3 文档以获取每个特定复合 API。

### Next.js Image 和 Link（替换 @chakra-ui/next-js）

```tsx
// v2 — @chakra-ui/next-js
import { LinkOverlay } from "@chakra-ui/next-js"

// v3 — asChild 模式
import NextLink from "next/link"
<ChakraLink asChild><NextLink href="/about">About</NextLink></ChakraLink>

import NextImage from "next/image"
<ChakraImage asChild><NextImage src="..." alt="..." /></ChakraImage>
```

---

## 第 8 步 — 主题迁移

### styleConfig 和 multiStyleConfig → recipes

```ts
// v3 — 单个组件（recipe）
import { defineRecipe } from "@chakra-ui/react"

// v2
const buttonStyle = {
  baseStyle: { fontWeight: "bold" },
  variants: { solid: { bg: "blue.500" } },
  defaultProps: { variant: "solid" },
}

const buttonRecipe = defineRecipe({
  base: { fontWeight: "bold" },
  variants: { variant: { solid: { bg: "blue.500" } } },
  defaultVariants: { variant: "solid" },
})
```

```ts
// v3 — slot recipe
import { defineSlotRecipe } from "@chakra-ui/react"

// v2 — multiStyleConfig（多部分组件）
const cardStyle = multiStyleConfig({
  parts: ["root", "header"],
  baseStyle: { root: { bg: "white" }, header: { fontWeight: "bold" } },
})

const cardSlotRecipe = defineSlotRecipe({
  slots: ["root", "header"],
  base: { root: { bg: "white" }, header: { fontWeight: "bold" } },
})
```

### Typegen for custom tokens

添加自定义令牌、语义令牌、recipes 或 slot recipes 后，运行 typegen 以保持 TypeScript 类型同步：

```bash
npx @chakra-ui/cli typegen ./theme.ts
```

> **复杂的主题迁移**——如果你正在迁移一个包含许多自定义令牌、语义令牌或多部分组件样式的 v2 主题，请使用 `chakra-ui-theming` 技能。它深入涵盖了 token/recipe/slot-recipe API，比本节单独使用更全面。

---

## 第 9 步 — Next.js 特定内容

### App Router

- 在 `app/layout.tsx` 中放置 `<Provider>`（服务器组件——无需 `"use client"`)
- 生成的 `components/ui/provider.tsx` 已经包含 `"use client"`
- 将 `suppressHydrationWarning` 添加到 `<html>` 以防止颜色模式闪烁
- 不要将整个应用或布局包裹在 `"use client"`

### Pages Router

```tsx
// pages/_app.js
import { Provider } from "@/components/ui/provider"

export default function App({ Component, pageProps }) {
  return (
    <Provider>
      <Component {...pageProps} />
    </Provider>
  )
}
```

从 `pages/_document.tsx` 中移除任何 `ColorModeScript`——它在 v3 中不再使用。

---

## 第 10 步 — 验证清单

迁移完成后，按以下步骤操作：

- [ ] 重新安装依赖：`npm install` / `pnpm install`
- [ ] TypeScript：`npx tsc --noEmit` — 解决所有类型错误
- [ ] Lint：`npm run lint`
- [ ] 构建：`npm run build`
- [ ] 视觉验证颜色模式切换（亮色 ↔ 暗色）
- [ ] 测试交互式组件：Dialog、Drawer、Menu、Tabs、Accordion
- [ ] 测试表单组件：Checkbox、Select/NativeSelect、Input、Radio
- [ ] 检查关键页面的视觉回归
- [ ] 在代码库中搜索剩余的 v2 导入：
  ```bash
  grep -r "ColorModeScript\|useColorModeValue\|extendTheme\|styleConfig\|@chakra-ui/icons\|@chakra-ui/next-js" src/
  ```

---

## 澄清问题（当上下文不明确时）

如果用户的版本、框架或范围不明确，请询问：

1. "你当前的 `@chakra-ui/react` 版本是什么？"
2. "你使用的是 Next.js App Router、Pages Router、Vite 还是纯 React？"
3. "你是迁移整个代码库还是特定组件？"

如果没有询问就进行假设，请明确说明假设。
