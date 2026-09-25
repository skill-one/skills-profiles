# assistant-ui 更新

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

分两步进行升级。首先使 AI SDK 及其 assistant-ui 适配器兼容，然后更新 assistant-ui 并应用其 API 迁移。编辑前请阅读相关参考，因为直接跳转可能会跨越多个弃用窗口。

## 参考

- [./references/ai-sdk.md](./references/ai-sdk.md) -- AI SDK v4 和 v5 到 v6 迁移，v6 到 v7 的变更，以及适配器固定
- [./references/assistant-ui.md](./references/assistant-ui.md) -- assistant-ui 0.8 到 0.15，工具包，LangGraph，以及弃用策略
- [./references/breaking-changes.md](./references/breaking-changes.md) -- 快速版本和症状查询

## 检测已安装的版本

从应用程序根目录运行以下命令。npm ls 报告已安装的依赖关系图，npm view 报告已发布的最新版本。

```bash
npm ls @assistant-ui/react @assistant-ui/ai-sdk @assistant-ui/react-ai-sdk @assistant-ui/core @assistant-ui/store assistant-stream ai @ai-sdk/react

npm view @assistant-ui/react version
npm view @assistant-ui/ai-sdk version
npm view @assistant-ui/react-ai-sdk version
npm view @assistant-ui/core version
npm view @assistant-ui/store version
npm view assistant-stream version
npm view ai version
npm view @ai-sdk/react version
```

截至 2026 年 9 月的当前已发布版本：

| 包 | 当前版本 |
| --- | --- |
| assistant-ui | 0.0.x |
| @assistant-ui/react | 0.15.x |
| @assistant-ui/ai-sdk | 0.0.x |
| @assistant-ui/react-ai-sdk | 1.4.x |
| @assistant-ui/core | 0.3.x |
| @assistant-ui/store | 0.3.x |
| assistant-stream | 0.3.x |
| assistant-cloud | 0.1.x |
| ai | 7.x |

@assistant-ui/react-ai-sdk 为旧版本重新导出相同的 API。新代码从 @assistant-ui/ai-sdk 导入。

## 选择迁移集

将已安装的 @assistant-ui/react 版本与以下每个阈值进行比较。按版本升序应用所有适用的指南。

| 已安装版本 | 检查 |
| --- | --- |
| 0.8.x | 历史上的 UI 包拆分。当前升级包有意排除了 v0-8/ui-package-split，因为其目标与当前运行时不兼容。手动移动到 Elements 注册中心。 |
| 0.9.x | v0-9/edge-package-split 代码修改器。 |
| 0.10.x | 捆绑的迁移没有专门的 0.10 代码修改器。运行后续的代码修改器，并解决项目当前工具链中的剩余包或构建错误。 |
| 0.11.x | ContentPart 名称和 MessagePrimitive.Content 变为 MessagePart 和 MessagePrimitive.Parts。 |
| 0.12.x | 统一状态 API、钩子别名和 camelCase 事件名称。 |
| 0.13.x | 在继续之前请先阅读 0.14 指南，因为它移除了 v0.11 和 v0.12 的弃用。 |
| 0.14.x | 移除了别名和运行时 API，以及原始子元素渲染函数。 |
| 0.15.x | 范围属性、移除遗留钩子、toolUIs、standalone-tool-call、AuiConfig 和 threads.selectionChanged。 |

## 迁移顺序

1. 首先迁移 AI SDK。当项目在 v4、v5 或 v6 上时，请阅读 [ai-sdk.md](./references/ai-sdk.md)。使用 @assistant-ui/ai-sdk 目标 ai@^7 和 @ai-sdk/react@^4。
2. 接下来更新 assistant-ui。使用阈值表和 [assistant-ui.md](./references/assistant-ui.md)，从最旧的适用版本开始。
3. 仅在包和源迁移都完成后进行验证。进行类型检查、构建，并测试应用程序使用的聊天、工具、审批和线程选择路径。

## 运行 CLI

```bash
# 更新所有已安装的 @assistant-ui/* 包。
npx assistant-ui@latest update

# 不安装它们的情况下预览包更改。
npx assistant-ui@latest update --dry

# 预览完整的捆绑迁移并打印每个转换后的文件。
npx assistant-ui@latest upgrade -d -p

# 对源目录应用一个代码修改器。
npx assistant-ui@latest codemod v0-11/content-part-to-message-part ./src

# 报告环境和依赖关系详情。
npx assistant-ui@latest doctor
npx assistant-ui@latest info
```

捆绑的升级命令按以下确切顺序运行这些代码修改器：

1. v0-9/edge-package-split
2. v0-11/content-part-to-message-part
3. v0-12/assistant-api-to-aui
4. v0-12/event-names-to-camelcase
5. v0-12/primitive-if-to-aui-if
6. v0-15/aui-accessor-calls-to-properties

首先使用干运行和打印形式。在审查 diff 后，无 -d 和 -p 运行升级。不要将历史 v0-8/ui-package-split 代码修改器添加到当前升级中。

