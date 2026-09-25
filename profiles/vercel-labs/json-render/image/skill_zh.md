# @json-render/image

使用 Satori 将 JSON 规范转换为 SVG 和 PNG 图片的图像渲染器。

## 快速入门

```typescript
import { renderToPng } from "@json-render/image/render";
import type { Spec } from "@json-render/core";

const spec: Spec = {
  root: "frame",
  elements: {
    frame: {
      type: "Frame",
      props: { width: 1200, height: 630, backgroundColor: "#1a1a2e" },
      children: ["heading"],
    },
    heading: {
      type: "Heading",
      props: { text: "Hello World", level: "h1", color: "#ffffff" },
      children: [],
    },
  },
};

const png = await renderToPng(spec, {
  fonts: [{ name: "Inter", data: fontData, weight: 400, style: "normal" }],
});
```

## 使用标准组件

```typescript
import { defineCatalog } from "@json-render/core";
import { schema, standardComponentDefinitions } from "@json-render/image";

export const imageCatalog = defineCatalog(schema, {
  components: standardComponentDefinitions,
});
```

## 添加自定义组件

```typescript
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    ...standardComponentDefinitions,
    Badge: {
      props: z.object({ label: z.string(), color: z.string().nullable() }),
      slots: [],
      description: "一个彩色徽章标签",
    },
  },
});
```

## 标准组件

| 组件 | 类别 | 描述 |
|-----------|----------|-------------|
| `Frame` | 根组件 | 根容器。定义宽度、高度、背景。必须是根组件。 |
| `Box` | 布局 | 具有内边距、外边距、边框、绝对定位的容器 |
| `Row` | 布局 | 水平弹性布局 |
| `Column` | 布局 | 垂直弹性布局 |
| `Heading` | 内容 | h1-h4 标题文本 |
| `Text` | 内容 | 带有完整样式的正文文本 |
| `Image` | 内容 | 从 URL 加载的图像 |
| `Divider` | 装饰 | 水平线分隔符 |
| `Spacer` | 装饰 | 空垂直空间 |

## 主要导出

| 导出 | 目的 |
|--------|---------|
| `renderToSvg` | 将规范渲染为 SVG 字符串 |
| `renderToPng` | 将规范渲染为 PNG 缓冲区（需要 `@resvg/resvg-js`） |
| `schema` | 图像元素规范 |
| `standardComponents` | 预构建的组件注册表 |
| `standardComponentDefinitions` | 用于 AI 提示的目录定义 |

## 子路径导出

| 导出 | 描述 |
|--------|-------------|
| `@json-render/image` | 完整包：规范、组件、渲染函数 |
| `@json-render/image/server` | 仅包含规范和目录定义（不含 React/Satori） |
| `@json-render/image/catalog` | 标准组件定义和类型 |
| `@json-render/image/render` | 仅包含渲染函数 |
