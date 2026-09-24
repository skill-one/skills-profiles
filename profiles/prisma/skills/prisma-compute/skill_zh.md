# Prisma Compute

指导智能体完成 Prisma Compute 应用创建、部署、运维，以及各框架特定的部署就绪工作。

## Prisma Compute CLI 接口

使用 Prisma Platform CLI 执行 Compute 应用工作流：

```bash
bunx @prisma/cli@latest app deploy --help
bunx @prisma/cli@latest app --help
bunx @prisma/cli@latest build logs --help
bunx create-prisma@latest --help
```

使用 `@prisma/cli@latest` 执行 Compute 应用部署。使用 `create-prisma@latest` 搭建新项目。

## 发送反馈并报告 CLI 问题

CLI 内置反馈通道。在命令崩溃（`UNEXPECTED_ERROR`）、故障经排查后仍无法解决，或用户要求向 Prisma 团队发送反馈时，使用反馈通道：

```bash
bunx @prisma/cli@latest feedback "app deploy 崩溃：<首个错误行>"
bunx @prisma/cli@latest feedback "非常喜欢部署流程" --email you@example.com
```

崩溃输出会单独指向此处：`--json` 崩溃信封在 `nextActions` 的 `recover` 条目中包含完整预填的命令（请原样执行），人类可读的崩溃输出以 `Tell us what happened:` 提示结尾。反馈默认匿名，仅在传入 `--email` 时会附加 CLI 版本、Node 版本以及操作系统平台/架构信息。切勿在消息中包含密钥、连接 URL 或用户数据。

## 事实来源优先级

在决定编辑或运行什么时，按照以下顺序使用证据：

1. 项目的生成脚本和配置，特别是 `prisma.compute.ts`、`compute:deploy`、框架配置以及 `package.json`。
2. 来自 `create-prisma` 和 `@prisma/cli` 的 CLI 帮助输出。
3. 本地安装的包代码、生成的产物和类型定义。
4. 官方文档。

## 适用场景

使用本技能处理以下场景：

- 创建可部署到 Prisma Compute 的新应用
- 将现有 TypeScript 应用部署到 Prisma Compute
- 创建或更新类型化的 `prisma.compute.ts` 部署配置
- 判断框架是否具备 Compute 就绪状态
- 调试 `create-prisma --deploy`、`compute:deploy` 或 `app deploy`
- 管理 Compute 应用日志、部署、环境变量和域名，并列出平台分支（`branch list`；不存在分支创建/删除命令）
- 检查 GitHub/控制台的构建日志和 GitHub 推送部署状态
- 使用浏览器认证、多个已存储的工作区或 Prisma 服务令牌运行非交互式部署
- 为 `@prisma/cli` 切换、选择、列出或注销本地 Prisma Platform 工作区
- 使用 `@prisma/cli feedback` 提交无法解决的 Compute CLI 失败反馈
- 使用 `@prisma/compute-sdk` 或管理 API 集成进行程序化部署

## 决策树

1. 现有项目部署或重新部署：
   阅读 [`references/app-deploy-cli.md`](references/app-deploy-cli.md)。

2. 类型化 Compute 配置、 monorepo、部署目标、应用根目录或构建/环境默认值：
   阅读 [`references/compute-config.md`](references/compute-config.md)。

3. 框架特定的构建/运行时工作：
   阅读 [`references/frameworks.md`](references/frameworks.md)。

4. 从脚手架新建项目：
   阅读 [`references/create-prisma.md`](references/create-prisma.md)。

5. 程序化部署、SDK、API 或底层 App/部署概念：
   阅读 [`references/sdk-api.md`](references/sdk-api.md)。

6. 构建、认证、环境、部署或运行时故障：
   阅读 [`references/troubleshooting.md`](references/troubleshooting.md)。

## 按优先级划分的规则

