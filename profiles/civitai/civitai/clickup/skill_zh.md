# ClickUp

通过 API 与 ClickUp 任务和文档进行交互。获取任务信息、查看评论、创建任务、管理分配、发布更新以及创建/编辑文档。

## 设置

**首先安装依赖项——一次性，每个签出：**

```bash
cd .claude/skills/clickup && npm install
```

`lib/markdown.mjs` 使用 `remark` 解析 markdown，而 `query.mjs` 通过 `lib/format.mjs` 在启动时访问它。**每个**命令——不仅仅是评论命令——在运行之前都以 `ERR_MODULE_NOT_FOUND` 退出。

然后在当前技能目录中创建 `accounts.json` 并输入您的 API 令牌：

```json
{
  "defaultAccount": "bot",
  "accounts": {
    "bot": {
      "apiToken": "pk_your_token_here"
    }
  }
}
```

在 ClickUp 设置 > 应用 > API 令牌处生成令牌

或者使用 CLI 添加帐户：

```bash
node query.mjs add-account bot --token pk_your_token_here
```

团队 ID、用户 ID 和其他字段在首次使用时自动检测并缓存。

**从 .env 迁移**：如果您有现有的 `.env` 文件，凭据将在首次运行时自动迁移到 `accounts.json`。`.env` 文件将保留；准备好时删除它。

### 默认列表（可选）

在您的帐户中设置 `defaultListId` 以启用创建任务而无需指定列表：

```json
{
  "defaultAccount": "bot",
  "accounts": {
    "bot": {
      "apiToken": "pk_...",
      "defaultListId": "901111220963"
    }
  }
}
```

### 多帐户

支持多个命名帐户（例如，“bot”用于自动化，“justin”用于个人使用）：

```json
{
  "defaultAccount": "bot",
  "accounts": {
    "bot": {
      "apiToken": "pk_...",
      "teamId": "8459928",
      "userId": "75386805",
      "defaultListId": "901111220963"
    },
    "justin": {
      "apiToken": "pk_...",
      "teamId": "8459928",
      "userId": "10620972"
    }
  }
}
```

每个帐户只需要 `apiToken`。其他字段将自动检测并缓存。

使用 `--account <name>` 与任何命令一起定位特定帐户：

```bash
node query.mjs me --account justin
node query.mjs my-tasks --account bot
```

帐户管理命令：

```bash
node query.mjs accounts                          # 列出所有帐户
node query.mjs switch-account justin             # 更改默认值
node query.mjs add-account justin --token pk_... # 添加帐户
node query.mjs remove-account old-account        # 删除帐户
```

## 运行命令

```bash
node query.mjs <command> [options]
```

### 任务命令

