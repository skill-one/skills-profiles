# 💰 钱包技能

多链钱包，支持 EVM（DeBank 支持的链）+ Solana。余额、转账、签名和政策管理。**脚本技能** — 通过 bash 调用以下功能；未注册钱包工具。

## 如何调用

所有读取/转账/签名操作都是 `core.skill_tools.wallet` 中的 Python 函数。从 bash 中运行它们并读取 JSON 结果：

```bash
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_balance(chain='base')))"
```

**唯一**一个不是脚本函数的操作是提议钱包政策 — 它需要在 UI 中渲染确认卡，因此它通过原生 `frontend_action` 工具（见下文政策管理）。

## 函数 (`from core.skill_tools import wallet`)

| 函数 | 描述 |
|------|------|
| `wallet_info()` | 获取所有 AGENT 钱包地址 |
| `get_user_wallets()` | 用户自己的钱包（登录 + 二级） — 只读，从环境变量获取 |
| `wallet_balance(chain, address="", asset="")` | 链上 EVM 余额（DeBank）。`chain` 必须提供 |
| `wallet_sol_balance(address="", asset="")` | Solana 余额（Birdeye） |
| `wallet_get_all_balances(evm_address="", sol_address="")` | 所有链一次性获取 |
| `wallet_transfer(to, amount, chain_id=1, data="", **kw)` | **广播** EVM 交易 (gas 默认由平台赞助) |
| `wallet_sign_transaction(to, amount, chain_id=1, data="", **kw)` | 签名 EVM 交易 (不广播) |
| `wallet_sign(message)` | EIP-191 消息签名 |
| `wallet_sign_typed_data(domain, types, primaryType, message)` | EIP-712 类型数据签名 |
| `wallet_transactions(chain="ethereum", asset="", limit=20)` | EVM 交易历史 |
| `wallet_sol_transfer(transaction, caip2=...)` | **广播** Solana 交易 (base64) |
| `wallet_sol_sign_transaction(transaction)` | 签名 Solana 交易 (不广播) |
| `wallet_sol_sign(message)` | Solana 消息签名 |
| `wallet_sol_transactions(chain="solana", asset="sol", limit=20)` | Solana 交易历史 |
| `wallet_get_policy(chain_type="ethereum")` | 检查政策状态 |
| `validate_and_clean_rules(rules, chain_type)` | 在提议政策规则之前预先验证 |

## 用户自己的钱包（登录 / 二级）

代理钱包不是用户的钱包。平台将用户自己的钱包身份作为环境变量注入（在容器启动时和用户钱包操作时与控制平面同步）：

- `USER_LOGIN_WALLET_ADDRESS` / `USER_LOGIN_WALLET_TYPE` — 用户登录时使用的钱包（或绑定为主钱包）。
- `USER_SECONDARY_WALLET_ADDRESS` / `USER_SECONDARY_WALLET_TYPE` — 用户的其它已链接钱包（例如，登录为 EVM 时是 Solana）。

当被问及“我的钱包是什么” / “我的登录钱包” / “检查我的余额”时，读取这些 — 不要回答代理钱包或表示不知道：

```bash
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.get_user_wallets()))"
```

空值/缺失值表示用户从未在该位置绑定钱包（例如，社交登录） — 这样说并引导他们到 Web 应用的钱包绑定。

规则：
- **只读。** 代理不持有这些钱包的密钥。要检查用户的余额，将地址传递给 `wallet_balance(chain, address=...)` / `wallet_sol_balance(address=...)`。
- **来自用户钱包的交易** 从不通过脚本函数 — 使用原生的 `frontend_action(action_type="user_wallet_tx", ...)` 流程，用户在 UI 中签名，`expected_from` 在服务器端强制执行。

## 关键事实

- **EVM 金额以 wei 为单位** (`wallet_transfer` / `wallet_sign_transaction`)。0.01 ETH = `10000000000000000`。对于 ERC-20 代币发送，`amount` 为 `0`（原生），转账在 `data` calldata 中编码。
- **EVM 链上默认赞助 gas** — 用户不需要原生代币支付 gas。如果不可用，则回退到用户支付。传递 `sponsor=False` 从钱包余额支付 gas。
- **政策默认：关闭**（允许所有）。只有当政策启用时，交易才需要 UI 确认。
- **支持的 EVM 链**：所有 DeBank 支持的链。常见名称自动映射（例如 `avalanche` → `avax`，`bsc` → `bsc`，`zksync` → `era`）。回退别名包括 ethereum/base/arbitrum/optimism/polygon/linea/bsc/avalanche/fantom/gnosis/zksync/scroll/blast/mantle/celo/aurora **以及** monad/world/unichain/abstract/sonic/berachain。
- **余额来源**：DeBank (EVM)，Birdeye (Solana)，wallet-service (回退)。DeBank/Birdeye 密钥由 sc-proxy 自动注入。

## 工作流程

### 检查余额
```bash
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_balance(chain='base')))"
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_get_all_balances()))"
```

