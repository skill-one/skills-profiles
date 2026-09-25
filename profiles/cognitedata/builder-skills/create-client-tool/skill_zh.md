# 创建客户端工具

使用 `AtlasTool` 框架创建一个名为 **$ARGUMENTS** 的工具。如果应用程序没有经过批准的 `useAtlasChat`，则通过 **`integrate-fusion-agent`** 实现一个 Fusion **操作**。

**前提条件：** 从 `integrate-atlas-chat` 中获取 `src/atlas-agent/` 和 `@sinclair/typebox`。

## 背景

客户端工具允许 Atlas Agent 调用浏览器端逻辑——图表、本地状态、UI 面板、导航。Agent 决定何时调用；应用程序执行并返回结果。

1. Agent 响应一个 `clientTool` 操作
2. TypeBox 验证参数
3. `execute()` 在浏览器中运行并返回 `{ output, details }`
4. `output`（字符串）发送回 Agent
5. `details` 可在 `message.toolCalls` 上用于 UI 渲染

---

## 第 1 步 — 理解代码库

在编写任何内容之前，请阅读：

- `useAtlasChat` 被调用的文件（通常是 `src/App.tsx` 或一个聊天钩子），以找到 `tools` 被传递的位置——导入通常来自 **`integrate-atlas-chat`** 后的 `./atlas-agent/react`
- 任何现有的工具定义，以匹配文件/命名约定

---

## 第 2 步 — 定义工具

使用 `@sinclair/typebox` 中的 `Type` 为参数模式定义（编译时类型 + 运行时验证）。

```ts
import { Type } from "@sinclair/typebox";
import type { AtlasTool } from "./atlas-agent/types";

export const myTool: AtlasTool = {
  name: "my_tool",            // snake_case — 这是 Agent 调用它时使用的名称
  description:
    "用一句话描述这个工具的作用以及 Agent 何时应该调用它。",
  parameters: Type.Object({
    exampleParam: Type.String({ description: "这个参数的用途" }),
    optionalNum: Type.Optional(Type.Number({ description: "..." })),
  }),
  execute: async (args) => {
    return {
      output: "发送回 Agent 的纯文本摘要",
      details: {
        // 你希望在 UI 中通过 message.toolCalls 获取的任何结构化数据
      },
    };
  },
};
```

如果工具文件不在 `src/` 下直接位于 `atlas-agent` 文件夹旁边（例如从 `src/tools/` 的 `../atlas-agent/types`），请调整 `./atlas-agent/...` 路径。

### TypeBox 快速参考

| 模式 | 用法 |
|---|---|
| `Type.String()` | 字符串 |
| `Type.Number()` | 数字 |
| `Type.Boolean()` | 布尔值 |
| `Type.Literal("foo")` | 精确值 |
| `Type.Union([Type.Literal("a"), Type.Literal("b")])` | 枚举 |
| `Type.Array(Type.String())` | 字符串[] |
| `Type.Object({ ... })` | 对象 |
| `Type.Optional(...)` | 将任何字段标记为可选 |

始终在工具和每个参数上添加 `description` — Agent 会使用这些字符串。

---

## 第 3 步 — 链接到 useAtlasChat

找到 `useAtlasChat` 调用并将工具添加到 `tools` 数组：

```ts
const { messages, send, ... } = useAtlasChat({
  client: isLoading ? null : sdk,
  agentExternalId: AGENT_EXTERNAL_ID,
  tools: [myTool],   // 添加在这里
});
```

---

## 第 4 步 — 渲染工具结果（如果需要）

如果工具返回结构化的 `details`，请在消息列表中渲染它们。
`message.toolCalls` 是一个 `ToolCall[]` — 按调用顺序，每个工具调用（客户端和服务器端）都有一个条目。
