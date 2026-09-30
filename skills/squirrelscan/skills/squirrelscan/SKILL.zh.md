---
name: squirrelscan
description: 松鼠扫描（squirrelscan）可对网站进行SEO、性能、安全、可访问性、内容和结构化数据问题的审计（260多项规则），并通过松鼠命令行界面（CLI）对网站健康状况进行评分。当用户需要检查、审计或提升网站的SEO、排名、速度或健康状况时，以及需要进行松鼠扫描本身、安装或更新CLI、登录和API密钥、运行审计、发布和共享报告、云信用额度、MCP服务器设置、配置或故障排除时，均可使用。此外，它还涵盖实体映射：即网站在JSON-LD中声明的全局实体图谱，以及修复结构化数据身份问题，例如组织信息在每个页面中单独声明的情况。
---

# squirrelscan CLI

squirrelscan 是一款为 AI 代理构建的网站审计工具。它回答“这个网站有什么问题以及如何修复它”：它像搜索引擎一样抓取网站，分析每个页面，针对 21 个类别中的 260 多条规则（包括 SEO、性能、安全、可访问性、内容、结构化数据、代理体验等），并返回健康评分以及具体的、可修复的问题。当用户想要检查他们的网站、提高排名、加快速度或使其更健康时，在部署前/后或 CI 中都可以使用它。

它作为单个 CLI 二进制文件 `squirrel` 提供，适用于 macOS、Windows 和 Linux。这项技能涵盖了操作它：安装、认证、运行审计、发布报告、云功能以及 MCP 集成。对于完整的修复网站工作流程（审计、将问题映射到代码、修复、重新审计），请使用配套的 `audit-website` 技能。

## 链接

