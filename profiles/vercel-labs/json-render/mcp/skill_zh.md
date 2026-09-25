# @json-render/mcp

MCP 应用的集成，将 json-render UI 作为交互式 MCP 应用在 Claude、ChatGPT、Cursor、VS Code 和其他支持 MCP 的客户端中提供服务。

## 快速入门

### 服务器 (Node.js)

```typescript
import { createMcpApp } from "@json-render/mcp";
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { shadcnComponentDefinitions } from "@json-render/shadcn/catalog";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import fs from "node:fs";

const catalog = defineCatalog(schema, {
  components: { ...shadcnComponentDefinitions },
  actions: {},
});

const server = createMcpApp({
  name: "我的应用",
  version: "1.0.0",
  catalog,
  html: fs.readFileSync("dist/index.html", "utf-8"),
});

await server.connect(new StdioServerTransport());
```

### 客户端 (React，在 iframe 内)

```tsx
import { useJsonRenderApp } from "@json-render/mcp/app";
import { JSONUIProvider, Renderer } from "@json-render/react";

function McpAppView({ registry }) {
  const { spec, loading, error } = useJsonRenderApp();
  if (error) return <div>错误：{error.message}</div>;
  if (!spec) return <div>等待中...</div>;
  return (
    <JSONUIProvider registry={registry} initialState={spec.state ?? {}}>
      <Renderer spec={spec} registry={registry} loading={loading} />
    </JSONUIProvider>
  );
}
```

## 架构

1. `createMcpApp()` 创建一个 `McpServer`，该服务器注册一个 `render-ui` 工具和一个 `ui://` HTML 资源
2. 工具描述包含目录提示，以便大语言模型知道如何生成有效的规范
3. HTML 资源是一个使用 Vite 打包的单文件 React 应用，包含 json-render 渲染器
4. 在 iframe 内，`useJsonRenderApp()` 通过 `postMessage` 连接到主机并渲染规范

## 服务器 API

- `createMcpApp(options)` - 主要入口，创建一个完整的 MCP 服务器
- `registerJsonRenderTool(server, options)` - 在现有服务器上注册一个 json-render 工具
- `registerJsonRenderResource(server, options)` - 注册 UI 资源

## 客户端 API (`@json-render/mcp/app`)

- `useJsonRenderApp(options?)` - React 钩子，返回 `{ spec, loading, connected, error, callServerTool }`
- `buildAppHtml(options)` - 从打包的 JS/CSS 生成 HTML

## 构建 iframe HTML

使用 Vite + `vite-plugin-singlefile` 将 React 应用打包成一个自包含的单文件 HTML 文件：

```typescript
// vite.config.ts
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import { viteSingleFile } from "vite-plugin-singlefile";

export default defineConfig({
  plugins: [react(), viteSingleFile()],
  build: { outDir: "dist" },
});
```

## 客户端配置

### Cursor (`.cursor/mcp.json`)

```json
{
  "mcpServers": {
    "my-app": {
      "command": "npx",
      "args": ["tsx", "server.ts", "--stdio"]
    }
  }
}
```

### Claude Desktop

```json
{
  "mcpServers": {
    "my-app": {
      "command": "npx",
      "args": ["tsx", "/path/to/server.ts", "--stdio"]
    }
  }
}
```

## 依赖项

```bash
# 服务器
npm install @json-render/mcp @json-render/core @modelcontextprotocol/sdk

# 客户端 (iframe)
npm install @json-render/react @json-render/shadcn react react-dom

# 构建工具
npm install -D vite @vitejs/plugin-react vite-plugin-singlefile
```
