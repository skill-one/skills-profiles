# Notion CLI

`notion` 是一个用于 Notion API 的命令行工具。单一 Go 二进制文件，完整 API 覆盖，双重输出（为人类准备的漂亮表格，为代理准备的 JSON）。当前版本：**v0.7.0**。

## 安装

```bash
# Homebrew
brew install 4ier/tap/notion-cli

# npm
npm install -g @4ier/notion-cli

# Go
go install github.com/4ier/notion-cli@latest

# 或者从 https://github.com/4ier/notion-cli/releases 下载二进制文件
```

## 认证

```bash
notion auth login --with-token <<< "ntn_xxxxxxxxxxxxx"
notion auth login --with-token --profile work <<< "ntn_xxx"  # 命名配置
export NOTION_TOKEN=ntn_xxxxxxxxxxxxx                        # 环境变量替代方案
notion auth status        # 显示工作空间 + 集成类型（内部/公开）
notion auth switch        # 交互式配置选择器
notion auth switch work   # 直接切换
notion auth doctor        # 健康检查 — 如果是内部集成会发出警告
```

`auth status` / `doctor` 会显示集成类型，因此当您需要在使用工作空间根内容之前共享父页面时，可以轻松发现。

## 搜索

```bash
notion search "query"                    # 所有内容
notion search "query" --type page        # 仅页面
notion search "query" --type database    # 仅数据库
```

## 页面

```bash
notion page view <id|url>                # 渲染页面内容
notion page list                         # 列出工作空间页面
notion page create <parent> --title "X" --body "content"
notion page create <db-id> --db "Name=Review" "Status=Todo"  # 数据库行

# 归档 / 恢复（软删除）
notion page archive <id>                 # 标准操作
notion page trash <id>                   # 别名
notion page delete <id>                  # 别名（遗留）
notion page restore <id>                 # 反向操作

# 移动 / 打开 / 编辑
notion page move <id> --to <parent>
notion page open <id>                    # 在浏览器中打开
notion page edit <id|url>                # 在 $EDITOR 中编辑（markdown 转换）

# 属性（类型感知）
notion page set <id> Key=Value ...
notion page props <id>                   # 显示所有（摘要；分页值可能被截断）
notion page props <id> <prop-id>         # 单个原始 JSON

# NEW in v0.7: 分页单属性获取（修复 >25 项截断问题）
notion page property <id> <prop-id>
notion page property <id> --name "References"         # 通过显示名称解析 id
notion page property <id> <prop-id> --format json

# 关系
notion page link <id> --prop "Rel" --to <target-id>
notion page unlink <id> --prop "Rel" --from <target-id>

# NEW in v0.7: 服务器端 markdown I/O（用于完整页面转储的首选方式）
notion page markdown <id>                # 打印到标准输出
notion page markdown <id> --out page.md  # 写入文件
notion page markdown <id> --format json  # 完整响应（截断标志，未知块 id）

notion page set-markdown <id> --file new.md           # 替换整个页面（默认）
cat new.md | notion page set-markdown <id> --file -   # 标准输入
notion page set-markdown <id> --append --text "\n\n> Appended"
notion page set-markdown <id> --after "Status...pending" --text "Now: done"
notion page set-markdown <id> --range "old...stale" --text "fresh" --allow-deleting-content
```

**`page markdown` vs `block list --md`**: 优先使用 `page markdown` 用于整个页面 — 它使用服务器渲染器并正确处理切换、列、同步块和数据库作为页面。仅在您需要单个子块时使用 `block list --md`。

## 数据库

```bash
notion db list                           # 列出数据库
notion db view <id>                      # 显示架构
notion db query <id>                     # 所有行
notion db query <id> -F 'Status=Done' -s 'Date:desc'
notion db query <id> --filter-json '{"or":[...]}'
notion db query <id> --all
notion db create <parent> --title "X" --props "Status:select,Date:date"
notion db update <id> --title "New Name" --add-prop "Priority:select"
notion db add <id> "Name=Task" "Status=Todo" "Priority=High"
notion db add-bulk <id> --file items.json
notion db export <id>                    # CSV（默认）
notion db export <id> --format json
notion db export <id> --format md -o report.md
notion db open <id>
```

### 过滤运算符

| 语法 | 含义 |
|------|------|
| `=` | 等于 |
| `!=` | 不等于 |
| `>` / `>=` | 大于（或等于） |
| `<` / `<=` | 小于（或等于） |
| `~=` | 包含 |

多个 `-F` 标志组合使用 AND。属性类型自动从架构检测。

### 排序：`-s 'Date:desc'` 或 `-s 'Name:asc'`

### 批量添加文件格式

```json
[{"Name": "Task A", "Status": "Todo"}, {"Name": "Task B", "Status": "Done"}]
```

