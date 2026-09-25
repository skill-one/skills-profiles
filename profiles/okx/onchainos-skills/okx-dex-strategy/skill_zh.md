# Onchain OS DEX 策略

包含四个子命令的 Agentic Wallet 限价订单界面——`create-limit`、`cancel`、`list`、`resume`。当 BE 返回 `UPGRADE_REQUIRED` 时，CLI 会透明地执行 SA 激活（Trader Mode 升级/重新升级），技能无需暴露该细节。

## 预飞行检查

> 阅读 `../okx-agentic-wallet/_shared/preflight.md`。如果该文件不存在，则回退到 `_shared/preflight.md`。策略端点需要经过身份验证的 Agentic Wallet 会话——在运行任何子命令之前确认登录。

## 显示标签和输出语言（单一事实来源）

本节是用户界面的**规范规则**。本技能中的其他部分都应遵循它。

**规范显示标签**——代理仅向用户展示的唯一字符串。CLI 直接返回这些字符串（`statusLabel`）用于 `status`；对于 `strategyType`，代理从下文的 §`strategyType` 和 §`status` 表中查找它们。

| 界面 | 规范英文显示标签 |
|---|---|
| `strategyType` (4 个值) | `Buy Dip` / `Take Profit` / `Stop Loss` / `Buy Above` |
| `status` (9 个值) | `Expired` / `Cancelling` / `Cancelled` / `Failed` / `Trading` / `Completed` / `Creating` / `Active` / `Suspended` |

**翻译规则**——匹配用户的对话语言。显示标签上方是规范英文。当用户使用其他语言对话时，代理在输出时将标签翻译为匹配对话语言。

**永远不要**（这些规则适用于此技能的每个地方）：
- 在一个标签中混合两种语言（选择一种——永远不要并排渲染英文标签和翻译），
- 向用户暴露底层的**枚举名称**（`BUY_DIP`、`CHASE_HIGH`、`COMPLETED`、…），
- 向用户暴露底层的**CLI 标志值**（`buy_dip`、`chase_high`、`completed`、`cancelled`、…），
- 当用户使用非英语语言对话时，**不要**原封不动地传递 CLI 的原始 `statusLabel`——翻译它。

**注意：**
- CHASE_HIGH 在英文中显示为 **`Buy Above`**（不是 "Chase High"）。
- SPEEDING_UP (-4) 不是有效的过滤器或显示值。

## 边界与 `okx-dex-swap`

| 用户意图 | 技能 |
|---|---|
| "现在用 X 交换 Y" / "用 USDC 买 0.5 ETH" | `okx-dex-swap`（市价单，立即执行） |
| "如果价格跌到 2000 美元就买 ETH" / "当 ETH 达到 5000 美元时卖出" / "在 X 处获利" / "在 Y 处止损" | 此技能（价格触发的限价单） |
| "取消我的挂单" | 此技能 |
| "我有哪些限价单？" | 此技能 |

如果场地明确命名（Uniswap、PancakeSwap、Raydium、Curve、…）→ 转向 `okx-dapp-discovery`。此技能仅支持 OKX 聚合限价单。

## 命令索引

### 1. `onchainos strategy create-limit`

放置单个价格触发的限价单。

```
onchainos strategy create-limit \
  --chain-id <id|alias> \
  --from-token <address> \
  --to-token <address> \
  --amount <decimal-string> \
  --direction <buy|sell> \
  --trigger-price <usd> \
  [--current-price <usd>] \
  [--slippage <value>] \
  [--mev-protection <on|off|default>] \
  [--expires-in <secs>]
```

