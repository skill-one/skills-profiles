---
name: okx-agent-payments-protocol
description: '处理代理支付和付费端点，通过 x402、MPP、支付链接、a2a-pay 和 HTTP-payment 递归或计量计费。用于 HTTP 402/支付必需；付费代理或 A2MCP 端点；x402/Permit2；MPP 渠道、代金券或会话；HTTP-payment 订阅；或支付ID/链接操作或状态。触发短语：x402/x402Version、X-PAYMENT、PAYMENT-REQUIRED、PAYMENT-SIGNATURE、WWW-Authenticate: Payment、x402 exact/exact+Permit2/upto/aggr_deferred、MPP charge/session、channelId/channel_id、支付渠道代金券/充值/结算/退款、计量计费、paymentId、a2a_、支付链接、A2MCP、付费端点，以及 HTTP 402 period/permit2_subscription。'
---

# OKX Agent 支付协议（调度器）

- 结构化的 `execute_a2mcp_payment` 操作 → 阅读
  `references/a2mcp-execute.md`；不要进入通用支付路由。

> **首先阅读 — 触发时不显示文本 + 永不跳过用户门禁。**
>
> 在检测到 402（或任何触发词）并发出第一个面向用户的面板——推荐步骤 A3.5 的推荐卡片，或确认步骤 A4 的确认卡片——之间，输出**零**用户可见文本。不要显示“收到 402”，不要显示“触发 OKX Agent 支付协议”，不要显示“检测到 N 个方案”，不要枚举方案 / 网络 / 代币 / 金额，不要显示“加载技能”——任何语言（其他语言中的等效短语也受此禁令约束）。技能加载工具调用可能会运行，但不会输出周围的散文。
>
> 每个支付**仅运行一个**确认卡片：A3.5 的推荐卡片（2+ 候选者且用户选择 `yes`）或 A4 的确认卡片（单个候选者，或用户从 A3.5 的扩展列表中选择了替代方案）。不要以“过去的用户偏好” / “精简” / “已确认一次”为借口跳过适用的卡片——这些偏好不存在。不要将两个卡片以相同的信息连续显示——在 A3.5.5 的 `yes` 之后，直接进入步骤 A5。检测后的下一个用户可见文本必须是这两个卡片中的一个。

三种支付路径，通过 HTTP 签名区分：**基于 `accepts` 的 402**（v1 的体中挑战或 v2 的 `PAYMENT-REQUIRED` 头部），**`WWW-Authenticate: Payment` 402**（通道化，`intent="charge"` 或 `"session"`），和 **a2a-pay**（基于 paymentId，无 402）。共享步骤如下（检测 → 解码 → 确认 → 钱包检查），然后调度到参考。

> **面向用户的术语 — 重要**
>
> **规则 1 — 始终称其为“OKX Agent 支付协议”，并始终加粗显示。** 在用户可见消息中始终使用英文术语 **OKX Agent Payments Protocol**，并始终用 markdown 加粗（**OKX Agent Payments Protocol**）以便用户看到它被强调。即使在其他中文句子中，也要将其保留为固定的英文名词短语。将协议字面量和内部标识符保留用于 CLI 调用、HTTP 头部、JSON 有效负载和代码——永远不要对用户说它们。
>
> **规则 2 — 不要叙述内部协议检测。** 调度逻辑（检测到的头部、加载的参考、选择的方案/意图、TEE 与本地密钥路径）是内部的——保持内部。用户只需要看到：(a) 什么正在被支付，(b) 他们需要确认什么，(c) 结果。
>
> **规则 2 的例外 — 仅限狭窄的替代方案列表。** 在步骤 A3.5 中，字面量 `exact` / `aggr_deferred` / `charge` 仅在用户选择“显示其他”的扩展**替代方案列表**中暴露给用户**，因为此时用户正在明确选择方案。它们**不能**出现在：默认推荐卡片、”N 种其他方法“摘要行、状态叙述、错误显示、支付后摘要或任何其他地方。推荐卡片仅显示网络 / 代币 / 金额 / 收款人——永远不会显示方案名称。
>
> **规则 3 — 外部定义的协议字面量保持字节级精确。** JSON 字段 `x402Version`、HTTP 头部 `X-PAYMENT` / `PAYMENT-SIGNATURE` / `PAYMENT-REQUIRED` / `WWW-Authenticate: Payment` 以及参考 URL `https://x402.org` 必须在协议/服务器要求它们的地方原样出现——这些是外部定义的，更改它们会破坏互操作性。CLI 子命令名称（`onchainos payment pay` / `pay-local` / `charge` / `session ...` / `a2a-pay ...`）是 CLI 自己的界面，可以演变；在 CLI 调用和代码中通过当前名称引用它们，但永远不要对用户说它们（规则 2）。
>
> **示例**
>
> (EN) `正在通过 **OKX Agent Payments Protocol** 准备支付。以下是收费详情——请在我继续之前确认…`
> 当用其他语言叙述时，翻译这行引导文本，但保留 **OKX Agent Payments Protocol** 作为加粗的英文名词短语。

