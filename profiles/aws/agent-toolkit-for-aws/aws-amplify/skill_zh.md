# AWS Amplify Gen2

使用 AWS Amplify Gen2 的 TypeScript 代码优先方法构建和部署全栈应用程序。这项技能涵盖后端资源创建、跨 8 个框架的前端集成以及部署工作流。

## 前置条件

- Node.js ^18.19.0 || ^20.6.0 || >=22 和 npm
- 配置了 AWS 凭证 (`aws sts get-caller-identity` 成功)
- 对于沙盒：`npx ampx --version` 返回有效版本
- 对于移动端：特定平台的工具（Xcode、Android Studio、Flutter SDK）

## 默认值与假设

当用户未指定框架时：

- **Web：** 默认使用 **React**（Vite）并解释选择原因。
- **移动端：** 询问平台（Flutter、Swift、Android 或 React Native）—— 没有通用的移动端默认值，猜测会导致浪费精力。
- **未指定：** 如果用户说“构建一个应用”而没有明确说明 Web 还是移动端，则在继续之前询问——框架选择会影响后续所有步骤。
- **仅后端：** 如果仅请求后端更改且未提及前端框架，则完全跳过前端集成步骤。

当用户未指定工具或策略时：

- **包管理器：** 默认使用 **npm**，除非用户指定 yarn 或 pnpm。
- **语言：** 默认使用 **TypeScript**。Gen2 后端仅支持 TypeScript；前端应遵循项目现有的语言。
- **Next.js：** 默认使用 **App Router**，除非用户指定 Pages Router。
- **React Native：** 询问用户是否使用 **Expo** 或 **裸 React Native CLI**。
- **认证：** 您 **必须** 询问用户想要的登录方法（电子邮件/密码、社交登录、SAML、无密码等）。不要假设默认值。
- **数据授权：** 默认为 **`publicApiKey`** (`allow.publicApiKey()`)——这是起步模板的默认值。当添加认证时，切换到 **基于所有者** (`allow.owner()`) 并使用 `defaultAuthorizationMode: 'userPool'`。

## 快速入门——路由到正确的参考

### 第 1 步：确定任务类型

| 任务                                     | 前往                                                                    |
| ---------------------------------------- | ------------------------------------------------------------------------ |
| **创建新项目**                 | → [scaffolding.md](references/scaffolding.md)，然后第 2 步和/或第 3 步 |
| **添加或修改后端功能**      | → 第 2 步（后端功能）                                              |
| **将前端连接到现有后端** | → 第 3 步（前端集成）                                          |
| **部署应用程序**               | → [deployment.md](references/deployment.md)                              |

### 第 2 步：后端功能

阅读您需要的每个后端功能的相应参考：

| 功能 | 参考 | 使用时机 |
|---------|-----------|-------------|
| 认证 | [auth-backend.md](references/auth-backend.md) | 电子邮件/密码、社交登录、MFA、SAML/OIDC |
| 数据模型 | [data-backend.md](references/data-backend.md) | GraphQL 模式、DynamoDB、关系、认证规则 |
| 文件存储 | [storage-backend.md](references/storage-backend.md) | S3 上传/下载、访问规则 |
| 函数与 API | [functions-and-api.md](references/functions-and-api.md) | Lambda、自定义解析器、REST/HTTP API、从客户端调用 |
| AI 功能 | [ai.md](references/ai.md) | 对话、生成、通过 Bedrock 的 AI 工具 *(后端配置 + React/Next.js 前端)* |
| Geo、PubSub、CDK | [geo-pubsub-cdk.md](references/geo-pubsub-cdk.md) | 仅后端：自定义 CDK 堆栈、覆盖、自定义输出。后端 + 前端：Geo、PubSub、人脸活体检测 |

每个后端功能文件都是自包含的。仅加载您需要的部分。

> **路由说明：** 这些文件适用于 **添加** 和 **修改** 功能。无论用户说“添加认证”还是“修改认证配置”，都路由到同一个文件——每个参考都涵盖完整的定义表面。

### 第 3 步：前端集成

配置后端资源后，连接前端。根据平台和功能选择：

**Web**（React、Next.js、Vue、Angular、React Native）：

| 功能                   | 参考                                   |
| ------------------------- | ------------------------------------------- |
| 认证 UI & 流程           | [auth-web.md](references/auth-web.md)       |
| 数据 CRUD & 订阅         | [data-web.md](references/data-web.md)       |
| 存储上传/下载   | [storage-web.md](references/storage-web.md) |

**移动端**（Flutter、Swift、Android）：

| 功能                   | 参考                                         |
| ------------------------- | ------------------------------------------------- |
| 认证 UI & 流程           | [auth-mobile.md](references/auth-mobile.md)       |
| 数据 CRUD & 订阅         | [data-mobile.md](references/data-mobile.md)       |
| 存储上传/下载   | [storage-mobile.md](references/storage-mobile.md) |

