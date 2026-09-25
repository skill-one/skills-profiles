# OKX CEX 交易 CLI

在 OKX 交易所上进行现货、永续互换、交割期货、**期权**和**事件合约**的订单管理。下单、取消、修改和监控订单；查询期权链和希腊字母；交易二元结果事件合约（是/否，上/下）；设置止盈/止损和跟踪止损；管理杠杆和头寸。**需要 API 凭证。**

> **CLI 与 MCP 工具名称** — 子命令使用空格（`okx swap algo place`，`okx bot grid create`），而不是连字符。**不要**将 MCP 工具标识符（`swap_place_algo_order`）转换为连字符连接的 CLI 命令（`okx swap place-algo`）— 那将返回“未知命令”。模块映射表位于 `references/<module>-commands.md`。

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置元数据中的 `metadata.version` 作为步骤 2 的参考。

## 前置条件

1. 安装 `okx` CLI：
   ```bash
   npm install -g @okx_ai/okx-trade-cli
   ```
2. 配置凭证：
   ```bash
   okx config init   # 选择站点 -> 按照浏览器 OAuth 流程
   ```
3. 使用演示模式进行测试（模拟交易，无实际资金）：
   ```bash
   okx --demo spot orders
   ```

> **安全**：**永远不要**在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

## 凭证与配置文件检查

**在任何经过身份验证的命令之前运行此检查。** 身份验证方法在 [预检查](../_shared/preflight.md) 第 2 步期间检测到，并会为会话记住。

### 步骤 A — 验证凭证

运行**两个**命令 — `okx auth status --json` 中的 `apiKey` 字段是身份验证二进制文件的内部状态，无论 `~/.okx/config.toml` 是否有 API 密钥配置文件，它始终为 `false`。`okx config show --json` 是 API 密钥存在的唯一权威来源。

```bash
okx config show --json      # 揭示 API 密钥配置文件 (TOML 配置)
okx auth status --json      # 揭示 OAuth 会话状态 (身份验证二进制文件状态)
```

按此顺序应用 — 第一个匹配项生效：

- `config show --json` 具有非空的 `api_key` 字段 → **API 密钥模式**。继续步骤 B。
- 没有 API 密钥配置文件**并且** `auth status --json` 返回 `"status":"logged_in"` → **OAuth 模式**。继续步骤 B。
- 没有 API 密钥配置文件**并且** `"status":"pending"` — 登录正在进行中，等待其完成。
- 没有 API 密钥配置文件**并且** `"status":"not_logged_in"` — **停止所有操作**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

### 步骤 B — 确认交易模式

**解析规则：**
1. 当前消息意图明确（例如 "实盘" / "实盘" / "实盘" → 实盘；"测试" / "模拟" / "演示" → 演示）→ 使用它并通知用户
2. 当前消息没有明确的声明 → 检查对话上下文以查找先前的选择：
   - 找到 → 重用它，通知用户
   - 未找到 → 询问：`"实盘 (实盘) 或 演示 (模拟盘)?"` — 在继续之前等待答案

**应用模式的方式取决于身份验证方法（在步骤 A 中检测到）：**

| 身份验证方法 | 实盘 (实盘) | 演示 (模拟盘) |
|---|---|---|
| **API 密钥** | `--profile <实盘配置文件>` | `--profile <演示配置文件>` |
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
| 实盘 (实盘) | 真实资金 — 不可逆 | `--profile <实盘配置文件>` | *(默认，不需要标志)* |
| 演示 (模拟盘) | 模拟资金 — 无实际资金 | `--profile <演示配置文件>` | `--demo` |

**规则：**
1. 交易模式在**每个经过身份验证的命令**上都是必需的 — 在“凭证与配置文件检查”步骤 B 中确定
2. 每个命令后的响应都必须附加：`[模式：实盘]` 或 `[模式：演示]`

## 技能路由

- 对于市场数据（价格、图表、深度、资金费率）→ 使用 `okx-cex-market`
- 对于账户余额、盈亏、头寸、费用、转账 → 使用 `okx-cex-portfolio`
- 对于常规的现货/互换/期货/期权/算法订单 → 使用 `okx-cex-trade`（此技能）
- 对于**浏览/发现**事件合约（有哪些可用、有多少、列出活跃的）→ 使用 `okx-cex-trade` 并配合 `okx event browse` / `okx event series`
- 对于**交易**事件合约（下单/取消/修改预测市场订单）→ 使用 `okx-cex-trade` 并配合 `okx event place` / `okx event cancel` / `okx event amend`
- 对于网格和 DCA 交易机器人 → 使用 `okx-cex-bot`

