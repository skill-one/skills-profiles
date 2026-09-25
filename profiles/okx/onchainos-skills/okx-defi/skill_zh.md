# OKX DeFi

通过 `onchainos defi` CLI 组发现和管理多链、OKX聚合的 DeFi 产品和头寸。

## 预检查

预检查：在每个线程开始时，完成 `../okx-agentic-wallet/_shared/preflight.md` 中的检查。如果缺失，请阅读 `_shared/preflight.md`。

## 意图路由

仅加载所选路由所需的参考文件。

| 用户意图 | 参考 |
|---|---|
| 发现/搜索 DeFi 产品，查找最佳 APY | [invest.md](references/invest.md) |
| 产品详情（APY、TVL、接受的代币） | [invest.md](references/invest.md) |
| 存入/质押/提供流动性 | [invest.md](references/invest.md) |
| 提取/赎回头寸（全部或部分） | [invest.md](references/invest.md) |
| 领取奖励（平台/投资/V3 费用/奖金/解锁本金） | [invest.md](references/invest.md) |
| APY 历史、TVL 历史、V3 深度/价格图表 | [invest.md](references/invest.md) |
| 查看 DeFi 头寸/持仓概览 | [portfolio.md](references/portfolio.md) |
| 单一协议头寸详情 | [portfolio.md](references/portfolio.md) |
| 精确参数/返回模式 — 投资命令、共享支持和图表命令 | [invest-cli-reference.md](references/invest-cli-reference.md) |
| 精确参数/返回模式 — 头寸命令 | [portfolio-cli-reference.md](references/portfolio-cli-reference.md) |
| 错误/失败的存入/过期的 calldata | [invest-troubleshooting.md](references/invest-troubleshooting.md) |
| 错误/空头寸/地址格式问题 | [portfolio-troubleshooting.md](references/portfolio-troubleshooting.md) |

典型流程跨越两者：查看头寸（持仓）→ 赎回或领取（投资）。当请求链式触发时，请同时阅读两个参考文件。

将命名第三方 DApp 请求（包括特定协议的 APY、TVL、交易量、历史或时间段分析）路由到 `okx-dapp-discovery`。通用的跨协议收益/APY/TVL 和 V3-流动性分析保留在此处。将代币搜索/价格/图表请求路由到 `okx-dex-market`，将现货交易、钱包余额、登录、合约调用或交易广播路由到 `okx-agentic-wallet`。

## 链名称支持

CLI 自动解析链名称（例如，`ethereum` → `1`，`bsc` → `56`，`solana` → `501`）。使用 [portfolio.md](references/portfolio.md) 中的链支持表获取 DeFi 特定的别名。

## 安全

### 地址解析

当用户未提供钱包地址时，在运行任何 DeFi 命令之前自动从智能钱包解析：

```
1. onchainos wallet status          → 检查是否登录，获取活跃账户
2. onchainos wallet addresses       → 获取按链类别分组的地址：
                                       - XLayer 地址
                                       - EVM 地址（Ethereum、BSC、Polygon 等）
                                       - Solana 地址
3. 将地址匹配到目标链：
   - EVM 链 → 使用 EVM 地址
   - Solana     → 使用 Solana 地址
   - XLayer     → 使用 XLayer 地址
```

规则：
- 如果用户提供明确地址，直接使用该地址 — 跳过此步骤
- 如果钱包未登录，先提示用户登录（→ `okx-agentic-wallet`）或手动提供地址
- 如果用户说“检查所有账户”或“所有钱包”，使用 `wallet balance --all` 获取所有账户 ID，然后对每个账户执行 `wallet switch <id>` + `wallet addresses`
- 如果账户有多个相同类型的地址，在继续之前始终向用户确认解析的地址

### 地址-链兼容性

`--address` 和链参数必须兼容。EVM 地址（`0x…`）只能查询 EVM 链；Solana 地址（base58）只能查询 `solana`。切勿混合使用 — API 将返回错误 84019（地址格式错误）。

- `0x…` 地址 → 仅传递 EVM 链：`ethereum,bsc,polygon,arbitrum,base,xlayer,avalanche,optimism,fantom,linea,scroll,zksync`
- base58 地址 → 仅传递 `solana`
- Sui 地址 → 仅传递 `sui`；Tron 地址（`T…`）→ 仅传递 `tron`；TON 地址 → 仅传递 `ton`
- 如果用户希望跨 EVM 和 Solana 查询头寸，请使用**两个独立的调用**并分别传递地址

## 全局说明

- 所有 DeFi 命令的钱包地址参数是 `--address`
- `defi positions` 使用 `--chains`（复数，逗号分隔）；`defi position-detail` 使用 `--chain`（单数）
- 在报告完成之前，验证所选命令是否成功，应用其路由参考的输出格式和安全检查，并明确报告任何部分或失败的链上步骤。
