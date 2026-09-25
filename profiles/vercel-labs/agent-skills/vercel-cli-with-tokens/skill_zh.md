# 使用 Token 的 Vercel CLI

使用 CLI 配合基于 Token 的身份验证来部署和管理 Vercel 上的项目，无需依赖 `vercel login`。

## 步骤 1：定位 Vercel Token

在运行任何 Vercel CLI 命令之前，需确定 Token 来源。按以下顺序处理这些场景：

### A) `VERCEL_TOKEN` 已在环境中设置

```bash
printenv VERCEL_TOKEN
```

如果返回了值，即可继续。跳过至步骤 2。

### B) Token 在 `VERCEL_TOKEN` 的 `.env` 文件中

```bash
grep '^VERCEL_TOKEN=' .env 2>/dev/null
```

若找到，则导出该变量：

```bash
export VERCEL_TOKEN=$(grep '^VERCEL_TOKEN=' .env | cut -d= -f2-)
```

### C) Token 在 `.env` 文件中，变量名称不同

查找任何类似 Vercel Token 的变量（Vercel Token 通常以 `vca_` 开头）：

```bash
grep -i 'vercel' .env 2>/dev/null
```

检查输出，确定哪个变量包含 Token，然后将其导出为 `VERCEL_TOKEN`：

```bash
export VERCEL_TOKEN=$(grep '^<VARIABLE_NAME>=' .env | cut -d= -f2-)
```

### D) 未找到 Token — 询问用户

若以上均未找到 Token，请询问用户提供。用户可在 vercel.com/account/tokens 创建 Vercel 访问令牌。

---

**重要：** 一旦将 `VERCEL_TOKEN` 作为环境变量导出，Vercel CLI 会原生读取它——**切勿将其作为 `--token` 参数传递**。将密钥置于命令行参数中会使其在 shell 历史记录和进程列表中暴露。

```bash
# 错误 — token 可见于 shell 历史记录和进程列表
vercel deploy --token "vca_abc123"

# 正确 — CLI 从环境读取 VERCEL_TOKEN
export VERCEL_TOKEN="vca_abc123"
vercel deploy
```

## 步骤 2：定位项目与团队

同样，检查项目 ID 与团队作用域。这些可让 CLI 直接针对正确项目，无需使用 `vercel link`。

```bash
# 检查环境
printenv VERCEL_PROJECT_ID
printenv VERCEL_ORG_ID

# 或检查 .env
grep -i 'vercel' .env 2>/dev/null
```

**如果你有项目 URL**（例如 `https://vercel.com/my-team/my-project`），提取团队 slug：

```bash
# 例如从 "https://vercel.com/my-team/my-project" 中提取 "my-team"
echo "$PROJECT_URL" | sed 's|https://vercel.com/||' | cut -d/ -f1
```

**如果你环境中同时有 `VERCEL_ORG_ID` 和 `VERCEL_PROJECT_ID`**，导出它们——CLI 会自动使用，并跳过任何 `.vercel/` 目录：

```bash
export VERCEL_ORG_ID="<org-id>"
export VERCEL_PROJECT_ID="<project-id>"
```

注意：`VERCEL_ORG_ID` 与 `VERCEL_PROJECT_ID` 必须同时设置——仅设置其中一个会导致错误。

## CLI 设置

确保已安装并更新 Vercel CLI：

```bash
npm install -g vercel
vercel --version
```

## 部署项目

除非用户明确要求生产环境，否则始终以 **预览** 模式部署。根据可用资源选择方法。

### 快速部署（有项目 ID — 无需关联）

当环境变量中已设置 `VERCEL_TOKEN` 和 `VERCEL_PROJECT_ID` 时，可直接部署：

```bash
vercel deploy -y --no-wait
```

若有团队作用域（通过 `VERCEL_ORG_ID` 或 `--scope` 提供）：

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

生产环境（仅当用户明确要求时）：

```bash
vercel deploy --prod --scope <team-slug> -y --no-wait
```

检查状态：

```bash
vercel inspect <deployment-url>
```

### 完整部署流程（无项目 ID — 需要关联）

适用于拥有 Token 和团队，但无现成项目 ID 的情况。

#### 首先检查项目状态

```bash
# 项目是否有 git 远程？
git remote get-url origin 2>/dev/null

# 是否已关联至 Vercel 项目？
cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null
```

#### 关联项目

**使用 git 远程（推荐）：**

```bash
vercel link --repo --scope <team-slug> -y
```

读取 git 远程并连接至匹配的 Vercel 项目，创建 `.vercel/repo.json`。比仅使用 `vercel link`（按目录名匹配）更可靠。

**不使用 git 远程：**

```bash
vercel link --scope <team-slug> -y
```

创建 `.vercel/project.json`。

**按名称关联特定项目：**

```bash
vercel link --project <project-name> --scope <team-slug> -y
```

如果项目已关联，检查 `.vercel/project.json` 或 `.vercel/repo.json` 中的 `orgId`，以验证其与预期团队是否匹配。

#### 关联后部署

**A) Git 推送部署 — 有 git 远程（推荐）**

Git 推送将触发 Vercel 自动部署。

1. **在推送前询问用户。** 绝不未经明确许可就推送。
2. 提交并推送：
   ```bash
   git add .
   git commit -m "deploy: <变更描述>"
   git push
   ```
3. Vercel 自动构建。非生产分支会获得预览部署。
4. 获取部署 URL：
   ```bash
   sleep 5
   vercel ls --format json --scope <team-slug>
   ```
   在 `deployments` 数组中找到最新条目。

