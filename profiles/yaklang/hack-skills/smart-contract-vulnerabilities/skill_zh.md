# 技能：智能合约漏洞——专家攻击手册

> **AI 加载指令**：专家级智能合约审计技术。涵盖重入（单函数、跨函数、跨合约、只读）、整数溢出、访问控制、delegatecall、随机性操纵、闪电贷、签名重放、前端运行/MEV 以及 CREATE2 利用。基础模型会遗漏代理模式中的微妙跨合约重入和存储布局冲突。

## 0. 相关路由

- [defi-attack-patterns](../defi-attack-patterns/SKILL.md) 当漏洞是 DeFi 协议漏洞的一部分（闪电贷、预言机操纵、治理攻击）
- [deserialization-insecure](../deserialization-insecure/SKILL.md) 当目标是链下基础设施反序列化区块链数据

### 高级参考

当您需要时，也加载 [SOLIDITY_VULN_PATTERNS.md](./SOLIDITY_VULN_PATTERNS.md)：
- 每个漏洞类别的易受攻击代码与修复代码的并排模式
- 引入漏洞的 Gas 优化陷阱
- 代理模式存储冲突示例及槽位计算

---

## 1. 重入

最经典的智能合约漏洞。外部调用会转移执行控制；如果状态在调用之前未更新，被调用者可以重入。

### 1.1 经典重入（单函数）

```
Victim.withdraw()
  ├── 检查 balance[msg.sender] > 0          ✓
  ├── msg.sender.call{value: balance}("")     ← 外部调用
  │   └── Attacker.receive()
  │       └── Victim.withdraw()               ← 在状态更新之前重入
  │           ├── 检查 balance[msg.sender]   ← 仍然 > 0！
  │           └── 再次发送 ETH
  └── balance[msg.sender] = 0                 ← 太晚了
```

### 1.2 跨函数重入

两个函数共享状态；攻击者在回调期间重入不同的函数：

| 步骤 | 执行 | 状态 |
|---|---|---|
| 1 | 调用 `withdraw()` → 外部调用 | balance 仍然为正 |
| 2 | Attacker fallback 调用 `transfer(attacker2)` | 在重置 balance 之前使用 balance |
| 3 | `transfer` 读取陈旧 balance → 转移资金 | attacker2 接收代币 |
| 4 | 原始 `withdraw` 完成，将 balance 归零 | 损害已造成 |

### 1.3 跨合约重入

合约 A 调用合约 B，合约 B 回调到合约 A（或读取 A 的陈旧状态的合约 C）。在 DeFi 协议中尤其危险，因为多个合约共享状态。

### 1.4 只读重入

被重入的函数是一个 `view` 函数，由第三方合约用于价格计算。受害者中没有状态修改，但陈旧的中介状态误导了读者。

**现实案例**：Curve 池 `get_virtual_price()` 在 `remove_liquidity()` 回调期间读取 → 价格被夸大 → 依赖的借贷协议获利。

### 缓解措施

| 模式 | 保护级别 |
|---|---|
| 检查-效果-交互 (CEI) | 核心防御；在调用外部函数之前更新状态 |
| `ReentrancyGuard` (OpenZeppelin) | 互斥锁；防止同一事务重入 |
| 提取支付模式 | 在状态更改函数中消除外部调用 |
| 所有公共函数的 CEI + 保护 | 防御深度防御，防止跨函数 |

---

## 2. 整数溢出 / 溢出

### 预 Solidity 0.8

算术操作会静默地回绕：`uint8(255) + 1 == 0`，`uint8(0) - 1 == 255`。

| 攻击 | 示例 |
|---|---|
| 平衡下溢 | `balances[attacker] -= amount` 当 amount > balance → 巨大的 balance |
| 供应溢出 | `totalSupply + mintAmount` 回绕 → 绕过上限检查 |
| 时间锁绕过 | `lockTime[msg.sender] + extend` 回绕到过去 → 提前解锁 |

### Solidity 0.8 之后

默认检查算术溢出会导致溢出时回滚。但 `unchecked{}` 块会重新引入风险：

```solidity
unchecked {
    // "Gas 优化" — 但如果我可以被用户输入影响，溢出会返回
    for (uint i = start; i < end; i++) { ... }
}
```

### SafeMath 绕过场景

