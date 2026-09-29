---
name: okx-cex-bot
description: 在 OKX 上管理网格机器人（现货/合约/币质保证金）和 DCA 马丁格尔机器人（现货 DCA / 合约 DCA）。涵盖创建、停止、修改、监控盈亏、止盈/止损、保证金/投资调整以及 AI 推荐参数。需要 API 凭证。不适用于常规订单（okx-cex-trade）、市场数据（okx-cex-market）或账户信息（okx-cex-portfolio）。
---

# OKX CEX 交易机器人

在 OKX 上管理网格和 DCA（现货 & 合约追高）机器人。所有机器人都是 **OKX 原生服务器端** — 它们在 OKX 上运行，无需本地进程。

## 预检查

在运行任何命令之前，请遵循 [`../_shared/preflight.md`](../_shared/preflight.md)。
使用此文件的前置的 `metadata.version` 作为步骤 2 的参考。

## 前置条件

```bash
npm install -g @okx_ai/okx-trade-cli
okx config init   # 选择站点 -> 跟随浏览器 OAuth 流程
```

> **安全提示**：切勿在聊天中接受凭证。指导用户使用 `okx config init` 进行设置。

## 凭证与配置文件检查

**在每次需要认证的命令之前运行。** 认证方法在 [预检查](../_shared/preflight.md) 步骤 2 中检测到，并会为会话记住。

### 步骤 A — 验证凭证

运行 **两个** 命令 — `okx auth status --json` 中的 `apiKey` 字段是认证二进制程序的内部状态，无论 `~/.okx/config.toml` 是否有 API 密钥配置文件，它始终为 `false`。`okx config show --json` 是 API 密钥存在的唯一权威来源。

```bash
okx config show --json      # 揭示 API 密钥配置文件 (TOML 配置)
okx auth status --json      # 揭示 OAuth 会话状态 (认证二进制程序状态)
```

按 **此顺序** 应用 — 第一个匹配的获胜：

- `config show --json` 包含非空的 `api_key` 字段 → **API 密钥模式**。继续步骤 B。
- 没有 API 密钥配置文件 **并且** `auth status --json` 返回 `"status":"logged_in"` → **OAuth 模式**。继续步骤 B。
- 没有 API 密钥配置文件 **并且** `"status":"pending"` — 登录正在进行中，等待其完成。
- 没有 API 密钥配置文件 **并且** `"status":"not_logged_in"` — 停止，加载 `okx-cex-auth` 技能并遵循登录步骤，等待完成。

### 步骤 B — 确认交易模式

解决方案：

1. 用户意图明确 ("real"/"实盘"/"live" → live; "test"/"模拟"/"demo" → demo) → 使用它，通知用户
2. 没有明确的声明 → 检查对话上下文以查找先前的选择 → 如果找到则重用
3. 什么都没找到 → 询问："实盘 (实盘) 或 模拟盘 (模拟盘)?" — 等待后再继续

**如何应用模式取决于认证方法（在步骤 A 中检测到）：**

| 认证方法 | 实盘 (实盘) | 模拟盘 (模拟盘) |
|---|---|---|
| **API 密钥** | `--profile <live-profile>` | `--profile <demo-profile>` |
| **OAuth** | *(无需标志，实盘是默认值)* | `--demo` |

- **API 密钥用户**：运行 `okx config show --json` 以发现可用的配置文件名称及其 `demo` 设置。
- **OAuth 用户**：为实盘省略标志；为模拟交易添加 `--demo`。

**在每次命令之后**：附加 `[mode: live]` 或 `[mode: demo]`

### 处理 401 错误

**认证错误**（错误包含 "401"、"会话过期" 或 "首先运行 `okx auth login`"）：
1. 立即停止
2. 加载 `okx-cex-auth` 技能并遵循重新认证步骤
3. 重试原始命令

## 技能路由

| 需求 | 技能 |
|---|---|
| 市场数据、价格、深度 | `okx-cex-market` |
| 账户余额、头寸、费用 | `okx-cex-portfolio` |
| 常规现货/掉期/期货订单 | `okx-cex-trade` |
| **网格 / DCA 机器人** | **`okx-cex-bot`（此技能）** |

## 命令索引

### 网格机器人

