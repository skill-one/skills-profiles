# 检查 GitHub 通知

检查 GitHub 通知、最近的 Issues 和最近的 PRs，针对一组监控的仓库。

## 触发条件

当用户要求检查通知、查看最新动态或检查监控仓库的更新时。

## 监控仓库

- `zilliztech/claude-context`
- `zilliztech/memsearch`
- `zilliztech/mcp-server-milvus`
- `langchain-ai/langchain-milvus`
- `milvus-io/milvus-haystack`
- `zilliztech/milvus-marketplace`
- `zilliztech/vector-graph-rag`

## 执行步骤

### 第 1 步：确定目标仓库

- 如果用户指定了特定仓库（例如，"check mcp-server-milvus"），则仅查询该仓库。通过部分名称与监控列表进行匹配。
- 如果未指定仓库，则查询所有监控仓库。

### 第 2 步：获取 GitHub 通知

针对每个目标仓库，获取未读通知：

```bash
gh api notifications --jq '[.[] | select(.repository.full_name == "REPO_NAME")] | sort_by(.updated_at) | reverse'
```

按原因将通知分为两个优先级等级：

**高优先级（优先显示，并附带详情）：**
- `mention` - 有人 @你
- `review_requested` - 请求 review
- `assign` - 分配给你

**中优先级（在高优先级之后显示）：**
- `author` - 你的 PR/Issue 更新
- `state_change` - 状态变更（已合并/已关闭）
- `comment` - 你的线程中的新评论

跳过 `subscribed` 和 `CheckSuite` 通知——这些是噪音。

### 第 3 步：获取最近的 Issues

针对每个目标仓库，获取过去 7 天内创建的 Issues：

```bash
gh api "repos/REPO_NAME/issues?state=all&sort=created&direction=desc&per_page=20&since=SEVEN_DAYS_AGO_ISO" --jq '[.[] | select(.pull_request == null)]'
```

- 使用 `date -d '7 days ago' -u +%Y-%m-%dT%H:%M:%SZ` 计算自日期。
- 如果一个仓库有超过 10 个最近的 Issues，仅显示最近的 10 个，并注明有多少被省略。
- **跳过已关闭的 Issues**——仅显示开放的 Issues。

### 第 4 步：获取最近的 PRs

针对每个目标仓库，获取过去 7 天内更新的 PRs：

```bash
gh api "repos/REPO_NAME/pulls?state=all&sort=updated&direction=desc&per_page=20" --jq '[.[] | select(.updated_at >= "SEVEN_DAYS_AGO_ISO")]'
```

- 如果一个仓库有超过 10 个最近的 PRs，仅显示最近的 10 个，并注明有多少被省略。
- **跳过已合并和已关闭的 PRs**——仅显示开放的 PRs。

### 第 5 步：输出格式

以中文输出。按仓库分组结果。在每个仓库内，按以下顺序显示：

```
## 📋 通知概览

### zilliztech/mcp-server-milvus

#### 🔴 高优先级通知
- [review_requested] PR #42: 添加新端点 - @someone 请求你 review (2h ago)
- [mention] Issue #38: Bug 报告 - @someone 在评论中提到了你 (5h ago)

#### 🟡 中优先级通知
- [author] PR #40: 你的 PR 标题 - 已合并 (1d ago)
- [comment] Issue #35: 讨论标题 - 3 条新评论 (3h ago)

#### 📝 最近 Issues (近 7 天，共 N 条)
- #50 [open] Issue 标题 (2h ago) by @user
- #49 [closed] Issue 标题 (1d ago) by @user

#### 🔀 最近 PRs (近 7 天，共 N 条)
- #48 [open] PR 标题 (3h ago) by @user
- #47 [merged] PR 标题 (2d ago) by @user

---
### 下一个仓库...
```

- 显示相对时间（例如，"2h ago"、"3d ago"）以提高可读性。
- 如果一个仓库在过去 7 天内没有通知、没有 Issues 和没有 PRs，显示 "✅ 暂无新动态" 并继续。
- 最后，显示总结行："共 X 条高优先级通知，Y 条中优先级通知，Z 条新 Issue，W 条新 PR"

## 注意事项

- 所有查询使用 `gh api`，这需要 `gh` CLI 进行认证。
- 不要将任何通知标记为已读。
- 7 天窗口是默认值。如果用户要求不同的时间范围（例如，"这个月"），请相应调整。
- 保持输出简洁。如果数据过多，优先考虑最新和最重要。
