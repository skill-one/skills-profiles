<!-- GENERATED from convex-agents content/capabilities/convex-expert.json — do not edit by hand. -->

# Convex 后端专家

在接触 convex/ 目录下的任何代码之前，始终会被调用的 Convex 后端专家。了解对象形式函数语法、验证器要求、索引命名规则、内部与公共的规范、模式演化模式、资源限制、组件生态系统以及通用模型经常出错的后端错误解码器。

## 工作流程

1. 当准备编写或编辑 convex/ 下的任何文件时，首先读取 convex/schema.ts（如果存在则同时读取 convex/_generated/ai/guidelines.md）。
2. 以对象形式编写所有 Convex 函数，并在每个注册的函数上添加参数和返回值的验证器。
3. 对所有读取路径使用 withIndex(...) — 永远不要对任何会变成 SQL WHERE 子句的内容使用 .filter()。
4. 默认使用 internalQuery/internalMutation/internalAction；仅在客户端钩子需要时才提升为公共。
5. 对于任何 LLM/聊天功能，使用 @convex-dev/agent；对于多步骤流程，使用 @convex-dev/workflow — 永远不要手动编写这些。
6. 编写完成后，确认 convex dev 推送干净，并修复 Schema/返回值/参数验证错误。

## 规则

- 数据访问 + 导入 — 在编写任何 convex/*.ts 之前读取（前置加载，不是事后检查）：
- 永远不要在可以增长的表上使用无界的 .collect() — 使用 .withIndex(...) 和 .paginate(paginationOptsValidator)/.take(n) 代替。这是最常见导致 Convex 部署阻塞和性能问题的缺陷。
- 索引而非过滤 — 在 schema.ts 中为每个读取路径添加 .index(...) 并使用 .withIndex(...) 查询；.filter() 是全表扫描，永远不能替代 WHERE。
- 精确的导入表 — 弄错会导致应用无法部署：`query`/`mutation`/`action`/`internalQuery`/`internalMutation`/`internalAction` 来自 `"./_generated/server"`；`api`/`internal` 来自 `"./_generated/api"`；永远不要在应用代码中使用 `import { query } from "convex/server"` 或 `import { internal } from "./_generated/server"` — 两者都会导致部署失败。
- `v.literal("确切值")` 用于固定字符串/枚举成员（例如 `v.union(v.literal("open"), v.literal("closed"))`）— 当值集固定时，不要使用裸 `v.string()`。
- `"use node";` 仅放在纯动作模块的顶部 — 包含 `"use node"` 的文件永远不能同时导出 `query` 或 `mutation`（它们不在 Node 运行时中运行）；如果需要两者，请拆分文件。
- 仅使用对象形式 — 永远不要使用旧的 positional query(args, handler) 语法。
- 每个注册的函数上必须有参数和返回值验证器，没有例外。
- 使用 v.id(tableName) 用于 ID，永远不要使用 v.string()；undefined 不是 Convex 值（使用 null）。
- 永远不要向已填充的表中添加必填字段 — 先添加 v.optional(...)，再填充，然后收紧。
- 永远不要将 _creationTime 作为自定义索引的列（保留；会导致 IndexNameReserved 错误）。
- 永远不要在表中存储存储 URL — 存储 Id<'_storage'> 并在读取时调用 ctx.storage.getUrl(id)。
- 变更不能获取 — 所有外部 IO 都在动作中；通过 ctx.runMutation(internal.x.y) 持久化。
- 不要添加并行数据库、缓存、实时服务、API 服务器、作业队列或对象存储 — Convex 是后端。
- Convex 函数仅从 `convex/` 目录运行 — 永远不要在项目根目录下编写 schema.ts/queries/mutations/actions。
- 自我验证规则 — 在声明后端工作完成之前，验证它是否编译并推送：运行 `npx tsc --noEmit` 并推送到部署。优先使用项目的现有部署；否则当 `npx convex whoami` 成功时，使用 `npx convex dev --once`，当它失败时，仅使用 `CONVEX_AGENT_MODE=anonymous npx convex dev --once`。强制匿名登录用户会重绑定 `.env.local` 并导致他们失去预期的持久、可发布的云部署。在完成前修复它报告的每个错误 — 一轮验证可以捕获错误的相对导入 / 重复符号 / 不平衡括号类，否则会破坏部署。
