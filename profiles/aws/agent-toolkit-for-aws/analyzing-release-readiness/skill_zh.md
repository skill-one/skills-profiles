# 发布准备就绪审查

> **AgentSpace 路由（仅 SigV4）：** 如果您的工具列表中存在 `list_agent_spaces`，并且本次会话尚未调用多空间编排技能，请首先调用它以确定要使用的 `agent_space_id`。然后在所有后续工具调用中传递 `agent_space_id`。对于承载令牌认证，这不需要——令牌已经针对一个空间进行了范围限制。

通过 AWS DevOps Agent 运行发布准备就绪审查。分析代码更改的风险、正确性和潜在的回滚问题。返回一个包含可操作发现的结构化报告。

**规则：**

- 如果提供了 **PR/MR URL**：提取 URL 中的所有字段。不要检查本地工作区或 git 状态。
- **绝对不要**使用 `gh` CLI、`glab` CLI 或任何外部工具来获取 PR/MR 详细信息。所有必需字段（仓库、prNumber/mergeRequestIid、hostname）必须直接从 URL 或用户输入中解析。DevOps Agent 会自行获取内容——您只需要传递标识符。
- **仅**在用户引用没有 PR/MR 链接的仓库或包时使用本地工作区流程。

## 收集执行参数

自动从用户请求中推断所有信息——不要请求可以推导出的参数。

**输入源决策树：**

```
用户是否提供了拉取请求/合并请求链接或 ID？
├── 是：github.com PR URL               → 使用下方的 "GitHub PR" 流程
├── 是：gitlab.com MR URL               → 使用下方的 "GitLab MR" 流程
└── 未提供链接——仅提供仓库名称    → 使用下方的 "本地 GitHub/GitLab 仓库" 流程
```

---

### GitHub PR (github.com URL 或 PR 引用)

- 解析输入以提取字段——除非可以从输入中确定字段，否则不要尝试网络获取。
- `repository`（必需）：PR URL 中的 `owner/repo`
- 至少需要以下之一：`headSha`（提交 SHA）、`headBranch`（分支名称）、`prNumber`（PR 编号作为 **字符串**，例如 `"8"` 而不是 `8`）
- `hostname`：从 URL 中提取（例如，`github.com` 或自托管主机名）
- 将这些字段传递给 `create_release_readiness_review`，作为 `content.githubPrContent` 下的 **对象数组**（即使对于单个 PR）。

**示例：**

```json
{
  "content": {
    "githubPrContent": [
      {
        "repository": "owner/repo",
        "prNumber": "8",
        "hostname": "github.com"
      }
    ]
  }
}
```

> **关键格式规则**：`githubPrContent` 必须是数组（而不是单个对象）。`prNumber` 必须是字符串（而不是整数）。

---

### GitLab MR (gitlab.com URL)

- 解析输入以提取字段——除非可以从输入中确定字段，否则不要尝试网络获取。
- `repository`（必需）：MR URL 中的 `owner/repo`
- 至少需要以下之一：`headSha`（提交 SHA）、`headBranch`（分支名称）、`mergeRequestIid`（MR 编号作为 **字符串**，例如 `"1"` 而不是 `1`）
- `hostname`：从 URL 中提取（例如，`gitlab.com` 或自托管主机名）
- 将这些字段传递给 `create_release_readiness_review`，作为 `content.gitlabMrContent` 下的 **对象数组**（即使对于单个 MR）。

**示例：**

```json
{
  "content": {
    "gitlabMrContent": [
      {
        "repository": "namespace/repo",
        "mergeRequestIid": "1",
        "hostname": "gitlab.com"
      }
    ]
  }
}
```

> **关键格式规则**：`gitlabMrContent` 必须是数组（而不是单个对象）。`mergeRequestIid` 必须是字符串（而不是整数）。违反任何规则会导致任务立即失败且没有日志记录。

---

### 本地 GitHub/GitLab 仓库（未提供 PR/MR URL——仅限本地工作区）

