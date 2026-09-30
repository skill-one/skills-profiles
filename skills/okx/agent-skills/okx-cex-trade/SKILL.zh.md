---
name: okx-cex-trade
description: 在用户请求“购买BTC”、“卖出ETH”、“挂限价单”、“挂市价单”、“取消我的订单”、“修改我的订单”、“做多BTC永续合约”、“做空ETH掉期合约”、“开仓”、“平仓”、“设置止盈”、“限价止盈”、“立即止盈”、“设置止损”、“自我交易防范”、“STP模式”、“收盘自动取消”、“跟踪止损”、“待成交单”、“追价单”、“冰山单”、“TWAP”、“拆分订单”、“大额订单”、“设置杠杆”、“查询我的订单”、“成交历史”、“买入看涨期权”、“卖出看跌期权”、“期权链”、“隐含波动率”、“IV”、“希腊字母”、“Delta”、“Gamma”、“事件合约”、“买入Yes”、“买入No”、“买入Up”、“买入Down”、“预测市场”，或任何在OKX CEX上请求开仓、取消或修改现货、掉期、期货、期权或事件合约订单的请求时使用。涵盖条件（止盈/止损/跟踪）算法订单。需要API凭证。请勿用于市场数据（okx-cex-market）、账户余额（okx-cex-portfolio）或机器人（okx-cex-bot）。
---

# OKX CEX 交易 CLI

在 OKX 交易所上进行现货、永续互换、交割期货、**期权**和**事件合约**的订单管理。下单、撤单、修改和监控订单；查询期权链和希腊字母；交易二元结果事件合约（是/否，涨/跌）；设置止盈/止损和追踪止损；管理杠杆和仓位。**需要 API 凭证。**

> **CLI 与 MCP 工具名称** — 子命令使用空格 (`okx swap algo place`, `okx bot grid create`)，而不是连字符。**不要**将 MCP 工具标识符 (`swap_place_algo_order`) 转换为连字符连接的 CLI 命令 (`okx swap place-algo`) — 那将返回“未知命令”。每个模块的映射表位于 `references/<module>-commands.md`。

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置的 `metadata.version` 作为步骤 2 的参考。

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 配置凭证：
   ```bash
   okx config init   # 选择站点 -> 按照浏览器 OAuth 流程
   ```
3. 使用演示模式（模拟交易，无真实资金）：
   ```bash
   okx --demo spot orders
   ```

> **安全**：**永远不要**在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

## 凭证与配置文件检查

**在任何经过身份验证的命令之前运行此检查。** 身份验证方法在 [预检查](../_shared/preflight.md) 步骤 2 中检测到，并会为会话记住。

### 步骤 A — 验证凭证

运行**两个**命令 — `okx auth status --json` 的 `apiKey` 字段是身份验证二进制程序的内部状态，无论 `~/.okx/config.toml` 是否有 API 密钥配置文件，它始终是 `false`。`okx config show --json` 是 API 密钥存在的唯一权威来源。

```bash
okx config show --json      # 揭示 API 密钥配置文件 (TOML 配置)
okx auth status --json      # 揭示 OAuth 会话状态 (身份验证二进制程序状态)
```

按**此顺序**应用 — 第一个匹配项生效：

- `config show --json` 包含非空的 `api_key` 字段的任何配置文件 → **API 密钥模式**。继续步骤 B。
- 没有 API 密钥配置文件 **并且** `auth status --json` 返回 `"status":"logged_in"` → **OAuth 模式**。继续步骤 B。
- 没有 API 密钥配置文件 **并且** `"status":"pending"` — 登录正在进行中，等待其完成。
- 没有 API 密钥配置文件 **并且** `"status":"not_logged_in"` — **停止所有操作**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

### 步骤 B — 确认交易模式

**解析规则**：
1. 当前消息意图明确（例如 "real" / "实盘" / "live" → live；"test" / "模拟" / "demo" → demo）→ 使用它并通知用户
2. 当前消息没有明确的声明 → 检查对话上下文以查找先前的选择：
   - 找到 → 重用它，通知用户
   - 未找到 → 询问：`"Live (实盘) or Demo (模拟盘)?"` — 等待答案后再继续

**如何应用模式取决于身份验证方法（在步骤 A 中检测到）：**