| 优先级 | 类别 | 影响 | 前缀 |
|--------|------|------|------|
| 1 | 命令校验 | CRITICAL | `verify-` |
| 2 | 认证与工作区选择 | CRITICAL | `auth-` |
| 3 | 框架就绪状态 | CRITICAL | `framework-` |
| 4 | 运行时主机与端口绑定 | CRITICAL | `runtime-` |
| 5 | 类型化 Compute 配置 | HIGH | `config-` |
| 6 | 分支、环境与数据库配置 | HIGH | `env-` |
| 7 | 部署操作 | HIGH | `deploy-` |
| 8 | SDK 与 API 自动化 | MEDIUM | `sdk-` |

## 快速规则

### 1. 命令校验

- `verify-help-first` - 在处理时使用 CLI 帮助输出来确认命令语法。
- `verify-prisma-vs-platform-cli` - 不要默认认为 ORM CLI 中存在 `prisma app deploy`；确认任务应使用 `@prisma/cli`。
- `verify-generated-scripts` - 当项目已有生成脚本时，优先使用生成的 `compute:deploy` 脚本。
- `verify-public-url` - 实际部署后，请求公开的部署 URL，而不是信任本地或就绪状态检查。
- `verify-config-support` - 将 `prisma.compute.ts` 视为类型化的 Compute 配置；编辑或部署前，检查项目的配置和生成脚本。
- `verify-auth-workspace-support` - 使用 `@prisma/cli auth workspace` 命令执行本地工作区列表/使用/注销流程。

### 2. 认证与工作区选择

- `auth-source-precedence` - 非空的 `PRISMA_SERVICE_TOKEN` 是命令和本地 OAuth 工作区执行时的活跃认证来源，存储的 OAuth 工作区会被忽略。如果已设置但为空，CLI 应直接失败，而非回退到存储的 OAuth。
- `auth-multi-workspace` - `auth login` 可为同一台机器上的多个工作区存储 OAuth 会话。活跃工作区指针决定哪个存储的 OAuth 授权被普通命令使用。
- `auth-list-before-switch` - 使用 `auth workspace list --json` 检查本地会话。智能体应优先从 JSON 中获取工作区 ID，而非名称，因为名称可能具有歧义。
- `auth-switch-explicitly` - 使用 `auth workspace use <id-or-name>` 进行非交互式切换。仅使用不带参数的 `auth workspace use` 用于交互式选择器，或仅当存在且仅存在一个本地 OAuth 工作区时使用。
- `auth-no-fallthrough` - 如果活跃的 OAuth 工作区已注销或刷新失败，CLI 不应静默回退到另一个缓存工作区。运行 `auth workspace use <id>` 选择下一个工作区。
- `auth-single-workspace-logout` - 使用 `auth workspace logout <id-or-name>` 或 `auth logout --workspace <id-or-name>` 移除一个本地 OAuth 工作区会话。普通的 `auth logout` 清除所有本地 OAuth 工作区会话。
- `auth-service-token-switching` - 当设置 `PRISMA_SERVICE_TOKEN` 时，`auth workspace use` 不可用，因为服务令牌是活跃认证来源；需取消设置该环境变量以切换本地 OAuth 工作区。工作区注销仅清理本地 OAuth 状态。
- `auth-storage-awareness` - 本地 OAuth 凭证存储在平台认证文件中，工作区元数据存储在伴生的上下文文件中。项目固定值存储在 `.prisma/local.json`，CLI 应用/项目状态存储在 `.prisma/cli/state.json`（`prisma.compute.ts` 附近，若存在）。

### 3. 框架就绪状态

- `framework-cli-first` - 根据 `@prisma/cli app deploy` 评估部署就绪状态，而非根据 `create-prisma` 可搭建的内容评估。
- `framework-supported-cli-deploy` - Compute 部署支持 `nextjs`、`nuxt`、`astro`、`hono`、`nestjs`、`tanstack-start`、`custom` 和 `bun`。
- `framework-create-prisma-defaults-only` - `create-prisma` 可提供生成的默认值和 `compute:deploy`，但它不是现有应用的一般部署接口。
- `framework-build-output` - Compute 需要服务入口或框架产物，而不仅仅是有静态输出。

### 4. 运行时主机与端口绑定

