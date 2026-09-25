# 在 Base 上查询链上数据

使用 CDP SQL API 在 Base 上查询链上数据（事件、交易、区块、转账）。查询通过 x402 执行，并按查询收费。

## 确认钱包已初始化并授权

```bash
npx awal@2.10.0 status
```

如果钱包未授权，请参考 `authenticate-wallet` 技能。

## 执行查询

```bash
npx awal@2.10.0 x402 pay https://x402.cdp.coinbase.com/platform/v2/data/query/run -X POST -d '{"sql": "<YOUR_QUERY>"}' --json
```

**重要提示**：始终单引号 `-d` 中的 JSON 字符串，以防止 bash 变量扩展。

## 输入验证

在构建命令之前，验证输入以防止 shell 注入：

- **SQL 查询**：始终将查询嵌入在单引号 JSON 字符串中 (`-d '{"sql": "..."}'`)。不要使用双引号作为外部的 `-d` 包装器，因为这会启用查询中 `$` 和反引号 的 shell 扩展。
- **地址**：必须是有效的 `0x` 十六进制地址 (`^0x[0-9a-fA-F]{40}$`)。拒绝任何包含 shell 保留字符的值。

不要将未验证的用户输入传递给命令。

## 关键：索引字段

对 `base.events` 的查询**必须**在索引字段上过滤，以避免全表扫描。索引字段如下：

| 索引字段 | 用途 |
| --- | --- |
| `event_signature` | 按事件类型过滤。出于性能考虑，使用此字段代替 `event_name`。 |
| `address` | 按合约地址过滤。 |
| `block_timestamp` | 按时间范围过滤。 |

**始终在 WHERE 子句中包含至少一个索引字段**。结合所有三个字段可以获得最佳性能。

## CoinbaseQL 语法

CoinbaseQL 是基于 ClickHouse 的 SQL 方言。支持的特性：

- **子句**：SELECT (DISTINCT), FROM, WHERE, GROUP BY, ORDER BY (ASC/DESC), LIMIT, WITH (CTEs), UNION (ALL/DISTINCT)
- **连接**：INNER, LEFT, RIGHT, FULL with ON
- **运算符**：`=`, `!=`, `<>`, `<`, `>`, `<=`, `>=`, `+`, `-`, `*`, `/`, `%`, AND, OR, NOT, BETWEEN, IN, IS NULL, LIKE
- **表达式**：CASE/WHEN/THEN/ELSE, CAST (支持 `CAST()` 和 `::` 语法), 子查询, 使用 `[]` 的数组/映射索引, 点表示法
- **字面量**：数组 `[...]`, 映射 `{...}`, 元组 `(...)`
- **函数**：标准 SQL 函数, 使用 `->` 语法 的 lambda 函数

## 可用表

### base.events

智能合约交互的解码事件日志。**这是大多数查询的主要表。**

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| log_id | String | 唯一日志标识符 |
| block_number | UInt64 | 区块号 |
| block_hash | FixedString(66) | 区块哈希 |
| block_timestamp | DateTime64(3, 'UTC') | 区块时间戳 (**INDEXED**) |
| transaction_hash | FixedString(66) | 交易哈希 |
| transaction_to | FixedString(42) | 交易接收方 |
| transaction_from | FixedString(42) | 交易发送方 |
| log_index | UInt32 | 区块内的日志索引 |
| address | FixedString(42) | 合约地址 (**INDEXED**) |
| topics | Array(FixedString(66)) | 事件主题 |
| event_name | LowCardinality(String) | 解码的事件名称 |
| event_signature | LowCardinality(String) | 事件签名 (**INDEXED** - 优先于 event_name) |
| parameters | Map(String, Variant(Bool, Int256, String, UInt256)) | 解码的事件参数 |
| parameter_types | Map(String, String) | 参数的 ABI 类型 |
| action | Enum8('removed' = -1, 'added' = 1) | 添加或移除 (重组) |

### base.transactions

完整的交易数据。

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| block_number | UInt64 | 区块号 |
| block_hash | String | 区块哈希 |
| transaction_hash | String | 交易哈希 |
| transaction_index | UInt64 | 区块中的索引 |
| from_address | String | 发送方地址 |
| to_address | String | 接收方地址 |
| value | String | 转移的值 (wei) |
| gas | UInt64 | Gas 限制 |
| gas_price | UInt64 | Gas 价格 |
| input | String | 输入数据 |
| nonce | UInt64 | 发送方 nonce |
| type | UInt64 | 交易类型 |
| max_fee_per_gas | UInt64 | EIP-1559 最大费用 |
| max_priority_fee_per_gas | UInt64 | EIP-1559 优先费用 |
| chain_id | UInt64 | 链 ID |
| v | String | 签名 v |
| r | String | 签名 r |
| s | String | 签名 s |
| is_system_tx | Bool | 系统交易标志 |
| max_fee_per_blob_gas | String | Blob Gas 费用 |
| blob_versioned_hashes | Array(String) | Blob 哈希 |
| timestamp | DateTime | 区块时间戳 |
| action | Int8 | 添加 (1) 或移除 (-1) |

