## 概述

TanStack Query（前身为React Query）管理服务器状态——即存储在服务器上的数据，需要被获取、缓存、同步和更新。它提供了自动缓存、后台重新获取、陈旧验证模式、分页、无限滚动和乐观更新的开箱即用功能。

**包:** `@tanstack/react-query`
**开发工具:** `@tanstack/react-query-devtools`
**当前版本:** v5

## 安装

```bash
npm install @tanstack/react-query
npm install -D @tanstack/react-query-devtools  # 可选
```

## 设置

```tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60, // 1分钟
      gcTime: 1000 * 60 * 5, // 5分钟（垃圾回收）
      retry: 3,
      refetchOnWindowFocus: true,
      refetchOnReconnect: true,
    },
  },
})

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <YourApp />
      <ReactQueryDevtools initialIsOpen={false} />
    </QueryClientProvider>
  )
}
```

## 核心概念

### 查询键

查询键唯一标识缓存的请求数据。它们必须是可序列化的数组：

```tsx
// 简单键
useQuery({ queryKey: ['todos'], queryFn: fetchTodos })

// 带变量的（依赖数组模式）
useQuery({ queryKey: ['todos', { status, page }], queryFn: fetchTodos })

// 用于失效的层级键
useQuery({ queryKey: ['todos', todoId], queryFn: () => fetchTodo(todoId) })
useQuery({ queryKey: ['todos', todoId, 'comments'], queryFn: () => fetchComments(todoId) })

// 失效匹配前缀：
// queryClient.invalidateQueries({ queryKey: ['todos'] })
// ^ 使所有以'todos'开头的查询失效
```

### 查询函数

```tsx
// 查询函数接收一个QueryFunctionContext
useQuery({
  queryKey: ['todos', todoId],
  queryFn: async ({ queryKey, signal, meta }) => {
    const [_key, id] = queryKey
    const response = await fetch(`/api/todos/${id}`, { signal })
    if (!response.ok) throw new Error('获取失败')
    return response.json()
  },
})

// 使用signal进行自动取消
useQuery({
  queryKey: ['todos'],
  queryFn: async ({ signal }) => {
    const response = await fetch('/api/todos', { signal })
    return response.json()
  },
})
```

### queryOptions 辅助函数

创建可重用、类型安全的查询配置：

```tsx
import { queryOptions } from '@tanstack/react-query'

export const todosQueryOptions = queryOptions({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  staleTime: 5000,
})

export const todoQueryOptions = (todoId: string) =>
  queryOptions({
    queryKey: ['todos', todoId],
    queryFn: () => fetchTodo(todoId),
    enabled: !!todoId,
  })

// 使用
const { data } = useQuery(todosQueryOptions)
const { data } = useSuspenseQuery(todoQueryOptions(id))
await queryClient.prefetchQuery(todosQueryOptions)
```

## 查询（useQuery）

### 基本用法

```tsx
import { useQuery } from '@tanstack/react-query'

function Todos() {
  const {
    data,
    error,
    isLoading,      // 第一次加载，还没有数据
    isFetching,     // 任何正在进行的获取（包括后台）
    isError,
    isSuccess,
    isPending,      // 还没有数据（大多数情况下与isLoading相同）
    status,         // 'pending' | 'error' | 'success'
    fetchStatus,    // 'fetching' | 'paused' | 'idle'
    refetch,
    isStale,
    isPlaceholderData,
    dataUpdatedAt,
    errorUpdatedAt,
  } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })

  if (isLoading) return <Spinner />
  if (isError) return <Error message={error.message} />
  return <TodoList todos={data} />
}
```

