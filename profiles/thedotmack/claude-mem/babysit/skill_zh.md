# 临时照看 PR

持续关注 PR，直到它真正变为干净状态。不要在评论或评审线程仍有未解决的问题时停止。

## 工作流程

1. 识别 PR 编号、分支和基础分支。
2. 确认 PR 不是草稿，并检查合并性、检查项、评审决定、评论和评审线程。
3. 关注待处理的检查，直到它们完成。以实际间隔轮询，通常是 30-60 秒，除非用户要求不同的节奏。
4. 阅读新评论和未解决的评审线程。将机器人摘要视为有用信息，但需对照代码验证可操作的发现。
5. 在专注的提交中修复真实问题，运行相关测试/构建，推送，然后返回步骤 2。
6. 只有在验证代码或生成的工件现在已解决评论后，才解决过时的评审线程。
7. 只有在检查通过或有意跳过、评审决定可接受、无可操作的评论剩余、无未解决的评审线程剩余时才停止。

## GitHub CLI 检查

使用 `gh pr view` 查看粗略状态：

```bash
gh pr view <number> --json \
  number,state,isDraft,mergeable,mergeStateStatus,reviewDecision,headRefOid,statusCheckRollup,url
```

在使用 GraphQL 之前解决仓库所有者/名称：

```bash
repo_json=$(gh repo view --json owner,name)
owner=$(jq -r '.owner.login // .owner.name' <<<"$repo_json")
repo=$(jq -r '.name' <<<"$repo_json")
```

使用 GraphQL 查询未解决的评审线程。包含 `pageInfo`；在第一页时省略 `cursor`，然后当 `hasNextPage` 为 `true` 时，使用 `-f cursor="$cursor"` 传递前一个 `endCursor`。

```bash
gh api graphql \
  -f query='query($owner:String!,$repo:String!,$number:Int!,$cursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100,after:$cursor){pageInfo{hasNextPage endCursor}nodes{id,isResolved,isOutdated,path,line,comments(last:1){nodes{author{login},body,createdAt,url}}}}}}}' \
  -f owner="$owner" -f repo="$repo" -F number=<number>
```

当 PR 可能有许多评审线程时，使用此循环：

```bash
thread_query='query($owner:String!,$repo:String!,$number:Int!,$cursor:String){repository(owner:$owner,name:$repo){pullRequest(number:$number){reviewThreads(first:100,after:$cursor){pageInfo{hasNextPage endCursor}nodes{id,isResolved,isOutdated,path,line,comments(last:1){nodes{author{login},body,createdAt,url}}}}}}}'
cursor_args=()

while :; do
  page=$(gh api graphql -f query="$thread_query" -f owner="$owner" -f repo="$repo" -F number=<number> "${cursor_args[@]}")
  printf '%s\n' "$page" | jq -r '.data.repository.pullRequest.reviewThreads.nodes[]
    | select(.isResolved==false)
    | [.id,.path,(.line//""),(.isOutdated|tostring),(.comments.nodes[-1].author.login//""),(.comments.nodes[-1].body|gsub("\n";" ")|.[0:240])]
    | @tsv'

  jq -e '.data.repository.pullRequest.reviewThreads.pageInfo.hasNextPage' >/dev/null <<<"$page" || break
  cursor=$(jq -r '.data.repository.pullRequest.reviewThreads.pageInfo.endCursor' <<<"$page")
  cursor_args=(-f cursor="$cursor")
done
```

使用 `jq` 过滤未解决的线程：

```bash
jq -r '.data.repository.pullRequest.reviewThreads.nodes[]
  | select(.isResolved==false)
  | [.id,.path,(.line//""),(.isOutdated|tostring),(.comments.nodes[-1].author.login//""),(.comments.nodes[-1].body|gsub("\n";" ")|.[0:240])]
  | @tsv'
```

只有当修复已验证时才解决过时的线程：

```bash
gh api graphql \
  -f query='mutation($threadId:ID!){resolveReviewThread(input:{threadId:$threadId}){thread{id,isResolved}}}' \
  -f threadId=<thread-id>
```

## 操作规则

- 在长检查待处理时保持监视器运行。
- 如果生成的文件是分发的一部分，则在解决评论前验证源代码和生成的工件是否一致。
- 如果机器人报告了针对过时代码的问题，确认线程是否已过时或在最新主分支中已解决。
- 在最终报告前，对 PR 状态、未解决的线程、最近评论和本地 `git status` 进行一次新鲜扫描。
- 报告具体证据：最新提交 SHA、检查名称和结果、未解决线程数量、运行的测试以及任何未更改的脏本地文件。
