# Token 集成分析器

## 目的

使用 Trail of Bits 的 token 集成清单，系统性地分析代码库中的 token 相关安全问题：

1. **Token 实现**：分析您的 token 是否遵循 ERC20/ERC721 标准，或具有非标准行为
2. **Token 集成**：分析您的协议如何处理任意 token，包括奇怪的/非标准的 token
3. **链上分析**：查询已部署合约的稀缺性、分配和配置
4. **安全评估**：识别来自 20+ 已知的奇怪 token 模式的风险

**框架**：构建安全合约 - Token 集成清单 + 奇怪 ERC20 数据库

---

## 工作原理

### 第一阶段：上下文发现
确定分析上下文：
- **Token 实现**：您是否正在构建一个 token 合约？
- **Token 集成**：您的协议是否与外部 token 交互？
- **平台**：以太坊、其他 EVM 链或不同平台？
- **Token 类型**：ERC20、ERC721 或两者？

### 第二阶段：Slither 分析（如果使用 Solidity）
对于 Solidity 项目，我将帮助运行：
- `slither-check-erc` - ERC 一致性检查
- `slither --print human-summary` - 复杂性和升级分析
- `slither --print contract-summary` - 函数分析
- `slither-prop` - 为测试生成属性

### 第三阶段：代码分析
分析：
- 合约组成和复杂性
- 所有者权限和集中化风险
- ERC20/ERC721 一致性
- 已知的奇怪 token 模式
- 集成安全模式

### 第四阶段：链上分析（如果已部署）
如果您提供合约地址，我将查询：
- Token 稀缺性和分配
- 总供应量和持有者集中度
- 交易所上市情况
- 链上配置

### 第五阶段：风险评估
提供：
- 已识别的漏洞
- 非标准行为
- 集成风险
- 优先级建议

---

## 评估类别

我检查 10 个全面的类别，涵盖 token 安全的所有方面。有关详细标准、模式和清单，请参阅 [ASSESSMENT_CATEGORIES.md](resources/ASSESSMENT_CATEGORIES.md)。

### 快速参考：

