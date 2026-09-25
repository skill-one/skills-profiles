# Grimoire Polymarket 技能

使用此技能通过 `polymarket` 场地适配器进行 Polymarket 市场发现、CLOB 市场数据以及订单管理操作。

推荐的调用方式：

- `grimoire venue polymarket ...`
- `npx -y @grimoirelabs/cli venue polymarket ...`（无需安装）
- `bun run packages/cli/src/index.ts venue polymarket ...`（本地仓库）
- `grimoire-polymarket ...`（来自 `@grimoirelabs/venues` 的直接二进制文件）

推荐的预检查：

- `grimoire venue doctor --adapter polymarket --json`
- `grimoire venue polymarket info --format json`

## 命令

规范代理命令：

- `grimoire venue polymarket info [--format <auto|json|table>]`
- `grimoire venue polymarket search-markets [--query <text>] [--slug <slug|url>] [--question <text>] [--event <text>] [--tag <text>] [--category <text>] [--league <text>] [--sport <text>] [--open-only <true|false>] [--active-only <true|false>] [--ignore-end-date <true|false>] [--tradable-only <true|false>] [--all-pages <true|false>] [--max-pages <n>] [--stop-after-empty-pages <n>] [--limit <n>] [--format <auto|json|table>]`

允许的传递组（官方 CLI 表面，由包装器策略限制）：

- `markets` (`list|get|search|tags`)
- `data` (positions/value/leaderboards/etc.)

此包装器中禁止的组（有意不暴露给代理）：

- `wallet`
- `bridge`
- `approve`
- `ctf`
- `setup`
- `upgrade`
- `shell`

遗留兼容性别名仍然支持 (`market`, `book`, `midpoint`, `spread`, `price`, `last-trade-price`, `tick-size`, `neg-risk`, `fee-rate`, `price-history`, `order`, `trades`, `open-orders`, `balance-allowance`, `closed-only-mode`, `server-time`)，但不应用于新的代理流程。

## 示例

```bash
# 包装器/健康检查
grimoire venue polymarket info --format json
grimoire venue polymarket status --format json

# 规范发现
grimoire venue polymarket search-markets --query bitcoin --active-only true --open-only true --format json
grimoire venue polymarket search-markets --category sports --league "la liga" --active-only true --open-only true --format json

# 官方传递发现/数据
grimoire venue polymarket markets list --limit 25 --format json
grimoire venue polymarket markets search "atleti" --limit 25 --format json
grimoire venue polymarket data positions <address> --limit 25 --format json
grimoire venue polymarket data trades <address> --limit 25 --format json
grimoire venue polymarket data leaderboard --period week --order-by vol --limit 25 --format json

# 遗留兼容性别名（仍然支持）
grimoire venue polymarket book --token-id <token_id> --format json
grimoire venue polymarket price --token-id <token_id> --side buy --format json
grimoire venue polymarket order --order-id <order_id> --format json
grimoire venue polymarket open-orders --market <condition_id> --format json
```

## 运行时配置

适配器/运行时认证（用于技能执行）：

- 默认需要：`POLYMARKET_PRIVATE_KEY`
- 可选 API 凭证：`POLYMARKET_API_KEY`, `POLYMARKET_API_SECRET`, `POLYMARKET_API_PASSPHRASE`
- 可选派生开关（默认为 true）：`POLYMARKET_DERIVE_API_KEY=true|false`
- 可选签名路由：`POLYMARKET_SIGNATURE_TYPE` (`0` EOA, `1` POLY_PROXY, `2` GNOSIS_SAFE), `POLYMARKET_FUNDER`
- `grimoire cast` / `grimoire resume` 基于密钥的流程会将相同的钱包管理器密钥注入 Polymarket 适配器，因此不需要单独的 `POLYMARKET_PRIVATE_KEY` 环境变量。

场地 CLI 后端：

- 官方二进制文件需要：`polymarket`
- 安装：`brew tap Polymarket/polymarket-cli && brew install polymarket`
- 可选路径覆盖：`POLYMARKET_OFFICIAL_CLI=/custom/path/polymarket`

## 技能操作

Polymarket 使用 `custom` 操作类型，并带有 `op: "order"` 用于订单创建：

```spell
polymarket.custom(
  op="order",
  token_id="TOKEN_ID",
  price="0.55",
  size="100",
  side="BUY",
  order_type="GTC",
)
```

适配器不支持运行时约束（`max_slippage` 等）。订单路由：
- `GTC`/`GTD` → 限价单 (`createAndPostOrder`)
- `FOK`/`FAK` → 市场单 (`createAndPostMarketOrder`)

## 指标表面（技能比较）

Polymarket 暴露 `mid_price` 用于 CLOB 代币中点比较：

```spell
poly_mid = metric("mid_price", polymarket, USDC, "token_id=<clobTokenId>")
```

接受的筛选器键：`token_id`, `tokenid`, `market_id`, `id`。
如果筛选器被省略，指标会回退到第 3 个参数的值。

## 适配器说明

- 适配器名称：`polymarket`
- 执行类型：`offchain`
- 支持的链元数据：`137`（Polygon）
- 操作类型：`custom`
- 支持的自定义操作：`order`, `cancel_order`, `cancel_orders`, `cancel_all`, `heartbeat`

接受的订单参数别名：

- 代币：`token` 或 `tokenID` 或 `tokenId` 或 `coin`
- 数量：`size` 或 `amount`
- 方向：`BUY`/`SELL`
- 订单类型：`GTC`/`GTD`/`FOK`/`FAK`
- 额外兼容性别名：`arg0..arg5`, `reduce_only`

订单类型路由：

- `GTC`/`GTD` -> 限价单路径 (`createAndPostOrder`)
- `FOK`/`FAK` -> 市场单路径 (`createAndPostMarketOrder`)

## 注意事项

- 代理和自动化工作流程中优先使用 `--format json`。
- `search-markets` 是面向代理的规范化发现命令；传递 `markets search` 更为精简，更接近官方行为。
- 保持 CLI 表面的提示/工具；不要直接从建议工具调用 Polymarket HTTP API。
