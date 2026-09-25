# 部署到 Vercel

将任何项目部署到 Vercel。**始终以预览模式部署**（而不是生产模式），除非用户明确要求生产模式。

目标是让用户进入最佳的长期设置：他们的项目与 Vercel 关联，并通过 git-push 进行部署。以下所有方法都试图将用户推向这种状态。

## 第 1 步：收集项目状态

在决定使用哪种方法之前，请运行所有四个检查：

```bash
# 1. 检查是否存在 git 远程
git remote get-url origin 2>/dev/null

# 2. 检查是否本地链接到 Vercel 项目（任意一个文件都表示已链接）
cat .vercel/project.json 2>/dev/null || cat .vercel/repo.json 2>/dev/null

# 3. 检查 Vercel CLI 是否已安装并认证
vercel whoami 2>/dev/null

# 4. 列出可用团队（如果已认证）
vercel teams list --format json 2>/dev/null
```

### 团队选择

如果用户属于多个团队，请将所有可用的团队 slugs 以项目符号列表的形式呈现，并询问要部署到哪个团队。一旦用户选择了一个团队，请立即进入下一步——不要再次询问其他确认。

在后续的所有 CLI 命令（`vercel deploy`、`vercel link`、`vercel inspect` 等）中通过 `--scope` 传递团队 slugs：

```bash
vercel deploy [path] -y --no-wait --scope <team-slug>
```

如果项目已经链接（存在 `.vercel/project.json` 或 `.vercel/repo.json`），则这些文件中的 `orgId` 决定了团队——无需再次询问。如果只有一个团队（或仅个人账户），请直接使用它。

**关于 `.vercel/` 目录：** 已链接的项目要么有：
- `.vercel/project.json` — 由 `vercel link` 创建（单个项目链接）。包含 `projectId` 和 `orgId`。
- `.vercel/repo.json` — 由 `vercel link --repo` 创建（基于仓库的链接）。包含 `orgId`、`remoteName` 和一个将目录映射到 Vercel 项目 ID 的 `projects` 数组。

任意一个文件都表示项目已链接。检查这两个文件。

**不要**在未链接的目录中使用 `vercel project inspect`、`vercel ls` 或 `vercel link` 来检测状态——在没有 `.vercel/` 配置的情况下，它们会交互式地提示（或使用 `--yes`，静默地作为副作用进行链接）。只有 `vercel whoami` 可以在任何地方安全运行。

## 第 2 步：选择部署方法

### 已链接（存在 `.vercel/`）+ 存在 git 远程 → Git Push

这是理想状态。项目已链接并具有 git 集成。

1. **在推送前询问用户。** 除非获得明确批准，否则**不要**推送：
   ```
   此项目通过 git 连接到 Vercel。我可以提交并推送以触发部署。要继续吗？
   ```

2. **提交并推送：**
   ```bash
   git add .
   git commit -m "deploy: <变更描述>"
   git push
   ```
   Vercel 会自动从推送进行构建。非生产分支会获得预览部署；生产分支（通常是 `main`）会获得生产部署。

3. **获取预览 URL。** 如果 CLI 已认证：
   ```bash
   sleep 5
   vercel ls --format json
   ```
   JSON 输出包含一个 `deployments` 数组。找到最新的条目——其 `url` 字段就是预览 URL。

   如果 CLI 未认证，请告知用户检查 Vercel 仪表板或其 git 提供商上的提交状态检查以获取预览 URL。

---

### 已链接（存在 `.vercel/`）+ 不存在 git 远程 → `vercel deploy`

项目已链接，但没有 git 仓库。使用 CLI 直接部署。

```bash
vercel deploy [path] -y --no-wait
```

使用 `--no-wait` 以使 CLI 立即返回部署 URL 而不是阻塞直到构建完成（构建可能需要较长时间）。然后使用以下命令检查部署状态：

```bash
vercel inspect <deployment-url>
```