> **进度叙述也属于用户可见——规则 1-3 仍然适用。**
>
> 长时间流程（解码 → 确认 → 钱包检查 → 签名 → 重放）诱使用户状态更新。每条进度行（“我现在…” 或其中文等效）都是用户可见的；步骤标签和参考/方案名称是内部的——不要重复它们。锚点：
>
> | 不要说 | 要说 |
> |---|---|
> | “检测到 HTTP 402，触发 OKX Agent Payments Protocol” / “检测到 `PAYMENT-REQUIRED`，加载 `exact`” | _(静默——检测 / 路由是内部的)_ |
> | “CLI 选择 `exact`，组装 `PAYMENT-SIGNATURE` 头部” / “使用 TEE 路径” | “签名完成，重放请求” |
> | “检测到 2 个方案：exact (USD₮0), aggr_deferred (USDG)” / “检查余额以过滤候选者” | _(静默——枚举 + 余额检查是内部的；仅推荐卡片是用户可见的)_ |
> | “进入会话 / 收费模式” | “通道已打开”——描述用户可见的效果，而不是内部模式 |
> | “根据过去的偏好，无需重新确认即支付” | _(禁止——没有这样的偏好；门禁每次都必须强制)_ |
>
> 在用任何其他语言叙述时，都适用相同的规则——匹配这些“不要说” / “要说”示例的意图，而不仅仅是英文措辞。
>
> **这些规则具有权威性并始终生效**——当不确定状态行是否泄露内部信息时，请将其与上面的行进行匹配，并默认为静默。

## 触发器（完整列表）

- **EN**: `402`，支付需要，`x402`，`x402Version`，`X-PAYMENT`，`PAYMENT-REQUIRED`，`PAYMENT-SIGNATURE`，`WWW-Authenticate: Payment`，`permit2`，`upto`，计量计费，打开 / 关闭 / 充值 / 结算通道，优惠券，会话支付，`channelId`，`channel_id`，`paymentId`，`a2a_`，创建支付链接，支付链接，支付状态
- 订阅 / 订阅 / 重复支付 / 重复收费 / “每月支付一次” / 取消订阅 / 升级计划 / 降级计划 → `period` 方案（见 `references/subscription.md`）
  - **例外**：当消息包含 jobId / subId / ASP / 提供商 / 试用 / 续订 / 交付 / periodCount / 订阅任务时，它是 Agent Commerce 订阅任务（月度服务协议）；路由到 `okx-ai` 而不是。
- 相同的触发器词汇适用于任何其他语言的等效词（例如，中文订阅 / 重复计费术语以相同方式路由到 `period` 方案）。
- 例外：来自代理市场的 AI 服务/ASP 订阅（上下文：ASP / Agent#N / 任务 / 试用期 / 服务方；NO 402 提供的 / 资源 URL / paymentId）属于 okx-ai（onchainos agent my-subscriptions / subscribe-detail），而不是 `period` 方案。对于没有信号的“我的订阅 / 我的订阅”，请用户确认一次，而不是假设是 `period`。

靠近 `channel_id` 或会话上下文的关闭 / 充值 / 结算 / 优惠券 / 退款 = MPP 会话操作 → `references/session.md`。