| 身份验证方法 | 实盘 (实盘) | 模拟盘 (模拟盘) |
|---|---|---|
| **API 密钥** | `--profile <实盘配置文件>` | `--profile <模拟盘配置文件>` |
| **OAuth** | *(不需要标志，实盘是默认值)* | `--demo` |

- **API 密钥用户**：运行 `okx config show --json` 以发现可用的配置文件名称及其 `demo` 设置。使用 `--profile <名称>` 选择正确的配置文件。
- **OAuth 用户**：省略标志进行实盘交易；添加 `--demo` 进行模拟交易。**不要**使用 `--profile` 切换模式。

### 处理身份验证错误

**身份验证错误**（错误包含 "401"、"会话过期" 或 "首先运行 `okx auth login`"）：
1. **立即停止** — 不要重试相同的命令
2. 通知用户："身份验证失败。您的会话可能已过期。"
3. 加载 `okx-cex-auth` 技能并按照重新身份验证步骤操作
4. 成功重新身份验证后，重试原始命令

## 演示模式与实盘模式

| 模式 | 资金 | API 密钥参数 | OAuth 参数 |
|---|---|---|---|
| 实盘 (live) | 真实资金 — 不可逆 | `--profile <实盘配置文件>` | *(默认，不需要标志)* |
| 模拟盘 (demo) | 模拟资金 — 无真实资金 | `--profile <模拟盘配置文件>` | `--demo` |

**规则**：
1. 交易模式在**每个经过身份验证的命令**上都是**必需的** — 在“凭证与配置文件检查”步骤 B 中确定
2. 每个命令后的响应必须附加：`[模式：实盘]` 或 `[模式：模拟盘]`

## 技能路由

- 对于市场数据（价格、图表、深度、资金费率）→ 使用 `okx-cex-market`
- 对于账户余额、盈亏、仓位、费用、转账 → 使用 `okx-cex-portfolio`
- 对于常规的现货/互换/期货/期权/算法订单 → 使用 `okx-cex-trade`（此技能）
- 对于**浏览/发现**事件合约（有哪些可用、有多少、列出活跃的）→ 使用 `okx-cex-trade` 与 `okx event browse` / `okx event series`
- 对于**交易**事件合约（下单/撤单/修改预测市场订单）→ 使用 `okx-cex-trade` 与 `okx event place` / `okx event cancel` / `okx event amend`
- 对于网格和 DCA 交易机器人 → 使用 `okx-cex-bot`

> **重要**：当用户询问关于事件合约或预测市场的“合约”时，路由到此技能 — **不要**路由到 `okx-cex-portfolio`。投资组合不处理事件合约 — 它仅涵盖账户余额、仓位、盈亏和转账。

## 期权衍生品 Sz 处理

### ⚠ 关键：下单前始终验证合约面值

在下达任何 SWAP/FUTURES/OPTION 订单之前，调用 `market_get_instruments` 获取 `ctVal`（合约面值）。**不要**假设合约大小 — 它们因工具而异（例如 ETH-USDT-SWAP = 0.1 ETH/合约，BTC-USDT-SWAP = 0.01 BTC/合约）。

使用 `ctVal` 来：
- 计算从用户预期仓位大小正确的合约数量
- 提交订单前验证保证金要求
- 向用户显示实际仓位价值：`sz × ctVal × 价格`

### SWAP 和 FUTURES 订单

**三种 `tgtCcy` 模式用于 USDT 计价的尺寸**：

| `--tgtCcy` | sz 含义 | 转换公式 | 示例：在 10 倍杠杆下 "500U" |
|---|---|---|---|
| `base_ccy` (默认) | 合约数量 | 无转换 | 500 合约 |
| `quote_ccy` | USDT 名义价值 | `floor(sz / (ctVal * lastPx))` | 500 USDT 名义价值 |
| `margin` | USDT 保证金成本 | `floor(sz * lever / (ctVal * lastPx))` | 500 USDT 保证金 = 5000 USDT 名义价值 |

**当用户指定 USDT 金额**（例如 "200U"、"500 USDT"、"1000 美元”）：
→ **模糊** — 这可能意味着名义价值或保证金成本。
  您必须在使用前要求用户澄清：
  - **名义价值**：sz = USDT 中的仓位价值（例如 500 USDT 直接购买 500 USDT 价值的合约）
  - **保证金成本**：实际仓位 = sz × 杠杆（例如 500 USDT 保证金在 10× = 5000 USDT 名义仓位）
  等待用户的答案后再继续。
