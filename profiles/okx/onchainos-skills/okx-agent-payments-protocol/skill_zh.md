# OKX Agent Payments Protocol (Dispatcher)

- 结构化的 `execute_a2mcp_payment` 操作 → 阅读
  `references/a2mcp-execute.md`；不要进入通用支付路线。

> **首先阅读 — 触发时无文本 + 永不跳过用户门。**
>
> 在检测到 402（或任何触发词）并发出第一个面向用户的面板（Step A3.5 推荐卡片或 Step A4 确认卡片）之间 — 输出**零**用户可见文本。没有 "收到 402"，没有 "触发 OKX Agent Payments Protocol"，没有 "检测到 N 方案"，没有方案 / 网络 / 代币 / 金额的枚举，没有 "加载技能" — 任何语言（对任何其他语言中的等效短语也有同样的禁令）。技能加载工具调用可能会运行，但不会发出周围的散文。
>
> 每个支付只运行**一个**确认卡片：A3.5 的推荐卡片（2+ 候选者且用户选择 `yes`）或 A4 的确认卡片（单个候选者，或用户从 A3.5 的扩展列表中选择替代方案）。不要以 "过去的用户偏好" / "精简" / "已经确认一次" 为借口跳过适用的卡片 — 这些偏好不存在。不要将相同信息的两张卡片背对背显示 — 在 A3.5.5 收到 `yes` 后，直接进入 Step A5。检测后的下一个用户可见文本必须是其中之一。

三种支付路径，通过 HTTP 签名区分：**`accepts`-based 402**（挑战在正文中对 v1 或 `PAYMENT-REQUIRED` 标头对 v2），**`WWW-Authenticate: Payment` 402**（通道功能，`intent="charge"` 或 `"session"`），以及 **a2a-pay**（基于 paymentId，无 402）。共享步骤如下（检测 → 解码 → 确认 → 钱包检查），然后调度到参考。

