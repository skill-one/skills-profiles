# CopilotKit v1到v2迁移指南

## 在线文档 (MCP)

此插件包含一个MCP服务器(`copilotkit-docs`)，提供`search-docs`和`search-code`工具用于查询在线CopilotKit文档和源代码。在迁移过程中查找当前v2 API签名时很有用。

- **Claude代码:** 由插件的`.mcp.json`自动配置 -- 无需设置。
- **Codex:** 需要手动配置。请参阅[ copilotkit-debug技能 ](../copilotkit-debug/SKILL.md#mcp-setup)的设置说明。

## 概述

CopilotKit v2是基于AG-UI协议(`@ag-ui/client` / `@ag-ui/core`)从零开始重写的。用户继续安装和导入`@copilotkit/*`包 -- v2的变更通过相同的包名（在其`/v2`子路径下）暴露，API已更新（新的钩子名称、组件名称、运行时配置）。底层的`@ag-ui/*`包是内部实现细节，通过`@copilotkit/react-core/v2`重新导出，因此用户无需直接安装它们。

## 迁移工作流程

### 1. 审计当前使用情况

扫描代码库中所有v1导入和API使用情况：

```
@copilotkit/react-core    -> 钩子、CopilotKit提供器、类型
@copilotkit/react-ui      -> CopilotChat、CopilotPopup、CopilotSidebar
@copilotkit/react-textarea -> CopilotTextarea (v2中已移除)
@copilotkit/runtime       -> CopilotRuntime、服务适配器、框架集成
@copilotkit/runtime-client-gql -> GraphQL客户端、消息类型
@copilotkit/shared         -> 工具类型、常量
@copilotkit/sdk-js         -> LangGraph/LangChain SDK
```

### 2. 识别已弃用的API

需要查找和替换的关键钩子和组件：

| v1 API                             | v2替换                                             |
| ---------------------------------- | ---------------------------------------------------------- |
| `useCopilotAction`                 | `useFrontendTool`                                          |
| `useCopilotReadable`               | `useAgentContext`                                          |
| `useCopilotChat`                   | `useAgent`                                                 |
| `useCoAgent`                       | `useAgent`                                                 |
| `useCoAgentStateRender`            | `useRenderTool` / `useRenderActivityMessage`               |
| `useCopilotContext`                | `useCopilotKit` (来自`@copilotkit/react-core/v2/context`) |
| `useLangGraphInterrupt`            | `useInterrupt`                                             |
| `useCopilotChatSuggestions`        | `useConfigureSuggestions` + `useSuggestions`               |
| `useCopilotAdditionalInstructions` | `useAgentContext`                                          |
| `useMakeCopilotDocumentReadable`   | `useAgentContext`                                          |
| `CopilotKit` (根导入)             | `CopilotKit` (来自`@copilotkit/react-core/v2`)            |
| `CopilotTextarea`                  | 已移除 -- 使用标准textarea + `useFrontendTool`       |

### 3. 映射到v2等价物

参考`references/v1-to-v2-migration.md`获取详细的原始/修改后代码示例。

### 4. 更新包依赖项

`@copilotkit/*`包名称保持不变。v2不会引入新的包名称 -- v2 API从现有包的`/v2`子路径中发布（`@copilotkit/react-core/v2`，`@copilotkit/runtime/v2`）。没有`@copilotkit/react`或`@copilotkit/agent`包。更新到最新的v2版本：

```
@copilotkit/react-core         -> @copilotkit/react-core (v2符号位于/v2子路径下)
@copilotkit/react-ui           -> 聊天组件移至@copilotkit/react-core/v2；react-ui在v2中仅贡献样式
@copilotkit/react-textarea     -> 已移除 (v2无等价物)
@copilotkit/runtime            -> @copilotkit/runtime (v2符号位于/v2子路径下)
@copilotkit/runtime-client-gql -> 已移除 (被AG-UI协议取代；@ag-ui/client类型从@copilotkit/react-core/v2重新导出)
@copilotkit/shared             -> @copilotkit/shared (相同包)
@copilotkit/sdk-js             -> 已移除 (BuiltInAgent现从@copilotkit/runtime/v2发布)
```

### 5. 更新运行时配置

v1 `CopilotRuntime`接受服务适配器（OpenAI、Anthropic、LangChain等）和端点定义。v2 `CopilotRuntime`直接接受AG-UI `AbstractAgent`实例。

**v1模式** (服务适配器 + 端点):

```ts
import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime";
const runtime = new CopilotRuntime({ actions: [...] });
// 与框架处理器如copilotRuntimeNextJSAppRouterEndpoint() (Next.js)等一起使用
```

**v2模式** (代理 + Hono端点):

```ts
import {
  CopilotRuntime,
  BuiltInAgent,
  createCopilotHonoHandler,
} from "@copilotkit/runtime/v2";
const runtime = new CopilotRuntime({
  agents: { myAgent: new BuiltInAgent({ model: "openai/gpt-4o" }) },
});
const app = createCopilotHonoHandler({ runtime, basePath: "/api/copilotkit" });
```

> 使用`createCopilotHonoHandler`（来自`@copilotkit/runtime/v2`）作为标准的Hono端点工厂。`createCopilotEndpoint`是**已弃用**的别名 -- 在新代码中避免使用。对于Express，使用`@copilotkit/runtime/v2/express`中的`createCopilotExpressHandler` (`createCopilotEndpointExpress`是其已弃用的别名)。

### 6. 更新提供器

提供器组件保持名称`CopilotKit` -- 仅导入路径更改。包根(`@copilotkit/react-core`)是遗留v1提供器；`/v2`子路径是迁移目标。

**v1 (根导入):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";
<CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>;
```

**v2 (`/v2`导入):**

```tsx
import { CopilotKit } from "@copilotkit/react-core/v2";
<CopilotKit runtimeUrl="/api/copilotkit">{children}</CopilotKit>;
```

> **注意:** `@copilotkit/react-core/v2`还导出`CopilotKitProvider`组件。不要迁移到它 -- 它是`CopilotKit`的功能子集，是v1和v2之间的兼容性桥梁，并接受`CopilotKitProvider`的所有属性。

### 7. 验证

- 运行应用程序并检查运行时错误
- 验证所有代理交互是否正常工作（聊天、工具调用、中断）
- 检查工具渲染器是否正确显示
- 确认建议是否加载并显示

## 快速参考

| 概念              | v1                                              | v2                                                                                 |
| -------------------- | ----------------------------------------------- | ---------------------------------------------------------------------------------- |
| 包范围        | `@copilotkit/*`                                 | `@copilotkit/*` (相同范围，更新API)                                         |
| 协议             | GraphQL                                         | AG-UI (SSE)                                                                        |
| 提供器组件   | `CopilotKit` (来自`@copilotkit/react-core`)    | `CopilotKit` (来自`@copilotkit/react-core/v2`)                                    |
| 定义前端工具 | `useCopilotAction`                              | `useFrontendTool`                                                                  |
| 共享应用状态      | `useCopilotReadable`                            | `useAgentContext`                                                                  |
| 代理交互    | `useCoAgent`                                    | `useAgent`                                                                         |
| 处理中断    | `useLangGraphInterrupt`                         | `useInterrupt`                                                                     |
| 渲染工具调用    | `useCopilotAction({ render })`                  | `useFrontendTool({ render })` 或 `useRenderTool` (仅渲染)                     |
| 聊天建议     | `useCopilotChatSuggestions`                     | `useConfigureSuggestions`                                                          |
| 运行时类        | `CopilotRuntime` (适配器)                     | `CopilotRuntime` (代理，来自`@copilotkit/runtime/v2`)                           |
| 端点设置       | `copilotRuntimeNextJSAppRouterEndpoint()`       | `createCopilotHonoHandler()` (`createCopilotEndpoint`是已弃用的别名)       |
| 代理定义     | `LangGraphAgent` 端点                       | `AbstractAgent` / `BuiltInAgent` (来自`@copilotkit/runtime/v2`)                   |
| 聊天组件      | `CopilotChat`，`CopilotPopup`，`CopilotSidebar` | `CopilotChat`，`CopilotPopup`，`CopilotSidebar` (来自`@copilotkit/react-core/v2`) |
