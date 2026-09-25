# assistant-ui 运行时

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

运行时是聊天界面的状态和动作层：它拥有消息、线程、分支和运行生命周期，所有原始操作和钩子都通过统一的 `AssistantClient` 从中读取。构建运行时有两种方式。`LocalRuntime` (`useLocalRuntime`) 为你管理消息存储；你只需实现一个 `ChatModelAdapter.run` 函数，分支、编辑和再生功能即可免费使用。`ExternalStoreRuntime` (`useExternalStoreRuntime`) 则相反：你拥有消息，UI 功能的开启取决于你提供的回调。框架适配器（如 `useChatRuntime` (`@assistant-ui/ai-sdk`））和协议运行时（如 `useAssistantTransportRuntime`）都是基于这两种方式构建的。一旦在 `AssistantRuntimeProvider` 下挂载，每个运行时都以相同的方式被读取和驱动，通过 `useAui`、`useAuiState` 和 `useAuiEvent`。

## 参考

- [./references/local-runtime.md](./references/local-runtime.md) -- `useLocalRuntime` 深入：流式传输、工具调用、人机交互、审批门、恢复运行
- [./references/external-store.md](./references/external-store.md) -- `useExternalStoreRuntime` 深入：处理矩阵、分支、排队、工具结果
- [./references/state-hooks.md](./references/state-hooks.md) -- `useAui`、`useAuiState`、`useAuiEvent`、状态形状、已移除的遗留钩子
- [./references/types.md](./references/types.md) -- `ThreadMessage`、`MessageStatus`、`MessagePart`、附件和功能类型
- [./references/adapters.md](./references/adapters.md) -- 附件、语音、听写、反馈、建议和历史适配器
- [./references/voice.md](./references/voice.md) -- 使用 `RealtimeVoiceAdapter` 的实时双向语音
- [./references/runtime-concepts.md](./references/runtime-concepts.md) -- 不稳定_策略、`useAssistantTransportRuntime`、`MessageNotSentError`、重新加载主线程、消息时间

## 运行时层次结构

```
AssistantRuntime
├── ThreadListRuntime (threads)
│   └── ThreadListItemRuntime[] (threadListItem)
└── ThreadRuntime (thread)
    ├── ComposerRuntime (composer)        新消息输入
    ├── SuggestionRuntime[] (suggestion)  后续提示，通过 `thread.suggestions`
    └── MessageRuntime[] (message)
        ├── ComposerRuntime (composer)    编辑消息输入
        ├── MessagePartRuntime[] (part)
        ├── ChainOfThoughtRuntime (chainOfThought)
        │   └── MessagePartRuntime[] (part)
        └── AttachmentRuntime[] (attachment)
```

`modelContext` 和 `tools` 独立于线程范围独立解析；参见 [runtime-concepts.md](./references/runtime-concepts.md) 和 [tools](../tools/SKILL.md) 技能。树中的每个节点都可以从 `aui.<scope>`（命令式）或 `s.<scope>`（在 `useAuiState` 选择器内部）（响应式）中访问，自动范围到调用组件渲染的位置。

## useAui、useAuiState、useAuiEvent

`useAui()` 返回当前的 `AssistantClient`。它不会订阅状态，因此其身份仅在结构变化时改变（例如切换线程）；在事件处理程序和命令式代码中使用它。

```tsx
import { useAui } from "@assistant-ui/react";

const aui = useAui();
aui.thread.append({ role: "user", content: [{ type: "text", text: "Hello!" }] });
aui.thread.cancelRun();
```

`useAuiState(selector)` 订阅 `AssistantState` 的一部分，并且仅在选定值变化时（与 `Object.is` 相比）重新渲染。选择器在每个存储更新时运行，因此它必须返回一个原始值或一个稳定的引用，永远不会是一个新的对象或数组字面量，并且永远不会是整个状态（那会抛出错误）。

```tsx
import { useAuiState } from "@assistant-ui/react";

const isRunning = useAuiState((s) => s.thread.isRunning);   // 原始值：正确
const messages = useAuiState((s) => s.thread.messages);      // 稳定的数组引用：正确

// 错误：每次调用都返回一个新的对象字面量，导致每次存储更新时都重新渲染
const bad = useAuiState((s) => ({ isRunning: s.thread.isRunning, text: s.composer.text }));
```

对每个值调用一次 `useAuiState`（或组合多个调用）；不要将范围展开到一个新对象中来捆绑值。

`useAuiEvent(nameOrSelector, callback)` 在组件生命周期内订阅。回调在效果-事件包装器内部运行，因此最新的闭包会触发，而无需记忆化引用。

```tsx
import { useAuiEvent } from "@assistant-ui/react";

useAuiEvent("thread.modelContextUpdate", ({ threadId }) => {
  console.log("Model context updated", threadId);
});
```

## 范围访问器是属性

自 0.15 版本起，`aui.<scope>` 是一个属性，而不是一个调用；调用它 (`aui.thread()`) 仍然有效，但已弃用。范围上的方法保留其括号。

```tsx
aui.thread.getState();             // 属性访问器
aui.threads.switchToNewThread();
aui.thread.composer().send();      // `composer()` 是线程范围的一个方法
aui.thread.message({ index: 0 });  // 选择器对象，而不是裸索引
```

选择一个不可用的范围不再抛出错误；`aui.message` 始终为真。在使用前检查可用性，使用 `source`，当范围未挂载时 `source` 为 `null`：

```tsx
if (aui.message.source != null) {
  aui.message.reload();
}
```

`source`、`query` 和 `name` 是保留的访问器属性，永远不会解析为范围方法。

## AuiConfig 和 AuiProvider

`AuiProvider` 为一个子树挂载一个 `AssistantClient`。其 `config` 属性必须使用 `AuiConfig({...})` 构建，从 `@assistant-ui/react` 导入（原始对象字面量是类型错误）。在顶层 `config` 仅创建子树的客户端。在父提供程序下嵌套时，`extends` 是强制性的：`extends={aui}` 扩展父客户端，`extends={null}` 隔离一个新鲜根（开发强制）。`AssistantRuntimeProvider` 内部安装一个 `AuiProvider`，并且额外接受 `config` 以附加额外的范围（如工具包）与运行时自己的范围一起使用；用它代替手动围绕运行时连接 `AuiProvider`。

```tsx
import { AssistantRuntimeProvider, AuiConfig, AuiProvider, Tools, useAui } from "@assistant-ui/react";

// 运行时根：config 附加额外的范围，紧邻运行时自己的范围
const config = AuiConfig({ tools: Tools({ toolkit }) });
<AssistantRuntimeProvider runtime={runtime} config={config}>{children}</AssistantRuntimeProvider>;

// 嵌套范围：扩展父客户端
function MessageScope({ children }: { children: React.ReactNode }) {
  const aui = useAui();
  const nested = AuiConfig({ tools: Tools({ toolkit: extraToolkit }) });
  return <AuiProvider extends={aui} config={nested}>{children}</AuiProvider>;
}

// 隔离根：与任何父客户端分离
const isolated = AuiConfig({});
<AuiProvider extends={null} config={isolated}>{children}</AuiProvider>;
```

配置是纯数据：将其提升到模块作用域，按渲染构建它，或记忆化它，提供程序永远不会依赖配置身份。`AuiProvider` 上的 `ref` 在挂载后接收结果客户端。

## 线程和消息操作

```tsx
const aui = useAui();
const thread = aui.thread;

thread.append({ role: "user", content: [{ type: "text", text: "Hello" }] });
thread.startRun({ parentId: null });
thread.cancelRun();

const state = thread.getState();   // { messages, isRunning, capabilities, composer, ... }

const message = thread.message({ index: 0 });   // 或 { id: messageId }
message.reload();
message.switchToBranch({ position: "next" });
message.submitFeedback({ type: "positive" });

const editComposer = message.composer();
editComposer.beginEdit();
editComposer.setText("Updated");
editComposer.send();
```

## 事件

大多数事件已弃用，因为可以从 `useAuiState` 衍生出相同的转换，这在首次渲染时是正确的，并且以事件处理程序无法的方式重放。

| 事件 | 状态 |
|-------|--------|
| `threads.selectionChanged` | 当前：每次主线程切换时触发一次，带有 `{ threadId, previousThreadId }`。挂载时初始选中的线程不会触发 |
| `thread.modelContextUpdate` | 当前：模型上下文存在于提供程序中，而不是状态中，因此没有状态可派生的等效项 |
| `composer.attachmentAddError` | 当前：`reason` 是 `"no-adapter"` \| `"not-accepted"` \| `"adapter-error"` |
| `composer.send`、`composer.attachmentAdd` | 弃用：观察 `composer.text` / `attachments` |
| `thread.runStart`、`thread.runEnd` | 弃用：观察 `s.thread.isRunning` 切换 |
| `thread.initialize` | 弃用：观察 `s.thread.messages` 变为非空 |
| `threadListItem.switchedTo`、`threadListItem.switchedAway` | 弃用：使用 `threads.selectionChanged`，如果需要，在每项范围内按 ID 过滤 |

已弃用的对仍然会触发并继续工作，直到下一个主版本。`threads.selectionChanged` 也会在旧对未触发的情况下触发，例如 `switchToNewThread()` 和挂载后解析的深度链接初始线程。

## 可选范围

`s.optional.<scope>` 在范围未挂载时解析为 `undefined`，而不是抛出错误，这是从在它内部和外部都渲染的组件中安全读取范围的方法。

```tsx
const partType = useAuiState((s) => s.optional.part?.type);
```

命令式等效方法是 `aui.<scope>.source != null`。

## 功能

```tsx
const capabilities = useAuiState((s) => s.thread.capabilities);
```

`RuntimeCapabilities`（来自 `@assistant-ui/core`）：`switchToBranch`、`switchBranchDuringRun`、`edit`、`reload`、`delete`、`cancel`、`refetchThread`、`unstable_copy`、`speech`、`dictation`、`voice`、`attachments`、`feedback`、`queue`。运行时几乎所有的这些功能都从你提供的（回调、适配器）中派生，而不是显式选项；`unstable_copy` 是 `ExternalStoreRuntime` 通过 `unstable_capabilities` 允许你强制关闭的唯一标志。`refetchThread` 报告 `aui.threads.reloadMainThread()` 是否会刷新打开的线程，还是会回退到重新挂载运行时；参见 [runtime-concepts.md](./references/runtime-concepts.md)。

## 常见陷阱

**"Cannot read property of undefined"**
- 确保钩子在 `AssistantRuntimeProvider`（或其配置提供范围的 `AuiProvider`）内部调用。
- 对于可能未挂载的范围，读取 `s.optional.<scope>` 或在 `aui.<scope>.source != null` 上进行保护。

**来自 `useAuiState` 的无限重新渲染**
- 返回了一个新的对象或数组字面量，包括将范围展开到其中。使用单独的调用选择原始值，或返回一个记忆化引用。

**遗留钩子导入无法解析**
- `useAssistantRuntime`、`useThreadRuntime`、`useThread`、`useMessage`、`useComposer`、`useMessagePart`、`useAttachment`、`useThreadListItem` 和其他朋友在 0.15 中已移除。参见 [state-hooks.md](./references/state-hooks.md) 获取完整映射，或 [更新](../update/SKILL.md) 技能。

**状态未更新**
- 使用 `useAuiState` 的选择器，而不是在渲染中读取 `getState()`；`getState()` 是一次性快照，不是订阅。

**多个线程或对话侧边栏**
- 此技能涵盖单个线程的状态和运行时钩子。要创建、切换、存档和渲染线程列表，请使用 [thread-list](../thread-list/SKILL.md) 技能。

## 相关技能

- [thread-list](../thread-list/SKILL.md) -- 多线程 UI、线程 CRUD、`threads.selectionChanged` 消费者
- [tools](../tools/SKILL.md) -- 工具包编写、工具调用 UI、审批门和人机工具深入
- [elements](../elements/SKILL.md) -- 读取此状态的样式化 `Thread` 和作曲家组件
- [cloud](../cloud/SKILL.md) -- `AssistantCloud`、管理持久性和 `useChatRuntime({ cloud })`
- [streaming](../streaming/SKILL.md) -- `DataStream` 和协议运行时底层的 AssistantTransport 线协议