> **注意：** AI 和函数前端模式分别包含在
> [ai.md](references/ai.md) 和
> [functions-and-api.md](references/functions-and-api.md) 中——它们**不是**拆分为单独的 Web/移动端文件。

## 核心概念

### Amplify Gen2 架构

- **代码优先：** 所有后端资源定义在 `amplify/` 下的 TypeScript 中
- **主配置：** `amplify/backend.ts` 通过 `defineBackend()` 导入并组合所有资源
- **资源文件：** `amplify/auth/resource.ts`、`amplify/data/resource.ts`、`amplify/storage/resource.ts`、`amplify/functions/<name>/resource.ts`
- **生成输出：** `amplify_outputs.json`——由前端 `Amplify.configure()` 消费。**忽略 Git**——由 `npx ampx sandbox`（本地开发）或 `npx ampx pipeline-deploy`（CI/CD）生成，从不提交。

### 目录结构

`amplify/` 和 `src/` 必须作为项目根目录下的同级目录——将它们放在不同的目录级别会破坏沙盒检测。（例外：在单体仓库中，`amplify/` 可能在 `packages/` 子目录中——关键是 `amplify_outputs.json` 必须可以从前端入口点访问。）

```text
project-root/
├── amplify/
│   ├── backend.ts            # defineBackend({ auth, data, ... })
│   ├── auth/resource.ts      # defineAuth({ ... })
│   ├── data/resource.ts      # defineData({ schema })
│   ├── storage/resource.ts   # defineStorage({ ... })
│   └── functions/
│       └── my-func/
│           ├── resource.ts   # defineFunction({ ... })
│           └── handler.ts    # export const handler = ...
├── src/                      # 前端代码
├── amplify_outputs.json      # 生成，忽略 Git——从不编辑或提交
└── package.json
```

### 关键 API

| 包 | 目的 |
|---------|---------|
| `@aws-amplify/backend` | `defineAuth`、`defineData`、`defineStorage`、`defineFunction`、`defineBackend` |
| `aws-amplify` | 前端：`Amplify.configure()`、`generateClient()`、认证/数据/存储 API |
| `@aws-amplify/ui-react` | 预构建 UI：`<Authenticator>`、`<StorageBrowser>` |
| `@aws-amplify/ui-react-ai` | AI UI：`<AIConversation>`、`useAIConversation` |

## 框架设置

这些模式适用于**每个** Web 任务——不仅限于新项目。在实现任何功能之前，请验证每一个。

### Gen2 检测

在修改任何代码之前，检查项目是否已经是 Gen2：

1. 存在 `amplify/` 目录并包含 `backend.ts`
2. `package.json` 中存在 `@aws-amplify/backend` 在 `devDependencies` 中

如果两者都为真，则项目已经是 Gen2——跳到功能实现。如果存在 `amplify/.config/`，则这是一个 Gen1 项目——不要继续（需要单独的迁移技能）。

### 前端配置

导入生成的输出并在您的框架的**正确入口点**配置 Amplify。将此内容放在错误的位置会导致静默失败——Amplify API 调用返回未定义或空响应且无错误。

**警告：** `amplify_outputs.json` 必须在应用程序可以编译之前存在——没有它，构建会因为模块未找到错误而失败。首先运行 `npx ampx sandbox`（或 `npx ampx sandbox --once`）来生成它。有关正确顺序，请参阅 [scaffolding.md](references/scaffolding.md)。

**React (Vite)** — `src/main.tsx`:

```typescript
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';
Amplify.configure(outputs);
```

**Next.js (App Router)** — `app/layout.tsx`:

> **重要：** `layout.tsx` 是 App Router 中的服务器组件。使用下面的客户端组件模式 `ConfigureAmplifyClientSide`。

`{ ssr: true }` 是 **Next.js 仅**选项（Vue、Angular 或 React SPA 不需要）。App Router 和 Pages Router 都使用它，但应用方式不同：

> - **App Router** — 在 `ConfigureAmplifyClientSide` 客户端组件中全局设置
> - **Pages Router** — 在需要服务器端访问的每个文件中设置

#### Next.js App Router：客户端配置

Next.js App Router 需要一个专用的客户端组件来为浏览器端操作配置 Amplify：

```typescript
// components/ConfigureAmplifyClientSide.tsx
"use client";
import { Amplify } from "aws-amplify";
import outputs from "@/amplify_outputs.json";

Amplify.configure(outputs, { ssr: true });

export default function ConfigureAmplifyClientSide() {
  return null;
}
```

在根布局中导入：

```typescript
// app/layout.tsx
import ConfigureAmplifyClientSide from "@/components/ConfigureAmplifyClientSide";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>
        <ConfigureAmplifyClientSide />
        {children}
      </body>
    </html>
  );
}
```

> **原因：** 在 App Router 中，`layout.tsx` 是服务器组件。客户端组件需要 `Amplify.configure()` 才能在浏览器中运行。没有它，您会收到“Auth UserPool not configured”错误。

**Vue** — `src/main.js`:

