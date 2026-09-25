# UI样式技能

创建美观、可访问的用户界面综合技能，结合shadcn/ui组件、Tailwind CSS实用样式和基于画布的视觉设计系统。

## 参考

- shadcn/ui: https://ui.shadcn.com/llms.txt
- Tailwind CSS: https://tailwindcss.com/docs

## 何时使用此技能

使用时：
- 使用基于React的框架（Next.js、Vite、Remix、Astro）构建UI
- 实现可访问的组件（对话框、表单、表格、导航）
- 使用实用优先的CSS方法进行样式设置
- 创建响应式、移动优先的布局
- 实现暗黑模式和主题定制
- 构建具有一致令牌的设计系统
- 生成视觉设计、海报或品牌材料
- 快速原型设计，提供即时视觉反馈
- 添加复杂的UI模式（数据表格、图表、命令面板）

## 核心技术栈

### 组件层：shadcn/ui
- 通过Radix UI原语提供的预构建可访问组件
- 复制粘贴分发模式（组件存在于您的代码库中）
- TypeScript优先，提供完整的类型安全
- 可组合原语，用于构建复杂UI
- 基于CLI的安装和管理

### 样式层：Tailwind CSS
- 实用优先的CSS框架
- 构建时处理，无运行时开销
- 移动优先的响应式设计
- 一致的设计令牌（颜色、间距、排版）
- 自动死代码消除

### 视觉设计层：画布
- 博物馆级视觉构图
- 以哲学驱动的设计方法
- 复杂的视觉传达
- 最少文字，最大视觉冲击力
- 系统化模式和精致美学

## 脚本路径

此技能及其`references/`中的脚本路径相对于包含此SKILL.md的目录，而不是项目：`scripts/<文件>`是此技能自己的`scripts/`文件夹，而`../<技能>/scripts/<文件>`是与它一起安装的兄弟子技能。从该目录（Claude Code在技能加载时报告为技能的基本目录）构建完整路径，并将工作目录保持在项目根目录——脚本相对于它读取和写入项目文件，例如`docs/品牌指南.md`、`assets/设计令牌.json`或`src/`。

## 快速入门

### 组件+样式设置

**使用Tailwind安装shadcn/ui：**
```bash
npx shadcn@latest init
```

CLI会提示框架、TypeScript、路径和主题偏好。这会配置shadcn/ui和Tailwind CSS。

**添加组件：**
```bash
npx shadcn@latest add button card dialog form
```

**使用实用样式组件：**
```tsx
import { Button } from "@/components/ui/button"
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card"

export function Dashboard() {
  return (
    <div className="container mx-auto p-6 grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      <Card className="hover:shadow-lg transition-shadow">
        <CardHeader>
          <CardTitle className="text-2xl font-bold">分析</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-muted-foreground">查看您的指标</p>
          <Button variant="default" className="w-full">
            查看详情
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 替代方案：仅Tailwind设置

**Vite项目：**
```bash
npm install -D tailwindcss @tailwindcss/vite
```

```javascript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
export default { plugins: [tailwindcss()] }
```

```css
/* src/index.css */
@import "tailwindcss";
```

## 组件库指南

**包含使用模式、安装和组合示例的全面组件目录。**

参见：`references/shadcn-components.md`

涵盖：
- 表单和输入组件（Button、Input、Select、Checkbox、日期选择器、表单验证）
- 布局和导航（Card、Tabs、Accordion、导航菜单）
- 覆盖和对话框（Dialog、Drawer、Popover、Toast、Command）
- 反馈和状态（Alert、Progress、Skeleton）
- 显示组件（Table、数据表格、Avatar、Badge）

## 主题和定制

**主题配置、CSS变量、暗黑模式实现和组件定制。**

参见：`references/shadcn-theming.md`

涵盖：
- 使用next-themes设置的暗黑模式
- CSS变量系统
- 颜色定制和调色板
- 组件变体定制
- 主题切换实现

## 可访问性模式

**ARIA模式、键盘导航、屏幕阅读器支持和可访问组件使用。**

参见：`references/shadcn-accessibility.md`

涵盖：
- Radix UI可访问性功能
- 键盘导航模式
- 聚焦管理
- 屏幕阅读器公告
- 表单验证可访问性

## Tailwind实用工具

**布局、间距、排版、颜色、边框和阴影的核心实用类。**

参见：`references/tailwind-utilities.md`

涵盖：
- 布局实用工具（Flexbox、Grid、定位）
- 间距系统（padding、margin、gap）
- 排版（字体大小、权重、对齐、行高）
- 颜色和背景
- 边框和阴影
- 用于自定义样式的任意值

## 响应式设计

**移动优先断点、响应式实用工具和自适应布局。**

参见：`references/tailwind-responsive.md`

涵盖：
- 移动优先方法
- 断点系统（sm、md、lg、xl、2xl）
- 响应式实用工具模式
- 容器查询
- 最大宽度查询
- 自定义断点

## Tailwind定制

**配置文件结构、自定义实用工具、插件和主题扩展。**

参见：`references/tailwind-customization.md`

涵盖：
- 用于自定义令牌的@theme指令
- 自定义颜色和字体
- 间距和断点扩展
- 自定义实用工具创建
- 自定义变体
- 层级组织（@layer base、components、utilities）
- 用于组件提取的Apply指令

## 视觉设计系统

**基于画布的设计哲学、视觉传达原则和复杂构图。**

参见：`references/canvas-design-system.md`

涵盖：
- 设计哲学方法
- 视觉传达优于文字
- 系统化模式和构图
- 颜色、形状和空间设计
- 最少文字集成
- 博物馆级执行
- 多页设计系统

## 实用脚本

**用于组件安装和配置生成的Python自动化。**

### shadcn_add.py
使用依赖管理添加shadcn/ui组件：
```bash
python scripts/shadcn_add.py button card dialog
```

### tailwind_config_gen.py
使用自定义主题生成tailwind.config.js：
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --fonts display:Inter
```

