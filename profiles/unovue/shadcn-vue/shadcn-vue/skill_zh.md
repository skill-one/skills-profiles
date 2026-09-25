# shadcn-vue

一个用于构建 UI、组件和设计系统的框架。组件通过 CLI 添加到用户的项目中作为源代码。

> **重要提示**：使用项目的包运行器运行所有 CLI 命令：`npx shadcn-vue@latest`、`pnpm dlx shadcn-vue@latest` 或 `bunx --bun shadcn-vue@latest` — 基于项目的 `packageManager`。下面的示例使用 `npx shadcn-vue@latest`，但请将正确的运行器替换为项目。

## 当前项目上下文

```json
!`npx shadcn-vue@latest info --json`
```

上面的 JSON 包含项目配置和已安装的组件。使用 `npx shadcn-vue@latest docs <component>` 获取任何组件的文档和示例 URL。

## 原则

1. **优先使用现有组件。** 在编写自定义 UI 之前，使用 `npx shadcn-vue@latest search` 检查注册中心。也检查社区注册中心。
2. **组合，不要重新发明。** 设置页面 = Tabs + Card + 表单控件。仪表板 = 侧边栏 + Card + 图表 + 表格。
3. **在自定义样式之前使用内置变体。** `variant="outline"`、`size="sm"` 等。
4. **使用语义颜色。** `bg-primary`、`text-muted-foreground` — 永远不要使用原始值，如 `bg-blue-500`。

## 严格规则

这些规则**始终强制执行**。每个链接到一个包含不正确/正确代码对的文件。

### 样式 & Tailwind → [styling.md](./rules/styling.md)

- **`class` 用于布局，而不是样式。** 永远不要覆盖组件颜色或排版。
- **没有 `space-x-*` 或 `space-y-*`。** 使用 `flex` 与 `gap-*`。对于垂直堆叠，`flex flex-col gap-*`。
- **当宽度和高度相等时使用 `size-*`。** `size-10` 而不是 `w-10 h-10`。
- **使用 `truncate` 简写。** 不是 `overflow-hidden text-ellipsis whitespace-nowrap`。
- **没有手动 `dark:` 颜色覆盖。** 使用语义标记 (`bg-background`、`text-muted-foreground`)。
- **使用 `cn()` 进行条件类。** 不要编写手动模板字面量的三元运算符。
- **覆盖层组件没有手动 `z-index`。** 对话框、Sheet、Popover 等。它们自己处理堆叠。

### 表单 & 输入 → [forms.md](./rules/forms.md)

- **表单使用 `FieldGroup` + `Field`。** 永远不要使用原始 `div` 与 `space-y-*` 或 `grid gap-*` 进行表单布局。
- **`InputGroup` 使用 `InputGroupInput`/`InputGroupTextarea`。** 永远不要在 `InputGroup` 中使用原始 `Input`/`Textarea`。
- **输入内的按钮使用 `InputGroup` + `InputGroupAddon`。**
- **选项集（2-7 个选择）使用 `ToggleGroup`。** 不要循环 `Button` 并使用手动活动状态。
- **`FieldSet` + `FieldLegend` 用于分组相关的复选框/单选按钮。** 不要使用带有标题的 `div`。
- **字段验证使用 `data-invalid` + `aria-invalid`。** `data-invalid` 在 `Field` 上，`aria-invalid` 在控件上。对于禁用：`data-disabled` 在 `Field` 上，`disabled` 在控件上。

### 组件结构 → [composition.md](./rules/composition.md)

- **项目始终在其组内。** `SelectItem` → `SelectGroup`。`DropdownMenuItem` → `DropdownMenuGroup`。`CommandItem` → `CommandGroup`。
- **对话框、Sheet 和抽屉始终需要一个标题。** `DialogTitle`、`SheetTitle`、`DrawerTitle` 对可访问性是必需的。如果视觉上隐藏，请使用 `class="sr-only"`。
- **使用完整的 Card 组合。** `CardHeader`/`CardTitle`/`CardDescription`/`CardContent`/`CardFooter`。不要将所有内容都放入 `CardContent`。
- **按钮没有 `isPending`/`isLoading`。** 使用 `Spinner` + `data-icon` + `disabled` 组合。
- **`TabsTrigger` 必须在 `TabsList` 内。** 永远不要直接在 `Tabs` 中渲染触发器。
- **`Avatar` 始终需要一个 `AvatarFallback`。** 当图像加载失败时。

