---
name: signed-audit-trails-recipe
description: 逐步指南：在Claude Code工具调用中设置密码学签名审计追踪。在提交protect-mcp运行时钩子之前，用于解释、评估或演示该模式。涵盖Cedar策略、Ed25519收据、离线验证、篡改检测、CI/CD集成和SLSA组合。
---

# 对 Claude 代码工具调用的数字签名审计追踪

这是一个关于 Claude 代码工具调用的加密签名收据的食谱式指南。这是教学技能。对于运行时实现，请安装 [`protect-mcp`](../../../protect-mcp/) 插件。

## 这能为你提供什么

每个工具调用（`Bash`、`Edit`、`Write`、`WebFetch`）都会：

1. **在执行前与 Cedar 策略进行评估**。如果策略拒绝该调用，则工具不会运行。
2. **在执行后作为 Ed25519 收据进行签名**。收据是 JCS 标准化的，并且任何人只要有公钥都可以离线验证。

审计员、监管机构或交易对手可以在之后验证每个收据（步骤 5）。无需网络调用、无需供应商查找、无需信任操作员。

## 何时使用此模式

- **受监管环境**（金融、医疗保健、关键基础设施），在这些环境中你需要代理行为的防篡改证据
- **CI/CD 管道**，你希望证明每个自动构建步骤都持有一个策略门
- **多方协作**，其中交易对手希望在不信任你的操作员的情况下验证你的代理的行为
- **合规环境**（欧盟 AI 法案第 12 条、SLSA 代理构建软件的来源），其中标准日志记录不足

## 步骤 1：安装钩子配置

使用 `/plugin install protect-mcp` 安装 `protect-mcp` 插件。它的钩子在每次工具调用前运行 `evaluate.sh`，在调用后运行 `sign.sh`。这两个脚本都从标准输入读取钩子事件，因为 Claude 代码不设置 `TOOL_NAME` 或 `TOOL_INPUT` 变量。有关钩子配置以及每个脚本传递给 protect-mcp 的内容，请参阅 [`references/hook-wiring.md`](references/hook-wiring.md)。

protect-mcp 0.7.4 不会创建签名密钥，没有密钥，收据将是未签名的。创建一次 `./protect-mcp.key`。该命令永远不会替换现有密钥：

```bash
if [ ! -e ./protect-mcp.key ]; then
  d=$(mktemp -d) && npx protect-mcp@0.7.4 init --dir "$d" && mv "$d/keys/gateway.json" ./protect-mcp.key
fi
```

将审计员的 `publicKey` 值从该文件提供给审计员。不要提交该文件，因为它还包含私钥。

将私钥和收据目录添加到 `.gitignore`：

```bash
echo "/protect-mcp.key" >> .gitignore
echo "/receipts/" >> .gitignore
```

## 步骤 2：编写一个 Cedar 策略

从 [`references/cedar-policy.md`](references/cedar-policy.md) 中的示例创建 `./protect.cedar`。它允许只读工具，并允许一个短列表的 Bash 命令，拒绝 shell 链接和破坏性命令，并限制写入项目，带有 `..` 段的写入被拒绝。

## 步骤 3：正常使用 Claude Code

启动 Claude Code。每个工具调用都会通过两个钩子：

```
你：请阅读 README 并总结它。

Claude：我将阅读 README.md。
  [PreToolUse: 读取 ./README.md -> 允许]
  [Tool: 执行读取]
  [PostToolUse: 收据 rcpt-a8f3c9d2 签名到 ./receipts/]

... README 的摘要 ...
```

一个包含 20 个工具调用的会话将 20 个收据追加到 `./receipts/receipts.jsonl`。

## 步骤 4：检查收据

protect-mcp 0.7.4 将每个收据追加为 `./receipts/receipts.jsonl` 的一行。打印最新的一个：

```bash
tail -n 1 ./receipts/receipts.jsonl | python3 -m json.tool
```

收据是一个命名工具的 v2 封装，其中不包含公钥。有关样本和签名字段的详细信息，请参阅 [`references/receipt-format.md`](references/receipt-format.md)。

## 步骤 5：验证收据

将 `./protect-mcp.key` 中的 `publicKey` 值传递给验证器：

```bash
PUB=$(node -p 'JSON.parse(require("fs").readFileSync("./protect-mcp.key")).publicKey')
npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
```

退出代码：

| 代码 | 含义 |
|------|---------|
| `0`  | 每个收据都通过验证 |
| `1`  | 一个收据验证失败（被篡改、密钥错误或格式化行错误） |
| `2`  | 无法读取收据文件 |

## 步骤 6：展示篡改检测

将最新收据的 `decision` 从 `allow` 改为 `deny`：

```bash
python3 -c "
import json
path = './receipts/receipts.jsonl'
lines = open(path).read().splitlines()
r = json.loads(lines[-1])
r['payload']['decision'] = 'deny'
lines[-1] = json.dumps(r)
open(path, 'w').write('\n'.join(lines) + '\n')
"

npx @veritasacta/verify@0.9.2 --replay-chain ./receipts/receipts.jsonl --key "$PUB"
```

