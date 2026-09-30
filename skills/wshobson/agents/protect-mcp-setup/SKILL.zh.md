---
name: protect-mcp-setup
description: 配置Cedar策略执行和Ed25519签名收据，用于Claude代码工具调用。在设置需要加密审计追踪、策略门控工具执行或合规性准备好的代理操作证据的项目时使用。
---

# protect-mcp — 政策执行 + 签名回执

针对 Claude Code 每个工具调用的加密治理。每次调用都会在执行前与 Cedar 政策进行评估，并生成一个 Ed25519 签名的回执，任何人都可以离线验证。

## 概述

Claude Code 运行强大的工具：`Bash`、`Edit`、`Write`、`WebFetch`。默认情况下没有审计追踪，没有政策执行，也没有办法证明事后做了什么决定。`protect-mcp` 弥补了这三个方面的所有空白：

- **Cedar 政策**（AWS 的开放授权引擎）在执行前评估每个工具调用。Cedar 拒绝是权威的。
- **Ed25519 回执**记录运行的工具名称，并使用您的密钥签名。
- 通过 `npx @veritasacta/verify` 进行离线验证。无需服务器，无需账户，无需信任操作员。

## 问题

AI 代理做出的决策会影响金钱、安全和权利。Claude Code 会话日志记录了发生的事情，但日志是：

- 可变的——任何有访问权限的人都可以编辑它
- 未签名的——没有办法证明完整性
- 与操作员绑定——验证需要信任持有日志的人

对于合规环境（金融、医疗保健、受监管的研究），这并不充分。您需要防篡改的证据，并且可以由第三方在不信任您的情况下进行验证。

## 解决方案

将 `protect-mcp` 添加到您的 Claude Code 项目中：

```bash
# 1. 安装插件（添加钩子 + 技能到您的项目）
claude plugin install wshobson/agents/protect-mcp

# 2. 创建 ./protect.cedar（见下文）。插件会安装钩子。

# 3. 一次性创建签名密钥（protect-mcp 0.7.4 的 sign 命令不会创建它）。
#    现有密钥永远不会被替换。参见 references/receipt-format.md 以旋转密钥。
if [ ! -e ./protect-mcp.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./protect-mcp.key
fi
echo "/protect-mcp.key" >> .gitignore

# 4. 正常使用 Claude Code。现在每个工具调用都会被政策评估
#    并在 ./receipts/ 中生成签名回执。
```

## 钩子配置

安装插件会添加 `hooks/hooks.json` 中的钩子。每个钩子运行插件捆绑的脚本：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/evaluate.sh" }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hooks": [
          { "type": "command", "command": "\"${CLAUDE_PLUGIN_ROOT}\"/hooks/sign.sh" }
        ]
      }
    ]
  }
}
```

Claude Code 将钩子事件作为 JSON 传递给命令作为标准输入，并且不会设置 `TOOL_NAME` 或 `TOOL_INPUT` 变量。`evaluate.sh` 从该负载中读取 `tool_name` 和 `tool_input`，并将它们作为标志传递给 `protect-mcp`；`sign.sh` 仅读取 `tool_name`，因为 0.7.4 的签名器不会记录其他任何内容。将 `PROTECT_MCP_POLICY`、`PROTECT_MCP_RECEIPTS` 和 `PROTECT_MCP_KEY` 设置为更改默认路径。当策略文件缺失时，PreToolUse 钩子会向标准错误打印警告并允许调用。

### 每个钩子的作用

**PreToolUse** — 在工具执行之前运行。评估工具调用与您的 Cedar 策略文件。如果 Cedar 返回 `deny`，钩子会以代码 2 退出，Claude Code 会完全阻止工具调用。

**PostToolUse** 在工具完成后运行。它会签署一个包含工具名称的回执，并将其追加到 `./receipts/receipts.jsonl`。protect-mcp 0.7.4 不会记录工具输入或输出。

## Cedar 策略文件

在项目根目录下创建 `./protect.cedar`：

```cedar
// 只读工具：一个规则可以命名多个工具在 `when` 中。添加 WebFetch
// 并使用您自己的 URL 规则。
permit (principal, action == Action::"MCP::Tool::call", resource) when {
    resource == Tool::"Read" || resource == Tool::"Glob" || resource == Tool::"Grep"
};

