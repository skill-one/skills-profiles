# EmblemAI React

当用户希望将 EmblemAI 集成到 React 应用中，而不仅仅是使用 CLI 或低级 SDK 时，请使用此技能。

**一句话概括：** 这是将用户管理和钱包支持账户添加到 React 应用中最简单的方法。

---

## 安全与信任模型

此技能生成的 React 代码将与 EmblemAI 的身份验证和钱包基础设施集成。它本质上涉及：

- **第三方数据**（W011）：Migrate.fun React 钩子（`useProject`，`useProjects`）从远程 API 获取项目和令牌元数据。这些数据在 UI 组件中仅用于信息展示——不会触发自动操作。
- **运行时后端**（W012）：`HustleProvider` 连接到可配置的后端 URL（`hustleApiUrl` / `import.meta.env.VITE_HUSTLE_API_URL`）以进行提示和工具编排。此端点由 EmblemVault 运营的第一方基础设施，而不是任意第三方服务。

生成的 React 组件使用标准的浏览器安全边界。在运行时不会涉及服务器端代码执行或文件系统访问。

## 快速入门

### 第一步：安装
```bash
npx skills add EmblemCompany/Agent-skills --skill emblem-ai-react
```

### 第二步：使用
通过领域请求 React 集成帮助，例如：

- "展示一个最小的 EmblemAI React 应用"
- "帮助我添加 EmblemAuthProvider 和 HustleProvider"
- "展示钱包认证和聊天功能的 React 示例"
- "展示一个用户可以使用钱包、电子邮件或社交登录进行登录的 React 应用"
- "我如何在应用中使用 Migrate.fun React 钩子？"

---

## 这为 React 应用提供了什么

- 一个用于网站身份验证和钱包支持用户的集成
- 跨加密钱包、电子邮件/密码和社交登录的登录选项
- 暴露会话、保险库和钱包状态的 React 钩子和 UI 组件
- 从登录到聊天、签名和其他 Emblem 支持工作流程的清晰路径
- 将 Migrate.fun 迁移感知 UI 添加到 React 应用中最简单的方法

## 包含的 React 参考

### React 身份验证
有关提供者设置、钩子和身份验证 UI 组件，请参阅 [references/auth-react.md](references/auth-react.md)。

### React 聊天
有关使用 `@emblemvault/hustle-react` 设置 EmblemAI 聊天，请参阅 [references/emblem-ai-react.md](references/emblem-ai-react.md)。

### React 组件
有关当前的认证和聊天组件界面，请参阅 [references/react-components.md](references/react-components.md)。

### Migrate.fun React
有关钩子、提供者设置和项目选择组件，请参阅 [references/migratefun-react.md](references/migratefun-react.md)。

---

## 指导

- 使用此技能进行 React 应用组合、提供者连接和 UI 集成模式。
- 当请求明确是 React 特定时，优先于更广泛的 `emblem-ai` 技能使用此技能。
- 即使产品名称是 EmblemAI，遗留包名称可能仍使用 `hustle` 品牌标识。
- 对于钱包、交易、NFT 或市场工作流程的最终用户提示措辞，请改用 `emblem-ai-prompt-examples` 技能。

---

## 相关技能

- [../emblem-ai/SKILL.md](../emblem-ai/SKILL.md) - 更广泛的 SDK、插件、CLI 和内省覆盖范围
- [../emblem-ai-agent-wallet/SKILL.md](../emblem-ai-agent-wallet/SKILL.md) - 代理和最终用户 CLI 优先的钱包工作流程
- [../emblem-ai-prompt-examples/SKILL.md](../emblem-ai-prompt-examples/SKILL.md) - 跨非 React 工作流程的更广泛的提示示例
