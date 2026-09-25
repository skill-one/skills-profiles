# 设置和使用 Flags SDK

Flags SDK（`flags` npm 包）是 Next.js 和 SvelteKit 的功能标志工具包。它将每个功能标志转换为可调用的函数，通过适配器与任何标志提供程序协同工作，并使用预计算模式保持页面静态。Vercel Flags 是官方提供程序，让您可以通过 Vercel 仪表板或 `vercel flags` CLI 管理标志。

- 文档：https://flags-sdk.dev
- 仓库：https://github.com/vercel/flags

当用户要求安装、配置或设置功能标志时，请遵循 [设置 SDK](#设置-sdk)（包括当 `.env.local` 缺失时 `vercel env pull`）。当用户要求创建或添加标志时，请遵循 [创建标志](#创建标志)。当用户要求检查、创建或更改远程标志且请求不涉及代码时，请求是仅限 CLI 的；然后请遵循 [仅限 CLI 的标志管理](#cli-only-flag-management)。在应用程序存储库内，将模糊请求视为完整流程。不要将 CLI 步骤作为用户的“下一步” — 自己执行它们。

## 核心概念

### 将标志作为代码

每个标志都声明为一个函数。调用位置没有字符串键：

```ts
import { flag } from 'flags/next';

export const exampleFlag = flag({
  key: 'example-flag',
  decide() { return false; },
});

const value = await exampleFlag();
```

### 服务器端评估

标志在服务器端评估，以避免布局偏移、保持页面静态并维护机密性。结合路由中间件和预计算模式，从 CDN 提供静态变体。

### 适配器模式

适配器替换标志声明上的 `decide` 和 `origin`，将您的标志连接到提供程序。Vercel Flags（`@flags-sdk/vercel`）是官方适配器。第三方适配器适用于 Statsig、LaunchDarkly、PostHog 等。

```ts
import { flag } from 'flags/next';
import { vercelAdapter } from '@flags-sdk/vercel';

export const exampleFlag = flag({
  key: 'example-flag',
  adapter: vercelAdapter,
});
```

> **版本说明**：SDK 以 `flags` 发布（从 `@vercel/flags` 更名；旧名称仍出现在版本历史记录中）。`flags` 4.2.0+ 接受适配器工厂的引用（`adapter: vercelAdapter`）并对每个声明解析一次。旧版本需要调用它（`adapter: vercelAdapter()`）。调用形式在新版本中仍然有效，因此除非您针对 `flags` < 4.2.0，否则请优先使用简写形式。

## 设置 SDK

一次性项目设置。当 Flags SDK 尚未安装时运行此命令，或者当 Toolbar / Flags Explorer / `.env.local` 缺失时运行。跳过任何已完成的步骤。

### 开始之前

检查项目状态以调整命令并决定您可以跳过哪些步骤：

- 哪个锁文件存在（`pnpm-lock.yaml`、`package-lock.json`、`yarn.lock`、`bun.lockb`）？ → 相应地调整所有包管理器命令（`pnpm add`、`npm install`、`yarn add`、`bun add`）。
- `package.json` 中是否有 `flags`？ → 跳过安装（步骤 1）
- 项目是否已链接？ → 跳过步骤 2 中的 `vercel link`
- `.env.local` 是否包含 `VERCEL_OIDC_TOKEN=`（或 `FLAGS=` SDK 密钥）？ → 环境变量已拉取，跳过步骤 3
- `package.json` 中是否有 `@vercel/toolbar`？ → 跳过 Toolbar 设置（步骤 4）
- 是否存在 `flags.ts`（或 `lib/flags.ts`、`src/flags.ts`）？ → 跳过创建它（步骤 5）
- 是否存在 `app/.well-known/vercel/flags/route.ts`？ → Flags Explorer 已设置，跳过步骤 6

### 步骤

1. **安装包**（如果不在 `package.json` 中）：
   ```bash
   pnpm i flags @flags-sdk/vercel
   ```

2. **将项目链接到 Vercel**（`vercel env pull` 和本地 OIDC 令牌刷新所需）：
   > **前提条件**：必须安装并认证 Vercel CLI。如果未安装，请运行 `pnpm i -g vercel`。对于认证或链接问题，如果 `vercel-cli` 技能已可用，请遵循 `vercel-cli` 技能。如果不可用，建议用户使用 `npx skills add vercel/vercel@vercel-cli` 安装它（不要自动安装它），并暂时依赖 `vercel <command> --help`。

   按照描述在 [项目目标](#项目目标) 中验证链接。如果项目未链接，请运行 `vercel link`。

3. **拉取环境变量**：如果 `.env.local` 缺少 `VERCEL_OIDC_TOKEN=`，请遵循 [拉取环境变量](#拉取环境变量)。

4. **设置 Vercel Toolbar**（如果尚未存在）：
   - 运行 `pnpm i @vercel/toolbar`
   - 用 Toolbar 插件包装 `next.config.ts`
   - 在根布局中渲染 `<VercelToolbar />`
   参考完整代码 [references/nextjs.md — Toolbar Setup](references/nextjs.md#toolbar-setup)。

5. **确保存在 `flags.ts`**：如果缺失，请创建 `flags.ts`（或 `lib/flags.ts` / `src/flags.ts` 以匹配项目），并使用 `export {}` 以便 TypeScript 将其视为模块。Flags Explorer 导入此文件 — 在发现路由之前创建它。

6. **设置 Flags Explorer**（如果尚未存在）：创建 `app/.well-known/vercel/flags/route.ts` — 参考完整代码 [Flags Explorer 设置](#flags-explorer-setup)。仅在 `flags.ts` 存在后才执行此操作。将导入指向实际的标志文件路径（代码片段假设根 `flags.ts`）。

## 拉取环境变量

`vercel env pull` 将开发凭证写入 `.env.local`：Vercel OIDC 令牌（`vercelAdapter` 在本地使用它，部署自动接收它，[入门指南](https://vercel.com/docs/flags/vercel-flags/quickstart#pull-local-openid-connect-credentials)）以及开发 `FLAGS_SECRET` 用于 Flags Explorer 和覆盖。当以下情况发生时运行它：

- `.env.local` 缺少 `VERCEL_OIDC_TOKEN=`（或 `FLAGS=` SDK 密钥）
- 您创建了项目的第一个标志；激活 Vercel Flags 为每个环境创建一个 `FLAGS_SECRET`
- 本地评估因认证错误而失败；SDK 通过链接的项目刷新过期令牌，重新拉取是备用方案

SDK 密钥（`FLAGS`）仅适用于 Vercel 外的应用程序、自定义环境或另一个项目的标志（[SDK 密钥](https://vercel.com/docs/flags/vercel-flags/dashboard/sdk-keys)）。如果拉取后 `FLAGS_SECRET` 仍然缺失，请按照 [FLAGS_SECRET](#flags_secret) 为每个环境生成它。

## 创建标志

当用户要求您创建或添加 Vercel 上尚不存在的功能标志时，请按顺序遵循以下步骤。对于 [仅限 CLI 的请求](#cli-only-flag-management)，仅运行步骤 2。如果标志已在仪表板中创建（提示中说明，或 `vercel flags create` 报告键已存在），请遵循 [添加 Vercel 上已存在的标志](#add-a-flag-that-already-exists-on-vercel)。

### 开始之前

- 如果缺少包、Vercel 链接、`.env.local`、Toolbar、`flags.ts` 或 Flags Explorer，请先完成 [设置 SDK](#设置-sdk)。跳过已完成的步骤。对于 [仅限 CLI 的请求](#cli-only-flag-management)，请完全跳过此步骤。
- `.env.local` 是否包含 `VERCEL_OIDC_TOKEN=`？ → 环境变量已拉取；如果本地评估因认证错误而失败，请参考 [拉取环境变量](#拉取环境变量)。
- 是否存在 `flags.ts`（或 `lib/flags.ts`、`src/flags.ts`）？ → 添加到其中，而不是从头开始创建。

### 步骤

1. **确保 SDK 已设置**：如果需要，请遵循 [设置 SDK](#设置-sdk)，然后继续。

2. **使用 Vercel 注册标志**：运行 `vercel flags create <flag-key> --kind boolean --description "<description>"`。

   按照描述在 [项目目标](#项目目标) 中目标项目。

3. **拉取环境变量**：如果这是项目的第一个标志，请再次遵循 [拉取环境变量](#拉取环境变量)；激活创建了 `FLAGS_SECRET`。

4. **在代码中声明标志**：使用 `vercelAdapter` 将其添加到 `flags.ts`（如果不存在，请创建该文件）：
   ```ts
   import { flag } from 'flags/next';
   import { vercelAdapter } from '@flags-sdk/vercel';

   export const myFlag = flag({
     key: 'my-flag',
     adapter: vercelAdapter,
   });
   ```

5. **使用标志**：在页面或组件中调用它，并根据结果有条件地渲染：
   ```tsx
   import { myFlag } from '../flags';

   export default async function Page() {
     const enabled = await myFlag();
     return <div>{enabled ? '功能开启' : '功能关闭'}</div>;
   }
   ```

## 添加 Vercel 上已存在的标志

当标志已在仪表板中创建或由其他人创建时，请使用此流程，例如当提示说明标志“已创建”或要求您运行 `vercel flags inspect` 时。不要为现有键运行 `vercel flags create`。对于 [仅限 CLI 的请求](#cli-only-flag-management)，仅运行步骤 2。

1. **确保 SDK 已设置**：如果需要，请遵循 [设置 SDK](#设置-sdk)。
2. **读取定义**：运行 `vercel flags inspect <flag-key>`。注意类型、变体（值和标签）、描述以及每个环境提供的内容。
3. **拉取环境变量**：如果 `.env.local` 缺少 `VERCEL_OIDC_TOKEN=`，请遵循 [拉取环境变量](#拉取环境变量)。
4. **声明标志**：使用 `vercelAdapter` 将其添加到 `flags.ts`，映射 `inspect` 输出：
   - `key`：标志键的准确值
   - 类型 → 类型参数：`boolean` → `flag<boolean>`，`string` → `flag<string>`，`number` → `flag<number>`，`json` → `flag<YourType>`
   - `description`：从 `inspect` 复制
   - `defaultValue`：标志存档或评估失败时提供的值（通常是今天生产的值）
   - `options`：可选；在您使用预计算或希望在 Flags Explorer 中列出变体时镜像变体
   - `identify`：当标志具有目标时添加或重用一个，使用仪表板中配置的实体属性（见 [带评估上下文的标志](#flag-with-evaluation-context)）
   ```ts
   export const welcomeMessage = flag<string>({
     key: 'welcome-message',
     description: '在着陆页上显示的文本',
     defaultValue: 'control',
     adapter: vercelAdapter,
   });
   ```
5. **使用标志**，如 [创建标志](#创建标志) 步骤 5 中所述。

## 仅限 CLI 的标志管理

使用 `vercel flags` 管理远程标志需要经过认证的 CLI，但不需要 SDK 包、Toolbar、Flags Explorer 或 `.env.local`。对于仅限 CLI 的请求，请跳过应用程序设置和代码更改。按照 [项目目标](#项目目标) 中描述的目标项目，然后遵循 [references/providers.md — `vercel flags` CLI](references/providers.md#vercel-flags-cli) 了解命令语义和安全注意事项。

CLI 认证与应用程序的 OIDC 或 SDK 密钥是分开的。仅在应用程序需要本地 SDK 评估时才拉取本地凭证，而不是为 CLI 标志命令做准备。

### 项目目标

使用 `--project <name-or-id>` 和 `--scope <team>` 选择目标，而无需本地链接。如果 CLI 拒绝 `--project`，请先升级它（`pnpm i -g vercel`）。如果没有这些选项，命令将使用链接的项目：运行 `vercel project inspect --non-interactive` 并检查报告的所有者和项目名称；仅 `.vercel/` 目录并不能证明链接。如果它报告 `link_required`，则项目未链接。如果用户命名了项目或团队，而输出不同，请停止并询问，而不是重新链接。对于未链接目录中的仅限 CLI 请求，请优先使用 `--project` / `--scope` 而不是 `vercel link`；如果目标项目未知，请询问。

## Vercel Flags

Vercel Flags 是 Vercel 的功能标志平台。您可以通过 Vercel 仪表板或 `vercel flags` CLI 创建和管理标志，然后使用 `@flags-sdk/vercel` 适配器将它们连接到您的代码。`vercelAdapter()` 使用项目的 Vercel OIDC 令牌进行认证，并评估当前环境的配置；SDK 密钥（`FLAGS`）仅用于手动认证（[SDK 密钥](https://vercel.com/docs/flags/vercel-flags/dashboard/sdk-keys)）。激活 Vercel Flags 为每个环境创建一个 `FLAGS_SECRET` 用于 Flags Explorer。

要安装 SDK，请遵循 [设置 SDK](#设置-sdk)。要端到端创建标志，请遵循 [创建标志](#创建标志)。对于 Vercel 上已存在的标志，请遵循 [添加 Vercel 上已存在的标志](#add-a-flag-that-already-exists-on-vercel)。

对于完整的 Vercel 提供程序参考 — 用户目标、CLI 如何映射到 SDK（密钥、类型、目标属性、SDK 密钥、覆盖、`prepare`）、生命周期和安全、自定义适配器配置以及 Flags Explorer 设置，请参阅 [references/providers.md](references/providers.md#vercel)。

对于当前的 `vercel flags` 子命令和选项（目标、分割、发布、规则、分段、评估、版本等），请运行 `vercel flags --help` 或 `vercel flags <cmd> --help`。对于 CLI 全局契约（链接、非交互模式、输出解析），请使用 `vercel-cli` 技能。

## 声明标志

使用 Vercel Flags 时，使用 `vercelAdapter` 声明标志，如 [创建标志](#创建标志) 中所示。对于其他提供程序，请参阅 [references/providers.md](references/providers.md)。以下是通用的 `flag()` 模式。

### 基本标志

```ts
import { flag } from 'flags/next'; // 或 'flags/sveltekit'

export const showBanner = flag<boolean>({
  key: 'show-banner',
  description: '显示促销横幅',
  defaultValue: false,
  options: [
    { value: false, label: '隐藏' },
    { value: true, label: '显示' },
  ],
  decide() { return false; },
});
```

### 带评估上下文的标志

使用 `identify` 建立请求是谁的。返回的实体将传递给 `decide`：

```ts
import { dedupe, flag } from 'flags/next';
import type { ReadonlyRequestCookies } from 'flags';

interface Entities {
  user?: { id: string };
}

const identify = dedupe(
  ({ cookies }: { cookies: ReadonlyRequestCookies }): Entities => {
    const userId = cookies.get('uid')?.value;
    return { user: userId ? { id: userId } : undefined };
  },
);

export const dashboardFlag = flag<boolean, Entities>({
  key: 'new-dashboard',
  identify,
  decide({ entities }) {
    if (!entities?.user) return false;
    return ['user1', 'user2'].includes(entities.user.id);
  },
});
```

使用 `vercelAdapter`，返回对象中的实体和属性名称（此处为 `user.id`）是仪表板规则和 `vercel flags split|rollout|rules --by` 目标的。它们必须与仪表板中配置的实体匹配。见 [references/providers.md — 用户目标](references/providers.md#user-targeting)。

### 使用其他适配器的标志

适配器将标志连接到第三方提供程序。每个适配器替换 `decide` 和 `origin`：

```ts
import { flag } from 'flags/next';
import { statsigAdapter } from '@flags-sdk/statsig';

export const myGate = flag({
  key: 'my_gate',
  adapter: statsigAdapter.featureGate((gate) => gate.value),
  identify,
});
```

请参阅 [references/providers.md](references/providers.md) 了解所有支持的适配器。

### 关键参数

| 参数      | 类型                               | 描述                                          |
| --------- | ---------------------------------- | ------------------------------------------- |
| `key`     | `string`                           | 唯一标志标识符                               |
| `decide`  | `function`                         | 解析标志值                                  |
| `defaultValue` | `any`                              | 如果 `decide` 返回 `undefined` 或抛出，则使用备用值 |
| `description` | `string`                           | 在 Flags Explorer 中显示                      |
| `origin`  | `string`                           | 提供程序仪表板中管理标志的 URL                 |
| `options` | `{ label?: string, value: any }[]` | 可能的值，用于预计算 + Flags Explorer         |
| `adapter` | `Adapter`                          | 实现 `decide` 和 `origin` 的提供程序适配器      |
| `identify` | `function`                         | 返回 `decide` 的评估上下文（实体）             |

## dedupe

将共享函数（尤其是 `identify`）包装在 `dedupe` 中，以便每个请求只运行一次：

```ts
import { dedupe } from 'flags/next';

const identify = dedupe(({ cookies }) => {
  return { user: { id: cookies.get('uid')?.value } };
});
```

注意：`dedupe` 在 Pages Router 中不可用。

## 批量评估

要一次评估 **多个** 标志，请调用 `evaluate()`（来自 `flags/next`），而不是依次等待标志或使用 `Promise.all()`。要评估 **单个** 标志，只需调用它：`await myFlag()`。

```ts
import { evaluate } from 'flags/next';
import { flagA, flagB } from '../flags';

// 避免：每个 `await` 阻塞下一个，因此标志按顺序解析
const a = await flagA();
const b = await flagB();

// 避免：并行，但每个标志都是独立评估的
const [a, b] = await Promise.all([flagA(), flagB()]);

// 优先：跨批量共享工作
const [a, b] = await evaluate([flagA, flagB]);
```

`evaluate()` 比这两种方法更快。依次等待标志会使总延迟成为每个标志评估的延迟总和，而不是最慢的单个标志，而 `Promise.all()` 并行运行它们，但每个标志都是独立评估的。`evaluate()` 一次预读取整个批量的标头、cookie 和覆盖，并允许适配器一次性解析一组，这减少了运行时管理的并行承诺数量，并减少了异步工作被其他微任务中断的空间。

它接受数组（位置结果）或对象（键值结果）：

```ts
const [a, b] = await evaluate([flagA, flagB]);
const { a, b } = await evaluate({ a: flagA, b: flagB });
```

在 App Router 外（Pages Router `getServerSideProps`/API 路由或路由中间件），将请求作为第二个参数传递：`await evaluate([flagA, flagB], request)`。

`evaluate()` 始终在请求时评估标志。它不用于读取 [预计算](#预计算模式)（静态）值 — 对于这些，请使用 `getPrecomputed`（或调用标志，`await myFlag(code, flagGroup)`）。

适配器可以选择通过实现可选的 `bulkDecide` 钩子来启用批处理。Vercel 适配器（`@flags-sdk/vercel`）实现了它 — 在解析数百个标志时，大约减少了 10 倍的评估时间。请参阅 [references/providers.md — 自定义适配器](references/providers.md#custom-adapters) 了解如何实现 `bulkDecide`，以及 [references/api.md — `evaluate`](references/api.md#evaluate) 了解完整签名。

## Flags Explorer 设置

### Next.js (App Router)

```ts
// app/.well-known/vercel/flags/route.ts
import { createFlagsDiscoveryEndpoint } from 'flags/next';
import { getProviderData } from '@flags-sdk/vercel';
import * as flags from '../../../../flags'; // 如果标志位于 lib/ 或 src/ 下，请调整

export const GET = createFlagsDiscoveryEndpoint(async () => {
  return getProviderData(flags);
});
```

### 使用外部提供程序数据

当使用第三方提供程序与 Vercel Flags 一起使用时，使用 `mergeProviderData` 组合它们的数据。每个提供程序适配器都导出它自己的 `getProviderData` — 请参阅 [references/providers.md](references/providers.md) 中提供程序特定的示例。

### SvelteKit

```ts
// src/hooks.server.ts
import { createHandle } from 'flags/sveltekit';
import { FLAGS_SECRET } from '$env/static/private';
import * as flags from '$lib/flags';

export const handle = createHandle({ secret: FLAGS_SECRET, flags });
```

## FLAGS_SECRET

对于预计算和 Flags Explorer 是必需的。Vercel Flags 激活为每个环境创建一个值。保留现有值；在普通 SDK 设置期间不要旋转它们。本地值缺失并不意味着远程值缺失：首先检查目标环境，然后遵循 [拉取环境变量](#拉取环境变量) 为开发环境。

仅生成缺少的本地密钥的环境的密钥。使用 32 个加密随机字节，base64 编码，每个环境具有不同的值。将预览和生产的值标记为敏感。将生成的值直接发送到存储，例如 `vercel env add` 的 `stdin`；不要将它们打印到终端输出、日志或聊天中，或嵌入到命令参数中。

## 预计算模式

使用预计算来在功能标志使用的同时保持页面静态。中间件评估标志并通过重写将结果编码到 URL 中。页面读取预计算值而不是重新评估。

高级流程：
1. 声明标志并将它们分组到一个数组中
2. 在中间件中调用 `precompute(flagGroup)`，获取一个 `code` 字符串
3. 将请求重写为 `/${code}/original-path`
4. 页面从 `code` 中读取标志值：`await myFlag(code, flagGroup)`

有关完整实现细节，请参阅框架特定参考：
- **Next.js**: 参考 [references/nextjs.md](references/nextjs.md) — 涵盖代理中间件、预计算设置、ISR、generatePermutations、多个组
- **SvelteKit**: 参考 [references/sveltekit.md](references/sveltekit.md) — 涵盖重定向钩子、中间件、预计算设置、ISR、预渲染

## 自定义适配器

创建一个返回包含 `origin` 和 `decide` 的对象的自定义适配器工厂。有关完整模式（包括默认适配器和单例客户端示例），请参阅 [references/providers.md](references/providers.md#custom-adapters)。

## 加密函数

用于在浏览器中保持标志数据机密性的（用于 Flags Explorer）：

| 函数                   | 目的                             |
| ---------------------- | ----------------------------------- |
| `encryptFlagValues`        | 加密解析的标志值                |
| `decryptFlagValues`        | 解密标志值                     |
| `encryptFlagDefinitions`   | 加密标志定义/元数据             |
| `decryptFlagDefinitions`   | 解密标志定义                    |
| `encryptOverrides`         | 加密工具栏覆盖                 |
| `decryptOverrides`         | 解密工具栏覆盖                 |

所有函数默认使用 `FLAGS_SECRET`。示例：

```tsx
import { encryptFlagValues } from 'flags';
import { FlagValues } from 'flags/react';

async function ConfidentialFlags({ values }) {
  const encrypted = await encryptFlagValues(values);
  return <FlagValues values={encrypted} />;
}
```

## React 组件

```tsx
import { FlagValues, FlagDefinitions } from 'flags/react';

// 渲染带有 Flags Explorer 标志值的脚本标签
<FlagValues values={{ myFlag: true }} />

// 渲染带有 Flags Explorer 标志定义的脚本标签
<FlagDefinitions definitions={{ myFlag: { options: [...], description: '...' } }} />
```

## 参考

详细的框架和提供程序指南分别保存在单独的文件中以保持上下文简洁：

- **[references/nextjs.md](references/nextjs.md)**: Next.js 快速入门、Toolbar、App Router、Pages Router、中间件/代理、预计算、dedupe、仪表板页面、营销页面、suspense 回退
- **[references/sveltekit.md](references/sveltekit.md)**: SvelteKit 快速入门、Toolbar、钩子设置、使用重定向 + 中间件进行预计算、仪表板页面、营销页面
- **[references/providers.md](references/providers.md)**: 所有提供程序适配器 — Vercel、全局配置、Statsig、LaunchDarkly、PostHog、GrowthBook、Flagsmith、Reflag、Split、Optimizely、OpenFeature，以及自定义适配器
- **[references/api.md](references/api.md)**: `flags`、`flags/react`、`flags/next` 和 `flags/sveltekit` 的完整 API 参考
