# 设置 Python 工具执行

为 **$ARGUMENTS** 添加客户端 Pyodide 执行。如果应用使用 Atlas / EOS 侧边栏 (`integrate-fusion-agent`)，则跳过此步骤。

**前提条件：** 从 `integrate-atlas-chat` 获取 `src/atlas-agent/`，以及 `@sinclair/typebox`。将 `python.ts`、`pyodide.ts`、`pyodide-react.ts`、`pyodide-runtime.ts` 从 `integrate-atlas-chat/code/` 复制到 `src/atlas-agent/`。

CDF `runPythonCode` 工具以 `toolConfirmation` + `clientTool` 的形式出现。将 `usePyodideRuntime` 连接并传递 `pythonRuntime` 到 `useAtlasChat` — 无需 `PythonToolConfig` 条目。Pyodide 大约 30MB，首次加载后将被缓存。

---

## 第 1 步 — 理解应用

在触摸任何内容之前，请阅读这些文件：

- `package.json` — 检测包管理器和现有依赖项
- 调用 `useAtlasChat` 的组件 — 了解当前工具/配置

---

## 第 2 步 — 安装 Pyodide

使用应用的包管理器**精确地**安装 `pyodide@0.29.3`。
此版本必须与运行时加载的 CDN 资产匹配 — 安装不同版本将导致错误。

- pnpm → `pnpm add pyodide@0.29.3`
- npm  → `npm install pyodide@0.29.3`
- yarn → `yarn add pyodide@0.29.3`

> `@sinclair/typebox` 应已从 `integrate-atlas-chat` 安装。如果缺失，请添加它。

---

## 第 3 步 — 设置 usePyodideRuntime

在调用 `useAtlasChat` 的组件中，添加 Pyodide 运行时钩子：

```tsx
import { loadPyodide } from "pyodide";
import { usePyodideRuntime } from "./atlas-agent/pyodide-react";
import { useAtlasChat } from "./atlas-agent/react";

function MyChat() {
  const { sdk, isLoading } = useDune();

  // 初始化 Python 运行时（加载 Pyodide、安装包、设置 Cognite SDK）
  const {
    runtime: pythonRuntime,
    loading: pythonLoading,
    progress: pythonProgress,
    error: pythonError,
    isReady: pythonReady,
  } = usePyodideRuntime({
    loadPyodide,
    client: isLoading ? null : sdk,
    requirements: ["pandas", "numpy"],    // 可选 — 额外包
  });

  // ... 下面使用 useAtlasChat
}
```

### 钩子 API 参考

| 返回字段 | 类型 | 描述 |
|---|---|---|
| `runtime` | `PythonRuntime \| undefined` | 初始化的运行时，如果未准备好则为 undefined |
| `loading` | `boolean` | Pyodide 正在加载/初始化时为 True |
| `error` | `string \| null` | 初始化失败时的错误消息 |
| `progress` | `{ stage: string; percent: number }` | 当前初始化进度，用于 UI 显示 |
| `isReady` | `boolean` | 便利性：`!loading && !error && runtime !== undefined` |

### 加载状态 UI

将加载指示器**放置在聊天输入框上方**，而不是消息列表中。
保持它紧凑 — 一个显示阶段文本和百分比的药丸/徽章。单独显示错误徽章。
首次加载需要 ~30-60s（下载 ~30MB）；后续加载从浏览器缓存中 <2s。

```tsx
{/* 加载 — Pyodide 初始化时在输入框上方显示 */}
{pythonLoading && (
  <div className="flex items-center gap-2 rounded-lg border bg-muted/50 px-3 py-2 text-sm text-muted-foreground">
    {/* 可选：`<IconBrandPython />` 来自 @tabler/icons-react */}
    <span>{pythonProgress.stage || "正在初始化 Python..."}</span>
    {pythonProgress.percent > 0 && pythonProgress.percent < 100 && (
      <span className="text-xs opacity-70">({pythonProgress.percent}%)</span>
    )}
  </div>
)}

{/* 错误 — 如果初始化失败（加载完成后）显示 */}
{pythonError && !pythonLoading && (
  <div className="flex items-center gap-2 rounded-lg border border-destructive/30 bg-destructive/10 px-3 py-2 text-sm text-destructive">
    <span>Python 运行时加载失败</span>
  </div>
)}
```

---

## 第 4 步 — 连接到 useAtlasChat

将运行时传递给 `useAtlasChat`。这样就足够了 — 无需工具配置：

```tsx
const { messages, send, isStreaming, progress, error, reset, abort } = useAtlasChat({
  client: isLoading ? null : sdk,
  agentExternalId: "my-agent",
  tools: [renderTimeSeries],   // 普通客户端工具（声明给代理），如果有
  pythonRuntime,               // 来自 usePyodideRuntime — 启用 Python 工具执行
});
```

**注意**：Python 工具不是通过 `tools` 声明给代理的。代理已经从其 CDF 配置中知道它们。库在需要时自动获取代码。

---

## 第 5 步 — 在 Python 加载时禁用输入

在运行时准备好之前，用户不应发送消息。禁用**整个输入区域**（而不仅仅是发送按钮），以便状态明确：

```tsx
<ChatInput
  onSend={handleSend}
  disabled={isStreaming || pythonLoading}
  // ...
/>
```

如果您有一个带有建议芯片的主页，也禁用它们：

```tsx
<ChatHomePage
  onSuggestionClick={handleSuggestionClick}
  disabled={pythonLoading}
/>
```

---

## 完成

应用现在可以通过 Pyodide 在客户端执行 Python 工具。当代理调用 Python 工具时，库会自动从代理配置中获取其代码，在浏览器中运行它，并将结果返回给代理。
