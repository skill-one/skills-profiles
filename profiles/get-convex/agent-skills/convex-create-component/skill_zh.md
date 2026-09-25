# Convex 创建组件

使用清晰的边界和面向应用的较小 API 创建可重用的 Convex 组件。

## 何时使用

- 在现有应用中创建新的 Convex 组件
- 将可重用的后端逻辑提取到组件中
- 构建应拥有自己的表和工作流的第三方集成
- 打包 Convex 功能以跨多个应用重用

## 何时不使用

- 属于主应用的临时业务逻辑
- 无需 Convex 表或函数的薄工具
- 应保留在 `convex/` 中的应用级编排
- 正常 TypeScript 库就足够的情况

## 工作流程

1. 询问用户正在构建什么以及最终目标是什么。如果存储库已经使答案显而易见，请说明并确认后再继续。
2. 使用下方的决策树选择形状，并阅读匹配的参考文件。
3. 判断是否需要组件。如果功能不需要隔离的表、后端函数或可重用的持久状态，则优先考虑普通应用代码或常规库。
4. 制定简短计划：
   - 组件拥有的表
   - 组件公开的公共函数
   - 从应用中必须传递的数据（认证、环境变量、父级 ID）
   - 应保留在应用中的包装器或 HTTP 挂载
5. 使用 `convex.config.ts`、`schema.ts` 和函数文件创建组件结构。
6. 使用组件自己的 `./_generated/server` 导入实现函数，而不是应用生成的文件。
7. 使用 `app.use(...)` 将组件连接到应用。如果应用还没有 `convex/convex.config.ts`，请创建它。
8. 通过 `components.<name>` 使用 `ctx.runQuery`、`ctx.runMutation` 或 `ctx.runAction` 从应用中调用组件。
9. 如果 React 客户端、HTTP 调用者或公共 API 需要访问，请在应用中创建包装函数，而不是直接暴露组件函数。
10. 在完成之前运行 `npx convex dev` 并修复代码生成、类型或边界问题。

## 选择形状

询问用户，然后选择一条路径：

| 目标                                              | 形状            | 参考                           |
| ------------------------------------------------- | ---------------- | ----------------------------------- |
| 仅此应用使用的组件                               | Local            | `references/local-components.md`    |
| 发布或跨应用共享                                  | Packaged         | `references/packaged-components.md` |
| 用户明确需要本地 + 共享库代码                     | Hybrid           | `references/hybrid-components.md`   |
| 不确定                                          | 默认为本地      | `references/local-components.md`    |

进行下一步之前，请阅读一个参考文件。

## 默认方法

除非用户明确希望 npm 包，否则默认为本地组件：

- 将其放在 `convex/components/<componentName>/`
- 在其自己的 `convex.config.ts` 中使用 `defineComponent(...)` 定义它
- 从应用的 `convex/convex.config.ts` 中使用 `app.use(...)` 安装它
- 让 `npx convex dev` 生成组件自己的 `_generated/` 文件

## 组件骨架

一个包含表和两个函数的最小本地组件，以及应用连接。

```ts
// convex/components/notifications/convex.config.ts
import { defineComponent } from "convex/server";

export default defineComponent("notifications");
```

```ts
// convex/components/notifications/schema.ts
import { defineSchema, defineTable } from "convex/server";
import { v } from "convex/values";

export default defineSchema({
  notifications: defineTable({
    userId: v.string(),
    message: v.string(),
    read: v.boolean(),
  }).index("by_user_read", ["userId", "read"]),
});
```

```ts
// convex/components/notifications/lib.ts
import { v } from "convex/values";
import { mutation, query } from "./_generated/server.js";

export const send = mutation({
  args: { userId: v.string(), message: v.string() },
  returns: v.id("notifications"),
  handler: async (ctx, args) => {
    return await ctx.db.insert("notifications", {
      userId: args.userId,
      message: args.message,
      read: false,
    });
  },
});

export const listUnread = query({
  args: { userId: v.string() },
  returns: v.array(
    v.object({
      _id: v.id("notifications"),
      _creationTime: v.number(),
      userId: v.string(),
      message: v.string(),
      read: v.boolean(),
    }),
  ),
  handler: async (ctx, args) => {
    return await ctx.db
      .query("notifications")
      .withIndex("by_user_read", (q) =>
        q.eq("userId", args.userId).eq("read", false),
      )
      .collect();
  },
});
```

```ts
// convex/convex.config.ts
import { defineApp } from "convex/server";
import notifications from "./components/notifications/convex.config.js";

const app = defineApp();
app.use(notifications);

export default app;
```

