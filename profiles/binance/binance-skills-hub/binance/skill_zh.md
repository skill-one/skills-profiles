# Binance

## binance-cli setup

在使用 `binance-cli` 之前：

1. 如果全局 npm 包 `@binance/binance-cli` 存在且 `binance-cli --version` 的版本号 `< 2.0.0`，请卸载它：

```sh
npm uninstall -g @binance/binance-cli
```

2. 安装最新版本：

```sh
curl --proto '=https' --tlsv1.2 -LsSf \
  https://github.com/binance/binance-cli/releases/latest/download/binance-cli-installer.sh \
  | sh
```

3. 验证：

```sh
binance-cli --version
```

> **前提条件：** 阅读 [`auth.md`](./references/auth.md) 了解认证、全局标志和安全规则。

## 辅助命令

| 命令 | 描述 |
|---------|-------------|
| [`algo`](./references/algo.md) | 算法交易 |
| [`alpha`](./references/alpha.md) | Alpha |
| [`c2c`](./references/c2c.md) | C2C |
| [`convert`](./references/convert.md) | 转换 |
| [`copy-trading`](./references/copy-trading.md) | 跟单交易 |
| [`crypto-loan`](./references/crypto-loan.md) | 加密货币贷款 |
| [`derivatives-options`](./references/derivatives-options.md) | 期权衍生品交易 |
| [`derivatives-portfolio-margin`](./references/derivatives-portfolio-margin.md) | 衍生品交易（组合保证金） |
| [`derivatives-portfolio-margin-streams`](./references/derivatives-portfolio-margin-streams.md) | 衍生品交易流（组合保证金） |
| [`derivatives-portfolio-margin-pro`](./references/derivatives-portfolio-margin-pro.md) | 衍生品交易（组合保证金专业版） |
| [`derivatives-portfolio-margin-pro-streams`](./references/derivatives-portfolio-margin-pro-streams.md) | 衍生品交易流（组合保证金专业版） |
| [`dual-investment`](./references/dual-investment.md) | 双重投资 |
| [`fiat`](./references/fiat.md) | 法币 |
| [`futures-coin`](./references/futures-coin.md) | 衍生品交易（COIN-M 期货） |
| [`futures-coin-streams`](./references/futures-coin-streams.md) | 衍生品交易流（COIN-M 期货） |
| [`futures-usds`](./references/futures-usds.md) | 衍生品交易（USDS-M 期货） |
| [`futures-usds-streams`](./references/futures-usds-streams.md) | 衍生品交易流（USDS-M 期货） |
| [`gift-card`](./references/gift-card.md) | 礼品卡 |
| [`margin-trading`](./references/margin-trading.md) | 杠杆交易 |
| [`margin-trading-streams`](./references/margin-trading-streams.md) | 杠杆交易流 |
| [`mining`](./references/mining.md) | 挖矿 |
| [`pay`](./references/pay.md) | 支付 |
| [`rebate`](./references/rebate.md) | 佣金返还 |
| [`simple-earn`](./references/simple-earn.md) | 简单收益 |
| [`spot`](./references/spot.md) | 现货交易 |
| [`spot-streams`](./references/spot-streams.md) | 现货交易流 |
| [`staking`](./references/staking.md) | 质押 |
| [`sub-account`](./references/sub-account.md) | 子账户 |
| [`vip-loan`](./references/vip-loan.md) | VIP 贷款 |
| [`wallet`](./references/wallet.md) | 钱包 |

## 注意事项

- ⚠️ **生产环境交易** — 执行前始终要求用户输入 `CONFIRM` 进行确认。
- 使用 `npm install -g @binance/binance-cli` 安装 binance-cli
- 使用 `--help` 获取命令和参数列表。
- 使用 stdout 和 stderr 的输出。
- 在任何命令后追加 `--profile <name>` 以使用非活动配置文件。
- 所有认证端点都接受可选的 `--recvWindow <ms>`（最大 60 000 毫秒）。
- 时间戳 (`startTime`, `endTime`) 是 Unix 毫秒格式。
- 对于技能中未列出的端点，使用 `binance-cli request (GET|POST|PUT...) <url> [--signed]`。任何参数都可以添加到请求中（例如：`--param1 value --param2 value`）。