### 查询选项

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,

  // 新鲜度
  staleTime: 5000,            // ms 数据保持新鲜（默认：0）
  gcTime: 300000,             // ms 未使用的数据保持缓存（默认：5分钟）

  // 重新获取
  refetchInterval: 10000,     // 每10秒轮询
  refetchIntervalInBackground: false, // 标签页隐藏时不轮询
  refetchOnMount: true,       // 组件挂载时如果陈旧则重新获取
  refetchOnWindowFocus: true, // 窗口聚焦时如果陈旧则重新获取
  refetchOnReconnect: true,   // 网络重新连接时重新获取

  // 重试
  retry: 3,                   // 重试次数（或函数）
  retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

  // 条件性
  enabled: !!userId,          // 仅在为真时运行

  // 初始/占位符数据
  initialData: () => cachedData,
  initialDataUpdatedAt: Date.now() - 10000,
  placeholderData: (previousData) => previousData, // 保持之前的数据模式
  placeholderData: initialTodos,

  // 转换
  select: (data) => data.filter(todo => !todo.done),

  // 结构共享（默认：true）
  structuralSharing: true,

  // 网络模式
  networkMode: 'online', // 'online' | 'always' | 'offlineFirst'

  // 元数据（可在查询函数上下文中访问）
  meta: { purpose: '用户界面' },
})
```

## 变更（useMutation）

### 基本用法

```tsx
import { useMutation, useQueryClient } from '@tanstack/react-query'

function AddTodo() {
  const queryClient = useQueryClient()

  const mutation = useMutation({
    mutationFn: (newTodo: { title: string }) => {
      return fetch('/api/todos', {
        method: 'POST',
        body: JSON.stringify(newTodo),
      }).then(res => res.json())
    },
    // 生命周期回调
    onMutate: async (variables) => {
      // 调用mutationFn之前
      // 适用于乐观更新
      return { previousTodos } // 用于onError的上下文
    },
    onSuccess: (data, variables, context) => {
      // 使相关查询失效
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
    onError: (error, variables, context) => {
      // 撤销乐观更新
      queryClient.setQueryData(['todos'], context.previousTodos)
    },
    onSettled: (data, error, variables, context) => {
      // 成功或失败时始终运行
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  return (
    <button
      onClick={() => mutation.mutate({ title: 'New Todo' })}
      disabled={mutation.isPending}
    >
      {mutation.isPending ? '添加中...' : '添加待办事项'}
    </button>
  )
}
```

### 变更状态

```tsx
const {
  mutate,         // 发起并忘记
  mutateAsync,    // 返回Promise
  isPending,      // 变更进行中
  isError,
  isSuccess,
  isIdle,         // 尚未发起
  data,           // 成功响应
  error,          // 错误对象
  reset,          // 重置状态为空闲
  variables,      // 传递给mutate的变量
  status,         // 'idle' | 'pending' | 'error' | 'success'
} = useMutation({ ... })
```

## 乐观更新

```tsx
const mutation = useMutation({
  mutationFn: updateTodo,
  onMutate: async (newTodo) => {
    // 1. 取消正在进行的重新获取
    await queryClient.cancelQueries({ queryKey: ['todos', newTodo.id] })

    // 2. 快照之前值
    const previousTodo = queryClient.getQueryData(['todos', newTodo.id])

    // 3. 乐观更新
    queryClient.setQueryData(['todos', newTodo.id], newTodo)

    // 4. 返回上下文用于回滚
    return { previousTodo }
  },
  onError: (err, newTodo, context) => {
    // 出错时回滚
    queryClient.setQueryData(['todos', newTodo.id], context.previousTodo)
  },
  onSettled: () => {
    // 始终重新获取以与服务器同步
    queryClient.invalidateQueries({ queryKey: ['todos'] })
  },
})
```

### 列表中的乐观更新

```tsx
onMutate: async (newTodo) => {
  await queryClient.cancelQueries({ queryKey: ['todos'] })
  const previousTodos = queryClient.getQueryData(['todos'])

  queryClient.setQueryData(['todos'], (old) => [...old, newTodo])

  return { previousTodos }
},
onError: (err, newTodo, context) => {
  queryClient.setQueryData(['todos'], context.previousTodos)
},
```

## 查询失效

```tsx
const queryClient = useQueryClient()

// 使所有查询失效
queryClient.invalidateQueries()

// 按前缀失效
queryClient.invalidateQueries({ queryKey: ['todos'] })

// 精确匹配失效
queryClient.invalidateQueries({ queryKey: ['todos', 1], exact: true })

// 带谓词失效
queryClient.invalidateQueries({
  predicate: (query) =>
    query.queryKey[0] === 'todos' && query.queryKey[1]?.status === 'done',
})

// 失效并立即重新获取
queryClient.refetchQueries({ queryKey: ['todos'] })

// 完全从缓存中移除
queryClient.removeQueries({ queryKey: ['todos', 1] })

// 重置为初始状态
queryClient.resetQueries({ queryKey: ['todos'] })
```

## 无限查询

```tsx
import { useInfiniteQuery } from '@tanstack/react-query'

function InfiniteList() {
  const {
    data,
    fetchNextPage,
    fetchPreviousPage,
    hasNextPage,
    hasPreviousPage,
    isFetchingNextPage,
    isFetchingPreviousPage,
  } = useInfiniteQuery({
    queryKey: ['projects'],
    queryFn: async ({ pageParam }) => {
      const res = await fetch(`/api/projects?cursor=${pageParam}`)
      return res.json()
    },
    initialPageParam: 0,
    getNextPageParam: (lastPage, allPages, lastPageParam) => {
      return lastPage.nextCursor ?? undefined // undefined = 没有更多页面
    },
    getPreviousPageParam: (firstPage, allPages, firstPageParam) => {
      return firstPage.prevCursor ?? undefined
    },
    maxPages: 3, // 缓存最多3页（为了性能）
  })

  return (
    <div>
      {data.pages.map((page) =>
        page.items.map((item) => <Item key={item.id} item={item} />)
      )}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage || isFetchingNextPage}
      >
        {isFetchingNextPage ? '加载中...' : hasNextPage ? '加载更多' : '没有更多'}
      </button>
    </div>
  )
}
```

## 并行查询

```tsx
// 多个独立的查询自动并行运行
function Dashboard() {
  const usersQuery = useQuery({ queryKey: ['users'], queryFn: fetchUsers })
  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: fetchProjects })

  // 同时获取
}

// 动态并行查询使用useQueries
function UserProjects({ userIds }) {
  const queries = useQueries({
    queries: userIds.map((id) => ({
      queryKey: ['user', id],
      queryFn: () => fetchUser(id),
    })),
    combine: (results) => ({
      data: results.map(r => r.data),
      pending: results.some(r => r.isPending),
    }),
  })
}
```

## 依赖查询

```tsx
// 使用enabled的顺序查询
function UserPosts({ userId }) {
  const userQuery = useQuery({
    queryKey: ['user', userId],
    queryFn: () => fetchUser(userId),
  })

  const postsQuery = useQuery({
    queryKey: ['posts', userId],
    queryFn: () => fetchPostsByUser(userId),
    enabled: !!userQuery.data, // 用户加载后才运行
  })
}
```

## 分页查询

```tsx
function PaginatedList() {
  const [page, setPage] = useState(1)

  const { data, isPlaceholderData } = useQuery({
    queryKey: ['todos', page],
    queryFn: () => fetchTodos(page),
    placeholderData: (previousData) => previousData, // 保持显示旧数据
  })

  return (
    <div style={{ opacity: isPlaceholderData ? 0.5 : 1 }}>
      {data.items.map(item => <Item key={item.id} item={item} />)}
      <button
        onClick={() => setPage(p => p + 1)}
        disabled={isPlaceholderData || !data.hasMore}
      >
        下一页
      </button>
    </div>
  )
}
```

## Suspense 集成

```tsx
import { useSuspenseQuery, useSuspenseInfiniteQuery } from '@tanstack/react-query'

// 组件将在数据加载完成后挂起
function TodoList() {
  const { data } = useSuspenseQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })
  // data 在这里保证已定义
  return <ul>{data.map(todo => <li key={todo.id}>{todo.title}</li>)}</ul>
}