| 命令 | 描述 |
|------|------|
| `get <url\|id>` | 获取任务详细信息（名称、描述、状态、分配者等） |
| `comments <url\|id>` | 列出任务上的评论（使用 `--threads` 将回复内联展开） |
| `thread <comment_id>` | 查看特定评论上的线程回复 |
| `reply <comment_id> "message"` | 向评论发布线程回复 |
| `comment <url\|id> "message"` | 向任务发布评论（支持 markdown） |
| `status <url\|id> [status]` | 更新任务状态（或列出可用状态） |
| `tasks <list_id>` | 列出列表中的任务 |
| `me` | 显示当前用户信息 |
| `create [list_id] "title"` | 创建新任务（如果设置了默认值，则可选 list_id） |
| `my-tasks` | 列出工作区中分配给您的所有任务 |
| `search [query]` | 搜索任务——需要范围：`--list`、`--folder`、`--me`、`--assignee`、`--status` 或 `--all` |
| `find-list "name"` | 通过名称查找列表或文件夹（快速结构遍历，无需获取任务） |
| `assign <task> <user>` | 将任务分配给用户（通过名称、电子邮件或 ID） |
| `due <task> "date"` | 设置截止日期（例如，“明天”、“星期五”、“+3d”） |
| `priority <task> <level>` | 设置优先级（紧急、高、正常、低、无） |
| `subtask <task> "title"` | 创建子任务 |
| `parent <task> <parent_task>` | 将现有任务作为另一个任务的子任务 |
| `milestone <task> <on\|off>` | 将任务转换为里程碑，或恢复为普通任务 |
| `move <task> <list_id>` | 将任务移动到不同的列表 |
| `link <task> <url> ["desc"]` | 添加外部链接引用（作为评论） |
| `checklist <task> "item"` | 向任务添加清单项目 |
| `delete-comment <comment_id>` | 删除评论 |
| `watch <task> <user>` | 将用户添加为任务的观察者/关注者 |
| `tag <task> "tag_name"` | 向任务添加标签 |
| `description <task> "text"` | 更新任务描述（支持 markdown） |
| `start <task> "date"` | 设置开始日期（与截止日期格式相同） |
| `schedule <task> "start" "due"` | 设置开始和截止日期 |
| `rename <task> "new name"` | 重命名任务 |
| `depends <task> <other>` | 将任务设置为等待另一个任务 |
| `blocks <task> <other>` | 将任务设置为阻塞另一个任务 |
| `task-link <task> <other>` | 在任务之间创建双向链接 |
| `update-comment <id> "text"` | 更新评论的文本 |
| `resolve-comment <id>` | 解决/关闭评论 |
| `remove-tag <task> "tag"` | 从任务中删除标签 |
| `unwatch <task> <user>` | 从任务中删除观察者 |
| `archive <task>` | 归档任务（从活动视图中删除） |
| `unarchive <task>` | 恢复归档任务 |
| `claim <task>` | 将您的会话与此任务链接（为可恢复性设置会话 ID 自定义字段） |

### 列表命令

| 命令 | 描述 |
|------|------|
| `list <list_id>` | 获取列表详细信息（名称、状态、任务数量） |
| `create-list <space> "name"` | 在空间中创建新列表 |
| `update-list <list_id>` | 更新列表属性 (`--name`、`--content`) |
| `delete-list <list_id>` | 删除列表 |
| `lists <folder_id>` | 列出文件夹中的所有列表 |
| `space-lists <space_id>` | 列出无文件夹列表 |

### 文档命令

| 命令 | 描述 |
|------|------|
| `docs ["query"]` | 搜索/列出工作区中的文档（可选搜索查询） |
| `doc <doc_id>` | 获取文档详细信息和页面列表 |
| `create-doc "title"` | 创建新文档（使用 `--content` 设置初始内容） |
| `page <doc_id> <page_id>` | 获取页面内容（markdown 格式） |
| `create-page <doc_id> "title"` | 向文档添加新页面（使用 `--parent` 创建子页面） |
| `edit-page <doc_id> <page_id>` | 编辑页面内容或名称 |

### 附件命令