- 强制转换：`uint256` → `uint128` 在 SafeMath 检查之前截断
- 汇编块：`mstore` / `add` 绕过 Solidity 级别的检查
- 中间乘法溢出：`(a * b) / c` 其中 `a * b` 溢出

---

## 3. 访问控制

### tx.origin vs msg.sender

| 属性 | `msg.sender` | `tx.origin` |
|---|---|---|
| 值 | 直接调用者 | 发起事务的 EOA |
| 安全性 | 是 | **否** — 仿射合约可以继承 tx.origin |

攻击：诱骗所有者调用攻击者合约 → 攻击者合约使用所有者的 `tx.origin` 调用受害者。

### 常见模式

| 问题 | 影响 |
|---|---|
| 关键函数缺少 `onlyOwner` | 任何人都可以调用管理员函数 |
| 未保护的 `selfdestruct` | 任何人都可以销毁合约，强制发送 ETH |
| 未保护的 `delegatecall` | 攻击者在受害者的上下文中执行任意代码 |
| 默认可见性（预 0.6.0） | 函数默认为 `public` |
| 缺少零地址检查 | 所有权转移到 `address(0)` |

---

## 4. 随机性操纵

链上随机性源对矿工/验证者是可预测的：

| 源 | 可预测性 |
|---|---|
| `block.timestamp` | 矿工有 ~15 秒的时间操纵 |
| `blockhash(block.number - 1)` | 在执行时所有已知 |
| `blockhash(block.number)` | 总是返回 0（当前区块哈希未知） |
| `block.difficulty` / `block.prevrandao` | 合并后：已知的 beacon 链值 |

**提交-揭示绕过**：如果揭示阶段不强制执行超时或保证金，攻击者可以选择不揭示不利结果（选择性中止攻击）。

---

## 5. delegatecall 漏洞

`delegatecall` 在调用者的存储上下文中执行被调用者的代码。存储槽布局必须完全匹配。

### 存储布局冲突

```
代理（存储）：         实现（代码）：
槽 0：owner            槽 0：someVariable
槽 1：implementation   槽 1：anotherVariable
```

实现写入 `someVariable`（槽 0）→ 覆盖代理的 `owner`。攻击者调用实现函数写入槽 0 → 成为代理所有者。

### 函数选择器冲突

4 字节函数选择器可能会冲突。如果代理的 `admin()` 选择器与实现的 `transfer()` 选择器冲突，在代理上调用 `admin()` 会执行 `transfer()` 逻辑。

工具：`cast selectors <bytecode>`（Foundry）来枚举选择器。

---

## 6. 前端运行 / MEV

### 交易排序操纵

```
Victim 提交 DEX 交换事务（可见在 mempool）
├── Front-runner：在 victim 之前购买代币（提高价格）
├── Victim tx 在更差的价格执行
└── Back-runner：在 victim 之后出售代币（从价差中获利）
= 三明治攻击
```

### 保护模式

| 防御 | 机制 |
|---|---|
| 提交-揭示 | 隐藏交易意图直到揭示 |
| Flashbots / 私有 mempool | 直接将 tx 提交给区块构建者 |
| 滑动保护 | 设置 `minAmountOut` 限制 MEV 提取 |
| 时间锁 | 延迟执行以降低可预测性 |

---

## 7. 签名重放

### 缺少 Nonce

重复使用有效签名来重复执行操作（例如，转移）多次。

### 跨链重放

相同合约在多个链上部署使用相同地址 → 签名在所有链上都有效。必须在签名消息中包含 `block.chainid`。

### EIP-712 实现错误

| 错误 | 后果 |
|---|---|
| 缺少 `DOMAIN_SEPARATOR` 与 chainId | 跨链重放 |
| 部署时缓存的域分隔符 | 在改变 chainId 的硬分叉后失效 |
| 结构哈希中缺少 nonce | 签名重放 |
| `ecrecover` 在无效签名上返回 `address(0)` | 通过 `== address(0)` 所有者检查 |

---

## 8. self-destruct & 强制发送 ETH

`selfdestruct(recipient)` 强制将所有合约 ETH 发送到 recipient — 绕过 `receive()` 和 `fallback()`，无法拒绝。

破坏依赖 `address(this).balance` 进行逻辑的合约（例如，`require(balance == expected)`）。

Post-EIP-6780 (Dencun)：`selfdestruct` 只发送 ETH；代码/存储删除仅在创建事务中调用时发生。

