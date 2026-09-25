# Clerk Expo (React Native)

在 Expo / React Native 项目中实现 Clerk。此技能内联了稳定表面的验证模式（提供者、令牌缓存、流程），并且需要检查已安装的 `@clerk/expo` 包的源代码以处理任何易变的内容（组件属性、钩子签名）。

## 激活规则

当以下任一条件为真时激活：
- 用户在 Expo 或 React Native 应用中请求身份验证，或在原生应用中提到 `@clerk/expo`、`ClerkProvider`、Expo Router 身份验证或 Clerk 钩子。
- 项目是 Expo/React Native (`app.json` / `app.config.js`、`package.json` 中的 `expo`、`metro.config.js`、`@clerk/expo` 依赖项)。

当以下情况发生时重定向：
- 原生 iOS/Swift 项目（`.xcodeproj`、`Package.swift`）→ `clerk-swift`
- 原生 Android/Kotlin 项目（`build.gradle` 不包含 React Native）→ `clerk-android`
- 仅 Web 框架（Next.js、Remix、纯 React 等）→ 匹配的框架技能

## 意图映射

匹配用户请求的内容，然后加载列表中列出的参考。仅加载任务所需的参考。

| 用户意图（示例） | 路径 | 参考 |
|------------------|------|------|
| "将身份验证添加到我的应用" / "使用 Clerk 添加登录" | 预构建的原生组件（默认） | references/setup.md + references/prebuilt-components.md |
| "添加身份验证" 但需要 Expo Go / Web / 自定义 UI | 自定义流程 | references/setup.md + references/custom-flows.md |
| "添加电话 / SMS 身份验证"、"电子邮件 OTP"、"无密码" | 自定义流程、`phoneCode` / `emailCode` | references/custom-flows.md |
| "使用 Google/Apple/GitHub 登录"、"社交登录"、"SSO" | 浏览器 SSO 或原生按钮 | references/sso-and-native-auth.md |
| "MFA / 2FA / TOTP"、"忘记密码"、"电子邮件链接" | 自定义流程添加 | references/custom-flows.md |
| "保护路由/屏幕"、"如果未登录则重定向" | Expo Router 保护 | references/protected-routes.md |
| "显示用户资料"、"组织切换"、"推送通知"、"注销"、"调用我的后端" | 应用配方 | references/recipes.md |
| "生物识别登录"、"Face ID"、"密钥" | 设备功能 | references/recipes.md |

## 默认路径决策

当用户说 "添加身份验证" 而未指定 UI 时：

1. **默认使用预构建的原生组件** (`AuthView` + `UserButton` 来自 `@clerk/expo/native`)。最快实现身份验证；UI 由 Clerk 维护。告知开发者他们处于测试阶段，需要开发构建版本。
2. **回退到自定义流程** 当以下任一条件成立时——切换时说明原因：
   - 项目必须在 Expo Go 中运行（无开发构建）。
   - 应用目标是 Web（原生组件在 Web 上无法渲染）。
   - 开发者希望自己的 UI 或特定的品牌体验，超出主题范围。
3. 如果开发者有现有的身份验证 UI，扩展现有内容——不要在没有请求的情况下移除自定义流程以插入 `AuthView`（反之亦然）。

不要将预构建组件和自定义流程混合用于同一身份验证步骤（例如 `AuthView` 加上自定义密码表单）。混合仅在开发者明确要求时允许。

## 快速工作流程

1. 确认项目类型（Expo/RN）并根据意图映射 / 默认路径规则选择路径。
2. 按照 references/setup.md：安装、环境密钥、提供者、令牌缓存、配置插件、构建类型。
3. 验证仪表板先决条件（下文 Gate 2 和 Gate 3）。
4. 仅根据选定的参考实现。
5. 通过构建验证，而不仅仅是编写：
   - 运行项目的类型检查 (`npx tsc --noEmit` 或等效)。
   - 构建并启动：`npx expo run:ios` / `run:android` 用于原生功能，`npx expo start` 用于 Expo Go 流程。如果构建失败，修复并迭代重建——针对已安装 SDK 的构建错误是在此技能和 SDK 产生分歧时的真实依据。在约 5 次失败的修复尝试后，停止并询问开发者如何继续，而不是反复折腾。
   - 带开发者走一个真实的登录，然后确认会话在应用重启后仍然存在（令牌缓存工作正常）。