| 标志 | 必填 | 备注 |
|---|---|---|
| `--chain-id` | 是 | 链标识符或别名：`1`、`solana`、`bsc`、`arbitrum`、`base`、`xlayer` |
| `--from-token` | 是 | 卖方代币合约地址 |
| `--to-token` | 是 | 买方代币合约地址 |
| `--amount` | 是 | 要卖出的 `from_token` 数量（字符串，无精度损失） |
| `--direction` | 是 | `buy` 或 `sell`（不区分大小写）。策略类型由 `--direction` + `--trigger-price` + 当前市场价格推导；代理**不会**显式传递策略类型。 |
| `--trigger-price` | 是 | USD 触发价格。对于策略类型推导是必需的。 |
| `--current-price` | 否 | 比较代币（`to-token` 对于 `buy`，`from-token` 对于 `sell`）当前的 USD 价格（要省略 CLI 通过 `market price` 获取它。当代理已经为确认页面检索了价格时，传递它以跳过额外的 HTTP 循环）。 |
| `--slippage` | 否 | 百分比滑点。默认 `15`。将百分比作为普通数字传递（`slippage 20%` → `--slippage 20`）。注意 `0.05` = 0.05%，不是 5%——对于 5% 传递 `--slippage 5`。 |
| `--mev-protection` | 否 | 三态 `on` / `off` / `default`（默认 = `default`；`default` = BE 选择）。 |
| `--expires-in` | 否 | 订单 TTL（秒）。默认 604800（7 天）——见 §默认订单过期。 |

**输出（JSON，始终——CLI 没有人性化格式模式）：**
```json
{
  "ok": true,
  "data": {
    "orderId": "<id>",
    "status": <int>,
    "statusLabel": "<label>",
    "estimatedWaitTime": <int|null>,
    "eventCursor": "<string|null>"
  }
}
```

**Solana 订单返回 `estimatedWaitTime=0`**——订单可以立即查询；对于所有其他链，代理遵循 §异步等待模式（在重新查询之前固定 3 秒睡眠）。

#### 默认订单过期

BE 默认 = **7 天** (`604800` 秒)。此技能中所有其他 "7 天" 提及都由此处推导。

#### 支持的链

策略订单仅支持这 6 条链。任何其他链必须由代理在第一时间拒绝——不要调用 `create-limit`，甚至不要打开步骤 1 确认。

| chainIndex | 名称 | `--chain-id` 别名 |
|---|---|---|
| 1 | Ethereum | `ethereum`、`eth`、`1` |
| 56 | BSC | `bsc`、`56` |
| 196 | X Layer | `xlayer`、`196` |
| 501 | Solana | `solana`、`sol`、`501` |
| 8453 | Base | `base`、`8453` |
| 42161 | Arbitrum | `arbitrum`、`arb`、`42161` |

**预飞行规则（代理）**：当用户提到链时，将其解析为其 chainIndex 并检查此列表。如果链**不在**表中（例如，Polygon `137`、Optimism `10`、Avalanche `43114`、Linea `59144`、Sui `784`、Tron `195`、…），直接回复：

> Strategy orders are only supported on Ethereum / BSC / X Layer / Solana / Base / Arbitrum right now. `<requested chain>` is not supported — pick one of these to continue.

**不要**继续到步骤 1 确认。**不要**调用 CLI。CLI 也防御此行为（在 BE 之前验证相同的 6 链白名单），但代理在更早捕获它可以节省一个往返行程并提供更清晰的与用户确切措辞相关的消息。

#### `strategyType` 枚举 + 推导

`strategyType` 在 CLI 中**完全推导**自 `(--direction, --trigger-price, 当前市场价格)`——没有 `--type` 标志，代理永远不会传递或计算整数。此单一表格涵盖了两种用途：为步骤 1 确认页面推导**显示标签**，以及将 `list` 响应中的 `strategyType` 整数映射回显示标签。显示标签是唯一面向用户的字符串（见 §显示标签 & 输出语言）。

| strategyType (int) | 枚举名称 | 方向 | 触发与当前 | 显示标签 | 含义 |
|---|---|---|---|---|---|
| 2 | BUY_DIP | buy | trigger < current | Buy Dip | 当价格跌至触发价时买入 |
| 5 | CHASE_HIGH | buy | trigger ≥ current | Buy Above | 当价格上涨至触发价时买入 |
| 3 | TAKE_PROFIT | sell | trigger > current | Take Profit | 当价格上涨至触发价时卖出 |
| 4 | STOP_LOSS | sell | trigger ≤ current | Stop Loss | 当价格下跌至触发价时卖出 |

相等折叠到激进的一侧（CHASE_HIGH / STOP_LOSS），与 CLI 匹配。

**代理流程:**

