# shadcn/ui 组件

将 shadcn/ui 组件添加到主题化的 React 项目中。此技能在 `tailwind-theme-builder` 设置 CSS 变量、ThemeProvider 和暗黑模式之后运行。它处理组件安装、定制以及将组件组合成可工作的模式。

**前提条件**：主题基础设施必须存在（CSS 变量、components.json、cn() 工具）。如果尚未设置，请先使用 `tailwind-theme-builder`。

## 安装顺序

按依赖顺序安装组件。首先安装基础组件，然后安装功能组件：

### 基础组件（首先安装）

```bash
pnpm dlx shadcn@latest add button
pnpm dlx shadcn@latest add input label
pnpm dlx shadcn@latest add card
```

### 功能组件（按需安装）

```bash
# 表单
pnpm dlx shadcn@latest add form        # 需要：react-hook-form, zod, @hookform/resolvers
pnpm dlx shadcn@latest add textarea select checkbox switch

# 反馈
pnpm dlx shadcn@latest add toast        # 需要：sonner
pnpm dlx shadcn@latest add alert badge

# 覆盖层
pnpm dlx shadcn@latest add dialog sheet popover dropdown-menu

# 数据展示
pnpm dlx shadcn@latest add table        # 用于数据表格，也：@tanstack/react-table
pnpm dlx shadcn@latest add tabs separator avatar

# 导航
pnpm dlx shadcn@latest add navigation-menu command
```

### 外部依赖

| 组件 | 需要 |
|-----------|----------|
| 表单 | `react-hook-form`, `zod`, `@hookform/resolvers` |
| Toast | `sonner` |
| 数据表格 | `@tanstack/react-table` |
| Command | `cmdk` |
| 日期选择器 | `date-fns` (可选) |

单独安装外部依赖：`pnpm add react-hook-form zod @hookform/resolvers`

## 已知注意事项

这些是文档中记录的修正，可防止常见错误：

### Radix Select — 不使用空字符串

```tsx
// 不要使用空字符串值
<SelectItem value="">All</SelectItem>           // BREAKS

// 使用哨兵值
<SelectItem value="__any__">All</SelectItem>    // WORKS
const actual = value === "__any__" ? "" : value
```

### React Hook Form — 空值

```tsx
// 不要展开 {...field} — 它传递 null，Input 会拒绝
<Input
  value={field.value ?? ''}
  onChange={field.onChange}
  onBlur={field.onBlur}
  name={field.name}
  ref={field.ref}
/>
```

### Lucide Icons — 拆卸

```tsx
// 不要使用动态导入 — 图标在生产环境中会被拆卸
import * as LucideIcons from 'lucide-react'
const Icon = LucideIcons[iconName]  // BREAKS in prod

// 使用显式映射
import { Home, Users, Settings, type LucideIcon } from 'lucide-react'
const ICON_MAP: Record<string, LucideIcon> = { Home, Users, Settings }
const Icon = ICON_MAP[iconName]
```

### 对话框宽度覆盖

```tsx
// 默认 sm:max-w-lg 不会被 max-w-6xl 覆盖
<DialogContent className="max-w-6xl">       // DOESN'T WORK

// 使用相同的断点前缀
<DialogContent className="sm:max-w-6xl">    // WORKS
```

## 定制组件

shadcn 组件使用主题中的语义 CSS 令牌。要定制：

### 变体扩展

通过编辑 `src/components/ui/` 中的组件文件添加自定义变体：

```tsx
// button.tsx — 添加 "brand" 变体
const buttonVariants = cva("...", {
  variants: {
    variant: {
      default: "bg-primary text-primary-foreground",
      brand: "bg-brand text-brand-foreground hover:bg-brand/90",
      // ... 现有变体
    },
  },
})
```

### 颜色覆盖

使用主题中的语义令牌 — 永远不要使用原始的 Tailwind 颜色：

```tsx
// 不要使用原始颜色
<Button className="bg-blue-500">             // WRONG

// 使用语义令牌
<Button className="bg-primary">              // RIGHT
<Card className="bg-card text-card-foreground">  // RIGHT
```

## 工作流程

### 第一步：评估需求

确定项目需要哪些 UI 模式：

| 需求 | 组件 |
|------|-----------|
| 带验证的表单 | Form, Input, Label, Select, Textarea, Button, Toast |
| 带排序的数据展示 | Table, Badge, Pagination |
| 管理员 CRUD 界面 | Dialog, Form, Table, Button, Toast |
| 营销/着陆页 | Card, Button, Badge, Separator |
| 设置/偏好设置 | Tabs, Form, Switch, Select, Toast |
| 导航 | NavigationMenu (桌面), Sheet (移动), ModeToggle |

### 第二步：安装组件

首先安装基础组件，然后为已识别的需求安装功能组件。使用上述命令。

### 第三步：构建配方

将组件组合成可工作的模式。参见 [references/recipes.md](references/recipes.md) 获取完整的可工作示例：

- **联系表单** — Form + Input + Textarea + Button + Toast
- **数据表格** — Table + 列排序 + Pagination + 搜索
- **模态 CRUD** — Dialog + Form + Button
- **导航** — Sheet + NavigationMenu + ModeToggle
- **设置页面** — Tabs + Form + Switch + Select + Toast

### 第四步：定制

使用主题中的语义令牌应用项目特定的颜色和变体。

## 参考文件

| 当... | 阅读 |
|------|------|
| 选择组件、安装命令、属性 | [references/component-catalogue.md](references/component-catalogue.md) |
| 构建完整的 UI 模式 | [references/recipes.md](references/recipes.md) |
