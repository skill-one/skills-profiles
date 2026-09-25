# 将 CI 失败问题转化为 GitHub 问题

调查失败的 GitHub Actions 任务，提取根本原因，并向 `NVIDIA/Megatron-LM` 提交结构良好的 Bug 问题。

## 工作流程

### 1. 解析 URL

参数是一个 GitHub Actions URL。它将是以下其中一种：

- **任务 URL**：`https://github.com/<owner>/<repo>/actions/runs/<run_id>/job/<job_id>`
- **运行 URL**：`https://github.com/<owner>/<repo>/actions/runs/<run_id>`

提取 `run_id`，如果存在，则提取 `job_id`。

### 2. 确定失败的任务

- 如果提供了 `job_id`，则直接使用该任务。
- 如果只提供了 `run_id`，则列出运行中所有失败的任务：

  ```bash
  gh run view <run_id> --repo NVIDIA/Megatron-LM --json jobs \
    --jq '[.jobs[] | select(.conclusion == "failure") | {id: .databaseId, name: .name, url: .url}]'
  ```

  如果多个任务失败，询问用户要调查哪个任务，或者如果他们表示全部调查，则调查所有任务。

### 3. 获取失败日志

对于每个失败的任务，检索日志并将其缩小到失败部分：

```bash
# 拉取原始日志并仅保留包含错误行的日志
gh api repos/NVIDIA/Megatron-LM/actions/jobs/<job_id>/logs 2>&1 \
  | grep -E "(FAILED|ERROR|\bError\b|assert|Traceback|Exception|##\[error\])" \
  | head -200
```

同时捕获完整的任务名称：

```bash
gh run view --job <job_id> --repo NVIDIA/Megatron-LM --json name --jq .name
```

如果 `grep` 输出稀疏，则下载完整日志并查找 pytest 的 `FAILURES` 部分或最后一个非零退出信号。

### 4. 解决触发 PR 和测试作者

**触发 PR**：运行的头分支遵循 `pull-request/<number>` 模式。提取它并解决 PR：

```bash
gh run view <run_id> --repo NVIDIA/Megatron-LM --json headBranch --jq .headBranch
# → 例如 "pull-request/4332"
# 提取 PR 编号并获取元数据：
gh pr view <pr_number> --repo NVIDIA/Megatron-LM --json number,title,url \
  --jq '{number: .number, title: .title, url: .url}'
```

**测试文件作者**：找到最后修改失败测试文件的 GitHub 登录名。文件可能不存在于 `main` 上 — 首先确定 PR 的基础分支，然后从那里搜索：

```bash
# 1. 获取 PR 的基础分支（例如 "main"、"dev"、"release/X.Y"）
gh pr view <pr_number> --repo NVIDIA/Megatron-LM --json baseRefName --jq .baseRefName

# 2. 在该基础分支上搜索提交
gh api "repos/NVIDIA/Megatron-LM/commits?path=<test-file-path>&sha=<base-branch>&per_page=1" \
  --jq '.[0] | {login: .author.login, name: .commit.author.name, sha: .sha}'
```

如果结果为空（文件由 PR 本身引入），则查询 PR 的提交：

```bash
gh api "repos/NVIDIA/Megatron-LM/pulls/<pr_number>/commits" \
  --jq '[.[] | select(.files? // [] | any(.filename == "<test-file-path>"))] | .[0].author.login'
```

作为最后的手段，列出 PR 提交并选择与失败测试文件最相关的提交的作者。

### 5. 提取根本原因

从日志中识别：

- **失败的测试**：匹配 `FAILED tests/...::...` 的行给出 pytest 的确切节点 ID。
- **错误消息**：断言失败、异常类型或第一个有意义的回溯帧 — 保持长度在 ~30 行以内。
- **任务名称**：GitHub Actions 任务名称（例如 `tests/unit_tests/transformer/moe/**/*.py - latest`）。
- **运行 / 任务 URL** 和 **PR URL**：用于在问题中链接。

### 6. 检查重复问题

搜索已打开的问题，这些问题已经涵盖了相同的测试：

```bash
gh issue list --repo NVIDIA/Megatron-LM \
  --state open \
  --search "<failed-test-filename>" \
  --json number,title,url \
  --limit 10
```

- 如果存在匹配的打开问题，**不要创建新问题**。向用户报告现有问题并停止。
- 如果未找到匹配项，则继续创建新问题。

### 7. 创建问题

将 `--assignee <test-author-login>` 传递给分配给测试文件作者的 issue。在 issue 正文包含触发 PR URL。

```bash
gh issue create \
  --repo NVIDIA/Megatron-LM \
  --title "🐛 CI 失败：<failed-test-node-id>" \
  --label "bug" \
  --assignee "<test-author-login>" \
  --body "..."
```

使用 Bug 报告模板正文结构：

```markdown
**描述问题**

CI 测试 `<failed-test-node-id>` 在任务 [`<job-name>`](<job-url>) 中失败。
@NVIDIA/mcore-oncall 标签以引起 oncall 的注意。

**失败的运行**

| 字段 | 值 |
|------|----|
| PR   | [#<pr_number>: <pr_title>](<pr_url>) |
| 运行 | [<run_id>](<run_url>) |
| 任务 | [<job_name>](<job_url>) |

**错误**

```
<核心错误消息 / 回溯 — 最大 30 行>
```

**复现步骤/代码**

重新运行上述链接的失败 CI 任务，或在开发容器中本地运行：

```bash
pytest <failed-test-node-id>
```

**附加上下文**

通过 `/triage-issue` 自动调查。
```

如果同一任务中多个测试失败，则在 "描述问题" 下为每个测试列出单独的要点，并包含组合的错误片段。将 issue 分配给失败列表中首先出现的测试文件的作者。

### 8. 向用户报告

打印新创建的 issue URL（或找到的重复 issue），以便用户可以查看或分享。

## 重要指南

- 如果已存在重复问题，则**不要创建新问题** — 而是链接现有问题。
- 始终在 issue 正文包含触发 PR 链接。
- 始终将 issue 分配给测试文件的最新的作者。如果作者查找失败（例如，提交由机器人完成或登录名不可用），则跳过 `--assignee` 并在 "附加上下文" 部分注明。
- 保持错误片段简洁（≤30 行）。截断长回溯并注明完整日志可通过任务 URL 获取。
- 不要猜测根本原因 — 逐字引用实际的日志输出。
- 如果任务仍在进行中或日志不可用，请说明并要求用户在运行完成后重试。
