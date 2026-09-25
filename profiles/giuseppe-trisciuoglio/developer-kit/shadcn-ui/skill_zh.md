# shadcn/ui 组件模式

使用 shadcn/ui、Radix UI 和 Tailwind CSS 构建 可访问、可定制的 UI 组件。

## 概述

- 组件**复制到您的项目中** — 您拥有并自定义代码
- 基于 **Radix UI** 基础元素，实现完全可访问性
- 使用 **Tailwind CSS** 和 CSS 变量进行主题化
- 基于CLI的安装：`npx shadcn@latest add <component>`

## 何时使用

在用户请求涉及以下内容时激活：

- "设置 shadcn/ui"、"初始化 shadcn"、"添加 shadcn 组件"
- "安装按钮/输入/表单/对话框/卡片/选择/提示/表格/图表"
- "React Hook Form"、"Zod 验证"、"带验证的表单"
- "可访问组件"、"Radix UI"、"Tailwind 主题"
- "shadcn 按钮"、"shadcn 对话框"、"shadcn 表单"、"shadcn 表格"
- "暗黑模式"、"CSS 变量"、"自定义主题"
- "带 Recharts 的图表"、"柱状图"、"折线图"、"饼图"

## 快速参考

### 可用组件

| 组件 | 安装命令 | 描述 |
|------|---------|------|
| `button` | `npx shadcn@latest add button` | 变体：默认、破坏性、轮廓、次要、幽灵、链接 |
| `input` | `npx shadcn@latest add input` | 文本输入字段 |
| `form` | `npx shadcn@latest add form` | React Hook Form 集成，带验证 |
| `card` | `npx shadcn@latest add card` | 带有标题、内容和页脚的容器 |
| `dialog` | `npx shadcn@latest add dialog` | 模态覆盖层 |
| `sheet` | `npx shadcn@latest add sheet` | 滑动面板（顶部/右侧/底部/左侧） |
| `select` | `npx shadcn@latest add select` | 下拉选择 |
| `toast` | `npx shadcn@latest add toast` | 提示通知 |
| `table` | `npx shadcn@latest add table` | 数据表格 |
| `menubar` | `npx shadcn@latest add menubar` | 桌面风格菜单栏 |
| `chart` | `npx shadcn@latest add chart` | Recharts 封装，带主题化 |
| `textarea` | `npx shadcn@latest add textarea` | 多行文本输入 |
| `checkbox` | `npx shadcn@latest add checkbox` | 复选框输入 |
| `label` | `npx shadcn@latest add label` | 可访问的表单标签 |

## 说明

### 初始化项目

```bash
# 新 Next.js 项目
npx create-next-app@latest my-app --typescript --tailwind --eslint --app
cd my-app
npx shadcn@latest init

# 现有项目
npm install tailwindcss-animate class-variance-authority clsx tailwind-merge lucide-react
npx shadcn@latest init

# 安装组件
npx shadcn@latest add button input form card dialog select toast
```

### 基本组件使用

```tsx
// 带变体和大小的按钮
import { Button } from "@/components/ui/button"

<Button variant="default">默认</Button>
<Button variant="destructive" size="sm">删除</Button>
<Button variant="outline" disabled>加载中...</Button>
```

### 带Zod验证的表单

```tsx
"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  email: z.string().email("无效的邮箱"),
  password: z.string().min(8, "密码至少需要8个字符"),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "" },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-4">
        <FormField name="email" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>邮箱</FormLabel>
            <FormControl><Input type="email" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField name="password" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>密码</FormLabel>
            <FormControl><Input type="password" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">登录</Button>
      </form>
    </Form>
  )
}
```

参考 [references/forms-and-validation.md](references/forms-and-validation.md) 了解高级多字段表单、带API提交的联系表单和登录卡片模式。

### 对话框（模态）

```tsx
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">打开</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>编辑个人资料</DialogTitle>
    </DialogHeader>
    {/* 内容 */}
  </DialogContent>
</Dialog>
```

### 提示通知

```tsx
// 1. 在 app/layout.tsx 中添加 <Toaster />
import { Toaster } from "@/components/ui/toaster"

// 2. 在组件中使用
import { useToast } from "@/components/ui/use-toast"

const { toast } = useToast()
toast({ title: "成功", description: "更改已保存。" })
toast({ variant: "destructive", title: "错误", description: "发生了一些问题。" })
```

### 柱状图

```tsx
import { Bar, BarChart, CartesianGrid, XAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const chartConfig = {
  desktop: { label: "桌面", color: "var(--chart-1)" },
} satisfies import("@/components/ui/chart").ChartConfig

<ChartContainer config={chartConfig} className="min-h-[200px] w-full">
  <BarChart data={data}>
    <CartesianGrid vertical={false} />
    <XAxis dataKey="month" />
    <Bar dataKey="desktop" fill="var(--color-desktop)" radius={4} />
    <ChartTooltip content={<ChartTooltipContent />} />
  </BarChart>
</ChartContainer>
```

