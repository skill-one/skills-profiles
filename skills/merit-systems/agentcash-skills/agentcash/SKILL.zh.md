---
name: agentcash
description: '按调用付费 x402/MPP API（Base、Solana、Tempo 上使用 USDC）。无需 API 密钥——钱包按请求付费。

  如果任务匹配下方列出的 SERVICES 来源，则跳过搜索，直接进入发现 → 获取。

  仅在没有任何列出的来源适用时才进行搜索。


  SERVICES：stableenrich（人员/公司、网络搜索、抓取、地图、领英、邮箱验证、新闻），stablesocial（抖音、Instagram、YouTube、Facebook、Reddit、领英、GitHub），stablestudio（AI 图像/视频），stableupload（文件/网站托管），stableemail（邮箱、收件箱、子域名），stablephone（AI 通话、电话号码），stablejobs（工作），stabletravel（旅行），stablebrowser（浏览器自动化）。

  TRIGGERS：研究、丰富、抓取、网络搜索、生成图像、视频、社交媒体、发送邮件、电话呼叫、旅行、工作、查找联系人、查找 API、x402、mpp、agentcash'
---

# AgentCash — 付费 API 访问

调用任何 x402 或 MPP-保护的 API，享受自动钱包认证和支付功能。无需 API 密钥或订阅。

### 查询余额

```mcp
agentcash.get_balance()
```

返回在所有支持网络中的 USDC 总余额。在付费调用前使用此命令以确认资金充足。

### 兑换邀请码

```mcp
agentcash.redeem_invite(code="YOUR_CODE")
```

每个邀请码仅限一次性使用。积分将即时到账。兑换后运行 `agentcash.get_balance()` 以验证。

### 提款 USDC

1. 调用 `agentcash.list_accounts()` 获取各网络的钱包地址和提款链接
2. 向 **Base 网络** (eip155:8453) 或 **Solana** (solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp) 的对应地址发送 USDC
3. 或打开返回的提款链接以选择网络

**重要提示**：仅限 Base 或 Solana 网络的 USDC。其他网络或代币将被丢失。

## 调用付费 API

### 1. 选择源站 — 或搜索

**首先查看下方的可用服务表。** 如果有源站明确覆盖任务，则跳过搜索直接进入步骤 2（发现）。示例：

| 任务 | 源站 (跳过搜索) |
|------|----------------|
| 查询个人或公司信息 | `stableenrich.dev` |
| 生成图像或视频 | `stablestudio.dev` |
| 获取 Instagram/TikTok 数据 | `stablesocial.dev` |
| 发送电子邮件 | `stableemail.dev` |
| 上传文件 | `stableupload.dev` |

**仅当列表中的源站都不适用时使用搜索：**

```mcp
agentcash.search(query="发送实体邮件")
```

返回匹配的源站、端点及定价（通常第一个匹配项包含 schema，可直接调用 **fetch**）。

### 2. 发现端点

```mcp
agentcash.discover_api_endpoints(url="https://stableenrich.dev")
```

返回所有端点、定价和使用说明。**务必阅读 `instructions` 字段** — 它包含关键端点特定指导。

### 3. 检查 schema (可选)

```mcp
agentcash.check_endpoint_schema(url="https://stableenrich.dev/api/fullenrich/people-search")
```

返回特定端点的完整请求/响应 JSON schema 和定价。

### 4. 发起付费请求

```mcp
agentcash.fetch(
  url="https://stableenrich.dev/api/fullenrich/people-search",
  method="POST",
  body={
    "current_company_domains": [{"value": "stripe.com"}],
    "current_position_seniority_level": [{"value": "VP"}]
  }
)
```

支付自动完成：发送请求、接收 402 挑战、签名 USDC 支付、重试请求并返回结果。支付仅在成功（2xx）时结算 — 失败请求不收费。
`agentcash.fetch` 也会自动处理 SIWX 认证端点（当路由支持该流程时）。

## 可用服务