### 使用组件，而不是自定义标记 → [composition.md](./rules/composition.md)

- **在编写自定义标记之前使用现有组件。** 在编写带样式的 `div` 之前，检查是否存在组件。
- **Callouts 使用 `Alert`。** 不要构建自定义样式的 div。
- **空状态使用 `Empty`。** 不要构建自定义空状态标记。
- **Toast 通过 `vue-sonner`。** 使用 `vue-sonner` 的 `toast()`。
- **使用 `Separator`** 代替 `<hr>` 或 `<div class="border-t">`。
- **使用 `Skeleton`** 用于加载占位符。不要使用自定义 `animate-pulse` div。
- **使用 `Badge`** 代替自定义样式的 span。

### 图标 → [icons.md](./rules/icons.md)

- **按钮中的图标使用 `data-icon`。** 图标上使用 `data-icon="inline-start"` 或 `data-icon="inline-end"`。
- **组件中的图标没有尺寸类。** 组件通过 CSS 处理图标尺寸。没有 `size-4` 或 `w-4 h-4`。
- **将图标作为对象传递，而不是字符串键。** `:icon="CheckIcon"`，而不是字符串查找。

### CLI

- **使用 CLI 直接应用预设代码。** 使用 `npx shadcn-vue@latest apply <code>` 为现有项目添加，或在初始化时使用 `npx shadcn-vue@latest init --preset <code>`。

## 关键模式

这些是最常见的模式，它们区分了正确的 shadcn-vue 代码。对于边缘情况，请参阅上面链接的规则文件。

```html
<!-- 表单布局：FieldGroup + Field，而不是 div + Label。 -->
<FieldGroup>
  <Field>
    <FieldLabel for="email">Email</FieldLabel>
    <Input id="email" />
  </Field>
</FieldGroup>

<!-- 验证：data-invalid 在 Field 上，aria-invalid 在控件上。 -->
<Field data-invalid>
  <FieldLabel>Email</FieldLabel>
  <Input aria-invalid />
  <FieldDescription>无效的电子邮件。</FieldDescription>
</Field>

<!-- 按钮中的图标：data-icon，没有尺寸类。 -->
<Button>
  <SearchIcon data-icon="inline-start" />
  搜索
</Button>

<!-- 间距：gap-*，而不是 space-y-*. -->
<div class="flex flex-col gap-4">  <!-- 正确 -->
<div class="space-y-4">           <!-- 错误 -->

<!-- 相同尺寸：size-*，而不是 w-* h-*. -->
<Avatar class="size-10">   <!-- 正确 -->
<Avatar class="w-10 h-10"> <!-- 错误 -->

<!-- 状态颜色：Badge 变体或语义标记，而不是原始颜色。 -->
<Badge variant="secondary">+20.1%</Badge>    <!-- 正确 -->
<span class="text-emerald-600">+20.1%</span> <!-- 错误 -->
```

## 组件选择

| 需要                       | 使用                                                                                                 |
| -------------------------- | --------------------------------------------------------------------------------------------------- |
| 按钮/操作                  | `Button` 与适当的变体                                                                   |
| 表单输入                | `Input`、`Select`、`Combobox`、`Switch`、`Checkbox`、`RadioGroup`、`Textarea`、`InputOTP`、`Slider` |
| 在 2-7 个选项之间切换      | `ToggleGroup` + `ToggleGroupItem`                                                                   |
| 数据显示               | `Table`、`Card`、`Badge`、`Avatar`                                                                  |
| 导航                 | `Sidebar`、`NavigationMenu`、`Breadcrumb`、`Tabs`、`Pagination`                                     |
| 覆盖层                   | `Dialog`（模态）、`Sheet`（侧边面板）、`Drawer`（底部面板）、`AlertDialog`（确认）       |
| 反馈                   | `vue-sonner`（Toast）、`Alert`、`Progress`、`Skeleton`、`Spinner`                                   |
| 命令面板            | `Command` 在 `Dialog` 内                                                                           |
| 图表                     | `Chart`（包装 Unovis）                                                                              |
| 布局                     | `Card`、`Separator`、`Resizable`、`ScrollArea`、`Accordion`、`Collapsible`                          |
| 空状态               | `Empty`                                                                                             |
| 菜单                      | `DropdownMenu`、`ContextMenu`、`Menubar`                                                            |
| 提示/信息              | `Tooltip`、`HoverCard`、`Popover`                                                                   |