对于生产部署（仅当用户明确要求时）：
```bash
vercel deploy [path] --prod -y --no-wait
```

---

### 未链接 + CLI 已认证 → 首先链接，然后部署

CLI 可以正常工作，但项目尚未链接。这是将用户带入最佳状态的机会。

1. **询问用户要部署到哪个团队。** 呈现第 1 步中的团队 slugs 作为项目符号列表。如果只有一个团队（或仅个人账户），请跳过此步骤。

2. **选择团队后，立即进行链接。** 告知用户会发生什么，但不要单独进行确认：
   ```
   将此项目链接到 Vercel 上的 <team name>。这将创建一个部署的 Vercel 项目并启用未来的 git 推送自动部署。
   ```

3. **如果存在 git 远程，** 使用选定的团队范围进行基于仓库的链接：
   ```bash
   vercel link --repo --scope <team-slug>
   ```
   这会读取 git 远程 URL 并将其匹配到从该仓库部署的现有 Vercel 项目。它会创建 `.vercel/repo.json`。这比不带 `--repo` 的 `vercel link` 更可靠，后者尝试通过目录名称进行匹配，当本地文件夹和 Vercel 项目名称不同时经常失败。

   **如果不存在 git 远程，** 回退到标准链接：
   ```bash
   vercel link --scope <team-slug>
   ```
   这会提示用户选择或创建项目。它会创建 `.vercel/project.json`。

4. **然后使用最佳可用方法进行部署：**
   - 如果存在 git 远程 → 提交并推送（见 git push 方法）
   - 如果不存在 git 远程 → `vercel deploy [path] -y --no-wait --scope <team-slug>`，然后 `vercel inspect <url>` 检查状态

---

### 未链接 + CLI 未认证 → 安装、认证、链接、部署

Vercel CLI 完全未设置。

1. **安装 CLI（如果尚未安装）：**
   ```bash
   npm install -g vercel
   ```

2. **认证：**
   ```bash
   vercel login
   ```
   用户在浏览器中完成认证。如果在无法交互的环境（登录不可用）中运行，请跳转到**无认证回退**下方。

3. **询问要部署到哪个团队** — 呈现 `vercel teams list --format json` 中的团队 slugs 作为项目符号列表。如果只有一个团队 / 个人账户，请跳过。一旦选择，立即进行下一步。

4. **链接项目** 使用选定的团队范围（如果存在 git 远程，使用 `--repo`；否则使用普通 `vercel link`）：
   ```bash
   vercel link --repo --scope <team-slug>   # 如果存在 git 远程
   vercel link --scope <team-slug>          # 如果不存在 git 远程
   ```

5. **部署** 使用最佳可用方法（如果远程存在，则 git push；否则 `vercel deploy -y --no-wait --scope <team-slug>`，然后 `vercel inspect <url>` 检查状态）。

---

### 无认证回退 — claude.ai 沙盒

**何时使用：** 当 CLI 无法在 claude.ai 沙盒中安装或认证时。这不需要认证——它返回一个**预览 URL**（实时站点）和一个**声明 URL**（转移到您的 Vercel 账户）。

```bash
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh [path]
```

**参数：**
- `path` - 要部署的目录，或 `.tgz` 文件（默认为当前目录）

**示例：**
```bash
# 部署当前目录
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh

# 部署特定项目
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh /path/to/project

# 部署现有 tarball
bash /mnt/skills/user/deploy-to-vercel/resources/deploy.sh /path/to/project.tgz
```

脚本会自动检测 `package.json` 中的框架，打包项目（排除 `node_modules`、`.git`、`.env`），上传它，并等待构建完成。

**告知用户：** "您的部署已准备好，预览 URL 为 [previewUrl]。在 [claimUrl] 处声明它以管理您的部署。"

---

### 无认证回退 — Codex 沙盒

**何时使用：** 在 Codex 沙盒中，CLI 可能未认证。Codex 默认在沙盒化环境中运行——首先尝试使用 CLI，如果认证失败，则回退到部署脚本。

