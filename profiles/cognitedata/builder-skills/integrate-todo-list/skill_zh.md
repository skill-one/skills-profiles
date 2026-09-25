# 集成待办事项列表

添加一个 `TodoWrite` 工具和面板，以便应用内的 Atlas 代理可以显示任务进度。

如果应用使用 Atlas / EOS 侧边栏（`integrate-fusion-agent`），则跳过此步骤。前提条件：`useAtlasChat` + `src/atlas-agent/` + 从 `integrate-atlas-chat` 引入的 `@sinclair/typebox`。

---

## 第 1 步 — 读取应用

在编写任何内容之前，请阅读：

- `package.json` — 确认已安装 `@tabler/icons-react`；如果没有，请使用应用的包管理器安装它
- `src/App.tsx` — 找到添加 `TodoProvider` 的位置
- 调用 `useAtlasChat` 的文件（可能是 `src/chat/useChatViewModel.ts` 或 `src/App.tsx`）— 这是将工具连接起来的地方
- 渲染消息的聊天视图组件 — 这是放置 `TodoPanel` 和 `TodoToolResultCard` 的地方

---

## 第 2 步 — 创建 `src/todo/` 模块

通过在项目根目录下运行 `find . -path "*/.agents/skills/integrate-todo-list/code" -type d` 找到技能目录。

从 `<skill-dir>/code/` 中的每个文件读取内容，并使用相同的文件名写入 `src/todo/`：

| 文件 | 目的 |
|------|---------|
| `types.ts` | `TodoItem` 和 `TodoList` 类型 |
| `TodoContext.tsx` | React 上下文 + `TodoProvider` |
| `useTodoList.ts` | 用于读取/写入待办事项列表的钩子 |
| `todoWriteTool.ts` | `createTodoWriteTool` 工厂 — 具有完整 CDF 任务分解指导的 `AtlasTool` |
| `useTodoWriteTool.ts` | 使用当前状态访问的钩子，缓存工具 |
| `TodoPanel.tsx` | 卡片 UI：进度条 + 任务行 |
| `TodoItemRow.tsx` | 带有动画状态图标的单个行 |
| `TodoToolResultCard.tsx` | 用于工具调用显示的紧凑摘要卡片 |

所有文件使用相对导入（`./types`、`./TodoContext` 等）— 无需更改。

---

## 第 3 步 — 用 `TodoProvider` 包裹应用

在 `src/App.tsx`（或根组件）中，用 `<TodoProvider>` 包裹现有树：

```tsx
import { TodoProvider } from './todo/TodoContext'; // 调整路径以匹配应用规范

function App() {
  return (
    <TodoProvider>
      {/* 现有子元素 */}
    </TodoProvider>
  );
}
```

---

## 第 4 步 — 将工具连接到 `useAtlasChat`

在调用 `useAtlasChat` 的文件中，添加以下内容。调整导入路径以匹配应用的规范。

```ts
import { useRef, useCallback } from 'react';
import { useTodoList } from './todo/useTodoList';
import { useTodoWriteTool } from './todo/useTodoWriteTool';

// 在钩子/组件内部：
const { todos, setTodos } = useTodoList();
const todoWriteTool = useTodoWriteTool();

// 保持一个引用，以便 `getAppContext` 总是读取最新状态，而不会重新创建回调。
const todosRef = useRef(todos);
todosRef.current = todos;

const getAppContext = useCallback(() => {
  const t = todosRef.current;
  if (t.length === 0) return undefined;
  const lines = t.map((item, i) => `${i + 1}. [${item.status}] ${item.content}`);
  return `当前待办事项列表：\n${lines.join('\n')}`;
}, []);

// 添加到 `useAtlasChat` 选项：
const { messages, send, isStreaming, progress, error, reset, abort } = useAtlasChat({
  client: isLoading ? null : sdk,
  agentExternalId: AGENT_EXTERNAL_ID,
  tools: [todoWriteTool],   // 与现有工具一起添加
  getAppContext,
});

// 在重置处理程序中，清空待办事项列表：
const handleReset = useCallback(() => {
  reset();
  setTodos([]);
}, [reset, setTodos]);

// 在返回值中暴露 `todos`，以便视图可以渲染 `TodoPanel`：
return { ..., todos };
```

---

## 第 5 步 — 在聊天视图中渲染 `TodoPanel`

在渲染聊天输入区域的组件中，在输入字段上方添加 `<TodoPanel>`：

```tsx
import { TodoPanel } from './todo/TodoPanel'; // 调整路径

// 在渲染中：
<TodoPanel todos={todos} />
<YourChatInput ... />
```

`TodoPanel` 在列表为空时会返回 `null`，因此始终渲染它是安全的。

---

## 第 6 步 — 为工具调用步骤渲染 `TodoToolResultCard`

在渲染每条消息工具调用的组件中（通常是步骤手风琴或类似结构），根据工具名称进行分支：

```tsx
import { TodoToolResultCard } from './todo/TodoToolResultCard'; // 调整路径

{toolCalls.map((tc, i) =>
  tc.name === 'TodoWrite' ? (
    <TodoToolResultCard key={i} toolCall={tc} />
  ) : (
    <YourDefaultToolCallCard key={i} toolCall={tc} />
  )
)}
```

---

## 第 7 步 — 验证

运行应用的类型检查命令（通常是 `pnpm tsc --noEmit`），并确认没有错误。
如果项目有测试，请运行它们以确认没有回归。

---

## 完成

代理现在可以使用 `TodoWrite` 来创建和跟踪任务。它将：

- 一旦开始多步骤工作，就会显示任务面板
- 实时更新任务状态（`pending` → `in_progress` → `completed`）
- 当所有任务完成时自动清空列表
- 通过 `getAppContext` 将当前任务列表注入每个提示，以便知道它之前在哪里停止