## 执行门禁（不可跳过）

1. **可发布密钥** — 从 `process.env.EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY`（`.env` 文件）读取。绝不 `NEXT_PUBLIC_`，绝不硬编码。如果不存在密钥，请询问开发者获取一个（或运行 `npx clerk@latest init --framework expo`，这将安装 SDK 并写入环境文件），然后等待编辑文件之前。
2. **原生 API 仪表板开关** — Clerk 的原生 API 必须为实例启用：Clerk 仪表板 → **原生应用** (`https://dashboard.clerk.com/~/native-applications`)。告知开发者在设置期间验证此内容；它对于任何原生集成都是必需的。
3. **因子可用性** — 在实现特定策略（SMS、电子邮件代码、社交提供者）之前，确认它已为实例启用。从可发布密钥派生前端 API URL（解码中间段落的 base64）并获取 `<frontendApiUrl>/v1/environment?_is_native=true`，或询问开发者检查仪表板（**用户与身份验证**）。SMS 特别依赖于实例配置——为禁用的因子编写的代码在运行时失败，而不是在构建时。
4. **当前自定义流程 API 仅** — `useSignIn()` / `useSignUp()` 来自 `@clerk/expo`（v3.4+）返回 `{ signIn, errors, fetchStatus }` 并使用基于方法的流程：`signIn.password()`、`signIn.phoneCode.sendCode()`、`signIn.finalize()`。绝不生成遗留模式：从 `useSignIn()`/`useSignUp()` 解构 `isLoaded`/`setActive`（当前钩子不返回它们），或 `signIn.create()` 链接 `prepareFirstFactor()`/`attemptFirstFactor()` + `setActive({ session })`。该模式位于 `@clerk/expo/legacy`，仅用于维护现有遗留代码，绝不用于新工作。范围说明：`useAuth()`/`useUser()` 中的 `isLoaded` 是当前 API，在保护中是必需的；`signIn.create()` 本身仍然存在用于高级用例——优先使用特定因子的方法。
5. **`useSSO()`，绝不 `useOAuth()`** — `useOAuth` 已弃用。注意不对称性：`startSSOFlow()` 仍然返回 `{ createdSessionId, setActive }` 并需要 `setActive({ session: createdSessionId })`——SSO 不使用 `finalize()`。
6. **令牌缓存** — 来自 `@clerk/expo/token-cache` 的 `tokenCache` 在 `ClerkProvider` 上。绝不直接使用 `expo-secure-store` 处理会话令牌，绝不使用 AsyncStorage。
7. **`resourceCache`，绝不 `secureStore`** — 如果出现离线资源缓存，`@clerk/expo/secure-store` 已弃用；使用来自 `@clerk/expo/resource-cache` 的 `resourceCache`。
8. **构建类型门禁** — 原生组件 (`@clerk/expo/native`) 和原生钩子 (`useSignInWithGoogle`、`useSignInWithApple`、`useLocalCredentials`) 需要开发构建 (`npx expo run:ios` / `run:android`)，不是 Expo Go，并且在 Web 上不存在。对于 Web 目标，使用 `@clerk/expo/web` 组件或自定义流程。在实现原生独有功能之前说明构建要求。
9. **组合登录或注册默认** — 除非开发者要求单独的登录和注册屏幕，否则使用一个组合流程。
10. **机器人保护** — 自定义注册屏幕必须渲染 `<View nativeID="clerk-captcha" />`；Clerk 的机器人保护默认启用，需要此挂载点。
11. **易变表面源验证** — 在使用原生组件属性或原生钩子选项之前，确认与已安装的包：`node_modules/@clerk/expo/dist/native/*.d.ts` 和 `package.json` `exports`。如果存在分歧，已安装的版本优先于此技能。
12. **新鲜度门禁** — 此技能针对 `@clerk/expo` 3.6.x 进行了验证。检查已安装版本 (`node_modules/@clerk/expo/package.json`)。如果它是更新的次要版本或主要版本，将此技能的代码片段视为可疑：重新验证旁边引用的文档 URL（每个参考部分都带有一个）或已安装的 `.d.ts` 之前使用它们。如果它比 3.4 更旧，基于方法的自定义流程 API 可能不存在——提供升级而不是编写遗留代码。

