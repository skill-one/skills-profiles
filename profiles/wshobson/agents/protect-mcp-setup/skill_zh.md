# protect-mcp — 政策执行 + 签名收据

针对每个 Claude Code 工具调用进行加密治理。每次调用都会根据 Cedar 政策进行评估，并生成一个 Ed25519 签名的收据，任何人都可以离线验证。

## 概述

Claude Code 运行强大的工具：`Bash`、`Edit`、`Write`、`WebFetch`。默认情况下，没有审计追踪，没有政策执行，也没有办法证明事后决定的内容。`protect-mcp` 弥补了这三个方面的空白：

- **Cedar 政策**（AWS 的开源授权引擎）在执行前评估每个工具调用。Cedar 拒绝是权威性的。
- **Ed25519 收据**记录每个决策及其输入、控制该决策的政策以及结果。收据是哈希链式连接的。
- **离线验证**通过 `npx @veritasacta/verify` 进行。无需服务器，无需账户，无需信任操作员。

## 问题

AI 代理做出的决策会影响金钱、安全和权利。Claude Code 会话日志记录了发生的事情，但该日志：

- 可变——任何有访问权限的人都可以编辑它
- 无签名——没有办法证明完整性
- 与操作员绑定——验证需要信任持有日志的人

对于合规环境（金融、医疗保健、受监管的研究），这并不充分。您需要可篡改的证据，并且可以由第三方在不信任您的情况下进行验证。

## 解决方案

将 `protect-mcp` 添加到您的 Claude Code 项目中：

```bash
# 1. 安装插件（为您的项目添加钩子 + 技能）
claude plugin install wshobson/agents/protect-mcp

# 2. 创建 ./protect.cedar（见下文）。插件会安装钩子。

# 3. 启动收据签名服务器（在本地运行，无外部调用）
npx protect-mcp@latest serve --enforce

# 4. 正常使用 Claude Code。现在每个工具调用都会被政策评估
#    并在 ./receipts/ 中生成签名收据
```

## 钩子配置

安装插件会添加来自 `hooks/hooks.json` 的钩子。每个钩子运行插件捆绑的脚本：

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

Claude Code 将钩子事件作为 JSON 传递给命令的 stdin，并且不会设置 `TOOL_NAME` 或 `TOOL_INPUT` 变量。`evaluate.sh` 从该负载中读取 `tool_name` 和 `tool_input`，并将它们作为标志传递给 `protect-mcp`；`sign.sh` 仅读取 `tool_name`，因为 0.7.4 签名器记录了其他任何内容。将 `PROTECT_MCP_POLICY`、`PROTECT_MCP_RECEIPTS` 和 `PROTECT_MCP_KEY` 设置为更改默认路径。当政策文件缺失时，PreToolUse 钩子会向 stderr 打印警告并允许调用。

### 每个钩子的作用

**PreToolUse** — 在工具执行之前运行。根据您的 Cedar 政策文件评估工具调用。如果 Cedar 返回 `deny`，钩子会以代码 2 退出，Claude Code 完全阻止工具调用。

**PostToolUse** — 在工具完成后运行。签署一个包含工具名称、输入哈希、输出哈希、决策、政策摘要和时间的收据。将收据写入 `./receipts/<timestamp>.json`。

## Cedar 政策文件

在项目根目录下创建 `./protect.cedar`：

```cedar
// 默认允许只读工具
permit (
    principal,
    action in [Action::"Read", Action::"Glob", Action::"Grep", Action::"WebFetch"],
    resource
);

// 破坏性工具需要显式允许
permit (
    principal,
    action == Action::"Bash",
    resource
) when {
    // 仅允许安全命令
    context.command_pattern in ["git", "npm", "ls", "cat", "echo", "pwd", "test"]
};

// 永不允许递归删除
forbid (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern == "rm -rf"
};

// 项目外写入需要确认
forbid (
    principal,
    action in [Action::"Edit", Action::"Write"],
    resource
) when {
    context.path_starts_with != "."
};
```

## 验证

验证单个收据：

```bash
npx @veritasacta/verify receipts/2026-04-15T10-30-00Z.json
# 退出 0 = 有效
# 退出 1 = 被篡改
# 退出 2 = 格式错误
```

验证整个链：

```bash
npx @veritasacta/verify receipts/*.json
```

在 Claude Code 内部使用插件的斜杠命令：

```
/verify-receipt receipts/latest.json
/audit-chain ./receipts/ --last 20
```

## 收据格式

每个收据是一个具有以下结构的 JSON 文件：

```json
{
  "receipt_id": "rec_8f92a3b1",
  "receipt_version": "1.0",
  "issuer_id": "claude-code-protect-mcp",
  "event_time": "2026-04-15T10:30:00.000Z",
  "tool_name": "Bash",
  "input_hash": "sha256:a3f8...",
  "decision": "allow",
  "policy_id": "autoresearch-safe",
  "policy_digest": "sha256:b7e2...",
  "parent_receipt_id": "rec_3d1ab7c2",
  "public_key": "4437ca56815c0516...",
  "signature": "4cde814b7889e987..."
}
```

- **Ed25519** 签名（RFC 8032）
- **JCS 规范化**（RFC 8785）在签名之前进行
- **哈希链式连接**到前一个收据 via `parent_receipt_id`
- **离线可验证**——无需网络调用，无需供应商查找

## 这为何重要

| 之前 | 之后 |
|------|------|
| "请相信，代理只读取了文件" | 加密可证明：每个 Read 都被记录并签名 |
| "日志显示它发生了" | 收据证明它发生了，而且没有人可以编辑它 |
| "您需要审计我们的系统" | 任何人都可以离线验证每个收据 |
| "日志可能现在已经不同了" | Ed25519 签名在签名时锁定记录 |

## 标准

- **Ed25519** — RFC 8032（数字签名）
- **JCS** — RFC 8785（确定性 JSON 规范化）
- **Cedar** — AWS 的开源授权政策语言
- **IETF 草案** — [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)

## 相关

- **npm**: [protect-mcp](https://www.npmjs.com/package/protect-mcp)
- **Verify CLI**: [@veritasacta/verify](https://www.npmjs.com/package/@veritasacta/verify)
- **源代码**: [github.com/ScopeBlind/scopeblind-gateway](https://github.com/ScopeBlind/scopeblind-gateway)
- **协议**: [veritasacta.com](https://veritasacta.com)
- **集成**: Microsoft Agent Governance Toolkit (PR #667)，AWS cedar-policy/cedar-for-agents (PR #64)
