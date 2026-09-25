# Apollo Server 5.x 指南

Apollo Server 是一个开源的 GraphQL 服务器，可与任何 GraphQL 模式配合使用。Apollo Server 5 是框架无关的，可以独立运行或与 Express、Fastify 和无服务器环境集成。

## 快速入门

### 第 1 步：安装

```bash
npm install @apollo/server graphql
```

对于 Express 集成：

```bash
npm install @apollo/server @as-integrations/express5 express graphql cors
```

### 第 2 步：定义模式

```typescript
const typeDefs = `#graphql
  type Book {
    title: String
    author: String
  }

  type Query {
    books: [Book]
  }
`;
```

### 第 3 步：编写解析器

```typescript
const resolvers = {
  Query: {
    books: () => [
      { title: "了不起的盖茨比", author: "F. Scott Fitzgerald" },
      { title: "1984", author: "George Orwell" },
    ],
  },
};
```

### 第 4 步：启动服务器

**独立运行（推荐用于原型设计）：**

独立服务器非常适合原型设计，但对于生产服务，我们建议将 Apollo Server 与更功能完善的 Web 框架（如 Express、Koa 或 Fastify）集成。从独立服务器切换到 Web 框架后很方便。

```typescript
import { ApolloServer } from "@apollo/server";
import { startStandaloneServer } from "@apollo/server/standalone";

const server = new ApolloServer({ typeDefs, resolvers });

const { url } = await startStandaloneServer(server, {
  listen: { port: 4000 },
});

console.log(`服务器运行在 ${url}`);
```

**Express：**

```typescript
import { ApolloServer } from "@apollo/server";
import { expressMiddleware } from "@as-integrations/express5";
import { ApolloServerPluginDrainHttpServer } from "@apollo/server/plugin/drainHttpServer";
import express from "express";
import http from "http";
import cors from "cors";

const app = express();
const httpServer = http.createServer(app);

const server = new ApolloServer({
  typeDefs,
  resolvers,
  plugins: [ApolloServerPluginDrainHttpServer({ httpServer })],
});

await server.start();

app.use(
  "/graphql",
  cors(),
  express.json(),
  expressMiddleware(server, {
    context: async ({ req }) => ({ token: req.headers.authorization }),
  }),
);

await new Promise<void>((resolve) => httpServer.listen({ port: 4000 }, resolve));
console.log("服务器运行在 http://localhost:4000/graphql");
```

## 模式定义

### 标量类型

- `Int` - 32 位整数
- `Float` - 双精度浮点数
- `String` - UTF-8 字符串
- `Boolean` - true/false
- `ID` - 唯一标识符（序列化为字符串）

### 类型定义

```graphql
type User {
  id: ID!
  name: String!
  email: String
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String
  author: User!
}

input CreatePostInput {
  title: String!
  content: String
}

type Query {
  user(id: ID!): User
  users: [User!]!
}

type Mutation {
  createPost(input: CreatePostInput!): Post!
}
```

### 枚举和接口

```graphql
enum Status {
  草稿
  发布
  归档
}

interface Node {
  id: ID!
}

type Article implements Node {
  id: ID!
  title: String!
}
```

## 解析器概述

解析器遵循以下签名：`(parent, args, contextValue, info)`

- **parent**：来自父解析器的结果（根解析器接收 undefined）
- **args**：传递给字段的参数
- **contextValue**：共享的上下文对象（认证、数据源等）
- **info**：字段特定信息和模式细节（很少使用）

```typescript
const resolvers = {
  Query: {
    user: async (_, { id }, { dataSources }) => {
      return dataSources.usersAPI.getUser(id);
    },
  },
  User: {
    posts: async (parent, _, { dataSources }) => {
      return dataSources.postsAPI.getPostsByAuthor(parent.id);
    },
  },
  Mutation: {
    createPost: async (_, { input }, { dataSources, user }) => {
      if (!user) throw new GraphQLError("未认证");
      return dataSources.postsAPI.create({ ...input, authorId: user.id });
    },
  },
};
```

## 上下文设置

上下文按请求创建，并传递给所有解析器。

```typescript
interface MyContext {
  token?: string;
  user?: User;
  dataSources: {
    usersAPI: UsersDataSource;
    postsAPI: PostsDataSource;
  };
}

const server = new ApolloServer<MyContext>({
  typeDefs,
  resolvers,
});

// 独立运行
const { url } = await startStandaloneServer(server, {
  context: async ({ req }) => ({
    token: req.headers.authorization || "",
    user: await getUser(req.headers.authorization || ""),
    dataSources: {
      usersAPI: new UsersDataSource(),
      postsAPI: new PostsDataSource(),
    },
  }),
});

// Express 中间件
expressMiddleware(server, {
  context: async ({ req, res }) => ({
    token: req.headers.authorization,
    user: await getUser(req.headers.authorization),
    dataSources: {
      usersAPI: new UsersDataSource(),
      postsAPI: new PostsDataSource(),
    },
  }),
});
```

## 参考文件

特定主题的详细文档：

- [解析器](references/resolvers.md) - 解析器模式和最佳实践
- [上下文和认证](references/context-and-auth.md) - 认证和授权
- [插件](references/plugins.md) - 服务器和请求生命周期钩子
- [数据源](references/data-sources.md) - RESTDataSource 和 DataLoader
- [错误处理](references/error-handling.md) - GraphQLError 和错误格式化
- [故障排除](references/troubleshooting.md) - 常见问题和解决方案

## 关键规则

### 模式设计

- 使用 **!**（非空）表示始终有值的字段
- 优先使用输入类型而不是内联参数进行变异
- 使用接口表示多态类型
- 为文档保留模式描述

### 解析器最佳实践

- 保持解析器精简 - 委托给服务/数据源
- 始终显式处理错误
- 使用 DataLoader 批量处理相关查询
- 尽可能返回部分数据（GraphQL 的优势）

### 性能

- 使用 `@defer` 和 `@stream` 处理大型响应
- 实现 DataLoader 解决 N+1 查询
- 考虑为生产环境使用持久化查询
- 在适当的地方使用缓存头和 CDN

## 基本规则

- 始终使用 Apollo Server 5.x 模式（不使用 v4 或更早版本）
- 始终使用 TypeScript 泛型类型化上下文
- 始终使用 `graphql` 包中的 `GraphQLError` 处理错误
- 永远不要在生产错误中暴露堆栈跟踪
- 仅用于原型设计时使用 `startStandaloneServer`
- 对于生产应用，使用与服务器框架（如 Express、Koa、Fastify、Next 等）的集成
- 在上下文中实现认证，在解析器中实现授权