| 命令 | 类型 | 描述 |
|---|---|---|
| `okx bot grid create` | 写入 | 创建网格机器人（现货或合约） |
| `okx bot grid amend` | 写入 | 修改运行中的网格机器人的价格范围、网格数量或 TP/SL |
| `okx bot grid stop` | 写入 | 停止网格机器人 |
| `okx bot grid positions` | 读取 | 查询开放的合约网格头寸（平仓价格、保证金比率、未实现盈亏） |
| `okx bot grid liquidate-price` | 读取 | 估计合约网格机器人的平仓价格 |
| `okx bot grid close-position` | 写入 | 机器人停止后（stopType=2）关闭剩余头寸 |
| `okx bot grid orders` | 读取 | 列出活动或历史网格机器人 |
| `okx bot grid details` | 读取 | 网格机器人详情 + 盈亏 |
| `okx bot grid sub-orders` | 读取 | 单个网格成交或挂起订单 |

### DCA 机器人（现货 & 合约）

| 命令 | 类型 | 描述 |
|---|---|---|
| `okx bot dca create` | 写入 | 创建 DCA（追高）机器人（现货或合约） |
| `okx bot dca stop` | 写入 | 停止 DCA 机器人（现货或合约） |
| `okx bot dca orders` | 读取 | 列出活动或历史 DCA 机器人（默认：contract_dca） |
| `okx bot dca details` | 读取 | DCA 机器人详情 + 盈亏 |
| `okx bot dca sub-orders` | 读取 | DCA 周期内的 DCA 订单 |

## 操作流程

### 步骤 1 — 确定机器人类型和操作

解析用户请求 → 确定模块（网格 / DCA）和操作（创建 / 停止 / 列表 / 详情）。

### 步骤 2 — 执行

**读取命令**（订单、详情、子订单）：在配置文件确认后立即运行。

**写入命令**（创建、修改、停止）：在执行前与用户确认关键参数。

### 步骤 3 — 写入后验证

- 创建后 → 运行相应的 `orders` 命令以确认活动
- 修改后 → 运行 `bot grid details` 以确认配置已更新
- 停止后 → 运行 `orders --history` 以确认已停止

## 关键规则

- **切勿自动转移资金。** 如果余额不足以创建机器人，请报告差额（当前可用 vs 需要），并询问用户如何操作： (1) 手动转移资金， (2) 减少规模，或 (3) 取消。
- **`algoId`** 是机器人的算法订单 ID（从创建或列表输出）。它 **不是** 普通的 `ordId`。切勿编造 — 始终从先前的命令中获取。
- **`algoOrdType`** 对于网格必须与机器人的实际类型匹配。始终使用 `bot grid orders` 中的值 — 不要仅凭用户描述进行推断。不匹配会导致错误 `50016`。
- 在操作现有机器人时，**始终首先列出** 以获取正确的 ID，除非用户提供它们。
- **TP/SL 限制**：`tpTriggerPx`/`tpRatio` 和 `slTriggerPx`/`slRatio` 是互斥的对。

## CLI 命令参考

### 网格机器人 — 创建

```bash
okx bot grid create --instId <id> --algoOrdType <type> \
  --maxPx <px> --minPx <px> --gridNum <n> \
  [--runType <1|2>] \
  [--quoteSz <n>] [--baseSz <n>] \
  [--direction <long|short|neutral>] [--lever <n>] [--sz <n>] \
  [--basePos] [--no-basePos] \
  [--tpTriggerPx <px>] [--slTriggerPx <px>] [--tpRatio <ratio>] [--slRatio <ratio>] \
  [--algoClOrdId <id>] [--json]
```

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `--instId` | 是 | - | 仪器（例如，`BTC-USDT` 用于现货，`BTC-USDT-SWAP` 用于 USDT-M 合约，`BTC-USD-SWAP` 用于币-M 合约） |
| `--algoOrdType` | 是 | - | `grid`（现货网格）或 `contract_grid`（合约网格，包括币保证金） |
| `--maxPx` | 是 | - | 上限价格 |
| `--minPx` | 是 | - | 下限价格 |
| `--gridNum` | 是 | - | 网格级别（2–100） |
| `--runType` | 否 | `1` | `1`=算术间隔，`2`=几何间隔 |
| `--quoteSz` | 条件 | - | USDT 投资 — 现货网格仅限（提供 `quoteSz` 或 `baseSz`） |
| `--baseSz` | 条件 | - | 基币投资 — 现货网格仅限 |
| `--direction` | 条件 | - | `long`、`short` 或 `neutral` — 合约网格所需 |
| `--lever` | 条件 | - | 杠杆（例如，`5`） — 合约网格仅限 |
| `--sz` | 条件 | - | USDT 中的投资保证金（USDT-M）或币（币-M） — 合约网格仅限 |
| `--basePos` / `--no-basePos` | 否 | `true` | 创建时开立基础头寸 — 合约网格仅限（中性忽略）。使用 `--no-basePos` 禁用 |
| `--tpTriggerPx` | 否 | - | 止盈触发价格（与 `--tpRatio` 互斥） |
| `--slTriggerPx` | 否 | - | 止损触发价格（与 `--slRatio` 互斥） |
| `--tpRatio` | 否 | - | 止盈比率 — 合约网格仅限（与 `--tpTriggerPx` 互斥） |
| `--slRatio` | 否 | - | 止损比率 — 合约网格仅限（与 `--slTriggerPx` 互斥） |
| `--algoClOrdId` | 否 | - | 客户定义的算法订单 ID（1-32 字母数字）。每个用户唯一，支持幂等创建 |

