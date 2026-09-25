# Wrangler 命令行界面

在编写命令或配置之前，请使用项目的 Wrangler 版本并获取相关文档。命令行标志和配置字段会发生变化；不要依赖记忆中的示例。

## 检查项目

- 找到包管理器、已安装的 Wrangler 版本、包脚本、框架和 Wrangler 配置。通过项目的脚本或包管理器运行命令，以便它们使用其本地版本。在需要时使用现有的锁定文件安装依赖项；不要在当前文档中无声升级 Wrangler。如果 Wrangler 不是依赖项，请按照 [安装指南](https://developers.cloudflare.com/workers/wrangler/install-and-update/) 将其本地添加。
- 确定构建或部署命令使用的配置，包括框架生成的配置。编辑其源代码，而不是生成的输出。
- 在运行更改它们的命令之前，确定目标帐户、Worker、环境和资源。对于数据操作，确定目标是本地还是远程。

## 获取任务所需内容

如果可用，请使用 Cloudflare MCP `docs` 工具，或者直接获取相关链接页面。遵循链接到特定命令或产品；避免加载整个参考。如果页面已移动，请通过 [Wrangler 命令索引](https://developers.cloudflare.com/workers/wrangler/commands/) 或 Cloudflare 文档搜索重新发现它。

| 任务 | 来源 |
| --- | --- |
| 发现命令和标志，包括资源管理、部署、回滚和诊断 | 项目本地的 `wrangler --help` 和 `wrangler <命令> --help`；[命令参考](https://developers.cloudflare.com/workers/wrangler/commands/) |
| 编辑配置或添加绑定 | 已安装的 `wrangler/config-schema.json`（通常在 `node_modules` 下）；[配置参考](https://developers.cloudflare.com/workers/wrangler/configuration/) |
| 部署框架应用程序 | [框架指南](https://developers.cloudflare.com/workers/framework-guides/)；遵循项目现有框架和适配器的指南 |
| 在请求时将应用程序迁移到 Workers | [页面到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)；[Vercel 到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/vercel-to-workers/) |
| 配置暂存或生产环境 | [环境](https://developers.cloudflare.com/workers/wrangler/environments/) |
| 在本地、CI 或已部署的 Worker 上设置密钥 | [密钥](https://developers.cloudflare.com/workers/configuration/secrets/) |
| 生成绑定和运行时类型 | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/) |
| 本地运行或选择测试方法 | [本地开发](https://developers.cloudflare.com/workers/local-development/)；[测试](https://developers.cloudflare.com/workers/testing/) |
| 诊断身份验证或选择帐户 | [通用命令](https://developers.cloudflare.com/workers/wrangler/commands/general/)，包括 `whoami`；[身份验证配置文件](https://developers.cloudflare.com/workers/wrangler/profiles/) |
| 部署未身份验证的原型 | [声明部署](https://developers.cloudflare.com/workers/platform/claim-deployments/) 以处理资格、过期和声明 URL；使用永久帐户进行生产或 CI |

使用已安装的帮助和模式来检查项目版本中是否存在文档中记录的功能。如果需要升级的功能，请明确该依赖项。如果无法检索，请说明差距并使用可用的本地证据，而不是编造语法。

## 应用更改

- 优先使用 `wrangler.jsonc` 进行新配置。将新项目的 [兼容性日期](https://developers.cloudflare.com/workers/configuration/compatibility-dates/) 设置为今天；在推进现有项目的日期时，请检查运行时更改并进行测试。保留现有项目的约定，并避免偶然的格式迁移。
- 在添加绑定或变量之前检查环境继承。某些字段必须为每个环境单独指定；一个工作的默认配置并不能证明暂存环境已配置。
- 使用 Cloudflare Vite 插件，在开发或构建时通过 `CLOUDFLARE_ENV` 选择环境。部署生成的构建；在部署时设置环境不会重新定位其扁平化配置。请参阅 [Vite 环境](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/)。
- 在部署之前，将仪表板更改与配置进行协调：Wrangler 可以覆盖仪表板变量和路由。在绑定现有资源时，请验证它们的标识符；省略的标识符可能会触发 [自动配置](https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning)。
- 在开发过程中区分本地模拟和远程绑定。本地运行的 Worker 仍然可以访问真实资源；在测试写入之前，请检查选定的绑定。
- 不要将密钥值放入命令参数、源代码和日志中。使用文档中记录的交互式输入或受保护的文件/stdin 机制。本地密钥文件必须被版本控制忽略，并且不会自动作为部署的密钥上传。对于缺失的本地密钥，请检查文件优先级和密钥文档中任何 `secrets.required` 声明。
- 将 `wrangler secret put` 和 `secret delete` 视为部署：它们创建一个版本并立即部署它。当更改必须分阶段进行时，请使用文档中记录的 `wrangler versions secret` 工作流程。
- 在回滚之前，请检查 [回滚限制](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/)：连接的资源及其数据不会与 Worker 代码一起回滚。

## 验证

在 TypeScript 项目中更改配置或绑定后，请使用项目的 `wrangler types` 命令重新生成类型，而不是手动编辑生成的声明。运行相关的现有类型检查或测试。

对于部署更改，请使用项目的构建工作流，并在支持的情况下使用 `wrangler deploy --dry-run`，并使用预期的配置和环境。成功的干运行检查构建和打包；它不会证明远程资源或运行时行为是否正常。根据请求的工作适当使用特定任务的本地或远程检查。

报告更改内容、目标环境、执行检查以及任何未解决的验证差距。当结果取决于当前命令或配置行为时，请链接使用的文档。
