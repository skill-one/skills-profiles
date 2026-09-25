这项技能建立在 copilotkit/react-core（用于 `CopilotKit` 提供者基础）和 copilotkit/runtime（用于 CopilotRuntime 基础）之上。请先阅读这些内容。

## 设置

A2UI 有两个部分。运行时声明 a2ui 中间件；客户端启用提供者上的 a2ui 属性。一旦两者都设置完成，`/info` 会标记 A2UI，客户端会自动挂载 `createA2UIMessageRenderer` — 你不需要自己连接 `renderActivityMessages`。

### 运行时部分 (`app/routes/api.copilotkit.$.tsx`)

```tsx
import type { Route } from "./+types/api.copilotkit.";
import {
  CopilotRuntime,
  createCopilotRuntimeHandler,
  BuiltInAgent,
  convertInputToTanStackAI,
} from "@copilotkit/runtime/v2";
import { chat } from "@tanstack/ai";
import { openaiText } from "@tanstack/ai-openai";

const agent = new BuiltInAgent({
  type: "tanstack",
  factory: ({ input, abortController }) => {
    const { messages, systemPrompts } = convertInputToTanStackAI(input);
    return chat({
      adapter: openaiText("gpt-4o"),
      messages,
      systemPrompts,
      abortController,
    });
  },
});

const runtime = new CopilotRuntime({
  agents: { default: agent },
  // 启用这个键会导致 `/info` 向客户端宣传 A2UI。
  a2ui: {},
});

const handler = createCopilotRuntimeHandler({
  runtime,
  basePath: "/api/copilotkit",
});

export async function loader({ request }: Route.LoaderArgs) {
  return handler(request);
}
export async function action({ request }: Route.ActionArgs) {
  return handler(request);
}
```

### 客户端部分 (`app/root.tsx` 或应用外壳)

```tsx
import { CopilotKit, CopilotChat } from "@copilotkit/react-core/v2";
import "@copilotkit/react-core/v2/styles.css";

export default function App() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      a2ui={{
        theme: {
          // 传递给 A2UIProvider → ThemeProvider 的主题对象。
          // Tokens 映射到 A2UI 的基本目录 CSS 变量。
          colors: { primary: "#0ea5e9" },
        },
      }}
    >
      <CopilotChat agentId="default" className="h-full" />
    </CopilotKit>
  );
}
```

## 核心模式

### 自定义目录

传递自定义目录以扩展内置组件集。`createCatalog` 和 `extractSchema` 让代理看到它可以渲染哪些组件。

```tsx
import { createCatalog } from "@copilotkit/a2ui-renderer";
import { z } from "zod";

const theme = { colors: { primary: "#0ea5e9" } };

// 定义是平台无关的（Zod 模式 + 描述）。
// 渲染器是平台特定的（React 组件）。
// TypeScript 强制要求渲染器键与定义键完全匹配。
const definitions = {
  ProductCard: {
    description: "一个带有标题和价格的产品卡片",
    props: z.object({ title: z.string(), price: z.number() }),
  },
};

const catalog = createCatalog(
  definitions,
  {
    ProductCard: ({ props }) => (
      <div className="rounded-xl border p-3">
        <div className="font-medium">{props.title}</div>
        <div className="text-sm text-muted-foreground">${props.price}</div>
      </div>
    ),
  },
  { includeBasicCatalog: true },
);

<CopilotKit runtimeUrl="/api/copilotkit" a2ui={{ theme, catalog }}>
  <CopilotChat agentId="default" />
</CopilotKit>;
```

`extractSchema(definitions)` 可用于将定义的 JSON-序列化视图传递给运行时的 `a2ui.schema` 配置 — 它不是一个通用的类型助手。类型参数在运行时会被擦除；代理需要一个真实的运行时模式值（Zod）。

### 覆盖加载骨架

```tsx
<CopilotKit
  runtimeUrl="/api/copilotkit"
  a2ui={{
    theme,
    loadingComponent: () => <div className="animate-pulse">正在构建 UI…</div>,
  }}
>
  <CopilotChat agentId="default" />
</CopilotKit>
```

## 常见错误

### 关键性忘记 runtime.a2ui

错误：

