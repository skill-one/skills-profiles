# 创建新的 AEM Edge Delivery 站点

本指南将引导您完成新 AEM Edge Delivery 站点的完整入职流程。它处理所有可自动化的任务，并明确标示需要人工操作的步骤。

## 使用此技能的场景

在以下情况下使用此技能：
- 用户希望从零开始创建全新的 AEM Edge Delivery 站点
- 用户要求“设置新站点”、“创建新的 EDS 项目”或“入职新站点”
- 项目目前还没有 GitHub 仓库或 DA 内容

**不要使用此技能的情况：**
- 导入或迁移现有页面（使用 **page-import** 技能）
- 在现有站点上构建或修改组件（使用 **content-driven-development** 技能）

## 前提条件

- 一个具有在目标组织创建仓库权限的 GitHub 账户
- 一个可以访问 DA（da.live）的 Adobe IMS 账户
- `gh` CLI 已认证（`gh auth status`）或具有 `repo` 范围的 GitHub 个人访问令牌
- Node.js（用于通过 da-auth-helper 管理 DA 令牌）

## 相关技能

- **page-import** — 将现有页面导入新创建的站点
- **content-driven-development** — 在站点存在后构建和修改组件
- **building-blocks** — 实现新组件代码

---

## 第 0 步：创建 TodoList

创建一个清单来跟踪进度（如果您的代理有任务跟踪工具，请使用它）：

1. **收集输入** — 收集组织、仓库名称、站点名称
2. **创建 GitHub 仓库** — 使用样板模板创建仓库
3. **安装 aem-code-sync** *(需要人工操作)* — 在仓库上安装 GitHub App
4. **使用 DA 进行身份验证** — 获取有效的 IMS 令牌
5. **在 DA 中创建初始内容** — 创建导航、页脚、索引
6. **触发预览** — 所有三个路径返回 200/201
7. **交接** — 将预览 URL 和 DA 链接交付给用户

---

## 第 1 步：收集输入

向用户请求以下信息。在提供所有必需输入之前，不要继续进行。

1. **GitHub 组织** — 仓库将创建的 GitHub 组织或用户名（例如 `my-org`）
2. **项目名称** — 仓库名称，小写，仅使用连字符（例如 `my-site`）
3. **站点名称** — 用于内容的人类可读名称（例如 `My Site`）。如果未提供，则从项目名称中派生。

存储为：`{{ORG}}`，`{{REPO}}`，`{{SITE_NAME}}`

---

## 第 2 步：创建 GitHub 仓库

使用 `adobe/aem-boilerplate` 模板创建新仓库。

**选项 A — GitHub CLI（首选，自动处理身份验证）：**
```bash
gh repo create {{ORG}}/{{REPO}} \
  --template adobe/aem-boilerplate \
  --description "{{SITE_NAME}} — AEM Edge Delivery 站点" \
  --public
```

使用 `gh auth status` 检查是否可以访问 `gh`。如果未认证，请先运行 `gh auth login`。

**选项 B — GitHub API（如果 `gh` CLI 不可用）：**
```
POST https://api.github.com/repos/adobe/aem-boilerplate/generate
Authorization: Bearer {{GITHUB_TOKEN}}
Content-Type: application/json

{
  "owner": "{{ORG}}",
  "name": "{{REPO}}",
  "description": "{{SITE_NAME}} — AEM Edge Delivery 站点",
  "private": false,
  "include_all_branches": false
}
```

获取令牌：https://github.com/settings/tokens/new — 范围：`repo`。

**成功：** HTTP 201（API）或退出代码 0（CLI）。现在可以在 `https://github.com/{{ORG}}/{{REPO}}` 访问仓库。

---

## 第 3 步：安装 aem-code-sync *(需要人工操作)*

aem-code-sync GitHub App 将仓库连接到 AEM 的内容交付管道。此步骤无法自动化 — 用户必须在浏览器中完成它。

告诉用户：

> **操作要求：** 在新仓库上安装 AEM Code Sync 应用。
>
> 1. 打开此 URL：https://github.com/apps/aem-code-sync/installations/new
> 2. 在“仓库访问”下，选择 **仅选择仓库**
> 3. 从列表中选择 **{{ORG}}/{{REPO}}**
> 4. 点击 **保存**
>
> 完成后回复 "done"。

