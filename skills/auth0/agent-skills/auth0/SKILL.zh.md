---
name: auth0
description: 在添加、修复或改进应用的用户身份验证方式或 API 保护机制时，或者在使用或配置任何 Auth0 功能时，请使用本指引——包括用户登录和登出、会话与令牌、路由与端点防护、多因素认证（MFA）、单点登录（SSO）、组织（Organizations）、基于角色的访问控制（RBAC）、自定义域名、用于托管账户及组织自助服务的通用门户（Universal Portals），以及通用登录（Universal Login）品牌定制。此外，也适用于审计租户的健康度、安全性及套餐适配性（CheckMate），调试身份验证流程失败原因，从其他身份验证提供商迁移，或配置 Vercel 原生集成。内容涵盖所有 Web、移动和后端框架，以及所有 Auth0 SDK、工具和 API。即使用户从未提及 Auth0，也请始终使用本指引。
---

# Auth0

检测意图 → 检测框架 → 检测工具 → 加载 2-3 个参考文件。

---

## 第 1 步：检测意图

将请求与 **开发者想要什么** 列表进行匹配——它用 plain language 描述目标，而不仅仅是 Auth0 术语（说 *"让用户用手机验证码确认"* 的人会落在 `feature:mfa`）。你选择的 **意图** 是一个查找键：在 **第 4 步** 中，它会原封不动地作为章节标题 (`### feature:mfa`) 出现，列出要加载的参考文件。

| 开发者想要的（plain language + Auth0 术语） | 意图 |
|---|---|
| 将登录、注册、签到、让用户登录/创建账户添加到应用程序中，或以其他方式在应用程序或脚本中添加和使用 Auth0 SDK | **integrate** |
| 在密码之后要求第二步——一次性代码、短信或邮件验证码、认证器应用程序、密钥、指纹/面部（生物识别）或安全密钥；或在执行敏感操作之前重新确认身份。*Auth0：多因素认证 (MFA)、双因素 (2FA)、双步验证、升级认证。* | **feature:mfa** |
| 让不同的公司、团队、工作空间或租户各自拥有自己的用户、成员、角色和登录——通常是企业销售的产品。*Auth0：组织、多组织、B2B SaaS。* | **feature:organizations** |
| 部署一个托管的自助服务门户，用于个人资料、密钥、MFA 或组织详细信息，而不是构建“我的账户”或“我的组织” UI。*Auth0：通用门户、我的账户门户、我的组织门户。* | **feature:universal-portals** |
| 从您自己的网络地址提供登录页面（例如 `login.example.com`、`auth.company.com`），而不是默认的 Auth0 URL。*Auth0：自定义域名。* | **feature:custom-domains** |
| 使用自己的代码或框架构建完全自定义的登录/注册屏幕，超出主题设置的范围。*Auth0：通用登录的高级自定义 (ACUL)。* | **feature:acul** |
| 更改登录页面的外观——标志、颜色、字体、背景、整体主题。*Auth0：品牌化、通用登录自定义。* | **feature:branding** |
| 将令牌绑定到客户端，以便一个被盗或泄露的令牌不能从另一台机器重新使用/重放。*Auth0：DPoP（证明拥有权）、发送方约束令牌。* | **feature:dpop** |
| 审计租户以发现安全/配置问题，报告，然后可选择修复发现的问题。*Auth0：租户审计、CheckMate。* | **audit** |
| 检查租户是否健康并在正确的计划上——两个分数 + 推荐意见。*Auth0：健康检查。* | **healthcheck** |
| 寻求最佳实践、"这是安全的吗？"、如何安全地处理令牌、"我应该怎么做 X"。*Auth0：指导/安全。* | **guidance** |
| 遇到错误：401 未授权、403 禁止、CORS、回调 URL 不匹配、重定向循环。*Auth0：调试。* | **debug** |
| 遇到速率限制：429 请求过多、配额超出。*Auth0：速率限制。* | **debug:rate-limit** |
| 将现有应用程序从 Clerk、NextAuth.js、Firebase、Cognito、Okta、Supabase、Passport.js 或其他身份提供商迁移。*Auth0：提供商迁移。* | **migrate** |
| 将 Auth0 SDK 本身升级到新的主版本（例如 Auth0.swift v2→v3、Auth0.Android v3→v4）——存在破坏性变更、弃用 API、"更新到最新的 SDK"。*Auth0：SDK 主版本升级。* | **upgrade-sdk** |
| 安装 Auth0 的 Vercel Marketplace 集成，将 Auth0 连接到 Vercel 项目，或将 Auth0 配置同步到 Vercel 托管的 Next.js 应用程序。*Auth0：Vercel 原生集成。* | **integrate** |
| 直接使用 Auth0 CLI——"使用 `auth0` CLI 创建应用程序/API"、"脚本租户设置" 或在 CI 中自动化 Auth0 配置——没有任何应用程序框架参与。*Auth0：CLI / 仅工具。* | **tooling** |

