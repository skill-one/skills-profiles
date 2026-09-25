# 代码规范

## 核心技术
- **前端:** ReactJS, Next.js (App Router 结构), TypeScript
- **样式:** TailwindCSS v3.x (绝不使用 v4), Shadcn UI
- **构建工具:** Vite (在适用情况下)
- **后端:** Postgres 兼容的 convex.dev 或 Supabase (始终询问，绝不使用本地 Postgres)
- **部署:** Netlify 或 Vercel 或 Fly - 推荐
- **环境:** Mac M2, Python3 配合虚拟环境, 无 CUDA, 无 Docker
- **替代语言:** 尽量避免 Python, 尝试使用 RUST

## 代码风格与结构
- 使用 ES 模块 (import/export) 语法
- 尽可能解构导入
- 所有新代码使用 TypeScript
- 使用 async/await 而非 Promise 链
- 倾向于 const/let 而非 var; 使用早期返回
- 使用 const 而非函数: `const toggle = () =>`。定义类型。
- 使用描述性变量名并搭配辅助动词 (例如, `isLoading`, `hasError`)
- 目录名使用小写和短横线 (例如, `components/auth-wizard`)

## 框架规范
- **Next.js:** 使用 App Router (app 目录) 结构和 page.tsx 文件
- **React:** 函数式和声明式模式; 避免 class
- **状态管理:** Zustand, TanStack React Query
- **验证:** Zod 用于模式验证

## 组件库与样式
- **组件库:** 优先使用 `@/components/ui` 的 shadcn 组件
- **样式:** Tailwind 工具类
- **布局:** 使用带 `gap` 的 Grid/flex 包装器进行间距控制
- **图标:** `@phosphor-icons/react`
- **提示框:** `sonner` 用于通知
- 始终添加加载状态、加载动画、占位符动画

## 质量保证与测试
- **TDD:** 先编写失败的测试, 提交它们, 然后迭代直到测试套件通过
- 绝不模拟测试 - 如果有测试脚本, 执行所有测试直到完成
- 始终分块编写 SQL, 每块后添加测试步骤
- 代码变更后进行类型检查
- 提交前运行测试
- 倾向于运行单个测试而非整个测试套件以提升性能

## 错误处理
- 实现适当的错误处理和用户输入验证
- 错误信息应让非技术人员理解
- 使用早期返回处理错误情况
- 先通过 curl 命令测试 API, 然后在代码中实现

## 性能与架构
- 最小化 `'use client'`, `useEffect`, `setState`; 优先使用 RSC 和 Next.js SSR
- 实现动态导入进行代码拆分
- 优化图片: WebP 格式, 大小数据, 懒加载
- 倾向于小型、简单、命名清晰的模块

## 开发流程
**流程:** 探索 → 规划 → 编码 → 提交
- 阅读相关文件
- 制定计划
- 实现
- 然后提交
- 绝不使用本地后端, 始终询问 (通常使用 Supabase, Neon)
- 最小依赖, 无 Docker

## 环境与部署
- 为 API 密钥添加 .env 文件; 提醒我在 Vercel/Netlify 环境变量中保存密钥
- 编写可部署到 Netlify 或 Vercel 的代码; 首先准备本地构建
- 在 progress.md 中记录进度; 询问实现计划
