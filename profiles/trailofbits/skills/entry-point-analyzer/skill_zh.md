# 入口点分析器

系统性地识别智能合约代码库中所有**状态改变**的入口点，以指导安全审计。

## 使用场景

在以下情况下使用此技能：
- 开始智能合约安全审计以映射攻击面
- 被要求查找入口点、外部函数或审计流程
- 分析代码库中的访问控制模式
- 识别特权操作和角色限制函数
- 建立对哪些函数可以修改合约状态的理解

## 不适用场景

不使用此技能用于：
- 漏洞检测（使用 audit-context-building 或 domain-specific-audits）
- 编写利用 POC（使用 solidity-poc-builder）
- 代码质量或 gas 优化分析
- 非智能合约代码库
- 分析只读函数（此技能排除它们）

## 范围：仅限状态改变函数

此技能专注于仅分析可以修改状态的函数。**排除：**

| 语言 | 排除模式 |
|----------|-------------------|
| Solidity | `view`, `pure` 函数 |
| Vyper | `@view`, `@pure` 函数 |
| Solana | 没有 `mut` 账户引用的函数 |
| Move | 非入口 `public fun`（仅模块可调用） |
| TON | `get` 方法（FunC）、只读接收器（Tact） |
| CosmWasm | `query` 入口点及其处理程序 |

**为何排除只读函数？** 它们不能直接导致资金损失或状态损坏。虽然它们可能会泄露信息，但主要审计重点在于可以改变状态的函数。

## 工作流程

1. **检测语言** - 通过文件扩展名和语法识别合约语言
2. **使用工具（如果可用）** - 对于 Solidity，检查 Slither 是否可用并使用它
3. **定位合约** - 查找所有合约/模块文件（如果指定，则应用目录过滤器）
4. **提取入口点** - 解析每个文件以查找外部可调用、状态改变的函数
5. **分类访问** - 根据访问级别对每个函数进行分类
6. **生成报告** - 输出结构化的 markdown 报告

## Slither 集成（Solidity）

对于 Solidity 代码库，Slither 可以自动提取入口点。在进行手动分析之前：

### 1. 检查 Slither 是否可用

```bash
which slither
```

### 2. 如果检测到 Slither，运行入口点打印器

```bash
slither . --print entry-points
```

这将输出所有状态改变入口点的表格，包括：
- 合约名称
- 函数名称
- 可见性
- 应用的修饰符

### 3. 使用 Slither 输出作为基础

- 解析 Slither 输出表格以填充您的分析
- 与手动检查进行交叉引用以进行访问控制分类
- Slither 可能会遗漏某些模式（回调、动态访问控制）—补充手动检查
- 如果 Slither 失败（编译错误、不支持的特性），则回退到手动分析

### 4. 当 Slither 不可用时

如果 `which slither` 返回空，则使用语言特定的参考文件进行手动分析。

## 语言检测

| 扩展名 | 语言 | 参考 |
|-----------|----------|-----------|
| `.sol` | Solidity | [{baseDir}/references/solidity.md]({baseDir}/references/solidity.md) |
| `.vy` | Vyper | [{baseDir}/references/vyper.md]({baseDir}/references/vyper.md) |
| `.rs` + `Cargo.toml` with `solana-program` | Solana (Rust) | [{baseDir}/references/solana.md]({baseDir}/references/solana.md) |
| `.move` + `Move.toml` with `edition` | [{baseDir}/references/move-sui.md]({baseDir}/references/move-sui.md) |
| `.move` + `Move.toml` with `Aptos` | [{baseDir}/references/move-aptos.md]({baseDir}/references/move-aptos.md) |
| `.fc`, `.func`, `.tact` | TON (FunC/Tact) | [{baseDir}/references/ton.md]({baseDir}/references/ton.md) |
| `.rs` + `Cargo.toml` with `cosmwasm-std` | CosmWasm | [{baseDir}/references/cosmwasm.md]({baseDir}/references/cosmwasm.md) |

在分析之前，根据检测到的语言加载适当的参考文件。

## 访问分类

将每个状态改变入口点分类到以下类别之一：

### 1. 公开（无限制）
任何人都可以调用的函数，没有任何限制。

### 2. 角色限制
仅限于特定角色的函数。常见的检测模式：
- 明确的角色名称：`admin`, `owner`, `governance`, `guardian`, `operator`, `manager`, `minter`, `pauser`, `keeper`, `relayer`, `lender`, `borrower`
- 角色检查模式：`onlyRole`, `hasRole`, `require(msg.sender == X)`, `assert_owner`, `#[access_control]`
- 当角色不明确时，标记为 **"限制（需要审核）**" 并注明限制模式

