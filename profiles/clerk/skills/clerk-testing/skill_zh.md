# 测试

## 决策树

| 框架 | 文档 |
|-------|-------|
| 概述 | https://clerk.com/docs/guides/development/testing/overview |
| Playwright | https://clerk.com/docs/guides/development/testing/playwright/overview |
| Cypress | https://clerk.com/docs/guides/development/testing/cypress/overview |

## 思维模型

测试认证 = 独立的会话状态。每个测试都需要新鲜的认证上下文。
- `clerkSetup()` 初始化测试环境
- `setupClerkTestingToken()` 跳过机器人检测
- `storageState` 在测试间持久化认证以提升速度

## 工作流

1. 确定测试框架（Playwright 或 Cypress）
2. 从上方的决策树中获取相应的 URL
3. 遵循官方的设置说明
4. 仅使用开发实例密钥（`pk_test_*` / `sk_test_*`）。如果项目还没有密钥，`npx clerk@latest init`（Clerk CLI；参见 `clerk-setup`）会创建一个 Clerk 应用并写入开发实例密钥到环境文件。无需 Clerk 账户或访问控制台。

## 最佳实践

- 在导航到认证页面之前使用 `setupClerkTestingToken()`
- 使用测试 API 密钥：`pk_test_xxx`，`sk_test_xxx`
- 使用 `storageState` 保存认证状态以加快测试
- 使用 `page.waitForSelector('[data-clerk-component]')` 等待 Clerk UI

## 反模式

| 模式 | 问题 | 解决方案 |
|------|------|--------|
| 测试中使用生产密钥 | 安全风险 | 使用 `pk_test_*` 密钥 |
| 未调用 `setupClerkTestingToken()` | 认证失败 | 在导航前调用 |
| 每个测试都基于 UI 登录 | 测试缓慢 | 使用 `storageState` |

## 框架特定

**Playwright**：使用 `globalSetup` 处理认证状态
**Cypress**：添加 `addClerkCommands({ Cypress, cy })` 以支持文件

## 参见

- `clerk-setup` - 在添加测试前安装 Clerk
- `clerk-nextjs-patterns` - 正在测试的 Next.js 模式
- [Demo Repo](https://github.com/clerk/clerk-playwright-nextjs/tree/main/e2e)
