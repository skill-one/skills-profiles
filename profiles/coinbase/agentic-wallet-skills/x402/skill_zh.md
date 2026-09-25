# x402 支付协议

使用 `npx awal@2.10.0 x402` 命令，通过 X402 支付协议发现、检查和调用付费 API 端点。支付使用 Base 上的 USDC 进行。

## 工作流程

典型的 x402 工作流程如下：

1. **查找服务** - 在市场搜索或获取已知端点的详细信息
2. **检查要求** - 检查价格、方法和输入模式
3. **发起请求** - 调用端点并自动进行 USDC 支付

## 命令

### 搜索市场

使用 CDP 的向量搜索按关键词查找付费服务：

```bash
npx awal@2.10.0 x402 bazaar search <query> [-k <n>] [--network <network>] [--scheme <scheme>] [--max-price <price>] [--json]
```

| 选项                  | 描述                                                              |
| ----------------------- | ------------------------------------------------------------------------ |
| `-k, --top <n>`         | 结果数量，1–20（默认：20）                                        |
| `--network <name>`      | 按链过滤（base、base-sepolia、polygon、solana、solana-devnet）     |
| `--scheme <scheme>`     | 按支付方案过滤：`exact` 或 `upto`                                  |
| `--max-price <price>`   | 最大价格（美元，例如 `0.01`）                                       |
| `--asset <address>`     | 按支付资产地址过滤                                          |
| `--pay-to <address>`    | 按接收者钱包地址过滤                                       |
| `--extensions <type>`   | 按扩展类型过滤（例如 `outputSchema`、`bazaar`）                 |
| `--json`                | 输出为 JSON                                                           |

### 列出市场资源

浏览所有可用资源：

```bash
npx awal@2.10.0 x402 bazaar list [--network <network>] [--full] [--refresh] [--json]
```

| 选项             | 描述                                                          |
| ------------------ | -------------------------------------------------------------------- |
| `--network <name>` | 按链过滤（base、base-sepolia、polygon、solana、solana-devnet） |
| `--full`           | 显示完整详细信息，包括模式                                  |
| `--refresh`        | 从 CDP API 重新获取资源索引                                 |
| `--json`           | 输出为 JSON                                                       |

### 发现支付要求

在不支付的情况下检查端点的 x402 支付要求：

```bash
npx awal@2.10.0 x402 details <url> [--json]
```

通过尝试每个方法直到收到 402 响应来自动检测正确的 HTTP 方法（GET、POST、PUT、DELETE、PATCH），然后显示价格、接受的支付方案、网络和输入/输出模式。

### 发起付费请求

使用自动 USDC 支付调用 x402 端点：

```bash
npx awal@2.10.0 x402 pay <url> [-X <method>] [-d <json>] [-q <params>] [-h <json>] [--max-amount <n>] [--json]
```

| 选项                  | 描述                                        |
| ----------------------- | -------------------------------------------------- |
| `-X, --method <method>` | HTTP 方法（默认：GET）                         |
| `-d, --data <json>`     | 请求体为 JSON 字符串                        |
| `-q, --query <params>`  | 查询参数为 JSON 字符串                    |
| `-h, --headers <json>`  | 自定义 HTTP 头部为 JSON 字符串                 |
| `--max-amount <amount>` | 最大支付量（USDC 原子单位，1000000 = $1.00） |
| `--correlation-id <id>` | 将相关操作分组                           |
| `--json`                | 输出为 JSON                                     |

## 示例

```bash
# 搜索与天气相关的付费 API
npx awal@2.10.0 x402 bazaar search "weather"

# 搜索更多结果
npx awal@2.10.0 x402 bazaar search "情感分析" -k 10

# 检查端点费用
npx awal@2.10.0 x402 details https://example.com/api/weather

# 发起 GET 请求（自动支付）
npx awal@2.10.0 x402 pay https://example.com/api/weather

# 发起 POST 请求带请求体
npx awal@2.10.0 x402 pay https://example.com/api/sentiment -X POST -d '{"text": "我喜欢这个产品"}'

# 限制最大支付为 $0.10
npx awal@2.10.0 x402 pay https://example.com/api/data --max-amount 100000

# 浏览所有市场资源带完整详细信息
npx awal@2.10.0 x402 bazaar list --full
```

## USDC 数量

X402 使用 USDC 原子单位（6 位小数）：

| 原子单位 | 美元   |
| ------------ | ----- |
| 1000000      | $1.00 |
| 100000       | $0.10 |
| 50000        | $0.05 |
| 10000        | $0.01 |

## 前置条件

- **搜索/详情**：无需认证
- **支付**：必须认证（`npx awal@2.10.0 auth login <email>`）且 USDC 余额充足（`npx awal@2.10.0 balance`）

## 错误处理

- "未认证" - 首先运行 `npx awal@2.10.0 auth login <email>`
- "未找到 X402 支付要求" - URL 可能不是 x402 端点
- "CDP API 返回 429" - 被限流；如果可用将使用缓存数据
- "余额不足" - 用 USDC 充值钱包（`npx awal@2.10.0 balance` 查看余额）
