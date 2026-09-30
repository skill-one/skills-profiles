---
name: clerk-setup
description: 使用 Clerk CLI 和官方框架快速入门，在任何项目中设置 Clerk 认证。在添加 Clerk、初始化 Clerk、使用 Clerk 搭建新应用，或迁移现有认证系统到 Clerk 时使用。
---

# 设置 Clerk

使用 [Clerk CLI](https://clerk.com/docs/cli) 添加身份验证。在代理环境中，支持的框架默认为无账户设置：`npx -y clerk@latest init --no-skills` 会创建一个可认领的应用并写入临时开发密钥，而无需使用 Clerk 账户。

## 开始前

向用户展示此清单并等待确认：

```
我会执行以下操作来帮助您使用 Clerk 进行设置。

1. 在此项目中设置 Clerk，如果此目录为空，则搭建一个新应用。
2. 使用 Clerk 安装的应用启动您的应用。

是否继续？
```

## 现有身份验证

在 `init` 之前，检查身份验证依赖项、路由、中间件、会话和用户记录——永远不要修改环境文件。如果存在其他身份验证提供者，请停止并获取迁移计划的批准，包括：

- 后端 API 用户导入、稳定的外部 ID、兼容的密码哈希和 OAuth 连续性。
- 受保护的路线、令牌、会话切换和发布策略。

未经批准，不要修改或删除现有的身份验证。

查看 [迁移指南](https://clerk.com/docs/guides/development/migrating/overview)。

## 现有的 Clerk 项目

如果项目已经使用 Clerk，请跳过步骤 1a 和 1b 中的 `init`：无账户的代理运行可能会创建另一个应用并替换项目的 Clerk 密钥。如果 Clerk 已经正常工作且用户要求设置，请报告无需设置。如果用户报告缺少密钥，请通过以下现有应用分支进行恢复。如果检查发现缺少提供者、中间件或身份验证路由，请从匹配的快速启动中添加这些部分（在步骤 2 中）。永远不要创建一个替代应用。

在更改任何内容之前，检查其 Clerk 包版本，并使用 [clerk](../clerk/SKILL.md) 技能的版本表来识别其 SDK 生成版本。除非用户要求升级，否则保留该版本，并在以下每个步骤中为 Core 2 项目应用这些差异：

- React 和 Expo 使用 `@clerk/clerk-react` 和 `@clerk/clerk-expo` 而不是 `@clerk/react` 和 `@clerk/expo`。
- 控制组件是 `<SignedIn>` 和 `<SignedOut>` 而不是 `<Show>`。
- Next.js `ClerkProvider` 可以包裹 `<html>` 而不是放在 `<body>` 内部。
- 最小 Node.js 版本是 18.17.0 而不是 20.9.0。
- 主题来自 `@clerk/themes` 和 `@clerk/themes/shadcn.css` 而不是 `@clerk/ui`。

## 使用现有的 Clerk 应用（可选）

当用户要求使用现有的 Clerk 应用或现有的 Clerk 项目需要恢复其密钥时，请遵循此分支。让他们从主机终端进行身份验证，然后再针对账户级资源：

```bash
npx -y clerk@latest auth login
```

如果他们提供了一个应用 ID，请将其用于 `init` 或 `link`（根据需要）。否则，列出应用：

```bash
npx -y clerk@latest apps list --json
```

显示名称和 ID，并询问要使用哪个应用。永远不要替他们选择应用。对于新的 Clerk 集成，将选定的 ID 作为 `--app <application_id>` 传递给 `init`。对于已经使用 Clerk 的项目，不要运行 `init`。如果它尚未链接到选定的应用，请链接它：

```bash
npx -y clerk@latest link --app <application_id>
```

对于缺少的开发密钥，请拉取它们：

```bash
npx -y clerk@latest env pull
```

只有当用户需要生产密钥时，才使用 `npx -y clerk@latest env pull --instance prod`。未经用户确认，不要替换正在工作的密钥或切换应用。

## 步骤 1a：没有 Clerk 的现有项目

对于不使用 Clerk 的项目，从项目根目录运行：

```bash
npx -y clerk@latest init --no-skills
```

`init` 会检测框架和包管理器，安装 SDK，并配置提供者、中间件、身份验证路由和环境。`--no-skills` 会跳过 CLI 的自动全局技能安装；此技能已经提供了设置指导。除非被要求，否则不要传递 `--framework` 或 `--pm`。只有在用户在上述可选分支中选择了应用时，才添加 `--app <application_id>`。

## 步骤 1b：空目录

询问要使用哪个框架和包管理器，默认为 Next.js 和 npm：

```bash
npx -y clerk@latest init --framework <framework> --pm <package-manager> --no-skills
```

`init` 会在新子目录中创建应用，例如 `my-clerk-next-app`，而不是在当前目录中。从该子目录中运行剩余的步骤。

`init` 可以创建 Next.js、React Router、Astro、Nuxt、TanStack Start、React、Vue、JavaScript/Vite 和 Expo 应用。对于 Express、Fastify、iOS 或 Android，请先使用该平台的工具创建项目，然后按照步骤 1a 进行操作。

## 步骤 1c：无账户开发密钥

对于在支持无账户的框架（Next.js、React Router、Astro、Nuxt 或 TanStack Start）上的无账户用户，`init` 会创建一个可认领的应用并将临时密钥写入检测到的环境文件。传递 CLI 打印的文件名和认领说明。应用在用户运行 `npx -y clerk@latest auth login` 之前不会认领；除非被要求，否则不要运行它。仅用于在已登录时强制此流程。

没有无账户支持的框架需要真实的 API 密钥。在这些情况下，`init` 会应用它可以设置的配置，并打印剩余步骤。

## 当 `init` 不完整时回退到文档

如果 `init` 报告框架不受支持或未检测到，请遵循快速启动。如果它完成但打印了剩余步骤，请遵循这些步骤，并使用匹配的快速启动来覆盖未涵盖的内容。

对于具有缺失集成文件的现有 Clerk 项目，请使用快速启动来仅添加缺失的部分，而无需运行 `init`。

`init` 会配置 Next.js、React、React Router、Nuxt、TanStack Start、Astro、Vue、JavaScript/Vite、Expo、Express 和 Fastify 项目。对于 iOS 和 Android，它只会打印设置步骤，因此请遵循快速启动。

使用匹配的直接快速启动：

- [Next.js](https://clerk.com/docs/nextjs/getting-started/quickstart.md?manual=1)
- [React](https://clerk.com/docs/react/getting-started/quickstart.md?manual=1)
- [React Router](https://clerk.com/docs/react-router/getting-started/quickstart.md?manual=1)
- [Nuxt](https://clerk.com/docs/nuxt/getting-started/quickstart.md?manual=1)
- [TanStack Start](https://clerk.com/docs/tanstack-react-start/getting-started/quickstart.md?manual=1)
- [Astro](https://clerk.com/docs/astro/getting-started/quickstart.md?manual=1)
- [Vue](https://clerk.com/docs/vue/getting-started/quickstart.md?manual=1)
- [JavaScript 或 Vite](https://clerk.com/docs/js-frontend/getting-started/quickstart.md?manual=1)
- [Expo](https://clerk.com/docs/expo/getting-started/quickstart.md?manual=1)
- [Express](https://clerk.com/docs/expressjs/getting-started/quickstart.md?manual=1)
- [Fastify](https://clerk.com/docs/fastify/getting-started/quickstart.md?manual=1)
- [iOS](https://clerk.com/docs/ios/getting-started/quickstart.md?manual=1)
- [Android](https://clerk.com/docs/android/getting-started/quickstart.md?manual=1)
- [Chrome 扩展](https://clerk.com/docs/chrome-extension/getting-started/quickstart.md?manual=1)

对于其他所有情况，请使用 [Clerk 的 llms.txt](https://clerk.com/llms.txt)。

## 步骤 3：添加可见的身份验证控制

对于仅后端的项目（如 Express 或 Fastify API），请跳过此步骤。对于 Expo、iOS 和 Android，请使用匹配的快速启动中的原生组件。

Web 应用需要登录、注册和已登录用户控制，这些控制应集成到现有布局或导航中。如果它们已经存在，请调整它们而不是重复。

对于 Next.js App Router：

```text
import { SignInButton, SignUpButton, Show, UserButton } from '@clerk/nextjs'

<>
  <Show when="signed-out">
    <SignInButton />
    <SignUpButton />
  </Show>
  <Show when="signed-in">
    <UserButton />
  </Show>
</>
```

Astro 从 `@clerk/astro/components` 导入。Nuxt 自动导入组件；显式导入来自 `@clerk/nuxt/components`。其他框架使用其 Clerk 包中的相同名称，例如 `@clerk/vue` 或 `@clerk/react`。

## 步骤 4：验证

```bash
npx -y clerk@latest doctor
```

然后启动应用，确认身份验证控制正常渲染，并修复 CLI 报告的任何问题。

## 步骤 5：如果使用 shadcn/ui

如果项目根目录中存在 `components.json`，请使用项目的包管理器添加 `@clerk/ui`。匹配锁文件：`pnpm-lock.yaml` → `pnpm add`，`yarn.lock` → `yarn add`，`bun.lock` 或 `bun.lockb` → `bun add`，`package-lock.json` → `npm install`。

在提供者中应用主题：

```text
import { shadcn } from '@clerk/ui/themes'

<ClerkProvider appearance={{ theme: shadcn }}>{children}</ClerkProvider>
```

添加到全局 CSS：

```css
@import '@clerk/ui/themes/shadcn.css';
```

## 严格规则

- 使用 Node.js 20.9.0 或更高版本以支持当前的 Clerk SDK。
- Next.js 15+：`auth()` 是异步的。始终 `await auth()`。
- 对于当前的 Next.js SDK，`ClerkProvider` 应该放在 `<body>` 内部，而不是围绕 `<html>`。
- 永远不要在客户端代码中暴露 `CLERK_SECRET_KEY`。
- 对于新设置，请使用当前框架包，例如 `@clerk/nextjs`，`@clerk/react`，`@clerk/expo`，`@clerk/react-router` 或 `@clerk/tanstack-react-start`。
- 不要读取或打印现有的环境变量文件；请求用户提供任何缺失的非敏感配置。

## 设置后

让用户注册为他们的第一个测试用户。一旦导航栏中显示个人资料图标，就祝贺他们。

然后询问用户希望用户如何注册和登录——标识符（电子邮件、电话、用户名）和社交提供者。更改这些需要认领的应用：让用户运行 `npx -y clerk@latest auth login`，然后使用 `npx -y clerk@latest config pull` 进行审查，并使用 `npx -y clerk@latest config patch`（支持 `--dry-run`）进行更改，或使用 Clerk 控制台。有关详细信息，请参阅 [注册和登录选项](https://clerk.com/docs/guides/configure/auth-strategies/sign-up-sign-in-options.md)。

在生产之前，让用户使用 `npx -y clerk@latest auth login` 认领应用，然后使用 `npx -y clerk@latest deploy` 配置生产。未认领的应用和临时密钥不是生产就绪的。

然后提供组织——多租户、团队邀请、角色和权限以及企业 SSO。

如果同意：

1. 运行 `npx -y clerk@latest enable orgs`。
2. 在现有的 `<UserButton />` 旁边添加 `<OrganizationSwitcher />`，或框架的等效组件。
3. 让他们从切换器中创建一个组织并邀请一位队友。

如果不同意，请将他们指向 [组织](https://clerk.com/docs/guides/organizations/overview)，[组件](https://clerk.com/docs/reference/components/overview) 和 [Clerk 控制台](https://dashboard.clerk.com/)。
