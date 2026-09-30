---
name: analyzing-release-readiness
description: 在 GitHub PR、GitLab MR 或本地分支上触发预合并发布就绪性审查。当用户希望在合并前分析代码变更的风险、正确性及潜在回滚问题时使用。触发词包括：发布就绪性、分析 PR、分析 MR、审查 PR、风险分析、预合并、安全可发布、准备合并、准备提交、存在任何风险、合并前、验证变更、发布管理。
---

# 发布就绪性审查

> **AgentSpace 路由（仅 SigV4）：** 如果您的工具列表中存在 `list_agent_spaces`，并且本次会话尚未调用多空间编排技能，请首先调用它以确定要使用的 `agent_space_id`。然后在所有后续工具调用中传递 `agent_space_id`。对于基于令牌的身份验证，这不需要——令牌已经针对一个空间进行了范围限制。

通过 AWS DevOps Agent 运行发布就绪性审查。分析代码更改的风险、正确性和潜在的回滚问题。返回一个包含可操作发现的结构化报告。

**规则：**

- 如果提供了 **PR/MR URL**：从 URL 中提取所有字段。不要检查本地工作区或 git 状态。
- **绝对不要**使用 `gh` CLI、`glab` CLI 或任何外部工具来获取 PR/MR 详细信息。所有必需字段（仓库、prNumber/mergeRequestIid、hostname）必须直接从 URL 或用户输入中解析。DevOps Agent 会自行获取内容——您只需要传递标识符。
- **仅**在用户引用没有 PR/MR 链接的仓库或包时使用本地工作区流程。

## 收集执行参数

自动从用户请求中推断所有信息——不要请求可以推导出的参数。

**输入源决策树：**

```
用户是否提供了拉取请求/合并请求链接或 ID？
├── 是：github.com PR URL               → 使用下面的 "GitHub PR" 流程
├── 是：gitlab.com MR URL               → 使用下面的 "GitLab MR" 流程
└── 未提供链接——仅提供仓库名称    → 使用下面的 "本地 GitHub/GitLab 仓库" 流程
```

---

### GitHub PR (github.com URL 或 PR 引用)

- 解析输入以提取字段——除非可以从输入中确定字段，否则不要尝试进行网络获取。
- `repository`（必需）：从 PR URL 中获取 `owner/repo`
- 至少需要一个以下字段：`headSha`（提交 SHA）、`headBranch`（分支名称）、`prNumber`（PR 编号作为 **字符串**，例如 `"8"` 而不是 `8`）
- `hostname`：从 URL 中提取（例如 `github.com` 或自托管主机名）
- 将这些字段作为 **对象数组**（即使对于单个 PR）传递给 `create_release_readiness_review`，作为 `content.githubPrContent` 下的内容。

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

- 解析输入以提取字段——除非可以从输入中确定字段，否则不要尝试进行网络获取。
- `repository`（必需）：从 MR URL 中获取 `owner/repo`
- 至少需要一个以下字段：`headSha`（提交 SHA）、`headBranch`（分支名称）、`mergeRequestIid`（MR 编号作为 **字符串**，例如 `"1"` 而不是 `1`）
- `hostname`：从 URL 中提取（例如 `gitlab.com` 或自托管主机名）
- 将这些字段作为 **对象数组**（即使对于单个 MR）传递给 `create_release_readiness_review`，作为 `content.gitlabMrContent` 下的内容。

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

**强制要求**：当用户引用没有 PR/MR 链接的仓库或分支时，您必须按顺序执行以下所有步骤。不要通过直接获取远程 URL 和 SHA 来简化操作——审查代理需要从已推送的分支读取。跳过推送步骤会导致分析失败或结果不完整。

1. **导航到仓库目录**：`cd` 到仓库根目录（例如，克隆目录）。如有需要，请询问用户。
2. **确定基础分支**：使用 `main`，除非用户指定了不同的分支。验证远程跟踪分支是否存在：

   ```bash
   BASE_BRANCH="main"
   if ! git show-ref --verify --quiet refs/remotes/origin/$BASE_BRANCH; then
       git fetch origin $BASE_BRANCH
   fi
   ```

   如果获取失败（例如，"找不到远程引用"），请询问用户指定基础分支并停止。