在继续之前等待确认。

**验证：** 确认后，检查 `https://admin.hlx.page/status/{{ORG}}/{{REPO}}/main/` 返回有效的 JSON 响应（不是 404）。如果返回的是，则应用已正确安装。

---

## 第 4 步：使用 DA 进行身份验证

DA 需要 Adobe IMS 身份验证。选择适当的路径：

**选项 A — da-auth-helper（首选）**

`da-auth-helper`（https://github.com/adobe-rnd/da-auth-helper）在 `~/.aem/da-token.json` 中缓存 IMS 令牌。始终在触发新的 OAuth 流之前检查缓存。

1. 检查是否有有效的缓存令牌：
```bash
node -e "
  const fs = require('fs');
  const p = process.env.HOME + '/.aem/da-token.json';
  if (!fs.existsSync(p)) { console.log('No cache'); process.exit(1); }
  const t = JSON.parse(fs.readFileSync(p));
  console.log('Valid:', t.expires_at > Date.now());
  console.log('Expires:', new Date(t.expires_at).toISOString());
"
```

2. 如果有效，捕获令牌并跳到第 5 步：
```bash
DA_TOKEN=$(node -e "const t = require(process.env.HOME + '/.aem/da-token.json'); process.stdout.write(t.access_token);")
```

3. 如果缺失或过期，从 GitHub 安装 da-auth-helper（它未发布到 npm）并刷新：
```bash
npm install -g github:adobe-rnd/da-auth-helper
da-auth-helper token
```
这将打开浏览器进行 Adobe IMS 登录，并将新令牌写入 `~/.aem/da-token.json`。然后按第 2 步捕获它。

**选项 B — DA MCP 已配置**

如果 DA MCP 服务器可用，触发身份验证工具启动 OAuth 流，并与用户共享授权 URL。

**选项 C — 手动令牌**

要求用户从其浏览器（例如从 DA 网络选项卡或现有会话）获取 IMS 令牌并粘贴。存储为 `{{DA_TOKEN}}`。

---

## 第 5 步：在 DA 中创建初始内容

创建 EDS 站点所需的三个必填页面。使用以下模板精确创建 — 它们已预验证以符合 EDS 标准。

**选项 A — DA MCP：**
三次调用 DA 创建源工具，使用以下内容。

**选项 B — DA API：**

先将每个文件写入临时文件，然后使用 `@` 语法 POST。内联多行内容使用 `-F 'data=...'` 会导致 curl 失败（退出代码 26）。显式使用 `/usr/bin/curl` 以避免子 shell 中的 PATH 解析问题。

```bash
cat > /tmp/nav.html << 'EOF'
<nav content>
EOF
/usr/bin/curl -s -o /dev/null -w "%{http_code}" -X POST "https://admin.da.live/source/{{ORG}}/{{REPO}}/nav.html" \
  -H "Authorization: Bearer {{DA_TOKEN}}" \
  -F "data=@/tmp/nav.html;type=text/html"
```

对 `footer.html` 和 `index.html` 重复操作。

**验证：** 每次POST后，预期返回 HTTP 201。如果返回 401，则令牌已过期 — 返回第 4 步。

---

### nav.html

```html
<main>
  <div>
    <p><a href="/">{{SITE_NAME}}</a></p>
  </div>
  <div>
    <ul>
      <li><a href="/">Home</a></li>
    </ul>
  </div>
  <div></div>
</main>
```

### footer.html

```html
<main>
  <div>
    <p>© 2024 {{SITE_NAME}}. 保留所有权利。</p>
  </div>
</main>
```

### index.html

```html
<main>
  <div>
    <h1>欢迎来到 {{SITE_NAME}}</h1>
    <p>您的站点已准备就绪。开始在 DA 中编辑此页面。</p>
  </div>
</main>
```

---

## 第 6 步：触发预览

预览将 DA 内容拉入 AEM 交付管道，并在 `.aem.page` 域名上使其可访问。

DA 源内容需要在预览请求中使用 Bearer 令牌 — 即使对于公共仓库也是如此。显式使用 `/usr/bin/curl`。

