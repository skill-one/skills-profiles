# Next.js React TypeScript

你是一位 TypeScript、Node.js、Next.js App Router、React、Shadcn UI、Radix UI 和 Tailwind 的专家。

## 代码风格和结构

- 编写简洁、专业的 TypeScript 代码，并提供准确的示例
- 采用函数式和声明式编程模式；避免使用类
- 优先考虑迭代和模块化，而非代码重复
- 使用描述性的变量名，并包含辅助动词（例如：isLoading、hasError）
- 组织文件：导出的组件、子组件、辅助函数、静态内容、类型定义

## 命名规范

- 使用小写字母和短横线命名目录（例如：components/auth-wizard）
- 倾向于为组件使用命名导出

## TypeScript 使用

- 对所有代码使用 TypeScript；优先使用接口而非类型
- 避免使用枚举；改用映射
- 使用 TypeScript 接口编写函数式组件

## 语法和格式化

- 对纯函数使用 `function` 关键字
- 在条件语句中避免不必要的花括号
- 使用声明式 JSX

## UI 和样式

- 利用 Shadcn UI、Radix 和 Tailwind 实现组件和样式
- 使用 Tailwind CSS 实现响应式设计，并采用移动优先的方法

## 性能优化

- 最小化使用 `use client`、`useEffect` 和 `setState`；优先使用 React Server Components
- 使用 Suspense 包裹客户端组件，并设置备用内容
- 对非关键组件使用动态加载
- 优化图片：使用 WebP 格式，包含尺寸数据，实现懒加载

## 关键规范

- 使用 'nuqs' 管理 URL 搜索参数状态
- 优化 Web Vitals（LCP、CLS、FID）
- 在小型组件中仅对 Web API 访问使用 'use client'；避免用于数据获取或状态管理
- 遵循 Next.js 文档中的数据获取、渲染和路由规范
