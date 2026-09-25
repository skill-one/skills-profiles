# 智能钱包

通过 `awal` CLI 操作加密货币钱包。此技能是一个路由器：针对当前任务，在 `references/` 目录中读取相关的参考文件。

## 预检查：确认钱包状态

在进行需要身份验证的钱包操作（除 x402 搜索/详情之外的所有操作）之前，请检查状态：

```bash
npx awal@2.12.1 status
```

如果钱包未通过身份验证，请阅读 `references/auth.md` 并先完成登录。

## 路由

在采取行动之前，选择与任务匹配的参考文件并“阅读”它：

| 任务 | 参考 |
| --- | --- |
| 登录、连接钱包、OTP 验证、“未登录”错误 | `references/auth.md` |
| 查看余额、“我有多少 USDC/ETH/POL/SOL”、“按链查看余额”、“JSON 格式余额输出” | `references/balance.md` |
| 向地址或 ENS 名称（Base、Polygon、Solana）发送 USDC / ETH / POL / SOL | `references/send-usdc.md` |
| 在 Base 或 Polygon 上进行代币兑换/交易/转换 | `references/trade.md` |
| 添加资金、充值、上币、购买 USDC | `references/fund.md` |
| 在 x402 市场上查找/浏览/搜索付费服务 | `references/x402-search.md` |
| 调用带有自动 USDC 支付的 x402 付费 API 端点 | `references/x402-pay.md` |
| 构建或部署其他智能体可以付费使用的付费 API 服务器 | `references/x402-monetize.md` |
| 通过 CDP SQL API 查询 Base 上的链上数据（事件、交易、区块） | `references/query-onchain.md` |

如果没有明确的匹配项，并且用户希望使用外部功能，请在 x402 市场上搜索（`references/x402-search.md`）——可能存在付费服务。

## 共享规则

- **输入验证**：每个参考文件都列出了用户提供的值必须匹配的正则表达式/白名单，才能将其放入 shell 命令中。严格验证；拒绝包含空格、分号、管道、反引号或其他 shell 保留字符的输入。不要将未验证的用户输入传递给命令。
- **单引号 `$` 金额**：任何以 `'$1.00'` 形式写入的金额都必须使用单引号，以防止 bash 变量扩展。
- **JSON 输出**：每个 `awal` 命令都支持 `--json` 以获取机器可读的输出。
- **身份验证错误意味着重新认证**：如果任何命令因“未通过身份验证”或类似错误而失败，请阅读 `references/auth.md` 并运行登录流程。
- **余额不足**：请阅读 `references/fund.md` 进行充值。

## 快速命令索引

| 命令 | 目的 |
| --- | --- |
| `npx awal@2.12.1 status` | 服务器健康状态 + 身份验证状态 |
| `npx awal@2.12.1 address` | 获取钱包地址 |
| `npx awal@2.12.1 balance` | 获取 Base、Polygon、Solana 上的余额（使用 `--chain` 查询单个链） |
| `npx awal@2.12.1 show` | 打开钱包配套窗口（用于充值） |
| `npx awal@2.12.1 auth login <email>` | 发送 OTP 码 |
| `npx awal@2.12.1 auth verify <otp>` | 完成登录 |
| `npx awal@2.12.1 auth logout` | 注销并清除会话 |
| `npx awal@2.12.1 send <amount> <recipient>` | 发送代币 |
| `npx awal@2.12.1 trade <amount> <from> <to>` | 兑换代币 |
| `npx awal@2.12.1 x402 bazaar search <query>` | 搜索付费服务 |
| `npx awal@2.12.1 x402 bazaar list` | 列出市场资源 |
| `npx awal@2.12.1 x402 details <url>` | 检查支付要求 |
| `npx awal@2.12.1 x402 pay <url>` | 支付并调用 x402 端点 |
