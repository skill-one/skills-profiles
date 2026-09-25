## 概述

TanStack CLI 是一个交互式脚手架工具，用于创建 TanStack Start 应用。它提供引导式项目创建，包含 30 多个预构建集成，涵盖认证、数据库、部署和开发者工具。它还包括一个 MCP（模型上下文协议）服务器，用于 AI 代理协助，并支持自定义模板，以实现团队标准化设置。

**包名：** `@tanstack/cli`
**状态：** 稳定

## 安装与使用

```bash
# 创建新项目（交互式）
npx @tanstack/cli create my-app

# 使用特定集成创建
npx @tanstack/cli create my-app --integrations tanstack-query,clerk,drizzle

# 全局安装
npm install -g @tanstack/cli
tanstack create my-app
```

## 项目创建

### 交互式模式

```bash
npx @tanstack/cli create my-app
# 提示输入：
# - 项目名称
# - 集成选择
# - 配置选项
```

### 使用集成标志

```bash
# 多个集成
npx @tanstack/cli create my-app --integrations tanstack-query,tanstack-form,drizzle,neon,clerk

# 部署目标
npx @tanstack/cli create my-app --integrations vercel

# 全栈设置
npx @tanstack/cli create my-app --integrations tanstack-query,tanstack-form,tanstack-table,clerk,drizzle,neon,vercel,sentry
```

## 可用集成

### TanStack 库

| 集成 | 描述 |
|-------------|-------------|
| `tanstack-query` | 异步状态管理 |
| `tanstack-form` | 类型安全的表单管理 |
| `tanstack-table` | 无头表格/数据网格 |
| `tanstack-store` | 反应式数据存储 |
| `tanstack-virtual` | 列表虚拟化 |
| `tanstack-ai` | AI SDK 集成 |
| `tanstack-db` | 客户端数据库 |
| `tanstack-pacer` | 防抖/节流工具 |

### 认证

| 集成 | 描述 |
|-------------|-------------|
| `clerk` | Clerk 认证 |
| `better-auth` | Better Auth 集成 |
| `workos` | WorkOS 身份管理 |

### 数据库与 ORMs

| 集成 | 描述 |
|-------------|-------------|
| `drizzle` | Drizzle ORM |
| `prisma` | Prisma ORM |
| `neon` | Neon 服务器端 Postgres |
| `convex` | Convex 后端平台 |

### 部署

| 集成 | 描述 |
|-------------|-------------|
| `vercel` | Vercel 部署 |
| `netlify` | Netlify 部署 |
| `cloudflare` | Cloudflare Workers/Pages |
| `nitro` | Nitro 服务器引擎 |

### 开发者工具

| 集成 | 描述 |
|-------------|-------------|
| `eslint` | ESLint 配置 |
| `biome` | Biome 检查/格式化 |
| `shadcn-ui` | shadcn/ui 组件库 |
| `storybook` | Storybook 组件开发 |

### API 与后端

| 集成 | 描述 |
|-------------|-------------|
| `trpc` | tRPC 类型安全 API |
| `orpc` | oRPC 集成 |

### 服务

| 集成 | 描述 |
|-------------|-------------|
| `sentry` | 错误监控 |
| `paraglide` | 国际化 (i18n) |
| `strapi` | Strapi CMS |

## 自定义模板

### 创建模板

```bash
# 以模板为基础创建项目
npx @tanstack/cli create my-template --integrations tanstack-query,drizzle,clerk

# 作为 git 仓库或 npm 包共享
```

### 使用自定义模板

```bash
# 从 git 仓库
npx @tanstack/cli create my-app --template https://github.com/myorg/my-template

# 从本地路径
npx @tanstack/cli create my-app --template ./templates/my-template
```

### 模板结构

```
my-template/
├── template.config.ts    # 模板配置
├── src/
│   ├── app/
│   │   ├── routes/
│   │   └── components/
│   └── lib/
├── package.json
├── tsconfig.json
├── app.config.ts
└── vite.config.ts
```

## MCP 服务器

TanStack CLI 包含一个 MCP（模型上下文协议）服务器，用于 AI 代理集成。

### 功能

- **文档搜索** - AI 代理可查询 TanStack 文档
- **项目脚手架** - 通过 AI 助手引导项目创建
- **集成发现** - 搜索和推荐集成
- **部署指导** - 平台特定部署帮助

### 与 Claude 一起使用

MCP 服务器使 Claude 和其他 AI 助手能够：
- 搜索 TanStack 文档以获取准确、最新的信息
- 帮助使用适当的集成脚手架新项目
- 提供上下文感知推荐
- 协助配置和部署

### 配置

```json
// .claude/mcp.json 或等效文件
{
  "mcpServers": {
    "tanstack": {
      "command": "npx",
      "args": ["@tanstack/cli", "mcp"]
    }
  }
}
```

## 生成的项目结构

一个典型的生成项目如下：

```
my-app/
├── src/
│   ├── app/
│   │   ├── routes/
│   │   │   ├── __root.tsx
│   │   │   └── index.tsx
│   │   ├── router.tsx
│   │   ├── routeTree.gen.ts
│   │   └── client.tsx
│   ├── lib/
│   │   ├── db.ts          # (如果使用 drizzle/prisma)
│   │   ├── auth.ts        # (如果使用 clerk/better-auth)
│   │   └── query.ts       # (如果使用 tanstack-query)
│   └── components/
├── app.config.ts
├── vite.config.ts
├── package.json
├── tsconfig.json
└── .env.example
```

## Web 构建界面

TanStack CLI 还提供了一个交互式 Web 构建界面：

- 可视化技术栈选择
- 导出前预览生成文件
- 集成兼容性检查
- 一键生成项目

## CLI 命令参考

| 命令 | 描述 |
|---------|-------------|
| `create <name>` | 创建新项目 |
| `create <name> --integrations <list>` | 使用特定集成创建 |
| `create <name> --template <path>` | 从模板创建 |
| `mcp` | 启动 MCP 服务器 |

## 最佳实践

1. **从最小集成开始** - 根据需要添加更多，而不是一开始就包含所有内容
2. **使用 `--integrations` 标志** - 在 CI/文档中创建可重复的项目
3. **创建团队模板** - 在整个组织中保持一致的项目结构
4. **使用 MCP 服务器** 与 AI 助手进行引导式设置
5. **生成后检查 `.env.example`** - 查找所需的环境变量
6. **在添加业务逻辑前审查生成代码** - 理解脚手架结构
7. **使用部署集成** - 预配置托管平台设置
8. **组合认证 + 数据库集成** - 完整栈认证脚手架（例如 `clerk,drizzle,neon`）

## 常见陷阱

- 项目创建后未设置环境变量（检查 `.env.example`）
- 选择不兼容的集成组合
- 生成后未运行 `npm install` / `pnpm install`
- 使用 Drizzle/Prisma 集成时忘记初始化数据库
- 未配置部署平台的環境变量
- 使用过时的 CLI 版本（始终使用 `npx @tanstack/cli` 获取最新版本）
