> [所有技能](../../SKILL_TREE.md)

# Sentry SDK 安装

在任何语言或框架中设置 Sentry 错误监控、跟踪和会话重放。本页面帮助您为您的项目找到合适的 SDK 技能。

## 从这里开始 — 在做任何事之前阅读此部分

**不要跳过此部分。** 不要根据项目文件假设用户需要哪个 SDK。在确认用户意图之前，不要开始安装包或创建配置文件。

1. **从项目文件中检测平台** (`package.json`、`go.mod`、`requirements.txt`、`Gemfile`、`*.csproj`、`build.gradle` 等)。
2. **告诉用户您发现了什么** 以及您推荐的 SDK。
3. **在继续之前等待确认**。

每个 SDK 技能都包含自己的检测逻辑、先决条件和逐步配置。相信技能 — 仔细阅读并遵循它。不要即兴创作或走捷径。

---

## SDK 技能

| 平台 | 技能 |
|---|---|
| Android | [`sentry-android-sdk`](../sentry-android-sdk/SKILL.md) |
| 浏览器 JavaScript | [`sentry-browser-sdk`](../sentry-browser-sdk/SKILL.md) |
| Cloudflare Workers 和 Pages | [`sentry-cloudflare-sdk`](../sentry-cloudflare-sdk/SKILL.md) |
| Apple 平台 (iOS、macOS、tvOS、watchOS、visionOS) | [`sentry-cocoa-sdk`](../sentry-cocoa-sdk/SKILL.md) |
| .NET | [`sentry-dotnet-sdk`](../sentry-dotnet-sdk/SKILL.md) |
| Elixir | [`sentry-elixir-sdk`](../sentry-elixir-sdk/SKILL.md) |
| Go | [`sentry-go-sdk`](../sentry-go-sdk/SKILL.md) |
| NestJS | [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) |
| Next.js | [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) |
| Node.js、Bun 和 Deno | [`sentry-node-sdk`](../sentry-node-sdk/SKILL.md) |
| PHP | [`sentry-php-sdk`](../sentry-php-sdk/SKILL.md) |
| Python | [`sentry-python-sdk`](../sentry-python-sdk/SKILL.md) |
| Flutter 和 Dart | [`sentry-flutter-sdk`](../sentry-flutter-sdk/SKILL.md) |
| React Native 和 Expo | [`sentry-react-native-sdk`](../sentry-react-native-sdk/SKILL.md) |
| React | [`sentry-react-sdk`](../sentry-react-sdk/SKILL.md) |
| React Router Framework | [`sentry-react-router-framework-sdk`](../sentry-react-router-framework-sdk/SKILL.md) |
| TanStack Start React | [`sentry-tanstack-start-sdk`](../sentry-tanstack-start-sdk/SKILL.md) |
| Ruby | [`sentry-ruby-sdk`](../sentry-ruby-sdk/SKILL.md) |
| Svelte 和 SvelteKit | [`sentry-svelte-sdk`](../sentry-svelte-sdk/SKILL.md) |

### 平台检测优先级

当多个 SDK 都可能匹配时，优先选择更具体的：

