# TypeScript 代码风格指南

## 类型与类型安全

- 当 TypeScript 能够推断类型时，避免显式类型注解
- 避免隐式使用 `any`；在必要时显式声明类型
- 使用精确的类型：优先使用 `Record<PropertyKey, unknown>` 而不是 `object` 或 `any`
- 对于对象形状，优先使用 `interface`（例如 React props）；对于联合类型/交叉类型，使用 `type`
- 优先使用 `as const satisfies XyzInterface` 而不是普通的 `as const`
- 优先使用 `@ts-expect-error` 而不是 `@ts-ignore` 而不是 `as any`
- 避免无意义的 null/undefined 参数；设计严格的函数契约
- 优先使用 ES 模块扩展（`declare module '...'`）而不是 `namespace`；不要引入基于 `namespace` 的扩展模式
- 当类型需要可扩展性时，在源类型中暴露一个小型的可合并接口，并让每个特性/插件在本地扩展它，而不是在单个注册文件中集中所有扩展字段
- 对于包内部的扩展模式（如 `PipelineContext.metadata`），在读取或写入元数据的处理器/提供者/插件旁边定义元数据字段

## 异步模式

- 优先使用 `async`/`await` 而不是回调或 `.then()` 链
- **IO 优先异步**：新的 IO 代码（fs、child_process 等）必须在边界处使用异步 API — 使用基于 Promise 的变体，如 `import { readFile } from 'fs/promises'`，永远不要默认使用 `*Sync`。函数着色是不对称的：异步→同步迁移永远不需要，而同步→异步（当 IO 变慢、获得并发性或增长子进程/网络调用时）强制重写链上的每个调用者 — 同步优先的债务会累积。异步的微成本（线程池调度、缓存竞争）不是有效理由：竞争通过缓存 Promise 而不是结果来解决
- `*Sync` 只有一个地方可以使用：在你不控制的同步契约中锁定的调用点 — 现有的同步签名链（不要在修复程序中病毒式重构遗留的同步链，但新的独立模块必须不扩展这种链），或仅同步的回调如 `process.on('exit')`。模块加载时间和 CLI 启动初始化不是例外 — 在那里使用顶层 `await`（ESM）
- 在安全的情况下，使用 `Promise.all`、`Promise.race` 进行并发操作

## 导入

- 让 lint 强制执行 `simple-import-sort/imports` 和 `consistent-type-imports`，使用单独的 `import type` 语句（`fixStyle: 'separate-type-imports'`）。

## 代码结构

- 优先使用**命名导出**而不是 `export default` — 保持重构重命名和 IDE 自动导入同步，并避免 `import Foo from './foo'` 中 `default` 重命名的漂移。将 `export default` 保留给框架要求的文件（Next.js 页面/路由/布局、React.lazy 目标、配置文件如 `vitest.config.ts`）。代码库中仍然有许多 `export default` 出现 — 这是历史债务，而不是要复制的模式；不要在上述框架要求的案例之外模仿现有的 `export default` 使用

## 可重用性

- 在添加守卫、解析、规范化、计时或 JSON 安全辅助函数之前，搜索 `packages/utils` 和已安装的包。重用 `@lobechat/utils` 或其相关子路径，而不是在特性之间重复辅助函数
- 不要手动编写可重用的记录/对象映射守卫，如 `typeof value === 'object' && value !== null`；从 `@lobechat/utils/object` 中导入 `isRecord`、`isPlainRecord`、`isObjectLike`、`toRecord`、`pickString`、`UnknownRecord` 等辅助函数
- 将 `Date.now()` 赋值给一个常量并重用以保持一致性

## 日志记录

- 永远不要记录用户私人信息（API 密钥等）
- 不要直接使用 `import { log } from 'debug'`（日志输出到控制台）
- 在 catch 块中使用 `console.error` 而不是调试包
- 在 `.catch()` 回调中始终记录错误 — 安静的 `.catch(() => fallback)` 会吞噬失败并使调试变得不可能