## 块

```bash
notion block list <parent-id>            # 列出子块
notion block list <parent-id> --all
notion block list <parent-id> --depth 3  # 递归
notion block list <parent-id> --md       # markdown；优先使用 'page markdown' 用于页面
notion block get <id>

# 追加 / 插入 — 两者都自动处理 >100 个子块和 >2000 字符的代码块
notion block append <parent> "text"
notion block append <parent> "text" -t bullet
notion block append <parent> "text" -t code --lang ts        # 'ts' / 'sh' / 'yml' 等。标准化
notion block append <parent> --file notes.md                 # 任何长度，自动分批
notion block append <parent> --file big.md --on-oversize=truncate
notion block insert <parent> "text" --after <block-id>

# 更新 — 现在支持 markdown
notion block update <id> --text "plain new content"
notion block update <id> --text "See **[docs](https://x.com)**" --markdown
notion block update <id> --file patch.md                     # 必须解析为单个块

notion block delete <id1> [id2] [id3]
notion block move <id> --after <target>
notion block move <id> --before <target>
notion block move <id> --parent <new-parent>
```

块类型：`paragraph`/`p`, `h1`/`h2`/`h3`, `bullet`, `numbered`, `todo`, `quote`, `code`, `callout`, `divider`。

### 媒体块（图像 / 文件 / 视频 / 音频 / PDF）

```bash
# 外部 URL (http/https)
notion block append <page> --image-url https://example.com/a.png --caption "fig 1"

# 本地文件 → 一个命令上传并嵌入
notion block append <page> --image-file ./chart.png --caption "heap usage"
notion block append <page> --pdf-file ./spec.pdf
notion block append <page> --video-file ./demo.mp4

# 引用现有的文件上传 id
notion block append <page> --image-upload 351d45fb-... --caption "reused"
```

同样存在三个 (`--<kind>-url` / `--<kind>-file` / `--<kind>-upload`) 用于 `image`, `file`, `video`, `audio`, `pdf`。`--caption` 对任何块都有效。

## 评论

```bash
notion comment list <page-id>
notion comment add <page-id> --text "comment text"
notion comment add <page-id> --text "with @mention" --mention-user <user-id>
notion comment get <comment-id>
notion comment reply <comment-id> "reply text"          # 相同线程

# NEW in v0.7
notion comment update <comment-id> --text "edited text"
notion comment update <comment-id> --text "with @mention" --mention-user <user-id>
notion comment delete <comment-id>                      # 单个或多个
notion comment delete <id1> <id2> <id3>                 # 可变参数
```

## 用户

```bash
notion user me                           # 当前机器人信息
notion user list                         # 所有工作空间用户
notion user get <user-id>
```

## 文件

```bash
# 列出 / 获取 / 上传
notion file list
notion file get <upload-id>                                # NEW in v0.7 — 状态 / 大小 / URL
notion file upload ./local/file.pdf                        # 本地路径
notion file upload https://example.com/chart.png --name chart.png   # URL 源
curl -sSL https://host/file.zip | notion file upload - --name file.zip   # 标准输入
notion file upload ./image.png --to <page-id>              # 上传并附加到页面
```

## 原始 API（逃生舱）

```bash
notion api GET /v1/users/me              # /v1/ 如果缺失会自动添加
notion api GET /users/me                 # → 打印 'note: prepending /v1...' 并正常工作
notion api POST /v1/search --body '{"query":"test"}'
notion api PATCH /v1/pages/<id> --body @body.json        # 从文件读取正文
echo '{"query":"x"}' | notion api POST /v1/search --body -  # 显式标准输入
```

## 输出模式

- **终端 (TTY)**：彩色表格，可读格式
- **管道 / 脚本**：自动 JSON
- **显式**：`--format json` / `--format table` / `--format md`
- `--debug`：显示 HTTP 请求/响应详细信息

所有输出都包含完整的 Notion UUID。所有命令都接受 Notion URL 或 ID。

## 代理的提示

- `notion db add` 和 `notion page set` 自动检测架构中的属性类型，因此 `Tags=a,b,c`（多选）和 `Done=true`（复选框）都直接工作。
- 对于长 markdown，优先使用 `notion page set-markdown --file` 而不是 `notion block append --file` — 服务器端解析没有 100 个子块的限制。
- 对于可能包含 >25 项的关系 / 汇总属性，始终使用 `notion page property`（而不是 `page view` / `page props`）。
- 管道到 `jq`：`notion db query <id> -F 'Status=Done' --format json | jq '.results[].id'`
- 当错误看起来令人困惑时，检查它是否有 `→` 提示行 — CLI 会用可操作的下一步装饰常见的 API 错误。
- 当使用内部集成时：不允许创建工作空间根页面 — 首先共享一个父页面，然后传递其 id。