> **重要**：当用户询问事件合约或预测市场背景下的“合约”时，路由到此技能 — **不要**路由到 `okx-cex-portfolio`。投资组合不处理事件合约 — 它仅涵盖账户余额、头寸、盈亏和转账。

## 期权合约的 Sz 处理

### ⚠ 关键：下单前始终验证合约面值

在下达任何 SWAP/FUTURES/OPTION 订单之前，调用 `market_get_instruments` 获取 `ctVal`（合约面值）。**不要**假设合约大小 — 它们因工具而异（例如 ETH-USDT-SWAP = 0.1 ETH/合约，BTC-USDT-SWAP = 0.01 BTC/合约）。

使用 `ctVal` 来：
- 计算从用户预期头寸大小正确的合约数量
- 在提交订单前验证保证金要求
- 向用户显示实际头寸价值：`sz × ctVal × 价格`

### SWAP 和 FUTURES 订单

**三种 tgtCcy 模式用于以 USDT 计价的尺寸：**

| `--tgtCcy` | sz 含义 | 转换公式 | 示例：在 10 倍杠杆下 "500U" |
|---|---|---|---|
| `base_ccy` (默认) | 合约数量 | 无转换 | 500 合约 |
| `quote_ccy` | USDT 名义价值 | `floor(sz / (ctVal * lastPx))` | 500 USDT 名义价值 |
| `margin` | USDT 保证金成本 | `floor(sz * lever / (ctVal * lastPx))` | 500 USDT 保证金 = 5000 USDT 名义价值 |

**当用户指定 USDT 金额**（例如 "200U"，"500 USDT"，"$1000"）：
→ **模糊** — 这可能意味着名义价值**或**保证金成本。
  您必须在使用前询问用户澄清：
  - **名义价值**：sz = 美元价值中的头寸价值（例如 500 USDT 买入 500 USDT 价值的合约）
  - **保证金成本**：实际头寸 = sz × 杠杆（例如 500 USDT 保证金在 10× = 5000 USDT 名义头寸）
  等待用户的答案再继续。
- 如果名义价值 → 使用 `--tgtCcy quote_ccy`
- 如果保证金成本 → 使用 `--tgtCcy margin`

**当用户指定合约**（例如 "2 张"，"5 合约"）：
→ 首先通过 `market_get_instruments` 验证 `ctVal`，然后使用 `--sz` 与合约数量。向用户确认："X 合约 = X × ctVal 基础资产，总价值 ≈ $Y"。

**当用户给出一个没有单位的普通数字**（用于 swap/futures）：
→ **模糊** — 您必须在使用前询问用户澄清：
  - **合约数量**：X 合约（每个合约的价值为 ctVal 的基础资产）
  - **USDT 名义价值**：美元价值中的头寸价值
  - **USDT 保证金成本**：保证金金额（实际头寸 = X × 杠杆）
  等待用户的答案再继续。

⚠ **逆合约**（`*-USD-SWAP`，`*-USD-YYMMDD`）：`tgtCcy=quote_ccy` 和 `tgtCcy=margin` 也适用（注意：逆合约的 `quote_ccy` = 美元，不是 USDT）。始终警告："这是一个逆合约。保证金和盈亏以 BTC 结算，而不是 USDT。"

### 期权订单

当用户为期权指定 USDT 金额时，使用 `--tgtCcy quote_ccy`（名义价值）或 `--tgtCcy margin`（保证金成本）并将金额作为 `--sz`。系统会自动转换为合约。注意：期权合约通常具有较大的面值（例如 ctVal=1 BTC ≈ $84,000），因此 1 合约的最低 USDT 金额很高。对于期权卖方（`cross`/`isolated` tdMode），`margin` 模式会自动考虑杠杆。

## 快速入门

