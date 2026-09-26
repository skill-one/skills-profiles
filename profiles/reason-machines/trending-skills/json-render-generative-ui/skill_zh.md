# json-render 生成式 UI 框架

> 技能来自 [ara.so](https://ara.so) — 每日 2026 技能集合。

json-render 是一个 **生成式 UI 框架**，它允许 AI 从自然语言提示中生成动态界面，并受限于预定义的组件目录。AI 输出 JSON；json-render 安全且可预测地跨任何平台渲染它。

## 安装

```bash
# React (核心)
npm install @json-render/core @json-render/react

# React + shadcn/ui (36 个预构建组件)
npm install @json-render/shadcn

# React Native
npm install @json-render/core @json-render/react-native

# Vue
npm install @json-render/core @json-render/vue

# Svelte
npm install @json-render/core @json-render/svelte

# SolidJS
npm install @json-render/core @json-render/solid

# 视频 (Remotion)
npm install @json-render/core @json-render/remotion

# PDF
npm install @json-render/core @json-render/react-pdf

# 邮件
npm install @json-render/core @json-render/react-email @react-email/components @react-email/render

# 3D (React Three Fiber)
npm install @json-render/core @json-render/react-three-fiber @react-three/fiber @react-three/drei three

# OG 图片 / SVG / PNG
npm install @json-render/core @json-render/image

# 状态管理适配器
npm install @json-render/zustand   # 或 redux, jotai, xstate

# MCP 集成 (Claude, ChatGPT, Cursor)
npm install @json-render/mcp

# YAML 线路格式
npm install @json-render/yaml
```

## 核心概念

| 概念 | 描述 |
|---|---|
| **目录** | 定义允许的组件和操作（AI 的约束条件） |
| **规范** | AI 生成的 JSON，描述要渲染的组件和属性 |
| **注册表** | 将目录组件名称映射到实际渲染实现 |
| **渲染器** | 平台特定的组件，它接受规范 + 注册表并渲染 UI |
| **操作** | AI 可以触发的命名事件（例如 `export_report`, `refresh_data`） |

## 规范格式

扁平规范格式使用根键 + 元素映射：

```typescript
const spec = {
  root: "card-1",
  elements: {
    "card-1": {
      type: "Card",
      props: { title: "Dashboard" },
      children: ["metric-1", "metric-2", "button-1"],
    },
    "metric-1": {
      type: "Metric",
      props: { label: "Revenue", value: "124000", format: "currency" },
      children: [],
    },
    "metric-2": {
      type: "Metric",
      props: { label: "Growth", value: "0.18", format: "percent" },
      children: [],
    },
    "button-1": {
      type: "Button",
      props: { label: "Export Report", action: "export_report" },
      children: [],
    },
  },
};
```

## 第 1 步：定义目录

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    Card: {
      props: z.object({ title: z.string() }),
      description: "带标题的卡片容器",
    },
    Metric: {
      props: z.object({
        label: z.string(),
        value: z.string(),
        format: z.enum(["currency", "percent", "number"]).nullable(),
      }),
      description: "显示单个指标值，可选格式化",
    },
    Button: {
      props: z.object({
        label: z.string(),
        action: z.string(),
      }),
      description: "可点击的按钮，触发操作",
    },
    Stack: {
      props: z.object({
        direction: z.enum(["row", "column"]).default("column"),
        gap: z.number().optional(),
      }),
      description: "堆叠子元素的布局容器",
    },
  },
  actions: {
    export_report: { description: "将当前仪表板导出为 PDF" },
    refresh_data: { description: "刷新所有指标数据" },
    navigate: {
      description: "导航到页面",
      payload: z.object({ path: z.string() }),
    },
  },
});
```

## 第 2 步：定义注册表（React）

```tsx
import { defineRegistry, Renderer } from "@json-render/react";

function format(value: string, fmt: string | null): string {
  if (fmt === "currency") return `$${Number(value).toLocaleString()}`;
  if (fmt === "percent") return `${(Number(value) * 100).toFixed(1)}%`;
  return value;
}

