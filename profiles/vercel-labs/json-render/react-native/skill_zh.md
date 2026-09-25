# @json-render/react-native

一个将 JSON 规范转换为原生移动组件树的 React Native 渲染器，支持标准组件、数据绑定、可见性、动作和动态属性。

## 快速入门

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react-native/schema";
import {
  standardComponentDefinitions,
  standardActionDefinitions,
} from "@json-render/react-native/catalog";
import { defineRegistry, Renderer, type Components } from "@json-render/react-native";
import { z } from "zod";

// 创建包含标准组件和自定义组件的目录
const catalog = defineCatalog(schema, {
  components: {
    ...standardComponentDefinitions,
    Icon: {
      props: z.object({ name: z.string(), size: z.number().nullable(), color: z.string().nullable() }),
      slots: [],
      description: "图标显示",
    },
  },
  actions: standardActionDefinitions,
});

// 仅注册自定义组件（标准组件是内置的）
const { registry } = defineRegistry(catalog, {
  components: {
    Icon: ({ props }) => <Ionicons name={props.name} size={props.size ?? 24} />,
  } as Components<typeof catalog>,
});

// 渲染
function App({ spec }) {
  return (
    <StateProvider initialState={{}}>
      <VisibilityProvider>
        <ActionProvider handlers={{}}>
          <Renderer spec={spec} registry={registry} />
        </ActionProvider>
      </VisibilityProvider>
    </StateProvider>
  );
}
```

## 标准组件

### 布局
- `Container` - 带有内边距、背景和圆角的包装器
- `Row` - 带有间隙和排列的横向弹性布局
- `Column` - 带有间隙和排列的纵向弹性布局
- `ScrollContainer` - 可滚区域（垂直或水平）
- `SafeArea` - 用于刘海屏/主屏幕指示器的安全区域偏移
- `Pressable` - 在点击时触发动作的可点击包装器
- `Spacer` - 固定或灵活的间距
- `Divider` - 细线分隔符

### 内容
- `Heading` - 标题文本（1-6级）
- `Paragraph` - 正文文本
- `Label` - 小型标签文本
- `Image` - 带有尺寸模式的图像显示
- `Avatar` - 圆形头像图像
- `Badge` - 小型状态徽章
- `Chip` - 分类标签/芯片

### 输入
- `Button` - 带有变体的可点击按钮
- `TextInput` - 文本输入字段
- `Switch` - 开关
- `Checkbox` - 带标签的复选框
- `Slider` - 范围滑块
- `SearchBar` - 搜索输入

### 反馈
- `Spinner` - 加载指示器
- `ProgressBar` - 进度指示器

### 复合组件
- `Card` - 带有可选标题的卡片容器
- `ListItem` - 带有标题、副标题和辅助组件的列表行
- `Modal` - 底部抽屉式模态框

## 可见性条件

在元素上使用 `visible`。语法：`{ "$state": "/path" }`，`{ "$state": "/path", "eq": value }`，`{ "$state": "/path", "not": true }`，`[ cond1, cond2 ]` 用于 AND。

## Pressable + setState 模式

使用 `Pressable` 和内置的 `setState` 动作创建交互式 UI（如标签栏）：

```json
{
  "type": "Pressable",
  "props": {
    "action": "setState",
    "actionParams": { "statePath": "/activeTab", "value": "home" }
  },
  "children": ["home-icon", "home-label"]
}
```

## 动态属性表达式

任何属性值都可以是数据驱动的表达式，在渲染时解析：

- **`{ "$state": "/state/key" }`** - 从状态模型读取（单向读取）
- **`{ "$bindState": "/path" }`** - 双向绑定：用于表单组件的自然值属性（值、选中、按下等）。
- **`{ "$bindItem": "field" }`** - 双向绑定到重复项字段。在重复作用域内使用。
- 嵌套列表使用 `{ "repeat": { "statePath": { "$item": "comments" } } }` 在外围重复作用域内。
- **`{ "$cond": <condition>, "$then": <value>, "$else": <value> }`** - 条件值

```json
{
  "type": "TextInput",
  "props": {
    "value": { "$bindState": "/form/email" },
    "placeholder": "Email"
  }
}
```

组件不使用 `statePath` 属性进行双向绑定。而是在自然值属性上使用 `{ "$bindState": "/path" }`。

## 内置动作

`setState` 动作由 `ActionProvider` 自动处理，直接更新状态模型，重新评估可见性条件和动态属性表达式：

```json
{ "action": "setState", "actionParams": { "statePath": "/activeTab", "value": "home" } }
```

## 提供者

| 提供者 | 目的 |
|----------|---------|
| `StateProvider` | 跨组件共享状态（JSON 指针路径）。接受可选的 `store` 属性用于受控模式。 |
| `ActionProvider` | 处理从组件派发的动作 |
| `VisibilityProvider` | 基于状态启用条件渲染 |
| `ValidationProvider` | 表单字段验证 |

### 外部存储（受控模式）

将 `StateStore` 传递给 `StateProvider`（或 `JSONUIProvider` / `createRenderer`）以使用外部状态管理：

```tsx
import { createStateStore, type StateStore } from "@json-render/react-native";

const store = createStateStore({ count: 0 });

<StateProvider store={store}>{children}</StateProvider>

store.set("/count", 1); // React 自动重新渲染
```

当提供 `store` 时，`initialState` 和 `onStateChange` 将被忽略。

## 关键导出

| 导出 | 目的 |
|--------|---------|
| `defineRegistry` | 从目录创建类型安全的组件注册表 |
| `Renderer` | 使用注册表渲染规范 |
| `schema` | React Native 元素树规范 |
| `standardComponentDefinitions` | 所有标准组件的目录定义 |
| `standardActionDefinitions` | 标准动作的目录定义 |
| `standardComponents` | 预构建的组件实现 |
| `createStandardActionHandlers` | 创建标准动作处理程序 |
| `useStateStore` | 访问状态上下文 |
| `useStateValue` | 从状态获取单个值 |
| `useBoundProp` | 通过 `$bindState`/`$bindItem` 进行双向状态绑定 |
| `useStateBinding` | _(已弃用)_ 通过路径进行遗留双向绑定 |
| `useActions` | 访问动作上下文 |
| `useAction` | 获取单个动作派发函数 |
| `useUIStream` | 从 API 端点流规范 |
| `createStateStore` | 创建框架无关的内存 `StateStore` |
| `StateStore` | 用于插入外部状态管理的接口 |
