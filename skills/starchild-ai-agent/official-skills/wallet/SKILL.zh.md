---
name: wallet
description: 使用 Agent 钱包在 Monad 测试网或主网上发送交易，这些交易可以是智能合约部署、链上操作（如交换或智能合约调用）以及签名消息。
---

## ⚠️ 严重警告：安全多重签名必须使用 - 无例外

除部署 Safe 多重签名之外的所有交易都必须通过已部署的多重签名向用户提出。

有关如何创建和使用 Safe 多重签名的说明，请查看 utils 文件夹中的 SAFE_WALLET_MANAGEMENT.md 文件。

**提出交易时：** 始终从 utils 文件夹中调用 `propose.sh` 包装器（它启动 `propose.mjs` 并使用缓存的依赖项）—— 永远不要编写自定义脚本。运行后，不要添加你自己的摘要、状态消息或重新格式化输出。脚本输出包含用户必须看到的确切打印的 QR 码。你唯一后续的操作应该是要求用户批准交易并提供交易哈希。

**安全规则：**
- 绝对不要索要用户的私钥（严重违规）
- 使用代理钱包（加密的 keystore 位于 `~/.monskills/keystore`）
- 绝对不要导出或以明文形式存储私钥

检查代理是否已生成钱包。如果 keystore 目录 `~/.monskills/keystore` 存在并包含 keystore 文件，则钱包已经存在。

如果未找到，则创建钱包。

## 创建钱包

需要安装 Foundry 才能生成钱包。

### 检查 Foundry 是否已安装

使用以下命令检查 Foundry 是否已安装。

```bash
foundryup --version
```

Foundry 的安装说明可以在这里找到：https://www.getfoundry.sh/introduction/installation

## 生成新钱包

1. 创建 keystore 目录并生成加密的 keystore：

```bash
mkdir -p ~/.monskills/keystore && cast wallet new ~/.monskills/keystore --unsafe-password ""
```

这会在 `~/.monskills/keystore/` 中创建一个加密的 keystore 文件。私钥永远不会以明文形式存储。

2. 记录输出中的地址。要稍后检索地址：

```bash
cast wallet list --dir ~/.monskills/keystore
```

3. 告知用户钱包 keystore 存储的位置（`~/.monskills/keystore/`）。
4. 在部署之前，通过 faucet 在 Monad 测试网上为钱包提供资金。

## 为脚本解密私钥

当脚本需要私钥（例如，作为环境变量）时，动态解密它。`cast wallet decrypt-keystore` 打印 `<uuid>'s private key is: 0x...` — 通过 `awk '{print $NF}'` 将其重定向以仅保留十六进制密钥，否则 Foundry 命令会拒绝带有 "Failed to decode private key" 前缀的字符串：

```bash
cast wallet decrypt-keystore --keystore-dir ~/.monskills/keystore <KEYSTORE_FILENAME> --unsafe-password "" | awk '{print $NF}'
```

将 `<KEYSTORE_FILENAME>` 替换为 `~/.monskills/keystore/` 中 keystore 文件的文件名（不包括目录路径）。

**为什么这很重要：** 用户需要访问他们的钱包来：
- 部署额外的合约
- 与已部署的合约交互
- 管理资金
- 验证所有权
