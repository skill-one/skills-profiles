<!-- 由 convex-agents content/capabilities/quickstart.json 生成 — 请勿手工编辑。 -->

# 快速开始：一个极简的 Convex 模板，正在运行

从想法出发，在本地使用匿名开发部署，搭建一个极简的 Next.js + Convex 模板。设计上力求极简：本地开发服务器，无需发布步骤，无需预置的认证。

## 工作流

1. 运行配方 `quickstart-recipe@^2`，并传入 {idea, template}（该包会获取并缓存它；提供固定的离线回退方案）。它会创建项目、安装依赖、启动后端（匿名）和 Web 开发服务器。
2. 当它打印出开发 URL 时，为用户打开它。
3. 在基于模板构建额外功能之前，提出简要计划并确认。

## 规则

- 如果该配方已报告成功，切勿重复运行。
- 将 `convex/` 下的任何代码委托给 `convex-expert` 能力。
- 切勿添加 Postgres/Redis/Express —— 使用 Convex 原语。
- 切勿在此处添加托管/发布或预置的认证 —— 保持模板极简，除非用户要求更多。
- **降级规则** — 如果脚手架无法运行（非交互式会话、无网络、沙盒临时目录，或用户仅需代码而非应用）：跳过该配方，直接编写标准的 Convex 项目。所有后端代码必须放在 `convex/` 目录下（schema.ts、functions）——绝不能放在项目根目录；Convex 函数只能从 `convex/` 目录运行。除非明确要求，否则编写零个脚手架/文档文件（无需 START_HERE.md、ARCHITECTURE.md、MANIFEST.txt、README walls）。“为我构建后端”指的是代码，而非繁文缛节。
- **数据访问与导入** —— 在编写任何 `convex/*.ts` 文件之前，切勿对可增长的表执行无界 `.collect()` —— 使用 `.withIndex(...)` 和 `.paginate(...)`/`.take(n)`。对于任何会被写成 SQL WHERE 的逻辑，使用索引而非 `.filter()`。`.withIndex(...)` 回调仅支持 `eq`/`gt`/`gte`/`lt`/`lte` —— 没有 `.range(...)` 方法。导入：`query`/`mutation`/`action`/`internalQuery`/`internalMutation`/`internalAction` 来自 `./_generated/server`；`api`/`internal` 来自 `./_generated/api`；在应用代码中永远不要从 `convex/server` 导入。对于固定的字符串/枚举成员，使用 `v.literal("exact value")`，而非裸字符串。`"use node"` 仅出现在仅包含 action 的模块顶部 —— 永远不要在任何同时导出 `query` 或 `mutation` 的文件中使用。永远不要在缺少 `"use node"` 的文件中导入 Node 内置模块（`crypto`/`fs`/`path`/`http`/`child_process`/`os`，无论是否带 `node:` 前缀）——包括 `http.ts` 路由处理程序；在可能的情况下，使用 Web Crypto（`crypto.subtle`）而非导入 `crypto`。
- **保留名称** —— 切勿将 `export const <jsReservedWord>` = ...（例如 `delete`、`new`、`class`、`function`、`return`）作为 query/mutation/action 的导出名称；esbuild 无法解析它。切勿使用以下划线 `_` 开头的表名或索引名（例如 `_migrations: defineTable(...)`）——`_` 为保留字符，在推送时会报错为 `TableNameReserved`/`IndexNameReserved`。
- **HTTP 路由** —— `httpRouter` 不支持 Express 风格的 `:param` 段（`path: "/users/:id"` 仅匹配该字面字符串且属于无效代码）；使用 `pathPrefix` 并自行解析末尾的段。每个 `http.route({...})` 中的 `handler:` 都必须用 `./_generated/server` 中的 `httpAction(...)` 进行包装 —— 简单的 `async (ctx, request) => {...}` 类型检查通过，但不是有效的 HTTP 动作。
- `ctx.runQuery`/`ctx.runMutation`/`ctx.runAction` 需要代码生成的函数引用（`api.foo.bar`/`internal.foo.bar`），绝不能使用原始导入的模块成员（`import * as queries from "./queries"; ctx.runQuery(queries.getX, ...)` 虽能编译但在运行时会失败）。
- **自检规则** —— 在声明后端工作已完成之前，验证其能够编译并推送到部署环境：运行 `npx tsc --noEmit` 并将其推送到部署环境。优先使用项目现有的部署；否则，在 `npx convex whoami` 成功时运行 `npx convex dev --once`，且仅在 `CONVEX_AGENT_MODE=anonymous npx convex dev --once` 不适用时才使用匿名模式。强制对已登录用户使用匿名模式会重置 `.env.local`，并导致他们失去期望的持久化、可发布云部署。完成前修复所有报错 —— 一次自检足以捕获导致部署失败的错误相对导入 / 重复符号 / 括号不匹配类错误。
