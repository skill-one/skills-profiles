# OKX CEX 智能资金 CLI

智能资金排行榜、交易者分析、仓位追踪和聚合共识信号。

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置内容中的 `metadata.version` 作为步骤 2 的参考。

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 配置凭证：
   ```bash
   okx config init   # 选择站点 -> 按照浏览器 OAuth 流程操作
   ```
3. 验证：`okx smartmoney traders-by-filter --limit 5`

> **安全提示**：切勿在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

---

## 凭证与配置文件检查

在运行任何需要认证的命令之前，请同时运行以下命令——`okx auth status --json` 中的 `apiKey` 字段是认证二进制程序的内部状态，无论 `~/.okx/config.toml` 是否有 API 密钥配置文件，它始终为 `false`。`okx config show --json` 是 API 密钥存在的唯一权威来源。认证方法在 [预检查](../_shared/preflight.md) 步骤 2 中检测到，并会记住用于会话。

```bash
okx config show --json      # 揭示 API 密钥配置文件 (TOML 配置)
okx auth status --json      # 揭示 OAuth 会话状态 (认证二进制程序状态)
```

按此顺序应用——第一个匹配项生效：

- `config show --json` 包含非空的 `api_key` 字段的任何配置文件 → **API 密钥模式**。继续操作。
- 无 API 密钥配置文件 **并且** `auth status --json` 返回 `"status":"logged_in"` → **OAuth 模式**。继续操作。
- 无 API 密钥配置文件 **并且** `"status":"pending"` — 登录正在进行中，等待其完成。
- 无 API 密钥配置文件 **并且** `"status":"not_logged_in"` — **停止**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

智能资金不支持模拟模式（排行榜数据仅实时有效）。始终使用实时模式静默操作——除非出现错误，否则不要提及它。
- **API 密钥用户**：使用 `--profile <live-profile>`（没有 `demo=true` 的配置文件）。
- **OAuth 用户**：无需标志（实时是默认模式）。

**遇到认证错误（401 / "会话过期" / "先运行 `okx auth login`"）**：立即停止，加载 `okx-cex-auth` 技能并按照重新认证步骤操作，然后重试。

---

## 技能路由

| 用户意图 | 路由到技能 |
|---|---|
| 市场价格、行情、K线图 | `okx-cex-market` |
| 现货 / 互换 / 期货 / 期权订单 | `okx-cex-trade` |
| 账户余额、仓位、转账 | `okx-cex-portfolio` |
| 网格 / DCA 交易机器人 | `okx-cex-bot` |
| 简易收益、闪电收益、链上收益、双币赢或自动赚币 | `okx-cex-earn` |
| 智能资金排行榜、信号、交易者分析 | **此技能** |

---

## 命令索引（10 个命令，全部只读）

### 交易者系列（6 个）

| 命令 | 类型 | 认证 | 描述 |
|---|---|---|---|
| `smartmoney traders-by-filter` | 读取 | 需要 | 根据池条件（周期 / 最小 PnL / 最小胜率 / 最大回撤 / 最小 AUM）进行排行榜排名。按 `authorId` 分页。名称使用 `min*` / `max*` 前缀——与信号端的 `*Tier` 命名空间不冲突。 |
| `smartmoney performance-by-trader --authorIds <id1,id2>` | 读取 | 需要 | 一个或多个 authorIds 的 PnL / 胜率配置文件。`--sortBy <pnl\|pnlRatio>`（默认 `pnl`）和 `--period <3\|7\|30\|90>`（默认 `90`）控制排名和回溯窗口。 |
| `smartmoney search-trader --keyword <name>` | 读取 | 需要 | 通过昵称关键词搜索顶级交易员（最多 10 个结果，按粉丝数量排名）。 |
| `smartmoney trader-positions --authorId <id>` | 读取 | 需要 | 一个交易者的当前持仓。按 `--instId <BTC-USDT-SWAP>`（或裸基础货币）过滤。 |
| `smartmoney trader-positions-history --authorId <id>` | 读取 | 需要 | 带有已实现 PnL 的已平仓仓位历史。按 `posId` 分页。 |
| `smartmoney trader-orders-history --authorId <id>` | 读取 | 需要 | 订单 / 成交记录。按 `ordId` 分页。 |

### 信号 / 货币系列（4 个）

| 命令 | 类型 | 认证 | 描述 |
|---|---|---|---|
| `smartmoney signal-overview-by-filter` | 读取 | 需要 | 多资产信号，按层级过滤的池。通过 `--topInstruments`（前 N 个最热门）或 `--instCcyList BTC,ETH,SOL`（特定）选择货币——必须且仅能选择一个。使用此命令发现智能资金中最热门的货币。 |
| `smartmoney signal-overview-by-trader --authorIds <id1,id2>` | 读取 | 需要 | 在一组手动选择的交易员（authorIds-直接查找）上聚合多资产信号。通过 `--topInstruments` 或 `--instCcyList` 选择货币。`--sortBy`（默认 `pnl`）和 `--period`（默认 `7`）控制能力指标。能力层级过滤器（pnlTier / winRateTier / 等）未公开。 |
| `smartmoney signal-trend-by-filter --instCcy <ccy> [--asOfTime <yyyyMMddHH>]` | 读取 | 需要 | 以 `asOfTime`（默认为当前 UTC 小时）为基准的单货币智能资金信号时间序列，按层级过滤的池。`--granularity 1h\|1d`，`--limit` 控制桶数量。 |
| `smartmoney signal-trend-by-trader --authorIds <id1,id2> --instCcy <ccy> [--asOfTime <yyyyMMddHH>]` | 读取 | 需要 | 在一组手动选择的交易员（authorIds-直接查找）上聚合单货币智能资金信号。`--granularity 1h\|1d`（默认 `1h`），`--sortBy`（默认 `pnl`），`--period`（默认 `7`）。能力层级过滤器未公开。 |

