需要 `pricewin` MCP 服务器。此技能自身不发出任何网络调用。

# 价格比较

**MCP 服务器：** `pricewin`。比较 **Booking.com、Agoda、Traveloka**（爬取）加上 **OpenTravel**（直接 API）的实时汇率。

比较是在返回的源上进行操作——没有服务器端的比较调用。根据用户提供的输入选择入口点：

| 用户提供了 | 工具 |
|---|---|
| 一个**城市**——"比较岘港的酒店价格" | `search_hotels_live` → `poll_search_results` |
| 一个**已命名的酒店**——"Mercure Danang 在 Agoda 或 Booking 上是否更便宜？" | `get_ota_hotel_detail` |
| 一个已知是 **OpenTravel 直接**的酒店（`source: "OPENTRAVEL_DIRECT"`，有 `propertyId`） | `get_hotel_detail` |

## 全城比较

`search_hotels_live` 会立即返回一个 `sessionId`——它**不**返回酒店。

1. `search_hotels_live` — 必要：`city`、`checkIn`、`checkOut`（YYYY-MM-DD）。可选：`adults`（默认 2）、`rooms`、`area`、`hotelName`、`priceMin`、`priceMax`、`language`
2. 等待 5 秒 → `poll_search_results(sessionId, nights)`
3. 当 `status` 为 `pending` 或 `partial`：等待 5 秒并再次轮询——最多 18 次（90 秒）
4. 一旦 `status == "partial"` 就呈现酒店；继续静默轮询并优化

然后针对每个酒店跨其源进行比较。有关完整的去重 + 呈现契约，请参阅 [`pricewin-hotel-search`](../pricewin-hotel-search/SKILL.md)——此处不重复陈述。

## 单个已命名的酒店

`get_ota_hotel_detail` —— 用于用户命名的特定 Booking.com/Agoda 酒店。

- 必要：`checkIn`、`checkOut`。当知道时，传递 `hotelName` + `city` + `queryText`（用户文本的逐字复制）
- **不要为已命名的酒店调用 `search_hotels_live`**——那会返回整个城市的列表
- 实时爬取，**~20–60 秒**。直到实际返回之前，不要提及“加载”
- 加速：如果先前的搜索已经给了你 `prices.booking.url`，将其作为 `propertyUrl` 传递以跳过名称解析
- 如果在负载下返回未找到，重试**一次**

返回该物业的房间、价格、设施、照片、评论。

## OpenTravel 直接物业

`get_hotel_detail` —— 仅用于带有 `source: "OPENTRAVEL_DIRECT"` 的结果。

- 当可用时，传递 `propertyId`（来自 `opentravelResults[].propertyId` 的 UUID）
- `hotelName` + `city` 仅作为**已确认**为 OpenTravel 直接的物业的回退
- 必要：`checkIn`、`checkOut`。可选：`adults`、`children`、`language`
- 返回带有 `roomTypeId` 和 `ratePlanId` 的房间类型——这些是使物业可预订的关键

⚠️ 路由规则：**有 `propertyId` → `get_hotel_detail`。仅名称 → `get_ota_hotel_detail`。**

## 取消条款

仅适用于 OpenTravel 率计划：`get_cancellation_policy(propertyId, ratePlanId, checkInDate)` → 非可退标志、免费取消窗口、退款比例以及计算出的截止日期。

`ratePlanId` 来自 `get_hotel_detail` → `roomTypes[].ratePlanId`。传递 `checkInDate` 或你将不会得到截止日期。OTA 酒店没有结构化政策——引用爬取返回的内容。

## 呈现比较

- **纯粹按价格排序**。没有源会获得优先权，包括 OpenTravel
- 首先显示最便宜的源，然后在其下方显示其他源：
  `Agoda $X · Booking $Y · OpenTravel $Z`
- 与下一个最便宜源的比较：`(next - cheapest) / next * 100` → "节省 Z%"
- 当差距较小时，优先选择免费取消选项并说明原因
- 所有价格以美元计价，除非工具另有说明。不进行转换

工具输入和响应字段：[reference.md](reference.md)。

## 安全与数据处理

仅文档——无代码、无依赖、无自身网络调用。唯一发送的数据是比较查询（城市或酒店名称、日期、客人，加上 `queryText`——用户的逐字消息），到 PriceWin 的托管 MCP 服务器 `https://mcp.price.win/mcp`（无凭证、无账户）。无 PII，并且此技能无法预订或支付任何东西。完整的披露——操作员、后端来源、每个工具的确切字段——在 [`SECURITY.md`](./SECURITY.md)。