---

### 网格机器人 — 修改

```bash
okx bot grid amend --algoId <id> \
  [--maxPx <px> --minPx <px> --gridNum <n>] \
  [--instId <id>] \
  [--tpTriggerPx <px>] [--slTriggerPx <px>] \
  [--tpRatio <ratio>] [--slRatio <ratio>] \
  [--topUpAmt <n>] [--json]
```

支持两种模式，可以组合在一个调用中：

**价格范围模式** — 当提供 `--maxPx` 时触发：

| 参数 | 必填 | 描述 |
|---|---|---|
| `--algoId` | 是 | 网格机器人算法订单 ID |
| `--maxPx` | 是 | 新上限价格 |
| `--minPx` | 是 (with maxPx) | 新下限价格 |
| `--gridNum` | 是 (with maxPx) | 新网格数量（整数） |
| `--topUpAmt` | 否 | 额外保证金（合约网格仅限；省略以自动使用最低要求） |

**TP/SL 模式** — 当至少提供一个 TP/SL 参数时触发；`--instId` 也需要：

| 参数 | 必填 | 描述 |
|---|---|---|
| `--instId` | 是 | 仪器 ID（例如，`BTC-USDT`） |
| `--tpTriggerPx` | 否 | 止盈触发价格（绝对值）。传递 `-1` 以清除 |
| `--slTriggerPx` | 否 | 止损触发价格（绝对值）。传递 `-1` 以清除 |
| `--tpRatio` | 否 | 止盈比率（例如，`0.1` = 10%）。合约网格仅限。传递 `-1` 以清除 |
| `--slRatio` | 否 | 止损比率（例如，`0.1` = 10%）。合约网格仅限。传递 `-1` 以清除 |
| `--topUpAmt` | 否 | 额外保证金（合约网格仅限） |

> **注意**：`tpTriggerPx`/`tpRatio` 互斥。`slTriggerPx`/`slRatio` 同样互斥。

---

### 网格机器人 — 停止

```bash
okx bot grid stop --algoId <id> --algoOrdType <type> --instId <id> \
  [--stopType <1|2>] [--json]
```

> **`--algoId`** 和 **`--algoOrdType`** 必须来自 `bot grid orders` 输出。`algoOrdType` 必须与机器人的实际类型匹配 — 不要猜测。

**工作流程**：
1. 运行 `bot grid details --algoId <id> --algoOrdType <type>` 并检查 `state` 字段。
2. 如果 `state=running`：使用 `--stopType 1`（默认，干净退出）或 `--stopType 2` 停止（保留资产）。
3. 如果 `state=no_close_position`（用户之前使用 stopType=2 停止）：再次使用 `--stopType 1` 来关闭剩余的开放头寸。

| `--stopType` | 现货网格 | 合约网格 |
|---|---|---|
| `1` (默认) | 卖出所有基础资产 | 市场平仓所有开放头寸 |
| `2` | 保留基础资产不变 | 取消网格订单，保留头寸开放 |

---

### 网格机器人 — 头寸

```bash
okx bot grid positions --algoId <id> --algoOrdType contract_grid [--json]
```

返回开放的合约网格头寸：平仓价格 (`liqPx`)、保证金比率 (`mgnRatio`) 和未实现盈亏 (`upl`)。仅适用于 `contract_grid` 机器人。

---

### 网格机器人 — 平仓价格

```bash
okx bot grid liquidate-price --instId <id> --sz <margin> --lever <leverage> \
  --maxPx <px> --minPx <px> --gridNum <n> --direction <long|short|neutral> \
  [--runType <1|2>] [--triggerStrategy <instant|price|rsi|webhook>] [--json]
```

