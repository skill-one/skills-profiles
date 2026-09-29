---
name: here-now
description: 这里。现在让代理在几秒钟内将网站和文件发布到实时URL。将HTML、文档、图像、PDF、视频和静态文件发布到{slug}。here.now或自定义域名。当被要求“发布这个”、“托管这个”、“部署这个”、“在网络上分享这个”、“制作一个网站”、“将这个上线”、“创建一个网页”、“生成一个URL”、“构建一个聊天机器人”、“为这个网站设置密码保护”、“将这个网站设为私密”或“只与特定人群分享这个网站”时，请使用here.now。here.now还包括工作区——共享的团队账户，其中网站属于团队，并在{label}。{workspace}。here.now上提供服务——当被要求“将这个发布到我们的团队工作区”、“与我的团队分享这个”或“将这个放入我们的公司工作区”时，请使用。代理还可以通过here.now为网站购买域名（无加价，DNS和SSL自动）——当被要求“购买域名”、“给我注册一个.com”或“注册一个域名”时，请使用。
---

# here.now

**技能版本：1.32.0**

here.now 允许代理在几秒钟内将网站和文件发布到实时 URL。

核心原语是一个 **站点**：发布一个文件或文件夹，即可在 `{slug}.here.now` 或自定义域名下获得一个实时 URL。每个站点都有访问控制：公开链接（默认）、密码或仅限受邀者访问。

here.now 还包括 **工作区** — 共享的团队账户，站点属于团队，并在 `{label}.{workspace}.here.now` 下提供服务（见下文“发布到工作区”）。

在付费计划上的个人账户可以开启 **个性化 URL**：用户名在 `{name}.here.now`，之后他们发布的每个站点（包括通过你发布的）也会在可读的 `{site-name}.{name}.here.now` 地址下服务，该地址根据其标题命名。当用户希望将所有站点都用自己的名字发布时，使用 `PUT /api/v1/vanity-urls/subdomain` 并带上 `{"subdomain": "name"}` 来开启；对于在所选主机名下的一个站点，使用自定义域名；对于团队拥有的站点，使用工作区。最终响应包含 `primaryUrl` 和 `urls[]`（最佳优先）；当 `primaryUrl` 与 `siteUrl` 不同时，请提及 `primaryUrl`。参见 https://here.now/docs#vanity-urls。

要安装或更新（推荐）：`npx skills add heredotnow/skill --skill here-now -g`

对于仓库固定/项目本地安装，运行相同的命令，不带 `-g`。

## 当前文档

**在回答有关 here.now 功能、特性或工作流的问题之前，请阅读当前文档：**

→ **https://here.now/docs**

在以下情况下阅读文档：

- 在对话中第一次与 here.now 相关的交互时
- 任何时间用户询问如何做某事
- 任何时间用户询问可能、支持或推荐的内容
- 在告诉用户某个功能不受支持之前

需要当前文档的主题（不要仅依赖本地技能文本）：

