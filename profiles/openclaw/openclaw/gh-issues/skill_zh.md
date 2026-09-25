# gh-issues

用于问题到 PR 的自动化。优先使用 `gh` CLI；仅在高级命令缺少所需字段时才回退到 `gh api`。

## 参数

- 位置参数 `owner/repo`：可选；否则从 `git remote get-url origin` 推断。
- `--label <label>`：过滤。
- `--limit <n>`：默认 10。
- `--milestone <title>`：过滤。
- `--assignee <login|@me>`：过滤。
- `--state open|closed|all`：默认 open。
- `--fork <owner/repo>`：将分支推送到分支，PR 推送到源。
- `--watch`：轮询问题和评审。
- `--interval <minutes>`：默认 5。
- `--dry-run`：仅列出。
- `--yes`：无需确认。
- `--reviews-only`：跳过问题修复；处理 PR 评审。
- `--cron`：启动并退出；隐含 `--yes`。
- `--model <id>`：在支持时传递给工作进程。
- `--notify-channel <id>`：可选的最终通知目标。

## 第一阶段：解析仓库

```bash
git remote get-url origin
if [ -z "${GH_TOKEN:-}" ]; then
  CONFIG_PATH="${OPENCLAW_CONFIG_PATH:-${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/openclaw.json}"
  GH_TOKEN=$(jq -r '.skills.entries["gh-issues"].apiKey // empty' "$CONFIG_PATH" 2>/dev/null || true)
  if [ -n "$GH_TOKEN" ]; then export GH_TOKEN; fi
fi
gh auth status
gh repo view OWNER/REPO --json nameWithOwner,defaultBranchRef
```

如果 `gh auth status` 失败且 `GH_TOKEN` 缺失，停止并请求 GitHub 认证/配置。

派生：

- `SOURCE_REPO`：问题仓库。
- `PUSH_REPO`：如果设置，则分支，否则源。
- `BASE_BRANCH`：除非用户另有说明，否则为源默认分支。
- `PUSH_REMOTE`：分支模式下为 `fork`，否则为 `origin`。

除非用户确认工作进程应忽略未提交的更改，否则在脏工作区时停止。

在分支模式下，在确认之前或 `--dry-run` 期间，不要修改远程。

仅验证认证/读取访问权限：

```bash
gh auth token >/dev/null || test -n "${GH_TOKEN:-}"
gh repo view "$PUSH_REPO" --json nameWithOwner
git ls-remote --exit-code origin HEAD
```

## 第二阶段：获取问题

构建过滤器并获取：

```bash
gh issue list --repo "$SOURCE_REPO" --state open --limit 10 --json number,title,labels,url,body,assignees,milestone
```

根据请求添加 `--label`、`--milestone`、`--assignee`、`--state`、`--limit`。`gh issue list` 已排除 PR。

如果没有找到：报告无匹配项。如果 `--dry-run`：显示紧凑列表并停止。

## 第三阶段：避免重复工作

对于每个候选：

```bash
gh pr list --repo "$SOURCE_REPO" --search "$SOURCE_REPO#<n>" --state open --json number,url,title,headRefName
gh pr list --repo "$SOURCE_REPO" --head "fix/issue-<n>" --state open --json number,url
gh api "repos/$PUSH_REPO/branches/fix/issue-<n>" >/dev/null
```

跳过具有打开 PR、现有分支或活动本地声明的候选。

声明文件：

```text
${OPENCLAW_STATE_DIR:-$HOME/.openclaw}/gh-issues-<owner>-<repo>.json
```

过期 2 小时以上的声明。
在写入之前创建父目录。

## 第四阶段：确认

除非 `--yes` 或 `--cron`，否则请求用户选择：

- `all`
- 用逗号分隔的问题编号
- `cancel`

确认后，在分支模式下，在将工作交给代理之前，配置推送远程：

```bash
gh auth setup-git
git remote get-url fork || git remote add fork "https://github.com/$PUSH_REPO.git"
git remote set-url fork "https://github.com/$PUSH_REPO.git"
git ls-remote --exit-code fork HEAD
```

## 第五阶段：启动工作进程

启动最多 8 个后台工作进程。在 `--cron` 时不要阻塞每个工作进程。

在每次启动之前，使用当前 ISO 时间戳为 `SOURCE_REPO#<n>` 写入声明。在工作进程报告 PR/失败后，删除或更新声明。这可防止在分支或 PR 存在之前轮询/cron 重叠。

工作进程提示必须包括：

- 问题 URL、标题、正文、标签。
- `SOURCE_REPO`、`PUSH_REPO`、`BASE_BRANCH`、`PUSH_REMOTE`、分支模式。
- 目标分支 `fix/issue-<n>`。
- 必需的证明和 PR 正文。
- 通知路线。

工作进程指令：

```text
使用 gh 和 git。不要含糊其辞。
从 BASE_BRANCH 检出/创建 fix/issue-<n>。
实现最小修复。
运行相关测试。
使用常规消息提交。
推送到 PUSH_REMOTE。
对 SOURCE_REPO BASE_BRANCH 打开 PR。
PR 正文：解决了什么问题 + 为什么做出此更改 + 用户影响 + 证据 + 可见修复 SOURCE_REPO#<n>。
报告 PR URL 或失败原因。
如果提供路线，使用 openclaw message send 发送完成/失败。
```

在可用时使用 `coding-agent` 启动规则。

## 第六阶段：收集

使用 `process` 或任务注册表轮询工作进程。报告：

- 问题编号 + 标题。
- 状态：PR 打开、跳过、失败、超时。
- PR URL 或原因。

仅使用最终紧凑摘要通知通道。

## 仅评审 / 轮询评审

发现打开的 PR：

```bash
gh pr list --repo "$SOURCE_REPO" --state open --json number,title,url,headRefName,reviewDecision \
  --jq '[.[] | select(.headRefName | startswith("fix/issue"))]'
```

获取评审线程/评论：

```bash
gh pr view <n> --repo "$SOURCE_REPO" --json url,headRefName,comments,reviews
gh api "repos/$SOURCE_REPO/pulls/<n>/comments"
gh api "repos/$SOURCE_REPO/issues/<n>/comments"
```

除非用户明确命名 PR 编号，否则仅处理由此工作流程创建的 `fix/issue-*` PR。按 PR 分组可操作的评论。忽略赞扬、状态、重复和已处理的评论。为每个选定的/范围的 PR 启动一个工作进程，相同的后台规则。

评审工作进程指令：

```text
检出 PR 分支。
阅读所有可操作的评审评论。
进行最小更改。
运行相关测试。
正常提交和推送；除非明确指示，否则不要强制推送。
对已处理的评论回复修复 + 提交/文件引用。
报告已处理的评论/跳过和证明。
```

## 轮询模式

循环：

1. 获取问题。
2. 启动符合条件的问题工作进程。
3. 处理可操作的 PR 评审。
4. 休眠 `--interval`。
5. 用户停止时停止。

保持累积摘要紧凑。
