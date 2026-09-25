# assistant-ui Markdown

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

Assistant-ui 为助手文本部分提供两种渲染器。`MarkdownTextPrimitive` 是轻量级的 `react-markdown` 路径，而已安装的 `MarkdownText` 元素是其样式化实现。`StreamdownTextPrimitive` 在需要块感知流式传输以及可选的 Shiki、KaTeX、Mermaid 或 CJK 支持时作为较大渲染器的替代方案。

## 参考

- [./references/markdown-text.md](./references/markdown-text.md) -- 安装和组合 `MarkdownText`，自定义 `MarkdownTextPrimitive`，以及区分行内代码与围栏代码
- [./references/syntax-highlighting.md](./references/syntax-highlighting.md) -- 安装 Shiki 或 Prism 渲染器，并为每种围栏语言选择一个
- [./references/latex-mermaid.md](./references/latex-mermaid.md) -- 配置 KaTeX，规范化模型数学，保留代码跨度，并在流完成时拦截 Mermaid
- [./references/streamdown.md](./references/streamdown.md) -- 使用 Streamdown 替代方案、插件、Tailwind 源，以及延迟解析

## 选择渲染器

当应用需要小型渲染器、自定义 `react-markdown` 组件映射，或按语言覆盖 `SyntaxHighlighter` 和 `CodeHeader` 时，请使用 `markdown-text`。仅在消息格式需要时才添加高亮、数学和 Mermaid。

当文本部分需要基于块的流式传输、不完整的 Markdown 修复，或可选的代码、数学、Mermaid 和 CJK 插件时，请使用 `StreamdownTextPrimitive`。它会替换该文本部分的 Markdown 渲染器。不要为同一部分挂载两个渲染器。

## 安装和连接 MarkdownText

安装渲染器，它位于 `components/assistant-ui/elements/markdown-text.tsx`。

```bash
npx assistant-ui@latest add markdown-text
```

`MarkdownText` 会读取活动消息部分本身。仅在 `text` 分支中渲染它，而其他部分类型保留自己的渲染器。

```tsx
"use client";

import { MessagePrimitive } from "@assistant-ui/react";
import { MarkdownText } from "@/components/assistant-ui/elements/markdown-text";

export function AssistantMessageText() {
  return (
    <MessagePrimitive.Parts>
      {({ part }) => (part.type === "text" ? <MarkdownText /> : null)}
    </MessagePrimitive.Parts>
  );
}
```

`thread` 元素已包含此渲染器。仅在替换线程的消息布局时直接组合它。

## 自定义 primitive

`MarkdownTextPrimitive` 通过上下文读取周围的文本部分，因此它不会接收文本子元素或值属性。它的 `components` 映射控制常规 Markdown 标签，以及 `SyntaxHighlighter` 和 `CodeHeader`；`componentsByLanguage` 会替换任一插槽以用于一种围栏语言。有关直接 primitive 实现的详细信息，请参阅 [markdown-text.md](./references/markdown-text.md)。

`preprocess` 在平滑和解析之前运行在完整累积文本上。它是模型特定分隔符修复的接口。`smooth` 默认为 `true`；`defer` 默认为 `false`。当 React 应该优先考虑输入和滚动而不是中间解析时，请为大型、快速增长的消息设置 `defer`。在渲染器挂载期间保持其值不变，因为切换它会重新挂载解析的树。

## 高亮围栏代码

`MarkdownText` 会将围栏代码显示为普通代码，直到注册了 `SyntaxHighlighter`。优先使用运行时感知的 Shiki 元素，它会等待其活动部分稳定后再进行分词。

```bash
npx assistant-ui@latest add shiki-highlighter
```

```tsx
import { SyntaxHighlighter } from "@/components/assistant-ui/elements/shiki-highlighter.aui";

const defaultComponents = memoizeMarkdownComponents({
  SyntaxHighlighter,
});
```

基于 Prism 的 `syntax-highlighter` 元素对于已经依赖 `react-syntax-highlighter` 的应用仍然有用。

```bash
npx assistant-ui@latest add syntax-highlighter
```

```tsx
import { SyntaxHighlighter } from "@/components/assistant-ui/elements/syntax-highlighter";
```

编辑已安装的 `markdown-text` 组件的默认映射，或在元素渲染处传递 `components` 覆盖。有关精确渲染器契约的详细信息，请参阅 [syntax-highlighting.md](./references/syntax-highlighting.md)。

## 渲染数学和图表

KaTeX 需要 `remark-math`、`rehype-katex` 和 KaTeX 样式表。Markdown 包导出 `normalizeMathDelimiters`、`rewriteCustomMathTags`、`rewriteLatexBracketDelimiters` 和 `escapeCurrencyDollars` 以用于预处理模型输出。辅助工具会在行内代码和围栏代码外重写，因此代码中的示例保持字面值。

安装 `mermaid-diagram` 并将其 `.aui` 渲染器注册为 `mermaid` 语言覆盖。它会读取消息部分状态，在流运行时显示骨架，而不是解析不完整的 Mermaid 源。有关详细信息，请参阅 [latex-mermaid.md](./references/latex-mermaid.md)。

## 使用 Streamdown 代替

`StreamdownTextPrimitive` 读取相同的文本部分上下文，并且可以连接到相同的 `MessagePrimitive.Parts` 分支。它默认为 `mode="streaming"`，这会保持已完成块的稳定性，同时最终块在增长。显式提供可选插件，并为 Streamdown 和每个已安装插件添加 Tailwind `@source` 条目，以便其控件和光标接收样式。

这里同时可用 `defer` 和 `smooth`。`defer` 默认为 `false`，在负载下可能会跳过中间状态，但仍会渲染最终文本。`smooth` 也默认为 `false`；除非需要特定的打字机揭示效果，否则请使用 Streamdown 的原生 `animated` 属性进行入口动画。完整设置和迁移接口在 [streamdown.md](./references/streamdown.md) 中。

## 常见问题

**Markdown 渲染为普通文本**

- 在 `text` 分支中渲染 `MarkdownText` 或 `StreamdownTextPrimitive`。直接渲染 `part.text` 会绕过 Markdown 解析。

**围栏代码没有语法颜色**

- `markdown-text` 包括标签和复制控制，但没有高亮器。安装并注册 `shiki-highlighter` 或 `syntax-highlighter`。

**数学输出未样式化或价格变为数学**

- 一次导入 `katex/dist/katex.min.css` 以用于 KaTeX。当消息包含单美元数学和货币时，组合 `escapeCurrencyDollars(normalizeMathDelimiters(text))`。

**Mermaid 在响应流式传输时重绘**

- 在 `componentsByLanguage` 中使用 `@/components/assistant-ui/elements/mermaid-diagram.aui`。其运行时包装器会保持解析，直到消息部分完成。

**延迟解析导致视觉重置**

- 挂载后不要切换 `defer`。这两个 primitive 在该属性更改时会选择不同的延迟渲染器路径。

**Streamdown 控件或光标样式未应用**

- 为 `streamdown` 和每个已安装的 `@streamdown/*` 插件添加所需的 Tailwind `@source` 指令。

## 相关技能

- [primitives](../primitives/SKILL.md) -- 组合 `MessagePrimitive.Parts` 和周围的消息 UI
- [elements](../elements/SKILL.md) -- 安装和自定义复制的 `markdown-text`、高亮器和 Mermaid 元素源
