# TanStack Query (React Query) v5

**最后更新**: 2026-01-20
**版本**: @tanstack/react-query@5.90.19, @tanstack/react-query-devtools@5.91.2
**要求**: React 18.0+ (使用 useSyncExternalStore), TypeScript 4.7+ (推荐)

---

## v5 新功能

### useMutationState - 跨组件变异跟踪

无需层层传递道具即可从任何地方访问变异状态：

```tsx
import { useMutationState } from '@tanstack/react-query'

function GlobalLoadingIndicator() {
  // 获取所有待处理的变异
  const pendingMutations = useMutationState({
    filters: { status: 'pending' },
    select: (mutation) => mutation.state.variables,
  })

  if (pendingMutations.length === 0) return null
  return <div>正在保存 {pendingMutations.length} 项...</div>
}

// 按变异键过滤
const todoMutations = useMutationState({
  filters: { mutationKey: ['addTodo'] },
})
```

### 简化的乐观更新

使用 `variables` 的新模式 - 无需缓存操作，无需回滚：

```tsx
function TodoList() {
  const { data: todos } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos })

  const addTodo = useMutation({
    mutationKey: ['addTodo'],
    mutationFn: (newTodo) => api.addTodo(newTodo),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })

  // 使用待处理变异的 variables 显示乐观 UI
  const pendingTodos = useMutationState({
    filters: { mutationKey: ['addTodo'], status: 'pending' },
    select: (mutation) => mutation.state.variables,
  })

  return (
    <ul>
      {todos?.map(todo => <li key={todo.id}>{todo.title}</li>)}
      {/* 使用视觉指示器显示待处理项 */}
      {pendingTodos.map((todo, i) => (
        <li key={`pending-${i}`} style={{ opacity: 0.5 }}>{todo.title}</li>
      ))}
    </ul>
  )
}
```

### throwOnError - 错误边界

重命名为 `useErrorBoundary` (破坏性变更)：

```tsx
import { QueryErrorResetBoundary } from '@tanstack/react-query'
import { ErrorBoundary } from 'react-error-boundary'

function App() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary onReset={reset} fallbackRender={({ resetErrorBoundary }) => (
          <div>
            错误！ <button onClick={resetErrorBoundary}>重试</button>
          </div>
        )}>
          <Todos />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  )
}

function Todos() {
  const { data } = useQuery({
    queryKey: ['todos'],
    queryFn: fetchTodos,
    throwOnError: true, // ✅ v5 (v4 中的 useErrorBoundary)
  })
  return <div>{data.map(...)}</div>
}
```

### 网络模式 (离线/PWA 支持)

控制离线时的行为：

```tsx
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      networkMode: 'offlineFirst', // 离线时使用缓存
    },
  },
})

// 每个查询的覆盖
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  networkMode: 'always', // 即使离线也始终尝试 (适用于本地 API)
})
```

| 模式 | 行为 |
|------|----------|
| `online` (默认) | 仅在线时获取 |
| `always` | 始终尝试 (适用于本地/service worker API) |
| `offlineFirst` | 首先使用缓存，在线时获取 |

**检测暂停状态:**
```tsx
const { isPending, fetchStatus } = useQuery(...)
// isPending + fetchStatus === 'paused' = 离线，等待网络
```

### useQueries with Combine

组合并行查询的结果：

```tsx
const results = useQueries({
  queries: userIds.map(id => ({
    queryKey: ['user', id],
    queryFn: () => fetchUser(id),
  })),
  combine: (results) => ({
    data: results.map(r => r.data),
    pending: results.some(r => r.isPending),
    error: results.find(r => r.error)?.error,
  }),
})

// 访问组合结果
if (results.pending) return <Loading />
console.log(results.data) // [user1, user2, user3]
```

### infiniteQueryOptions 辅助函数

用于无限查询的类型安全工厂 (与 `queryOptions` 平行)：

```tsx
import { infiniteQueryOptions, useInfiniteQuery, prefetchInfiniteQuery } from '@tanstack/react-query'

const todosInfiniteOptions = infiniteQueryOptions({
  queryKey: ['todos', 'infinite'],
  queryFn: ({ pageParam }) => fetchTodosPage(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})

// 跨钩子重用
useInfiniteQuery(todosInfiniteOptions)
useSuspenseInfiniteQuery(todosInfiniteOptions)
prefetchInfiniteQuery(queryClient, todosInfiniteOptions)
```

