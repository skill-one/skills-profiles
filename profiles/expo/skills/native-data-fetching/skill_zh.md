# Expo Networking

**你必须使用这项技能来完成任何网络工作，包括 API 请求、数据获取、缓存或网络调试。**

## 参考资料

根据需要查阅这些资源：

```
references/
  expo-router-loaders.md   使用 Expo Router 加载器进行路由级数据加载（web、SDK 55+）
```

## 使用场景

在以下情况下使用这项技能：

- 实现 API 请求
- 设置数据获取（React Query、SWR）
- 使用 Expo Router 数据加载器（`useLoaderData`、web SDK 55+）
- 调试网络故障
- 实现缓存策略
- 处理离线场景
- 身份验证/令牌管理
- 配置 API URL 和环境变量

## 偏好设置

- 避免使用 axios，优先使用 expo/fetch

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
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ["user", userId],
    queryFn: () => fetchUser(userId),
  });

  if (isLoading) return <Loading />;
  if (error) return <Error message={error.message} />;

  return <Profile user={data} />;
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
    mutation.mutate(data);
  };

  return <Form onSubmit={handleSubmit} isLoading={mutation.isPending} />;
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
    // 网络错误（无网络、超时等）
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

### 4. 身份验证

**令牌管理**：

```tsx
import * as SecureStore from "expo-secure-store";

const TOKEN_KEY = "auth_token";

export const auth = {
  getToken: () => SecureStore.getItemAsync(TOKEN_KEY),
  setToken: (token: string) => SecureStore.setItemAsync(TOKEN_KEY, token),
  removeToken: () => SecureStore.deleteItemAsync(TOKEN_KEY),
};

// 带身份验证的 Fetch 封装
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

**检查网络状态**：

```tsx
import NetInfo from "@react-native-community/netinfo";

// 网络状态 Hook
function useNetworkStatus() {
  const [isOnline, setIsOnline] = useState(true);

  useEffect(() => {
    return NetInfo.addEventListener((state) => {
      setIsOnline(state.isConnected ?? true);
    });
  }, []);

  return isOnline;
}
```

**使用 React Query 的离线优先**：

```tsx
import { onlineManager } from "@tanstack/react-query";
import NetInfo from "@react-native-community/netinfo";

// 使 React Query 与网络状态同步
onlineManager.setEventListener((setOnline) => {
  return NetInfo.addEventListener((state) => {
    setOnline(state.isConnected ?? true);
  });
});

// 查询将在离线时暂停，在线时恢复
```

---

### 6. 环境变量

**使用环境变量配置 API**：

Expo 支持以 `EXPO_PUBLIC_` 前缀的环境变量。这些变量在构建时内联，并在 JavaScript 代码中可用。

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

**特定环境的配置**：

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

- 仅以 `EXPO_PUBLIC_` 前缀的环境变量会暴露到客户端包
- 不要将密钥（具有写权限的 API 密钥、数据库密码）放在 `EXPO_PUBLIC_` 变量中——它们会在构建的应用中可见
- 环境变量在**构建时**内联，而不是在运行时
- 修改 `.env` 文件后需要重启开发服务器
- 对于 API 路由中的服务器端密钥，使用不带 `EXPO_PUBLIC_` 前缀的环境变量

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

**卸载时取消**：

```tsx
useEffect(() => {
  const controller = new AbortController();

  fetch(url, { signal: controller.signal })
    .then((response) => response.json())
    .then(setData)
    .catch((error) => {
      if (error.name !== "AbortError") {
        setError(error);
      }
    });

  return () => controller.abort();
}, [url]);
```

**使用 React Query**（自动）：

```tsx
// React Query 会自动取消在查询失效或组件卸载时的请求
```

---

## 决策树

```
用户询问关于网络
  |-- 路由级数据加载（web、SDK 55+）？
  |   \-- Expo Router 加载器 — 查阅 references/expo-router-loaders.md
  |
  |-- 基本fetch？
  |   \-- 使用 fetch API 并进行错误处理
  |
  |-- 需要缓存/状态管理？
  |   |-- 复杂应用 -> React Query (TanStack Query)
  |   \-- 简单需求 -> SWR 或自定义 Hook
  |
  |-- 身份验证？
  |   |-- 令牌存储 -> expo-secure-store
  |   \-- 令牌刷新 -> 实现刷新流程
  |
  |-- 错误处理？
  |   |-- 网络错误 -> 首先检查连接状态
  |   |-- HTTP 错误 -> 解析响应，抛出类型化错误
  |   \-- 重试 -> 指数退避
  |
  |-- 离线支持？
  |   |-- 检查状态 -> NetInfo
  |   \-- 队列请求 -> React Query 持久化
  |
  |-- 环境/API 配置？
  |   |-- 客户端 URL -> .env 中的 EXPO_PUBLIC_ 前缀
  |   |-- 服务器密钥 -> API 路由中非前缀环境变量
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
-> 使用 fetch，包装错误处理

用户："我应该使用 React Query 还是 SWR？"
-> 复杂应用使用 React Query，简单需求使用 SWR

用户："我的应用需要支持离线"
-> 使用 NetInfo 检查状态，使用 React Query 持久化进行缓存

用户："如何处理身份验证令牌？"
-> 存储在 expo-secure-store，实现刷新流程

用户："API 调用很慢"
-> 检查缓存策略，使用 React Query staleTime
用户："如何为开发和生产配置不同的 API URL？"
-> 使用 EXPO*PUBLIC* 环境变量，配合 .env.development 和 .env.production 文件
用户："我的 API 密钥应该放在哪里？"
-> 客户端安全密钥：.env 中的 EXPO*PUBLIC*。密钥：仅在 API 路由中非前缀环境变量

用户："如何在 Expo Router 中为页面加载数据？"
-> 查阅 references/expo-router-loaders.md，使用路由级加载器（web、SDK 55+）。原生使用 React Query 或 fetch。
