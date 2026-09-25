# Convex 认证设置

在 Convex 中实现安全的认证，包括用户管理和访问控制。

## 何时使用

- 首次设置认证
- 实现用户管理（用户表、身份映射）
- 创建认证辅助函数
- 设置认证提供者（Convex Auth、Clerk、WorkOS AuthKit、Auth0、自定义 JWT）

## 何时不使用

- 非 Convex 后端的认证
- 没有 Convex 实现的纯 OAuth/OIDC 文档
- 调试偶然出现在认证代码附近的不相关错误
- 认证提供者已完全配置，用户只需要修复一行代码

## 第一步：选择认证提供者

Convex 支持多种认证方法。不要假设提供者。

在编写设置代码之前：

1. 询问用户他们想要的认证解决方案，除非存储库已经使其显而易见
2. 如果存储库已经使用提供者，则继续使用该提供者，除非用户想切换
3. 如果用户尚未选择提供者且存储库没有使其显而易见，则在继续之前询问

常见选项：

- [Convex Auth](https://docs.convex.dev/auth/convex-auth) - 当用户希望直接在 Convex 中处理认证时是好的默认选择
- [Clerk](https://docs.convex.dev/auth/clerk) - 当应用程序已经使用 Clerk 或用户希望使用 Clerk 的托管认证功能时使用
- [WorkOS AuthKit](https://docs.convex.dev/auth/authkit/) - 当应用程序已经使用 WorkOS 或用户希望使用 AuthKit 时使用
- [Auth0](https://docs.convex.dev/auth/auth0) - 当应用程序已经使用 Auth0 时使用
- 自定义 JWT 提供者 - 当集成上述未涵盖的现有认证系统时使用

在询问之前在存储库中寻找信号：

- 依赖项，例如 `@clerk/*`、`@workos-inc/*`、`@auth0/*` 或 Convex Auth 包
- 现有文件，例如 `convex/auth.config.ts`、认证中间件、提供者包装器或登录组件
- 明确指向提供者的环境变量

## 选择提供者后

阅读提供者的官方指南和匹配的本地参考文件：

- Convex Auth: [官方文档](https://docs.convex.dev/auth/convex-auth)，然后 `references/convex-auth.md`
- Clerk: [官方文档](https://docs.convex.dev/auth/clerk)，然后 `references/clerk.md`
- WorkOS AuthKit: [官方文档](https://docs.convex.dev/auth/authkit/)，然后 `references/workos-authkit.md`
- Auth0: [官方文档](https://docs.convex.dev/auth/auth0)，然后 `references/auth0.md`

本地参考文件包含具体的工作流程、预期的文件和环境变量、易错点和验证检查。

使用这些资源进行：

- 包安装
- 客户端提供者连接
- 环境变量
- `convex/auth.config.ts` 设置
- 登录和登出 UI 模式
- React、Vite 或 Next.js 的特定框架设置

对于共享认证行为，使用官方 Convex 文档作为事实来源：

- [在函数中认证](https://docs.convex.dev/auth/functions-auth) 用于 `ctx.auth.getUserIdentity()`
- [在 Convex 数据库中存储用户](https://docs.convex.dev/auth/database-auth) 用于可选的应用级用户存储
- [认证](https://docs.convex.dev/auth) 用于一般的认证和授权指南
- [Convex Auth 授权](https://labs.convex.dev/auth/authz) 当提供者是 Convex Auth 时

优先使用官方文档而不是回忆步骤，因为提供者 CLI 和 Convex Auth 内部在不同版本之间会发生变化。从记忆中发明设置有风险使用过时的模式。对于第三方提供者，只有在应用程序确实需要在 Convex 中需要用户文档时才添加应用级用户存储。并非每个应用程序都需要 `users` 表。对于 Convex Auth，请遵循 Convex Auth 文档和内置认证表，而不是添加一个并行的 `users` 表加上 `storeUser` 流程，因为 Convex Auth 已经内部管理用户记录。在运行提供者初始化命令后，验证生成的文件并完成提供者参考中调用的后初始化连接步骤。初始化命令很少完成整个集成。

## 核心模式：保护后端函数

最常见的认证任务是检查 Convex 函数中的身份。

```ts
// 不良：信任客户端提供的 userId
export const getMyProfile = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.userId);
  },
});
```

```ts
// 良好：在服务器端验证身份
export const getMyProfile = query({
  args: {},
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity();
    if (!identity) throw new Error("未认证");

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

1. 通过询问用户或从存储库中推断来确定提供者
2. 询问用户是否现在想要本地仅设置或生产就绪设置
3. 阅读匹配的提供者参考文件
4. 遵循官方提供者文档以获取当前设置详细信息
5. 遵循官方 Convex 文档以获取共享后端认证行为、用户存储和授权模式
6. 只有在文档和应用程序需求要求时才添加应用级用户存储
7. 仅在应用程序需要时添加所有权、角色或团队访问的授权检查
8. 如果需要，验证登录状态、受保护的查询、环境变量和生产配置

如果流程在交互式提供者或部署设置上阻塞，请明确要求用户提供所需的确切手动步骤，然后在他们完成后继续。对于面向 UI 的认证流程，在设置完成后提供验证真实注册或登录流程的机会。如果环境有浏览器自动化工具，您可以使用它们。如果没有，请给用户提供一个简短的手动验证清单。

## 参考文件

### 提供者参考

- `references/convex-auth.md`
- `references/clerk.md`
- `references/workos-authkit.md`
- `references/auth0.md`

## 清单

- [ ] 在编写设置代码之前选择了正确的认证提供者
- [ ] 阅读了相关的提供者参考文件
- [ ] 询问用户是否想要本地仅设置或生产就绪设置
- [ ] 使用了官方提供者文档进行提供者特定连接
- [ ] 使用了官方 Convex 文档进行共享认证行为和授权模式
- [ ] 只有在应用程序实际上需要时才添加了应用级用户存储
- [ ] 没有为 Convex Auth 发明跨提供者的 `users` 表或 `storeUser` 流程
- [ ] 在受保护的后端函数中添加了认证检查
- [ ] 在应用程序实际需要的地方添加了授权检查
- [ ] 清晰的错误消息（"未认证"、"未授权"）
- [ ] 为所选提供者配置了客户端认证提供者
- [ ] 如果需要，也涵盖了生产认证设置