## 预检

预检检查：在每个线程开始时，完成 `../okx-agentic-wallet/_shared/preflight.md` 中的检查。如果缺失，请阅读 `_shared/preflight.md`。

## 命令路由与参考映射

每个 402 信号（或 paymentId）→ CLI 命令 → 参考。详细的门禁 + 解码/确认步骤在下面的路径 A / 路径 B 中。

| 信号 | 命令 | 参考 |
|---|---|---|
| 402 + `PAYMENT-REQUIRED` (v2) / 体 `x402Version` (v1) — 一个**或多个** `accepts[]` 方案 (`exact` / `exact`+Permit2 / `upto` / `aggr_deferred`) | **主要 — 路径 A**：`payment quote <url>` → 确认 → `payment pay --payment-id --yes`。单方案和多方案都使用**相同的**报价流程（CLI 解码、转换、余额检查、签名、**重放**，并返回收据）。即使你已经手动抓取了原始 402，也请通过 `payment quote <url>` 重新输入——永远不要手动组装头部，也永远不要直接跳转到仅签名。**兼容性仅**：`payment pay --payload [--selected-index]`（仅签名 + 手动重放）当 `quote` 不可用时。 | 成功路径加载**无**参考。`references/accepts-schemes.md` 仅用于：支付后方案特定的收据阅读，`Permit2 允许不足` 一次性批准，`pay-local`，`pay --payload` 兼容性路径，或遗留 x402 v1（CLI 输出字段告诉您哪个方案——`permit2Authorization` = `upto` / `exact`+Permit2，`sessionCert` = `aggr_deferred`，`authorization` = `exact`） |
| 402 提供的带有 `accepts[]` 条目的 `scheme == "period"`（即 `permit2_subscription`）——重复/订阅计费 | `payment subscription subscribe/access/change/cancel/cancel-pending/my-subscriptions/allowance-status` | `references/subscription.md` |
| 402 + `WWW-Authenticate: Payment`，`intent="charge"` | `payment charge --challenge` | `references/charge.md` |
| 402 + `WWW-Authenticate: Payment`，`intent="session"`（或会话中的 `channel_id`） | `payment session open/voucher/topup/close` | `references/session.md` |
| paymentId / `a2a_…` 链接 / 创建或检查支付链接 | `payment a2a-pay create/pay/status` | `references/a2a_charge.md` |
| A2MCP / 402 端点 URL，“支付此端点”，条目 A/B 支付节点 | `payment quote <url> [--param k=v ...] [--method GET \| POST \| ...]` | (内联——路径 A) |
| A2MCP **MCP-transport** 端点（URL 以 `/mcp` 或 `/sse` 结尾，返回 `text/event-stream` / JSON-RPC，或您有工具名称） | `payment quote <url>`（发现 → `mcpTools[]`）→ `payment quote <url> --tool <name> --param k=v`（触发 402）→ `payment pay --payment-id <id> --yes` | `references/a2mcp-mcp.md` |
| 用户确认了报价的支付（货币/金额/方案选择） | `payment pay --payment-id <id> [--selected-index <n>] --yes` | (内联——路径 A) |
| 需要解码 `PAYMENT-RESPONSE` 头部或收费收据 | `payment decode-receipt (--header <b64> \| --receipt <json>)` | (内联——只读) |

> **在成功路径上不要加载参考。** 在主要路径 A 流中，`onchainos payment pay --payment-id --yes` 直接签名、重放并返回结算收据——完全跳过 `references/accepts-schemes.md`（这适用于单个 `accepts[]` 方案与多方案完全相同）。在兼容性 `pay --payload` 路径中，CLI 返回一个 `authorization_header`，您需要自己重放——相同的规则，成功时不要加载参考。仅在失败 / 遗留路径上加载 `references/accepts-schemes.md`：`Permit2 允许不足` → `references/accepts-schemes.md`（一次性批准），或遗留 x402 v1 原始证明→其“遗留：x402 v1”部分。`charge` / `session` / `a2a_charge` 总是加载——那些是多阶段流程。

