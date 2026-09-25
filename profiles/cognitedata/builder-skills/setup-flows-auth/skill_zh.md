# 设置 Flows 身份验证

为 React 应用程序配置 Flows 身份验证，以便它能够与 Fusion 内部的 CDF 通信。存在两种流程；根据 `app.json` 选择其中一种。

## 选择流程

如果存在 `app.json`，请读取它：

| `app.json` `infra` | 流程 | 身份验证源 | 额外包 |
|---|---|---|---|
| `"appsApi"` | **Apps API**（新的 Fusion 应用程序主机） | `connectToHostApp` 从 `@cognite/app-sdk` | `@cognite/app-sdk` |
| 缺失 / 其他 | **经典**（遗留 Files API） | `DuneAuthProvider` + `useDune()` 从 `@cognite/dune` | — |

没有 `app.json`？询问用户。默认为 **Apps API** — 它是 `npx @cognite/cli@latest apps create` 的默认值。

## 第 1 步 — 读取状态，决定是否采取行动

读取 `package.json`、`src/main.tsx`（或 `src/index.tsx`）、`vite.config.ts`、`app.json`。

如果存在任何以下情况，则表示已经存在有效的设置 — 在这种情况下无需执行任何操作并报告无操作：

- **经典**：`<DuneAuthProvider>` 从 `@cognite/dune` 在入口文件中包装 `<App />`。
- **Apps API，提供程序模式**：`<CogniteSdkProvider>` 从 `@cognite/app-sdk/react` 包装应用程序（在 `App.tsx` 或 `main.tsx` 中），嵌套组件通过 `useCogniteSdk()` 消费客户端。需要 `@cognite/app-sdk >= 0.5.1`。

从锁文件中检测包管理器（`pnpm-lock.yaml` → pnpm，`yarn.lock` → yarn，否则 npm）。

## 第 2 步 — 安装缺失的依赖项

**经典流程：**

| 包 | 类型 |
|---|---|
| `@cognite/dune` | 运行时 |
| `@cognite/sdk` | 运行时 |
| `@tanstack/react-query` | 运行时 |
| `vite-plugin-mkcert` | 开发 |

**Apps API 流程：**

| 包 | 类型 |
|---|---|
| `@cognite/app-sdk` | 运行时 |
| `@cognite/sdk` | 运行时 |
| `@tanstack/react-query` | 运行时 |
| `vite-plugin-mkcert` | 开发 |

跳过 `package.json` 中已有的任何内容。使用检测到的包管理器（`pnpm add`，`npm install`，`yarn add`；`-D` / `--save-dev` 用于开发依赖项）。

## 第 3 步 — Vite 配置

仅添加缺失的内容。不要删除现有的插件。

### 经典流程

```ts
import { fusionOpenPlugin } from "@cognite/dune/vite";
import mkcert from "vite-plugin-mkcert";

export default defineConfig({
  base: "./",
  plugins: [react(), mkcert(), fusionOpenPlugin(), /* ... */],
  server: { port: 3001 },
  worker: { format: "es" },
});
```

### Apps API 流程

```ts
// 或查看 @cognite/cli/_templates/app/new/config/vite.config.ts.ejs.t 源文件以获取最新配置
import { fusionOpenPlugin, manifestCspPlugin } from "@cognite/app-sdk/vite";
import mkcert from "vite-plugin-mkcert";

export default defineConfig({
  base: "./",
  // manifestCspPlugin() 必须是第一个 — 其中间件在 HTML 响应之前设置 CSP 标头
  plugins: [manifestCspPlugin(), react(), mkcert(), fusionOpenPlugin(), /* ... */],
  server: { port: 3001 },
  worker: { format: "es" },
});
```

- `base: "./"` — 对于 Fusion iframe 部署是必需的。
- `mkcert()` — 为开发服务器提供 HTTPS（Fusion 父级是 HTTPS）。
- `fusionOpenPlugin()` — 自动在 Fusion 中打开开发 URL。
- `manifestCspPlugin()`（仅限 Apps API） — 强制执行 `manifest.json` 中声明的 CSP；必须为第一个。
- `server.port: 3001` — 惯例；如果未设置端口，插件会回退到 3001。

## 第 4 步 — 连接入口文件和组件

### 经典流程

`src/main.tsx`：

```tsx
import { DuneAuthProvider } from "@cognite/dune";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000, gcTime: 10 * 60 * 1000 } },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <DuneAuthProvider>
        <App />
      </DuneAuthProvider>
    </QueryClientProvider>
  </React.StrictMode>
);
```

在组件中，使用 `useDune()`：

```tsx
import { useDune } from "@cognite/dune";

const { sdk, isLoading, error } = useDune();
// sdk 是一个经过身份验证的 CogniteClient
```

### Apps API 流程（生成器默认，`@cognite/app-sdk >= 0.5.1`）

`src/main.tsx` 不用任何身份验证提供程序包装 — 身份验证在 `App.tsx` 内部处理：

```tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.tsx";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 5 * 60 * 1000, gcTime: 10 * 60 * 1000 } },
});

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>
);
```

`src/App.tsx` 使用 `@cognite/app-sdk/react` 的 `CogniteSdkProvider`。提供程序内部处理 Comlink 握手、加载和错误状态。嵌套组件通过 `useCogniteSdk()` 读取客户端：

```tsx
import { CogniteSdkProvider, useCogniteSdk } from "@cognite/app-sdk/react";

function AppContent() {
  const client = useCogniteSdk();
  // client 是一个经过身份验证的 CogniteClient
  return <div>{client.project}</div>;
}

function App() {
  return (
    <CogniteSdkProvider
      loadingFallback={<div>Loading...</div>}
      errorFallback={<div>Failed to connect to Fusion</div>}
    >
      <AppContent />
    </CogniteSdkProvider>
  );
}
```

如果 `CogniteSdkProvider` 外部调用 `useCogniteSdk()`，则会抛出错误 — 始终将其嵌套在内。

## 第 5 步 — 清理过时的代码

仅删除现在冗余的内容：

- 自定义 CDF 身份验证提供程序/钩子
- 手动 `CogniteClient` 实例化
- OIDC/令牌管理代码
- CDF 环境变量（`VITE_CDF_PROJECT`，`VITE_CDF_CLUSTER` 等）— Flows/主机提供这些

如有疑问，请保留并标记给用户。
