# 搜索 x402 市场

使用 `npx awal@2.10.0 x402` 命令来发现和检查 x402 市场上的付费 API 端点。搜索无需认证或余额。

## 命令

### 搜索市场

使用 CDP 的向量搜索按关键词查找付费服务：

```bash
npx awal@2.10.0 x402 bazaar search <query> [-k <n>] [--network <network>] [--scheme <scheme>] [--max-price <price>] [--json]
```

| 选项                  | 描述                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `-k, --top <n>`         | 结果数量，1–20（默认：20）                                        |
| `--network <name>`      | 按链过滤（base, base-sepolia, polygon, solana, solana-devnet）     |
| `--scheme <scheme>`     | 按支付方案过滤：`exact` 或 `upto`                                  |
| `--max-price <price>`   | 最大价格（美元），例如 `0.01`                                       |
| `--asset <address>`     | 按支付资产地址过滤                                          |
| `--pay-to <address>`    | 按收款钱包地址过滤                                       |
| `--extensions <type>`   | 按扩展类型过滤（例如 `outputSchema`, `bazaar`）                 |
| `--json`                | 以 JSON 格式输出                                                           |

### 列出市场资源

浏览所有可用资源：

```bash
npx awal@2.10.0 x402 bazaar list [--network <network>] [--full] [--refresh] [--json]
```

| 选项             | 描述                                                              |
| ------------------ | -------------------------------------------------------------------- |
| `--network <name>` | 按链过滤（base, base-sepolia, polygon, solana, solana-devnet） |
| `--full`           | 显示完整详情，包括模式                                          |
| `--refresh`        | 从 CDP API 重新获取资源索引                                     |
| `--json`           | 以 JSON 格式输出                                                       |

### 发现支付要求

在不付费的情况下检查端点的 x402 支付要求：

```bash
npx awal@2.10.0 x402 details <url> [--json]
```

通过尝试每种 HTTP 方法（GET、POST、PUT、DELETE、PATCH）直到收到 402 响应来自动检测正确的 HTTP 方法，然后显示价格、接受的支付方案、网络以及输入/输出模式。

## 示例

```bash
# 搜索与天气相关的付费 API
npx awal@2.10.0 x402 bazaar search "weather"

# 搜索更多结果
npx awal@2.10.0 x402 bazaar search "情感分析" -k 10

# 浏览所有市场资源并显示完整详情
npx awal@2.10.0 x402 bazaar list --full

# 检查端点的费用
npx awal@2.10.0 x402 details https://example.com/api/weather
```

## 前置条件

- 搜索、列出或详情命令无需认证

## 下一步

找到想要使用的服务后，使用 `pay-for-service` 技能向端点发起付费请求。

## 错误处理

- "CDP API 返回 429" - 被限流；如果可用将使用缓存数据
- "未找到 X402 支付要求" - URL 可能不是 x402 端点
