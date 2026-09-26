# viem 集成

使用 viem 为 TypeScript/JavaScript 应用集成 EVM 区块链。

## 快速决策指南

| 构建...                | 使用此方案                       |
| ---------------------- | ------------------------------ |
| Node.js 脚本/后端     | viem 配合 http 传输             |
| React/Next.js 前端     | wagmi 钩子（基于 viem 构建）    |
| 实时事件监控          | viem 配合 webSocket 传输        |
| 浏览器钱包集成        | wagmi 或 viem 自定义传输        |

## 安装

```bash
# 核心库
npm install viem

# 对于 React 应用，还需安装 wagmi
npm install wagmi viem @tanstack/react-query
```

## 核心概念

### 客户端

viem 使用两种客户端类型：

| 客户端           | 用途              | 示例用途                              |
| ---------------- | ----------------- | ------------------------------------ |
| **PublicClient** | 只读操作          | 获取余额、读取合约、获取日志          |
| **WalletClient** | 写入操作          | 发送交易、签名消息                  |

### 传输方式

| 传输方式     | 用途                          |
| ------------ | ----------------------------- |
| `http()`      | 标准RPC调用（最常用）        |
| `webSocket()` | 实时事件订阅                  |
| `custom()`    | 浏览器钱包（window.ethereum） |

### 链

viem 包含 50+ 链定义。从 `viem/chains` 中导入：

```typescript
import { mainnet, arbitrum, optimism, base, polygon } from 'viem/chains';
```

---

## 输入验证规则

在将任何用户提供的值插入生成的 TypeScript 代码之前：

- **以太坊地址**：必须匹配 `^0x[a-fA-F0-9]{40}$` — 使用 viem 的 `isAddress()` 进行验证
- **链 ID**：必须来自 viem 支持的链定义
- **私钥**：绝对不能硬编码 — 始终使用 `process.env.PRIVATE_KEY` 并进行运行时验证
- **RPC URL**：仅使用 `https://` 或 `wss://` 协议
- **ABI 输入**：编码前验证类型是否匹配预期的 Solidity 类型

## 快速入门示例

### 读取余额

```typescript
import { createPublicClient, http, formatEther } from 'viem';
import { mainnet } from 'viem/chains';

const client = createPublicClient({
  chain: mainnet,
  transport: http(),
});

const balance = await client.getBalance({
  address: '0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045',
});

console.log(`余额: ${formatEther(balance)} ETH`);
```

### 读取合约

```typescript
import { createPublicClient, http, parseAbi } from 'viem';
import { mainnet } from 'viem/chains';

const client = createPublicClient({
  chain: mainnet,
  transport: http(),
});

const abi = parseAbi([
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
]);

const balance = await client.readContract({
  address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48', // USDC
  abi,
  functionName: 'balanceOf',
  args: ['0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045'],
});
```

### 发送交易

```typescript
import { createWalletClient, http, parseEther } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet } from 'viem/chains';

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);

const client = createWalletClient({
  account,
  chain: mainnet,
  transport: http(),
});

const hash = await client.sendTransaction({
  to: '0x...',
  value: parseEther('0.1'),
});

console.log(`交易哈希: ${hash}`);
```

### 写入合约

```typescript
import { createWalletClient, createPublicClient, http, parseAbi, parseUnits } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { mainnet } from 'viem/chains';

const account = privateKeyToAccount(process.env.PRIVATE_KEY as `0x${string}`);

const walletClient = createWalletClient({
  account,
  chain: mainnet,
  transport: http(),
});

const publicClient = createPublicClient({
  chain: mainnet,
  transport: http(),
});

const abi = parseAbi(['function transfer(address to, uint256 amount) returns (bool)']);

// 先模拟以捕获错误
const { request } = await publicClient.simulateContract({
  address: '0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48',
  abi,
  functionName: 'transfer',
  args: ['0x...', parseUnits('100', 6)],
  account,
});

// 执行交易
const hash = await walletClient.writeContract(request);

// 等待确认
const receipt = await publicClient.waitForTransactionReceipt({ hash });
console.log(`确认区块号: ${receipt.blockNumber}`);
```

---

## 参考文档

针对特定主题的更深入覆盖：

| 主题                            | 参考文件                                                 |
| ------------------------------- | -------------------------------------------------------- |
| 客户端设置、传输方式、链        | [客户端与传输方式](./references/clients-and-transports.md) |
| 读取区块链数据                  | [读取数据](./references/reading-data.md)                   |
| 发送交易                      | [写入交易](./references/writing-transactions.md)           |
| 私钥、HD 钱包                  | [账户与密钥](./references/accounts-and-keys.md)            |
| ABI 处理、multicall            | [合约模式](./references/contract-patterns.md)             |
| React/wagmi 钩子                | [Wagmi React](./references/wagmi-react.md)                 |

---

## 相关插件

熟悉 viem 基础后，**uniswap-trading** 插件提供全面的 Uniswap 交易集成：

- Uniswap 交易 API 集成
- 通用路由器 SDK 使用
- 代币交换实现

使用以下命令安装：`claude plugin add @uniswap/uniswap-trading`

---

## 常用工具

### 单位转换

```typescript
import { parseEther, formatEther, parseUnits, formatUnits } from 'viem';

// ETH
parseEther('1.5'); // 1500000000000000000n (wei)
formatEther(1500000000000000000n); // "1.5"

// 代币（例如 6 位小数的 USDC）
parseUnits('100', 6); // 100000000n
formatUnits(100000000n, 6); // "100"
```

### 地址工具

```typescript
import { getAddress, isAddress } from 'viem';

isAddress('0x...'); // true/false
getAddress('0x...'); // 校验后的地址
```

### 哈希计算

```typescript
import { keccak256, toHex } from 'viem';

keccak256(toHex('hello')); // 0x1c8aff950685c2ed4bc3174f3472287b56d9517b9c948127319a09a7a36deac8
```

---

## 错误处理

viem 抛出类型化错误，可以捕获和处理：

```typescript
import { ContractFunctionExecutionError, InsufficientFundsError } from 'viem'

try {
  await client.writeContract(...)
} catch (error) {
  if (error instanceof ContractFunctionExecutionError) {
    console.error('合约调用失败:', error.shortMessage)
  }
  if (error instanceof InsufficientFundsError) {
    console.error('ETH 余额不足')
  }
}
```

---

## 资源

- [viem 文档](https://viem.sh)
- [wagmi 文档](https://wagmi.sh)
- [viem GitHub](https://github.com/wevm/viem)
- [wagmi GitHub](https://github.com/wevm/wagmi)