1. **一般考虑** - 安全审核、团队透明度、安全联系方式
2. **合约组成** - 复杂性分析、SafeMath 使用、函数数量、入口点
3. **所有者权限** - 可升级性、铸造、暂停、黑名单、团队问责制
4. **ERC20 一致性** - 返回值、元数据、小数位数、竞态条件、Slither 检查
5. **ERC20 扩展风险** - 外部调用/钩子、转账费用、重铸/收益型 token
6. **Token 稀缺性分析** - 供应分配、持有者集中度、交易所分配、闪电贷/铸造风险
7. **奇怪 ERC20 模式**（包括 24 种模式）：
   - 重入调用（ERC777 钩子）
   - 缺少返回值（USDT、BNB、OMG）
   - 转账费用（STA、PAXG）
   - 转账外余额修改（Ampleforth、Compound）
   - 可升级 token（USDC、USDT）
   - 闪电可铸造（DAI）
   - 黑名单（USDC、USDT）
   - 可暂停 token（BNB、ZIL）
   - 授权竞态保护（USDT、KNC）
   - 授权/转账到零地址时回滚
   - 零值授权/转账时回滚
   - 多个 token 地址
   - 低小数位数（USDC: 6, Gemini: 2）
   - 高小数位数（YAM-V2: 24）
   - `transferFrom` 中 `src == msg.sender`
   - 非字符串元数据（MKR）
   - 失败时不回滚（ZRX、EURS）
   - 大额授权时回滚（UNI、COMP）
   - 通过 token 名称进行代码注入
   - 不寻常的 permit 函数（DAI、RAI、GLM）
   - 转账金额小于数量（cUSDCv3）
   - ERC-20 本地货币表示（Celo、Polygon、zkSync）
   - [更多...](resources/ASSESSMENT_CATEGORIES.md#7-weird-erc20-patterns)
8. **Token 集成安全** - 安全转账模式、余额验证、白名单、包装器、防御模式
9. **ERC721 一致性** - 转账到 0x0、safeTransferFrom、元数据、ownerOf、授权清除、token ID 不可变性
10. **ERC721 常见风险** - onERC721Received 重入、安全铸造、销毁授权清除

---

## 示例输出

分析完成后，您将收到一个结构化的综合报告，如下所示：

```
=== TOKEN 集成分析报告 ===

项目：MultiToken DEX
分析的 Token：自定义奖励 Token + 集成安全
平台：Solidity 0.8.20
分析日期：2024 年 3 月 15 日

---

## 执行摘要

Token 类型：ERC20 实现 + 协议集成外部 Token
整体风险级别：中等
严重问题：2
高优先级问题：3
中等优先级问题：4

**主要关注点：**
⚠ 转账费用 Token 处理不当
⚠ 未对缺少返回值进行验证（USDT 兼容性）
⚠ 所有者可以无限制铸造 token 而无上限

**建议**：在主网上线前解决严重/高优先级问题。

---

## 1. 一般考虑

✓ 合约由 CertiK 审计（2023 年 6 月）
✓ 可通过 security@project.com 联系团队
✗ 没有安全邮件列表用于发布关键公告

**风险**：用户不会收到关键问题通知
**行动**：建立 security@project.com 邮件列表

---

## 2. 合约组成

### 复杂性分析

**Slither human-summary 结果：**
- 456 行代码
- 圈复杂度：平均 6，最大 14（transferWithFee()）
- 12 个函数，8 个状态变量
- 继承深度：3（中等）

✓ 合约复杂性合理
⚠ transferWithFee() 复杂度高（14）- 考虑拆分

### SafeMath 使用

✓ 使用 Solidity 0.8.20（内置溢出保护）
✓ 未发现未检查的块
✓ 所有算术操作受保护

### 非Token 函数

**超出 ERC20 的函数：**
- setFeeCollector() - 管理员函数 ✓
- setTransferFee() - 管理员函数 ✓
- withdrawFees() - 管理员函数 ✓
- pause()/unpause() - 紧急函数 ✓

⚠ 4 个非 token 函数（可接受但增加了复杂性）

### 地址入口点

✓ 单个合约地址
✓ 没有使用多个入口点的代理
✓ 没有token迁移导致地址混淆

**状态**：通过

---

## 3. 所有者权限

### 可升级性

⚠ 合约使用 TransparentUpgradeableProxy
**风险**：所有者可以随时更改合约逻辑

**当前实现：**
- ProxyAdmin: 0x1234...（2/3 多签）✓
- Timelock: 无 ✗

**建议**：为所有升级添加 48 小时时间锁

### 铸造能力

❌ 严重问题：无限制铸造
文件：contracts/RewardToken.sol:89
```solidity
function mint(address to, uint256 amount) external onlyOwner {
    _mint(to, amount);  // 无上限！
}
```

**风险**：所有者可以任意增加供应
**修复**：添加最大供应上限或速率限制铸造

### 暂停功能

✓ 已实现暂停模式（OpenZeppelin）
✓ 只有所有者可以暂停
⚠ 暂停状态会影响所有转账（包括现有持有人）

**风险**：所有者可以冻结所有用户资金
**缓解**：使用多签暂停函数（已实现 ✓）

### 黑名单

✗ 没有黑名单功能
**评估**：良好 - 没有集中化审查风险

### 团队透明度

✓ 团队成员公开（team.md）
✓ 公司注册在瑞士
✓ 责任且可联系

**状态**：可接受

---

## 4. ERC20 一致性

### slither-check-erc 结果

命令：slither-check-erc . RewardToken --erc erc20

✓ transfer 返回 bool
✓ transferFrom 返回 bool
✓ name、decimals、symbol 存在
✓ decimals 返回 uint8（值：18）
✓ 竞态条件已缓解（increaseAllowance/decreaseAllowance）

**状态**：完全符合

### slither-prop 测试结果

命令：slither-prop . --contract RewardToken

**生成 12 个属性，全部通过：**
✓ 转账不会改变总供应量
✓ 授权正确更新
✓ 余额更新与转账金额匹配
✓ 不可能进行余额操作
[... 8 个更多属性 ...]

**Echidna 模糊测试**：50,000 次运行，无违规 ✓

**状态**：优秀

---

## 5. 奇怪 Token 模式分析

### 集成安全检查

**您的协议集成 5 个外部 Token：**
1. USDT (0xdac17f9...)
2. USDC (0xa0b86991...)
3. DAI (0x6b175474...)
4. WETH (0xc02aaa39...)
5. UNI (0x1f9840a8...)

### 发现的关键问题

❌ **模式 7.2：缺少返回值**
**发现于**：USDT 集成
文件：contracts/Vault.sol:156
```solidity
IERC20(usdt).transferFrom(msg.sender, address(this), amount);
// 没有返回值检查！USDT 不返回 bool
```

**风险**：USDT 转账时出现静默失败
**利用**：用户看似存款，但 token 未实际转移
**修复**：使用 OpenZeppelin SafeERC20 包装器

---

❌ **模式 7.3：转账费用**
**风险**：任何具有转账费用的 token
文件：contracts/Vault.sol:170
```solidity
uint256 balanceBefore = IERC20(token).balanceOf(address(this));
token.transferFrom(msg.sender, address(this), amount);
shares = amount * exchangeRate;  // 错误！应使用实际接收的金额
```

**风险**：如果 token 收取费用，会计不匹配
**利用**：用户获得的份额多于存款的 token
**修复**：从 `balanceAfter - balanceBefore` 计算份额

---

### 已知非标准 Token 处理

✓ **USDC**：正确处理（SafeERC20，6 位小数已考虑）
⚠ **DAI**：未使用 permit() 函数（有机会节省 gas）
✗ **USDT**：未处理缺少返回值（严重问题）
✓ **WETH**：标准包装器，正确处理
⚠ **UNI**：未检查大额授权处理（回滚 >= 2^96）

---

[... 其他分析类别的附加部分 ...]
```

有关完整报告模板和交付格式，请参阅 [REPORT_TEMPLATES.md](resources/REPORT_TEMPLATES.md)。

---

## 理由说明（不要跳过）

| 理由说明 | 为什么这是错误的 | 必要行动 |
|-----------------|-----------------|-----------------|
| "Token 看起来标准，ERC20 检查通过" | 存在 20+ 奇怪 token 模式，超出 ERC20 合规性 | 检查数据库中的所有奇怪 token 模式（缺少返回值、回滚到零、钩子等） |
| "Slither 显示没有问题，集成是安全的" | Slither 检测到某些模式，但遗漏了集成逻辑 | 完成所有 5 个 token 集成标准的手动分析 |
| "未检测到转账费用，跳过该检查" | 转账费用可以是所有者控制或条件性的 | 测试所有转账场景，检查条件费用逻辑 |
| "余额检查存在，处理是安全的" | 余额检查本身不能保护所有奇怪 token | 验证安全转账包装器、回滚处理、授权模式 |
| "Token 由信誉良好的团队部署，假设标准" | 信誉不能保证标准行为 | 分析实际代码和链上行为，不要依赖假设 |
| "集成使用 OpenZeppelin，一定是安全的" | OpenZeppelin 库不能保护所有外部奇怪 token | 验证所有外部 token 调用周围的防御模式 |
| "无法运行 Slither，跳过自动分析" | Slither 提供关键 ERC 一致性检查 | 手动验证所有 slither-check-erc 标准，或记录阻止原因 |
| "这个模式看起来没问题" | 直觉会遗漏 token 集成中的细微错误 | 系统地检查所有 20+ 奇怪 token 模式，附带代码证据 |

---

## 交付物

分析完成后，我将提供：

1. **合规性清单** - 所有评估类别的复选框
2. **奇怪 Token 模式分析** - 所有 24 种模式的存在/不存在，风险级别和证据
3. **链上分析报告**（如果适用）- 持有者分配、交易所上市情况、配置
4. **集成安全评估**（如果适用）- 安全转账使用、防御模式、奇怪 token 处理
5. **优先级建议** - 严重/高/中/低问题，具体修复措施

完整交付物模板可在 [REPORT_TEMPLATES.md](resources/REPORT_TEMPLATES.md) 中找到。

---

## 准备开始

**我需要**：
- 您的代码库
- 上下文：Token 实现 或 集成？
- Token 类型：ERC20、ERC721 或两者？
- 合约地址（如果已部署且希望进行链上分析）
- RPC 端点（如果查询链上）

让我们分析您的 token 实现 或 集成中的安全风险！
