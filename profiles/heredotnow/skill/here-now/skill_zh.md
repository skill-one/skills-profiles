# here.now

**技能版本：1.31.0**

here.now 允许代理在几秒钟内将网站和文件发布到实时 URL。

核心原语是一个 **站点**：发布一个文件或文件夹，即可在 `{slug}.here.now` 或自定义域名下获得一个实时 URL。每个站点都有访问控制：公开链接（默认）、密码或仅限受邀者访问。

here.now 还包括 **工作区** — 共享的团队账户，站点属于团队，并在 `{label}.{workspace}.here.now` 下提供服务（见下文“发布到工作区”）。

付费计划上的个人账户可以开启 **个性化 URL**：用户名在 `{name}.here.now`，之后发布的每个站点（包括通过您发布的）也将在可读的 `{site-name}.{name}.here.now` 地址下服务，该地址根据其标题命名。当用户希望将所有站点都用自己的名字发布时，使用 `PUT /api/v1/vanity-urls/subdomain` 并带上 `{"subdomain": "name"}` 来开启；对于在您选择的单个主机名下的一个站点，使用自定义域名；对于团队拥有的站点，使用工作区。最终响应包含 `primaryUrl` 和 `urls[]`（最佳优先）；当它与 `siteUrl` 不同时，请提及 `primaryUrl`。请参阅 https://here.now/docs#vanity-urls。

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
- 驱动器和驱动器共享
- 自定义域名
- 个性化 URL (`{site-name}.{name}.here.now`；见 https://here.now/docs#vanity-urls)
- 购买域名（先搜索和报价；说明价格和续费价格，并在调用购买前获得用户的明确同意——购买是最终的；见 https://here.now/docs#buy-domain）
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

**如果文档和实时 API 行为不一致，请信任实时 API 行为。**

从 https://here.now/docs（curl、WebFetch 等）获取命令行获取（fetch）会收到一个 markdown 摘要，而不是完整的 HTML 文档：它列出了每个稳定公共端点及其简短描述，但此技能中的部分锚点（如 `/docs#access-control`）仅在 HTML 版本中解析，工作示例也存放在那里。对于完整的请求/响应模式和参数，获取 **https://here.now/openapi.json**。不要仅从 markdown 摘要中得出操作不受支持的结论——首先检查 OpenAPI 规范。

如果文档获取失败或超时，请继续使用本地技能和实时 API/脚本输出。对于活动操作，请优先考虑实时 API 行为。

## 要求

- 必要的二进制文件：`curl`、`file`、`jq`
- 必要的网络访问：`https://here.now`（API）和 `https://*.r2.cloudflarestorage.com`（直接将文件上传到存储；确切的主机名在每个上传 URL 中）。在沙盒或代理后面有出站允许列表的情况下，允许这两个主机。如果仅允许 `here.now`，创建调用成功，每个上传失败，最终响应报告缺少文件。
- 可选环境变量：`$HERENOW_API_KEY`
- 可选驱动器令牌变量：`$HERENOW_DRIVE_TOKEN`
- 可选凭证文件：`~/.herenow/credentials`
- 预装的帮助程序：
  - `./scripts/publish.sh` 用于发布站点
  - `./scripts/drive.sh` 用于私人驱动器存储

## 如果帮助脚本未安装

某些环境在未提供 `scripts/` 目录的情况下接收此文档（例如，仅提供 `$HERENOW_API_KEY` 的托管平台集成）。在这种情况下，请先安装完整捆绑包：

```bash
npx skills add heredotnow/skill --skill here-now -g
```

或者直接调用 API——此文档中的每个脚本工作流都是公共 API 的包装。发布是一个三步流程：`POST /api/v1/publish` 带有 `files` 数组（`[{path, size}]`）返回预签名的上传目标，将每个文件的字节PUT到其返回的 URL，然后POST返回的 `finalizeUrl`。站点在 finalize 成功后才会上线。完整的工作流程，包括请求/响应示例：https://here.now/docs#create（然后是 #upload 和 #finalize），机器可读模式：https://here.now/openapi.json。

## 创建站点

```bash
./scripts/publish.sh {file-or-dir}
```

输出实时 URL（例如 `https://bright-canvas-a7k2.here.now/`）。

在底层，这是一个创建/更新 -> 上传文件 -> finalize 的三步流程。站点在 finalize 成功后才会上线。

没有 API 密钥，这将创建一个 **匿名站点**，24 小时后过期。
使用保存的 API 密钥，站点是永久的。

**文件结构**：对于 HTML 站点，将 `index.html` 放在要发布的目录的根目录下，而不是放在子目录中。目录的内容成为站点根目录。例如，在存在 `my-site/index.html` 的 `my-site/` 下发布——不要发布包含 `my-site/` 的父文件夹。

您还可以发布原始文件，无需任何 HTML。单个文件获得丰富的自动查看器（图像、PDF、视频、音频）。多个文件获得自动生成的目录列表，具有文件夹导航和图像库。

## 更新现有站点

```bash
./scripts/publish.sh {file-or-dir} --slug {slug}
```

脚本在更新匿名站点时自动加载 `claimToken` 从 `.herenow/state.json`。要覆盖，请传递 `--claim-token {token}`。

认证更新需要保存的 API 密钥。

**陈旧基保护**。实时站点可能自本地文件发布以来已更改——所有者可以使用其他工具（另一个代理、here.now 编辑器、队友）编辑它。脚本在每次发布后记录实时的 `versionId` 到 `.herenow/state.json`，并在下次从同一目录更新同一 slug 时将其作为 `baseVersionId` 发送；如果实时站点已经超过它，更新将被拒绝，并报告实时版本及其创建方式，代码为 `version_conflict`。当发生这种情况时，请将消息转发给用户，并提供以下选项：(a) 使用 `GET /api/v1/publish/{slug}/files`（每个都带有 `url` 列出它们）和 `GET /api/v1/publish/{slug}/files/{path}`（字节；需要所有者 API 密钥，适用于密码保护和限制站点，无需访客密码）读取实时文件，将它们协调到本地文件，然后重新发布，或 (b) 使用 `--overwrite` 无论如何替换实时版本。在编辑您最近未触及的认证站点的本地文件之前，请先检查是否存在差异：`GET /api/v1/publish/{slug}` 返回 `currentVersionId` 加上 `currentVersionSource` 和 `currentVersionCreatedAt`（更改它的时间和方式，例如 `editor`）——如果 id 与您的状态文件的 `versionId` 不同，请在编辑前读取实时文件。已发布的版本是共享的真相；永远不要获取所有者站点的公共 URL 来读取（它受到保护），永远不要要求用户提供访客密码来读取他们自己的站点。匿名站点无法调用这些端点；它们依赖于保存的状态和服务器强制执行。省略 `baseVersionId`（或使用 `--overwrite`）是无检查的完整替换——原始 API 调用者的默认设置是今天。

每次发布都会记录一个不可变版本。如果用户要求查看站点的早期版本、撤销发布或回滚：使用 `GET /api/v1/publish/{slug}/versions` 列出历史记录，并使用 `POST /api/v1/publish/{slug}/versions/{versionId}/restore` 立即恢复（恢复会保留当前的访问模式、密码和域名）。版本访问包含在所有计划中，无论是个人还是工作区。字节相同重新发布将从 finalize 返回 `unchanged: true` 而不是创建一个新版本。请参阅 https://here.now/docs#versions。

已登录的用户还有公开资料。代理可以通过 API 文档（https://here.now/docs#profile）帮助用户在资料上显示或隐藏站点并管理资料设置。

## 发布到工作区

工作区是共享的团队账户：发布到其中的站点属于团队，而不是发布成员，并在 `{label}.{workspace}.here.now` 下获得一个易于记忆的 URL。

```bash
./scripts/publish.sh {file-or-dir} --workspace {subdomain}
```

需要保存的 API 密钥和工作区成员资格。使用 `GET /api/v1/accounts` 列出用户的工 作区（以及有效的子域名）。工作区站点默认为成员仅限访问；脚本报告团队 URL 作为 `publish_result.account_url`。

对于其他所有内容——创建工作区、邀请和自动加入、工作区域名和变量、标签重命名——请阅读当前文档：

→ **https://here.now/docs#workspaces**

## 站点访问控制

站点一次使用一种访问模式：

- **anyone_with_link**（默认）：拥有 URL 的任何人都可以查看。
- **password**：访客必须输入共享密码。
- **restricted**：仅限邀请；只有所有者允许的经过验证的电子邮件地址或电子邮件域名可以查看。

工作区拥有的站点默认为 **account_members**（访客登录并必须是工作区成员），并支持公开、带密码的公开和 **restricted**。在工作区站点上，`restricted` 意味着工作区成员加上每个站点的访客允许列表：成员始终有访问权限，允许列表中的电子邮件/域名是外部访客，他们只能查看该站点——他们永远不会成为工作区成员，尽管该站点会出现在访客自己的仪表板中作为共享站点。工作区限制至少需要一个访客电子邮件或域名——空允许列表会被拒绝，返回 400（使用 `account_members` 仅限成员）。请参阅 https://here.now/docs#workspace-access。

使用 `GET`/`PATCH /api/v1/publish/{slug}/access` 管理访问（密码通过元数据端点）。限制访问需要一个已声明的站点。PATCH 会替换完整的允许列表——读取、合并，然后写入。在处理访问控制之前，请阅读当前文档：

→ **https://here.now/docs#access-control**

## 使用 Drive

当用户希望为代理文件（文档、上下文、记忆、计划、资源、媒体、研究、代码和任何其他应该持久化而不作为网站发布的内容）使用私人云存储时，请使用 Drive。

每个已登录的账户都有一个默认 Drive，名为 `My Drive`。

```bash
./scripts/drive.sh default
./scripts/drive.sh ls My Drive
./scripts/drive.sh put My Drive notes/today.md --from ./notes/today.md
./scripts/drive.sh cat My Drive notes/today.md
./scripts/drive.sh share My Drive --perms write --prefix notes/ --ttl 7d
```

使用作用域 Drive 令牌进行代理之间的传递。如果您收到一个 `herenow_drive` 共享块，请使用其 `token` 作为 `Authorization: Bearer <token>` 对 `api_base`，如果存在，请尊重 `pathPrefix`，并在写入时保留 ETags。`pathPrefix` 为 `null` 意味着完整驱动器访问。如果技能可用，请优先使用 `./scripts/drive.sh`；否则，直接调用列出的 API 操作。

## 客户端归因

传递 `--client` 与您正在运行的 **代理产品或框架** 的名称——`cursor`、`claude-code`、`codex`、`grok-bot`、`openclaw`、`gemini` 等：

```bash
./scripts/publish.sh {file-or-dir} --client claude-code
```

这将发布 API 调用上发送 `X-HereNow-Client: claude-code/publish-sh`。如果省略，脚本将发送一个备用值。

使用平台的名称，**不是**在内部获得的名称。如果您是一个名为 "research-bot" 在 Grok Bot 内运行的机器人，正确的值是 `grok-bot`——不是 `research-bot`。机器人名称、角色、子代理、项目和线程名称不会识别平台。要记录您的实例名称，请在斜杠后附加它：

```bash
./scripts/publish.sh {file-or-dir} --client grok-bot/research-bot
```

只有独立运行的代理（不使用任何框架）才应使用自己的产品名称。

## API 密钥存储

发布脚本从这些来源读取 API 密钥（第一个匹配的获胜）：

1. `--api-key {key}` 标志（CI/脚本仅用——避免在交互式使用中）
2. `$HERENOW_API_KEY` 环境变量
3. `~/.herenow/credentials` 文件（推荐用于代理）

要存储密钥，请将其写入凭证文件：

```bash
mkdir -p ~/.herenow && echo "{API_KEY}" > ~/.herenow/credentials && chmod 600 ~/.herenow/credentials
```

**重要**：收到 API 密钥后，请立即保存——自己运行上述命令。不要要求用户手动运行。避免在交互式会话中通过 CLI 标志（例如 `--api-key`）传递密钥；凭证文件是首选的存储方法。

永远不要将凭证或本地状态文件（`~/.herenow/credentials`、`.herenow/state.json`）提交到源代码控制。

## 获取 API 密钥

要从匿名（24 小时）升级到永久站点：

1. 询问用户他们的电子邮件地址。
2. 请求一次性登录代码：

```bash
curl -sS https://here.now/api/auth/agent/request-code \
  -H "content-type: application/json" \
  -d '{"email": "user@example.com"}'
```

3. 告诉用户：“检查您的收件箱，从 here.now 发送的登录代码，并将其粘贴在这里。”
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

每次站点创建/更新后，脚本都会写入工作目录中的 `.herenow/state.json`：

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

在创建或更新站点之前，您可以检查此文件以找到先前的 slugs。
将 `.herenow/state.json` 视为内部缓存。
永远不要将此本地文件路径作为 URL 显示，也永远不要将其用作认证模式、过期或声明 URL 的真相来源。

## 告诉用户什么

对于已发布的站点：

- 始终共享当前脚本运行中的 `siteUrl`。
- 将站点 URL 放在单独的一行上，该行上没有任何其他内容——没有标点符号、破折号或状态文本（聊天客户端会自动链接到空白之前的一切，将您的文字粘到 URL 中）。状态详细信息（如“永久，保存到您的账户”）放在下一行。
- 读取并遵循脚本 stderr 中的 `publish_result.*` 行以确定认证模式。
- 当 `publish_result.account_url` 非空（工作区发布）时，请将其作为主要的团队 URL 与 `siteUrl` 一起分享。
- 当 `publish_result.primary_url` 非空时，请首先分享它；`siteUrl` 仍然有效。
- 当 `publish_result.auth_mode=authenticated`：告诉用户站点是 **永久的**，并保存到他们的账户。不需要声明 URL。
- 当 `publish_result.auth_mode=anonymous`：告诉用户站点 **24 小时后过期**。分享声明 URL（如果 `publish_result.claim_url` 非空且以 `https://` 开头），以便他们可以永久保存。逐字节复制它作为可点击的链接——永远不要缩短、编辑、总结或用 `...` 替换任何部分；修改后的声明链接将无法工作。警告声明令牌只返回一次，并且无法恢复。
- 永远不要告诉用户检查 `.herenow/state.json` 以获取声明 URL 或认证状态。

对于 Drive：

- 不要将 Drive 文件描述为公共 URL。
- 告诉用户 Drive 内容除非与作用域令牌共享否则是私有的。
- 当与其他代理共享访问权限时，请优先使用具有狭窄 `pathPrefix` 和短 TTL 的作用域令牌。

## publish.sh 选项

| 标志                   | 描述                                  |
| ---------------------- | -------------------------------------------- |
| `--slug {slug}`        | 更新现有站点而不是创建                 |
| `--workspace {subdomain}` | 发布到您所属的工作区（团队账户）         |
| `--claim-token {token}`| 覆盖匿名更新的声明令牌                |
| `--overwrite`          | 跳过陈旧基检查并替换实时版本             |
| `--title {text}`       | 查看器标题（非 HTML 站点）             |
| `--description {text}` | 查看器描述                            |
| `--ttl {seconds}`      | 设置过期（仅限认证）                   |
| `--client {name}`      | 代理框架用于归因——您运行的平台（例如 `cursor`、`grok-bot`），而不是您的机器人/角色名称；可选地附加它：`grok-bot/research-bot` |
| `--base-url {url}`     | API 基 URL（默认：`https://here.now`）    |
| `--allow-nonherenow-base-url` | 允许向非默认 `--base-url` 发送认证 |
| `--api-key {key}`      | API 密钥覆盖（优先使用凭证文件）    |
| `--spa`                | 启用 SPA 路由（为未知路径提供 index.html） |

## 超越 publish.sh

对于 Drive 操作，使用 `./scripts/drive.sh` 或 Drive API。对于更广泛的账户和站点管理——站点数据、搜索、分析、资料、删除、元数据、访问控制、域名、变量、代理路由、复制等——请参阅当前文档：

→ **https://here.now/docs**

完整文档：https://here.now/docs
