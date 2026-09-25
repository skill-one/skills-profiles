# OKX CEX 组合与账户 CLI

OKX 交易所的账户余额、持仓、盈亏、账单、费用和资金转账。**需要 API 凭证。**

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置部分的 `metadata.version` 作为步骤 2 的参考。

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
   okx --demo account balance
   ```

> **安全**：切勿在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

## 凭证与配置文件检查

**在任何经过身份验证的命令之前运行此检查。** 身份验证方法在 [预检查](../_shared/preflight.md) 第 2 步期间检测到，并在会话中记住。

### 步骤 A — 验证凭证

检查**两个**来源（参见 [预检查步骤 2](../_shared/preflight.md#step-2--detect-auth-method-once-per-session) 的决策表）。`okx auth status --json` 单独是不够的——其 `apiKey` 字段始终为 `false`，并且**不反映** TOML 配置。

```bash
okx config show --json      # API 密钥存在的权威来源
okx auth status --json      # OAuth 会话状态的权威来源
```

按顺序分支——第一个匹配的获胜：

- `config show` 具有任何具有非空 `api_key` 的配置文件——**API 密钥模式**。继续步骤 B。
- 没有 API 密钥配置文件**并且** `auth status` 返回 `"status": "logged_in"` — **OAuth 模式**。继续步骤 B。
- 没有 API 密钥配置文件**并且** `auth status` 返回 `"status": "pending"` — 登录正在进行中，请等待。
- 没有 API 密钥配置文件**并且** `auth status` 返回 `"status": "not_logged_in"` — **停止所有操作**，加载 `okx-cex-auth` 技能并按照登录步骤操作，等待完成。

### 步骤 B — 确认交易模式

**解析规则：**
1. 当前消息意图明确（例如 "实盘" / "实盘" / "实盘" → 实盘；"测试" / "模拟" / "演示" → 演示）→ 使用它并通知用户
2. 当前消息没有明确的声明 → 检查对话上下文以查找先前的选择：
   - 找到 → 重用它，通知用户
   - 未找到 → 询问：`"实盘 (实盘) 或 演示 (模拟盘)?"` — 等待答案后再继续

**应用模式的方式取决于身份验证方法（在步骤 A 中检测到）：**

| 身份验证方法 | 实盘 (实盘) | 演示 (模拟盘) |
|---|---|---|
| **API 密钥** | `--profile <实盘配置文件>` | `--profile <演示配置文件>` |
| **OAuth** | *(不需要标志，实盘是默认值)* | `--demo` |

- **API 密钥用户**：运行 `okx config show --json` 以发现可用的配置文件名称及其 `demo` 设置。使用 `--profile <名称>` 选择正确的配置文件。
- **OAuth 用户**：省略标志进行实盘交易；添加 `--demo` 进行模拟交易。**不要**使用 `--profile` 切换模式。

### 处理身份验证错误

**身份验证错误**（错误包含 "401"、"会话过期" 或 "首先运行 `okx auth login`"）：
1. **立即停止**——不要重试相同的命令
2. 通知用户："身份验证失败。您的会话可能已过期。"
3. 加载 `okx-cex-auth` 技能并按照重新身份验证步骤操作
4. 成功重新身份验证后，重试原始命令

## 演示模式与实盘模式

| 模式 | 资金 | API 密钥参数 | OAuth 参数 |
|---|---|---|---|
| 实盘 (实盘) | 实际资金 | `--profile <实盘配置文件>` | *(默认，不需要标志)* |
| 演示 (模拟盘) | 模拟资金 | `--profile <演示配置文件>` | `--demo` |

```bash
# API 密钥用户
okx --profile okx-prod  account balance     # 实盘
okx --profile okx-demo  account balance     # 演示

