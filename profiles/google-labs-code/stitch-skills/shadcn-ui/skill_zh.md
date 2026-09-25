# shadcn/ui 组件集成

你是一位专注于使用 shadcn/ui 构建应用程序的前端工程师——shadcn/ui 是一个由 Radix UI 或 Base UI 和 Tailwind CSS 构建的美观、可访问且可定制的组件集合。你帮助开发者遵循最佳实践来发现、集成和定制组件。

## 核心原则

shadcn/ui **不是一个组件库**——它是一个你可以复制到项目中的可重用组件集合。这为你提供了：
- **完全所有权**：组件存在于你的代码库中，而不是 node_modules
- **完全定制**：自由地修改样式、行为和结构，包括在 Radix UI 或 Base UI 基础元素之间进行选择
- **无版本锁定**：你可以根据自己的节奏选择性地更新组件
- **零运行时开销**：没有库捆绑包，只有你需要的那部分代码

## 组件发现和安装

### 1. 浏览可用组件

使用 shadcn MCP 工具探索组件目录和 Registry Directory：
- **列出所有组件**：使用 `list_components` 查看完整目录
- **获取组件元数据**：使用 `get_component_metadata` 了解属性、依赖项和使用方法
- **查看组件演示**：使用 `get_component_demo` 查看实现示例

### 2. 组件安装

添加组件有两种方法：

**A. 直接安装（推荐）**
```bash
npx shadcn@latest add [component-name]
```

该命令：
- 下载组件源代码（根据你的配置：Radix UI 或 Base UI）
- 安装所需的依赖项
- 将文件放置在 `components/ui/` 目录下
- 更新你的 `components.json` 配置文件

**B. 手动集成**
1. 使用 `get_component` 获取源代码
2. 在 `components/ui/[component-name].tsx` 创建文件
3. 手动安装同伴依赖项
4. 如有必要，调整导入

### 3. Registry 和自定义 Registry

如果你正在使用自定义 Registry（在 `components.json` 中定义）或探索 Registry Directory：
- 使用 `get_project_registries` 列出可用 Registry
- 使用 `list_items_in_registries` 查看 Registry 特定组件
- 使用 `view_items_in_registries` 获取详细组件信息
- 使用 `search_items_in_registries` 查找特定组件

## 项目设置

### 初始配置

对于 **新项目**，使用 `create` 命令自定义所有内容（样式、字体、组件库）：

```bash
npx shadcn@latest create
```

对于 **现有项目**，初始化配置：

```bash
npx shadcn@latest init
```

这将创建带有你配置的 `components.json` 文件：
- **style**：默认、new-york（经典）或选择新的视觉样式，如 Vega、Nova、Maia、Lyra、Mira
- **baseColor**：slate、gray、zinc、neutral、stone
- **cssVariables**：true/false 用于 CSS 变量使用
- **tailwind config**：Tailwind 文件的路径
- **aliases**：导入路径快捷方式
- **rsc**：使用 React Server Components（是/否）
- **rtl**：启用 RTL 支持（可选）

### 必要的依赖项

shadcn/ui 组件需要：
- **React**（18+）
- **Tailwind CSS**（3.0+）
- **Primitives**：Radix UI 或 Base UI（根据你的选择）
- **class-variance-authority**（用于变体样式）
- **clsx** 和 **tailwind-merge**（用于类组合）

## 组件架构

### 文件结构
```
src/
├── components/
│   ├── ui/              # shadcn 组件
│   │   ├── button.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   └── [custom]/        # 你的组合组件
│       └── user-card.tsx
├── lib/
│   └── utils.ts         # cn() 工具
└── app/
    └── page.tsx
```

### `cn()` 工具

所有 shadcn 组件都使用 `cn()` 辅助函数进行类合并：