---

## 9. CREATE2 & 确定性地址利用

`CREATE2` 地址 = `keccak256(0xff ++ deployer ++ salt ++ keccak256(initCode))`。

| 攻击 | 方法 |
|---|---|
| 预资助利用 | 预测地址 → 在部署之前发送代币/ETH → `selfdestruct` → 在相同地址重新部署不同代码 |
| 预批准利用 | 预测地址获得代币批准 → 部署恶意合约 → 排空批准的代币 |
| 变形合约 | `CREATE2` → `selfdestruct` → 使用相同 salt 但不同 `initCode` 的 `CREATE2`（预 EIP-6780） |

---

## 10. 闪电贷攻击模式

```
单笔交易：
├── 借入大量金额（无抵押）
├── 操纵状态（价格预言机、治理等）
├── 从操纵状态中提取利润
├── 偿还贷款 + 费用
└── 保留利润
```

关键：整个序列必须原子性地成功，否则整个事务会回滚。

---

## 11. 短地址攻击

EVM 用零填充 ABI 编码的 calldata 中缺失的字节。如果 `transfer(address, uint256)` 被调用时使用 19 字节地址，uint256 金额会向左移 8 位 → 乘以 256。

缓解措施：验证 calldata 长度；现代 Solidity 编译器会添加检查。

---

## 12. 工具

| 工具 | 目的 | 使用 |
|---|---|---|
| Slither | 静态分析，漏洞检测 | `slither .` 在项目根目录 |
| Mythril | 符号执行，路径探索 | `myth analyze contract.sol` |
| Echidna | 基于属性的模糊测试 | 定义不变量，模糊测试违规 |
| Foundry (Forge) | 测试框架，模糊测试，Gas 分析 | `forge test --fuzz-runs 10000` |
| Hardhat | 开发，测试，部署 | `npx hardhat test` |
| Certora | 形式验证 | 编写规范，证明/反驳属性 |
| 4naly3er | 自动 Gas 优化 + 漏洞报告 | CI 集成 |

---

## 13. 决策树

```
审计智能合约？
├── 它是代理模式吗？
│   ├── 是 → 检查存储布局冲突（第 5 节）
│   │   ├── 比较代理和实现之间的槽位分配
│   │   ├── 检查函数选择器冲突
│   │   └── 验证初始化器不能被调用两次
│   └── 否 → 继续
├── 它进行外部调用吗？
│   ├── 是 → 检查重入（第 1 节）
│   │   ├── 状态在调用之前更新？ → CEI 模式 OK
│   │   ├── ReentrancyGuard 存在？ → 检查所有入口点
│   │   ├── 跨函数状态共享？ → 跨函数重入风险
│   │   └── 视图函数在回调期间读取？ → 只读重入
│   └── 否 → 继续
├── 它处理代币/ETH 吗？
│   ├── 是 → 检查整数溢出（第 2 节）
│   │   ├── Solidity < 0.8？ → 所有算术可疑
│   │   ├── unchecked{} 块？ → 验证没有受用户输入影响的值
│   │   └── 在 uint 大小之间强制转换？ → 截断风险
│   └── 也检查 self-destruct 强制发送（第 8 节）
├── 它使用签名吗？
│   ├── 是 → 检查重放（第 7 节）
│   │   ├── 包含 Nonce？ → 验证增量
│   │   ├── 包含 ChainId？ → 跨链安全
│   │   └── 检查 ecrecover 结果是否为 address(0)？ → OK
│   └── 否 → 继续
├── 它使用链上随机性吗？
│   ├── 是 → 可预测（第 4 节）
│   │   └── 建议 Chainlink VRF 或带保证金的提交-揭示
│   └── 否 → 继续
├── 它与 DeFi 协议交互吗？
│   ├── 是 → 加载 [defi-attack-patterns](../defi-attack-patterns/SKILL.md)
│   │   ├── 闪电贷向量
│   │   ├── 预言机操纵
│   │   └── MEV 暴露
│   └── 否 → 继续
├── 它使用 CREATE2 吗？
│   ├── 是 → 检查确定性地址利用（第 9 节）
│   └── 否 → 继续
└── 运行自动化工具（第 12 节）
    ├── Slither 进行静态分析
    ├── Mythril 进行符号执行
    └── Echidna 在不变量上进行模糊测试
```