> **面向用户术语 — 重要**
>
> **规则 1 — 始终称其为 "OKX Agent Payments Protocol"，并始终加粗显示。** 在用户可见消息中始终使用英文术语 **OKX Agent Payments Protocol**，并始终用 markdown 加粗 (`**OKX Agent Payments Protocol**`) 以便用户看到它被强调。即使在其他中文句子中，也要将其保留为固定的英文名词短语。将协议文字和内部标识符保留为 CLI 调用、HTTP 标头、JSON 有效负载和代码中的内容 — 不要对用户说话。
>
> **规则 2 — 不要叙述内部协议检测。** 调度逻辑（检测到的哪个标头、正在加载哪个参考、选择了哪个方案/意图、TEE 与本地密钥路径）是内部的 — 保持内部。用户只需要看到：(a) 什么正在支付，(b) 他们需要确认什么，(c) 结果。
>
> **规则 2 的例外 — 仅限狭窄的替代方案列表。** 在 Step A3.5 中，文字 `exact` / `aggr_deferred` / `charge` 仅在扩展的 **替代方案列表**（用户选择 "显示其他" 后显示的列表）中暴露给用户 **仅此**，因为此时用户正在明确选择方案。它们绝不能出现在：(默认推荐卡片、"N 其他方法" 摘要行、状态叙述、错误显示、支付后摘要或任何其他地方。推荐卡片仅显示网络 / 代币 / 金额 / 收款人 — 绝不显示方案名称。
>
> **规则 3 — 外部定义的协议文字保持字节精确。** JSON 字段 `x402Version`、HTTP 标头 `X-PAYMENT` / `PAYMENT-SIGNATURE` / `PAYMENT-REQUIRED` / `WWW-Authenticate: Payment`、参考 URL `https://x402.org` 必须在任何协议/服务器要求它们的地方原样出现 — 这些是外部定义的，更改它们会破坏互操作性。CLI 子命令名称 (`onchainos payment pay` / `pay-local` / `charge` / `session ...` / `a2a-pay ...`) 是该 CLI 自己的表面，可以发展；在 CLI 调用和代码中引用它们当前的名称，但永远不要对用户说话（规则 2）。
>
> **示例**
>
> (EN) `正在通过 **OKX Agent Payments Protocol** 准备支付。以下是收费详情 — 请在继续之前确认…`
> 当用其他语言叙述时，翻译这一引导行，但保留 **OKX Agent Payments Protocol** 为加粗的英文名词短语。

> **进度叙述计为用户可见 — 规则 1-3 仍然适用。**
>
> 长时间流程（解码 → 确认 → 钱包检查 → 签名 → 重放）诱使用户状态更新。每条进度行 ("我现在…" 或其中文等效) 都是用户可见的；步骤标签和参考/方案名称是内部的 — 不要重复它们。锚点：
>
> | 不要说 | 说 |
> |---|---|
> | "检测到 HTTP 402，触发 OKX Agent Payments Protocol" / "检测到 `PAYMENT-REQUIRED`，加载 `exact`" | _(静默 — 检测 / 路由是内部的)_ |
> | "CLI 选择 `exact`，组装 `PAYMENT-SIGNATURE` 标头" / "采取 TEE 路径" | "签名完成，重放请求" |
> | "检测到 2 个方案：exact (USD₮0), aggr_deferred (USDG)" / "检查余额以过滤候选者" | _(静默 — 枚举 + 余额检查是内部的；仅推荐卡片是用户可见的)_ |
> | "进入会话 / 收费模式" | "通道已打开" — 描述用户可见的效果，而不是内部模式 |
> | "根据过去的偏好，无需重新确认即可支付" | _(禁止 — 没有这样的偏好；每次都必须强制执行门)_ |

> 相同的规则适用于使用任何其他语言叙述时 — 不要只是匹配这些 "不要说" / "说" 示例的意图，而不仅仅是英文措辞。
>
> **这些规则是权威的，始终生效** — 当不确定状态行是否泄漏内部信息时，请与上面的行进行匹配，并默认为静默。

## 触发器（完整列表）

- **EN**: `402`, 支付需要, `x402`, `x402Version`, `X-PAYMENT`, `PAYMENT-REQUIRED`, `PAYMENT-SIGNATURE`, `WWW-Authenticate: Payment`, `permit2`, `upto`, 计量计费, 打开 / 关闭 / 充值 / 结算通道, 优惠券, 会话支付, `channelId`, `channel_id`, `paymentId`, `a2a_`, 创建支付链接, 支付链接, 支付状态
- 订阅 / 订阅 / 重复支付 / 重复收费 / "每月支付" / 取消订阅 / 升级计划 / 降级计划 → `period` 方案（见 `references/subscription.md`）
  - **例外**: 当消息包含 jobId / subId / ASP / 提供商 / 试用期 / 续订 / 交付 / periodCount / 订阅任务时，它是 Agent Commerce 订阅任务（每月服务协议）；路由到 `okx-ai` 而不是。
- 相同的触发词汇表适用于任何其他语言的等效词（例如，中文订阅 / 重复计费术语以相同的方式路由到 `period` 方案）。
- 例外：来自代理市场的 AI 服务/ASP 订阅（上下文：ASP / Agent#N / 任务 / 试用期 / 服务方; NO 402 提供的 / 资源 URL / paymentId）属于 okx-ai（onchainos agent my-subscriptions / subscribe-detail），不是 `period` 方案。对于没有信号、资源 URL 或 paymentId 的简单 "我的订阅 / 我的订阅" 的情况，请询问用户一次，而不是假设 `period`。

任何靠近 `channel_id` 或会话上下文的关闭 / 充值 / 结算 / 优惠券 / 退款 = MPP 会话操作 → `references/session.md`。

## 预检

预检检查：在每个线程开始时，完成 `../okx-agentic-wallet/_shared/preflight.md` 中的检查。如果缺失，请阅读 `_shared/preflight.md`。

## 命令路由 & 参考映射

每个 402 信号（或 paymentId）→ CLI 命令 → 参考。详细的门控 + 解码/确认步骤在下面的 Path A / Path B 中。

| 信号 | 命令 | 参考 |
|---|---|---|
| 402 + `PAYMENT-REQUIRED` (v2) / 正文 `x402Version` (v1) — 一个 **或多个** `accepts[]` 方案 (`exact` / `exact`+Permit2 / `upto` / `aggr_deferred`) | **主要 — Path A:** `payment quote <url>` → 确认 → `payment pay --payment-id --yes`. 单方案和多方案采用 **相同的** 引导流程（CLI 解码、转换、余额检查、签名、**重放**，并返回收据）。即使你已经 curl 了原始 402，也请通过 `payment quote <url>` 重新输入 — 永远不要手动组装标头，也永远不要直接跳转到仅签名。**兼容仅:** `payment pay --payload [--selected-index]`（仅签名 + 手动重放）当 `quote` 不可用时。 | 成功路径加载 **无** 参考。`references/accepts-schemes.md` 仅用于：支付后方案特定的收据阅读、`Permit2 允许不足` 一次性批准、`pay-local`、`pay --payload` 兼容路径或遗留 x402 v1（CLI 输出字段告诉您哪个方案 — `permit2Authorization` = `upto` / `exact`+Permit2, `sessionCert` = `aggr_deferred`, `authorization` = `exact`) |
| 402 提供包含 `accepts[]` 条目的报价，其 `scheme == "period"`（又名 `permit2_subscription`） — 重复/订阅计费 | `payment subscription subscribe/access/change/cancel/cancel-pending/my-subscriptions/allowance-status` | `references/subscription.md` |
| 402 + `WWW-Authenticate: Payment`, `intent="charge"` | `payment charge --challenge` | `references/charge.md` |
| 402 + `WWW-Authenticate: Payment`, `intent="session"`（或会话中的 `channel_id`） | `payment session open/voucher/topup/close` | `references/session.md` |
| paymentId / `a2a_…` 链接 / 创建或检查支付链接 | `payment a2a-pay create/pay/status` | `references/a2a_charge.md` |
| A2MCP / 402 端点 URL, "支付此端点", 条目 A/B 支付节点 | `payment quote <url> [--param k=v ...] [--method GET \| POST \| ...]` | (内联 — Path A) |
| A2MCP **MCP-transport** 端点（URL 以 `/mcp` 或 `/sse` 结尾，返回 `text/event-stream` / JSON-RPC，或您有一个工具名称） | `payment quote <url>`（发现 → `mcpTools[]`）→ `payment quote <url> --tool <name> --param k=v`（触发 402）→ `payment pay --payment-id <id> --yes` | `references/a2mcp-mcp.md` |
| 用户确认了引用的支付（货币/金额/方案选择） | `payment pay --payment-id <id> [--selected-index <n>] --yes` | (内联 — Path A) |
| 需要解码 `PAYMENT-RESPONSE` 标头或收费收据 | `payment decode-receipt (--header <b64> \| --receipt <json>)` | (内联 — 只读) |

