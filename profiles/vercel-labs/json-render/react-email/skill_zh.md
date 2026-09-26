# @json-render/react-email

一个将 JSON 规范转换为 HTML 或纯文本邮件输出的 React 邮件渲染器。

## 快速入门

```typescript
import { renderToHtml } from "@json-render/react-email";
import { schema, standardComponentDefinitions } from "@json-render/react-email";
import { defineCatalog } from "@json-render/core";

const catalog = defineCatalog(schema, {
  components: standardComponentDefinitions,
});

const spec = {
  root: "html-1",
  elements: {
    "html-1": { type: "Html", props: { lang: "en", dir: "ltr" }, children: ["head-1", "body-1"] },
    "head-1": { type: "Head", props: {}, children: [] },
    "body-1": {
      type: "Body",
      props: { style: { backgroundColor: "#f6f9fc" } },
      children: ["container-1"],
    },
    "container-1": {
      type: "Container",
      props: { style: { maxWidth: "600px", margin: "0 auto", padding: "20px" } },
      children: ["heading-1", "text-1"],
    },
    "heading-1": { type: "Heading", props: { text: "Welcome" }, children: [] },
    "text-1": { type: "Text", props: { text: "Thanks for signing up." }, children: [] },
  },
};

const html = await renderToHtml(spec);
```

## 规范结构（元素树）

与 `@json-render/react` 相同的扁平元素树：`root` 键加上 `elements` 映射。根必须是 `Html`；`Html` 的子元素应该是 `Head` 和 `Body`。在 `Body` 内部使用 `Container`（例如最大宽度 600px）以实现客户端安全的布局。

## 创建目录和注册表

```typescript
import { defineCatalog } from "@json-render/core";
import { schema, defineRegistry, renderToHtml } from "@json-render/react-email";
import { standardComponentDefinitions } from "@json-render/react-email/catalog";
import { Container, Heading, Text } from "@react-email/components";
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    ...standardComponentDefinitions,
    Alert: {
      props: z.object({
        message: z.string(),
        variant: z.enum(["info", "success", "warning"]).nullable(),
      }),
      slots: [],
      description: "一个高亮显示的消息块",
    },
  },
  actions: {},
});

const { registry } = defineRegistry(catalog, {
  components: {
    Alert: ({ props }) => (
      <Container style={{ padding: 16, backgroundColor: "#eff6ff", borderRadius: 8 }}>
        <Text style={{ margin: 0 }}>{props.message}</Text>
      </Container>
    ),
  },
});

const html = await renderToHtml(spec, { registry });
```

## 服务器端渲染 API

| 函数 | 目的 |
|------|------|
| `renderToHtml(spec, options?)` | 将规范渲染为 HTML 邮件字符串 |
| `renderToPlainText(spec, options?)` | 将规范渲染为纯文本邮件字符串 |

`RenderOptions`：`registry`、`includeStandard`（默认为 true）、`state`（用于 `$state` / `$cond`）。

## 可见性和状态

支持 `visible` 条件、`$state`、`$cond`、重复（`repeat.statePath`）、嵌套重复路径（使用 `{ "$item": "field" }`）以及与 `@json-render/react` 相同的表达式语法。在服务器端渲染时使用 `RenderOptions` 中的 `state`，以便表达式能够解析。

## 服务器端安全导入

无需 React 或 `@react-email/components` 即可导入规范和目录：

```typescript
import { schema, standardComponentDefinitions } from "@json-render/react-email/server";
```

## 主要导出

| 导出 | 目的 |
|------|------|
| `defineRegistry` | 从目录创建类型安全的组件注册表 |
| `Renderer` | 在浏览器中渲染规范（例如预览）；与 `JSONUIProvider` 一起使用以支持状态/操作 |
| `createRenderer` | 带有状态/操作/验证的独立渲染器组件 |
| `renderToHtml` | 服务器：规范转换为 HTML 字符串 |
| `renderToPlainText` | 服务器：规范转换为纯文本字符串 |
| `schema` | 邮件元素规范 |
| `standardComponents` | 预构建的组件实现 |
| `standardComponentDefinitions` | 目录定义（Zod 属性） |

## 子路径导出

| 路径 | 目的 |
|------|------|
| `@json-render/react-email` | 完整包 |
| `@json-render/react-email/server` | 仅包含规范和目录（无 React） |
| `@json-render/react-email/catalog` | 标准组件定义和类型 |
| `@json-render/react-email/render` | 仅包含渲染函数 |

## 标准组件

所有组件都接受一个 `style` 属性（对象），用于内联样式。使用内联样式以提高邮件客户端兼容性；避免使用外部 CSS。

### 文档结构

| 组件 | 描述 |
|------|------|
| `Html` | 根包装器（lang、dir）。子元素：Head、Body。 |
| `Head` | 邮件头部区域。 |
| `Body` | 身体包装器；使用 `style` 设置背景。 |

### 布局

| 组件 | 描述 |
|------|------|
| `Container` | 限制宽度（例如最大宽度 600px）。 |
| `Section` | 组合内容；基于表格以实现兼容性。 |
| `Row` | 水平行。 |
| `Column` | 行中的列；通过 `style` 设置宽度。 |

### 内容

| 组件 | 描述 |
|------|------|
| `Heading` | 标题文本（作为 h1–h6）。 |
| `Text` | 正文文本。 |
| `Link` | 超链接（text、href）。 |
| `Button` | 样式为按钮的 CTA 链接（text、href）。 |
| `Image` | 从 URL 加载的图片（src、alt、width、height）。 |
| `Hr` | 水平线。 |

### 工具

| 组件 | 描述 |
|------|------|
| `Preview` | Html 内部的收件箱预览文本。 |
| `Markdown` | 将 Markdown 内容转换为邮件安全的 HTML。 |

## 邮件最佳实践

- 限制宽度（例如 Container 最大宽度 600px）。
- 使用内联样式或 React Email 的样式属性；许多客户端会剥离 `<style>` 块。
- 优先使用基于表格的布局（Section、Row、Column）以获得广泛的客户端支持。
- 使用绝对 URL 加载图片；许多客户端在某些情况下会阻止相对路径或 cid: 引用。
- 在多个客户端（Gmail、Outlook、Apple Mail）中测试；如有可能，使用预览工具或类似 Litmus 的服务。