估计合约网格机器人的平仓价格。在创建机器人之前使用以评估平仓风险。估计需要 **完整的预期配置** — 后端需要 `instId`、`sz`、`lever`、网格范围（`maxPx`/`minPx`/`gridNum`）和 `direction`（中性机器人使用 `neutral`）；省略任何一项都会快速失败并显示缺少的内容。`runType` 默认为 `1`（算术；`2`=几何）和 `triggerStrategy` 是可选的。

---

### 网格机器人 — 关闭头寸

```bash
okx bot grid close-position --algoId <id> (--mktClose | --no-mktClose) [--sz <size>] [--px <price>] [--json]
```

关闭合约网格机器人（使用 `stopType='2'` 停止）的剩余开放头寸。关闭模式是 **必需的**（没有默认值，因为它移动资金）：传递 `--mktClose` 以进行市价平仓（立即），或 `--no-mktClose --sz <size> --px <price>` 以进行限价平仓订单。省略两者将被拒绝。

---

### 网格机器人 — 列出订单

```bash
okx bot grid orders --algoOrdType <type> [--instId <id>] [--algoId <id>] [--history] [--json]
```

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `--algoOrdType` | 是 | - | `grid`（现货）、`contract_grid`（合约）或 `moon_grid`（月亮） |
| `--instId` | 否 | - | 按仪器筛选 |
| `--algoId` | 否 | - | 按算法订单 ID 筛选。**不是** 普通交易订单 ID |
| `--history` | 否 | false | 显示已完成/停止的机器人，而不是活动的 |

---

### 网格机器人 — 详情

```bash
okx bot grid details --algoOrdType <type> --algoId <id> [--json]
```

返回：机器人配置、当前盈亏 (`pnlRatio`)、网格范围、网格数量、状态、头寸信息。

---

### 网格机器人 — 子订单

```bash
okx bot grid sub-orders --algoOrdType <type> --algoId <id> [--pending] [--groupId <id>] [--after <id>] [--before <id>] [--limit <n>] [--json]
```

| 标志 | 效果 |
|---|---|
| *(默认)* | 已成交子订单（执行的网格交易） |
| `--pending` | 当前在订单簿上的挂起网格订单。 (在模拟模式下工作。 `--live` 是已弃用的别名，不能与 `--demo` 结合使用。) |
| `--groupId` | 筛选到单个买入-卖出对（共享 groupId） |
| `--after` | 分页游标 — 比此 ID 更旧的记录 |
| `--before` | 分页游标 — 比此 ID 更新的记录 |
| `--limit` | 返回的最大记录数（默认 100） |

---

### DCA 机器人 — 创建（现货 & 合约）

```bash
okx bot dca create --algoOrdType <spot_dca|contract_dca> --instId <id> --direction <long|short> \
  --initOrdAmt <n> --maxSafetyOrds <n> --tpPct <ratio> \
  [--lever <n>] [--safetyOrdAmt <n>] [--pxSteps <ratio>] [--pxStepsMult <mult>] [--volMult <mult>] \
  [--slPct <ratio>] [--slMode <limit|market>] [--allowReinvest] \
  [--triggerStrategy <instant|price|rsi>] [--triggerPx <price>] \
  [--triggerCond <cross_up|cross_down>] [--thold <threshold>] [--timeframe <timeframe>] [--timePeriod <period>] \
  [--algoClOrdId <id>] [--reserveFunds <true|false>] [--tradeQuoteCcy <ccy>] [--json]
```

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `--algoOrdType` | 是 | - | `spot_dca`（现货 DCA）或 `contract_dca`（合约 DCA） |
| `--instId` | 是 | - | 仪器（例如，`BTC-USDT` 用于现货，`BTC-USDT-SWAP` 用于合约） |
| `--lever` | 条件 | - | 杠杆乘数（例如，`3`）。`contract_dca` 所需 |
| `--direction` | 是 | - | `long` 或 `short`。`spot_dca` 必须为 `long` |
| `--initOrdAmt` | 是 | - | 初始订单金额（计价货币） |
| `--maxSafetyOrds` | 是 | - | 最大安全订单，整数 [0, 100]（例如，`3`；`0` = 无 DCA） |
| `--safetyOrdAmt` | 条件 | - | 安全订单金额（计价货币）。当 `maxSafetyOrds > 0` 时需要 |
| `--pxSteps` | 条件 | - | 初始价格偏差 [0.001, 0.5]，例如，`0.03` = 3%。当 `maxSafetyOrds > 0` 时需要 |
| `--pxStepsMult` | 条件 | `1` | 价格步长乘数（例如，`1.2`）。当 `maxSafetyOrds > 0` 时需要 |
| `--volMult` | 条件 | `1` | 安全订单大小乘数（例如，`1.5`）。当 `maxSafetyOrds > 0` 时需要 |
| `--tpPct` | 是 | - | 止盈比率：长 [0.001, 10]，短 [0.001, 0.9999]（例如，`0.03` = 3%） |
| `--slPct` | 否 | - | 止损比率，必须超过 MPD（例如，`0.05` = 5%）。必须与 `--slMode` 一起使用 |
| `--slMode` | 否 | `market` | 止损类型：`limit` 或 `market`。必须与 `--slPct` 一起使用 |
| `--allowReinvest` | 否 | `true` | 将利润再投资到下一个 DCA 周期 |
| `--triggerStrategy` | 否 | `instant` | contract_dca: `instant`、`price`、`rsi`；spot_dca: `instant`、`rsi` |
| `--triggerPx` | 否 | - | 触发价格 — 当 `triggerStrategy=price` 时需要（合约 DCA 仅限） |
| `--triggerCond` | 否 | - | `cross_up` 或 `cross_down` — 当 `triggerStrategy=rsi` 时需要，当 `triggerStrategy=price` 时可选 |
| `--thold` | 否 | - | RSI 阈值（例如. `30`） — 当 `triggerStrategy=rsi` 时需要 |
| `--timeframe` | 否 | - | RSI 时间框架（例如. `15m`） — 当 `triggerStrategy=rsi` 时需要 |
| `--timePeriod` | 否 | `14` | RSI 期间 — 当 `triggerStrategy=rsi` 时可选 |
| `--algoClOrdId` | 否 | - | 客户定义的策略订单 ID（1-32 字母数字） |
| `--reserveFunds` | 否 | `true` | `true` 或 `false` — 是否保留资金 |
| `--tradeQuoteCcy` | 否 | - | 交易计价货币 |