const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) => (
      <div className="rounded-lg border p-4 shadow-sm">
        <h3 className="text-lg font-semibold mb-3">{props.title}</h3>
        {children}
      </div>
    ),

    Metric: ({ props }) => (
      <div className="flex flex-col">
        <span className="text-sm text-gray-500">{props.label}</span>
        <span className="text-2xl font-bold">
          {format(props.value, props.format)}
        </span>
      </div>
    ),

    Button: ({ props, emit }) => (
      <button
        className="px-4 py-2 bg-blue-600 text-white rounded"
        onClick={() => emit("press")}
      >
        {props.label}
      </button>
    ),

    Stack: ({ props, children }) => (
      <div
        style={{
          display: "flex",
          flexDirection: props.direction ?? "column",
          gap: props.gap ?? 8,
        }}
      >
        {children}
      </div>
    ),
  },
});
```

## 第 3 步：渲染规范

```tsx
import { Renderer } from "@json-render/react";

function Dashboard({ spec, onAction }) {
  return (
    <Renderer
      spec={spec}
      registry={registry}
      onAction={(action, payload) => {
        console.log("触发了操作:", action, payload);
        onAction?.(action, payload);
      }}
    />
  );
}
```

## 使用 AI 生成规范（Vercel AI SDK）

```typescript
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt } from "@json-render/core";

async function generateDashboard(userPrompt: string) {
  const { object: spec } = await generateObject({
    model: openai("gpt-4o"),
    schema: getCatalogSchema(catalog),
    system: getCatalogPrompt(catalog),
    prompt: userPrompt,
  });

  return spec;
}

// 使用示例
const spec = await generateDashboard(
  "创建一个销售仪表板，显示收入、转化率和导出按钮"
);
```

## 流式传输规范

```tsx
import { streamObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt, parseSpecStream } from "@json-render/core";
import { Renderer } from "@json-render/react";
import { useState, useEffect } from "react";

function StreamingDashboard({ prompt }: { prompt: string }) {
  const [spec, setSpec] = useState(null);

  useEffect(() => {
    async function stream() {
      const { partialObjectStream } = await streamObject({
        model: openai("gpt-4o"),
        schema: getCatalogSchema(catalog),
        system: getCatalogPrompt(catalog),
        prompt,
      });

      for await (const partial of partialObjectStream) {
        setSpec(partial); // Renderer 会优雅地处理部分规范
      }
    }
    stream();
  }, [prompt]);

  if (!spec) return <div>正在生成 UI...</div>;
  return <Renderer spec={spec} registry={registry} />;
}
```

## 使用预构建的 shadcn/ui 组件

```tsx
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { defineRegistry, Renderer } from "@json-render/react";
import { shadcnComponentDefinitions } from "@json-render/shadcn/catalog";
import { shadcnComponents } from "@json-render/shadcn";

// 从 36 个可用的 shadcn 组件中选择任意一个
const catalog = defineCatalog(schema, {
  components: {
    Card: shadcnComponentDefinitions.Card,
    Stack: shadcnComponentDefinitions.Stack,
    Heading: shadcnComponentDefinitions.Heading,
    Text: shadcnComponentDefinitions.Text,
    Button: shadcnComponentDefinitions.Button,
    Badge: shadcnComponentDefinitions.Badge,
    Table: shadcnComponentDefinitions.Table,
    Chart: shadcnComponentDefinitions.Chart,
    Input: shadcnComponentDefinitions.Input,
    Select: shadcnComponentDefinitions.Select,
  },
  actions: {
    submit: { description: "提交表单" },
    export: { description: "导出数据" },
  },
});

const { registry } = defineRegistry(catalog, {
  components: {
    Card: shadcnComponents.Card,
    Stack: shadcnComponents.Stack,
    Heading: shadcnComponents.Heading,
    Text: shadcnComponents.Text,
    Button: shadcnComponents.Button,
    Badge: shadcnComponents.Badge,
    Table: shadcnComponents.Table,
    Chart: shadcnComponents.Chart,
    Input: shadcnComponents.Input,
    Select: shadcnComponents.Select,
  },
});

function AIPage({ spec }) {
  return <Renderer spec={spec} registry={registry} />;
}
```

## Vue 渲染器

```typescript
import { h, defineComponent } from "vue";
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/vue/schema";
import { defineRegistry, Renderer } from "@json-render/vue";
import { z } from "zod";

const catalog = defineCatalog(schema, {
  components: {
    Card: {
      props: z.object({ title: z.string() }),
      description: "卡片容器",
    },
    Button: {
      props: z.object({ label: z.string() }),
      description: "按钮",
    },
  },
  actions: {
    click: { description: "按钮被点击" },
  },
});

const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) =>
      h("div", { class: "card" }, [
        h("h3", null, props.title),
        children,
      ]),
    Button: ({ props, emit }) =>
      h("button", { onClick: () => emit("click") }, props.label),
  },
});

