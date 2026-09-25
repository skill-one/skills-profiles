# Typefully 技能

使用 [Typefully](https://typefully.com) 创建、安排和发布跨 X、LinkedIn、Threads、Bluesky、Mastodon 和 Substack Notes 的社交媒体内容。所有操作通过 `./scripts/typefully.js` (Node.js 18+，无依赖) 运行。所有命令输出 JSON。

> **脚本路径** 下方是相对于此技能目录的路径。根据技能安装位置解析它们。
>
> **新鲜度检查**：如果自上方的 `last-updated` 日期以来已超过 30 天，请告知用户该技能可能已过时，并指向 [`references/setup.md`](references/setup.md) 中的更新方法。
>
> **身份验证失败**：如果 CLI 返回 **"API key not found"**、**"Authentication failed"**、**"HTTP 401"** 或任何无效/过期密钥消息，请告知用户运行 `./scripts/typefully.js setup` 或更新 `TYPEFULLY_API_KEY`，然后停止。不要搜索凭证或回退到 Typefully 网页界面、浏览器抓取或本地开发服务器。参见 [`references/setup.md`](references/setup.md)。

## 被丢弃的 Typefully 草稿 URL

当用户给您一个 Typefully 草稿 URL 时，使用此技能而不是浏览或抓取 Typefully 网页界面。

- `https://typefully.com/?a=<social_set_id>&d=<draft_id>` 映射到：

  ```bash
  ./scripts/typefully.js drafts:get <social_set_id> <draft_id>
  ```

- `https://typefully.com/?d=<draft_id>` 可以使用配置的默认社交媒体集：

  ```bash
  ./scripts/typefully.js drafts:get <draft_id> --use-default
  ```

对于被丢弃的草稿 URL 上的草稿评论、回复、解决或编辑，首先使用上述映射获取草稿，然后在需要评论工作流详细信息时加载 [`references/comments.md`](references/comments.md)。

## 参考指南

仅在任务需要时加载这些：

| 指南 | 需要时... |
|-------|-------------------------|
| [`references/setup.md`](references/setup.md) | 配置 API 密钥、修复 "API key not found" 错误、设置 CI 或检查技能是否为最新版本 |
| [`references/comments.md`](references/comments.md) | 在草稿上添加、回复、解决或删除评论，或编辑已有评论的草稿 |
| [`references/platforms/x.md`](references/platforms/x.md) | 拉取 X（前身为 Twitter）的 analytics、引用或回复帖子、发布到社区或添加披露标签 |
| [`references/platforms/linkedin.md`](references/platforms/linkedin.md) | 在 LinkedIn 上提及公司或个人 |
| [`references/platforms/x-articles.md`](references/platforms/x-articles.md) | 编写或编辑长格式 X Article（独立平台） |

---

## 1. 选择一个社交媒体集

"社交媒体集" 是用户称为 "账户" 的东西——一个身份的连接平台。大多数命令在配置默认值后无需 `social_set_id` 即可工作。可以位置传递 (`drafts:list 123`) 或作为 `--social-set-id 123` 传递。

要决定使用哪个社交媒体集：

1. 运行 `config:show`。如果 `default_social_set` 已设置，CLI 会自动使用它——继续。
2. 否则运行 `social-sets:list`。如果只有一个，就使用它。
3. 如果存在多个且没有默认值，询问用户，然后提供保存它的选项：`config:set-default`。
4. 重复会话中先前解析的社交媒体集，而无需再次询问。

---

## 2. 创建草稿

```bash
./scripts/typefully.js drafts:create --text "您的帖子"
```

- 如果省略 `--platform`，将自动选择第一个连接的平台。命名平台：`x`、`linkedin`、`threads`、`bluesky`、`mastodon`、`substack`（Substack Notes）、`x_article`。
- 使用单独的一行上的 `---` 分割线程。例外：`substack` 每个草稿只接受一个帖子——没有线程。对于一个线程加一个 Substack Note，使用下面的单草稿模式，以给 `substack` 其自己的单帖子内容。
- Substack Notes 媒体：仅限图片和 GIF（最多 6 个）——视频会被拒绝。
- 使用 `--media` 附加媒体，使用 `--tags` 添加标签，使用 `--scratchpad` 添加内部笔记，使用 `--title` 添加内部名称。
- 使用 `--file ./post.txt` 从文件读取内容，而不是 `--text`。

### 每个帖子一个草稿——始终

对于多个平台上的相同内容，将多个平台传递给**单个**草稿：

```bash
./scripts/typefully.js drafts:create --platform x,linkedin --text "重大公告！"
./scripts/typefully.js drafts:create --all --text "发布到所有平台！"   # 所有连接的平台
```

当内容应在每个平台有所不同（例如一个 X 线程加一个定制的 LinkedIn 帖子）时，**仍然使用一个草稿**——使用第一个平台创建，然后使用 `drafts:update` 添加另一个不同内容的草稿：

```bash
./scripts/typefully.js drafts:create --platform linkedin --text "很兴奋要分享..."   # -> id draft-123
./scripts/typefully.js drafts:update draft-123 --platform x --text "🧵 线程时间！" --use-default
```

除非用户明确希望每个平台有单独的草稿，否则**永远不要创建多个草稿**。

> `--all` 排除 `x_article`。X Article 是独立的，不能与其他任何平台组合——参见 [`references/platforms/x-articles.md`](references/platforms/x-articles.md)。
>
> `--all` 在连接时包括 `substack`。由于 Substack Notes 只接受一个帖子，`--all` 与线程内容会出错——通过 `--platform` 排除 `substack`，或使用 `drafts:update` 给它自己的单帖子内容。

### Scratchpad 笔记

当用户要求向草稿添加笔记、想法或上下文时，使用 `--scratchpad`——**不要写入本地文件。** Scratchpad 笔记附加到 Typefully 中的草稿，在 UI 中可见，保持私密，并且永远不会发布。

```bash
./scripts/typefully.js drafts:create --text "我的帖子" --scratchpad "想法：1) 添加统计数据 2) 包含引用"
```

### 链接预览

当帖子包含 URL 时，Typefully 会自动获取文本中最后一个 URL 的 Open Graph 元数据，并在 **LinkedIn、Threads、Bluesky 和 Substack Notes** 上发布一个富链接预览卡片。不需要标志——它只是工作。X 和 Mastodon 在发布后会自动展开链接。在 Substack Notes 中，当笔记包含图片时（图片和链接卡片是互斥的）会跳过卡片。

要作为纯文本发布 URL 而不显示卡片，传递 `--hide-link-preview`。抑制仅支持 **LinkedIn、Threads 和 Substack Notes**（与 Typefully 编辑器匹配）；如果目标平台中没有一个，该标志会出错，并且会被忽略在混合平台草稿中的其他平台：

```bash
./scripts/typefully.js drafts:create --platform linkedin,threads --text "阅读这个 https://example.com" --hide-link-preview
./scripts/typefully.js drafts:update draft-123 --hide-link-preview --use-default   # 在现有草稿上隐藏卡片
```

---

## 3. 安排和发布

```bash
./scripts/typefully.js drafts:create --text "..." --schedule next-free-slot   # 或 ISO 时间，或 "now"
./scripts/typefully.js drafts:schedule <draft_id> --time next-free-slot --use-default
./scripts/typefully.js drafts:publish <draft_id> --use-default
./scripts/typefully.js drafts:create --text "..." --plan next-free-slot      # 计划：有日期但无效
./scripts/typefully.js drafts:plan <draft_id> --time next-free-slot --use-default
```

- `next-free-slot` 让 Typefully 选择最佳时间。
- **发布是不可逆的且是公开的**——除非用户说 "立即发布" / "立即发布"，否则先确认。创建草稿是安全的。
- **计划草稿** 停留在其日期的队列/日历上，但永远不会自动发布。使用 `drafts:schedule`（或使用 `drafts:publish` 发布它）将其确认到实际日程中。日期已过期的计划草稿**不是逾期也不是失败**——它只是尚未确认；重新计划或确认它。`--plan`/`--schedule` 互斥；`drafts:update --plan null` 将草稿恢复为普通草稿状态。
- 单参数命令在配置了默认社交媒体集时需要 `--use-default`（见下方的 [安全说明](#commands)）。

---

## 常见操作

| 用户说... | 操作 |
|--------------|--------|
| "草稿一条关于 X 的推文" | `drafts:create --text "..."` |
| "发布这个到 LinkedIn" | `drafts:create --platform linkedin --text "..."` |
| "发布一个 Substack Note" | `drafts:create --platform substack --text "..."`（单个帖子，没有线程） |
| "发布到 X 和 LinkedIn"（相同内容） | `drafts:create --platform x,linkedin --text "..."` |
| "X 线程 + 定制的 LinkedIn 帖子" | 一个草稿，然后使用 `drafts:update` 添加平台 |
| "安排这个到明天" / "最近的帖子？" | `drafts:list --status scheduled` / `--status published` |
| "将这个安排为明天" | `drafts:create --text "..." --schedule "<ISO time>"` |
| "立即发布这个" | `drafts:create --text "..." --schedule now` 或 `drafts:publish <id> --use-default` |
| "为周二安排这个"（没有发布承诺） | `drafts:create --text "..." --plan "<ISO time>"`，稍后使用 `drafts:schedule` 确认 |
| "检查可用标签" | `tags:list` |
| "检查我的发布配额" | `social-sets:get` → `publishing_quota` |
| "草稿一个 X Article" | 参见 [`references/platforms/x-articles.md`](references/platforms/x-articles.md) |
| "在 LinkedIn 上提及一家公司" | 参见 [`references/platforms/linkedin.md`](references/platforms/linkedin.md) |
| "显示我的 X analytics / 关注者" | 参见 [`references/platforms/x.md`](references/platforms/x.md) |
| "在 / 解决一个评论" | 参见 [`references/comments.md`](references/comments.md) |

---

## 命令

所有命令输出 JSON。每个 `[social_set_id]` 都是可选的，并回退到配置的默认值。

> **安全说明**：`drafts:get`、`drafts:update`、`drafts:delete`、`drafts:schedule`、`drafts:plan` 和 `drafts:publish` 在传递单个参数（草稿 ID）时需要 `--use-default`，而配置了默认社交媒体集。

平台和工作流特定命令位于它们的指南中：[`platforms/x.md`](references/platforms/x.md)（analytics、quotes、replies、communities、disclosures）、[`platforms/linkedin.md`](references/platforms/linkedin.md)（mentions）、[`platforms/x-articles.md`](references/platforms/x-articles.md)、[`comments.md`](references/comments.md) 和 [`setup.md`](references/setup.md)。

### 用户和社交媒体集

| 命令 | 描述 |
|---------|-------------|
| `me:get` | 获取认证用户信息 |
| `social-sets:list` | 列出您可以访问的所有社交媒体集 |
| `social-sets:get <id>` | 社交媒体集详细信息，包括连接的平台和 `publishing_quota` |

`social-sets:get` 在可用时返回 `publishing_quota` 对象：`used`、`remaining`（或 `"unlimited"`）和 `resets_at`。在用户询问容量或发布/安排失败时带有配额副本时检查它。发布/安排时。

### 草稿

每个草稿命令接受一个可选的前导 `[social_set_id]`，它回退到配置的默认值。四个基本命令：

| 命令 | 描述 |
|---------|-------------|
| `drafts:list [social_set_id]` | 列出草稿。使用 `--status scheduled\|published\|...` 过滤，使用 `--sort` 排序 |
| `drafts:get [social_set_id] <draft_id>` | 获取具有完整内容的草稿。添加 `--exclude-comment-markers` 以渲染 `posts[*].text` 而没有评论锚点（仅显示） |
| `drafts:create [social_set_id] --text "<post text>"` | 创建草稿（如果省略 `--platform`，则自动选择平台） |
| `drafts:update [social_set_id] <draft_id> --text "<post text>"` | 替换草稿内容 |

将以下任何标志添加到 `drafts:create` 或 `drafts:update` 命令。**适用** 列表示示每个标志的有效位置：

| 标志 | 效果 | 适用 |
|------|--------|-----------|
| `--platform x,linkedin` | 目标特定平台，逗号分隔 | create, update |
| `--all` | 所有连接的平台（排除 `x_article`） | create |
| `--file <path>` | 从文件读取内容而不是 `--text` | create, update |
| `--append --text "<text>"` | 追加到现有线程 | update |
| `--media <media_ids>` | 附加媒体（逗号分隔） | create, update |
| `--tags "tag1,tag2"` | 设置标签（如果这是更新中唯一的变化，内容保持不变） | create, update |
| `--title "<internal title>"` | 内部草稿标题（不发布） | create, update |
| `--scratchpad "<notes>"` | 附加内部笔记（见 [Scratchpad 笔记](#scratchpad-notes)） | create, update |
| `--share` | 生成公共分享 URL | create, update |
| `--schedule <iso\|next-free-slot\|now>` | 安排或重新安排草稿 | create, update |
| `--plan <iso\|next-free-slot>` | 计划草稿：有日期但无效，直到确认（与 `--schedule` 互斥；更新中的 `null` 将其恢复为普通草稿） | create, update |
| `--hide-link-preview` | 抑制链接预览卡片（仅限 LinkedIn/Threads/Substack — 见 [链接预览](#link-previews)） | create, update |
| `--exclude-comment-markers` | 渲染响应而不带锚点（仅显示；验证仍然适用） | update |
| `--force-overwrite-comments` | 破坏性最后手段——参见 [`comments.md`](references/comments.md) | update |

例如，像这样组合基本命令与标志：

```bash
./scripts/typefully.js drafts:create --text "发布日！" --platform x,linkedin --tags product --schedule next-free-slot
./scripts/typefully.js drafts:update 456 --text "修订版本" --media abc-123 --use-default
```

> 仅限 X 草稿标志 (`--reply-to`、`--quote-post-url`、`--community`、`--paid-partnership`、`--made-with-ai`): 参见 [`platforms/x.md`](references/platforms/x.md)。X Article 标志 (`--content-markdown`、`--cover-media-id`): 参见 [`platforms/x-articles.md`](references/platforms/x-articles.md)。

### 安排和发布

单参数形式在配置了默认社交媒体集时需要 `--use-default`。

| 命令 | 描述 |
|---------|-------------|
| `drafts:schedule <social_set_id> <draft_id> --time <iso\|next-free-slot>` | 安排到时间或下一个可用槽位（也确认计划草稿） |
| `drafts:plan <social_set_id> <draft_id> --time <iso\|next-free-slot>` | 计划到日期，但不自动发布；稍后使用 `drafts:schedule` 确认 |
| `drafts:publish <social_set_id> <draft_id>` | 立即发布 |
| `drafts:delete <social_set_id> <draft_id>` | 删除草稿 |

### 队列

队列是一个**特定社交媒体集的时间线**：来自社交媒体集的队列时间槽（来自社交媒体集的队列时间表）加上该相同社交媒体集的安排和计划草稿/帖子。当用户询问某个日期范围内某个账户的安排或空闲情况时，使用 `queue:get`。

| 命令 | 描述 |
|---------|-------------|
| `queue:get [social_set_id] --start-date <YYYY-MM-DD> --end-date <YYYY-MM-DD>` | 队列时间线：空闲槽位加上日期范围内的安排/计划草稿和帖子（检查每个草稿的 `status` — 计划草稿永远不会自动发布） |
| `queue:schedule:get [social_set_id]` | 获取队列时间表规则 |
| `queue:schedule:put [social_set_id] --rules '[{"h":9,"m":30,"days":["mon","wed","fri"]}]'` | 替换队列时间表规则（完整替换） |

蛇形命名日期别名 (`--start_date`、`--end_date`) 被接受。

### 标签

标签按每个社交媒体集的范围——一个社交媒体集中的标签不会出现在另一个社交媒体集中。在创建之前检查现有标签。

| 命令 | 描述 |
|---------|-------------|
| `tags:list [social_set_id]` | 列出所有标签 |
| `tags:create [social_set_id] --name "Tag Name"` | 创建一个新标签 |

### 媒体

| 命令 | 描述 |
|---------|-------------|
| `media:upload [social_set_id] <file_path>` | 上传媒体，等待处理，返回准备好的 `media_id` |
| `media:upload ... --no-wait` | 立即上传并返回（使用 `media:status` 查询） |
| `media:upload ... --timeout <seconds>` | 自定义处理超时（默认 60 秒） |
| `media:status [social_set_id] <media_id>` | 检查上传状态 |

### 示例

```bash
# 创建推文（默认社交媒体集）
./scripts/typefully.js drafts:create --text "你好，世界!"

# 显式社交媒体集 ID
./scripts/typefully.js drafts:create 123 --text "你好，世界!"

# 跨平台，相同内容
./scripts/typefully.js drafts:create --platform x,linkedin,threads --text "重大公告！"
./scripts/typefully.js drafts:create --all --text "发布到所有平台！"

# 创建并安排到下一个槽位
./scripts/typefully.js drafts:create --text "安排的帖子" --schedule next-free-slot

# 创建带标签
./scripts/typefully.js drafts:create --text "营销帖子" --tags marketing,product

# 列出安排的帖子，最新安排的优先
./scripts/typefully.js drafts:list --status scheduled --sort scheduled_date

# 队列视图，日期范围
./scripts/typefully.js queue:get --start-date 2026-02-01 --end-date 2026-02-29

# 替换队列时间表规则
./scripts/typefully.js queue:schedule:put --rules '[{"h":9,"m":30,"days":["mon","wed","fri"]}]'

# 带 Scratchpad 笔记的草稿
./scripts/typefully.js drafts:create --text "下周发布！" --scratchpad "在发布前与营销团队协调。"

# 上传媒体，然后附加它
./scripts/typefully.js media:upload ./image.jpg          # -> {"media_id": "abc-123", "status": "ready"}
./scripts/typefully.js drafts:create --text "查看这张图片！" --media abc-123

# 向现有草稿添加媒体
./scripts/typefully.js drafts:update 456 --text "更新帖子并添加图片" --media xyz --use-default
```

---

## 参考

### 字符限制

X 280 · LinkedIn 3000 · Threads 500 · Bluesky 300 · Mastodon 500 · Substack Notes 10000。

### 草稿 URL

Typefully 草稿 URL 编码了社交媒体集和草稿 ID：`https://typefully.com/?a=<social_set_id>&d=<draft_id>`（例如 `a=12345` → 社交媒体集 ID，`d=67890` → 草稿 ID）。参见 [被丢弃的 Typefully 草稿 URL](#dropped-typefully-draft-urls) 中的命令映射。

### 自动化指南

为了保持账户的良好状态，尤其是在 X 上：

- 跨账户不重复内容。
- 不发送未经请求的自动回复——只有在用户明确请求时才回复。
- 不进行趋势操纵，不进行虚假互动（点赞/转发/关注）。
- 尊重速率限制；草稿在发布或明确分享之前保持私密。

当不确定时，为用户审查创建草稿，而不是直接发布。
