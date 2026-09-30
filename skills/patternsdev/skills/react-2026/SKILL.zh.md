---
name: react-2026
description: 提供一份关于现代 React 2026 技术栈的全面指南。适用于启动新 React 项目或使用当前框架、构建工具、路由、状态管理或 AI 集成来现代化现有项目。
---

# React 框架模式

## 目录

- [何时使用](#何时使用)
- [说明](#说明)
- [详情](#详情)
- [来源](#来源)

React 自从早期简单的组件库时代已经走了很长一段路。到 2025 年底，React 生态系统**丰富但复杂**，提供了多种选择来构建应用程序的堆栈。现代 React 开发者面临着在堆栈的每一层做出选择，从**构建工具**和**框架**到**路由器**和其他库。官方 React 文档（现在在 **react.dev**）鼓励为新项目使用更高级别的框架。事实上，**Create React App (CRA)** - 曾经是首选的启动工具 - 在 2025 年初被弃用，标志着我们开始 React 应用的方式发生了转变。

与其从零开始拼接自己的工具链，建议要么**使用 React 框架**（如 Next.js 或 Remix），要么如果你有特殊需求，从现代的**构建工具**（如 Vite 或 Parcel）开始。在这个有见地的指南中，我们将探索 2025 年的 React 景象：我们建议给中高级开发者的**工具链和堆栈**，涵盖构建工具（Vite、Turbopack、Webpack）、路由解决方案（React Router 与 TanStack Router）、流行框架（Next.js、Remix 等）、用于状态和数据管理的关键库，甚至**人工智能如何影响 React 开发**。

## 何时使用

- 在选择 React 堆栈（框架、构建工具、路由、状态管理）时，将其用作参考
- 在开始新的 React 项目并评估现代生态系统选项时，这很有帮助

## 说明

- 对于需要 SSR/SEO 的全栈应用程序：使用 Next.js 或 Remix 作为框架
- 对于 SPAs、内部工具和仪表板：使用 Vite + React Router 或 TanStack Router
- 将 Vite 作为任何自定义（非框架）React 设置的构建工具
- 考虑在自定义堆栈中使用 TanStack Router 进行类型安全的路由；否则使用框架提供的路由
- 使用 TanStack Query（React Query）进行服务器状态，使用 Zustand 或 Redux 进行复杂的全局状态
- 在支持的地方使用 React 19 API（ref 作为 prop、use()、Actions）
- 采用 AI 辅助开发工具，但始终验证生成的代码

## 详情

**目标受众**：本指南面向中级到高级 React 开发者，他们了解基础知识，并希望在 2025 年就其堆栈做出明智的选择。

### 官方指南和不断演变的最佳实践

React 核心团队已经根据社区趋势更新了其指南。新的 React 文档强调在开始项目时 *"不要重新发明轮子"*。**Create React App** 在快速启动 React SPAs 方面为我们服务得很好，但它难以扩展到生产需求（例如缺乏内置路由或 SSR）。随着 CRA 现在被弃用，开发者被推向**功能齐全的框架**或使用较轻的工具自行组装堆栈。React 核心给出的经验法则是：**如果你的应用程序需要路由，你将受益于框架**。现代框架紧密集成路由、数据获取、代码拆分等功能，因此你不会自己编写一个微型框架。

为什么会有这种转变？在过去的几年里，React 引入了强大的特性，如**钩子**、**并发渲染**和**服务器组件**。但实际上，要在最佳方式下利用其中许多特性通常需要复杂的工具。像 Next.js 这样的框架已成为 React 最新功能的载体（例如流式 SSR、服务器端数据加载等）。**React 服务器组件 (RSC)** 作为生产就绪的功能，在 Next.js 13 的 App Router 中发布，实现了*混合渲染模型*（服务器驱动的 UI，服务器渲染的组件没有 JS 成本）。早期报告显示，使用 RSC 时，**捆绑包大小减少了 20% 以上**，因为运行在服务器上的逻辑不会发送到客户端。React 19 也在稳定化**服务器操作**（使用 `'use server'` 指令调用），这允许你定义在服务器上运行表单提交或其他突变 - 进一步模糊了前后端的界限。

话虽如此，并非每个项目都需要一个重型框架。React 团队承认有*采用轻量级方案的案例*：小部件、将 React 添加到现有网站或通过从头开始构建进行学习。如果你选择自定义路线，你仍然可以遵循 React 更新的“从头开始构建”指南，使用现代工具如 Vite 或 **RSBuild**。

### 2025 年的构建工具：Vite、Turbopack 和未来

构建工具链是将你的 React 代码（JSX、CSS 等）转换为可在浏览器中运行的元素。在 2025 年，开发者体验有了很大的改善：

* **Vite** 已成为非框架 React 项目的非官方选择。Vite 提供了一个超快的开发服务器（由 ESBuild 驱动）并使用 Rollup 进行生产捆绑。它的流行度飙升，到 2025 年，其 React 集成是继 Next.js 之后的第二广泛的构建设置。吸引力：**即时服务器启动**和近乎即时的模块热重载。如果你要从 CRA 迁移，React 团队明确建议 **Vite** 作为首选。

* **Turbopack** - 由 Vercel 引入的新 Rust-based 捆绑器 - 是一颗即将升起的新星，定位为 Webpack 的精神续作，专注于**增量编译**以实现超快重载。它在 Next.js 中集成，所以如果你使用 Next.js，你可能会从中受益。在 Next.js 之外，Turbopack 尚未成为通用工具。

* **Webpack** - 长期以来的工作horse - 仍然存在，但主要在遗留模式下。对于新项目，在 2025 年你很少会直接选择 Webpack，除非你有非常特定的需求。**遗留项目使用 Webpack，新项目使用 Vite（或框架默认）**。

* **Rspack / RSBuild** - 是新一代 **Rust-powered 捆绑器**的一部分。**Rspack** 是一个高性能捆绑器，与 Webpack 的生态系统高度兼容。**RSBuild** 是一个零配置构建工具，基于 Rspack 构建，为包括 React 在内的框架提供轻松设置。

总而言之，**我们大多数情况下的选择是 Vite** - 它启动快速，运行快速，并且得到了很好的支持。

### 框架和起点

在 2025 年为 React 项目选择**起点**通常意味着选择一个**框架**。

**Next.js (全栈 React 框架)**：由 Vercel 维护的 Next.js 已成为*生产 React 应用的首选解决方案*。它提供了开箱即用的**基于文件的路由**、**SSR**、**SSG**、**图像优化**、API 路由和**React 服务器组件**。Next 的优势在于其**强大的默认值和约定**。我们**推荐为构建新 React 应用程序**的完整解决方案。

**Remix (以及 React Router v7)**：Remix 强调网络基础知识和发展增强。由 React Router 团队创建，Remix 引入了一种集成的**路由 + 数据加载 + 突变**方法。React Router v7 采用了许多 Remix 的模式。对于希望对服务器端和客户端工作进行细粒度控制的应用程序来说，这是一个坚实的基础选择。

**“无框架”自定义设置 (Vite + 库堆栈)**：如果你决定不需要完整的框架，从 **Vite** 开始，并添加组件：例如，**React Router 或 TanStack Router 用于路由，React Query 用于数据获取**。你可能选择这种方案用于像内部工具这样不需要 SSR/SEO 的场景。

**其他值得注意的**：**Astro** 因内容网站（默认无 JS，混合框架）而受到关注。**RedwoodJS** 提供了一个意见一致的“React + GraphQL + Prisma + SSR”堆栈。**Expo** 与 **Expo Router** 将 React Native 和 Web 结合在一起。

**我们的意见**：根据工作匹配工具：
- **Next.js** 用于需要 SSR、SEO 或服务器组件的面向公众的应用程序
- **Remix** 用于强调发展增强和网络基础知识的应用程序
- **Vite + React Router/TanStack Router** 用于 SPAs、仪表板、内部工具和任何不需要 SSR 的应用程序

**自定义 Vite SSR（没有元框架）**：如果你需要 SSR 但不想使用完整的框架，Vite 提供了内置的 SSR 支持。像 **Vike**（以前是 vite-plugin-ssr）这样的工具在 Vite 之上提供了一个薄层，用于基于文件的带 SSR 路由，给你框架般的 DX，同时保持完全控制。

```typescript
// server.ts — 最小的自定义 Vite SSR 设置
import express from 'express'
import { createServer as createViteServer } from 'vite'

const app = express()
const vite = await createViteServer({ server: { middlewareMode: true } })
app.use(vite.middlewares)

app.use('*', async (req, res) => {
  const template = await vite.transformIndexHtml(req.originalUrl, indexHtml)
  const { render } = await vite.ssrLoadModule('/src/entry-server.tsx')
  const appHtml = await render(req.originalUrl)
  res.send(template.replace('<!--app-->', appHtml))
})
```

当你的应用程序需要 SSR 以实现 SEO 或性能，但你的应用程序的路由和数据加载足够简单，以至于框架增加了比价值更多的复杂性时，这是一个很好的选择。

到 2025 年，许多成功的 React 应用程序在 Vite 中运行，而没有元框架。关键在于根据你的约束选择正确的工具，而不是默认选择最功能丰富的选项。

### 路由解决方案：React Router 与 TanStack Router

**框架提供的路由**：如果你使用 Next.js 或 Remix，路由基本上由框架解决。这些框架将路由与数据获取紧密集成，这避免了常见的陷阱，如加载瀑布。

**React Router**：经过实战检验且广泛使用。React Router v6 引入了一个简化的 API，使用钩子和嵌套路由。从 v6.4+ 开始，它添加了**异步数据和 suspense 支持**。如果你不使用框架，仍然是一个顶级选择。

**TanStack Router**：一个较新的参与者，具有第一流的**TypeScript**支持、内置的**带缓存的加载数据**以及丰富的 API 用于**搜索参数**。它试图给你 Remix/Next 路由器的功能，但与特定框架解耦。

**主要区别**：**类型安全**和**开发者体验**。TanStack Router 是“TS-first”构建的。React Router 更为简约。两者都可以进行嵌套路由和数据加载。

**我们的建议**：对于自定义堆栈，认真考虑 **TanStack Router**，因为它具有现代的功能集。React Router 仍然完全有效，特别是如果你的团队已经熟悉它。

```jsx
import { createRootRoute, createRoute, createRouter, RouterProvider } from '@tanstack/react-router';

const rootRoute = createRootRoute();
const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: () => <div>Hello, world!</div>,
});

const routeTree = rootRoute.addChildren([indexRoute]);
const router = createRouter({ routeTree });

export default function App() {
  return <RouterProvider router={router} />;
}
```

### 状态管理和数据获取库

**本地和全局状态使用钩子**：对于本地状态，`useState` 和 `useReducer` 足够了。React 的 Context API 适用于轻量级的全局状态，但要小心——上下文更新会重新渲染所有消费者。

**Redux（以及现代 Redux Toolkit）**：在 2025 年仍然非常活跃，尽管集中在大型应用程序中。**Redux Toolkit (RTK)** 显著减少了样板代码。**何时你应该使用 Redux？** 如果你的应用程序具有非常复杂的状态转换或你需要功能，如撤销/重做、缓存、devtools。

**Zustand、Jotai 和轻量级状态库**：对于简单的全局存储需求。Zustand 提供了一个极简的、基于钩子的全局状态存储，**没有样板代码**。

**TanStack Query**：管理**服务器状态**的领导者。提供像 `useQuery` 和 `useMutation` 这样的钩子来声明式地获取和缓存数据。

```tsx
import { useQuery } from '@tanstack/react-query';

function TodoList() {
  const { data: todos, error, isLoading } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  });
  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  return <ul>{todos.map(t => <li key={t.id}>{t.title}</li>)}</ul>;
}
```

**React Query 和朋友即使在 RSC 的时代仍然相关**——它们可能更多地用于*突变和实时更新*，而初始加载则转移到服务器端。

**表单状态**：**React Hook Form** 已确立为一个很棒的库。结合**Zod** 用于模式，你可以声明式地验证输入。

**关键库**：MUI、Chakra UI、Radix UI、Headless UI 用于组件。**@tanstack/react-virtual** 用于列表虚拟化。**Vitest + React Testing Library** 用于 Vite 项目的测试，**Jest + React Testing Library** 用于其他设置，**Cypress** 或 **Playwright** 用于 E2E。

### 使用 Vitest 进行测试

对于 Vite 项目，**Vitest** 是自然的测试伴侣——它与 Vite 的配置、转换和插件管道共享，因此没有单独的测试捆绑器需要配置或同步。

```typescript
// vite.config.ts — Vitest 直接使用此配置
/// <reference types="vitest/config" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    globals: true,
    setupFiles: './src/test/setup.ts',
    css: true,
  },
})
```

```typescript
// src/test/setup.ts
import '@testing-library/jest-dom/vitest'
```

```tsx
// src/components/Button.test.tsx
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { Button } from './Button'

test('calls onClick when clicked', async () => {
  const onClick = vi.fn()
  render(<Button onClick={onClick}>Save</Button>)
  await userEvent.click(screen.getByRole('button', { name: 'Save' }))
  expect(onClick).toHaveBeenCalledOnce()
})
```

Vitest 给你：即时观看模式（与 Vite 的转换缓存共享）、原生 ESM 支持、Jest 兼容 API（`describe`、`it`、`expect`、`vi.fn()`）、源代码内测试，以及内置的 `v8` 或 `istanbul` 代码覆盖率。

### React 19 和现代 API

React 19 带来了几个重要的 API 变化，简化了常见的模式：

**ref 作为常规 prop**：不再需要 `forwardRef`——直接将 `ref` 作为 prop 传递：

```tsx
// React 19 — ref 只是 prop
function Input({ ref, ...props }: InputProps & { ref?: React.Ref<HTMLInputElement> }) {
  return <input ref={ref} {...props} />
}
```

**`use()` API**：可以读取承诺或上下文，并且与钩子不同，它可以有条件地调用：

```tsx
import { use } from 'react'

function UserPanel({ show }: { show: boolean }) {
  if (!show) return null
  const user = use(UserContext)
  return <div>{user.name}</div>
}
```

**Actions 和 useActionState**：使用服务器和客户端操作简化表单处理：

```tsx
function ContactForm() {
  const [state, formAction, isPending] = useActionState(submitContact, null)
  return (
    <form action={formAction}>
      <input name="email" type="email" required />
      <button disabled={isPending}>Submit</button>
      {state?.error && <p>{state.error}</p>}
    </form>
  )
}
```

**`useOptimistic`**：在异步操作期间提供即时 UI 反馈：

```tsx
function TodoList({ todos }: { todos: Todo[] }) {
  const [optimisticTodos, addOptimistic] = useOptimistic(todos)

  async function addTodo(text: string) {
    addOptimistic([...optimisticTodos, { id: 'temp', text, pending: true }])
    await saveTodo(text)
  }

  return <ul>{optimisticTodos.map(t => <li key={t.id}>{t.text}</li>)}</ul>
}
```

**React Compiler**：一个可选的编译器，自动记忆化组件和表达式，消除大多数情况下对手动 `useMemo`、`useCallback` 和 `React.memo` 的需求。对于 Vite 项目，将其作为 Babel 插件添加：

```typescript
// vite.config.ts
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [
    react({
      babel: {
        plugins: ['babel-plugin-react-compiler'],
      },
    }),
  ],
})
```

需要 React 19。可以按文件逐个文件采用，使用 `'use memo'` 指令。

### Vite 特定最佳实践

在使用 Vite + React（不使用元框架）时，请遵循以下要点：

- **模块化文件导入**是导致打包体积过大的首要问题——直接从源文件导入，而不是导入模块化文件`index.ts`。如果需要更便捷的语法，可以使用`vite-plugin-barrel`。
- **手动拆分代码块**——按稳定性拆分供应商代码（react、router、query、UI库），以实现更好的缓存效果。
- **路由级别的代码拆分**——使用`React.lazy()`为每个路由添加，并用`<Suspense>`包裹。
- **依赖预打包**——将难以解析的依赖添加到`optimizeDeps.include`中，以加快开发服务器的速度。
- **打包分析**——在每次主要依赖更改后运行`npx vite-bundle-visualizer`。

请参考**vite-bundle-optimization**技能，了解完整的 Vite 配置模式。

### React + AI：“氛围编码”的新前沿

**AI 辅助开发**：像 Copilot、ChatGPT 或 Cursor 这样的工具可以生成组件、建议钩子并配置构建工具。术语**“氛围编码”**描述了一种开发者与 AI 助手协作的工作流程。资深开发者从中受益更多，因为他们知道该询问什么以及如何验证输出结果。

有效进行“氛围编码”的技巧：
- 使用 AI 生成模板和配置
- 生成组件模板
- 利用 AI 进行测试和类型定义
- 保持控制权——始终审查 AI 生成的代码

**React 应用中的 AI（AI 驱动的 UI）**：React 开发者越来越多地被要求构建包含 AI 功能的 UI。关键考虑因素包括提示管理、流式响应、错误处理和 AI 特定的 UI 元素。Vercel AI SDK 提供了如`useChat`之类的钩子，以抽象流式传输和缓存。

**我们的观点**：将 AI 视为 React 开发工作流程中的工具。利用您的专业知识指导 AI：您定义架构，让 AI 填充模板，然后您完善结果。

### 结论

2026 年的 React 提供了丰富的选择：

* **构建工具**：大多数情况下从 Vite 开始（如果在使用 Next.js，则使用 Turbopack）。
* **框架或非框架**：对于任何规模较大的应用，倾向于使用 React 框架（Next.js 是领先者）。
* **路由**：如果使用 Next/Remix，则使用内置路由。如果构建自己的堆栈，请考虑 TanStack Router 以实现类型安全或使用 React Router 以获得可靠性。
* **状态和数据库**：使用 React Query 处理服务器数据，使用 Zustand 或 Redux 处理复杂的全局状态。
* **拥抱新的 React 功能**：钩子是标准。使用 React 19 API（`use()`、Actions、`useOptimistic`）。了解**服务器组件**。尝试使用 React Compiler 实现自动记忆化。
* **性能**：使用`useTransition`处理非紧急更新，使用派生状态而不是存储状态，使用`useSyncExternalStore`处理外部订阅。请参考**react-render-optimization**和**react-data-fetching**技能。
* **工作流程中的 AI**：使用 AI 编码助手提高生产力，但始终验证输出结果。

React 比以往任何时候都更强大。通过选择合适的堆栈，您将能够构建健壮、可扩展的应用程序。祝您编码愉快，并希望您的组件仅在必要时才重新渲染！

## 来源

- [patterns.dev/react/react-2026](https://patterns.dev/react/react-2026)
