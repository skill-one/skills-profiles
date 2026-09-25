# React/Next.js 开发工作流

## 概述

专门用于使用现代模式（包括 App Router、服务器组件、TypeScript 和 Tailwind CSS）构建 React 和 Next.js 14+ 应用的工作流。

## 何时使用此工作流

当您需要：
- 构建新的 React 应用
- 创建使用 App Router 的 Next.js 14+ 项目
- 实现服务器组件
- 在 React 中设置 TypeScript
- 使用 Tailwind CSS 进行样式设计
- 构建全栈 Next.js 应用

## 工作流阶段

### 阶段 1：项目设置

#### 需要调用的技能
- `app-builder` - 应用程序脚手架
- `senior-fullstack` - 全栈指导
- `nextjs-app-router-patterns` - Next.js 14+ 模式
- `typescript-pro` - TypeScript 设置

#### 操作步骤
1. 选择项目类型（React 单页应用、Next.js 应用）
2. 选择构建工具（Vite、Next.js、Create React App）
3. 搭建项目结构
4. 配置 TypeScript
5. 设置 ESLint 和 Prettier

#### 复制粘贴提示
```
使用 @app-builder 脚手架创建新的 Next.js 14 项目并使用 App Router
```

```
使用 @nextjs-app-router-patterns 设置服务器组件
```

### 阶段 2：组件架构

#### 需要调用的技能
- `frontend-developer` - 组件开发
- `react-patterns` - React 模式
- `react-state-management` - 状态管理
- `react-ui-patterns` - UI 模式

#### 操作步骤
1. 设计组件层级结构
2. 创建基础组件
3. 实现布局组件
4. 设置状态管理
5. 创建自定义钩子

#### 复制粘贴提示
```
使用 @frontend-developer 创建可重用的 React 组件
```

```
使用 @react-patterns 实现正确的组件组合
```

```
使用 @react-state-management 设置 Zustand 存储
```

### 阶段 3：样式和设计

#### 需要调用的技能
- `frontend-design` - UI 设计
- `tailwind-patterns` - Tailwind CSS
- `tailwind-design-system` - 设计系统
- `core-components` - 组件库

#### 操作步骤
1. 设置 Tailwind CSS
2. 配置设计令牌
3. 创建实用类
4. 构建组件样式
5. 实现响应式设计

#### 复制粘贴提示
```
使用 @tailwind-patterns 使用 Tailwind CSS v4 样式化组件
```

```
使用 @frontend-design 创建现代化的仪表板 UI
```

### 阶段 4：数据获取

#### 需要调用的技能
- `nextjs-app-router-patterns` - 服务器组件
- `react-state-management` - React Query
- `api-patterns` - API 集成

#### 操作步骤
1. 实现服务器组件
2. 设置 React Query/SWR
3. 创建 API 客户端
4. 处理加载状态
5. 实现错误边界

#### 复制粘贴提示
```
使用 @nextjs-app-router-patterns 实现服务器组件数据获取
```

### 阶段 5：路由和导航

#### 需要调用的技能
- `nextjs-app-router-patterns` - App Router
- `nextjs-best-practices` - Next.js 模式

#### 操作步骤
1. 设置基于文件的路由
2. 创建动态路由
3. 实现嵌套路由
4. 添加路由守卫
5. 配置重定向

#### 复制粘贴提示
```
使用 @nextjs-app-router-patterns 设置并行路由和拦截路由
```

### 阶段 6：表单和验证

#### 需要调用的技能
- `frontend-developer` - 表单开发
- `typescript-advanced-types` - 类型验证
- `react-ui-patterns` - 表单模式

#### 操作步骤
1. 选择表单库（React Hook Form、Formik）
2. 设置验证（Zod、Yup）
3. 创建表单组件
4. 处理提交
5. 实现错误处理

#### 复制粘贴提示
```
使用 @frontend-developer 使用 React Hook Form 和 Zod 创建表单
```

### 阶段 7：测试

#### 需要调用的技能
- `javascript-testing-patterns` - Jest/Vitest
- `playwright-skill` - E2E 测试
- `e2e-testing-patterns` - E2E 模式

#### 操作步骤
1. 设置测试框架
2. 编写单元测试
3. 创建组件测试
4. 实现E2E 测试
5. 配置 CI 集成

#### 复制粘贴提示
```
使用 @javascript-testing-patterns 编写 Vitest 测试
```

```
使用 @playwright-skill 为关键流程创建 E2E 测试
```

### 阶段 8：构建和部署

#### 需要调用的技能
- `vercel-deployment` - Vercel 部署
- `vercel-deploy-claimable` - Vercel 部署
- `web-performance-optimization` - 性能优化

#### 操作步骤
1. 配置构建设置
2. 优化包大小
3. 设置环境变量
4. 部署到 Vercel
5. 配置预览部署

#### 复制粘贴提示
```
使用 @vercel-deployment 将 Next.js 应用部署到生产环境
```

## 技术栈

| 类别 | 技术 |
|------|------|
| 框架 | Next.js 14+、React 18+ |
| 语言 | TypeScript 5+ |
| 样式 | Tailwind CSS v4 |
| 状态 | Zustand、React Query |
| 表单 | React Hook Form、Zod |
| 测试 | Vitest、Playwright |
| 部署 | Vercel |

## 质量门禁

- [ ] TypeScript 无错误编译
- [ ] 所有测试通过
- [ ] 代码风格检查干净
- [ ] 性能指标达标（LCP、CLS、FID）
- [ ] 无障碍性检查（WCAG 2.1）
- [ ] 响应式设计验证

## 相关工作流包

- `development` - 常规开发
- `testing-qa` - 测试工作流
- `documentation` - 文档
- `typescript-development` - TypeScript 模式

## 限制
- 仅在任务明确匹配上述范围时使用此技能。
- 不要将输出视为环境特定验证、测试或专家评审的替代品。
- 如果缺少必要的输入、权限、安全边界或成功标准，请停止并请求澄清。
