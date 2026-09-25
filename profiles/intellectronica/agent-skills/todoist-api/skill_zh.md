# Todoist CLI 技能

此技能提供使用 `td` CLI 工具操作 Todoist 的操作指南。

## 前置条件

必须安装并认证 `td` CLI。使用以下命令验证：

```bash
td auth status
```

如果 td 未安装或未认证：
- **未安装**：提示用户使用 `npm install -g @doist/todoist-cli` 安装
- **未认证**：提示用户运行 `td auth login` 通过 OAuth 进行认证

## 代理的输出格式

对于机器可读的输出，使用以下标志：
- `--json` - 以 JSON 数组格式输出
- `--ndjson` - 以行分隔的 JSON 格式输出（每行一个对象）
- `--full` - 在 JSON 输出中包含所有字段（默认仅显示基本字段）

## 确认要求

**在执行任何破坏性操作前，始终使用 AskUserQuestion 或类似工具询问用户确认。** 一个确认即可满足一个逻辑相关的操作组。

破坏性操作包括：
- 删除任务、项目、分区、标签或评论
- 完成任务
- 更新现有资源
- 归档项目

只读操作不需要确认。

## 快速命令

| 命令 | 描述 |
|------|------|
| `td add "text"` | 使用自然语言解析的快速添加 |
| `td today` | 今天到期和过期的任务 |
| `td upcoming [days]` | 未来 N 天到期的任务（默认：7 天） |
| `td inbox` | 收件箱中的任务 |
| `td completed` | 最近完成的任务 |

### 快速添加示例

```bash
td add "明天买牛奶 p1 #购物"
td add "每周一给牙医打电话 @健康"
td add "审查 PR #工作 /代码审查"
```

快速添加解析器支持：
- 到期日期：`明天`、`下周一`、`1月15日`
- 优先级：`p1`（紧急）到 `p4`（正常）
- 项目：`#项目名称`
- 分区：`/分区名称`
- 标签：`@标签1 @标签2`

## 任务

### 列出任务

```bash
td task list [选项]
```

**过滤器：**
- `--project <name>` - 按项目名称或 id:xxx 过滤
- `--label <name>` - 按标签过滤（多个标签用逗号分隔）
- `--priority <p1-p4>` - 按优先级过滤
- `--due <date>` - 按到期日期过滤（今天、过期或 YYYY-MM-DD）
- `--filter <query>` - 原始 Todoist 过滤查询
- `--assignee <ref>` - 按指派者过滤（me 或 id:xxx）
- `--workspace <name>` - 按工作区过滤
- `--personal` - 仅过滤个人项目

**输出：**
```bash
td task list --json                    # JSON 数组
td task list --project "工作" --json   # 过滤后的 JSON
td task list --all --json              # 所有任务（无限制）
```

### 查看任务详情

```bash
td task view <ref>              # 人类可读格式
td task view <ref> --json       # JSON 输出
```

`ref` 可以是任务名称、部分匹配或 `id:xxx`。

### 创建任务

**快速添加（自然语言）：**
```bash
td add "带有 #项目 @标签 明天 p2 的任务文本"
```

**显式标志：**
```bash
td task add --content "任务文本" \
  --project "工作" \
  --due "明天" \
  --priority p2 \
  --labels "紧急,审查" \
  --description "附加详情"
```

**选项：**
- `--content <text>` - 任务内容（必需）
- `--due <date>` - 到期日期（自然语言或 YYYY-MM-DD）
- `--deadline <date>` - 截止日期（YYYY-MM-DD）
- `--priority <p1-p4>` - 优先级级别
- `--project <name>` - 项目名称或 id:xxx
- `--section <id>` - 分区 ID
- `--labels <a,b>` - 逗号分隔的标签
- `--parent <ref>` - 子任务的父任务
- `--description <text>` - 任务描述
- `--assignee <ref>` - 指派给用户（名称、邮箱、id:xxx 或 "me"）
- `--duration <time>` - 持续时间（例如，30m、1h、2h15m）

### 更新任务

```bash
td task update <ref> --content "新内容" --due "下周"
```

**选项：**
- `--content <text>` - 新内容
- `--due <date>` - 新到期日期
- `--deadline <date>` - 截止日期
- `--no-deadline` - 移除截止日期
- `--priority <p1-p4>` - 新优先级
- `--labels <a,b>` - 替换标签
- `--description <text>` - 新描述
- `--assignee <ref>` - 指派给用户
- `--unassign` - 移除指派者
- `--duration <time>` - 持续时间

### 完成任务

```bash
td task complete <ref>
```

### 重新打开任务

```bash
td task uncomplete id:xxx
```