### maxPages - 内存优化

限制无限查询中缓存的页面数：

```tsx
useInfiniteQuery({
  queryKey: ['posts'],
  queryFn: ({ pageParam }) => fetchPosts(pageParam),
  initialPageParam: 0,
  getNextPageParam: (lastPage) => lastPage.nextCursor,
  getPreviousPageParam: (firstPage) => firstPage.prevCursor, // 与 maxPages 一起使用时需要
  maxPages: 3, // 仅在内存中保留 3 页
})
```

**注意**: `maxPages` 需要双向分页 (`getNextPageParam` AND `getPreviousPageParam`)。

---

## 快速设置

```bash
npm install @tanstack/react-query@latest
npm install -D @tanstack/react-query-devtools@latest
```

### 步骤 2: Provider + 配置

```tsx
// src/main.tsx
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ReactQueryDevtools } from '@tanstack/react-query-devtools'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 分钟
      gcTime: 1000 * 60 * 60, // 1 小时 (v5: 重命名为 cacheTime)
      refetchOnWindowFocus: false,
    },
  },
})

<QueryClientProvider client={queryClient}>
  <App />
  <ReactQueryDevtools initialIsOpen={false} />
</QueryClientProvider>
```

### 步骤 3: 查询 + 变异钩子

```tsx
// src/hooks/useTodos.ts
import { useQuery, useMutation, useQueryClient, queryOptions } from '@tanstack/react-query'

// 查询选项工厂 (v5 模式)
export const todosQueryOptions = queryOptions({
  queryKey: ['todos'],
  queryFn: async () => {
    const res = await fetch('/api/todos')
    if (!res.ok) throw new Error('获取失败')
    return res.json()
  },
})

export function useTodos() {
  return useQuery(todosQueryOptions)
}

export function useAddTodo() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: async (newTodo) => {
      const res = await fetch('/api/todos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(newTodo),
      })
      if (!res.ok) throw new Error('添加失败')
      return res.json()
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['todos'] })
    },
  })
}

// 使用示例:
function TodoList() {
  const { data, isPending, isError, error } = useTodos()
  const { mutate } = useAddTodo()

  if (isPending) return <div>加载中...</div>
  if (isError) return <div>错误: {error.message}</div>
  return <ul>{data.map(todo => <li key={todo.id}>{todo.title}</li>)}</ul>
}
```

---

## 关键规则

### 必须做

✅ **对所有钩子使用对象语法**
```tsx
// v5 仅支持此：
useQuery({ queryKey, queryFn, ...options })
useMutation({ mutationFn, ...options })
```

✅ **使用数组查询键**
```tsx
queryKey: ['todos']              // 列表
queryKey: ['todos', id]          // 详情
queryKey: ['todos', { filter }]  // 过滤
```

✅ **适当配置 staleTime**
```tsx
staleTime: 1000 * 60 * 5 // 5 分钟 - 防止过度重新获取
```

✅ **使用 isPending 初始加载状态**
```tsx
if (isPending) return <Loading />
// isPending = 尚无数据且正在获取
```

✅ **在 queryFn 中抛出错误**
```tsx
if (!response.ok) throw new Error('获取失败')
```

✅ **变异后使查询失效**
```tsx
onSuccess: () => {
  queryClient.invalidateQueries({ queryKey: ['todos'] })
}
```

✅ **使用 queryOptions 工厂重用模式**
```tsx
const opts = queryOptions({ queryKey, queryFn })
useQuery(opts)
useSuspenseQuery(opts)
prefetchQuery(opts)
```

✅ **使用 gcTime (而不是 cacheTime)**
```tsx
gcTime: 1000 * 60 * 60 // 1 小时
```

### 绝对不要做

❌ **绝对不要使用 v4 数组/函数语法**
```tsx
// v4 (v5 中已移除):
useQuery(['todos'], fetchTodos, options) // ❌

// v5 (正确):
useQuery({ queryKey: ['todos'], queryFn: fetchTodos }) // ✅
```