> **时间锚点**：`signal-trend-by-{filter,trader}` 接受可选的 `--asOfTime <yyyyMMddHH>`（10 位 UTC 小时，例如 `2026050100`）。返回以该锚点结束的最新 `--limit` 桶。省略 `--asOfTime` 以使用当前 UTC 小时。`signal-overview-by-{filter,trader}` 没有暴露任何时间输入——处理器始终使用当前小时。

> **多货币选择**：`signal-overview-by-filter` 和 `signal-overview-by-trader` 接受 `--topInstruments`（前 N 个最热门）**或** `--instCcyList BTC,ETH,SOL`（显式基础货币列表）。这两个标志是互斥的。不传递任何内容将默认为 `--topInstruments=20`。

> **⚠ 仅线性范围**：所有四个 `signal-*` 命令仅聚合 **USDT 融资和 USDS 融资合约**。币融资合约（`BTC-USD-SWAP`，`BTC-USD-DELIVERY`，`ETH-USD-SWAP`，…）在上游被排除——一个交易员的币融资仓位会从 `longNotional` / `shortNotional` / `tradersWithPosition` 中静默移除。如果一个交易员持有大量币融资敞口，但该币上没有线性头寸，则他们根本不会出现在信号中。要查看一个交易员的完整仓位簿，包括币融资，请运行 `smartmoney trader-positions --authorId <id>`。

> **需要交易者的完整信息？** 旧的 `smartmoney trader` 组合命令已移除。并行运行 `performance-by-trader`，`trader-positions` 和 `trader-orders-history`。

有关完整命令语法和参数，请阅读 `{baseDir}/references/trader-commands.md` 和 `{baseDir}/references/signal-commands.md`。

---

## 操作流程

### 第 0 步 — 凭证与配置文件检查

在运行任何需要认证的命令之前：参见 [凭证与配置文件检查](#credential--profile-check)。始终静默使用实时模式。

### 第 1 步 — 确定意图

**交易者发现 / 排名：**
- "推荐交易员" / "top traders" / "牛人榜" → 使用 `smartmoney traders-by-filter` 进行排序/过滤。参见 `{baseDir}/references/trader-commands.md`。
- "查看某个交易员" / "trader detail" → 并行运行 `performance-by-trader`，`trader-positions`，`trader-orders-history`（旧的组合 `smartmoney trader` 已移除）。
- "搜索 alice / 小明" / "按昵称查找交易员" → `smartmoney search-trader --keyword <name>`（返回 ≤10 个匹配项，并包含 `authorId` 以供其他工具使用）。
- "验证这些 authorIds" / 已知 authorId → `smartmoney performance-by-trader --authorIds <id1,id2>`（直接查找；`--sortBy` / `--period` 受到尊重，默认 `pnl` / `90`）。
- "他的当前持仓" / "current positions only" → `smartmoney trader-positions --authorId <id>`。
- "他的成交记录" / "trade history" → `smartmoney trader-orders-history --authorId <id>`（分页）。
- "历史平仓" / "closed positions" / "已实现 PnL 追踪记录" → `smartmoney trader-positions-history --authorId <id>`（分页）。

**信号分析：**
- "BTC 聪明钱信号" / "smart money signal for BTC" → `smartmoney signal-overview-by-filter --instCcyList BTC`。参见 `{baseDir}/references/signal-commands.md`。
- "BTC ETH SOL 这几个币的信号" / "signals for these specific coins" → `smartmoney signal-overview-by-filter --instCcyList BTC,ETH,SOL`。
- "这几个交易员看哪些币？" / "这些特定交易员的一致意见" → `smartmoney signal-overview-by-trader --authorIds <id1,id2>`（默认为该组中最热门的 20 个，或传递 `--instCcyList`）。
- "聪明钱关注哪些币？" / "智能资金当前正在交易什么？" → `smartmoney signal-overview-by-filter`（默认为 `--topInstruments=20`）。参见 `{baseDir}/references/signal-commands.md`。
- "信号趋势" / "signal trend over time" → `smartmoney signal-trend-by-filter --instCcy <ccy> [--asOfTime <yyyyMMddHH>] [--limit 24]`（或 `signal-trend-by-trader --authorIds <ids> --instCcy <ccy>` 以获取 authorIds 范围的趋势）。

### 第 2 步 — 执行并展示

所有命令都是只读的——无需确认。始终传递 `--json` 并将结果渲染为 Markdown 表格。

对于多步骤工作流（推荐交易员然后深入挖掘，带上下文的信号分析），请阅读 `{baseDir}/references/workflows.md`。

---

## 全局说明

- **安全提示**：切勿要求用户将 API 密钥或秘密粘贴到聊天中。
- **输出**：始终传递 `--json` 到列表/查询命令并将结果渲染为 Markdown 表格——切勿粘贴原始终端输出。
- **网络错误**：如果命令因连接错误失败，提示用户检查 VPN：`curl -I https://www.okx.com`
- **语言**：始终使用用户的语言进行响应。
- **时间输入**：`signal-trend-by-{filter,trader}` 接受可选的 `--asOfTime <yyyyMMddHH>` 锚点（10 位 UTC 小时）；省略以使用当前 UTC 小时。`--limit` 控制以该锚点结束返回的桶数量。`signal-overview-by-{filter,trader}` 不接受时间输入——处理器始终使用当前小时。

有关数字/时间格式和响应结构约定，请阅读 `{baseDir}/references/templates.md`。