3. **检查本地更改**：运行 `git status --short` 和 `git rev-list --count origin/$BASE_BRANCH..HEAD` 以确定状态并相应地沟通：

   - **干净且未领先**：告知用户没有新内容需要分析并停止。

   - **有未提交的更改（无论是否有未推送的提交）**：
     - 如果有一个或多个未推送的提交（rev-list 计数 >= 1），请告知用户：
       > "您有未提交的更改和 N 个未推送的提交。我将提交您的未提交更改，然后将所有 N+1 个提交推送到一个新分支进行分析。所有更改将显示为相对于基础分支的单个差异。是否继续？"
     - 如果没有其他未推送的提交（rev-list 计数 = 0），请告知用户：
       > "我将提交您的未提交更改并将它们推送到一个新分支进行发布就绪性审查。是否继续？"
     - **在用户批准之前不要继续。** 如果他们拒绝，停止。
     - **干净但领先于远程（rev-list 计数 > 0，没有未提交的更改）**：
       - 如果领先超过 1 个提交，请告知用户：
         > "您有 N 个未推送的提交。我将把它们全部推送到一个新分支进行分析。所有更改将显示为相对于基础分支的单个差异。是否继续？"
       - 如果正好领先 1 个提交，请告知用户：
         > "我将您的最新提交推送到一个新分支进行发布就绪性审查。是否继续？"
     - **在用户批准之前不要继续。** 如果他们拒绝，停止。

4. **暂存未提交的更改**（如果工作目录干净则跳过此步骤）：

   ```bash
   git stash push --include-untracked -m "release-analysis: 保留工作更改"
   ```

5. **创建审查分支**（在此步骤之前执行此操作，以便快照提交仅存在于可丢弃分支上）：

   ```bash
   ORIGINAL_BRANCH=$(git rev-parse --abbrev-ref HEAD)
   BRANCH_NAME="feat/release-readiness-review"
   git checkout -b $BRANCH_NAME 2>/dev/null || { BRANCH_NAME="feat/release-readiness-review-$(date +%Y%m%d-%H%M%S)"; git checkout -b $BRANCH_NAME; }
   ```

6. **在审查分支上应用暂存更改并提交**（如果工作目录干净则跳过此步骤——直接进入步骤 7）：

   ```bash
   git stash apply
   ```

   在暂存之前，检查敏感文件：

   ```bash
   git status --short | grep -iE '\.(env|pem|key|p12|pfx|credentials|secret)'
   ```

   如果检测到敏感文件，警告用户并在继续之前请求确认。如果用户拒绝，中止：

   ```bash
   git checkout $ORIGINAL_BRANCH && git branch -D $BRANCH_NAME && git stash drop
   ```

   确认后（或未发现敏感文件）：

   ```bash
   git add -A
   git commit -m "chore: 快照用于发布就绪性审查"
   ```

7. **推送所有未推送的提交**（需要先获得用户批准）：
   如果用户在步骤 3 中已经批准推送，则直接进行。否则（例如，流程在没有明确批准提示的情况下到达此处），在推送之前确认：
   > "我即将将分支 `$BRANCH_NAME` 推送到 `origin`。这是先决步骤，我可以继续吗？"
   **在用户批准之前不要推送。** 如果他们拒绝，中止并跳到步骤 11。

   批准后（或如果步骤 3 中已经批准）：

   ```bash
   git push -u origin HEAD
   ```

8. **确定仓库标识符和主机名**：运行 `git remote get-url origin | sed 's|://[^@]*@|://|'` 以提取 `owner/repo` 和主机名。
   - GitHub URL（github.com 或自托管）→ 使用 `githubPrContent`，从 URL 中获取主机名
   - GitLab URL（gitlab.com 或自托管）→ 使用 `gitlabMrContent`，从 URL 中获取主机名

9. **构建内容**：将 `headBranch` 设置为 `$BRANCH_NAME`，`repository` 设置为提取的 `owner/repo`，并将主机名设置为步骤 8 中的值。将对象包装在数组中：
   - GitHub: `{"githubPrContent": [{"repository": "owner/repo", "headBranch": "feat/release-readiness-review", "hostname": "github.com"}]}`
   - GitLab: `{"gitlabMrContent": [{"repository": "namespace/repo", "headBranch": "feat/release-readiness-review", "hostname": "gitlab.com"}]}`

10. **告知用户**：告诉他们创建了哪个分支并推送了，然后继续执行以下核心工作流。
11. **分析完成后**：清理并恢复工作状态：

    ```bash
    git checkout $ORIGINAL_BRANCH
    git push origin --delete $BRANCH_NAME 2>/dev/null || true
    git branch -D $BRANCH_NAME 2>/dev/null || true
    ```

    如果执行了步骤 4（暂存了未提交的更改），请也运行：

    ```bash
    git stash pop
    ```

**重要**：不要创建 PR/MR——仅推送分支。发布就绪性审查代理将直接读取分支。

## 核心工作流

> **严格顺序**：以下步骤按编号排列。您必须完成每个步骤才能进入下一个步骤。特别是，步骤 1（自动测试提示）必须在上述“收集执行参数”流程完全完成后才能发生——所有 git 操作完成、分支推送（如果本地流程）、内容对象构建、并告知用户分支。只有到那时才能继续步骤 1。

