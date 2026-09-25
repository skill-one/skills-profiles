# 应用托管基础

## 描述

此技能使代理能够使用 Firebase App Hosting 部署和管理现代全栈 Web 应用程序（Next.js、Angular 等）。

**重要提示**：要使用 App Hosting，您的 Firebase 项目必须位于 Blaze 定价计划上。请将用户引导至 https://console.firebase.google.com/project/_/overview?purchaseBillingPlan=metered 升级他们的计划。

## 托管与 App Hosting

**选择 Firebase Hosting 如果：**

- 您正在部署静态网站（HTML/CSS/JS）。
- 您正在部署简单的 SPA（React、Vue 等，没有 SSR）。
- 您希望通过 CLI 完全控制构建和部署过程。

**选择 Firebase App Hosting 如果：**

- 您正在使用 Next.js 或 Angular 等受支持的全栈框架。
- 您需要服务器端渲染（SSR）或 ISR。
- 您希望实现零配置的自动化“git push to deploy”工作流。

## 部署到 App Hosting

### 从源代码部署

这是大多数用户推荐的工作流程。

1. 使用 `apphosting` 块配置 `firebase.json`。
   
   ```json
   {
     "apphosting": {
       "backendId": "my-app-id",
       "rootDir": "/",
       "ignore": [
         "node_modules",
         ".git",
         "firebase-debug.log",
         "firebase-debug.*.log",
         "functions"
       ]
     }
   }
   ```
1. 创建或编辑 `apphosting.yaml` - 更多关于如何配置的信息，请参阅 [配置](references/configuration.md)。
1. 如果应用程序需要安全访问敏感密钥，请使用 `npx -y firebase-tools@latest apphosting:secrets` 命令设置并授予密钥访问权限。
1. 准备部署时，运行 `npx -y firebase-tools@latest deploy`。

### 通过 GitHub 自动部署（CI/CD）

或者，设置连接到 GitHub 仓库的后端，以实现自动“git push”部署。这仅推荐给更高级的用户，并且不是使用 App Hosting 所必需的。更多关于如何使用 CLI 命令设置此内容的信息，请参阅 [CLI 命令](references/cli_commands.md)。

## 模拟

更多关于如何使用 Firebase Local Emulator Suite 在本地测试应用程序的信息，请参阅 [模拟](references/emulation.md)。