```bash
# 市场买入 0.01 BTC (现货)
okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.01

# 买入 10 美元价值的 SOL (现货，USDT 金额)
okx spot place --instId SOL-USDT --side buy --ordType market --sz 10 --tgtCcy quote_ccy

# 限制卖出 0.01 BTC 在 $100,000 (现货)
okx spot place --instId BTC-USDT --side sell --ordType limit --sz 0.01 --px 100000

# 每份 BTC 永续合约多头 (交叉保证金)
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1 \
  --tdMode cross --posSide long

# 1000 USDT 名义价值的 BTC 永续合约多头 (自动转换为合约)
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1000 \
  --tgtCcy quote_ccy --tdMode cross --posSide long

# 使用 500 USDT 保证金以当前杠杆多头 (例如 10x → 5000 USDT 名义)
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 500 \
  --tgtCcy margin --tdMode cross --posSide long

# 带有止盈/止损的单步多头
okx swap place --instId BTC-USDT-SWAP --side buy --ordType market --sz 1 \
  --tdMode cross --posSide long \
  --tpTriggerPx 105000 --tpOrdPx=-1 --slTriggerPx 88000 --slOrdPx=-1

# 完全以市场方式关闭 BTC 永续合约多头头寸
okx swap close --instId BTC-USDT-SWAP --mgnMode cross --posSide long

# 为 BTC 永续合约设置 10 倍杠杆 (交叉)
okx swap leverage --instId BTC-USDT-SWAP --lever 10 --mgnMode cross

# 为现货 BTC 头寸设置止盈/止损
okx spot algo place --instId BTC-USDT --side sell --ordType oco --sz 0.01 \
  --tpTriggerPx 105000 --tpOrdPx=-1 \
  --slTriggerPx 88000 --slOrdPx=-1

# 在 BTC 永续合约多头上设置跟踪止损 (回调 2%)
okx swap algo trail --instId BTC-USDT-SWAP --side sell --sz 1 \
  --tdMode cross --posSide long --callbackRatio 0.02

# 查看开放的现货订单
okx spot orders

# 查看开放的互换头寸
okx swap positions

# 取消一个现货订单
okx spot cancel --instId BTC-USDT --ordId <ordId>

# --- 事件合约 ---
# 列出事件系列
okx event series

# 浏览系列中的实时市场
okx event markets BTC-ABOVE-DAILY --state live

# 下达事件合约订单
okx event place --instId BTC-ABOVE-DAILY-260224-1600-70000 --side buy --outcome YES --sz 10
```

## 命令索引