// 在你的 Vue 组件文件中：
// <template>
//   <Renderer :spec="spec" :registry="registry" />
// </template>
```

## React Native 渲染器

```tsx
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react-native/schema";
import {
  standardComponentDefinitions,
  standardActionDefinitions,
} from "@json-render/react-native/catalog";
import { defineRegistry, Renderer } from "@json-render/react-native";

// 开箱即用 25+ 标准移动组件
const catalog = defineCatalog(schema, {
  components: { ...standardComponentDefinitions },
  actions: standardActionDefinitions,
});

const { registry } = defineRegistry(catalog, {
  components: {}, // 使用所有标准实现
});

export function AIScreen({ spec }) {
  return <Renderer spec={spec} registry={registry} />;
}
```

## PDF 生成

```typescript
import { renderToBuffer } from "@json-render/react-pdf";

const invoiceSpec = {
  root: "doc",
  elements: {
    doc: {
      type: "Document",
      props: { title: "Invoice #1234" },
      children: ["page-1"],
    },
    "page-1": {
      type: "Page",
      props: { size: "A4" },
      children: ["heading-1", "table-1"],
    },
    "heading-1": {
      type: "Heading",
      props: { text: "Invoice #1234", level: "h1" },
      children: [],
    },
    "table-1": {
      type: "Table",
      props: {
        columns: [
          { header: "Item", width: "60%" },
          { header: "Amount", width: "40%", align: "right" },
        ],
        rows: [
          ["Widget A", "$10.00"],
          ["Widget B", "$25.00"],
          ["Total", "$35.00"],
        ],
      },
      children: [],
    },
  },
};

// 返回一个可以发送的 Buffer
const buffer = await renderToBuffer(invoiceSpec);

// 在 Next.js 路由处理程序中：
export async function GET() {
  const buffer = await renderToBuffer(invoiceSpec);
  return new Response(buffer, {
    headers: { "Content-Type": "application/pdf" },
  });
}
```

## 邮件生成

```typescript
import { renderToHtml } from "@json-render/react-email";
import { schema, standardComponentDefinitions } from "@json-render/react-email";
import { defineCatalog } from "@json-render/core";

const catalog = defineCatalog(schema, {
  components: standardComponentDefinitions,
});

const emailSpec = {
  root: "html-1",
  elements: {
    "html-1": {
      type: "Html",
      props: { lang: "en" },
      children: ["head-1", "body-1"],
    },
    "head-1": { type: "Head", props: {}, children: [] },
    "body-1": {
      type: "Body",
      props: { style: { backgroundColor: "#f6f9fc" } },
      children: ["container-1"],
    },
    "container-1": {
      type: "Container",
      props: { style: { maxWidth: "600px", margin: "0 auto" } },
      children: ["heading-1", "text-1", "button-1"],
    },
    "heading-1": {
      type: "Heading",
      props: { text: "Welcome aboard!" },
      children: [],
    },
    "text-1": {
      type: "Text",
      props: { text: "Thanks for signing up. Click below to get started." },
      children: [],
    },
    "button-1": {
      type: "Button",
      props: { text: "Get Started", href: "https://example.com" },
      children: [],
    },
  },
};

const html = await renderToHtml(emailSpec);
```

## MCP 集成（Claude, ChatGPT, Cursor）

```typescript
import { createMCPServer } from "@json-render/mcp";

const server = createMCPServer({
  catalog,
  name: "my-ui-server",
  version: "1.0.0",
});

server.start();
```

## 状态管理集成

```typescript
import { create } from "zustand";
import { createZustandAdapter } from "@json-render/zustand";

const useStore = create((set) => ({
  data: {},
  setData: (data) => set({ data }),
}));

const stateStore = createZustandAdapter(useStore);

// 传递给 Renderer 以使用状态处理操作
<Renderer spec={spec} registry={registry} stateStore={stateStore} />;
```

## YAML 线路格式

```typescript
import { parseYAML, toYAML } from "@json-render/yaml";

// AI 可以输出 YAML 而不是 JSON（通常更高效）
const yamlSpec = `
root: card-1
elements:
  card-1:
    type: Card
    props:
      title: Hello World
    children: [button-1]
  button-1:
    type: Button
    props:
      label: Click Me
    children: []
`;

const spec = parseYAML(yamlSpec);
```

## 完整的 Next.js App Router 示例

```tsx
// app/dashboard/page.tsx
import { generateObject } from "ai";
import { openai } from "@ai-sdk/openai";
import { getCatalogSchema, getCatalogPrompt } from "@json-render/core";
import { DashboardRenderer } from "./DashboardRenderer";
import { catalog } from "@/lib/catalog";

