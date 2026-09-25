# 使用 AWS 启动

使用 CLI 脚本驱动 AWS 迁移的全流程。它接收用户的 Web 应用程序，进行分析，生成包含成本估算的迁移计划，并提供可部署的 [AWS Blocks](https://docs.aws.amazon.com/blocks/latest/devguide/what-is-blocks.html) 基础设施代码。

推荐使用 AWS MCP 服务器，但不是必需的。此技能通过其 CLI 脚本独立工作，可在任何代理环境中运行。

## 脚本调用

所有命令都通过以下方式运行：

```bash
python3 scripts/launch_with_aws.py <command> [args...]
```

其中 `scripts/` 是相对于此技能目录的路径。代理必须在调用命令之前将工作目录设置为技能根目录。

必需文件：[launch_with_aws.py](scripts/launch_with_aws.py)、[launch_config.py](scripts/launch_config.py)、[auth.py](scripts/auth.py)、[auth_callback_server.py](scripts/auth_callback_server.py)、[launch_api_client.py](scripts/launch_api_client.py)、[archive.py](scripts/archive.py)、[服务模型](references/launchwithaws-2026-06-15.json)。通过 MCP 加载时，获取所有文件并写入临时目录以保留结构，然后调用。

每个命令在成功时将 JSON 输出到标准输出，或在标准错误中非零退出并输出 JSON 错误。

依赖项：Python 3.10+ 和 `boto3`。脚本在启动时检查两者，如果任何一项缺失，则清晰报错退出。

## 支持的应用类型

使用 vibe-coding 平台构建的全栈应用程序，以及前端 Web 应用程序和网站（静态网站、SPAs 和具有静态导出的 SSR 框架）。

| 原始平台 | 覆盖范围 |
|----------------|---------------|
| Lovable | Lovable 生成的全栈应用程序（React + Supabase） |
| Bolt.new | Bolt.new 生成的全栈应用程序（React + Supabase） |
| Replit | Replit 托管的 全栈应用程序（React + Express.js + PostgreSQL） |

| 框架 | 示例 |
|-----------|---------|
| React 生态系统 | React、CRA、Vite + React、Gatsby、Docusaurus |
| Vue 生态系统 | Vue、Nuxt（静态导出）、VitePress |
| Angular | Angular |
| Svelte 生态系统 | Svelte、SvelteKit（静态导出） |
| 具有静态导出的 SSR | Next.js、Nuxt、Astro、SvelteKit |
| 其他现代框架 | Astro、Solid、Preact、Lit、Eleventy |
| Vite（通用） | 任何基于 Vite 的应用程序 |

其他框架也可能适用。如果用户的应用程序不匹配这些类型，请参阅下文中的 **不支持的应用程序处理**。

### 迁移内容与保留内容

**Lovable / Bolt.new 应用程序（基于 Supabase）：**

| 组件 | 发生的事情 |
|-----------|-------------|
| 前端和托管 | 迁移到 AWS（S3 + CloudFront + Lambda） |
| 边缘函数 / 服务器函数 | 迁移到 AWS Lambda |
| AI 调用（例如 Lovable AI Gateway） | 迁移到 Amazon Bedrock |
| 数据库（Supabase DB） | 保留在 Supabase 上 — 不迁移 |
| 认证（Supabase Auth） | 保留在 Supabase 上 — 不迁移 |
| 存储 & Realtime | 保留在 Supabase 上 — 不迁移 |

应用程序继续从 AWS 托管的应用程序调用 Supabase 进行数据库、认证、存储和 Realtime。

**Replit 应用程序（Express.js + PostgreSQL）：**

| 组件 | 发生的事情 |
|-----------|-------------|
| 前端和托管 | 迁移到 AWS（S3 + CloudFront + Lambda） |
| 服务器逻辑（Express.js） | 迁移到 AWS Lambda（API Gateway） |
| 数据库（PostgreSQL） | 模式和代码迁移到 AWS（Aurora Serverless / DynamoDB）。现有数据不会被迁移 — 客户必须单独导出和导入他们的数据。 |
| 认证（Replit Auth） | 代码迁移到 AWS（Cognito）。现有用户账户不会被迁移 — 客户必须在 Cognito 中重新创建或邀请用户。 |
| Realtime（WebSockets） | 迁移到 AWS（API Gateway WebSocket） |
| 文件存储 | 迁移到 AWS（S3）。现有文件不会被迁移。 |

Replit 应用程序的基础设施和代码迁移到 AWS 原生服务，但现有数据、用户账户和文件必须由客户单独迁移。

## 输入解析

将用户的输入解析为本地目录路径或 GitHub URL：

- 如果用户提供 **本地路径**：直接传递该路径。
- 如果用户提供 **GitHub URL**：直接传递（服务在服务器端克隆它）。
- 如果两者都未提供：使用当前工作目录。如果看起来不像应用程序目录，请要求用户提供路径。

## 流程

按顺序运行脚本命令，并在每一步向用户显示结果：

### 1. 认证

```bash
python3 scripts/launch_with_aws.py auth-start
```

始终首先运行。立即返回 JSON：

- 如果已经认证：`{"authenticated": true, "reusedCachedSession": true, "baseUrl": "..."}`
- 如果静默刷新成功：`{"authenticated": true, "reusedCachedSession": false, "baseUrl": "..."}`
- 如果需要交互式登录：`{"authenticated": false, "signInUrl": "https://...", "pid": 12345, "port": 54321, "baseUrl": "..."}`

当 `authenticated` 为 `false` 时，**立即向用户显示 `signInUrl`**（以便他们可以在浏览器中打开），并在同一响应中调用 `auth-wait`：

```bash
python3 scripts/launch_with_aws.py auth-wait <pid>
```

其中 `<pid>` 是 `auth-start` 响应中的 `pid` 值。这会阻塞，直到用户完成浏览器登录（或在 600 秒后超时）。成功时返回 `{"authenticated": true, "baseUrl": "..."}`。

会话最多为 90 天，即使身份提供者未设置过期时间；之后需要再次进行交互式流程。

要检查当前会话而不进行认证，或注销：

```bash
python3 scripts/launch_with_aws.py session-status
python3 scripts/launch_with_aws.py sign-out
```

`session-status` 报告是否存在会话以及令牌和会话过期前的剩余时间。`sign-out` 尽力撤销刷新令牌并删除本地 `~/.launch-with-aws/session.json`。在共享或不信任的工作站上，完成时运行 `sign-out`。

### 2. 创建启动

对于本地目录，显示此确认并等待明确的批准：

> 您的源代码将被上传到 Launch with AWS 服务以分析您的应用程序并生成迁移计划。如果您稍后批准执行，AWS 托管的代理将根据计划修改您的源代码副本，并为您生成可下载的迁移快照。您的上传源代码和相关启动数据在传输中和静止时都是加密的，并保留长达 48 小时以供恢复。您的数据永远不会用于训练 AI 模型。我们排除 Git 历史记录、Git 忽略的文件以及匹配常见敏感文件模式的文件。敏感文件过滤是尽力而为的；请检查您的项目以查找密钥。继续？

**不要**在用户明确确认之前调用 `create-launch` 对于本地目录。缺失或模糊的响应意味着不执行。

```bash
python3 scripts/launch_with_aws.py create-launch <source-path-or-github-url> [name]
```

从本地目录（压缩、上传然后创建）或 GitHub URL（直接传递）创建启动。返回包含完整 `launch` 对象的 JSON，包括 `launch.launchId`。

启动以 `analyzing` 状态开始，并自动通过分析和规划。

### 3. 汇报启动状态

```bash
python3 scripts/launch_with_aws.py get-launch-status <launch-id>
```

轮询，直到 `status` 为 `planned`（准备执行）、`awaiting_input`（需要上下文答案 — 见步骤 4）或 `failed`。关键状态进展：

- `analyzing` → 检测应用程序类型和依赖项
- `awaiting_input` → 需要上下文答案（见 `refine-plan`）
- `planning` → 生成迁移计划
- `planned` → 准备执行
- `executing` → 部署中
- `completed` → 完成
- `failed` → 检查 `failureReason`

如果 `status` 为 `awaiting_input`，请检查 `contextInputs` 以获取需要回答的问题。带有 `required: true` 的输入必须回答才能继续启动；其他是可选的增强。

### 4. 优化计划（如果 awaiting_input）

```bash
python3 scripts/launch_with_aws.py refine-plan <launch-id> key1=value1 key2=value2
```

提供上下文答案以优化计划。触发重新规划。

### 5. 获取完整启动详情并确认

```bash
python3 scripts/launch_with_aws.py get-launch <launch-id> plan,cost_estimate
```

获取完整启动详情。可选的第二参数是逗号分隔的包含列表：`analysis`、`plan`、`execution`、`cost_estimate`、`download_url`。

向用户展示成本估算和计划。响应中的 `costEstimate` 字段包含 `estimatedMonthlyCost`、`region` 和按服务划分的成本。

**确认门 — 展示并等待明确的批准：**

> **迁移摘要**
>
> - 应用程序类型：[从分析中检测到的类型]
> - 架构：[从计划中目标架构]
> - 预计月成本：$X.XX/月
> - 区域：us-east-1
>
> 准备继续？这将在一个 AWS 管理的环境中执行迁移（对您免费），并生成可下载的迁移快照。

**不要**在用户明确确认之前调用 `start-launch-execution`。

### 6. 开始执行

```bash
python3 scripts/launch_with_aws.py start-launch-execution <launch-id>
```

开始部署。然后使用 `get-launch-status` 轮询，直到 `status` 为 `completed` 或 `failed`。轮询之间至少暂停 30 秒。

### 7. 下载

```bash
python3 scripts/launch_with_aws.py get-launch-download-url <launch-id>
```

**始终向用户展示完整的下载 URL** — 他们可能需要它直接下载迁移快照或参考。

### 8. 列出或删除启动

```bash
python3 scripts/launch_with_aws.py list-launches
python3 scripts/launch_with_aws.py delete-launch <launch-id>
```

### 9. 迁移后：本地应用迁移代码

获取下载 URL 后（如果平台不是 POSIX，请调整命令）：

#### 步骤 A：下载和解包

```bash
curl -L -o /tmp/migration-snapshot.zip "<download_url>"
mkdir -p /tmp/migration-output
unzip -o /tmp/migration-snapshot.zip -d /tmp/migration-output
```

#### 步骤 B：准备本地工作区

确保用户的当前工作目录是干净的：

```bash
cd <user-app-directory>
git status
```

如果有未提交的更改，请要求用户先提交或暂存。**不要**在脏的工作树中继续。

#### 步骤 C：应用迁移（三方合并）

创建迁移分支并覆盖迁移文件：

```bash
cd <user-app-directory>
git checkout -b aws-migration
rsync -a /tmp/migration-output/ .
git status
git diff --stat
```

与用户一起审查更改。关键新增项包括：

- `aws-blocks/` — AWS Blocks 基础设施定义
- `DEPLOY.md` — 部署说明
- 任何修改的配置文件

如果有与用户现有文件的冲突，请展示它们并询问如何解决。

#### 步骤 D：遵循 DEPLOY.md

阅读项目根目录中的 `DEPLOY.md` 文件并遵循其说明将应用程序部署到用户的 AWS 账户。典型步骤：

1. AWS 认证（`aws login --profile aws-migrate --region us-east-1`）
2. CDK 引导（仅首次）：`npm install && npx cdk bootstrap`
3. 部署：`npx cdk deploy --all --progress events`
4. 验证 CDK 完成时打印的 CloudFront URL。

**重要提示：**始终从迁移输出中阅读 `DEPLOY.md` — 它是针对此应用程序和架构生成的。不要假设从记忆中获取部署步骤。

## 不支持的应用程序处理

如果启动在分析期间失败，并且 `failureReason` 指示不支持的应用程序类型（或用户的堆栈不匹配支持列表）：

1. 告诉用户："此应用程序类型目前尚未直接由 Launch with AWS 支持。让我搜索其他技能以帮助部署此类应用程序。"

2. 根据应用程序类型搜索相关技能（例如 `aws-serverless`、`aws-containers`、`databases-on-aws`、`deploy-on-aws`、`aws-cdk`、`sagemaker-ai`）。
