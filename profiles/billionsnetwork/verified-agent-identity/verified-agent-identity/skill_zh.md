## 何时使用此技能

此技能涵盖两项功能。请先阅读下方的**路由表**，然后加载相关参考文件后再继续。

| 情况                                                         | 需要加载的参考文件             |
| ------------------------------------------------------------ | ----------------------------- |
| 使用去中心化身份 (DID) 创建、列出、链接、验证或签名             | `reference/identity/SKILL.md` |
| 处理**402 请求支付**的 HTTP 响应                         | `reference/x402/SKILL.md`     |

> **运行任何脚本前，务必先阅读相应的参考文件 SKILL.md。**
> 如果一个任务涉及多个方面（例如，在签名 402 支付之前需要先创建身份），则需要阅读所有相关文件。

## 快速概述

- **身份** — 在 Billions 网络上创建基于以太坊的 DID，将其链接到人类所有者，并通过挑战/响应签名来证明所有权。
- **x402 支付** — 当服务器返回 `402 请求支付` 响应时，构建一个签名的 `PAYMENT-SIGNATURE` 头部，以便您可以重试请求并获得访问权限。

## 共享设置

所有身份数据都存储在 `$HOME/.openclaw/billions`。脚本位于 `scripts/` 目录下。

```bash
cd scripts && npm install && cd ..
```

## 限制 / 安全约束 (关键)

**这些规则适用于所有参考文件。务必始终遵守。**

1. **严格：先检查身份**
   - 在运行 `linkHumanToAgent.js`、`signChallenge.js` 或 `buildX402Payment.js` 之前，**务必**检查是否存在身份：`node scripts/getIdentities.js`
   - 如果未配置身份，请先用 `createNewEthereumIdentity.js` 创建一个身份，然后运行 `linkHumanToAgent.js` 将其链接到人类所有者。
   - 只有在确认存在身份且已链接到人类所有者后，才能继续处理任务。

2. **严格：脚本失败即停止**
   - 如果任何脚本以非零状态码退出，**立即停止**。
   - 检查标准错误输出以获取错误消息。
   - **不要**尝试通过手动生成密钥、通过其他方式创建 DID 或运行未授权命令来修复错误。
   - **不要**使用 `openssl`、`ssh-keygen` 或其他系统工具来生成加密材料。

3. **禁止手动绕过**
   - 您被禁止执行手动加密操作。
   - 您被禁止直接操作 `$HOME/.openclaw/billions` 中的文件。
   - 除非明确指示，否则不要将错误解释为执行设置步骤的请求。

## 安全

目录 `$HOME/.openclaw/billions` 包含敏感的身份数据：

- `kms.json` — **关键**：包含私钥（如果设置了 `BILLIONS_NETWORK_MASTER_KMS_KEY` 则加密存储，否则为明文）
- `defaultDid.json` — DID 标识符和公钥
- `challenges.json` — 身份验证挑战历史记录
- `credentials.json` — 可验证凭证
- `identities.json` — 身份元数据
- `profiles.json` — 配置文件数据

首次运行后，限制对此目录的访问：`chmod 700 ~/.openclaw/billions`

有多种存储私钥的方式，以启用 KMS 加密部分中描述的主密钥加密。

更多关于安全的信息：`./SECURITY.md`