**强制要求**：当用户引用没有 PR/MR 链接的仓库或分支时，您必须按顺序执行以下所有步骤。不要通过直接获取远程 URL 和 SHA 来跳过步骤——审查代理需要从已推送的分支读取。跳过推送步骤会导致分析失败或结果不完整。

1. **导航到仓库目录**：`cd` 到仓库根目录（例如，克隆目录）。如有需要，请询问用户。
2. **确定基础分支**：使用 `main`，除非用户指定了其他分支。验证远程跟踪分支是否存在：

   ```bash
   BASE_BRANCH="main"
   if ! git show-ref --verify --quiet refs/remotes/origin/$BASE_BRANCH; then
       git fetch origin $BASE_BRANCH
   fi
   ```

   如果获取失败（例如，"找不到远程引用"），请询问用户指定基础分支并停止。
3. **检查本地更改**：运行 `git status --short` 和 `git rev-list --count origin/$BASE_BRANCH..HEAD` 以确定状态并相应地沟通：

   - **干净且未 ahead**：告知用户没有新内容需要分析并停止。

   - **存在未提交的更改（无论是否有未推送的提交）**：
     - 如果存在一个或多个未推送的提交（rev-list 计数 >= 1），请告知用户：
       > "您有未提交的更改和 N 个未推送的提交。我将提交您的未提交更改，然后将所有 N+1 个提交推送到一个新分支进行分析。所有更改将显示为相对于基础分支的单个 diff。您要继续吗？"
     - 如果没有其他未推送的提交（rev-list 计数 = 0），请告知用户：
       > "我将提交您的未提交更改并将它们推送到一个新分支进行发布准备审查。您要继续吗？"
     - **在用户批准之前不要继续**。如果他们拒绝，请停止。
     - **干净但 ahead of remote（rev-list 计数 > 0，没有未提交的更改）**：
       - 如果 ahead 超过 1 个提交，请告知用户：
         > "您有 N 个未推送的提交。我将它们全部推送到一个新分支进行分析。所有更改将显示为相对于基础分支的单个 diff。您要继续吗？"
       - 如果 ahead 恰好为 1 个提交，请告知用户：
         > "我将您的最新提交推送到一个新分支进行发布准备审查。您要继续吗？"
     - **在用户批准之前不要继续**。如果他们拒绝，请停止。
4. **暂存未提交的更改**（如果工作目录不干净，请跳过此步骤）：

   ```bash
   git stash push --include-untracked -m "release-analysis: 保留工作更改"
   ```
5. **创建审查分支**（在提交之前执行此操作，以便快照提交仅存在于可丢弃的分支上）：

   ```bash
   ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
   BRANCH_NAME="feat/release-readiness-review"
   git checkout -b $BRANCH_NAME 2>/dev/null || { BRANCH_NAME="feat/release-readiness-review-$(date +%Y%m%d-%H%M%S)"; git checkout -b $BRANCH_NAME; }
   ```
6. **在审查分支上应用暂存更改并提交**（如果工作目录干净，请跳过此步骤——直接进入步骤 7）：

   ```bash
   git stash apply
   ```

   在暂存之前，检查敏感文件：

   ```bash
   git status --short | grep -iE '\.(env|pem|key|p12|pfx|credentials|secret)'
   ```

   如果检测到敏感文件，请警告用户并在继续之前请求确认。如果用户拒绝，则中止：

   ```bash
   git checkout $ORIGINAL_BRANCH && git branch -D $BRANCH_NAME && git stash drop
   ```

   确认后（或未发现敏感文件）：

   ```bash
   git add -A
   git commit -m "chore: 快照用于发布准备审查"
   ```
7. **推送所有未推送的提交**（需要先获得用户批准）：
   如果用户在步骤 3 中已经批准推送，请直接进行。否则（例如，流程在此处到达而没有明确的批准提示），请在推送之前确认：
   > "我即将将分支 `$BRANCH_NAME` 推送到 `origin`。这是先决步骤，我可以继续吗？"
   **在用户批准之前不要推送**。如果他们拒绝，请中止并跳到步骤 11。
   一旦获得批准（或步骤 3 中已经批准）：

   ```bash
   git push -u origin HEAD
   ```