```tsx
// 服务器
new CopilotRuntime({ agents: { default: agent } });
// 客户端
<CopilotKit runtimeUrl="/api/copilotkit" a2ui={{ theme }} />;
```

正确：

```tsx
// 服务器
new CopilotRuntime({ agents: { default: agent }, a2ui: {} });
// 客户端
<CopilotKit runtimeUrl="/api/copilotkit" a2ui={{ theme }} />;
```

没有 `runtime.a2ui`，`/info` 从不标记 A2UI，提供者的 a2ui 属性静默无操作 — 渲染器从不挂载。

来源：packages/runtime/src/v2/runtime/core/runtime.ts:55-58,217,242

### 高度手动连接 renderActivityMessages 用于 A2UI

错误：

```tsx
import { createA2UIMessageRenderer } from "@copilotkit/react-core/v2";

<CopilotKit
  runtimeUrl="/api/copilotkit"
  renderActivityMessages={[createA2UIMessageRenderer({ theme })]}
/>;
```

正确：

```tsx
<CopilotKit runtimeUrl="/api/copilotkit" a2ui={{ theme }} />
```

`CopilotKit` 提供者通过 `/info` 自动检测运行时 A2UI 并注入内置渲染器。通过 `renderActivityMessages` 传递它会重复渲染器，并可能与自动注入的渲染器竞争。

来源：packages/react-core/src/v2/providers/CopilotKitProvider.tsx:188-222,294-296

### 中等重新发射 createSurface 在每个快照

错误：

```python
# 伪代码 — 在你的代理生成器内部。确切的 API 名称/参数因 A2UI SDK 版本而异；查阅你的 SDK 文档以获取真实的调用形状。
async def agent_generator():
    # 代理在每个状态增量时重新发射 createSurface 操作
    async for update in stream:
        yield a2ui.create_surface(surface_id="main", ...)  # 每个快照
        yield a2ui.update_components(...)
```

正确：

```python
# 伪代码 — 在你的代理生成器内部。
# 每个表面Id 发射一次 createSurface；使用 updateComponents / updateDataModel 进行更改。
async def agent_generator():
    yield a2ui.create_surface(surface_id="main", ...)  # 一次
    async for update in stream:
        yield a2ui.update_components(surface_id="main", ...)
```

MessageProcessor 在 `surfaceId` 上去重，但重新发射是一个代理端的错误 — 客户端为无意义地重新运行调和逻辑并闪烁。

来源：packages/react-core/src/v2/a2ui/A2UIMessageRenderer.tsx:218-226

### 中等没有 a2uiAction 清理的自定义操作桥

错误：

```ts
copilotkit.setProperties({ ...copilotkit.properties, a2uiAction: msg });
await copilotkit.runAgent({ agent });
// 没有 finally — a2uiAction 泄漏到下一次运行的性质
```

正确：

```ts
try {
  copilotkit.setProperties({ ...copilotkit.properties, a2uiAction: msg });
  await copilotkit.runAgent({ agent });
} finally {
  if (copilotkit.properties) {
    const { a2uiAction, ...rest } = copilotkit.properties;
    copilotkit.setProperties(rest);
  }
}
```

内置桥接器总是在 `finally` 中删除 `a2uiAction`，并由 `copilotkit.properties` 的空检查保护，所以它不会用 `TypeError` 掩盖原始 `runAgent` 错误。跳过清理会保留先前操作连接到后续运行。

来源：packages/react-core/src/v2/a2ui/A2UIMessageRenderer.tsx:146-167

### 中等安装 @copilotkitnext/a2ui-renderer

错误：

```ts
import { createA2UIMessageRenderer } from "@copilotkitnext/a2ui-renderer";
```

正确：

```ts
// 低级原语（很少需要 — CopilotKit 提供者的 a2ui 属性是默认路径）：
import {
  A2UIProvider,
  A2UIRenderer,
  createCatalog,
} from "@copilotkit/a2ui-renderer";
// 自动挂载的渲染器位于 react-core/v2：
import { createA2UIMessageRenderer } from "@copilotkit/react-core/v2";
```

这个包作为 `@copilotkit/a2ui-renderer` 提供，不是 `@copilotkitnext/a2ui-renderer`。`@copilotkitnext/` 范围保留用于其他单独提供的包 — 不要假设它适用于这里。

来源：packages/a2ui-renderer/package.json