## 版本说明（v3.5–v3.6，2026 年 6 月）

- 最小 React Native 提高到 **0.75** 在 v3.5.0（iOS SDK 现在通过 SPM podspec 链接）。同伴范围：`expo >=53 <57`。
- 原生组件成熟：iOS 转移到 Expo Modules；原生↔JS 会话同步是自动和双向的——原生组件认证后永不调用 `setActive()`。
- 配置插件接受一个 `theme` JSON 文件用于原生组件样式（见 references/prebuilt-components.md）。
- 原生 Google 登录将迁移到下一个主要版本的单独 `@clerk/expo-google-signin` 包（`@clerk/expo/google` 导入在 v3 中仍然有效；开发警告宣布迁移）。不要在 v3 中预安装新包。

## 常见陷阱

| 级别 | 问题 | 预防 |
|------|------|------|
| CRITICAL | 生成遗留自定义流程代码 (`signIn.create` + `prepareFirstFactor` + `setActive`) | 使用当前基于方法的 API（Gate 4） |
| CRITICAL | 使用 `useOAuth()` | 使用 `useSSO()`（Gate 5） |
| CRITICAL | 在未检查因子已启用的情况下实现 SMS/社交认证 | 首先检查环境/仪表板（Gate 3） |
| CRITICAL | 针对 Expo Go 或 Web 的原生组件 | 需要开发构建；否则提供自定义流程（Gate 8） |
| CRITICAL | 注册屏幕缺少 `<View nativeID="clerk-captcha" />` | 始终包含它（Gate 10） |
| HIGH | `NEXT_PUBLIC_` 环境前缀，或在 `node_modules` 内读取环境变量 | `EXPO_PUBLIC_CLERK_PUBLISHABLE_KEY`，显式传递给 `ClerkProvider` |
| HIGH | 重启时丢失会话 | 来自 `@clerk/expo/token-cache` 的 `tokenCache` 在提供者上 |
| HIGH | 在 `AuthView` / `UserButton` 认证后调用 `setActive()` | 原生组件自动同步会话 |
| HIGH | 将 `AuthView` 与 `useSignInWithGoogle`/`useSignInWithApple` 配对 | `AuthView` 自动渲染启用的社交提供者 |
| HIGH | 手动调用 `WebBrowser.maybeCompleteAuthSession()` | `ClerkProvider` 处理它 |
| HIGH | 未被请求的情况下拆分登录/注册 | 默认组合流程（Gate 9） |
| MEDIUM | 在保护中 `isLoaded` 检查之前使用 `isSignedIn` | 始终首先基于 `isLoaded` 进行门控 |
| MEDIUM | 使用 `yalc`/`pnpm link` 进行本地 `@clerk/expo` 开发 | 使用 Verdaccio 或 pkg.pr.new |

## 参见

- `clerk` — 顶级路由
- `clerk-swift` / `clerk-android` — 原生移动 SDK
- `clerk-orgs`、`clerk-billing`、`clerk-webhooks` — 功能技能（在 Expo 中钩子工作方式相同）
- 已安装包源：`node_modules/@clerk/expo/`
- https://clerk.com/docs/getting-started/quickstart（Expo SDK 标签页）
- https://clerk.com/docs/reference/expo/overview
- https://github.com/clerk/clerk-expo-quickstart — 三个官方示例应用：仅 JS（Expo Go）、JS + 原生登录按钮、原生组件