8. **确定仓库标识符和主机名**：运行 `git remote get-url origin | sed 's|://[^@]*@|://|'` 以提取 `owner/repo` 和主机名。
   - GitHub URL（github.com 或自托管）→ 使用 `githubPrContent`，从 URL 中提取主机名
   - GitLab URL（gitlab.com 或自托管）→ 使用 `gitlabMrContent`，从 URL 中提取主机名
9. **构建内容**：将 `headBranch` 设置为 `$BRANCH_NAME`，`repository` 设置为提取的 `owner/repo`，并将 `hostname` 设置为步骤 8 中的值。将对象包装在数组中：
   - GitHub: `{"githubPrContent": [{"repository": "owner/repo", "headBranch": "feat/release-readiness-review", "hostname": "github.com"}]}`
   - GitLab: `{"gitlabMrContent": [{"repository": "namespace/repo", "headBranch": "feat/release-readiness-review", "hostname": "gitlab.com"}]}`
10. **告知用户**：告诉他们创建了哪个分支并已推送，然后继续执行以下核心工作流。
11. **分析完成后**：清理并恢复工作状态：

    ```bash
    git checkout $ORIGINAL_BRANCH
    git push origin --delete $BRANCH_NAME 2>/dev/null || true
    git branch -D $BRANCH_NAME 2>/dev/null || true
    ```

    如果步骤 4 已执行（存在未提交的更改并已暂存），请运行：

    ```bash
    git stash pop
    ```

**重要**：不要创建 PR/MR——仅推送分支。发布准备审查代理将直接读取分支。

## 核心工作流

> **严格顺序**：以下步骤按编号顺序执行。您必须完成每个步骤才能进入下一个步骤。特别是，步骤 1（自动测试提示）必须在上述“收集执行参数”流程完全完成后才能发生——所有 git 操作完成、分支推送（如果本地流程）、内容对象构建、并告知用户分支。只有到那时才能继续步骤 1。

### 1. 确定 `skip_automated_testing`（仅内容准备好后询问）

`skip_automated_testing` 参数控制代理是否运行自动测试（自动验证测试）或仅静态分析。

| 值     | 行为     |
|-------|---------|
| `true` | 跳过自动测试，仅运行静态分析（快速——代码审查、风险评估、依赖项检查） |
| `false` | 全部分析，包括自动测试（较长——启动测试环境、构建代码、运行自动验证测试） |

提供选择并等待响应：
> "您想要快速静态分析（代码审查、风险评估、依赖项检查），还是完整分析（包括自动测试）？自动测试会启动测试环境、构建您的代码并运行自动验证测试——它更彻底但需要更长时间。"

**在用户回答之前不要继续。**

- 如果用户说 "是" / "包括测试" / "完整分析" / "运行测试" → 使用 `skip_automated_testing=false`
- 如果用户说 "否" / "仅静态" / "跳过测试" / "快速" / 拒绝 → 使用 `skip_automated_testing=true`
- 如果响应不明确（例如，"继续"、"当然"、"进行"）→ 请求用户澄清他们更喜欢哪个选项。

### 2. 检查工具可用性

验证以下工具是否可用：`aws_devops_agent__create_release_readiness_review`、`aws_devops_agent__get_task`、`aws_devops_agent__list_journal_records`、`aws_devops_agent__get_release_readiness_report`。这些工具不是延迟加载的——如果它们未出现在您的工具列表中，则不可用。不要通过 ToolSearch 搜索它们。如果有任何缺失，请跳过此部分剩余步骤并使用下方的 "Fallback (aws-mcp)" 路径。告诉用户："远程服务器不可用——使用直接 aws-mcp 服务器回退。"

### 3. 启动任务

```
aws_devops_agent__create_release_readiness_review(
    content={...},
    skip_automated_testing=true/false
)
→ {"taskId": "...", "executionId": "...", "status": "started"}
```