# OAuth 用户
okx account balance                          # 实盘 (默认)
okx --demo account balance                   # 演示
```

**规则：**
- **读取命令**（余额、持仓、账单等）：始终说明使用了哪种模式
- **写入命令**（`transfer`、`set-position-mode`）：**执行前必须确认模式**（参见 "凭证与配置文件检查" 步骤 B）；转账尤其如此——错误模式意味着错误的账户
- 每个命令后的响应必须附加：`[模式：实盘]` 或 `[模式：演示]`

## 技能路由

- 对于市场数据（价格、图表、深度、资金利率）→ 使用 `okx-cex-market`
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

# 所有开放的持仓，每个产品
okx account positions

# 仅一个产品的持仓——当用户命名产品时始终缩小范围
okx account positions --instType SWAP     # SWAP | FUTURES | OPTION | MARGIN | EVENTS

# 已关闭的持仓历史记录（带实现盈亏）
okx account positions-history

# 最近账户账单（最后 100）
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
| 1 | `okx account balance-all [ccy]` | 读取 | 一次性快照：一次调用中包含交易 + 资金 (+ 估值) |
| 2 | `okx account balance [ccy]` | 读取 | 交易账户净值、可用、冻结 |
| 3a | `okx account asset-balance [ccy]` | 读取 | 资金账户余额（按货币列表） |
| 3b | `okx account asset-balance [ccy] --valuation [--valuationCcy <ccy>]` | 读取 | 相同 + 跨账户估值（交易/资金/收益）；默认货币为 USDT，使用 `--valuationCcy BTC` 覆盖 |
| 4 | `okx account positions [--instType <type>] [--instId <id>]` | 读取 | 开放合约/掉期持仓。**当用户命名产品**（"我的掉期持仓"、"期货持仓"、"期权持仓"），传递 `--instType <type>` (`SWAP` \| `FUTURES` \| `OPTION` \| `MARGIN` \| `EVENTS`）——或者使用该产品自己的命令（`okx swap positions`，`okx futures positions`，`okx option positions`）。只有当用户确实想要所有内容时才省略过滤器：未过滤的列表更大，并且将产品过滤留给模型，这是错误发生的地方 |
| 5 | `okx account positions-history` | 读取 | 已关闭的持仓 + 实现盈亏 |
| 6 | `okx account bills` | 读取 | 账户总账（存款、取款、交易） |
| 7 | `okx account fees --instType <type>` | 读取 | 我的交易费用等级（做市商/吃进） |
| 8 | `okx account config` | 读取 | 账户级别、持仓模式、UID |
| 9 | `okx account max-size --instId <id> --tdMode <mode>` | 读取 | 当前价格下的最大买入/卖出量 |
| 10 | `okx account max-avail-size --instId <id> --tdMode <mode>` | 读取 | 下一个订单的可用量 |
| 11 | `okx account max-withdrawal [ccy]` | 读取 | 每种货币的最大可提款金额 |

### 写入命令

| # | 命令 | 类型 | 描述 |
|---|---|---|---|
| 12 | `okx account set-position-mode <mode>` | 写入 | 切换净额/对冲持仓模式 |
| 13 | `okx account transfer` | 写入 | 在账户之间转账资金 |

## 跨技能工作流

### 交易前余额检查
> 用户："我想买入 0.1 BTC — 我有足够的 USDT 吗？"

```
1. okx-cex-portfolio okx account balance-all                 → 一次性交易 + 资金 + 估值快照
   → 检查交易详情（交易账户中可用）
   → 如果交易余额 < 需要的：检查资金详情——可能需要转账
2. okx-cex-market    okx market ticker BTC-USDT              → 检查当前价格
        ↓ 用户批准
3. okx-cex-trade     okx spot place --instId BTC-USDT --side buy --ordType market --sz 0.1
```

### 机器人交易前余额检查
> 用户："我想启动一个使用 1000 USDT 的 BTC 网格机器人"

```
1. okx-cex-portfolio okx account balance-all                 → 一次性交易 + 资金 + 估值快照
   → 检查交易详情 ≥ 1000（网格机器人必须的资金在交易账户中）
   → 如果资金详情中有 USDT 而不是：首先使用账户转账
