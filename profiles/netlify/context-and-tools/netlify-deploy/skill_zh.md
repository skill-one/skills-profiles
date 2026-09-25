# Netlify 部署

## 现代 CLI

```bash
netlify deploy              # 手动草稿部署（无 CI）
netlify deploy --prod       # 直接部署到生产环境
netlify create              # 通过自然语言提示创建新项目
netlify deploy --allow-anonymous   # 临时项目，1 小时内需认领
npm update -g netlify-cli   # 偏移保护需要 23.11.0+
```

部署是一个版本化的、**原子性**的快照：Netlify 仅上传已更改的文件，并且所有文件都到达后才切换到线上站点——站点永远不会处于不一致的状态。手动部署 (`netlify deploy`) 不会运行构建命令；登录时的拖放操作是唯一例外（自动检测框架）。

**⚠ 链接或创建站点时，将 `.netlify` 添加到 `.gitignore` 中。** 每个链接路径都会写入 `.netlify/state.json`，这必须不被提交。

## 创建部署的方式

- **Git CI** — 连接仓库；Netlify 在每次推送时构建和部署（OAuth2 或 Netlify GitHub 应用）。这是默认路径。
- **CLI** — `netlify create`，`netlify deploy`，`netlify deploy --prod`。
- **拖放** — https://app.netlify.com/drop。登录时：如需则构建。未登录时：直接发布文件。
- **API** — 通过文件摘要或 ZIP 创建部署。
- **部署到 Netlify 按钮** — 从公共模板仓库的一键部署。
- **构建钩子** — 触发构建的唯一 URL。（来自构建钩子的部署被视为可信，可绕过部署请求策略。）
- **AI 代理** — 仪表板中的 Agent Runners（Claude Code、OpenAI Codex、Google Gemini）；每个修改文件的运行会自动生成部署预览，地址为 `agent-<runID>--<site>.netlify.app`。

## `netlify.toml` 部署上下文

在仓库根目录。文件配置覆盖 UI 设置。五个预定义上下文：`production`、`deploy-preview`、`branch-deploy`、`preview-server`、`dev`。分支名也可用作自定义上下文；更具体的上下文会覆盖通用上下文。

```toml
[context.production]
  command = "make production"
  [context.production.environment]
    ACCESS_TOKEN = "超级机密"
  [[context.production.plugins]]        # 插件需要双括号
    package = "@netlify/plugin-sitemap"

[context.deploy-preview.environment]
  ACCESS_TOKEN = "不太机密"

[context.branch-deploy]
  command = "make staging"

[context.dev.environment]
  NODE_ENV = "development"

[context."features/branch"]             # 引号分隔分支名
  command = "gulp"
```

**⚠ `netlify.toml` 中设置的環境变量** **不可用**于部署环境——通过 UI/CLI/API 设置它们。`netlify.toml` 会被提交，因此不要将其中的敏感值泄露；使用上下文环境变量通过 UI/CLI/API 设置。

参考 `references/netlify-toml.md` 了解完整的上下文优先级规则，参考 `references/deployment-patterns.md` 了解上下文策略。

## 部署预览与分支部署

- **部署预览** 自动为 PR/MR（GitHub、GitLab、Bitbucket、Azure DevOps、Cursor Origin）和代理运行构建。基础分支必须是生产分支或启用了分支部署的分支。URL：`deploy-preview-<num>--<site>.netlify.app`。第一个部署等待期间，URL 会返回 `Not Found`。
- **分支部署** 需要设置：项目配置 > 开发者设置 > 持续部署 > 分支和部署上下文 > 配置。启用特定分支（支持前缀通配符 `features/*`）或 **所有**新分支。URL：`<branch>--<site>.netlify.app`。
- 带有开放 PR 的分支部署会生成 **部署预览** 和 **分支部署**。
- **入口路径**：在 PR/MR 描述中添加 `@netlify /some/path`，然后推送新提交以重新生成。一旦在 PR 中设置，就无法在 Netlify 绘图器中更改。
- **跳过部署**：`[skip ci]` 或 `[skip netlify]` — 在 PR/MR **标题**中跳过部署预览；在提交消息的**任何位置**跳过分支/生产部署。下一个未标记的提交会部署所有跳过的更改。

