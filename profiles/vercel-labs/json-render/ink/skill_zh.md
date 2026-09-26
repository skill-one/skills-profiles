# @json-render/ink

Ink 终端渲染器，将 JSON 规范转换为具有标准组件、数据绑定、可见性、操作和动态属性的交互式终端组件树。

## 快速入门

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/ink/schema";
import {
  standardComponentDefinitions,
  standardActionDefinitions,
} from "@json-render/ink/catalog";
import { defineRegistry, Renderer, type Components } from "@json-render/ink";
import { z } from "zod";

// 创建包含标准组件和自定义组件的目录
const catalog = defineCatalog(schema, {
  components: {
    ...standardComponentDefinitions,
    CustomWidget: {
      props: z.object({ title: z.string() }),
      slots: [],
      description: "自定义组件",
    },
  },
  actions: standardActionDefinitions,
});

// 仅注册自定义组件（标准组件是内置的）
const { registry } = defineRegistry(catalog, {
  components: {
    CustomWidget: ({ props }) => <Text>{props.title}</Text>,
  } as Components<typeof catalog>,
});

// 渲染
function App({ spec }) {
  return (
    <JSONUIProvider initialState={{}}>
      <Renderer spec={spec} registry={registry} />
    </JSONUIProvider>
  );
}
```

## 规范结构（扁平元素映射）

Ink schema 使用具有根键的扁平元素映射：

```json
{
  "root": "main",
  "elements": {
    "main": {
      "type": "Box",
      "props": { "flexDirection": "column", "padding": 1 },
      "children": ["heading", "content"]
    },
    "heading": {
      "type": "Heading",
      "props": { "text": "Dashboard", "level": "h1" },
      "children": []
    },
    "content": {
      "type": "Text",
      "props": { "text": "Hello from the terminal!" },
      "children": []
    }
  }
}
```

## 标准组件

### 布局
- `Box` - Flexbox 布局容器（类似于终端 `<div>`）。用于分组、间距、边框、对齐。默认的 flexDirection 是 row。
- `Text` - 带可选样式的文本输出（颜色、粗体、斜体等）。
- `Newline` - 插入空行。必须位于 flexDirection 为 column 的 Box 内。
- `Spacer` - 沿主轴扩展的灵活空白空间。

### 内容
- `Heading` - 区分标题（h1：粗体+下划线，h2：粗体，h3：粗体+淡化，h4：淡化）
- `Divider` - 带可选居中标题的水平分隔符
- `Badge` - 带颜色的内联标签（变体：默认、信息、成功、警告、错误）
- `Spinner` - 带可选标签的动画加载器
- `ProgressBar` - 水平进度条（0-1）
- `Sparkline` - 使用 Unicode 块字符的行内图表
- `BarChart` - 带标签和值的水平条形图
- `Table` - 带标题和行的表格数据
- `List` - 项目符号或编号列表
- `ListItem` - 带标题、副标题、前导/尾随文本的结构化列表行
- `Card` - 带可选标题的带边框容器
- `KeyValue` - 键值对显示
- `Link` - 可点击的 URL（带可选标签）
- `StatusLine` - 带彩色图标的彩色状态消息（信息、成功、警告、错误）
- `Markdown` - 带终端样式的 markdown 文本渲染

### 交互
- `TextInput` - 文本输入字段（事件：提交、改变）
- `Select` - 带箭头键导航的选择菜单（事件：改变）
- `MultiSelect` - 带空格切换的多选（事件：改变、提交）
- `ConfirmInput` - 是/否确认提示（事件：确认、拒绝）
- `Tabs` - 带左右箭头键的选项卡导航（事件：改变）

## 可见性条件

在元素上使用 `visible` 以根据状态显示/隐藏。语法：`{ "$state": "/path" }`，`{ "$state": "/path", "eq": value }`，`{ "$state": "/path", "not": true }`，`{ "$and": [cond1, cond2] }` 用于 AND，`{ "$or": [cond1, cond2] }` 用于 OR。

## 动态属性表达式

任何属性值都可以是数据驱动的表达式，在渲染时解析：

- **`{ "$state": "/state/key" }`** - 从状态模型读取（单向读取）
- **`{ "$bindState": "/path" }`** - 双向绑定：用于表单组件的自然值属性
- **`{ "$bindItem": "field" }`** - 双向绑定到重复项字段
- **`{ "$cond": <condition>, "$then": <value>, "$else": <value> }`** - 条件值
- **`{ "$template": "Hello, ${/name}!" }`** - 将状态值插入字符串

组件不使用 `statePath` 属性进行双向绑定。而是在自然值属性上使用 `{ "$bindState": "/path" }`。

## 事件系统

组件使用 `emit` 发射命名事件。元素的 `on` 字段将事件映射到操作绑定：

```tsx
CustomButton: ({ props, emit }) => (
  <Box>
    <Text>{props.label}</Text>
    {/* emit("press") 触发 spec 中绑定的 on.press 操作 */}
  </Box>
),
```

```json
{
  "type": "CustomButton",
  "props": { "label": "Submit" },
  "on": { "press": { "action": "submit" } },
  "children": []
}
```

## 内置操作

`setState`、`pushState` 和 `removeState` 是内置的，自动处理：

```json
{ "action": "setState", "params": { "statePath": "/activeTab", "value": "home" } }
{ "action": "pushState", "params": { "statePath": "/items", "value": { "text": "New" } } }
{ "action": "removeState", "params": { "statePath": "/items", "index": 0 } }
```

## 重复（动态列表）

在容器元素上使用 `repeat` 字段从状态数组渲染项：

```json
{
  "type": "Box",
  "props": { "flexDirection": "column" },
  "repeat": { "statePath": "/items", "key": "id" },
  "children": ["item-row"]
}
```

在重复的子元素中，使用 `{ "$item": "field" }` 从当前项读取，使用 `{ "$index": true }` 获取当前索引。

对于嵌套列表，内部重复可以使用 `{ "statePath": { "$item": "children" } }` 来迭代包含项的数组。

## 流式传输

使用 `useUIStream` 从 JSONL 补丁流逐步渲染规范：

```tsx
import { useUIStream } from "@json-render/ink";

