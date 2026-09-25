# React 组件编写指南

## 样式

| 场景                                                         | 方法                                                       |
| ------------------------------------------------------------ | -------------------------------------------------------------- |
| 大多数情况                                                 | `createStaticStyles` + `cssVar.*`（零运行时，模块级）       |
| 简单一次性                                                 | 内联 `style` 属性                                       |
| 真正动态（如 `readableColor`/`chroma` 的 JS 颜色函数） | `createStyles` + `token` — **最后手段**                     |

## 组件优先级

1. **`src/components`** — 项目特定的可重用组件
2. **`@lobehub/ui/base-ui`** — 无头原始组件。**如果组件在此处，请使用它。不要导入同名的根导出。**
3. **`@lobehub/ui`** — 更高级别/antd 封装组件（仅当没有 base-ui 对应组件时使用）
4. **antd** — 仅当 base-ui 和 `@lobehub/ui` 根导出都不提供时使用
5. **自定义实现** — 真正的最后手段

如果不确定可用组件，请搜索现有代码或检查 `node_modules/@lobehub/ui/es/index.mjs` 和 `node_modules/@lobehub/ui/es/base-ui/`。

### `@lobehub/ui/base-ui` — 优先使用这些

| 组件                                  | 导入                                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------------------------------------------------- |
| `Alert` (+ `AlertProps`)                   | `import { Alert, type AlertProps } from '@lobehub/ui/base-ui';`                                         |
| `Select` (+ `SelectProps`, `SelectOption`) | `import { Select } from '@lobehub/ui/base-ui';`                                                         |
| `Modal` (命令式 API)                   | `import { createModal, confirmModal, useModalContext, type ModalInstance } from '@lobehub/ui/base-ui';` |
| `DropdownMenu`                             | `import { DropdownMenu } from '@lobehub/ui/base-ui';`                                                   |
| `ContextMenu`                              | `import { ContextMenu } from '@lobehub/ui/base-ui';`                                                    |
| `Popover`                                  | `import { Popover } from '@lobehub/ui/base-ui';`                                                        |
| `ScrollArea`                               | `import { ScrollArea } from '@lobehub/ui/base-ui';`                                                     |
| `Switch`                                   | `import { Switch } from '@lobehub/ui/base-ui';`                                                         |
| `Toast`                                    | `import { Toast } from '@lobehub/ui/base-ui';`                                                          |
| `FloatingSheet`                            | `import { FloatingSheet } from '@lobehub/ui/base-ui';`                                                  |
| `Drawer`                                   | `import { Drawer } from '@lobehub/ui/base-ui';`                                                         |

对于 Modal 特定，请参阅专门的 **modal** 技能 — 使用命令式 `createModal({ content: … })` 模式而不是遗留的 `<Modal open … />` 声明式模式。base-ui 已经在 `SPAGlobalProvider` 中挂载了自己的 `ModalHost`。

> 常见错误：`import { Select } from '@lobehub/ui'` 看起来没问题，但它使用的是 antd 封装的 Select。请使用 base-ui Select。`Modal`、`DropdownMenu` 等同理。

### `@lobehub/ui` 根导出 — 当 base-ui 没有对应组件时使用

| 类别     | 组件                                                                            |
| ------------ | ------------------------------------------------------------------------------------- |
| 常规      | ActionIcon, ActionIconGroup, Block, Button, Icon                                      |
| 数据展示 | Avatar, Collapse, Empty, Highlighter, Markdown, Tag, Tooltip                          |
| 数据输入   | CodeEditor, CopyButton, EditableText, Form, Input, InputPassword, SearchBar, TextArea |
| 布局       | Center, DraggablePanel, Flexbox, Grid, Header, MaskShadow                             |
| 导航       | Burger, Menu, SideNav, Tabs                                                           |

## 状态管理

将短暂状态保持在最小的有用所有者中。当状态转换和处理器使渲染变得模糊或形成可重用的单元时，提取自定义钩子；不要仅因为组件有特定数量的钩子而提取。

仅当需要建立真实状态、重用、渲染更新或挂载能力边界时才拆分组件。不要仅因为文件变小而拆分。将复杂的领域功能分解为宿主组装的原子属于 **`compose-atoms`**。

## 渲染性能和记忆化

将 `memo`、`useMemo` 和 `useCallback` 视为可选优化，而不是默认组件包装器。添加之前，先识别实际的重绘边界，并优先考虑结构修复：

1. 在更新边界处拆分。
2. 将短暂状态移至最小所有者。
3. 使用窄 Zustand 选择器并避免宽泛订阅。

不要记忆化无参数或简单渲染的组件，或通常接收新对象、数组、函数或 JSX 子组件的组件。不要使用记忆化来弥补状态在树中持有过高的问题。

仅在子树明显昂贵或频繁重复、其相关输入在正常父渲染期间保持稳定，并且分析或具体渲染路径识别了避免的工作时使用记忆化。在实现摘要或 PR 中说明原因。

## 布局

使用 `@lobehub/ui` 中的 `Flexbox` 和 `Center`。参见 `references/layout-kit.md` 获取完整属性和示例。

- 使用 `gap` 而不是 `margin` 用于 flex 子项之间的间距
- 使用 `flex={1}` 填充可用空间
- 嵌套 Flexbox 用于复杂布局；为可滚动区域设置 `overflow: 'auto'`

## 相关技能

- **`ux`**：加载视觉效果和用户界面交互设计。不要使用 antd `Spin` / `<Spin />`。
- **`modal`**：命令式 base-ui modal 模式。
- **`spa-routes`**：SPA 导航、路由所有权、路由配置和 `.desktop` 变体。
- **`compose-atoms`**：将复杂的领域功能分解为可挂载能力原子；每个宿主仅导入它挂载的部分。
- **`zustand`**：存储结构和选择器约定。