> **在成功路径上不要加载参考。** 在主要 Path A 流程中，`onchainos payment pay --payment-id --yes` 直接签名、重放并返回结算收据 — 完全跳过 `references/accepts-schemes.md`（对于单个 `accepts[]` 方案与多方案完全相同）。在兼容的 `pay --payload` 路径中，CLI 返回 `authorization_header`，您需要自行重放 — 相同的规则，成功路径上没有参考。仅在失败 / 遗留路径上加载 `references/accepts-schemes.md`：`Permit2 允许不足` → `references/accepts-schemes.md`（一次性批准），或遗留 x402 v1 原始证明 → 其 "遗留: x402 v1" 部分。`charge` / `session` / `a2a_charge` 始终加载 — 这些是多阶段流程。

> **重放（成功路径 — 无需参考）:** 重新发送原始请求，带有返回的标头 (`<header_name>: <authorization_header>`, 或遗留 v1 的 `X-PAYMENT` 您组装的)，期望 `HTTP 200`，并本地解码任何 `PAYMENT-RESPONSE` 标头 (`echo '<value>' | base64 -d | jq .`) 以读取 `status` / `transaction` / `amount` / `payer`。向用户展示结算详情；建议非正式地继续对话 — 永远不要暴露内部字段名称或技能 ID。