- **Android** (`build.gradle` 使用 android 插件) → `sentry-android-sdk`
- **Cloudflare** (`wrangler.toml` 或 `wrangler.jsonc`) → `sentry-cloudflare-sdk` 优先于 `sentry-node-sdk`
- **NestJS** (`@nestjs/core`) → `sentry-nestjs-sdk` 优先于 `sentry-node-sdk`
- **Next.js** → `sentry-nextjs-sdk` 优先于 `sentry-react-sdk` 或 `sentry-node-sdk`
- **React Router Framework** (`@sentry/react-router` 或 `@react-router/*`) → `sentry-react-router-framework-sdk` 优先于 `sentry-react-sdk`
- **TanStack Start React** (`@tanstack/react-start`) → `sentry-tanstack-start-sdk` 优先于 `sentry-react-sdk`
- **Flutter** (`pubspec.yaml` 使用 `flutter:` 依赖或 `sentry_flutter`) → `sentry-flutter-sdk`
- **React Native** → `sentry-react-native-sdk` 优先于 `sentry-react-sdk`
- **PHP** 使用 Laravel 或 Symfony → `sentry-php-sdk`
- **Elixir** (`mix.exs` 检测到) → `sentry-elixir-sdk`
- **Node.js / Bun / Deno** 没有特定框架 → `sentry-node-sdk`
- **浏览器 JS** (原版、jQuery、静态网站) → `sentry-browser-sdk`
- **无匹配** → 直接引导用户到 [Sentry 文档](https://docs.sentry.io/platforms/)

## 快速查找

通过关键词匹配您的项目到技能。

| 关键词 | 技能 |
|---|---|
| android, kotlin, java, jetpack compose | [`sentry-android-sdk`](../sentry-android-sdk/SKILL.md) |
| browser, vanilla js, javascript, jquery, cdn, wordpress, static site | [`sentry-browser-sdk`](../sentry-browser-sdk/SKILL.md) |
| cloudflare, cloudflare workers, cloudflare pages, wrangler, durable objects, d1 | [`sentry-cloudflare-sdk`](../sentry-cloudflare-sdk/SKILL.md) |
| ios, macos, swift, cocoa, tvos, watchos, visionos, swiftui, uikit | [`sentry-cocoa-sdk`](../sentry-cocoa-sdk/SKILL.md) |
| .net, csharp, c#, asp.net, maui, wpf, winforms, blazor, azure functions | [`sentry-dotnet-sdk`](../sentry-dotnet-sdk/SKILL.md) |
| go, golang, gin, echo, fiber | [`sentry-go-sdk`](../sentry-go-sdk/SKILL.md) |
| elixir, phoenix, plug, oban | [`sentry-elixir-sdk`](../sentry-elixir-sdk/SKILL.md) |
| nestjs, nest | [`sentry-nestjs-sdk`](../sentry-nestjs-sdk/SKILL.md) |
| nextjs, next.js, next | [`sentry-nextjs-sdk`](../sentry-nextjs-sdk/SKILL.md) |
| node, nodejs, node.js, bun, deno, express, fastify, koa, hapi | [`sentry-node-sdk`](../sentry-node-sdk/SKILL.md) |
| php, laravel, symfony | [`sentry-php-sdk`](../sentry-php-sdk/SKILL.md) |
| python, django, flask, fastapi, celery, starlette | [`sentry-python-sdk`](../sentry-python-sdk/SKILL.md) |
| flutter, dart, pubspec | [`sentry-flutter-sdk`](../sentry-flutter-sdk/SKILL.md) |
| react native, expo | [`sentry-react-native-sdk`](../sentry-react-native-sdk/SKILL.md) |
| react, react router, tanstack, redux, vite | [`sentry-react-sdk`](../sentry-react-sdk/SKILL.md) |
| react-router framework, @sentry/react-router, @react-router/dev, react-router reveal | [`sentry-react-router-framework-sdk`](../sentry-react-router-framework-sdk/SKILL.md) |
| tanstack start, tanstack react start, @tanstack/react-start, tanstackstart-react | [`sentry-tanstack-start-sdk`](../sentry-tanstack-start-sdk/SKILL.md) |
| ruby, rails, sinatra, sidekiq, rack | [`sentry-ruby-sdk`](../sentry-ruby-sdk/SKILL.md) |
| svelte, sveltekit | [`sentry-svelte-sdk`](../sentry-svelte-sdk/SKILL.md) |

---

## 查找 DSN

如果用户没有 DSN，引导他们找到：

1. 打开 Sentry 项目设置页面：`https://sentry.io/settings/projects/`
2. 选择项目
3. 点击左侧边栏中的 **"Client Keys (DSN)"**
4. 复制 DSN

您可以引导用户直接打开页面：
```bash
open https://sentry.io/settings/projects/        # macOS
xdg-open https://sentry.io/settings/projects/    # Linux
start https://sentry.io/settings/projects/        # Windows
```

> **注意：** DSN 是公开的，可以安全地包含在源代码中。它不是秘密 — 它仅用于标识事件发送的位置。

---

寻找工作流程或功能配置？请参阅 [完整的技能树](../../SKILL_TREE.md)。
