# GraphQL 操作指南

本指南涵盖了客户端开发者编写 GraphQL 操作（查询、变更、订阅）的最佳实践。编写良好的操作是高效的、类型安全的且易于维护的。

## 操作基础

### 查询结构

```graphql
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
  }
}
```

### 变更结构

```graphql
mutation CreatePost($input: CreatePostInput!) {
  createPost(input: $input) {
    id
    title
    createdAt
  }
}
```

### 订阅结构

```graphql
subscription OnMessageReceived($channelId: ID!) {
  messageReceived(channelId: $channelId) {
    id
    content
    sender {
      id
      name
    }
  }
}
```

## 快速参考

### 操作命名

| 模式      | 示例                                     |
| ------------ | ------------------------------------------- |
| 查询        | `GetUser`, `ListPosts`, `SearchProducts`    |
| 变更     | `CreateUser`, `UpdatePost`, `DeleteComment` |
| 订阅      | `OnMessageReceived`, `OnUserStatusChanged`  |

### 变量语法

```graphql
# 必填变量
query GetUser($id: ID!) { ... }

# 可选变量带默认值
query ListPosts($first: Int = 20) { ... }

# 多个变量
query SearchPosts($query: String!, $status: PostStatus, $first: Int = 10) { ... }
```

### 片段语法

```graphql
# 定义片段
fragment UserBasicInfo on User {
  id
  name
  avatarUrl
}

# 使用片段
query GetUser($id: ID!) {
  user(id: $id) {
    ...UserBasicInfo
    email
  }
}
```

### 指令

```graphql
query GetUser($id: ID!, $includeEmail: Boolean!) {
  user(id: $id) {
    id
    name
    email @include(if: $includeEmail)
  }
}

query GetPosts($skipDrafts: Boolean!) {
  posts {
    id
    title
    draft @skip(if: $skipDrafts)
  }
}
```

## 关键原则

### 1. 仅请求所需内容

```graphql
# 良好：特定字段
query GetUserName($id: ID!) {
  user(id: $id) {
    id
    name
  }
}

# 避免：过度获取
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
    email
    bio
    posts {
      id
      title
      content
      comments {
        id
      }
    }
    followers {
      id
      name
    }
    # ... 许多未使用的字段
  }
}
```

### 2. 为所有操作命名

```graphql
# 良好：命名操作
query GetUserPosts($userId: ID!) {
  user(id: $userId) {
    posts {
      id
      title
    }
  }
}

# 避免：匿名操作
query {
  user(id: "123") {
    posts {
      id
      title
    }
  }
}
```

### 3. 使用变量而非内联值

```graphql
# 良好：变量
query GetUser($id: ID!) {
  user(id: $id) {
    id
    name
  }
}

# 避免：硬编码值
query {
  user(id: "123") {
    id
    name
  }
}
```

### 4. 将片段与组件放在一起

```tsx
// UserAvatar.tsx
export const USER_AVATAR_FRAGMENT = gql`
  fragment UserAvatar on User {
    id
    name
    avatarUrl
  }
`;

function UserAvatar({ user }) {
  return <img src={user.avatarUrl} alt={user.name} />;
}
```

## 参考文件

特定主题的详细文档：

- [查询](references/queries.md) - 查询模式和优化
- [变更](references/mutations.md) - 变更模式和错误处理
- [片段](references/fragments.md) - 片段组织和复用
- [变量](references/variables.md) - 变量使用和类型
- [工具](references/tooling.md) - 代码生成和代码检查

## 基本规则

- 始终为操作命名（不允许匿名查询/变更）
- 始终使用变量处理动态值
- 始终仅请求所需的字段
- 始终为可缓存类型包含 `id` 字段
- 永远不在操作中硬编码值
- 永远不在文件间重复字段选择
- 优先使用片段处理可复用的字段选择
- 优先将片段与组件放在一起
- 使用描述性的操作名称反映其目的
- 使用 `@include`/`@skip` 处理条件字段
