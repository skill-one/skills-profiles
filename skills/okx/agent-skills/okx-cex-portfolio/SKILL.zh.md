---
name: okx-cex-portfolio
description: 当用户询问“账户余额”、“我有多少USDT”、“我的资金账户”、“显示我的持仓”、“开仓”、“持仓盈亏”、“未实现盈亏”、“已平仓”、“持仓历史”、“已实现盈亏”、“账户账单”、“交易历史”、“交易手续费”、“费率等级”、“账户配置”、“最大订单量”、“我能购买多少”、“可提现金额”、“转账资金”、“将USDT转入交易账户”或“切换持仓模式”时，应使用此技能。也适用于“总资产”、“全部余额”、“所有资产”、“总持有量”、“净资产”、“我总共有多少”、“显示我所有余额”、“所有账户余额”、“资产概览”、“汇总余额”、“资产快照”、“资产快照”。需要API凭证。不应用于市场价格（使用okx-cex-market）、下单/取消订单（使用okx-cex-trade）或网格/DCA机器人（使用okx-cex-bot）。
---

# OKX CEX 组合与账户 CLI

OKX 交易所的账户余额、持仓、盈亏、账单、费用和资金转账。**需要 API 凭证。**

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
3. 使用演示模式（模拟交易，无实际资金）：
   ```bash
   okx --demo account balance
   ```

> **安全**：切勿在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

## 凭证与配置文件检查

**在任何经过身份验证的命令之前运行此检查。** 身份验证方法在 [预检查](../_shared/preflight.md) 步骤 2 中检测到，并会为会话保留。

### 步骤 A — 验证凭证