1. **解析方向（buy / sell）** 从用户意图（"buy" / "ape in" / "snap up" → buy；"sell" / "take profit" / "stop loss" / "exit" → sell）。原封不动地传递为 `--direction <buy|sell>`。
2. **获取当前价格**——调用 `onchainos market price --chain <chain> --address <token>`，读取 `data[0].price`。对于 BUY 方向查询**to-token** 的当前价格；对于 SELL 方向查询 **from-token** 的当前价格。代理需要此信息用于（a）步骤 0 USD 值预飞行，(b) 步骤 1 确认页面 "Trigger Price vs current"，以及 (c) 根据上表计算显示标签。
3. **将 `--current-price <usd>` 传递给 CLI** 以便它不会重新获取。 （如果代理省略它，CLI 会自己获取相同的值——正确但会多一个往返行程。）

#### 两步确认流程（代理必须遵循）

`create-limit` 是写操作。**代理必须首先向用户展示确认摘要，然后用户明确确认后才能调用 CLI。** CLI 本身不进行限制（它直接调用 BE）；此合同在技能层强制执行。

**步骤 0 — 最小订单值预飞行（必须在步骤 1 之前运行）：**

BE 强制最小订单值为 **$1 USD**（否则返回错误 `100010 ORDER_AMOUNT_TOO_SMALL`）。为了避免浪费一个往返行程和确认页面在 BE 将拒绝的金额上，代理必须首先验证 `from-side` USD 值。

1. **获取 from-token 价格 (USD):**
   - 如果 from-token 是众所周知的稳定币（USDT / USDC / USDG / USDe / DAI / FDUSD / ...）：假设 `from_price ≈ 1.0` 而无需 HTTP 调用。
   - 否则：调用 `onchainos market price --chain <chain> --address <from_token>`，读取 `data[0].price` 作为 `from_price`。
2. **计算 USD 值：** `usd_value = from_amount × from_price`。
3. **如果 `usd_value < 1.0`:**
   - 计算 `min_from_amount = ceil(1.0 ÷ from_price)`，四舍五入到合理的显示精度（例如，当 `from_price ≥ 0.1` 时为整数单位；其他情况下为 2-4 位有效数字）。
   - 向用户展示**正好这一行规范文本**，**没有额外的文本**——没有 USD 值计算，没有 $1 阈值提及，没有回显用户原始金额，没有后续句子，没有道歉：

     `Minimum order amount: <min_from_amount> <from_symbol>`

     将前缀在输出时根据 §显示标签 & 输出语言进行翻译（例如，对于中文用户，代理以中文渲染相同的事实）。结构保持单行：`<localised prefix> <min_from_amount> <from_symbol>`。
   - **停止。不要渲染步骤 1。不要调用 CLI。** 等待用户提供更大的 `--amount`，然后从顶部重新运行步骤 0。
4. **如果 `usd_value ≥ 1.0`:** 保留 `from_price` 并继续（步骤 1 的 "Value" 列重用它；无需重新获取），然后继续到步骤 1。

**示例**（用户希望在一条链上花费 1 OKB，其中 OKB ≈ $0.10）：
- `from_price = 0.10`, `usd_value = 1 × 0.10 = 0.10 < 1.0` → 失败
- `min_from_amount = ceil(1.0 / 0.10) = 10`
- 输出: `Minimum order amount: 10 OKB`
- 停止。没有步骤 1，没有额外的文本。

**步骤 1 — 显示订单摘要供用户确认。** 五个顶级类别和子项；代理可以自由组织运行时文本，但**不能**省略任何类别：

| # | 类别 | 子项 | 来源 |
|---|---|---|---|
| 1 | 链 | — | 从 `--chain-id` 解析的人类可读链名（Arbitrum / BSC / Solana / …） |
| 2 | 订单类型 | 根据 §`strategyType` 表的显示标签 (`Buy Dip` / `Take Profit` / `Stop Loss` / `Buy Above`) — 根据 §显示标签 & 输出语言翻译 | 推导的 "Strategy type derivation" 以上 |
| 3 | From token | 符号（例如 `USDC`）；数量（例如 `10`） | 代币元数据中的符号；数量是原始 `--amount` 值 |
| 4 | To token | 符号（例如 `ARB`）；触发价格（例如 `$0.10`，以美元计价）；预计数量（预测的 to-token 数量）；值（估计的 USD 值） | 符号/触发价格直接；预计数量和值由代理计算——见公式以下 |
| 5 | Slippage | 要么 `Default 15%`（用户没有提到 slippage）要么 `User-specified X%`（用户明确说了 "slippage X%") | 见 Slippage 显示规则以下 |

**预计数量 / 值公式:**

