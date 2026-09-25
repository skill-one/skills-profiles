# React Query 最佳实践

你是一位 React Query、TypeScript 和 React 开发的专家。React Query（现更名为 TanStack Query）通过内置缓存、后台更新和过期数据管理简化了数据获取逻辑。

## 核心原则

- 使用 React Query 进行所有数据获取和缓存
- 利用 React Query 的内置状态管理来替代 `useState` 处理服务器数据
- 使用 React Context 和 `useReducer` 管理客户端全局状态
- 通过合理的缓存策略避免过多的 API 调用
- 始终正确处理加载状态和错误

## 项目结构

```
src/
  components/
    [功能]/
      index.tsx
      queries.ts           # 功能特定的查询钩子
      mutations.ts         # 功能特定的变异钩子
  hooks/
    useAuth.ts
    useApi.ts
  services/
    api/
      client.ts            # Axios/fetch 配置
      users.ts             # 用户 API 函数
      posts.ts             # 帖子 API 函数
  providers/
    ReactQueryProvider.tsx
  types/
    index.ts
```

## 设置

### 提供者配置

```typescript
// providers/ReactQueryProvider.tsx
import { QueryClient, QueryClientProvider } from 'react-query';
import { ReactQueryDevtools } from 'react-query/devtools';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,    // 5 分钟
      cacheTime: 30 * 60 * 1000,   // 30 分钟
      retry: 2,
      refetchOnWindowFocus: true,
    },
  },
});

export function ReactQueryProvider({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      {children}
      <ReactQueryDevtools />
    </QueryClientProvider>
  );
}
```

## 查询模式

### 基本查询钩子

```typescript
import { useQuery } from 'react-query';
import { fetchUser, User } from '@/services/api/users';

export function useUser(userId: string) {
  return useQuery<User, Error>(
    ['user', userId],
    () => fetchUser(userId),
    {
      enabled: !!userId,
      staleTime: 1000 * 60 * 10, // 10 分钟
    }
  );
}
```

### 带错误处理的查询

服务应抛出用户友好的错误，让 React Query 捕获并显示：

```typescript
// services/api/users.ts
export async function fetchUser(userId: string): Promise<User> {
  const response = await fetch(`/api/users/${userId}`);

  if (!response.ok) {
    // 抛出用户友好的错误消息
    throw new Error('无法加载用户资料。请重试。');
  }

  return response.json();
}

// 组件使用
function UserProfile({ userId }: { userId: string }) {
  const { data: user, isLoading, error } = useUser(userId);

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={error.message} />;

  return <ProfileCard user={user} />;
}
```

### 依赖查询

```typescript
function useUserWithPosts(userId: string) {
  const userQuery = useUser(userId);

  const postsQuery = useQuery(
    ['posts', userId],
    () => fetchUserPosts(userId),
    {
      enabled: !!userQuery.data,
    }
  );

  return { userQuery, postsQuery };
}
```

### 分页查询

```typescript
function usePaginatedUsers(page: number, limit: number = 10) {
  return useQuery(
    ['users', 'list', { page, limit }],
    () => fetchUsers({ page, limit }),
    {
      keepPreviousData: true,
    }
  );
}
```

### 无限滚动

```typescript
import { useInfiniteQuery } from 'react-query';

function useInfiniteUsers() {
  return useInfiniteQuery(
    ['users', 'infinite'],
    ({ pageParam = 1 }) => fetchUsers({ page: pageParam }),
    {
      getNextPageParam: (lastPage) => lastPage.nextPage ?? undefined,
    }
  );
}
```

## 变异模式

### 基本变异

```typescript
import { useMutation, useQueryClient } from 'react-query';

function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation(createUser, {
    onSuccess: () => {
      queryClient.invalidateQueries(['users']);
    },
    onError: (error: Error) => {
      toast.error(error.message);
    },
  });
}
```

### 乐观更新

```typescript
function useUpdateUser() {
  const queryClient = useQueryClient();

  return useMutation(updateUser, {
    onMutate: async (updatedUser) => {
      await queryClient.cancelQueries(['user', updatedUser.id]);

      const previousUser = queryClient.getQueryData(['user', updatedUser.id]);

      queryClient.setQueryData(['user', updatedUser.id], updatedUser);

      return { previousUser };
    },
    onError: (err, updatedUser, context) => {
      if (context?.previousUser) {
        queryClient.setQueryData(['user', updatedUser.id], context.previousUser);
      }
    },
    onSettled: (data, error, updatedUser) => {
      queryClient.invalidateQueries(['user', updatedUser.id]);
    },
  });
}
```