> **通道会话操作**（带有活动 `channel_id` 的关闭 / 充值 / 结算 / 优惠券 / 退款，无论是否新鲜 402）→ 直接跳入 `references/session.md` 在匹配的阶段。**不要**搜索单独的 `close-channel` / `topup-channel` / `settle-channel` 工具——它们都是 `onchainos payment session ...` 子命令。

提供 `funded`、`cancel`，以及——仅当可用时——`选择其他支付方式`；绝不宣传 `无论如何支付` 或询问通用的 `是/否`。路由：`funded` → 重新报价；替代方案 → 显示 `candidates[] + alternatives[]` 中其他足够的条目（如果过期则先重新报价），然后使用 `acceptsIndex` 确认一次；`cancel` → 停止。非主动的、明确的请求，尽管存在资金短缺也要支付，这是单一授权；模糊的 `是` 不是。不要运行 `funding-check` 或添加硬余额门禁。

将所选候选者的 **`acceptsIndex`** 作为 `--selected-index` 传递（不是其在 `candidates[]`/`alternatives[]` 中的位置），以便 CLI 签署用户批准的确切条目。**您必须在支付前停止并确认——不要自动支付。**

### 步骤 A4 — 支付
运行：`onchainos payment pay --payment-id <id> --selected-index <n> --yes [--param key=value ...]`
`--yes` 是必需的（确认资金转移的门禁）。`pay` 签署报价的有效负载，重放，并返回收据——它永远不会重新获取 402。读取 `data.status`：
- `success` → 报告 `txHash`；(条目 B) 任务系统将节点标记为已支付。
- `failed` → 显示 `data.error`；提供重试。
- `pending` → 检查 / 等待最终状态，然后继续。

> 要随时解码返回的 `PAYMENT-RESPONSE` 头或收费收据，请运行 `onchainos payment decode-receipt (--header <b64> | --receipt <json>)`。

---

## 步骤 A1：从原始响应开始（遗留 / WWW-Authenticate 详细信息）

> **`accepts`-基础的 402 → 返回路径 A `payment quote`。** 以下步骤是 **遗留手动路径**（解码 → 组装 → 自己重放）以及 `WWW-Authenticate: Payment` 收费 / 会话挑战的共享解码详细信息。如果您持有的 402 是 **`accepts`-基础的**（`PAYMENT-REQUIRED` 头 v2 / `x402Version` 正文 v1 — `exact` / `exact`+Permit2 / `upto` / `aggr_deferred`，无论是单一方案还是多个方案），请不要继续这里：丢弃原始 402 并在 **路径 A** 中使用 `payment quote <url>` 重新进入。报价流程运行相同的强制确认门禁，并为单方案和多方案返回相同的收据模式——单一方案不是跳过 `quote` 的捷径。仅当您需要回退到显式的 `pay --payload` 签署兼容路径时，或需要 `payment quote` 真正不可用且必须回退到 `WWW-Authenticate: Payment` 收费 / 会话详细信息时，才继续下方。

您已经有了原始 HTTP 响应。如果它不是 402，请直接返回正文。否则 → 步骤 A2。

**捕获用户提示提供的任何请求参数**（例如，“旧金山天气” → `city=旧金山`，`token=0x…`；“翻译成中文” → `lang=zh`）。将每个记录为 `名称 → 值`，用于步骤 A3-Params 计划——这里提供的值**永远不会重新询问**，只是在确认卡中显示。即使第一个请求不需要它们，也要保留它们；卖家可能在支付重放时要求它们。

## 步骤 A2：检测协议

```
优先级 1：response.headers['WWW-Authenticate']
  以 "Payment " 开头        → 继续步骤 A3-WWW-Authenticate
优先级 2：response.headers['PAYMENT-REQUIRED']
  base64 编码的 JSON        → 继续步骤 A3-Accepts (v2)
优先级 3：response.body JSON 包含 "x402Version"
                                → 继续步骤 A3-Accepts (v1)
否则                       → 不是支持的支付协议，停止
```

**两个指示器都存在** — 根据 WWW-Authenticate 的意图分支：