验证器退出代码为 `1` 并报告失败的行。Ed25519 签名不再与被篡改的有效负载的 JCS 标准化字节匹配。

恢复该字段，验证再次通过。

## 密码学的工作原理

两个不变性使得收据可以在任何符合规范的实现中离线验证：

1. **签名前的 JCS 标准化（RFC 8785）**。密钥排序，空白最小化，字符串 NFC 标准化。两个独立的实现为相同收据内容生成字节相同的签名有效负载。
2. **Ed25519 签名（RFC 8032）** 覆盖标准化的字节。确定性，固定大小，无nonce依赖。

protect-mcp 0.7.4 收据不包含与前一个收据的链接，因此被删除的收据将无法检测到。

有关正式的线格式，请参阅 [draft-farley-acta-signed-receipts](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/)。

## 跨实现互操作性

收据格式目前有四个独立的实现：

| 实现 | 语言 | 用例 |
|----------------|----------|----------|
| [protect-mcp](https://www.npmjs.com/package/protect-mcp) | TypeScript | Claude Code, Cursor, MCP 主机 |
| [protect-mcp-adk](https://pypi.org/project/protect-mcp-adk/) | Python | Google 代理开发套件 |
| [sb-runtime](https://github.com/ScopeBlind/sb-runtime) | Rust | OS 级沙盒（Landlock + seccomp） |
| APS 治理钩子 | Python | CrewAI, LangChain |

由其中任何一个生成的收据都可以验证 [`@veritasacta/verify`](https://www.npmjs.com/package/@veritasacta/verify)。审计员不需要信任操作员的工具选择：格式就是合同。

## CI/CD 集成

在 CI 中验证收据，以便被篡改的收据导致构建失败。
[`references/ci-cd.md`](references/ci-cd.md) 包含一个在默认分支推送时运行的 GitHub Actions 工作流程。它从分支限制的环境安装签名密钥，运行代理，验证收据，并上传它们。它不会在拉取请求上运行，因为那将密钥交给未审查的代码。

## 与 SLSA 代理构建软件的来源组合

当 Claude Code 构建和发布软件（作为工具调用运行 `npm install`、`npm build`、`npm publish`）时，收据链是每一步的构建日志。SLSA Provenance v1 有一个扩展点用于此目的：`byproducts` 字段可以引用收据链以及构建证明。

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

SLSA 来源由构建者身份签名；收据证明由监督钩子身份签名。两个信任域在 byproduct 层交叉引用。有关组合讨论，请参阅 [slsa-framework/slsa#1594](https://github.com/slsa-framework/slsa/issues/1594)。

## 常见陷阱

**版本控制中的私钥**。生成的 `./protect-mcp.key` 必须不提交。上面的示例将其添加到 `.gitignore`。如果密钥意外提交，请立即轮换它。将密钥和 `./receipts/receipts.jsonl` 移动到存档，然后再次运行步骤 1 命令。使用旧的公钥验证存档收据。

**钩子有效负载在标准输入上**。Claude 代码不设置 `$TOOL_NAME` 或 `$TOOL_INPUT` 变量。一个传递 `--tool "$TOOL_NAME"` 的钩子命令发送一个空的有效工具名称，因此策略拒绝每个调用。像插件脚本一样从标准输入读取有效负载。

**CI 中的收据目录**。如果 Claude 代码在 CI 中运行，请在作业结束时将收据作为工件上传，否则收据将在作业结束时丢失。

**策略缺失**。当 `./protect.cedar` 不存在时，`evaluate.sh` 会向标准错误打印警告并允许调用。直到你在步骤 2 中创建策略之前，没有调用会被限制。

## 市场中的相关内容

- [`protect-mcp`](../../../protect-mcp/) — 运行时钩子实现（在生产中使用此插件）
- [`review-agent-governance`](../../../review-agent-governance/) — 在审查表面操作之前需要人工批准；与 protect-mcp 组合

## 参考文献

- [`draft-farley-acta-signed-receipts`](https://datatracker.ietf.org/doc/draft-farley-acta-signed-receipts/) — IETF 草稿，收据线格式
- [RFC 8032](https://datatracker.ietf.org/doc/html/rfc8032) — Ed25519
- [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) — JCS
- [Cedar 策略语言](https://docs.cedarpolicy.com/)
- [protect-mcp on npm](https://www.npmjs.com/package/protect-mcp)
- [@veritasacta/verify on npm](https://www.npmjs.com/package/@veritasacta/verify)
- [in-toto/attestation#549](https://github.com/in-toto/attestation/pull/549) — 决策收据谓词提案
- [agent-commit build type](https://refs.arewm.com/agent-commit/v0.2) — 代理生成的提交的 SLSA 来源
- [Microsoft Agent Governance Toolkit](https://github.com/microsoft/agent-governance-toolkit) (`examples/protect-mcp-governed/`)
- [AWS Cedar for Agents](https://github.com/cedar-policy/cedar-for-agents)