- 买入方向 (BUY_DIP / CHASE_HIGH):
  - `Estimated Amount` = `from_amount` ÷ `trigger_price`（以 to-token 的单位）
  - `Value` = `from_amount` × `from_token_USD_price`（如果 from 是稳定币，≈ `from_amount`）
- 卖出方向 (TAKE_PROFIT / STOP_LOSS):
  - `Estimated Amount` = `from_amount` × `trigger_price`（以 to-token 的单位，通常是稳定币）
  - `Value` = `from_amount` × `trigger_price`（如果 to 是稳定币，等于预计数量）

**Slippage 显示规则:**

- 用户**没有**在对话中提到 slippage → 显示 `Slippage: Default 15%`，并且**省略 `--slippage`** 在 CLI 调用中（CLI 默认为 15）。
- 用户明确说了 "slippage X%" / "use X% slippage" / 类似 → 显示 `Slippage: User-specified X%`，并且传递 `--slippage X` 在 CLI 调用中。

**结构示例**（显示标签来自 §`strategyType` / §`status` 表；见 §显示标签 & 输出语言中的跨切规则）:

```
1. Chain: Arbitrum
2. Order Type: Buy Dip
3. From: USDC 10
4. To:
   - Symbol: ARB
   - Trigger Price: $0.10
   - Estimated Amount: 100 ARB
   - Value: $10
5. Slippage: 15% (default)

If the trigger condition is not met within 7 days, this order auto-expires.

Reply confirm / change / cancel.
```

**过期说明（强制）**：在 5 个类别和回复提示之前，代理必须显示订单在创建 7 天后自动过期（如果触发条件未满足）。默认措辞：`If the trigger condition is not met within 7 days, this order auto-expires.`

**步骤 2 — 处理用户的回复:**

- 用户说 "confirm" / "yes" / "submit" → 调用 `onchainos strategy create-limit ...`.
- 用户说 "change amount = 5" / "set trigger to 0.08" / 类似 → 更新相应的字段并**重新渲染步骤 1** 进行另一个确认。
- 用户说 "cancel" / "abort" → **不要**调用 CLI；确认订单已放弃。

> 严格限制：
> 1. **直到用户明确确认之前，永远不要调用 `strategy create-limit`。**
> 2. `Estimated Amount` / `Value` 是代理端的估计值，来自 `trigger_price`，**不是** BE 引用。实际成交数量由 BE 执行时间由滑点和聚合器路由决定；代理必须**不能**将这些估计值呈现为 "实际成交数量"。
> 3. `--trigger-price` 是一个 USD 价格。代理必须向用户明确说明以避免与 "exchange rate = X from-token per 1 to-token" 混淆。
> 4. **当步骤 0 的 USD 值检查失败时，永远不要渲染步骤 1。** 输出单行最小金额警告并停止——用户必须重新开始使用更大的 `--amount`。

### 2. `onchainos strategy cancel`

取消单个、批量或所有活动订单。传递正好一个的三个标志之一：

```
onchainos strategy cancel --order-id <id>
onchainos strategy cancel --order-ids id1,id2,...
onchainos strategy cancel --all
```

**输出 (JSON):** `{ok:true,data:{updateNum:N,estimatedWaitTime:null|n}}`。`updateNum` 是 BE 接受的数量，**不是** 达到终端状态的数量——在等待后使用 `list` 重新查询。

### 3. `onchainos strategy list`

```
onchainos strategy list \
  [--order-id <id>] \
  [--status active,suspended,...] \
  [--chain-id 1,501] \
  [--token <address>] \
  [--limit <int>] \
  [--cursor <string>] \
  [--strategy-mode 7]
```

两种模式：

- **单个订单**：传递 `--order-id <id>` → GET `openOrderDetail`（返回完整的订单形状）。
- **分页查询**：省略 `--order-id` → POST `getOpenOrder`. 活动钱包的地址自动提供；传递 `--limit`（最大 100，默认 100）和 `--cursor` 从上一次响应的 `nextCursor` 进行分页。

**标志 CSV 支持**——`--status` 和 `--chain-id` 接受逗号分隔列表；`--token` 只接受**单个**地址。对于多代币查询，对每个代币调用一次 `list` 并合并结果。

> 完整当前-limitations 列表：见 [references/backend-schema.md](references/backend-schema.md).
