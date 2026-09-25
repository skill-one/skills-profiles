# Expo Networking

**你必须在任何网络工作中使用这项技能，包括 API 请求、数据获取、缓存或网络调试。**

## 参考资料

按需查阅这些资源：

```
references/
  expo-router-loaders.md        使用 Expo Router 路由级数据加载（web、SDK 55+）
  offline-and-cancellation.md   NetInfo 网络状态、离线优先 React Query、AbortController
```

## 使用场景

在以下情况下使用这项技能：

- 实现 API 请求
- 设置数据获取（React Query、SWR）
- 使用 Expo Router 数据加载器（`useLoaderData`，web SDK 55+）
- 调试网络故障
- 实现缓存策略
- 处理离线场景
- 身份验证/令牌管理
- 配置 API URL 和环境变量

## 偏好设置

- 避免 axios，优先使用 expo/fetch

## 每个屏幕都有四种状态

为加载数据的屏幕设计 **加载中**、**错误**、**空** 和 **内容**。这些状态可以重叠：刷新错误应与缓存的內容共存。

- **加载中 ≠ 空。** 空表示 *解析为没有条目*，不是数据缺失。在检查列表长度之前，处理初始加载、失败和预取。在 TanStack Query v5 中，`isLoading` 表示第一个请求正在运行；一个禁用或离线暂停的查询可以没有数据而不处于加载中。在这种情况下，显示先决条件或离线状态。
- **空是一个设计状态，不是空白列表。** 在 FlatList/FlashList 上使用 `ListEmptyComponent`：解释为什么它是空的，并提供相关的下一步操作。可以提供“还没有条目”；“没有结果”应提供更改或清除搜索/筛选。
- **刷新会保留过时的內容。** 即使刷新失败，也要渲染缓存的 `data`，带有非阻塞错误和重试。使用 `isLoading` 用于第一个请求的旋转器，使用 `isFetching` 用于后台活动；对于具有已知布局的慢速初始加载，优先使用骨架屏，使用 `RefreshControl` 用于用户发起的刷新。
- **预取控制。** 当初始 UI 或重定向依赖于持久化状态（认证令牌、引导标志）时，根布局在状态加载之前不渲染任何内容——或启动画面。未预取状态闪烁在每次冷启动时显示错误的屏幕，并错误地路由在预取之前到达的深层链接。

**保存可保留工作。** 在等待突变期间，禁用重复提交。失败时，保留草稿，显示内联错误，并允许用户重试；成功后才能清除或关闭。如果乐观更新，失败时恢复以前的值或标记编辑为未同步。通过失败的保存后重试来验证。

## 常见问题及解决方案

### 1. 基本 Fetch 使用

**简单的 GET 请求**：

```tsx
const fetchUser = async (userId: string) => {
  const response = await fetch(`https://api.example.com/users/${userId}`);

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};
```

**带请求体的 POST 请求**：

```tsx
const createUser = async (userData: UserData) => {
  const response = await fetch("https://api.example.com/users", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(userData),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message);
  }

  return response.json();
};
```

---

### 2. React Query (TanStack Query)

**设置**：

```tsx
// app/_layout.tsx
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 分钟
      retry: 2,
    },
  },
});

export default function RootLayout() {
  return (
    <QueryClientProvider client={queryClient}>
      <Stack />
    </QueryClientProvider>
  );
}
```

**获取数据**：

```tsx
import { useQuery } from "@tanstack/react-query";

function UserProfile({ userId }: { userId: string }) {
  const { data, fetchStatus, error, refetch } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetchUser(userId),
  });

  if (data === undefined) {
    if (error) return <ErrorState message={error.message} onRetry={() => refetch()} />;
    if (fetchStatus === "paused") return <OfflineState />;
    return <Loading />;
  }

  return (
    <>
      {error && <InlineError message="无法刷新。显示保存的数据。" onRetry={() => refetch()} />}
      {data === null ? <EmptyState message="用户未找到" /> : <Profile user={data} />}
    </>
  );
}
```

**突变**：

```tsx
import { useMutation, useQueryClient } from "@tanstack/react-query";

