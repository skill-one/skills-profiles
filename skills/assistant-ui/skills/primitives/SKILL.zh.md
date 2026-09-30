---
name: primitives
description: 构建和定制 assistant-ui 聊天界面 UI，基于可组合、无样式的 @assistant-ui/react 基础组件：ThreadPrimitive、ComposerPrimitive（包含 Unstable_TriggerPopover 用于提及和斜杠命令）、MessagePrimitive 和 MessagePartPrimitive、ActionBarPrimitive、BranchPickerPrimitive、AttachmentPrimitive、ErrorPrimitive、AssistantModalPrimitive、ChainOfThoughtPrimitive、SelectionToolbarPrimitive、SuggestionPrimitive、QueueItemPrimitive，以及 ThreadList 基础组件。在组装或样式化自定义 Thread、Composer、消息列表、操作栏、分支选择器或建议网格时使用；连接 Composer 输入、语音输入、引用或附件；处理编辑、分支、虚拟化、滚动或思维链 UI。涵盖 MessagePrimitive.Parts 按部分类型渲染函数、groupPartByType、selector 形式的 AuiIf，以及无样式注意事项（AssistantRuntimeProvider、className）。预构建 UI 使用 setup，样式目录使用 elements，多线程侧边栏使用 thread-list。
---

# assistant-ui 基础组件