生成器在存在任何兄弟`tailwind.config.js`、`.cjs`、`.mjs`或`.ts`文件时拒绝创建或替换配置。首先查看报告的配置，然后仅在竞争输出是故意时才传递`--force`：
```bash
python scripts/tailwind_config_gen.py --colors brand:blue --force
```

## 最佳实践

1. **组件组合**：从简单的可组合原语构建复杂UI
2. **实用优先样式**：直接使用Tailwind类；仅当真正重复时才提取组件
3. **移动优先响应式**：从移动样式开始，分层响应式变体
4. **可访问性优先**：利用Radix UI原语，添加聚焦状态，使用语义HTML
5. **设计令牌**：使用一致的间距比例、颜色调色板、排版系统
6. **暗黑模式一致性**：对所有主题元素应用暗黑变体
7. **性能**：利用自动CSS清除，避免动态类名
8. **TypeScript**：使用完整的类型安全以获得更好的DX
9. **视觉层次**：让组合引导注意力，有意使用间距和颜色
10. **专家工艺**：每个细节都很重要——将UI视为一门工艺

## 参考导航

**组件库**
- `references/shadcn-components.md` - 完整组件目录
- `references/shadcn-theming.md` - 主题和定制
- `references/shadcn-accessibility.md` - 可访问性模式

**样式系统**
- `references/tailwind-utilities.md` - 核心实用工具类
- `references/tailwind-responsive.md` - 响应式设计
- `references/tailwind-customization.md` - 配置和扩展

**视觉设计**
- `references/canvas-design-system.md` - 设计哲学和画布工作流

**自动化**
- `scripts/shadcn_add.py` - 组件安装
- `scripts/tailwind_config_gen.py` - 配置生成

## 常见模式

**带验证的表单：**
```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormField, FormItem, FormLabel, FormControl, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

const schema = z.object({
  email: z.string().email(),
  password: z.string().min(8)
})

export function LoginForm() {
  const form = useForm({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" }
  })

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(console.log)} className="space-y-6">
        <FormField control={form.control} name="email" render={({ field }) => (
          <FormItem>
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="email" {...field} />
            </FormControl>
            <FormMessage />
          </FormItem>
        )} />
        <Button type="submit" className="w-full">登录</Button>
      </form>
    </Form>
  )
}
```

**带暗黑模式的响应式布局：**
```tsx
<div className="min-h-screen bg-white dark:bg-gray-900">
  <div className="container mx-auto px-4 py-8">
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <Card className="bg-white dark:bg-gray-800 border-gray-200 dark:border-gray-700">
        <CardContent className="p-6">
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
            内容
          </h3>
        </CardContent>
      </Card>
    </div>
  </div>
</div>
```

## 资源

- shadcn/ui文档：https://ui.shadcn.com
- Tailwind CSS文档：https://tailwindcss.com
- Radix UI：https://radix-ui.com
- Tailwind UI：https://tailwindui.com
- Headless UI：https://headlessui.com
- v0（AI UI生成器）：https://v0.dev
