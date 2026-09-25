# assistant-ui React MCP

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

`@assistant-ui/react-mcp` 允许用户在浏览器中连接预设或自定义的 Streamable HTTP MCP 服务器。该管理器持久化服务器和认证状态，将连接状态暴露给基础组件，并将每个连接的工具注册到 `modelContext` 中，作为前端工具名为 `serverId__toolName`。

## 参考

- [./references/setup.md](./references/setup.md) -- 管理器配置、存储、状态、命令式方法以及资源读取
- [./references/ui.md](./references/ui.md) -- 复制的配置对话框以及每个管理器、服务器和添加表单基础组件
- [./references/oauth.md](./references/oauth.md) -- 认证形状、OAuth 回调处理、CIMD 以及连接状态

## 挂载管理器

使用 `defineConnector` 声明固定连接器，然后使用配置扩展最近的 `aui` 范围。`connectionTimeout` 是管理器的默认值，以毫秒为单位。连接器或自定义服务器可以覆盖它，以用于自己的连接和 `listTools()` 就绪流程。

```tsx
"use client";

import type { ReactNode } from "react";
import { AuiConfig, AuiProvider, useAui } from "@assistant-ui/react";
import { McpManagerResource, defineConnector } from "@assistant-ui/react-mcp";

const connectors = [
  defineConnector({
    id: "linear",
    name: "Linear",
    url: "https://mcp.linear.app",
    auth: { type: "oauth", scopes: ["read"] },
    icon: "/icons/linear.svg",
  }),
  defineConnector({
    id: "weather",
    name: "Weather",
    url: "https://mcp.example.com/weather",
    auth: { type: "none" },
    connectionTimeout: 10_000,
  }),
];

export function Providers({ children }: { children: ReactNode }) {
  const aui = useAui();
  const config = AuiConfig({
    mcp: McpManagerResource({
      connectors,
      connectionTimeout: 15_000,
    }),
  });

  return (
    <AuiProvider extends={aui} config={config}>
      {children}
    </AuiProvider>
  );
}
```

连接器是应用程序的预设，不能被移除。自定义服务器通过 `McpAddFormPrimitive` 或 `aui.mcp.addCustomServer(...)` 供用户使用。这两种类型共享状态、存储、提示和工具注册路径。有关管理器选项和存储生命周期规则，请参阅 [setup](./references/setup.md)。

## 前端工具调用后继续

管理器会自动注册连接的工具。聊天运行时仍然需要将完成的前端工具结果发送到路由，以便模型可以继续。

```tsx
"use client";

import type { ReactNode } from "react";
import { lastAssistantMessageIsCompleteWithToolCalls } from "ai";
import { AssistantRuntimeProvider } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";

export function Chat({ children }: { children: ReactNode }) {
  const runtime = useChatRuntime({
    sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls,
  });

  return <AssistantRuntimeProvider runtime={runtime}>{children}</AssistantRuntimeProvider>;
}
```

如果没有聊天运行时提供 `modelContext`，管理器会挂载一个最小的聊天运行时。在事件处理程序中直接调用时，使用 `aui.mcp.server({ id }).callTool(...)`。

## 使用配置 UI

使用 `npx assistant-ui@latest add mcp-config` 安装带样式的对话框。它是一个复制的运行时连接元素，因此从 `@/components/assistant-ui/elements/mcp-config.aui` 导入它，并在管理器提供程序下渲染它。

```tsx
import { McpConfigDialog } from "@/components/assistant-ui/elements/mcp-config.aui";

export function ServerSettings() {
  return <McpConfigDialog />;
}
```

将一个元素作为 `children` 传递以替换其默认触发器。对于设置页面、侧边栏或自定义添加流程，请在 [ui](./references/ui.md) 中组合无头基础组件。

## 渲染提示请求

MCP 服务器可以在工具调用进行中请求结构化输入。在连接的服务器相同的 `mcpServer` 范围内渲染 `Items`。在连接器或自定义服务器上设置 `elicitation: false` 以退出协议功能。