### 发送交易 (EVM)
始终在之前验证余额，并在之后验证结果/历史。
```bash
# 1. 检查
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_balance(chain='base')))"
# 2. 转账 (金额以 wei 为单位)
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_transfer(to='0x...', amount='10000000000000000', chain_id=8453)))"
# 3. 验证
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_transactions(chain='base')))"
```

### 签名 EIP-712 类型数据
```bash
python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_sign_typed_data(domain={...}, types={...}, primaryType='Permit', message={...})))"
```

## 政策管理

检查政策是脚本函数；**提议**政策使用原生 `frontend_action` 工具（它在 UI 中渲染签名卡 — 脚本无法执行）。

1. 检查当前政策：
   ```bash
   python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.wallet_get_policy(chain_type='ethereum')))"
   ```
2. （可选）预验证规则：
   ```bash
   python3 -c "from core.skill_tools import wallet; import json; print(json.dumps(wallet.validate_and_clean_rules([...], 'ethereum')))"
   ```
3. 提议 — 调用**`frontend_action` 工具**（不是脚本）：
   ```
   frontend_action(action_type="update_wallet_policy", chain_type="ethereum", rules=[...])
   ```
   用户确认并在 UI 中签名。**每个链调用一次**（EVM + Solana = 两次调用）。

### 标准通配符政策（需要时）
```
rules = [
  {"name": "拒绝密钥导出", "method": "exportPrivateKey", "conditions": [], "action": "DENY"},
  {"name": "允许所有", "method": "*", "conditions": [], "action": "ALLOW"},
]
```

### 政策模式 — 关键决策表

⚠️ **Privy 中 DENY > ALLOW。`DENY *` 会覆盖所有 ALLOW 规则。永远不要混合它们。**

| 模式 | 规则 | 效果 |
|------|------|------|
| **允许所有**（默认） | `DENY exportPrivateKey` + `ALLOW *` | 允许所有操作，除了密钥导出 |
| **拒绝所有**（锁定） | `DENY exportPrivateKey` + `DENY *` | 什么也不工作。没有 ALLOW 规则！ |
| **白名单**（选择性） | `DENY exportPrivateKey` + 仅特定 ALLOW 规则 | 只有白名单的操作有效，其余隐式拒绝 |

### 模式 1：允许所有（标准通配符）
```
rules = [
  {"name": "拒绝密钥导出", "method": "exportPrivateKey", "conditions": [], "action": "DENY"},
  {"name": "允许所有", "method": "*", "conditions": [], "action": "ALLOW"},
]
```

### 模式 2：拒绝所有（锁定）
```
rules = [
  {"name": "拒绝密钥导出", "method": "exportPrivateKey", "conditions": [], "action": "DENY"},
  {"name": "拒绝所有操作", "method": "*", "conditions": [], "action": "DENY"},
]
# ⚠️ 这里没有 ALLOW 规则 — DENY * 会覆盖它们！
```

### 模式 3：白名单（选择性允许）
```
rules = [
  {"name": "拒绝密钥导出", "method": "exportPrivateKey", "conditions": [], "action": "DENY"},
  {"name": "允许转账到 Uniswap", "method": "eth_sendTransaction", "conditions": [
    {"field_source": "ethereum_transaction", "field": "to", "operator": "eq", "value": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913"}
  ], "action": "ALLOW"},
]
# ⚠️ 这里没有 "DENY *"！enabled=true 已经拒绝所有未明确 ALLOW 的操作。
# 添加 DENY * 会覆盖上面的 ALLOW 规则（DENY > ALLOW）。
```

## Privy 政策规则 — 关键约束

| 规则 | 详情 |
|------|------|
| **默认行为** | `enabled=true` → 拒绝所有，除非明确 ALLOW |
| **DENY > ALLOW** | DENY 总是优先于 ALLOW |
| **空条件** | 只有 `exportPrivateKey` 和 `*`（通配符）允许 `conditions: []` |
| **交易方法需要条件** | `eth_sendTransaction`，`eth_signTransaction`，`eth_signTypedData_v4`，`eth_signUserOperation`，`signAndSendTransaction` 等。所有这些都需要 ≥1 个条件 |
| **有效的 field_sources** | EVM: `ethereum_transaction`（to/value/chain_id），`ethereum_calldata`（function_name），`ethereum_typed_data_domain`（chainId/verifyingContract），`ethereum_typed_data_message`，`system` |
| **有效的运算符** | `eq`，`gt`，`gte`，`lt`，`lte`，`in`（数组，最多 100 个值） |
| **双链** | 调用 `frontend_action(action_type="update_wallet_policy", ...)` 两次（每个链类型一次） |

## 注意事项

- 政策提议通过 `frontend_action` 工具 — 需要活跃的 SSE 会话（背景任务中无法工作）。
- `wallet_balance` 需要 `chain` — 使用 `wallet_get_all_balances` 进行发现。
- 对于 EVM + Solana 政策，调用 `frontend_action` 两次（每个链类型一次）。
