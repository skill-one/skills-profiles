# shadcn-svelte

一个用于为 Svelte 构建 UI、组件和设计系统的框架。组件通过 CLI 添加到用户的项目源代码中。

> **重要提示**：使用项目的包运行器运行所有 CLI 命令：`npx shadcn-svelte@latest`、`pnpm dlx shadcn-svelte@latest` 或 `bunx --bun shadcn-svelte@latest` — 根据项目的包管理器。下面的示例使用 `npx shadcn-svelte@latest`，但请为项目替换正确的运行器。

## 当前项目上下文

在项目根目录下读取 `components.json`，当您需要实时文件布局时，列出由 `aliases.ui` 路径指定的目录（与 CLI 使用相同的解析规则）。

## 导入（Svelte）

每个组件都位于其自己的文件夹中，并带有 `index.ts` 巴雷尔。匹配 [安装文档](https://shadcn-svelte.com/docs/installation)：

- **多部分组件**（对话框、选择、卡片、字段、选项卡、…）：`import * as Dialog from "$lib/components/ui/dialog"` 然后是 `Dialog.Content`、`Dialog.Title`、`Card.Root`、`Card.Header` 等 — 任何巴雷尔导出的内容（简称和/或 `Root as …` 别名）。
- **单组件巴雷尔**（文件夹中只有一个有意义的组件）：**命名导入** — `import { Button } from "$lib/components/ui/button"` 和 `<Button>`，而不是 `import * as Button` + `Button.Root`。相同模式适用于 `{ Input }`、`{ Badge }`、`{ Spinner }`、`{ Checkbox }`、`{ Separator }`、`{ Skeleton }` 等。

```ts
import * as Dialog from "$lib/components/ui/dialog";
import { Button } from "$lib/components/ui/button";
import { Separator } from "$lib/components/ui/separator";
```

使用来自 `components.json` 的真实别名（通常是 `$lib/components/ui/...`），而不是硬编码的路径。

## 原则

1. **首先使用现有组件。** 运行 `npx shadcn-svelte@latest add` 带无参数来浏览可用组件，或在编写自定义 UI 之前查看 [组件](https://shadcn-svelte.com/docs/components)。
2. **组合，不要重新发明。** 设置页面 = 选项卡 + 卡片 + 表单控件。仪表板 = 侧边栏 + 卡片 + 图表 + 表格。
3. **在自定义样式之前使用内置变体。** `variant="outline"`、`size="sm"` 等。
4. **使用语义颜色。** `bg-primary`、`text-muted-foreground` — 永远不要使用原始值，如 `bg-blue-500`。

## 严格规则

这些规则**始终强制执行**。每个链接到一个包含不正确/正确代码对的文件。

### 样式 & Tailwind → [styling.md](./rules/styling.md)

- **`class` 用于布局，而不是样式。** 永远不要覆盖组件颜色或排版。
- **没有 `space-x-*` 或 `space-y-*`。** 使用 `flex` 与 `gap-*`。对于垂直堆叠，`flex flex-col gap-*`。
- **当宽度和高度相等时使用 `size-*`。** `size-10` 而不是 `w-10 h-10`。
- **使用 `truncate` 简写。** 不是 `overflow-hidden text-ellipsis whitespace-nowrap`。
- **没有手动 `dark:` 颜色覆盖。** 使用语义标记（`bg-background`、`text-muted-foreground`）。
- **使用 `cn()` 进行条件类。** 不要编写手动模板字面量三元运算符。
- **没有手动 `z-index` 在覆盖组件上。** 对话框、Sheet、Popover 等。处理它们自己的堆叠。

### 表单 & 输入 → [forms.md](./rules/forms.md)

- **表单使用 `Field.FieldGroup` + `Field.Field`。** 永远不要使用原始 `div` 与 `space-y-*` 或 `grid gap-*` 进行表单布局。
- **`InputGroup` 使用 `InputGroup.Input`/`InputGroup.Textarea`。** 永远不要在 `InputGroup.Root` 中使用原始 `Input`/`Textarea`。
- **输入中的按钮使用 `InputGroup.Root` + `InputGroup.Addon`。**
- **选项集（2-7 个选择）使用 `ToggleGroup`。** 不要循环 `Button` 并使用手动活动状态。
- **`Field.FieldSet` + `Field.FieldLegend` 用于分组相关的复选框/单选按钮。** 不要使用带有标题的 `div`。
- **字段验证使用 `data-invalid` + `aria-invalid`。** `data-invalid` 在 `Field` 上，`aria-invalid` 在控件上。对于禁用：`data-disabled` 在 `Field` 上，`disabled` 在控件上。

### 组件结构 → [composition.md](./rules/composition.md)

- **项目始终在其组内。** `Select.Item` → `Select.Group`。`DropdownMenu.Item` → `DropdownMenu.Group`。`Command.Item` → `Command.Group`。
- **自定义触发器。** 将控件包裹在 `Dialog.Trigger` / `AlertDialog.Trigger` 中，或使用 `bind:open` 在根上控制打开状态 — 见组件文档。
- **对话框、Sheet 和抽屉始终需要一个标题。** `Dialog.Title`、`Sheet.Title`、`Drawer.Title` 对可访问性是必需的。如果视觉上隐藏，请使用 `class="sr-only"`。
- **使用完整的卡片组合。** `Card.Header`/`Card.Title`/`Card.Description`/`Card.Content`/`Card.Footer`。不要将所有内容都放入 `Card.Content`。
- **按钮没有 `isPending`/`isLoading`。** 使用 `Spinner` 在 `Button` 内部 + `disabled` 组合；使用 `data-icon="inline-start"` / `inline-end` 在 `Spinner` 上以正确间距（`import { Button }`，`import { Spinner }`）。
- **`Tabs.Trigger` 必须在 `Tabs.List` 内。** 永远不要直接在 `Tabs` 中渲染触发器。
- **`Avatar` 始终需要一个 `Avatar.Fallback`。** 当图像加载失败时。

### 使用组件，而不是自定义标记 → [composition.md](./rules/composition.md)

- **在编写自定义标记之前使用现有组件。** 检查是否存在组件，然后再编写带有样式的 `div`。
- **Callouts 使用 `Alert`。** 不要构建自定义样式的 div。
- **空状态使用 `Empty`。** 不要构建自定义空状态标记。
- **Toast 通过 `svelte-sonner`。** 使用 `svelte-sonner` 的 `toast()` 并使用 UI 文件夹中的 Sonner 组件。
- **使用 `Separator`** 而不是 `<hr>` 或带有边框类的 `div`。
- **使用 `Skeleton`** 用于加载占位符。不要使用自定义 `animate-pulse` div。
- **使用 `Badge`** 而不是自定义样式的 span。

### 图标 → [icons.md](./rules/icons.md)

- **`Button` 中的图标使用 `data-icon`。** 图标上使用 `data-icon="inline-start"` 或 `data-icon="inline-end"`。
- **组件中的图标没有尺寸类。** 组件通过 CSS 处理图标尺寸。没有 `size-4` 或 `w-4 h-4`。
- **将图标作为组件传递。** 从配置的 `iconLibrary`（例如 `@lucide/svelte`）导入，而不是字符串键。

### CLI

- **预设** — 从 [shadcn-svelte.com](https://shadcn-svelte.com) 设计系统构建器中复制编码字符串，并将其传递给 `npx shadcn-svelte@latest init --preset <code>`。

## 关键模式

这些是最常见的模式，它们区分了正确的 shadcn-svelte 代码。对于边缘情况，请参阅上面链接的规则文件。

```svelte
<script lang="ts">
  import * as Field from "$lib/components/ui/field";
  import { Input } from "$lib/components/ui/input";
  import { Button } from "$lib/components/ui/button";
  import SearchIcon from "@lucide/svelte/icons/search";
  import { Badge } from "$lib/components/ui/badge";
  import * as Avatar from "$lib/components/ui/avatar";
</script>

<!-- 表单布局：Field.FieldGroup + Field.Field，而不是 div + Label。 -->
<Field.FieldGroup>
  <Field.Field>
    <Field.FieldLabel for="email">Email</Field.FieldLabel>
    <Input id="email" />
  </Field.Field>
</Field.FieldGroup>

<!-- 验证：data-invalid 在 Field 上，aria-invalid 在控件上。 -->
<Field.Field data-invalid>
  <Field.FieldLabel for="email">Email</Field.FieldLabel>
  <Input id="email" aria-invalid />
  <Field.FieldDescription>无效的电子邮件。</Field.FieldDescription>
</Field.Field>

<!-- 按钮中的图标：data-icon，没有尺寸类。 -->
<Button>
  <SearchIcon data-icon="inline-start" />
  搜索
</Button>

<!-- 间距：gap-*, 不是 space-y-*. -->
<div class="flex flex-col gap-4"></div>

<!-- 相等尺寸：size-*, 不是 w-* h-*. -->
<Avatar.Root class="size-10">
  <Avatar.Image src="/u.png" alt="用户" />
  <Avatar.Fallback>U</Avatar.Fallback>
</Avatar.Root>

<!-- 状态颜色：Badge 变体或语义标记，不是原始颜色。 -->
<Badge variant="secondary">+20.1%</Badge>
```

## 组件选择

| 需要                       | 使用                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------- |
| 按钮/操作                  | `Button` 带有适当的变体（`import { Button }`）                                             |
| 表单输入                | `Input`、`Select`、`Combobox`、`Switch`、`Checkbox`、`RadioGroup`、`Textarea`、`InputOTP`、`Slider` |
| 在 2-5 个选项之间切换 | `ToggleGroup.Root` + `ToggleGroup.Item`                                                             |
| 数据显示               | `Table`、`Card`、`Badge`、`Avatar`                                                                  |
| 导航                 | `Sidebar`、`NavigationMenu`、`Breadcrumb`、`Tabs`、`Pagination`                                     |
| 覆盖层                   | `Dialog`（模态）、`Sheet`（侧边面板）、`Drawer`（底部面板）、`AlertDialog`（确认）       |
| 反馈                   | `svelte-sonner`（Toast）、`Alert`、`Progress`、`Skeleton`、`Spinner`                                 |
| 命令面板            | `Command` 在 `Dialog` 内部                                                                           |
| 图表                     | `Chart`（LayerChart）                                                                                |
| 布局                     | `Card`、`Separator`、`Resizable`、`ScrollArea`、`Accordion`、`Collapsible`                          |
| 空状态               | `Empty`                                                                                             |
| 菜单                      | `DropdownMenu`、`ContextMenu`、`Menubar`                                                            |
| 提示/信息              | `Tooltip`、`HoverCard`、`Popover`                                                                   |

## 关键字段

使用 `components.json` 和文件系统 — 不要使用单独的 `info` 命令：

- **`aliases`** → 使用配置中的实际别名前缀（例如 `$lib/`），永远不要硬编码不相关的项目。
- **`tailwind.css`** → 包含主题变量的全局 CSS 文件。编辑此文件以调整主题；除非用户已经使用了一个，否则不要添加第二个全局文件。
- **`style`** → 视觉处理（例如 `nova`、`vega`、…）和注册样式路径。
- **`iconLibrary`** → 确定图标包（`@lucide/svelte`、`@tabler/icons-svelte` 等）。永远不要假设 `@lucide/svelte`。
- **`registry`** → CLI 从哪里获取组件；默认官方注册表位于 `shadcn-svelte.com`。
- **`resolvedPaths`**（概念上）→ CLI 将 `aliases` 解析为绝对路径；在磁盘上列出 `aliases.ui` 以查看已安装的组件。

参见 [cli.md](./cli.md) 以获取命令和标志。

## 组件文档、示例和用法

打开 `https://shadcn-svelte.com/docs/components/<name>.md` 获取文档和示例。**在创建、修复、调试或使用组件时，首先阅读官方页面**，以便您遵循文档化的 API。

## 工作流程

1. **获取项目上下文** — 读取 `components.json` 并在需要时列出 UI 组件目录。
2. **首先检查已安装的组件** — 在运行 `add` 之前，列出解析的 `ui` 路径下的文件。不要导入尚未添加的组件，也不要重新添加已经存在的组件，除非更新。
3. **发现组件** — `npx shadcn-svelte@latest add` 带无参数（交互式列表），或文档网站。
4. **安装或更新** — `npx shadcn-svelte@latest add <name>` 或注册表 **URL**。要从注册表刷新现有文件，请使用 `npx shadcn-svelte@latest update`（参见 [cli.md](./cli.md)）。
5. **修复第三方/URL 添加项中的导入** — 添加来自自定义注册表 URL 后，检查不匹配项目 `aliases` 的硬编码路径。将导入重写为使用 `components.json` 中的项目 `ui` / `lib` 别名。
6. **审查添加的组件** — 添加后，**阅读添加的文件** 并验证组合（组、标题、验证属性）。对图标导入与 `iconLibrary` 保持一致。
7. **远程注册表项** — 通过 URL 添加是明确的；如果用户想要来自未知源的组件，请在运行 `add` 之前确认注册表 URL 或项。

## 更新组件

使用 **`update`** 命令来拉取项目中组件的最新注册表版本。在 `update` 后使用 `git diff` 审查更改。

1. 提交或暂存本地工作。
2. 运行 `npx shadcn-svelte@latest update [component]` 或 `--all`。
3. 如果您已经自定义了文件，请解决合并冲突。
4. **在未得到用户明确批准的情况下，永远不要在 `add` 上使用 `--overwrite`**，因为它会破坏有意编辑。

## 快速参考

```bash
# 在您的项目中初始化 shadcn-svelte。
npx shadcn-svelte@latest init

# 使用文档网站构建器中的预设字符串初始化。
npx shadcn-svelte@latest init --preset <code>

# 添加组件（带无名称时运行为交互式）。
npx shadcn-svelte@latest add
npx shadcn-svelte@latest add button card dialog
npx shadcn-svelte@latest add --all

# 更新已安装的组件。
npx shadcn-svelte@latest update button
npx shadcn-svelte@latest update --all --yes

# 构建自定义注册表（注册表作者）。
npx shadcn-svelte@latest registry build
```

**注册表：** 默认 `https://shadcn-svelte.com/registry` — 如有必要，在 `components.json` 中覆盖。  
**文档：** [shadcn-svelte.com](https://shadcn-svelte.com)

## 详细参考

- [rules/forms.md](./rules/forms.md) — Field.FieldGroup、Field.Field、InputGroup、ToggleGroup、Field.FieldSet、验证状态
- [rules/composition.md](./rules/composition.md) — 组、覆盖层、Card、Tabs、Avatar、Alert、Empty、Toast、Separator、Skeleton、Badge、按钮加载
- [rules/icons.md](./rules/icons.md) — data-icon、图标尺寸、传递图标组件
- [rules/styling.md](./rules/styling.md) — 语义颜色、变体、类、间距、尺寸、truncate、暗黑模式、cn()、z-index
- [cli.md](./cli.md) — 命令、标志、注册表
- [customization.md](./customization.md) — 主题、CSS 变量、扩展组件