- 如果名义价值 → 使用 `--tgtCcy quote_ccy`
- 如果保证金成本 → 使用 `--tgtCcy margin`

**当用户指定合约**（例如 "2 张"、"5 合约”）：
→ 首先通过 `market_get_instruments` 验证 `ctVal`，然后使用 `--sz` 与合约数量。向用户确认："X 合约 = X × ctVal 基础资产，总价值 ≈ $Y"。

**当用户给出一个没有单位的纯数字**（用于 swap/futures）：
→ **模糊** — 您必须在使用前要求用户澄清：
  - **合约数量**：X 合约（每个价值 ctVal 的基础资产）
  - **USDT 名义价值**：USDT 中的仓位价值
  - **USDT 保证金成本**：保证金金额（实际仓位 = X × 杠杆）
  等待用户的答案后再继续。

⚠ **逆合约** (`*-USD-SWAP`, `*-USD-YYMMDD`)：`tgtCcy=quote_ccy` 和 `tgtCcy=margin` 也适用（注意：`quote_ccy` = 美元，不是 USDT，对于逆合约工具）。始终警告："这是一个逆合约。保证金和盈亏以 BTC 结算，而不是 USDT。"

### 期权订单

当用户为期权指定 USDT 金额时，使用 `--tgtCcy quote_ccy`（名义价值）或 `--tgtCcy margin`（保证金成本）并传递金额作为 `--sz`。系统会自动转换为合约。注意：期权合约通常具有较大的面值（例如 ctVal=1 BTC ≈ $84,000），因此 1 合约的最低 USDT 金额很高。对于期权卖方（`cross`/`isolated` tdMode），`margin` 模式会自动考虑杠杆。

## 快速入门

```bash
# 现货买入 0.01 BTC
okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.01

# 买入 10 美元价值的 SOL (现货，USDT 金额)
okx spot place --instId SOL-USDT --side buy --ordType market --sz 10 --tgtCcy quote_ccy

# 现货限价卖出 0.01 BTC，价格为 100,000 美元
okx spot place --instId BTC-USDT --side sell --ordType limit --sz 0.01 --px 100000

# 每份 BTC 永续合约多头（交叉保证金）
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1 \
  --tdMode cross --posSide long

# 买入 1000 USDT 名义价值的 BTC 永续合约（自动转换为合约）
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1000 \
  --tgtCcy quote_ccy --tdMode cross --posSide long

# 使用 500 USDT 保证金在当前杠杆下多头（例如 10× → 5000 USDT 名义价值）
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 500 \
  --tgtCcy margin --tdMode cross --posSide long

# 带有附加止盈/止损的 1 合约多头（一步）
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1 \
  --tdMode cross --posSide long \
  --tpTriggerPx 105000 --tpOrdPx=-1 --slTriggerPx 88000 --slOrdPx=-1

# 完全以市价关闭 BTC 永续合约多头仓位
okx swap close --instId BTC-USDT-SWAP --mgnMode cross --posSide long

# 为 BTC 永续合约设置 10 倍杠杆（交叉）
okx swap leverage --instId BTC-USDT-SWAP --lever 10 --mgnMode cross

# 为现货 BTC 仓位设置止盈/止损
okx spot algo place --instId BTC-USDT --side sell --ordType oco --sz 0.01 \
  --tpTriggerPx 105000 --tpOrdPx=-1 \
  --slTriggerPx 88000 --slOrdPx=-1

# 在 BTC 永续合约多头上设置追踪止损（回调 2%）
okx swap algo trail --instId BTC-USDT-SWAP --side sell --sz 1 \
  --tdMode cross --posSide long --callbackRatio 0.02

# 查看开放的现货订单
okx spot orders

# 查看开放的互换仓位
okx swap positions

# 撤销一个现货订单
okx spot cancel --instId BTC-USDT --ordId <ordId>

# --- 事件合约 ---
# 列出事件系列
okx event series

# 浏览系列中的实时市场
okx event markets BTC-ABOVE-DAILY --state live

# 下单事件合约
okx event place --instId BTC-ABOVE-DAILY-260224-1600-70000 --side buy --outcome YES --sz 10
```

## 命令索引