从响应中记录 **taskId** 和 **executionId**。

### 4. 定期轮询状态

每 **30 秒** 调用一次 `aws_devops_agent__get_task(task_id=TASK_ID)`，直到状态过渡到 `IN_PROGRESS` 或终止状态（`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`）。

### 5. 监控直至完成

一旦 `IN_PROGRESS`，循环轮询进度：

1. 调用 `aws_devops_agent__list_journal_records(execution_id=EXEC_ID, order="ASC")` 获取新发现。
2. 将每条记录以友好的进度更新呈现给用户。
3. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
4. 每次轮询迭代之间等待 **15 秒**。
5. 定期检查 `aws_devops_agent__get_task(task_id=TASK_ID)`——在终止状态时停止。

### 6. 呈现结果

一旦任务达到终止状态：

- 如果 `COMPLETED`：
  1. 调用 `aws_devops_agent__get_release_readiness_report(execution_id=EXEC_ID)` 获取完整报告。
  2. 将报告内容写入 markdown 文件：

     ```
     release-readiness-review-<YYYY-MM-DD-HHmmss>.md
     ```
  3. 告知用户报告已保存，包括文件路径。
  4. **自动修复流程（强制要求）**：保存报告后，您必须尝试为所有可操作的发现生成和呈现修复——这是审查工作流的主要价值，不是可选步骤。
     - 首先，在当前工作区中定位分析的仓库：
       1. 运行 `ls` 列出工作区中的可用目录。
       2. 通过 `owner/repo` 或 `namespace/repo` 的最后一部分进行匹配。例如，`testgroupadthiru/repo1updated` → 查找名为 `repo1updated` 的目录。
       3. 如果找到一个匹配，请确认用户："我找到了 `<match>` —— 这是 `<namespace/repo>` 的正确本地副本吗？"
       4. 如果有多个匹配，请询问用户哪个是正确的。
       5. 如果没有明显的匹配，请询问用户："我找不到与 `<repo-name>` 匹配的本地目录。它是本地以不同名称可用，还是我应该直接显示建议的修复？"
     - 如果 **找到本地**：
       - **验证分支**：运行 `git -C <repo-directory> branch --show-current` 以确认您位于预期分支上。如果不位于预期分支，请在继续之前检查出正确的分支。
       - 扫描相关代码，解释报告中的风险/问题。然后告诉用户：
         > "报告确定了 N 个可操作的发现。我可以生成本地仓库中的修复，并将它们推送到新分支 `feat/release-readiness-fix`。您要继续吗？"
       - **在用户批准之前不要继续**。如果他们拒绝，请停止。
       - 一旦批准，生成修复。然后：

         ```bash
         cd <repo-directory>
         git checkout -b feat/release-readiness-fix 2>/dev/null || { git checkout -b "feat/release-readiness-fix-$(date +%Y%m%d-%H%M%S)"; }
         # 应用修复
         git add -A
         git commit -m "fix: 解决发布准备审查发现的问题"
         ```

       - **推送之前再次验证分支**：运行 `git branch --show-current` 并确认它显示 `feat/release-readiness-fix*`。如果您在任何其他分支上，请不要推送。

         ```bash
         git push -u origin HEAD
         ```

         告知用户：修复了哪些问题，创建了哪个分支，以及修复已推送。
     - 如果 **未找到本地**：将建议的修复从报告中作为具体的、可直接复制粘贴的代码补丁呈现。使用每个风险中的 `suggestedFix`。将它们格式化为代码块，用户可以直接复制粘贴。逐步解释每个可操作风险：解释问题，显示确切的修复，并说明目标文件/行。
     - 如果报告发现 **没有风险或问题**：告知用户分析完成且没有可操作的发现。
- 如果 `FAILED` 或 `TIMED_OUT`：呈现错误信息并建议下一步操作。
- 如果 `CANCELED`：告知用户任务已取消且没有报告可用。

## 取消任务

