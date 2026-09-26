# 技能：crypto-com-app

## 代理能力要求

此技能要求您的代理平台支持以下功能。如果您的平台缺少任何**必需**的功能，该技能将无法正常工作。

| 功能 | 必需 | 详细说明 |
|---|---|---|
| **Shell 命令执行** | 是 | 必须能够运行 `npx tsx ./scripts/...` 并捕获 stdout |
| **环境变量** | 是 | 必须从 shell 环境中读取 `CDC_API_KEY` 和 `CDC_API_SECRET` |
| **JSON 解析** | 是 | 必须解析脚本 stdout 中的结构化 JSON 以提取字段 |
| **多轮对话** | 是 | 交易使用报价 → 确认的流程，跨越多个用户回合 |
| **持久内存** | 否 | 用于 `confirmation_required` 偏好设置。如果不受支持，则默认始终确认交易 |
| **经过时间感知** | 否 | 用于检查报价有效期（`countdown` 字段）。如果不受支持，则始终尝试确认并妥善处理 `invalid_quotation` 错误 |

## 关键：此技能的工作原理

**你必须使用 TypeScript 脚本进行所有 API 交互。绝对不要使用 `curl`、`fetch` 或任何其他 HTTP 方法直接调用 API。**

脚本处理请求签名、错误处理和响应格式化。如果你绕过它们：
- 请求将失败（缺少 HMAC 签名）
- 响应不会被过滤或结构化

**对于每个用户请求，在下方找到匹配的命令并使用 `npx tsx` 运行它。读取 JSON 输出。根据它采取行动。**

## 配置
- BASE_URL: `https://wapi.crypto.com`
- CDC_API_KEY: `{{env.CDC_API_KEY}}`
- CDC_API_SECRET: `{{env.CDC_API_SECRET}}`
- CONFIRMATION_REQUIRED: `{{memory.confirmation_required}}`（默认：true）
- SKILL_DIR: 包含此 `SKILL.md` 文件的目录。从您加载此文件的路径中解析它（例如，如果您读取 `/home/user/skills/crypto-com-app/SKILL.md`，则 `SKILL_DIR` 是 `/home/user/skills/crypto-com-app`）。

## 环境设置
- `CDC_API_KEY` 和 `CDC_API_SECRET` 必须在使用前作为环境变量设置。
- **在运行任何脚本之前**，通过运行以下命令检查是否设置了这两个变量：
  ```bash
  echo "CDC_API_KEY=${CDC_API_KEY:+set}" "CDC_API_SECRET=${CDC_API_SECRET:+set}"
  ```
  如果任一打印为空而不是 `set`，提示用户：
  > "您的 API 凭证未配置。请在终端中设置它们，然后我才能继续：
  > ```
  > export CDC_API_KEY="your-api-key"
  > export CDC_API_SECRET="your-api-secret"
  > ```
  > 您可以在 https://help.crypto.com/en/articles/13843786-api-key-management 生成 API 密钥。
  > 设置完成后，请告诉我。"
  
  然后 **停止并等待** 用户确认后再重试。
- 如果脚本返回 `MISSING_ENV` 错误，请按相同方式处理：提示用户设置变量并等待。

## 脚本命令

**所有 API 交互必须通过这些脚本进行。** 它们处理签名、执行、过滤和错误格式化。通过 shell 运行下方的适当命令，然后解析 JSON 输出。

**前提条件：** `npx tsx`（需要 Node.js 18+；`tsx` 由 `npx` 自动获取）。

**重要：** 下方所有脚本路径都使用 `$SKILL_DIR` 作为此技能根目录的占位符。从您加载 SKILL.md 的路径中解析它，或 `cd` 进入技能目录并使用 `./scripts/...` 作为路径。两种方法都有效。

### 账户命令

```bash
# 过滤非零余额（范围：fiat | crypto | all）
npx tsx $SKILL_DIR/scripts/account.ts balances [fiat|crypto|all]

# 单个代币余额查询
npx tsx $SKILL_DIR/scripts/account.ts balance <SYMBOL>

# 周交易限额
npx tsx $SKILL_DIR/scripts/account.ts trading-limit

# 查找用于交易的资金来源钱包
npx tsx $SKILL_DIR/scripts/account.ts resolve-source <purchase|sale|exchange>

# 关闭开关 — 撤销 API 密钥
npx tsx $SKILL_DIR/scripts/account.ts revoke-key
```

### 交易命令

