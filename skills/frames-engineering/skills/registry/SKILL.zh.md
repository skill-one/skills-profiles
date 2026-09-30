---
name: registry
description: 按调用付费的API网关，适用于AI代理。通过x402即可使用10项服务——无需API密钥，无需订阅。
---

# 帧注册中心

按调用付费的 API 网关，用于 AI 代理。通过 x402 支付协议提供 10 项服务。无需 API 密钥，无需订阅——只需使用加密货币按请求付费。

## 基础 URL

```
https://registry.frames.ag
```

## 前置条件

使用付费端点需要使用 USDC 资金的加密货币钱包。有两种选择：

- **AgentWallet**（推荐用于代理）——服务器端钱包，通过单个 `POST /x402/fetch` 调用自动处理 402 检测、支付签名和重试。无需在您这边管理私钥。
- **自管理钱包**——任何 EVM 钱包（Base）或带有 USDC 的 Solana 钱包。您直接签名 x402 支付标头。

## 快速入门

1. **设置钱包**——创建 [AgentWallet](https://frames.ag/skill.md) 或用 USDC 资金您的钱包
2. **发现服务：** `GET https://registry.frames.ag/api/services`
3. **阅读服务文档：** `GET https://registry.frames.ag/api/service/{slug}/skill.md`
4. **查看定价：** `GET https://registry.frames.ag/api/pricing`
5. **发起付费请求**——通过 AgentWallet 的 `/x402/fetch` 或直接使用 x402 标头（见支付协议下方）

## 服务 (10)

| 服务 | Slug | 描述 | 端点 | 价格范围 |
|------|------|------|------|------|
| [Twitter API](https://registry.frames.ag/api/service/twitter/skill.md) | `twitter` | 完整的 Twitter API 访问权限 - 用户、推文、搜索、社区、空间、趋势等，通过 twitterapi.io | 26 | $0.005 - $0.02 |
| [AI 生成 API](https://registry.frames.ag/api/service/ai-gen/skill.md) | `ai-gen` | 运行用于图像、视频、音频和 3D 生成的人工智能模型 | 1 | $0.01 |
| [x402 测试服务](https://registry.frames.ag/api/service/test/skill.md) | `test` | 在 Base Sepolia (EVM) 和 Solana Devnet 上测试 x402 支付流程。使用此服务来验证您的 x402 客户端集成是否正常工作。 | 2 | $0.001 |
| [Exa API](https://registry.frames.ag/api/service/exa/skill.md) | `exa` | 通过 Exa 进行语义网络搜索 | 4 | $0.002 - $0.01 |
| [Wordspace Agent](https://registry.frames.ag/api/service/wordspace/skill.md) | `wordspace` | 具有沙盒执行和 OpenProse 技能的 AI 代理循环 | 1 | $2 |
| [OpenRouter](https://registry.frames.ag/api/service/openrouter/skill.md) | `openrouter` | 通过 300 多个模型（OpenAI、Anthropic、Google、Meta 等）进行文本生成 | 0 | 免费 |
| [Jupiter API](https://registry.frames.ag/api/service/jupiter/skill.md) | `jupiter` | 通过 Jupiter 进行 Solana 代币兑换、价格、搜索和投资组合 | 4 | $0.002 - $0.01 |
| [NEAR Intents API](https://registry.frames.ag/api/service/near-intents/skill.md) | `near-intents` | 通过 1Click 存款地址进行跨链代币兑换 | 1 | $0.01 |
| [AgentMail API](https://registry.frames.ag/api/service/agentmail/skill.md) | `agentmail` | AI 代理的电子邮件基础设施——创建收件箱、发送/接收电子邮件、管理线程 | 5 | $0.005 - $0.01 |
| [CoinGecko API](https://registry.frames.ag/api/service/coingecko/skill.md) | `coingecko` | 加密货币价格数据、市场信息和代币搜索——价格、市值、热门代币，以及跨越 10,000 多种加密货币的搜索 | 5 | $0.002 - $0.005 |

## 服务端点

每个服务都位于 `https://registry.frames.ag/api/service/{slug}`，并暴露：

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
| `POST /api/user-tweets` | $0.01 | 通过用户名或用户 ID 获取用户的最新推文，可选包含回复和游标分页 |
| `POST /api/user-followers` | $0.01 | 列出关注用户的账户，分页最多每页 200 个，使用游标导航 |
| `POST /api/user-following` | $0.01 | 列出用户关注的账户，分页最多每页 200 个，使用游标导航 |
| `POST /api/verified-followers` | $0.01 | 列出关注用户的仅验证（蓝色勾号）账户，通过用户 ID 使用游标分页 |
| `POST /api/search-users` | $0.01 | 通过关键字搜索 Twitter 用户——匹配名称、简介和用户名 |
| `POST /api/user-mentions` | $0.01 | 获取提及用户的推文，可选时间范围过滤（sinceTime/untilTime unix 时间戳） |
| `POST /api/check-follow` | $0.005 | 检查一个用户是否关注另一个用户——返回两个用户名之间的关注关系 |
| `POST /api/batch-users` | $0.02 | 通过逗号分隔的用户 ID 在一次请求中获取多个用户资料 |
| `POST /api/tweets-by-ids` | $0.01 | 通过逗号分隔的推文 ID 获取完整的推文数据 |
| `POST /api/tweet-replies` | $0.01 | 获取特定推文的回复，可按相关性、最新或点赞排序，使用游标分页 |
| `POST /api/search-tweets` | $0.01 | 高级推文搜索，支持运算符——支持 from:、to:、has:media、日期范围、参与度过滤和布尔逻辑 |
| `POST /api/tweet-quotes` | $0.01 | 获取特定推文的全部引用推文，可选时间范围和回复过滤 |
| `POST /api/tweet-retweeters` | $0.01 | 列出转推特定推文的用户，使用游标分页 |
| `POST /api/tweet-thread` | $0.01 | 获取推文的完整对话线程——上下文中的父推文和回复 |
| `POST /api/list-tweets` | $0.01 | 通过列表 ID 获取 Twitter 列表中的推文，可选时间范围和回复过滤 |
| `POST /api/list-followers` | $0.01 | 列出关注特定 Twitter 列表的用

```
POST https://frames.ag/x402/fetch
{
  "url": "https://registry.frames.ag/api/service/twitter/api/search-tweets",
  "method": "POST",
  "body": { "query": "AI agents" }
}
```

AgentWallet 检测到 402 响应，会自动签名支付并重试。

### 直接 x402（自管理钱包）

需要具有 USDC 且能够签名 EIP-3009 或 SPL 转账的 EVM 或 Solana 钱包。

1. 向付费端点发起请求
2. 解析 402 响应中的 `PAYMENT-REQUIRED` 头（Base64 JSON 格式，包含价格、网络、payTo）
3. 对确切金额进行支付授权签名
4. 使用 `PAYMENT-SIGNATURE` 头重试