```
aws_devops_agent__cancel_release_readiness_review(task_id=TASK_ID)
```

## 错误处理

1. 如果 `FAILED` 或 `TIMED_OUT` — 停止并呈现错误。如果任务快速失败（在第一次或几次轮询内），请调用 `aws_devops_agent__list_associations()` 检查目标仓库的主机服务（GitHub/GitLab 主机名）是否与代理空间关联。
2. 如果任务在 5 分钟内未达到 `IN_PROGRESS` — 使用 `cancel_release_readiness_review` 取消。
3. 如果被限流（`429` 或 `ThrottlingException`）— 等待 30 秒，最多重试 3 次。
4. 如果错误与上述任何已知模式不匹配，请将原始错误输出呈现给用户。

## Fallback (aws-mcp)

如果 `aws-devops-agent` 远程服务器不可用，请直接使用 AWS CLI：

告诉用户："远程服务器不可用——使用 aws-mcp 服务器回退。"

### 1. 选择 Agent Space

列出可用的代理空间：

```
aws devops-agent list-agent-spaces --region us-east-1
```

将列表呈现给用户并询问他们想使用哪个代理空间。**在用户选择后才能继续**。在后续所有调用中使用选择的 `agentSpaceId` 作为 `SPACE_ID`。

### 2. 启动任务

```
aws devops-agent create-backlog-task \
  --agent-space-id SPACE_ID \
  --task-type RELEASE_READINESS_REVIEW \
  --title 'Release Readiness Review' \
  --priority MEDIUM \
  --description '{\"agentInput\": {\"content\": <CONTENT_JSON>, \"metadata\": {\"skipAutomatedTesting\": true}}}' \
  --region us-east-1
```

> **关键**：`content` 值必须是一个单个对象——不能包装在列表中。正确：`"content": {"githubPrContent": [...]}`。错误：`"content": [{"githubPrContent": [...]}]`。在列表中包装会导致后端 Pydantic 验证失败。内容中的值应为字符串格式，例如 PR 编号应为字符串。

默认为 `"skipAutomatedTesting": true`（仅静态）。仅在用户明确选择自动测试时设置为 `false`。

### 3. 定期轮询状态

```
aws devops-agent get-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --region us-east-1
```

每 **30 秒** 轮询一次，直到状态过渡到 `IN_PROGRESS` 或终止状态（`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`）。

### 4. 监控直至完成

一旦 `IN_PROGRESS`，循环轮询进度：

```
aws devops-agent list-journal-records \
  --agent-space-id SPACE_ID \
  --execution-id EXEC_ID \
  --order ASC \
  --region us-east-1
```

1. 将每条记录以友好的进度更新呈现给用户。
2. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
3. 每次轮询迭代之间等待 **15 秒**。
4. 定期检查 `get-backlog-task`——在终止状态时停止。

### 5. 呈现结果

一旦任务达到终止状态：

- 如果 `COMPLETED`：
  1. 获取报告：

     ```
     aws devops-agent list-journal-records \
       --agent-space-id SPACE_ID \
       --execution-id EXEC_ID \
       --record-type release_analysis_report \
       --order ASC \
       --region us-east-1
     ```

  2. 将报告内容写入 markdown 文件：

     ```
     release-readiness-review-<YYYY-MM-DD-HHmmss>.md
     ```

  3. 告知用户报告已保存，包括文件路径。
  4. **自动修复流程（强制要求）**：保存报告后，您必须尝试为所有可操作的发现生成和呈现修复——这是审查工作流的主要价值，不是可选步骤。遵循上述核心工作流部分中描述的自动修复流程（定位仓库、验证分支、生成修复、推送到 `feat/release-readiness-fix`）。
- 如果 `FAILED` 或 `TIMED_OUT`：呈现错误信息并建议下一步操作。
- 如果 `CANCELED`：告知用户任务已取消且没有报告可用。

#### 取消（回退）

```
aws devops-agent update-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --task-status CANCELED \
  --region us-east-1
```