- `runtime-bind-all-interfaces` - 部署的服务器必须绑定到所有接口（`0.0.0.0` 或框架等效地址），不得硬编码为 `localhost` 或 `127.0.0.1`。
- `runtime-match-http-port` - 应用必须监听已部署的 HTTP 端口：尽可能读取 `process.env.PORT`，或传入匹配的 `--http-port`。
- `runtime-readiness-port-only` - Compute 就绪状态监控监听端口；仅监听回环地址的监听器可能看起来就绪，但公网入口无法访问它。
- `runtime-respond-within-60s` - 入口给应用 60 秒的时间响应，之后返回 `504 Gateway Time-out` 并取消请求。设计处理程序时，需确保先响应，较长的处理任务在 `waitUntil` 中运行或从队列中执行，绝不能放在请求内部。

### 5. 类型化 Compute 配置

- `config-optional-simple-app` - 部署普通单应用无需 `prisma.compute.ts`；若无持久化配置，则使用标志。
- `config-init-formalizer` - 使用 `bunx @prisma/cli@latest init` 生成全新配置：它会检测框架、固定名称/框架/HTTP 端口（以及 Bun/Hono 的入口），并提供项目链接。`--format json` 会写入依赖无关的 `prisma.compute.json`。`init` 在任意配置已存在时拒绝执行，从不生成代码，也从不部署。
- `config-use-prisma-compute-ts` - 将可复用的部署默认值放在 `prisma.compute.ts` 中使用 `defineComputeConfig`，而非放在 `prisma.config.ts` 中。
- `config-app-vs-apps` - 使用 `app` 表示单个部署目标，使用 `apps` 表示 monorepo 或多应用仓库；需明确定义其一。
- `config-monorepo-roots` - 对于 monorepo，使用 `prisma.compute.ts` 声明应用目标、根目录、框架默认值、入口、端口和环境输入。
- `config-targets` - 在多应用配置中，`@prisma/cli app deploy web` 选择 `apps.web` 目标。若无 `[app]`，命令可从当前目录推断目标；否则部署可运行所有目标，而构建/运行需指定一个目标。
- `config-region-new-app-only` - 配置的 `region` 仅为新建应用提供默认值；部署到现有应用时，保留应用的当前区域。
- `config-custom-artifact` - 使用 `framework: "custom"` 配合 `build.outputDirectory` 和 `build.entrypoint` 处理预构建或自定义构建产物。
- `config-no-project-branch-secrets` - 不要将 Workspace、Project、Branch、生产意图、服务令牌或密钥值提交到 `prisma.compute.ts`；应将这些内容放在标志、`.prisma/local.json`、环境存储或 CI 密钥中。应用级默认值（如 `region`、`root`、`framework`、`entry`、`httpPort` 以及非密钥环境文件路径）属于配置内容。
- `config-flags-win` - 部署标志如 `--framework`、`--entry`、`--http-port`、`--region` 和 `--env` 会覆盖匹配的配置值。

### 6. 分支、环境与数据库

- `env-do-not-leak-secrets` - 切勿打印完整的 `DATABASE_URL`、服务令牌或密钥值。
- `env-deploy-loads-dotenv` - 生成的部署脚本可通过 `prisma.compute.ts` 或 `--env .env` 加载环境变量；重新部署前，检查实际脚本/配置。
- `env-migrations-separate` - 重新部署脚本不会运行迁移或种子数据。需单独运行适当的 Prisma 数据库脚本。
- `env-cli-token-name` - `@prisma/cli` 使用 `PRISMA_SERVICE_TOKEN` 进行服务令牌认证。
- `env-branch-scope` - 分支部署、分支环境变量和分支数据库必须使用相同的分支名称；针对预览分支部署时，需明确传入 `--branch <git-name>`。
- `env-production-vs-preview` - 生产环境使用 `--role production`，预览模板环境使用 `--role preview`，分支特定覆盖使用 `--branch <git-name>`。
- `env-db-explicit` - 通过数据库和项目环境命令保持数据库与环境的配置明确；部署示例不应添加数据库设置，部署也不会运行迁移、种子数据或自动为每个应用创建数据库。

### 7. 部署操作