### 现货订单（12 个命令）

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 1 | `okx spot place` | 写入 | 下单现货订单（市价/限价/仅限挂单/FOK/IOC） |
| 2 | `okx spot cancel` | 写入 | 撤销现货订单 |
| 3 | `okx spot amend` | 写入 | 修改现货订单价格或数量 |
| 4 | `okx spot algo place` | 写入 | 下单现货止盈/止损算法订单 |
| 5 | `okx spot algo amend` | 写入 | 修改现货止盈/止损水平 |
| 6 | `okx spot algo cancel` | 写入 | 撤销现货算法订单 |
| 7 | `okx spot algo trail` | 写入 | 下单现货追踪止损订单 |
| 8 | `okx spot orders` | 读取 | 列出开放的或历史的现货订单 |
| 9 | `okx spot get` | 读取 | 单个现货订单详情 |
| 10 | `okx spot fills` | 读取 | 现货交易成交历史 |
| 11 | `okx spot algo orders` | 读取 | 列出现货止盈/止损算法订单 |
| 12 | `okx spot leverage` | 写入 | 为现货**保证金**设置杠杆（借入）。层级级 (`--instId`) 或货币级交叉 (`--ccy`，需要借入启用/多货币/投资组合保证金) |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/spot-commands.md`。

### 互换 / 永续订单（15 个命令）

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 13 | `okx swap place` | 写入 | 下单永续互换订单 |
| 14 | `okx swap cancel` | 写入 | 撤销互换订单 |
| 15 | `okx swap amend` | 写入 | 修改互换订单价格或数量 |
| 16 | `okx swap close` | 写入 | 以市价关闭整个仓位 |
| 17 | `okx swap leverage` | 写入 | 为工具设置杠杆 |
| 18 | `okx swap algo place` | 写入 | 下单互换止盈/止损算法订单 |
| 19 | `okx swap algo trail` | 写入 | 下单互换追踪止损订单 |
| 20 | `okx swap algo amend` | 写入 | 修改互换算法订单 |
| 21 | `okx swap algo cancel` | 写入 | 撤销互换算法订单 |
| 22 | `okx swap positions` | 读取 | 开放的永续互换仓位 |
| 23 | `okx swap orders` | 读取 | 列出开放的或历史的互换订单 |
| 24 | `okx swap get` | 读取 | 单个互换订单详情 |
| 25 | `okx swap fills` | 读取 | 互换交易成交历史 |
| 26 | `okx swap get-leverage` | 读取 | 当前杠杆设置 |
| 27 | `okx swap algo orders` | 读取 | 列出互换算法订单 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/swap-commands.md`。

### 期货 / 交割订单（15 个命令）

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 28 | `okx futures place` | 写入 | 下单交割期货订单 |
| 29 | `okx futures cancel` | 写入 | 撤销交割期货订单 |
| 30 | `okx futures amend` | 写入 | 修改交割期货订单价格或数量 |
| 31 | `okx futures close` | 写入 | 以市价关闭整个期货仓位 |
| 32 | `okx futures leverage` | 写入 | 为期货工具设置杠杆 |
| 33 | `okx futures algo place` | 写入 | 下单期货止盈/止损算法订单 |
| 34 | `okx futures algo trail` | 写入 | 下单期货追踪止损订单 |
| 35 | `okx futures algo amend` | 写入 | 修改期货算法订单 |
| 36 | `okx futures algo cancel` | 写入 | 撤销期货算法订单 |
| 37 | `okx futures orders` | 读取 | 交割期货订单 |
| 38 | `okx futures positions` | 读取 | 开放的交割期货仓位 |
| 39 | `okx futures fills` | 读取 | 交割期货成交历史 |
| 40 | `okx futures get` | 读取 | 单个交割期货订单详情 |
| 41 | `okx futures get-leverage` | 读取 | 当前期货杠杆设置 |
| 42 | `okx futures algo orders` | 读取 | 列出期货算法订单 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/futures-commands.md`。

### 期权订单（10 个命令）

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 43 | `okx option instruments` | 读取 | 期权链：列出基础资产的可用合约 |
| 44 | `okx option greeks` | 读取 | 通过基础资产获取隐含波动率 + 希腊字母（delta/gamma/theta/vega） |
| 45 | `okx option place` | 写入 | 下单期权订单（看涨或看跌，买方或卖方） |
| 46 | `okx option cancel` | 写入 | 撤销未成交的期权订单 |
| 47 | `okx option amend` | 写入 | 修改期权订单价格或数量 |
| 48 | `okx option batch-cancel` | 写入 | 批量撤销最多 20 个期权订单 |
| 49 | `okx option orders` | 读取 | 列出期权订单（实时 / 历史 / 归档） |
| 50 | `okx option get` | 读取 | 单个期权订单详情 |
| 51 | `okx option positions` | 读取 | 带实时希腊字母的开放期权仓位 |
| 52 | `okx option fills` | 读取 | 期权交易成交历史 |

有关完整命令语法、USDT 到合约转换公式、tdMode 规则和边缘情况，请阅读 `{baseDir}/references/options-commands.md`。

### 事件合约订单（9 个命令）

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 53 | `okx event browse` | 读取 | 浏览按类型分组的活动事件合约（系列 + 单次调用中的实时市场） |
| 54 | `okx event series` | 读取 | 列出事件系列（例如 BTC-ABOVE-DAILY, BTC-UPDOWN-15MIN） |
| 55 | `okx event events <seriesId>` | 读取 | 列出系列中的事件 |
| 56 | `okx event markets <seriesId>` | 读取 | 列出市场；过期包括结果和结算价值 |
| 57 | `okx event place ...` | 写入 | 下单事件订单（结果必需） |
| 58 | `okx event amend <instId> <ordId>` | 写入 | 修改事件订单（价格/数量） |
| 59 | `okx event cancel <instId> <ordId>` | 写入 | 撤销事件订单 |
| 60 | `okx event orders` | 读取 | 待处理或历史订单 |
| 61 | `okx event fills` | 读取 | 成交历史 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/event-commands.md`。

