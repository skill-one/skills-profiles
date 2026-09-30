---
name: github-issues
description: 使用MCP工具创建、更新和管理GitHub问题。当用户需要创建错误报告、功能请求或任务问题时，更新现有问题，添加标签/指派者/里程碑，管理仓库标签，设置问题字段（日期、优先级、自定义字段），设置问题类型，管理问题工作流，链接问题，添加依赖关系，或跟踪被阻塞/阻塞关系，请使用此技能。在请求如“创建问题”、“提交错误”、“请求功能”、“更新问题X”、“设置优先级”、“设置开始日期”、“创建标签”、“重命名标签”、“列出仓库标签”、“链接问题”、“添加依赖关系”、“被阻塞”、“阻塞”，或任何GitHub问题管理任务时触发。
---

# GitHub 问题

使用 `@modelcontextprotocol/server-github` MCP 服务器管理 GitHub 问题。

## 可用工具

### MCP 工具（读取操作）

| 工具 | 目的 |
|------|---------|
| `mcp__github__issue_read` | 读取问题详情、子问题、评论、标签（方法：get、get_comments、get_sub_issues、get_labels） |
| `mcp__github__list_issues` | 按状态、标签、日期列出和筛选仓库问题 |
| `mcp__github__search_issues` | 使用 GitHub 搜索语法跨仓库搜索问题 |
| `mcp__github__projects_list` | 列出项目、项目字段、项目项、状态更新 |
| `mcp__github__projects_get` | 获取项目、字段、项或状态更新的详情 |
| `mcp__github__projects_write` | 添加/更新/删除项目项，创建状态更新 |

### MCP 工具（写入操作）

| 工具 | 目的 |
|------|---------|
| `mcp__github__issue_write` | 创建或更新问题（方法：create、update）。支持标题、正文、类型、标签、指派者、里程碑和问题字段 |
| `mcp__github__add_issue_comment` | 添加评论或对问题进行反应 |
| `mcp__github__sub_issue_write` | 添加、删除或重新排序子问题 |

### CLI / REST API（写入操作）

`gh api` 执行相同的写入操作，并是下面示例中使用的形式。当 MCP 服务器未连接时，或需要 MCP 工具未暴露的 REST 字段时，请使用它。

| 操作 | 命令 |
|-----------|---------|
| 创建问题 | `gh api repos/{owner}/{repo}/issues -X POST -f title=... -f body=...` |
| 更新问题 | `gh api repos/{owner}/{repo}/issues/{number} -X PATCH -f title=... -f state=...` |
| 添加评论 | `gh api repos/{owner}/{repo}/issues/{number}/comments -X POST -f body=...` |
| 关闭问题 | `gh api repos/{owner}/{repo}/issues/{number} -X PATCH -f state=closed` |
| 设置问题类型 | 在创建调用中包含 `-f type=Bug`（仅限 REST API，`gh issue create` CLI 不支持） |

**注意：** `gh issue create` 适用于基本问题创建，但**不支持** `--type` 标志。当需要设置问题类型时，请使用 `gh api`。

## 工作流程

1. **确定操作**：创建、更新或查询？
2. **收集上下文**：获取仓库信息，如果需要，获取现有标签、里程碑
3. **结构化内容**：使用来自 [references/templates.md](references/templates.md) 的适当模板
4. **执行**：使用 MCP 工具进行读取，使用 `gh api` 进行写入
5. **确认**：向用户报告问题 URL

## 创建问题

使用 `gh api` 创建问题。这支持所有参数，包括问题类型。

```bash
gh api repos/{owner}/{repo}/issues \
  -X POST \
  -f title="问题标题" \
  -f body="使用 markdown 编写的问题正文" \
  -f type="Bug" \
  --jq '{number, html_url}'
```

### 可选参数

将以下标志添加到 `gh api` 调用中：

```
-f type="Bug"                    # 问题类型（Bug、Feature、Task、Epic 等）
-f 'labels[]=bug'                # 标签（可重复多个）
-f 'assignees[]=username'        # 指派者（可重复多个）
-f milestone=1                   # 里程碑编号
```

**将整个 `name[]=value` 对引号括起来。** `[]` 是 zsh（macOS 的默认 shell）中的通配符，因此未引用的 `-f labels[]=bug` 不会到达 `gh`：

```
zsh: no matches found: labels[]=bug
```

**问题类型** 是组织级别的元数据。要发现可用类型，请使用：
```bash
gh api graphql -f query='{ organization(login: "ORG") { issueTypes(first: 10) { nodes { name } } } }' --jq '.data.organization.issueTypes.nodes[].name'
```

**优先使用问题类型而不是标签进行分类。** 当问题类型可用时（例如 Bug、Feature、Task），请使用 `type` 参数而不是应用等效标签，如 `bug` 或 `enhancement`。问题类型是 GitHub 上对问题进行分类的规范方式。只有在组织未配置问题类型时，才应回退到标签。

