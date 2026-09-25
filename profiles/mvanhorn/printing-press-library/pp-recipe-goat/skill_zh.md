<!-- 自动生成的文件 — 请勿编辑。
     此文件是库/餐饮/食谱/recipe-goat/SKILL.md 的逐字镜像，
     合并后由工具/generate-skills/ 重新生成。在此处进行的任何手动编辑
     都将在下次重新生成时被静默覆盖。请编辑库/源代码。
     请参阅仓库代理指南，第“生成的工件：registry.json，cli-skills/”部分。 -->

# 食谱山羊 — 打印机 CLI

## 前置条件：安装 CLI

此技能驱动 `recipe-goat-pp-cli` 二进制文件。**您必须在调用此技能的任何命令之前验证 CLI 是否已安装。** 如果它缺失，请先安装它：

1. 通过打印机安装程序安装。它将二进制文件默认设置为 macOS/Linux 上的 `$HOME/.local/bin` 和 Windows 上的 `%LOCALAPPDATA%\Programs\PrintingPress\bin`：
   ```bash
   npx -y @mvanhorn/printing-press-library install recipe-goat --cli-only
   ```
2. 验证：`recipe-goat-pp-cli --version`
3. 确保报告的安装目录在 `$PATH` 中，以便代理/运行时将调用此技能。

如果 `npx` 安装失败（没有 Node.js、离线等），请回退到直接 Go 安装（需要 Go 1.26.6 或更高版本）：

```bash
go install github.com/mvanhorn/printing-press-library/library/food-and-dining/recipe-goat/cmd/recipe-goat-pp-cli@latest
```

如果安装后 `--version` 报告“命令未找到”，则运行时无法看到 `$PATH` 上的二进制目录。在验证成功之前，请不要继续使用技能命令。

## 不应使用此 CLI 的情况

不要为此 CLI 激活需要创建、更新、删除、发布、评论、点赞、邀请、订购、发送消息、预订、购买或更改远程状态的请求。此打印 CLI 仅公开用于检查、导出、同步和分析的只读命令。

## HTTP 传输

此 CLI 使用与 Chrome 兼容的 HTTP 传输，用于面向浏览器的端点。它不需要驻留的浏览器进程即可进行正常 API 调用。

## 命令参考

**goat** — 跨站食谱排名器

- `recipe-goat-pp-cli goat <query>` — 从精选食谱网站获取候选者，然后按查询相关性、评分、评论量、时效性和网站可信度进行排名

**search** — 在精选网站上搜索食谱标题

- `recipe-goat-pp-cli search <query>` — 在精选网站上搜索食谱标题，不获取完整食谱；使用 `--site`、`--kid-friendly`、`--in-season` 和 `--limit` 来缩小结果范围

**recipe** — 获取、打开和检查食谱

- `recipe-goat-pp-cli recipe get <url>` — 从其源 URL 获取并渲染食谱，可选包含份量缩放、单位转换、Markdown/纯文本输出和 USDA 营养信息回填
- `recipe-goat-pp-cli recipe open <id>` — 在默认浏览器中打开保存的食谱
- `recipe-goat-pp-cli recipe reviews <id>` — 显示保存食谱的评论修改摘要占位符
- `recipe-goat-pp-cli recipe cost <id>` — 估算保存食谱的每份成本

**trending** — 精选食谱网站上的热门食谱

- `recipe-goat-pp-cli trending` — 显示每个网站主页上当前推荐的食谱；使用 `--site` 和 `--limit` 来限定扩展范围

**sub** — 烹饪替代品

- `recipe-goat-pp-cli sub <ingredient>` — 查找某个成分的替代品，可选按上下文或纯素食建议进行过滤

**trust** — 排名器的网站可信度分数

- `recipe-goat-pp-cli trust list` — 列出内置的每个网站可信度分数
- `recipe-goat-pp-cli trust set <site> <delta>` — 为排名器实验保存本地每个网站的可信度调整

**save** — 本地食谱簿捕获

- `recipe-goat-pp-cli save [url]` — 获取并保存一个食谱 URL，或使用 `--stdin` 从标准输入读取 URL；使用 `--tags` 附加本地标签

**cookbook** — 本地食谱簿搜索、标签和食品柜匹配

