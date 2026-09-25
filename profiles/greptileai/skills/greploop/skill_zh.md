# Greploop

迭代修复 PR/MR/CL，直到 Greptile 给出完美评审：5/5 置信度，零未解决的评论。

## 输入

- **PR/MR/CL 编号**（可选）：如果未提供，将检测当前分支的 PR/MR，或 p4 的默认待处理变更列表。

## 说明

### 0. 检测平台

首先检查 Perforce，然后回退到 git 远程检测：

```bash
# 检查 Perforce 环境
if p4 info >/dev/null 2>&1; then
  VCS="perforce"
else
  REMOTE_URL=$(git remote get-url origin)
  if echo "$REMOTE_URL" | grep -qi "gitlab"; then
    VCS="gitlab"
  else
    VCS="github"
  fi
fi
```

对于主机名不包含 "gitlab" 的自托管 GitLab 实例，用户可以通过传递 `--vcs gitlab` 作为输入来覆盖。对于 Perforce，传递 `--vcs perforce`。

### 1. 识别 PR/MR/CL

**GitHub:**
```bash
gh pr view --json number,headRefName -q '{number: .number, branch: .headRefName}'
```

**GitLab:**
```bash
glab mr view --output json | jq '{iid: .iid, branch: .source_branch}'
```

如果尚未在 PR/MR 分支上，请切换到该分支。

**Perforce:**
```bash
# 列出当前用户/客户端的待处理变更列表
p4 changes -s pending -u $P4USER -c $P4CLIENT

# 描述特定的 CL
p4 describe -s <CL_NUMBER>
```

确保在继续之前设置正确的工区（`p4 client`）。

关键字段差异：
- GitHub: `number`, `headRefName`, `headRefOid`
- GitLab: `iid`, `source_branch`, `sha`
- Perforce: 变更列表编号, `P4CLIENT`, 暂存文件

### 2. 循环

重复以下循环。**最多 5 次迭代**以避免无限循环。

#### A. 触发 Greptile 评审

推送/暂存最新更改（如果有）：

**GitHub/GitLab:**
```bash
git push
```

**Perforce:**
```bash
# 重新暂存以更新用于评审的暂存文件
p4 shelve -f -c <CL_NUMBER>
```

推送/暂存后等待检查开始：

```bash
sleep 5
```

**GitHub** — 在发布新的触发评论之前，检查 Greptile 是否已经在运行：

```bash
GREPTILE_STATE=$(gh pr checks <PR_NUMBER> --json name,state | jq -r '.[] | select(.name | test("greptile"; "i")) | .state')
```

如果 Greptile **尚未**运行（`PENDING` 或 `IN_PROGRESS`），请求新的评审：

```bash
if [ "$GREPTILE_STATE" != "PENDING" ] && [ "$GREPTILE_STATE" != "IN_PROGRESS" ]; then
  gh pr comment <PR_NUMBER> --body "@greptile review"
fi
```

然后轮询 Greptile 检查运行以完成：

```bash
HEAD_SHA=$(gh pr view <PR_NUMBER> --json headRefOid -q .headRefOid)
ATTEMPTS=0
MAX_ATTEMPTS=60
POLL_INTERVAL_SECONDS=10

while true; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -gt "$MAX_ATTEMPTS" ]; then
    echo "Timed out waiting for the Greptile check run after approximately 10 minutes." >&2
    exit 1
  fi

  GREPTILE_CHECK=$(gh api "repos/{owner}/{repo}/commits/$HEAD_SHA/check-runs" \
    --jq '.check_runs[] | select(.name | test("greptile"; "i"))' 2>/dev/null)
  
  if [ -z "$GREPTILE_CHECK" ]; then
    echo "Waiting for Greptile check to appear..."
    sleep "$POLL_INTERVAL_SECONDS"
    continue
  fi
  
  STATUS=$(echo "$GREPTILE_CHECK" | jq -r '.status // "completed"')
  CONCLUSION=$(echo "$GREPTILE_CHECK" | jq -r '.conclusion // "pending"')
  
  if [ "$STATUS" = "completed" ]; then
    if [ "$CONCLUSION" = "success" ]; then
      echo "Greptile check passed!"
    else
      echo "Greptile check completed with: $CONCLUSION"
    fi
    break
  fi
  
  echo "Waiting for Greptile... (status: $STATUS)"
  sleep "$POLL_INTERVAL_SECONDS"
done
```