- 站点访问控制（密码和限制访问）
- 工作区（团队账户、成员资格、标签 URL）
- 文件夹（组织用户的仪表板；见 https://here.now/docs#folders）
- 驱动器和驱动器共享
- 自定义域名
- 个性化 URL (`{site-name}.{name}.here.now`；见 https://here.now/docs#vanity-urls)
- 购买域名（先搜索和报价；说明价格和续费价格，并在调用购买前获得用户的明确同意 — 购买是最终的；见 https://here.now/docs#buy-domain）
- 站点数据
- 公共资料
- 代理路由和服务变量
- 限制和配额
- SPA 路由
- 所有者站点搜索
- 站点分析
- 站点版本历史记录、预览和回滚
- 错误处理和纠正
- 功能可用性

**如果文档和实时 API 行为不一致，请相信实时 API 行为。**

从 https://here.now/docs（curl、WebFetch 等）获取命令行时，会收到一个 markdown 摘要，而不是完整的 HTML 文档：它列出了每个稳定的公共端点及其简短描述，但此技能中的部分锚点（如 `/docs#access-control`）仅在 HTML 版本中解析，工作示例也存放在那里。要获取完整的请求/响应模式和参数，请获取 **https://here.now/openapi.json**。不要仅从 markdown 摘要就得出某个操作不受支持的结论 — 首先检查 OpenAPI 规范。

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于活动操作，请优先考虑实时 API 行为。

## 要求

- 必要的二进制文件：`curl`、`file`、`jq`
- 必要的网络访问：`https://here.now`（API）和 `https://*.r2.cloudflarestorage.com`（直接将文件上传到存储；确切的主机名在每个上传 URL 中）。在沙盒或代理后面，允许这两个主机。如果仅允许 `here.now`，则创建调用成功，每个上传失败，并且 finalize 报告缺少文件。
- 可选环境变量：`$HERENOW_API_KEY`
- 可选 Drive 令牌变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭据文件：`~/.herenow/credentials`
- 预装的帮助程序：
  - `./scripts/publish.sh` 用于发布站点
  - `./scripts/drive.sh` 用于私有 Drive 存储

## 如果帮助脚本未安装

某些环境在未提供 `scripts/` 目录的情况下接收此文档（例如，仅提供 `$HERENOW_API_KEY` 的托管平台集成）。在这种情况下，请先安装完整捆绑包：

```bash
npx skills add heredotnow/skill --skill here-now -g
```

或者直接调用 API — 本文档中的每个脚本工作流都是公共 API 的包装。发布是一个三步流程：`POST /api/v1/publish` 带有 `files` 数组（`[{path, size}]`）返回预签名的上传目标，将每个文件的字节 `PUT` 到其返回的 URL，然后 `POST` 返回的 `finalizeUrl`。站点在 finalize 成功后才会上线。完整的工作流程，包括请求/响应示例：https://here.now/docs#create（然后是 #upload 和 #finalize），机器可读模式：https://here.now/openapi.json。

## 创建站点

```bash
./scripts/publish.sh {file-or-dir}
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

在底层，这是一个创建/更新 -> 上传文件 -> finalize 的三步流程。站点在 finalize 成功后才会上线。

没有 API 密钥，这将创建一个 **匿名站点**，24 小时后过期。
使用保存的 API 密钥，站点是永久的。

**文件结构**：对于 HTML 站点，将 `index.html` 放在要发布的目录的根目录中，而不是放在子目录中。目录的内容成为站点根目录。例如，将 `my-site/` 发布到 `my-site/index.html` 存在的地方 — 不要发布包含 `my-site/` 的父文件夹。

您还可以发布原始文件，无需任何 HTML。单个文件会获得丰富的自动查看器（图像、PDF、视频、音频）。多个文件会获得自动生成的目录列表，包含文件夹导航和图像库。

## 更新现有站点

```bash
./scripts/publish.sh {file-or-dir} --slug {slug}
```

脚本在更新匿名站点时自动加载 `claimToken` 从 `.herenow/state.json`。要覆盖，请传递 `--claim-token {token}`。

认证更新需要保存的 API 密钥。

**陈旧基线保护**。实时站点可能自本地文件发布以来已更改 — 所有者可以使用其他工具（另一个代理、here.now 编辑器、队友）编辑它。脚本在每次发布后记录实时 `versionId` 在 `.herenow/state.json` 中，并在下次从同一目录更新同一 `slug` 时将其作为 `baseVersionId` 发送；如果实时站点已经超过它，则更新会被拒绝，并带有 `code: "version_conflict"`，指明实时版本及其来源。当发生这种情况时，将消息转发给用户，并提供以下选项：(a) 使用 `GET /api/v1/publish/{slug}/files`（每个都带有 `url` 列出它们）和 `GET /api/v1/publish/{slug}/files/{path}`（字节；需要所有者 API 密钥，适用于密码保护和限制站点，无需访客密码），读取实时文件，并将它们协调到本地文件，然后重新发布，或 (b) 使用 `--overwrite` 重新运行以强制替换实时版本。在编辑您最近未触摸的认证站点的本地文件之前，请先检查是否存在差异：`GET /api/v1/publish/{slug}` 返回 `currentVersionId` 加上 `currentVersionSource` 和 `currentVersionCreatedAt`（更改它的时间和方式，例如 `editor`）— 如果 id 与状态文件中的 `versionId` 不同，则在编辑之前读取实时文件。已发布的版本是共享的真相；永远不要获取公共 URL 来读取您拥有的站点（它受到保护），并且永远不要要求用户提供访客密码来读取他们自己的站点。匿名站点无法调用这些端点；它们依赖于保存的状态和服务器强制执行。省略 `baseVersionId`（或使用 `--overwrite`）是未经检查的完整替换 — 对于原始 API 调用者，今天的默认值是 `unchanged: true`。

每次发布都会记录一个不可变版本。如果用户要求查看站点的早期版本、撤销发布或回滚：使用 `GET /api/v1/publish/{slug}/versions` 列出历史记录，并使用 `POST /api/v1/publish/{slug}/versions/{versionId}/restore` 立即恢复（恢复会保留当前的访问模式、密码和域名）。版本访问包含在所有计划中，个人和工作区 alike。字节完全相同的重新发布会从 finalize 返回 `unchanged: true` 而不是创建一个新版本。参见 https://here.now/docs#versions。

已登录的用户还有公共资料。代理可以帮助用户在他们的资料上显示或隐藏站点并管理资料设置，通过 API 文档 https://here.now/docs#profile。

## 发布到工作区

工作区是共享的团队账户：发布的站点属于团队，而不是发布成员，并在 `{label}.{workspace}.here.now` 下获得一个易于记忆的 URL。

```bash
./scripts/publish.sh {file-or-dir} --workspace {subdomain}
```

需要保存的 API 密钥和工作区成员资格。使用 `GET /api/v1/accounts` 列出用户的工 作区（以及有效的子域名）。工作区站点默认为成员仅限访问；脚本报告团队 URL 作为 `publish_result.account_url`。

对于其他所有内容 — 创建工作区、邀请和自动加入、工作区域名和变量、标签重命名 — 请阅读当前文档：

→ **https://here.now/docs#workspaces**

## 站点访问控制

站点一次使用一种访问模式：

- **anyone_with_link**（默认）：任何拥有 URL 的人都可以查看。
- **password**：访客必须输入共享密码。
- **restricted**：仅限邀请；只有所有者允许的经过验证的电子邮件地址或电子邮件域名可以查看。

工作区拥有的站点默认为 **account_members**（访客必须登录并是工作区成员），并支持公开、带密码的公开和 **restricted**。在工作区站点上，`restricted` 意味着工作区成员加上每个站点的访客允许列表：成员始终有访问权限，并且允许列表中的电子邮件/域名是外部访客，他们只能查看该站点 — 他们永远不会成为工作区成员，尽管该站点会出现在访客自己的仪表板中作为共享站点。工作区限制至少需要一个访客电子邮件或域名 — 空允许列表会被拒绝，返回 400（使用 `account_members` 仅限成员）。参见 https://here.now/docs#workspace-access。

使用 `GET`/`PATCH /api/v1/publish/{slug}/access` 管理访问（密码通过元数据端点）。限制访问需要已声明的站点。PATCH 会替换完整的允许列表 — 读取、合并，然后写入。在处理访问控制之前，请阅读当前文档：

→ **https://here.now/docs#access-control**

## 文件夹（组织用户的仪表板）

已登录的用户可以在 here.now 仪表板中将他们的站点分组到 **文件夹** 中。文件夹是关于账户的事实，而不是站点的地址：扁平（无嵌套）、每个站点一个文件夹、由工作区的每个成员共享、对访客不可见。将站点归档不会改变其 URL 或访问权限。

当用户为站点命名文件夹、项目或客户（“将此发布到我的报告文件夹”、“归档到 Acme”）时，作为发布的一部分进行归档：

```bash
./scripts/publish.sh {file-or-dir} --folder "Reports"
```

`--folder` 接受文件夹名称或 id。名称不区分大小写匹配，并且如果不存在则 **创建**，因此第一次使用时此操作有效；脚本将结果报告为 `publish_result.folder`。它需要 API 密钥（匿名站点没有账户可以归档），并可以与 `--slug`（移动现有站点）和 `--workspace`（工作区的文件夹）一起使用。

没有脚本，相同的字段在 `POST /api/v1/publish`、`PUT /api/v1/publish/{slug}` 和 `PATCH /api/v1/publish/{slug}/metadata` 上是 `folder`（无需发布新版本即可归档站点；“folder": null 将其移回根目录）。`GET /api/v1/folders` 列出账户的文件夹；`GET /api/v1/publishes?folder={name-or-id}` 列出文件夹的站点。重命名和删除是 `PATCH`/`DELETE /api/v1/folders/{id}`（删除文件夹会取消归档其站点并删除其他任何东西）。每个账户最多 50 个文件夹，名称最多 60 个字符。

**永远不要凭空创建文件夹或归档用户未要求归档的站点。** 文件夹结构是他们的；每个文件夹都会作为瓷砖出现在他们的仪表板中。参见 https://here.now/docs#folders。

## 使用 Drive

当用户希望为代理文件（文档、上下文、记忆、计划、资源、媒体、研究、代码和任何其他应持久保存而不作为网站发布的内容）提供私有云存储时，请使用 Drive。

每个已登录的账户都有一个默认的 Drive，名为 `My Drive`。

```bash
./scripts/drive.sh default
./scripts/drive.sh ls My Drive
./scripts/drive.sh put My Drive notes/today.md --from ./notes/today.md
./scripts/drive.sh cat My Drive notes/today.md
./scripts/drive.sh share My Drive --perms write --prefix notes/ --ttl 7d
```

使用范围的 Drive 令牌进行代理之间的传递。如果您收到一个 `herenow_drive` 分享块，请使用其 `token` 作为 `Authorization: Bearer <token>` 对 `api_base`，如果存在则尊重 `pathPrefix`，并在写入时保留 ETags。`pathPrefix` 为 `null` 意味着完整 Drive 访问。如果技能可用，请优先使用 `./scripts/drive.sh`；否则，直接调用列出的 API 操作。

## 客户归因

将 `--client` 与您正在运行的 **代理产品或框架的名称** — `cursor`、`claude-code`、`codex`、`grok-bot`、`openclaw`、`gemini` 等：

```bash
./scripts/publish.sh {file-or-dir} --client claude-code
```

这将发布 API 调用上发送 `X-HereNow-Client: claude-code/publish-sh`。如果省略，脚本会发送一个备用值。

使用平台名称，**而不是**在其中的名称。如果您是一个名为“research-bot”的机器人，在 Grok Bot 中运行，正确的值是 `grok-bot` — 不是 `research-bot`。机器人名称、角色、子代理、项目和线程名称不能识别平台。要记录您的实例名称，请在斜杠后附加它：

```bash
./scripts/publish.sh {file-or-dir} --client grok-bot/research-bot
```

只有独立运行的代理（不使用任何框架）应使用自己的产品名称。

## API 密钥存储

发布脚本从这些来源读取 API 密钥（第一个匹配的胜出）：

1. `--api-key {key}` 标志（CI/脚本仅用 — 避免在交互式使用中）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐用于代理）

要存储密钥，将其写入凭据文件：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要**：收到 API 密钥后，请立即保存 — 自己运行上述命令。不要要求用户手动运行它。避免在交互式会话中通过 CLI 标志（例如 `--api-key`）传递密钥；凭据文件是首选的存储方法。

永远不要将凭据或本地状态文件（`~/.herenow/credentials`、`.herenow/state.json`）提交到源代码管理。

## 获取 API 密钥

要从匿名（24 小时）升级到永久站点：

1. 询问用户他们的电子邮件地址。
2. 请求一次性登录代码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“检查您的收件箱，查找来自 here.now 的登录代码，并将其粘贴在这里。”
4. 验证代码并获取 API 密钥：

```bash
curl -sS https://here.now/api/auth/agent/verify-code \
  -H "content-type: application/json" \
  -d '{"email":"user@example.com","code":"ABCD-2345"}'
```

5. 自己保存返回的 `apiKey`（不要要求用户这样做）：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

## 状态文件

在每次站点创建/更新后，脚本会写入工作目录中的 `.herenow/state.json`：

```json
{
  "publishes": {
    "bright-canvas-a7k2": {
      "siteUrl": "https://bright-canvas-a7k2.here.now/",
      "claimToken": "4fQ9tK2mXb7cW1pZ",
      "claimUrl": "https://here.now/c/4fQ9tK2mXb7cW1pZ",
      "expiresAt": "2026-02-18T01:00:00.000Z"
    }
  }
}
```

在创建或更新站点之前，您可以查看此文件以查找先前的 slugs。
将 `.herenow/state.json` 视为内部缓存仅。
永远不要将此本地文件路径呈现为 URL，也永远不要将其用作认证模式、过期时间或声明 URL 的真实来源。

## 应向用户说明的内容

对于已发布的站点：

- 始终共享当前脚本运行时的 `siteUrl`。
- 将站点 URL 单独放在一行上，该行上不能有其他任何内容——没有标点符号、连字符或状态文本（聊天客户端会自动链接到空白字符之前的内容，将您的文字粘合到 URL 中）。状态详细信息（如“永久，已保存到您的账户”）放在下一行。
- 读取并遵循脚本标准错误输出中的 `publish_result.*` 行，以确定认证模式。
- 当 `publish_result.account_url` 非空（工作区发布）时，请将其作为主要团队 URL 与 `siteUrl` 一起共享。
- 当 `publish_result.primary_url` 非空时，请首先共享它；`siteUrl` 仍然有效。
- 当 `publish_result.folder` 非空时，请告知用户该站点已存放在其仪表板中的该文件夹中。
- 当 `publish_result.auth_mode=authenticated`：告诉用户该站点是**永久**的，并已保存到他们的账户。不需要声明 URL。
- 当 `publish_result.auth_mode=anonymous`：告诉用户该站点**将在 24 小时后过期**。共享声明 URL（如果 `publish_result.claim_url` 非空且以 `https://` 开头），以便他们可以永久保留它。按字节逐字节地复制它作为可点击的链接——永远不要缩短、编辑、总结或用 `...` 替换其任何部分；修改后的声明链接将无法工作。警告称声明令牌只返回一次且无法恢复。
- 永远不要告诉用户检查 `.herenow/state.json` 以获取声明 URL 或认证状态。

对于 Drives：

- 不要将 Drive 文件描述为公共 URL。
- 告知用户 Drive 内容是私有的，除非使用具有作用域令牌共享。
- 当与其他代理共享访问权限时，请优先使用具有狭窄 `pathPrefix` 和短 TTL 的作用域令牌。

## publish.sh 选项

| 标志                   | 描述                                  |
| ---------------------- | -------------------------------------------- |
| `--slug {slug}`        | 更新现有站点而不是创建                 |
| `--workspace {subdomain}` | 发布到您所属的工作区（团队账户）         |
| `--claim-token {token}`| 覆盖匿名更新的声明令牌                |
| `--overwrite`          | 跳过陈旧基础检查并替换实时版本         |
| `--title {text}`       | 查看器标题（非 HTML 站点）             |
| `--description {text}` | 查看器描述                            |
| `--folder {name-or-id}` | 将站点存放在仪表板文件夹中（如果缺少则创建名称；仅认证） |
| `--ttl {seconds}`      | 设置过期时间（仅认证）               |
| `--client {name}`      | 归因代理套件——您运行的平台（例如 `cursor`、`grok-bot`），而不是您的机器人/角色名称；可选地附加它：`grok-bot/research-bot` |
| `--base-url {url}`     | API 基础 URL（默认：`https://here.now`） |
| `--allow-nonherenow-base-url` | 允许向非默认 `--base-url` 发送认证 |
| `--api-key {key}`      | API 密钥覆盖（优先使用凭证文件）    |
| `--spa`                | 启用 SPA 路由（为未知路径提供 index.html） |

## 超越 publish.sh

对于 Drive 操作，请使用 `./scripts/drive.sh` 或 Drive API。对于更广泛的账户和站点管理——站点数据、搜索、分析、配置文件、删除、元数据、访问控制、域、变量、代理路由、复制等——请参阅当前文档：

→ **https://here.now/docs**

完整文档：https://here.now/docs
