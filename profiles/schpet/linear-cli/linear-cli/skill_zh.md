# 线性命令行界面

一个用于从命令行管理 Linear 问题的命令行工具，与 git 和 jj 集成。

## 前置条件

`linear` 命令必须在 PATH 环境变量中可用。检查方法：

```bash
linear --version
```

如果未全局安装，可以通过 npx 运行它：

```bash
npx @schpet/linear-cli --version
```

后续所有命令都可以用 `npx @schpet/linear-cli` 代替 `linear`。否则，请按照以下链接的安装说明操作：\
https://github.com/schpet/linear-cli?tab=readme-ov-file#install

## 常见任务

可复制粘贴的最常见流程的配方。优先使用这些专用命令，而不是 `linear api` — 只有在没有专用命令或标志涵盖操作时，才使用 GraphQL 降级方案。

### 使用过滤器查询问题

`issue query` 在所有指派者中搜索，并支持可以组合的结构化过滤器：

```bash
linear issue query --team ENG --state started --json
linear issue query --project "移动应用" --state 待处理 --state 筛选 --未分配
linear issue query --assignee sam --label bug --updated-after 2026-01-01
```

注意：`linear issue list` 是 `issue mine` 的别名，并且只显示您自己的问题 — 使用 `issue query` 查询其他人或整个团队/项目的问题范围。

### 列出我的问题

```bash
linear issue mine --state started --sort 优先级
```

### 创建问题

```bash
linear issue create --team ENG --title "修复登录重定向" \
  --description-file ./description.md --no-interactive
```

将多行 markdown 写入文件，并传递 `--description-file`（见下文 markdown 部分）；`--no-interactive` 避免在脚本使用中弹出提示。

### 更新问题的状态、指派者或标签

```bash
linear issue update ENG-123 --state "审核中" --assignee sam
linear issue update ENG-123 --unassign
linear issue update ENG-123 --add-label security             # 添加，保留现有标签
linear issue update ENG-123 --remove-label sprint-42         # 分离；不会删除标签
linear issue update ENG-123 --remove-label sprint-42 --add-label sprint-43  # 原子交换
linear issue update ENG-123 --label infra --label security   # 替换标签集
```

### 从模板创建问题或项目

```bash
linear template list --type issue --team ENG              # 查找团队期望的模板
linear template view "Bug report"                         # 查看它预填充的内容（标题、字段、正文、子问题）
linear issue create --team ENG --template "Bug report" --title "Safari 上登录失败"
linear project create --name "Q3 发布" --team ENG --template "Kickoff"
```

显式标志会覆盖模板的值，`--label` 会与标签合并，`--description` 会替换正文（省略它以保留正文）。文档模板不能通过 API 应用。

### 添加评论

```bash
linear issue comment add ENG-123 --body-file ./comment.md
```

### 附加图像或截图以便在行内显示

```bash
linear issue comment add ENG-123 --attach ./screenshot.png
```

这将上传图像并将其嵌入评论中，Linear 会将其行内渲染。当图像必须可见时，不要使用 `linear issue attach` — 该命令创建侧边栏链接附件，不会行内渲染图像。

### 查看问题 / 获取其 URL

```bash
linear issue view ENG-123          # 包括评论的详细信息
linear issue view ENG-123 --json   # 结构化输出
linear issue url ENG-123           # 仅打印 URL
```

### 关闭、删除或存档问题

```bash
linear issue update ENG-123 --state Done       # 或 Canceled；Linear 会稍后自动存档关闭的问题
linear issue delete ENG-123                    # 垃圾箱；可在 Linear 中恢复 30 天
linear issue archive ENG-123 --confirm         # 很少适用，见下文
```

优先选择关闭或删除，而不是存档。Linear 的文档说“存档会自动发生，没有手动存档项目的选项”（https://linear.app/docs/delete-archive-issues）：关闭的问题会在团队配置的周期后自动存档，Linear 已从其应用中移除了手动存档，因为人们将其用作垃圾箱。`issue archive` 直接调用 `issueArchive` 变异，绕过自动存档对开放父级、子问题、循环和项目的检查，存档的问题会从 `issue list`、`issue query` 和搜索中消失，除非传递 `--include-archived`。只有在用户明确要求时才存档。

## Markdown 内容的最佳实践

在处理包含 markdown 的问题描述或评论正文时，**始终优先使用基于文件的标志**，而不是将内容作为命令行参数传递：