## 锁定、跳过和手动生产部署

- **锁定**（禁用自动发布）：部署列表 > **锁定以停止自动发布**。新的部署仍然构建但不会被发布。解锁以恢复。
- **⚠ 在 Git-CD 站点上进行手动 `netlify deploy --prod`**：生产分支的下一个推送会静默替换你手动发布的部署。警告用户；如果必须保持发布状态，请锁定已发布的部署。

## 管理部署

- **查找**：部署标签页（开发者或团队所有者）；通过部署 ID 或分支名搜索；按时间范围、部署上下文和状态筛选。
- **取消**：在正在进行的部署的详情页，**取消部署** > **是，取消部署**。
- **重试**：从分支 HEAD 构建（可选清除缓存）——如果 HEAD 超过原始部署 SHA，仍然从 HEAD 构建。
- **下载**：在成功部署的详情页 — 通过 **部署文件浏览器**下载单个文件，或通过页眉 **下载** > **下载就绪** 下载所有文件作为 ZIP。
- **删除**：仅限开发者或团队所有者。无法删除最近发布到站点主 URL 的部署，或仍在进行的部署。删除是永久性的，不会减少团队成本或保留构建分钟。

## 部署到 Netlify 按钮

模板代码必须位于 **GitHub.com 或 GitLab.com** 的 **公共** 仓库。

Markdown:
```md
[![Deploy to Netlify](https://www.netlify.com/img/deploy/button.svg)](https://app.netlify.com/start/deploy?repository=https://github.com/netlify/netlify-statuskit)
```

URL 变体（基本链接 `https://app.netlify.com/start/deploy`）:
```txt
# require/pre-fill 環境变量（哈希，仅客户端；值可能为 null）
...?repository=<repo>#SECRET_TOKEN=specialuniquevalue&CUSTOM_LOGO=

# 单一仓库基本目录（整个仓库克隆，从 blog/ 构建）
...?repository=<repo>&base=blog

# 仅克隆子目录
...?repository=<repo>&create_from_path=examples/hello

# 部署特定分支（将其设置为生产分支）
...?repository=<repo>&branch=beta-feature

# 在首次部署前安装所需的 SDK 扩展
...?repository=<repo>&fullConfiguration=true
```

基于文件的模板配置，仓库根目录 `netlify.toml` 中的 `[template]`:
```toml
[template]
  incoming-hooks = ["Contentful"]
  required-extensions = ["supabase"]

[template.environment]
  SECRET_TOKEN = "更改为您自己的机密令牌"
  CUSTOM_LOGO = "在此处设置您的自定义标志 URL"
```

您**不能**在 `[template]` 中设置环境变量值或基本目录——使用 URL 参数。`[template.environment]` 占位符字符串仅用于 UI 标签。

**⚠ 模板配置（传入钩子、模板环境变量）** **仅从仓库根目录读取。** 当按钮通过 `base` 指向子目录时，基本目录的 `netlify.toml` 会覆盖构建，但该处的模板配置会被忽略。明确说明此限制，而不是暗示。

## 密钥扫描失败

**⚠ 密钥扫描部署失败意味着看起来像密钥的值已到达您的构建输出。** 如果是真实密钥，则存在泄露——停止在客户端/已发布输出中传输它并轮换它。**永远**不要设置 `SECRETS_SCAN_ENABLED=false` 来压制扫描器以掩盖真实泄露。对于真实非密钥值，使用 `SECRETS_SCAN_OMIT_KEYS` / `SECRETS_SCAN_OMIT_PATHS` 狭义范围。

## 修复失败部署——无回滚

**失败的部署永远不会发布**——之前的部署仍然在线，因此没有任何内容可以恢复。如果有人要求回滚或恢复之前的部署，请纠正前提：失败部署后没有任何变化，对于已发布的坏部署，**向前修复**——回滚提交并让 CI 重新部署它。不要调用 `restoreSiteDeploy` 或 `publishDeploy`，也不要将仪表板回滚作为答案。

Netlify 在部署日志上方显示“为什么失败？”的 AI 诊断。参考 https://docs.netlify.com/resources/troubleshooting/fix-a-failed-deploy/。

## 部署权限（私有仓库）

