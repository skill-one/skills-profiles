# Prisma Compute

指导代理通过 Prisma Compute 应用创建、部署、操作以及特定框架的部署就绪。

## Prisma Compute CLI 界面

使用 Prisma 平台 CLI 进行 Compute 应用工作流：

```bash
bunx @prisma/cli@latest app deploy --help
bunx @prisma/cli@latest app --help
bunx @prisma/cli@latest build logs --help
bunx create-prisma@latest --help
```

使用 `@prisma/cli@latest` 进行 Compute 应用部署。使用 `create-prisma@latest` 进行新项目脚手架。

## 发送反馈和报告 CLI 问题

CLI 具有内置的反馈渠道。在以下情况时使用它：命令崩溃（`UNEXPECTED_ERROR`）、故障在排错后仍然存在，或用户要求向 Prisma 团队发送反馈：

```bash
bunx @prisma/cli@latest feedback "app deploy crashed: <first error line>"
bunx @prisma/cli@latest feedback "love the deploy flow" --email you@example.com
```

崩溃输出将单独指向此处：`--json` 崩溃信封会携带预填写的确切命令作为 `nextActions` 中的 `recover` 条目（直接运行它），而人类崩溃输出将以 `Tell us what happened:` 提示结束。反馈是匿名的，除非传递了 `--email`，否则仅附加 CLI 版本、node 版本和操作系统平台/架构。切勿在消息中包含密钥、连接 URL 或用户数据。

## 真实情况顺序

在决定要编辑或运行的内容时，按此顺序使用证据：

1. 项目的生成脚本和配置，特别是 `prisma.compute.ts`、`compute:deploy`、框架配置和 `package.json`。
2. `create-prisma` 和 `@prisma/cli` 的 CLI 帮助输出。
3. 本地安装的包代码、生成工件和类型定义。
4. 官方文档。

## 适用场景

使用此技能的场景：

- 创建可部署到 Prisma Compute 的新应用
- 将现有的 TypeScript 应用部署到 Prisma Compute
- 创建或更新类型的 `prisma.compute.ts` 部署配置
- 判断框架是否 Compute 就绪
- 调试 `create-prisma --deploy`、`compute:deploy` 或 `app deploy`
- 管理 Compute 应用日志、部署、环境变量和域名，以及列出平台分支（`branch list`；没有分支创建/删除命令）
- 检查 GitHub/控制台构建日志和 GitHub 推送部署状态
- 使用浏览器认证、多个存储工作区或 Prisma 服务令牌运行非交互式部署
- 切换、选择、列出或注销本地 Prisma 平台工作区（用于 `@prisma/cli`）
- 使用 `@prisma/cli feedback` 发送关于无法解决的 Compute CLI 失败的反馈
- 使用 `@prisma/compute-sdk` 或 Management API 集成进行程序化部署

## 决策树

1. 现有项目部署或重新部署：
   阅读 [`references/app-deploy-cli.md`](references/app-deploy-cli.md)。

2. 类型的 Compute 配置、单仓库、部署目标、应用根或构建/环境默认值：
   阅读 [`references/compute-config.md`](references/compute-config.md)。

3. 框架特定的构建/运行时工作：
   阅读 [`references/frameworks.md`](references/frameworks.md)。

4. 从脚手架创建的新项目：
   阅读 [`references/create-prisma.md`](references/create-prisma.md)。

5. 程序化部署、SDK、API 或低级 App/部署概念：
   阅读 [`references/sdk-api.md`](references/sdk-api.md)。

6. 构建、认证、环境、部署或运行时失败：
   阅读 [`references/troubleshooting.md`](references/troubleshooting.md)。

## 优先级规则

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 命令验证 | 关键 | `verify-` |
| 2 | 认证和工作区选择 | 关键 | `auth-` |
| 3 | 框架就绪 | 关键 | `framework-` |
| 4 | 运行时主机和端口绑定 | 关键 | `runtime-` |
| 5 | 类型的 Compute 配置 | 高 | `config-` |
| 6 | 分支、环境和数据库连接 | 高 | `env-` |
| 7 | 部署操作 | 高 | `deploy-` |
| 8 | SDK 和 API 自动化 | 中 | `sdk-` |

## 快速规则

### 1. 命令验证

- `verify-help-first` - 在工作时使用 CLI 帮助输出确认命令语法。
- `verify-prisma-vs-platform-cli` - 不要假设 ORM CLI 中存在 `prisma app deploy`；检查任务是否应使用 `@prisma/cli`。
- `verify-generated-scripts` - 当项目已经有一个时，优先使用生成的 `compute:deploy` 脚本。
- `verify-public-url` - 在实际部署后，请求公共部署 URL，而不是信任本地或仅就绪检查。
- `verify-config-support` - 将 `prisma.compute.ts` 视为类型的 Compute 配置；在编辑或部署之前检查项目的配置和生成脚本。
- `verify-auth-workspace-support` - 使用 `@prisma/cli auth workspace` 命令进行本地工作区列表/使用/注销流程。

### 2. 认证和工作区选择

- `auth-source-precedence` - 非空的 `PRISMA_SERVICE_TOKEN` 是命令和本地 OAuth 工作区的活动认证源。如果它被设置但为空，CLI 应失败，而不是回退到存储的 OAuth。
- `auth-multi-workspace` - `auth login` 可以存储同一机器上多个工作区的 OAuth 会话。活动工作区指针选择正常命令使用的存储的 OAuth 授权。
- `auth-list-before-switch` - 使用 `auth workspace list --json` 检查本地会话。代理应优先选择来自 JSON 的工作区 ID 而不是名称，因为名称可能存在歧义。
- `auth-switch-explicitly` - 使用 `auth workspace use <id-or-name>` 进行非交互式切换。仅在没有参数的情况下使用 `auth workspace use` 仅用于交互式选择器或当本地 OAuth 工作区恰好存在一个时。
- `auth-no-fallthrough` - 如果活动 OAuth 工作区已注销或刷新失败，CLI 不应静默回退到另一个缓存的工
