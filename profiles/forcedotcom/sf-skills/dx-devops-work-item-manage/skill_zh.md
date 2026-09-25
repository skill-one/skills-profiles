# DevOps Center 工作项管理

管理 DevOps Center 中的完整工作项生命周期——从创建到状态转换再到推广就绪。提供无头 CLI 驱动的操作，用于自主发布工作流。

## 范围

- **在范围内**：列出工作项、创建新工作项、将更改提交到工作项分支、更新工作项字段（主题、描述、状态）、转换工作项状态（新建 → 进行中 → 准备推广）、为工作项分支创建拉取请求
- **超出范围**：推广/部署、冲突检测、管道或项目管理（单独的技能）

---

## 必需输入

在进行之前收集或推断：

- **操作类型**：list、create、update、commit 或 create-review
- **对于 list**：项目 ID（必需）——如果未提供，则通过 `sf devops project list --json` 获取
- **对于 create**：项目 ID（必需）、主题（必需）、描述（可选）
- **对于 commit**：工作项名称或 ID（必需）以检索分支名称、要提交的文件、提交信息
- **对于 update**：工作项名称（例如，WI-000001）或工作项 ID（必需）、要更新的字段（主题、描述、状态）
- **对于 create-review**：工作项名称（例如，WI-000001）或工作项 ID（必需）

默认值（除非指定）：
- 输出格式：`--json` 用于无头消费
- 工作项标识符：当两者都可用时，优先使用 `--work-item-name`（WI-000001）而不是 `--work-item-id`（名称更易于人类阅读）

如果用户提供清晰的请求（"列出 Project Alpha 的工作项"、"创建修复登录错误的工作项"、"将 WI-12345 移至进行中"、"为 WI-12345 创建 PR"），请立即执行，无需不必要的提问。

---

## 工作流

所有操作都使用 `sf devops work-item` CLI 命令并使用 `--json` 输出进行结构化消费。

### 第一阶段 — 确定操作

1. **根据用户意图确定操作类型**：
   - 关键词如 "list"、"show"、"find" → list 操作
   - 关键词如 "create"、"new"、"add" → create 操作
   - 关键词如 "commit"、"push"、"save changes"、"git commit" → commit 操作
   - 关键词如 "update"、"change"、"modify"、"edit"、"move"、"transition"、"advance"、"mark as" → update 操作
   - 关键词如 "create PR"、"pull request"、"code review"、"review"、"open PR" → create-review 操作

### 第二阶段 — 执行操作

2. **在执行任何操作之前验证 org 认证**：
   ```bash
   sf org display --json
   ```
   - 如果没有设置默认 org 或认证已过期，指示用户运行：
     ```bash
     sf org login web --set-default --alias <alias>
     ```
   - 通过尝试列出项目来验证已认证的 org 已启用 DevOps Center
   - 如果用户想要针对特定 org，在所有后续命令中使用 `--target-org <alias>`

3. **列出工作项**——当用户想要查看现有工作项时：
   ```bash
   sf devops work-item list --project-id <project-id> --json
   ```
   - `--project-id` 是必需的——如果用户提供项目名称而不是 ID，首先运行 `sf devops project list --json` 将名称解析为 ID
   - 验证命令返回状态 0（成功）
   - 解析 JSON 输出：工作项位于 `.result[]` 数组中
   - 每个工作项具有：`name`（例如，WI-000001）、`subject`、`branch`、`environment`、`status`、`description`
   - 以可读格式显示工作项名称、主题、状态、分支和环境
   - 如果 `.result[]` 是空数组，确认 "在项目 <project-name> 中未找到工作项。"
   - 如果用户请求按状态过滤（例如，"显示准备推广状态的工作项"），运行：
     ```bash
     sf devops work-item list --project-id <id> --json | jq '.result[] | select(.status == "<requested-status>")'
     ```
     然后显示匹配的工作项