### 1. 确定 `skip_automated_testing`（仅内容准备好后询问）

`skip_automated_testing` 参数控制代理是否运行自动测试（自动验证测试）或仅静态分析。

| 值     | 行为                               |
|-------|-----------------------------------|
| `true` | 跳过自动测试，仅运行静态分析（快速——代码审查、风险评估、依赖项检查） |
| `false` | 全部分析，包括自动测试（较长——启动测试环境、构建代码、运行自动验证测试） |

提供选择并等待响应：
> "您希望进行快速静态分析（代码审查、风险评估、依赖项检查），还是进行全面分析（包括自动测试）？自动测试会启动测试环境、构建您的代码并运行自动验证测试——它更彻底但需要更长时间。"

**在用户回答之前不要继续。**

- 如果用户说 "是" / "包括测试" / "全面分析" / "运行测试" → 使用 `skip_automated_testing=false`
- 如果用户说 "否" / "仅静态" / "跳过测试" / "快速" / 拒绝 → 使用 `skip_automated_testing=true`
- 如果响应不明确（例如，"继续"、"当然"、"进行"）→ 请求用户澄清他们更喜欢哪个选项。

### 2. 检查工具可用性

验证以下工具是否可用：`aws_devops_agent__create_release_readiness_review`、`aws_devops_agent__get_task`、`aws_devops_agent__list_journal_records`、`aws_devops_agent__get_release_readiness_report`。这些工具不是延迟加载的——如果它们不在您的工具列表中，则不可用。不要通过 ToolSearch 搜索它们。如果有任何工具缺失，请跳过此部分剩余步骤并使用下面的 "Fallback (aws-mcp)" 路径。告诉用户："远程服务器不可用——使用直接 aws-mcp 服务器回退。"

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

每 **30 秒** 调用一次 `aws_devops_agent__get_task(task_id=TASK_ID)`，直到状态过渡到 `IN_PROGRESS` 或终端状态 (`COMPLETED`、`FAILED`、`CANCELED`、`TIMED_OUT`)。

### 5. 监控直至完成

一旦 `IN_PROGRESS`，循环轮询进度：

1. 调用 `aws_devops_agent__list_journal_records(execution_id=EXEC_ID, order="ASC")` 获取新发现。
2. 将每条记录以友好的进度更新呈现给用户。
3. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
4. 在每次轮询迭代之间等待 **15 秒**。
5. 定期检查 `aws_devops_agent__get_task(task_id=TASK_ID)`——在终端状态时停止。

### 6. 呈现结果

一旦任务达到终端状态：

- 如果 `COMPLETED`：
  1. 调用 `aws_devops_agent__get_release_readiness_report(execution_id=EXEC_ID)` 以检索完整报告。
  2. 将报告内容写入 markdown 文件：

     ```
     release-readiness-review-<YYYY-MM-DD-HHmmss>.md
     ```

  3. 告知用户报告已保存，包括文件路径。
  4. **自动修复流程（强制要求）**：保存报告后，您必须尝试为所有可操作的已知风险生成和呈现修复——这是审查工作流的主要价值，不是可选步骤。
     - 首先，在当前工作区中定位分析的仓库：
       1. 运行 `ls` 列出工作区中的可用目录。
       2. 通过仓库名称（`owner/repo` 或 `namespace/repo` 的最后一部分）进行匹配。例如，`testgroupadthiru/repo1updated` → 查找名为 `repo1updated` 的目录。
       3. 如果找到一个匹配，请与用户确认： "我找到了 `<match>` —— 这是 `<namespace/repo>` 的正确本地副本吗？"
       4. 如果有多个匹配，请询问用户哪个是正确的。
       5. 如果没有明显的匹配，请询问用户： "我找不到与 `<repo-name>` 匹配的本地目录。它是本地以不同名称可用，还是我应该直接显示建议的修复？"
     - 如果 **找到本地副本**：
       - **验证分支**：运行 `git -C <repo-directory> branch --show-current` 以确认您位于预期的分支上。如果不位于预期分支，请在继续之前切换到正确的分支。
       - 扫描相关代码，解释报告中的风险/问题。然后告诉用户：
         > "报告识别了 N 个可操作的已知问题。我可以生成您本地仓库中的修复，并将它们推送到一个新分支 `feat/release-readiness-fix`。是否继续？"
       - **在用户批准之前不要继续。** 如果他们拒绝，停止。
       - 批准后，生成修复。然后：

         ```bash
         cd <repo-directory>
         git checkout -b feat/release-readiness-fix 2>/dev/null || { git checkout -b "feat/release-readiness-fix-$(date +%Y%m%d-%H%M%S)"; }
         # 应用修复
         git add -A
         git commit -m "fix: 解决发布就绪性审查识别的问题"
         ```

       - **推送前再次验证分支**：运行 `git branch --show-current` 并确认它显示 `feat/release-readiness-fix*`。如果您位于任何其他分支，则不要推送。

         ```bash
         git push -u origin HEAD
         ```

         告知用户：已修复哪些问题，创建了哪个分支，以及修复已推送。
     - 如果 **未找到本地副本**：从报告中呈现建议的修复作为具体的、可直接复制粘贴的代码补丁。使用每个风险中的 `suggestedFix` 字段。将它们格式化为用户可以复制粘贴的代码块。逐步解释每个可操作的已知风险：解释问题，显示确切的修复，并说明哪个文件/行它针对。
     - 如果报告发现 **没有风险或问题**：告知用户分析完成且没有可操作的发现。
