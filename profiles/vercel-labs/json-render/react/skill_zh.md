# @json-render/react

一个将 JSON 规范转换为 React 组件树的 React 渲染器。

## 快速入门

```typescript
import { defineRegistry, Renderer } from "@json-render/react";
import { catalog } from "./catalog";

const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) => <div>{props.title}{children}</div>,
  },
});

function App({ spec }) {
  return <Renderer spec={spec} registry={registry} />;
}
```

## 创建目录

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { defineRegistry } from "@json-render/react";
import { z } from "zod";

// 使用属性模式创建目录
export const catalog = defineCatalog(schema, {
  components: {
    Button: {
      props: z.object({
        label: z.string(),
        variant: z.enum(["primary", "secondary"]).nullable(),
      }),
      description: "可点击的按钮",
    },
    Card: {
      props: z.object({ title: z.string() }),
      slots: ["default"],
      description: "带标题的卡片容器",
    },
    Layout: {
      props: z.object({}),
      slots: ["default", "header", "footer"],
      description: "带命名内容区域的布局",
    },
  },
});

// 使用类型安全的属性定义组件实现
const { registry } = defineRegistry(catalog, {
  components: {
    Button: ({ props }) => (
      <button className={props.variant}>{props.label}</button>
    ),
    Card: ({ props, children }) => (
      <div className="card">
        <h2>{props.title}</h2>
        {children}
      </div>
    ),
    Layout: ({ children, slots }) => (
      <div>
        <header>{slots?.header}</header>
        <main>{children}</main>
        <footer>{slots?.footer}</footer>
      </div>
    ),
  },
});
```

## 规范结构（元素树）

React 模式使用元素树格式：

```json
{
  "root": {
    "type": "Card",
    "props": { "title": "Hello" },
    "children": [{ "type": "Button", "props": { "label": "Click me" } }]
  }
}
```

## 命名插槽

使用 `children` 表示 `"default"` 插槽。使用元素顶层的 `slots` 对象表示目录声明的其他插槽名称：

```json
{
  "type": "Layout",
  "props": {},
  "children": ["main"],
  "slots": {
    "header": ["heading"],
    "footer": ["actions"]
  }
}
```

Registry 组件接收命名内容为 `slots?.header`、`slots?.footer` 等。不要使用 `slots.default`。

## 可见性条件

在元素上使用 `visible` 来根据状态显示/隐藏。新语法：`{ "$state": "/path" }`、`{ "$state": "/path", "eq": value }`、`{ "$state": "/path", "not": true }`、`{ "$and": [cond1, cond2] }` 用于 AND，`{ "$or": [cond1, cond2] }` 用于 OR。辅助函数：`visibility.when("/path")`、`visibility.unless("/path")`、`visibility.eq("/path", val)`、`visibility.and(cond1, cond2)`、`visibility.or(cond1, cond2)`。

## 提供者

| 提供者             | 目的                                                                                                      |
| -------------------- | -------------------------------------------------------------------------------------------------------- |
| `StateProvider`      | 跨组件共享状态（JSON Pointer 路径）。接受可选的 `store` 属性用于受控模式。                               |
| `ActionProvider`     | 处理通过事件系统派发的动作                                                                                   |
| `VisibilityProvider` | 基于状态启用条件渲染                                                                                       |
| `ValidationProvider` | 表单字段验证                                                                                              |

### 外部存储（受控模式）

将 `StateStore` 传递给 `StateProvider`（或 `JSONUIProvider` / `createRenderer`）以使用外部状态管理（Redux、Zustand、XState 等）：

```tsx
import { createStateStore, type StateStore } from "@json-render/react";

const store = createStateStore({ count: 0 });

<StateProvider store={store}>{children}</StateProvider>;

// 从任何地方修改——React 自动重新渲染：
store.set("/count", 1);
```

当 `store` 提供时，`initialState` 和 `onStateChange` 将被忽略。

## 动态属性表达式

任何属性值都可以是渲染器在组件接收属性之前解析的数据驱动表达式：

- **`{ "$state": "/state/key" }`** - 从状态模型读取（单向读取）
- **`{ "$bindState": "/path" }`** - 双向绑定：从状态读取并启用写回。用于表单组件的自然值属性（value、checked、pressed 等）。
- **`{ "$bindItem": "field" }`** - 双向绑定到重复项字段。在重复作用域内使用。
- **过滤列表**：`repeat` 加上同一容器上的 `$item` 可见条件仅渲染匹配项：`{ "repeat": { "statePath": "/tasks", "key": "id" }, "visible": { "$item": "status", "eq": "todo" }, "children": ["task-card"] }`。AND 组合的 `$state` 联结门控容器外壳；`$item`/`$index` 联结过滤项。
- **嵌套列表**：在重复内使用 `{ "repeat": { "statePath": { "$item": "comments" }, "key": "id" } }` 以迭代外围项的数组。
- **`{ "$cond": <condition>, "$then": <value>, "$else": <value> }`** - 条件值
- **`{ "$template": "Hello, ${/name}!" }`** - 将状态值插入字符串
- **`{ "$computed": "fn", "args": { ... } }`** - 调用注册的函数并传递解析的参数

```json
{
  "type": "Input",
  "props": {
    "value": { "$bindState": "/form/email" },
    "placeholder": "Email"
  }
}
```

组件不使用 `statePath` 属性进行双向绑定。在自然值属性上使用 `{ "$bindState": "/path" }` 代替。

组件接收已解析的属性。对于双向绑定的属性，使用渲染器提供的 `bindings` 映射和 `useBoundProp` 钩子。

通过 `JSONUIProvider` 或 `createRenderer` 上的 `functions` 属性注册 `$computed` 函数：

```tsx
<JSONUIProvider
  functions={{ fullName: (args) => `${args.first} ${args.last}` }}