## 关键字段

注入的项目上下文中包含这些关键字段：

- **`aliases`** → 使用实际的别名前缀进行导入（例如 `@/`、`~/`），永远不要硬编码。
- **`tailwindVersion`** → `"v4"` 使用 `@theme inline` 块；`"v3"` 使用 `tailwind.config.js`。
- **`tailwindCssFile`** → 全局 CSS 文件，其中定义了自定义 CSS 变量。始终编辑此文件，永远不要创建新文件。
- **`style`** → 组件视觉处理（例如 `nova`、`vega`）。
- **`base`** → 基础库 (`reka`)。影响组件 API 和可用属性。
- **`iconLibrary`** → 确定图标导入。使用 `@lucide/vue` 用于 `lucide`，`@tabler/icons-vue` 用于 `tabler` 等。永远不要假设 `@lucide/vue`。
- **`resolvedPaths`** → 组件、工具、钩子等的精确文件系统目的地。
- **`framework`** → 路由和文件约定（例如 Nuxt 与 Vite SPA）。
- **`packageManager`** → 用于任何非 shadcn-vue 依赖项安装（例如 `pnpm add date-fns` 与 `npm install date-fns`）。

有关完整字段参考，请参阅 [cli.md — `info` 命令](./cli.md)。

## 组件文档、示例和用法

运行 `npx shadcn-vue@latest docs <component>` 获取组件文档、示例和 API 参考的 URL。获取这些 URL 以获取实际内容。

```bash
npx shadcn-vue@latest docs button dialog select
```

**在创建、修复、调试或使用组件时，始终运行 `npx shadcn-vue@latest docs` 并首先获取 URL。** 这确保您使用的是正确的 API 和使用模式，而不是猜测。

## 工作流程