export default async function DashboardPage({
  searchParams,
}: {
  searchParams: { q?: string };
}) {
  const prompt = searchParams.q ?? "Show me a sales overview dashboard";

  const { object: spec } = await generateObject({
    model: openai("gpt-4o"),
    schema: getCatalogSchema(catalog),
    system: getCatalogPrompt(catalog),
    prompt,
  });

  return <DashboardRenderer spec={spec} />;
}
```

```tsx
// app/dashboard/DashboardRenderer.tsx
"use client";
import { Renderer } from "@json-render/react";
import { registry } from "@/lib/registry";
import { useRouter } from "next/navigation";

export function DashboardRenderer({ spec }) {
  const router = useRouter();

  return (
    <Renderer
      spec={spec}
      registry={registry}
      onAction={(action, payload) => {
        switch (action) {
          case "navigate":
            router.push(payload.path);
            break;
          case "export_report":
            window.open("/api/export", "_blank");
            break;
          case "refresh_data":
            router.refresh();
            break;
        }
      }}
    />
  );
}
```

## 常见模式

### 条件组件可用性

```typescript
// 根据用户角色限制目录
function getCatalogForRole(role: "admin" | "viewer") {
  const base = { Card, Stack, Heading, Text, Metric };
  const adminOnly = role === "admin" ? { Button, Form, Table } : {};
  const adminActions = role === "admin"
    ? { export: { description: "Export data" } }
    : {};

  return defineCatalog(schema, {
    components: { ...base, ...adminOnly },
    actions: adminOnly ? adminActions : {},
  });
}
```

### 带运行时数据的动态属性

```tsx
// 组件可以获取自己的数据
const { registry } = defineRegistry(catalog, {
  components: {
    LiveMetric: ({ props }) => {
      const { data } = useSWR(`/api/metrics/${props.metricId}`);
      return (
        <div>
          <span>{props.label}</span>
          <span>{data?.value ?? "..."}</span>
        </div>
      );
    },
  },
});
```

### 类型安全的操作处理

```typescript
import { type ActionHandler } from "@json-render/core";

const handleAction: ActionHandler<typeof catalog> = (action, payload) => {
  // action 和 payload 基于你的目录定义完全类型化
  if (action === "navigate") {
    router.push(payload.path); // payload.path 类型为 string
  }
};
```

## 故障排除

| 问题 | 原因 | 解决方法 |
|---|---|---|
| AI 生成未知组件类型 | 目录中不存在组件 | 将组件添加到 `defineCatalog` 或更新 AI 提示 |
| 属性验证错误 | AI 想象了属性 | 严格 Zod 模式，添加 `.strict()` 或 `.describe()` 提示 |
| 渲染器显示为空 | `root` 键不匹配 `elements` 键 | 检查规范结构；根必须引用一个有效的元素 ID |
| 部分规范渲染不正确 | 未处理流式传输 | 使用 `parseSpecStream` 工具或渲染前检查空元素 |
| 操作未触发 | 未传递 `onAction` 到 `Renderer` | 将 `onAction` 属性传递给 `<Renderer>` |
| shadcn 组件未样式化 | 缺少 Tailwind 配置 | 确保 `@json-render/shadcn` 路径在 `tailwind.config.js` 内容数组中 |
| 目录/注册表不匹配的 TypeScript 错误 | 确保 `defineRegistry(catalog, ...)` 使用相同的 `catalog` 实例 |

## 环境变量

```bash
# 用于 AI 生成（使用你喜欢的提供者）
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here

# 用于 MCP 服务器
MCP_SERVER_PORT=3001
```

## 关键 API 参考

```typescript
// 核心
defineCatalog(schema, { components, actions })  // 定义约束条件
getCatalogSchema(catalog)                        // 获取 AI 的 Zod 模式
getCatalogPrompt(catalog)                        // 获取 AI 的系统提示

// React
defineRegistry(catalog, { components })          // 创建类型化注册表
<Renderer spec={spec} registry={registry} onAction={fn} />

// 核心工具
parseSpecStream(stream)    // 解析流式部分规范
toYAML(spec)              // 将规范转换为 YAML
parseYAML(yaml)           // 解析 YAML 规范为 JSON

// PDF
renderToBuffer(spec)       // → Buffer
renderToStream(spec)       // → ReadableStream

// 邮件
renderToHtml(spec)         // → HTML 字符串
renderToText(spec)         // → 纯文本字符串
```