### 现货订单 (12 个命令)

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 1 | `okx spot place` | WRITE | 下单现货订单 (市场/限制/仅限指令/FOK/IOC) |
| 2 | `okx spot cancel` | WRITE | 取消现货订单 |
| 3 | `okx spot amend` | WRITE | 修改现货订单价格或大小 |
| 4 | `okx spot algo place` | WRITE | 下单现货止盈/止损算法订单 |
| 5 | `okx spot algo amend` | WRITE | 修改现货止盈/止损水平 |
| 6 | `okx spot algo cancel` | WRITE | 取消现货算法订单 |
| 7 | `okx spot algo trail` | WRITE | 下单现货跟踪止损订单 |
| 8 | `okx spot orders` | READ | 列出开放的或历史的现货订单 |
| 9 | `okx spot get` | READ | 单个现货订单详情 |
| 10 | `okx spot fills` | READ | 现货交易成交历史 |
| 11 | `okx spot algo orders` | READ | 列出现货止盈/止损算法订单 |
| 12 | `okx spot leverage` | WRITE | 为现货**保证金**设置杠杆（借入）。按合约级别 (`--instId`) 或货币级别交叉 (`--ccy`，需要借入/多货币/投资组合保证金） |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/spot-commands.md`。

### 互换 / 永续订单 (15 个命令)

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 13 | `okx swap place` | WRITE | 下单永续互换订单 |
| 14 | `okx swap cancel` | WRITE | 取消互换订单 |
| 15 | `okx swap amend` | WRITE | 修改互换订单价格或大小 |
| 16 | `okx swap close` | WRITE | 以市场方式关闭整个头寸 |
| 17 | `okx swap leverage` | WRITE | 为工具设置杠杆 |
| 18 | `okx swap algo place` | WRITE | 下单互换止盈/止损算法订单 |
| 19 | `okx swap algo trail` | WRITE | 下单互换跟踪止损订单 |
| 20 | `okx swap algo amend` | WRITE | 修改互换算法订单 |
| 21 | `okx swap algo cancel` | WRITE | 取消互换算法订单 |
| 22 | `okx swap positions` | READ | 开放的永续互换头寸 |
| 23 | `okx swap orders` | READ | 列出开放的或历史的互换订单 |
| 24 | `okx swap get` | READ | 单个互换订单详情 |
| 25 | `okx swap fills` | READ | 互换交易成交历史 |
| 26 | `okx swap get-leverage` | READ | 当前杠杆设置 |
| 27 | `okx swap algo orders` | READ | 列出互换算法订单 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/swap-commands.md`。

### 期货 / 交割订单 (15 个命令)

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 28 | `okx futures place` | WRITE | 下单交割期货订单 |
| 29 | `okx futures cancel` | WRITE | 取消交割期货订单 |
| 30 | `okx futures amend` | WRITE | 修改交割期货订单价格或大小 |
| 31 | `okx futures close` | WRITE | 以市场方式关闭整个期货头寸 |
| 32 | `okx futures leverage` | WRITE | 为期货工具设置杠杆 |
| 33 | `okx futures algo place` | WRITE | 下单期货止盈/止损算法订单 |
| 34 | `okx futures algo trail` | WRITE | 下单期货跟踪止损订单 |
| 35 | `okx futures algo amend` | WRITE | 修改期货算法订单 |
| 36 | `okx futures algo cancel` | WRITE | 取消期货算法订单 |
| 37 | `okx futures orders` | READ | 交割期货订单 |
| 38 | `okx futures positions` | READ | 开放的交割期货头寸 |
| 39 | `okx futures fills` | READ | 交割期货成交历史 |
| 40 | `okx futures get` | READ | 单个交割期货订单详情 |
| 41 | `okx futures get-leverage` | READ | 当前期货杠杆设置 |
| 42 | `okx futures algo orders` | READ | 列出期货算法订单 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/futures-commands.md`。

### 期权订单 (10 个命令)

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 43 | `okx option instruments` | READ | 期权链：列出基础资产的可用合约 |
| 44 | `okx option greeks` | READ | 基于基础资产的隐含波动率 + 希腊字母（delta/gamma/theta/vega） |
| 45 | `okx option place` | WRITE | 下单期权订单（看涨或看跌，买方或卖方） |
| 46 | `okx option cancel` | WRITE | 取消未成交的期权订单 |
| 47 | `okx option amend` | WRITE | 修改期权订单价格或大小 |
| 48 | `okx option batch-cancel` | WRITE | 批量取消最多 20 个期权订单 |
| 49 | `okx option orders` | READ | 列出期权订单（实时 / 历史 / 归档） |
| 50 | `okx option get` | READ | 单个期权订单详情 |
| 51 | `okx option positions` | READ | 开放的期权头寸，具有实时希腊字母 |
| 52 | `okx option fills` | READ | 期权交易成交历史 |

有关完整命令语法、USDT 转换为合约的公式、tdMode 规则和边缘情况，请阅读 `{baseDir}/references/options-commands.md`。

### 事件合约订单 (9 个命令)

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 53 | `okx event browse` | READ | 浏览活跃的事件合约，按类型分组（系列 + 实时市场在一个调用中） |
| 54 | `okx event series` | READ | 列出事件系列（例如 BTC-ABOVE-DAILY, BTC-UPDOWN-15MIN） |
| 55 | `okx event events <seriesId>` | READ | 列出系列中的事件 |
| 56 | `okx event markets <seriesId>` | READ | 列出市场；过期包括结果和结算价值 |
| 57 | `okx event place ...` | WRITE | 下达事件订单（结果必需） |
| 58 | `okx event amend <instId> <ordId>` | WRITE | 修改事件订单（价格/大小） |
| 59 | `okx event cancel <instId> <ordId>` | WRITE | 取消事件订单 |
| 60 | `okx event orders` | READ | 待处理或历史的订单 |
| 61 | `okx event fills` | READ | 成交历史 |

有关完整命令语法、参数表和边缘情况，请阅读 `{baseDir}/references/event-commands.md`。

## 操作流程

### 步骤 0 — 凭证与配置文件检查

在任何经过身份验证的命令之前：参见 [凭证与配置文件检查](#credential--profile-check)。在执行任何命令之前确定身份验证方法和交易模式。

在每次命令结果之后：附加 `[模式：实盘]` 或 `[模式：演示]`。

### 步骤 1 — 确定工具类型和操作

**现货**（instId 格式：`BTC-USDT`）：
- 下单/取消/修改订单 → `okx spot place/cancel/amend`
- TP/SL 条件 → `okx spot algo place/amend/cancel`
- 跟踪止损 → `okx spot algo trail`
- 查询 → `okx spot orders/get/fills/algo orders`

**Swap/Perpetual**（instId 格式：`BTC-USDT-SWAP`）：
- 下单/取消/修改订单 → `okx swap place/cancel/amend`
- 关闭头寸 → `okx swap close`
- 杠杆 → `okx swap leverage` / `okx swap get-leverage`
- TP/SL 条件 → `okx swap algo place/amend/cancel`
- 跟踪止损 → `okx swap algo trail`
- 查询 → `okx swap positions/orders/get/fills/get-leverage/algo orders`

**Futures/Delivery**（instId 格式：`BTC-USDT-<YYMMDD>`）：
- 下单/取消/修改订单 → `okx futures place/cancel/amend`
- 关闭头寸 → `okx futures close`
- 杠杆 → `okx futures leverage` / `okx futures get-leverage`
- TP/SL 条件 → `okx futures algo place/amend/cancel`
- 跟踪止损 → `okx futures algo trail`
- 查询 → `okx futures orders/positions/fills/get/get-leverage/algo orders`

**Options**（instId 格式：`BTC-USD-250328-95000-C` 或 `...-P`）：
- 步骤 1（必需）：找到有效的 instId → `okx option instruments --uly BTC-USD`
- 步骤 2（推荐）：检查 IV 和希腊字母 → `okx option greeks --uly BTC-USD`
- 下单/取消/修改 → `okx option place/cancel/amend`
- 批量取消 → `okx option batch-cancel --orders '[...]``
- 查询 → `okx option orders/get/positions/fills`
- **tdMode**: 买方为 `cash`；卖方为 `cross` 或 `isolated`；现货始终使用 `cash`（自动设置）

**Event Contracts**:

Instrument ID (`instId`, API 字段) 格式: `{UNDERLYING}-{TYPE}-{YYMMDD}-{HHMM}-{STRIKE}` 对于 "目标价以上" / "触碰目标" 合约（例如 `BTC-ABOVE-DAILY-260224-1600-70000`），或 `{UNDERLYING}-{TYPE}-{YYMMDD}-{START}-{END}` 对于 "价格方向 (上/下)" 合约（例如 `BTC-UPDOWN-15MIN-260224-1600-1615`). 始终从 `okx event markets <seriesId>` 获取合约 ID — 永远不要猜测或使用占位符。系列 ID (`seriesId`, API 字段): 可读的（例如 `BTC-ABOVE-DAILY`, `BTC-UPDOWN-15MIN`）或内部随机字符串（例如 `FMQRZ`）。两者都有效。从 `okx event series` 获取。

