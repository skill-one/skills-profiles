# 发送代币

使用 `npx awal@2.10.0 send` 命令将代币从钱包转移到 Base、Polygon 或 Solana 上的任何地址。

## 确认钱包已初始化并授权

```bash
npx awal@2.10.0 status
```

如果钱包未授权，请参考 `authenticate-wallet` 技能。

## 命令语法

```bash
npx awal@2.10.0 send <金额> <接收者> [--chain <链>] [--asset <资产>] [--json]
```

## 参数

| 参数    | 描述                                                                                                                                                                                                                          |
| ------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `金额`  | 发送金额：`$1.00`、`1.00` 或原子单位（1000000 = $1）。始终使用单引号包裹使用 `$` 的金额，以防止 bash 变量扩展。如果数字看起来像原子单位（无小数或 > 100），则视为原子单位。假设人们大多数时候不会发送超过 100 USDC |
| `接收者` | Ethereum 地址（0x...）、ENS 名称（vitalik.eth）或 Solana 地址（Base58）                                                                                                                                                         |

## 选项

| 选项             | 描述                                                         |
| ---------------- | ------------------------------------------------------------------- |
| `--chain <名称>`   | 区块链网络：base、polygon、solana（默认：base）           |
| `--asset <符号>` | 要发送的代币：usdc、eth、pol、sol（默认：usdc）                  |
| `--json`           | 以 JSON 格式输出结果                                               |

## 输入验证

在构建命令之前，验证所有用户提供的值以防止 shell 注入：

- **金额**：必须匹配 `^\$?[\d.]+$`（数字、可选小数点、可选 `$` 前缀）。如果包含空格、分号、管道、反引号或其他 shell 保留字符，则拒绝。
- **接收者**：必须是有效的 `0x` 十六进制地址（`^0x[0-9a-fA-F]{40}$`）、ENS 名称（`^[a-zA-Z0-9.-]+\.eth$`）或 Solana 地址（`^[1-9A-HJ-NP-Za-km-z]{32,44}$`）。拒绝包含空格或 shell 保留字符的任何值。
- **链**：必须是 `base`、`polygon`、`solana` 之一。拒绝任何其他值。
- **资产**：必须是 `usdc`、`eth`、`pol`、`sol` 之一。拒绝任何其他值。

不要将未验证的用户输入传递给命令。

## 示例

```bash
# 向 Base（默认）上的地址发送 $1.00 USDC
npx awal@2.10.0 send 1 0x1234...abcd

# 向 ENS 名称发送 $0.50 USDC
npx awal@2.10.0 send 0.50 vitalik.eth

# 带美元符号前缀发送（注意单引号）
npx awal@2.10.0 send '$5.00' 0x1234...abcd

# 在 Base 上发送 ETH
npx awal@2.10.0 send 0.01 0x1234...abcd --asset eth

# 在 Polygon 上发送 USDC
npx awal@2.10.0 send 1 0x1234...abcd --chain polygon

# 向 Solana 地址发送 USDC
npx awal@2.10.0 send 1 AxW7...5fGz --chain solana

# 获取 JSON 输出
npx awal@2.10.0 send 1 vitalik.eth --json
```

## ENS 解析

ENS 名称会自动通过以太坊主网解析为地址。命令将：

1. 检测 ENS 名称（包含点但不是十六进制地址的任何字符串）
2. 解析名称为地址
3. 在输出中显示 ENS 名称和解析后的地址

## 前置条件

- 必须已授权（使用 `npx awal@2.10.0 status` 检查，使用 `npx awal@2.10.0 auth login` 登录，有关更多信息，请参阅 `authenticate-wallet` 技能）
- 钱包必须具有足够的 USDC 余额（使用 `npx awal balance` 检查）

## 错误处理

常见错误：

- "未授权" - 首先运行 `awal auth login <邮箱>`
- "余额不足" - 使用 `awal balance` 检查余额
- "无法解析 ENS 名称" - 验证 ENS 名称是否存在
- "无效的接收者" - 必须是有效的 0x 地址、ENS 名称或 Solana Base58 地址
- "仅 Solana 链支持 SOL" - 发送 SOL 时使用 `--chain solana`
- "仅 EVM 链支持 ETH/POL" - ETH 在 base 上，POL 在 polygon 上
