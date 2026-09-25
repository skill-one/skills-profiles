# 帧注册中心

按调用付费的 API 网关，用于 AI 代理。通过 x402 支付协议提供 10 项服务。无需 API 密钥，无需订阅——只需使用加密货币按请求付费。

## 基础 URL

```
https://registry.frames.ag
```

## 前置条件

使用付费端点需要使用 USDC 资金的加密货币钱包。有两种选择：

- **AgentWallet**（推荐用于代理）——服务器端钱包，通过单个 `POST /x402/fetch` 调用自动处理 402 检测、支付签名和重试。无需在您的端管理私钥。
- **自管理钱包**——任何 EVM 钱包（Base）或带有 USDC 的 Solana 钱包。您直接签名 x402 支付标头。

## 快速入门

1. **设置钱包**——创建 [AgentWallet](https://frames.ag/skill.md) 或使用 USDC 资金自管理钱包
2. **发现服务:** `GET https://registry.frames.ag/api/services`
3. **阅读服务文档:** `GET https://registry.frames.ag/api/service/{slug}/skill.md`
4. **查看定价:** `GET https://registry.frames.ag/api/pricing`
5. **发起付费请求**——通过 AgentWallet 的 `/x402/fetch` 或直接使用 x402 标头（见支付协议下方）

## 服务 (10)

| 服务 | Slug | 描述 | 端点 | 价格范围 |
|------|------|------|------|------|
| [Twitter API](https://registry.frames.ag/api/service/twitter/skill.md) | `twitter` | 完整 Twitter API 访问——用户、推文、搜索、社区、空间、趋势等，通过 twitterapi.io | 26 | $0.005 - $0.02 |
| [AI 生成 API](https://registry.frames.ag/api/service/ai-gen/skill.md) | `ai-gen` | 运行用于图像、视频、音频和 3D 生成的人工智能模型 | 1 | $0.01 |
| [x402 测试服务](https://registry.frames.ag/api/service/test/skill.md) | `test` | 在 Base Sepolia (EVM) 和 Solana Devnet 上测试 x402 支付流程。使用此服务验证您的 x402 客户端集成是否正常工作。 | 2 | $0.001 |
| [Exa API](https://registry.frames.ag/api/service/exa/skill.md) | `exa` | 通过 Exa 进行语义网络搜索 | 4 | $0.002 - $0.01 |
| [Wordspace Agent](https://registry.frames.ag/api/service/wordspace/skill.md) | `wordspace` | 具有沙盒执行和 OpenProse 技能的 AI 代理循环 | 1 | $2 |
| [OpenRouter](https://registry.frames.ag/api/service/openrouter/skill.md) | `openrouter` | 通过 300 多个模型（OpenAI、Anthropic、Google、Meta 等）进行文本生成 | 0 | 免费 |
| [Jupiter API](https://registry.frames.ag/api/service/jupiter/skill.md) | `jupiter` | 通过 Jupiter 进行 Solana 代币兑换、价格、搜索和投资组合 | 4 | $0.002 - $0.01 |
| [NEAR Intents API](https://registry.frames.ag/api/service/near-intents/skill.md) | `near-intents` | 通过 1Click 存款地址进行跨链代币兑换 | 1 | $0.01 |
| [AgentMail API](https://registry.frames.ag/api/service/agentmail/skill.md) | `agentmail` | AI 代理的电子邮件基础设施——创建收件箱、发送/接收电子邮件、管理线程 | 5 | $0.005 - $0.01 |
| [CoinGecko API](https://registry.frames.ag/api/service/coingecko/skill.md) | `coingecko` | 加密货币价格数据、市场信息和代币搜索——价格、市值、热门代币，跨越 10,000 多种加密货币进行搜索 | 5 | $0.002 - $0.005 |

## 服务端点

每个服务位于 `https://registry.frames.ag/api/service/{slug}`，并暴露：

| 端点 | 描述 |
|------|------|
| `GET /` | 服务信息 |
| `GET /health` | 健康检查 |
| `GET /docs` | 交互式 API 文档 |
| `GET /openapi.json` | OpenAPI 3.x 规范 |
| `GET /skill.md` | 代理友好的文档 |

## 定价详情

### Twitter API (`twitter`)

Base: `https://registry.frames.ag/api/service/twitter` | [文档](https://registry.frames.ag/api/service/twitter/docs) | [OpenAPI](https://registry.frames.ag/api/service/twitter/openapi.json) | [技能](https://registry.frames.ag/api/service/twitter/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/user-info` | $0.005 | 通过用户名查找 Twitter 用户的个人资料——返回简介、粉丝/关注者数量、验证状态和配置文件元数据 |
| `POST /api/user-tweets` | $0.01 | 通过用户名或用户 ID 获取用户的最近推文，可选包含回复和游标分页 |
| `POST /api/user-followers` | $0.01 | 列出关注用户的账户，分页最多每页 200 个，使用游标导航 |
| `POST /api/user-following` | $0.01 | 列出用户关注的账户，分页最多每页 200 个，使用游标导航 |
| `POST /api/verified-followers` | $0.01 | 列出关注用户的仅验证（蓝色勾号）账户，通过用户 ID 和游标分页 |
| `POST /api/search-users` | $0.01 | 通过关键字搜索 Twitter 用户——匹配名称、简介和用户名 |
| `POST /api/user-mentions` | $0.01 | 获取提及用户的推文，可选时间范围过滤（sinceTime/untilTime Unix 时间戳） |
| `POST /api/check-follow` | $0.005 | 检查一个用户是否关注另一个用户——返回两个用户名之间的关注关系 |
| `POST /api/batch-users` | $0.02 | 通过逗号分隔的用户 ID 在一次请求中获取多个用户资料 |
| `POST /api/tweets-by-ids` | $0.01 | 通过逗号分隔的推文 ID 获取完整的推文数据 |
| `POST /api/tweet-replies` | $0.01 | 获取特定推文的回复，可按相关性、最新或点赞排序，使用游标分页 |
| `POST /api/search-tweets` | $0.01 | 高级推文搜索，支持运算符——支持 from:、to:、has:media、日期范围、参与度过滤和布尔逻辑 |
| `POST /api/tweet-quotes` | $0.01 | 获取特定推文的全部引用推文，可选时间范围和回复过滤 |
| `POST /api/tweet-retweeters` | $0.01 | 列出转推特定推文的用户，使用游标分页 |
| `POST /api/tweet-thread` | $0.01 | 获取推文的完整对话线程——上下文中的父推文和回复 |
| `POST /api/list-tweets` | $0.01 | 通过列表 ID 获取 Twitter 列表中的推文，可选时间范围和回复过滤 |
| `POST /api/list-followers` | $0.01 | 列出关注特定 Twitter 列表的用户，使用游标分页 |
| `POST /api/list-members` | $0.01 | 列出 Twitter 列表的所有成员，使用游标分页 |
| `POST /api/community-info` | $0.005 | 获取 Twitter 社区的元数据——名称、描述、成员数量、规则和创建日期 |
| `POST /api/community-members` | $0.01 | 列出 Twitter 社区的成员，使用游标分页 |
| `POST /api/community-tweets` | $0.01 | 获取 Twitter 社区中发布的推文，使用游标分页 |
| `POST /api/space-detail` | $0.005 | 获取 Twitter 空间的详细信息——标题、主持人、参与者、日程和状态（直播/计划/结束） |
| `POST /api/article` | $0.01 | 通过包含它的推文 ID 获取长格式 Twitter 文章（笔记） |
| `POST /api/trends` | $0.01 | 获取某个位置的当前热门话题，通过 WOEID（1=全球，23424977=美国，2459115=纽约） |
| `POST /api/invoke` | $0.01 | 搜索推文（遗留——请使用 /api/search-tweets） |
| `POST /api/search` | $0.01 | 搜索推文（遗留——请使用 /api/search-tweets） |

### AI 生成 API (`ai-gen`)

Base: `https://registry.frames.ag/api/service/ai-gen` | [文档](https://registry.frames.ag/api/service/ai-gen/docs) | [OpenAPI](https://registry.frames.ag/api/service/ai-gen/openapi.json) | [技能](https://registry.frames.ag/api/service/ai-gen/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/invoke` | $0.01 | 运行 AI 模型预测（价格因模型而异） |

### x402 测试服务 (`test`)

Base: `https://registry.frames.ag/api/service/test` | [文档](https://registry.frames.ag/api/service/test/docs) | [OpenAPI](https://registry.frames.ag/api/service/test/openapi.json) | [技能](https://registry.frames.ag/api/service/test/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/invoke` | $0.001 | 测试 x402 支付流程（Base Sepolia & Solana Devnet） |
| `POST /api/echo` | $0.001 | 带有支付验证的回显数据 |

### Exa API (`exa`)

Base: `https://registry.frames.ag/api/service/exa` | [文档](https://registry.frames.ag/api/service/exa/docs) | [OpenAPI](https://registry.frames.ag/api/service/exa/openapi.json) | [技能](https://registry.frames.ag/api/service/exa/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/search` | $0.01 | 语义网络搜索 |
| `POST /api/find-similar` | $0.01 | 查找相似页面 |
| `POST /api/contents` | $0.002 | 提取 URL 内容 |
| `POST /api/answer` | $0.01 | AI 驱动的答案 |

### Wordspace Agent (`wordspace`)

Base: `https://registry.frames.ag/api/service/wordspace` | [文档](https://registry.frames.ag/api/service/wordspace/docs) | [OpenAPI](https://registry.frames.ag/api/service/wordspace/openapi.json) | [技能](https://registry.frames.ag/api/service/wordspace/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/invoke` | $2 | 运行 wordspace AI 代理循环 |

### Jupiter API (`jupiter`)

Base: `https://registry.frames.ag/api/service/jupiter` | [文档](https://registry.frames.ag/api/service/jupiter/docs) | [OpenAPI](https://registry.frames.ag/api/service/jupiter/openapi.json) | [技能](https://registry.frames.ag/api/service/jupiter/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/swap` | $0.01 | 获取兑换报价和未签名的交易 |
| `POST /api/price` | $0.002 | 代币价格查询 |
| `POST /api/tokens` | $0.002 | 代币搜索和元数据 |
| `POST /api/portfolio` | $0.005 | 钱包投资组合位置 |

### NEAR Intents API (`near-intents`)

Base: `https://registry.frames.ag/api/service/near-intents` | [文档](https://registry.frames.ag/api/service/near-intents/docs) | [OpenAPI](https://registry.frames.ag/api/service/near-intents/openapi.json) | [技能](https://registry.frames.ag/api/service/near-intents/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/quote` | $0.01 | 跨链兑换报价和存款地址 |

### AgentMail API (`agentmail`)

Base: `https://registry.frames.ag/api/service/agentmail` | [文档](https://registry.frames.ag/api/service/agentmail/docs) | [OpenAPI](https://registry.frames.ag/api/service/agentmail/openapi.json) | [技能](https://registry.frames.ag/api/service/agentmail/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/inbox/create` | $0.01 | 为 AI 代理创建新的电子邮件收件箱 |
| `POST /api/send` | $0.01 | 从代理收件箱发送电子邮件 |
| `POST /api/messages` | $0.005 | 列出收件箱中的消息 |
| `POST /api/message` | $0.005 | 通过 ID 获取特定消息 |
| `POST /api/threads` | $0.005 | 列出收件箱中的电子邮件线程 |

### CoinGecko API (`coingecko`)

Base: `https://registry.frames.ag/api/service/coingecko` | [文档](https://registry.frames.ag/api/service/coingecko/docs) | [OpenAPI](https://registry.frames.ag/api/service/coingecko/openapi.json) | [技能](https://registry.frames.ag/api/service/coingecko/skill.md)

| 端点 | 价格 | 描述 |
|------|------|------|
| `POST /api/price` | $0.002 | 获取任何法定货币/加密货币中的代币价格 |
| `POST /api/token-info` | $0.005 | 获取详细的代币信息和市场数据 |
| `POST /api/trending` | $0.005 | 获取当前热门的代币 |
| `POST /api/markets` | $0.005 | 获取代币市场数据，支持排序和分页 |
| `POST /api/search` | $0.003 | 通过名称或符号搜索代币 |

### AI 模型定价 (`ai-gen`)

价格根据请求正文中 `model` 字段动态设置。

**图像模型:**

| 模型 | 价格 |
|------|------|
| `flux/schnell` | $0.004/图像 |
| `flux/2-pro` | $0.02 |
| `flux/kontext-pro` | $0.05/图像 |
| `bytedance/seedream-4` | $0.04/图像 |
| `google/nano-banana` | $0.05/图像 |
| `google/nano-banana-2` | $0.09/图像 (1K), $0.13/图像 (2K), $0.19/图像 (4K) |
| `google/nano-banana-pro` | $0.18/图像 |
| `google/imagen-4-fast` | $0.03/图像 |
| `ideogram/v3-turbo` | $0.04/图像 |
| `prunaai/z-image-turbo` | $0.006/图像 |
| `prunaai/p-image` | $0.006/图像 |
| `fofr/sdxl-emoji` | $0.01 |
| `qwen/qwen-image-edit-2511` | $0.04/图像 |
| `openai/dall-e-3` | $0.15/图像 |
| `nightmareai/real-esrgan` | $0.003/图像 |

**视频模型:**

| 模型 | 价格 |
|------|------|
| `google/veo-3` | $0.48/秒 (音频), $0.24/秒 (无音频) |
| `google/veo-3-fast` | $0.18/秒 (音频), $0.12/秒 (无音频) |
| `google/veo-3.1` | $0.48/秒 (音频), $0.24/秒 (无音频) |
| `google/veo-3.1-fast` | $0.18/秒 (音频), $0.12/秒 (无音频) |
| `openai/sora-2` | $0.12/秒 |
| `openai/sora-2-pro` | $0.36/秒 (720p), $0.60/秒 (1080p) |
| `kwaivgi/kling-v2.5-turbo-pro` | $0.09/秒 |
| `kwaivgi/kling-v2.6` | $0.09/秒 |
| `kwaivgi/kling-v2.6-motion-control` | $0.09/秒 (标准), $0.15/秒 (专业) |
| `bytedance/seedance-1-pro` | $0.04/秒 (480p), $0.08/秒 (720p), $0.18/秒 (1080p) |
| `bytedance/seedance-1-lite` | $0.03/秒 (480p), $0.05/秒 (720p), $0.09/秒 (1080p) |
| `bytedance/seedance-1-pro-fast` | $0.02/秒 (480p), $0.03/秒 (720p), $0.08/秒 (1080p) |
| `bytedance/seedance-1.5-pro` | $0.04/秒 (720p), $0.07/秒 (720p+音频) |
| `minimax/video-01` | $0.60 |
| `wan-video/wan-2.2-t2v-fast` | $0.12 |
| `wan-video/wan-2.2-i2v-fast` | $0.07 |
| `wan-video/wan-2.5-i2v-fast` | $0.09/秒 (720p), $0.13/秒 (1080p) |
| `runwayml/gen4-turbo` | $0.06/秒 |
| `runwayml/gen4-aleph` | $0.22/秒 |
| `veed/fabric-1.0` | $0.10/秒 (480p), $0.18/秒 (768p) |
| `shreejalmaharjan-27/tiktok-short-captions` | $0.002/秒 |

## 支付协议 (x402)

所有付费端点使用 [x402](https://www.x402.org/) 支付协议。无需 API 密钥。

**流程:**

1. 调用任何付费端点而不带支付标头
2. 接收 `402 Payment Required` 和 `PAYMENT-REQUIRED` 标头（Base64 JSON，包含价格、网络、payTo 地址）
3. 在您选择的网络上对请求的金额进行支付签名
4. 使用 `PAYMENT-SIGNATURE` 标头重试相同的请求
5. 接收响应和 `PAYMENT-RESPONSE` 确认标头

失败的请求将自动退款。

**支持的网络:**

| 网络 | ID | 类型 | 环境 |
|------|----|------|------|
| Base | `eip155:8453` | EVM | 主网 |
| Base Sepolia | `eip155:84532` | EVM | 测试网 |
| Solana | `solana:5eykt4UsFv8P8NJdTREpY1vzqKqZKvdp` | Solana | 主网 |
| Solana Devnet | `solana:EtWTRABZaYq6iMfeYKouRu166VU2xqa1` | Solana | 开发网 |

**接受的代币:** USDC、USDT、CASH（可用性因网络而异）

## 平台端点 (免费)

| 端点 | 描述 |
|------|------|
| `GET https://registry.frames.ag/api` | 平台信息和版本 |
| `GET https://registry.frames.ag/api/services` | 列出所有服务及其元数据 |
| `GET https://registry.frames.ag/api/services/:slug` | 单个服务详细信息 |
| `GET https://registry.frames.ag/api/pricing` | 所有定价策略 |
| `GET https://registry.frames.ag/api/networks` | 支持的支付网络 |
| `GET https://registry.frames.ag/api/health` | 健康检查 |
| `GET https://registry.frames.ag/api/packages` | 技能/代理包目录 |
| `GET https://registry.frames.ag/api/packages/:slug/bundle` | 下载包捆绑包 |
| `GET https://registry.frames.ag/.well-known/x402` | x402 发现文档 |
| `GET https://registry.frames.ag/docs` | 交互式文档 (HTML) |

## 代理集成

### 使用 AgentWallet（推荐）

[AgentWallet](https://frames.ag/skill.md) 是 AI 代理的服务器端钱包。它管理密钥、余额和 x402 支付签名，因此代理无需直接处理加密货币。

1. 使用 AgentWallet 进行身份验证（电子邮件 OTP → API 令牌）
2. 在 Base 或 Solana 上使用 USDC 资金您的钱包
3. 通过 AgentWallet 的代理调用任何 Frames Registry 端点：

```
POST https://frames.ag/x402/fetch
{
  "url": "https://registry.frames.ag/api/service/twitter/api/search-tweets",
  "method": "POST",
  "body": { "query": "AI agents" }
}
```

AgentWallet 检测 402 响应，进行支付签名并自动重试。

### 直接 x402（自管理钱包）

需要带有 USDC 的 EVM 或 Solana 钱包，并能够签署 EIP-3009 或 SPL 转账。

1. 调用付费端点
2. 从 402 响应中解析 `PAYMENT-REQUIRED` 标头（Base64 JSON，包含价格、网络、payTo）
3. 对确切的金额进行支付授权签名
4. 使用 `PAYMENT-SIGNATURE` 标头重试
