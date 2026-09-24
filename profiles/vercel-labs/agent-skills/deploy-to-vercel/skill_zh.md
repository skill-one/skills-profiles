# 部署到 Vercel

将任何项目部署到 Vercel。**始终以预览模式部署**（而非生产环境），除非用户明确要求生产环境。

目标是让用户进入最佳长期配置：项目与 Vercel 关联，通过 git push 进行部署。下方所有方法都致力于让用户更接近这一状态。

## 步骤 1：收集项目状态

在决定使用哪种方法之前，请运行以下四项检查：

```bash
# 1. 检查是否存在 git 远程仓库
git remote get-url origin 2>/dev/null

# 2. 检查是否已与 Vercel 项目本地关联（任一文件存在即表示已关联）
cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null

# 3. 检查 Vercel CLI 是否已安装并认证
vercel whoami 2>/dev/null

# 4. 列出可用团队（如已认证）
vercel teams list --format json 2>/dev/null
```

### 团队选择

如果用户属于多个团队，将所有可用的团队 slug 以列表形式呈现，并询问用户部署到哪个团队。用户选定团队后，立即进入下一步——不要要求额外的确认。

在后续的所有 CLI 命令（`vercel deploy`、`vercel link`、`vercel inspect` 等）中，通过 `--scope` 传递团队 slug：

```bash
vercel deploy [path] -y --no-wait --scope <team-slug>
```

如果项目已关联（`.vercel/project.json` 或 `.vercel/repo.json` 存在），这些文件中的 `orgId` 决定了团队——无需再次询问。如果只有一个团队（或仅个人账户），跳过提示，直接使用。

**关于 `.vercel/` 目录：** 已关联的项目包含以下之一：
- `.vercel/project.json` — 由 `vercel link`（单项目关联）创建。包含 `projectId` 和 `orgId`。
- `.vercel/repo.json` — 由 `vercel link --repo`（基于仓库关联）创建。包含 `orgId`、`remoteName` 和一个 `projects` 数组，用于将目录映射到 Vercel 项目 ID。

这两个文件中的任何一个都表示项目已关联。请检查两者。

**请勿**使用 `vercel project inspect`、`vercel ls` 或 `vercel link` 在未关联的目录中检测状态——若无 `.vercel/` 配置，它们会进行交互式提示（或使用 `--yes` 时，会静默地作为副作用进行关联）。在任何位置运行 `vercel whoami` 都是安全的。

## 步骤 2：选择部署方法

### 已关联（`.vercel/` 存在）+ 有 git 远程仓库 → Git Push

这是理想状态。项目已关联，并具备 git 集成。

1. **在推送前询问用户。** 绝不可未经明确许可进行推送：
   ```
   This project is connected to Vercel via git. I can commit and push to
   trigger a deployment. Want me to proceed?
   ```

2. **提交并推送：**
   ```bash
   git add .
   git commit -m "deploy: <description of changes>"
   git push
   ```
   Vercel 会从推送自动构建。非生产分支会获得预览部署；生产分支（通常为 `main`）会获得生产部署。

3. **获取预览 URL。** 如果 CLI 已认证：
   ```bash
   sleep 5
   vercel ls --format json
   ```
   JSON 输出包含 `deployments` 数组。找到最新条目——其 `url` 字段即为预览 URL。

   如果 CLI 未认证，请告知用户到 Vercel 仪表板或 git 提供商的提交状态检查中查看预览 URL。

---

### 已关联（`.vercel/` 存在）+ 无 git 远程仓库 → `vercel deploy`

项目已关联但没有 git 仓库。可直接使用 CLI 进行部署。

```bash
vercel deploy [path] -y --no-wait
```

使用 `--no-wait`，以便 CLI 立即以部署 URL 返回，而不是阻塞等待构建完成（构建可能需要较长时间）。然后使用以下命令检查部署状态：

```bash
vercel inspect <deployment-url>
```