- `intent="session"` 与 `accepts`-基础的选项一起提供 → 停止并询问用户：
  > 服务器通过 **OKX Agent Payments 协议** 提供两种支付风格：
  > 1. **会话（多请求）** — 打开通道并为每个请求签发凭证
  > 2. **一次性购买**
  >
  > 您想使用哪种？

  选项 1 → 继续步骤 A3-WWW-Authenticate（会话路径）。选项 2 → 放弃会话意图并继续步骤 A3-Accepts 使用接受选项。

- `intent="charge"` 与 `accepts`-基础的选项一起提供 → 所有选项都是一次性购买；**不要**显示会话与一次性购买的提示。解码两种协议系列（步骤 A3-Accepts 和步骤 A3-WWW-Authenticate），合并候选者，并让步骤 A3.5 处理推荐。

## 步骤 A3-Accepts：解码

为您**仅用于显示 + 推荐**自己解码 402 有效负载——没有 CLI 循环：

```
raw_402 = response.headers['PAYMENT-REQUIRED']   // v2 (base64 编码的 JSON)
       or response.body                          // v1 (已经是纯 JSON)

decoded = JSON.parse(atob(raw_402))              // v2；v1 的它是 JSON: JSON.parse(response.body)
```

提取用于显示：

```
accepts = decoded.accepts
option  = decoded.accepts[0]       // 仅用于显示
```

**保留 `raw_402` 原样** — 步骤 A6 直接将其传递给 `onchainos payment pay --payload`（CLI 重新解码并签署）。本地解码仅用于显示；永远不要重新编码或组装任何内容。

## 步骤 A3-WWW-Authenticate：解码

解析 WWW-Authenticate 头：

```
Payment id="...", realm="...", method="evm", intent="...", request="<base64url>", expires="..."
```

base64url 解码 `request` 以获取 JSON 正文。保存：

```
intent              charge | session
amount              基本单位字符串（例如 "1000000"）
currency            ERC-20 合约地址
recipient           商家收款地址
methodDetails:
  chainId           EVM 链 ID（例如 X Layer 为 196）
  escrowContract    会话必需，收费不存在
  feePayer          true（交易模式） | false（哈希模式）
  splits            可选，收费仅限，最多 10 条记录
  minVoucherDelta   可选，会话仅限
  channelId         可选，会话充值/凭证仅限——预存在的通道
suggestedDeposit    可选，会话仅限——建议的初始存款
unitType            可选——"request" | "second" | "byte" 等
```

**方法检查**——此处仅支持 `method="evm"`。如果 `method` 是 `"tempo"`、`"svm"`、`"stripe"` 等 → 停止并告诉用户此调度器无法处理。

**挑战过期**——如果 `expires=...`（ISO-8601）已过期，挑战已死亡：在签署前重新发送原始请求以获取新的 402。过期的挑战会以 `30001 错误参数` 失败。

将 `amount` 从基本单位转换为人类可读格式（见 `_shared/amount-display.md`）。

## 步骤 A3-Params：构建请求参数计划

> **在步骤 A3 解码后、任何确认卡之前运行。** 除了支付条款外，卖家可能声明付费重放必须携带哪些参数以及如何携带。构建一个 **param plan**，以便用户在确认支付的同时确认参数，并且重放正确附加它们。

param plan 是一个 `{ name, value, carrier, required, source }` 列表，`carrier ∈ {query, body, header, path}`。没有卖家声明的参数且没有用户命名的参数 → **空计划**；重放不变。

### 源 1 — Bazaar `outputSchema.input`（首选）

如果解码的 402（或任何 `accepts[i]`）携带 `outputSchema.input`，解析它：

| 字段 | 使用 |
|---|---|
| `input.type` | `"http"` → 此处处理。`"mcp"` → 不在范围内，跳过参数组装。 |
| `input.method` | 重放时使用的方法（可能与原始不同）。`GET`/`HEAD`/`DELETE` → 参数在 **查询** 中；`POST`/`PUT`/`PATCH` → 在 **正文** (`input.bodyType`: `json`/`form-data`/`text`) 中。 |
| `input.queryParams` / `input.body` / `input.pathParams` / `input.headers` | 该载体的参数（查询 / 正文 / 路径 / 头部）。 |