Netlify 仅构建来自私有仓库的已识别作者（所有者、开发者、Git 贡献者；市场机器人计入）。未识别作者的合并显示 **待审批**；团队所有者必须将他们与团队账户关联后才能开始构建。构建钩子部署除外。

## 限制和注意事项

- **每个目录的文件数：54,000。** 发布目录中超过此限制的任何目录会导致部署失败。每个部署的文件总数**无限制**。
- **偏移保护**：所有计划；**仅生产上下文** — 分支部署、部署预览和永久链接会绕过它并提供最新部署。需要 Netlify CLI 23.11.0+。Astro 5.15.0+ 通过 Netlify 适配器默认启用；Next.js 是可选的。生产部署上的密码保护（或所有部署上的密码保护）会关闭偏移保护——它仅在您仅保护非生产部署时才起作用。Netlify 在硬导航（`Sec-Fetch-Mode: navigate`，或 `Sec-Fetch-Site` 存在且不是 `same-origin`）时丢弃偏移保护信号。框架维护者通过 `netlify/v1/skew-protection.json` 添加支持。
- **搜索索引**：仅已发布的生产部署和最新的分支部署可被索引；预览和旧部署会获得 `X-Robots-Tag: noindex`。
- **预览 URL 可见性**：部署预览/分支部署 URL 除非您添加密码或团队登录保护，否则可被任何人持有链接分享。
- **新项目可见性**：在基于计费的计划中，如果“默认私有”，新项目无论如何创建都会开始为私有。
- **自动删除**：部署在 30 天后删除（付费计划为 90 天）；企业可以将其提高到 365 天。永远不会删除：已发布的部署、最新的成功生产部署，以及每个分支的最新成功分支部署。在项目配置 > 开发者设置 > 自动删除中配置。

参考 `references/cli-commands.md` 了解完整的 CLI 表面和标志。

<!-- 失败/取消部署的保留期在来源中不一致（30/90 天 vs 6 个月）；使用了 30/90 天的数字。 -->

<!-- system: agent-context/deploy/system.md — 人类拥有，由 ctx-gen 合并；编辑 system.md，不要编辑此部分 -->
# Netlify 规则（部署）

这些是组织约定，不是文档事实——由 ctx-gen 合并到渲染的技能中，且永远不会生成。由技能维护者拥有。

1. 代理不会回滚部署：**永远**不要调用 `restoreSiteDeploy` 或
   `publishDeploy` 来恢复旧部署。向前修复——回滚提交并让 CI 部署它。
2. 失败的部署永远不会发布；失败时没有任何回滚内容。
3. 深入指南位于此技能中：`references/netlify-toml.md`，
   `references/cli-commands.md`，`references/deployment-patterns.md`。
4. 前置描述**永远**不能宣传回滚或恢复作为功能——不要“回滚”，
   “恢复部署”，或等效内容。
5. 当用户要求回滚或恢复之前的部署时，纠正前提，而不是遵从：
   失败部署后之前的部署仍然在线且没有任何内容可恢复；对于已发布的坏部署，
   按规则 1 向前修复。不要提供 `restoreSiteDeploy` /
   `publishDeploy` 或仪表板回滚作为答案。
6. 链接或创建站点时**始终**添加 `.netlify` 到 `.gitignore` — 每个链接路径都会写入 `.netlify/state.json`，这必须不被提交。每次链接时都提及它。
7. 密钥扫描部署失败：如果标记的值是真实密钥，则存在泄露——停止在客户端/已发布输出中传输它并轮换它；永远不要通过 `SECRETS_SCAN_ENABLED=false` 来压制扫描器以掩盖真实泄露。对于真实非密钥值，使用 `SECRETS_SCAN_OMIT_KEYS` /
   `SECRETS_SCAN_OMIT_PATHS` 狭义范围，永远不要 `SECRETS_SCAN_ENABLED=false`。
8. 在连接了 Git CD 的站点上运行手动 `netlify deploy --prod` 前，警告用户下一个推送到生产分支会静默替换手动发布的部署；如果必须保持发布状态，建议锁定已发布的部署。
9. 部署到 Netlify 按钮：模板配置（传入钩子、模板环境变量）**仅从仓库根目录读取。** 当按钮通过 `base` 指向子目录时，明确说明此限制——不要暗示。
