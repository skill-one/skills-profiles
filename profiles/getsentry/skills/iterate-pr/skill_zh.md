# 迭代 PR 直至 CI 通过

目标：修复可操作的 CI 失败和高/中优先级评审反馈。停止并报告人工审批、草稿就绪和合并就绪的关卡。

要求：
- 经过身份验证的 `gh`
- `uv`
- 目标仓库根目录作为当前工作目录
- 以技能根相对路径的脚本，例如 `scripts/fetch_pr_checks.py`

## 组合脚本

| 脚本 | 运行 | 输出 |
|------|-----|------|
| `scripts/fetch_pr_checks.py` | `uv run scripts/fetch_pr_checks.py [--pr NUMBER]` | JSON：`pr`, `summary`, `checks`, 失败片段 |
| `scripts/fetch_pr_feedback.py` | `uv run scripts/fetch_pr_feedback.py [--pr NUMBER]` | JSON 桶：`high`, `medium`, `low`, `bot`, `resolved` |
| `scripts/monitor_pr_checks.py` | `uv run scripts/monitor_pr_checks.py [--pr NUMBER]` | 终端标记加制表符分隔的检查 |
| `scripts/reply_to_thread.py` | `uv run scripts/reply_to_thread.py THREAD_ID BODY [...]` | JSON 回复结果 |

检查摘要字段包括 `failed`, `pending`, `actionable_pending` 和 `human_gate_pending`。

监控标记：
- `ALL_CHECKS_PASSED`
- `CHECKS_DONE_WITH_FAILURES`
- `NO_CHECKS_REGISTERED`
- `DRAFT_PR_WITH_NO_CHECKS`
- `CHECKS_BLOCKED_BY_REVIEW_GATE`

## 工作流

### 1. 确定 PR

运行：
```bash
gh pr view --json number,url,headRefName,isDraft,reviewDecision
```

停止当：
- 不存在 PR
- 草稿 PR 在监控宽限期后没有检查：报告 `DRAFT_PR_WITH_NO_CHECKS`

草稿规则：仅检查现有检查/反馈。除非被要求，否则不要标记为评审就绪。

### 2. 处理反馈

运行 `uv run scripts/fetch_pr_feedback.py [--pr NUMBER]`。

| 桶 | 操作 |
|------|-----|
| `high` | 修复 |
| `medium` | 修复 |
| `low` | 询问用户要处理哪个 |
| `bot` | 跳过信息性评论 |
| `resolved` | 跳过 |

反馈修复清单：
- 验证根本原因
- 搜索相关代码
- 修复所有实例
- 对于 `review_bot: true`：修复真实问题，解释误报

低优先级提示格式：
```text
发现 3 个低优先级建议：
1. [l] "考虑重命名此变量" - @reviewer 在 api.py:42
2. [nit] "可以使用列表推导式" - @reviewer 在 utils.py:18
3. [style] "添加一个文档字符串" - @reviewer 在 models.py:55

我应该处理哪个？("1,3", "all", 或 "none")
```

### 3. 检查 CI 状态

运行 `uv run scripts/fetch_pr_checks.py [--pr NUMBER]`。

| 状态 | 操作 |
|------|-----|
| `failed > 0` 且 `actionable_pending == 0` | 修复失败 |
| `actionable_pending > 0` | 等待；等待时轮询反馈 |
| `pending > 0` 且 `actionable_pending == 0` | 报告 `CHECKS_BLOCKED_BY_REVIEW_GATE` |
| 宽限期后没有检查 | 报告 `NO_CHECKS_REGISTERED` 或 `DRAFT_PR_WITH_NO_CHECKS` |
| 所有可操作的检查通过 | 运行 CI 后反馈检查 |

等待可操作的评审机器人：sentry, warden, cursor, bugbot, seer, codeql。
不要等待审批、`isDraft`、`REVIEW_REQUIRED`、Codecov 或信息性机器人。

### 4. 修复 CI 失败

对于每个失败：
1. 读取完整日志：`gh run view <run-id> --log-failed`
2. 从断言/异常/lint 规则追溯到源代码
3. 编辑前说明原因："因为 X 失败，受 Y 影响"
4. 搜索相关调用点/模式
5. 修复根本原因，而不是症状
6. 需要时添加聚焦的测试覆盖率

### 5. 本地验证，然后提交并推送

提交前：
- 测试修复：重跑特定测试
- lint/类型修复：重跑受影响的检查器
- 代码修复：重跑覆盖的测试
- 本地失败：推送前修复

```bash
git add <files>
git commit -m "fix: <描述性消息>"
git push
```

### 6. 监控 CI 并处理反馈

循环：
1. 运行 `uv run scripts/fetch_pr_checks.py`
2. 处理步骤 3 中的表格
3. 当 `actionable_pending > 0` 时，运行 `uv run scripts/fetch_pr_feedback.py`
4. 立即修复新的高/中优先级反馈
5. 如果有变更，验证、提交、推送，重启循环
6. 否则休眠 30 秒后重复
7. 检查通过后，等待 10 秒，再次获取反馈
8. 如果存在新的高/中优先级反馈，返回步骤 4

Claude Code 可选：通过 `MonitorTool` 运行 `uv run scripts/monitor_pr_checks.py`，设置 `persistent: false`；将超时设置为普通仓库 CI 持续时间。每次推送后重启监控。

## 退出条件

| 退出 | 条件 |
|------|------|
| 成功 | 可操作 CI 通过；CI 后反馈干净；低优先级选择已处理 |
| 询问用户 | 两次尝试后相同失败；反馈不明确；基础设施问题 |
| 停止 | 没有 PR；分支需要 rebase；没有检查；草稿无检查；仅剩人工关卡 |

## 回退

如果脚本失败，直接使用 `gh` CLI：
- `gh pr view --json number,url,headRefName,isDraft,reviewDecision`
- `gh pr checks --json name,state,bucket,description,link`
- `gh run view <run-id> --log-failed`
- `gh api repos/{owner}/{repo}/pulls/{number}/comments`