交易遵循 **两步流程**：首先获取报价，然后确认订单。

```bash
# 第一步 — 获取报价（类型：purchase | sale | exchange）
npx tsx $SKILL_DIR/scripts/trade.ts quote <type> '<json-params>'
# 返回：{"ok": true, "data": {"id": "<quotation-id>", "from_amount": {...}, "to_amount": {...}, "countdown": 15, ...}}

# 第二步 — 确认订单：将第一步中的数据.id 作为 <quotation-id> 传递
npx tsx $SKILL_DIR/scripts/trade.ts confirm <type> <quotation-id>

# 查看最近交易
npx tsx $SKILL_DIR/scripts/trade.ts history
```

**如何将用户意图映射到交易类型：**

| 用户说 | 交易类型 | 从 | 到 |
|-----------|-----------|------|-----|
| "用 100 美元购买 CRO" | `purchase` | USD (fiat) | CRO (crypto) |
| "出售 0.1 BTC" | `sale` | BTC (crypto) | USD (fiat) |
| "用 0.1 BTC 交换 ETH" | `exchange` | BTC (crypto) | ETH (crypto) |

**报价 JSON 参数按交易类型：**

| 类型 | JSON 字段 |
|------|------------|
| purchase | `{"from_currency":"USD","to_currency":"CRO","from_amount":"100"}` 或使用 `to_amount` 代替 |
| sale | `{"from_currency":"BTC","to_currency":"USD","from_amount":"0.1","fixed_side":"from"}` |
| exchange | `{"from_currency":"BTC","to_currency":"ETH","from_amount":"0.1","side":"buy"}` |

**示例 — "用 100 美元购买 CRO":**

1. 运行：`npx tsx $SKILL_DIR/scripts/trade.ts quote purchase '{"from_currency":"USD","to_currency":"CRO","from_amount":"100"}'`
2. 从响应中读取 `data.id`、`data.from_amount`、`data.to_amount`、`data.countdown`。
3. **如果需要确认**（默认）：询问用户 "确认：100 美元换 X CRO？有效期为 {countdown} 秒。回复 'YES' 继续。"
   - 如果用户在倒计时内说 YES：`npx tsx $SKILL_DIR/scripts/trade.ts confirm purchase <data.id>`
4. **如果选择不确认**（`memory.confirmation_required` 为 `false`）：跳过询问并立即运行 `npx tsx $SKILL_DIR/scripts/trade.ts confirm purchase <data.id>`

**选择/取消选择：** 用户可以说 "停止询问确认" 以自动执行交易，或 "需要确认" 以重新启用提示。见下文第 3 节。

### 代币发现命令

```bash
# 搜索代币
npx tsx $SKILL_DIR/scripts/coins.ts search '{"keyword":"BTC","sort_by":"rank","sort_direction":"asc","native_currency":"USD","page_size":10}'
```

**必需的 JSON 参数：**

| 参数 | 类型 | 允许的值 |
|-----------|------|----------------|
| `sort_by` | string | `rank`, `market_cap`, `alphabetical`, `volume`, `performance` |
| `sort_direction` | string | `asc`, `desc` |
| `native_currency` | string | 大写货币代码（例如 `USD`） |
| `keyword` | string | 搜索字符串，1–100 个字符；仅匹配代币名称和符号 |
| `page_size` | integer | 每页结果数量 |

**可选：** `page_token` — 用于获取下一页的透明令牌（见分页说明）。

**分页：** 响应包括一个 `pagination` 对象，其中包含 `has_more`（布尔值）和 `next_page_token`（字符串）。当 `has_more` 为 `true` 时，将 `next_page_token` 作为 `page_token` 在下一个请求中获取下一页。

**每个代币的关键响应字段：** `rails_id`（与 `currency_id` / `currency` 在交易和账户 API 中相同 — 使用此值进行交叉引用）、`price_native`、`price_usd`、`percent_change_*_native`（过去时间段内的价格表现，例如 `percent_change_24h_native`）。

### 现金（法定货币）命令

现金命令处理存款、取款和银行账户管理。

