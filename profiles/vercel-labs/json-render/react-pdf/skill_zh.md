# @json-render/react-pdf

使用 `@react-pdf/renderer` 从 JSON 规范生成 PDF 文档的 React PDF 渲染器。

## 安装

```bash
npm install @json-render/core @json-render/react-pdf
```

## 快速入门

```typescript
import { renderToBuffer } from "@json-render/react-pdf";
import type { Spec } from "@json-render/core";

const spec: Spec = {
  root: "doc",
  elements: {
    doc: { type: "Document", props: { title: "发票" }, children: ["page"] },
    page: {
      type: "Page",
      props: { size: "A4" },
      children: ["heading", "table"],
    },
    heading: {
      type: "Heading",
      props: { text: "发票 #1234", level: "h1" },
      children: [],
    },
    table: {
      type: "Table",
      props: {
        columns: [
          { header: "项目", width: "60%" },
          { header: "价格", width: "40%", align: "right" },
        ],
        rows: [
          ["小部件 A", "$10.00"],
          ["小部件 B", "$25.00"],
        ],
      },
      children: [],
    },
  },
};

const buffer = await renderToBuffer(spec);
```

## 渲染 API

```typescript
import { renderToBuffer, renderToStream, renderToFile } from "@json-render/react-pdf";

// 内存中的缓冲区
const buffer = await renderToBuffer(spec);

// 可读流（输出到 HTTP 响应）
const stream = await renderToStream(spec);
stream.pipe(res);

// 直接写入文件
await renderToFile(spec, "./output.pdf");
```

所有渲染函数接受一个可选的第二参数：`{ registry?, state?, handlers? }`。

## 标准组件

| 组件 | 描述 |
|-----------|-------------|
| `Document` | 顶层 PDF 包装器（必须为根节点） |
| `Page` | 具有尺寸（A4、LETTER）、方向、边距的页面 |
| `View` | 通用容器（内边距、边距、背景、边框） |
| `Row`, `Column` | 具有间隙、对齐、对齐的弹性布局 |
| `Heading` | h1-h4 标题文本 |
| `Text` | 正文文本（fontSize、颜色、权重、对齐） |
| `Image` | 从 URL 或 base64 获取的图像 |
| `Link` | 带有文本和 href 的超链接 |
| `Table` | 带有类型化列和行的数据表 |
| `List` | 有序或无序列表 |
| `Divider` | 水平线分隔符 |
| `Spacer` | 空白垂直空间 |
| `PageNumber` | 当前页码和总页数 |

## 自定义目录

```typescript
import { defineCatalog } from "@json-render/core";
import { schema, defineRegistry, renderToBuffer } from "@json-render/react-pdf";
import { standardComponentDefinitions } from "@json-render/react-pdf/catalog";
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
  actions: {},
});

const { registry } = defineRegistry(catalog, {
  components: {
    Badge: ({ props }) => (
      <View style={{ backgroundColor: props.color ?? "#e5e7eb", padding: 4 }}>
        <Text>{props.label}</Text>
      </View>
    ),
  },
});

const buffer = await renderToBuffer(spec, { registry });
```

## 外部存储（受控模式）

传递 `StateStore` 以完全控制状态：

嵌套列表可以在包含的重复中设置 `repeat.statePath` 为 `{ "$item": "field" }`。

```typescript
import { createStateStore } from "@json-render/react-pdf";

const store = createStateStore({ invoice: { total: 100 } });
store.set("/invoice/total", 200);
```

## 服务器安全导入

导入架构和目录而不引入 React：

```typescript
import { schema, standardComponentDefinitions } from "@json-render/react-pdf/server";
```