- `recipe-goat-pp-cli cookbook list` — 列出保存的食谱，可选按标签、网站或作者进行过滤
- `recipe-goat-pp-cli cookbook search <query>` — 通过标题和成分进行全文搜索保存的食谱，包含包含/排除成分过滤器
- `recipe-goat-pp-cli cookbook match` — 根据使用 `--have` 提供的食品柜成分查找可制作的保存食谱
- `recipe-goat-pp-cli cookbook tag <id> <tag>[,<tag>]` — 为保存的食谱附加一个或多个标签
- `recipe-goat-pp-cli cookbook untag <id> <tag>` — 从保存的食谱中移除标签
- `recipe-goat-pp-cli cookbook remove <id>` — 从本地食谱簿中移除食谱

**tonight** — 从本地食谱簿中选择晚餐

- `recipe-goat-pp-cli tonight` — 通过最大时间、时效性、饮食过滤器、标签和结果限制从保存的食谱中选择晚餐

**meal-plan** — 膳食计划和购物清单

- `recipe-goat-pp-cli meal-plan set <date> <meal> <recipe-id>` — 为特定日期和餐次计划保存的食谱
- `recipe-goat-pp-cli meal-plan show` — 显示指定日期范围内的计划餐次或当前一周
- `recipe-goat-pp-cli meal-plan remove <date> <meal>` — 清除计划餐次
- `recipe-goat-pp-cli meal-plan shopping-list` — 跨计划餐次聚合成分，可选按货架分组或导出为 Markdown、文本或 CSV

**cook** — 烹饪会话日志

- `recipe-goat-pp-cli cook log <recipe-id>` — 记录带有评分、笔记和可选日期的烹饪会话
- `recipe-goat-pp-cli cook history` — 列出过去的烹饪会话，可选按食谱或时间窗口进行过滤

**sync** — 本地 SQLite 同步，用于 API 支持的资源

- `recipe-goat-pp-cli sync` — 将 API 数据同步到本地 SQLite，用于离线搜索和分析，包含资源、检查点、分页和并发控制

**export** — 数据导出

- `recipe-goat-pp-cli export <resource> [id]` — 将 API 数据导出为 JSONL 或 JSON，用于备份、迁移或分析

**import** — JSONL 导入

- `recipe-goat-pp-cli import <resource>` — 通过发出 API 创建/更新调用导入记录；使用 `--dry-run` 预览而不发送

**workflow** — 复合数据工作流

- `recipe-goat-pp-cli workflow archive` — 将所有支持的资源同步到本地存储，用于离线访问和搜索
- `recipe-goat-pp-cli workflow status` — 显示本地存档状态和同步状态

**foods** — USDA 食品数据中央 — 成分营养查找

- `recipe-goat-pp-cli foods get` — 通过 FDC ID 获取特定食品
- `recipe-goat-pp-cli foods list` — 分页列出食品
- `recipe-goat-pp-cli foods search` — 在 USDA 食品数据中央搜索与查询匹配的食品

### 找到正确的命令

当您知道要做什么但不知道哪个命令可以做到时，直接询问 CLI：

```bash
recipe-goat-pp-cli which "<您自己的话描述功能>"
```

`which` 将自然语言的功能查询解析为与此 CLI 的精选功能索引中最佳匹配的命令。退出码 `0` 表示至少有一个匹配；退出码 `2` 表示没有自信的匹配 — 回退到 `--help` 或使用更窄的查询。

## 认证设置

通过环境变量设置您的 API 密钥：

```bash
export USDA_FDC_API_KEY="<您的密钥>"
```

或将其持久存储在 `~/.config/recipe-goat-pp-cli/config.toml` 中。

运行 `recipe-goat-pp-cli doctor` 以验证设置。

## 代理模式

向任何命令添加 `--agent`。扩展为：`--json --compact --no-input --no-color --yes`。

- **可管道** — JSON 输出到 stdout，错误输出到 stderr
- **可过滤** — `--select` 保留字段子集。点路径深入嵌套结构；数组按元素遍历。这对于在冗长 API 上保持上下文小至关重要：

  ```bash
  recipe-goat-pp-cli foods list --agent --select id,name,status
  ```
- **可预览** — `--dry-run` 显示请求而不发送
- **离线友好** — 同步/搜索命令在可用时可以使用本地 SQLite 存储库
- **非交互式** — 从不提示，每个输入都是一个标志
- **只读** — 不要使用此 CLI 进行创建、更新、删除、发布、评论、点赞、邀请、订购、发送或其他修改请求

