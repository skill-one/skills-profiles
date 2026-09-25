## 概述

TanStack Devtools 提供了一个统一的调试界面，将 TanStack Query、Router 及其他库的调试工具整合到一个面板中。它具有框架无关的插件架构、实时状态检查以及自定义插件支持。使用 Solid.js 构建，性能轻量。

**React:** `@tanstack/react-devtools`
**核心:** `@tanstack/devtools`
**状态:** Alpha

## 安装

```bash
npm install @tanstack/react-devtools
```

## 基本设置

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

const queryClient = new QueryClient()

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TanStackDevtools />
      {/* 您的应用内容 */}
      <MyApp />
    </QueryClientProvider>
  )
}
```

## 内置插件

### Query Devtools

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TanStackDevtools
        plugins={[
          {
            id: 'react-query',
            name: 'React Query',
            render: () => <ReactQueryDevtoolsPanel />,
          },
        ]}
      />
      <MyApp />
    </QueryClientProvider>
  )
}
```

### Router Devtools

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'

function App() {
  return (
    <TanStackDevtools
      plugins={[
        {
          id: 'router',
          name: 'Router',
          render: () => <TanStackRouterDevtoolsPanel router={router} />,
        },
      ]}
    />
  )
}
```

### 组合设置

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { ReactQueryDevtoolsPanel } from '@tanstack/react-query-devtools'
import { TanStackRouterDevtoolsPanel } from '@tanstack/react-router-devtools'

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <TanStackDevtools
        plugins={[
          {
            id: 'react-query',
            name: 'React Query',
            render: () => <ReactQueryDevtoolsPanel />,
          },
          {
            id: 'router',
            name: 'Router',
            render: () => <TanStackRouterDevtoolsPanel router={router} />,
          },
        ]}
      />
      <MyApp />
    </QueryClientProvider>
  )
}
```

### AI Devtools

用于调试 TanStack AI 工作流：

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'
import { AIDevtoolsPanel } from '@tanstack/ai-react/devtools'

function App() {
  return (
    <TanStackDevtools
      plugins={[
        {
          id: 'ai',
          name: 'AI',
          render: () => <AIDevtoolsPanel />,
        },
      ]}
    />
  )
}
```

AI Devtools 功能：
- **消息检查器** - 查看完整对话历史及元数据
- **令牌使用情况** - 跟踪输入/输出令牌及每次请求的成本
- **流式可视化** - 实时查看流式数据块
- **工具调用调试** - 检查工具调用、参数及结果
- **思考/推理查看器** - 调试思考模型中的推理令牌
- **适配器切换** - 在开发中测试不同提供者

## 插件系统

### 插件接口

```typescript
interface DevtoolsPlugin {
  id: string          // 唯一标识符
  name: string        // Devtools 面板中的显示名称
  render: () => JSX.Element  // 要渲染的 React 组件
}
```

### 自定义插件

```tsx
import { TanStackDevtools } from '@tanstack/react-devtools'

// 自定义状态检查插件
const stateInspectorPlugin = {
  id: 'state-inspector',
  name: '状态',
  render: () => (
    <div style={{ padding: '16px' }}>
      <h3>应用状态</h3>
      <pre>{JSON.stringify(appState, null, 2)}</pre>
    </div>
  ),
}

// 自定义网络日志插件
const networkLoggerPlugin = {
  id: 'network-logger',
  name: '网络',
  render: () => <NetworkLoggerPanel />,
}

function App() {
  return (
    <TanStackDevtools
      plugins={[
        stateInspectorPlugin,
        networkLoggerPlugin,
      ]}
    />
  )
}
```

### 动态插件注册

```tsx
function App() {
  const [plugins, setPlugins] = useState<DevtoolsPlugin[]>([])

  useEffect(() => {
    // 条件注册插件
    const activePlugins: DevtoolsPlugin[] = []

    if (process.env.NODE_ENV === 'development') {
      activePlugins.push({
        id: 'debug',
        name: '调试',
        render: () => <DebugPanel />,
      })
    }

    setPlugins(activePlugins)
  }, [])

  return <TanStackDevtools plugins={plugins} />
}
```

## Vite 插件集成

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { tanstackDevtools } from '@tanstack/devtools/vite'

export default defineConfig({
  plugins: [
    tanstackDevtools(),
  ],
})
```

## 生产环境注意事项

```tsx
// 仅在生产环境开发时包含调试工具
function App() {
  return (
    <>
      {process.env.NODE_ENV === 'development' && (
        <TanStackDevtools plugins={plugins} />
      )}
      <MyApp />
    </>
  )
}

// 或者使用懒加载
const TanStackDevtools = lazy(() =>
  import('@tanstack/react-devtools').then((m) => ({ default: m.TanStackDevtools }))
)
```

## 支持的框架

| 框架 | 包 | 状态 |
|-----------|---------|--------|
| React | `@tanstack/react-devtools` | Alpha |
| Solid | `@tanstack/solid-devtools` | 计划中 |
| Vue | `@tanstack/vue-devtools` | 计划中 |
| Angular | `@tanstack/angular-devtools` | 计划中 |

## 功能

- **统一面板** - 所有 TanStack 调试的单一界面
- **实时更新** - 状态变化的实时监控
- **插件架构** - 可通过自定义和第三方插件扩展
- **内置插件** - Query、Router 和 AI 调试面板
- **轻量级** - 使用 Solid.js 构建，开销最小
- **类型安全** - 完整的 TypeScript 支持插件定义
- **框架无关的核心** - 插件逻辑跨框架工作

## 最佳实践

1. **在生产环境中条件包含** - 使用环境检查或代码拆分
2. **使用特定插件** 而不是加载所有可用插件
3. **为插件提供唯一 ID** 以防止冲突
4. **保持插件渲染函数轻量** - 避免昂贵的计算
5. **使用 Vite 插件** 在基于 Vite 的项目中自动设置
6. **组合 Query + Router + AI 插件** 进行全栈 TanStack 调试
7. **创建特定领域的插件** 用于应用级状态检查
8. **使用 AI 调试工具** 调试流式、工具调用或令牌使用

## 常见陷阱

- 在生产构建中包含调试工具而不进行树摇
- 使用重复的插件 ID（导致渲染冲突）
- 插件中重渲染函数过重（减慢调试工具面板）
- 使用 Query 插件时忘记包裹 QueryClientProvider
- 未将路由实例传递给 Router 调试面板
