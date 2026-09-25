需要 `pricewin` MCP 服务器。处理真实货币：它创建预订和支付链接。使用前请阅读下方的确认规则。

# 预订助手

**MCP 服务器：** `pricewin`。协调发现 → 详情 → 推荐 → **预订 → 支付 → 管理**。

## 实际可预订的内容

| 来源 | 这里可以预订吗？ |
|---|---|
| `source: "OPENTRAVEL_DIRECT"`（包含 `propertyId`） | ✅ **是** — 通过 `create_booking` 进行完整预订和支付 |
| Booking.com / Agoda / Traveloka | ❌ 否 — 仅限比较。将用户的 OTA `url` 交给用户 |

只有 OpenTravel 直接的物业会提供 `propertyId` + `roomTypeId`，这是 `create_booking` 所需的。切勿暗示通过此技能可以预订 OTA 酒店。

## 推荐流程

1. **发现** — `search_hotels_live(city, checkIn, checkOut, adults, …)` → `sessionId`，然后每 5 秒轮询 `poll_search_results(sessionId, nights)`，直到 `status` 为 `pending`/`partial`（最多 18 次/90 秒）
2. **评分** — `rating × log(reviewCount + 1)` — 平衡质量与可信度。强候选者：`rating ≥ 8.0` 且 `reviewCount ≥ 100`
3. **排序** — 评分前 3–5 名
4. **详情** — 对 OpenTravel 挑选的酒店调用 `get_hotel_detail(propertyId, checkIn, checkOut, adults)`；对命名的 OTA 酒店调用 `get_ota_hotel_detail(hotelName, city, checkIn, checkOut, queryText)`（约 20–60 秒）
5. **推荐** — 根据客人容量过滤房间，然后选择最佳性价比

## 预订链接规则（OTA 酒店）

- **绝不编造 URL** — 只能使用工具返回的 `url`
- 始终在链接旁边标明 OTA 名称；如果多个 OTA 提供相同房间，显示所有带价格
- 将用户的日期附加到原始 URL — 参见 [`pricewin-hotel-search`](../pricewin-hotel-search/SKILL.md)

## 预订流程（OpenTravel 直接）

### 1. 首先获取房间 — 强制性

在预订前调用 `get_hotel_detail` 以获取 `roomTypeId`、总价和货币。不要猜测任何一项。

可选地调用 `get_cancellation_policy(propertyId, ratePlanId, checkInDate)` 并在收款前显示退款条款。

### 2. 一次性请求所有四项信息

在您**首次**请求客人信息时，**一次性**请求所有这些信息 — 不要跨回合拆分，并始终使用用户的语言：

1. 全名
2. 电话号码
3. **电子邮件** — 确认邮件将发送至此
4. 支付方式

⚠️ **切勿自动填充电子邮件** 来自账户/个人资料。客人通常不是账户所有者。必须来自用户在此聊天中输入的内容。如果缺失，请询问。

将三种支付方式作为**平等选择、无默认值、无推荐顺序**呈现：

- 通过 QR 码银行转账（SePay）→ `SEPAY`
- 通过 Polar 国际卡 → `POLAR`
- PayPal → `PAYPAL`

如果用户已经表明了偏好，**推断并跳过重新询问**：

| 他们说 | 方式 |
|---|---|
| "扫描 QR", "quét mã", "转账", "bank transfer", "VietQR" | `SEPAY` |
| "卡", "thẻ", "信用卡/借记卡", "visa", "mastercard" | `POLAR` |
| "PayPal" | `PAYPAL` |

如果他们的回复后仍有缺失项，再次询问仅缺失项。

### 3. 确认后再扣款

**总结回所有内容** — 酒店、房间类型、入住/退房日期、客人、**总价**（全额，非押金）、客人姓名、**电子邮件地址**（强调 — 拼写错误意味着确认邮件不会到达）、电话、支付方式 — 然后明确询问用户所有内容是否正确。

### 4. 然后才调用 `create_booking`

必需：`propertyId`、`roomTypeId`、`checkIn`、`checkOut`、`adults`、`guestName`、`guestPhone`、`guestEmail`、`paymentMethod`、`totalAmount`、`currency`。
同时传递 `queryText`（用户的原始文本，逐字）。

返回支付链接和 `confirmationCode`（例如 `K7X9M2P4`） — 同时展示。

## 预订后

| 用户说 | 工具 |
|---|---|
| "我已付款" / "查看我的预订" | `check_booking_status(confirmationCode)` |
| "支付链接过期了" | `recreate_payment_link(confirmationCode)` |
| "取消我的预订" | `request_cancel_token` → 然后 `cancel_booking` |

🚨 **切勿对同一住宿调用两次 `create_booking`。** 过期的支付链接通过 `recreate_payment_link` 修复 — 它重用相同的确认码。再次调用 `create_booking` 会创建**重复预订**和重复的确认邮件。

### 取消 — 设计为两步

1. `request_cancel_token(confirmationCode, guestEmail)` — 邮件必须与预订的主要客人匹配。这将向客人发送一个魔法链接
2. 客人将令牌粘贴回来 → `cancel_booking(confirmationCode, cancelToken, reason)` (`reason` ≥ 3 个字符)

没有客人从他们的收件箱获取该令牌，您无法取消。告诉他们检查电子邮件，而不是重试步骤 1。

## 输出格式

```
### 酒店名称 ★★★★☆
- 评分：8.5/10（1,234 条评论）
- 最佳房间：豪华双人间 — $85/晚
- 免费取消：至 2026-08-10
- 预订：[立即预订](payment-link)          ← OpenTravel 直接
- 或比较：[Agoda](url) | [Booking.com](url)
```

工具输入和响应字段：[reference.md](reference.md)。

## 安全与数据处理

此技能具有**真实交易权限**，并将**客人 PII**（姓名、电话、电子邮件）传输到 PriceWin 的托管 MCP 服务器 `https://mcp.price.win/mcp` — 这是预订的固有属性，这也是为什么预订是一个独立的技能而非搜索。它不发送任何代码，也不进行自己的网络调用。

**卡号、CVV 和银行凭证绝不会通过技能或代理传递** — `create_booking` 返回一个支付 *链接*，用户在提供商自己的页面上付款。切勿索要卡详细信息；如果提供，请拒绝。

在每次 `create_booking` 之前，与用户确认**完整摘要和总价**。完整披露 — 操作员、确切 PII 字段按工具、支付边界、取消模式 — 在 [`SECURITY.md`](./SECURITY.md)。
