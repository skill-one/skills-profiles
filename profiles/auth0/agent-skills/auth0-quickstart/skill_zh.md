# Auth0 快速入门

检测您的框架并开始使用 Auth0 身份验证。

---

## 第 1 步：检测您的框架

**运行此命令以识别您的框架：**

```bash
# 检查 package.json 依赖项（Node.js 项目）
cat package.json | grep -E "react|next|vue|nuxt|angular|express|fastify|@nestjs|expo"

# 或者检查项目文件
ls -la | grep -E "angular.json|vue.config.js|next.config|app.json|Package.swift|build.gradle"
```

**框架检测表：**

| 框架         | 检测方式     | 使用技能     |
|--------------|--------------|--------------|
| React (Vite/CRA) | package.json 中包含 "react"，不包含 Next.js | `auth0-react` |
| Next.js      | package.json 中包含 "next" | `auth0-nextjs` |
| Vue.js       | package.json 中包含 "vue"，不包含 Nuxt | `auth0-vue` |
| Nuxt         | package.json 中包含 "nuxt" | `auth0-nuxt` |
| Angular      | 存在 angular.json 或包含 "@angular/core" | `auth0-angular` |
| Express.js   | package.json 中包含 "express" | `auth0-express` |
| Fastify (Web 应用) | package.json 中包含 "fastify"，且包含 `@fastify/view` | `auth0-fastify` |
| Fastify (API)  | package.json 中包含 "fastify"，不包含视图引擎 | `auth0-fastify-api` |
| React Native  | package.json 中包含 "react-native" 或 "expo" | `auth0-react-native` |
| Flask        | requirements.txt、Pipfile 或 pyproject.toml 中包含 "flask" | `auth0-flask` |
| Node.js API   | package.json 中包含 "express-oauth2-jwt-bearer" | `express-oauth2-jwt-bearer` |
| ASP.NET Core Web 应用 | 存在 *.csproj 文件，且包含 `Views/` 或 `Pages/` 文件夹 | `auth0-aspnetcore-authentication` |

**未看到您的框架？** 请查看下方的 Tier 2 框架。

---

## 第 2 步：设置 Auth0 账户

### 安装 Auth0 CLI

**macOS/Linux:**
```bash
brew install auth0/auth0-cli/auth0
```

**Windows:**
```bash
scoop install auth0
# 或者：choco install auth0-cli
```