// 用Suspense边界包裹
function App() {
  return (
    <ErrorBoundary fallback={<Error />}>
      <Suspense fallback={<Loading />}>
        <TodoList />
      </Suspense>
    </ErrorBoundary>
  )
}

// 多个Suspense查询（并行获取）
function Dashboard() {
  const [{ data: users }, { data: projects }] = useSuspenseQueries({
    queries: [
      { queryKey: ['users'], queryFn: fetchUsers },
      { queryKey: ['projects'], queryFn: fetchProjects },
    ],
  })
}
```

## 预取

```tsx
const queryClient = useQueryClient()

// 悬停时预取
function TodoLink({ todoId }) {
  const prefetch = () => {
    queryClient.prefetchQuery({
      queryKey: ['todo', todoId],
      queryFn: () => fetchTodo(todoId),
      staleTime: 5000, // 只有当数据比5秒旧时才预取
    })
  }

  return (
    <Link to={`/todos/${todoId}`} onMouseEnter={prefetch}>
      待办事项 {todoId}
    </Link>
  )
}

// 路由加载器中的预取（TanStack Router集成）
export const Route = createFileRoute('/todos/$todoId')({
  loader: ({ context: { queryClient }, params: { todoId } }) =>
    queryClient.ensureQueryData(todoQueryOptions(todoId)),
})