### 3. 合约仅限（内部集成点）
仅其他合约可以调用的函数，EOA 不能调用。指示器：
- 回调：`onERC721Received`, `uniswapV3SwapCallback`, `flashLoanCallback`
- 接口实现带有合约调用者检查
- 如果 `tx.origin == msg.sender` 则回滚的函数
- 跨合约钩子

## 输出格式

生成具有以下结构的 markdown 报告：

```markdown
# 入口点分析：[项目名称]

**分析时间**： [timestamp]
**范围**： [分析的目录或 "完整代码库"]
**语言**： [检测到的语言]
**重点**： 仅限状态改变函数（排除 view/pure）

## 摘要

| 类别 | 数量 |
|----------|-------|
| 公开（无限制） | X |
| 角色限制 | X |
| 限制（需要审核） | X |
| 合约仅限 | X |
| **总计** | **X** |

---

## 公开入口点（无限制）

任何人都可以调用的状态改变函数—优先进行攻击面分析。

| 函数 | 文件 | 备注 |
|----------|------|-------|
| `functionName(params)` | `path/to/file.sol:L42` | 如果相关，简要备注 |

---

## 角色限制入口点

### 管理员 / 所有者
| 函数 | 文件 | 限制 |
|----------|------|-------------|
| `setFee(uint256)` | `Config.sol:L15` | `onlyOwner` |

### 治理
| 函数 | 文件 | 限制 |
|----------|------|-------------|

### 守护者 / 暂停者
| 函数 | 文件 | 限制 |
|----------|------|-------------|

### 其他角色
| 函数 | 文件 | 限制 | 角色 |
|----------|------|-------------|------|

---

## 限制（需要审核）

具有访问控制模式需要手动验证的函数。

| 函数 | 文件 | 模式 | 审核原因 |
|----------|------|---------|------------|
| `execute(bytes)` | `Executor.sol:L88` | `require(trusted[msg.sender])` | 动态信任列表 |

---

## 合约仅限（内部集成点）

仅其他合约可以调用的函数—有助于理解信任边界。

| 函数 | 文件 | 预期调用者 |
|----------|------|-----------------|
| `onFlashLoan(...)` | `Vault.sol:L200` | 闪电贷提供者 |

---

## 分析的文件

- `path/to/file1.sol`（X 个状态改变入口点）
- `path/to/file2.sol`（X 个状态改变入口点）
```

## 过滤

当用户指定目录过滤器时：
- 仅分析该路径内的文件
- 在报告标题中注明过滤器
- 示例： "仅分析 `src/core/`" → 范围 = `src/core/`

## 分析指南

1. **彻底**：不要跳过文件。每个状态改变的外部可调用函数都很重要。
2. **保守**：当不确定访问级别时，标记为审核而不是错误分类。
3. **跳过只读**：排除 `view`, `pure` 和等效的只读函数。
4. **注明继承**：如果函数的访问控制来自父合约，请注明。
5. **跟踪修饰符**：列出每个函数应用的所有访问相关修饰符/装饰器。
6. **识别模式**：查找常见模式，例如：
   - 初始化函数（通常在第一次调用时无限制）
   - 升级函数（高权限）
   - 紧急/暂停函数（守护者级）
   - 费用/参数设置器（管理员级）
   - 代币转移和批准（通常为公开）

## 常见角色模式按协议类型

| 协议类型 | 常见角色 |
|---------------|--------------|
| DEX | `owner`, `feeManager`, `pairCreator` |
| 借贷 | `admin`, `guardian`, `liquidator`, `oracle` |
| 治理 | `proposer`, `executor`, `canceller`, `timelock` |
| NFT | `minter`, `admin`, `royaltyReceiver` |
| 桥接 | `relayer`, `guardian`, `validator`, `operator` |
| 库/收益 | `strategist`, `keeper`, `harvester`, `manager` |

## 拒绝的合理化

在分析入口点时，拒绝这些捷径：
- "这个函数看起来标准" → 仍然分类它；标准函数可以有非标准的访问控制
- "修饰符名称很清楚" → 验证修饰符的实际实现
- "这显然是管理员专用的" → 追踪实际限制；"明显"的假设会遗漏微妙的绕过
- "我会跳过回调" → 回调定义信任边界；始终包括它们
- "它没有修改太多状态" → 任何状态改变都可能被利用；包括所有非 view 函数

## 错误处理

如果文件无法解析：
1. 在报告的 "分析警告" 下注明
2. 继续分析其余文件
3. 建议手动审核无法解析的文件