2. okx-cex-market    okx market candles BTC-USDT --bar 4H --limit 50  → 确定价格范围
        ↓ 用户批准
3. okx-cex-bot       okx bot grid create --instId BTC-USDT --algoOrdType grid \
                       --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000
```

### 净值快速查看
> 用户："我的总资产是多少?" / "总资产多少?"

```
1. okx-cex-portfolio okx account balance-all                 → 返回 {交易, 资金, 估值, 元数据}
   → 估值.totalBal = USDT 中的总净值
   → 交易.totalEq = 交易账户净值
   → 资金详情 = 每种货币的资金余额
   → 元数据.partialFailure = 如果任何部分失败（仍然返回可用数据）
```

### 查看开放持仓和盈亏
> 用户："显示我的当前持仓以及它们的性能"

```
1. okx-cex-portfolio okx account positions                  → 开放持仓带 UPL
2. okx-cex-portfolio okx account positions-history          → 最近关闭的持仓
3. okx-cex-market    okx market ticker BTC-USDT-SWAP        → 检查当前价格与入场价格
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

**每个命令结果后：** 在响应中附加 `[模式：实盘]` 或 `[模式：演示]` 标签以供审计参考

### 步骤 1：识别账户操作

- 一次性检查所有余额 → `okx account balance-all`（一次调用中包含交易 + 资金 + 估值；推荐用于 "总资产 / 净值 / 所有余额")
- 检查余额 → `okx account balance`（交易净值仅）或 `okx account asset-balance`（资金余额）或 `okx account asset-balance --valuation`（所有账户在 USDT 中的总估值）
- 查看开放持仓 → `okx account positions`
- 查看已关闭的持仓 + 盈亏 → `okx account positions-history`
- 查看交易历史 → `okx account bills`
- 检查费用等级 → `okx account fees`
- 检查账户设置 → `okx account config`
- 计算订单大小 → `okx account max-size` 或 `okx account max-avail-size`
- 检查提款限额 → `okx account max-withdrawal`
- 转账资金 → `okx account transfer`
- 更改持仓模式 → `okx account set-position-mode`

### 步骤 2：立即运行读取命令——确认配置文件（步骤 0）然后写入

**读取命令**（1–10）：立即运行，无需确认。

- `ccy` 过滤器：使用货币符号，如 `USDT`，`BTC`，`ETH`
- `--instType` 用于费用/持仓：`SPOT`，`SWAP`，`FUTURES`，`OPTION`
- `--archive` 用于账单：访问默认窗口之外的旧记录
- `--tdMode` 用于 max-size：`cash`（现货），`cross` 或 `isolated`

**写入命令**（11–12）：执行前确认一次。