### 如果没有明确匹配

选择最接近的目标。如果目标确实不明确，请询问开发者他们试图完成什么——不要猜测意图。

---

## 第 2 步：检测框架

> **对于 `tooling` 意图跳过此步骤**——CLI 首选请求没有框架。跳到第 3 步，加载工具参考；只有当开发者后来转向将身份验证集成到应用程序中时才询问框架。

自上而下工作。**在第一个匹配框架的层级停止。**

### 第 1 层级——Auth0 SDK 已安装（最强信号）

### Node.js / JavaScript / TypeScript —— 检查 `package.json` → `dependencies`

行是最具体的优先：Ionic/Capacitor 项目也包含基础 SDK，因此检查 `@capacitor/browser` 行之前先检查它。

| 包 | 框架 |
|---|---|
| `@capacitor/browser` + `@auth0/auth0-angular` | `ionic-angular` |
| `@capacitor/browser` + `@auth0/auth0-react` | `ionic-react` |
| `@capacitor/browser` + `@auth0/auth0-vue` | `ionic-vue` |
| `@auth0/nextjs-auth0` | `nextjs` |
| `@auth0/auth0-nuxt` | `nuxt` |
| `@auth0/auth0-tanstack-start-react` | `tanstack-start` |
| `@auth0/auth0-react` | `react` |
| `@auth0/auth0-vue` | `vue` |
| `@auth0/auth0-angular` | `angular` |
| `@auth0/auth0-spa-js` | `spa-js` |
| `express-openid-connect` | `express` |
| `@auth0/auth0-fastify` | `fastify` |
| `@auth0/auth0-fastify-api` | `fastify-api` |
| `express-oauth2-jwt-bearer` | `express-jwt` |
| `react-native-auth0` + `app.json` 或 `app.config.js` 存在 | `expo` |
| `react-native-auth0`（没有 Expo 文件） | `react-native` |
| `@auth0/auth0-api-js` | `auth0-api-js` |
| `@auth0/auth0-server-js` | `auth0-server-js` |
| `@auth0/auth0-auth-js` | `auth0-auth-js` |
| `auth0`（裸包，不是 `@auth0/*`） | `node-auth0` |

### Python —— 检查 `requirements.txt` 或 `pyproject.toml`

行是最具体的优先：`auth0-server-python` 是无框架的服务器核心，因此检查是否同时安装了 Web 框架，然后再回退到裸 SDK 行。

| 包 | 框架 |
|---|---|
| `auth0-server-python` + `flask` | `flask` |
| `auth0-server-python`（没有 Flask Web 框架） | `server-python` |
| `auth0-fastapi-api` | `fastapi-api` |

### Java / Kotlin —— 检查 `build.gradle` 或 `pom.xml`

| 依赖项 | 框架 |
|---|---|
| `mvc-auth-commons` (`com.auth0:mvc-auth-commons`) | `java-mvc` |
| `spring-security-oauth2-resource-server` | `springboot-api` |

### .NET —— 检查 `*.csproj` 或 `NuGet.Config`

| 包 | 框架 |
|---|---|
| `Auth0.AspNetCore.Authentication`（没有 `.Api` 后缀） | `aspnetcore-auth` |
| `Auth0.AspNetCore.Authentication.Api` | `aspnetcore-api` |
| `Auth0.OidcClient.MAUI` | `maui` |
| `Auth0.OidcClient.AndroidX` | `net-android` |
| `Auth0.OidcClient.iOS` | `net-ios` |
| `Auth0.OidcClient.WinForms` | `winforms` |
| `Auth0.OidcClient.WPF` | `wpf` |

### PHP —— 检查 `composer.json`

