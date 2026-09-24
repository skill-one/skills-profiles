# hosting-basics

本技能提供有关使用 Firebase Hosting 的说明和参考资料。Firebase Hosting 是用于托管您的 Web 应用、静态和动态内容以及微服务的快速且安全的托管服务。

## 概述

Firebase Hosting 为开发者提供生产级的 Web 内容托管服务。通过一条命令，您可以部署 Web 应用，并将静态和动态内容发布到全球 CDN（内容分发网络）。

**主要特性：**

- **快速内容分发：** 文件在全球 CDN 边缘的 SSD 上缓存。
- **默认安全：** 内置零配置 SSL。
- **预览通道：** 在部署到生产环境之前，通过临时预览 URL 查看和测试更改。
- **GitHub 集成：** 使用 GitHub Actions 自动化预览和部署。
- **动态内容：** 使用 Cloud Functions 或 Cloud Run 提供动态内容和微服务。

## 托管与应用程序托管

**如果选择 Firebase Hosting，请考虑以下情况：**

- 您正在部署静态网站（HTML/CSS/JS）。
- 您正在部署简单的单页应用（SPA）（如 React、Vue 等，不含 SSR）。
- 您希望通过命令行（CLI）完全掌控构建和部署流程。

**如果选择 Firebase 应用程序托管，请考虑以下情况：**

- 您正在使用 Next.js 或 Angular 等受支持的全栈框架。
- 您需要服务器端渲染（SSR）或 ISR。
- 您希望拥有零配置的自动化“git 推送即部署”工作流。

## 说明

### 1. 配置（`firebase.json`）

有关配置托管行为的详细信息，包括公共目录、重定向、重写和响应头等，请参阅 [configuration.md](references/configuration.md)。

### 2. 部署

有关部署您的网站、使用预览通道和管理发布的说明，请参阅 [deploying.md](references/deploying.md)。

### 3. 模拟

在本地测试您的应用时：

```bash
npx -y firebase-tools@latest emulators:start --only hosting
```

默认情况下，此命令将在 `http://localhost:5000` 上提供您的应用。
