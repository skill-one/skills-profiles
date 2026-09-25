# Vercel CLI 技能

Vercel CLI (`vercel` 或 `vc`) 可从命令行部署、管理和开发 Vercel 平台上的项目。使用 `vercel <命令> --help` 获取任何命令的完整标志详情。

已安装的 CLI 帮助信息是模糊或新添加标志的权威来源。如果这里的命令示例不够，请在采取行动前检查 `vercel <命令> --help` 而不是猜测。

仅解析 stdout 获取 URL 和 JSON。警告、进度和 `--help` 输出到 stderr；仅在搜索帮助文本时合并流。某些帮助命令在打印使用说明后退出状态码 2，因此将打印的使用说明视为成功的帮助读取。

在代理/非交互模式下，许多命令将错误和所需确认作为包含 `status`、`reason`、`hint` 和 `next`（可运行的后续命令）的 JSON 对象输出到 stdout。优先选择建议的 `next` 命令，而不是在确认它保留了用户的预期目标和授权后仅重试；不要自动运行链接、认证或变更后续操作。读取 `list`、`logs`、`inspect` 和 `api` 等命令保持其正常输出格式。

## 重要提示：项目链接

项目上下文取决于命令的工作目录。在进行有意义的读取或变更之前，从预期目录运行 `vercel project inspect --non-interactive` 并确认报告的所有者和项目。此命令在非交互模式下仅解析现有上下文；在遇到 `link_required` 或目标不匹配时停止，而不是自动链接。

许多感知项目的命令也接受 `--project <名称或ID>` 与 `--scope <团队>` 以显式指定单命令目标。在使用它们之前，确认目标和范围是否保留了用户的意图。

- **`<cwd>/.vercel/project.json`**：由 `vercel link` 创建。此精确的工作目录链接优先于仓库链接。CLI 通常不会从任意子目录继承根 `project.json`。
- **`<repo-root>/.vercel/repo.json`**：由 `vercel link --repo` 创建。CLI 选择包含工作目录的最深层项目目录。
- **不匹配的仓库路径**：如果没有任何仓库映射包含工作目录，交互式仓库解析会在配置的项目中提示。非交互式仓库解析当前选择唯一配置的项目，或在存在多个选择时保持未解析状态。然后，设置项目的命令可能会进入链接流程，因此非交互模式通常不会导致失败。

位于应用目录内并不能证明已选择预期的项目。明确检查解析的项目，尤其是在仓库映射不覆盖该目录时。

`vercel whoami --format json` 识别认证用户和有效团队；纯非 TTY 的 `vercel whoami` 仅打印用户名。两者都不验证链接的项目。只读项目命令仍可能需要登录或团队 SAML 重新认证并打开浏览器/设备流程。在继续之前，请提示用户完成该流程。

## 快速入门

```bash
npm i -g vercel
vercel login
vercel link              # 单个项目
# 或者
vercel link --repo       # 单一仓库
vercel pull
vercel dev        # 本地开发
vercel deploy     # 预览部署
vercel --prod     # 生产部署
```

## 决策树

使用此路由到正确的参考文件：

- **部署、重新部署、强制构建、无缓存构建或部署源/来源** → `references/deployment.md`
- **滚动发布、部署钩子、定时任务、缓存、git 连接、边缘配置、重定向、自定义环境** → `references/project-infra.md`
- **本地开发** → `references/local-development.md`
- **环境变量** → `references/environment-variables.md`
- **CI/CD 自动化** → `references/ci-automation.md`
- **域名或 DNS** → `references/domains-and-dns.md`
- **项目或团队** → `references/projects-and-teams.md`
- **Vercel 工具栏评论 (`vercel comments`)** → `references/comments.md`
- **构建失败、部署错误、日志、指标、Speed Insights、核心网络生命体征、活动、性能、预览访问或生产调试** → `references/monitoring-and-debugging.md`
- **警报、使用量、合同、计费购买、令牌、遥测或 CLI 升级** → `references/platform-ops.md`
- **对象存储** → `references/storage.md`
- **容器注册表 (`vercel vcr`：仓库、镜像、标签、docker/podman/buildah 登录、推送/拉取)** → `references/container-registry.md`
- **集成（数据库、存储等）** → `references/integrations.md`
- **连接器 (`vercel connect`)** → `references/connectors.md`
- **路由规则** → `references/routing.md`
- **防火墙（WAF 规则、IP 块、速率限制）** → `references/firewall.md`
- **访问预览部署** → 使用 `vercel curl`（参见 `references/monitoring-and-debugging.md`）
- **CLI 命令不可用或输出缺少所需字段** → 在第一类 CLI 路径不可用或不足时使用 `vercel api`（参见 `references/advanced.md`）
- **Node.js 后端（Express、Hono 等）** → `references/node-backends.md`
- **单一仓库（Turborepo、Nx、工作区）** → `references/monorepos.md`
- **Bun 运行时** → `references/bun.md`
- **功能标志 (`vercel flags`：创建、检查、设置、拆分、发布、规则、分段、sdk-keys)** → `references/flags.md`
- **微前端** → `references/microfrontends.md`
- **沙盒** → `references/sandbox.md`
- **代理、MCP、技能发现或 AI 网关** → `references/agent-and-ai.md`
- **捕获的请求跟踪 (`vercel traces`，包括 `--open` / `--view`)** → `references/advanced.md`
- **高级 (`vercel api` 回退、webhooks)** → `references/advanced.md`
- **全局标志** → `references/global-options.md`
- **首次设置** → `references/getting-started.md`

## 反模式

- **在具有多个项目的单一仓库中使用错误的链接类型**：`vercel link` 创建 `project.json`，它仅跟踪一个项目。使用 `vercel link --repo` 代替。当出现问题时，首先检查 `.vercel/`。
- **在单一仓库中让命令自动链接**：如果 `.vercel/` 不存在，许多命令会隐式运行 `vercel link`。这会创建 `project.json`，它可能是错误的。首先运行 `vercel link`（或 `--repo`）。
- **假设应用子目录决定了项目**：使用 `vercel project inspect --non-interactive` 进行验证；当前不匹配的仓库路径可以在非交互模式下回退到唯一配置的项目。
- **使用 `vercel whoami` 作为链接项目验证**：`vercel whoami --format json` 报告认证和团队上下文，而不是选择的项目。
- **在纯 CI 运行中忘记非交互标志**：检测到的代理默认获得 `--non-interactive`，但纯 CI 没有 — 在那里显式传递它，并且仅在需要确认的命令中添加 `--yes`。
- **在 `vercel build` 后使用 `vercel deploy` 而没有 `--prebuilt`**：构建输出会被忽略。
- **使用 `vercel redeploy` 进行无缓存重建**：`vercel redeploy` 不暴露无缓存标志；当您需要不保留构建缓存的最新部署时，使用 `vercel deploy --force` 而不使用 `--with-cache`。
- **在标志中硬编码令牌**：使用 `VERCEL_TOKEN` 环境变量，而不是 `--token`。
- **禁用部署保护**：使用 `vercel curl` 而不是访问预览部署。
- **过早使用 `vercel api`**：当第一类 CLI 命令暴露所需数据或变更时，优先使用它们。