**条件必填逻辑：**
- 始终必填：`--algoOrdType`、`--instId`、`--direction`、`--initOrdAmt`、`--maxSafetyOrds`、`--tpPct`
- 当 `algoOrdType=contract_dca` 时：还需必填 `--lever`
- 当 `maxSafetyOrds > 0` 时：还需必填 `--safetyOrdAmt`、`--pxSteps`、`--pxStepsMult`、`--volMult`
- `--slPct` 和 `--slMode` 必须同时设置或同时省略

---

### DCA Bot — 停止

```bash
okx bot dca stop --algoOrdType <spot_dca|contract_dca> --algoId <id> [--stopType <1|2>] [--json]
```

**工作流程：**
1. 运行 `bot dca details --algoId <id> --algoOrdType <type>` 并检查 `state` 字段。
2. 如果 `state=running`：调用停止（spot_dca 需要带 `--stopType`）。
3. 如果 `state=no_close_position`（用户之前用 stopType=2 停止过）：再次用 `--stopType 1` 调用停止以关闭剩余的持仓。

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `--algoOrdType` | 是 | - | `spot_dca` 或 `contract_dca` |
| `--algoId` | 是 | - | DCA bot 策略订单 ID（来自创建或列表输出）。不是普通交易订单 ID |
| `--stopType` | 条件必填 | `1` | `spot_dca` 需要的：`1`=卖出所有代币，`2`=保留代币。`contract_dca`：`1`=平仓（默认），`2`=保持持仓开放 |

---

### DCA Bot — 列出订单

```bash
okx bot dca orders [--algoOrdType <spot_dca|contract_dca>] [--algoId <id>] [--instId <id>] [--history] [--json]
```

| 参数 | 必填 | 默认 | 描述 |
|---|---|---|---|
| `--algoOrdType` | 否 | `contract_dca` | 按策略类型筛选 |
| `--algoId` | 否 | - | 按DCA bot 策略订单 ID 筛选 |
| `--instId` | 否 | - | 按合约筛选 |
| `--history` | 否 | false | 显示已完成/停止的 bot 而不是活跃的 |

---

### DCA Bot — 详情

```bash
okx bot dca details --algoOrdType <spot_dca|contract_dca> --algoId <id> [--json]
```

返回：`avgPx`、`upl`、`liqPx`、`sz`、`tpPx`、`slPx`、`initPx`、`fundingFee`、`fee`、`fillSafetyOrds`、`algoClOrdId`、`baseSz`、`quoteSz`、`tradeQuoteCcy`。

---

### DCA Bot — 子订单

```bash
okx bot dca sub-orders --algoOrdType <spot_dca|contract_dca> --algoId <id> [--cycleId <id>] [--after <id>] [--before <id>] [--limit <n>] [--json]
```