4. **创建工作项**——当用户想要创建新工作项时：
   ```bash
   sf devops work-item create \
     --project-id <project-id> \
     --subject "<subject>" \
     --description "<description>" \
     --json
   ```
   - `--project-id` 是必需的（从用户处获取或通过 `sf devops project list --json` 获取）
   - `--subject` 是必需的（面向用户的标题）
   - `--description` 是可选的（如果省略，则默认为空白）
   - 从 JSON 输出中捕获返回的工作项名称（例如，WI-000001）、分支名称和环境，以供后续操作使用
   - 等幂性：如果用户尝试创建重复项（相同的主题 + 项目），请先通过列表检查，然后返回现有工作项

5. **执行 commit 操作**——当操作类型为 commit 时：
   - DevOps Center 为每个工作项创建一个专用的特性分支（在创建操作中返回）
   - 用户必须将更改提交并推送到此分支，然后才能转换状态或创建 PR
   - 标准的 git 工作流：
     ```bash
     git checkout <branch-name>
     git add <files>
     git commit -m "<commit-message>"
     git push origin <branch-name>
     ```
   - 分支名称可从工作项的 `branch` 字段获取（通过列表或创建操作检索）
   - 在工作项可以标记为 "准备推广" 或在创建 PR 之前，必须提交更改

6. **更新工作项**——当用户想要更改主题、描述或状态时：
   ```bash
   sf devops work-item update \
     --work-item-name <WI-name> \
     --subject "<new-subject>" \
     --description "<new-description>" \
     --status "<In Progress|Ready to Promote>" \
     --json
   ```
   - 工作项标识符是必需的：使用 `--work-item-name <WI-000001>`（首选）或 `--work-item-id <id>`
   - 如果用户通过主题而不是名称提供工作项，首先将其解析为名称：
     ```bash
     sf devops work-item list --project-id <id> --json | jq -r '.result[] | select(.subject == "<user-provided-subject>") | .name'
     ```
     然后将返回的名称（例如，WI-000001）传递给更新命令
   - 至少必须提供 `--subject`、`--description` 或 `--status` 中的一个
   - 有效状态值："In Progress" 或 "Ready to Promote"（带空格的精确字符串）
   - 仅包含正在更新的字段的标志（省略未更改的字段）
   - 验证命令返回状态 0（成功）
   - 解析 JSON 响应：`.result.name`、`.result.subject`、`.result.status` 包含更新后的值
   - **对于状态转换特定情况**：命令完成后，通过检查 JSON 响应中的 `.result.status` 明确确认状态转换。如果更新响应中缺少状态字段，请重新运行 `sf devops work-item list` 并过滤以验证状态是否持久化

7. **创建拉取请求**——当用户想要创建代码审查的 PR 时：
   ```bash
   sf devops review create \
     --work-item-name <WI-name> \
     --json
   ```
   - 工作项标识符是必需的：使用 `--work-item-name <WI-000001>`（首选）或 `--work-item-id <id>`
   - 如果用户通过主题而不是名称提供工作项，首先将其解析为名称：
     ```bash
     sf devops work-item list --project-id <id> --json | jq -r '.result[] | select(.subject == "<user-provided-subject>") | .name'
     ```
     然后将返回的名称（例如，WI-000001）传递给 review create 命令
   - 通过 DevOps Center API 使用存储在 org 中的 VCS 凭据创建 PR
   - 无需本地 VCS 认证——DevOps Center 处理 GitHub/Bitbucket 认证
   - 支持 GitHub 和 Bitbucket
   - 验证命令返回状态 0（成功）
   - 解析 JSON 响应：`.result.pullRequestUrl` 包含 PR URL，`.result.status` 包含 PR 状态（新创建的 PR 通常为 "open"），`.result.number` 包含 PR 编号
   - 如果命令因 VCS 凭据错误而失败，指示用户在 DevOps Center org 中配置 VCS 凭据（设置 → DevOps Center → VCS 凭据）
   - 如果命令因 "PR 已存在" 错误而失败，报告此工作项已存在 PR（等幂性操作）