function CreateUserForm() {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: createUser,
    onSuccess: () => {
      // 使查询失效并重新获取
      queryClient.invalidateQueries({ queryKey: ["users"] });
    },
  });

  const handleSubmit = (data: UserData) => {
    if (mutation.isPending) return;
    mutation.mutate(data);
  };

  // 表单在错误时保留其草稿，并在 isLoading 时禁用提交。
  return <Form onSubmit={handleSubmit} isLoading={mutation.isPending} error={mutation.error?.message} />;
}
```

---

### 3. 错误处理

**全面的错误处理**：

```tsx
class ApiError extends Error {
  constructor(message: string, public status: number, public code?: string) {
    super(message);
    this.name = "ApiError";
  }
}

const fetchWithErrorHandling = async (url: string, options?: RequestInit) => {
  try {
    const response = await fetch(url, options);

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new ApiError(
        error.message || "请求失败",
        response.status,
        error.code
      );
    }

    return response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    // 网络错误（没有互联网、超时等）
    throw new ApiError("网络错误", 0, "NETWORK_ERROR");
  }
};
```

**重试逻辑**：

```tsx
const fetchWithRetry = async (
  url: string,
  options?: RequestInit,
  retries = 3
) => {
  for (let i = 0; i < retries; i++) {
    try {
      return await fetchWithErrorHandling(url, options);
    } catch (error) {
      if (i === retries - 1) throw error;
      // 指数退避
      await new Promise((r) => setTimeout(r, Math.pow(2, i) * 1000));
    }
  }
};
```

---

### 4. 认证

**令牌管理**：

```tsx
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "auth_token";

export const auth = {
  getToken: () => SecureStore.getItemAsync(TOKEN_KEY),
  setToken: (token: string) => SecureStore.setItemAsync(TOKEN_KEY, token),
  removeToken: () => SecureStore.deleteItemAsync(TOKEN_KEY),
};

// 认证封装的 fetch
const authFetch = async (url: string, options: RequestInit = {}) => {
  const token = await auth.getToken();

  return fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      Authorization: token ? `Bearer ${token}` : "",
    },
  });
};
```

**令牌刷新**：

```tsx
let isRefreshing = false;
let refreshPromise: Promise<string> | null = null;

const getValidToken = async (): Promise<string> => {
  const token = await auth.getToken();

  if (!token || isTokenExpired(token)) {
    if (!isRefreshing) {
      isRefreshing = true;
      refreshPromise = refreshToken().finally(() => {
        isRefreshing = false;
        refreshPromise = null;
      });
    }
    return refreshPromise!;
  }

  return token;
};
```

---

### 5. 离线支持

使用 NetInfo 检测网络状态和离线优先 React Query 设置：参见 [./references/offline-and-cancellation.md](./references/offline-and-cancellation.md)。

---

### 6. 环境变量

**使用环境变量配置 API**：

Expo 支持以 `EXPO_PUBLIC_` 前缀的环境变量。它们在构建时内联，并在 JavaScript 代码中可用。

```tsx
// .env
EXPO_PUBLIC_API_URL=https://api.example.com
EXPO_PUBLIC_API_VERSION=v1

// 代码中使用
const API_URL = process.env.EXPO_PUBLIC_API_URL;

const fetchUsers = async () => {
  const response = await fetch(`${API_URL}/users`);
  return response.json();
};
```

**特定环境配置**：

```tsx
// .env.development
EXPO_PUBLIC_API_URL=http://localhost:3000

// .env.production
EXPO_PUBLIC_API_URL=https://api.production.com
```

**使用环境配置创建 API 客户端**：

```tsx
// api/client.ts
const BASE_URL = process.env.EXPO_PUBLIC_API_URL;

if (!BASE_URL) {
  throw new Error("EXPO_PUBLIC_API_URL is not defined");
}

