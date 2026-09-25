# spartan/ui

spartan/ui 是一个 Angular UI 库。它采用**双层架构**：

- **Brain (`@spartan-ng/brain`)** - 可访问性、无样式的原始组件（Angular 指令/组件），通过 npm 安装。这是行为和可访问性层。
- **Helm (`@spartan-ng/helm`)** - 样式层（Tailwind + class-variance-authority）。Helm 代码由 CLI 复制到用户项目中，以便用户拥有并可以自定义它。

您将 Helm 指令/组件组合到宿主元素上；Helm 在底层自动连接匹配的 Brain 原始组件。始终优先使用现有组件而不是手写标记。

所有 CLI 命令都通过工作区的 runner 运行。从项目中检测它：

- **Nx 工作区**（有 `nx.json`）：`npx nx g @spartan-ng/cli:<generator>`（或 `pnpm nx g ...`）。
- **Angular CLI 工作区**（有 `angular.json`，没有 `nx.json`）：`ng g @spartan-ng/cli:<generator>`。

## 当前项目上下文

在生成任何代码之前，收集项目上下文：

```bash
npx nx g @spartan-ng/cli:info --json     # Nx
ng g @spartan-ng/cli:info --json         # Angular CLI
```

这是只读的，并打印包含以下内容的 JSON：

- `workspaceType` - `nx` | `angular-cli`（决定使用哪个 runner）。
- `config.componentsPath` - Helm 组件复制的位置（例如 `libs/ui`）。
- `config.importAlias` - Helm 的导入前缀，默认 `@spartan-ng/helm`。
- `config.generateAs` - `library` | `entrypoint`（Nx 布局选择）。
- `versions` - Angular、Angular CDK、Tailwind、`@spartan-ng/brain`、`@spartan-ng/cli`。
- `iconLibrary` - 当存在时为 `@ng-icons`。
- `tailwindCssFile` - 导入预设的全局样式表。
- `installedComponents` - 已存在的组件（不要重新添加这些）。
- `availableComponents` - CLI 可以生成的一切。

如果 `components.json` 不存在，项目尚未设置 - 首先运行 `@spartan-ng/cli:init`（它安装依赖项和主题）。`components.json` 本身在您使用 `ui` 添加第一个组件时创建（见 `cli.md`）。

## 原则

1. **首先使用现有组件。** 检查 `installedComponents`，然后 `availableComponents`。通过 MCP 服务器（`spartan_components_list` / `spartan_components_get`）或 `https://www.spartan.ng/components/<name>` 的实时文档查找文档。见 `mcp.md`。
2. **组合，不要重新发明。** 使用现有的 Helm + Brain 片段构建仪表板、表单和对话框，而不是自定义标记。
3. **在自定义样式之前使用内置变体。** 按钮、徽章、警报等提供 `variant` 和 `size` 输入 - 使用它们而不是覆盖类。
4. **使用语义颜色，永远不要使用原始值。** `bg-primary text-primary-foreground`，而不是 `bg-blue-500`。见 `rules/styling.md`。

## 严格规则

在执行相关工作之前，阅读规则文件：

- **`rules/styling.md`** - `hlm()` 工具、语义颜色标记、仅布局类、`gap-*` 覆盖 `space-*`、`size-*`、暗黑模式、覆盖层上不要手动设置 z-index。
- **`rules/forms.md`** - 使用 `hlmField`（标签、控件、错误、描述）和 `hlmFieldSet` / `hlmFieldLegend` 在原生 `<fieldset>`/`<legend>` 上组合表单；选项集（2-7 个选择）使用 `hlm-toggle-group`。
- **`rules/composition.md`** - 项目应属于其组内；对话框/表单需要标题；完整卡片组合；`hlm-tabs-list` 内的选项卡触发器；头像始终有备用；使用 `Alert`/`Empty`/`Skeleton`/`Badge`/`Separator`/`Spinner` 而不是自定义标记。
- **`rules/icons.md`** - 图标是 `<ng-icon name="lucide...">`；通过 `provideIcons` 注册；组件内不要手动设置尺寸类 - 使用 `size` 输入。
- **`rules/brain-vs-helm.md`** - 双层模型（一个无头库 Brain，加上样式 Helm 层）；何时直接使用 Brain，何时使用 Helm，以及如何通过指令进行组合。
- **`cli.md`** - 每个生成器（`init`、`ui`、`ui-theme`、`healthcheck`、`info`、`migrate-*`），以及 Nx 和 Angular CLI 调用。
- **`registry.md`** - Brain-npm + Helm 复制进来的分发模型、`components.json` 和固定的组件目录（CLI 使用不远程或自定义注册表）。
- **`customization.md`** - 通过 `hlm-tailwind-preset.css`、CSS 变量、`ui-theme` 生成器以及扩展复制的 Helm 组件进行主题化。
- **`mcp.md`** - 使用 `@spartan-ng/mcp` 工具、资源和提示进行发现。