事件合约交易流程:
1. **发现** → `okx event browse`（首选，一次调用返回系列 + 实时市场）— 以分组形式显示结果；突出显示命名系列；始终显示系列 ID
2. **浏览实时市场** → `okx event markets <seriesId> --state live` — 获取可交易的每个合约的 instrument ID；如果显示实时价格，它是事件合约价格（0.01–0.99），不是基础资产价格 — 反映了在积极交易时市场隐含的概率
3. **检查事件详情** → `okx event events <seriesId>`
4. **确认 + 下单** → `okx event place <instId> <side> <outcome> <sz>` — 用户明确确认后才能
5. **跟踪** → `okx event orders --status open` / `okx account positions --instType EVENTS`
6. **退出或结算** → 通过 `okx event place <instId> sell <outcome> <sz>` 卖出，或等待 `--state expired`

**事件合约 sz 规则**:

- **市场订单** (`ordType=market`): `--sz` 是计价货币金额。
- **限价订单** (`ordType=limit` / `post_only`): `--sz` 是合约数量（整数）。每个合约结算 1 单位计价货币；每个合约成本 = `px`（事件合约价格，0.01–0.99）。例如 10 合约在 px=0.5 成本 5。
- **px 语义**: `px` 是事件合约价格（0.01–0.99），不是基础资产价格。在积极交易时，它反映了市场隐含的概率。例如 `px=0.6` 意味着市场以大约 60% 的价格定价事件。

对于事件合约工作流程和分步示例，请阅读 `{baseDir}/references/event-workflows.md`。

对于跨技能工作流程和分步示例，请阅读 `{baseDir}/references/workflows.md`。

### 步骤 2 — 确认配置文件，然后确认写入参数

**读取命令**（订单、头寸、成交、获取、获取杠杆、algo 订单）: 立即运行。

- `--history` 标志：默认为活动/开放；仅当用户明确要求历史时使用 `--history`
- `--ordType` for algo: `conditional` = 单个 TP 或 SL; `oco` = TP 和 SL 一起
- `--tdMode` for swap/futures: `cross` 或 `isolated`; 现货始终使用 `cash`（自动设置）
- `--posSide` for hedge mode: `long` 或 `short`; 在净模式中省略

**写入命令**（下单、取消、修改、关闭、杠杆、algo）: 在执行前确认关键订单详细信息一次:

