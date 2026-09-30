---
name: portable-text-serialization
description: 将 Portable Text 渲染并序列化为 React、Svelte、Vue、Astro、HTML、Markdown 和纯文本。适用于在任意前端框架中实现 Portable Text 渲染、为非标准块类型构建自定义序列化器、在服务器端将 Portable Text 转换为 HTML 字符串、将 Portable Text 转换为 Markdown、从 Portable Text 中提取纯文本，或排查与 marks、blocks、lists 或自定义类型相关的渲染问题。
---

# 可移植文本序列化

使用 `@portabletext/*` 库系列跨框架渲染可移植文本内容。每个库都遵循相同的组件映射模式：你需要提供一个 `components` 对象，将 PT 节点类型映射到特定框架的渲染器。

## 可移植文本结构（快速参考）

PT 是一个块数组。每个块都有 `_type`、可选的 `style`、`children`（跨度）、`markDefs`、`listItem` 和 `level`。

```
根数组
├── 块 (_type: "block")
│   ├── style: "normal" | "h1" | "h2" | "blockquote" | ...
│   ├── children: [span, span, ...]
│   │   └── span: { _type: "span", text: "...", marks: ["strong", "<markDefKey>"] }
│   ├── markDefs: [{ _key, _type: "link", href: "..." }, ...]
│   ├── listItem: "bullet" | "number" (可选)
│   └── level: 1, 2, 3... (可选，用于嵌套列表)
├── 自定义块 (_type: "image" | "code" | 任何自定义类型)
└── ...更多块
```

**标记** 有两种形式：
- **装饰器**：`marks[]` 中的字符串值，如 `"strong"`、`"em"`、`"underline"`、`"code"`
- **注释**：`marks[]` 中的键，引用 `markDefs[]` 中的条目（例如，链接、内部引用）

## 组件映射模式（所有框架）

每个 `@portabletext/*` 库都接受一个具有以下键的 `components` 对象：

| 键 | 渲染 | 属性/数据 |
|-----|---------|------------|
| `types` | 自定义块/内联类型（图像、代码、CTA） | `value`（块数据） |
| `marks` | 装饰器 + 注释 | `children` + `value`（标记数据） |
| `block` | 块样式（h1、normal、blockquote） | `children` |
| `list` | 列表包装器（ul、ol） | `children` |
| `listItem` | 列表项 | `children` |
| `hardBreak` | 块内的换行 | — |

## 框架特定规则

阅读与你框架匹配的规则文件：

- **React / Next.js**：`rules/react.md` — `@portabletext/react` 或 `next-sanity`
- **Svelte / SvelteKit**：`rules/svelte.md` — `@portabletext/svelte`
- **Vue / Nuxt**：`rules/vue.md` — `@portabletext/vue`
- **Astro**：`rules/astro.md` — `astro-portabletext`
- **HTML（服务器端）**：`rules/html.md` — `@portabletext/to-html`
- **Markdown**：`rules/markdown.md` — `@portabletext/markdown`
- **纯文本提取**：`rules/plain-text.md` — `@portabletext/toolkit`

### 社区其他序列化器

这些列在 [portabletext.org](https://www.portabletext.org/integrations/serializers/) 上，但没有专用的规则文件：

| 目标 | 包 |
|--------|---------|
| React Native | `@portabletext/react-native-portabletext` |
| React PDF | `@portabletext/react-pdf-portabletext` |
| Solid | `solid-portabletext` |
| Qwik | `portabletext-qwik` |
| Shopify Liquid | `portable-text-to-liquid` |
| PHP | `sanity-php`（SanityBlockContent 类） |
| Python | `portabletext-html` |
| C# / .NET | `dotnet-portable-text` |
| Dart / Flutter | `flutter_sanity_portable_text` |

## 常见模式（所有框架）

### 自定义类型需要显式组件

PT 渲染器默认只处理标准块。自定义类型（`image`、`code`、`callToAction` 等）需要显式组件映射——否则不会渲染。

### 保持组件对象稳定

在 React/Vue 中，将 `components` 定义在渲染函数外部或进行记忆化。每次重新创建都会导致不必要的重新渲染。

### 优雅处理缺失组件

所有库都接受 `onMissingComponent` 来控制遇到未知类型时的行为：
- `false` — 抑制警告
- 自定义函数 — 记录或报告

### 使用 GROQ 查询 PT

始终在自定义块内展开引用：

```groq
body[]{
  ...,
  _type == "image" => {
    ...,
    asset->
  },
  markDefs[]{
    ...,
    _type == "internalLink" => {
      ...,
      "slug": @.reference->slug.current
    }
  }
}
```
