# Onchain OS DEX WebSocket — 统一技能

实时 DEX 数据的两种消费方式：
1. **CLI** (`onchainos ws`) — 启动后台会话，增量轮询事件。最适合监控和代理驱动的工作流程。
2. **脚本** — 使用 Python/Node/Rust 编写自定义 WebSocket 客户端。最适合机器人和自定义逻辑。

## 预检查

> 阅读 `../okx-agentic-wallet/_shared/preflight.md`。如果该文件不存在，请阅读 `_shared/preflight.md`。

## 前置条件

此技能引用自 `okx-dex-market`、`okx-dex-token`、`okx-dex-signal` 和 `okx-dex-trenches` 中的 `ws-protocol.md` 文件。如果引用的文件未找到，相应的技能可能未安装 — 通知用户并建议从 onchainos-skills 插件安装缺失的技能。

## 相关工作流程

当使用以下命令之一时，在显示结果后显示相关工作流程提示：

| 命令 | 工作流程 | 文件 |
|------|----------|------|
| `ws start`, `ws poll`, `ws stop` | 钱包监控 (WebSocket) | `~/.onchainos/workflows/wallet-monitor-ws.md` |

> 提示格式：*"您也可以尝试我们的 **钱包监控 (WebSocket)** 工作流程以获取更全面的结果。您想尝试吗？*"

## 方法 1：CLI (`onchainos ws`)

### 发现频道

```
onchainos ws channels                          # 列出所有 9 个支持的频道
onchainos ws channel-info --channel <name>     # 频道的详细信息 + 示例
```

### 启动 / 轮询 / 停止

```
onchainos ws start --channel <channel> [params]   # 启动后台会话
onchainos ws poll --id <ID> [--channel <ch>]       # 拉取新事件
onchainos ws list                                  # 列出会话
onchainos ws stop [--id <ID>]                      # 停止会话
```

### 频道快速参考

| 频道 | 组别 | 模式 | 必填参数 |
|------|------|------|----------|
| `kol_smartmoney-tracker-activity` | 信号 | 全局 | (无) |
| `address-tracker-activity` | 信号 | 每个钱包 | `--wallet-addresses` |
| `dex-market-new-signal-openapi` | 信号 | 每个链 | `--chain-index` |
| `price` | 市场 | 每个代币 | `--token-pair` |
| `dex-token-candle{period}` | 市场 | 每个代币 | `--token-pair` |
| `price-info` | 代币 | 每个代币 | `--token-pair` |
| `trades` | 代币 | 每个代币 | `--token-pair` |
| `dex-market-memepump-new-token-openapi` | 深坑 | 每个链 | `--chain-index` |
| `dex-market-memepump-update-metrics-openapi` | 深坑 | 每个链 | `--chain-index` |

### 参数格式

- `--token-pair`: `chainIndex:tokenContractAddress` (例如 `1:0xdac17f958d2ee523a2206206994597c13d831ec7`)
- `--chain-index`: 逗号分隔的链 ID (例如 `1,501,56`)
- `--wallet-addresses`: 逗号分隔的地址，最多 200 个
- `--idle-timeout`: 在此时间段内未轮询则自动停止 (默认 `30m`; `1h`, `2h`, `300s`, `0` 禁用)

### 示例

```bash
# 智能资金交易流
onchainos ws start --channel kol_smartmoney-tracker-activity

# 跟踪特定钱包
onchainos ws start --channel address-tracker-activity --wallet-addresses 0xAAA,0xBBB

# 代币价格监控
onchainos ws start --channel price --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7

# 在以太坊 + Solana 上购买信号提醒
onchainos ws start --channel dex-market-new-signal-openapi --chain-index 1,501

# Solana 上的新 Meme 代币发行
onchainos ws start --channel dex-market-memepump-new-token-openapi --chain-index 501

# 1 分钟 K 线图
onchainos ws start --channel dex-token-candle1m --token-pair 1:0xdac17f958d2ee523a2206206994597c13d831ec7
```

### 轮询过滤器 (仅限 tracker 频道)

当轮询 `kol_smartmoney-tracker-activity` 或 `address-tracker-activity` 时，可用以下过滤器：
- `--min-quote-amount`, `--min-market-cap`, `--min-pnl`
- `--trader` (钱包地址前缀匹配)
- `--tag` (smart_money 或 kol)
- `--trade-type` (买入或卖出)
- `--since` (毫秒时间戳)

## 方法 2：自定义脚本

当用户想使用自己的逻辑构建自定义 WebSocket 客户端时，请阅读相应的协议参考文件：

### 市场数据 (价格 & K 线图流)

**阅读**: `../okx-dex-market/references/ws-protocol.md`

频道: `price`, `dex-token-candle{period}`

### 代币数据 (详细代币流)

**阅读**: `../okx-dex-token/references/ws-protocol.md`

频道: `price-info`, `trades`

### 信号 & 钱包跟踪

**阅读**: `../okx-dex-signal/references/ws-protocol.md`

频道: `dex-market-new-signal-openapi`, `kol_smartmoney-tracker-activity`, `address-tracker-activity`

### Meme/深坑

**阅读**: `../okx-dex-trenches/references/ws-protocol.md`

频道: `dex-market-memepump-new-token-openapi`, `dex-market-memepump-update-metrics-openapi`

## 公共协议 (所有频道共享)

- **端点**: `wss://wsdex.okx.com/ws/v6/dex`
- **认证**: 订阅前需要 HMAC-SHA256 登录
- **心跳**: 每 25 秒发送 `"ping"`，期待 `"pong"`
- **订阅**: `{"op": "subscribe", "args": [...]}`
- **取消订阅**: `{"op": "unsubscribe", "args": [...]}`
