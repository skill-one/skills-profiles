# here.now

**技能版本：1.32.0**

here.now 允许代理在几秒钟内将网站和文件发布到实时 URL。

核心原语是一个 **站点**：发布一个文件或文件夹，并在 `{slug}.here.now` 或自定义域名下获得一个实时 URL。每个站点都有访问控制：公开链接（默认）、密码或限制邀请-only 访问。

here.now 还包括 **工作区** — 共享的团队账户，站点属于团队，并在 `{label}.{workspace}.here.now` 下提供服务（见下文“发布到工作区”）。

在付费计划上的个人账户可以开启 **个性化 URL**：用户的名字在 `{name}.here.now`，之后他们发布的每个站点（包括通过你发布的）也将在可读的 `{site-name}.{name}.here.now` 地址下服务，该地址从其标题命名。当用户希望将所有属于他们自己的站点都发布在他们的名字下时，使用 `PUT /api/v1/vanity-urls/subdomain` 并带有 `{"subdomain": "name"}` 来开启；对于在用户选择的单个主机名下的一个站点，使用自定义域名；对于属于团队的站点，使用工作区。最终响应包含 `primaryUrl` 和 `urls[]`（最佳优先）；当 `primaryUrl` 与 `siteUrl` 不同时，请提及 `primaryUrl`。参见 https://here.now/docs#vanity-urls。

要安装或更新（推荐）：`npx skills add heredotnow/skill --skill here-now -g`

对于仓库固定/项目本地安装，运行相同的命令而不带 `-g`。

## 当前文档

**在回答有关 here.now 功能、特性或工作流程的问题之前，请阅读当前文档：**

→ **https://here.now/docs**

在以下情况下阅读文档：

- 在对话中第一次与 here.now 相关的交互时
- 任何时间用户询问如何做某事
- 任何时间用户询问可能、支持或推荐的内容
- 在告诉用户某个功能不受支持之前

需要当前文档的主题（不要仅依赖本地技能文本）：