- 如果 `FAILED` 或 `TIMED_OUT`：呈现错误信息并建议下一步操作。
- 如果 `CANCELED`：告知用户任务已取消且没有报告可用。

## 取消任务

```
aws_devops_agent__cancel_release_readiness_review(task_id=TASK_ID)
```

## 错误处理

1. 如果是 `FAILED` 或 `TIMED_OUT` — 停止并显示错误。如果作业快速失败（在前几次轮询内），调用 `aws_devops_agent__list_associations()` 来检查目标仓库的托管服务（GitHub/GitLab 主机名）是否与代理空间关联。
2. 如果作业在 5 分钟内未达到 `IN_PROGRESS` 状态 — 使用 `cancel_release_readiness_review` 进行取消。
3. 如果被限流（`429` 或 `ThrottlingException`）— 等待 30 秒，最多重试 3 次。
4. 如果错误与上述任何已知模式不匹配，向用户显示原始错误输出。

## 回退（aws-mcp）

如果 `aws-devops-agent` 远程服务器不可用，直接使用 AWS CLI：

告知用户："远程服务器不可用 — 使用 aws-mcp 服务器回退。"

### 1. 选择代理空间

列出可用的代理空间：

```
aws devops-agent list-agent-spaces --region us-east-1
```

向用户展示列表并询问他们想使用哪个代理空间。**直到用户选择一个后才能继续。** 使用选择的 `agentSpaceId` 作为后续所有调用中的 `SPACE_ID`。

### 2. 启动作业

```
aws devops-agent create-backlog-task \
  --agent-space-id SPACE_ID \
  --task-type RELEASE_READINESS_REVIEW \
  --title 'Release Readiness Review' \
  --priority MEDIUM \
  --description '{\"agentInput\": {\"content\": <CONTENT_JSON>, \"metadata\": {\"skipAutomatedTesting\": true}}}' \
  --region us-east-1
```

> **关键提示：** `content` 值必须是一个单一对象 — 不能用列表包裹。正确：`"content": {"githubPrContent": [...]}`。错误：`"content": [{"githubPrContent": [...]}]`。用列表包裹会导致后端 Pydantic 验证失败。内容中的值应全部为字符串格式，例如 PR 编号应为字符串。

默认是 `"skipAutomatedTesting": true`（仅静态）。仅当用户明确选择启用自动测试时才设置为 `false`。

### 3. 轮询状态

```
aws devops-agent get-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --region us-east-1
```

每 **30 秒** 轮询一次，直到状态变为 `IN_PROGRESS` 或终端状态（`COMPLETED`, `FAILED`, `CANCELED`, `TIMED_OUT`）。

### 4. 监控直至完成

一旦 `IN_PROGRESS`，循环轮询进度：

```
aws devops-agent list-journal-records \
  --agent-space-id SPACE_ID \
  --execution-id EXEC_ID \
  --order ASC \
  --region us-east-1
```

1. 向用户友好地展示每条记录的进度更新。
2. 使用响应中的 `next_token` 在后续轮询中仅获取新记录。
3. **每次轮询迭代之间等待 15 秒**。
4. 定期检查 `get-backlog-task` — 当达到终端状态时停止。

### 5. 展示结果

一旦作业达到终端状态：

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
  4. **自动修复流程（强制要求）**：保存报告后，你必须尝试为所有可操作的已知风险生成并展示修复方案 — 这是审查工作流的主要价值，不是可选步骤。遵循上述核心工作流部分中描述的相同自动修复流程（定位仓库、验证分支、生成修复、推送到 `feat/release-readiness-fix`）。
- 如果 `FAILED` 或 `TIMED_OUT`：显示错误信息并建议后续步骤。
- 如果 `CANCELED`：告知用户作业已取消且无报告可用。

#### 取消（回退）

```
aws devops-agent update-backlog-task \
  --agent-space-id SPACE_ID \
  --task-id TASK_ID \
  --task-status CANCELED \
  --region us-east-1
```