- 使用 `--description-file` 为 `issue create` 和 `issue update` 命令
- 使用 `--body-file` 为 `comment add` 和 `comment update` 命令

**为什么使用基于文件的标志：**

- 确保 Linear 网页界面中的格式正确
- 避免换行符和特殊字符的 shell 转义问题
- 防止 markdown 中出现字面值 `\n` 序列
- 更容易处理多行内容

**示例工作流程：**

```bash
# 将 markdown 写入临时文件
cat > /tmp/description.md <<'EOF'
## 摘要

- 第一项
- 第二项

## 详情

这是一个具有正确格式的详细描述。
EOF

# 使用文件创建问题
linear issue create --title "我的问题" --description-file /tmp/description.md

# 或用于评论
linear issue comment add ENG-123 --body-file /tmp/comment.md
```

**仅用于简单、单行内容** 使用内联标志 (`--description`, `--body`)。

## Linear Markdown 功能

### 使用普通 URL 提及人员和资源

Linear 将 Markdown 中的资源**普通 Linear URL** 转换为链接提及。字面值 `@name`、`@[Name](id)` 或 Markdown 链接（如 `[Name](url)`）不会创建相同的提及。直接将普通 URL 放在评论或描述中：

```markdown
https://linear.app/yourworkspace/profiles/someuser 能否您审查这个？ https://linear.app/yourworkspace/issue/ENG-123 是相关的。
```

先在相关团队中解析人员。团队通常可以从问题标识符或当前目录推断：

```bash
linear team members ENG --json
```

使用选定成员的 `url` 字段原样粘贴到 Markdown 中。如果预期人员不属于该团队，请停止并确认后再使用 `linear user list --json` 搜索整个工作区；提及团队外的人员可能是偶然的。对于问题，使用 `linear issue url ENG-123` 并包含该普通 URL。

### 添加可折叠部分

使用 `+++ [标题]` 打开可折叠部分，并使用 `+++` 关闭它：

```markdown
+++ [服务器日志]

初始隐藏的 Markdown 内容。

+++
```

方括号中的标题和关闭的 `+++` 是必需的。

## 可用命令

从 `linear --help` 生成的紧凑命令列表：

```bash
linear api

linear auth
linear auth default
linear auth list
linear auth login
linear auth logout
linear auth migrate
linear auth token
linear auth whoami

linear config

linear cycle
linear cycle list
linear cycle view

linear document
linear document comment
linear document comment add
linear document comment list
linear document create
linear document delete
linear document list
linear document update
linear document view

linear initiative
linear initiative add-project
linear initiative archive
linear initiative comment
linear initiative comment add
linear initiative comment list
linear initiative create
linear initiative delete
linear initiative list
linear initiative remove-project
linear initiative unarchive
linear initiative update
linear initiative view

linear initiative-update
linear initiative-update create
linear initiative-update list

linear issue
linear issue agent-session
linear issue agent-session list
linear issue agent-session view
linear issue archive
linear issue attach
linear issue comment
linear issue comment add
linear issue comment delete
linear issue comment list
linear issue comment update
linear issue commits
linear issue create
linear issue delete
linear issue describe
linear issue id
linear issue link
linear issue mine
linear issue pull-request
linear issue query
linear issue relation
linear issue relation add
linear issue relation delete
linear issue relation list
linear issue start
linear issue title
linear issue update
linear issue url
linear issue view

linear label
linear label create
linear label delete
linear label list

linear markdown

linear milestone
linear milestone create
linear milestone delete
linear milestone list
linear milestone update
linear milestone view

linear project
linear project comment
linear project comment add
linear project comment list
linear project create
linear project delete
linear project list
linear project update
linear project view

linear project-update
linear project-update create
linear project-update list

linear schema

linear team
linear team autolinks
linear team create
linear team delete
linear team id
linear team list
linear team members
linear team states

linear template
linear template list
linear template view

linear user
linear user list
```

## 参考文档