### base.blocks

区块级元数据。

| 列名 | 类型 | 描述 |
| --- | --- | --- |
| block_number | UInt64 | 区块号 |
| block_hash | String | 区块哈希 |
| parent_hash | String | 父区块哈希 |
| timestamp | DateTime | 区块时间戳 |
| miner | String | 区块生产者 |
| nonce | UInt64 | 区块 nonce |
| sha3_uncles | String | Uncles 哈希 |
| transactions_root | String | 交易默克尔根 |
| state_root | String | 状态默克尔根 |
| receipts_root | String | 收据默克尔根 |
| logs_bloom | String | 布隆过滤器 |
| gas_limit | UInt64 | 区块 Gas 限制 |
| gas_used | UInt64 | 区块使用的 Gas |
| base_fee_per_gas | UInt64 | 每 Gas 基础费用 |
| total_difficulty | String | 链总难度 |
| size | UInt64 | 区块字节数 |
| extra_data | String | 额外数据字段 |
| mix_hash | String | 混合哈希 |
| withdrawals_root | String | 提款根 |
| parent_beacon_block_root | String | Beacon 链父根 |
| blob_gas_used | UInt64 | Blob Gas 使用量 |
| excess_blob_gas | UInt64 | 多余的 Blob Gas |
| transaction_count | UInt64 | 交易数量 |
| action | Int8 | 添加 (1) 或移除 (-1) |

## 示例查询

### 获取最近的 USDC 转账事件（带解码参数）

```sql
SELECT
  parameters['from'] AS sender,
  parameters['to'] AS to,
  parameters['value'] AS amount,
  address AS token_address
FROM base.events
WHERE
  event_signature = 'Transfer(address,address,uint256)'
  AND address = '0x833589fcd6edb6e08f4c7c32d4f71b54bda02913'
  AND block_timestamp >= now() - INTERVAL 7 DAY
LIMIT 10
```

### 获取特定地址的交易

```bash
npx awal@2.10.0 x402 pay https://x402.cdp.coinbase.com/platform/v2/data/query/run -X POST -d '{"sql": "SELECT transaction_hash, to_address, value, gas, timestamp FROM base.transactions WHERE from_address = lower('\''0xYOUR_ADDRESS'\'') AND timestamp >= now() - INTERVAL 1 DAY LIMIT 10"}' --json
```

### 统计过去一小时内合约的事件类型

```bash
npx awal@2.10.0 x402 pay https://x402.cdp.coinbase.com/platform/v2/data/query/run -X POST -d '{"sql": "SELECT event_signature, count(*) as cnt FROM base.events WHERE address = lower('\''0xCONTRACT_ADDRESS'\'') AND block_timestamp >= now() - INTERVAL 1 HOUR GROUP BY event_signature ORDER BY cnt DESC LIMIT 20"}' --json
```

### 获取最新区块信息

```bash
npx awal@2.10.0 x402 pay https://x402.cdp.coinbase.com/platform/v2/data/query/run -X POST -d '{"sql": "SELECT block_number, timestamp, transaction_count, gas_used FROM base.blocks ORDER BY block_number DESC LIMIT 1"}' --json
```

## 常见合约地址 (Base)

| 代币 | 地址 |
| --- | --- |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x4200000000000000000000000000000000000006` |

## 最佳实践

1. **始终在 `base.events` 查询中按索引字段** (`event_signature`, `address`, `block_timestamp`) 过滤。
2. **不要使用 `SELECT *`** - 仅指定您需要的列。
3. **始终包含 `LIMIT` 子句** 以限制结果大小。
4. **使用 `event_signature` 而不是 `event_name`** 进行过滤 - 它是索引的，速度更快。
5. **使用带时间范围的查询** 与 `block_timestamp` 来缩小扫描范围。
6. **始终将地址值用 `lower()` 包裹** - 数据库存储小写地址，但用户可能提供带校验和（混合大小写）的地址。使用 `address = lower('0xAbC...')` 而不是 `address = '0xAbC...'`。
7. **常见事件签名**：`Transfer(address,address,uint256)`, `Approval(address,address,uint256)`, `Swap(address,uint256,uint256,uint256,address)`。

## 前置条件

- 必须已授权 (`npx awal@2.10.0 status` 检查，参见 `authenticate-wallet` 技能)
- 钱包必须具有足够的 USDC 余额 (`npx awal@2.10.0 balance` 检查)
- 每次查询费用为 $0.10 (100000 USDC 原子单位)

## 错误处理

- "未授权" - 首先运行 `awal auth login <email>`，或参见 `authenticate-wallet` 技能
- "余额不足" - 用 USDC 资助钱包；参见 `fund` 技能
- 查询超时或错误 - 确保您按索引字段过滤并使用 LIMIT