```bash
/usr/bin/curl -s -o /dev/null -w "%{http_code}" -X POST "https://admin.hlx.page/preview/{{ORG}}/{{REPO}}/main/nav" \
  -H "Authorization: Bearer {{DA_TOKEN}}"
/usr/bin/curl -s -o /dev/null -w "%{http_code}" -X POST "https://admin.hlx.page/preview/{{ORG}}/{{REPO}}/main/footer" \
  -H "Authorization: Bearer {{DA_TOKEN}}"
/usr/bin/curl -s -o /dev/null -w "%{http_code}" -X POST "https://admin.hlx.page/preview/{{ORG}}/{{REPO}}/main/" \
  -H "Authorization: Bearer {{DA_TOKEN}}"
```

**成功：** 每个路径返回 HTTP 200 或 201。主页现在可以在：
```
https://main--{{REPO}}--{{ORG}}.aem.page/
```

---

## 第 7 步：确认并交接

告诉用户：

> **您的站点已准备就绪！**
>
> - **预览：** `https://main--{{REPO}}--{{ORG}}.aem.page/`
> - **在 DA 中浏览内容：** `https://da.live/#/{{ORG}}/{{REPO}}/`
> - **编辑主页：** `https://da.live/edit#/{{ORG}}/{{REPO}}/index`
> - **编辑导航：** `https://da.live/edit#/{{ORG}}/{{REPO}}/nav`
> - **编辑页脚：** `https://da.live/edit#/{{ORG}}/{{REPO}}/footer`
> - **GitHub 仓库：** `https://github.com/{{ORG}}/{{REPO}}`
>
> 要开始本地开发：
> ```bash
> git clone https://github.com/{{ORG}}/{{REPO}}.git
> cd {{REPO}}
> npm install
> aem up
> ```
>
> 您想接下来做什么 — 添加更多页面、自定义组件或设置自定义域名？

---

## 故障排除

| 症状 | 可能的原因 | 解决方法 |
|---|---|---|
| 第 2 步返回 422 | 仓库名称已存在 | 要求用户使用不同的名称 |
| 第 3 步验证返回 404 | 未安装 aem-code-sync | 重新发送安装 URL |
| 第 4 步缓存令牌缺失/过期 | 此机器上没有之前的 DA 会话 | 从 GitHub 安装 da-auth-helper (`npm install -g github:adobe-rnd/da-auth-helper`) 并运行 `da-auth-helper token` |
| 第 5 步 curl 退出代码 26 | `-F` 标志中的内联多行内容 | 将内容写入临时文件并使用 `@/tmp/file.html` 语法 |
| 第 5 步返回 401 | 过期或缺失 IMS 令牌 | 重新检查 `~/.aem/da-token.json` 过期时间；要求用户获取新令牌 |
| 第 5 步返回 403 | 令牌缺乏对此组织/仓库的权限 | 确认用户在 DA 中具有 `{{ORG}}/{{REPO}}` 的写入权限 |
| 第 6 步返回 401 | DA 源内容需要在预览请求中进行身份验证 | 在预览请求中添加 `-H "Authorization: Bearer {{DA_TOKEN}}"` |
| 第 6 步返回 404 | aem-code-sync 未正确安装 | 验证第 3 步，然后重试 |
| 脚本中 `curl: command not found` | 子 shell 中未解析 PATH | 显式使用 `/usr/bin/curl` |
| 预览 URL 显示空白页面 | nav 或 index 未预览 | 重新运行第 6 步针对失败的路径 |

---

## 参考

- 样板：https://github.com/adobe/aem-boilerplate
- aem-code-sync 应用：https://github.com/apps/aem-code-sync
- DA 文档：https://da.live/docs
- DA Admin API：https://opensource.adobe.com/da-admin/
- DA Auth（IMS 令牌助手）：https://github.com/adobe-rnd/da-auth-helper
- AEM Admin API：https://www.aem.live/docs/admin.html
- 完整入职指南：https://www.aem.live/developer/create-site.md

### DA URL 模式

- 浏览文件夹：`https://da.live/#/{{org}}/{{repo}}{{folder-path}}`
- 编辑 HTML 文档：`https://da.live/edit#/{{org}}/{{repo}}{{path-without-extension}}`
- 编辑 JSON/表单：`https://da.live/sheet#/{{org}}/{{repo}}{{path-without-extension}}`