```ts
// convex/notifications.ts  (应用侧包装器)
import { v } from "convex/values";
import { mutation, query } from "./_generated/server";
import { components } from "./_generated/api";
import { getAuthUserId } from "@convex-dev/auth/server";

export const sendNotification = mutation({
  args: { message: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    await ctx.runMutation(components.notifications.lib.send, {
      userId,
      message: args.message,
    });
    return null;
  },
});

export const myUnread = query({
  args: {},
  handler: async (ctx) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    return await ctx.runQuery(components.notifications.lib.listUnread, {
      userId,
    });
  },
});
```

注意参考路径形状：`convex/components/notifications/lib.ts` 中的函数作为 `components.notifications.lib.send` 从应用中调用。

## 关键规则

- 将认证保留在应用中，因为 `ctx.auth` 在组件内部不可用。
- 将环境访问保留在应用中，因为组件函数无法读取 `process.env`。
- 将父应用 ID 跨边界作为字符串传递，因为 `Id` 类型在面向应用的 `ComponentApi` 中变为普通字符串。
- 不要在组件参数或模式中使用 `v.id("parentTable")` 来引用应用拥有的表，因为组件无法访问应用的表命名空间。
- 从组件自己的 `./_generated/server` 导入 `query`、`mutation` 和 `action`，而不是应用的生成文件。
- 不要将组件函数直接暴露给客户端。当需要客户端访问时创建应用包装器，因为组件是内部的，需要应用提供的认证/环境连接。
- 如果组件定义了 HTTP 处理程序，请在应用的 `convex/http.ts` 中挂载路由，因为组件无法注册自己的 HTTP 路由。
- 如果组件需要分页，请使用 `convex-helpers` 中的 `paginator` 而不是内置的 `.paginate()`，因为 `.paginate()` 无法跨组件边界工作。
- 为查询字段定义索引，而不是在数据库查询后使用 Convex `.filter()`。
- 为所有公共组件函数添加 `args` 和 `returns` 验证器，因为组件边界需要显式的类型合同。

## 模式

### 认证和环境访问

```ts
// Bad: 组件代码不能依赖应用的认证或环境
const identity = await ctx.auth.getUserIdentity();
const apiKey = process.env.OPENAI_API_KEY;
```

```ts
// Good: 应用解析认证和环境，然后传递显式值
const userId = await getAuthUserId(ctx);
if (!userId) throw new Error("Not authenticated");

await ctx.runAction(components.translator.translate, {
  userId,
  apiKey: process.env.OPENAI_API_KEY,
  text: args.text,
});
```

### 面向客户端的 API

```ts
// Bad: 假设客户端可以直接调用组件函数
export const send = components.notifications.send;
```

```ts
// Good: 通过应用突变或查询重新导出
export const sendNotification = mutation({
  args: { message: v.string() },
  returns: v.null(),
  handler: async (ctx, args) => {
    const userId = await getAuthUserId(ctx);
    if (!userId) throw new Error("Not authenticated");

    await ctx.runMutation(components.notifications.lib.send, {
      userId,
      message: args.message,
    });
    return null;
  },
});
```

### 跨边界的 ID

```ts
// Bad: 父应用表 ID 不是有效的组件验证器
args: {
  userId: v.id("users"),
}
```

```ts
// Good: 在边界处将父拥有的 ID 视为字符串
args: {
  userId: v.string(),
}
```

### 高级模式

有关更多模式，包括用于回调的函数句柄、从模式派生验证器、使用全局表进行静态配置以及基于类的客户端包装器，请参阅 `references/advanced-patterns.md`。

## 验证

按以下顺序尝试验证：

1. `npx convex codegen --component-dir convex/components/<name>`
2. `npx convex codegen`
3. `npx convex dev`

重要：

- 新存储库可能在这些命令失败，直到 `CONVEX_DEPLOYMENT` 配置完成。
- 在代码生成运行之前，组件本地 `./_generated/*` 导入和应用侧 `components.<name>...` 引用将不会类型检查。
- 如果验证在 Convex 登录或部署设置上阻塞，请停止并要求用户提供该确切步骤，而不是猜测。

## 参考文件

用户确认目标后，阅读以下其中一个：

- `references/local-components.md`
- `references/packaged-components.md`
- `references/hybrid-components.md`

官方文档：
[编写组件](https://docs.convex.dev/components/authoring)

## 检查清单

- [ ] 询问用户他们想构建什么并确认了形状
- [ ] 阅读了匹配的参考文件
- [ ] 确认组件是正确的抽象
- [ ] 规划了表、公共 API、边界和应用包装器
- [ ] 组件位于 `convex/components/<name>/`（如果发布则为包布局）
- [ ] 组件从自己的 `./_generated/server` 导入
- [ ] 认证、环境访问和 HTTP 路由保留在应用中
- [ ] 父应用 ID 跨边界作为 `v.string()` 传递
- [ ] 公共函数有 `args` 和 `returns` 验证器
- [ ] 运行 `npx convex dev` 并修复代码生成或类型问题
