# squirrelscan CLI

squirrelscan 是为 AI 代理构建的网站审计工具。它回答“这个网站有什么问题以及如何修复它”：它像搜索引擎一样抓取网站，分析每个页面，针对 21 个类别中的 260 多条规则（包括 SEO、性能、安全、可访问性、内容、结构化数据、代理体验等），并返回健康评分以及具体的可修复问题。在部署前/后或 CI 过程中，每当用户希望检查、提升排名、加快速度或改善网站健康状况时，都可以使用它。

它作为 macOS、Windows 和 Linux 的单个 CLI 二进制文件 `squirrel` 提供。本技能涵盖其操作：安装、认证、运行审计、发布报告、云功能以及 MCP 集成。对于完整的修复网站工作流（审计、将问题映射到代码、修复、重新审计），请使用配套的 `audit-website` 技能。

## 链接

- 网站：[squirrelscan.com](https://squirrelscan.com)
- 文档：[docs.squirrelscan.com](https://docs.squirrelscan.com)
- 规则参考：`https://docs.squirrelscan.com/rules/{rule_category}/{rule_id}`
- 仪表板（云账户、审计历史记录、积分）：[app.squirrelscan.com](https://app.squirrelscan.com)

## 安装

下载和安装说明：[squirrelscan.com/download](https://squirrelscan.com/download)

二进制文件安装到 `~/.local/bin/squirrel`。验证方式：

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
| `squirrel report [id]` | 查询、渲染、差异化和发布存储的报告 |
| `squirrel entities` | 查询网站的结构化数据实体图；过滤、导出、差异化 |
| `squirrel init` | 创建 `squirrel.toml` 项目配置 |
| `squirrel config` | 显示或编辑配置 |
| `squirrel auth` | 登录 / 注销 / 状态 / whoami |
| `squirrel keys` | 创造、列出、撤销组织 API 密钥 |
| `squirrel credits` | 云积分余额 + 功能定价 |
| `squirrel mcp` | 运行本地 MCP 服务器（stdio） |
| `squirrel skills` | 安装或更新代理技能 |
| `squirrel self` | install / update / doctor / disk / completion / version / settings / uninstall |
| `squirrel feedback` | 向 squirrelscan 团队发送反馈 |

每个命令都支持 `--help`。

## 快速入门

```bash
squirrel init -n my-project        # 可选：当前目录中的项目配置
squirrel audit https://example.com --format llm
```

- 本地审计免费，完全在您的机器上运行。无需账户。
- 当代理读取输出时，使用 `--format llm`：这是一种紧凑、针对令牌优化的格式，专为 LLM 设计。
- 审计结果存储在本地项目数据库中；`squirrel report` 重新渲染而不重新抓取。

### 覆盖模式

| 模式 | 默认页面 | 行为 |
|------|---------------|----------|
| `quick` (默认) | 25 | 仅种子 + 网站地图，快速健康检查 |
| `surface` | 100 | 每个 URL 模式一个样本（`/blog/{slug}` 仅抓取一次） |
| `full` | 500 | 抓取所有内容，直到限制 |

```bash
squirrel audit https://example.com -C full -m 500 --format llm
```

## 认证和账户

本地审计永远不会需要账户。登录以解锁云功能（发布、浏览器渲染、计划抓取、积分）：

```bash
squirrel auth login      # 基于浏览器的登录
squirrel auth status     # 源、范围、活动组织
squirrel auth whoami
squirrel auth logout
```

无头 / CI 环境使用组织 API 密钥：

```bash
squirrel keys create     # 需要登录会话；打印 sq_... 密钥
```

将其设置为环境变量 `SQUIRRELSCAN_API_KEY`。将密钥视为密钥；切勿提交它们。

## 报告

渲染最新（或特定）存储的审计：

```bash
squirrel report --list                 # 最近审计
squirrel report <audit-id> --format llm
squirrel report example.com --format markdown -o report.md
```

格式：`console`、`text`、`json`、`html`、`markdown`、`xml`、`llm`。使用 `--severity error` 或 `--category core,links` 过滤。

### 发布

已登录的审计默认将可共享的报告发布到 reports.squirrelscan.com（可见性：不公开）。控制它：

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

差异模式支持 `console`、`text`、`json`、`llm` 和 `markdown`。

## 结构化数据：实体图

每次审计都将网站的 JSON-LD 折叠为一个实体图，而不是一个块列表。报告的实体部分包含它：`html` 中的交互式图、`markdown` 和 `text` 中的表格、`json` 中 `entities` 下面的整个文档、`llm` 和 `xml` 中的 `<entities>` 块。

这能捕捉到每页验证器无法发现的问题。六十个没有 `@id` 的有效 `Organization` 块对搜索引擎来说就是六十个组织，并且没有任何积累：不是评论，不是个人资料链接，不是权威。

```bash
squirrel entities                              # 最新审计的摘要
squirrel entities --list                       # 存储的审计及其实体计数
squirrel entities "https://example.com/#org"   # 一个实体，通过 @id、键或名称
squirrel entities --problem no-id              # 值得修复的实体
squirrel entities --problem split-identity     # 重复声明的一件事
squirrel entities -f jsonld -o graph.json      # 导出
squirrel entities --diff                       # 自上次审计以来发生了什么变化
```

过滤器：`--type`、`--page`、`--problem`（可重复或逗号分隔），`--crawl <id>`、`--input <file>`。格式：`json`、`jsonld`、`html`、`markdown`、`csv`、`dot`、`graphml`、`mermaid`。`--diff` 接受 `markdown` 或 `json`。

问题：`no-id`、`conflict`、`dangling`、`single-page`、`split-identity`。

**当出现 `schema/entity-*` 找到时，请阅读 `references/entity-map-fixes.md`。** 它包含了有效形状和针对 Yoast、Rank Math、WordLift、Next.js、Astro 和 tangly 的确切更改。

### 证明修复已应用

重新审计后的 `squirrel entities --diff`。获得 `@id` 的实体会**改变键**，因为当存在 `@id` 时，键就是 `@id`，所以一个简单的比较报告它为一个删除和一个添加，修复看起来像是损坏。`gainedId` 部分才是它已应用的原因。

在宣布完成之前需要检查两件事：

- **`coverage`** 在每个 `gainedId` 行上：`proven` 表示更新的审计访问了声明了损坏版本的每个页面，并且在所有页面上都找到了替换。`partial` 表示其中之一无法确定，因此重新审计与第一次运行相同的范围。
- **`notCrawled`** 应该为空。列出的实体没有被删除；只是它们的页面没有被再次访问。

缺少 `gainedId` 行不是失败的证明：匹配需要类型和名称保持不变，所以在一个编辑中更改 `@id` 和名称会显示为一个删除和一个添加。

文档：https://docs.squirrelscan.com/entity-map

## 云功能和积分

云功能按使用付费，使用积分（无需预付费）。检查余额和定价：

```bash
squirrel credits
```

- `--render` / `--render-mode auto|all|off`：云浏览器渲染客户端渲染页面（使用积分，需要登录）。
- `--yes` 跳过花费确认，直到配置的每个审计积分上限。
- `--fail-on "score<90"`（可重复）在阈值触发时使 CI 运行非零退出。
- 仪表板在 [app.squirrelscan.com](https://app.squirrelscan.com) 显示审计历史记录、问题和积分使用情况。

## MCP 服务器

通过 MCP 连接代理有两种方式：

- **本地（stdio）**：`squirrel mcp` 运行在本地 CLI 上。在您的代理的 MCP 配置中注册它，使用命令 `squirrel` 和参数 `["mcp"]`。
- **托管（streamable-http）**：`https://mcp.squirrelscan.com/mcp`。通过 MCP 客户端 OAuth 登录，或发送 `Authorization: Bearer sq_...` API 密钥标头。

### 实体工具

五个工具通过 MCP 提供实体图，在两个服务器上使用相同的名称和输入。在本地服务器上，它们读取项目存储，因此无需账户也无需花费积分。

| 工具 | 回答 |
|---|---|
| `list_entities` | 这个网站声明了什么？按 `type`、`page`、`problem`、`q` 过滤；页面使用 `limit`/`offset`。 |
| `get_entity` | 为什么这个被标记了？属性、声明页面、冲突值、内外引用。 |
| `get_entity_graph` | 图作为 `json`、`jsonld`、`mermaid`、`dot`、`graphml` 或 `markdown`。 |
| `compare_entities` | 两个审计之间的变化是什么，修复是否已应用？ |
| `get_entity_findings` | 审计的 `schema/entity-*` 判决，以及修复文本。 |

这些工具构建的循环，以及为什么优先于手动重新派生任何内容的原因：

1. 使用 `problem: "no-id"` 的 `list_entities` 找到在多个页面上声明但没有关联的实体。
2. 修复它们（参见 `references/entity-map-fixes.md`）。
3. 重新审计：`run_audit`，或 `squirrel audit`。
4. `compare_entities` 并检查您修复的每个键的 `gainedId`，每个键的 `coverage: "proven"`。
5. 读取表示您未被告知的字段的字段，而不是从空结果中推断：

- **`truncation`**：列表是否被截断。否则，截断的列表和完整的列表看起来相同。
- **`warnings`**：是否跳过了存储实体的最新审计，或者无法读取项目存储。这是您避免将昨天的健康图描述为今天的方法。
- `get_entity_findings` 上的 **`analyzed`**：false 表示规则从未运行，所以空结果表示证据的缺失，而不是干净的结果。
- `jsonld` 图上的 **`generatedIds`**：网站留为匿名实体的 `@id`s，导出为发明的。它们不在网站上。

文档：https://docs.squirrelscan.com/developers/mcp

### 代理反馈

在任何会话中，如果某件事让您感到意外，请调用 `send_feedback` 工具。它接受 `category`、`message` 和可选的 `run_id`/`website_id`。选择适合的类别：

- `bug_report`：squirrelscan 本身的缺陷，例如错误或缺失的规则结果、崩溃或损坏的工具。包括网站、规则 ID 和您期望的内容。
- `feature_request`：squirrelscan 应该做但没做的事情。
- `what_worked`：某事工作良好，您希望团队知道。
- `confusing`：响应或行为不明确。
- `missing_data`：报告或工具响应缺少您需要的内容。
- `tool_ergonomics`：工具形状、参数或命名笨拙。
- `other`：任何其他内容。

反馈直接发送到团队审查队列，并附有您的组织。它适用于任何经过认证的凭据，包括只读 API 密钥，并且现在可在托管 MCP 表面使用（尚未在 `squirrel mcp` 本地 stdio 上）。当您是代理报告会话中时，使用它而不是 `squirrel feedback`；人类可以使用 `squirrel feedback` 或 [squirrelscan.com/support](https://squirrelscan.com/support)。

## 配置

项目配置存储在 `squirrel.toml`（由 `squirrel init` 创建）。用户设置存储在 `~/.squirrel/settings.json`。

```bash
squirrel config show
squirrel config set <key> <value>
squirrel config path
squirrel config validate
```

有用部分：`[crawler]`（延迟、标头、增量重新抓取）、`[cloud]`（渲染模式、每个审计的最大积分）。

### 自定义请求标头

使用可重复的 `-H "Name: Value"` 标头或将 `headers` 映射放在 `[crawler]` 下，将标头附加到每个抓取请求。主要用例是 Web Bot Auth（Shopify / Cloudflare），因此 squirrelscan 可以授权那些阻止未知爬虫的平台。标头值是密钥：squirrelscan 在输出中隐藏它们，您应该从密钥存储中获取它们，而不是提交它们。完整配方：https://docs.squirrelscan.com/guides/web-bot-auth

## 维护

```bash
squirrel self doctor       # 健康检查
squirrel self update       # 更新二进制文件
squirrel self completion   # shell 完成
squirrel skills update     # 更新安装的代理技能
squirrel self disk         # 每个项目和总 ~/.squirrel 磁盘使用情况
```

### 回收磁盘空间

每次审计都在项目数据库中保留其完整历史记录，因此重新审计同一网站会使 `~/.squirrel` 每次运行增长约一个审计（一个 1,000 页的网站每个审计大约 95 MB）。`squirrel self disk` 显示空间在哪里。`--prune` 退役最新的 `--keep` 之外的审计，并重建数据库，以便空间返回到文件系统：

```bash
squirrel self disk --prune --keep 3 --dry-run   # 列出将要删除的内容，不删除
squirrel self disk --prune --keep 3             # 打印计划，询问，然后退役
squirrel self disk --prune --keep 3 --project my-project --yes
```

- `--keep <n>` 是必需的：退役的审计报告无法重新渲染，并且 `report --list`、`--diff` 和 `--regression-since` 会深入该历史记录，因此窗口由用户决定。在为它们选择之前先询问。
- 退役会保留下一个审计读取的所有内容（每个 URL 的最新页面记录、子资源、链接、图像），因此增量重新抓取仍然获得 `ETag`s，并且不会重新获取网站。
- 审计永远不会自动修剪。需要 squirrel 0.0.92 或更高版本；在旧版本上运行 `squirrel self update` 之前。

## 故障排除

- **`squirrel: command not found`**：从 [squirrelscan.com/download](https://squirrelscan.com/download) 安装，并确保 `~/.local/bin` 在 PATH 中。
- **Session expired / 401**：再次运行 `squirrel auth login`，或检查 `SQUIRRELSCAN_API_KEY`。
- **Slow or stuck crawl**：添加 `--verbose` 查看进度；大型网站可能需要几分钟。
- **Invalid URL**：包括协议：`https://example.com`，而不是 `example.com`。
- **Anything else**：运行 `squirrel self doctor`，然后报告它：代理通过 `send_feedback` MCP 工具（`bug_report` 类别），人类通过 `squirrel feedback` 或 [squirrelscan.com/support](https://squirrelscan.com/support)。