**完整安装指南：** 查看 [CLI 参考](references/cli.md#installation)

### 登录 Auth0

```bash
auth0 login
```

这将打开您的浏览器以使用 Auth0 进行身份验证。

---

## 第 3 步：创建 Auth0 应用

根据您的框架选择应用类型：

**单页应用 (React、Vue、Angular):**
```bash
auth0 apps create --name "My App" --type spa \
  --auth-method None \
  --callbacks "http://localhost:3000" \
  --logout-urls "http://localhost:3000" \
  --metadata "created_by=agent_skills"
```

**常规 Web 应用 (Next.js、Nuxt、Express、Fastify):**
```bash
auth0 apps create --name "My App" --type regular \
  --callbacks "http://localhost:3000/api/auth/callback" \
  --logout-urls "http://localhost:3000" \
  --metadata "created_by=agent_skills"
```

**原生应用 (React Native):**
```bash
auth0 apps create --name "My App" --type native \
  --auth-method None \
  --callbacks "myapp://callback" \
  --logout-urls "myapp://logout" \
  --metadata "created_by=agent_skills"
```

**获取您的凭证：**
```bash
auth0 apps list          # 查找您的应用
auth0 apps show <app-id> # 获取客户端 ID 和密钥
```

**更多 CLI 命令：** 查看 [CLI 参考](references/cli.md)

### 应用品牌（可选）

创建应用后，应用品牌以确保 Auth0 Universal Login 页面与您的应用匹配：

```bash
auth0 ul update \
  --accent "#YOUR_BRAND_COLOR" \
  --background "#YOUR_BACKGROUND_COLOR" \
  --logo "https://your-app.com/logo.png" \
  --favicon "https://your-app.com/favicon.ico"
```

这将确保用户在登录屏幕上看到的是您应用的品牌，而不是默认的 Auth0 品牌。您还可以使用 `acul-screen-generator` 技能进行完整的登录屏幕设计。

---

## 第 4 步：使用框架特定技能

根据您的框架检测结果，使用相应的技能：

### Tier 1 框架（专用技能）

**前端：**
- **`auth0-react`** - React SPAs (Vite, Create React App)
- **`auth0-nextjs`** - Next.js (App Router 和 Pages Router)
- **`auth0-vue`** - Vue.js 3 应用
- **`auth0-nuxt`** - Nuxt 3/4 应用
- **`auth0-angular`** - Angular 12+ 应用

**后端：**
- **`auth0-express`** - Express.js Web 应用
- **`auth0-flask`** - Flask Web 应用
- **`auth0-fastify`** - Fastify Web 应用
- **`auth0-fastify-api`** - Fastify API 身份验证
- **`express-oauth2-jwt-bearer`** - Node.js/Express API JWT Bearer 验证
- **`auth0-aspnetcore-authentication`** - ASP.NET Core MVC、Razor Pages、Blazor Server Web 应用

**移动端：**
- **`auth0-react-native`** - React Native 和 Expo (iOS/Android)

### Tier 2 框架（使用 Auth0 文档）

尚未作为单独技能提供。使用 Auth0 文档：

**前端：**
- [SvelteKit](https://auth0.com/docs/quickstart/webapp/sveltekit)
- [Remix](https://auth0.com/docs/quickstart/webapp/remix)

**后端：**
- [FastAPI (Python)](https://auth0.com/docs/quickstart/backend/python)
- [Django (Python)](https://auth0.com/docs/quickstart/webapp/django)
- [Rails (Ruby)](https://auth0.com/docs/quickstart/webapp/rails)
- [Laravel (PHP)](https://auth0.com/docs/quickstart/webapp/laravel)
- [Go](https://auth0.com/docs/quickstart/webapp/golang)
- [Spring Boot](https://auth0.com/docs/quickstart/webapp/java-spring-boot)

**移动端：**
- [iOS (Swift)](https://auth0.com/docs/quickstart/native/ios-swift)
- [Android (Kotlin)](https://auth0.com/docs/quickstart/native/android)
- [Flutter](https://auth0.com/docs/quickstart/native/flutter)

---

## 从其他提供者迁移

**从其他身份验证提供者迁移？** 使用 **`auth0-migration`** 技能。

迁移技能涵盖：
- 从 Firebase、Cognito、Supabase、Clerk 等处导出用户
- 批量导入到 Auth0
- 代码迁移模式（示例前后对比）
- JWT 验证更新
- 渐进式迁移策略

---

## 参考文档

### 环境变量
框架特定的环境变量设置：
- [Vite、Create React App、Angular](references/environments.md#single-page-applications-spas)
- [Next.js、Express](references/environments.md#server-side-applications)
- [React Native、Expo](references/environments.md#mobile-applications)

### Auth0 概念
核心概念和故障排除：
- [应用类型](references/concepts.md#application-types)
- [关键术语](references/concepts.md#key-terms)
- [OAuth 流程](references/concepts.md#oauth-flows)
- [故障排除](references/concepts.md#troubleshooting)
- [安全最佳实践](references/concepts.md#security-best-practices)

### CLI 命令
完整的 Auth0 CLI 参考：
- [CLI 安装](references/cli.md#installation)
- [创建应用](references/cli.md#creating-applications)
- [用户管理](references/cli.md#user-management)
- [测试与调试](references/cli.md#testing--debugging)
- [命令快速参考](references/cli.md#command-quick-reference)

---

## 常见错误

| 错误               | 修复方法             |
|--------------------|----------------------|
| 应用类型错误       | SPAs 需要使用 "Single Page Application"，服务器应用需要 "Regular Web Application"，移动应用需要 "Native" |
| 回调 URL 未配置   | 将您的应用的回调 URL 添加到 Auth0 控制面板中的允许回调 URL |
| 使用错误的凭证   | 客户端密钥仅适用于常规 Web 应用，不适用于 SPAs |
| 代码中硬编码凭证 | 始终使用环境变量，切勿将密钥提交到 git |
| 未先在本地测试   | 在部署到生产环境前，在 Auth0 中设置本地 URL |
| 混合应用类型     | 不要使用 SPA SDK 用于服务器端应用，反之亦然 |

---

## 相关技能

### 核心集成
- `auth0-migration` - 从其他身份验证提供者迁移

### SDK 技能
- `auth0-spa-js` - SPA 集成
- `auth0-react` - React SPA 集成
- `auth0-nextjs` - Next.js 集成
- `auth0-vue` - Vue.js 集成
- `auth0-nuxt` - Nuxt 3/4 集成
- `auth0-angular` - Angular 集成
- `auth0-express` - Express.js 集成
- `auth0-flask` - Flask Web 应用集成
- `auth0-fastify` - Fastify Web 应用集成
- `auth0-fastify-api` - Fastify API 集成
- `express-oauth2-jwt-bearer` - Node.js/Express API JWT Bearer 验证
- `auth0-react-native` - React Native CLI (裸流程) 集成
- `auth0-expo` - Expo (管理流程) 集成
- `auth0-android` - Android (Kotlin/Java) 集成
- `auth0-swift` - iOS/macOS (Swift) 集成
- `auth0-fastapi-api` - FastAPI API 验证
- `auth0-aspnetcore-authentication` - ASP.NET Core Web 应用验证
- `auth0-aspnetcore-api` - ASP.NET Core API 验证

### 高级功能
- `auth0-mfa` - 多因素身份验证

---

## 参考

- [Auth0 文档](https://auth0.com/docs)
- [Auth0 快速入门指南](https://auth0.com/docs/quickstart)
- [Auth0 CLI 文档](https://auth0.github.io/auth0-cli/)
- [Auth0 社区论坛](https://community.auth0.com/)