❌ **绝对不要使用查询回调 (查询中的 onSuccess, onError, onSettled)**
```tsx
// v5 从查询中移除了这些:
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  onSuccess: (data) => {}, // ❌ v5 中已移除
})

// 使用 useEffect 代替:
const { data } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos })
useEffect(() => {
  if (data) {
    // 执行某些操作
  }
}, [data])

// 或使用变异回调 (仍然支持):
useMutation({
  mutationFn: addTodo,
  onSuccess: () => {}, // ✅ 变异中仍然有效
})
```

❌ **绝对不要使用已弃用的选项**
```tsx
// v5 中已弃用:
cacheTime: 1000 // ❌ 使用 gcTime 代替
isLoading: true // ❌ 含义已改变，使用 isPending
keepPreviousData: true // ❌ 使用 placeholderData 代替
onSuccess: () => {} // ❌ 从查询中移除
useErrorBoundary: true // ❌ 使用 throwOnError 代替
```

❌ **绝对不要假设 isLoading 表示“尚无数据”**
```tsx
// v5 已更改:
isLoading = isPending && isFetching // ❌ 现在 表示 “正在获取且正在请求”
isPending = 尚无数据 // ✅ 使用此进行初始加载
```

❌ **绝对不要忘记无限查询的 initialPageParam**
```tsx
// v5 需要此:
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: ({ pageParam }) => fetchProjects(pageParam),
  initialPageParam: 0, // ✅ v5 中需要
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})
```

❌ **绝对不要在 useSuspenseQuery 中使用 enabled**
```tsx
// 不允许:
useSuspenseQuery({
  queryKey: ['todo', id],
  queryFn: () => fetchTodo(id),
  enabled: !!id, // ❌ 不适用于 Suspense
})

// 使用条件渲染代替:
{id && <TodoComponent id={id} />}
```

❌ **绝对不要依赖 refetchOnMount: false 对于错误的查询**
```tsx
// 不起作用 - 错误总是陈旧的
useQuery({
  queryKey: ['data'],
  queryFn: failingFetch,
  refetchOnMount: false,  // ❌ 当查询出错时会被忽略
})

// 使用 retryOnMount 代替
useQuery({
  queryKey: ['data'],
  queryFn: failingFetch,
  refetchOnMount: false,
  retryOnMount: false,  // ✅ 防止错误查询在挂载时重新获取
  retry: 0,
})
```

---

## 已知问题预防

这项技能可防止 **16 个已记录的问题** 从 v5 迁移、SSR/水合错误以及常见错误：