JSON Schema `properties` + `required` 给出每个参数的类型和是否必需。每个声明参数一个计划条目。

### 源 2 — 非Bazaar（保守）

没有 `outputSchema.input` → 仅在卖家明确信号下添加参数；**永远不要凭空发明一个**：

- 响应 **正文** 列出要求（`required` / `params` / `parameters` / `fields` / `inputSchema`），OR
- 一个 **错误消息** 命名缺失的参数（例如 `缺少必需的查询参数 "city"`），OR
- 文档化的响应 **头部** 要求一个。

模糊 → 添加任何内容，重放不变。

### 填充值

每个条目，解析 `value`：(1) 用户提示（步骤 A1）→ `source=prompt`，不要重新询问；(2) 对话上下文 → `source=context`；(3) 仍然缺失且必需 → 询问用户，将它们分组为单个问题（这是一个合法的门禁，不是叙述——ZERO-TEXT-ON-TRIGGER 不禁止它）。可选 + 未解决 → 删除。

## 步骤 A3.5：多方案推荐（适用时）

**仅当**组合候选池包含 **2 或更多** 的 `{exact, aggr_deferred, charge, period}` 时适用。否则直接跳转到步骤 A4 使用单个可用候选。

> 当 402 `accepts[]` 包含 2 或更多 `{exact, aggr_deferred, charge, period}` 时，加载 `references/multi-scheme.md`。将 `period` 视为周期性订阅选项：仅在用户意图是持续订阅而不是单次调用时推荐它。

适用时 → **加载 `references/multi-scheme.md`** 并按其顺序执行。它返回所选候选并告诉您在哪里继续：步骤 A4（用户选择了一个替代方案）或直接到步骤 A6（用户使用 `yes` 接受——A5 的钱包检查已经满足）。

## 步骤 A4：显示支付详情并停止

**如果**用户在 A3.5.5 中使用 `yes` 接受了推荐，**请完全跳过此步骤**（卡已显示网络 / 代币 / 金额 / 收款人）。直接进入步骤 A5（如果 A3.5.2 已经处理了登录则为空操作）→ A6。

**如果**正常运行此步骤，则如果：
- 步骤 A3.5 未运行（单候选路径），OR
- 用户从 A3.5 扩展列表中选择了替代方案（所选候选仍需完整详情确认）。

**运行时必须**：显示详情并停止以等待明确的用户确认。在用户确认之前，**不要**调用 `onchainos wallet status` 或任何其他工具。

对于报价流程候选，还显示其 `balanceStatus`；当不足时，显示 `availableAmount`、`requiredAmount` 和 `shortfall`，然后遵循步骤 A3 的单资金卡和操作表。

对于 **`accepts`-基础的 402**（`PAYMENT-REQUIRED` 头 v2 / `x402Version` 正文 v1）：

> 此资源需要通过 **OKX Agent Payments 协议** 支付：
> - **网络**：`<chain name>` (`<option.network>`)
> - **代币**：`<token symbol>` (`<option.asset>`)
> - **金额**：`<人类可读金额>`（来自 v2 的 `option.amount`，或 v1 的 `option.maxAmountRequired`；使用代币小数位从最小单位转换）。对于 `upto` 方案，此金额是一个授权**上限**，不是固定费用——将其显示为 "最多 `<amount>`" / "最多 `<amount>`"。
> - **支付给**：`<option.payTo>`
> - **请求参数**（如果步骤 A3-Params 计划为空，请完全省略此行）：每行参数作为 `<name> = <value>` → `<carrier: query | body | header | path>`
>
> 继续支付？(是 / 否)

对于 **`WWW-Authenticate: Payment` 402**：