- `deploy-prod-intent` - 仅在用户意图执行生产部署时使用 `--prod --yes`。应用的首次生产部署会自动提升，无需 `--prod`；该标志用于限制后续生产分支部署。
- `deploy-no-promote` - 使用 `app deploy --no-promote` 执行构建后验证：它会构建一个可访问其自身 URL 的候选版本，且不触碰线上部署，之后用 `app promote <deployment-id>` 提升。
- `deploy-github-default-branch` - 当 Compute 应用连接到 GitHub 推送部署时，合并到默认分支是生产部署路径；检查部署记录或 GitHub 检查运行，而非告知用户重新部署合并的 PR 分支或运行默认分支预览部署。
- `deploy-build-logs` - 使用 `@prisma/cli build logs <build-id>` 查看 GitHub/控制台构建输出。使用 `app logs` 查看运行时部署日志；两个 ID 不同。
- `deploy-noninteractive-auth` - 非交互式部署需要正确的活跃已存储 OAuth 工作区或支持的服务令牌环境变量；切勿打印令牌。
- `deploy-json-for-agents` - 用于脚本和智能体可读输出的，使用 `--json --no-interactive`。
- `deploy-create-project` - 仅在用户希望部署创建并链接新项目时使用 `--create-project <name>`；它与 `--project` 和 `PRISMA_PROJECT_ID` 冲突。
- `deploy-ops-targets` - App 的 show/open/logs/list-deploys/promote/rollback/remove 以及域名命令均可接受来自 `prisma.compute.ts` 的 `[app]` 目标。
- `deploy-report-cli-bugs` - 在 `UNEXPECTED_ERROR` 或不可解决的故障时，使用反馈命令报告问题；参见上方“发送反馈并报告 CLI 问题”。

### 8. SDK 与 API

- `sdk-use-cli-first` - 优先使用 `@prisma/cli app deploy` 处理应用工作流；仅在用户构建底层自动化时才使用 `create-prisma`。
- `sdk-result-handling` - `@prisma/compute-sdk` 返回 `Result` 值；检查 `isOk()`/`isErr()` 而非依赖异常。
- `sdk-snapshot-detection` - 对于未检出到磁盘的仓库快照，使用 `detectComputeApp` 检测；自行枚举工作区，为每个候选应用根目录调用一次。

## 推荐工作流

1. 检查项目：包管理器、模板/框架、`package.json` 脚本、Prisma 版本、Prisma 客户端位置、`prisma.compute.ts` 以及现有 `compute:deploy`。
2. 验证实际使用的包的 CLI 帮助输出。
3. 在修改项目/应用前验证认证上下文：`auth whoami --json`，以及当可能存在多个本地会话时，执行 `auth workspace list --json`。
4. 选择路径：
   - 现有应用部署：存在配置支持的目标、生成的 `compute:deploy`，或 `@prisma/cli app build/run/deploy` 标志
   - 新应用搭建：`create-prisma`，然后生成 `compute:deploy` 或 `@prisma/cli app deploy`
   - 底层自动化：`@prisma/compute-sdk` 或管理 API
5. 检查框架就绪状态以及主机/端口/环境/运行时要求，包括项目与分支范围。
6. 在可行的情况下，部署前先执行本地构建或 `app build`。
7. 自动化时使用 JSON 输出进行部署，然后请求公开 URL，并汇总应用 URL、应用 ID、部署 ID、项目 ID、工作区 ID 以及后续步骤。
8. 对于 GitHub/控制台构建，在猜测构建失败原因前，先检查 `Prisma Compute Deploy` 检查运行或 `build logs <build-id>`。

## 需避免

- 不要将 Compute 部署指导混入通用的 `prisma-cli` 技能中。
- 不要在现有应用中运行 `create-prisma` 仅为了部署它；使用生成的 `compute:deploy` 脚本或 `@prisma/cli app deploy`。
- 不要告知用户每个 `create-prisma` 模板都能自动部署。
- 不要使用占位符 `DATABASE_URL` 值进行部署。
- 不要默认认为 `next start` 是 Compute 运行时路径；Next.js 部署需要独立输出。