### 问题 #1: 对象语法要求
**错误**: `useQuery 不是函数` 或类型错误
**来源**: [v5 迁移指南](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#removed-overloads-in-favor-of-object-syntax)
**为什么会发生**: v5 移除了所有函数重载，仅对象语法有效
**预防**: 始终使用 `useQuery({ queryKey, queryFn, ...options })`

**之前 (v4):**
```tsx
useQuery(['todos'], fetchTodos, { staleTime: 5000 })
```

**之后 (v5):**
```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  staleTime: 5000
})
```

### 问题 #2: 查询回调已移除
**错误**: 回调未运行，TypeScript 错误
**来源**: [v5 破坏性变更](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#callbacks-on-usequery-and-queryobserver-have-been-removed)
**为什么会发生**: onSuccess, onError, onSettled 从查询中移除 (变异中仍然有效)
**预防**: 使用 `useEffect` 执行副作用，或移动逻辑到变异回调

**之前 (v4):**
```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  onSuccess: (data) => {
    console.log('加载完成:', data)
  },
})
```

**之后 (v5):**
```tsx
const { data } = useQuery({ queryKey: ['todos'], queryFn: fetchTodos })
useEffect(() => {
  if (data) {
    console.log('加载完成:', data)
  }
}, [data])
```

### 问题 #3: 加载状态 → 待处理
**错误**: UI 显示错误的加载状态
**来源**: [v5 迁移: isLoading 重命名](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#isloading-and-isfetching-flags)
**为什么会发生**: `status: 'loading'` 重命名为 `status: 'pending'`, isLoading 含义已改变
**预防**: 使用 `isPending` 初始加载，`isLoading` 用于“正在获取且正在请求”

**之前 (v4):**
```tsx
const { data, isLoading } = useQuery(...)
if (isLoading) return <div>加载中...</div>
```

**之后 (v5):**
```tsx
const { data, isPending, isLoading } = useQuery(...)
if (isPending) return <div>加载中...</div>
// isLoading = isPending && isFetching (首次获取时正在请求)
```

### 问题 #4: cacheTime → gcTime
**错误**: `cacheTime is not a valid option`
**来源**: [v5 迁移: gcTime](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#cachetime-has-been-replaced-by-gctime)
**为什么会发生**: 重命名为更准确地反映“垃圾回收时间”
**预防**: 使用 `gcTime` 代替 `cacheTime`

**之前 (v4):**
```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  cacheTime: 1000 * 60 * 60,
})
```

**之后 (v5):**
```tsx
useQuery({
  queryKey: ['todos'],
  queryFn: fetchTodos,
  gcTime: 1000 * 60 * 60,
})
```

### 问题 #5: useSuspenseQuery + enabled
**错误**: 类型错误，enabled 选项不可用
**来源**: [GitHub 讨论 #6206](https://github.com/TanStack/query/discussions/6206)
**为什么会发生**: Suspense 保证数据可用，不能有条件禁用
**预防**: 使用条件渲染代替 `enabled` 选项

**之前 (v4/不正确):**
```tsx
useSuspenseQuery({
  queryKey: ['todo', id],
  queryFn: () => fetchTodo(id),
  enabled: !!id, // ❌ 不允许
})
```

**之后 (v5/正确):**
```tsx
// 条件渲染:
{id ? (
  <TodoComponent id={id} />
) : (
  <div>未选择 ID</div>
)}

// 在 TodoComponent 中:
function TodoComponent({ id }: { id: number }) {
  const { data } = useSuspenseQuery({
    queryKey: ['todo', id],
    queryFn: () => fetchTodo(id),
    // 不需要 enabled 选项
  })
  return <div>{data.title}</div>
}
```

### 问题 #6: initialPageParam Required
**错误**: `initialPageParam is required` 类型错误
**来源**: [v5 迁移: 无限查询](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#new-required-initialPageParam-option)
**为什么会发生**: v4 将 `pageParam` 传递为 `undefined`，v5 需要显式值
**预防**: 无限查询始终指定 `initialPageParam`

**之前 (v4):**
```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: ({ pageParam = 0 }) => fetchProjects(pageParam),
})
```

**之后 (v5):**
```tsx
useInfiniteQuery({
  queryKey: ['projects'],
  queryFn: ({ pageParam }) => fetchProjects(pageParam),
  initialPageParam: 0, // ✅ v5 中需要
  getNextPageParam: (lastPage) => lastPage.nextCursor,
})
```

### 问题 #7: keepPreviousData Removed
**错误**: `keepPreviousData is not a valid option`
**来源**: [v5 迁移: placeholderData](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#removed-keeppreviousdata-in-favor-of-placeholderdata-identity-function)
**为什么会发生**: 用更灵活的 `placeholderData` 函数替换
**预防**: 使用 `placeholderData: keepPreviousData` 辅助函数

**之前 (v4):**
```tsx
useQuery({
  queryKey: ['todos', page],
  queryFn: () => fetchTodos(page),
  keepPreviousData: true,
})
```

**之后 (v5):**
```tsx
import { keepPreviousData } from '@tanstack/react-query'

useQuery({
  queryKey: ['todos', page],
  queryFn: () => fetchTodos(page),
  placeholderData: keepPreviousData,
})
```

### 问题 #8: TypeScript 错误类型默认
**错误**: 错误处理中的类型错误
**来源**: [v5 迁移: 错误类型](https://tanstack.com/query/latest/docs/framework/react/guides/migrating-to-v5#typeerror-is-now-the-default-error)
**为什么会发生**: v4 使用 `unknown`, v5 默认为 `Error` 类型
**预防**: 如果抛出非 Error 类型，请显式指定错误类型

**之前 (v4 - 错误为 unknown):
```tsx
const { error } = useQuery({
  queryKey: ['data'],
  queryFn: async () => {
    if (Math.random() >