### 标题指南

- 具体且可操作
- 保持在 72 个字符以内
- 当问题类型设置时，不要添加冗余的前缀，如 `[Bug]`
- 示例：
  - `启用 SSO 时登录失败`（类型=Bug）
  - `添加暗黑模式支持`（类型=Feature）
  - `为 auth 模块添加单元测试`（类型=Task）

### 正文结构

始终使用 [references/templates.md](references/templates.md) 中的模板。根据问题类型选择：

| 用户请求 | 模板 |
|--------------|----------|
| Bug、错误、损坏、无法工作 | Bug 报告 |
| Feature、增强、添加、新 | 功能请求 |
| Task、杂项、重构、更新 | 任务 |

## 更新问题

使用 `gh api` 与 PATCH：

```bash
gh api repos/{owner}/{repo}/issues/{number} \
  -X PATCH \
  -f state=closed \
  -f title="更新后的标题" \
  --jq '{number, html_url}'
```

仅包含您要更改的字段。可用字段：`title`、`body`、`state`（open/closed）、`labels`、`assignees`、`milestone`。

## 示例

### 示例 1：Bug 报告

**用户**： "创建一个 Bug 问题 - 使用 SSO 时登录页面崩溃"

**操作**： 
```bash
gh api repos/github/awesome-copilot/issues \
  -X POST \
  -f title="使用 SSO 时登录页面崩溃" \
  -f type="Bug" \
  -f body="## 描述
使用 SSO 进行身份验证时，登录页面崩溃。

## 复现步骤
1. 导航到登录页面
2. 点击 '使用 SSO 登录'
3. 页面崩溃

## 预期行为
SSO 身份验证应完成并重定向到仪表板。

## 实际行为
页面无响应并显示错误。" \
  --jq '{number, html_url}'
```

### 示例 2：功能请求

**用户**： "创建一个高优先级的功能请求 - 添加暗黑模式"

**操作**：
```bash
gh api repos/github/awesome-copilot/issues \
  -X POST \
  -f title="添加暗黑模式支持" \
  -f type="Feature" \
  -f 'labels[]=high-priority' \
  -f body="## 摘要
为改善用户体验和可访问性添加暗黑模式主题选项。

## 动机
- 减少低光环境下的眼睛疲劳
- 用户越来越期望这一功能

## 提议的解决方案
实现带系统偏好检测的主题切换。

## 接受标准
- [ ] 设置中的切换开关
- [ ] 持久化用户偏好
- [ ] 默认尊重系统偏好" \
  --jq '{number, html_url}'
```

## 常用标签

在适用时使用这些标准标签：

| 标签 | 用于 |
|-------|---------|
| `bug` | 什么功能无法正常工作 |
| `enhancement` | 新功能或改进 |
| `documentation` | 文档更新 |
| `good first issue` | 适合新人 |
| `help wanted` | 需要额外关注 |
| `question` | 需要进一步信息 |
| `wontfix` | 将不会处理 |
| `duplicate` | 已存在 |
| `high-priority` | 紧急问题 |

## 小贴士

- 始终在创建问题前确认仓库上下文
- 缺少关键信息时请请求，而不是猜测
- 当知道相关问题时，请链接相关问题：`Related to #123`
- 更新时，先获取当前问题以保留未更改的字段

## 扩展功能

以下功能需要超出基本 MCP 工具的 REST 或 GraphQL API。每个功能都在自己的参考文件中进行了文档记录，以便代理仅加载它需要的知识。

| 功能 | 使用场景 | 参考 |
|------------|-------------|-----------|
| 高级搜索 | 带布尔逻辑的复杂查询、日期范围、跨仓库搜索、问题字段过滤器（`field.name:value`） | [references/search.md](references/search.md) |
| 子问题和父问题 | 将工作分解为分层任务 | [references/sub-issues.md](references/sub-issues.md) |
| 里程碑 | 创建、读取、更新、关闭、重新打开、删除里程碑和管理里程碑问题 | [references/milestones.md](references/milestones.md) |
| 标签 | 发现、创建、重命名、重新着色和删除仓库标签；在问题上添加或替换标签 | [references/labels.md](references/labels.md) |
| 问题依赖关系 | 跟踪被阻塞/阻塞关系 | [references/dependencies.md](references/dependencies.md) |
| 高级问题类型 | 超出 MCP `list_issue_types` / `type` 参数的 GraphQL 操作 | [references/issue-types.md](references/issue-types.md) |
| 项目 V2 | 项目看板、进度报告、字段管理 | [references/projects.md](references/projects.md) |
| 问题字段 | 自定义元数据：日期、优先级、文本、数字（私人预览） | [references/issue-fields.md](references/issue-fields.md) |
| 问题描述中的图片 | 通过 CLI 在问题描述和评论中嵌入图片 | [references/images.md](references/images.md) |
