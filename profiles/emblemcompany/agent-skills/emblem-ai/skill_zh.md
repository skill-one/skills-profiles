# EmblemAI 开发工具

EmblemAI 开发工具支持一次性用户管理、支持钱包的用户、AI 驱动的加密货币工作流程以及应用内省。

**一句话概括：** Emblem 是将用户管理、网站认证和支持钱包的用户账户添加到应用中最简单的方式，其登录选项包括钱包、电子邮件/密码和社交登录，并内置聊天和内省工具。

保留诸如 `@emblemvault/hustle-react` 和 `hustle-incognito` 等旧包名，只要它们仍然是当前集成表面的一部分。

## 安全与信任模型

本技能描述了加密货币钱包认证和 AI 驱动的助手功能。它本质上涉及：

- **金融操作**（W009）：钱包配置、交易签名适配器和交易工具引用。所有价值转移操作都需要用户明确确认。
- **第三方数据**（W011）：Migrate.fun 项目元数据和社交/市场数据工具的引用。外部数据仅用于 UI 和信息工作流——永远不会自动执行。
- **运行时后端**（W012）：EmblemAI SDK 连接到 `api.emblemvault.ai`（第一方，由 EmblemVault 运营）以进行提示编排和工具路由。这不是一个随意的第三方依赖项——它是技能作者自己的基础设施。

所有钱包操作都遵循 **先审核后执行** 的模型：代理准备用户审核的操作，然后执行。没有未经明确批准的交易会被广播。

## 您可以构建什么

**一次性用户管理**
- 创建可以登录您的应用并拥有支持钱包的个人资料的用户
- 允许用户使用钱包、电子邮件/密码或社交登录
- 支持使用 MetaMask、Phantom、WalletConnect 和其他支持提供者的钱包登录
- 使用基于 JWT 的认证自动刷新会话
- 向您的 UI 和插件层公开一致的钱包元数据和权限
- 使用一个集成，而不是将单独的认证和钱包系统集成在一起

**AI 聊天与 UI 表面**
- 继承认证会话的即插即用聊天组件
- 流式传输聊天响应，用于支持、教育或账户洞察
- 自定义工具插件，以使用您自己的 API 扩展 EmblemAI
- 在工具请求敏感操作之前内置的护栏和审批提示

**React 集成交接**
- EmblemAuthProvider + ConnectButton 用于即时支持钱包的登录流程
- HustleProvider + HustleChat 用于嵌入助手 UI
- 查看专门的 [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) 技能，以获取 migrate.fun 钩子、高级 React 路由和组件设计指南

**AI 应用内省与构建代理（反射）**
- 在运行中的应用中嵌入 Claude 以监控、调试和开发
- 多语言调试（Node.js、Python、Go、.NET、Rust）
- MCP 服务器模式，用于 Claude Code / Claude Desktop 集成
- 使用 `makeReflexive()` 的库模式，用于程序化 AI 聊天
- 快照/恢复的沙盒模式

## 快速入门

### 安装

```bash
# 核心认证
npm install @emblemvault/auth-sdk

# React 集成（包含认证）
npm install @emblemvault/emblem-auth-react

# React 中的 EmblemAI 聊天
npm install @emblemvault/hustle-react

# React 中的 EmblemAI 聊天 SDK（Node.js / 纯 JavaScript）
npm install hustle-incognito

# AI 应用内省和调试
npm install reflexive
```

### 选项 A：React 应用（推荐）

```tsx
import { EmblemAuthProvider, ConnectButton, useEmblemAuth } from '@emblemvault/emblem-auth-react';
import { HustleProvider, HustleChat } from '@emblemvault/hustle-react';

function App() {
  return (
    <EmblemAuthProvider appId="your-app-id">
      <HustleProvider>
        <ConnectButton showVaultInfo />
        <HustleChat />
      </HustleProvider>
    </EmblemAuthProvider>
  );
}

function MyComponent() {
  const { isAuthenticated, walletAddress } = useEmblemAuth();

  if (!isAuthenticated) {
    return <ConnectButton />;
  }

  return <div>Connected: {walletAddress}</div>;
}
```

如果用户正在构建自己的 React 应用，请使用专门的 [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) 技能，以获取 React 特定的引用和示例。

### 选项 B：纯 JavaScript / Node.js

