# review-agent-governance — 设置

在明确的人工批准后，为 Gate AI 代理的审查操作（PR 审查、评论、合并、CI 编辑）启用操作。每次尝试，无论批准还是拒绝，都会生成一个 Ed25519 签名的收据。

## 使用此插件的场景

在以下项目中安装它，其中 Claude Code 代理：

- 审查、评论或合并拉取请求（`gh pr review`，`gh pr merge`）
- 分配问题（`gh issue comment`，`gh issue close`）
- 发布发布（`gh release create`）
- 修改 CI 配置（`.github/workflows/`，`.gitlab-ci.yml`）
- 推送到受保护分支（`main`，`master`，`release`，`production`）
- 发布到外部通知表面（Slack webhooks，Discord）

如果代理仅进行本地文件编辑和运行测试，则此插件过于复杂。使用 `protect-mcp` 进行通用工具调用策略执行，并跳过此插件。

## 一次性设置

### 1. 安装插件

```bash
claude plugin install wshobson/agents/review-agent-governance
```

### 2. 将默认策略复制到您的项目

```bash
cp .claude/plugins/review-agent-governance/policies/review-agent-governance.cedar \
   ./review-governance.cedar
```

您可以编辑此文件以匹配您项目的特定规则。有关编写审查策略的指导，请参阅 `../agents/review-policy-author.md`。

### 3. 创建收据目录和签名密钥

```bash
mkdir -p ./review-receipts
echo "./review-receipts/" >> .gitignore
echo "./review-governance.key" >> .gitignore
echo "./.review-approved" >> .gitignore
```

第一次调用 `protect-mcp sign` 将创建密钥。提交第一个收据的公钥，以便审计员可以稍后验证。

## 每次会话的工作流程

Cedar 策略无条件拒绝审查表面操作。要批准特定操作，请在操作之前打开批准窗口，并在之后关闭它。

### 标记文件（最简单）

```bash
# 在您要批准的操作之前
touch ./.review-approved

# 让 Claude Code 运行审查 / 评论 / 合并

# 立即之后
rm ./.review-approved
```

### 前缀命令（在 Claude Code 内部）

```
/approve-review "审查 PR #123 由贡献者 X 编写"
```

这会创建 `./.review-approved` 并将给定的原因嵌入为注释，并将人类批准的收据写入链。仍然需要后续的 `rm` 来关闭窗口。

### 模拟运行所有操作（强制完整策略评估）

如果您希望每个工具调用都通过 Cedar 而没有批准绕过：

```bash
export REVIEW_APPROVAL_FLAG=./.never-approve
```

任何匹配禁止规则的工具调用都将被拒绝；批准窗口无效。适用于 CI 或锁定审计运行。

## 验证链

列出所有收据：

```bash
ls -la ./review-receipts/
```

离线验证整个链：

```bash
npx @veritasacta/verify ./review-receipts/*.json
```

退出码 0 表示每个收据都是真实的，链是完整的。退出码 1 表示一个收据已被篡改。退出码 2 表示一个收据格式不正确。

查看最近的拒绝：

```
/list-pending
```

在 Claude Code 中，此前缀命令将遍历收据链并打印任何最近的 `decision: deny` 条目，包括工具名称、命令模式和时间戳。

## 示例：批准 PR 审查

```bash
# 1. 人类审查代理建议的评论
$ /list-pending
  Recent denials:
  - 2026-04-17T14:23:01Z  Bash "gh pr review 42 --approve --body 'LGTM'"
  - 2026-04-17T14:23:02Z  Bash "gh pr comment 42 --body 'Looking good'"

# 2. 人类决定第一个是适当的，批准它
$ /approve-review "在视觉检查后批准 PR 42 的 LGTM"
  ./.review-approved created

# 3. 代理重试操作；这次成功
$ agent: gh pr review 42 --approve --body "LGTM"
  [receipt: rec_XXX, decision=allow, reason=human_approved]

# 4. 人类关闭窗口
$ rm ./.review-approved
```

每一步都在收据链中。链是离线可验证的，供监管机构、交易对手或希望确认没有审查操作绕过人工门禁的下游审计员使用。

## 与 protect-mcp 组合

如果两个插件都已安装，每个插件的 `hooks/hooks.json` 都注册自己的 PreToolUse 钩子，Claude Code 在每个工具调用时都会运行两个：

```json
{ "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/evaluate.sh" }
```

每个 `evaluate.sh` 都从钩子有效负载的 stdin 读取 `tool_name` 和 `tool_input`（Claude Code 不设置 `TOOL_NAME` 变量），并评估自己的策略：`./protect.cedar` 为 protect-mcp，此处为 `./review-governance.cedar`。

两个钩子都必须通过，工具调用才能继续。任一策略中的 Cedar 拒绝都会阻止它。

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开放授权策略语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