| 标志 / 参数 | 效果 |
|---|---|
| *(默认)* | 列出所有周期 |
| `--cycleId <id>` | 显示特定周期内的订单 |

## 快速入门

```bash
# 现货网格：BTC 90k–100k，10 个网格，1000 USDT
okx bot grid create --instId BTC-USDT --algoOrdType grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000

# 合约网格：BTC perp，中性，5x，100 USDT 保证金
okx bot grid create --instId BTC-USDT-SWAP --algoOrdType contract_grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 \
  --direction neutral --lever 5 --sz 100

# 币本位合约网格：BTC 反向 perp
okx bot grid create --instId BTC-USD-SWAP --algoOrdType contract_grid \
  --minPx 90000 --maxPx 100000 --gridNum 10 \
  --direction long --lever 5 --sz 0.01

# 合约 DCA bot：BTC perp，做多，3x，3% 止盈
okx bot dca create --algoOrdType contract_dca --instId BTC-USDT-SWAP --lever 3 --direction long \
  --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
  --pxSteps 0.03 --pxStepsMult 1 --volMult 1 --tpPct 0.03

# 现货 DCA bot：BTC 现货，做多，5% 止盈
okx bot dca create --algoOrdType spot_dca --instId BTC-USDT --direction long \
  --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
  --pxSteps 0.03 --pxStepsMult 1.2 --volMult 1.5 --tpPct 0.05

# 修改网格价格区间
okx bot grid amend --algoId 3486105572796182528 --maxPx 102000 --minPx 88000 --gridNum 14

# 修改网格止盈/止损
okx bot grid amend --algoId 3486105572796182528 --instId BTC-USDT --tpTriggerPx 110000 --slTriggerPx 80000

# 一次调用修改两者（组合模式）
okx bot grid amend --algoId 3486105572796182528 \
  --maxPx 102000 --minPx 88000 --gridNum 14 \
  --instId BTC-USDT --tpTriggerPx 110000 --slTriggerPx 80000

# 清除止盈/止损（负值使用 =-1 语法）
okx bot grid amend --algoId 3486105572796182528 --instId BTC-USDT --tpTriggerPx=-1 --slTriggerPx=-1

# 列出所有活跃 bot
okx bot grid orders --algoOrdType grid
okx bot grid orders --algoOrdType contract_grid
okx bot dca orders --algoOrdType contract_dca
okx bot dca orders --algoOrdType spot_dca
```

## 跨技能工作流

### 网格 Bot

> 用户："在 90k 和 100k 之间启动 BTC 网格 bot，10 个网格，投资 1000 USDT"

```
1. okx-cex-market    okx market ticker BTC-USDT                     → 确认价格在范围内
2. okx-cex-portfolio okx account balance USDT                       → 确认有足够资金
        ↓ 用户批准
3. okx-cex-bot       okx bot grid create --instId BTC-USDT --algoOrdType grid \
                       --minPx 90000 --maxPx 100000 --gridNum 10 --quoteSz 1000
4. okx-cex-bot       okx bot grid orders --algoOrdType grid          → 确认 bot 活跃
5. okx-cex-bot       okx bot grid details --algoOrdType grid --algoId <id> → 监控 PnL
```

### 合约 DCA Bot

> 用户："启动 BTC perp 的长 DCA bot，3x 杠杆，200 美元初始，3% 止盈"

```
1. okx-cex-market    okx market ticker BTC-USDT-SWAP                → 确认当前价格
2. okx-cex-portfolio okx account balance USDT                       → 确认保证金
        ↓ 用户批准
3. okx-cex-bot       okx bot dca create --algoOrdType contract_dca --instId BTC-USDT-SWAP \
                       --lever 3 --direction long \
                       --initOrdAmt 200 --safetyOrdAmt 100 --maxSafetyOrds 3 \
                       --pxSteps 0.03 --pxStepsMult 1 --volMult 1 --tpPct 0.03
4. okx-cex-bot       okx bot dca orders --algoOrdType contract_dca   → 确认活跃
5. okx-cex-bot       okx bot dca details --algoOrdType contract_dca --algoId <id> → 监控 PnL
```

### 现货 DCA Bot

> 用户："帮我在现货上 DCA BTC，首单 100 USDT，5% 止盈"