注意：重新打开需要任务 ID（id:xxx 格式）。

### 删除任务

```bash
td task delete <ref>
```

### 移动任务

```bash
td task move <ref> --project "新项目"
td task move <ref> --section <section-id>
td task move <ref> --parent <task-ref>
```

### 在浏览器中打开

```bash
td task browse <ref>
```

## 项目

### 列出项目

```bash
td project list                     # 人类可读树形结构
td project list --json              # JSON 数组
td project list --personal --json   # 仅个人项目
```

### 查看项目

```bash
td project view <ref>
td project view <ref> --json
```

### 创建项目

```bash
td project create --name "项目名称" \
  --color "blue" \
  --parent "父项目" \
  --view-style board \
  --favorite
```

**选项：**
- `--name <name>` - 项目名称（必需）
- `--color <color>` - 颜色名称
- `--parent <ref>` - 父项目用于嵌套
- `--view-style <style>` - "list" 或 "board"
- `--favorite` - 标记为最爱

### 更新项目

```bash
td project update <ref> --name "新名称" --color "red"
```

### 归档/取消归档项目

```bash
td project archive <ref>
td project unarchive <ref>
```

### 删除项目

```bash
td project delete <ref>
```

注意：项目必须没有未完成的任务。

### 列出协作者

```bash
td project collaborators <ref>
```

## 分区

### 列出分区

```bash
td section list <project>           # 人类可读格式
td section list <project> --json    # JSON 数组
```

### 创建分区

```bash
td section create --name "分区名称" --project "项目名称"
```

### 更新分区

```bash
td section update <id> --name "新名称"
```

### 删除分区

```bash
td section delete <id>
```

## 标签

### 列出标签

```bash
td label list              # 人类可读格式
td label list --json       # JSON 数组
```

### 创建标签

```bash
td label create --name "标签名称" --color "绿色" --favorite
```

### 更新标签

```bash
td label update <ref> --name "新名称" --color "蓝色"
```

### 删除标签

```bash
td label delete <name>
```

## 评论

### 列出评论

```bash
td comment list <task-ref>                    # 任务上的评论
td comment list <project-ref> --project       # 项目上的评论
```

### 添加评论

```bash
td comment add <task-ref> --content "评论文本"
td comment add <project-ref> --project --content "评论文本"
```

### 更新评论

```bash
td comment update <id> --content "更新文本"
```

### 删除评论

```bash
td comment delete <id>
```

## 提醒

### 列出提醒

```bash
td reminder list <task-ref>
```

### 添加提醒

```bash
td reminder add <task-ref> --due "明天 9 点"
```

### 删除提醒

```bash
td reminder delete <id>
```

## 过滤器

### 列出保存的过滤器

```bash
td filter list --json
```

### 显示匹配过滤器的任务

```bash
td filter show <filter-ref> --json
```

### 创建过滤器

```bash
td filter create --name "我的过滤器" --query "今天 & p1"
```

## 已完成任务

```bash
td completed                              # 今天的已完成任务
td completed --since 2024-01-01           # 自特定日期以来
td completed --project "工作" --json      # 过滤后的 JSON 输出
td completed --all --json                 # 所有已完成（无限制）
```

**选项：**
- `--since <date>` - 开始日期（YYYY-MM-DD），默认：今天
- `--until <date>` - 结束日期（YYYY-MM-DD），默认：明天
- `--project <name>` - 按项目过滤

## 活动和统计

```bash
td activity                  # 最近活动
td stats                     # 生产力统计和 karma
```

## 分页

对于大量结果集，使用 `--all` 获取所有内容，或使用游标处理分页：

```bash
# 第一页
result=$(td task list --json --limit 50)

# 如果响应中有 next_cursor，继续
cursor=$(echo "$result" | jq -r '.[-1].id // empty')
td task list --json --limit 50 --cursor "$cursor"
```

## 引用解析

命令中的 `<ref>` 参数接受：
- 任务/项目/标签名称（支持部分匹配）
- `id:xxx` 用于精确 ID 匹配
- 数字 ID（解释为 id:xxx）

## 其他参考

有关特定主题的详细信息，请参阅：
- `references/completed-tasks.md` - 通过 API 查询已完成任务历史的替代方法
- `references/filters.md` - Todoist 过滤查询语法 `--filter` 标志

## 工作流总结

1. **验证认证** - `td auth status`
2. **读取操作** - 直接执行，无需确认
3. **写入操作** - 执行前请求确认
4. **使用 JSON 输出** - 添加 `--json` 标志以获取机器可读数据
5. **处理大数据集** - 使用 `--all` 或使用 `--cursor` 进行分页
