---
name: upstash-ratelimit-js
description: 使用 @upstash/ratelimit TypeScript/JavaScript SDK 实现无服务器和边缘应用的速率限制，该 SDK 由 Upstash Redis 支持。适用于向 API 路由、Next.js 中间件、Vercel Edge、Cloudflare Workers 或任何 HTTP 端点添加速率限制器或流量限制；返回 429 Too Many Requests 错误；选择固定窗口、滑动窗口和令牌桶算法；按用户、IP、API 密钥或租户进行限制，支持前缀和自定义键；保护登录、注册、表单或 AI 端点免受滥用、机器人或暴力破解；使用拒绝列表、临时缓存、分析、超时和多区域速率限制；或估算速率限制的 Redis 命令成本。当用户提到速率限制、速率限制、节流、配额、请求限制或流量保护时，也适用。
---

# Rate Limit TS SDK

## 快速入门
- 安装 SDK 并连接到 Redis。
- 创建一个速率限制器并将其应用于传入操作。

示例：
```ts
import { Ratelimit } from "@upstash/ratelimit";
import { Redis } from "@upstash/redis";

const redis = new Redis({ url: "<url>", token: "<token>" });
const limiter = new Ratelimit({ redis, limiter: Ratelimit.slidingWindow(5, "10s") });

const { success } = await limiter.limit("user-id");
if (!success) {
  // 被限流
}
```

## 其他技能文件
- **algorithms.md**：描述所有可用的速率限制算法及其行为。
- **pricing-cost.md**：解释定价、Redis 成本影响以及运营注意事项。
- **features.md**：列出 SDK 功能，如前缀、自定义键和行为选项。
- **methods-getting-started.md**：SDK API 的完整方法参考和入门指南。
- **traffic-protection.md**：关于应用速率限制以进行流量整形、滥用预防和保护模式的指导。