参考 [references/charts-components.md](references/charts-components.md) 了解折线图、区域图和饼图示例。

## 示例

### 带验证的登录表单
```tsx
"use client"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"

const formSchema = z.object({
  email: z.string().email("无效的邮箱"),
  password: z.string().min(8, "至少8个字符"),
})

export function LoginForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { email: "", password: "" },
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-4">
        <FormField name="email" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>邮箱</FormLabel>
            <FormControl><Input type="email" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <FormField name="password" control={form.control} render={({ field }) => (
          <FormItem>
            <FormLabel>密码</FormLabel>
            <FormControl><Input type="password" {...field} /></FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit">登录</Button>
      </form>
    </Form>
  )
}
```

### 带操作的表格
```tsx
import { ColumnDef } from "@tanstack/react-table"
import { Button } from "@/components/ui/button"
import { Checkbox } from "@/components/ui/checkbox"
import { DataTable } from "@/components/ui/data-table"

const columns: ColumnDef<User>[] = [
  { id: "select", header: ({ table }) => (
    <Checkbox checked={table.getIsAllPageRowsSelected()} />
  ), cell: ({ row }) => (
    <Checkbox checked={row.getIsSelected()} />
  )},
  { accessorKey: "name", header: "姓名" },
  { accessorKey: "email", header: "邮箱" },
  { id: "actions", cell: ({ row }) => (
    <Button variant="ghost" size="sm">编辑</Button>
  )},
]
```

### 带表单的对话框
```tsx
import { Button } from "@/components/ui/button"
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog"

<Dialog>
  <DialogTrigger asChild>
    <Button variant="outline">添加用户</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>添加新用户</DialogTitle>
    </DialogHeader>
    {/* <LoginForm /> */}
  </DialogContent>
</Dialog>
```

### 提示通知
```tsx
import { useToast } from "@/components/ui/use-toast"
import { Button } from "@/components/ui/button"

const { toast } = useToast()

toast({ title: "已保存", description: "更改已成功保存。" })
toast({ variant: "destructive", title: "错误", description: "保存失败。" })
```

## 最佳实践

- **可访问性**：使用 Radix UI 基础元素 — ARIA 属性已内置
- **客户端组件**：为交互式组件添加 `"use client"`（钩子、事件）
- **类型安全**：使用 TypeScript 和 Zod 模式进行表单验证
- **主题化**：在 `globals.css` 中配置 CSS 变量以实现一致的设计
- **自定义**：直接修改组件文件 — 您拥有代码
- **路径别名**：确保在 `tsconfig.json` 中配置 `@` 别名
- **注册表安全**：仅从可信注册表安装组件；在生产使用前审查生成的代码
- **暗黑模式**：使用 CSS 变量策略和 `next-themes` 设置
- **表单**：始终使用 `Form`、`FormField`、`FormItem`、`FormLabel`、`FormMessage` 一起
- **Toaster**：在根布局中添加 `<Toaster />` 一次

## 限制和警告

- **不是 NPM 包**：组件复制到您的项目中；它们不是版本化的依赖项
- **注册表安全**：从 `npx shadcn@latest add` 获取的组件是远程获取的；安装前始终验证注册表源是否可信
- **客户端组件**：大多数交互式组件需要 `"use client"` 指令
- **Radix 依赖项**：确保所有 `@radix-ui` 包都已安装
- **Tailwind 必需**：组件依赖 Tailwind CSS 工具
- **路径别名**：在 `tsconfig.json` 中配置 `@` 别名以进行导入

## 参考

查阅这些文件以获取详细的模式和代码示例：

- **[references/setup-and-configuration.md](references/setup-and-configuration.md)** — 完整安装、tsconfig、tailwind 配置、CSS 变量
- **[references/ui-components.md](references/ui-components.md)** — 按钮、输入、卡片、对话框、表单、选择、提示、表格、菜单栏
- **[references/forms-and-validation.md](references/forms-and-validation.md)** — React Hook Form + Zod、高级表单、登录卡片、联系表单
- **[references/charts-components.md](references/charts-components.md)** — 柱状图、折线图、区域图、饼图，带 ChartContainer 和主题化
- **[references/nextjs-integration.md](references/nextjs-integration.md)** — App Router、服务器/客户端组件、暗黑模式、元数据
- **[references/customization.md](references/customization.md)** — 自定义变体、CSS 变量、cn() 工具、扩展组件