对于生产环境部署（仅当用户明确要求时）：
```bash
vercel deploy [path] --prod -y --no-wait
```

---

### 未关联 + CLI 已认证 → 先关联，再进行部署

CLI 可用，但项目尚未关联。这是让用户进入最佳状态的机会。

1. **询问用户部署到哪个团队。** 根据步骤 1 将团队 slug 以列表形式呈现。如果只有一个团队（或仅个人账户），跳过此步骤。

2. **选定团队后，直接进入关联阶段。** 告知用户将要发生什么，但不要要求单独的确认：
   ```
   Linking this project to <team name) on Vercel. This will create a Vercel
   project to deploy to and enable automatic deployments on future git pushes.
   ```

3. **如果存在 git 远程仓库**，使用基于仓库的关联，并选择所选团队的 scope：
   ```bash
   vercel link --repo --scope <team-slug>
   ```
   此命令会读取 git 远程仓库 URL，并匹配来自该仓库的现有 Vercel 项目。它会创建 `.vercel/repo.json`。这比 `vercel link`（不使用 `--repo`）更可靠，后者尝试按目录名称匹配，当本地文件夹与 Vercel 项目命名不同时往往会失败。

   **如果没有 git 远程仓库**，回退到标准关联：
   ```bash
   vercel link --scope <team-slug>
   ```
   此命令会提示用户选择或创建项目。它会创建 `.vercel/project.json`。

4. **然后使用最佳可用方法进行部署：**
   - 如果存在 git 远程仓库 → 提交并推送（见上方的 git push 方法）
   - 如果没有 git 远程仓库 → `vercel deploy [path] -y --no-wait --scope <team-slug>`，然后 `vercel inspect <url>` 检查状态

---

### 未关联 + CLI 未认证 → 安装、认证、关联、部署

Vercel CLI 完全未设置。

1. **安装 CLI（如果尚未安装）：**
   ```bash
   npm install -g vercel
   ```

2. **进行认证：**
   ```bash
   vercel login
   ```
   用户在浏览器中完成认证。如果在无法进行登录的非交互式环境中运行，跳过下方**无认证回退**。

3. **询问部署到哪个团队**——将 `vercel teams list --format json` 的团队 slug 以列表形式呈现。如果只有一个团队/个人账户，跳过。选定后立即进行。

4. **使用所选团队的 scope 关联项目**（如果存在 git 远程仓库则使用 `--repo`，否则使用普通的 `vercel link`）：
   ```bash
   vercel link --repo --scope <team-slug>   # 如果存在 git 远程仓库
   vercel link --scope <team-slug>          # 如果没有 git 远程仓库
   ```

5. **使用最佳可用方法进行部署**（如果存在远程仓库则使用 git push，否则使用 `vercel deploy -y --no-wait --scope <team-slug>`，然后使用 `vercel inspect <url>` 检查状态）。

---

### 无认证回退 — claude.ai 沙盒环境

**适用场景：** 当 CLI 无法在 claude.ai 沙盒环境中安装或认证时的最后手段。此方式无需认证，返回一个**预览 URL**（在线站点）和一个**认领 URL**（转移到您的 Vercel 账户）。

```bash
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh [path]
```

**参数：**
- `path` - 部署目录，或 `.tgz` 文件（默认为当前目录）

**示例：**
```bash
# 部署当前目录
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh

# 部署特定项目
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh /path/to/project

# 部署现有压缩包
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh /path/to/project.tgz
```

该脚本根据 `package.json` 自动检测框架，打包项目（排除 `node_modules`、`.git`、`.env`），上传项目，并等待构建完成。

**告知用户：** "您的部署已准备就绪，地址为 [previewUrl]。在 [claimUrl] 进行认领以管理您的部署。"

---

### 无认证回退 — Codex 沙盒环境

**适用场景：** 在 Codex 沙盒环境中，CLI 可能无法认证。Codex 默认运行在沙盒环境中——先尝试使用 CLI，如果认证失败，则回退到部署脚本。