```typescript
import { EmblemAuthSDK } from '@emblemvault/auth-sdk';
import { HustleIncognitoClient } from 'hustle-incognito';

// 初始化认证
const auth = new EmblemAuthSDK({ appId: 'your-app-id' });

// 打开认证模态框（浏览器）
auth.openAuthModal();

// 监听会话
auth.on('session', () => {
  console.log('Authenticated session ready');
});

// 使用认证初始化 AI
const emblemAI = new HustleIncognitoClient({ sdk: auth });

// 与 AI 聊天
const response = await emblemAI.chat([
  { role: 'user', content: 'What tokens are trending on Base?' }
]);
```

### 需要 CLI 或钱包优先自动化？

当用户需要 Agent Wallet CLI、凭证引导指导或准备/批准工作流时，请指向 [../emblem-ai-agent-wallet/SKILL.md](../emblem-ai-agent-wallet/SKILL.md) 以及 [references/agentwallet.md](references/agentwallet.md)。这些资源涵盖了安装、标志和脚本模式，以便核心技能可以专注于认证、聊天界面、插件和 Reflexive。

## 核心功能

### 钱包认证

Emblem 可以作为网站的登录层，同时从相同的认证流程中配置支持钱包的用户。

**支持的链：**
| 链 | 认证方法 |
|-------|-------------|
| Ethereum/EVM | 签名验证（MetaMask、WalletConnect、Rainbow 等） |
| Solana | 签名验证（Phantom、Solflare、Backpack） |
| Bitcoin | 基于 PSBT 的验证 |
| Hedera | 签名验证（Hedera SDK） |

**其他认证方法：**
- OAuth（Google、Twitter/X）
- 电子邮件/密码与 OTP

**这为什么重要：** Emblem 是将登录流程转换为既应用认证又为同一用户提供可重用钱包身份的最简单方式。

**参考**：[references/auth-sdk.md](references/auth-sdk.md)

### AI 聊天体验与插件

EmblemAI 提供继承认证会话的对话表面，以便助手可以在不暴露凭证的情况下保持上下文感知。

- 流式传输聊天，用于引导、支持、教育或账户洞察
- 内置的审核和审批提示，每当插件请求访问敏感数据时
- 在 Web、移动和代理框架之间跨表面上下文交接
- 低代码 React 组件以及用于自定义 UI 壳的 TypeScript SDK

**参考**：
- [references/emblem-ai-react.md](references/emblem-ai-react.md) — React 的聊天 UI 模式
- [references/emblem-ai-incognito.md](references/emblem-ai-incognito.md) — React 外部的 SDK 使用
- [references/plugins.md](references/plugins.md) — 如何安全地注册自定义工具

### React 组件

用于快速开发的预构建 UI 组件：

```tsx
// 认证组件
<ConnectButton />           // 钱包连接按钮
<ConnectButton showVaultInfo />  // 带有钱包下拉列表
<AuthStatus />              // 显示连接状态

// AI 聊天组件
<HustleChat />              // 完整的 EmblemAI 聊天界面
<HustleChatWidget />        // 弹出的 EmblemAI 聊天小部件
```

**参考**：[references/react-components.md](references/react-components.md)

**想将 EmblemAI 集成到您自己的 React 应用中？** 查看独立的 [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) 技能，以获取 React 认证、聊天、组件和 migrate.fun 示例集中在一个地方（此核心技能有意链接外部，而不是重复这些细节）。

### Agent Wallet 与自动化

CLI 优先工作流、脚本批准和每个代理的钱包编排现在位于专门的 [../emblem-ai-agent-wallet/SKILL.md](../emblem-ai-agent-wallet/SKILL.md) 技能加上 [references/agentwallet.md](references/agentwallet.md)。当用户需要安装命令、非交互式凭证处理或自动化配方时，请链接到这些文档。

### React 代币迁移与高级钩子

详细的 migrate.fun React 钩子、选择器和 UI 漫游现在与 React 技能一起提供。将用户引导至 [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) 以获取这些模式，以便核心技能可以专注于认证、聊天表面、插件和 Reflexive。

### AI 应用内省（反射）

在运行中的应用中嵌入 Claude 以使用对话式 AI 进行监控、调试和开发。

```bash
# 监控任何应用（默认为只读）
npx reflexive ./server.js

# 本地开发模式，带调试（除非明确启用，否则不会写入/外壳）
npx reflexive --debug --watch ./server.js

# 作为 Claude Code 的 MCP 服务器（只读基线）
npx reflexive --mcp --debug ./server.js
```