```
1. okx-cex-market    okx market ticker BTC-USDT                     → 确认当前价格
2. okx-cex-portfolio okx account balance USDT                       → 确认资金
        ↓ 用户批准
3. okx-cex-bot       okx bot dca create --algoOrdType spot_dca --instId BTC-USDT \
                       --direction long \
                       --initOrdAmt 100 --safetyOrdAmt 50 --maxSafetyOrds 3 \
                       --pxSteps 0.03 --pxStepsMult 1.2 --volMult 1.5 --tpPct 0.05
4. okx-cex-bot       okx bot dca orders --algoOrdType spot_dca       → 确认活跃
```

## 边缘情况

### 网格 Bot

- **价格超出范围**：`--minPx` 必须小于当前价格 < `--maxPx`；先用 `okx-cex-market` 检查
- **余额不足**：检查 `okx-cex-portfolio` → `account balance` 再创建。如果不足，**不要自动转账** — 报告短缺并要求用户指示
- **合约网格方向**：`long`（低价时买入更多）、`short`（高价时卖出）、`neutral`（两者）。方向对合约网格是必填的
- **合约网格 basePos**：默认为 `true` — 做多/做空网格在创建时自动开底仓。中性方向忽略此设置。传递 `--no-basePos` 禁用
- **合约网格 --sz**：投资保证金（USDT-M 为 USDT；币本位为 {base}），不是合约数量
- **币本位网格**：使用反向合约（如 `BTC-USD-SWAP`）。保证金单位是基础币（BTC），不是 USDT
- **停止类型**：`stopType 1` 卖出/平仓所有（默认）；`stopType 2` 保留资产（现货网格）或留持仓待手动平仓（合约网格）
- **止盈/止损**：`tpTriggerPx`/`tpRatio` 和 `slTriggerPx`/`slRatio` 是互斥对。比率止盈/止损仅限合约网格
- **修改 — 至少需要一种模式**：必须提供价格区间参数（`--maxPx`+`--minPx`+`--gridNum`）或止盈/止损参数；两者都不提供会返回验证错误
- **修改 — 组合模式**：价格区间和止盈/止损可以在一个调用中组合（内部是两个顺序 API 请求）
- **修改 — 清除止盈/止损**：传递 `--tpTriggerPx=-1` 或 `--slTriggerPx=-1`（负值使用 `=` 语法，不是 `--flag -1`）
- **修改 — 合约网格 topUpAmt**：如果新区间需要更多保证金，提供 `--topUpAmt`；省略则自动使用最小所需
- **修改 — 现货网格 topUpAmt**：不支持；省略 `--topUpAmt` 对现货网格
- **已停止 bot**：停止会返回错误 — 先用 `bot grid orders --history` 确认状态
- **保证金不足 (51340)**：从错误中提取所需最小值，通过 `okx-cex-portfolio` 检查余额，向用户报告短缺 — 不要自动转账
- **演示模式**：`okx --demo bot grid create ...`（OAuth）或 `okx --profile <demo-profile> bot grid create ...`（API Key）— 安全测试，无真实资金
- **algoClOrdId 重复**：如果相同的 `algoClOrdId` 已存在，API 返回错误码 `51065`

### DCA Bot

- **现货 DCA 方向**：必须始终为 `long`。如果用户说 "现货 DCA 短"，解释现货 DCA 仅支持长方向
- **现货 DCA 停止类型**：停止时，始终询问用户是否要卖出所有代币（`1`）或保留（`2`）
- **合约 DCA 杠杆**：必填。如果缺失，工具会返回验证错误
- **pxStepsMult**：`1.0` = 等间距；`>1.0` = 加宽连续安全订单之间的间距
- **volMult**：`1.0` = 等量；`>1.0` = 增加每个安全订单的大小（马丁格尔扩展）
- **触发策略**：`instant` 立即开始；`price` 等待触发价格（合约_dca 仅限）；`rsi` 等待 RSI 条件（现货_dca 和合约_dca）
- **已停止 bot**：停止会返回错误 — 先用 `bot dca orders --history` 确认
- **演示模式**：`okx --demo bot dca create ...`（OAuth）或 `okx --profile <demo-profile> bot dca create ...`（API Key）— 安全测试，无真实资金
- **INVALID_PRICE_STEPS_MULTIPLIER 错误**：调整 `slPct`。重新计算 MPD = Σ(pxSteps × pxStepsMult^i，i = 0..maxSafetyOrds−1)，然后设置 `slPct` > MPD
- **algoClOrdId 重复**：错误码 `51065`

## 沟通指南