如果轮询超时，请停止 greploop 工作流程并报告超时。不要继续使用陈旧或缺失的评审结果。

**GitLab** — 在发布触发评论之前，检查 Greptile 是否已经在运行：

```bash
PIPELINES=$(glab api "projects/:fullpath/merge_requests/<MR_IID>/pipelines")
GREPTILE_RUNNING=$(echo "$PIPELINES" | jq '[.[] | select(.status == "running" or .status == "pending")] | length')
```

如果没有运行任何管道，请发布触发评论：

```bash
if [ "$GREPTILE_RUNNING" = "0" ]; then
  glab mr note <MR_IID> --message "@greptile review"
fi
```

**Perforce** — Perforce 没有原生的检查运行。如果通过在 `p4 shelve` 触发的 webhook 集成 Greptile，请等待它处理。检查您的 Greptile 安装的自定义 webhook 端点或仪表板以获取评审状态。通过重新获取 CL 上的 Greptile 评审评论来轮询，直到出现分数。

然后轮询 Greptile 管道作业以完成（见 [GitLab API 参考](references/gitlab-api.md)）：

```bash
HEAD_SHA=$(glab mr view <MR_IID> --output json | jq -r '.sha')
ATTEMPTS=0
MAX_ATTEMPTS=60
POLL_INTERVAL_SECONDS=10

while true; do
  ATTEMPTS=$((ATTEMPTS + 1))
  if [ "$ATTEMPTS" -gt "$MAX_ATTEMPTS" ]; then
    echo "Timed out waiting for the Greptile pipeline job after approximately 10 minutes." >&2
    exit 1
  fi

  PIPELINES=$(glab api "projects/:fullpath/merge_requests/<MR_IID>/pipelines")
  # 查找此 SHA 的最新管道
  PIPELINE_ID=$(echo "$PIPELINES" | jq -r --arg sha "$HEAD_SHA" \
    '[.[] | select(.sha == $sha)] | sort_by(.id) | last | .id // empty')

  if [ -z "$PIPELINE_ID" ]; then
    echo "Waiting for Greptile pipeline to appear..."
    sleep "$POLL_INTERVAL_SECONDS"
    continue
  fi

  JOBS=$(glab api "projects/:fullpath/pipelines/$PIPELINE_ID/jobs")
  GREPTILE_JOB=$(echo "$JOBS" | jq '.[] | select(.name | test("greptile"; "i"))')

  if [ -z "$GREPTILE_JOB" ]; then
    echo "Waiting for Greptile job to appear..."
    sleep "$POLL_INTERVAL_SECONDS"
    continue
  fi

  JOB_STATUS=$(echo "$GREPTILE_JOB" | jq -r '.status')

  if [ "$JOB_STATUS" = "success" ] || [ "$JOB_STATUS" = "failed" ] || [ "$JOB_STATUS" = "canceled" ]; then
    echo "Greptile job completed with: $JOB_STATUS"
    break
  fi

  echo "Waiting for Greptile... (status: $JOB_STATUS)"
  sleep "$POLL_INTERVAL_SECONDS"
done
```

如果轮询超时，请停止 greploop 工作流程并报告超时。不要继续使用陈旧或缺失的评审结果。

#### B. 获取 Greptile 评审结果

Greptile 可能在多个位置显示其分数——检查所有相关的来源：

**GitHub:**

**1. PR 描述（正文）:**
```bash
gh pr view <PR_NUMBER> --json body -q '.body'
```

**2. 一般 PR 评论（问题评论）:**
```bash
gh api --paginate "repos/{owner}/{repo}/issues/<PR_NUMBER>/comments?per_page=100"
```

过滤 Greptile 生成的评论，并使用最新更新的评论的正文（`updated_at`），而不是最新创建的评论。Greptile 可能会在每个评审周期中编辑相同的普通 PR 评论；在确定没有剩余问题之前，解析当前正文，包括“使用 AI 修复所有问题”部分。

**3. PR 评审:**
```bash
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/reviews
```

查找来自 `greptile-apps[bot]` 或 `greptile-apps-staging[bot]` 的最新条目。

