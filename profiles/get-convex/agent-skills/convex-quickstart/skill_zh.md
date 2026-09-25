<!-- GENERATED from convex-agents content/capabilities/quickstart.json — do not edit by hand. -->

# 快速入门：一个简化的 Convex 模板，运行

从想法开始，在本地使用匿名开发部署，搭建一个简化的 Next.js + Convex 模板。设计上极简：本地开发服务器、无发布步骤、无预置认证。

## 工作流程

1. 运行配方 `quickstart-recipe@^2` 并传入 {idea, template}（配方会获取并缓存它；离线时使用固定版本）。它会创建项目、安装依赖、启动后端（匿名）和网页开发服务器。
2. 当它打印开发 URL 时，为用户打开它。
3. 展示简短计划并在构建模板之外的特性前确认。

## 规则

- 如果配方已经报告成功，切勿重新运行。
- 将 `convex/` 下的任何代码委托给 `convex-expert` 能力。
- 不要添加 Postgres/Redis/Express — 使用 Convex 原语。
- 不要在此处添加托管/发布或预置认证 — 除非用户要求更多，否则保持模板极简。
- **降级规则** — 如果脚手架无法运行（非交互式会话、无网络、沙盒临时目录，或用户只想代码而非应用）：跳过配方并直接编写标准 Convex 项目。所有后端代码都放在 `convex/` 下（schema.ts, functions）— 绝不放在项目根目录；Convex 函数仅从 `convex/` 目录运行。除非明确要求，否则不编写任何脚手架/文档文件（无 START_HERE.md, ARCHITECTURE.md, MANIFEST.txt, README 墙）。"给我搭个后端" 意味着代码，而非仪式。
- 数据访问 + 导入 — 在编写任何 convex/*.ts 之前：对可增长的表永远不要无界的 `.collect()` — 使用 `.withIndex(...)` 和 `.paginate(...)/`.take(n)`。使用索引而非 `.filter()` 进行任何 SQL WHERE 条件。`.withIndex(...)` 回调仅支持 `eq`/`gt`/`gte`/`lt`/`lte` — 没有 `.range(...)` 方法。导入：`query`/`mutation`/`action`/`internalQuery`/`internalMutation`/`internalAction` 来自 `./_generated/server`；`api`/`internal` 来自 `./_generated/api`；应用代码中绝不能从 `convex/server` 导入。`v.literal("exact value")` 用于固定字符串/枚举成员，而非裸字符串。"use node" 仅在纯动作模块顶部使用 — 绝不在同时导出 `query` 或 `mutation` 的文件中使用。从未将 Node 内建模块（`crypto`/`fs`/`path`/`http`/`child_process`/`os`，带或不带 `node:` 前缀）导入缺少 "use node" 的文件中 — 包括 `http.ts` 路由处理器；尽可能使用 Web Crypto (`crypto.subtle`) 而非导入 `crypto`。
- 保留名称 — 永远不要将 `export const <jsReservedWord> = ...`（例如 `delete`、`new`、`class`、`function`、`return`）作为查询/变更/动作导出名称；esbuild 无法解析它。表名或索引名不能以 `_` 开头（例如 `_migrations: defineTable(...)`）— `_` 被保留，在推送时会导致 `TableNameReserved`/`IndexNameReserved` 错误。
- HTTP 路由 — `httpRouter` 没有类似 Express 的 `:param` 段（`path: "/users/:id"` 仅匹配该字面字符串且为死代码）；使用 `pathPrefix` 并自行解析尾部段。每个 `http.route({...})` 的 `handler:` 必须用 `./_generated/server` 中的 `httpAction(...)` 包裹 — 裸 `async (ctx, request) => {...}` 可类型检查但不是有效的 HTTP 动作。
- `ctx.runQuery`/`ctx.runMutation`/`ctx.runAction` 需要代码生成的函数引用（`api.foo.bar`/`internal.foo.bar`），而非原始导入的模块成员（`import * as queries from "./queries"; ctx.runQuery(queries.getX, ...)` 编译通过但在运行时失败）。
- **自我验证规则** — 在声明后端工作完成前，验证其编译并推送：运行 `npx tsc --noEmit` 并推送到部署。优先使用项目的现有部署；否则当 `npx convex whoami` 成功时，运行 `npx convex dev --once`，当 `npx convex whoami` 失败时，仅当 `CONVEX_AGENT_MODE=anonymous npx convex dev --once`。强制匿名登录用户会重置 `.env.local` 并失去他们期望的持久、可发布的云端部署。在完成前修复所有报告的错误 — 一轮验证即可捕获错误的相对路径导入 / 重复符号 / 不平衡括号类，否则部署会失败。
