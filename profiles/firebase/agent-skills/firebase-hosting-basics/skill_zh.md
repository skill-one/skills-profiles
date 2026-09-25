# hosting-basics

这个技能提供了与 Firebase Hosting 合作的使用说明和参考资料。Firebase Hosting 是一个快速且安全的托管服务，可用于您的 Web 应用、静态和动态内容以及微服务。

## 概述

Firebase Hosting 为开发者提供生产级的 Web 内容托管服务。通过一个命令，您就可以部署 Web 应用，并通过全球 CDN（内容分发网络）提供静态和动态内容。

**主要功能：**

- **快速内容分发**：文件被缓存在全球各地 CDN 边缘的 SSD 上。
- **默认安全**：内置零配置 SSL。
- **预览频道**：在部署上线前，通过临时预览 URL 查看和测试更改。
- **GitHub 集成**：使用 GitHub Actions 自动化预览和部署。
- **动态内容**：使用 Cloud Functions 或 Cloud Run 提供动态内容和微服务。

## 托管与 App 托管

**选择 Firebase Hosting 如果：**

- 您正在部署静态站点（HTML/CSS/JS）。
- 您正在部署简单的 SPA（React、Vue 等，没有 SSR）。
- 您想通过 CLI 完全控制构建和部署过程。

**选择 Firebase App Hosting 如果：**

- 您正在使用 Next.js 或 Angular 等受支持的全栈框架。
- 您需要服务器端渲染（SSR）或 ISR。
- 您想要一个零配置的“git push 即部署”工作流。

## 说明

### 1. 配置 (`firebase.json`)

有关配置 Hosting 行为的详细信息，包括公共目录、重定向、重写和标题，请参阅 [configuration.md](references/configuration.md)。

### 2. 部署

有关部署您的站点、使用预览频道和管理发布的说明，请参阅 [deploying.md](references/deploying.md)。

### 3. 模拟

要在本地测试您的应用：

```bash
npx -y firebase-tools@latest emulators:start --only hosting
```

默认情况下，这将使您的应用在 `http://localhost:5000` 上运行。
