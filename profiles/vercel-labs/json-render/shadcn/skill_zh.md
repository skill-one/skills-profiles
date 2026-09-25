# @json-render/shadcn

json-render的预构建shadcn/ui组件定义和实现。提供基于Radix UI和Tailwind CSS构建的36个组件。

## 两个入口点

| 入口点 | 导出 | 用于 |
|--------|------|------|
| `@json-render/shadcn/catalog` | `shadcnComponentDefinitions` | 目录模式（无React依赖，适用于服务器端） |
| `@json-render/shadcn` | `shadcnComponents` | React实现 |

## 使用模式

从标准定义中选择所需的组件。不要展开所有定义——明确选择应用程序使用的内容：

```typescript
import { defineCatalog } from "@json-render/core";
import { schema } from "@json-render/react/schema";
import { shadcnComponentDefinitions } from "@json-render/shadcn/catalog";
import { defineRegistry } from "@json-render/react";
import { shadcnComponents } from "@json-render/shadcn";

// 目录：选择定义
const catalog = defineCatalog(schema, {
  components: {
    Card: shadcnComponentDefinitions.Card,
    Stack: shadcnComponentDefinitions.Stack,
    Heading: shadcnComponentDefinitions.Heading,
    Button: shadcnComponentDefinitions.Button,
    Input: shadcnComponentDefinitions.Input,
  },
  actions: {},
});

// 注册：选择匹配的实现
const { registry } = defineRegistry(catalog, {
  components: {
    Card: shadcnComponents.Card,
    Stack: shadcnComponents.Stack,
    Heading: shadcnComponents.Heading,
    Button: shadcnComponents.Button,
    Input: shadcnComponents.Input,
  },
});
```

> 状态操作（`setState`、`pushState`、`removeState`）已集成到React模式中，并由`ActionProvider`自动处理。无需声明它们。

## 使用自定义组件扩展

与标准组件一起添加自定义组件：

```typescript
const catalog = defineCatalog(schema, {
  components: {
    // 标准
    Card: shadcnComponentDefinitions.Card,
    Stack: shadcnComponentDefinitions.Stack,

    // 自定义
    Metric: {
      props: z.object({
        label: z.string(),
        value: z.string(),
        trend: z.enum(["up", "down", "neutral"]).nullable(),
      }),
      description: "KPI指标显示",
    },
  },
  actions: {},
});

const { registry } = defineRegistry(catalog, {
  components: {
    Card: shadcnComponents.Card,
    Stack: shadcnComponents.Stack,
    Metric: ({ props }) => <div>{props.label}: {props.value}</div>,
  },
});
```

## 可用组件

### 布局
- **Card** - 带可选标题、描述、maxWidth、居中的容器
- **Stack** - 带方向、间隙、对齐、 justify 的 Flex 容器
- **Grid** - 带列数（数字）和间隙的网格布局
- **Separator** - 带方向的可视分隔符

### 导航
- **Tabs** - 带tabs数组、defaultValue、value的标签导航
- **Accordion** - 带items数组和类型（单选/多选）的可折叠部分
- **Collapsible** - 带标题的单个可折叠部分
- **Pagination** - 带totalPages和page的页面导航

### 覆盖层
- **Dialog** - 带标题、描述、openPath的模态对话框
- **Drawer** - 带标题、描述、openPath的底部抽屉
- **Tooltip** - 带内容和文本的悬停提示
- **Popover** - 带触发器和内容的点击触发弹出层
- **DropdownMenu** - 带标签和items数组的下拉菜单

### 内容
- **Heading** - 带级别（h1-h4）的标题文本
- **Text** - 带variant（body、caption、muted、lead、code）的段落
- **Image** - 带alt、width、height的图片
- **Avatar** - 带src、name、size的用户头像
- **Badge** - 带文本和variant（default、secondary、destructive、outline）的状态徽章
- **Alert** - 带标题、消息、类型（success、warning、info、error）的提示横幅
- **Carousel** - 带items数组的可滚动轮播
- **Table** - 带columns（string[]）和rows（string[][]）的数据表

### 反馈
- **Progress** - 带value、max、label的进度条
- **Skeleton** - 带width、height、rounded的加载占位符
- **Spinner** - 带size和label的加载旋转器

### 输入
- **Button** - 带label、variant（primary、secondary、danger）、disabled的按钮
- **Link** - 带label和href的锚链接
- **Input** - 带label、name、type、placeholder、value、checks的文本输入
- **Textarea** - 带label、name、placeholder、rows、value、checks的多行输入
- **Select** - 带label、name、options（string[]）、value、checks的下拉选择
- **Checkbox** - 带label、name、checked、checks、validateOn的复选框
- **Radio** - 带label、name、options（string[]）、value、checks、validateOn的单选组
- **Switch** - 带label、name、checked、checks、validateOn的切换开关
- **Slider** - 带label、min、max、step、value的范围滑块
- **Toggle** - 带label、pressed、variant的切换按钮
- **ToggleGroup** - 带items、type、value的切换组
- **ButtonGroup** - 带buttons数组和selected的按钮组

## 内置操作（来自`@json-render/react`）

这些已集成到React模式中，并由`ActionProvider`自动处理。它们在提示中显示，无需在目录中声明。

- **setState** - 在状态路径设置值（`{ statePath, value }`）
- **pushState** - 将值推到数组（`{ statePath, value, clearStatePath? }`）
- **removeState** - 通过索引删除数组项（`{ statePath, index }`）
- **validateForm** - 验证所有字段，将`{ valid, errors }`写入状态（`{ statePath? }`）

## 验证时机（`validateOn`）

所有表单组件支持`validateOn`来控制验证何时运行：
- `"change"` — 每次输入变化时验证（Select、Checkbox、Radio、Switch的默认值）
- `"blur"` — 字段失去焦点时验证（Input、Textarea的默认值）
- `"submit"` — 仅在表单提交时验证

## 重要说明

- `/catalog`入口点无React依赖——用于服务器端提示生成
- 组件使用Tailwind CSS类——您的应用程序必须配置Tailwind
- 组件实现使用捆绑的shadcn/ui基元（不是应用程序的`components/ui/`）
- 所有表单输入支持`checks`进行验证（类型+消息对）和`validateOn`控制时机
- 事件：输入触发`change`/`submit`/`focus`/`blur`；按钮触发`press`；选择触发`change`/`select`