```bash
# 现金概览 — 余额 + 每种货币的可用支付网络
npx tsx $SKILL_DIR/scripts/fiat.ts discover

# 货币的支付网络
npx tsx $SKILL_DIR/scripts/fiat.ts payment-networks <CURRENCY>

# 存款方法详情（银行路由信息）
npx tsx $SKILL_DIR/scripts/fiat.ts deposit-methods <CURRENCY> <DEPOSIT_METHOD>

# 通过电子邮件向用户发送存款说明
npx tsx $SKILL_DIR/scripts/fiat.ts email-deposit-info <CURRENCY> <VIBAN_TYPE>

# 取款详情（配额、费用、最低金额）
npx tsx $SKILL_DIR/scripts/fiat.ts withdrawal-details <CURRENCY> <VIBAN_TYPE>

# 创建取款订单（返回包含费用和应收金额的订单）
npx tsx $SKILL_DIR/scripts/fiat.ts create-withdrawal-order '<json-params>'

# 执行取款（可能需要提示 TOTP 认证码）
npx tsx $SKILL_DIR/scripts/fiat.ts create-withdrawal <ORDER_ID>

# 列出已链接的银行账户
npx tsx $SKILL_DIR/scripts/fiat.ts bank-accounts [CURRENCY]
```

**关键参数：**

| 参数 | 描述 | 示例值 |
|-----------|-------------|----------------|
| `CURRENCY` | 大写货币代码 | `USD`, `EUR`, `GBP`, `AUD` |
| `DEPOSIT_METHOD` | 来自 `payment-networks` 的网络 ID | `us_ach`, `sepa`, `uk_fps` |
| `VIBAN_TYPE` | 与存款方法/取款网络相同 | `us_ach`, `sepa`, `uk_fps` |

**取款订单 JSON 参数：**

| 字段 | 必需 | 描述 |
|-------|----------|-------------|
| `currency` | 是 | 货币代码（例如 `"USD"`） |
| `amount` | 是 | 作为字符串的金额（例如 `"500.00"`） |
| `viban_type` | 是 | 支付网络（例如 `"us_ach"`） |
| `bank_account_id` | 否 | 特定的银行账户 ID |

**示例 — "如何存入 USD？"：**

1. 运行：`npx tsx $SKILL_DIR/scripts/fiat.ts payment-networks USD`
2. 读取 `data` 数组 — 每个条目都有 `deposit_push_payment_networks`（例如 `["us_ach", "us_wire_transfer"]`）
3. 获取详情：`npx tsx $SKILL_DIR/scripts/fiat.ts deposit-methods USD us_ach`
4. 读取 `data` 数组 — 包含 `bank_details`，其中包含路由号、账户号码等。

**示例 — "通过 ACH 提取 500 USD"：**

1. 运行：`npx tsx $SKILL_DIR/scripts/fiat.ts withdrawal-details USD us_ach` — 检查配额和费用
2. 运行：`npx tsx $SKILL_DIR/scripts/fiat.ts create-withdrawal-order '{"currency":"USD","amount":"500","viban_type":"us_ach"}'`
3. 从响应中读取 `data.id`（订单 ID）、`data.fee`、`data.receivable_amount`。
4. **向用户确认：** "通过 ACH 提取 500 USD。费用：{fee}。您将收到：{receivable_amount}。确认？"
5. 如果是 YES：`npx tsx $SKILL_DIR/scripts/fiat.ts create-withdrawal <order-id>`
6. 如果需要 TOTP，脚本将在 stderr 上提示输入 6 位认证码。

### 输出格式

每个脚本将结构化 JSON 打印到 stdout：

**成功：**
```json
{"ok": true, "data": { ... }}
```

**错误：**
```json
{"ok": false, "error": "ERROR_CODE", "error_message": "Human-readable message"}
```

## 限制
- **验证：** 成功需要脚本输出中的 `ok: true`。
- **确认窗口：** 报价有效期由报价数据中的 `countdown` 字段定义。
- **执行警告：** 如果订单确认时间 > 5 秒，通知："订单提交，但耗时比预期长。请使用 'Show recent trades' 查看订单状态。"
- **速率限制：**
  - 最大 **每分钟 10 笔交易**。
  - 最大 **每分钟 100 个 API 调用**。
  - 在 HTTP 429 (`RATE_LIMITED` 错误)：在重试相同请求前等待 **60 秒**。通知用户："速率限制达到 — 请等待 60 秒再尝试。"

## 错误处理

所有脚本返回结构化错误。解析 `error` 字段以确定适当的响应。

### 脚本错误代码

这些是脚本 JSON 输出中的 `error` 值。它们告诉您发生了哪种类别的失败。

