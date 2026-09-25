# 对 Claude 代码工具调用进行数字签名审计追踪

这是一个关于对 Claude 代码工具调用的每个调用都进行密码学签名的食谱式指南。这是教学技能。对于运行时实现，请安装 [`protect-mcp`](../../protect-mcp/) 插件。

## 这能为你提供什么

每个工具调用（`Bash`、`Edit`、`Write`、`WebFetch`）都会：

1. **在执行前与 Cedar 策略进行评估**。如果策略拒绝该调用，则工具不会运行。
2. **在执行后作为 Ed25519 收据进行签名**。收据是 JCS 标准化的、哈希链式的，并且任何人只要有公钥都可以离线验证。

审计员、监管机构或交易对手可以在稍后使用单个 CLI 命令（`npx @veritasacta/verify receipts/*.json`）验证完整的链。无需网络调用、无需供应商查找、无需信任操作员。

## 何时使用此模式

- **受监管环境**（金融、医疗保健、关键基础设施），在这些环境中需要代理行为的防篡改证据
- **CI/CD 管道**，在这些管道中，您希望证明每个自动构建步骤都持有了策略门
- **多方协作**，其中交易对手希望验证您的代理行为，而无需信任您的操作员
- **合规环境**（欧盟 AI 法第 12 条、SLSA 起源，用于代理构建的软件），其中标准日志记录不足

## 第 1 步：安装钩子配置

在您的项目根目录下创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest evaluate --policy ./protect.cedar --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --fail-on-missing-policy false"
        }
      }
    ],
    "PostToolUse": [
      {
        "matcher": ".*",
        "hook": {
          "type": "command",
          "command": "npx protect-mcp@latest sign --tool \"$TOOL_NAME\" --input \"$TOOL_INPUT\" --output \"$TOOL_OUTPUT\" --receipts ./receipts/ --key ./protect-mcp.key"
        }
      }
    ]
  }
}
```

`protect-mcp sign` 的第一次运行如果不存在，将生成 `./protect-mcp.key`（Ed25519 私钥）。提交**公钥**的指纹（在任何收据的 `public_key` 字段中可见）；不要提交私钥。

将私钥和收据目录添加到 `.gitignore`：

```bash
echo "./protect-mcp.key" >> .gitignore
echo "./receipts/" >> .gitignore
```

## 第 2 步：编写一个 Cedar 策略

创建 `./protect.cedar`：

```cedar
// 默认情况下允许所有只读工具。
permit (
    principal,
    action in [Action::"Read", Action::"Glob", Action::"Grep", Action::"WebSearch"],
    resource
);

// 仅允许来自安全列表的 Bash 命令。
permit (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern in [
        "git", "npm", "pnpm", "yarn", "ls", "cat", "pwd",
        "echo", "test", "node", "python", "make"
    ]
};

// 明确拒绝破坏性命令。Cedar deny 具有权威性。
forbid (
    principal,
    action == Action::"Bash",
    resource
) when {
    context.command_pattern in ["rm -rf", "dd", "mkfs", "shred"]
};

// 限制对项目目录的写入。
permit (
    principal,
    action in [Action::"Write", Action::"Edit"],
    resource
) when {
    context.path_starts_with == "./"
};
```

四条规则：

- 只读工具始终允许
- `Bash` 仅允许安全的命令模式（`git`、`npm` 等）
- `Bash rm -rf` 和类似的破坏性命令明确拒绝
- 仅在项目内（`./` 前缀）允许写入

Cedar `forbid` 规则优先于 `permit` 规则，因此破坏性命令无法被后续的允许规则绕过。

## 第 3 步：正常使用 Claude Code

启动 Claude Code。每个工具调用都会通过两个钩子：

```
您：请阅读 README 并总结它。

Claude：我将阅读 README.md。
  [PreToolUse: 读取 ./README.md -> 允许]
  [工具：执行读取]
  [PostToolUse: 收据 rcpt-a8f3c9d2 签名到 ./receipts/]

