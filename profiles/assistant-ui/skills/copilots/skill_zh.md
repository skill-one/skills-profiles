# assistant-ui Copilots

**请始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

Copilots 将助手与您的运行应用相结合：通过指令引导它，向其提供惰性应用状态，让它读取并驱动渲染的组件，通过可交互元素实现双向状态，并在 iframe 边界之间共享模型上下文。

## 参考

- [./references/instructions.md](./references/instructions.md) -- useAssistantInstructions
- [./references/model-context.md](./references/model-context.md) -- useAssistantContext, imperative modelContext().register, ModelContextRegistry
- [./references/visible.md](./references/visible.md) -- makeAssistantVisible
- [./references/interactables.md](./references/interactables.md) -- 应用范围和线程范围的可交互元素、版本、持久化、部分更新
- [./references/assistant-frame.md](./references/assistant-frame.md) -- AssistantFrameProvider 和 useAssistantFrameHost

## 指南

所有 API 都来自 `@assistant-ui/react` 并在 `AssistantRuntimeProvider` 内部运行。为任务选择最小的工具：

```
您需要助手知道或做什么？
├─ 使用系统提示引导行为 → useAssistantInstructions("...")
├─ 提供只读应用状态（页面、选择、购物车）→ useAssistantContext({ getContext })
├─ 让它读取/点击/编辑渲染的组件 → makeAssistantVisible(Component, { clickable, editable })
├─ 通过工具读取和写入持久化组件状态
│    ├─ 由您挂载，应用内任何位置 → unstable_useInteractable(name, config)
│    └─ 由模型创建，线程内内联 → defineToolkit 内的 unstable_interactableTool(config)
├─ 命令式地一起注册指令+工具 → aui.modelContext.register({ getModelContext })
└─ 从嵌入的 iframe 与父窗口共享工具/指令 → AssistantFrameProvider + useAssistantFrameHost
```

指令和上下文是轻量级的起点。当助手需要感知或驱动现有 DOM 时，使用 `makeAssistantVisible`；当它需要结构化的双向状态并通过自动生成的 `update_{name}` 工具进行修改时，使用可交互元素。

可交互元素有两代。当前一代是 `unstable_` 系列 (`unstable_Interactables()`, `unstable_useInteractable`, `unstable_interactableTool`)；前缀表示其可能变更，而非不受支持。遗留系列 (`Interactables()`, `useAssistantInteractable`, `useInteractableState`) 自 2026-06-14 起已弃用，并计划在 2026-09-14 或之后移除。这两个范围是互斥的：在单个 `AuiConfig` 中挂载仅一个可交互元素 API。

```tsx
import { useAssistantInstructions, useAssistantContext } from "@assistant-ui/react";

function CheckoutCopilot() {
  useAssistantInstructions("您帮助用户完成结账。请简洁。");
  useAssistantContext({ getContext: () => `当前页面: ${window.location.href}` });
  return null;
}
```

`getContext` 每次读取模型上下文时都会重新评估，因此它始终反映当前状态。当指令和工具需要从同一提供程序发送时，命令式注册：

```tsx
import { useAui } from "@assistant-ui/react";
import { useEffect } from "react";

function SearchCopilot() {
  const aui = useAui();
  useEffect(() => {
    return aui.modelContext.register({
      getModelContext: () => ({
        system: "您是一个有帮助的搜索助手。",
        tools: { search: mySearchTool },
      }),
    });
  }, [aui]);
  return null;
}
```

`register` 返回一个取消订阅函数；将其从 `useEffect` 返回会在卸载时清理提供程序。多个提供程序可以组合：`system` 字符串会连接，`tools` 映射会合并。

## 可交互元素范围

通过 `config` 一次性挂载范围。应用范围和线程范围的可交互元素都需要它；线程范围的还需要注册其工具包。

```tsx
import { AuiConfig, AssistantRuntimeProvider, unstable_Interactables } from "@assistant-ui/react";
import { useChatRuntime } from "@assistant-ui/ai-sdk";

function Providers({ children }: { children: React.ReactNode }) {
  const runtime = useChatRuntime();
  const config = AuiConfig({ unstable_interactables: unstable_Interactables() });

  return (
    <AssistantRuntimeProvider runtime={runtime} config={config}>
      {children}
    </AssistantRuntimeProvider>
  );
}
```

然后 `unstable_useInteractable(name, config)` 会注册一个实例并返回 `[state, { id, setState, isPending, error, flush }]`；框架会根据您 `stateSchema` 的部分版本生成 `update_{name}` 工具。有关线程范围形式、版本、持久化和部分更新如何合并，请参阅 [interactables.md](./references/interactables.md)。

## 常见问题

**助手忽略指令或上下文**
- 钩子或 `register` 调用必须在 `AssistantRuntimeProvider` 内部运行。
- 对于 `aui.modelContext.register`，在 `useEffect` 中调用并返回结果以取消订阅；在渲染中注册会导致提供程序泄漏。

**上下文过时**
- 使用 `getContext` 回调形式，而不是捕获的值。它在发送时重新读取，因此闭包在新鲜状态上工作；预计算的字符串不会更新。

**makeAssistantVisible 无效**
- 没有选项时组件是只读的（暴露其 `outerHTML`）。传递 `{ clickable: true }` 以允许点击，传递 `{ editable: true }` 以编辑 `<input>` / `<textarea>`。嵌套的可见组件仅暴露最外层。

**可交互元素在每次渲染时重置其状态**
- 在组件外部定义 `stateSchema` 和 `initialState`（或将其记忆化）。每次渲染都使用新的模式标识会重新注册可交互元素并清除其状态。

**同时注册了两个可交互元素范围**
- `unstable_Interactables()` 和遗留的 `Interactables()` 是互斥的。在 `AuiConfig` 中保持一个；新代码使用 `unstable_Interactables()`。

**部分更新未按预期生效**
- 普通字段浅合并：模型只发送已更改的内容，并发送的嵌套对象会替换该字段，而不是深度合并到其中。
- 具有唯一 `id` 的数组字段会使用操作（`add` / `update` / `remove` / `clear`），而不是替换数组。

**框架主机从未接收到工具或指令**
- 双方都会验证消息来源。iframe 的 `AssistantFrameProvider.addModelContextProvider(registry, targetOrigin)` 和父窗口的 `useAssistantFrameHost({ targetOrigin })` 必须为跨域嵌入指定相同的显式来源；任何一方省略 `targetOrigin` 都会默认为该窗口自己的来源。

## 相关技能

- [tools](../tools/SKILL.md) -- 工具包 (`defineToolkit`)、后端和前端工具定义，以及自定义工具调用 UI。
- [runtime](../runtime/SKILL.md) -- 运行时创建、`AssistantRuntimeProvider`，以及读取或修改线程状态 (`useAui`, `useAuiState`, `useAuiEvent`)。