1. **检查 Vercel CLI 是否已安装**（无需进行升级检查）：
   ```bash
   command -v vercel
   ```

2. **如果 `vercel` 已安装，** 尝试使用 CLI 部署：
   ```bash
   vercel deploy [path] -y --no-wait
   ```

3. **如果 `vercel` 未安装，** 或 CLI 因 "未找到现有凭证" 而失败，**使用回退脚本：**
   ```bash
   skill_dir="<path-to-skill>"

   # 部署当前目录
   bash "$skill_dir/resources/deploy-codex.sh"

   # 部署特定项目
   bash "$skill_dir/resources/deploy-codex.sh" /path/to/project

   # 部署现有 tarball
   bash "$skill_dir/resources/deploy-codex.sh" /path/to/project.tgz
   ```

脚本处理框架检测、打包和部署。它会等待构建完成并返回包含 `previewUrl` 和 `claimUrl` 的 JSON。

**告知用户：** "您的部署已准备好，预览 URL 为 [previewUrl]。在 [claimUrl] 处声明它以管理您的部署。"

**升级网络访问权限：** 仅当沙盒化阻止网络调用（`sandbox_permissions=require_escalated`）时，才升级实际部署命令。**不要**升级 `command -v vercel` 检查。

---

## Agent-Specific Notes

### Claude 代码 / 基于终端的代理

您拥有完整的 shell 访问权限。**不要**使用 `/mnt/skills/` 路径。直接使用 CLI 按照上述决策流程执行。

对于无认证回退，从技能的安装位置运行部署脚本：
```bash
bash ~/.claude/skills/deploy-to-vercel/resources/deploy.sh [path]
```
路径可能因用户安装技能的位置而异。

### 沙盒化环境（claude.ai）

您可能无法运行 `vercel login` 或 `git push`。直接进入**无认证回退 — claude.ai 沙盒**。

### Codex

Codex 在沙盒化环境中运行。首先检查 CLI 是否可用，然后回退到部署脚本。进入**无认证回退 — Codex 沙盒**。

---

## 输出

始终向用户显示部署 URL。

- **Git push：** 使用 `vercel ls --format json` 找到预览 URL。如果 CLI 未认证，请告知用户检查 Vercel 仪表板或提交状态检查。
- **CLI 部署：** 显示 `vercel deploy --no-wait` 返回的 URL。使用 `vercel inspect <url>` 检查构建状态并报告给用户。
- **无认证回退：** 显示预览 URL 和声明 URL：
  ```
  部署成功！

  预览 URL: https://my-app-abc123.vercel.app
  声明 URL:   https://vercel.com/claim-deployment?code=...

  在预览 URL 处查看您的网站。
  要将此部署转移到您的 Vercel 账户，请访问声明 URL。
  ```

**不要**使用 curl 或 fetch 部署的 URL 来验证其是否正常工作。只需返回链接。

---

## 故障排除

### 网络出口错误（claude.ai）

如果由于 claude.ai 的网络限制导致部署失败，请告知用户：

```
部署因网络限制失败。要修复此问题：

1. 前往 https://claude.ai/settings/capabilities
2. 将 *.vercel.com 添加到允许的域名
3. 再次尝试部署
```

### 升级网络访问权限（Codex / 沙盒化环境）

如果由于网络问题（超时、DNS 错误、连接重置）在沙盒化环境中部署失败，使用升级权限重新运行（`sandbox_permissions=require_escalated`）。不要升级初始 CLI 可用性检查——仅升级实际部署命令。

示例指导用户：
```
部署需要升级网络访问权限才能部署到 Vercel。我可以使用升级权限重新运行命令——要继续吗？
```

### CLI 认证失败

如果 `vercel login` 或 `vercel deploy` 因认证错误而失败，回退到无认证部署脚本（根据环境可能是 claude.ai 或 Codex 变体）。