- `set-position-mode`：确认模式 (`net` = 单向——多头和空头相抵消）
- `transfer`：确认 `--ccy`，`--amt`，`--from`，`--to`（账户类型：`6`=资金账户，`18`=交易账户）；首先验证源余额

### 写入后验证

- `set-position-mode` 后：运行 `okx account config` 以确认 `posMode` 已更新
- `transfer` 后：运行 `okx account balance` 和 `okx account asset-balance` 以确认余额已更新

## CLI 命令参考

### 余额所有 — 一次性聚合快照

```bash
okx account balance-all [ccy] [--accounts trading,funding] [--no-valuation] [--no-aggregate] [--valuationCcy <ccy>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 按货币过滤（逗号分隔）。仅应用于交易 + 资金查询。 |
| `--accounts` | 否 | `trading,funding` | 要查询的逗号分隔账户 |
| `--no-valuation` | 否 | - | 跳过跨账户估值（默认：包含估值） |
| `--no-aggregate` | 否 | - | 强制直接并行路径而不是服务器聚合。当你需要每个账户的估值分解，或者非美元 `--valuationCcy`（聚合路径以美元为单位的估值）时使用。 |
| `--valuationCcy` | 否 | `USDT` | 估值货币 |

此命令首先调用服务器端聚合端点，当它不可用时自动回退到并行查询；输出合同是相同的。

返回 `{ trading, funding, valuation, meta }`。每个部分都有 `available: boolean`：
- `trading`: `totalEq`, `adjEq`, `details[]`（按货币）
- `funding`: `details[]`（按货币 `ccy`, `bal`, `availBal`, `frozenBal`)
- `valuation`: `valuationCcy`, `totalBal`, `details[]`（按账户分解仅在并行路径上填充；使用 `--no-aggregate` 强制它）
- `meta`: `requestedAt` (ISO 8601), `elapsedMs`, `partialFailure`, `source` (`aggregate` 或 `fallback`), `site`

当 `--json` 未设置时：如果 `meta.partialFailure=true` 打印 `[PARTIAL]` 标记，然后是三个部分（交易 / 资金 / 估值），然后是 `[source: ...]` 脚本显示提供数据的路径。失败的节显示 `[ERROR: <msg>]`。

---

### 余额账户 — 交易账户

```bash
okx account balance [ccy] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 过滤到单一货币（例如，`USDT`） |

返回表格：`currency`, `equity`, `available`, `frozen`. 仅显示余额 > 0 的货币。

---

### 资产余额 — 资金账户

```bash
okx account asset-balance [ccy] [--valuation] [--valuationCcy <ccy>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `ccy` | 否 | - | 过滤到特定货币（例如，`USDT`）；不 affect 估值货币 |
| `--valuation` | 否 | false | 还显示跨所有账户类型（交易/资金/收益）的总资产估值 |
| `--valuationCcy` | 否 | `USDT` | 用于表示总资产估值的货币（例如，`USDT`，`BTC`）。仅在 `--valuation` 设置时使用。 |

返回：`ccy`, `bal`, `availBal`, `frozenBal`. 仅显示余额 > 0 的货币。

使用 `--valuation`：额外打印估值摘要表格，包含 `totalBal` 和按账户类型分解（`classic`/`earn`/`funding`/`trading`）。数字以 `--valuationCcy`（默认 `USDT`）表示。

**重要**：`ccy`（余额过滤器）和 `--valuationCcy`（估值货币）是独立参数——`ccy=BTC` 过滤余额列表到 BTC 行，但**不改变**估值货币；明确设置 `--valuationCcy BTC` 以获得以 BTC 为单位的估值总计。

---

### 持仓 — 开放持仓

```bash
okx account positions [--instType <type>] [--instId <id>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--instType` | 否 | - | 过滤：`SWAP`, `FUTURES`, `OPTION` |
| `--instId` | 否 | - | 过滤到特定工具 |

返回：`instId`, `instType`, `side` (posSide), `pos`, `avgPx`, `upl` (未实现盈亏), `lever`. 仅显示大小 ≠ 0 的持仓。

---

### 持仓历史 — 已关闭的持仓

```bash
okx account positions-history [--instType <type>] [--instId <id>] [--limit <n>] [--json]
```

返回：`instId`, `direction`, `openAvgPx`, `closeAvgPx`, `realizedPnl`, `uTime`.

---

### 账单 — 账户总账

```bash
okx account bills [--archive] [--instType <type>] [--ccy <ccy>] [--limit <n>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--archive` | 否 | false | 访问默认窗口之外的旧记录（存档端点） |
| `--instType` | 否 | - | 按工具类型过滤 |
| `--ccy` | 否 | - | 按货币过滤 |
| `--limit` | 否 | 100 | 记录数 |

返回：`billId`, `instId`, `type`, `ccy`, `balChg`, `bal`, `ts`.

---

### 费用 — 交易费用等级

```bash
okx account fees --instType <type> [--instId <id>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--instType` | 是 | - | `SPOT`, `SWAP`, `FUTURES`, `OPTION` |
| `--instId` | 否 | - | 特定工具（可选） |

返回：`level`, `maker`, `taker`, `makerU`, `takerU`, `ts`.

---

### 配置 — 账户配置

```bash
okx account config [--json]
```

返回：`uid`, `acctLv` (账户级别), `posMode` (net/long_short_mode), `autoLoan`, `greeksType`, `level`, `levelTmp`.

---

### 最大大小 — 最大订单大小

```bash
okx account max-size --instId <id> --tdMode <mode> [--px <price>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--instId` | 是 | - | 工具 ID |
| `--tdMode` | 是 | - | `cash` (现货), `cross`, 或 `isolated` |
| `--px` | 否 | - | 参考价格（省略时使用市价） |

返回：`instId`, `maxBuy`, `maxSell`.

---

### 最大可用大小

```bash
okx account max-avail-size --instId <id> --tdMode <mode> [--json]
```

返回：`instId`, `availBuy`, `availSell` — 下一个订单的立即可用量。

---

### 最大提款

```bash
okx account max-withdrawal [ccy] [--json]
```

返回表格：`ccy`, `maxWd`, `maxWdEx`（使用借入）。如果没有过滤器，显示所有货币。

---

### 设置持仓模式

```bash
okx account set-position-mode <net|long_short_mode> [--json]
```

| 值 | 行为 |
|---|---|
| `net` | 单向（默认）——多头和空头相抵消 |
| `long_short_mode` | 对冲模式——多头和空头可以共存 |

> **警告**：当持仓开放时切换模式可能会导致意外行为。首先检查 `okx account positions`。

---

### 转账资金

```bash
okx account transfer --ccy <ccy> --amt <n> --from <acctType> --to <acctType> \
  [--transferType <type>] [--subAcct <name>] [--json]
```

| 参数 | 必需 | 默认 | 描述 |
|---|---|---|---|
| `--ccy` | 是 | - | 要转账的货币（例如，`USDT`） |
| `--amt` | 是 | - | 转账金额 |
| `--from` | 是 | - | 源账户类型: `6`=资金账户, `18`=交易账户 |
| `--to` | 是 | - | 目标账户类型: `6`=资金账户, `18`=交易账户 |
| `--transferType` | 否 | `0` | `0`=账户内转账, `1`=转账到子账户, `2`=从子账户转账 |
| `--subAcct` | 否 | - | 子账户名称（子账户转账时必需） |

返回：`transId`, `ccy`, `amt`.

---

## MCP 工具参考

| 工具 | 描述 |
|---|---|
| `account_get_balance_all` | 交易 + 资金 + 估值的一次性快照，由服务器端聚合端点提供，自动回退到并行查询。使用 `showValuation=true`（默认）包含跨账户总计；`valuationCcy='USDT'` 默认。强制使用并行路径（每个账户的估值分解 / 非美元估值）。优先于单独调用 `account_get_balance` + `account_get_asset_balance`。
| `account_get_balance` | 交易账户余额 |
| `account_get_asset_balance` | 资金账户余额。使用 `showValuation=true` 包含交易/资金/收益账户的总估值。使用 `valuationCcy`（默认 `"USDT"`) 设置估值总计的货币——例如 `valuationCcy="BTC"` 返回 BTC 中的总计。
| `account_get_positions` | 开放持仓 |
| `account_get_positions_history` | 已关闭的持仓历史记录 |
| `account_get_bills` | 账户账单（最近） |
| `account_get_bills_archive` | 账户账单（存档） |
| `account_get_trade_fee` | 交易费用等级 |
| `account_get_config` | 账户配置 |
| `account_get_max_size` | 最大订单大小 |
| `account_get_max_avail_size` | 最大可用大小 |
| `account_get_max_withdrawal` | 最大可提款 |
| `account_set_position_mode` | 设置持仓模式 |
| `account_transfer` | 账户之间转账 |