- 站点访问控制（密码和限制访问）
- 工作区（团队账户、成员资格、标签 URL）
- 文件夹（组织用户的仪表板；参见 https://here.now/docs#folders）
- 驱动器和驱动器共享
- 自定义域名
- 个性化 URL (`{site-name}.{name}.here.now`；参见 https://here.now/docs#vanity-urls)
- 购买域名（先搜索和报价；说明价格和续费价格并获取用户的明确同意后再调用购买 — 购买是最终的；参见 https://here.now/docs#buy-domain）
- 站点数据
- 公开资料
- 代理路由和服务变量
- 限制和配额
- SPA 路由
- 所有者站点搜索
- 站点分析
- 站点版本历史记录、预览和回滚
- 错误处理和纠正
- 功能可用性

**如果文档和实时 API 行为不一致，请相信实时 API 行为。**

从 https://here.now/docs（curl、WebFetch 等）获取命令行获取（curl、WebFetch 等）会收到一个 markdown 摘要，而不是完整的 HTML 文档：它列出了每个稳定的公共端点及其简短描述，但此技能中的部分锚点（如 `/docs#access-control`）仅在 HTML 版本中解析，工作示例也存在于那里。对于完整的请求/响应模式和参数，获取 **https://here.now/openapi.json**。不要仅从 markdown 摘要中得出操作不受支持的结论 — 首先检查 OpenAPI 规范。

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于活动操作，请优先考虑实时 API 行为。

## 要求

- 必要的二进制文件：`curl`、`file`、`jq`
- 必要的网络访问：`https://here.now`（API）和 `https://*.r2.cloudflarestorage.com`（直接将文件上传到存储；每个上传 URL 中的确切主机是）。在一个沙盒或通过具有出站允许列表的代理时，允许这两个主机。仅允许 `here.now` 时，创建调用成功，每个上传失败，finalize 报告丢失文件。
- 可选环境变量：`$HERENOW_API_KEY`
- 可选 Drive 令牌变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭证文件：`~/.herenow/credentials`
- 预装的帮助程序：
  - `./scripts/publish.sh` 用于发布站点
  - `./scripts/drive.sh` 用于私人 Drive 存储

## 如果帮助脚本未安装

某些环境在没有捆绑 `scripts/` 目录的情况下接收此文档（例如，仅提供 `$HERENOW_API_KEY` 的托管平台集成）。在这种情况下，请先安装完整捆绑包：

```bash
npx skills add heredotnow/skill --skill here-now -g
```

或者直接调用 API — 此文档中的每个脚本工作流都是公共 API 的包装。发布是一个三步流程：`POST /api/v1/publish` 带有 `files` 数组（`[{path, size}]`）返回预签名的上传目标，将每个文件的字节 `PUT` 到其返回的 URL，然后 `POST` 返回的 `finalizeUrl`。站点在 finalize 成功后才会上线。完整的工作流程，包括请求/响应示例：https://here.now/docs#create（然后 #upload 和 #finalize），机器可读模式：https://here.now/openapi.json。

## 创建站点

```bash
./scripts/publish.sh {file-or-dir}
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

在底层这是一个三步流程：创建/更新 -> 上传文件 -> finalize。站点在 finalize 成功后才会上线。

没有 API 密钥，这将创建一个 **匿名站点**，在 24 小时后过期。
使用保存的 API 密钥，站点是永久的。

**文件结构**：对于 HTML 站点，将 `index.html` 放在要发布的目录的根目录中，而不是放在子目录中。目录的内容成为站点根。例如，在存在 `my-site/index.html` 的 `my-site/` 下发布 — 不要发布包含 `my-site/` 的父文件夹。

您还可以发布原始文件，而无需任何 HTML。单个文件会获得丰富的自动查看器（图像、PDF、视频、音频）。多个文件会获得自动生成的目录列表，具有文件夹导航和图像库。

## 更新现有站点

```bash
./scripts/publish.sh {file-or-dir} --slug {slug}
```

脚本在更新匿名站点时自动加载 `claimToken` 从 `.herenow/state.json`。要覆盖，请传递 `--claim-token {token}`。

认证更新需要一个保存的 API 密钥。

**陈旧基保护**。自本地文件发布以来，实时站点可能已更改 — 所有者可以使用其他工具（另一个代理、here.now 编辑器、队友）编辑它。脚本在每次发布后将实时 `versionId` 记录在 `.herenow/state.json` 中，并在下次从同一目录更新同一 slug 时将其作为 `baseVersionId` 发送；如果实时站点已经超过它，则更新会被拒绝，并带有 `code: "version_conflict"` 指出实时版本及其创建方式。当这种情况发生时，将消息转发给用户，并提供以下选项：（a）使用 `GET /api/v1/publish/{slug}/files`（每个都带有 `url` 列出它们）和 `GET /api/v1/publish/{slug}/files/{path}`（字节；需要所有者 API 密钥，适用于密码保护和限制站点，无需访客密码），将它们协调到本地文件，并重新发布，或（b）使用 `--overwrite` 无论如何替换实时版本重新运行。在编辑最近未触摸的认证站点的本地文件之前，请先检查漂移：`GET /api/v1/publish/{slug}` 返回 `currentVersionId` 加上 `currentVersionSource` 和 `currentVersionCreatedAt`（更改它的时间和方式，例如 `editor`）— 如果 id 与您的状态文件的 `versionId` 不同，请在编辑之前读取实时文件。发布的版本是共享的真相；永远不要获取所有者站点的公共 URL 来读取它（它受到保护），永远不要要求用户提供访客密码来读取他们自己的站点。匿名站点无法调用这些端点；它们依赖于保存的状态和服务器强制执行。省略 `baseVersionId`（或使用 `--overwrite`）是无检查的完整替换 — 今天对原始 API 调用者的默认值。

每次发布都会记录一个不可变的版本。如果用户要求查看站点的早期版本、撤销发布或回滚：使用 `GET /api/v1/publish/{slug}/versions` 列出历史记录，并使用 `POST /api/v1/publish/{slug}/versions/{versionId}/restore` 立即恢复（恢复会保留当前的访问模式、密码和域名）。版本访问包含在所有计划中，个人和工作区 alike。字节相同重新发布会从 finalize 返回 `unchanged: true` 而不是创建一个新版本。参见 https://here.now/docs#versions。

已登录的用户还有公开资料。代理可以帮助用户在他们的资料上显示或隐藏站点并管理资料设置，通过在 https://here.now/docs#profile 中记录的 API 文档。

## 发布到工作区

工作区是共享的团队账户：发布的站点属于团队，而不是发布成员，并在 `{label}.{workspace}.here.now` 下获得一个可记忆的 URL。

```bash
./scripts/publish.sh {file-or-dir} --workspace {subdomain}
```

需要一个保存的 API 密钥和工作区成员资格。使用 `GET /api/v1/accounts` 列出用户的工