| 命令 | 描述 |
|------|------|
| `attach <url\|id>` | 将文件附件（多个）上传到任务 (`--attach path`，可重复） |
| `fetch-image <url>` | 将 ClickUp 附件下载到本地临时文件 (`--output path` 用于自定义位置) |

### 选项

| 标志 | 描述 |
|------|------|
| `--json` | 输出原始 JSON 响应 |
| `--threads`, `-t` | 在列出评论时内联展开线程回复 |
| `--subtasks` | 获取任务详细信息时包含子任务 |
| `--me` | 过滤到分配给我的任务（用于任务命令） |
| `--content`, `-c` | 内联内容字符串（仅限短文本）。 |
| `--file`, `-f` | 从文件路径读取内容。**对于任何超过一句话的内容，首选。** |
| `--cleanup` | 成功执行后删除 `--file` |
| `--name`, `-n` | 编辑页面时的新页面名称 |
| `--parent`, `-p` | 创建页面时的父页面 ID（创建为子页面） |
| `--space`, `-s` | 创建文档时的空间 ID（将文档放置在该空间中） |
| `--assignee`, `-a` | 任务创建时的分配者 |
| `--due`, `-d` | 任务创建时的截止日期 |
| `--description`, `--desc` | 任务创建时的描述（支持 markdown） |
| `--attach` | 作为附件上传的文件路径（可重复；用于 `attach` 和 `comment` 命令） |
| `--output` | `fetch-image` 的自定义输出路径（默认：临时目录） |
| `--account` | 使用特定命名的帐户（来自 accounts.json） |

## 示例

### 获取任务详细信息

```bash
# 使用完整 URL
node query.mjs get "https://app.clickup.com/t/86a1b2c3d"

# 直接使用任务 ID
node query.mjs get 86a1b2c3d

# 包含子任务
node query.mjs get 86a1b2c3d --subtasks
```

### 创建任务

```bash
# 使用显式的 list ID
node query.mjs create 901111220963 "新功能：深色模式"

# 使用默认列表（如果设置了 CLICKUP_DEFAULT_LIST_ID）
node query.mjs create "快速任务"
```

### 列出我的任务

```bash
# 工作区中分配给您的所有任务
node query.mjs my-tasks
```

### 搜索任务

ClickUp 的 v2 API 没有跨任务的本地文本搜索，因此 `search` 需要一个**范围**以使工作区遍历保持有界。选择适合的范围：

```bash
# 范围到特定列表（最快，推荐）
node query.mjs search "authentication" --list 901111220963

# 分配给您的所有任务具有特定状态
node query.mjs search --me --status "in progress"

# 范围到文件夹（"项目"）——扫描该文件夹中的每个列表
node query.mjs search "oauth" --folder 90111122009

# 通过分配者 + 文本过滤
node query.mjs search "migration" --assignee justin

# 多个状态（逗号分隔）
node query.mjs search --me --status "in progress,review"

# 无范围的全工作区扫描——慢，获取每个任务。谨慎使用。
node query.mjs search "dark mode" --all
```

如果没有范围标志（并且没有 `--all`），`search` 将以有用的错误退出，而不是默默地猛击 API。

### 通过名称查找列表或文件夹

当您有一个列表名称（"Red Launch"、"Triage"、"Sprint 12"）但没有 ID 时，使用 `find-list`——它仅使用元数据端点遍历工作区结构（空间 → 文件夹 → 列表）。快速，无需获取任务。

```bash
node query.mjs find-list "Red Launch"
node query.mjs find-list "triage" --json
```

匹配排名：精确 > 以...开头 > 包含，不区分大小写。返回列表匹配和嵌套在文件夹中的列表（文件夹），所以如果您命名的东西是文件夹，您仍然可以看到您可能想要的列表。

### 更新任务状态

```bash
# 列出任务的可用状态
node query.mjs status 86a1b2c3d

# 更新状态（不区分大小写，部分匹配）
node query.mjs status 86a1b2c3d "in progress"
node query.mjs status 86a1b2c3d "complete"
```

### 分配任务

```bash
# 通过用户名分配
node query.mjs assign 86a1b2c3d justin

# 通过电子邮件分配
node query.mjs assign 86a1b2c3d jane@example.com
```

### 设置截止日期

```bash
node query.mjs due 86a1b2c3d "tomorrow"
node query.mjs due 86a1b2c3d "next friday"
node query.mjs due 86a1b2c3d "+3d"
node query.mjs due 86a1b2c3d "2024-01-15"
```

### 设置优先级

```bash
node query.mjs priority 86a1b2c3d urgent
node query.mjs priority 86a1b2c3d high
node query.mjs priority 86a1b2c3d none  # 清除优先级
```

### 创建子任务

```bash
node query.mjs subtask 86a1b2c3d "编写单元测试"
node query.mjs subtask 86a1b2c3d "更新文档"
```

### 重新分配现有任务

`subtask` 创建新任务。`parent` 将已存在的任务作为另一个任务的子任务：

```bash
node query.mjs parent 86a1b2c3d 86a9z8y7x   # 86a1b2c3d 成为 86a9z8y7x 的子任务
```

它拒绝将任务设置为它自己的父级，拒绝将任务移动到它自己的任何后代下，并报告从服务器读取的父级，而不是您请求的父级。

在使用它之前需要了解两件事：

- **没有分离。** ClickUp 的 UpdateTask 文档："您不能通过将 `parent` 设置为 `null` 将子任务转换为任务。" 取消重新分配需要 ClickUp UI。
- **跨列表重新分配将任务移动到父级所在的列表中。** 将任务从 "Agent Follow-ups" 下移到 "Synced Team" 中的父级，将任务移动到 "Synced Team"；当发生这种情况时，命令将打印 `List moved: ... -> ...`。

### 里程碑

```bash
node query.mjs milestone 86a1b2c3d on    # 标记为里程碑
node query.mjs milestone 86a1b2c3d off   # 恢复为普通任务
```

里程碑是一个任务 *类型*，而不是一个状态。类型 ID 是按工作区区分的，因此它通过名称解析，而不是硬编码。与重新分配不同，这是可逆的。

模式是必需的。`milestone <task>` 没有 `on`/`off` 是一个错误，而不是默认值，因为默认值会导致像是一个问题的命令的写入。

### 移动任务

```bash
node query.mjs move 86a1b2c3d 901111220964
```

### 添加链接

```bash
# 添加带描述的链接
node query.mjs link 86a1b2c3d "https://github.com/..." "PR #123"

# 添加不带描述的链接
node query.mjs link 86a1b2c3d "https://docs.example.com/guide"
```

### 添加清单项目

```bash
node query.mjs checklist 86a1b2c3d "审查代码"
node query.mjs checklist 86a1b2c3d "运行测试"
node query.mjs checklist 86a1b2c3d "部署到预发布环境"
```

### 列出列表中的任务

```bash
# 列表中的所有任务
node query.mjs tasks 901111220963

# 仅分配给我的任务
node query.mjs tasks 901111220963 --me
```

### 查看评论

```bash
node query.mjs comments "https://app.clickup.com/t/86a1b2c3d"

# 内联展开所有线程回复
node query.mjs comments 86a1b2c3d --threads

# 查看特定评论线程的回复
node query.mjs thread 90110200841741

# 回复特定评论线程
node query.mjs reply 90110200841741 "听起来不错，我会处理的。"
```

### 发布评论

```bash
node query.mjs comment 86a1b2c3d "开始处理这个任务"

# 多行评论
node query.mjs comment 86a1b2c3d "状态更新：
- 完成初步审查
- 发现 3 个问题需要解决
- 将在下班前提交 PR"
```

### 在评论中 @提及用户

该技能支持两种提及语法：

1. **显式（首选）**：`@[identifier]` — 带括号的语法，通过名称、电子邮件或用户 ID 模糊匹配
2. **裸（自动检测）**：`@Name` 或 `@First Last` — 自动匹配工作区成员

裸提及是**后备**，这样即使代理忘记括号语法，提及也能工作。两者都产生相同的 ClickUp 提及属性。

```bash
# 显式括号语法（首选）
node query.mjs comment 86a1b2c3d "嘿 @[justin]，你能审查这个吗?"

# 裸提及（自动检测工作区成员）
node query.mjs comment 86a1b2c3d "嘿 @Justin Maier，你能审查这个吗?"

# 两者都相同——这些是等效的：
node query.mjs comment 86a1b2c3d "@[justin] 请审查"
node query.mjs comment 86a1b2c3d "@Justin 请审查"

# 通过数字用户 ID 提及（仅限括号语法）
node query.mjs comment 86a1b2c3d "@[10620972] 请查看"

# 通过电子邮件提及（仅限括号语法）
node query.mjs comment 86a1b2c3d "分配给 @[jane@example.com]"

# 一个评论中包含多个提及
node query.mjs comment 86a1b2c3d "@[justin] 和 @[koen] - 需要你们的意见"
```

**括号语法**：模糊匹配部分名称、电子邮件或数字 ID。`@[justin]` 匹配 "Justin Maier"。未知用户会报错。

**裸语法**：匹配 `@Name` 对工作区成员用户名（不区分大小写）。首先尝试全名 (`@Justin Maier`), 然后尝试名 (`@Justin`)。未匹配的裸提及将保留为纯文本（不报错）。

### 显示当前用户

```bash
node query.mjs me
```

### 删除评论

```bash
# 从评论命令中获取评论 ID（显示在 --json 输出中）
node query.mjs delete-comment 90110200841741
```

### 添加/删除观察者

```bash
# 将用户添加为任务的观察者/关注者
node query.mjs watch 86a1b2c3d koen

# 移除观察者
node query.mjs unwatch 86a1b2c3d koen
```

### 添加标签

```bash
# 向任务添加标签
node query.mjs tag 86a1b2c3d "DevOps"
node query.mjs tag 86a1b2c3d "bug"
```

### 更新描述

```bash
# 使用 markdown 更新任务描述
node query.mjs description 86a1b2c3d "## 摘要
这是一个 **粗体** 声明。

- 项目 1
- 项目 2

更多信息请参考 [文档](https://example.com)。
```

### 归档/恢复任务

```bash
# 归档任务（从活动视图中删除）
node query.mjs archive 86a1b2c3d

# 恢复归档任务
node query.mjs unarchive 86a1b2c3d
```

### 声明任务（会话链接）

当您开始处理 ClickUp 任务时，**立即声明它**，以便您的会话可以在以后恢复。这将向任务的 "Session ID" 自定义字段写入您的 Claude Code 会话 ID，允许从您离开的地方继续工作。

```bash
# 开始处理任务后立即声明任务
node query.mjs claim 86a1b2c3d

# 使用 URL 也一样
node query.mjs claim "https://app.clickup.com/t/86a1b2c3d"
```

**要求**：
- 任务的列表必须有一个文本自定义字段，其中包含 "Session"（例如，"Session ID"）
- 会话 ID 解析顺序：`$CLAUDE_SESSION_ID` → 最近修改的 `~/.claude/projects/*/*.jsonl`（在 60 秒内）。后备处理不暴露环境变量的 harness。

**何时声明**：开始处理 ClickUp 任务时。这是我们以后如果需要继续处理同一个任务，如何从您离开的地方继续工作的方式。

### 获取列表详细信息

```bash
# 获取包括状态的列表信息
node query.mjs list 901111220963
```

### 创建列表

```bash
# 使用空间 ID 创建列表
node query.mjs create-list 20128955 "新列表"

# 使用空间 URL 创建列表
node query.mjs create-list "https://app.clickup.com/8459928/v/s/20128955" "Sprint Backlog"

# 创建带描述的列表
node query.mjs create-list 20128955 "Bug Tracker" --content "在此处跟踪所有错误"
```

### 删除列表

```bash
node query.mjs delete-list 901111220963
```

### 列出/搜索文档

```bash
# 列出工作区中的所有文档
node query.mjs docs

# 通过名称搜索文档
node query.mjs docs "API"
```

### 获取文档详细信息

```bash
# 获取文档详细信息和页面列表
node query.mjs doc abc123def

# 使用文档 URL
node query.mjs doc "https://app.clickup.com/12345/v/dc/abc123def"
```

### 创建文档

```bash
# 创建空文档
node query.mjs create-doc "项目笔记"

# 创建带初始内容的文档（填充第一个页面）
node query.mjs create-doc "API 文档" --content "# API 文档

此文档涵盖了 API 端点和用法。

## Overview
..."
```

### 获取页面内容

```bash
# 获取特定页面的内容
node query.mjs page abc123def page456
```

### 创建页面

```bash
# 仅带标题创建页面
node query.mjs create-page abc123def "新部分"

# 创建带内容的页面
node query.mjs create-page abc123def "入门指南" --content "# 欢迎使用

这是入门指南。

## 编辑页面

```bash
# 更新页面内容
node query.mjs edit-page abc123def page456 --content "在此处更新内容"

# 重命名页面
node query.mjs edit-page abc123def page456 --name "新页面名称"

# 更新内容和名称
node query.mjs edit-page abc123def page456 --content "新内容" --name "新名称"
```

### 上传附件

```bash
# 将单个文件上传到任务
node query.mjs attach 86a1b2c3d --attach ./screenshot.png

# 上传多个文件
node query.mjs attach 86a1b2c3d --attach ./screenshot1.png --attach ./report.pdf

# 先发布评论，然后上传文件附件
node query.mjs comment 86a1b2c3d "这里有一些截图" --attach ./screenshot.png

# 带多个附件的评论
node query.mjs comment 86a1b2c3d "设计审查资源" --attach ./mockup.png --attach ./spec.pdf
```

**支持的文件类型**：图像（PNG、JPG、GIF、WebP、SVG）、文档（PDF、DOCX、XLSX）、存档（ZIP），以及 ClickUp 接受的任何其他文件类型。

**注意**：ClickUp API 将文件附加到任务本身（在任务的附件列表中可见）。当使用 `--attach` 与 `comment` 命令一起使用时，评论首先发布，然后文件上传为任务的附件。它们出现在任务中，但不会内联嵌入在评论文本中。

### 在评论中查看附件

包含图像或文件附件的评论在纯文本输出中内联显示它们：

```
[Feb 11, 2026, 04:55 PM] Justin Maier (id: 90110209630450):
  [附件: image.png](https://t8459928.p.clickup-attachments.com/...)
  如果您查看组件，您会看到...
```

要查看实际图像，请使用 `fetch-image` 将其下载到本地临时文件：

```bash
# 从评论输出中显示的 URL 下载附件
node query.mjs fetch-image "https://t8459928.p.clickup-attachments.com/t8459928/.../image.png"
# → 下载：/tmp/clickup-attachments/image.png

# 保存到特定路径
node query.mjs fetch-image "https://..." --output ./screenshot.png
```

下载后，使用您的文件查看器或 `Read` 工具查看图像。

## 基于文件的 内容（推荐）

对于任何超过一句话的内容，**首先将内容写入临时 markdown 文件**，然后使用 `--file` 而不是 `--content`。这避免了 shell 转义问题，并支持正确的多行 markdown。

### 工作流程

1. 将您的内容写入临时 markdown 文件
2. 使用 `--file path/to/file.md`
3. 可选地添加 `--cleanup` 以在成功后自动删除文件

### 示例

```bash
# 从准备好的 markdown 文件创建文档
node query.mjs create-doc "架构规范" --file ./docs/spec.md --space 90114072520

# 从文件更新页面，然后自动删除临时文件
node query.mjs edit-page abc123 page456 --file /tmp/updated-content.md --cleanup

# 从文件发布详细评论
node query.mjs comment 86a1b2c3d --file ./review-notes.md

# 从文件设置任务描述
node query.mjs description 86a1b2c3d --file ./task-brief.md
```

### 使用哪种方式

| 方法 | 使用场景 |
|------|----------|
| `--content "short text"` | 一行，简单状态更新 |
| `--file path.md` | 多行内容，带格式的 markdown，规范，文档 |
| `--file path.md --cleanup` | 临时内容（代理写入文件，推送到 ClickUp，删除文件） |

`--file` 可用于：`create-doc`, `create-page`, `edit-page`, `comment`, `description`, `create-list`, `update-list`

## 任务/列表/空间/文档 URL 格式

该技能识别以下 ClickUp URL 格式：

**任务**：
- `https://app.clickup.com/t/{task_id}`
- `https://app.clickup.com/{team_id}/v/li/{list_id}?p={task_id}`
- 自定义任务 ID：`#DEV-123` 或 `DEV-123`
- 直接任务 ID：`86a1b2c3d`

**列表**：
- `https://app.clickup.com/{team_id}/v/li/{list_id}`
- 直接列表 ID：`901111220963`

**空间**：
- `https://app.clickup.com/{team_id}/v/s/{space_id}`
- 直接空间 ID：`20128955`

**文档**：
- `https://app.clickup.com/{team_id}/v/dc/{doc_id}`
- `https://app.clickup.com/{team_id}/docs/{doc_id}`
- 直接文档 ID：`abc123def`
## 使用场景

**任务**：
- **理解上下文**：在开始工作之前获取任务详细信息
- **快速创建任务**：在不离开终端的情况下创建任务
- **每日站立会议**：使用 `my-tasks` 查看您的分配
- **状态更新**：在您工作时发布进度评论
- **任务管理**：分配、设置优先级和设置截止日期
- **协作**：查看任务上的最新评论以获取上下文，添加观察者
- **任务组织**：添加标签对任务进行分类
- **任务链接**：在提交消息中引用任务 ID
- **会话跟踪**：使用 `claim` 声明任务，以便稍后可以继续进行

**文档**：
- **文档**：创建和维护项目文档
- **知识库**：构建参考指南和维基
- **会议记录**：存储会议记录和决定
- **规范**：编写和更新技术规范
- **快速编辑**：在不离开终端的情况下更新文档内容
- **文档协作**：查看和回复文档评论以进行内联审阅

## 评论线程最佳实践

在回复任务讨论时，**始终首先检查线程上下文**：

1. **在发布评论之前**，运行 `comments <task> --threads` 以查看现有的对话。
2. **如果用户的消息或上下文引用了特定的评论线程**（例如，他们回复了线程，或者您正在继续先前的对话），请使用 `reply <comment_id> "text"` 在该线程中发布——**不要** `comment <task> "text"`.
3. **仅使用 `comment**`（顶级）**对于不属于现有线程的新主题**。
4. **经验法则**：如果您之前发布了一个评论，并且有人回复了它在一个线程中，则您的下一个回复应使用 `reply` 位于该相同的线程中。

## 提示

- 团队 ID、用户 ID 和其他字段在 `accounts.json` 中自动缓存
- 在您的帐户中设置 `defaultListId` 以跳过创建任务时 list_id
- 使用 `my-tasks` 快速查看您的分配情况
- 使用自然语言日期："明天"、"下周五"、"+3d"
- 发布评论以保持利益相关者了解进度
- 在提交消息中包含任务 ID 以便可追溯
- 使用 `--json` 进行脚本或将其传递到其他工具
- 文档内容使用 markdown 格式进行输入和输出
- 文档 API 使用 v3 端点（基于工作区而不是基于团队）
- 支持自定义任务 ID：`#DEV-123` 或 `DEV-123`
- 所有任务/评论查询自动分页（无需手动处理分页）
- 自动处理速率限制，使用重试和回退


## 参考

不太常见的材料位于 [reference.md](reference.md) 中——当您需要时阅读它：

- **输出格式**——任务、列表、评论、文档、页面的示例输出形状
- **技术说明**——每个功能的 markdown 处理、@提及解析、文档页面结构、分页
- **测试**——冒烟测试套件
- **Webhook 观察者**——通过 webhook.site + `listen.mjs` 进行实时事件监控
- **任务观察者（轮询）**——无依赖的单个任务/列表观察者 via `watch.mjs`
- **批量任务创建**——`batch-create` JSON 计划模式 schema 和依赖连接
- **团队工作流模式**——领导/工人/QA/文档保管者和阶段门模式
