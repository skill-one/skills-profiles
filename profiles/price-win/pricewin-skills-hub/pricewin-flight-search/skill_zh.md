需要 `pricewin` MCP 服务器。此技能自身不发出任何网络调用。

## 设置（每台机器只需执行一次）

如果没有注册 MCP 服务器，此技能将处于无效状态——它会提示你调用
`search_flights_live`，但该工具不存在。`skills add` 仅复制文件，因此请运行：

```bash
bash install.sh          # 首先添加 --dry-run 以查看它将进行哪些更改
```

它会将托管服务器（`https://mcp.price.win/mcp`，Streamable HTTP，无需凭证）注册到它找到的每个代理——Claude Code、Cursor、Windsurf、Gemini CLI、VS Code、Codex——在触摸任何文件之前会先创建 `.bak` 文件，并跳过它无法解析的配置。重新运行它不会改变任何内容。**之后需要重启代理。**

# 实时航班搜索

**MCP 服务器：** `pricewin`。工具 `search_flights_live` 会启动异步爬取 Agoda、Trip.com 和 Traveloka；`poll_flight_results` 返回合并后的、按航班最低价的票价。

## 关键：仅限 IATA 代码

两个机场都必须是 3 个字母的 IATA 代码。**此服务器上没有机场查询工具**——请自行解析城市：`Sài Gòn / TP.HCM → SGN`，`Hà Nội → HAN`，`Đà Nẵng → DAD`，`Bangkok → BKK`（主要国际），`Tokyo → NRT 或 HND`，`Seoul → ICN`。

当一个城市有多个机场而用户没有说明时，**问一个简短的问题**——永远不要默默选择。不要编造代码。

## 关键：轮询模式（与酒店搜索不同）

`search_flights_live` 会立即返回带有 `sessionId` 和零个航班的响应。

1. 使用出发地、目的地、出发日期（YYYY-MM-DD），以及仅适用于往返票的 `returnDate` 调用 `search_flights_live`。根据需要添加 `adults`、`cabin`、`language="vi"`。
2. 调用 `poll_flight_results(sessionId)`。**此工具内部会阻塞长达 ~30 秒**，并在第一个票价到达时立即返回——调用它之前**不要休眠**。
3. `status` 是 `pending` | `searching` | `completed` | `failed`。如果它返回 `searching` 且航班很少或没有，**再次调用——最多再调用 4 次**。
4. 一旦航班到达就立即呈现结果；如果用户想要更多，则继续轮询。

会话在最后一次轮询后 **15 分钟** 过期。之后，开始新的搜索——旧的 `sessionId` 已失效。

> `poll_flight_results` 已注册为对航班小部件可见的应用程序可见。如果你的主机没有将其暴露给模型，让小部件进行轮询，不要编造票价。

## 关键：`price` 是总费用，单位为美元

`price` 是所有 `adults` 的**总费用**——不是按人计算，也不是两段航班的总和。自己除以 `adults` 以获得按人计算的金额。

`currency` 是 **`"USD"`**。不要转换它。只有在实时汇率不可用时才会回退到 `"VND"`——所以**读取 `currency` 并用它标记金额**，而不是假设是其中之一。

## 响应格式（必须完全遵循）

仅呈现每段航班的 TOP 5-7 个航班。对于每个航班：

```
✈️ *<airline> <flightNumber>*  ← 使用 Markdown 粗体
🕐 <dep.time> <origin> → <arr.time> <destination> · <Xh Ym> · <直飞 | N 个中转点>
💰 $<price> 总费用为 <adults> 位乘客 (~$<price/adults>/人)
🔗 <bookingUrl>
```

航班之间换行，不要使用项目符号。**最便宜的航班会获得 🏆。** `duration` 以**分钟**为单位——格式化为 `2h 10m`。当 `arrival.date` 与 `departure.date` 不同时，标记为夜间到达。

## 往返票

`outboundFlights` 和 `returnFlights` 是**两个独立的单程搜索**。在单独的标题下列出它们。你可以声明合并估算，例如
`最低价单程 + 最低价返程`，但将其标记为**两个单独的单程票**——这不是一个报价的往返票价，且两段航程是分开预订的。

## 预订 URL —— 使用原文

`bookingUrl` 是最便宜代理的深度链接，其中已包含日期和乘客信息。**永远不要追加、重写或构造参数**（与酒店技能不同）。`bookingUrl` 精确为
`https://www.price.win/` 表示没有捕获代理深度链接——建议在提供商网站上重新检查票价，而不是将其呈现为点击预订链接。

仅从 URL 主机（`agoda.com`、`trip.com`、`traveloka.com`）归因来源——结果没有显式的来源字段，所以不要猜测一个。

## 看起来有用但实际上没有的字段

- `stopCities` — 总是空的；仅按数量描述中转点
- `departure.city` / `arrival.city` — 重复 IATA 代码，而不是真实城市名称
- `legs` — 在列表结果中通常不存在；不要承诺分段分解

## 排序

按 `price` 排序。按价格从低到高，但当非直飞或更短时间的选项只略贵时，会优先显示——用一句话说明，而不是默默重新排序。

## 安全与数据处理

没有运行时代码和自身网络调用；唯一可执行的是
`install.sh`，它将一个 MCP 条目（`pricewin` → `https://mcp.price.win/mcp`）添加到用户已有的代理配置中，首先备份每个文件并跳过任何它无法解析的文件。它不会下载或执行任何内容。唯一发送的数据是路线查询（IATA 代码、日期、乘客、舱位）——没有乘客姓名，没有个人身份信息（PII），没有凭证。仅用于比较：此技能无法预订或付款。完整披露在 [`SECURITY.md`](./SECURITY.md)。