| 源站 | 服务 | 功能 |
|---|---|---|
| `https://stableenrich.dev` | StableEnrich | FullEnrich（人/公司搜索）、PDL & Minerva（人信息增强）、CompanyEnrich（公司资料）、Clado（联系人）、Exa（网络搜索）、Firecrawl（网页抓取）、Cloudflare（网站抓取）、Google Maps + Solar + Aerial View、Serper（新闻/购物/图像/镜头）、Whitepages、Reddit、Hunter（邮箱验证） |
| `https://stableupload.dev` | StableUpload | 文件托管（按大小收费 $0.005-$2.00，基于套餐保留期）+ 带自定义域的静态网站托管 |
| `https://stablestudio.dev` | StableStudio | AI 图像/视频生成：GPT Image、Flux、Grok、Nano Banana、Sora、Veo、Seedance、Wan、图像转 SVG |
| `https://stablesocial.dev` | StableSocial | 社交媒体数据：TikTok、Instagram、YouTube、Facebook、LinkedIn、Reddit、Rumble、GitHub、广告库（Scrape Creators），以及 Lightreel UGC 研究代理。$0.06/次调用，异步任务 |
| `https://stableemail.dev` | StableEmail | 发送电子邮件（$0.02）、转发收件箱（$1/月）、自定义子域名（$5） |
| `https://stablephone.dev` | StablePhone | AI 电话呼叫（$0.54）、电话号码（$20）、充值（$15） |
| `https://stablejobs.dev` | StableJobs | 通过 Coresignal 搜索工作（预览 $0.10/页，收集 $0.20/次） |
| `https://stabletravel.dev` | StableTravel | 航班价格和预订（Google Flights）、奖励可用性（Seats.aero）、实时航班跟踪和机场数据（FlightAware） |
| `https://stablebrowser.dev` | StableBrowser | 云浏览器自动化：创建会话（$0.10），然后 AI 驱动的导航/操作/提取/观察/截图（免费 SIWX） |

在任意源站上运行 `agentcash.discover_api_endpoints(url="<origin>")` 查看其完整端点目录。

## 快速参考

| 任务 | 工具 |
|------|------|
| 查询余额 | `agentcash.get_balance` |
| 获取提款链接和钱包地址 | `agentcash.list_accounts` |
| 兑换代码 | `agentcash.redeem_invite(code="...")` |
| 通过自然语言查找 API | `agentcash.search(query="...")` |
| 发现端点 | `agentcash.discover_api_endpoints(url="...")` |
| 检查定价/schema | `agentcash.check_endpoint_schema(url="...")` |
| 付费 POST 请求 | `agentcash.fetch(url="...", method="POST", body={...})` |
| 付费 GET 请求 | `agentcash.fetch(url="...")` |
| 认证 GET（无需支付） | `agentcash.fetch(url="...")` |

## 小贴士

- **当列表中的源站符合任务时跳过搜索。** 直接使用 `discover_api_endpoints`。仅在可用服务表中没有匹配的源站时使用 `search`。
- 调用任意路径前务必先发现 — `instructions` 字段包含关键端点特定模式和必需参数。
- 支付仅在成功（2xx）时结算 — 失败请求不收费。
- 不确定请求/响应格式时使用 `check_endpoint_schema`。
- 独立的 `agentcash.fetch` 调用可并行运行以提升吞吐量。
- 网络：Base (eip155:8453) 或 Solana (solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp)，货币：USDC。

## 故障排除

| 问题 | 解决方案 |
|-------|----------|
| "MCP 工具未找到" | 重新安装 MCP，重启 IDE |
| "余额不足" | 运行 `agentcash.get_balance()`，然后 `agentcash.list_accounts()` 或兑换邀请码 |
| "支付失败" | 暂时性错误 — 重试请求 |
| "无效的邀请码" | 代码已被使用或不存在 |
| 余额未更新 | 等待 Base 或 Solana 网络确认 (~2 秒) |