| 错误代码 | 含义 | 代理响应 |
|------------|---------|----------------|
| `MISSING_ENV` | `CDC_API_KEY` 或 `CDC_API_SECRET` 未设置 | 告知用户通过终端设置环境变量 |
| `API_ERROR` | API 返回非 200 或 `ok !== true` | 报告："交易失败：{error_message}" |
| `INVALID_ARGS` | 命令行参数错误 | 显示 `error_message` 中的正确用法 |
| `QUOTATION_FAILED` | 报价请求被 API 拒绝 | 向用户报告 `error_message`（见 API 错误下方） |
| `EXECUTION_FAILED` | 订单确认失败 | 报告并建议："请使用 'Show recent trades' 查看订单状态" |
| `API_KEY_NOT_FOUND` | 密钥已撤销或不存在 | "API 密钥未找到 — 它可能已经撤销。" |
| `RATE_LIMITED` | 请求过多（HTTP 429） | "速率限制达到 — 请等待 60 秒再尝试。" |
| `UNKNOWN` | 预期之外的错误 | 直接向用户报告 `error_message` |

**规则：** 当输出中的 `ok` 为 `false` 时，停止当前操作并向用户报告上述错误。失败后绝不能进行下一步。

### 常见 API 错误（快速参考）

这些是出现在 `QUOTATION_FAILED`、`EXECUTION_FAILED` 或 `API_ERROR` 响应中的 *特定* API 错误代码。它们告诉您 API 为什么拒绝请求。

| `error` | 含义 | 恢复 |
|---------|---------|----------|
| `not_enough_balance` | 余额不足 | 检查余额，减少交易金额 |
| `invalid_currency` | 未知货币代码 | 通过代币搜索验证 |
| `invalid_quotation` | 报价过期或已使用 | 请求新报价 |
| `failed_to_create_quotation` | 报价引擎错误 | 短暂重试 |
| `not_eligible_for_prime` | 不符合 Prime 奖励条件 | 无 Prime 地进行 |
| `unauthorized` | 账户未批准进行交易 | 联系支持 |
| `restricted_feature` | 账户上限制功能 | 向用户报告 `error_message` |
| `existing_currency_order_error` | 正在进行中的现有订单 | 等待或取消现有订单 |
| `viban_purchase_not_enabled` | 法定货币到加密货币未启用 | 账户功能不可用 |
| `crypto_viban_not_enabled` | 加密货币到法定货币未启用 | 账户功能不可用 |
| `bank_transfer_not_enabled` | 银行转账未启用 | 账户功能不可用 |
| `missing_parameter` | 缺少必需参数 | 脚本错误 — 报告它 |
| `failed_to_create_transaction` | 交易创建失败 | 重试或联系支持 |
| `key_not_active` | API 密钥已撤销或过期 | 生成新 API 密钥，更新环境变量 |
| `api_key_not_found` | 密钥不存在或属于其他用户 | 验证 `CDC_API_KEY` 中是否设置了正确的密钥 |
| `totp_required` | 取款需要 2FA 代码 | 脚本将自动处理 — 提示用户输入认证码 |
| `withdrawal_limit_exceeded` | 每日/每月配额超出 | 通过 `withdrawal-details` 显示限额，减少金额 |
| `invalid_bank_account` | 银行账户不符合资格 | 查看具有 `status: completed` 的有效账户 `bank-accounts` |
| `withdrawal_cooling_off` | 最近更改了取款设置 | 等待冷却期，向用户报告 `error_message` |
| `email_cooldown` | 过多存款信息邮件 | 等待冷却期（显示在错误中），稍后再试 |

对于动态错误（限额超出、货币禁用、冷却期等），直接向用户报告 `error` 和 `error_message`。有关完整详细信息，请参阅 [references/errors.md](references/errors.md)。

---

## 逻辑与规则

### 1. 资产与来源消歧义

首先确定交易类型：
- **购买** — 法定货币 → 加密货币
- **出售** — 加密货币 → 法定货币
- **交换** — 加密货币 → 加密货币

然后解析资金来源钱包：
- 对于 **购买**：运行 `npx tsx $SKILL_DIR/scripts/account.ts resolve-source purchase`。脚本只返回资金来源的法定货币条目。
- 对于 **出售** 或 **交换**：运行 `npx tsx $SKILL_DIR/scripts/account.ts resolve-source sale`（或 `exchange`）。脚本只返回资金来源的加密货币条目。

