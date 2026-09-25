# Chakra UI 重构与评审

你正在使用 Chakra UI v3 来评审和改进 UI 代码。根据开发者的需求，你需要产出结构化的评审意见、重写的代码，或者两者都提供。在产出任何结果之前，请充分阅读代码和项目背景。

---

## 第 1 步 — 定位并确定意图

在输出任何内容之前，需要明确以下信息：

- **Chakra UI 版本** — 检查 `package.json`；默认使用 v3
- **框架** — Next.js App Router、Pages Router、Vite、纯 React
- **源类型** — 现有 Chakra UI、纯 HTML/CSS、Tailwind、CSS Modules、styled-components
- **用户的需求是什么：**
  - **仅评审** — "检查这个"、"这是否正确/符合规范"、"有什么问题"、"评审我的代码" → 产出带有针对性修复的评审意见，不进行完整重写
  - **重构/转换** — "重构这个"、"从 Tailwind 转换"、"清理这个" → 产出重写的代码
  - **两者都需要** — "评审和修复" → 先进行评审，然后提供重写的代码

在响应顶部说明你的阅读情况（例如："以现有 Chakra v3 代码进行评审。假设使用 Next.js App Router。"）。

如果代码尚未共享，请请求提供。不要评审代码的描述。

---

## 第 2 步 — 分析代码

无论输出模式如何，都需要从以下维度分析代码。对于评审，这些将成为发现的问题；对于重构，这些将成为需要修复的清单。

**可访问性**

- 所有交互元素是否都有可访问的标签？(`aria-label` 在图标按钮上、`htmlFor`/`id` 在标签+输入对上、`alt` 在图像上)
- 是否可以进行键盘导航？（焦点环未被抑制，交互元素实际上是可聚焦的）
- 标题层级是否合理？（没有跳过层级，没有将 `h1` 用作样式快捷方式）
- 表单字段是否被包裹在 `Field.Root` 中，并带有 `Field.Label` 和 `Field.ErrorText`？
- 组件是否可以在没有颜色作为唯一信号的情况下正常工作？

**响应式设计**

- 布局组件是否在多个断点处指定了行为？
- 是否有硬编码的像素值，而响应式令牌会更好？
- 这是否会在移动设备上失效？（固定宽度、`overflow: hidden` 在小视口上）

**Chakra API 正确性**

- 是否使用了 v3 的 prop 名称？（`disabled` 而不是 `isDisabled`、`colorPalette` 而不是 `colorScheme`、`gap` 而不是 `spacing`、`open` 而不是 `isOpen`）
- 是否正确使用了复合组件？（`Field.Root`/`Field.Label`、`Dialog.Root`/`Dialog.Content` 等）
- 在 Next.js App Router 中是否正确放置了 `"use client"`？
- 是否仍然存在 v2 的模式？（`extendTheme`、`ColorModeScript`、`useColorModeValue`、`sx` prop）

**令牌和样式使用**

- 是否在可以使用语义令牌的地方使用了硬编码的颜色？（`bg="#f9fafb"` → `bg="bg.subtle"`）
- 是否使用了原始的十六进制值或调色板值，而不是语义令牌？这些不会尊重暗黑模式。
- 是否有应该使用 Chakra 样式 prop 的内联 `style={{}}` prop？

**组件结构**

- 是否有不必要的嵌套？（`Box > Box > Box` 而一个 `Box` 就足够）
- 是否在可以使用 `Stack gap={4}` 的情况下使用了手动间距（每个子元素上的 `mt={4}`）？
- 是否使用了正确的布局原语？（`Flex` vs `Stack` vs `Grid` vs `SimpleGrid`）

**可维护性**

- 是否有 3 次或更多次重复的相同视觉模式？（适合提取为组件或配方）
- 是否有临时的样式覆盖，暗示需要配方或插槽配方？
- prop 类型 / TypeScript 类型是否存在且准确？

---

## 第 3a 步 — 评审输出

当用户需要评审而不是重写时使用此方法。

按影响对发现的问题进行分类：

**关键** — 导致行为中断或排除用户的错误和可访问性问题

- 图标按钮缺少 `aria-label`
- 表单字段没有标签关联
- 带有 `onClick` 但没有键盘访问的交互式 `Box`
- 错误的 v3 prop 名称，静默无效果（`isDisabled` 在 v3 中不禁用）
- App Router 组件缺少 `"use client"`

**改进** — 不是紧急的正确性和质量问题

- 硬编码的颜色导致暗黑模式失效
- 缺少响应式断点
- 不必要的嵌套或错误的布局原语
- 仍然有效但应该更新的 v2 模式

**可选建议** — 非阻塞的想法

- 将重复的模式提取为组件
- 用配方变体替换临时的样式
- 添加缺失的 TypeScript 类型

对于每个关键问题和重要的改进，展示一个最小的修复：

```
**关闭按钮缺少 aria-label** (关键)
用于关闭对话框的 IconButton 没有可访问的标签。

// 之前
<IconButton icon={<CloseIcon />} onClick={onClose} />
// 之后
<IconButton aria-label="关闭对话框" icon={<CloseIcon />} onClick={onClose} />
```

如果某个部分没有可报告的内容，则跳过该部分。根据代码的长度调整评审的详细程度——一个 20 行的组件需要紧密的评审，而不是详尽的评审。

---

## 第 3b 步 — 重构/转换输出

当用户需要重写代码时使用此方法。

### 按源类型转换策略

**从纯 HTML / CSS**