### 第三阶段 — 验证和报告

8. **验证操作成功**：
   - **对于 list**：确认 CLI 返回状态 0，解析 JSON `.result[]` 数组，并验证它是否包含工作项（如果没有匹配项则为空）。如果用户通过名称指定项目，请确认解析的项目 ID 是否匹配。
   - **对于 create**：验证 CLI 返回状态 0，并且 JSON 输出包含 `.result.name`（工作项 ID，如 WI-000001）、`.result.branch`（分支名称）和 `.result.environment` 字段。
   - **对于 commit**：验证每个 git 命令返回退出代码 0。如果 `git push` 成功，则提交将保存到工作项分支。
   - **对于 update（一般字段）**：验证 CLI 返回状态 0，并比较返回的 JSON 字段与用户请求的更改。如果更新主题，请确认 `.result.subject` 匹配新值。
   - **对于 update（状态转换）**：验证 CLI 返回状态 0，然后**明确确认状态转换**，通过检查 JSON 响应中的 `.result.status` 是否匹配目标状态（例如，"准备推广"）。如果响应不包含状态字段，请重新运行 `sf devops work-item list` 并过滤以验证状态是否持久化。
   - **对于 create-review**：验证 CLI 返回状态 0，并且 JSON 输出包含 `.result.pullRequestUrl`（PR URL）和 `.result.status`（应为 "open" 或等效）。如果 VCS 凭据缺失，CLI 返回错误——向用户显示此错误。

9. **报告结果**：
   - **List**：以可读格式显示工作项名称、主题、状态、分支和环境。如果请求按状态过滤，则仅显示匹配的工作项。
   - **Create**：返回工作项名称（例如，WI-000001）、分支名称、环境，并确认 "工作项创建成功。"
   - **Commit**：确认已暂存的文件、提交 SHA（来自 git 输出），以及 "更改已提交并推送到分支 <branch-name>。"
   - **Update（一般）**：确认更改的字段及其旧/新值（例如，"主题从 'X' 更新为 'Y'。"）
   - **状态转换**：明确说明转换，例如 "状态更新：进行中 → 准备推广。"
   - **Create-review**：返回 PR URL 并确认 "拉取请求创建成功。状态：open。URL：<url>"

---

## 规则 / 限制

| 限制 | 理由 |
|-----------|-----------|
| 所有 sf devops 命令必须使用 `--json` 标志 | 结构化输出是必需的，用于无头消费；人类可读输出不可靠，无法解析 |
| 提交、更新和 create-review 需要工作项标识符 | 使用 `--work-item-name`（首选）或 `--work-item-id`；从列表或先前的 create 获取 |
| 列出和创建需要项目 ID | 所有工作项都属于一个项目；如果未提供，请运行 `sf devops project list --json` |
| 至少需要更新一个字段 | 如果未提供 `--subject`、`--description` 或 `--status` 标志，更新命令将失败 |
| 状态值必须是精确字符串 | "In Progress" 和 "Ready to Promote"（带空格，正确的大小写）；其他值将失败 |
| 等幂性 create 操作 | 在创建重复项（相同的主题 + 项目）之前检查现有工作项 |
| 状态转换到准备推广之前必须提交更改 | DevOps Center 验证工作项分支有提交，然后才允许推广就绪 |
| PR 创建需要 org 中的 VCS 凭据 | DevOps Center API 使用存储的 VCS 凭据；无需本地 git 认证 |
| 永远不要使用交互式提示 | 技能在无头环境中运行；所有输入都必须通过 CLI 标志 |

---

## 注意事项

