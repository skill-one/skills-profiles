---
name: review-agent-setup
description: 在Claude Code中为AI代理的审核操作配置人工介入的网关。在设置项目时使用，当代理可能发布PR审核、评论、合并或编辑CI配置，并且您需要一个经过Cedar强制执行的、具有加密审计能力的批准路径时。
---

# review-agent-governance — 设置

在明确的人工批准后，为 Gate AI 代理的审查操作（PR 审查、评论、合并、CI 编辑）启用。每次尝试，无论批准还是拒绝，都会生成一个 Ed25519 签名的收据。

## 何时使用此插件

在以下项目中安装它，其中 Claude Code 代理：

- 审查、评论或合并拉取请求（`gh pr review`，`gh pr merge`）
- 分配问题（`gh issue comment`，`gh issue close`）
- 发布发布（`gh release create`）
- 修改 CI 配置（`.github/workflows/`，`.gitlab-ci.yml`）
- 推送到受保护分支（`main`，`master`，`release`，`production`）
- 发布到外部通知表面（Slack webhooks，Discord），一旦您为发布命令添加了规则（默认策略不限制它们）

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
echo "/review-receipts/" >> .gitignore
echo "/review-governance.key" >> .gitignore
echo "/.review-approved" >> .gitignore
if [ ! -e ./review-governance.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./review-governance.key
fi
```

protect-mcp 0.7.4 `sign` 不会创建密钥，因此最后一个命令会创建它，并且永远不会替换现有密钥。没有密钥，收据将是未签名的。要轮换密钥，请先存档 `./review-governance.key` 和 `./review-receipts/receipts.jsonl`，然后再次运行命令。将 `publicKey` 值从 `./review-governance.key` 分发给审计员。不要提交该文件，因为它还包含私钥。

## 每次会话的工作流程

Cedar 策略无条件拒绝审查表面操作。要批准特定操作，请在操作之前打开批准窗口，并在之后关闭它。

### 标志文件（最简单）

```bash
# 在您要批准的操作之前
touch ./.review-approved

# 让 Claude Code 运行审查 / 评论 / 合并

# 立即之后
rm ./.review-approved
```

### 前缀命令（在 Claude Code 内）

```
/approve-review "审查 PR #123 由贡献者 X 编写"
```

这会创建 `./.review-approved`，并将给定的原因嵌入为注释，并将原因记录在 `./review-receipts/approvals/` 下的未签名批准日志中。仍然需要后续的 `rm` 来关闭窗口。

### 模拟运行所有操作（强制完整策略评估）

如果您希望每个工具调用都通过 Cedar 而没有任何批准绕过：

```bash
export REVIEW_APPROVAL_FLAG=./.never-approve
```

任何匹配禁止规则的工具调用都将被拒绝；批准窗口没有任何效果。适用于 CI 或锁定审计运行。

## 验证收据

列出所有收据：

```bash
ls -la ./review-receipts/
```

使用公钥离线验证每个收据：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./review-governance.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./review-receipts/receipts.jsonl --key "$PUB"
```

退出码 0 表示每个收据都通过验证。退出码 1 表示收据验证失败，因为它被篡改、密钥错误或某行格式不正确。退出码 2 表示收据文件无法读取。

被拒绝的调用不会运行，因此没有收据。要在 Claude Code 内查看策略阻止的内容，请运行此命令：

```
/list-pending
```

它列出了 PreToolUse 钩子在当前会话中阻止的工具调用，包括工具名称和命令或路径。

## 示例：批准 PR 审查

```bash
# 1. 人工审查代理建议的评论
$ /list-pending
  本会话中阻止的操作：
  - Bash "gh pr review 42 --approve --body 'LGTM'"
  - Bash "gh pr comment 42 --body 'Looking good'"

# 2. 人工决定第一个是适当的，批准它
$ /approve-review "在视觉检查后批准 PR 42 的 LGTM"
  ./.review-approved 创建

# 3. 代理重试操作；这次成功了
$ agent: gh pr review 42 --approve --body "LGTM"
  [收据附加到 ./review-receipts/receipts.jsonl，决策=允许]

# 4. 人工关闭窗口
$ rm ./.review-approved
```

允许的调用有一个已签名的收据，任何拥有公钥的人都可以离线验证。被拒绝的尝试没有收据，并且批准日志未签名，因此请记住这两点，当您向审计员展示轨迹时。

## 与 protect-mcp 组合

如果两个插件都已安装，每个插件的 `hooks/hooks.json` 都注册自己的 PreToolUse 钩子，Claude Code 在每个工具调用时都会运行两个：

```json
{ "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/evaluate.sh" }
```

每个 `evaluate.sh` 都从标准输入的钩子负载中读取 `tool_name` 和 `tool_input`（Claude Code 不设置 `TOOL_NAME` 变量），并评估自己的策略：`./protect.cedar`（protect-mcp）和 `./review-governance.cedar`。

两个钩子都必须通过，工具调用才能继续。任一策略中的 Cedar 拒绝都会阻止它。

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开放授权策略语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)