`auth0/auth0-php` 通过 `SdkConfiguration` 的 `strategy` 为 PHP Web 应用程序和 API 提供动力。`STRATEGY_API` 行更具体——首先检查它。

| 包 | 框架 |
|---|---|
| `auth0/auth0-php` + `SdkConfiguration::STRATEGY_API`（或 `strategy: 'api'`） | `php-api` |
| `auth0/auth0-php`（没有 `STRATEGY_API` / `STRATEGY_REGULAR` 或 `strategy: 'webapp'`） | `php` |
| `auth0/login`（Laravel，没有 `AuthorizationGuard`） | `laravel` |
| `auth0/login` + `AuthorizationGuard` | `laravel-api` |

> 如果安装了 `auth0/auth0-php` 但尚未设置 `SdkConfiguration` 策略（新项目），则回退到以下变体区分。

### Go —— 检查 `go.mod`

| 模块 | 框架 |
|---|---|
| `github.com/auth0/go-jwt-middleware` | `go` |

### 移动（原生）

| 信号 | 框架 |
|---|---|
| `build.gradle(.kts)` + `com.auth0.kmp:auth0`（Kotlin 多平台模块） | `kmp` |
| `Package.swift` 或 `.xcodeproj` + Auth0.swift | `swift` |
| `build.gradle` + `com.auth0.android:auth0` | `android` |
| `pubspec.yaml` + `auth0_flutter` + 开发者名称/目标 Windows 桌面 | `flutter-windows` |
| `pubspec.yaml` + `auth0_flutter` + `flutter.web: false` | `flutter-native` |
| `pubspec.yaml` + `auth0_flutter` + 启用 Web | `flutter-web` |

### 第 2 层级——非 Auth0 工作空间依赖项的框架

如果没有匹配的 Auth0 SDK，则从普通（非 Auth0）依赖项检测框架。**在第一个匹配时停止。** 这会选中基础版本；任何 Web vs API 变体都在下面的“变体区分”中解决。与第 1 层级一样，在检查 `@ionic/*` 行之前先检查它们。

| 信号 | 基础框架 |
|---|---|
| `package.json` 中的 `next` | `nextjs` |
| `package.json` 中的 `nuxt` | `nuxt` |
| `package.json` 中的 `@tanstack/react-start` | `tanstack-start` |
| `package.json` 中的 `@ionic/*` + `@angular/core` | `ionic-angular` |
| `package.json` 中的 `@ionic/*` + `react` | `ionic-react` |
| `package.json` 中的 `@ionic/*` + `vue` | `ionic-vue` |
| `package.json` 中的 `@angular/core` | `angular` |
| `package.json` 中的 `vue`（没有 `nuxt`） | `vue` |
| `package.json` 中的 `expo` | `expo` |
| `react-native`（没有 `expo`） | `react-native` |
| `react`（没有上述元框架） | `react`（SPA）——见注释 |
| `package.json` 中的 `express` | `express`（变体下方） |
| `package.json` 中的 `fastify` | `fastify`（变体下方） |
| `requirements.txt`/`pyproject.toml` 中的 `flask` | `flask` |
| `requirements.txt`/`pyproject.toml` 中的 `fastapi` | `fastapi-api`（变体下方） |
| `pom.xml`/`build.gradle` 中的 `spring-boot` | `springboot-api` |
| `composer.json` 中的 `laravel/framework` | `laravel`（变体下方） |
| `composer.json` 存在（没有 Laravel） | `php`（变体下方） |
| `go.mod` 存在 + HTTP 服务器/路由器 | `go` |
| `org.jetbrains.kotlin.multiplatform` 插件 + `commonMain` 源集（共享 Android+iOS 模块） | `kmp` |
| `Package.swift` 或 `.xcodeproj` | `swift` |
| `pubspec.yaml`（Flutter） + 开发者名称/目标 Windows 桌面 | `flutter-windows` |
| `pubspec.yaml`（Flutter，Web 禁用） | `flutter-native` |
| `pubspec.yaml`（Flutter，Web 启用） | `flutter-web` |
| `*.csproj` 引用 MAUI | `maui` |
| `*.csproj`（WinForms） | `winforms` |
| `*.csproj`（WPF） | `wpf` |
| `*.csproj` ASP.NET（Web 应用程序或 API） | `aspnetcore`（变体下方） |