## 状态管理集成

### 与 Context/Reducer 结合

使用 React Query 处理服务器状态，使用 Context/Reducer 处理客户端状态：

```typescript
// 客户端状态使用 Context
const AppStateContext = createContext<AppState | undefined>(undefined);
const AppDispatchContext = createContext<Dispatch<Action> | undefined>(undefined);

function AppProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  return (
    <AppStateContext.Provider value={state}>
      <AppDispatchContext.Provider value={dispatch}>
        {children}
      </AppDispatchContext.Provider>
    </AppStateContext.Provider>
  );
}

// 服务器状态使用 React Query
function UserDashboard() {
  const { theme } = useAppState();         // 客户端状态
  const { data: user } = useUser(userId);  // 服务器状态

  return <Dashboard theme={theme} user={user} />;
}
```

### 与 Zustand（替代方案）结合

```typescript
import { create } from 'zustand';

// 客户端状态存储
const useStore = create((set) => ({
  theme: 'light',
  setTheme: (theme) => set({ theme }),
}));

// 同时使用的组件
function App() {
  const theme = useStore((state) => state.theme);
  const { data: user } = useUser(userId);

  return <Layout theme={theme} user={user} />;
}
```

## 性能优化

### 查询键最佳实践

```typescript
// 结构化查询键
const queryKeys = {
  users: {
    all: ['users'] as const,
    lists: () => [...queryKeys.users.all, 'list'] as const,
    list: (filters: Filters) => [...queryKeys.users.lists(), filters] as const,
    details: () => [...queryKeys.users.all, 'detail'] as const,
    detail: (id: string) => [...queryKeys.users.details(), id] as const,
  },
};
```

### 选择性订阅

```typescript
// 仅订阅用户名变化
function useUserName(userId: string) {
  return useUser(userId, {
    select: (user) => user.name,
  });
}
```

### 预取

```typescript
function UserListItem({ userId }: { userId: string }) {
  const queryClient = useQueryClient();

  const handleMouseEnter = () => {
    queryClient.prefetchQuery(
      ['user', userId],
      () => fetchUser(userId),
      { staleTime: 60000 }
    );
  };

  return (
    <li onMouseEnter={handleMouseEnter}>
      <Link to={`/users/${userId}`}>查看资料</Link>
    </li>
  );
}
```

## 错误处理模式

### 全局错误处理器

```typescript
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      onError: (error: Error) => {
        console.error('查询错误:', error);
      },
    },
    mutations: {
      onError: (error: Error) => {
        toast.error(error.message);
      },
    },
  },
});
```

### 错误边界

```typescript
import { QueryErrorResetBoundary } from 'react-query';
import { ErrorBoundary } from 'react-error-boundary';

function App() {
  return (
    <QueryErrorResetBoundary>
      {({ reset }) => (
        <ErrorBoundary
          onReset={reset}
          fallbackRender={({ error, resetErrorBoundary }) => (
            <div>
              <p>发生错误: {error.message}</p>
              <button onClick={resetErrorBoundary}>重试</button>
            </div>
          )}
        >
          <UserProfile />
        </ErrorBoundary>
      )}
    </QueryErrorResetBoundary>
  );
}
```

## 关键约定

1. 使用 React Query DevTools 检查缓存并跟踪查询状态
2. 将 react-query 钩子分组到功能特定的目录（基于功能的组织）
3. 始终正确处理错误，使用用户友好的消息和重试选项
4. 仅获取所需数据 - 使用 API 参数减少数据传输
5. 避免深层嵌套查询 - 尽可能扁平化以提升性能
6. 使用本地状态处理组件特定数据，全局状态处理共享数据
7. 利用 React Query 的内置缓存和状态管理功能

## 应避免的反模式

- 不要使用 `useEffect` 进行数据获取
- 不要将服务器数据存储在 `useState` 中
- 不要忘记处理加载和错误状态
- 不要创建没有适当缓存失效策略的查询
- 不要忽略条件查询的 `enabled` 选项
- 不要忽略查询响应的 TypeScript 类型
