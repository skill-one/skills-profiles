# Onchain OS 安全

5个用于代币风险分析、DApp 仿冒检测、交易预执行安全、签名安全性和审批管理的命令。

## 预检查

> 阅读 `../okx-agentic-wallet/_shared/preflight.md`。如果该文件不存在，请读取 `_shared/preflight.md`。

## 安全保障原则（关键）

### 扫描完成 — 检测到风险

如果安全扫描**成功完成**并返回 `action: "block"` 或 `action: "warn"`，请遵循以下风险操作优先级规则。代理**必须**不得覆盖风险判定。

### 扫描失败 — 基础设施错误

如果安全扫描**未能完成**（网络错误、API 超时、速率限制、响应格式错误），代理**必须**：
- 向用户清晰地报告错误。
- **询问用户**是否要重试扫描或无需扫描结果直接进行。
- 如果用户选择继续，显示警告：
  > "⚠️ 安全扫描未能完成。未进行验证即继续操作 — 请确保您信任此操作。"
- 记录跳过的扫描以供审计。

> 未能完成的扫描**不等于通过**。始终告知用户并让他们做出明确决定。

## 风险操作优先级规则

### tx-scan / sig-scan（交易和签名扫描）

`block` > `warn` > safe（空）。顶层 `action` 字段反映来自 `riskItemDetail` 的最高优先级。

| `action` 值 | 风险等级 | 代理行为 |
|---|---|---|
| (空/NULL) | 低风险 | 可以继续 |
| `warn` | 中风险 | 显示风险详情，要求用户明确确认 |
| `block` | 高风险 | **不得**继续，显示风险详情，建议取消 |

- 即使模拟失败，风险扫描结果仍然有效（`simulator.revertReason` 可能包含回滚原因）。
- 如果 `warnings` 字段已填充，扫描已完成但某些数据可能不完整。仍然提供可用的风险信息。
- 在**成功**的 API 响应中，空的/NULL `action` 表示“未检测到风险”。但如果 API 调用**失败**，`action` 的缺失**不等于**安全 — 应用安全保障原则。

### token-scan（代币风险标签扫描）

Token-scan 返回一个**`riskLevel`** 字段（`CRITICAL`、`HIGH`、`MEDIUM`、`LOW`），表示整体代币风险，由服务器端根据所有布尔标签、税收阈值和附加信号（链下情报、机器学习模型）计算得出。代理直接使用此字段，并对**购买**和**出售**操作应用不同的操作。

| `riskLevel` | 购买操作 | 出售操作 |
|---|---|---|
| **CRITICAL** | `block` — 拒绝购买 | `warn` — 显示风险，允许出售 |
| **HIGH** | `warn` + **暂停** — 要求明确 yes/no | `warn` — 显示风险，允许出售 |
| **MEDIUM** | `warn` — 信息提示，继续 | `warn` — 信息提示，继续 |
| **LOW** | safe — 继续 | safe — 继续 |

> 完整标签目录、税收阈值规则和显示格式在 `references/risk-token-detection.md` 中定义。**执行 `token-scan` 前必须加载该参考文件。**

关键原则：
- **`riskLevel` 具有权威性**：API 在服务器端返回整体风险等级。代理直接读取 `riskLevel` — 无需从单个标签进行客户端计算。
- **购买比出售更严格**：`CRITICAL` 拒绝购买，但在出售时仅警告（允许止损退出）。
- **`HIGH` 购买需要用户明确 yes/no 确认** — 不得自动继续。
- **不向用户显示单个标签级别** — 仅显示整体 `riskLevel`，触发的标签不带级别前缀显示。
- 如果 `isChainSupported: false`，则带警告跳过检测；不得阻止。
- 如果 API 失败，则警告但不得阻止。在兑换上下文中，Token-scan 失败会带警告自动继续，以避免阻止时间敏感的交易 — 这会覆盖一般安全保障的询问用户行为。

> 安全命令不需要钱包登录。它们可与任何地址一起使用。

## 链名称支持

CLI 接受人类可读的链名称并自动解析。

| 链 | 名称 | chainIndex |
|---|---|---|
| XLayer | `xlayer` | `196` |
| Ethereum | `ethereum` 或 `eth` | `1` |
| Solana | `solana` 或 `sol` | `501` |
| BSC | `bsc` 或 `bnb` | `56` |
| Polygon | `polygon` 或 `matic` | `137` |
| Arbitrum | `arbitrum` 或 `arb` | `42161` |
| Base | `base` | `8453` |
| Avalanche | `avalanche` 或 `avax` | `43114` |
| Optimism | `optimism` 或 `op` | `10` |
| zkSync Era | `zksync` | `324` |
| Linea | `linea` | `59144` |
| Scroll | `scroll` | `534352` |

**地址格式说明**：EVM 地址（`0x...`）适用于 Ethereum/BSC/Polygon/Arbitrum/Base 等。Solana 地址（Base58）和比特币地址（UTXO）格式不同。**不同链类型之间不得混用格式。**

## 相关工作流

使用以下命令之一时，在显示结果后显示相关工作流提示：

| 命令 | 工作流 | 文件 |
|---|---|------|
| `security token-scan` | 新代币筛选 | `~/.onchainos/workflows/new-token-screening.md` |
| `security token-scan` | 智能资金信号 | `~/.onchainos/workflows/smart-money-signals.md` |
| `security token-scan` | 代币研究 | `~/.onchainos/workflows/token-research.md` |
| `security token-scan` | 钱包监控 | `~/.onchainos/workflows/wallet-monitor.md` |

> 提示格式：*"您也可以尝试我们的 **[工作流名称]** 工作流以获得更全面的结果。您要尝试吗？"*

## 命令索引

| # | 命令 | 描述 |
|---|---|---|
| 1 | `onchainos security token-scan` | 代币风险/蜜罐检测（所有链） |
| 2 | `onchainos security dapp-scan` | DApp/URL 仿冒检测（链无关） |
| 3 | `onchainos security tx-scan` | 交易预执行安全（EVM + Solana） |
| 4 | `onchainos security sig-scan` | 消息签名安全（仅 EVM） |
| 5 | `onchainos security approvals` | 代币审批/Permit2 授权查询（仅 EVM） |

## 参考文件加载规则（强制）

执行任何安全命令前，您**必须**从 `skills/okx-security/references/` 读取相应的参考文件。不得依赖先验知识 — 始终先加载参考文件。

| 用户意图 | 首先读取此文件 |
|---|---|
| 代币安全，蜜罐检测，这个代币安全吗 | `references/risk-token-detection.md` |
| DApp/URL 仿冒，这个网站安全吗 | `references/risk-domain-detection.md` |
| 交易安全，交易预执行，签名安全，审批安全 | `references/risk-transaction-detection.md` |
| 审批，授权，Permit2，撤销 | `references/risk-approval-monitoring.md` |

> 当工作流涉及多个命令（例如，token-scan 然后 tx-scan）时，执行该命令前加载每个参考文件。

## 与其他技能的集成

安全扫描通常是其他钱包操作的先决条件：
- 在使用合约代币执行 `wallet send` 前：运行 `token-scan` 验证代币安全
- 在使用审批 calldata 执行 `wallet contract-call` 前：运行 `tx-scan` 检查花费者
- 在与任何 DApp URL 交互前：运行 `dapp-scan`
- 在签署任何 EIP-712 消息前：运行 `sig-scan`

使用 `okx-agentic-wallet` 技能执行后续的 send/contract-call 操作。