**结果（来自 `data.status`）：**
- **`SELECTED`** → 自动选择 `data.currency`。
- **`AMBIGUOUS`** → 提示用户从 `data.options` 中选择。
- **`EMPTY`** → 告知用户 "未找到资金钱包" 并停止。

**"全部出售" 场景：** 如果用户说 "出售所有 [TOKEN]"，运行 `npx tsx $SKILL_DIR/scripts/account.ts balance [TOKEN]`。使用 `data.available` 金额（或 `data.balance`）作为 `from_amount` 用于报价。

### 2. 交易流程（报价 → 确认 → 执行）

当用户询问购买、出售或交换加密货币时，**始终**遵循以下三步流程：

- **步骤 A — 获取报价：** 根据用户的请求构建 JSON 参数（见交易命令中的 "Quotation JSON params" 表格）并运行：
  `npx tsx $SKILL_DIR/scripts/trade.ts quote <type> '<json-params>'`
  从响应中读取 `data.id`、`data.from_amount`、`data.to_amount` 和 `data.countdown`。

- **步骤 B — 询问用户确认：**
    - **如果** `memory.confirmation_required` 为 `true`（或未设置）：
        - 提示："确认：{from_amount} 换 {to_amount}？有效期为 {countdown} 秒。回复 'YES' 继续。"
        - **过期逻辑：** 如果用户在 `countdown` 秒内回复 "YES"，则拒绝："交易被拒绝：报价汇率已过期。请请求新报价。"
        - 仅在用户在有效窗口内回复 "YES" 时才执行步骤 C。
    - **否则（已选择不确认）**：
        - 通知："报价已收到。自动执行..."
        - 立即执行步骤 C。

- **步骤 C — 执行订单：** 运行：`npx tsx $SKILL_DIR/scripts/trade.ts confirm <type> <data.id>`，使用步骤 A 中的 `id`。

### 3. 内存管理（选择/取消选择）
- **选择不确认：** 如果用户说 "停止询问确认" 或 "启用自动交易"，将 `memory.confirmation_required` 更新为 `false`。
- **选择确认：** 如果用户说 "需要确认" 或 "启用手动交易"，将 `memory.confirmation_required` 更新为 `true`。
- **没有持久内存的平台：** 如果您的平台不支持 `{{memory.*}}`，将 `confirmation_required` 视为始终 `true`（最安全的默认值）。

### 4. 错误处理
- 所有脚本输出都包含 `ok` 字段。成功仅定义为 `ok: true`。
- 如果 `ok` 为 `false`，读取 `error` 并根据上表中的指导进行响应。
- 失败后绝不能进行下一步。

### 5. 账户与历史
- **历史：** 运行 `npx tsx $SKILL_DIR/scripts/trade.ts history` — 显示 `data` 中的条目。
- **每周交易限额：** 运行 `npx tsx $SKILL_DIR/scripts/account.ts trading-limit` — 显示为："📊 每周交易限额：{data.used} / {data.limit} USD (剩余：{data.remaining} USD)"。
- **法定货币与加密货币余额路由：** 当用户询问特定货币余额时，确定它是 **法定货币**（USD、EUR、GBP、AUD、SGD、CAD、BRL 等）还是 **加密代币**（BTC、ETH、CRO 等）。
    - **法定货币** → 运行 `npx tsx $SKILL_DIR/scripts/account.ts balances fiat`（显示所有法定货币余额）或 `npx tsx $SKILL_DIR/scripts/fiat.ts discover`（显示余额 + 支付网络）。**绝对不要**使用 `balance <SYMBOL>` 查询法定货币 — 它会查询加密钱包，并且始终返回 0。
    - **加密代币** → 运行 `npx tsx $SKILL_DIR/scripts/account.ts balance <SYMBOL>`。
    - **不确定** → 运行 `npx tsx $SKILL_DIR/scripts/account.ts balances all` 以显示法定货币和加密货币。
