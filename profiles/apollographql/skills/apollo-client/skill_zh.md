# Apollo Client 4.x 指南

Apollo Client 是一个用于 JavaScript 的全面状态管理库，它使您能够使用 GraphQL 管理本地和远程数据。4.x 版本带来了改进的缓存、更好的 TypeScript 支持和 React 19 兼容性。

## 集成指南

根据您的应用程序设置选择相应的集成指南：

- **[客户端应用程序](references/integration-client.md)** - 适用于没有 SSR（Vite、Create React App 等）的客户端 React 应用程序
- **[Next.js 应用程序路由器](references/integration-nextjs.md)** - 适用于使用 React 服务器组件的 Next.js 应用程序路由器
- **[React 路由器框架模式](references/integration-react-router.md)** - 适用于具有流式 SSR 的 React 路由器 7 应用程序
- **[TanStack Start](references/integration-tanstack-start.md)** - 适用于具有现代路由的 TanStack Start 应用程序

每个指南都包含安装步骤、配置以及针对该环境的框架特定模式。

## 快速参考

### 基本查询

```tsx
import { gql } from "@apollo/client";
import { useQuery } from "@apollo/client/react";

const GET_USER = gql`
  query GetUser($id: ID!) {
    user(id: $id) {
      id
      name
    }
  }
`;

function UserProfile({ userId }: { userId: string }) {
  const { loading, error, data, dataState } = useQuery(GET_USER, {
    variables: { id: userId },
  });

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error: {error.message}</p>;

  // TypeScript 注意：为了更严格的类型缩小，您也可以在访问数据之前检查 `dataState === "complete"`
  return <div>{data?.user.name}</div>;
}
```

### 基本变异

```tsx
import { gql } from "@apollo/client";
import { useMutation } from "@apollo/client/react";

const CREATE_USER = gql`
  mutation CreateUser($input: CreateUserInput!) {
    createUser(input: $input) {
      id
      name
    }
  }
`;

function CreateUserForm() {
  const [createUser, { loading, error }] = useMutation(CREATE_USER);

  const handleSubmit = async (name: string) => {
    await createUser({ variables: { input: { name } } });
  };

  return <button onClick={() => handleSubmit("John")}>Create User</button>;
}
```

### Suspense 查询

```tsx
import { Suspense } from "react";
import { useSuspenseQuery } from "@apollo/client/react";

function UserProfile({ userId }: { userId: string }) {
  const { data } = useSuspenseQuery(GET_USER, {
    variables: { id: userId },
  });

  return <div>{data.user.name}</div>;
}

function App() {
  return (
    <Suspense fallback={<p>Loading user...</p>}>
      <UserProfile userId="1" />
    </Suspense>
  );
}
```

## 参考文件

特定主题的详细文档：

- [TypeScript 代码生成](references/typescript-codegen.md) - GraphQL 代码生成器设置用于类型安全的操作
- [查询](references/queries.md) - useQuery、useLazyQuery、轮询、refetching
- [Suspense 钩子](references/suspense-hooks.md) - useSuspenseQuery、useBackgroundQuery、useReadQuery、useLoadableQuery
- [变异](references/mutations.md) - useMutation、乐观 UI、缓存更新
- [片段](references/fragments.md) - 片段组合、useFragment、useSuspenseFragment、数据屏蔽
- [缓存](references/caching.md) - InMemoryCache、typePolicies、缓存操作
- [状态管理](references/state-management.md) - 反应式变量、本地状态
- [错误处理](references/error-handling.md) - 错误策略、错误链接、重试
- [故障排除](references/troubleshooting.md) - 常见问题和解决方案

## 关键规则

### 查询最佳实践

- **每个页面通常应该只有一个查询，由组合的片段组成。** 在所有非页面组件中使用 `useFragment` 或 `useSuspenseFragment`。使用 `@defer` 允许折叠下方的慢速字段稍后流式传输，并避免阻塞页面加载。
- **片段用于组合，而不是重用。** 每个片段应该描述特定组件的确切数据需求，而不是在组件之间共享公共字段。有关片段组合和数据屏蔽的详细信息，请参阅 [片段参考](references/fragments.md)。
- 使用非 Suspense 钩子（`useQuery`、`useLazyQuery`）时，始终在 UI 中处理 `loading` 和 `error` 状态。使用 Suspense 钩子（`useSuspenseQuery`、`useBackgroundQuery`）时，React 通过 `<Suspense>` 边界和错误边界处理这些状态。
- 使用 `fetchPolicy` 控制每个查询的缓存行为
- 使用 TypeScript 类型服务器查找函数和选项的文档（Apollo Client 具有广泛的 docblocks）

### 变异最佳实践

- **如果模式允许，变异返回值应该返回更新缓存所需的所有内容。** 既不需要手动更新，也不需要重新获取。
- 如果变异响应不足，请仔细权衡手动缓存操作与重新获取。手动更新有遗漏服务器逻辑的风险。如有必要，考虑使用细粒度重新获取进行乐观更新。
- 在 UI 中优雅地处理错误
- 谨慎使用 `refetchQueries`（优先让缓存自动更新）

### 缓存最佳实践

- 为没有 `id` 字段的类型配置 `keyFields`
- 通过将 `keyFields: false` 设置为不包含标识符且旨在将相关字段组合在父项下的类型来禁用规范化
- 使用 `typePolicies` 进行分页和计算字段
- 了解缓存规范化以调试问题
- **为所有新应用程序启用 [数据屏蔽](references/fragments.md#data-masking)** - 它防止组件访问它们不拥有的片段数据，强制执行适当的数据边界并防止过度渲染

### 性能

- 通过适当的字段选择避免过度获取
- 根据使用情况配置适当的 `fetchPolicy`
- 使用 `@defer` 进行延迟查询部分的增量交付，并使用 `@stream` 进行流式列表字段（`@stream` 在 Apollo Client 4.1+ 中可用）
- **在现代应用程序中优先使用 Suspense 钩子（`useSuspenseQuery`、`useBackgroundQuery`）** 以获得更好的加载状态处理和代码简洁性

## 基本规则

- 始终使用 Apollo Client 4.x 模式（不是 v3 或更早版本）
- 始终用 `ApolloProvider` 包裹您的应用程序
- 使用非 Suspense 钩子时，始终处理加载和错误状态
- 优先在现代应用程序中使用 Suspense 钩子（`useSuspenseQuery`、`useBackgroundQuery`）以获得更好的 DX
- 永远不要将 Apollo Client 存储在 React 状态中（使用模块级或上下文）
- 优先使用 `cache-first` 进行读取密集型数据，使用 `network-only` 进行实时数据
- 使用 TypeScript 以获得更好的 GraphQL 类型安全性
- 实现适当的缓存更新而不是重新获取整个查询
- 当协作调试 Apollo Client问题时，建议指导您查看 Apollo DevTools