- 现货下单: 确认 `--instId`, `--side`, `--ordType`, `--sz`（如果 `--tgtCcy quote_ccy` 是计价货币金额）
- 互换/期货下单: 确认 `--instId`, `--side`, `--sz`, `--tdMode`, 并**明确确认订单模式**当用户指定 USDT 金额时: `--tgtCcy quote_ccy`（名义价值，sz = 美元价值）或 `--tgtCcy margin`（保证金成本，实际头寸 = sz * 杠杆）。始终说明正在使用哪种模式。
- 期权下单: 确认 `--instId`, `--side`, `--sz`, `--tdMode`（如果 USDT 金额 — 系统会自动转换为合约）；不要附加 TP/SL
- 事件合约下单: 确认 `--instId`, `--side`, `--outcome`, `--sz`, `--ordType`; 市场订单 sz 是计价货币金额，限价订单 sz 是合约数量 + `--px` 要求
- 互换/期货关闭: 确认 `--instId`, `--mgnMode`, `--posSide`
- 杠杆: 确认新的杠杆以及对现有头寸的影响。**避免常见 400 错误的预检查**: (a) `--lever` 必须是正数，在工具的最大值内（见 `okx market instruments` → `lever`）；(b) 在对冲模式中的 `--mgnMode isolated`，`--posSide` 是必需的 — 每个方面 (`long`, `short`) 必须分别设置，设置一个方面**不会**自动应用于另一个方面；(c) **投资组合保证金账户不能调整 SWAP/FUTURES 的交叉杠杆** — OKX 将拒绝；如果不确定，请首先运行 `okx account config` 并检查 `acctLv`。
**如果设置杠杆失败**（错误提到 "取消订单或停止机器人"）: 按优先顺序解决问题 — (1) 首先查询待处理的 algo 订单 (`swap/futures algo-orders --status pending`), 因为这是最常见的阻止因素；(2) 如果没有 algo 订单, 检查活跃的机器人 (`bot grid-orders`). **不要自动取消订单或停止机器人** — 显示发现的内容，让用户决定

### 步骤 3 — 写入后验证

- 在 `spot place` 后: 运行 `okx spot orders` 以确认订单是活跃的或 `okx spot fills` 如果是市场订单
- 在 `swap place` 后: 运行 `okx swap orders` 或 `okx swap positions` 以确认
- 在 `swap close` 后: 运行 `okx swap positions` 以确认头寸大小为 0
- 在 `futures place` 后: 运行 `okx futures orders` 或 `okx futures positions` 以确认
- 在 `futures close` 后: 运行 `okx futures positions` 以确认头寸大小为 0
- 在现货 algo place/trail 后: 运行 `okx spot algo orders` 以确认 algo 是活跃的
- 在互换 algo place/trail 后: 运行 `okx swap algo orders` 以确认 algo 是活跃的
- 在期货 algo place/trail 后: 运行 `okx futures algo orders` 以确认 algo 是活跃的
- 在取消后: 运行 `okx spot orders` / `okx swap orders` / `okx futures orders` / `okx event orders` 以确认订单已消失
- 在 `event place` 后: 运行 `okx event orders --status open` 以确认订单是待处理的
- 在 `event cancel` 后: 运行 `okx event orders` 以确认订单已消失

## 全局说明

- 所有写入命令都需要有效凭证（OAuth 会话或 `~/.okx/config.toml` 中的 API 密钥）。
- 身份验证方法和交易模式在“凭证与配置文件检查”中确定；请参阅该部分以了解参数规则
- `--json` 默认返回 OKX API v5 响应的原始数据。添加 `--env` 将输出包装为 `{"env": "<实盘|演示>", "profile": "<名称>", "data": <响应>}` — 当您需要知道活动环境和凭证配置文件时，这很有用
- 速率限制：每 2 秒 60 个订单操作每个 UID
- 批量操作（批量取消、批量修改）如果需要，则可以直接使用 MCP 工具
- 头寸模式 (`net` 与 `long_short_mode`) 影响是否需要 `--posSide`
- **网络错误**：如果命令因连接错误而失败，提示用户检查 VPN: `curl -I https://www.okx.com`
- **能力发现**：运行 `okx list-tools --json` 以获取所有 CLI 命令、工具名称和参数的机器可读 JSON 列表 — 对于无需解析 `--help` 文本即可进行程序化枚举非常有用

有关 MCP 工具参考、输出约定和订单金额安全规则，请阅读 `{baseDir}/references/templates.md`.