## 操作流程

### 第 0 步 — 身份凭证与用户资料检查

在执行任何经过身份验证的命令前：请参考 [身份凭证与用户资料检查](#credential--profile-check)。在执行前确定认证方式和交易模式。

在每次命令结果后：附加 `[模式：实盘]` 或 `[模式：模拟盘]`。

### 第 1 步 — 确定合约类型和操作

**现汇** (instId 格式：`BTC-USDT`)：
- 下单/取消/修改订单 → `okx spot place/cancel/amend`
- 停损/止盈条件单 → `okx spot algo place/amend/cancel`
- 跟据止盈 → `okx spot algo trail`
- 查询 → `okx spot orders/get/fills/algo orders`

**掉期/永续合约** (instId 格式：`BTC-USDT-SWAP`)：
- 下单/取消/修改订单 → `okx swap place/cancel/amend`
- 平仓 → `okx swap close`
- 杠杆 → `okx swap leverage` / `okx swap get-leverage`
- 停损/止盈条件单 → `okx swap algo place/amend/cancel`
- 跟据止盈 → `okx swap algo trail`
- 查询 → `okx swap positions/orders/get/fills/get-leverage/algo orders`

**期货/交割** (instId 格式：`BTC-USDT-<YYMMDD>`)：
- 下单/取消/修改订单 → `okx futures place/cancel/amend`
- 平仓 → `okx futures close`
- 杠杆 → `okx futures leverage` / `okx futures get-leverage`
- 停损/止盈条件单 → `okx futures algo place/amend/cancel`
- 跟据止盈 → `okx futures algo trail`
- 查询 → `okx futures orders/positions/fills/get/get-leverage/algo orders`

**期权** (instId 格式：`BTC-USD-250328-95000-C` 或 `...-P`)：
- 第 1 步（必需）：查找有效 instId → `okx option instruments --uly BTC-USD`
- 第 2 步（推荐）：检查隐含波动率和希腊字母 → `okx option greeks --uly BTC-USD`
- 下单/取消/修改 → `okx option place/cancel/amend`
- 批量取消 → `okx option batch-cancel --orders '[...]'`
- 查询 → `okx option orders/get/positions/fills`
- **tdMode**：买方为 `cash`；卖方为 `cross` 或 `isolated`

**事件合约**：

合约 ID (`instId`, API 字段) 格式：对于“目标价以上”/“触碰目标”合约（例如 `BTC-ABOVE-DAILY-260224-1600-70000`），为 `{UNDERLYING}-{TYPE}-{YYMMDD}-{HHMM}-{STRIKE}`；对于“价格方向（上涨/下跌）”合约（例如 `BTC-UPDOWN-15MIN-260224-1600-1615`），为 `{UNDERLYING}-{TYPE}-{YYMMDD}-{START}-{END}`。始终从 `okx event markets <seriesId>` 获取合约 ID —— 不要猜测或使用占位符。

系列 ID (`seriesId`, API 字段)：人类可读（例如 `BTC-ABOVE-DAILY`、`BTC-UPDOWN-15MIN`）或内部随机字符串（例如 `FMQRZ`）。两者均适用于后续命令。从 `okx event series` 获取。

事件合约交易流程：
1. **发现** → `okx event browse`（首选，一次调用返回系列 + 实盘市场）或 `okx event series` — 结果按类型分组显示；突出显示命名系列；始终显示系列 ID
2. **浏览实盘市场** → `okx event markets <seriesId> --state live` — 获取每个可交易合约的合约 ID；如果显示实时价格，它是事件合约价格（0.01–0.99），不是标的资产价格 —— 反映了在积极交易时的市场隐含概率
3. **检查事件详情** → `okx event events <seriesId>`
4. **确认 + 下单** → `okx event place <instId> <side> <outcome> <sz>` — 仅在用户明确确认后
5. **跟踪** → `okx event orders --status open` / `okx account positions --instType EVENTS`
6. **平仓或结算** → 通过 `okx event place <instId> sell <outcome> <sz>` 卖出，或等待 `--state expired`

边缘情况：
- **结算结果**：`okx event markets <seriesId> --state expired` — 没有单独的结束工具

**事件合约 sz 规则**：

- **市价单** (`ordType=market`)：`--sz` 是计价货币金额。
- **限价单** (`ordType=limit` / `post_only`)：`--sz` 是合约数量（整数）。每个合约结算 1 单位计价货币；每份合约成本 = `px`（事件合约价格，0.01–0.99）。例如 10 份合约在 px=0.5 时成本为 5。
- **px 语义**：`px` 是事件合约价格（0.01–0.99），不是标的资产价格。在积极交易时，它反映了市场隐含概率。示例：`px=0.6` 表示市场将事件定价在约 60%。
- **结果显示**：过期/结果视图显示翻译后的值。对于 `price_up_down`，将 `YES/NO` 视为 `UP/DOWN`。

有关事件合约工作流和分步示例，请阅读 `{baseDir}/references/event-workflows.md`。

有关跨技能工作流和分步示例，请阅读 `{baseDir}/references/workflows.md`。

### 第 2 步 — 确认用户资料，然后确认写入参数

**读取命令**（订单、头寸、成交、获取、获取杠杆、algo 订单）：立即执行。

- `--history` 标志：默认为活跃/开放；仅当用户明确要求历史记录时使用 `--history`
- `--ordType` 对于 algo：`conditional` = 单个 TP 或 SL；`oco` = TP 和 SL 一起
- `--tdMode` 对于掉期/期货：`cross` 或 `isolated`；现汇始终使用 `cash`（自动设置）
- `--posSide` 对于对冲模式：`long` 或 `short`；净模式中省略

**写入命令**（下单、取消、修改、平仓、杠杆、algo）：在执行前确认关键订单细节：
- 现汇下单：确认 `--instId`、`--side`、`--ordType`、`--sz`（如果计价货币金额，则 `--tgtCcy quote_ccy`）
- 掉期/期货下单：确认 `--instId`、`--side`、`--sz`、`--tdMode`，并在用户指定 USDT 金额时**明确确认订单模式**：`--tgtCcy quote_ccy`（名义价值，sz = 头寸价值）或 `--tgtCcy margin`（保证金成本，实际头寸 = sz * 杠杆）。始终说明使用哪种模式。
- 期权下单：确认 `--instId`、`--side`、`--sz`、`--tdMode`（如果 USDT 金额，则 `--tgtCcy quote_ccy` 或 `--tgtCcy margin` — 系统自动转换）；**不要附加 TP/SL**
- 事件合约下单：确认 `--instId`、`--side`、`--outcome`、`--sz`、`--ordType`；对于市价单 sz 是计价货币金额，对于限价单 sz 是合约数量 + 需要 `--px`
- 掉期/期货平仓：确认 `--instId`、`--mgnMode`、`--posSide`
- 杠杆：确认新的杠杆以及对现有头寸的影响。**避免常见 400 错误的预检查**：(a) `--lever` 必须是标的资产允许范围内的正数（见 `okx market instruments` → `lever`）；(b) 在对冲头寸模式下，`--mgnMode isolated` 中 `--posSide` 是必需的 — 每个方向（`long`、`short`）必须**分别**设置，设置一个**不会**自动应用于另一个；(c) **组合保证金账户不能调整 SWAP/FUTURES 的 `cross` 杠杆** — OKX 将拒绝；如有疑问，请运行 `okx account config` 并检查 `acctLv`。**如果设置杠杆失败**（错误提到“取消订单或停止机器人”）：按优先级顺序排查 — (1) 首先查询待处理的 algo 订单（`swap/futures algo-orders --status pending`），因为这是最常见的障碍；(2) 如果没有 algo 订单，检查活跃机器人（`bot grid-orders`）。**不要自动取消订单或停止机器人** — 显示发现结果并让用户决定
- Algo 下单（TP/SL）：确认触发价格；使用 `--tpOrdPx=-1` 进行市价执行
- Algo 跟据止盈：确认 `--callbackRatio`（例如，`0.02` = 2%）或 `--callbackSpread`

有关每个命令的完整参数详情，请阅读相关参考文件。

### 错误建议的补救措施保护

当 OKX API 错误消息建议需要**写入操作**（取消订单、平仓头寸、停止机器人/策略、转账资金等）的修复时，您**必须****不能**自动执行这些操作。相反：

1. **报告**错误及其建议给用户，原封不动
2. **诊断** — 运行只读查询以识别阻塞项（例如，`algo-orders --status pending`、`positions`、`bot grid-orders --status active`）
3. **展示发现结果** — 向用户展示发现的内容以及需要取消/平仓/停止的具体项目
4. **在执行任何补救措施前等待明确确认**

这适用于所有错误代码，其消息建议破坏性操作，包括但不限于：
- 由待处理 algo 订单或活跃机器人阻止的设置杠杆
- 需要订单/头寸/策略清理的账户设置更改（例如，错误代码 59000、59002、59007）
- 需要平仓的头寸保证金模式切换
- 任何包含“取消”、“平仓”、“停止”、“转账 ... 前”等短语的错误

**理由**：错误消息列出所有可能的阻塞项，但实际阻塞项通常是单个项目（例如，单个 TP/SL 订单）。盲目遵循错误文本可能导致用户未打算的订单平仓或机器人关闭。

### 第 3 步 — 写入后验证

- 执行 `spot place` 后：运行 `okx spot orders` 确认订单为实盘状态，或 `okx spot fills` 如果是市价单
- 执行 `swap place` 后：运行 `okx swap orders` 或 `okx swap positions` 确认
- 执行 `swap close` 后：运行 `okx swap positions` 确认头寸大小为 0
- 执行 `futures place` 后：运行 `okx futures orders` 或 `okx futures positions` 确认
- 执行 `futures close` 后：运行 `okx futures positions` 确认头寸大小为 0
- 现汇 algo 下单/跟据止盈后：运行 `okx spot algo orders` 确认 algo 活跃
- 掉期 algo 下单/跟据止盈后：运行 `okx swap algo orders` 确认 algo 活跃
- 期货 algo 下单/跟据止盈后：运行 `okx futures algo orders` 确认 algo 活跃
- 执行取消后：运行 `okx spot orders` / `okx swap orders` / `okx futures orders` / `okx event orders` 确认订单已消失
- 执行 `event place` 后：运行 `okx event orders --status open` 确认订单为待处理状态
- 执行 `event cancel` 后：运行 `okx event orders` 确认订单已消失

## 全局注意事项

- 所有写入命令需要有效的凭证（OAuth 会话或 `~/.okx/config.toml` 中的 API 密钥）
- 认证方式和交易模式在“身份凭证与用户资料检查”中确定；请参考该部分参数规则
- `--json` 默认返回原始 OKX API v5 响应。添加 `--env` 将输出包装为 `{"env": "<live|demo>", "profile": "<name>", "data": <response>}` — 当您需要知道活跃环境和凭证资料时有用
- 速率限制：每 2 秒 60 个订单操作，每个 UID
- 批量操作（批量取消、批量修改）如果需要，可直接通过 MCP 工具执行
- 头寸模式（`net` vs `long_short_mode`）会影响是否需要 `--posSide`
- **网络错误**：如果命令因连接错误失败，提示用户检查 VPN：`curl -I https://www.okx.com`
- **能力发现**：运行 `okx list-tools --json` 获取机器可读的 JSON 列表，其中包含所有 CLI 命令、工具名称和参数 — 对于无需解析 `--help` 文本即可进行程序化枚举非常有用

有关 MCP 工具参考、输出约定和订单金额安全规则，请阅读 `{baseDir}/references/templates.md`。