> 此资源需要通过 **OKX Agent Payments 协议** 支付：
> - **支付类型**：`一次性支付 | 会话（多个请求）`（显示为 "一次性支付" / "会话（多个请求）" —— 永远不是 "单次购买"；翻译成其他语言时保持相同区分）
> - **网络**：`<chain name>` (`eip155:<chainId>`)
> - **代币**：`<symbol>` (`<currency address>`)
> - **每次请求金额**：`<人类可读>`（原子：`<amount>`)
> - **支付给**：`<recipient>`
> - **谁支付 gas**：`<服务器（交易模式） | 您自己广播>`（哈希模式）
> - **分割收款人**（仅限一次性支付，如果存在）：`<其他 N 方面也收到一部分>`
> - **建议预付余额**（仅限会话，如果存在）：`<人类可读>`
> - **请求参数**（如果步骤 A3-Params 计划为空，请完全省略此行）：每行参数作为 `<name> = <value>` → `<carrier: query | body | header | path>`
>
> 继续支付？(是 / 否)

- **用户确认** → 步骤 A5。
- **用户拒绝** → 停止。不支付，不检查钱包。

## 步骤 A5：检查钱包状态（仅用户明确确认后）

```bash
onchainos wallet status
```

- **已登录** → 步骤 A6。
- **未登录（`accepts`-基础路径）** → 询问用户选择 (1) 钱包登录（TEE 签署）或 (2) 本地私钥 (`onchainos payment pay-local`，支持 `exact + EIP-3009`，`exact + Permit2`，和 `upto` — `aggr_deferred` 不支持，需要 TEE 会话密钥）。在用户选择之前，不要读取文件或检查环境变量。
- **未登录（`WWW-Authenticate: Payment` 路径）** → 询问用户通过 `onchainos wallet login` 登录。**仅 TEE —— 此路径没有本地密钥回退**（只有 `accepts`-基础路径有）。

## 步骤 A6：转交给方案/意图参考

| 路径 | 操作 |
|---|---|
| **`accepts`-基础**（`PAYMENT-REQUIRED` 头 v2 / `x402Version` 正文 v1） | **主要 — 路径 A**：您应该已经在 `payment quote <url>` → 确认 → `payment pay --payment-id --yes` 流程（路径 A 顶部）；它签署、重放并返回收据——无需手组装，成功时无需加载参考。这是对于单一 `accepts[]` 方案和对于多方案相同的。<br>**兼容 / 仅回退**（`quote` 不可用，或显式遗留请求）：运行 `onchainos payment pay --payload '<raw_402 from Step A3>'`。如果步骤 A3.5 运行且用户选择了接受基础的候选，添加 `--selected-index <index in decoded.accepts>` 以便 CLI 签署确切条目；对于单个候选则省略它（CLI 自动选择）。CLI 解码，从所选账户签署，并返回 `{authorization_header, header_name, scheme, wallet}` — **无需手组装**；然后转到重放下方。<br>如果用户选择了本地密钥回退，运行 `onchainos payment pay-local --payload '<raw_402>'` 而不是（成功规则相同；支持 `exact + EIP-3009`，`exact + Permit2`，和 `upto` — `aggr_deferred` 仅 TEE）。<br>**`Permit2 允许不足` 错误**（`upto` / `exact`+permit2，首次支付）→ 加载 **`references/accepts-schemes.md`** 进行一次性批准，然后重试支付。<br>**遗留 v1** — CLI 返回原始证明（`signature`+`authorization`，没有 `authorization_header`）→ 加载 **`references/accepts-schemes.md`** 并遵循其 "遗留：x402 v1" 部分组装 `X-PAYMENT` 头。 |

| `period`（订阅 / `permit2_subscription`） | 在 "决定操作" 加载 **`references/subscription.md`**（订阅 vs 访问 vs 修改 vs 取消）。首次提供 → `payment subscription subscribe`；已激活资源 → `payment subscription access`（永远不重新订阅）；升级/降级 → `change`；拆除 → `cancel` / `cancel-pending`。 |
| **`WWW-Authenticate: Payment`，`intent="charge"`** | 在 "决定模式" 加载 **`references/charge.md`**。 |
| **`WWW-Authenticate: Payment`，`intent="session"`** | 在 "阶段 S1：打开通道" 加载 **`references/session.md`**（如果用户处于活动 `channel_id` 的会话中，可以跳到 S2 / S2b / S3）。 |

**重放（成功路径 — 无需参考）**：使用返回的头部重新发送原始请求（`<header_name>: <authorization_header>`，或为遗留 v1 组装的 `X-PAYMENT`），期望 `HTTP 200`，并本地解码任何 `PAYMENT-RESPONSE` 头 (`echo '<value>' | base64 -d | jq .`) 以读取 `status` / `transaction` / `amount` / `payer`。向用户显示结算详情；建议后续对话——永远不要暴露内部字段名称或技能 ID。

---

# 路径 B：a2a-pay（基于 paymentId，无 402）

用户明确调用此路径——通过提及 `paymentId` / `a2a_...` 链接，要求“创建支付链接”，或要求检查 a2a 支付状态。

## 路径 B1：确定角色

| 用户说… | 加载 | 角色 |
|---|---|---|
| "创建支付链接" / "生成支付" / `--amount`/`--recipient` | `references/a2a_charge.md` → "卖家 — 创建" | 卖家 |
| 提供 `paymentId` / `a2a_...` 以支付 | `references/a2a_charge.md` → "买家 — 支付" | 买家 |
| 提供 `paymentId` 并询问状态 | `references/a2a_charge.md` → "状态 — 查询" | 任何 |

如果用户只说“我想付款”而没有付款ID——停止并要求用户提供卖家发出的付款ID。不要尝试做任何其他事情。

## 步骤 B2：钱包状态

`create` 和 `pay` 都需要一个活跃的钱包会话。运行 `onchainos wallet status`：

- **已登录** → 继续（加载参考并遵循它）。
- **未登录** → 要求用户通过 `onchainos wallet login` 登录。**在没有活跃会话的情况下不要签名。**

## 步骤 B3：转交至 `references/a2a_charge.md`

参考包含完整的创建/付款/状态流程（包括自动轮询和信任委托说明）。买方信任被委托到上游——买方签署服务器上挑战声明的任何内容。

---

# 跨领域

## 读取卖家错误 (`WWW-Authenticate: Payment` / a2a-pay)

当卖家拒绝时，不要显示原始 JSON 或仅显示数字代码。优先提取人类可读的解释，使用第一个非空匹配：

1. `body.reason` (mppx, OKX TS 会话)
2. `body.detail` (RFC 9457 ProblemDetails)
3. `body.message`
4. `body.msg` (OKX SA API)
5. `body.error`
6. `body.title` (RFC 9457 简短标题——仅作为后备)
7. 转接——格式化整个 body 并添加 HTTP 状态

格式：

> 卖家拒绝：`<原因文本>`（代码 `<如果存在>`, HTTP `<状态>`）

## 金额显示

所有面向用户的金额在人类和原子形式中：`<人类> (<原子>)`，例如 `0.0004 USDC (400)`。小数表 + 未知符号后备 → `_shared/amount-display.md`。

## 建议下一步操作

在成功付款 + 响应后，建议对话式地：

| 已完成 | 建议 |
|---|---|
| `payment quote` 返回 `needsConfirm:true` | 确认一次：在足够时使用 `AskUserQuestion`，或在不足时使用自适应 QR 富集确认（`image-notify` PNG / `terminal-unicode`）；然后 `payment pay --payment-id <id> --selected-index <n> --yes` |
| `payment quote` 返回 `data.mcpTools[]` (MCP-传输，没有 `paymentId`) | 根据用户意图选择一个工具，然后 `payment quote <url> --tool <name> --param k=v …` 触发 402（见 `references/a2mcp-mcp.md`） |
| `payment pay` 返回 `status:"success"` | 报告 `txHash`；如果存在 `PAYMENT-RESPONSE` 头，`payment decode-receipt --header <b64>` |
| `payment pay` 返回 `status:"pending"` | `payment a2a-pay status --payment-id <id> --wait`（a2a）或等待促进者回调 |
| 成功的 HTTP 402 重放 | 通过 `okx-agentic-wallet` 检查余额影响；或向同一资源发起另一个请求 |
| 成功的 a2a 付款 | 通过 `okx-agentic-wallet` 验证付款后余额 |
| 重放时 402（过期） | 使用新的签名重试 |
| 会话进行中 | 当下一个请求到达时再发一张凭证；完成时关闭通道 |