**B) CLI 部署 — 无 git 远程**

```bash
vercel deploy --scope <team-slug> -y --no-wait
```

检查状态：

```bash
vercel inspect <deployment-url>
```

### 从远程仓库部署（代码未本地克隆）

1. 克隆仓库：
   ```bash
   git clone <repo-url>
   cd <repo-name>
   ```
2. 关联至 Vercel：
   ```bash
   vercel link --repo --scope <team-slug> -y
   ```
3. 通过 git 推送（如有推送权限）或 CLI 部署。

### 关于 `.vercel/` 目录

关联的项目拥有以下任一：
- `.vercel/project.json` — 来自 `vercel link`。包含 `projectId` 和 `orgId`。
- `.vercel/repo.json` — 来自 `vercel link --repo`。包含 `orgId`、`remoteName` 和一个 `projects` 映射。

当环境变量中同时设置 `VERCEL_ORG_ID` 和 `VERCEL_PROJECT_ID` 时，无需此目录。

**请勿**在已关联目录之外运行 `vercel project inspect` 或 `vercel link` 来检测状态——它们会交互式提示或作为副作用静默关联。`vercel ls` 是安全的（在未关联目录中默认显示该作用域下的所有部署）。`vercel whoami` 在任何地方都是安全的。

## 管理环境变量

```bash
# 为所有环境设置
echo "value" | vercel env add VAR_NAME --scope <team-slug>

# 为特定环境（生产、预览、开发）设置
echo "value" | vercel env add VAR_NAME production --scope <team-slug>

# 列出环境变量
vercel env ls --scope <team-slug>

# 将环境变量拉取至本地 .env.local 文件
vercel env pull --scope <team-slug>

# 移除变量
vercel env rm VAR_NAME --scope <team-slug> -y
```

## 检查部署

```bash
# 列出近期部署
vercel ls --format json --scope <team-slug>

# 检查特定部署
vercel inspect <deployment-url>

# 查看构建日志（需要 Vercel CLI v35+）
vercel inspect <deployment-url> --logs

# 查看运行时请求日志（默认实时跟踪；如需一次性快照，添加 --no-follow）
vercel logs <deployment-url>
```

## 管理域名

```bash
# 列出域名
vercel domains ls --scope <team-slug>

# 将域名添加到项目 — 已关联或环境关联目录（1 个参数）
vercel domains add <domain> --scope <team-slug>

# 将域名添加到未关联目录（需提供 <project> 位置参数）
vercel domains add <domain> <project> --scope <team-slug>
```

## Stripe 项目计划变更

如果该项目由 Stripe Projects 管理。**在运行任何付费或破坏性计划变更前，务必询问用户**——升级将计费真实信用卡，降级将移除席位。

首先运行 `stripe projects status --json` 以确认 Vercel 资源的本地名称。以下示例假设默认名称（`vercel-plan`）；若在 `stripe projects add` 时被重命名，请替换为实际名称。

- **升级至 Pro：** `stripe projects add vercel/pro`（或 `stripe projects upgrade vercel-plan pro`）
- **降级至 Hobby：** `stripe projects downgrade vercel-plan hobby`

### Pro 版本提供的功能

- 每月 20 美元平台费，包含每月 20 美元的使用额度。
- 新项目默认配备 Turbo 构建机器（30 vCPU、60 GB 内存）——构建速度远快于 Hobby。
- 1 个部署席位 + 无限数量的免费查看者席位（只读协作者、预览评论）。
- 更高的内置配额（每月 1 TB 快速数据传输、1000 万次边缘请求）。
- 可用付费附加项：SAML SSO、HIPAA BAA、Flags Explorer、Observability Plus、Speed Insights、Web Analytics Plus。

完整详情：https://vercel.com/docs/plans/pro-plan

## 工作约定

- **切勿将 `VERCEL_TOKEN` 作为 `--token` 参数传递。** 将其作为环境变量导出，让 CLI 原生读取。
- **在询问用户之前检查环境中的 Token。** 先查看当前环境与 `.env` 文件。
- **默认使用预览部署。** 仅当用户明确要求时部署到生产环境。
- **在推送至 git 前询问用户。** 绝不未经用户许可推送提交。
- **不要直接修改 `.vercel/` 文件。** 由 CLI 管理此目录。读取文件（例如以验证 `orgId`）是可以的。
- **不要通过 curl/fetch 获取已部署的 URL 进行验证。** 直接将链接返回给用户即可。
- **在结构化输出有助于后续步骤时，使用 `--format json`。**
- **在需要确认的命令上使用 `-y`**，以避免交互式阻塞。

## 故障排除

### Token 未找到

检查环境以及任何已存在的 `.env` 文件：

```bash
printenv | grep -i vercel
grep -i vercel .env 2>/dev/null
```

### 认证错误

若 CLI 因 `Authentication required` 而失败：
- Token 可能已过期或无效。
- 验证：`vercel whoami`（使用环境变量中的 `VERCEL_TOKEN`）。
- 请用户提供新的 Token。

### 团队错误

验证作用域是否正确：

```bash
vercel whoami --scope <team-slug>
```

### 构建失败

检查构建日志：

```bash
vercel inspect <deployment-url> --logs
```

常见原因：
- 缺少依赖——确保 `package.json` 完整并已提交。
- 缺少环境变量——使用 `vercel env add` 添加。
- 框架配置错误——检查 `vercel.json`。Vercel 会根据 `package.json` 自动检测框架（Next.js、Remix、Vite 等）；若检测错误，可用 `vercel.json` 覆盖。

### CLI 未安装

```bash
npm install -g vercel
```