---

# Path B: a2a-pay（基于 paymentId，无 402）

用户明确调用此路径 — 通过提及 `paymentId` / `a2a_...` 链接，要求 "创建支付链接"，或要求检查 a2a 支付状态。

## Step B1: 确定角色

| 用户说… | 加载 | 角色 |
|---|---|---|
| "创建支付链接" / "生成支付" / `--amount`/`--recipient` | `references/a2a_charge.md` → "卖家 — 创建" | 卖家 |
| 提供 `paymentId` / `a2a_` 以支付 | `references/a2a_charge.md` → "买家 — 支付" | 买家 |
| 提供 `paymentId` 并询问状态 | `references/a2a_charge.md` → "状态 — 查询" | 任何一方 |

如果用户只说 "我想支付" 而没有 paymentId — 停止并要求用户提供卖家发布的 paymentId。不要尝试做任何其他事情。

## Step B2: 钱包状态

`create` 和 `pay` 都需要一个活动的钱包会话。运行 `onchainos wallet status`：

- **登录** → 继续（加载参考并遵循它）。
- **未登录** → 要求用户通过 `onchainos wallet login` 登录。**不要在没有活动会话的情况下签名。**

## Step B3: 转发到 `references/a2a_charge.md`

参考包含完整的创建/支付/状态流程（包括自动轮询和信任委托说明）。买方侧信任委托到上游 — 买方签署服务器挑战声明的内容。

---

# 跨越

## 读取卖家错误 (`WWW-Authenticate: Payment` / a2a-pay)

当卖家拒绝时，不要显示原始 JSON 或仅显示数字代码。提取优先级顺序中的可读解释，使用第一个非空匹配项：

1. `body.reason` (mppx, OKX TS Session)
2. `body.detail` (RFC 9457 ProblemDetails)
3. `body.message`
4. `body.msg` (OKX SA API)
5. `body.error`
6. `body.title` (RFC 9457 短标题 — 仅作为后备)
7. 溢出 — 格式化整个正文并添加 HTTP 状态

格式：

> 卖家拒绝：`<reason text>` (代码 `<code if present>`, HTTP `<status>`)

## 金额显示

所有用户可见的金额在两者（人类和原子形式）中：`<human> (<atomic>)`, 例如 `0.0004 USDC (400)`。小数表 + 未知符号后备 → `_shared/amount-display.md`。

## 建议下一步

在成功的支付 + 响应之后，非正式地建议：

| 刚刚完成 | 建议 |
|---|---|
| `payment quote` 返回 `needsConfirm:true` | 确认一次：使用 `AskUserQuestion` 当足够时，或使用自适应 QR 富化确认卡片 (`image-notify` PNG / `terminal-unicode`) 当不足时；然后 `payment pay --payment-id <id> --selected-index <n> --yes` |
| `payment quote` 返回 `data.mcpTools[]`（MCP-transport，无 `paymentId`） | 根据用户的意图选择一个工具，然后 `payment quote <url> --tool <name> --param k=v …` 触发 402（见 `references/a2mcp-mcp.md`） |
| `payment pay` 返回 `status:"success"` | 报告 `txHash`；如果存在 `PAYMENT-RESPONSE` 标头，则 `payment decode-receipt --header <b64>` |
| `payment pay` 返回 `status:"pending"` | `payment a2a-pay status --payment-id <id> --wait` (a2a) 或等待促进者回调 |
| 成功的 HTTP 402 重放 | 通过 `okx-agentic-wallet` 检查余额影响；或者对相同资源发出另一个请求 |
| 成功的 a2a 支付 | 通过 `okx-agentic-wallet` 验证支付后余额 |
| 402 在重放时过期 | 使用新的签名重试 |
| 会话中的通道进行中 | 在下一个请求到达时发出另一个凭证；完成时关闭通道 |
