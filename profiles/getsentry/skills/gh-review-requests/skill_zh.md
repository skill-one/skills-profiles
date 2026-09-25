# GitHub Review Requests

获取未读的 `review_requested` 通知，针对开放的（未合并的）PR，并按 GitHub 团队进行筛选。

**要求**：已通过 GitHub CLI (`gh`) 进行身份验证。

**要求**：需要 `uv` CLI 进行 Python 包管理，安装指南位于 https://docs.astral.sh/uv/getting-started/installation/

## 第 1 步：确定团队

如果用户未指定团队，则询问：

> 我应该按哪个 GitHub 团队进行筛选？ (例如 `streaming-platform`)

接受团队缩写（`streaming-platform`）或显示名称 ("Streaming Platform") — 在传递给脚本之前转换为小写连字符缩写形式。

## 第 2 步：运行脚本

```bash
uv run scripts/fetch_review_requests.py --org getsentry --teams <team-slug>
```

要按多个团队进行筛选，请传递逗号分隔的列表：

```bash
uv run scripts/fetch_review_requests.py --org getsentry --teams <team slugs>
```

### 脚本输出

```json
{
  "total": 3,
  "prs": [
    {
      "notification_id": "12345",
      "title": "feat(kafka): 添加重启代理的工作流",
      "url": "https://github.com/getsentry/ops/pull/19144",
      "repo": "getsentry/ops",
      "pr_number": 19144,
      "author": "bmckerry",
      "reasons": ["opened by: bmckerry"]
    }
  ]
}
```

`reasons` 将包含以下一项或两项：
- `"review requested from: <Team Name>"` — 该团队是请求的审阅者
- `"opened by: <login>"` — PR 作者属于团队成员

## 第 3 步：展示结果

以包含完整 URL 的 Markdown 表格形式显示结果：

| # | 标题 | URL | 原因 |
|---|-------|-----|--------|
| 1 | feat(kafka): 添加重启代理的工作流 | https://github.com/getsentry/ops/pull/19144 | opened by: evanh |

如果 `total` 为 0，则显示："未找到该团队的未读审阅请求。"

## 备用方案

如果脚本失败，请手动运行：

```bash
gh api notifications --paginate
```

然后针对每个 `review_requested` 通知，检查：
- `gh api repos/{repo}/pulls/{number}` — 如果 `state == "closed"` 或 `merged_at` 已设置，则跳过
- `gh api repos/{repo}/pulls/{number}/requested_reviewers` — 检查 `teams[].name`
- `gh api orgs/{org}/teams/{slug}/members` — 检查作者是否为成员
