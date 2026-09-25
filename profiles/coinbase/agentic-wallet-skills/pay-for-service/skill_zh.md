# 使用付费 x402 请求

使用 `npx awal@2.10.0 x402 pay` 命令调用 Base 上的付费 API 端点，并自动进行 USDC 支付。

## 确认钱包已初始化并授权

```bash
npx awal@2.10.0 status
```

如果钱包未授权，请参考 `authenticate-wallet` 技能。

## 命令语法

```bash
npx awal@2.10.0 x402 pay <url> [-X <method>] [-d <json>] [-q <params>] [-h <json>] [--max-amount <n>] [--json]
```

## 选项

| 选项                  | 描述                                        |
| ----------------------- | -------------------------------------------------- |
| `-X, --method <method>` | HTTP 方法（默认：GET）                         |
| `-d, --data <json>`     | 请求体作为 JSON 字符串                        |
| `-q, --query <params>`  | 查询参数作为 JSON 字符串                    |
| `-h, --headers <json>`  | 自定义 HTTP 头部作为 JSON 字符串                 |
| `--max-amount <amount>` | 最大支付金额（USDC 原子单位，1000000 = $1.00） |
| `--correlation-id <id>` | 将相关操作分组                           |
| `--json`                | 输出为 JSON                                     |

## USDC 金额

X402 使用 USDC 原子单位（6 位小数）：

| 原子单位 | 美元   |
| ------------ | ----- |
| 1000000      | $1.00 |
| 100000       | $0.10 |
| 50000        | $0.05 |
| 10000        | $0.01 |

**重要提示**：始终使用单引号包裹使用 `$` 的金额，以防止 bash 变量扩展（例如 `'$1.00'` 而不是 `$1.00`）。

## 输入验证

在构建命令之前，验证所有用户提供的值以防止 shell 注入：

- **url**：必须是有效的 URL，以 `https://` 或 `http://` 开头。如果包含空格、分号、管道、反引号或 shell 保留字符，则拒绝。
- **data (-d)**：必须是有效的 JSON。始终使用单引号包裹以防止 shell 扩展。
- **max-amount**：必须是一个正整数 (`^\d+$`)。

不要将未验证的用户输入传递给命令。

## 示例

```bash
# 发起 GET 请求（自动支付）
npx awal@2.10.0 x402 pay https://example.com/api/weather

# 发起 POST 请求并附带请求体
npx awal@2.10.0 x402 pay https://example.com/api/sentiment -X POST -d '{"text": "I love this product"}'

# 限制最大支付金额为 $0.10
npx awal@2.10.0 x402 pay https://example.com/api/data --max-amount 100000
```

## 前置条件

- 必须已授权（使用 `npx awal@2.10.0 status` 检查，参考 `authenticate-wallet` 技能）
- 钱包必须具有足够的 USDC 余额（使用 `npx awal@2.10.0 balance` 检查）
- 如果不知道端点 URL，请先使用 `search-for-service` 技能查找服务

## 错误处理

- "未授权" - 首先运行 `awal auth login <email>`，或参考 `authenticate-wallet` 技能
- "未找到 X402 支付要求" - URL 可能不是 x402 端点；使用 `search-for-service` 查找有效端点
- "余额不足" - 使用 USDC 资助钱包；参考 `fund` 技能
