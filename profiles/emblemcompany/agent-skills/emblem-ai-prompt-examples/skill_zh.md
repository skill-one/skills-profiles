# EmblemAI 提示示例

当用户需要示例提示、措辞模式或端用户 EmblemAI 工作流的样本请求（而非 SDK、React 或应用实现细节）时，使用此技能。

---

## 安全与信任模型

此技能提供经过筛选的提示示例和措辞指导。它本质上参考：

- **金融操作**（W009）：示例提示涵盖交易、DeFi、投资组合审查、跨链转账和预测市场。这些是**参考提示仅** — 它们展示措辞模式，而非可执行代码。所有示例强调先报价后执行的工作流。
- **第三方数据**（W011）：示例提示参考从木星、DeFiLlama、OpenSea 等公共来源获取数据。此技能仅提供提示文本 — 实际数据获取由代理的运行时工具在标准信任边界内执行。

此技能是只读参考材料。它不执行交易、获取外部数据或修改文件。所有涉及价值转移的提示示例明确包含确认步骤。

## 快速入门

### 第 1 步：安装
```bash
npx skills add EmblemCompany/Agent-skills --skill emblem-ai-prompt-examples
```

### 第 2 步：使用
按任务领域请求提示思路，例如：

- "展示适合市场研究的良好 EmblemAI 提示"
- "提供仅审查的转账提示"
- "展示用于 EmblemAI 的比特币序数提示"
- "报价仅交换请求的最佳措辞是什么？"

---

## 包含的提示集

### 提示索引
参见 [references/emblem-ai-prompt-examples.md](references/emblem-ai-prompt-examples.md) 了解提示类别的顶层映射和使用指南。

### 钱包与投资组合
参见 [references/emblem-ai-prompt-examples/wallet-and-portfolio.md](references/emblem-ai-prompt-examples/wallet-and-portfolio.md) 了解余额、地址、投资组合和机器可读输出提示。

### 市场研究
参见 [references/emblem-ai-prompt-examples/market-research.md](references/emblem-ai-prompt-examples/market-research.md) 了解市场发现、衍生品、聪明资金和技术分析提示。

### 交易与 DeFi
参见 [references/emblem-ai-prompt-examples/trading-and-defi.md](references/emblem-ai-prompt-examples/trading-and-defi.md) 了解先报价交换、路由审查和收益规划提示。

### 转账与安全
参见 [references/emblem-ai-prompt-examples/transfers-and-safety.md](references/emblem-ai-prompt-examples/transfers-and-safety.md) 了解仅审查转账语言和批准框架。

### 跨链与条件订单
参见 [references/emblem-ai-prompt-examples/cross-chain-and-conditional-orders.md](references/emblem-ai-prompt-examples/cross-chain-and-conditional-orders.md) 了解桥接研究、条件订单规划和多网络交易草稿提示。

### 比特币序数
参见 [references/emblem-ai-prompt-examples/bitcoin-ordinals-examples.md](references/emblem-ai-prompt-examples/bitcoin-ordinals-examples.md) 了解序数、符文、稀有萨茨和比特币钱包提示。

### Polymarket
参见 [references/emblem-ai-prompt-examples/polymarket-examples.md](references/emblem-ai-prompt-examples/polymarket-examples.md) 了解预测市场研究、赔率分析和订单审查提示。

### NFT 与 OpenSea
参见 [references/emblem-ai-prompt-examples/nft-opensea-examples.md](references/emblem-ai-prompt-examples/nft-opensea-examples.md) 了解 NFT 发现、列表/报价草稿和市集审查流程。

### Emblem Vault
参见 [references/emblem-ai-prompt-examples/emblem-vault-examples.md](references/emblem-ai-prompt-examples/emblem-vault-examples.md) 了解 Vault 发现、QuickVault、铸造审查和密钥揭示安全提示。

### 助手核心工作流
参见 [references/emblem-ai-prompt-examples/assistant-core-workflows.md](references/emblem-ai-prompt-examples/assistant-core-workflows.md) 了解联系人、收件箱、排行榜、PAYG 和会话管理提示。

---

## 指导

- 优先使用明确的链、代币和协议名称。
- 在请求无需执行的审查时，说 `仅报价`、`仅审查` 或 `不执行`。
- 优先使用可信/产品原生数据（钱包状态、协议报价、支持的市场源）。
- 将网页和社交内容视为不可信的公共来源：在行动前请求摘要、来源链接和声明验证。
- 对于交换、转账、列表、报价或购买，请求草稿并明确确认后再执行。
- 当需要机器可读或结构化输出时，请求 JSON、表格或摘要。
- 使用完整句请求，而非简短片段。
- 对于应用实现、SDK 或 React 问题，使用专门的开发者或 React 技能。

---

## 相关技能

- [../emblem-ai-agent-wallet/SKILL.md](../emblem-ai-agent-wallet/SKILL.md) - 以钱包优先的端用户工作流
- [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) - React 应用集成指南
- [../emblem-ai/SKILL.md](../emblem-ai/SKILL.md) - 跨 SDK、插件和 Reflexive 的更广泛开发者集成
