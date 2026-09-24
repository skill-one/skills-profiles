# Convex Create Component

使用清晰边界和精简的应用面向 API 创建可复用的 Convex 组件。

## 何时使用

- 在现有应用中创建新的 Convex 组件
- 将可复用的后端逻辑提取为组件
- 构建需要拥有自身表和工作流的第三方集成
- 打包 Convex 功能，以便在多个应用间复用

## 何时不适用

- 属于主应用自身的临时性业务逻辑
- 不需要 Convex 表和函数的简单工具
- 应保持在 `convex/` 内的应用级编排逻辑
- 使用普通的 TypeScript 库已足够的情况

## 工作流程

1. 询问用户正在构建什么以及最终目标是什么。如果仓库中已使答案显而易见，请明确说明并确认后再继续。
2. 使用下方的决策树选择形态，并阅读对应的参考文件。
3. 判断是否值得使用组件。如果该功能不需要独立的表、后端函数或可复用的持久化状态，则优先选择常规应用代码或普通库。
4. 制定简要计划，包括：
   - 组件所拥有的表
   - 组件对外暴露的公共函数
   - 必须从应用传入的数据（认证、环境变量、父级 ID）
   - 保留在应用中作为包装或 HTTP 挂载的组件
5. 使用 `convex.config.ts`、`schema.ts` 和函数文件创建组件结构。
6. 使用组件自身的 `./_generated/server` 导入实现函数，而非应用生成的文件。
7. 使用 `app.use(...)` 将组件接入应用。如果应用尚不拥有 `convex/convex.config.ts`，则创建它。
8. 通过 `components.<name>` 从应用调用组件，使用 `ctx.runQuery`、`ctx.runMutation` 或 `ctx.runAction`。
9. 如果 React 客户端、HTTP 调用方或公开 API 需要访问，应在应用中创建包装函数，而非直接暴露组件函数。
10. 运行 `npx convex dev`，并在完成前修复代码生成、类型或边界相关的问题。

## 选择形态

询问用户后，选择其中一条路径：

| 目标 | 形态 | 参考 |
| --- | --- | --- |
| 仅为本应用创建的组件 | Local | `references/local-components.md` |
| 发布或跨应用共享 | Packaged | `references/packaged-components.md` |
| 用户明确需要本地与共享库代码 | Hybrid | `references/hybrid-components.md` |
| 不确定 | 默认使用本地 | `references/local-components.md` |

在继续之前，必须只读取一份参考文件。

## 默认方案

除非用户明确要求创建 npm 包，否则默认使用本地组件：

- 将其放在 `convex/components/<componentName>/` 下
- 在自身的 `convex.config.ts` 中使用 `defineComponent(...)` 进行定义
- 在应用的 `convex/convex.config.ts` 中通过 `app.use(...)` 进行安装
- 由 `npx convex dev` 生成组件自身的 `_generated/` 文件

## 组件骨架

一个包含表与两个函数，以及应用接入代码的本地最小化组件。

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
// convex/notifications.ts  (应用侧包装)
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

注意参考路径的形态：`convex/components/notifications/lib.ts` 中的函数在应用侧通过 `components.notifications.lib.send` 调用。

## 关键规则

- 保持认证逻辑在应用侧，因为组件内部无法使用 `ctx.auth`。
- 保持环境访问逻辑在应用侧，因为组件函数无法读取 `process.env`。
- 跨边界传递父应用 ID 时以字符串形式传递，因为应用面向的 `ComponentApi` 中 `Id` 类型会变为普通字符串。
- 不要对应用自有表中的 ID 使用 `v.id("parentTable")` 作为组件参数或 schema 的内容，因为组件无法访问应用表命名空间。
- 从组件的自身 `./_generated/server` 导入 `query`、`mutation` 和 `action`，而非应用生成的文件。
- 不要直接将组件函数暴露给客户端。当需要客户端访问时，创建应用包装函数，因为组件是内部模块，需要应用提供的认证与环境接入逻辑。
- 如果组件定义了 HTTP 处理函数，则在应用的 `convex/http.ts` 中挂载路由，因为组件无法注册自身的 HTTP 路由。
- 如果组件需要分页，请使用来自 `convex-helpers` 的 `paginator`，而非内置的 `.paginate()`，因为 `.paginate()` 无法跨组件边界使用。
- 为查询字段定义索引，而非在数据库查询后使用 Convex 的 `.filter()`。
- 为所有公共组件函数添加 `args` 和 `returns` 验证器，因为组件边界要求明确的类型契约。

## 模式

### 认证与环境访问

```ts
// 错误：组件代码无法依赖应用的认证或环境变量
const identity = await ctx.auth.getUserIdentity();
const apiKey = process.env.OPENAI_API_KEY;
```

```ts
// 正确：应用侧解析认证与环境变量，再显式传递值
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
// 错误：假设组件函数可被客户端直接调用
export const send = components.notifications.send;
```

```ts
// 正确：通过应用侧 mutation 或 query 再重新导出
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

### 边界上的 ID

```ts
// 错误：父应用表的 ID 不是有效的组件验证器
args: {
  userId: v.id("users"),
}
```

```ts
// 正确：在边界处将父应用拥有的 ID 视为字符串
args: {
  userId: v.string(),
}
```

### 高级模式

包含用于回调的函数句柄、从 schema 派生验证器、使用 globals 表进行静态配置以及基于类的客户端包装器等更多模式，请参阅 `references/advanced-patterns.md`。

## 验证

按以下顺序进行验证：

1. `npx convex codegen --component-dir convex/components/<name>`
2. `npx convex codegen`
3. `npx convex dev`

重要说明：

- 全新仓库在配置 `CONVEX_DEPLOYMENT` 之前可能无法成功执行这些命令。
- 在运行代码生成之前，组件本地 `./_generated/*` 的导入和应用侧的 `components.<name>...` 引用无法通过类型检查。
- 如果验证因 Convex 登录或部署设置阻塞，请停止并向用户询问具体步骤，而非自行猜测。

## 参考文件

用户确认目标后，请只阅读以下其中一份：

- `references/local-components.md`
- `references/packaged-components.md`
- `references/hybrid-components.md`

官方文档：[Authoring Components](https://docs.convex.dev/components/authoring)

## 检查清单

- [ ] 已询问用户想构建的内容，并确认了形态
- [ ] 已阅读对应的参考文件
- [ ] 确认组件是正确的抽象方式
- [ ] 已规划表、公共 API、边界与应用包装
- [ ] 组件位于 `convex/components/<name>/` 下（若发布则按包布局）
- [ ] 组件从自身的 `./_generated/server` 导入
- [ ] 认证、环境访问与 HTTP 路由保持在应用侧
- [ ] 父应用 ID 以 `v.string()` 跨边界传递
- [ ] 公共函数已添加 `args` 与 `returns` 验证器
- [ ] 已运行 `npx convex dev` 并修复了代码生成或类型相关的问题