### 响应包

读取本地存储或 API 的命令将输出包装在可追溯包中：

```json
{
  "meta": {"source": "live" | "local", "synced_at": "...", "reason": "..."},
  "results": <数据>
}
```

解析 `.results` 获取数据，解析 `.meta.source` 知道是实时还是本地。当 stdout 是终端时，仅在 stderr 打印人类可读的 `N results (live)` 摘要 — 管道/代理消费者在 stdout 上获得纯 JSON。

## 代理反馈

当您（或代理）注意到此 CLI 的问题时，请记录它：

```
recipe-goat-pp-cli feedback "the --since flag is inclusive but docs say exclusive"
recipe-goat-pp-cli feedback --stdin < notes.txt
recipe-goat-pp-cli feedback list --json --limit 10
```

条目存储在本地 `~/.recipe-goat-pp-cli/feedback.jsonl` 中。除非设置了 `RECIPE_GOAT_FEEDBACK_ENDPOINT` 并且传递了 `--send` 或 `RECIPE_GOAT_FEEDBACK_AUTO_SEND=true`，否则它们永远不会 POST。默认行为是本地仅。

写让您感到惊讶的内容，而不是错误报告。简短、具体、一行：这就是复合的关键。

## 输出交付

每个命令都接受 `--deliver <sink>`。输出除了（或代替）stdout 外还会发送到命名的接收器，以便代理可以无手动管道地路由命令结果。支持三种接收器：

| 接收器 | 效果 |
|------|------|
| `stdout` | 默认；仅写入 stdout |
| `file:<路径>` | 原子写入输出到 `<路径>`（临时 + 重命名） |
| `webhook:<url>` | 将输出正文 POST 到 URL (`application/json` 或 `application/x-ndjson` 当 `--compact` 时) |

未知方案会被拒绝，并命名支持的集合。Webhook 失败会返回非零值并在 stderr 上记录 URL + HTTP 状态。

## 命名配置文件

配置文件是保存的一组标志值，跨调用重用。当计划代理每次运行都使用相同的配置调用相同的命令时使用它 - HeyGen 的“信标”模式。

```
recipe-goat-pp-cli profile save briefing --json
recipe-goat-pp-cli --profile briefing foods list
recipe-goat-pp-cli profile list --json
recipe-goat-pp-cli profile show briefing
recipe-goat-pp-cli profile delete briefing --yes
```

显式标志始终优先于配置文件值；配置文件值优先于默认值。`agent-context` 列出所有可用配置文件，以便在运行时发现它们。

## 退出码

| 代码 | 含义 |
|------|------|
| 0 | 成功 |
| 2 | 使用错误（参数错误） |
| 3 | 资源未找到 |
| 4 | 需要认证 |
| 5 | API 错误（上游问题） |
| 7 | 被限流（等待并重试） |
| 10 | 配置错误 |

## 参数解析

解析 `$ARGUMENTS`：

1. **空、`help` 或 `--help** → 显示 `recipe-goat-pp-cli --help` 输出
2. **以 `install` 开头** → 以 `mcp` 结尾 → MCP 安装；否则 → 参见上述前置条件
3. **其他任何内容** → 直接使用（作为 CLI 命令使用 `--agent`）

## MCP 服务器安装

1. 安装 MCP 服务器：
   ```bash
   go install github.com/mvanhorn/printing-press-library/library/other/recipe-goat-pp-cli/cmd/recipe-goat-pp-mcp@latest
   ```
2. 向 Claude Code 注册：
   ```bash
   claude mcp add recipe-goat-pp-mcp -- recipe-goat-pp-mcp
   ```
3. 验证：`claude mcp list`

## 直接使用

1. 检查是否安装：`which recipe-goat-pp-cli`
   如果未找到，请提供安装（参见此技能开头的“前置条件”）。
2. 将用户查询匹配到上述唯一功能和命令参考中的最佳命令。
3. 使用 `--agent` 标志执行：
   ```bash
   recipe-goat-pp-cli <命令> [子命令] [参数] --agent
   ```
4. 如果不明确，请深入子命令帮助：`recipe-goat-pp-cli <命令> --help`.