export const apiClient = {
  get: async <T,>(path: string): Promise<T> => {
    const response = await fetch(`${BASE_URL}${path}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },

  post: async <T,>(path: string, body: unknown): Promise<T> => {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  },
};
```

**重要说明**：

- 只有以 `EXPO_PUBLIC_` 前缀的变量才会暴露给客户端包
- 不要将密钥（具有写权限的 API 密钥、数据库密码）放在 `EXPO_PUBLIC_` 变量中——它们在构建的应用中可见
- 环境变量在**构建时**内联，不是在运行时
- 更改 `.env` 文件后，需要重启开发服务器
- 对于 API 路由中的服务器端密钥，使用不带 `EXPO_PUBLIC_` 前缀的变量

**TypeScript 支持**：

```tsx
// types/env.d.ts
declare global {
  namespace NodeJS {
    interface ProcessEnv {
      EXPO_PUBLIC_API_URL: string;
      EXPO_PUBLIC_API_VERSION?: string;
    }
  }
}

export {};
```

---

### 7. 请求取消

在卸载时使用 AbortController（React Query 会自动取消）：参见 [./references/offline-and-cancellation.md](./references/offline-and-cancellation.md)。

---

## 决策树

```
用户询问关于网络
  |-- 路由级数据加载（web、SDK 55+）？
  |   \-- Expo Router 加载器 — 参见 references/expo-router-loaders.md
  |
  |-- 基本 fetch？
  |   \-- 使用 fetch API 并进行错误处理
  |
  |-- 需要缓存/状态管理？
  |   |-- 复杂应用 -> React Query (TanStack Query)
  |   \-- 简单需求 -> SWR 或自定义钩子
  |
  |-- 认证？
  |   |-- 令牌存储 -> expo-secure-store
  |   \-- 令牌刷新 -> 实现刷新流程
  |
  |-- 错误处理？
  |   |-- 网络错误 -> 首先检查连接性
  |   |-- HTTP 错误 -> 解析响应，抛出类型化的错误
  |   \-- 重试 -> 指数退避
  |
  |-- 离线支持？
  |   |-- 检查状态 -> NetInfo
  |   \-- 队列请求 -> React Query 持久化
  |
  |-- 环境/API 配置？
  |   |-- 客户端 URL -> .env 中的 EXPO_PUBLIC_ 前缀
  |   |-- 服务器密钥 -> 仅 API 路由的非前缀环境变量
  |   \-- 多个环境 -> .env.development、.env.production
  |
  \-- 性能？
      |-- 缓存 -> React Query 的 staleTime
      |-- 去重 -> React Query 会处理
      \-- 取消 -> AbortController 或 React Query
```

## 常见错误

**错误：没有错误处理**

```tsx
const data = await fetch(url).then((r) => r.json());
```

**正确：检查响应状态**

```tsx
const response = await fetch(url);
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const data = await response.json();
```

**错误：在 AsyncStorage 中存储令牌**

```tsx
await AsyncStorage.setItem("token", token); // 不安全！
```

**正确：使用 SecureStore 存储敏感数据**

```tsx
await SecureStore.setItemAsync("token", token);
```

## 示例调用

用户："如何在 React Native 中进行 API 调用？"
-> 使用 fetch，封装错误处理

用户："我应该使用 React Query 还是 SWR？"
-> React Query 用于复杂应用，SWR 用于简单需求

用户："我的应用需要支持离线"
-> 使用 NetInfo 检测状态，React Query 持久化用于缓存

用户："如何处理认证令牌？"
-> 存储在 expo-secure-store，实现刷新流程

用户："API 调用很慢"
-> 检查缓存策略，使用 React Query staleTime
用户："如何为开发和生产配置不同的 API URL？"
-> 使用 `EXPO_PUBLIC_` 环境变量和 .env.development、.env.production 文件
用户："我的 API 密钥应该放在哪里？"
-> 客户端安全的密钥：.env 中的 `EXPO_PUBLIC_`。密钥：仅在 API 路由中使用的非前缀环境变量

用户："如何在 Expo Router 中为页面加载数据？"
-> 参见 references/expo-router-loaders.md，用于路由级加载器（web、SDK 55+）。对于原生，使用 React Query 或 fetch。

## 提交反馈
如果你在技能中遇到错误、误导性或过时的信息，请报告以便 Expo 改进：
```bash
npx --yes submit-expo-feedback@latest --category skills --subject "expo-data-fetching" "<可操作的反馈>"
```
只有当你有具体且可操作的反馈时才提交。尽可能提供相关的上下文。
如果 AI 代理反复失败或用户不得不接管 Expo 任务，加载 expo-skill-feedback 技能并遵循其 eval-candidate 流程，而不是重复使用上面的命令。