- **余额（分类）：**
    - 如果 "列出法定货币"：运行 `npx tsx $SKILL_DIR/scripts/account.ts balances fiat`。
    - 如果 "列出加密货币"：运行 `npx tsx $SKILL_DIR/scripts/account.ts balances crypto`。
    - 如果 "列出全部"：运行 `npx tsx $SKILL_DIR/scripts/account.ts balances all`。**关键：** 当请求两者时，始终先显示法定货币部分，然后显示加密货币余额。
    - 脚本会自动过滤出余额为 0 的条目。如果一个类别中没有条目输出，则在该标题下显示 "No holdings"。
    - **加密货币余额** (`data.crypto`) 包含一个 `note` 字段（"可用于交易"）和一个 `wallets` 数组。始终向用户说明这些金额是可用于交易的 — 跨所有产品的总持有量可能更高。
    - **投资组合分配：** 当查询加密货币余额时，输出可能包含一个 `portfolio_allocation` 数组 — 每个条目都有一个产品 `name` 和 `price_native`（USD 值）。显示此摘要，以便用户了解其资产在产品间的分布（例如，加密钱包、交易所、赚取、质押等）。
    - **单个代币余额** (`balance <SYMBOL>`) 输出可能包含一个 `product_allocation` 对象 — 键是产品名称（例如 `crypto_earn`, `staking`, `supercharger`, `crypto_basket`, `airdrop_arena`），值是每个产品中持有的代币数量。仅包含非零产品的条目。将这些分配总结给用户，以便他们了解其代币的完整持有情况。

### 6. 关闭开关
- **触发：** 用户说 "停止所有交易", "kill switch" 或类似紧急停止命令。
- **始终要求明确确认**，无论 `memory.confirmation_required` 的值如何：
    - 提示："⚠️ 警告：这将立即撤销您的 API 密钥并禁用所有交易。必须生成新的 API 密钥才能恢复。回复 'CONFIRM KILL SWITCH' 继续。"
    - 仅在用户回复确切短语时执行。
- **执行：** 运行 `npx tsx $SKILL_DIR/scripts/account.ts revoke-key`。
- **成功 (`ok: true`)：** 通知："🛑 关闭开关已激活。API 密钥已被撤销。所有交易已禁用。生成新的 API 密钥并更新您的环境变量以恢复。"
- **`API_KEY_NOT_FOUND` 错误：** 通知："API 密钥未找到 — 它可能已经撤销或不存在。"
- **幂等性：** 撤销已撤销的密钥不是错误；按成功处理。

### 7. 余额显示格式
- **法定货币标题：** "🏦 法定货币余额"
- **加密货币标题：** "🪙 加密货币余额"
- 始终在请求两者时先显示法定货币部分，再显示加密货币部分。
- **绝对不显示余额为 0 的资产。** 仅显示余额大于 0 的资产。如果一个类别中的所有资产余额都为 0，则在该标题下显示 "No holdings"。

### 8. 现金存款与取款

**术语：** 使用 "现金"（不要使用 "法定货币"）在用户界面消息中。说 "您的现金余额" 而不是 "您的法定货币余额"。

**货币消歧义：** 如果用户没有指定货币，运行 `discover` 首先进行。
- **一个货币余额** → 自动选择它并继续。
- **多个货币余额** → 在继续之前向用户显示列表并要求选择。
- **没有余额** → 通知： "您还没有任何现金余额。" 并停止。

**存款流程：**
1. 运行 `discover` 以向用户显示其现金货币和可用网络
2. 用户选择货币和网络 — 运行 `deposit-methods` 获取银行详情
3. 向用户展示银行详情（路由号、账户号码、银行名称、参考）
4. 可选地运行 `email-deposit-info` 将说明通过电子邮件发送给用户
5. **速率限制：** `email-deposit-info` 的限制为每 30 分钟 5 个请求。在冷却错误时，通知用户并显示 `cooldown_in_seconds` 值。

**取款流程：**
1. 运行 `bank-accounts <currency>` 列出符合条件的账户（仅过滤 `status: "completed"`）
   - **一个符合条件的账户** → 自动选择它
   - **多个符合条件的账户** → 显示列表（银行名称、账户标识符、网络）并要求用户选择
   - **没有符合条件的账户** → 通知： "没有符合条件的银行账户 {currency}。您需要先链接银行账户。" 并停止
2. 运行 `withdrawal-details` 检查配额、费用和最低金额
3. 运行 `create-withdrawal-order` 使用金额、网络和步骤 1 中的 `bank_account_id` — 返回包含费用的订单
4. **始终向用户确认**，无论 `memory.confirmation_required` 的值如何：
   - 显示：金额、费用、应收金额、网络、目标银行账户、处理时间
   - 要求明确 "YES" 继续
5. 运行 `create-withdrawal` 使用订单 ID
6. **TOTP 处理：** 如果 API 返回 `totp_required`，脚本将在 stderr 上提示输入 6 位认证码。代理应告诉用户： "请在提示时输入您的 6 位认证码。" 绝对不要尝试生成或绕过 TOTP。