**GitLab:**

**1. MR 描述（正文）:**
```bash
glab mr view <MR_IID> --output json | jq -r '.description'
```

**2. MR 笔记（评论）:**
```bash
glab api "projects/:fullpath/merge_requests/<MR_IID>/notes"
```

过滤来自 Greptile 机器人用户的笔记（检查 `author.username` 字段——确切的用户名可能因安装而异；首次运行时请验证）。

**Perforce:**

**1. CL 描述:**
```bash
p4 describe -s <CL_NUMBER>
```
检查描述字段中的 Greptile 追加的分数块。

**2. CL 评论 / 评审笔记:**
如果您的安装使用 Helix Swarm 等评审工具，请通过其 API 获取评论。

示例（Swarm API）:
GET /api/v11/comments?topic=reviews/<REVIEW_ID>

感兴趣的响应字段通常包括：
- user（作者用户名）
- body（评论文本）
- flags/state 指示评论是否已解决

过滤由 Greptile 机器人编写的评论：
- 如果已知，请使用确切的用户名匹配
- 否则，使用启发式方法，其中作者姓名包含 "greptile"（不区分大小写）

对于所有平台，解析文本以获取：
- **置信度分数**：类似于 `3/5` 或 `5/5`（或 `Confidence: 3/5`）的模式。
- **评论数量**：摘要中注明的内联评审评论数量。

使用具有 **最新更新** 分数的来源。对于 GitHub，在比较编辑的 Greptile 摘要和旧评审条目时，优先使用来自问题评论的 `updated_at`。

同时获取所有未解决的内联评论：

**GitHub:**
```bash
gh api repos/{owner}/{repo}/pulls/<PR_NUMBER>/comments
```

同时获取最新 Greptile 一般 PR 评论中的可操作项，特别是“使用 AI 修复所有问题”部分，即使内联评论端点返回零未解决评论。

**GitLab:**
```bash
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions"
```

过滤为 `DiffNote` 类型讨论（`notes[0].type == "DiffNote"`）的 Greptile，这些讨论在最新提交上，尚未解决（`"resolved": false`）。

**Perforce:**
如果使用 Swarm：

# 获取与 CL 相关的评审的内置差异评论
GET /api/v11/comments?topic=reviews/<REVIEW_ID>

过滤来自 Greptile 机器人用户且未标记为已解决/处理的评论。

#### C. 检查退出条件

如果满足以下任一条件，请停止循环：

- 置信度分数为 **5/5** 并且 **零未解决的评论**
- 达到最大迭代次数（报告当前状态）

#### D. 修复可操作评论

对于每个未解决的 Greptile 评论：

1. 读取文件并理解评论的上下文。
2. 确定它是可操作的（需要代码更改）还是信息性的。
3. 如果可操作，请进行修复。
4. 如果是信息性的或误报，请记录但仍然解决线程。

#### E. 解决线程

**GitHub** — 获取未解决的评审线程并解决所有已处理的线程（见 [GraphQL 参考](references/graphql-queries.md)）：

```bash
gh api graphql -f query='
query($cursor: String) {
  repository(owner: "OWNER", name: "REPO") {
    pullRequest(number: PR_NUMBER) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id
          isResolved
          comments(first: 1) {
            nodes { body path author { login } }
          }
        }
      }
    }
  }
}'
```

解决已处理的线程：

```bash
gh api graphql -f query='
mutation {
  t1: resolveReviewThread(input: {threadId: "ID1"}) { thread { isResolved } }
  t2: resolveReviewThread(input: {threadId: "ID2"}) { thread { isResolved } }
}'
```

**GitLab** — 获取未解决的讨论并解决每个（见 [GitLab API 参考](references/gitlab-api.md)）：

```bash
glab api "projects/:fullpath/merge_requests/<MR_IID>/discussions?per_page=100"
```

过滤为 `"resolved": false` 的讨论。然后通过其 `id` 解决每个：

```bash
glab api --method PUT \
  "projects/:fullpath/merge_requests/<MR_IID>/discussions/<DISCUSSION_ID>" \
  --field resolved=true
```

对每个未解决的讨论 ID 重复此操作。（GitLab 没有批量解决——循环每个。）
