# UI 组件

使用 shadcn/ui 和 Radix Primitives 构建 可访问性 UI 组件库 的模式，作为对原生文档的薄层封装：快速入门配方、关键决策、反模式以及房屋差异。供应商机制（CVA 变体、cn() 工具、组件扩展、asChild 组合、对话框/菜单模式、数据属性样式）是上游的工作；参见 [上游覆盖（不要重述）](#upstream-coverage-do-not-restate)。每个剩余类别在 `rules/` 中都有单独的规则文件，按需加载。

## 快速参考

| 类别 | 规则 | 影响 | 使用场景 |
|------|-------|--------|-------------|
| [shadcn/ui](#shadcnui) | 1 | 高 | v4 样式、预设代码、样式检测 |
| [设计系统](#design-system) | 4 | 高 | W3C 令牌、OKLCH 主题、间距比例、排版、组件状态、动画 |
| [设计系统组件](#design-system-components) | 1 | 高 | 原子设计、CVA 变体、可访问性、Storybook |
| [表单](#forms) | 2 | 高 | React Hook Form v7、Zod 验证、服务器操作 |
| [现代 CSS & 工具](#modern-css--tooling) | 3 | 高 | CSS 级联层、Tailwind v4、Storybook CSF3 |
| [UX 基础](#ux-foundations) | 4 | 高 | 视觉层次结构、排版阈值、色彩系统、空状态 |

**总计：6 个类别中的 15 条规则。** Radix 原语机制和 shadcn 自定义教程由原生文档记录；参见 [上游覆盖（不要重述）](#upstream-coverage-do-not-restate) 和 [references/ork-delta.md](references/ork-delta.md) 了解哪些属于我们。

## 快速入门

```tsx
// 使用 CVA 变体系统和 cn() 工具
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground',
        outline: 'border border-input bg-background hover:bg-accent',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 px-3',
        lg: 'h-11 px-8',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  }
)
```

```tsx
// 使用 Radix Dialog 的 asChild 组合
import { Dialog } from 'radix-ui'

<Dialog.Root>
  <Dialog.Trigger asChild>
    <Button>打开</Button>
  </Dialog.Trigger>
  <Dialog.Portal>
    <Dialog.Overlay className="fixed inset-0 bg-black/50" />
    <Dialog.Content className="data-[state=open]:animate-in">
      <Dialog.Title>标题</Dialog.Title>
      <Dialog.Description>描述</Dialog.Description>
      <Dialog.Close>关闭</Dialog.Close>
    </Dialog.Content>
  </Dialog.Portal>
</Dialog.Root>
```

## shadcn/ui

基于 CVA 变体、cn() 工具和 OKLCH 主题构建的精美设计、可访问性组件。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| v4 样式 | `rules/shadcn-v4-styles.md` | 6 种样式（Vega→Luma）、预设代码、样式检测、类映射 |

自定义、表单和数据表格的逐步指南现由上游负责；参见 [上游覆盖（不要重述）](#upstream-coverage-do-not-restate)。我们在它们之上的约定记录在 [references/ork-delta.md](references/ork-delta.md) 中。

### v4 样式系统

shadcn CLI v4 提供 6 种视觉样式。每个都会重写组件类名——不仅仅是 CSS 变量。

| 样式 | 特征 | 最适合 |
|-------|-----------|----------|
| **Vega** | 平衡的半径、干净的线条 | 通用（New York 的继任者） |
| **Nova** | 紧凑的内边距、减少的边距 | 密集的仪表板、管理面板 |
| **Maia** | 柔和的、圆角的、宽大的间距 | 面向消费者、友好的应用程序 |
| **Lyra** | 尖锐的、零半径、等宽字体对 | 编辑器、开发者工具 |
| **Mira** | 超紧凑、极简的装饰 | 电子表格、数据密集型界面 |
| **Luma** | 极端圆角（`rounded-4xl`）、柔和的阴影（`shadow-md` + ring）、呼吸式布局 | 精致的原生应用感、受 macOS Tahoe 启发的 |

在 [ui.shadcn.com/create](https://ui.shadcn.com/create) 上进行视觉配置 → 选择样式、主题、字体、图标，然后复制生成的命令。**不要在文档中硬编码预设代码**——它们与特定的样式快照绑定，可能会漂移。

### shadcn CLI v4 (2026 年 4 月) — 新命令

| 命令 | 目的 |
|---------|---------|
| `npx shadcn@latest apply <style>` | 将已发布的样式（例如 `luma`、`nova`、`lyra`）应用到当前项目——无需重新添加即可重新样式化现有组件 |
| `npx shadcn@latest info` | 显示解析的配置：注册表、样式、令牌、组件存在、Tailwind 版本 |
| `npx shadcn@latest skills` | 列出 `shadcn/skills` 注册表——Claude Code-和 Cursor-就绪的技能包，捆绑了 CLI 命令和代理指导 |
| `npx shadcn@latest build` | 构建自定义注册表（已记录的）——与 `apply` 配合使用以交付私有样式 |

**检测：** 读取 `components.json` → `"style"` 字段（例如 `"radix-luma"`、`"base-nova"`）。旧的 `"new-york"` 和 `"default"` 样式已被 Vega 取代。

## 关键决策

| 决策 | 建议 |
|----------|----------------|
| 色彩格式 | OKLCH 用于感知均匀的主题 |
| 类合并 | 始终使用 cn() 解决 Tailwind 冲突 |
| 扩展组件 | 封装而不是修改源文件 |
| 变体 | 使用 CVA 进行类型安全的多轴变体 |
| 样式方法 | 数据属性 + Tailwind 任意变体 |
| 组合 | 使用 `asChild` 避免包装 div |
| 动画 | 仅 CSS 与数据状态选择器 |
| 表单组件 | 与 react-hook-form 结合 |
| 破坏性确认 | AlertDialog，永远不要使用普通的 Dialog（参见 [references/ork-delta.md](references/ork-delta.md)） |

## 反模式（禁止）

- **修改 shadcn 源代码**：封装和扩展而不是编辑生成的文件
- **跳过 cn()**：直接字符串连接会导致 Tailwind 类冲突
- **CVA 上的内联样式**：使用 CVA 进行类型安全、可重用的变体
- **包装 div**：使用 `asChild` 避免额外的 DOM 元素
- **缺少 Dialog.Title**：每个对话框都必须有一个可访问的标题
- **正向 tabindex**：使用 `tabindex > 0` 会破坏自然的 Tab 顺序
- **仅色彩状态**：使用数据属性 + 多个指示器
- **手动焦点管理**：使用 Radix 内置的焦点捕获

## 上游覆盖（不要重述）

这些主题已于 2026 年 7 月 31 日从本技能中移除，因为有一个原生源拥有它们。将会话指向源；在这里保留楼层、疤痕和房屋决策（它们位于 [references/ork-delta.md](references/ork-delta.md) 中）。

| 主题 | 原生源 |
|-------|--------------------|
| shadcn 设置、初始化清单、添加组件 | vercel:shadcn（市场技能）、https://ui.shadcn.com/docs/installation |
| shadcn 自定义、CVA 变体、cn() 工具、组件扩展 | vercel:shadcn（市场技能）、https://ui.shadcn.com/docs 和 https://cva.style/docs |
| OKLCH 主题变量、亮/暗 CSS 变量集 | https://ui.shadcn.com/docs/theming |
| 使用 next-themes 的暗模式切换 | https://ui.shadcn.com/docs/dark-mode 和 https://github.com/pacocoursey/next-themes |
| 使用 TanStack Table 的数据表格 | https://ui.shadcn.com/docs/components/data-table 和 https://tanstack.com/table |
| 表单字段包装和验证状态 | https://ui.shadcn.com/docs/components/form |
| Radix Dialog 和 AlertDialog 模式 | https://www.radix-ui.com/primitives/docs/components/dialog 和 .../components/alert-dialog |
| Radix asChild / 插槽组合 | https://www.radix-ui.com/primitives/docs/guides/composition |
| Radix 数据属性样式和焦点管理 | https://www.radix-ui.com/primitives/docs/guides/styling |
| 下拉菜单、弹出框、工具提示、悬停卡片 | https://www.radix-ui.com/primitives/docs/components/dropdown-menu（以及兄弟组件页面） |
| Radix 可访问性审计清单 | https://www.radix-ui.com/primitives/docs/overview/accessibility 加上 `ork:accessibility` |

## 详细文档

| 资源 | 描述 |
|----------|-------------|
| [scripts/](scripts/) | 模板：CVA 组件、扩展按钮、对话框、下拉菜单、主题 CSS |
| [references/ork-delta.md](references/ork-delta.md) | Ork 楼层、疤痕和房屋决策，保留在原生文档之外 |

## 设计系统

设计令牌架构、间距、排版和交互式组件状态。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 令牌架构 | `rules/design-system-tokens.md` | W3C 令牌、OKLCH 颜色、Tailwind @theme |
| 间距比例 | `rules/design-system-spacing.md` | 8px 网格、Tailwind space-1 到 space-12 |
| 排版比例 | `rules/design-system-typography.md` | 字体大小、权重、行高 |
| 组件状态 | `rules/design-system-states.md` | 悬停、焦点、激活、禁用、加载、动画预设 |

## 设计系统组件

原子设计组件架构模式和可访问性。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 组件架构 | `rules/design-system-components.md` | 原子设计、CVA 变体、WCAG 2.1 AA、Storybook |

## 表单

React Hook Form v7 与 Zod 验证和 React 19 服务器操作。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| React Hook Form | `rules/forms-react-hook-form.md` | useForm、字段数组、Controller、向导、文件上传 |
| Zod & 服务器操作 | `rules/forms-validation-zod.md` | Zod 模式、服务器操作、useActionState、异步验证 |

## 现代 CSS & 工具

现代 CSS 模式、Tailwind v4 和 2026 年的组件文档工具。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| CSS 级联层 | `rules/css-cascade-layers.md` | @layer 排序、无特异性的覆盖、第三方隔离 |
| Tailwind v4 | `rules/tailwind-v4-patterns.md` | CSS-优先 @theme、原生容器查询、@max-* 变体 |
| Storybook 文档 | `rules/storybook-component-docs.md` | CSF3 故事、play() 交互测试、Chromatic 可视回归 |

## UX 基础

基于认知科学 UI/UX 原则，为生产级界面提供具体的数值阈值。

| 规则 | 文件 | 关键模式 |
|------|------|-------------|
| 视觉层次结构 | `rules/visual-hierarchy.md` | 按钮层级、弱化、F/Z 扫描、Von Restorff、邻近性、最大宽度 |
| 排版阈值 | `rules/typography-thresholds.md` | 65ch 行长度、1.4–1.6 行高、rem 单位、模块化类型比例 |
| 色彩系统 | `rules/color-system.md` | OKLCH 9 色调比例、语义类别、无纯黑色、品牌色调的中性色 |
| 空状态 | `rules/empty-states.md` | 骨架优先、图标 + 标题 + 描述 + CTA、特定原因的语气 |

## 相关技能

- `ork:accessibility` - WCAG 合规性和 React Aria 模式
- `ork:testing-unit` - 组件测试模式