const { spec, send, isStreaming } = useUIStream({ api: "/api/generate" });
```

## 服务器端提示生成

使用 `./server` 导出从您的目录生成 AI 系统提示：

```typescript
import { catalog } from "./catalog";

const systemPrompt = catalog.prompt({ system: "You are a terminal assistant." });
```

## 提供者

| 提供者 | 目的 |
|----------|---------|
| `StateProvider` | 跨组件共享状态（JSON 指针路径）。接受可选的 `store` 属性用于受控模式。 |
| `ActionProvider` | 处理通过事件系统派发的事件 |
| `VisibilityProvider` | 基于状态启用条件渲染 |
| `ValidationProvider` | 表单字段验证 |
| `FocusProvider` | 管理交互组件的焦点 |
| `JSONUIProvider` | 所有上下文的组合提供者 |

### 外部存储（受控模式）

将 `StateStore` 传递给 `StateProvider`（或 `JSONUIProvider`）以使用外部状态管理：

```tsx
import { createStateStore, type StateStore } from "@json-render/ink";

const store = createStateStore({ count: 0 });

<StateProvider store={store}>{children}</StateProvider>

store.set("/count", 1); // React 自动重新渲染
```

当 `store` 提供时，`initialState` 和 `onStateChange` 被忽略。

## createRenderer（高级 API）

```tsx
import { createRenderer } from "@json-render/ink";
import { standardComponents } from "@json-render/ink";
import { catalog } from "./catalog";

const InkRenderer = createRenderer(catalog, {
  ...standardComponents,
  // 自定义组件覆盖
});

// InkRenderer 包含所有提供者（状态、可见性、操作、焦点）
render(
  <InkRenderer spec={spec} state={{ activeTab: "overview" }} />
);
```

## 关键导出

| 导出 | 目的 |
|--------|---------|
| `defineRegistry` | 从目录创建类型安全的组件注册表 |
| `Renderer` | 使用注册表渲染规范 |
| `createRenderer` | 高级：创建带内置提供者的组件 |
| `JSONUIProvider` | 所有上下文的组合提供者 |
| `schema` | Ink 扁平元素映射 schema（包含内置状态操作） |
| `standardComponentDefinitions` | 标准组件的所有标准组件的目录定义 |
| `standardActionDefinitions` | 标准操作的目录定义 |
| `standardComponents` | 预构建的组件实现 |
| `useStateStore` | 访问状态上下文 |
| `useStateValue` | 从状态获取单个值 |
| `useBoundProp` | `$bindState`/`$bindItem` 表达式的双向绑定 |
| `useActions` | 访问操作上下文 |
| `useAction` | 获取单个操作派发函数 |
| `useOptionalValidation` | useValidation 的非抛出变体 |
| `useUIStream` | 从 API 端点流规范 |
| `createStateStore` | 创建框架无关的内存 `StateStore` |
| `StateStore` | 插入外部状态管理的接口 |
| `Components` | 类型化的组件映射（目录感知） |
| `Actions` | 类型化的操作映射（目录感知） |
| `ComponentContext` | 类型化的组件上下文（目录感知） |
| `flatToTree` | 将扁平元素映射转换为树结构 |

## 终端 UI 设计指南

- 使用 Box 进行布局（flexDirection、padding、gap）。默认的 flexDirection 是 row。
- 终端宽度约为 80-120 列。优先使用垂直布局（flexDirection: column）作为主结构。
- 在 Box 上使用 borderStyle 以进行视觉分组（单线、双线、圆角、粗体）。
- 使用命名的终端颜色：红色、绿色、黄色、蓝色、品红、青色、白色、灰色。
- 使用 Heading 作为区段标题，使用 Divider 分隔区段，使用 Badge 显示状态，使用 KeyValue 显示标记数据，使用 Card 显示带边框的组。
- 使用 Tabs 进行多视图 UI，并在子内容上使用可见性条件。
- 使用 Sparkline 显示行内趋势，使用 BarChart 比较值。
