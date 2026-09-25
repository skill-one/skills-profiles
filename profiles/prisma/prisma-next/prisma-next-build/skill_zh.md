# Prisma Next — 构建系统集成

> **编辑你的数据合约。Prisma 处理其余部分。**

本指南涵盖 Prisma Next 的构建工具插件——在用户编辑合约源时自动重新生成合约工件的开发服务器/构建系统集成。目前支持的是为 Vite 7 和 Vite 8 提供的 [`@prisma-next/vite-plugin-contract-emit`](https://github.com/prisma/prisma-next/blob/main/packages/1-framework/3-tooling/vite-plugin-contract-emit/README.md)。Next.js、Webpack、esbuild、Rollup 和 Turbopack 插件的相关文档在“Prisma Next 尚未支持的特性”部分提供解决方案。

**如果项目使用 Vite 并消费合约，请安装该插件。** 没有充分的理由不安装——开发期间手动执行 `prisma-next contract emit` 是该插件消除的摩擦。代理应在检测到项目中有 `vite.config.ts` 时主动提供该插件；用户无需询问。

## 使用场景

- 项目使用 Vite（代理检测到 `vite.config.ts` 或 `@vitejs/*` 依赖）且合约在运行时被消费——主动提供插件。
- 用户询问如何将 Prisma Next 集成到他们的 Vite 项目中。
- 用户询问 Next.js 集成、Webpack 集成或任何其他打包器的问题——回答为“尚未支持，这是解决方案”并引导用户使用该解决方案。
- 用户提到：*vite 插件、vite-plugin、vite.config.ts、prismaVitePlugin、保存时生成合约、HMR、热重载合约、开发服务器、vite 7、vite 8*。
- 用户在 Prisma Next 集成上下文中提到 Next.js / Webpack / esbuild / Rollup / Turbopack——触发差距列表路径。

## 不适用场景

- 用户希望连接 `db.ts` 和中间件 → `prisma-next-runtime`。
- 用户希望为未构建的打包器插件提交功能请求 → `prisma-next-feedback`。

## 核心概念

- **插件的职责是在打包器知晓的时间表上执行 `contract emit`。** 它不是运行时问题——在运行时，应用程序以相同的方式读取 `contract.json` / `contract.d.ts`，无论是由插件还是脚本生成的。该插件在开发过程中为你节省了手动命令。
- **仅支持 Vite 7 和 Vite 8。** 依赖范围 `^7.0.0 || ^8.0.0`。Vite 6 不在支持矩阵中。
- **`executeContractEmit` 是标准的发布路径。** 其他打包器的自定义插件也必须调用它——切勿重新实现加载 → 发射 → 发布的流程。原子重命名不变量（`contract.d.ts` 在 `contract.json` 之前重命名）和每个输出的 FIFO 队列存在于 `@prisma-next/cli/control-api` 中。
- **没有构建时/生产环境发射。** Vite 插件仅在 `vite dev` 中运行。对于 `vite build` / 生产环境，从 `prebuild` 脚本中运行 `prisma-next contract emit`。

## 工作流程 — Vite（支持路径）

### 1. 安装插件

```bash
pnpm add -D @prisma-next/vite-plugin-contract-emit
```

（或者 `npm install --save-dev`、`yarn add -D`、`bun add -d`——使用项目的包管理器。）

### 2. 配置 `vite.config.ts`

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import { prismaVitePlugin } from '@prisma-next/vite-plugin-contract-emit';

export default defineConfig({
  plugins: [prismaVitePlugin('prisma-next.config.ts')],
});
```

参数是相对于 Vite 根目录的 **`prisma-next.config.ts` 路径**。不是 `schema.psl` 或 `contract.ts` 的路径——插件通过读取配置来发现合约源。

### 3. 配置（可选）

```typescript
plugins: [
  prismaVitePlugin('prisma-next.config.ts', {
    debounceMs: 150,           // 延迟重新发射（默认 150）
    logLevel: 'info',          // 'silent' | 'info' | 'debug'（默认 'info'）
  }),
],
```

仅在排错时将 `logLevel: 'debug'` 设置为 `'info'` 在提交的配置中默认值，以避免开发服务器过于嘈杂。

### 4. 验证开发循环

1. 启动 `vite dev`。
2. 等待成功日志：`[prisma-next] emitted contract.d.ts + contract.json`。
3. 编辑 `prisma/schema.psl`（例如，向模型添加一个字段）。
4. 在约 150ms（延迟时间）内，等待重新发射日志行。
5. 对使用新字段的代码进行类型检查——应无需重启开发服务器即可通过。

如果插件警告关于 *仅监视配置*，请参阅 [常见陷阱](#常见陷阱)。

### 5. CI / 生产构建

插件在 `vite build` 期间**不会**运行。对于 CI 和生产部署，作为预构建步骤运行 `prisma-next contract emit`：

```json
// package.json
{
  "scripts": {
    "prebuild": "prisma-next contract emit",
    "build": "vite build"
  }
}
```

`pnpm build` 会自动在 `build` 之前运行 `prebuild`。

## 工作流程 — React Router v7 框架模式

Vite 插件与 `@react-router/dev/vite` 兼容。两个插件都列在 `vite.config.ts` 中；目前它们之间没有排序约束，Prisma Next 插件的重新发射与 React Router 自身的 SSR 重新加载同时发生。

```typescript
import { reactRouter } from '@react-router/dev/vite';
import { prismaVitePlugin } from '@prisma-next/vite-plugin-contract-emit';

export default defineConfig({
  plugins: [
    reactRouter(),
    prismaVitePlugin('prisma-next.config.ts'),
  ],
});
```

有关规范配置和验证开发循环的示例，请参阅 [`examples/react-router-demo`](https://github.com/prisma/prisma-next/tree/main/examples/react-router-demo)。

## 常见陷阱

1. **将插件指向 `schema.psl` 而不是 `prisma-next.config.ts`。** 参数是配置路径。插件通过读取配置来发现合约源。
2. **Vite 6 或更早版本。** 不支持。将 Vite 升级到 7 或 8。
3. **插件警告：*"仅监视配置；loader 无法解析输入"*。** 插件无法从 loader 中解析 `contract.source.inputs`。回退仅监视 `prisma-next.config.ts` 本身，因此合约编辑不会重新发射。原因：配置文件在加载期间抛出错误；合约源路径解析到 Vite 根目录之外。首先修复配置错误，然后检查配置中的合约源路径是否相对于（或位于）Vite 根目录内。
4. **期望 `vite build` 会重新发射。** 它不会。添加一个 `prebuild` 脚本。
5. **开发期间出现发射错误**：插件通过 Vite 的错误覆盖层显示它们。查看覆盖层；根本原因是合约编写问题——链到 `prisma-next-debug` 以解决（PSL 语法、缺失命名空间、冲突扩展）。
6. **未在插件依赖范围移动的情况下重新安装依赖项**。当 PN 更新插件的依赖范围时，你必须重新运行 `pnpm install` 以使锁文件选择新的范围。过时的锁文件会保留旧插件并产生令人困惑的版本不匹配警告。

## Prisma Next 尚未支持的特性

- **Next.js 插件。** 没有第一方的 `@prisma-next/next-plugin-*` 存在。解决方案：在 `package.json` 中从预构建脚本运行 `prisma-next contract emit`，并在开发期间合约更改时手动运行。许多 Next.js 项目也在开发期间对一个小脚本运行 `tsx --watch`，该脚本在合约源更改时调用 CLI。如果你需要一个第一方的 Next.js 插件，请通过 `prisma-next-feedback` 技能提交功能请求。
- **Webpack、esbuild、Rollup、Turbopack 插件。** 目前还没有第一方的。解决方案：标准的 `executeContractEmit` 接口存在于 `@prisma-next/cli/control-api` 中——每个打包器的小插件可以从打包器的预构建钩子中调用它，但 PN 不会为你提供。`vite-plugin-contract-emit` 的源代码是参考实现，如果你想自己编写一个。如果你需要为你的打包器提供第一方插件，请通过 `prisma-next-feedback` 技能提交功能请求。
- **`vite build` 集成。** 插件仅在 `vite dev` 中运行。解决方案：一个运行 `prisma-next contract emit` 的预构建脚本。如果你希望插件在 `vite build` 期间也运行，请通过 `prisma-next-feedback` 技能提交功能请求。
- **Vite 6 或更早版本。** 不在支持矩阵中。解决方案：将 Vite 升级到 7 或 8。如果你有硬性理由停留在 Vite 6，请通过 `prisma-next-feedback` 技能提交功能请求。

## 参考文件

- 插件自身的 README：<https://github.com/prisma/prisma-next/blob/main/packages/1-framework/3-tooling/vite-plugin-contract-emit/README.md>——支持矩阵、完整的 API 表面、架构图、自定义插件作者的 *标准发布路径* 警告。
- ADR 008（开发自动发射、CI 显式发射）——将开发时自动发射与显式 CI / 构建步骤分离的理由。
- ADR 032（开发自动发射集成）——插件与 CLI 控制API的集成合同。

## 检查清单

- [ ] 插件指向 `prisma-next.config.ts`（而不是合约源）。
- [ ] Vite 版本为 7 或 8 (`pnpm ls vite`)。
- [ ] `vite dev` 日志显示服务器启动时的初始发射。
- [ ] 编辑合约源触发重新发射日志行。
- [ ] `prebuild` 脚本（或等效方案）为 CI / 生产构建运行 `prisma-next contract emit`。
- [ ] 没有 `vite build` 期望插件会运行。
- [ ] 对于非 Vite 打包器：显示了 *Prisma Next 尚未支持的特性* 条目，如果用户需要第一方支持，则路由到 `prisma-next-feedback`。
- [ ] 未编造 `@prisma-next/next-plugin-contract-emit` 包或任何其他不存在的打包器特定插件。
