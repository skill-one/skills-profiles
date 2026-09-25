# 使用令牌的 Vercel CLI

使用基于令牌的身份验证的 CLI 部署和管理 Vercel 项目，而无需依赖 `vercel login`。

## 第 1 步：定位 Vercel 令牌

在运行任何 Vercel CLI 命令之前，确定令牌的来源。按顺序处理以下场景：

### A) `VERCEL_TOKEN` 已在环境中设置

```bash
printenv VERCEL_TOKEN
```

如果此命令返回值，您就准备好了。跳转到第 2 步。

### B) 令牌位于 `VERCEL_TOKEN` 下方的 `.env` 文件中

```bash
grep '^VERCEL_TOKEN=' .env 2>/dev/null
```

如果找到，导出它：

```bash
export VERCEL_TOKEN=$(grep '^VERCEL_TOKEN=' .env | cut -d= -f2-)
```

### C) 令牌位于 `.env` 文件中的不同名称下

查找任何看起来像 Vercel 令牌的变量（Vercel 令牌通常以 `vca_` 开头）：

```bash
grep -i 'vercel' .env 2>/dev/null
```

检查输出以确定哪个变量包含令牌，然后将其导出为 `VERCEL_TOKEN`：

```bash
export VERCEL_TOKEN=$(grep '^<VARIABLE_NAME>=' .env | cut -d= -f2-)
```

### D) 未找到令牌——提示用户

如果以上方法均未找到令牌，请提示用户提供令牌。他们可以在 vercel.com/account/tokens 创建一个 Vercel 访问令牌。

---

**重要提示：** 一旦 `VERCEL_TOKEN` 被导出为环境变量，Vercel CLI 将原生读取它——**不要将其作为 `--token` 标志传递**。将密钥放在命令行参数中会在 shell 历史记录和进程列表中暴露它们。

```bash
# 不良——令牌会在 shell 历史记录和进程列表中可见
vercel deploy --token "vca_abc123"

# 良好——CLI 从环境变量中读取 VERCEL_TOKEN
export VERCEL_TOKEN="vca_abc123"
vercel deploy
```

## 第 2 步：定位项目和团队

类似地，检查项目 ID 和团队范围。这些允许 CLI 目标正确的项目，而无需 `vercel link`。

```bash
# 检查环境
printenv VERCEL_PROJECT_ID
printenv VERCEL_ORG_ID

# 或者检查 .env
grep -i 'vercel' .env 2>/dev/null
```

**如果您有一个项目 URL**（例如 `https://vercel.com/my-team/my-project`），请提取团队别名：

```bash
# 例如从 "https://vercel.com/my-team/my-project" 中提取 "my-team"
echo "$PROJECT_URL" | sed 's|https://vercel.com/||' | cut -d/ -f1
```

**如果您在环境中同时具有 `VERCEL_ORG_ID` 和 `VERCEL_PROJECT_ID`**，请导出它们——CLI 将自动使用这些并跳过任何 `.vercel/` 目录：

```bash
export VERCEL_ORG_ID="<org-id>"
export VERCEL_PROJECT_ID="<project-id>"
```

注意：`VERCEL_ORG_ID` 和 `VERCEL_PROJECT_ID` 必须一起设置——仅设置其中一个会导致错误。

## CLI 设置

确保 Vercel CLI 已安装并更新到最新版本：

```bash
npm install -g vercel
vercel --version
```

## 部署项目

始终以 **预览** 模式部署，除非用户明确要求生产。根据您拥有的资源选择方法。

### 快速部署（具有项目 ID——无需链接）

当 `VERCEL_TOKEN` 和 `VERCEL_PROJECT_ID` 在环境中设置时，直接部署：

```bash
vercel deploy -y --no-wait
```

具有团队范围（通过 `VERCEL_ORG_ID` 或 `--scope`）：

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

生产（仅在明确要求时）：

```bash
vercel deploy --prod --scope <team-slug> -y --no-wait
```

检查状态：

```bash
vercel inspect <deployment-url>
```

### 完整部署流程（无项目 ID——需要链接）

在您拥有令牌和团队但无预现有项目 ID 时使用此方法。

#### 首先检查项目状态

```bash
# 项目是否有 git 远程？
git remote get-url origin 2>/dev/null

# 是否已链接到 Vercel 项目？
cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null
```

#### 链接项目

**具有 git 远程（首选）：**

```bash
vercel link --repo --scope <team-slug> -y
```

读取 git 远程并连接到匹配的 Vercel 项目。创建 `.vercel/repo.json`。比纯 `vercel link` 更可靠，纯 `vercel link` 通过目录名称进行匹配。

**没有 git 远程：**

```bash
vercel link --scope <team-slug> -y
```

创建 `.vercel/project.json`。

**通过名称链接到特定项目：**

```bash
vercel link --project <project-name> --scope <team-slug> -y
```

如果项目已链接，请检查 `.vercel/project.json` 或 `.vercel/repo.json` 中的 `orgId` 以验证它是否匹配预期的团队。

#### 链接后部署

**A) Git 推送部署——具有 git 远程（首选）**

Git 推送会触发自动 Vercel 部署。

1. **在推送前提示用户。** 永远不要在没有明确批准的情况下推送。
2. 提交并推送：
   ```bash
   git add .
   git commit -m "deploy: <变更的描述>"
   git push
   ```
3. Vercel 自动构建。非生产分支会获得预览部署。
4. 获取部署 URL：
   ```bash
   sleep 5
   vercel ls --format json --scope <team-slug>
   ```
   在 `deployments` 数组中找到最新条目。