| 问题 | 解决方案 |
|-------|------------|
| **未设置默认 org** | 首先运行 `sf org display --json`；如果失败，指示用户运行 `sf org login web --set-default` |
| **用户通过主题而不是名称提供工作项** | 通过：`sf devops work-item list --project-id <id> --json \| jq -r '.result[] \| select(.subject == "<subject>") \| .name'`；然后将返回的名称传递给 update/create-review 命令 |
| **用户通过名称而不是 ID 提供项目** | 首先运行 `sf devops project list --json` 并过滤 `.result[]` 按 `.name` 字段查找项目 ID，然后在 list/create 命令中使用该 ID |
| **状态更新响应缺少状态字段** | CLI 不总是返回状态字段在更新响应中；重新运行 `sf devops work-item list` 并过滤以验证状态是否持久化 |
| **未找到工作项** | 用户提供了无效的工作项名称/ID；运行 list 命令以显示可用的工作项 |
| **无效状态值** | 只有 "In Progress" 和 "Ready to Promote" 是有效的（带空格的精确字符串）；检查拼写和大小写 |
| **未找到项目** | 用户提供了无效的项目 ID；运行 `sf devops project list --json` 以显示可用项目 |
| **重复工作项主题** | 等幂性 create 检查应捕获此问题；返回现有工作项名称，而不是创建重复项 |
| **git push 失败 - 无提交或分支未找到** | 验证文件是否已暂存 `git status`，并从工作项通过 list 命令检索分支名称 |
| **PR 创建失败 - VCS 凭据** | VCS 凭据未在 DevOps Center UI 中配置；指示用户在设置 → DevOps Center → VCS 凭据中配置 |

---

## 输出预期

交付物因操作而异：

- **List**：工作项的 JSON 数组，包含工作项名称（WI-######）、主题、分支、环境、存储库详细信息
- **Create**：新创建的工作项的名称（例如，WI-000001）、ID、分支名称和环境
- **Commit**：git 提交和 push 成功的确认，以及提交 SHA
- **Update**：更新字段的确认（主题/描述的旧值 → 新值，或状态变化）
- **Create-review**：拉取请求 URL、PR 编号和状态

输出来自 `sf devops work-item` CLI、`sf devops review create` CLI 和标准的 git 命令。

---

## 验证检查清单

在向用户报告结果之前：

### 通用检查
- [ ] 是否使用 `sf org display --json` 验证了 org 认证？
- [ ] 是否使用 `--json` 标志执行了 CLI 命令？
- [ ] CLI 是否返回成功退出代码（0）？
- [ ] JSON 输出是否可解析且非空？
- [ ] 如果是多 org 场景，是否在所有命令中使用 `--target-org`？

### List 操作检查
- [ ] 是否提供了 `--project-id`？
- [ ] 是否以可读格式显示工作项名称、主题、分支、环境？
- [ ] 如果列表为空，是否向用户传达了此信息？

### Create 操作检查
- [ ] JSON 输出中是否返回了工作项名称（WI-######）和 ID？
- [ ] 是否返回了分支名称？
- [ ] 是否提供了 `--subject`（或通过项目列表获取）？

### Commit 操作检查
- [ ] 是否成功检索了工作项分支名称？
- [ ] 是否使用 `git add` 暂存了文件？
- [ ] `git commit` 是否成功（退出代码 0）？
- [ ] `git push` 是否成功（退出代码 0）？

### Update 操作检查
- [ ] 是否提供了工作项标识符（名称或 ID）？
- [ ] 是否至少提供了一个更新字段（主题、描述或状态）？
- [ ] 如果状态更新，是否为有效值（"In Progress" 或 "Ready to Promote"）？
- [ ] 是否返回了更新后的工作项？

### Create-Review 操作检查
- [ ] 是否提供了工作项标识符（名称或 ID）？
- [ ] 是否返回了 PR URL？
- [ ] 是否确认了 PR 创建？

---

## 参考文件索引

| 文件 | 何时阅读 |
|------|-------------|
| `references/cli-commands.md` | 当您需要详细的 CLI 标志文档、JSON 输出模式或错误处理模式时 |
| `examples/common-workflows.md` | 当用户的请求匹配常见模式（批量更新、重新分配、等幂性创建、顺序转换）时 |