## 关键模式

```html
<!-- 按钮：使用 variant/size 输入，而不是自定义类 -->
<button hlmBtn variant="destructive" size="lg">删除</button>

<!-- 按钮中的图标：ng-icon -->
<button hlmBtn size="icon" variant="ghost">
	<ng-icon name="lucideTrash" />
</button>

<!-- 加载状态：组合一个 spinner，没有 isLoading 输入 -->
<button hlmBtn [disabled]="loading()">
	@if (loading()) {
	<hlm-spinner />
	} 保存
</button>

<!-- 布局：gap，而不是 space-*；当宽度等于高度时使用 size-* -->
<div class="flex items-center gap-2">
	<span hlmBadge variant="secondary">beta</span>
</div>
```

## 组件选择

| 需求                   | 组件                                                                                |
| ---------------------- | ----------------------------------------------------------------------------------- |
| 操作 / 按钮            | `button` (`hlmBtn`), `button-group`                                                |
| 文本/数字输入          | `input`, `textarea`, `input-otp`, `input-group`, `native-select`                     |
| 选择输入              | `select`, `combobox`, `autocomplete`, `radio-group`, `checkbox`, `switch`, `slider` |
| 切换 2-7 个选项       | `toggle-group`                                                                      |
| 表单布局/验证          | `field`, `label`                                                                    |
| 数据显示              | `chart`, `table`, `card`, `badge`, `avatar`, `kbd`, `item`                          |
| 导航                  | `sidebar`, `navigation-menu`, `breadcrumb`, `tabs`, `pagination`                   |
| 覆盖层                | `dialog`, `sheet`, `alert-dialog`, `popover`, `hover-card`, `tooltip`                |
| 菜单                  | `dropdown-menu`, `context-menu`, `menubar`, `command`                              |
| 反馈                  | `sonner` (toast), `alert`, `progress`, `skeleton`, `spinner`                        |
| 布局/容器             | `card`, `separator`, `resizable`, `scroll-area`, `accordion`, `collapsible`, `aspect-ratio` |
| 空状态                | `empty`                                                                            |
| 日期                  | `calendar`, `date-picker`                                                            |
| 图标                  | `icon` (`@ng-icons`)                                                                |
| 字体排版              | `typography`                                                                        |

## 工作流程

1. **获取上下文。** 运行 `@spartan-ng/cli:info --json`。如果项目尚未设置，运行 `:init`，然后使用 `:ui` 添加组件（第一个 `:ui` 运行会创建 `components.json`）。
2. **检查已安装的内容。** 不要重新添加 `installedComponents` 中的任何内容。
3. **查找组件。** 使用 MCP 工具或 `https://www.spartan.ng/components/<name>` 查找 API 和示例（见 `mcp.md`）。永远不要猜测选择器 - 确认它们。
4. **添加它。** `npx nx g @spartan-ng/cli:ui --name=<component>`（Nx）或 `ng g @spartan-ng/cli:ui --name=<component>`（Angular CLI）。这将安装 Brain 依赖项并复制 Helm 代码。省略 `--name` 以获取交互式多选。
5. **正确组合。** 导入 `*Imports` 常量（例如 `HlmDialogImports`）或从导入别名导入单个类，将它们添加到独立组件的 `imports` 中，并遵循组合规则。
6. **注册图标。** 您使用的任何 `<ng-icon>` 都必须传递给 `provideIcons(...)`（见 `rules/icons.md`）。
7. **验证。** 在进行较大更改或升级后，运行 `@spartan-ng/cli:healthcheck` 以捕获弃用的模式和修复导入。
8. **主题化/自定义。** 编辑复制的 Helm 文件和 CSS 变量；不要分支 Brain。

## 快速参考

```bash
# 初始化（创建 components.json，连接 Tailwind + 预设）
npx nx g @spartan-ng/cli:init
ng g @spartan-ng/cli:init

# 项目上下文作为 JSON
npx nx g @spartan-ng/cli:info --json

# 添加组件（交互式，或传递 --name）
npx nx g @spartan-ng/cli:ui
npx nx g @spartan-ng/cli:ui --name=dialog

# 生成主题变量
npx nx g @spartan-ng/cli:ui-theme

# 扫描 + 自动修复升级后的弃用 API/导入
npx nx g @spartan-ng/cli:healthcheck --autoFix
```