**B) CLI 部署——无 git 远程**

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

检查状态：

```bash
vercel inspect <deployment-url>
```

### 从远程存储库部署（本地未克隆代码）

1. 克隆存储库：
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```
2. 链接到 Vercel：
   ```bash
   vercel link --repo --scope <team-slug> -y
   ```
3. 通过 git 推送（如果您有推送权限）或 CLI 部署。

### 关于 `.vercel/` 目录

已链接的项目具有：
- `.vercel/project.json` — 来自 `vercel link`。包含 `projectId` 和 `orgId`。
- `.vercel/repo.json` — 来自 `vercel link --repo`。包含 `orgId`、`remoteName` 和一个 `projects` 映射。

当 `VERCEL_ORG_ID` + `VERCEL_PROJECT_ID` 都在环境中设置时，不需要此目录。

**不要** 在未链接的目录中直接运行 `vercel project inspect` 或 `vercel link` 来检测状态——它们会交互式提示或作为副作用静默链接。`vercel ls` 是安全的（在未链接的目录中，它会默认显示该范围内的所有部署）。`vercel whoami` 任何地方都是安全的。

## 管理环境变量

```bash
# 为所有环境设置
echo "value" | vercel env add VAR_NAME --scope <team-slug>

# 为特定环境（生产、预览、开发）设置
echo "value" | vercel env add VAR_NAME production --scope <team-slug>

# 列出环境变量
vercel env ls --scope <team-slug>

# 将环境变量拉取到本地 .env.local 文件
vercel env pull --scope <team-slug>

# 删除变量
vercel env rm VAR_NAME --scope <team-slug> -y
```

## 检查部署

```bash
# 列出最近部署
vercel ls --format json --scope <team-slug>

# 检查特定部署
vercel inspect <deployment-url>

# 查看构建日志（需要 Vercel CLI v35+）
vercel inspect <deployment-url> --logs

# 查看运行时请求日志（默认按顺序跟踪；添加 --no-follow 获取一次性快照）
vercel logs <deployment-url>
```

## 管理域名

```bash
# 列出域名
vercel domains ls --scope <team-slug>

# 将域名添加到项目——已链接或环境链接目录（1 个参数）
vercel domains add <domain> --scope <team-slug>

# 添加域名——未链接目录（需要 <project> 位置参数）
vercel domains add <domain> <project> --scope <team-slug>
```

## Stripe 项目计划变更

如果此项目由 Stripe 项目管理。**在运行任何付费或破坏性计划变更前提示用户**——升级会扣费真实卡，降级会移除座位。

首先运行 `stripe projects status --json` 确认 Vercel 资源的本地名称。以下示例假设默认名称为 `vercel-plan`；如果 `stripe projects add` 时重命名了，请替换实际名称。

- **升级到 Pro：** `stripe projects add vercel/pro`（或 `stripe projects upgrade vercel-plan pro`）
- **降级到 Hobby：** `stripe projects downgrade vercel-plan hobby`

### Pro 提供的内容

- 每月 20 美元的平台费，包含每月 20 美元的用量信用。
- 默认为新项目提供 Turbo 构建机器（30 vCPU，60 GB 内存）——比 Hobby 快得多。
- 1 个部署座位 + 无限免费 Viewer 座位（只读协作者，预览评论）。
- 更高的包含配额（1 TB 快速数据传输，每月 1000 万次边缘请求）。
- 可用付费附加功能：SAML SSO、HIPAA BAA、Flags Explorer、Observability Plus、Speed Insights、Web Analytics Plus。

详细信息：https://vercel.com/docs/plans/pro-plan

## 合作协议

- **永远不要将 `VERCEL_TOKEN` 作为 `--token` 标志传递。** 将其导出为环境变量并让 CLI 原生读取它。
- **在提示用户之前检查环境中的令牌。** 首先检查当前环境和 `.env` 文件。
- **默认为预览部署。** 仅在明确要求时部署到生产。
- **在推送到 git 前提示用户。** 永远不要在没有用户批准的情况下推送提交。
- **不要直接修改 `.vercel/` 文件。** CLI 管理此目录。读取它们（例如，以验证 `orgId`）是安全的。
- **不要 curl/fetch 部署 URL 来验证。** 仅将链接返回给用户。
- **使用 `--format json`** 当结构化输出将有助于后续步骤时。
- **在提示确认的命令上使用 `-y`** 以避免交互式阻塞。

## 故障排除

### 令牌未找到

检查环境和任何 `.env` 文件：

```bash
printenv | grep -i vercel
grep -i vercel .env 2>/dev/null
```

### 身份验证错误

如果 CLI 因 `Authentication required` 失败：
- 令牌可能已过期或无效。
- 验证：`vercel whoami`（使用环境中的 `VERCEL_TOKEN`）。
- 提示用户提供新令牌。

### 错误的团队

验证范围是否正确：

```bash
vercel whoami --scope <team-slug>
```

### 构建失败

检查构建日志：

```bash
vercel inspect <deployment-url> --logs
```

常见原因：
- 缺少依赖项——确保 `package.json` 是完整的并已提交。
- 缺少环境变量——使用 `vercel env add` 添加。
- 框架配置错误——检查 `vercel.json`。Vercel 会从 `package.json` 自动检测框架（Next.js、Remix、Vite 等）；如果检测错误，可以使用 `vercel.json` 覆盖。

### CLI 未安装

```bash
npm install -g vercel
```