... README 的摘要 ...
```

一个包含 20 个工具调用的会话将产生 20 个收据，每个收据都哈希链式链接到其前一个收据。

## 第 4 步：检查收据

```bash
cat ./receipts/$(ls -t ./receipts/ | head -1)
```

```json
{
  "receipt_id": "rcpt-a8f3c9d2",
  "receipt_version": "1.0",
  "issuer_id": "claude-code-protect-mcp",
  "event_time": "2026-04-17T12:34:56.123Z",
  "tool_name": "Read",
  "input_hash": "sha256:a3f8c9d2e1b7465f...",
  "decision": "allow",
  "policy_id": "protect.cedar",
  "policy_digest": "sha256:b7e2f4a6c8d0e1f3...",
  "parent_receipt_id": "rcpt-3d1ab7c2",
  "public_key": "4437ca56815c0516...",
  "signature": "4cde814b7889e987..."
}
```

除了 `signature` 和 `public_key` 之外，每个字段都由 Ed25519 签名覆盖。签名后修改任何字段都会使签名失效。

## 第 5 步：验证收据链

```bash
npx @veritasacta/verify ./receipts/*.json
```

退出代码：

| 代码 | 含义 |
|------|---------|
| `0`  | 所有收据验证通过；链完整 |
| `1`  | 一个收据签名验证失败（被篡改或使用了错误的密钥） |
| `2`  | 一个收据格式错误 |

## 第 6 步：演示篡改检测

修改任何收据的 `decision` 字段，从 `allow` 改为 `deny`：

```bash
python3 -c "
import json, os
path = './receipts/' + sorted(os.listdir('./receipts'))[-1]
r = json.loads(open(path).read())
r['decision'] = 'deny'
open(path, 'w').write(json.dumps(r))
"

npx @veritasacta/verify ./receipts/*.json
```

验证器退出并报告失败的收据。Ed25519 签名不再与被篡改的有效负载的 JCS 标准化字节匹配。

恢复该字段后，验证再次通过。

## 密码学工作原理

三个不变性使得收据可以在任何符合规范的实现中离线验证：

1. **签名前的 JCS 标准化（RFC 8785）**。密钥排序、空白最小化、字符串 NFC 标准化。两个独立的实现为相同的收据内容生成字节相同的签名负载。
2. **Ed25519 签名（RFC 8032）** 覆盖标准化字节。确定性、固定大小、无nonce依赖。
3. **哈希链链接**。每个收据的 `parent_receipt_hash` 是前一个收据的 SHA-256。插入、删除和重新排序会破坏后续收据。

有关正式的线格式，请参阅
[draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)。

## 跨实现互操作性

收据格式目前有四个独立的实现：

| 实现 | 语言 | 用例 |
|----------------|----------|----------|
| [protect-mcp](https://www.npmjs.com/package/protect-mcp) | TypeScript | Claude Code、Cursor、MCP 主机 |
| [protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/) | Python | Google Agent 开发工具包 |
| [sb-runtime](https://github.com/ScopeBlind/sb-runtime) | Rust | OS 级沙盒（Landlock + seccomp） |
| APS 治理钩子 | Python | CrewAI、LangChain |

任何它们生成的收据都可以通过
[`@veritasacta/verify`](https://www.npmjs.com/package/@veritasacta/verify) 进行验证。审计员无需信任操作员的工具选择：格式就是合同。

## CI/CD 集成

在收据链验证上设置合并门，以确保没有构建带有损坏的证据链：

```yaml
# .github/workflows/verify-receipts.yml
name: Verify Decision Receipts
on: [push, pull_request]

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - name: Run governed agent
        run: python scripts/run_agent.py > receipts.jsonl
      - name: Verify receipt chain
        run: npx @veritasacta/verify receipts.jsonl
```

将收据作为工件存档，以便链在作业运行结束后仍然存在：

```yaml
      - name: Upload receipts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: decision-receipts
          path: receipts/
```

## 与 SLSA 起源组合用于代理构建的软件

当 Claude Code 构建和发布软件（作为工具调用运行 `npm install`、`npm build`、`npm publish`）时，收据链是每一步的构建日志。SLSA Provenance v1 有一个扩展点用于此：`byproducts` 字段可以引用收据链以及构建证明。

[代理提交构建类型](https://refs.arewm.com/agent-commit/v0.2) 使用 ResourceDescriptor 形状记录此模式：

```json
{
  "name": "decision-receipts",
  "digest": { "sha256": "..." },
  "uri": "oci://registry/org/build-xyz/receipts:sha256-...",
  "annotations": {
    "predicateType": "https://veritasacta.com/attestation/decision-receipt/v0.1",
    "signerRole": "supervisor-hook"
  }
}
```

SLSA 起源由构建身份签名；收据证明由监督钩子身份签名。两个信任域在 byproduct 层级交叉引用。有关组合讨论，请参阅
[slsa-framework/slsa#1594](https://github.com/slsa-framework/slsa/issues/1594)。

## 常见陷阱

**私钥在版本控制中**。生成的 `./protect-mcp.key` 必须不提交。上述示例将其添加到 `.gitignore`。如果密钥意外提交，请立即轮换（删除密钥文件并让钩子在下次运行时重新生成）。

**钩子命令引号**。钩子将 `$TOOL_NAME` 和 `$TOOL_INPUT` 作为环境变量接收。保持引号 `"$TOOL_INPUT"`，以便带有空格或特殊字符的输入完整传递。

**CI 中的收据目录**。如果 Claude Code 在 CI 中运行，请在作业结束时上传收据作为工件，否则链将在作业结束时丢失。

**策略缺失**。示例 `PreToolUse` 钩子使用 `--fail-on-missing-policy false`，因此缺少 `./protect.cedar` 不会立即破坏 Claude Code。在生产中移除此标志，以便将缺失的策略视为硬失败。

## 市场中的相关内容

- [`protect-mcp`](../../protect-mcp/) — 运行时钩子实现（在生产中请使用此插件）
- [`review-agent-governance`](../../review-agent-governance/) — 在审查表面操作之前需要人工批准；与 protect-mcp 组合

## 参考文献

- [`draft-farley-acta-signed-receipts`](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/) — IETF 草案，收据线格式
- [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) — Ed25519
- [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) — JCS
- [Cedar 策略语言](https://docs.cedarpolicy.com/)
- [protect-mcp on npm](https://www.npmjs.com/package/protect-mcp)
- [@veritasacta/verify on npm](https://www.npmjs.com/package/@veritasacta/verify)
- [in-toto/attestation#549](https://github.com/in-toto/attestation/pull/549) — 决策收据谓词提案
- [agent-commit build type](https://refs.arewm.com/agent-commit/v0.2) — 代理生成的提交的 SLSA 起源
- [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (`examples/protect-mcp-governed/`)
- [AWS Cedar for Agents](https://github.com/cedar-policy/cedar-for-agents)
