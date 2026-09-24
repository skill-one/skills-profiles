# Convex 认证设置

在 Convex 中实现带有用户管理和访问控制的安全认证。

## 何时使用

- 首次设置认证
- 实现用户管理（用户表、身份映射）
- 创建认证辅助函数
- 设置认证提供商（Convex Auth、Clerk、WorkOS AuthKit、Auth0、自定义 JWT）

## 何时不使用

- 为非 Convex 后端提供认证
- 不包含 Convex 实现的纯 OAuth/OIDC 文档
- 调试与认证代码无关但碰巧在认证代码附近出现的 bug
- 认证提供商已完全配置，用户只需一行修复

## 第一步：选择认证提供商

Convex 支持多种认证方式。不要先入为主地假设某个提供商。

编写设置代码之前：

1. 询问用户希望使用哪种认证方案，除非该仓库已明确显示。
2. 如果仓库已使用某个提供商，除非用户想更换，则继续使用该提供商。
3. 如果用户尚未选择提供商且仓库未明确显示，在继续前进行询问。

常见选项：

- [Convex Auth](https://docs.convex.dev/auth/convex-auth) - 当用户希望直接在 Convex 中处理认证时的良好默认选项
- [Clerk](https://docs.convex.dev/auth/clerk) - 当应用已使用 Clerk 或用户希望使用 Clerk 的托管认证功能时使用
- [WorkOS AuthKit](https://docs.convex.dev/auth/authkit/) - 当应用已使用 WorkOS 或用户希望专门使用 AuthKit 时使用
- [Auth0](https://docs.convex.dev/auth/auth0) - 当应用已使用 Auth0 时使用
- 自定义 JWT 提供商 - 当需要集成上述未涵盖的现有认证系统时使用

在询问前检查仓库中的信号：

- 依赖项，如 `@clerk/*`、`@workos-inc/*`、`@auth0/*` 或 Convex Auth 包
- 现有文件，如 `convex/auth.config.ts`、认证中间件、提供商包装器或登录组件
- 明确指向某个提供商的环境变量

## 选择提供商之后

阅读提供商的官方指南和对应的本地参考文件：

- Convex Auth：[官方文档](https://docs.convex.dev/auth/convex-auth)，然后阅读 `references/convex-auth.md`
- Clerk：[官方文档](https://docs.convex.dev/auth/clerk)，然后阅读 `references/clerk.md`
- WorkOS AuthKit：[官方文档](https://docs.convex.dev/auth/authkit/)，然后阅读 `references/workos-authkit.md`
- Auth0：[官方文档](https://docs.convex.dev/auth/auth0)，然后阅读 `references/auth0.md`

本地参考文件包含具体的业务流程、预期文件、环境变量、常见陷阱与验证检查项。

使用以下来源：

- 包安装
- 客户端提供商配置
- 环境变量
- `convex/auth.config.ts` 的设置
- 登录和登出 UI 模式
- React、Vite 或 Next.js 的框架特定设置

对于共享的认证行为，以官方 Convex 文档作为权威来源：

- [Functions 中的认证](https://docs.convex.dev/auth/functions-auth) 用于 `ctx.auth.getUserIdentity()`
- [在 Convex 数据库中使用用户](https://docs.convex.dev/auth/database-auth) 用于可选的应用级用户存储
- [认证](https://docs.convex.dev/auth) 用于一般认证和授权指导
- [Convex Auth 授权](https://labs.convex.dev/auth/authz) 当提供商为 Convex Auth 时使用

优先使用官方文档而非凭记忆的步骤，因为提供商 CLI 和 Convex Auth 内部机制在不同版本间会发生变化。凭记忆编造设置可能存在过时的模式。对于第三方提供商，仅当应用确实需要在 Convex 中添加用户文档时，才添加应用级用户存储。并非所有应用都需要 `users` 表。对于 Convex Auth，请遵循 Convex Auth 文档和内置认证表，而不是添加平行的 `users` 表及 `storeUser` 流程，因为 Convex Auth 已内部管理用户记录。在运行提供商初始化命令后，验证生成的文件，并完成提供商参考文件中指出的初始化后配置步骤。初始化命令通常无法完成整个集成。

## 核心模式：保护后端函数

最常见的认证任务是检查 Convex 函数中的身份。

```ts
// 错误：信任客户端提供的 userId
export const getMyProfile = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.userId);
  },
});
```

```ts
// 正确：服务端验证身份
export const getMyProfile = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("Not authenticated");

    return await ctx.db
      .query("users")
      .withIndex("by_tokenIdentifier", (q) =>
        q.eq("tokenIdentifier", identity.tokenIdentifier),
      )
      .unique();
  },
});
```

## 工作流程

1. 通过询问用户或根据仓库推断来确定提供商
2. 询问用户是否需要现在进行仅本地设置，还是准备生产环境就绪的设置
3. 阅读匹配的提供商参考文件
4. 按照官方提供商文档了解当前的设置详情
5. 按照官方 Convex 文档了解共享的后端认证行为、用户存储和授权模式
6. 仅在文档与应用要求需要时添加应用级用户存储
7. 仅在应用需要时，为所有权、角色或团队访问添加授权检查
8. 如需，验证登录状态、受保护查询、环境变量和生产配置

如果流程因交互式的提供商或部署设置而阻塞，请明确询问用户所需的准确人工步骤，并在用户完成后继续。对于面向 UI 的认证流程，设置完成后，可以提供验证实际注册或登录流程的协助。如果环境有浏览器自动化工具，可以使用它们。如果没有，则提供简短的人工验证清单。

## 参考文件

### 提供商参考

- `references/convex-auth.md`
- `references/clerk.md`
- `references/workos-authkit.md`
- `references/auth0.md`

## 检查清单

- [ ] 在编写设置代码前选择了正确的认证提供商
- [ ] 阅读了相关的提供商参考文件
- [ ] 询问了用户是否需要仅本地设置还是生产环境就绪的设置
- [ ] 使用了官方提供商文档为提供商特定配置
- [ ] 使用了官方 Convex 文档为共享认证行为和授权模式
- [ ] 仅在实际需要时添加了应用级用户存储
- [ ] 未为 Convex Auth 编造跨提供商的 `users` 表或 `storeUser` 流程
- [ ] 在受保护的后端函数中添加了认证检查
- [ ] 在实际需要时添加了授权检查
- [ ] 错误消息清晰（如 "Not authenticated"、"Unauthorized"）
- [ ] 为所选提供商配置了客户端认证提供商
- [ ] 如需要，已涵盖生产环境认证设置