> **`react` 注释：** 一个纯 React 项目映射到 `react`，用于使用 React SDK 的 SPA，或者如果应用程序是框架无关的纯 JS，则映射到 `spa-js`。如果不确定，请在加载前询问。

### 第 3 层级——提示中的框架

如果没有工作空间信号匹配，则映射请求中提到的框架或语言。**在第一个匹配时停止。**

| 开发者提到... | 框架 |
|---|---|
| Next.js / `next` | `nextjs` |
| Nuxt | `nuxt` |
| TanStack Start（React） | `tanstack-start` |
| Angular（非 Ionic） | `angular` |
| Vue（非 Nuxt/Ionic） | `vue` |
| React SPA（非 Next.js） | `react` |
| 纯 JS / 纯 JS / 无框架 SPA | `spa-js` |
| node-auth0 / `auth0` npm 包 | `node-auth0` |
| `@auth0/auth0-api-js` / auth0-api-js / 低级资源服务器 SDK | `auth0-api-js` |
| `@auth0/auth0-server-js` / auth0-server-js / 服务器端 Auth0 会话 SDK | `auth0-server-js` |
| `@auth0/auth0-auth-js` / auth0-auth-js / AuthClient / 低级 OAuth OIDC | `auth0-auth-js` |
| Express（Web 应用程序 / 服务器渲染） | `express` |
| Express API / 保护 API 路径 | `express-jwt` |
| Fastify（Web） / Fastify API | `fastify` / `fastify-api` |
| Flask | `flask` |
| FastAPI（Web 应用程序） / FastAPI API | `server-python` / `fastapi-api` |
| `auth0-server-python` / 无框架的 Python 服务器 SDK / 没有专用参考的 Python OIDC Web 服务器（Django、Starlette、Sanic、Quart、aiohttp） | `server-python` |
| Spring Boot | `springboot-api` |
| Java MVC / servlet | `java-mvc` |
| ASP.NET Core Web 应用程序 / API | `aspnetcore-auth` / `aspnetcore-api` |
| MAUI / WinForms / WPF | `maui` / `winforms` / `wpf` |
| PHP Web 应用程序 / PHP API | `php` / `php-api` |
| Laravel Web 应用程序 / Laravel API | `laravel` / `laravel-api` |
| Go / Golang API | `go` |
| Kotlin Multiplatform / KMP / 共享 Android+iOS 身份验证代码 / `com.auth0.kmp` | `kmp` |
| Swift / iOS | `swift` |
| Android / Kotlin | `android` |
| Flutter（原生 / Web / Windows） | `flutter-native` / `flutter-web` / `flutter-windows` |
| React Native / Expo | `react-native` / `expo` |
| Ionic（Angular/React/Vue） | `ionic-angular` / `ionic-react` / `ionic-vue` |

### 变体区分（Web 应用程序 vs API）

某些框架有 Web 应用程序和 API 参考的分离版本。当第 1 层级未能固定变体时，选择 **意图优先**：

| 基础 | Web 应用程序变体 | API 变体 | 在以下情况下选择 API... |
|---|---|---|---|
| express | `express` | `express-jwt` | 保护 API 路径 / 验证 JWTs，没有服务器渲染 UI |
| fastify | `fastify` | `fastify-api` | 资源服务器 / 仅 JWT 验证 |
| fastapi | `server-python` | `fastapi-api` | 资源服务器 / 仅 JWT 验证；具有登录/登出 UI 的 Web 应用程序使用 `server-python` |
| php | `php` | `php-api` | 构建/保护 PHP API，没有 Web UI |
| laravel | `laravel` | `laravel-api` | API 仅（令牌守卫），没有 Blade UI |
| aspnetcore | `aspnetcore-auth` | `aspnetcore-api` | Web API / JWT 带宽，没有 Cookie 登录 UI |

如果意图仍然不明确（既是 UI 又是受保护的端点，或不确定），**说明检测到的内容并询问开发者** Web 应用程序 vs API，然后再加载。

### 如果没有匹配

询问开发者他们使用什么框架/语言。不要猜测。

### 冲突

如果第 2 层级（工作空间）和第 3 层级（提示）在实质性方面不一致（例如，提示说 "Next.js"，但 `package.json` 没有包含 `next`），**说明冲突并询问**，而不是默默选择。当两者都存在且一致时，工作空间信号优先于提示。

---

## 第 3 步：检测工具

读取项目文件树和请求——这是一个项目上下文决策，而不是产品偏好。

