# 应用托管基础

## 描述

此技能使智能体能够使用 Firebase App Hosting 部署和管理现代的全栈 Web 应用（Next.js、Angular 等）。

**重要**：若要使用应用托管，您的 Firebase 项目必须使用 Blaze 定价方案。请将用户引导至
https://console.firebase.google.com/project/_/overview?purchaseBillingPlan=metered
以升级其方案。

## 托管与 App Hosting 的区别

**选择 Firebase Hosting 如果：**

- 您正在部署静态网站（HTML/CSS/JS）。
- 您正在部署简单的单页应用（SPA）（React、Vue 等，不使用 SSR）。
- 您希望通过 CLI 完全控制构建和部署流程。

**选择 Firebase App Hosting 如果：**

- 您正在使用支持的全栈框架（如 Next.js 或 Angular）。
- 您需要服务端渲染（SSR）或 ISR。
- 您希望拥有无需配置的自动化“git push 即可部署”工作流。

## 部署到 App Hosting

### 从源部署

这是大多数用户的推荐流程。

1. 配置 `firebase.json`，添加一个 `apphosting` 块。

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
1. 创建或编辑 `apphosting.yaml`——有关如何操作的更多信息，请参阅
[Configuration](references/configuration.md)。
1. 如果应用需要以安全方式访问敏感密钥，请使用 `npx -y firebase-tools@latest apphosting:secrets` 命令来设置并授予对密钥的访问权限。
1. 准备好部署后，运行 `npx -y firebase-tools@latest deploy`。

### 通过 GitHub（CI/CD）实现自动化部署

 alternatively，设置与 GitHub 仓库关联的后端以实现自动化“git push”部署。这仅推荐给高级用户，且并非使用 App Hosting 的必要条件。有关如何使用 CLI 命令进行设置的更多信息，请参阅
[CLI Commands](references/cli_commands.md)。

## 模拟测试

有关如何使用 Firebase Local Emulator Suite 在本地测试您的应用，请参阅 [Emulation](references/emulation.md)。
