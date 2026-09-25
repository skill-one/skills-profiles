# @json-render/devtools

json-render 应用的浮动检查面板。框架无关的核心 + 每个框架的适配器（React、Vue、Svelte、Solid）。

生产环境安全：当 `NODE_ENV === "production"` 时，组件渲染 `null`。

## 安装

安装核心包以及与宿主应用渲染器匹配的适配器。

```bash
# React
npm install @json-render/devtools @json-render/devtools-react

# Vue
npm install @json-render/devtools @json-render/devtools-vue

# Svelte
npm install @json-render/devtools @json-render/devtools-svelte

# Solid
npm install @json-render/devtools @json-render/devtools-solid
```

## 即插即用使用

将 `<JsonRenderDevtools />` 放置在现有的 `<JSONUIProvider>`（或框架等效组件）内的任何位置。无需其他连接。

### React

```tsx
import { JsonRenderDevtools } from "@json-render/devtools-react";

<JSONUIProvider registry={registry} handlers={handlers}>
  <Renderer spec={spec} registry={registry} />
  <JsonRenderDevtools spec={spec} catalog={catalog} messages={messages} />
</JSONUIProvider>;
```

### Vue

```vue
<script setup>
import { JsonRenderDevtools } from "@json-render/devtools-vue";
</script>

<template>
  <JSONUIProvider :registry="registry">
    <Renderer :spec="spec" :registry="registry" />
    <JsonRenderDevtools :spec="spec" :catalog="catalog" :messages="messages" />
  </JSONUIProvider>
</template>
```

### Svelte

```svelte
<script>
  import { JsonRenderDevtools } from "@json-render/devtools-svelte";
</script>

<JSONUIProvider {registry}>
  <Renderer {spec} {registry} />
  <JsonRenderDevtools {spec} {catalog} {messages} />
</JSONUIProvider>
```

### Solid

```tsx
import { JsonRenderDevtools } from "@json-render/devtools-solid";

<JSONUIProvider registry={registry}>
  <Renderer spec={spec()} registry={registry} />
  <JsonRenderDevtools
    spec={spec()}
    catalog={catalog}
    messages={messages()}
  />
</JSONUIProvider>;
```

## 控件

- 浮动切换按钮位于右下角。
- 快捷键：`Ctrl`/`Cmd` + `Shift` + `J`（可通过 `hotkey` 属性配置）。
- 抽屉可调整大小；高度持久化到 localStorage。

## 属性

- `spec` (`Spec | null`) — 当前规范。
- `catalog` (`Catalog | null`) — 目录定义；Catalog 面板需要。
- `messages` (`UIMessage[]`) — AI SDK `useChat` 消息；扫描以查找规范数据部分。
- `initialOpen` (`boolean`) — 默认打开。
- `position` (`"bottom-right" | "bottom-left" | "right"`) — 锚定 + 切换角落。`"bottom-*"` 锚定在底部；`"right"` 锚定在右侧边缘全高（推荐用于已使用 `100vh` 或固定底部条的 app-shell）。
- `hotkey` (`string | false`) — 默认为 `"mod+shift+j"`。
- `bufferSize` (`number`) — 事件环缓冲区上限，默认 500。
- `reserveSpace` (`boolean`, 默认 `true`) — 当为 `true` 时，面板通过在 `body` 上应用 `padding-bottom` / `padding-right` 推动宿主应用。设为 `false` 以将面板作为纯覆盖层。
- `allowDockToggle` (`boolean`, 默认 `true`) — 显示工具栏按钮，使用户可以在底部锚定和右侧锚定之间切换面板。用户选择持久化到 `localStorage` 并覆盖后续挂载时的 `position`。传递 `false` 以锁定锚定到 `position`。
- `onEvent` (`(DevtoolsEvent) => void`) — 可选回调。

## 面板

- **Spec** — 以 `spec.root` 为根的元素树；属性/可见性/事件/监视器详情；集成的 `validateSpec` 警告。
- **State** — 每个JSON Pointer路径可通过 `store.set` 进行内联编辑。
- **Actions** — 分发动作时间线（名称、参数、结果/错误、持续时间）。
- **Stream** — 规范补丁、文本片段、令牌使用、生命周期标记按生成分组。
- **Catalog** — 目录中声明的组件 + 动作，带属性芯片。

## 选择器（工具栏）

元素选择器是面板标题中的工具栏按钮（Chrome-DevTools 风格），不是选项卡。点击它以激活选择模式，然后点击页面中的任何渲染元素 — 选择将跳转到 Spec 选项卡并聚焦于该元素。`Esc` 取消。

## 保留空间 & 锚定