1. **获取项目上下文** — 已经注入。如果您需要刷新，请再次运行 `npx shadcn-vue@latest info`。
2. **首先检查已安装的组件** — 在运行 `add` 之前，始终检查项目上下文中的 `components` 列表或列出 `resolvedPaths.ui` 目录。不要导入尚未添加的组件，也不要重新添加已安装的组件。
3. **查找组件** — `npx shadcn-vue@latest search`。
4. **获取文档和示例** — 运行 `npx shadcn-vue@latest docs <component>` 获取 URL，然后获取它们。使用 `npx shadcn-vue@latest view` 浏览尚未安装的注册中心项目。要预览已安装组件的更改，请使用 `npx shadcn-vue@latest add --diff`。
5. **安装或更新** — `npx shadcn-vue@latest add`。在更新现有组件时，使用 `--dry-run` 和 `--diff` 首先预览更改（见下文 [更新组件](#updating-components)）。
6. **修复第三方组件中的导入** — 添加来自社区注册中心的组件后，检查添加的非 UI 文件，查找硬编码的导入路径，如 `@/components/ui/...`。这些不会匹配项目的实际别名。使用 `npx shadcn-vue@latest info` 获取正确的 `ui` 别名（例如 `@workspace/ui/components`），并相应地重写导入。CLI 会重写自己的 UI 文件的导入，但第三方注册中心的组件可能使用默认路径，这些路径与项目不匹配。
7. **审查添加的组件** — 添加组件或块后，**始终阅读添加的文件并验证它们是否正确**。检查是否有缺失的子组件（例如 `SelectItem` 而没有 `SelectGroup`）、缺失的导入、不正确的组合或违反 [严格规则](#critical-rules) 的情况。还必须将任何图标导入替换为项目上下文中的 `iconLibrary`（例如，如果注册中心项目使用 `@lucide/vue` 但项目使用 `hugeicons`，请相应地交换导入和图标名称）。在继续之前修复所有问题。
8. **注册必须明确** — 当用户要求添加块或组件时，**不要猜测注册中心**。如果未指定注册中心（例如，用户说“添加一个登录块”而没有指定 `@shadcn` 等），请询问要使用哪个注册中心。永远不要代表用户选择注册中心。
9. **切换预设** — 首先询问用户：**覆盖**、**合并** 或 **跳过**？
   - **覆盖**：`npx shadcn-vue@latest apply <code>`。覆盖检测到的组件、字体和 CSS 变量。
   - **合并**：`npx shadcn-vue@latest init --preset <code> --force --no-reinstall`，然后运行 `npx shadcn-vue@latest info` 列出已安装的组件，然后对每个已安装的组件使用 `--dry-run` 和 `--diff` 以 [智能合并](#updating-components)。
   - **跳过**：`npx shadcn-vue@latest init --preset <code> --force --no-reinstall`。仅更新配置和 CSS，保留组件不变。
   - **重要**：始终在用户的 项目目录内运行预设命令。`apply` 仅适用于具有 `components.json` 文件的现有项目。CLI 自动保留当前的 `base` (`reka`) 从 `components.json`。如果您必须使用临时/临时目录（例如，用于 `--dry-run` 比较），请显式传递 `--base <current-base>` — 预设代码不包含 `base`。

## 更新组件

当用户要求在保留本地更改的情况下从上游更新组件时，使用 `--dry-run` 和 `--diff` 进行智能合并。**永远不要手动从 GitHub 获取原始文件 — 始终使用 CLI。**

1. 运行 `npx shadcn-vue@latest add <component> --dry-run` 查看所有受影响的文件。
2. 对于每个文件，运行 `npx shadcn-vue@latest add <component> --diff <file>` 查看上游与本地之间的更改。
3. 根据差异逐文件决定：
   - 没有本地更改 → 可以安全覆盖。
   - 有本地更改 → 阅读本地文件，分析差异，并在保留本地修改的同时应用上游更新。
   - 用户说“只是更新所有内容” → 使用 `--overwrite`，但先确认。
4. **永远不要在未经用户明确批准的情况下使用 `--overwrite`。**

## 快速参考

```bash
# 创建新项目。
npx shadcn-vue@latest init --name my-app --preset nova
npx shadcn-vue@latest init --name my-app --preset a2r6bw --template vite

# 初始化现有项目。
npx shadcn-vue@latest init --preset nova
npx shadcn-vue@latest init --defaults  # 快捷方式：--template=nuxt --preset=nova（隐含基础样式）

# 将预设应用于现有项目。
npx shadcn-vue@latest apply a2r6bw

# 添加组件。
npx shadcn-vue@latest add button card dialog
npx shadcn-vue@latest add --all

# 搜索注册中心。
npx shadcn-vue@latest search @shadcn -q "sidebar"

# 获取组件文档和示例 URL。
npx shadcn-vue@latest docs button dialog select

# 查看注册中心项目详细信息（对于尚未安装的项目）。
npx shadcn-vue@latest view @shadcn/button
```

**命名预设：** `nova`、`vega`、`maia`、`lyra`、`mira`、`luma`
**模板：** `nuxt`、`vite`、`astro` 和 `laravel`
**预设代码：** 版本前缀的 base62 字符串（例如 `a2r6bw`），来自 [shadcn-vue.com](https://shadcn-vue.com)。

## 详细参考

- [rules/forms.md](./rules/forms.md) — FieldGroup、Field、InputGroup、ToggleGroup、FieldSet、验证状态
- [rules/composition.md](./rules/composition.md) — 组、覆盖层、Card、Tabs、Avatar、Alert、Empty、Toast、Separator、Skeleton、Badge、Button 加载
- [rules/icons.md](./rules/icons.md) — data-icon、图标尺寸、将图标作为对象传递
- [rules/styling.md](./rules/styling.md) — 语义颜色、变体、class、间距、size、truncate、暗黑模式、cn()、z-index
- [cli.md](./cli.md) — 命令、标志、预设、模板
- [customization.md](./customization.md) — 主题、CSS 变量、扩展组件