- **网格/DCA**：使用 "bot" 而不是 "策略"（例如，"grid bot"、"DCA bot"）
- **DCA**：始终说 "DCA" 或 "Martingale" — DCA 支持现货 DCA 和合约 DCA
- **中文**：网格 = "网格"，现货 DCA = "现货马丁"，合约 DCA = "合约马丁"
- 使用自然语言描述参数 — "什么价格区间？" 而不是 "输入 minPx 和 maxPx"
- 如果用户已提供值，直接映射 — 不要重新询问

### 参数显示名称

> `{base}` 和 `{quote}`：从 `instId` 中通过 `-` 分割提取。例如，`BTC-USDT-SWAP` → base=BTC，quote=USDT。

#### 网格 Bot — 现货 (`algoOrdType=grid`)

| API 字段 | 英文 | 中文 |
|---|---|---|
| `instId` | 交易对 | 交易对 |
| `minPx` | 下限价格 | 网格下限价格 |
| `maxPx` | 上限价格 | 网格上限价格 |
| `gridNum` | 网格数量 | 网格数量 |
| `quoteSz` | 投入金额（{quote}） | 投入金额（{quote}） |
| `baseSz` | 投入金额（{base}） | 投入金额（{base}） |
| `runType` | 网格间距模式（1=等差, 2=等比） | 网格间距模式（1=等差, 2=等比） |
| `stopType` | 停止方式 | 停止方式 |

#### 网格 Bot — 合约 (`algoOrdType=contract_grid`)

| API 字段 | 英文 | 中文 |
|---|---|---|
| `instId` | 交易对 | 交易对 |
| `minPx` | 下限价格 | 网格下限价格 |
| `maxPx` | 上限价格 | 网格上限价格 |
| `gridNum` | 网格数量 | 网格数量 |
| `sz` | 投入保证金（USDT-M 为 USDT；币本位为 {base}） | 投入保证金（USDT-M 为 USDT；币本位为 {base}） |
| `direction` | 方向（做多 / 做空 / 中性） | 方向（做多 / 做空 / 中性） |
| `lever` | 杠杆倍数 | 杠杆倍数 |
| `runType` | 网格间距模式（1=等差, 2=等比） | 网格间距模式（1=等差, 2=等比） |
| `basePos` | 是否开底仓 | 是否开底仓 |
| `stopType` | 停止方式 | 停止方式 |

#### DCA Bot (现货 & 合约)

| API 字段 | 英文 | 中文 |
|---|---|---|
| `algoOrdType` | 策略类型（现货/合约） | 策略类型（现货/合约） |
| `instId` | 交易对 | 交易对 |
| `initOrdAmt` | 首单金额（{quote}） | 首单金额（{quote}） |
| `safetyOrdAmt` | 补仓金额（{quote}） | 补仓金额（{quote}） |
| `maxSafetyOrds` | 最大补仓次数 | 最大补仓次数 |
| `pxSteps` | 补仓价格跌幅（%） | 补仓价格跌幅（%） |
| `pxStepsMult` | 补仓跌幅倍数 | 补仓跌幅倍数 |
| `volMult` | 补仓金额倍数 | 补仓金额倍数 |
| `tpPct` | 止盈比例（%） | 止盈比例（%） |
| `slPct` | 止损比例（%） | 止损比例（%） |
| `slMode` | 止损类型（限价/市价） | 止损类型（限价/市价） |
| `lever` | 杠杆倍数 | 杠杆倍数 |
| `direction` | 方向（做多/做空） | 方向（做多/做空） |
| `allowReinvest` | 利润再投入 | 利润再投入 |
| `triggerStrategy` | 触发方式 | 触发方式 |
| `triggerPx` | 触发价格 | 触发价格 |
| `algoClOrdId` | 客户端策略订单 ID | 客户端策略订单 ID |
| `stopType` | 停止类型（卖出/保留） | 停止类型（卖出/保留） |
| `reserveFunds` | 预留资金 | 预留资金 |

> **`slPct` 止损逻辑：**
> - 做多：止损价格 = 初始成交价 × (1 − slPct)
> - 做空：止损价格 = 初始成交价 × (1 + slPct)
> 触发且完全平仓后，bot 结束。

## 全局说明

- 所有 bot 在 OKX 服务器上运行 — 停止 CLI 不会影响它们
- 认证方法和交易模式在 "凭证 & 配置检查" 中确定；请查看该部分参数规则
- `--json` 默认返回 OKX API v5 原始响应。添加 `--env` 将输出包装为 `{"env": "<live|demo>", "profile": "<name>", "data": <response>}`
- 速率限制：每个 UID 每 2 秒 20 个请求
- 网格 `--gridNum` 范围：2–100