## 0.15.x 后续操作

这些变更在 0.15.0 之后发布，没有其他重大更新。即使项目已经声明 0.15.x，也要检查这些变更。

### 移动 AI SDK 导入

```tsx
// 之前
import { useChatRuntime } from "@assistant-ui/react-ai-sdk";
```

```tsx
// 之后
import { useChatRuntime } from "@assistant-ui/ai-sdk";
```

### 用配置替换客户端构建

useAui 不需要配置。使用 AuiConfig 构建配置并将其提供给提供者。嵌套的 AuiProvider 必须声明它是否扩展父客户端或是否隔离。

```tsx
// 之前
const aui = useAui({ tools: Tools({ toolkit }) });
return <AuiProvider value={aui}>{children}</AuiProvider>;
```

```tsx
// 之后
const aui = useAui();
const config = AuiConfig({ tools: Tools({ toolkit }) });
return <AuiProvider extends={aui} config={config}>{children}</AuiProvider>;
```

在运行时边界处，用 config 替换 aui。对于隔离的根，使用 AuiProvider extends={null} config={config}。

```tsx
// 之前
return <AssistantRuntimeProvider runtime={runtime} aui={aui}>{children}</AssistantRuntimeProvider>;
```

```tsx
// 之后
const config = AuiConfig({ tools: Tools({ toolkit }) });
return <AssistantRuntimeProvider runtime={runtime} config={config}>{children}</AssistantRuntimeProvider>;
```

### 移动复制的注册组件

与运行时连接的注册组件位于 components/assistant-ui/elements/<name>.aui.tsx，并作为 @/components/assistant-ui/elements/<name>.aui 导入。渲染器和独立元素使用 components/assistant-ui/elements/<name>.tsx，并省略导入中的 .aui。在相同扫掠期间替换退役的 @/components/assistant-ui/<name> 导入。

### 合并线程选择事件

```tsx
// 之前
useAuiEvent("threadListItem.switchedTo", ({ threadId }) => select(threadId));
useAuiEvent("threadListItem.switchedAway", ({ threadId }) => clear(threadId));
```

```tsx
// 之后
useAuiEvent("threads.selectionChanged", ({ threadId, previousThreadId }) => {
  select(threadId);
  if (previousThreadId) clear(previousThreadId);
});
```

新事件由 threads 范围共享。之前位于线程列表项内的监听器可以按其项 ID 进行过滤。

### 替换遗留可交互项和工具注册

useAssistantInteractable、Interactables() 和 useInteractableState 自 2026-06-14 起已弃用，并计划在 2026-09-14 或之后移除。迁移到 unstable_useInteractable、unstable_Interactables() 和 unstable_interactableTool。

makeAssistantTool、useAssistantTool、makeAssistantToolUI 和 useAssistantToolUI 已弃用。将模型合约、执行器和渲染器放入 defineToolkit 条目中，并使用 AuiConfig({ tools: Tools({ toolkit }) }) 注册它。在转换状态或仅 UI 工具之前，请阅读 [assistant-ui.md](./references/assistant-ui.md) 中的工具包部分。

## 验证

```bash
npx tsc --noEmit
npm run build
npm test
```

还请打开一个真实的聊天路由，并验证一个普通消息、一个工具调用、一个审批门（如果存在）、一个线程切换以及项目持久化历史路径。当依赖关系或环境不匹配时，运行 npx assistant-ui@latest doctor 和 npx assistant-ui@latest info。

## 常见问题

**升级命令更改了导入，但应用程序仍然使用旧适配器**

- 包更新仅涵盖 @assistant-ui 包。单独更新 ai 和 @ai-sdk/react，然后遵循 AI SDK 参考。
- @assistant-ui/react-ai-sdk 是旧版本的别名。当前源从 @assistant-ui/ai-sdk 导入。

**AuiProvider 或 AssistantRuntimeProvider 不再接受旧属性**

- useAui() 仅是上下文访问。使用 AuiConfig({...}) 并将其作为 config 传递。
- 嵌套的 AuiProvider 需要 extends={aui}；隔离的则需要 extends={null}。

**范围查找不再像空检查一样行为**

- aui.thread 始终为真。在访问可选范围之前检查 aui.thread.source != null。
- 范围访问器是属性。调用范围方法，而不是范围本身。

**类型检查仍然找到已移除的钩子或工具映射**

- 应用 [assistant-ui.md](./references/assistant-ui.md) 中完整的移除钩子映射。
- 将 s.tools.tools 替换为 s.tools.toolUIs，并将 mcp-app 组键替换为 standalone-tool-call。

## 相关技能

- [setup](../setup/SKILL.md) -- 将 assistant-ui 安装到之前未使用它的项目中
- [runtime](../runtime/SKILL.md) -- 迁移后构建或自定义活动的运行时
- [tools](../tools/SKILL.md) -- 编写工具包、前端工具、审批和工具 UI
- [elements](../elements/SKILL.md) -- 安装和自定义复制的 Elements 注册组件