1. **检查 Vercel CLI 是否已安装**（此检查无需提权）：
   ```bash
   command -v vercel
   ```

2. **如果已安装 `vercel`**，则尝试使用 CLI 进行部署：
   ```bash
   vercel deploy [path] -y --no-wait
   ```

3. **如果未安装 `vercel`，或 CLI 因 \"未找到现有凭证\" 而失败**，使用回退脚本：
   ```bash
   skill_dir="<path-to-skill>"

   # 部署当前目录
   bash "$skill_dir/resources/deploy-codex.sh"

   # 部署特定项目
   bash "$skill_dir/resources/deploy-codex.sh" /path/to/project

   # 部署现有压缩包
   bash "$skill_dir/resources/deploy-codex.sh" /path/to/project.tgz
   ```

该脚本处理框架检测、打包和部署。它会等待构建完成，并返回包含 `previewUrl` 和 `claimUrl` 的 JSON 数据。

**告知用户：** "您的部署已准备就绪，地址为 [previewUrl]。在 [claimUrl] 进行认领以管理您的部署。"

**提权网络访问：** 仅当沙盒环境阻止网络调用（`sandbox_permissions=require_escalated`）时，才提权实际的部署命令。**请勿**提权 `command -v vercel` 检查。

---

## 特定 Agent 的说明

### Claude Code / 终端类 Agent

您拥有完整的 shell 访问权限。请勿使用 `/mnt/skills/` 路径。按照上述决策流程，直接使用 CLI 进行操作。

对于无认证回退，从技能已安装的位置运行部署脚本：
```bash
bash ~/.claude/skills/deploy-to-vercel/resources/deploy.sh [path]
```
路径可能因用户安装技能的位置而异。

### claude.ai 中的沙盒环境

您很可能无法运行 `vercel login` 或 `git push`。请直接前往**无认证回退 — claude.ai 沙盒环境**。

### Codex

Codex 在沙盒中运行。首先检查 CLI 是否可用，然后回退到部署脚本。前往**无认证回退 — Codex 沙盒环境**。

---

## 输出

始终向用户显示部署 URL。

- **Git push：** 使用 `vercel ls --format json` 查找预览 URL。如果 CLI 未认证，请告知用户到 Vercel 仪表板或提交状态检查中查看。
- **CLI 部署：** 显示 `vercel deploy --no-wait` 返回的 URL。使用 `vercel inspect <url>` 检查构建状态并告知用户。
- **无认证回退：** 同时显示预览 URL 和认领 URL：
  ```
  Deployment successful!

  Preview URL: https://my-app-abc123.vercel.app
  Claim URL:   https://vercel.com/claim-deployment?code=...

  View your site at the Preview URL.
  To transfer this deployment to your Vercel account, visit the Claim URL.
  ```

**请勿**使用 curl 或获取已部署的 URL 来验证其是否可用。只需返回链接。

---

## 故障排除

### 网络出口错误（claude.ai）

如果部署因 claude.ai 的网络限制而失败，告知用户：

```
部署因网络限制而失败。修复方法如下：

1. 前往 https://claude.ai/settings/capabilities
2. 将 *.vercel.com 添加到允许的域名列表
3. 再次尝试部署
```

### 提权网络访问（Codex / 沙盒环境）

如果部署因沙盒环境中的网络问题（超时、DNS 错误、连接重置）而失败，请使用提权权限重新运行（`sandbox_permissions=require_escalated`）。请勿提权初始的 CLI 可用性检查——仅提权实际的部署命令。

向用户提供的示例指导：
```
部署到 Vercel 需要提权网络访问。我可以使用提权权限重新运行该命令——是否继续？
```

### CLI 认证失败

如果 `vercel login` 或 `vercel deploy` 因认证错误而失败，回退到无认证部署脚本（根据环境选择 claude.ai 或 Codex 变体）。