| 项目包含... | 加载 |
|---|---|
| `terraform/` 目录 OR 任何 `*.tf` 文件 | `tooling-terraform/index.md` |
| 此代理会话中激活的 Auth0 MCP 服务器 | `tooling-mcp/index.md` |
| 请求 Auth0 Vercel Marketplace/原生集成，或将 Auth0 连接到 Vercel 项目 | `tooling-vercel/index.md` |
| 其他任何内容（默认） | `tooling-cli/index.md` |

---

## 第 4 步：加载参考文件

找到第 1 步中你选择的 **意图** 下面的章节，然后阅读它列出的参考文件。

### integrate
```
读取：references/framework-{framework}/index.md
读取：references/tooling-{tooling}/index.md
按照 references/framework-{framework}/index.md 中的集成工作流程进行操作。
使用 references/tooling-{tooling}/index.md 进行所有 Auth0 租户配置步骤。
```

### feature:mfa
```
读取：references/feature-mfa/index.md
读取：references/tooling-{tooling}/index.md
```

### feature:organizations
```
读取：references/feature-organizations/index.md
读取：references/tooling-{tooling}/index.md
如果检测到框架：读取 references/framework-{framework}/index.md
如果多租户架构 / B2B SaaS 设计问题：也读取 references/pattern-multi-tenant/index.md
```

### feature:universal-portals
```
读取：references/feature-universal-portals/index.md
读取：references/tooling-{tooling}/index.md
```

### feature:custom-domains
```
读取：references/feature-custom-domains/index.md
读取：references/tooling-{tooling}/index.md
```

### feature:acul
```
读取：references/feature-acul/index.md
读取：references/tooling-{tooling}/index.md
```

### feature:branding
```
读取：references/feature-branding/index.md
读取：references/tooling-{tooling}/index.md
```

### feature:dpop
```
读取：references/feature-dpop/index.md
读取：references/tooling-{tooling}/index.md
如果检测到 SPA 框架（vue/react/angular/spa-js）：读取 references/framework-{framework}/index.md
DPoP 仅限 SPA（无 SSR：Next.js/Nuxt）—— feature-dpop/index.md 指出排除。
```

### guidance
```
读取：references/pattern-security/index.md
如果检测到框架：读取 references/framework-{framework}/index.md（用于 SDK 特定指导——令牌存储、会话处理、路由保护）
如果令牌处理 / JWT vs 透明 / 存储：读取 references/pattern-token-handling/index.md
如果多租户 / B2B 架构：读取 references/pattern-multi-tenant/index.md + references/feature-organizations/index.md
```

### debug
```
读取：references/pattern-common-errors/index.md
如果检测到框架：读取 references/framework-{framework}/index.md
```

### debug:rate-limit
```
读取：references/pattern-rate-limiting/index.md
```

### migrate
```
读取：references/feature-migration/index.md
读取：references/tooling-{tooling}/index.md
如果检测到框架：读取 references/framework-{framework}/index.md
```

### audit
```
读取：references/feature-audit/index.md
读取：references/feature-audit-pricing/index.md
读取：references/feature-audit-remediation/index.md
读取：references/tooling-{tooling}/index.md
仅凭每条命令的确认来应用发现结果；通过重新获取来验证每个更改。
```

### healthcheck
```
读取：references/feature-healthcheck/index.md
读取：references/feature-audit/index.md
读取：references/feature-audit-pricing/index.md
读取：references/feature-audit-remediation/index.md
读取：references/tooling-{tooling}/index.md
如果可以运行扫描，则先执行审计工作流，然后评分并推荐计划。如果不行，则评分能力匹配并无论如何都推荐。永远不要引用企业定价。
```

### upgrade-sdk
```
读取：references/framework-{framework}/index.md
遵循其“主要版本迁移”部分（例如 Auth0.swift v3，Auth0.Android v4）。
这是一个 Auth0 SDK 版本升级——不是提供者迁移。不要加载 feature-migration/index.md。
如果没有检测到框架：询问开发者正在升级哪个 Auth0 SDK。
```

### tooling
```
读取：references/tooling-{tooling}/index.md
没有框架文件——这是一个仅 CLI/工具的任务（创建应用/API，脚本租户设置，在 CI 中自动化配置）。
如果开发者然后想要将认证集成到应用中，返回步骤 1 并带有集成意图。
```
