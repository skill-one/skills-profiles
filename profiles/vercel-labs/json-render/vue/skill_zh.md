# @json-render/vue

Vue 3 渲染器，将 JSON 规范转换为具有数据绑定、可见性和操作的 Vue 组件树。

## 安装

```bash
npm install @json-render/vue @json-render/core zod
```

依赖项：`vue ^3.5.0` 和 `zod ^4.0.0`。

## 快速入门

### 创建目录

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/vue/schema";
import { z } from "zod";

export const catalog = defineCatalog(schema, {
  components: {
    Card: {
      props: z.object({ title: z.string(), description: z.string().nullable() }),
      slots: ["default"],
      description: "卡片容器",
    },
    Layout: {
      props: z.object({}),
      slots: ["default", "header", "footer"],
      description: "具有命名内容区域的布局",
    },
    Button: {
      props: z.object({ label: z.string(), action: z.string() }),
      description: "可点击的按钮",
    },
  },
  actions: {},
});
```

### 使用 h() 渲染函数定义注册表

```typescript
import { h } from "vue";
import { defineRegistry } from "@json-render/vue";
import { catalog } from "./catalog";

export const { registry } = defineRegistry(catalog, {
  components: {
    Card: ({ props, children }) =>
      h("div", { class: "card" }, [
        h("h3", null, props.title),
        props.description ? h("p", null, props.description) : null,
        children,
      ]),
    Layout: ({ slots }) =>
      h("div", null, [
        h("header", null, slots.header?.()),
        h("main", null, slots.default?.()),
        h("footer", null, slots.footer?.()),
      ]),
    Button: ({ props, emit }) =>
      h("button", { onClick: () => emit("press") }, props.label),
  },
});
```

## 命名插槽

使用 `children` 表示 `"default"` 插槽。使用目录声明的其他插槽名称的元素顶层 `slots` 对象：

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

注册表组件接收 Vue 原生的插槽函数。使用 `slots.header?.()`、`slots.footer?.()` 等进行渲染。`slots.default?.()` 渲染规范的 `children`；`children` 上下文字段是那个渲染结果的便利别名。在 JSON 规范中，将默认内容保留在 `children` 中，而不是向 `slots` 添加 `default` 条目。

### 渲染规范

```vue
<script setup lang="ts">
import { StateProvider, ActionProvider, Renderer } from "@json-render/vue";
import { registry } from "./registry";

const spec = { root: "card-1", elements: { /* ... */ } };
</script>

<template>
  <StateProvider :initial-state="{ form: { name: '' } }">
    <ActionProvider :handlers="{ submit: handleSubmit }">
      <Renderer :spec="spec" :registry="registry" />
    </ActionProvider>
  </StateProvider>
</template>
```

## 提供者

| 提供者 | 目的 |
|----------|---------|
| `StateProvider` | 跨组件共享状态（JSON 指针路径）。接受 `initialState` 或 `store` 以进行受控模式。 |
| `ActionProvider` | 处理通过事件系统派发的操作 |
| `VisibilityProvider` | 基于状态启用条件渲染 |
| `ValidationProvider` | 表单字段验证 |

## 组合式 API

| 组合式 API | 目的 |
|------------|---------|
| `useStateStore()` | 访问状态上下文（`state` 作为 `ShallowRef`，`get`，`set`，`update`） |
| `useStateValue(path)` | 从状态获取单个值 |
| `useIsVisible(condition)` | 检查是否满足可见性条件 |
| `useActions()` | 访问操作上下文 |
| `useAction(binding)` | 获取单个操作派发函数 |
| `useFieldValidation(path, config)` | 字段验证状态 |
| `useBoundProp(propValue, bindingPath)` | `$bindState`/`$bindItem` 的双向绑定 |

注意：`useStateStore().state` 返回 `ShallowRef<StateModel>` — 使用 `state.value` 访问。

## 外部存储（StateStore）

嵌套列表可以在包含的重复中设置 `repeat.statePath` 为 `{ "$item": "field" }`。

将 `StateStore` 传递给 `StateProvider` 以将 json-render 连接到 Pinia、VueUse 或任何状态管理：

```typescript
import { createStateStore, type StateStore } from "@json-render/vue";

const store = createStateStore({ count: 0 });
```

```vue
<StateProvider :store="store">
  <Renderer :spec="spec" :registry="registry" />
</StateProvider>
```

## 动态属性表达式

属性支持 `$state`、`$bindState`、`$cond`、`$template`、`$computed`。在自然值属性上使用 `{ "$bindState": "/path" }` 以进行双向绑定。

## 可见性条件

```typescript
{ "$state": "/user/isAdmin" }
{ "$state": "/status", "eq": "active" }
{ "$state": "/maintenance", "not": true }
[ cond1, cond2 ]  // 隐式 AND
```

## 内置操作

`setState`、`pushState`、`removeState` 和 `validateForm` 已集成到 Vue 规范中并由 `ActionProvider` 处理：

```json
{
  "action": "setState",
  "params": { "statePath": "/activeTab", "value": "settings" }
}
```

## 事件系统

组件使用 `emit(event)` 触发事件，或使用 `on(event)` 处理元数据（`shouldPreventDefault`，`bound`）。

## 流式传输

`useUIStream` 和 `useChatUI` 返回用于从 API 流式传输规范的 Vue Refs。

## BaseComponentProps

用于目录无关的可重用组件：

```typescript
import type { BaseComponentProps } from "@json-render/vue";

const Card = ({ props, children }: BaseComponentProps<{ title?: string }>) =>
  h("div", null, [props.title, children]);
```

## 主要导出

| 导出 | 目的 |
|--------|---------|
| `defineRegistry` | 从目录创建类型安全的组件注册表 |
| `Renderer` | 使用注册表渲染规范 |
| `schema` | 元素树规范（来自 `@json-render/vue/schema`） |
| `StateProvider`、`ActionProvider`、`VisibilityProvider`、`ValidationProvider` | 上下文提供者 |
| `useStateStore`、`useStateValue`、`useBoundProp` | 状态组合式 API |
| `useActions`、`useAction` | 操作组合式 API |
| `useFieldValidation`、`useIsVisible` | 验证和可见性 |
| `useUIStream`、`useChatUI` | 流式传输组合式 API |
| `createStateStore` | 创建内存中的 `StateStore` |
| `BaseComponentProps` | 目录无关的组件属性类型 |