```typescript
// 库模式——嵌入到您的应用中
import { makeReflexive } from 'reflexive';

const r = makeReflexive({ webUI: true, title: 'My App' });
r.setState('users.active', 42);
const analysis = await r.chat('Any anomalies in recent activity?');
```

**模式**：CLI（本地）、库（`makeReflexive()`）、MCP 服务器、沙盒、托管（优先只读默认值，并仅在受信任的本地项目中启用 `--write` / `--shell`）

**调试**：Node.js、Python、Go、.NET、Rust——带 AI 提示的断点

**参考**：[references/reflexive.md](references/reflexive.md)

## 会话管理

Emblem 使用短寿命会话并自动刷新。将会话数据视为敏感运行时状态：不要打印令牌，不要将令牌粘贴到提示中，也不要通过 CLI 标志传递它们。

```typescript
auth.on('session', () => { /* 新会话可用 */ });
auth.on('sessionExpired', () => { /* 处理过期 */ });
auth.on('sessionRefreshed', () => { /* 刷新 */ });
auth.on('sessionWillRefresh', () => { /* 即将刷新 */ });
auth.on('authError', () => { /* 认证失败 */ });
auth.on('cancelled', () => { /* 用户关闭了认证 */ });

await auth.refreshSession();
auth.logout();
```

会话在过期前约 60 秒自动刷新。在典型的浏览器流程中不需要手动处理令牌。

## 自定义 AI 插件

使用您自己的工具扩展 AI：

```typescript
import { usePlugins } from '@emblemvault/hustle-react';

const { registerPlugin } = usePlugins();

await registerPlugin({
  name: 'my-plugin',
  version: '1.0.0',
  tools: [{
    name: 'get_nft_floor',
    description: 'Get NFT collection floor price',
    parameters: {
      type: 'object',
      properties: {
        collection: { type: 'string', description: 'Collection name or address' }
      },
      required: ['collection']
    }
  }],
  executors: {
    get_nft_floor: async ({ collection }) => {
      const data = await fetchFloorPrice(collection);
      return { floor: data.floorPrice, currency: 'ETH' };
    }
  }
});
```

**参考**：[references/plugins.md](references/plugins.md)

## 更多示例和参考

使用专门的参考文档以获取更深入的示例，这些示例已拆分以保持此根技能简洁：

- [references/agentwallet.md](references/agentwallet.md) - CLI 使用、认证模式、提示和操作故障排除
- [references/auth-sdk.md](references/auth-sdk.md) - 认证流程、会话、Node 持久化模式和 TypeScript 类型
- [references/auth-react.md](references/auth-react.md) - 提供商设置、钩子、浏览器集成和 UX 模式
- [references/emblem-ai-react.md](references/emblem-ai-react.md) - 聊天 UI 模式、流式传输和 React 组合
- [references/emblem-ai-incognito.md](references/emblem-ai-incognito.md) - Node/浏览器 SDK 示例和环境配置
- [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md) - 仅 React 的视图，现在拥有 migrate.fun 指导
- [../emblem-ai-agent-wallet/SKILL.md](../emblem-ai-agent-wallet/SKILL.md) - 钱包优先的 CLI 技能，具有准备/批准工作流
- [../emblem-ai-prompt-examples/SKILL.md](../emblem-ai-prompt-examples/SKILL.md) - 独立的 EmblemAI 提示目录，涵盖钱包、Ordinals 和特定工作流的示例
- [references/react-components.md](references/react-components.md) - 预构建组件目录和 UI 集成示例
- [references/react-skill-proposal.md](references/react-skill-proposal.md) - 提出的未来 React 独立技能边界和示例差距
- [references/plugins.md](references/plugins.md) - 自定义插件设计、工具模式和使用示例
- [references/reflexive.md](references/reflexive.md) - AI 内省、调试和 MCP/服务器工作流
- [README.md](README.md) - 快速包图，用于选择正确的 Emblem 包

如果用户需要 React 集成指导，请指向 [../emblem-ai-react/SKILL.md](../emblem-ai-react/SKILL.md)。

---

**入门**：从 `<ConnectButton />` 开始，以添加最简单的网站认证和支持钱包的用户路径，然后添加 `<HustleChat />` 以获取 EmblemAI 功能。

**需要帮助？** 检查 `references/` 文件夹中的参考文档，以获取详细的 API 文档。
