# OKX OnChainOS — 技能目录

> **本文件用途：** 指向 OKX 官方 `onchainos-skills` 仓库的目录页面。它本身**不包含任何逻辑**——所有下方的子技能均存在于 [`okx/onchainos-skills`](https://github.com/okx/onchainos-skills) 上游，并在安装时实时获取，因此您始终获得最新版本。

OKX OnChainOS 是一套包含 **8 个专业子技能**的套件，涵盖链上交易、市场分析、智能资金信号、DeFi 投资与头寸、钱包操作、安全扫描、支付协议、代理身份与任务市场，以及跨越 20 多条区块链（以太坊、索拉纳、XLayer、Base、BSC、Arbitrum、Polygon、Optimism、Avalanche、波场、…）的加密货币新闻与情绪分析。

大多数子技能会驱动单个二进制文件 `onchainos`，首次使用时下载。部分功能（仅读数据）也可以不依赖二进制文件，通过 Starchild 的 sc-proxy 访问——见下文**认证选项**。

---

## 实际安装流程

```bash
# 安装单个子技能（推荐——仅获取您需要的部分）
npx skills add okx/onchainos-skills@<子技能名称>

# 或通过长格式
npx skills add https://github.com/okx/onchainos-skills --skill <子技能名称>

# 安装全部（自动检测环境并相应安装）
npx skills add okx/onchainos-skills
```

每个子技能都包含自己的 SKILL.md + 参考文档 + 触发短语，因此您可以仅获取所需部分。

**插件市场**（替代方案）：

```text
/plugin marketplace add okx/onchainos-skills
/plugin install onchainos-skills
```

**CLI 安装**（`onchainos` 二进制文件——自动检测平台、验证 SHA256、安装到 `~/.local/bin` 或 `%USERPROFILE%\.local\bin`）：

```bash
# macOS / Linux
curl -sSL https://raw.githubusercontent.com/okx/onchainos-skills/main/install.sh | sh
# 添加 `-s -- --beta` 获取最新预发布版本（仅可选；不会降级）
```

```powershell
# Windows
irm https://raw.githubusercontent.com/okx/onchainos-skills/main/install.ps1 | iex
```

---

## 钱包——默认使用用户的代理钱包

使用平台 `wallet` 技能进行签名和广播。OKX DEX 端点返回未签名的调用数据 (`{to, value, data, ...}`)；将其传递给 `wallet_transfer(data=<calldata>)` 即可完成。无需单独的 OKX 钱包。

仅在用户明确要求时才使用 OnchainOS TEE 钱包 (`onchainos wallet login <email>`)。

---

## 认证选项（在调用任何功能前阅读）

存在两种不同的路径。根据代理需要执行的操作选择：

### 路径 A — 通过 Starchild sc-proxy 直接 HTTP 访问（无需 API Key）

对于仅读数据查询（价格、K线、智能资金信号、代币分析、安全检查、公开地址投资组合——**≈ 80 % 的 OnchainOS 功能**），代理可以完全跳过 CLI，直接通过 sc-proxy 调用 `https://web3.okx.com/...`：

```python
from core.http_client import proxied_get
r = proxied_get(
    "https://web3.okx.com/api/v6/dex/aggregator/supported/chain",
    headers={"SC-CALLER-ID": f"chat:{thread_id}"},
)
```

sc-proxy 自动注入平台 OKX 凭证，使用 HMAC-SHA256 签名每个请求，并计费调用者的 Starchild 信用额度。

- **成本**：$0.001 / 请求
- **速率限制**：60 请求/分钟
- **设置**：无
- **限制**：仅数据——无法发送交易或管理钱包

### 路径 B — 使用您自己的 OKX Web3 API Key 的 `onchainos` CLI

用于钱包操作（`wallet login`、`wallet send`、`wallet contract-call`）、DEX 交换执行、支付以及任何其他 CLI 驱动的流程。

`onchainos` CLI 随附**内置沙盒 API Key**，可用于本地测试——无需设置。这些 Key 是**共享、速率受限且仅用于评估**的：**切勿**在生产环境或使用真实资产时使用它们。使用内置 Key 产生的任何失败或损失均由调用者负责。

对于生产环境，请使用您自己的凭证：

1. 在 [web3.okx.com → OnchainOS → 开发门户](https://web3.okx.com/onchain-os/dev-portal) 申请
2. 设置环境变量（或在项目根目录中创建 `.env` 文件——切勿提交）：
   ```bash
   export OKX_API_KEY=<您的 Key>
   export OKX_SECRET_KEY=<您的密钥>
   export OKX_PASSPHRASE=<您的短语>
   ```
3. 运行任何子技能的 CLI 命令。

### 为什么 CLI 不能使用 sc-proxy

`onchainos` 二进制文件使用 Rust 的 `rustls` TLS 堆栈，并包含**捆绑的 `webpki-roots`**——Mozilla 根 CA 列表的编译时副本。它忽略系统信任库、忽略 `SSL_CERT_FILE`，且没有文档记录的环境变量覆盖。因此，sc-proxy 的 MITM CA 被视为 `UnknownIssuer`，CLI 无法透明代理。目前，路径 A（代理脚本直接 HTTP 访问）是使用平台凭证的唯一方式。

钱包创建 (`onchainos wallet login <email>`) 会为您提供一个由 TEE 管理的新账户——它**不会导入您现有的 OKX App / 扩展钱包**。

---

## 按类别划分的子技能

### 📊 发现与市场数据（2）

| 子技能 | 用于 |
|---|---|
| `okx-dex-market` | 仅读链上 DEX 数据：实时价格 / K线 / 指数 / 钱包盈亏、地址追踪活动、智能资金 / 大户 / KOL 信号追踪 + 排行榜排名、代币搜索 / 元数据 / 市值 / 排名 / 流动性 / 热门代币 / 持有者 & 簇分析 / 顶级交易者 / 交易历史、加密货币新闻 / 情绪 / 氛围 / KOL 排行榜、Meme 挖掘 / 深坑扫描 / 开发者声誉 / 套装检测，以及 WS/脚本实时流 |
| `okx-dapp-discovery` | 第三方 DApp 发现和直接插件路由——目前支持 Polymarket、Aave V3、Hyperliquid、PancakeSwap V3 AMM、Morpho V1 Optimizer |

### 💼 钱包、交易与安全（1）

| 子技能 | 用于 |
|---|---|
| `okx-agentic-wallet` | 钱包生命周期（认证、余额、投资组合盈亏、发送、交易历史、合约调用）、Gas Station、DEX 交换、跨链桥接、限价订单策略、交易网关（Gas / 模拟 / 广播 / 跟踪订单）、公开地址投资组合、安全扫描（代币风险、DApp 仿冒、交易 & 签名检查、授权）、审计日志 |

### 🏦 DeFi（1）

| 子技能 | 用于 |
|---|---|
| `okx-defi` | OKX 汇聚的 DeFi：产品发现、存款、取款、领取奖励（跨 Aave、Lido、PancakeSwap、Kamino、NAVI 等），以及跨协议和链的头寸与持有概览 |

### 💸 支付（1）

| 子技能 | 用于 |
|---|---|
| `okx-agent-payments-protocol` | 跨 x402 (`exact` / `aggr_deferred` 方案——TEE 或本地密钥签名）、MPP (`charge` / `session` 意图——开放 / 优惠券 / 充值 / 关闭，交易或哈希模式）、以及 a2a-pay（基于 paymentId 创建 / 支付 / 状态）。路由到每个方案/意图的引用。 |

### 🤖 代理与 AI（2）

| 子技能 | 用于 |
|---|---|
| `okx-ai` | ERC-8004 链上代理身份（注册 / 更新 / 搜索 / 评分 / 服务列表）+ 代理任务市场（发布 / 接受 / 交付 / 争议）+ 实时任务进度监控 |
| `okx-guide` | 引导与指南中心：Onchain OS 引导 + 欢迎横幅、OKX.AI 介绍 & 角色注册路由、客户支持 / 帮助中心指南 |

### 🛠️ 操作（1）

| 子技能 | 用于 |
|---|---|
| `okx-growth-competition` | 代理钱包专用的交易竞赛：列表、加入、查看排行榜、领取奖励 |

---

## 快速任务 → 子技能映射

| 我想… | 子技能 | 建议路径 |
|---|---|---|
| 检查代币价格或图表 | `okx-dex-market` | A（无需 Key） |
| 搜索 / 分析代币的持有者 | `okx-dex-market` | A（无需 Key） |
| 跟踪智能资金买入 | `okx-dex-market` | A（无需 Key） |
| 扫描新的 Meme 发起 | `okx-dex-market` | A（无需 Key） |
| 查看任何公开钱包 | `okx-agentic-wallet`（公开地址投资组合） | A（无需 Key） |
| 扫描代币 / DApp 的风险 | `okx-agentic-wallet`（安全扫描） | A（无需 Key） |
| 估计 Gas / 模拟交易 | `okx-agentic-wallet`（网关） | A 或 B |
| 管理 / 从我的钱包发送 | `okx-agentic-wallet` | B（需要登录） |
| 交换代币 | `okx-agentic-wallet`（DEX 交换）REST + 使用 `wallet` 技能（代理钱包）签名 |
| 查找最佳 DeFi 收益（任何协议） | `okx-defi` | B（签名） |
| 查看我的 DeFi 头寸 | `okx-defi` | A（无需 Key） |
| 使用特定 DApp（Aave、Polymarket、…） | `okx-dapp-discovery` | B（完整 DApp 流程） |
| 支付 x402 / MPP / a2a-pay 受限资源 | `okx-agent-payments-protocol` | B（签名） |
| 注册 / 评分链上代理、代理任务市场 | `okx-ai` | B（签名） |
| 引导、OKX.AI 介绍、客户支持 | `okx-guide` | A（无需 Key） |
| 加入交易竞赛 | `okx-growth-competition` | B（需要钱包） |
| 调试 CLI 失败 | `okx-agentic-wallet`（审计日志） | B（本地 CLI 日志） |

---

## 工作流——预构建的多技能编排

除了单个子技能，仓库还提供 `workflows/` 下的**工作流编排**，将多个技能组合成一个完整操作。代理读取 `workflows/INDEX.md` 路由请求，然后遵循匹配工作流文件中的分步说明。

| 工作流 | 它做什么 | CLI 命令 |
|---|---|---|
| Token Research | 价格、安全、持有者、簇、智能资金信号、可选的 Launchpad 深入分析 | `onchainos workflow token-research --address <addr>` |
| Daily Brief | 市场脉搏 + 智能资金 + 新代币活动 + 投资组合警报 | — |
| Smart Money Signals | 按代币聚合的 SM 信号列表 + 每个代币的尽职调查 | `onchainos workflow smart-money` |
| New Token Screening | 迁移的 Launchpad 扫描 + 安全 & 开发者增强（前 10 名） | `onchainos workflow new-tokens` |
| Wallet Analysis | 7d/30d 盈亏、交易行为、最近链上活动 | `onchainos workflow wallet-analysis --address <addr>` |
| Portfolio Check | 余额、总价值、30d 盈亏概览 | `onchainos workflow portfolio --address <addr>` |
| Wallet Monitor | 会话内轮询——在监控的钱包发生新交易时提醒 | — |
| Wallet Monitor (WS) | 背景 WebSocket 会话，用于离线钱包监控 | — |

### 复合 CLI 命令

单个命令替代多个单独工具调用：

```bash
# 代币报告：信息 + 价格 + 高级信息 + 安全扫描（并行）
onchainos token report --address <addr> --chain solana

# 完整工作流命令
onchainos workflow token-research --address <addr> [--chain solana]
onchainos workflow smart-money [--chain solana]
onchainos workflow new-tokens [--chain solana] [--stage MIGRATED]
onchainos workflow wallet-analysis --address <addr> [--chain ethereum]
onchainos workflow portfolio --address <addr> [--chains ethereum,solana]
```

### 典型技能流程

- **搜索 & 买入**：`okx-dex-market`（找到代币）→ `okx-agentic-wallet`（检查资金 + 执行交易）
- **投资组合概览**：`okx-agentic-wallet`（持有）→ `okx-dex-market`（用分析 + 价格图表丰富）
- **市场研究**：`okx-dex-market`（趋势/排名 + K线/历史）→ `okx-agentic-wallet`（交易）
- **交换 & 广播**：`okx-agentic-wallet`（获取报价 → 交换 → 广播 → 跟踪订单）
- **完整交易流程**：`okx-dex-market`（搜索 + 价格/图表）→ `okx-agentic-wallet`（检查余额 → 交换 → 模拟 + 广播 + 跟踪）
- **排行榜 → 研究 → 交易**：`okx-dex-market`（按盈亏/胜率排序的交易者 + 代币分析）→ `okx-agentic-wallet`（执行交易）
- **跟踪智能资金**：`okx-dex-market`（KOL/智能资金买入 + 代币详情 + 持有者簇 + 价格图表）→ `okx-agentic-wallet`（交易）

---

## MCP 服务器

`onchainos` CLI 充当原生 MCP 服务器，将其工具暴露给任何 MCP 兼容客户端。启动它：

```bash
onchainos mcp
```

---

## 重要说明

- **链标识符**：同时接受人类名称（`ethereum`、`solana`、`xlayer`）和数字 ID。运行 `onchainos swap chains` 或 `onchainos gateway chains` 获取完整列表。
- **仅读操作**（市场数据、信号、安全扫描、公开地址投资组合）通过路径 A 无需用户提供的 API Key 即可工作。
- **交易 & 发送**默认使用用户的代理钱包通过 `wallet` 技能。仅在用户要求时才回退到 `onchainos wallet login`。
- **安全门**：当 `okx-agentic-wallet` 的安全扫描报告失败时，调用代理必须阻止相关操作，而不是继续。

---

## 资源

- **上游仓库**：[okx/onchainos-skills](https://github.com/okx/onchainos-skills)
- **OnchainOS 文档**：[OKX Web3 Build — OnchainOS](https://www.okx.com/web3/build/docs/onchain-os/introduction)
- **技能注册表**：[skills.sh/okx/onchainos-skills](https://skills.sh/okx/onchainos-skills)
- **开发门户（API Key）**：[web3.okx.com/onchain-os/dev-portal](https://web3.okx.com/onchain-os/dev-portal)