检查**两个**来源（参见 [预检查步骤 2](../_shared/preflight.md#step-2--detect-auth-method-once-per-session) 的决策表）。`okx auth status --json` 单独不足以使用——其 `apiKey` 字段始终为 `false`，并且**不反映** TOML 配置。

```bash
okx config show --json      # API-key 存在性的权威来源
okx auth status --json      # OAuth 会话状态的权威来源
```

按此顺序分支——第一个匹配的获胜：

- `config show` 具有任何具有非空 `api_key` 的配置文件——**API Key 模式**。继续步骤 B。
- 没有 API-key 配置文件 **并且** `auth status` 返回 `"status": "logged_in"` — **OAuth 模式**。继续步骤 B。
- 没有 API-key 配置文件 **并且** `auth status` 返回 `"status": "pending"` — 登录正在进行中，请等待。
- 没有 API-key 配置文件 **并且** `auth status` 返回 `"status": "not_logged_in"` — **停止所有操作**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

### 步骤 B — 确认交易模式

**解析规则：**
1. 当前消息意图明确（例如 "实盘" / "实盘" / "实盘" → 实盘；"模拟" / "模拟" / "模拟" → 模拟）→ 使用它并通知用户
2. 当前消息没有明确的声明 → 检查对话上下文以查找先前的选择：
   - 找到 → 重用它，通知用户
   - 未找到 → 询问：`"实盘 (实盘) 或 模拟盘 (模拟盘)?"` — 等待答案后再继续

**如何应用模式取决于身份验证方法（在步骤 A 中检测到）：**

| 身份验证方法 | 实盘 (实盘) | 模拟盘 (模拟盘) |
|---|---|---|
| **API Key** | `--profile <实盘配置文件>` | `--profile <模拟配置文件>` |
| **OAuth** | *(不需要标志，实盘是默认值)* | `--demo` |

- **API Key 用户**：运行 `okx config show --json` 以发现可用的配置文件名称及其 `demo` 设置。使用 `--profile <名称>` 选择正确的配置文件。
- **OAuth 用户**：省略标志进行实盘交易；添加 `--demo` 进行模拟交易。**不要**使用 `--profile` 切换模式。

### 处理身份验证错误

**身份验证错误**（错误包含 "401"、"会话过期" 或 "首先运行 `okx auth login`"）：
1. **立即停止** — 不要重试相同的命令
2. 通知用户："身份验证失败。您的会话可能已过期。"
3. 加载 `okx-cex-auth` 技能并按照重新身份验证步骤操作
4. 成功重新身份验证后，重试原始命令

## 演示模式与实盘模式

| 模式 | 资金 | API Key 参数 | OAuth 参数 |
|---|---|---|---|
| 实盘 (实盘) | 实际资金 | `--profile <实盘配置文件>` | *(默认，不需要标志)* |
| 模拟盘 (模拟) | 模拟资金 | `--profile <模拟配置文件>` | `--demo` |

```bash
# API Key 用户
okx --profile okx-prod  account balance     # 实盘
okx --profile okx-demo  account balance     # 模拟盘

# OAuth 用户
okx account balance                          # 实盘 (默认)
okx --demo account balance                   # 模拟盘
```

**规则：**
- **读取命令**（余额、持仓、账单等）：始终说明使用了哪种模式
- **写入命令**（`transfer`、`set-position-mode`）：**执行前必须确认模式**（参见 "凭证与配置文件检查" 步骤 B）；转账尤其如此——错误模式意味着错误的账户
- 每个命令后的响应必须附加：`[模式：实盘]` 或 `[模式：模拟]`

## 技能路由

- 对于市场数据（价格、图表、深度、资金费率）→ 使用 `okx-cex-market`
- 对于账户余额、盈亏、持仓、费用、转账 → 使用 `okx-cex-portfolio`（此技能）
- 对于常规的现货/掉期/期货/算法订单 → 使用 `okx-cex-trade`
- 对于网格和 DCA 交易机器人 → 使用 `okx-cex-bot`

## 快速入门

```bash
# 一次性完整资产快照（推荐第一个命令）
okx account balance-all
okx account balance-all --no-valuation
okx account balance-all --valuationCcy BTC

# 交易账户余额（所有余额 > 0 的货币）
okx account balance

# 仅检查 USDT 余额
okx account balance USDT

# 资金账户余额
okx account asset-balance

# 所有未平仓持仓，每个产品
okx account positions

# 仅一个产品的持仓 — 当用户命名产品时始终缩小范围
okx account positions --instType SWAP     # SWAP | FUTURES | OPTION | MARGIN | EVENTS

# 已平仓持仓历史记录（含已实现盈亏）
okx account positions-history

# 最近账户账单（最后 100 条）
okx account bills

# 我的交易费用等级
okx account fees --instType SPOT

# 将 100 USDT 从资金账户（6）转移到交易账户（18）
okx account transfer --ccy USDT --amt 100 --from 6 --to 18
```

## 命令索引

### 读取命令

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 1 | `okx account balance-all [ccy]` | 读取 | 一次性快照：一次调用中包含交易 + 资金 + 估值 |
| 2 | `okx account balance [ccy]` | 读取 | 交易账户净值、可用、冻结 |
| 3a | `okx account asset-balance [ccy]` | 读取 | 资金账户余额（按货币列表） |
| 3b | `okx account asset-balance [ccy] --valuation [--valuationCcy <ccy>]` | 读取 | 相同 + 跨账户估值（交易/资金/收益）；默认货币为 USDT，使用 `--valuationCcy BTC` 覆盖 |
| 4 | `okx account positions [--instType <类型>] [--instId <id>]` | 读取 | 开仓合约/掉期持仓。**当用户命名产品**（"我的掉期持仓"、"期货持仓"、"期权持仓"），传递 `--instType <类型>` (`SWAP` \| `FUTURES` \| `OPTION` \| `MARGIN` \| `EVENTS`）— 或使用该产品自己的命令（`okx swap positions`、`okx futures positions`、`okx option positions`）。仅在用户确实想要所有内容时省略过滤器：未过滤的列表更大，并将产品过滤留给模型，这是错误发生的地方 |
| 5 | `okx account positions-history` | 读取 | 已平仓持仓 + 已实现盈亏 |
| 6 | `okx account bills` | 读取 | 账户总账（存款、取款、交易） |
| 7 | `okx account fees --instType <类型>` | 读取 | 我的交易费用等级（做市商/吃单商） |
| 8 | `okx account config` | 读取 | 账户级别、持仓模式、UID |
| 9 | `okx account max-size --instId <id> --tdMode <模式>` | 读取 | 当前价格下的最大买入/卖出量 |
| 10 | `okx account max-avail-size --instId <id> --tdMode <模式>` | 读取 | 下一个订单的可用量 |
| 11 | `okx account max-withdrawal [ccy]` | 读取 | 每种货币的最大可提现金额 |

### 写入命令

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 12 | `okx account set-position-mode <模式>` | 写入 | 切换净持仓/对冲持仓模式 |
| 13 | `okx account transfer` | 写入 | 在账户之间转账资金 |

## 跨技能工作流

### 交易前余额检查
> 用户："我想买入 0.1 BTC — 我有足够的 USDT 吗？"

```
1. okx-cex-portfolio okx account balance-all                 → 一次性交易 + 资金 + 估值快照
   → 检查交易详情（交易账户中的可用余额）
   → 如果交易余额 < 需要的：检查资金详情 — 可能需要转账
2. okx-cex-market    okx market ticker BTC-USDT              → 检查当前价格
        ↓ 用户批准
3. okx-cex-trade     okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.1
```

### 机器人交易前余额检查
> 用户："我想启动一个 1000 USDT 的 BTC 网格机器人"

```
1. okx-cex-portfolio okx account balance-all                 → 一次性交易 + 资金 + 估值快照
   → 检查交易详情 ≥ 1000（网格机器人必须在交易账户中有资金）
   → 如果资金详情有 USDT 而不是：先使用账户转账
2. okx-cex-market    okx market candles BTC-USDT --bar 4H --limit 50  → 确定价格范围
        ↓ 用户批准
3. okx-cex-bot       okx bot grid create --instId BTC-USDT --algoOrdType grid \
                       --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000
```

### 净资产快速查看
> 用户："我的总资产是多少?" / "总资产多少?"

```
1. okx-cex-portfolio okx account balance-all                 → 返回 {交易, 资金, 估值, 元数据}
   → 估值.totalBal = 以 USDT 为单位的总净资产
   → 交易.totalEq = 交易账户净值
   → 资金详情 = 每种货币的资金余额
   → 元数据.partialFailure = 如果任何部分失败（仍然返回可用数据）
```

### 查看未平仓持仓和盈亏
> 用户："显示我的当前持仓以及它们的性能"

```
1. okx-cex-portfolio okx account positions                  → 开仓持仓与 UPL
2. okx-cex-portfolio okx account positions-history          → 最近已平仓持仓
3. okx-cex-market    okx market ticker BTC-USDT-SWAP        → 检查当前价格与入场价
```

### 转账和交易
> 用户："将 500 USDT 从我的资金账户转移到交易 BTC"

```
1. okx-cex-portfolio okx account asset-balance USDT         → 确认资金余额 ≥ 500
        ↓ 用户批准
2. okx-cex-portfolio okx account transfer --ccy USDT --amt 500 --from 6 --to 18
3. okx-cex-portfolio okx account balance USDT               → 确认交易余额已更新
        ↓ 准备交易
4. okx-cex-trade     okx spot place ...
```

### 进入前检查最大持仓量
> 用户："我可以用交叉保证金购买多少 BTC?"

```
1. okx-cex-portfolio okx account balance                    → 总净值
2. okx-cex-portfolio okx account max-size --instId BTC-USDT-SWAP --tdMode cross  → 最大买入/卖出量
3. okx-cex-market    okx market ticker BTC-USDT-SWAP        → 当前价格参考
```

## 操作流程

### 步骤 0 — 凭证与配置文件检查

在任何经过身份验证的命令之前：参见 [凭证与配置文件检查](#credential--profile-check)。在执行之前确定身份验证方法和交易模式。

**每个命令结果之后**：在响应中附加 `[模式：实盘]` 或 `[模式：模拟]`

### 步骤 1：识别账户操作

- 一次性检查所有余额 → `okx account balance-all`（一次调用中包含交易 + 资金 + 估值；推荐用于 "总资产 / 净值 / 所有余额")
- 检查余额 → `okx account balance`（交易净值仅）或 `okx account asset-balance`（资金余额）或 `okx account asset-balance --valuation`（跨所有账户的 USDT 估值）
- 查看未平仓持仓 → `okx account positions`
- 查看已平仓持仓 + 盈亏 → `okx account positions-history`
- 查看交易历史 → `okx account bills`
- 检查费用等级 → `okx account fees`
- 检查账户设置 → `okx account config`
- 计算订单大小 → `okx account max-size` 或 `okx account max-avail-size`
- 检查提现限额 → `okx account max-withdrawal`
- 转账资金 → `okx account transfer`
- 更改持仓模式 → `okx account set-position-mode`

### 步骤 2：立即运行读取命令 — 然后确认写入

**读取命令**（1–10）：立即运行，不需要确认。

- `ccy` 过滤器：使用货币符号，如 `USDT`、`BTC`、`ETH`
- `--instType` 用于费用/持仓：`SPOT`、`SWAP`、`FUTURES`、`OPTION`
- `--archive` 用于账单：访问默认窗口之外的旧记录
- `--tdMode` 用于 max-size：`cash`（现货）、`cross` 或 `isolated`

**写入命令**（11–12）：执行前确认一次。

- `set-position-mode`：确认模式（`net` = 单向，`long_short_mode` = 对冲模式）；切换可能会影响已平仓持仓
- `transfer`：确认 `--ccy`、`--amt`、`--from`、`--to`（账户类型：`6`=资金，`18`=交易）；首先验证源余额

### 步骤 3：写入后验证

- 在 `set-position-mode` 后：运行 `okx account config` 以确认 `posMode` 已更新
- 在 `transfer` 后：运行 `okx account balance` 和 `okx account asset-balance` 以确认余额已更新

## CLI 命令参考

### 余额全部 — 一次性聚合快照

```bash
okx account balance-all [ccy] [--accounts trading,funding] [--no-valuation] [--no-aggregate] [--valuationCcy <ccy>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 按货币过滤（逗号分隔）。仅应用于交易 + 资金查询。 |
| `--accounts` | 否 | `trading,funding` | 要查询的逗号分隔账户 |
| `--no-valuation` | 否 | - | 跳过跨账户估值（默认：包含估值） |
| `--no-aggregate` | 否 | - | 强制直接并行路径而不是服务器聚合。当您需要按账户的估值明细，或非美元 `--valuationCcy` 时使用（聚合路径以美元为单位的估值）。 |
| `--valuationCcy` | 否 | `USDT` | 估值货币 |

此命令首先调用服务器端聚合端点，当它不可用时会自动回退到直接并行查询；无论哪种方式，输出合同都相同。

返回 `{ trading, funding, valuation, meta }`。每个部分都有 `available: boolean`：
- `trading`: `totalEq`, `adjEq`, `details[]`（按货币）
- `funding`: `details[]`（按货币 `ccy`, `bal`, `availBal`, `frozenBal`)
- `valuation`: `valuationCcy`, `totalBal`, `details[]`（按账户明细仅在并行路径上填充；使用 `--no-aggregate` 强制它）
- `meta`: `requestedAt`（ISO 8601），`elapsedMs`, `partialFailure`, `source` (`aggregate` 或 `fallback`), `site`

当 `--json` 未设置时：如果 `meta.partialFailure=true`，则打印 `[PARTIAL]` 标记，然后是三个部分（交易 / 资金 / 估值），然后是 `[source: ...]` 脚本显示提供数据的路径。失败的节显示 `[ERROR: <msg>]`。

---

### 账户余额 — 交易账户

```bash
okx account balance [ccy] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 过滤到单一货币（例如，`USDT`） |

返回表格：`currency`, `equity`, `available`, `frozen`。仅显示余额 > 0 的货币。

---

### 资产余额 — 资金账户

```bash
okx account asset-balance [ccy] [--valuation] [--valuationCcy <ccy>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 过滤到特定货币（例如，`USDT`）；不影响估值货币 |
| `--valuation` | 否 | false | 还显示跨所有账户类型（交易/资金/收益）的总资产估值 |
| `--valuationCcy` | 否 | `USDT` | 用于表示总资产估值的货币（例如，`USDT`，`BTC`）。仅在 `--valuation` 设置时使用。 |

返回：`ccy`, `bal`, `availBal`, `frozenBal`。仅显示余额 > 0 的货币。

使用 `--valuation`：额外打印估值摘要表格，包含 `totalBal` 和按账户类型（`classic`/`earn`/`funding`/`trading`）的明细。数字以 `--valuationCcy` 为单位（默认 `USDT`）。

**重要**：`ccy`（余额过滤器）和 `--valuationCcy`（估值货币）是独立的参数——`ccy=BTC` 过滤余额列表到 BTC 行，但**不会**改变估值货币；明确设置 `--valuationCcy BTC` 以获得以 BTC 为单位的总计。

---

### 持仓 — 未平仓持仓

```bash
okx account positions [--instType <类型>] [--instId <id>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--instType` | 否 | - | 过滤：`SWAP`，`FUTURES`，`OPTION` |
| `--instId` | 否 | - | 过滤到特定工具 |

返回：`instId`，`instType`，`side`（posSide），`pos`，`avgPx`，`upl`（未实现盈亏），`lever`。仅显示大小 ≠ 0 的持仓。

---

### 持仓历史 — 已关闭持仓

```bash
okx account positions-history [--instType <类型>] [--instId <id>] [--limit <n>] [--json]
```

返回：`instId`，`direction`，`openAvgPx`，`closeAvgPx`，`realizedPnl`，`uTime`。

---

### 账单 — 账户总账

```bash
okx account bills [--archive] [--instType <类型>] [--ccy <ccy>] [--limit <n>] [--json]
```

| 参数 | 是否必需 | 默认值 | 描述 |
|---|---|---|---|
| `--archive` | 否 | false | 访问旧记录（存档端点） |
| `--instType` | 否 | - | 按合约类型筛选 |
| `--ccy` | 否 | - | 按货币筛选 |
| `--limit` | 否 | 100 | 记录数量 |

返回：`billId`，`instId`，`type`，`ccy`，`balChg`，`bal`，`ts`。

---

### 手续费 — 交易费率等级

```bash
okx account fees --instType <类型> [--instId <id>] [--json]
```

| 参数 | 是否必需 | 默认值 | 描述 |
|---|---|---|---|
| `--instType` | 是 | - | `SPOT`，`SWAP`，`FUTURES`，`OPTION` |
| `--instId` | 否 | - | 特定合约（可选） |

返回：`level`，`maker`，`taker`，`makerU`，`takerU`，`ts`。

---

### 配置 — 账户配置

```bash
okx account config [--json]
```

返回：`uid`，`acctLv`（账户等级），`posMode`（net/long_short_mode），`autoLoan`，`greeksType`，`level`，`levelTmp`。

---

### 最大尺寸 — 最大订单尺寸

```bash
okx account max-size --instId <id> --tdMode <模式> [--px <价格>] [--json]
```

| 参数 | 是否必需 | 默认值 | 描述 |
|---|---|---|---|
| `--instId` | 是 | - | 合约 ID |
| `--tdMode` | 是 | - | `cash`（现货），`cross` 或 `isolated` |
| `--px` | 否 | - | 参考价格（省略时使用标记价格） |

返回：`instId`，`maxBuy`，`maxSell`。

---

### 最大可用尺寸

```bash
okx account max-avail-size --instId <id> --tdMode <模式> [--json]
```

返回：`instId`，`availBuy`，`availSell` — 下一个订单的立即可用尺寸。

---

### 最大提款

```bash
okx account max-withdrawal [ccy] [--json]
```

返回表格：`ccy`，`maxWd`，`maxWdEx`（含借入）。无筛选时显示所有货币。

---

### 设置持仓模式

```bash
okx account set-position-mode <net|long_short_mode> [--json]
```

| 值 | 行为 |
|---|---|
| `net` | 单向（默认）— 多空净出 |
| `long_short_mode` | 对冲模式 — 多空可共存 |

> **警告**：持仓开启时切换模式可能导致意外行为。先检查 `okx account positions`。

---

### 转账资金

```bash
okx account transfer --ccy <ccy> --amt <n> --from <acctType> --to <acctType> \
  [--transferType <类型>] [--subAcct <名称>] [--json]
```

| 参数 | 是否必需 | 默认值 | 描述 |
|---|---|---|---|
| `--ccy` | 是 | - | 转账货币（例如，`USDT`） |
| `--amt` | 是 | - | 转账金额 |
| `--from` | 是 | - | 源账户类型：`6`=资金，`18`=交易 |
| `--to` | 是 | - | 目标账户类型：`6`=资金，`18`=交易 |
| `--transferType` | 否 | `0` | `0`=账户内，`1`=转子账户，`2`=从子账户 |
| `--subAcct` | 否 | - | 子账户名称（子账户转账时必需） |

返回：`transId`，`ccy`，`amt`。

---

## MCP 工具参考

| 工具 | 描述 |
|---|---|
| `account_get_balance_all` | 一次性快照（交易+资金(+估值)），由服务器端聚合端点提供，自动回退到并行查询。使用 `showValuation=true`（默认）包含跨账户总额；`valuationCcy='USDT'` 默认。设置 `preferParallel=true` 强制并行路径（按账户估值明细 / 非美元估值）。优先于单独调用 `account_get_balance` + `account_get_asset_balance`。 |
| `account_get_balance` | 交易账户余额 |
| `account_get_asset_balance` | 资金账户余额。使用 `showValuation=true` 包含跨账户总资产估值。使用 `valuationCcy`（默认 `"USDT" `）设置估值总额的计价货币 — 例如 `valuationCcy="BTC"` 返回 BTC 总额。 |
| `account_get_positions` | 开仓持仓 |
| `account_get_positions_history` | 已关闭持仓历史 |
| `account_get_bills` | 账户账单（近期） |
| `account_get_bills_archive` | 账户账单（存档） |
| `account_get_trade_fee` | 交易费率等级 |
| `account_get_config` | 账户配置 |
| `account_get_max_size` | 最大订单尺寸 |
| `account_get_max_avail_size` | 最大可用尺寸 |
| `account_get_max_withdrawal` | 最大可提款金额 |
| `account_set_position_mode` | 设置持仓模式 |
| `account_transfer` | 账户间转账 |

---

## 输入 / 输出示例

**"我有多少 USDT？"**
```bash
okx account balance USDT
# → currency: USDT | equity: 5000.00 | available: 4500.00 | frozen: 500.00
```

**"显示我所有持仓"**
```bash
okx account positions
# → table: instId, instType, side, pos, avgPx, upl, lever
```

**"我的交易历史和已实现盈亏是什么？"**
```bash
okx account positions-history
# → table: instId, direction, openAvgPx, closeAvgPx, realizedPnl, uTime
```

**"显示我的近期账户活动"**
```bash
okx account bills --limit 20
# → table: billId, instId, type, ccy, balChg, bal, ts
```

**"我的 SWAP 交易费是多少？"**
```bash
okx account fees --instType SWAP
# → level: VIP1 | maker: -0.0001 | taker: 0.0005
```

**"我能在交叉保证金中购买多少 BTC？"**
```bash
okx account max-size --instId BTC-USDT-SWAP --tdMode cross
# → instId: BTC-USDT-SWAP | maxBuy: 12.5 | maxSell: 12.5
```

**"从资金账户转账 200 USDT 到交易账户"**
```bash
okx account transfer --ccy USDT --amt 200 --from 6 --to 18
# → Transfer: TXN123456 (USDT 200)
```

**"检查我的账户配置"**
```bash
okx account config
# → uid: 123456789 | acctLv: 2 | posMode: net | autoLoan: false
```

## 资金存放位置

OKX 将资产分散到多个子账户。`--valuation` 分解直接映射：

| 账户类型 | `details` 键 | 用于 | 查询 |
|---|---|---|---|
| 交易（统一） | `trading` | 现货、保证金、互换、期货、期权 | `okx account balance` 或 `details.trading` 在 `--valuation` |
| 资金 | `funding` | 存入/取出、闲置资金 | `okx account asset-balance` 或 `details.funding` 在 `--valuation` |
| 收益 | `earn` | 简易收益、质押、储蓄 | `details.earn` 在 `--valuation` |
| 经典 | `classic` | 经典账户（遗留，较少见） | `details.classic` 在 `--valuation` |

**用户说 "我有 X USDT 但不能交易" 时的典型流程：**
1. `okx account asset-balance --valuation` → 查看每个 `details.*` 字段
2. 如果 `details.funding` 较大且 `details.trading` 较小 → 资金在资金账户
3. 转账：`okx account transfer --ccy USDT --amt <n> --from 6 --to 18`
4. 确认：`okx account balance USDT` → 股本应反映转账金额

## 边缘情况

- **未显示余额**：余额过滤为 > 0 — 如果无显示，所有货币余额为 0
- **positions 命令返回空**：无开仓合约；现货持仓不在此显示（使用 `account balance`）
- **bills --archive**：需用于 7 天以上交易（默认窗口）；可能较慢
- **set-position-mode**：若同一合约既有多空持仓，不能切换到 `net`
- **transfer --from/--to 代码**：`6`=资金账户，`18`=交易账户；其他值用于子账户流程
- **max-size vs max-avail-size**：`max-size` 是理论最大值；`max-avail-size` 考虑现有订单和预留保证金
- **Demo 模式**：`okx --demo account balance`（OAuth）或 `okx --profile <demo-profile> account balance`（API Key）显示模拟余额，非真实资金

## 全局说明

- 所有写命令需有效凭证（OAuth 会话或 `~/.okx/config.toml` 中的 API Key）
- 认证方法和交易模式在 "凭证 & 配置检查" 中确定；参见该部分参数规则
- 每个命令结果包含 `[mode: live]` 或 `[mode: demo]` 标签供审计参考
- `--json` 默认返回 OKX API v5 原始响应。添加 `--env` 将输出包装为 `{"env": "<live|demo>", "profile": "<name>", "data": <response>}`
- 速率限制：账户端点每 2 秒 10 个请求
- 显示的持仓为统一交易账户；资金账户资产是独立的
- 账户类型：`6`=资金账户（存入/取出），`18`=统一交易账户（现货+衍生品）
