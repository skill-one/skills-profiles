# Wrangler CLI

在编写命令或配置之前，请使用项目的 Wrangler 版本，并获取相关文档。CLI 参数和配置字段会发生变化，请勿依赖记忆中的示例。

## 检查项目

- 查找包管理器、已安装的 Wrangler 版本、包脚本、框架和 Wrangler 配置。通过项目的脚本或包管理器执行命令，以便使用其本地版本。需要时使用现有的 lockfile 安装依赖；不要静默将 Wrangler 升级以匹配当前文档。如果 Wrangler 不是依赖项，请参考 [安装指南](https://developers.cloudflare.com/workers/wrangler/install-and-update/) 将其本地添加。
- 识别构建或部署命令使用的配置，包括框架生成的配置。编辑其源代码，而非生成的输出。
- 在运行更改环境、Worker 和资源等命令之前，先确立目标账户、Worker、环境和资源。对于数据操作，确定目标是本地还是远程。

## 获取任务所需的内容

如果可用，使用 Cloudflare MCP 的 `docs` 工具，或直接获取相关链接页面。链接至涉及的具体命令或产品；避免加载完整的参考文档。如果页面发生变动，通过 [Wrangler 命令索引](https://developers.cloudflare.com/workers/wrangler/commands/) 或 Cloudflare 文档搜索重新查找。

| 任务 | 来源 |
| --- | --- |
| 发现命令和参数，包括资源管理、部署、回滚和诊断 | 项目本地 `wrangler --help` 和 `wrangler <command> --help`；[命令参考](https://developers.cloudflare.com/workers/wrangler/commands/) |
| 编辑配置或添加绑定 | 已安装的 `wrangler/config-schema.json`（通常位于 `node_modules` 下）；[配置参考](https://developers.cloudflare.com/workers/wrangler/configuration/) |
| 部署框架应用程序 | [框架指南](https://developers.cloudflare.com/workers/framework-guides/)；按照项目现有框架和适配器的指南操作 |
| 在请求时迁移应用程序至 Workers | [Pages 到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/migrate-from-pages/)；[Vercel 到 Workers](https://developers.cloudflare.com/workers/static-assets/migration-guides/vercel-to-workers/) |
| 配置暂存或生产环境 | [环境](https://developers.cloudflare.com/workers/wrangler/environments/) |
| 在本地、CI 或部署的 Worker 中设置密钥 | [密钥](https://developers.cloudflare.com/workers/configuration/secrets/) |
| 生成绑定和运行时类型 | [TypeScript](https://developers.cloudflare.com/workers/languages/typescript/) |
| 本地运行或选择测试方式 | [本地开发](https://developers.cloudflare.com/workers/local-development/)；[测试](https://developers.cloudflare.com/workers/testing/) |
| 诊断认证或选择账户 | [通用命令](https://developers.cloudflare.com/workers/wrangler/commands/general/)，包括 `whoami`；[认证配置](https://developers.cloudflare.com/workers/wrangler/profiles/) |
| 部署未认证原型 | 使用 [Claim deployments](https://developers.cloudflare.com/workers/platform/claim-deployments/) 确认资格、过期时间及 Claim URL 的处理；生产环境或 CI 使用永久账户 |

使用已安装的帮助信息和模式检查项目中是否存在文档中描述的可用功能。如果所需功能需要升级，请将该依赖显式声明。若无法获取检索信息，请说明差距，并使用可用的本地证据，而非臆造语法。

## 应用变更

- 为新的配置优先使用 `wrangler.jsonc`。为新项目设置 [兼容性日期](https://developers.cloudflare.com/workers/configuration/compatibility-dates/) 为当日；在推进已有项目的日期时，审查运行时变化并进行测试。保留现有项目约定，避免非必要的格式迁移。
- 添加绑定或变量之前，检查环境继承情况。部分字段必须为每个环境单独指定；可用的默认配置并不表示已配置暂存环境。
- 在使用 Cloudflare Vite 插件时，通过在开发或构建时选择 `CLOUDFLARE_ENV` 来指定环境。部署生成的构建产物；在部署时设置环境并不会重新指向其扁平化配置。参见 [Vite 环境](https://developers.cloudflare.com/workers/vite-plugin/reference/cloudflare-environments/)。
- 部署前将仪表盘变更与配置进行核对：Wrangler 可能会覆盖仪表盘变量和路由。绑定现有资源时，验证其标识符；省略的标识符可能触发 [自动创建](https://developers.cloudflare.com/workers/wrangler/configuration/#automatic-provisioning)。
- 在开发期间区分本地模拟与远程绑定。本地运行的 Worker 仍可访问真实资源；在测试写入操作前，检查所选绑定。
- 将密钥值排除在命令参数、源代码和日志之外。使用文档中说明的交互输入或受保护的文件/stdin 机制来执行命令。本地密钥文件必须被版本控制忽略，且不会自动作为部署密钥上传。对于缺失的本地密钥，检查文件优先级以及密钥文档中任何 `secrets.required` 声明。
- 将 `wrangler secret put` 和 `secret delete` 视为部署操作：它们会创建版本并立即进行部署。当变更需要暂存时，使用文档中说明的 `wrangler versions secret` 工作流。
- 回滚之前，检查 [回滚限制](https://developers.cloudflare.com/workers/versions-and-deployments/rollbacks/)：已连接资源及其数据不会随 Worker 代码一起回滚。

## 验证

在 TypeScript 项目中更改配置或绑定时，请使用项目中的 `wrangler types` 命令重新生成类型，而非手动编辑生成的声明。运行相关的现有类型检查或测试。

对于部署变更，使用项目的构建工作流和受支持时的 `wrangler deploy --dry-run`，并指定预期的配置和环境。成功的试运行（dry run）会检查构建和打包；它并不能证明远程资源或运行时行为可用。根据所要求的工作，适当使用任务特定的本地或远程检查。

报告变更内容、目标环境、已执行的检查以及任何未解决的验证差距。在结果依赖于当前命令或配置行为时，链接所使用文档。