// 预取无限查询
queryClient.prefetchInfiniteQuery({
  queryKey: ['projects'],
  queryFn: fetchProjects,
  initialPageParam: 0,
  pages: 3, // 预取前3页
})
```

## SSR & Hydration

### 服务器端预取

```tsx
// 服务器组件或加载器
import { dehydrate, HydrationBoundary, QueryClient } from '@tanstack/react-query'

async function getServerSideProps() {
  const queryClient = new QueryClient()

  await queryClient.prefetchQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })

  return {
    props: {
      dehydratedState: dehydrate(queryClient),
    },
  }
}

function Page({ dehydratedState }) {
  return (
    <HydrationBoundary state={dehydratedState}>
      <Todos />
    </HydrationBoundary>
  )
}
```

### 流式SSR（React Server Components）

```tsx
import { dehydrate, HydrationBoundary } from '@tanstack/react-query'
import { makeQueryClient } from './query-client'

export default async function Page() {
  const queryClient = makeQueryClient()

  // 服务器上预取
  await queryClient.prefetchQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  })

  return (
    <HydrationBoundary state={dehydrate(queryClient)}>
      <TodoList />
    </HydrationBoundary>
  )
}
```

## QueryClient API

```tsx
const queryClient = useQueryClient()

// 获取缓存数据
queryClient.getQueryData(['todos'])

// 设置缓存数据
queryClient.setQueryData(['todos'], updatedTodos)
queryClient.setQueryData(['todos'], (old) => [...old, newTodo])

// 获取查询状态
queryClient.getQueryState(['todos'])

// 检查是否正在获取
queryClient.isFetching({ queryKey: ['todos'] })
queryClient.isMutating()

// 取消查询
queryClient.cancelQueries({ queryKey: ['todos'] })

// 失效（标记陈旧，正在重新获取）
queryClient.invalidateQueries({ queryKey: ['todos'] })

// 重新获取（即使新鲜也强制重新获取）
queryClient.refetchQueries({ queryKey: ['todos'] })

// 从缓存中移除
queryClient.removeQueries({ queryKey: ['todos'] })

// 重置为初始状态
queryClient.resetQueries({ queryKey: ['todos'] })

// 清除整个缓存
queryClient.clear()

// 预取
queryClient.prefetchQuery({ queryKey: ['todos'], queryFn: fetchTodos })
queryClient.ensureQueryData({ queryKey: ['todos'], queryFn: fetchTodos })

// 获取/设置默认值
queryClient.setQueryDefaults(['todos'], { staleTime: 10000 })
queryClient.getQueryDefaults(['todos'])
queryClient.setMutationDefaults(['addTodo'], { mutationFn: addTodo })
```

## 测试

```tsx
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

function createWrapper() {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false, // 测试中不重试
        gcTime: Infinity, // 防止测试期间垃圾回收
      },
    },
  })
  return ({ children }) => (
    <QueryClientProvider client={queryClient}>
      {children}
    </QueryClientProvider>
  )
}

test('fetches todos', async () => {
  const { result } = renderHook(() => useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
  }), { wrapper: createWrapper() })

  await waitFor(() => expect(result.current.isSuccess).toBe(true))
  expect(result.current.data).toEqual(expectedTodos)
})

// 使用setQueryData进行组件测试
test('renders todos', () => {
  const queryClient = new QueryClient()
  queryClient.setQueryData(['todos'], mockTodos)

  render(
    <QueryClientProvider client={queryClient}>
      <TodoList />
    </QueryClientProvider>
  )

  expect(screen.getByText('Todo 1')).toBeInTheDocument()
})
```

## TypeScript模式

### 类型化查询函数

```tsx
interface Todo {
  id: number
  title: string
  completed: boolean
}

// 类型从queryFn返回类型推断
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: async (): Promise<Todo[]> => {
    const res = await fetch('/api/todos')
    return res.json()
  },
})
// data: Todo[] | undefined

