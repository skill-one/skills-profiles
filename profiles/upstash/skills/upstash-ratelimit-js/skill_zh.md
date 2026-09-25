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
- **pricing-cost.md**：解释定价、Redis 成本影响以及操作注意事项。
- **features.md**：列出 SDK 功能，如前缀、自定义键和行为选项。
- **methods-getting-started.md**：SDK API 的完整方法参考和入门指南。
- **traffic-protection.md**：关于应用速率限制以进行流量整形、滥用预防和保护模式的指导。