```javascript
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';
Amplify.configure(outputs);
```

**Angular** — `src/main.ts`:

```typescript
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';
Amplify.configure(outputs);
```

#### Next.js Pages Router

Pages Router 不需要在 `_app.tsx` 中使用 `{ ssr: true }`。相反，在需要服务器端访问的每个文件中配置：

```typescript
// pages/api/protected.ts 或 getServerSideProps
import { Amplify } from 'aws-amplify';
import outputs from '@/amplify_outputs.json';
Amplify.configure(outputs, { ssr: true });
```

> **关键区别：** App Router 使用全局客户端组件。Pages Router 按文件配置。

`<Authenticator.Provider>` 在 `layout.tsx` 中是必需的，用于认证上下文。

### React Native

React Native 使用与 Web 框架相同的 `aws-amplify` JS 包（它是 amplify-js 的一部分，而不是原生移动端 SDK）。所有 Web API 都适用于 RN，并添加以下内容。

#### 必要包

```bash
npm install aws-amplify @aws-amplify/react-native \
  @react-native-async-storage/async-storage \
  react-native-get-random-values
```

`@react-native-async-storage/async-storage` 是**必需的**——Amplify SDK 使用它进行令牌持久化，没有它将在运行时失败。

#### 配置入口点

不需要插件注册——仅配置。

**React Native (Expo)** — `App.tsx`:

```typescript
import 'react-native-get-random-values';  // 必须是第一个
import { Amplify } from 'aws-amplify';
import outputs from './amplify_outputs.json';
Amplify.configure(outputs);
```

**React Native (裸 CLI)** — `index.js`（在 `AppRegistry.registerComponent` 之前）:

```typescript
import 'react-native-get-random-values';  // 必须是第一个
import { Amplify } from 'aws-amplify';
import outputs from './amplify_outputs.json';
Amplify.configure(outputs);
```

#### React Native 陷阱

- **导入顺序：** `react-native-get-random-values` 必须是入口文件中的**第一个**导入，在 `aws-amplify` 之前。颠倒顺序会导致运行时加密失败。
- **缺少 AsyncStorage：** 没有
  `@react-native-async-storage/async-storage`，认证令牌不会被持久化，用户必须在每次应用重启时重新认证。

### SvelteKit

在客户端钩子文件中配置 Amplify：

```typescript
// src/hooks.client.ts
import { Amplify } from 'aws-amplify';
import outputs from '../amplify_outputs.json';

Amplify.configure(outputs);
```

> **注意：** 没有针对 Svelte 的 `@aws-amplify/ui-*` 组件。直接使用核心 API。

### 不受支持的框架（Astro、Solid 等）

对于没有官方 Amplify 支持的框架：

1. 使用 `npm create amplify@latest -y` 来搭建后端（适用于任何项目）
2. 在**客户端组件**内部配置 Amplify（不要在构建时配置）

#### Astro

Amplify 在 Astro 中**仅客户端**。创建一个 React 组件（没有 Astro 语法）：

```typescript
// src/components/AuthenticatedApp.tsx
import { Amplify } from 'aws-amplify';
import { Authenticator } from '@aws-amplify/ui-react';
import outputs from '../amplify_outputs.json';

Amplify.configure(outputs);

export default function AuthenticatedApp() {
  return (
    <Authenticator>
      {({ signOut, user }) => <main>Hello {user?.username}</main>}
    </Authenticator>
  );
}
```

在带有 `client:only="react"` 的 Astro 页面中使用：

```astro
---
// src/pages/index.astro — 这里没有 Amplify 导入
---
<html>
  <body>
    <AuthenticatedApp client:only="react" />
  </body>
</html>
```

> **必须使用 `client:only="react"`**（**不是** `client:load`）以避免 SSR 渲染错误。

## 链接

> 所有文档链接默认使用 `react` 作为平台缩写。将任何 URL 中的 `/react/` 替换为您目标框架：

| 框架 | 缩写 |
|-----------|------|
| React | `react` |
| Next.js | `nextjs` |
| Vue | `vue` |
| Angular | `angular` |
| React Native | `react-native` |
| Flutter | `flutter` |
| Swift | `swift` |
| Android | `android` |

- [Amplify Docs for LLMs](https://docs.amplify.aws/ai/llms.txt)
- [Amplify Docs](https://docs.amplify.aws/)
- [How Amplify Works](https://docs.amplify.aws/react/how-amplify-works/)
- [CLI Commands](https://docs.amplify.aws/react/reference/cli-commands/)
- [React Quickstart](https://docs.amplify.aws/react/start/quickstart/)
- [Next.js Quickstart](https://docs.amplify.aws/nextjs/start/quickstart/)
- [Angular Quickstart](https://docs.amplify.aws/angular/start/quickstart/)
- [Vue Quickstart](https://docs.amplify.aws/vue/start/quickstart/)
- [React Native Quickstart](https://docs.amplify.aws/react-native/start/quickstart/)