| HTML                     | Chakra 等价物                           |
| ------------------------ | ------------------------------------------- |
| `<div>` 布局包装器       | `Box`、`Flex`、`Stack`、`Grid`              |
| `<section>`、`<article>` | `Box as="section"`、`Box as="article"`      |
| `<nav>`                  | `Box as="nav"`                              |
| `<ul>` / `<li>`          | `Box as="ul"` / `Box as="li"`，或 `Stack`   |
| `<button>`               | `Button` 或 `IconButton`                    |
| `<a>`                    | `Link`                                      |
| `<img>`                  | `Image`（保留 `alt`）                    |
| `<input>`、`<select>`    | `Input`、`NativeSelect` 在 `Field.Root` 内部 |

| CSS                      | Chakra 样式 prop             |
| ------------------------ | ----------------------------- |
| `display: flex`          | `Flex` 或 `display="flex"`    |
| `flex-direction: column` | `Stack` 或 `flexDir="column"` |
| `gap: 16px`              | `gap={4}`（1 单位 = 4px）      |
| `padding: 16px 24px`     | `py={4} px={6}`               |
| `border-radius: 8px`     | `rounded="md"`                |
| `color: #6b7280`         | `color="fg.muted"`            |
| `background: #f9fafb`    | `bg="bg.subtle"`              |

**从 Tailwind CSS**

| Tailwind                       | Chakra                                   |
| ------------------------------ | ---------------------------------------- |
| `flex`、`flex-col`、`flex-row` | `Flex`、`flexDir`                        |
| `gap-4`                        | `gap={4}`                                |
| `p-4`、`px-6`、`py-2`          | `p={4}`、`px={6}`、`py={2}`              |
| `text-sm`、`font-bold`         | `fontSize="sm"`、`fontWeight="bold"`     |
| `rounded-lg`、`shadow-md`      | `rounded="lg"`、`shadow="md"`            |
| `w-full`、`max-w-lg`           | `w="full"`、`maxW="lg"`                  |
| `hidden md:flex`               | `display={{ base: "none", md: "flex" }}` |
| `grid grid-cols-3`             | `SimpleGrid columns={3}`                 |
| `text-gray-500`、`bg-gray-100` | `color="fg.muted"`、`bg="bg.subtle"`     |
| `hover:bg-gray-100`            | `_hover={{ bg: "bg.subtle" }}`           |

用 Chakra 的断点对象语法替换 Tailwind 的响应式前缀：

```tsx
// Tailwind: text-sm md:base lg:text-lg
<Text fontSize={{ base: "sm", md: "md", lg: "lg" }} />
```

**从 CSS Modules** — 将可以转换为 Chakra prop 的内容转换为 prop；对于无法用 prop 表达的样式（动画、复杂选择器），保留 `className`：

```tsx
// 之前
<div className={styles.card}>...</div>
// 之后 — 转换为 prop；仅保留无法转换的样式使用 className
<Box p={4} rounded="lg" shadow="sm" className={styles.fadeIn}>...</Box>
```

一旦所有类名都被消除，就完全移除导入。

**从 styled-components / @emotion/styled** — 映射到 `Box` 并使用等效的样式 prop，然后移除导入并卸载如果不再在其他地方使用：

```tsx
// 之前
const Card = styled.div`padding: 1rem; &:hover { background: #f3f4f6; }`
// 之后
<Box p={4} _hover={{ bg: "bg.muted" }} />
```

**从现有的 Chakra UI（清理）**

- 展平 `Box > Box > Box` 嵌套；用 `Stack gap={N}` 替换每个子元素上的 `mt`/`mb`
- 将 `sx` 替换为 `css`（v3 重命名）；更新其中的嵌套 `&:hover` 选择器
- 将 `bg="gray.50"` → `bg="bg.subtle"` 和其他语义令牌的等价物
- 更新 v2 prop 名称：`isDisabled→disabled`、`colorScheme→colorPalette`、`spacing→gap`
- 更新复合组件：`FormControl→Field.Root`、`Modal→Dialog`、`Select→NativeSelect`

### 保留行为 — 非可协商

- 保持所有事件处理器、状态变量和条件渲染完全不变
- 保持 `aria-*` 属性；在明显需要时添加缺失的属性
- 保持语义 HTML 意图（`<nav>` → `Box as="nav"`，而不仅仅是 `Box`）
- 保持现有的 `"use client"`；仅在组件确实需要时添加
- 不要因为组件使用了 Chakra UI 就添加 `"use client"`
- 一个部分转换的、可以工作的组件比一个完全转换但无法工作的组件更好

### `asChild` 用于 Next.js Link 和 Image

```tsx
import NextLink from "next/link"
<ChakraLink asChild><NextLink href="/about">About</NextLink></ChakraLink>

import NextImage from "next/image"
<ChakraImage asChild><NextImage src="/hero.png" alt="Hero" width={800} height={400} /></ChakraImage>
```

### 重构输出格式

**1. 重构后的代码** — 完整、可运行、带有正确的导入

**2. 变更内容** — 简洁的列表，专注于非明显的决策：

```
- 将 `<div className="flex gap-4">` 替换为 `<Flex gap={4}>`
- 将 `bg="#f9fafb"` 替换为 `bg="bg.subtle"` 以兼容暗黑模式
- 保持表单提交处理程序和验证逻辑不变
- 为关闭图标按钮添加了 aria-label（之前缺失）
```

**3. 建议**（可选） — 超出此次重构的、有意义的改进：提取可重用的组件、采用配方、迁移 v2 模式。

---

## 何时询问 vs 直接进行

如果代码和意图清晰，则直接进行。在以下情况下询问：

- 代码尚未共享
- 组件非常大且范围不明确
- 有你看不到的上下文或状态会改变评审
- 有模糊的行为，可能有多种解释

在直接进行而不询问时，在响应顶部说明你的假设。