```tsx
import { McpElicitationPrimitive } from "@assistant-ui/react-mcp";

type FieldSchema = {
  type?: string;
  enum?: readonly string[];
};

export function ElicitationRequests() {
  return (
    <McpElicitationPrimitive.Items>
      {() => (
        <McpElicitationPrimitive.Root>
          <McpElicitationPrimitive.Message />
          <McpElicitationPrimitive.Error />
          <McpElicitationPrimitive.Fields>
            {({ name, schema, value, setValue }) => {
              const field = schema as FieldSchema;
              if (field.type === "boolean") {
                return (
                  <label>
                    {name}
                    <input
                      type="checkbox"
                      checked={value === true}
                      onChange={(event) => setValue(event.target.checked)}
                    />
                  </label>
                );
              }
              if (field.enum) {
                return (
                  <label>
                    {name}
                    <select
                      value={typeof value === "string" ? value : ""}
                      onChange={(event) => setValue(event.target.value)}
                    >
                      {!field.enum.includes("") && <option value="">Select {name}</option>}
                      {field.enum.map((option) => (
                        <option key={option} value={option}>
                          {option}
                        </option>
                      ))}
                    </select>
                  </label>
                );
              }
              return (
                <label>
                  {name}
                  <input
                    value={typeof value === "string" || typeof value === "number" ? String(value) : ""}
                    onChange={(event) => setValue(event.target.value)}
                  />
                </label>
              );
            }}
          </McpElicitationPrimitive.Fields>
          <McpElicitationPrimitive.Accept>Submit</McpElicitationPrimitive.Accept>
          <McpElicitationPrimitive.Decline>Decline</McpElicitationPrimitive.Decline>
          <McpElicitationPrimitive.Cancel>Cancel</McpElicitationPrimitive.Cancel>
        </McpElicitationPrimitive.Root>
      )}
    </McpElicitationPrimitive.Items>
  );
}
```

渲染函数每次都会接收到一个单独的活跃请求。当有效时，数字字符串会被强制转换，而布尔字段必须设置为布尔值。除非属性通过枚举成员或默认值允许，否则空字符串是未回答的，因此将枚举属性渲染为选择框。`Accept` 在缺少必填字段和无效值时仍然保持禁用状态。

## v1 范围

此包提供工具列表和调用、资源列表和读取、表单提示、带有 PKCE 和 DCR 的 OAuth、令牌和无需认证、Streamable HTTP 传输以及手动连接或断开连接。提示、采样、带退避的自动重连、每个工具的持久化启用、每个工具的同意以及内置的令牌加密功能被推迟。

## 常见问题

**工具从未到达模型**

- 服务器必须是 `connected`。其工具的名称为 `serverId__toolName`，而不仅仅是 MCP 工具名称。
- 在 `useChatRuntime` 上配置 `sendAutomaticallyWhen: lastAssistantMessageIsCompleteWithToolCalls`，以便完成的 frontend 工具调用继续模型。

**OAuth 回调失败或从未完成**

- 回调路由必须与 `oauthRedirectUri` 完全匹配，并在管理器提供程序下渲染 `McpOAuthCallback`。
- 没有注册端点的 CIMD 仅授权服务器需要一个静态 OAuth `clientId`。

**服务器状态跨用户泄漏或存储交换丢失记录**

- `McpLocalStorage()` 仅适用于浏览器，并以明文存储令牌。对于生产认证状态，请使用 HTTP 仅 cookie 支持的 `McpCustomStorage`。
- 不要为另一个用户交换 `storage`。重新挂载管理器，因为自定义服务器记录仅加载一次。请参阅 [存储身份](./references/setup.md#storage-and-scope-identity)。

**提示表单保持空白**

- `Items` 在没有挂起请求时不会渲染任何内容，并且需要匹配的服务器范围。确认服务器已连接并且没有设置 `elicitation: false`。

**资源浏览器在第一页后停止**

- 将每个返回的 `nextCursor` 传递给 `listResources({ cursor })`，直到它不存在，然后为选中的项目调用 `readResource(uri)`。

## 相关技能

- [tools](../tools/SKILL.md) -- 开发者拥有的前端和后端工具，补充用户管理的 MCP 服务器
- [setup](../setup/SKILL.md) -- CLI 设置和 `mcp` 项目模板
- [runtime](../runtime/SKILL.md) -- `useChatRuntime` 和运行时提供程序配置
- [elements](../elements/SKILL.md) -- 安装和修改复制的 `mcp-config` 元素