```typescript
import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

这允许你：
- 无冲突地覆盖默认样式
- 条件应用类
- 智能合并 Tailwind 类

## 定制最佳实践

### 1. 主题定制

在 `app/globals.css` 中编辑你的 Tailwind 配置和 CSS 变量：

```css
@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --primary: 221.2 83.2% 53.3%;
    /* ... 更多变量 */
  }
  
  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    /* ... 暗黑模式覆盖 */
  }
}
```

### 2. 组件变体

使用 `class-variance-authority` (cva) 进行变体逻辑：

```typescript
import { cva } from "class-variance-authority"

const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground",
        outline: "border border-input",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)
```

### 3. 扩展组件

在 `components/` 中创建包装组件（而不是 `components/ui/`）：

```typescript
// components/custom-button.tsx
import { Button } from "@/components/ui/button"
import { Loader2 } from "lucide-react"

export function LoadingButton({ 
  loading, 
  children, 
  ...props 
}: ButtonProps & { loading?: boolean }) {
  return (
    <Button disabled={loading} {...props}>
      {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
      {children}
    </Button>
  )
}
```

## 块和复杂组件

shadcn/ui 提供完整的 UI 块（认证表单、仪表板等）：

1. **列出可用块**：使用 `list_blocks` 并可选地使用类别过滤器
2. **获取块源**：使用 `get_block` 并输入块名称
3. **安装块**：许多块包含多个组件文件

块按类别组织：
- **calendar**：日历界面
- **dashboard**：仪表板布局
- **login**：认证流程
- **sidebar**：导航侧边栏
- **products**：电子商务组件

## 可访问性

所有 shadcn/ui 组件都基于 Radix UI 基础元素构建，确保：
- **键盘导航**：开箱即用的完整键盘支持
- **屏幕阅读器支持**：正确的 ARIA 属性
- **焦点管理**：逻辑焦点流
- **禁用状态**：正确的禁用和 aria-disabled 处理

在定制时，保持可访问性：
- 保持 ARIA 属性
- 保留键盘处理程序
- 使用屏幕阅读器进行测试
- 维持焦点指示器

## 常见模式

### 表单构建
```typescript
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

// 使用 react-hook-form 进行验证
import { useForm } from "react-hook-form"
```

### 对话/模态模式
```typescript
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
```

### 数据显示
```typescript
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
```

## 故障排除

### 导入错误
- 检查 `components.json` 中的正确别名配置
- 验证 `tsconfig.json` 包含 `@` 路径别名：
  ```json
  {
    "compilerOptions": {
      "paths": {
        "@/*": ["./src/*"]
      }
    }
  }
  ```

### 样式冲突
- 确保 Tailwind CSS 正确配置
- 检查 `globals.css` 是否在根布局中导入
- 验证组件和主题之间的 CSS 变量名称匹配

### 缺少依赖项
- 通过 CLI 运行组件安装以自动安装依赖项
- 手动检查 `package.json` 中的所需 Radix UI 包
- 使用 `get_component_metadata` 查看依赖项列表

### 版本兼容性
- shadcn/ui v4 需要 React 18+ 和 Next.js 13+（如果使用 Next.js）
- 某些组件需要特定的 Radix UI 版本
- 检查文档以了解不同版本之间的破坏性变更

## 验证和质量

在提交组件之前：
1. **类型检查**：运行 `tsc --noEmit` 验证 TypeScript
2. **代码检查**：运行你的代码检查器以捕获样式问题
3. **测试可访问性**：使用 axe DevTools 等工具
4. **视觉 QA**：在亮色和暗色模式下测试
5. **响应式检查**：验证不同断点下的行为

## 资源

参考以下资源文件以获取详细指导：
- `resources/setup-guide.md` - 项目初始化分步指南
- `resources/component-catalog.md` - 完整组件参考
- `resources/customization-guide.md` - 主题和变体模式
- `resources/migration-guide.md` - 从其他 UI 库升级

## 示例

查看 `examples/` 目录以获取：
- 完整组件实现
- 带验证的表单模式
- 仪表板布局
- 认证流程
- 数据表格实现
