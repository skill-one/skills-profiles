# Streamdown

流媒体优化的 React Markdown 渲染器。`react-markdown` 的即插即用替代品，内置流媒体支持、安全性和交互控制。

## 快速设置

### 1. 安装

```bash
npm install streamdown
```

可选插件（仅安装所需的）：
```bash
npm install @streamdown/code @streamdown/mermaid @streamdown/math @streamdown/cjk
```

### 2. 配置 Tailwind CSS（必需）

**这是最常被遗漏的步骤。** Streamdown 使用 Tailwind 进行样式设置，必须扫描 dist 文件。

**Tailwind v4** — 添加到 `globals.css`：
```css
@source "../node_modules/streamdown/dist/*.js";
```

仅添加您已安装的包的 `@source` 行（省略未安装的插件可避免 Tailwind 错误）。请参考插件页面获取确切路径：
- 代码：`@source "../node_modules/@streamdown/code/dist/*.js";`
- CJK：`@source "../node_modules/@streamdown/cjk/dist/*.js";`
- 数学：`@source "../node_modules/@streamdown/math/dist/*.js";`
- Mermaid：`@source "../node_modules/@streamdown/mermaid/dist/*.js";`

**Tailwind v3** — 添加到 `tailwind.config.js`：
```js
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/streamdown/dist/*.js",
  ],
};
```

### 3. 基本用法

```tsx
import { Streamdown } from 'streamdown';

<Streamdown>{markdown}</Streamdown>
```

### 4. 使用 AI 流媒体（Vercel AI SDK）

```tsx
'use client';
import { useChat } from '@ai-sdk/react';
import { Streamdown } from 'streamdown';
import { code } from '@streamdown/code';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <>
      {messages.map((msg, i) => (
        <Streamdown
          key={msg.id}
          plugins={{ code }}
          caret="block"
          isAnimating={isLoading && i === messages.length - 1 && msg.role === 'assistant'}
        >
          {msg.content}
        </Streamdown>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} disabled={isLoading} />
      </form>
    </>
  );
}
```

### 5. 静态模式（博客、文档）

```tsx
<Streamdown mode="static" plugins={{ code }}>
  {content}
</Streamdown>
```

## 关键属性

| 属性 | 类型 | 默认值 | 用途 |
|------|------|---------|---------|
| `children` | `string` | — | Markdown 内容 |
| `mode` | `"streaming" \| "static"` | `"streaming"` | 渲染模式 |
| `plugins` | `{ code?, mermaid?, math?, cjk? }` | — | 功能插件 |
| `isAnimating` | `boolean` | `false` | 流媒体指示器 |
| `caret` | `"block" \| "circle"` | — | 光标样式 |
| `components` | `Components` | — | 自定义元素覆盖 |
| `controls` | `boolean \| object` | `true` | 交互按钮；`download: { filename }` 设置自定义下载名称 |
| `linkSafety` | `LinkSafetyConfig` | `{ enabled: true }` | 链接确认模态框 |
| `shikiTheme` | `[light, dark]` | `['github-light', 'github-dark']` | 代码主题 |
| `className` | `string` | — | 容器类 |
| `allowedElements` | `string[]` | all | 允许的标签名 |
| `disallowedElements` | `string[]` | `[]` | 禁止的标签名 |
| `allowElement` | `AllowElement` | — | 自定义元素过滤器 |
| `unwrapDisallowed` | `boolean` | `false` | 保留禁止元素的子元素 |
| `skipHtml` | `boolean` | `false` | 忽略原始 HTML |
| `urlTransform` | `UrlTransform` | `defaultUrlTransform` | 转换/清理 URL |

完整 API 参考，请参阅 [references/api.md](references/api.md)。

## 插件快速参考

| 插件 | 包 | 用途 |
|--------|---------|---------|
| 代码 | `@streamdown/code` | 语法高亮（Shiki，200+ 语言） |
| Mermaid | `@streamdown/mermaid` | 图表（流程图、时序图等） |
| 数学 | `@streamdown/math` | LaTeX 通过 KaTeX（需要 CSS 导入） |
| CJK | `@streamdown/cjk` | 中日韩文本支持 |

**数学需要 CSS：**
```tsx
import 'katex/dist/katex.min.css';
```

插件配置详情，请参阅 [references/plugins.md](references/plugins.md)。

## 参考

用于更深入的实现细节：

- **[references/api.md](references/api.md)** — 完整的属性、类型和接口
- **[references/plugins.md](references/plugins.md)** — 插件设置、配置和自定义
- **[references/styling.md](references/styling.md)** — CSS 变量、数据属性、自定义组件、主题示例
- **[references/security.md](references/security.md)** — 强化、链接安全、自定义 HTML 标签、生产配置
- **[references/features.md](references/features.md)** — 光标、remend、静态模式、控制、GFM、记忆化、故障排除

## 示例配置

从 `assets/examples/` 复制并调整：

- **[basic-streaming.tsx](assets/examples/basic-streaming.tsx)** — 最小的 AI 聊天与 Vercel AI SDK
- **[with-caret.tsx](assets/examples/with-caret.tsx)** — 带块状光标光标的流媒体
- **[full-featured.tsx](assets/examples/full-featured.tsx)** — 所有插件、光标、链接安全、控制
- **[static-mode.tsx](assets/examples/static-mode.tsx)** — 博客/文档渲染
- **[custom-security.tsx](assets/examples/custom-security.tsx)** — 严格安全用于 AI 内容

## 常见问题

1. **Tailwind 样式缺失** — 添加 `@source` 指令或 `content` 条目为 `node_modules/streamdown/dist/*.js`
2. **数学未渲染** — 导入 `katex/dist/katex.min.css`
3. **光标未显示** — `caret` 属性 AND `isAnimating={true}` 都需要
4. **流媒体期间复制按钮** — 当 `isAnimating={true}` 时自动禁用
5. **链接安全模态框出现** — 默认启用；使用 `linkSafety={{ enabled: false }}` 禁用
6. **Next.js 中的 Shiki 警告** — 明确安装 `shiki`，添加到 `transpilePackages`
7. **`allowedTags` 不工作** — 仅与默认 rehype 插件一起工作
8. **数学使用 `$$` 而不是 `$`** — 默认禁用单个美元符号以避免货币冲突