面板可以锚定在底部或右侧边缘，默认情况下用户可以通过工具栏按钮在这两者之间切换（选择持久化到 `localStorage`）。如果宿主应用只适用于一种锚定，请设置 `allowDockToggle={false}` — 按钮隐藏，锚定锁定到 `position`。

选择适合您布局的初始锚定：

- **底部锚定（默认）** — 适用于文档 / 营销 / 内容流网站，以及使用 `height: 100%` 链构建的 app-shell（`html { height: 100% }` → `body { height: 100% }` → `.app { height: 100% }`）。面板将其高度写入 `--jr-devtools-offset-bottom` 并对 `body` 应用匹配的 `padding-bottom`，因此非固定内容会自然腾出空间。
- **右侧锚定** (`position="right"`) — 推荐用于使用 `100vh` 或 `position: fixed; bottom: 0` 的 app-shell 布局。右侧锚定完全绕过底部边缘，并将宽度写入 `--jr-devtools-offset-right`。

使用 `100vh`、`position: fixed` 或 `position: sticky` 的应用可以通过发布的 CSS 自定义属性选择特定元素：

```css
.composer   { bottom: var(--jr-devtools-offset-bottom, 0); }
.sidebar    { right:  var(--jr-devtools-offset-right,  0); }
.app-shell  { height: calc(100vh - var(--jr-devtools-offset-bottom, 0)); }
```

如果自动 body padding 导致特定布局问题，请传递 `reserveSpace={false}` 以使面板成为纯覆盖层 — CSS 自定义属性仍然发布，因此您可以手动保留空间。

(`--jr-devtools-offset` 保留作为向后兼容的别名，用于当前活动的边缘。)

## 页面上的多个渲染器（例如聊天）

单个 `<JsonRenderDevtools />` 可以同时检查多个 `<Renderer />` 实例 — 一个聊天，其中每个助手消息渲染自己的规范，一个由多个独立小部件组成的仪表板等。配方：

1. **一个顶层 `<JSONUIProvider>`** 以确保每个渲染器共享一个状态存储和一个动作分发器。Devtools 生活在其中并通过它看到所有内容。
2. **每个渲染器的规范、共享状态** — 每个助手消息直接渲染 `<Renderer spec={msgSpec} registry={registry} />`，而不是包裹在它自己的 `StateProvider` 中。来自不同消息的状态路径不能冲突。
3. **按回合命名空间状态** — 当源是 AI 流时，向代理传递一个唯一的 `messageId` 并要求每个元素键（`<id>-root`）和状态路径（`/<id>/count`）都以其前缀。
4. **传递 `spec={latest}` + `messages={all}`** — `spec` 驱动 Spec 面板（通常是最新助手消息的规范），而 `messages` 为 Stream 面板提供来自每个回合的补丁。
5. **动作和选择器已经是全局的** — `registerActionObserver` 捕获树中任何 `ActionProvider` 的分发，而 `data-jr-key` 由渲染器本身写入，因此 Pick 可以跨所有渲染元素工作，无论它由哪个消息生成。

有关此方式连接的完整 AI 聊天示例，请参阅 `examples/devtools`。

## 命令式 API（仅限 React）

```tsx
import { useJsonRenderDevtools } from "@json-render/devtools-react";

const devtools = useJsonRenderDevtools();
devtools?.open();
devtools?.toggle();
devtools?.recordEvent({ kind: "stream-text", at: Date.now(), text: "hi" });
```

在生产环境或组件挂载之前返回 `null`。

## 服务器端流捕获

在 API 路由处捕获规范补丁，以便事件持久化到服务器端或流入您自己的遥测。

```ts
import { tapJsonRenderStream, createEventStore } from "@json-render/devtools";
import { pipeJsonRender } from "@json-render/core";

const events = createEventStore({ bufferSize: 1000 });
const tapped = tapJsonRenderStream(result.toUIMessageStream(), events);
writer.merge(pipeJsonRender(tapped));
```

YAML 等价：`tapYamlStream`。

## 底层机制

- **Shadow-DOM 隔离面板** — 面板的样式永远不会泄漏到宿主应用，反之亦然。
- **环缓冲事件存储** — 限制大小的 devtools 事件日志（状态更改、动作分发、流补丁等）。
- **动作观察者注册表** — 每个框架的 `ActionProvider` 通过 `@json-render/core` 中的 `notifyActionDispatch` / `notifyActionSettle` 报告；devtools 通过 `registerActionObserver` 订阅。
- **选择器元素标记** — 当 devtools 挂载时，`ElementRenderer` 将每个渲染元素包裹在 `<span data-jr-key="..." style="display:contents">` 中，以便选择器可以映射 DOM → 规范键。无布局影响。
