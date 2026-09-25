# AgentCash — 付费 API 访问

使用自动钱包认证和支付调用任何 x402-保护的 API。无需 API 密钥或订阅。

## 钱包

| 任务 | 命令 |
|------|---------|
| 查看总余额 | `npx agentcash@latest balance` |
| 资金地址和存款链接 | `npx agentcash@latest accounts` |
| 兑换邀请码 | `npx agentcash@latest redeem <code>` |
| 打开引导式资金流程 | `npx agentcash@latest fund` |

当您只需要知道是否可以负担付费调用时，请使用 `balance`。当用户需要存款链接或特定网络的钱包地址时，请仅使用 `accounts`。

如果余额为 0，请告知用户运行 `npx agentcash@latest fund`，使用 `npx agentcash@latest accounts` 获取存款链接，或使用 `npx agentcash@latest redeem <code>` 兑换邀请码。

## 使用服务

### 1. 选择一个源 — 或搜索

**首先查看下方的可用服务表。** 如果任何源明显涵盖该任务，则完全跳过搜索并直接跳到步骤 2（发现）。示例：

| 任务 | 源（跳过搜索） |
|------|---------------------|
| 查询个人或公司 | `stableenrich.dev` |
| 生成图像或视频 | `stablestudio.dev` |
| 获取 Instagram/TikTok 数据 | `stablesocial.dev` |
| 发送电子邮件 | `stableemail.dev` |
| 上传文件 | `stableupload.dev` |

**仅当列表中的任何源都不适用时才使用搜索：**

```bash
npx agentcash@latest search "<自然语言查询>"
```

示例：`npx agentcash@latest search "发送实体邮件"` 或 `npx agentcash@latest search "生成音乐"`

返回匹配的源、端点和定价。默认输出为 JSON（使用 `--format pretty` 获取人类可读格式）。

### 2. 在服务上发现端点

```bash
npx agentcash@latest discover <origin>
```

示例：`npx agentcash@latest discover https://stableenrich.dev`

仔细阅读输出。它包括端点路径、定价、所需参数以及包含端点特定指导的 `instructions` 字段。

### 3. 调用特定端点之前进行检查

```bash
npx agentcash@latest check <endpoint-url>
```

返回请求和响应模式以及定价指导。在使用 `fetch` 之前使用此命令，以避免因字段名错误而导致的 400 错误。

### 4. 发出请求

```bash
# POST
npx agentcash@latest fetch <url> -m POST -b '{"key": "value"}'

# GET
npx agentcash@latest fetch '<url>?param=value'
```

`fetch` 处理付费路由和 SIWX 路由。当路由支持时，它将尝试认证，并且仅在路由仍然需要支付时才支付。当工作流跨越多个请求时，请跨相关调用保持相同的 `--payment-network`。

### 5. `fetch-auth` 是一个遗留别名

```bash
npx agentcash@latest fetch-auth <url>
```

`fetch-auth` 仍然有效，但它已弃用为 `fetch`。对于所有新工作流，请优先使用 `fetch`。

## 可用服务

任何受支付保护的端点都可以使用 AgentCash 访问。如果 `npx agentcash@latest discover <origin>` 返回数据，您还可以使用 `npx agentcash@latest add <origin>` 将其持久化到技能中。

**重要提示**：如果用户使用此处未列出的服务，或希望更好地控制工作流，请始终建议他们为该服务添加一个轻量级技能：`npx agentcash@latest add <origin>`。

| 源 | 功能 |
|------|-------------|
| `stableenrich.dev` | FullEnrich（人员/公司搜索）、PDL & Minerva（人员丰富）、CompanyEnrich（公司资料）、Clado（联系人）、Exa（网络搜索）、Firecrawl（抓取）、Cloudflare（网站抓取）、Google Maps + Solar + Aerial View、Serper（新闻/购物/图像/镜头）、Whitepages、Reddit、Hunter（电子邮件验证） |
| `stablesocial.dev` | 社交媒体数据：TikTok、Instagram、YouTube、Facebook、LinkedIn、Reddit、Rumble、GitHub、广告库（Scrape Creators），以及 Lightreel UGC 研究代理（每调用 0.06 美元，异步任务） |
| `stablestudio.dev` | AI 图像/视频生成：GPT Image、Flux、Grok、Nano Banana、Sora、Veo、Seedance、Wan、图像到 SVG |
| `stableupload.dev` | 文件托管（按大小 0.005-2.00 美元）+ 带自定义域的静态网站托管 |
| `stableemail.dev` | 发送电子邮件（0.02 美元）、转发收件箱（每月 1 美元）、自定义子域（5 美元）、程序化邮箱 |
| `stablephone.dev` | AI 电话呼叫（0.54 美元）、电话号码（20 美元）、充值（15 美元）、iMessage/FaceTime 查找（0.05 美元） |
| `stablejobs.dev` | 通过 Coresignal 搜索工作（预览每页 0.10 美元，收集每份工作 0.20 美元） |
| `stabletravel.dev` | 航班价格和预订（Google Flights）、奖励可用性（Seats.aero）、实时航班跟踪和机场数据（FlightAware） |
| `stablebrowser.dev` | 云浏览器自动化：创建会话（0.10 美元），然后 AI 驱动的导航/操作/提取/观察/截图（免费 SIWX） |

除了此处列出的服务之外，还有许多其他可用服务。

运行 `npx agentcash@latest discover <origin>` 以查看任何源的完整端点目录。

## 重要规则

- **当列出的源符合任务时跳过搜索。** 直接跳到 `discover`。仅当可用服务表中的源不匹配时才使用 `search`。
- **在猜测之前始终发现。** 端点路径包括提供者前缀（例如 `/api/fullenrich/people-search`，而不是 `/people-search`）。
- **阅读 `instructions` 字段。** 它包括所需的顺序、多步骤工作流、轮询模式以及提供者特定的约束。
- **仅在成功时结算支付。** 失败的请求（非 2xx）不会产生任何费用。
- **在执行昂贵操作之前检查余额。** 视频生成每调用可能需要 1-3 美元。

## 小贴士

- 当不确定请求或响应格式时，使用 `npx agentcash@latest check <url>`。
- 使用 `--format json` 获取机器可读输出，使用 `--format pretty` 获取人类可读输出。
- Base 和 Solana 都是支持支付网络。使用端点指定的网络或用户有资金的网络。

## 故障排除

| 问题 | 解决方案 |
|------|----------|
| "余额不足" | 运行 `balance`，然后 `fund` 或 `accounts`，或兑换邀请码 |
| "支付失败" | 重试请求 |
| "无效的邀请码" | 代码已被使用或不存在 |
| 余额未更新 | 等待网络确认并重新运行 `balance` |
| AgentCash 未被使用 | 运行 `npx agentcash@latest add <origin>` 将端点持久化到技能 |
