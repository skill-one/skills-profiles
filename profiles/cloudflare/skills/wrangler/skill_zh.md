# Wrangler CLI

在编写命令或配置之前，请使用项目的 Wrangler 版本并获取相关文档。CLI 标志和配置字段会发生变化；不要依赖记忆中的示例。

## 检查项目

- 找到包管理器、安装的 Wrangler 版本、包脚本、框架和 Wrangler 配置。通过项目的脚本或包管理器运行命令，以便它们使用其本地版本。在需要时使用现有的锁定文件安装依赖项；不要在无声中升级 Wrangler 以匹配当前文档。如果 Wrangler 不是依赖项，请按照 [安装指南](https://developers.cloudflare.com/workers/wrangler/install-and-update/) 将其本地添加。
- 确定构建或部署命令使用的配置，包括框架生成的配置。编辑其源代码，而不是生成的输出。
- 在运行会更改它们的命令之前，确定目标帐户、Worker、环境和资源。对于数据操作，确定目标是本地还是远程。

## 获取任务所需内容

如果可用，请使用 Cloudflare MCP `docs` 工具，或直接获取相关链接页面。遵循指向特定命令或产品的链接；避免加载整个参考。如果页面已移动，请通过 [Wrangler 命令索引](https://developers.cloudflare.com/workers/wrangler/commands/) 或 Cloudflare 文档搜索重新发现它。

| 任务 | 来源 |
| --- | --- |
| 发现命令和标志，包括资源管理、部署、回滚和诊断 | 项目本地的 `wrangler --help` 和 `wrangler <command> --help`；[命令参考](https://developers.cloudflare.com/workers/wrangler/commands/) |
| 编辑配置或添加绑定 | 安装的 `wrangler/config-schema.json`（通常在 `node_modules` 下）；[配置参考](https://developers.cloudflare.com/workers/wrangler/configuration/) |
| 部署框架应用程序 | [框架指南](https://developers.cloudflare.com/workers/framework-guides/)；遵循项目现有框架和适配器的指南 |
| 在请求时将应用程序迁移到 Workers | [页面到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)；[Vercel 到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/vercel-to-workers/) |
| 配置暂存或生产环境 | [环境](https://developers.cloudflare.com/workers/wrangler/environments/) |
| 在本地、CI 或已部署的 Worker 上设置密钥 | [密钥](https://developers.cloudflare.com/workers/configuration/secrets/) |
| 生成绑定和运行时类型 | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/) |
| 本地运行或选择测试方法 | [本地开发](https://developers.cloudflare.com/workers/local-development/)；[测试](https://developers.cloudflare.com/workers/testing/) |
| 为 Wrangler 选择角色、范围或 API 令牌权限 | [角色和权限](https://developers.cloudflare.com/workers/authorization/)；[Workers 角色和权限](https://developers.cloudflare.com/workers/authorization/workers/#wrangler) |
| 创建或管理分支或拉取请求环境 | [预览概述](https://developers.cloudflare.com/workers/previews/)；[开始使用](https://developers.cloudflare.com/workers/previews/get-started/)；[配置](https://developers.cloudflare.com/workers/previews/configuration/) |
| 决定预览资源是否隔离或共享 | [资源和隔离](https://developers.cloudflare.com/workers/previews/resources/)，包括其当前限制 |
| 配置预览 URL、访问、调试或 CI | [自定义域名](https://developers.cloudflare.com/workers/previews/custom-domains/)；[测试和调试](https://developers.cloudflare.com/workers/previews/test-and-debug/)；[示例](https://developers.cloudflare.com/workers/previews/examples/) |
| 在预览、版本 URL 和 Wrangler 环境之间选择 | [比较工作流](https://developers.cloudflare.com/workers/previews/compare-workflows/) |
| 诊断身份验证或选择帐户 | [通用命令](https://developers.cloudflare.com/workers/wrangler/commands/general/)，包括 `whoami`；[身份验证配置文件](https://developers.cloudflare.com/workers/wrangler/profiles/) |
| 部署未身份验证的原型 | [声明部署](https://developers.cloudflare.com/workers/platform/claim-deployments/) 以处理资格、过期和声明 URL；使用永久帐户进行生产或 CI |

使用已安装的帮助和模式来检查项目中是否存在文档中记录的功能。如果需要升级所需功能，请明确该依赖项。如果无法检索，请说明差距，并使用可用的本地证据，而不是编造语法。

## 应用更改

- 优先使用 `wrangler.jsonc` 进行新配置。将新项目的 [兼容性日期](https://developers.cloudflare.com/workers/configuration/compatibility-dates/) 设置为今天；在推进现有项目的日期时，请检查运行时更改并进行测试。保留现有项目的约定，并避免偶然的格式迁移。
- 在添加绑定或变量之前检查环境继承。某些字段必须为每个环境单独指定；一个工作的默认配置并不能证明暂存环境已配置。
- 使用 Cloudflare Vite 插件，在开发或构建时通过 `CLOUDFLARE_ENV` 选择环境。部署生成的构建；在部署时设置环境不会重新定位其扁平化配置。请参阅 [Vite 环境](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/)。
- 在部署之前，请与配置重新协调仪表板更改：Wrangler 可以覆盖仪表板变量和路由。在绑定现有资源时，请验证它们的标识符；省略标识符可能会触发 [自动提供](https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning)。
- 在开发过程中区分本地模拟和远程绑定。即使 Worker 在本地运行，它仍然可以访问真实资源；在测试写入之前，请检查所选的绑定。
- 在远程命令之前，请确定经过身份验证的成员或 API 令牌，并检索执行确切操作所需的当前角色和范围。优先选择最窄的范围来满足用户的意图。`wrangler login` OAuth 流不支持粒度授权；当需要粒度访问时，请使用帐户拥有的 API 令牌，并且永远不要要求用户将它的值粘贴到聊天中。
- 不要将密钥值放入命令参数、源代码和日志中。使用命令的文档交互式输入或受保护文件/stdin 机制。本地密钥文件必须被版本控制忽略，并且不会自动作为部署的密钥上传。对于缺失的本地密钥，请检查文件优先级以及密钥文档中任何 `secrets.required` 声明。
- 将 `wrangler secret put` 和 `secret delete` 视为部署：它们创建一个版本并立即部署它。当更改必须分阶段时，请使用文档中的 `wrangler versions secret` 工作流。
- 在回滚之前，请检查 [回滚限制](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/)：连接的资源和其数据不会与 Worker 代码一起回滚。

## 使用 Workers 预览

- Workers 预览需要项目本地的 Wrangler 4.135.0 或更高版本；项目命令不使用更新的全局安装。检查项目的固定版本，并明确任何必需的依赖项升级。
- 使用预览来管理分支和拉取请求环境，这些环境在同一个 Worker 下。使用版本 URL 来检查已上传的特定版本及其生产资源，并使用 Wrangler 环境来管理持久且单独部署的 Worker。请遵循 [比较工作流](https://developers.cloudflare.com/workers/previews/compare-workflows/)，而不是调整较旧的别名版本 URL 工作流。
- 首先检查用户如何管理生产配置和部署。通过相同的配置系统（例如 Wrangler、仪表板或 Terraform）配置预览域名。通过用户现有的路径运行预览部署，例如本地 CLI、Workers Builds 或外部 CI，除非用户请求不同的工作流。镜像管理方法，而不是生产资源绑定或数据。
- 在部署之前，请遵循当前的 [配置放置表](https://developers.cloudflare.com/workers/previews/configuration/#what-goes-in-the-previews-block) 和 [资源矩阵和限制](https://developers.cloudflare.com/workers/previews/resources/)。不要从预览名称推断隔离性，除非用户明确打算共享生产资源。
- 告知用户预览 URL 是公开的，除非配置了访问控制，然后让他们决定是否要保护这些 URL。请遵循为所选设置准备的 [自定义域名和访问指南](https://developers.cloudflare.com/workers/previews/custom-domains/)。
- 确认用户打算目标哪个 Worker 或 Wrangler 环境。当目标 Wrangler 环境时，请向每个预览命令传递相同的 `--env` 值；省略它将目标定位到顶级 Worker。

## 验证

在 TypeScript 项目中更改配置或绑定后，请使用项目的 `wrangler types` 命令重新生成类型，而不是手动编辑生成的声明。运行相关的现有类型检查或测试。

对于部署更改，请使用项目的构建工作流，并在支持的地方使用 `wrangler deploy --dry-run`，并使用预期的配置和环境。成功的干运行检查构建和打包；它并不能证明远程资源或运行时行为正常。根据请求的工作，使用适当的本地或远程检查。
对于预览，返回的 URL 并不能验证依赖于 Wrangler 报告为缺失的绑定的行为。请验证用户请求的行为，并在需要时使用预览特定的日志和配置。对生产资源的写入、破坏性测试和删除命名预览必须与用户的明确意图匹配。

报告发生了什么更改、目标环境、执行的检查以及任何未解决的验证差距。当结果取决于当前命令或配置行为时，请链接使用的文档。
