# Clerk 技能路由器

## 版本检测

检查 `package.json` 以确定 Clerk SDK 版本。这决定了要使用的模式：

| 包 | 核心 2（LTS 直到 2027 年 1 月） | 当前 |
|-----|-----------------------------|-----|
| `@clerk/nextjs` | v5–v6 | v7+ |
| `@clerk/react` 或 `@clerk/clerk-react` | v5–v6 | v7+ |
| `@clerk/expo` 或 `@clerk/clerk-expo` | v1–v2 | v3+ |
| `@clerk/react-router` | v1–v2 | v3+ |
| `@clerk/tanstack-react-start` | < v0.26.0 | v0.26.0+ |

如果版本不明确或项目是新的，则默认使用当前版本。核心 2 包使用 `@clerk/clerk-react` 和 `@clerk/clerk-expo`（带有 `clerk-` 前缀）；当前包使用 `@clerk/react` 和 `@clerk/expo`。

所有技能都是为当前 SDK 编写的。当核心 2 中有所不同时，会使用 `> **仅限核心 2（如果使用当前 SDK 则跳过）：**` 提示进行说明。例外是 `clerk-custom-ui`，它有单独的 `core-2/` 和 `core-3/` 目录，用于自定义流程钩子，因为这些 API 在不同版本中完全不同。

---

## 按任务分类

**将 Clerk 添加到您的项目中** → 使用 `clerk-setup`
- 框架检测和快速入门
- 环境设置、API 密钥、通过 `clerk init` 获取临时开发密钥
- 从其他身份验证提供程序迁移

**从 CLI 操作 Clerk** → 使用 `clerk-cli`
- 身份验证、链接、`doctor` 和环境拉取
- 用户、组织、会话、应用和实例管理
- 模拟用户 (`clerk impersonate`) 和本地 webhook 测试 (`clerk webhooks listen`)
- 功能开关 (`clerk enable orgs`, `clerk enable billing`)
- 通过 `clerk api` 进行后端、平台和前端 API 调用
- 部署交接和部署状态验证

**自定义登录/注册 UI** → 使用 `clerk-custom-ui`
- 使用 `useSignIn` / `useSignUp` 钩子自定义身份验证流程
- 外观和样式（主题、颜色、布局）
- `<Show>` 组件用于条件渲染

**高级 Next.js 模式** → 使用 `clerk-nextjs-patterns`
- 服务器与客户端身份验证 API
- 中间件策略
- 服务器操作、缓存
- API 路由保护

**React 模式** → 使用 `clerk-react-patterns`
- 钩子 (`useAuth`, `useUser`, `useClerk`)
- 受保护的路由、身份验证守卫
- 路由器集成

**React Router 模式** → 使用 `clerk-react-router-patterns`
- 带身份验证的加载器和操作
- 路由保护
- 服务器端渲染身份验证

**Vue 模式** → 使用 `clerk-vue-patterns`
- 组合式 (`useAuth`, `useUser`, `useClerk`)
- Vue 路由守卫
- Pinia 身份验证存储集成

**Nuxt 模式** → 使用 `clerk-nuxt-patterns`
- 服务器中间件身份验证
- 使用组合式的服务器端渲染身份验证
- 服务器 API 路由

**Astro 模式** → 使用 `clerk-astro-patterns`
- 服务器端渲染身份验证页面
- 带有 React 的岛组件
- 中间件和 API 路由

**TanStack Start 模式** → 使用 `clerk-tanstack-patterns`
- 带身份验证的服务器函数
- 通过加载器进行路由保护
- Vinxi 服务器集成

**Expo / React Native 身份验证** → 使用 `clerk-expo`
- 预构建的原生组件（AuthView, UserButton）
- 自定义流程：电子邮件、密码、SMS/电话 OTP、MFA
- OAuth/SSO 和原生 Google/Apple 登录
- Expo Router 受保护的路由、令牌存储、推送通知

**Chrome 扩展模式** → 使用 `clerk-chrome-extension-patterns`
- 背景脚本身份验证
- 弹出身份验证流程
- 带同步主机的内容脚本

**B2B / 组织** → 使用 `clerk-orgs`
- 多租户应用
- URL 中的组织别名
- 角色权限、RBAC
- 成员管理

**计费和订阅** → 使用 `clerk-billing`
- `<PricingTable />` 组件
- 使用 `has()` 进行计划和功能门控
- 基于座位的 B2B 计费与组织
- 订阅生命周期 webhook
- 免费试用、开票

**Webhooks** → 使用 `clerk-webhooks`
- 实时事件
- 数据同步
- 通知和集成

**端到端测试** → 使用 `clerk-testing`
- Playwright/Cypress 设置
- 身份验证流程测试
- 测试工具

**Swift / 原生 iOS 身份验证** → 使用 `clerk-swift`
- 原生 iOS Swift 和 SwiftUI 项目
- ClerkKit 和 ClerkKitUI 实现指南
- 从 `clerk-ios` 获取源驱动的模式

**Android / 原生移动身份验证** → 使用 `clerk-android`
- 原生 Android Kotlin 和 Jetpack Compose 项目
- `clerk-android-api` 和 `clerk-android-ui` 实现指南
- 从 `clerk-android` 获取源驱动的模式
- 不适用于 Expo 或 React Native 项目

**后端 REST API** → 使用 `clerk-backend-api`
- 浏览 API 标签和端点
- 检查端点模式
- 执行 API 请求并强制执行范围

## 快速导航

如果您知道您的任务，可以直接访问：
- `/clerk-setup` - 框架设置
- `/clerk-cli` - CLI 操作和 Clerk 资源管理
- `/clerk-custom-ui` - 自定义流程 & 外观
- `/clerk-nextjs-patterns` - Next.js 模式
- `/clerk-react-patterns` - React 模式
- `/clerk-react-router-patterns` - React Router 模式
- `/clerk-vue-patterns` - Vue 模式
- `/clerk-nuxt-patterns` - Nuxt 模式
- `/clerk-astro-patterns` - Astro 模式
- `/clerk-tanstack-patterns` - TanStack Start 模式
- `/clerk-expo` - Expo / React Native
- `/clerk-chrome-extension-patterns` - Chrome 扩展模式
- `/clerk-orgs` - 组织
- `/clerk-billing` - 计费 & 订阅
- `/clerk-webhooks` - Webhooks
- `/clerk-testing` - 测试
- `/clerk-swift` - Swift/原生 iOS
- `/clerk-android` - 原生 Android
- `/clerk-backend-api` - 后端 REST API

或者描述您的需求，我会推荐合适的选择。