- [api](references/api.md) - 发起原始 GraphQL API 请求
- [auth](references/auth.md) - 管理 Linear 身份验证
- [config](references/config.md) - 交互式生成 .linear.toml 配置文件
- [cycle](references/cycle.md) - 管理 Linear 团队周期
- [document](references/document.md) - 管理 Linear 文档
- [initiative](references/initiative.md) - 管理 Linear 举措
- [initiative-update](references/initiative-update.md) - 管理举措状态更新（时间线帖子）
- [issue](references/issue.md) - 管理 Linear 问题
- [label](references/label.md) - 管理 Linear 问题标签
- [markdown](references/markdown.md) - Linear 风格的 Markdown：提及和可折叠部分
- [milestone](references/milestone.md) - 管理 Linear 项目里程碑
- [project](references/project.md) - 管理 Linear 项目
- [project-update](references/project-update.md) - 管理项目状态更新
- [schema](references/schema.md) - 将 GraphQL 模式打印到标准输出
- [team](references/team.md) - 管理 Linear 团队
- [template](references/template.md) - 浏览 Linear 问题、项目和文档模板。使用 `issue create --template` 或 `project create --template` 应用一个。
- [user](references/user.md) - 管理 Linear 用户

有关组织功能（举措、标签、项目、批量操作）的精选示例，请参阅 [organization-features](references/organization-features.md)。

## 发现选项

要查看任何命令的可用子命令和标志，运行任何命令的 `--help`：

```bash
linear --help
linear issue --help
linear issue list --help
linear issue create --help
```

每个命令都有详细的帮助输出，描述所有可用的标志和选项。

一些命令有不是显而易见的必需标志。值得注意的例子：

- `issue list` 默认按优先级排序 — 通过 `--sort`（有效值：`manual`，`priority`）、`issue_sort` 配置选项或 `LINEAR_ISSUE_SORT` 环境变量覆盖。除非可以从目录推断团队，否则需要 `--team <key>` — 如果未知，请先运行 `linear team list`（`linear team list --json` 将团队名称映射到它们的 `key` 和 `id`）。
- `--no-pager` 仅在 `issue list` 上受支持 — 将其传递给其他命令（如 `project list`）将导致错误。

## 直接使用 Linear GraphQL API

**优先使用 CLI 执行所有支持的操作。** `api` 命令应仅作为未涵盖 CLI 的查询的降级方案使用。

### 检查模式以查找可用的类型和字段

将模式写入临时文件，然后搜索它：

```bash
linear schema -o "${TMPDIR:-/tmp}/linear-schema.graphql"
grep -i "cycle" "${TMPDIR:-/tmp}/linear-schema.graphql"
grep -A 30 "^type Issue " "${TMPDIR:-/tmp}/linear-schema.graphql"
```

### 发起 GraphQL 请求

`linear api` 将 GraphQL 文档作为其唯一位置参数，并且没有子命令。在引用的文档中放入 `query` 或 `mutation` 关键字：使用 `linear api 'query { ... }'`，决不使用 `linear api query '...'`。`linear issue query` 是一个单独的、真实的子命令，用于搜索问题。

**重要提示：** 包含非空类型标记（例如 `String` 后跟感叹号）的 GraphQL 查询必须通过 heredoc 标准输入传递，以避免转义问题。没有这些标记的简单查询可以内联传递。

```bash
# 简单查询（没有类型标记，因此内联即可）
linear api '{ viewer { id name email } }'

# 带有变量的查询 — 使用 heredoc 避免转义问题
linear api --variable teamId=abc123 <<'GRAPHQL'
query($teamId: String!) { team(id: $teamId) { name } }
GRAPHQL

# 通过文本搜索问题
linear api --variable term=onboarding <<'GRAPHQL'
query($term: String!) { searchIssues(term: $term, first: 20) { nodes { identifier title state { name } } } }
GRAPHQL

# 数字和布尔变量
linear api --variable first=5 <<'GRAPHQL'
query($first: Int!) { issues(first: $first) { nodes { title } } }
GRAPHQL

# 通过 JSON 传递复杂变量
linear api --variables-json '{"filter": {"state": {"name": {"eq": "In Progress"}}}}' <<'GRAPHQL'
query($filter: IssueFilter!) { issues(filter: $filter) { nodes { title } } }
GRAPHQL

# 管道到 jq 进行过滤
linear api '{ issues(first: 5) { nodes { identifier title } } }' | jq '.data.issues.nodes[].title'
```

### 高级：直接使用 curl

对于需要完全 HTTP 控制的用例，使用 `linear auth token`：

```bash
curl -s -X POST https://api.linear.app/graphql \
  -H "Content-Type: application/json" \
  -H "Authorization: $(linear auth token)" \
  -d '{"query": "{ viewer { id } }"}'
```