**始终查阅 [assistant-ui.com/llms.txt](https://www.assistant-ui.com/llms.txt) 获取最新 API。**

基础组件是可组合、无样式的组件，遵循 Radix 风格部分组合：`.Root` 提供上下文，`.PartName` 子组件读取它，并且每个部分都接受 `asChild` 以将行为合并到您自己的元素上而不是渲染包装器。它们不包含样式，对布局也没有任何意见，只有行为：键盘快捷键、自动滚动、流式状态、焦点管理以及禁用逻辑。在使用它们之前，请将您的树包裹在 `AssistantRuntimeProvider`（或嵌套的 `AuiProvider`）中。

## 参考

- [./references/thread.md](./references/thread.md) -- ThreadPrimitive: 视口、自动滚动、转向锚点、消息迭代器
- [./references/composer.md](./references/composer.md) -- ComposerPrimitive: 根、输入、发送、取消、提交行为
- [./references/message.md](./references/message.md) -- MessagePrimitive: 部分管道、工具解析、附件、引用、错误
- [./references/action-bar.md](./references/action-bar.md) -- ActionBarPrimitive 和 ActionBarMorePrimitive 的溢出菜单
- [./references/part-grouping.md](./references/part-grouping.md) -- GroupedParts、按类型分组Part、思维链 UI
- [./references/mentions.md](./references/mentions.md) -- `@` 提及、`/` 切割命令、自定义触发匹配器
- [./references/composer-input.md](./references/composer-input.md) -- 无头输入、输入历史记录、听写、引用、附件
- [./references/messages.md](./references/messages.md) -- 编辑、分支、消息时间、虚拟化、滚动条、图像部分
- [./references/suggestions.md](./references/suggestions.md) -- `Suggestions([...])`、建议适配器、`ThreadPrimitive.Suggestions`

## 导入

```tsx
import {
  AuiIf,
  ThreadPrimitive,
  ComposerPrimitive,
  MessagePrimitive,
  MessagePartPrimitive,
  ActionBarPrimitive,
  ActionBarMorePrimitive,
  BranchPickerPrimitive,
  AttachmentPrimitive,
  ErrorPrimitive,
  AssistantModalPrimitive,
  ChainOfThoughtPrimitive,
  SelectionToolbarPrimitive,
  SuggestionPrimitive,
  QueueItemPrimitive,
  ThreadListPrimitive,
  ThreadListItemPrimitive,
  ThreadListItemMorePrimitive,
} from "@assistant-ui/react";
```

## 基础组件部分

| 基础组件 | 部分 |
|-----------|-------|
| `ThreadPrimitive` | `.Root`, `.Viewport`, `.ViewportProvider`, `.ViewportFooter`, `.Messages`, `.MessageByIndex`, `.Unstable_MessageById`, `.ScrollToBottom`, `.Suggestions`, `.SuggestionByIndex`, `.Suggestion`, `.Empty` (已弃用), `.If` (已弃用) |
| `ComposerPrimitive` | `.Root`, `.Input`, `.Send`, `.Cancel`, `.AddAttachment`, `.Attachments`, `.AttachmentByIndex`, `.AttachmentDropzone`, `.Dictate`, `.StopDictation`, `.DictationTranscript`, `.Quote`, `.QuoteText`, `.QuoteDismiss`, `.Queue`, `.Unstable_TriggerPopoverRoot`, `.Unstable_TriggerPopover` (带 `.Directive` / `.Action`), `.Unstable_TriggerPopoverCategories`, `.Unstable_TriggerPopoverCategoryItem`, `.Unstable_TriggerPopoverItems`, `.Unstable_TriggerPopoverItem`, `.Unstable_TriggerPopoverBack`, `.If` (已弃用) |
| `MessagePrimitive` | `.Root`, `.Parts` (`.Content` 是已弃用的别名), `.PartByIndex`, `.GroupedParts`, `.Unstable_PartsGrouped`, `.Unstable_PartsGroupedByParentId`, `.Attachments`, `.AttachmentByIndex`, `.Quote`, `.Error`, `.GenerativeUI`, `.If` (已弃用) |
| `MessagePartPrimitive` | `.Text`, `.Image`, `.InProgress`, `.Messages` |
| `ActionBarPrimitive` | `.Root`, `.Copy`, `.Reload`, `.Edit`, `.Speak`, `.StopSpeaking`, `.FeedbackPositive`, `.FeedbackNegative`, `.ExportMarkdown` |
| `ActionBarMorePrimitive` | `.Root`, `.Trigger`, `.Content`, `.Item`, `.Separator` |
| `BranchPickerPrimitive` | `.Root`, `.Previous`, `.Next`, `.Number`, `.Count` |
| `AttachmentPrimitive` | `.Root`, `.Name`, `.Remove`, `.unstable_Thumb` |
| `ErrorPrimitive` | `.Root`, `.Message` |
| `AssistantModalPrimitive` | `.Root`, `.Trigger`, `.Content`, `.Anchor` |
| `ChainOfThoughtPrimitive` | `.Root`, `.AccordionTrigger`, `.Parts` (遗留，优先使用 `MessagePrimitive.GroupedParts`) |
| `SelectionToolbarPrimitive` | `.Root`, `.Quote` |
| `SuggestionPrimitive` | `.Title`, `.Description`, `.Trigger` |
| `QueueItemPrimitive` | `.Text`, `.Steer`, `.Remove` |
| `ThreadListPrimitive` | `.Root`, `.New`, `.Items`, `.ItemByIndex`, `.LoadMore` |
| `ThreadListItemPrimitive` | `.Root`, `.Trigger`, `.Title`, `.Archive`, `.Unarchive`, `.Delete` |
| `ThreadListItemMorePrimitive` | `.Root`, `.Trigger`, `.Content`, `.Item`, `.Separator` |

`ThreadListPrimitive`、`ThreadListItemPrimitive` 和 `ThreadListItemMorePrimitive` 驱动多线程侧边栏。本技能仅在上面的表格中涵盖它们；有关完整的自定义 UI、CRUD 操作和远程适配器演练，请参阅 [thread-list](../thread-list/SKILL.md)。

## 使用 AuiIf 进行条件渲染

对于每个新条件，请使用 `AuiIf`。它接受对整个助手状态的选取（`thread`、`message`、`composer`、`part`、`attachment`），而不是一组固定的布尔属性，并取代仍在 `ThreadPrimitive`、`MessagePrimitive` 和 `ComposerPrimitive` 上提供的已弃用的 `.If`。

```tsx
<AuiIf condition={(s) => s.thread.isEmpty}>
  <WelcomeScreen />
</AuiIf>

<AuiIf condition={(s) => s.thread.isRunning}>
  <ComposerPrimitive.Cancel>Stop</ComposerPrimitive.Cancel>
</AuiIf>

<AuiIf
  condition={(s) => s.message.role === "assistant" && s.message.status?.type === "complete"}
>
  <FollowUpCard />
</AuiIf>

<AuiIf condition={(s) => s.composer.dictation != null}>
  <ComposerPrimitive.StopDictation>Stop</ComposerPrimitive.StopDictation>
</AuiIf>
```

`AuiIf.Condition` 用于在 JSX 外部键入条件函数。`s.message` 和 `s.part` 仅在消息或部分上下文中填充；`s.thread` 和 `s.composer` 始终可用。

## 自定义线程示例

使用基础组件构建的完整线程：欢迎建议、按角色消息、内联编辑 Composer、操作栏、分支选择器以及运行中途交换 `Send` 为 `Cancel` 的 Composer 底部。

```tsx
function CustomThread() {
  return (
    <ThreadPrimitive.Root className="flex h-full flex-col">
      <ThreadPrimitive.Viewport className="flex flex-1 flex-col gap-4 overflow-y-auto p-4">
        <AuiIf condition={(s) => s.thread.isEmpty}>
          <div className="flex flex-1 flex-col items-center justify-center gap-3">
            <p>Ask me anything.</p>
            <ThreadPrimitive.Suggestions>
              {() => (
                <SuggestionPrimitive.Trigger send className="rounded-lg border px-3 py-2">
                  <SuggestionPrimitive.Title />
                </SuggestionPrimitive.Trigger>
              )}
            </ThreadPrimitive.Suggestions>
          </div>
        </AuiIf>

        <ThreadPrimitive.Messages>
          {({ message }) => {
            if (message.role === "user") {
              return message.composer.isEditing ? <EditComposer /> : <UserMessage />;
            }
            return <AssistantMessage />;
          }}
        </ThreadPrimitive.Messages>

        <ThreadPrimitive.ViewportFooter className="sticky bottom-0 pt-2">
          <ComposerPrimitive.Root className="flex items-end gap-2 rounded-2xl border bg-background p-2">
            <ComposerPrimitive.Input
              placeholder="Send a message..."
              rows={1}
              className="flex-1 resize-none bg-transparent px-2 py-1.5 focus:outline-none"
            />
            <AuiIf condition={(s) => !s.thread.isRunning}>
              <ComposerPrimitive.Send className="rounded-full bg-primary px-3 py-1.5 text-primary-foreground" />
            </AuiIf>
            <AuiIf condition={(s) => s.thread.isRunning}>
              <ComposerPrimitive.Cancel className="rounded-full border px-3 py-1.5" />
            </AuiIf>
          </ComposerPrimitive.Root>
        </ThreadPrimitive.ViewportFooter>
      </ThreadPrimitive.Viewport>
    </ThreadPrimitive.Root>
  );
}

function UserMessage() {
  return (
    <MessagePrimitive.Root className="flex flex-col items-end gap-1">
      <MessagePrimitive.Quote>
        {({ text }) => <blockquote className="border-l pl-2 text-sm italic">{text}</blockquote>}
      </MessagePrimitive.Quote>
      <div className="max-w-[80%] rounded-2xl bg-primary px-4 py-2 text-primary-foreground">
        <MessagePrimitive.Parts>
          {({ part }) => {
            if (part.type === "text") return <MessagePartPrimitive.Text />;
            if (part.type === "image") return <MessagePartPrimitive.Image className="max-w-full rounded-lg" />;
            return null;
          }}
        </MessagePrimitive.Parts>
      </div>
      <ActionBarPrimitive.Root hideWhenRunning autohide="not-last">
        <ActionBarPrimitive.Edit>Edit</ActionBarPrimitive.Edit>
      </ActionBarPrimitive.Root>
    </MessagePrimitive.Root>
  );
}

function EditComposer() {
  return (
    <MessagePrimitive.Root className="flex justify-end">
      <ComposerPrimitive.Root className="w-[80%] rounded-2xl border p-2">
        <ComposerPrimitive.Input className="w-full resize-none bg-transparent focus:outline-none" />
        <div className="flex justify-end gap-2 pt-1">
          <ComposerPrimitive.Cancel className="rounded-md px-2 py-1 text-sm">Cancel</ComposerPrimitive.Cancel>
          <ComposerPrimitive.Send className="rounded-md bg-primary px-2 py-1 text-sm text-primary-foreground">
            Save
          </ComposerPrimitive.Send>
        </div>
      </ComposerPrimitive.Root>
    </MessagePrimitive.Root>
  );
}

function AssistantMessage() {
  return (
    <MessagePrimitive.Root className="flex flex-col items-start gap-1">
      <div className="max-w-[80%] rounded-2xl bg-muted px-4 py-2">
        <MessagePrimitive.Parts>
          {({ part }) => {
            switch (part.type) {
              case "text":
                return <p className="whitespace-pre-wrap"><MessagePartPrimitive.Text /></p>;
              case "image":
                return <MessagePartPrimitive.Image className="max-w-full rounded-lg" />;
              case "file":
                return (
                  <a href={part.data ?? part.url} download={part.filename} className="text-sm underline">
                    {part.filename ?? part.mimeType}
                  </a>
                );
              case "reasoning":
                return (
                  <details className="text-sm text-muted-foreground">
                    <summary>Thinking</summary>
                    {part.text}
                  </details>
                );
              case "source":
                return part.sourceType === "url" ? (
                  <a href={part.url} className="text-sm underline">{part.title ?? part.url}</a>
                ) : (
                  <span className="text-sm">{part.title}</span>
                );
              case "tool-call":
                return part.toolUI ?? <div className="rounded-md border p-2 text-sm">{part.toolName}</div>;
              case "data":
                return part.dataRendererUI ?? null;
              case "generative-ui":
                return <MessagePrimitive.GenerativeUI />;
              default:
                return null; // 注册的工具和数据 UI 在返回 null 时仍然渲染
            }
          }}
        </MessagePrimitive.Parts>
      </div>
      <MessagePrimitive.Error>
        <ErrorPrimitive.Root className="text-sm text-destructive">
          <ErrorPrimitive.Message />
        </ErrorPrimitive.Root>
      </MessagePrimitive.Error>
      <div className="flex items-center gap-2">
        <BranchPickerPrimitive.Root hideWhenSingleBranch className="flex items-center gap-1 text-xs">
          <BranchPickerPrimitive.Previous>←</BranchPickerPrimitive.Previous>
          <span><BranchPickerPrimitive.Number /> / <BranchPickerPrimitive.Count /></span>
          <BranchPickerPrimitive.Next>→</BranchPickerPrimitive.Next>
        </BranchPickerPrimitive.Root>
        <ActionBarPrimitive.Root hideWhenRunning autohide="not-last">
          <ActionBarPrimitive.Copy>Copy</ActionBarPrimitive.Copy>
          <ActionBarPrimitive.Reload>Regenerate</ActionBarPrimitive.Reload>
        </ActionBarPrimitive.Root>
      </div>
    </MessagePrimitive.Root>
  );
}
```

助手消息的 `.Parts` 回调以上处理了管道可以提供的所有八种部分类型：三种模态部分（`text`、`image`、`file`）、四种提供者通道部分（`reasoning`、`source`、`tool-call`、`generative-ui`）以及开放式的 `data` 部分。从 `default` 案例返回 `null` 仍然允许按名称注册的工具 UI 或按 `name` 注册的数据渲染器自动接管；当您想完全抑制该部分时，请返回 `<></>`。

## 分支选择器

`BranchPickerPrimitive` 从最近的 `MessagePrimitive.Root` 读取分支状态，因此它必须在其中渲染。`Previous` 和 `Next` 在边界处自动禁用（以及在运行中时，除非运行时支持 `switchBranchDuringRun`）；`hideWhenSingleBranch` 在消息实际有替代方案之前移除整个选择器，这可以防止在单分支的常见情况下操作行跳动。

```tsx
<BranchPickerPrimitive.Root hideWhenSingleBranch className="inline-flex items-center gap-1">
  <BranchPickerPrimitive.Previous>←</BranchPickerPrimitive.Previous>
  <span><BranchPickerPrimitive.Number /> / <BranchPickerPrimitive.Count /></span>
  <BranchPickerPrimitive.Next>→</BranchPickerPrimitive.Next>
</BranchPickerPrimitive.Root>
```

当用户消息被编辑并重新发送时，或者当 `ActionBarPrimitive.Reload`（或 `aui.message.reload()`）重新生成助手消息时，会出现新的分支。有关使用 `aui.message.switchToBranch` 的程序分支导航，请参阅 [messages.md](./references/messages.md)。

## 常见问题

**基础组件什么也不渲染，或钩子在提供程序外抛出错误**
- 每个基础组件都从最近的运行时上下文读取。将树包裹在 `AssistantRuntimeProvider runtime={...}`（从运行时钩子如 `useChatRuntime` 或 `useLocalRuntime`）中，或嵌套 `AuiProvider extends={aui} config={AuiConfig({...})}` 以获得隔离范围。
- `ActionBarPrimitive`、`BranchPickerPrimitive` 和 `ErrorPrimitive` 需要一个 `MessagePrimitive.Root` 祖先；`SelectionToolbarPrimitive` 需要一个 `ThreadPrimitive.Root` 祖先，但必须位于 `ThreadPrimitive.Viewport` 之外。

**没有样式**
- 基础组件渲染裸的 DOM 元素（`<div>`、`<button>`、`<textarea>`、...）而没有类。请自行添加 `className`，或将 `asChild` 传递给已具有样式的组件以合并行为。

**`ThreadPrimitive.ViewportSlack` 不再存在**
- 它已从公共 API 中移除。顶部锚点目标注册现在在 `Viewport` 具有 `turnAnchor="top"` 时在 `MessagePrimitive.Root` 内部自动发生；用 `Viewport` 上的 `topAnchorMessageClamp` 替换任何 `fillClampThreshold` / `fillClampOffset` 自定义。

**`MessagePrimitive.Content`、`.Empty` 和每个 `.If` 仍然工作但已过时**
- `.Content` 是 `.Parts` 的已弃用别名。`ThreadPrimitive.Empty` 和每个基础组件的 `.If` 被 `AuiIf` 取代；仅在您尚未迁移的代码中保留它们。

**`groupPartByType({ "mcp-app": [...] })` 静默停止匹配**
- `"mcp-app"` 键在 0.15 中已移除。使用 `"standalone-tool-call"`，这是一个超集，也匹配任何注册 UI 选择 `display: "standalone"` 的工具调用。请参阅 [part-grouping.md](./references/part-grouping.md)。

**以 `Unstable_` 开头的属性、钩子和基础组件**
- Composer 触发器弹出家族、`unstable_useComposerInput`、`unstable_useComposerInputHistory` 和 `unstable_useThreadMessageIds` 是明确不稳定的，并且可以在没有主要版本升级的情况下更改。它们是安全的，但在升级之前请固定您依赖的确切行为。

## 相关技能

- [元素](../elements/SKILL.md) -- 由这些原始组件构建的、可用于复制到您项目中的样式化组件
- [设置](../setup/SKILL.md) -- `create`、`init`、`add` 以及 CLI 框架的其他部分
- [运行时](../runtime/SKILL.md) -- `useAui`、`useAuiState`、`AuiConfig` 以及每个原始组件读取的状态
- [工具](../tools/SKILL.md) -- `MessagePrimitive.Parts` 内解析为 `part.toolUI` 的 `render` 工具集条目
- [线程列表](../thread-list/SKILL.md) -- 深入了解 `ThreadListPrimitive` 和 `ThreadListItemPrimitive`