// 仅安全命令；git 限制为只读子命令
permit (principal, action == Action::"MCP::Tool::call", resource == Tool::"Bash") when {
    context has input && context.input has command &&
    (context.input.command like "git status*" || context.input.command like "git diff*" ||
     context.input.command like "git log*" || context.input.command like "git show*" ||
     context.input.command like "npm*" || context.input.command like "ls*" ||
     context.input.command like "cat*" || context.input.command like "echo*" ||
     context.input.command like "pwd*" || context.input.command like "test*")
};

// 无链式调用（`&` 也拒绝 `2>&1`）、`$` 展开、重定向（`>` 或
// `<`，这涵盖了 `<(`）、文件输出（`git diff --output`），或 rm -rf
forbid (principal, action == Action::"MCP::Tool::call", resource == Tool::"Bash") when {
    context has input && context.input has command &&
    (context.input.command like "*;*" || context.input.command like "*&*" ||
     context.input.command like "*|*" || context.input.command like "*$*" ||
     context.input.command like "*`*" || context.input.command like "*>*" ||
     context.input.command like "*<*" || context.input.command like "*\n*" ||
     context.input.command like "*--output*" || context.input.command like "*rm -rf*")
};

// 仅在项目内写入（路径是绝对路径），从不通过 `..`
permit (principal, action == Action::"MCP::Tool::call", resource) when {
    (resource == Tool::"Write" || resource == Tool::"Edit") &&
    context has input && context.input has file_path &&
    context.input.file_path like "/path/to/project/*"
};
forbid (principal, action == Action::"MCP::Tool::call", resource) when {
    (resource == Tool::"Write" || resource == Tool::"Edit") &&
    context has input && context.input has file_path &&
    (context.input.file_path like "*/../*" || context.input.file_path like "*/..")
};
```

字符串匹配是尽力而为的：`like` 检查原始字符串，而不是解析路径，并且 `npm*` 允许运行任意代码，因此它只有项目脚本的安全性。

## 验证

使用 `./protect-mcp.key` 中的公钥验证每个回执：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./protect-mcp.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
# 退出 0 = 每个回执都验证通过
# 退出 1 = 一个回执失败（被篡改、密钥错误或格式化行错误）
# 退出 2 = 文件无法读取
```

插件的命令行工具在 Claude Code 内部执行相同的操作。`/verify-receipt` 接收一个回执，例如从 `tail -n 1 ./receipts/receipts.jsonl > receipt.json`。

```
/verify-receipt receipt.json
/audit-chain --last 20
```

## 回执格式

每个回执是 `./receipts/receipts.jsonl` 的一行。参见 [`references/receipt-format.md`](references/receipt-format.md) 获取示例。

- **Ed25519** 签名（RFC 8032）覆盖所有字段，但 `signature`
- **JCS 规范化**（RFC 8785）在签名之前
- **回执中不含公钥**，因此需要用 `--key` 传递
- **无指向前一个回执的链接**，因此删除的行无法检测

## 这为何重要

| 之前 | 之后 |
|------|------|
| "请相信，代理只读取了文件" | 加密可证明：每个 Read 都被记录并签名 |
| "日志显示它发生了" | 回执证明它发生了，而且没有人可以编辑它 |
| "您需要审计我们的系统" | 任何人都可以离线验证每个回执 |
| "日志可能现在已经不同了" | Ed25519 签名在签名时锁定记录 |

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开放授权策略语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)

## 相关

- **npm**: [protect-mcp](https://www.npmjs.com/package/protect-mcp)
- **Verify CLI**: [@veritasacta/verify](https://www.npmjs.com/package/@veritasacta/verify)
- **源代码**: [github.com/ScopeBlind/scopeblind-gateway](https://github.com/ScopeBlind/scopeblind-gateway)
- **协议**: [veritasacta.com](https://veritasacta.com)
- **集成**: Microsoft Agent Governance Toolkit (PR #667)、AWS cedar-policy/cedar-for-agents (PR #64)