- 网站：[squirrelscan.com](https://squirrelscan.com)
- 文档：[docs.squirrelscan.com](https://docs.squirrelscan.com)
- 规则参考：`https://docs.squirrelscan.com/rules/{rule_category}/{rule_id}`
- 仪表板（云账户、审计历史记录、积分）：[app.squirrelscan.com](https://app.squirrelscan.com)

## 安装

下载和安装说明：[squirrelscan.com/download](https://squirrelscan.com/download)

二进制文件安装到 `~/.local/bin/squirrel`。使用以下命令验证：

```bash
squirrel --version
```

保持最新：

```bash
squirrel self update
```

如果找不到 `squirrel`，请确保 `~/.local/bin` 在 PATH 中，或从下载页面重新安装。

## 命令概览

| 命令 | 目的 |
|---------|---------|
| `squirrel audit <url>` | 一步完成抓取 + 分析 + 报告 |
| `squirrel crawl <url>` | 仅抓取（不分析） |
| `squirrel analyze` | 在存储的抓取上运行审计规则 |
| `squirrel report [id]` | 查询、渲染、差异和发布存储的报告 |
| `squirrel entities` | 查询网站的 结构化数据 实体图；过滤、导出、差异 |
| `squirrel init` | 创建 `squirrel.toml` 项目配置 |
| `squirrel config` | 显示或编辑配置 |
| `squirrel auth` | 登录 / 注销 / 状态 / whoami |
| `squirrel keys` | 创造、列出、撤销组织 API 密钥 |
| `squirrel credits` | 云积分余额 + 功能定价 |
| `squirrel mcp` | 运行本地 MCP 服务器（stdio） |
| `squirrel skills` | 检查、安装、更新或删除这些代理技能 |
| `squirrel self` | install / update / doctor / disk / completion / version / settings / uninstall |
| `squirrel feedback` | 向 squirrelscan 团队发送反馈 |

每个命令都支持 `--help`。

## 快速入门

```bash
squirrel init -n my-project        # 可选：当前工作目录中的项目配置
squirrel audit https://example.com --format llm
```

- 本地审计免费，完全在您的机器上运行。无需账户。
- 当代理读取输出时，使用 `--format llm`：这是一种紧凑的、针对令牌优化的格式，专为 LLM 设计。
- 审计结果缓存在本地项目数据库中；`squirrel report` 重新渲染而无需重新抓取。

### 覆盖模式

| 模式 | 默认页面 | 行为 |
|------|---------------|----------|
| `quick` (默认) | 25 | 仅种子 + 网站地图，快速健康检查 |
| `surface` | 100 | 每个 URL 模式一个样本（`/blog/{slug}` 一次抓取） |
| `full` | 500 | 抓取所有内容，直到限制 |

```bash
squirrel audit https://example.com -C full -m 500 --format llm
```

## 认证和账户

本地审计永远不会需要账户。登录以解锁云功能（发布、浏览器渲染、计划抓取、积分）：

```bash
squirrel auth login      # 基于浏览器的登录
squirrel auth status     # 来源、范围、活动组织
squirrel auth whoami
squirrel auth logout
```

无头 / CI 环境使用组织 API 密钥：

```bash
squirrel keys create     # 需要登录会话；打印一个 sq_... 密钥
```

将其设置为 `SQUIRRELSCAN_API_KEY` 环境变量。将密钥视为密钥；切勿提交它们。

## 报告

渲染最新（或特定）存储的审计：

```bash
squirrel report --list                 # 最近审计
squirrel report <audit-id> --format llm
squirrel report example.com --format markdown -o report.md
```

格式：`console`，`text`，`json`，`html`，`markdown`，`xml`，`llm`。使用 `--severity error` 或 `--category core,links` 进行过滤。

### 发布

默认情况下，登录后的审计会发布到 reports.squirrelscan.com 的可共享报告（可见性：不公开）。控制它：

```bash
squirrel report <audit-id> --publish --visibility unlisted   # public | unlisted | private
squirrel audit https://example.com --no-publish              # 跳过某个运行的发布
squirrel audit https://example.com --offline                 # 完全离线：无云、无发布、无遥测
```

### 回归差异

```bash
squirrel report --diff <baseline-audit-id> --format llm
squirrel report --regression-since example.com --format llm
```

差异模式支持 `console`，`text`，`json`，`llm`，和 `markdown`。

## 结构化数据：实体图

每次审计都会将网站的 JSON-LD 折叠成一个实体图，而不是一个它发出的块列表。报告的 Entities 部分包含它：`html` 中的交互式图，`markdown` 和 `text` 中的表格，`json` 中的 `entities` 下整个文档，以及 `llm` 和 `xml` 中的 `<entities>` 块。

这能捕捉到每页验证器无法捕捉到的问题。六十个没有 `@id` 的有效 `Organization` 块对搜索引擎来说就是六十个组织，并且没有任何东西会累积：不是评论，不是个人资料链接，也不是权威。

```bash
squirrel entities                              # 最新审计的摘要
squirrel entities --list                       # 存储的审计及其实体计数
squirrel entities "https://example.com/#org"   # 一个实体，通过 @id、键或名称
squirrel entities --problem no-id              # 值得修复的实体
squirrel entities --problem split-identity     # 两次声明的东西
squirrel entities -f jsonld -o graph.json      # 导出
squirrel entities --diff                       # 自上次审计以来发生了什么变化
```

过滤器：`--type`，`--page`，`--problem`（可重复或逗号分隔），`--crawl <id>`，`--input <file>`。格式：`json`，`jsonld`，`html`，`markdown`，`csv`，`dot`，`graphml`，`mermaid`。`--diff` 接受 `markdown` 或 `json`。

问题：`no-id`，`conflict`，`dangling`，`single-page`，`split-identity`。

**当出现 `schema/entity-*` 找到时，请阅读 `references/entity-map-fixes.md`。** 它包含了有效形状和 Yoast、Rank Math、WordLift、Next.js、Astro 和 tangly 的确切更改。

### 证明修复已应用

重新审计后的 `squirrel entities --diff`。获得 `@id` 的实体会 **改变键**，因为键在有 `@id` 时就是 `@id`，所以一个简单的比较报告它为一个删除加上一个添加，修复看起来像损坏。`gainedId` 部分才是它已应用的地方。

在将其称为完成之前，需要检查两件事：

- **`coverage`** 在每个 `gainedId` 行上：`proven` 意味着较新的审计访问了每个声明了损坏版本的页面，并且在所有这些页面上都找到了替换。`partial` 意味着其中之一无法确定，所以重新审计与第一次运行相同的范围。
- **`notCrawled`** 应该为空。列在其中的实体没有被删除；只是它们的页面没有被再次访问。

缺少 `gainedId` 行不是失败的证明：匹配需要类型和名称不变，所以在一个编辑中更改 `@id` 和名称会显示为一个删除加上一个添加。

Docs: https://docs.squirrelscan.com/entity-map

## 云功能和使用积分

云功能按使用付费，使用积分（无需预付费）。检查余额和定价：

```bash
squirrel credits
```

- `--render` / `--render-mode auto|all|off`：云浏览器渲染用于客户端渲染页面（使用积分，需要登录）。
- `--yes` 跳过花费确认，直到配置的每个审计积分上限。
- `--fail-on "score<90"`（可重复）使 CI 运行在阈值触发时非零退出。
- 仪表板在 [app.squirrelscan.com](https://app.squirrelscan.com) 显示审计历史记录、问题和积分使用情况。

## MCP 服务器

通过 MCP 连接代理有两种方式：

- **本地（stdio）**：`squirrel mcp` 运行在本地 CLI 上。在您的代理的 MCP 配置中注册它，使用命令 `squirrel` 和参数 `["mcp"]`。
- **托管（streamable-http）**：`https://mcp.squirrelscan.com/mcp`。通过 MCP 客户端进行 OAuth 登录，或发送 `Authorization: Bearer sq_...` API 密钥标头。

### 实体工具

五个工具通过 MCP 提供实体图，在两个服务器上使用相同的名称和输入。在本地服务器上，它们读取项目存储，因此无需账户也无需花费积分。

| 工具 | 回答 |
|---|---|
| `list_entities` | 这个网站声明了什么？按 `type`，`page`，`problem`，`q` 过滤；页面使用 `limit`/`offset`。 |
| `get_entity` | 为什么这个被标记了？属性、声明页面、冲突值、内外引用。 |
| `get_entity_graph` | 图作为 `json`，`jsonld`，`mermaid`，`dot`，`graphml` 或 `markdown`。 |
| `compare_entities` | 两个审计之间发生了什么变化，修复是否已应用？ |
| `get_entity_findings` | 审计的 `schema/entity-*` 裁决，以及修复文本。 |

这些工具构建的循环，以及为什么优先于手动重新派生任何内容的原因：

1. `list_entities` 使用 `problem: "no-id"` 找到在多个页面上声明但没有东西将它们联系起来的实体。
2. 修复它们（见 `references/entity-map-fixes.md`）。
3. 重新审计：`run_audit`，或 `squirrel audit`。
4. `compare_entities` 检查您修复的键，每个键都有 `coverage: "proven"`。

阅读那些说明您没有被告知的字段，而不是从空结果中推断：

- **`truncation`**：列表是否被截断。否则，截断的列表和完整的列表看起来相同。
- **`warnings`**：是否跳过了较新的审计以存储实体，或项目存储无法读取。这是您避免将昨天的健康图描述为今天的图的方式。
- `get_entity_findings` 上的 **`analyzed`**：false 意味着规则从未运行，所以空结果是一个证据的缺失，而不是一个干净的结果。
- `jsonld` 图上的 **`generatedIds`**：网站留名不明的实体，导出为其创造的 `@id`s。它们不在网站上。

Docs: https://docs.squirrelscan.com/developers/mcp

### 代理反馈

当 squirrelscan 在任务中途让您感到意外（一个误报、一个缺失的标记、一个令人困惑的报告，或某件工作得很好），请告诉团队。每个不同的发现发送一条消息，包括规则 ID、URL 和您期望的内容。切勿将审计期间发现的密钥或凭证粘贴到反馈中。选择适合的类别：

- `bug_report`：squirrelscan 本身的缺陷，例如错误或缺失的规则结果、崩溃或损坏的工具。包括网站、规则 ID 和您期望的内容。
- `feature_request`：squirrelscan 应该做但没做的事情。
- `what_worked`：某件工作得很好，您希望团队知道。
- `confusing`：响应或行为不清楚。
- `missing_data`：报告或工具响应缺少您需要的东西。
- `tool_ergonomics`：工具形状、参数或命名不协调。
- `other`：任何其他东西。

**通过 MCP 连接？** 调用 `send_feedback` 工具：`category`，`message`，以及可选的 `run_id`/`website_id`。它托管在 MCP 服务器上，并且从 squirrel 0.0.99 开始在本地 `squirrel mcp` 上可用。在托管服务器上，它适用于任何凭证，包括只读 API 密钥，并将您的组织附加到它。

**从终端**（squirrel 0.0.99+），当文本在命令行上或通过管道时，`squirrel feedback` 从不提示：

```bash
squirrel feedback --category bug_report \
  -m "<rule-id> flags <what> on <url>; expected <what>" \
  --run-id <audit id, if you have one> --json
```

- `--json` 打印一行：`{"ok":true,...}`，或 `{"ok":false,"code":...,"error":...,"fallback_url":...}` 并退出 1。失败时，给用户 `fallback_url` 而不是在循环中重试。
- 它需要一个回复地址：保存的地址、登录账户的地址，或 `--email <address>`。`"code":"email_required"` 意味着没有已知的回复地址：要求用户提供他们的电子邮件，切勿编造一个。
- 更长的笔记可以管道：`cat notes.md | squirrel feedback --category tool_ergonomics --json`（在 5,000 个字符处切割）。以 `-` 开头的文本需要 `--message="..."`。

人类可以运行 `squirrel feedback` 而没有任何文本以获取引导提示，或使用 [squirrelscan.com/support](https://squirrelscan.com/support)。

## 配置

项目配置存储在 `squirrel.toml`（由 `squirrel init` 创建）。用户设置存储在 `~/.squirrel/settings.json`。

```bash
squirrel config show
squirrel config set <key> <value>
squirrel config path
squirrel config validate
```

有用的部分：`[crawler]`（延迟、标头、增量重新抓取），`[cloud]`（渲染模式、每个审计的最大积分）。

### 自定义请求标头

使用可重复的 `-H "Name: Value"` 标头或将 `headers` 映射放在 `[crawler]` 下，将标头附加到每个抓取请求。主要用例是 Web Bot Auth（Shopify / Cloudflare），以便那些阻止未知爬取器的平台可以授权 squirrelscan。标头值是密钥：squirrelscan 在输出中隐藏它们，并且您应该从密钥存储中获取它们，而不是提交它们。完整配方：https://docs.squirrelscan.com/guides/web-bot-auth

## 维护

```bash
squirrel self doctor       # 健康检查
squirrel self update       # 更新二进制文件
squirrel self completion   # shell 完成
squirrel skills update     # 更新安装的代理技能
squirrel self disk         # 每个项目和总 ~/.squirrel 磁盘使用情况
```

### 保持这些技能最新

CLI 自己管理这些技能（`squirrelscan` 和 `audit-website`）。这项技能是版本 1.6：本文件顶部 `metadata.version`。

```bash
squirrel skills status          # 安装版本、位置和最新发布的
squirrel skills status --json   # 相同的，作为 JSON
squirrel skills update --check  # 有更新时退出 1
squirrel skills update          # 更新已安装的；保留编辑的文件
```

当 `squirrel skills status` 显示比这个技能自己的（最新列中的 `↑`）更新的版本时，或者当用户询问更新 squirrelscan 或其技能时，建议 `squirrel skills update`。不要在中间其他工作时不提示运行它，并且只有在用户希望自己的技能文件编辑被替换时才添加 `--force`（首先备份他们的副本）。自动更新开启时，默认情况下，技能与 CLI 一起更新，通常没有什么可做的。使用 `npx skills` 早期安装的技能会被 `squirrel skills install` 接管。这些命令需要 squirrel 0.0.99 或更高版本；在旧版本上，请先运行 `squirrel self update`。

### 回收磁盘空间

每次审计都在项目数据库中保留其完整历史记录，因此重新审计同一网站会随着每次运行大致增加 `~/.squirrel`（一个 1,000 页的网站每个审计大约 95 MB）。`squirrel self disk` 显示了空间在哪里。`--prune` 退役最新的 `--keep` 之外的审计，并重建数据库，以便空间返回到文件系统：

```bash
squirrel self disk --prune --keep 3 --dry-run   # 列出将要删除的内容，不删除任何内容
squirrel self disk --prune --keep 3             # 打印计划，询问，然后退役
squirrel self disk --prune --keep 3 --project my-project --yes
```

- `--keep <n>` 是必需的：已停用的审计报告将无法再渲染，而 `report --list`、`--diff` 和 `--regression-since` 会查询该历史记录，因此窗口由用户决定。在为用户选择之前请先询问。
- 停用会保留下一次审计读取的所有内容（每个 URL 的最新页面记录、子资源、链接、图片），因此增量重新抓取仍然能获取其 `ETag` 并不会重新获取整个站点。
- 审计不会自行清理。需要 squirrel 0.0.92 或更高版本；在旧版本上请先运行 `squirrel self update`。

## 故障排除

- **`squirrel: 命令未找到`**：从 [squirrelscan.com/download](https://squirrelscan.com/download) 安装，并确保 `~/.local/bin` 在 PATH 中。
- **会话过期 / 401**：再次运行 `squirrel auth login`，或检查 `SQUIRRELSCAN_API_KEY`。
- **缓慢或卡住的抓取**：添加 `--verbose` 查看进度；大型站点可能需要几分钟。
- **无效的 URL**：包含协议：`https://example.com`，而不是 `example.com`。
- **其他问题**：运行 `squirrel self doctor`，然后使用 `bug_report` 类别报告：通过 `send_feedback` MCP 工具或 `squirrel feedback --json`（参见 Agent 反馈）提交的代理，或通过 `squirrel feedback` 或 [squirrelscan.com/support](https://squirrelscan.com/support) 提交的人类。