// 使用select
const { data } = useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  select: (data): string[] => data.map(t => t.title),
})
// data: string[] | undefined
```

### 类型化错误

```tsx
// 默认错误类型是Error
const { error } = useQuery<Todo[], AxiosError>({
  queryKey: ['todos'],
  queryFn: fetchTodos,
})

// 或全局注册
declare module '@tanstack/react-query' {
  interface Register {
    defaultError: AxiosError
  }
}
```

### 查询选项模式（推荐）

```tsx
import { queryOptions, infiniteQueryOptions } from '@tanstack/react-query'

export const todosOptions = queryOptions({
  queryKey: ['todos'] as const,
  queryFn: fetchTodos,
  staleTime: 5000,
})

export const todoOptions = (id: string) =>
  queryOptions({
    queryKey: ['todos', id] as const,
    queryFn: () => fetchTodo(id),
    enabled: !!id,
  })

// 全部类型推断
const { data } = useQuery(todosOptions)
const { data } = useSuspenseQuery(todoOptions('123'))
await queryClient.ensureQueryData(todosOptions)
queryClient.invalidateQueries({ queryKey: todosOptions.queryKey })
```

## 高级模式

### 窗口聚焦重新获取

```tsx
// 全局禁用
const queryClient = new QueryClient({
  defaultOptions: {
    queries: { refetchOnWindowFocus: false },
  },
})

// 自定义聚焦管理器
import { focusManager } from '@tanstack/react-query'

// 对于React Native
focusManager.setEventListener((handleFocus) => {
  const subscription = AppState.addEventListener('change', (state) => {
    handleFocus(state === 'active')
  })
  return () => subscription.remove()
})
```

### 网络模式

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  // 'online'（默认）：仅在在线时获取
  // 'always': 始终获取（适用于本地优先）
  // 'offlineFirst': 尝试获取，离线时使用缓存
  networkMode: 'offlineFirst',
})
```

### 查询取消

```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: async ({ signal }) => {
    // signal是AbortSignal - 在卸载或键更改时自动取消
    const res = await fetch('/api/todos', { signal })
    return res.json()
  },
})

// 手动取消
queryClient.cancelQueries({ queryKey: ['todos'] })
```

### 持久化

```tsx
import { persistQueryClient } from '@tanstack/react-query-persist-client'
import { createSyncStoragePersister } from '@tanstack/query-sync-storage-persister'

const persister = createSyncStoragePersister({
  storage: window.localStorage,
})

persistQueryClient({
  queryClient,
  persister,
  maxAge: 1000 * 60 * 60 * 24, // 24小时
})
```

## 最佳实践

1. **使用`queryOptions`辅助函数**进行类型安全、可重用的查询配置
2. **按层级结构查询键**以实现粒度失效
3. **设置适当的`staleTime`** - 0表示挂载时始终重新获取（默认），增加对于不太动态的数据
4. **使用`placeholderData`**（而不是`initialData`）在分页时保持之前页面的数据
5. **优先使用`useSuspenseQuery`**当使用Suspense边界时，使组件代码更清晰
6. **使用`enabled`**对于依赖查询，而不是条件性钩子调用
7. **变更后始终失效** - 不要仅依赖乐观更新
8. **在`onMutate`中取消查询**以防止乐观更新时的竞争条件
9. **使用`ensureQueryData`**在路由加载器中而不是`prefetchQuery`以立即访问
10. **在测试中设置`retry: false`**以避免超时问题
11. **不要解构查询结果**如果你需要将结果传递到其他地方（会破坏响应性）
12. **使用`select`**对于派生数据而不是在组件中转换
13. **保持查询函数纯净**——它们应该只获取，不应引起副作用
14. **使用`gcTime: Infinity`**在测试中以防止断言期间的缓存清理

## 常见陷阱

- 使用`initialData`时你实际上需要`placeholderData`（initialData计为“新鲜”数据）
- 无限查询未提供`initialPageParam`（v5中需要）
- 条件性调用钩子（违反React规则）
- 在乐观更新之前未取消查询（竞争条件）
- 设置`staleTime`高于`gcTime`（数据在“新鲜”时被垃圾回收）
- 忘记在测试中包裹`QueryClientProvider`
- 在测试中未使用相同的`QueryClient`实例（共享状态）
- 当顺序很重要时，在变更回调中未等待`invalidateQueries`