>
```

## 事件系统

组件使用 `emit` 发射命名事件，或使用 `on()` 获取带元数据的事件句柄。元素的 `on` 字段将事件映射到动作绑定：

```tsx
// 简单事件发射
Button: ({ props, emit }) => (
  <button onClick={() => emit("press")}>{props.label}</button>
),

// 带元数据的事件句柄（例如 preventDefault）
Link: ({ props, on }) => {
  const click = on("click");
  return (
    <a href={props.href} onClick={(e) => {
      if (click.shouldPreventDefault) e.preventDefault();
      click.emit();
    }}>{props.label}</a>
  );
},
```

```json
{
  "type": "Button",
  "props": { "label": "Submit" },
  "on": { "press": { "action": "submit" } }
}
```

`on()` 返回的 `EventHandle` 包含：`emit()`、`shouldPreventDefault`（布尔值）和 `bound`（布尔值）。

## 状态监视器

元素可以声明一个 `watch` 字段（顶级、类型/属性/子元素的兄弟）以在状态值变化时触发动作：

```json
{
  "type": "Select",
  "props": {
    "value": { "$bindState": "/form/country" },
    "options": ["US", "Canada"]
  },
  "watch": { "/form/country": { "action": "loadCities" } },
  "children": []
}
```

## 内置动作

`setState`、`pushState`、`removeState` 和 `validateForm` 动作是 React 模式的一部分，并由 `ActionProvider` 自动处理。它们被注入 AI 提示中，无需在目录 `actions` 中声明：

```json
{ "action": "setState", "params": { "statePath": "/activeTab", "value": "home" } }
{ "action": "pushState", "params": { "statePath": "/items", "value": { "text": "New" } } }
{ "action": "removeState", "params": { "statePath": "/items", "index": 0 } }
{ "action": "validateForm", "params": { "statePath": "/formResult" } }
```

`validateForm` 验证所有注册字段并将 `{ valid, errors }` 写入状态。

注意：动作参数中的 `statePath`（例如 `setState.statePath`）指向突变路径。组件属性中的双向绑定使用 `{ "$bindState": "/path" }` 而不是 `statePath`。

## useBoundProp

对于需要双向绑定的表单组件，使用 `useBoundProp` 和渲染器提供的 `bindings` 映射：

```tsx
import { useBoundProp } from "@json-render/react";

Input: ({ element, bindings }) => {
  const [value, setValue] = useBoundProp<string>(
    element.props.value,
    bindings?.value
  );
  return (
    <input
      value={value ?? ""}
      onChange={(e) => setValue(e.target.value)}
    />
  );
},
```

`useBoundProp(propValue, bindingPath)` 返回 `[value, setValue]`。`value` 是解析的属性值；`setValue` 写回绑定状态路径（如果未绑定则为空操作）。

## BaseComponentProps

对于构建不依赖于特定目录的可重用组件库（例如 `@json-render/shadcn`）：

```typescript
import type { BaseComponentProps } from "@json-render/react";

const Card = ({ props, children }: BaseComponentProps<{ title?: string }>) => (
  <div>{props.title}{children}</div>
);
```

## defineRegistry

`defineRegistry` 仅在目录声明动作时才条件性地要求 `actions` 字段。具有 `actions: {}` 的目录可以省略它。

## 主要导出

| 导出                  | 目的                                                                                                    |
| ----------------------- | ------------------------------------------------------------------------------------------------------ |
| `defineRegistry`        | 从目录创建类型安全的组件注册表                                                                      |
| `Renderer`              | 使用注册表渲染规范                                                                                      |
| `schema`                | 元素树模式（包括内置状态动作：setState、pushState、removeState、validateForm）                         |
| `useStateStore`         | 访问状态上下文                                                                                          |
| `useStateValue`         | 从状态获取单个值                                                                                       |
| `useBoundProp`          | `$bindState`/`$bindItem` 表达式的双向绑定                                                              |
| `useActions`            | 访问动作上下文                                                                                        |
| `useAction`             | 获取单个动作派发函数                                                                                  |
| `useOptionalValidation` | useValidation 的非抛出变体（如果没有提供则返回 null）                                                     |
| `useUIStream`           | 从 API 端点流规范                                                                                      |
| `createStateStore`      | 创建框架无关的内存 `StateStore`                                                                      |
| `StateStore`            | 用于插入外部状态管理的接口                                                                            |
| `BaseComponentProps`    | 目录无关的可重用组件库基础类型                                                                      |
| `EventHandle`           | 事件句柄类型（`emit`、`shouldPreventDefault`、`bound`）                                                 |
| `ComponentContext`      | 类型化的组件上下文（目录感知）                                                                        |
