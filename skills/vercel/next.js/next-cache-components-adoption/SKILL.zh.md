---
name: next-cache-components-adoption
description: 在 Next.js 应用中启用缓存组件，并解决其呈现的阻塞路由。当用户希望启用、采用或迁移到缓存组件时使用，切换 `cacheComponents` 标志，处理大量阻塞预渲染/即时验证错误，运行 `cache-components-instant-false` 代码转换工具，或在通过 `export const instant = false` 排除路由与直接修复路由之间进行选择。
---

# next-cache-components-adoption

在应用上启用缓存组件，并将其引导至通过构建。这项技能按顺序执行工作；针对每个错误的配方存在于开发覆盖层的修复卡片和构建的终端输出中。[迁移至缓存组件的指南](https://nextjs.org/docs/app/guides/migrating-to-cache-components)是应用此技能所涉及的概念和每个API配方的权威参考——每当技能步骤引用模式（“使用缓存”、“cacheLife”、“<Suspense>”放置等）并希望获得完整解释时，请查阅该指南。

## 要求

- **App Router项目。** 缓存组件是App Router的功能；`cacheComponents: true` 对 `pages/` 路径无效。如果项目具有 `pages/` 或 `src/pages/` 树但没有 `app/` 或 `src/app/` 树，请停止并告知用户——页面到App的迁移是一个独立的项目，不是此技能的一部分。混合应用（同时具有 `pages/` 和 `app/`）是允许的：该标志影响 `app/` 路径；`pages/` 路径不受影响，无需选择退出。

- **一个已解析的应用目录。** 首先定位 `next.config.{js,ts,mjs,cjs}`：这是项目根目录，从子目录调用的代理否则会针对错误的 `cwd` 测试 `app/` 并找到 nothing。在它下面查找 `app/` 和 `src/app/`，并将此技能中的每个命令和glob视为相对于存在的目录。如果两者都存在，Next.js 构建 `app/` 并永远不会查看 `src/app/`，因此其路由被阴影且未构建——告知用户这一点，并询问要迁移哪个树而不是选择一个。

- **一个可运行的应用。** 整个循环针对 `next dev` 和浏览器进行验证，因此应用必须启动。如果它在导入时读取数据库或必需的环境（例如一个在缺少 `DATABASE_URL` 时抛出错误的 `env.ts`），请在步骤1之前确认它确实启动——使用真实环境或您设置的本地数据——然后才能进行步骤1。无法针对无法运行的应用进行采用验证。

- **Next.js 16.3 或更高版本。** 该版本是此技能依赖的组件发布的版本：顶层 `cacheComponents`、`export const instant`、开发覆盖层即时导航验证警告以及 `cache-components-instant-false` 代码转换器。如果 `next --version` 报告低于 16.3，请先升级：
  - `npx @next/codemod@latest upgrade latest` 应用版本到版本的代码转换器。
  - 阅读相关的 [版本升级指南](https://nextjs.org/docs/app/guides/upgrading)（例如 [版本 16](https://nextjs.org/docs/app/guides/upgrading/version-16)），了解代码转换器未涵盖的内容。

- **没有不兼容的配置键。** `cacheComponents: true` 在任何仍然导出 `dynamic`、`revalidate` 或 `fetchCache` 的文件上出错。在运行代码转换器之前，清点这些导出，然后遵循 [迁移指南的每个键部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components)。该指南是翻译每个值的来源。`cache-components-instant-false` 代码转换器不会删除这些配置。

- **`experimental.dynamicIO` 是致命的。** 它被重命名为顶层 `cacheComponents`，旧键现在在构建运行之前中止——首先删除它（或用 `cacheComponents: true` 替换）。`experimental.useCache` 仍然作为已弃用的别名被接受；一旦设置 `cacheComponents: true`，它就变得多余，因此为了清晰起见，请删除它。

### 注意事项

- **标志之前没有通过的基线。** 如果应用已经使用 `"use cache"`，则标志之前的构建会因 `please enable the feature flag cacheComponents` 而出错。启用标志是您首先做的事情（在增量中，在代码转换器之前；在直接中，在修复路由之前）——不是在获得通过构建之后做的事情。在您的起始摘要中注意这一点，以免它看起来像是一个回归。

- **现有的缓存可以保留。** 遵循迁移指南的 [`fetch` 和 `unstable_cache` 部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components#fetch-cache-options)。不要仅仅为了启用缓存组件而重写它们。

- **离线文档。** 指南链接在 `node_modules/next/dist/docs/` 下有离线副本（自 Next.js 16.2 起捆绑），目录布局按顺序编号（例如 `node_modules/next/dist/docs/01-app/02-guides/migrating-to-cache-components.md`）。如果您无法预测编号前缀，`find node_modules/next/dist/docs -name '<slug>.md'` 可以解决它。`/docs/messages/*` 错误页面未捆绑。

- **较旧版本没有捆绑的文档。** 在开始之前，建议用户运行 `npx @next/codemod@latest agents-md`：它下载与版本匹配的副本到 `.next-docs/` 并在 `AGENTS.md` 中写入索引。它会触及它们仓库中的文件，因此请先询问，只有在他们想要它的情况下才运行。

## 工作的形式

有一个循环：自上而下遍历路由树，一次一个功能，将每个路由针对 `next dev` + 浏览器进行采用。构建是每个功能的最终检查，而不是工作表面。

步骤1的选择是首先选择所有路由退出验证，还是边修复路由边进行。无论哪种方式，循环都是相同的：

- **使用安静的预步骤（增量）。** 运行代码转换器，修复它无法修复的内容，并完全迁移以前需要静态渲染的路由。其他路由保留其选择退出，以便后续的 PR。

- **不使用（直接）。** 启用 `cacheComponents` 并从构建标记的第一个开始启动循环。相同的循环，但每个修复都位于一个分支上，直到采用完成。

在两者中，每个路由的成功条形图都是相同的：**dev 循环报告没有错误并且 `next build` 通过**。在每项功能之后与用户确认，并建议提交，但未经他们确认绝不提交。预期大部分时间将花费在循环中，而不是在预步骤中。

## 背景

`cacheComponents: true` 要求每个路由都可以预渲染。一个在 `<Suspense>` 外部读取请求时间数据的路由是“阻塞”的，并且会失败构建。`export const instant = false` 将路由标记为允许阻塞，这会在开发和开发环境中清除它；在布局上，它在构建期间覆盖整个子树，但客户端导航仍然针对其每个子段进行验证。在 `"use cache"` 函数中包装的读取计为缓存边界，而不是阻塞读取。

当修复引入 `"use cache"` 时，请遵循缓存指南以选择数据级别或UI级别的边界并设置其生命周期 [在突变后重新验证](https://nextjs.org/docs/app/getting-started/caching#usage) 和 [使用 [`use cache` 缓存键参考](https://nextjs.org/docs/app/api-reference/directives/use-cache#cache-keys) 当结果因参数或捕获值而异时]。

出现三种类型的阻止，通常按此顺序：

每当修复引入 `<Suspense>`，请遵循流式指南的 [粒度流式模式](https://nextjs.org/docs/app/guides/streaming#granular-streaming-with-suspense) 和 [防止CLS的指导](https://nextjs.org/docs/app/guides/streaming#cls-cumulative-layout-shift)。

1. **请求时间读取** (`cookies()`，`headers()`，`await params`，`await searchParams`)。当在页面或布局顶部等待时，所有四个都会阻塞。`params` 和 `searchParams` 经常被遗漏，因为它们不像 cookie 和 headers 那样被框定为“请求数据”。修复方法是将读取推入一个用 `<Suspense>` 包装的子组件——对于 `params`/`searchParams`，将 Promise转发到子组件并在那里等待它；不要在页面顶部 `await`。

2. **模块/渲染时间同步IO** (`new Date()`，`Date.now()`，`Math.random()`，`crypto.randomUUID()`)。即使 `instant = false`，这些也会导致构建失败——选择退出不会抑制它们。如果它们在共享布局中，它们会阻塞其下的每个路由。代码转换器无法修复它们；运行它之后，使用每个构建错误及其链接的文档来识别要手动翻译的已报告调用（参见 [增量预步骤](#incremental)）。

3. **读取请求数据的 `"use cache"` 文件。** 一个具有顶层 `"use cache"` 指令的文件不能导出 `instant`；将这两个错误与 `Only async functions are allowed to be exported in a "use cache" file.` 结合，这意味着该指令不适用于该路由。在运行代码转换器之前删除它。

## 工作表面

### 查找阻塞路由

在您工作时，优先使用 `next dev` 而不是 `next build`。

- **`next dev`** — 工作表面。访问一个路由；其阻塞错误会在开发覆盖层中显示完整的堆栈跟踪和链接到每个错误文档的修复卡片。一次处理一个路由——错误不会在一个地方累积。路由本身仍然返回 HTTP 200，因此请查看覆盖层（或 `.next-dev.log`），而不是状态代码。清除覆盖层是调用路由干净的一半——另一半是浏览器验证（见 [步骤2](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)）并且该路由的构建通过。

- **`next build`** — 仅检测。构建是 `next dev` 的权威检查，不是其替代品。将其用作循环中每个功能的最后一道关卡（通过构建是每个路由成功条形图的一部分）以及跨整个应用的最终验证。在增量中，构建还确认预步骤（代码转换器选择退出每个页面和布局，没有共享布局仍然有同步IO阻止）在您提交该 PR 之前。在处理路由时，不要用构建代替开发循环——通过编译并不能告诉您最终进入了静态外壳和什么流式传输。默认情况下，构建会在第一个阻塞路由处停止，因此它也不适合估计工作量。两个标志在迭代时很有帮助：`--debug-build-paths` 仅构建您命名的路由（逗号分隔的文件路径模式，相对于项目根目录，例如 `--debug-build-paths="app/admin/**/page.tsx"`——不是URL路径；`--debug-build-paths="app/(marketing)/about/page.tsx"`——不是 `/about`；`--debug-build-paths="app/admin"` 匹配不到任何内容并静默构建零个路由），以及 `--debug-prerender` 禁用早期退出，因此构建会继续通过第一个预渲染失败，报告每个阻塞路由，并打印一个更完整的堆栈跟踪，其中包含原始文件和行。

每个阻塞错误都有一个文档页面——打开它。开发覆盖层和构建终端都会打印每个错误时 `https://nextjs.org/docs/messages/<slug>` 链接。该页面是修复的权威配方；内联消息只是一个摘要。即使您认为您知道该模式，也要获取每个不同错误的链接——配方会演变，并且相同的错误类别可以根据路由读取的内容有不同的正确修复。不要仅凭内联消息进行即兴创作。（`/docs/messages/*` 页面未捆绑离线；如果您没有网络，请回退到 `node_modules/next/dist/docs/` 下的每个API指南，并在报告时注明限制。）

### 在运行时验证每个修复

通过构建或清除覆盖层并不能证明路由实际上在运行——缓存组件是一个运行时问题（一个带有流式数据的静态外壳）。在每次修复后验证，而不仅仅是在结束时。

按优先顺序：

1. **[`next-dev-loop`](https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop) — 强烈推荐。** 通过 `agent-browser` 与实时浏览器交叉检查 `/_next/mcp`，并在一次传递中显示编译和运行时问题。诊断（React 树、suspense 边界、控制台+网络）比手动操作 `next dev` 更丰富。

   在开始循环之前安装它。不要等到您遇到 `next dev` 单独无法解释的东西。它随此技能一起提供，因此请先检查它是否已经可用，如果不可用，则安装它：

   ```bash
   npx skills add https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop
   ```

   技能声明其所需的 `agent-browser` 版本，并引导您完成它。

   **需要 Turbopack。** 如果 `package.json` 的 `dev` 脚本传递 `--webpack`，请向用户报告并询问是否有理由停留在 webpack。如果没有，请切换到 Turbopack（Next.js 16.3+ 默认）。如果他们想保留 webpack，请跳过此安装并使用 [仅构建的循环](#the-loop-build-only-fallback) 代替。

   您不需要权限来安装 `next-dev-loop` 本身。它是一个工具，就像安装一个开发依赖项。如果用户在场，请简要告诉他们您正在为其验证安装它。在非交互式运行（CI、仪表板、沙盒）中，无需询问即可安装它——“无法提示用户”不是跳过的理由。唯一合法的跳过是真实的技术阻止：没有网络、没有 npm、只读文件系统、声明的无新依赖政策或 webpack-only 开发脚本。如果跳过，请在最终报告中命名具体的阻止。

2. **一个您可以自己驾驶的浏览器。** Playwright、直接 `agent-browser`、任何浏览器自动化工具。仅在 `next-dev-loop` 真正被阻止时使用。您将错过框架侧检查（`/_next/mcp`），因此仅 DOM 断言无法捕获每个回归——对您称为“验证”的内容要更加谨慎。

3. **仅构建。** 如果您根本无法运行开发服务器，构建是您唯一的信号。`○ (静态)` 路由如果没有 `<Suspense>` 则完全由构建验证（没有流式传输用于测试）。`◐ (部分预渲染)` 路由仅外壳验证——在报告时标记它们。

4. **没有任何工具。** 请用户运行开发服务器（或构建）并报告他们看到的内容，或者将您已达到的里程碑移交给下一个阶段。

## 步骤1：选择策略

根据用户希望提交的PR，而不是工作的大小询问用户。在与用户交谈时，永远不要使用内部标签（增量、直接）——那是您自己的脚手架。用PR和功能来询问，例如：“您希望我首先打开一个PR来启用缓存组件并选择所有路由退出验证，然后在后续PR中逐个功能处理路由采用？还是所有内容都在一个分支上？” 即使在小型应用上，增量路径仍然有价值（审查大小的PR、可回滚、`// TODO: Cache Components adoption` 标记也作为您下次会话的工作队列）。不要替他们选择。

如果没有用户可以询问，默认为 **增量** 并记录选择。

尊重请求中的明确选择。如果用户要求增量迁移，并且还要求您完成迁移，请在继续到同一任务中的剩余路由之前建立和验证增量检查点。“完成”设置停止点；它不会改变选择的策略。

- **增量** — 安静的预步骤 + 循环。运行代码转换器以选择所有页面和布局退出验证，使构建通过，停止并与用户确认（见 [预步骤的末尾](#end-of-the-pre-step-check-in)），然后进入 [步骤2的循环](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time) 并作为后续PR提交每个功能。
- **直接** — 跳过预步骤。启用 `cacheComponents` 并直接进入 [步骤2的循环](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)；构建的阻塞路由是工作队列。

### 增量

在调用代码转换器之前，跨应用目录使用 `^export const (revalidate|dynamic|fetchCache)` 进行grep，并遵循每个匹配的迁移指南。将使用 `dynamic = 'force-static'` 或 `dynamic = 'error'` 的路由标记为此PR中完全迁移。代码转换器不会删除不兼容的配置。

代码转换器拒绝在脏工作树上运行。首先提交或暂存无关的工作，或者传递 `--force` 以让它的编辑与您的WIP一起应用。常见的误报：如果您最近升级了Next.js，`package.json` 和锁文件将已经脏——首先提交这些。

```bash
npx @next/codemod@latest cache-components-instant-false ./app
```

通过 [requires](#requires) 中解析的应用程序目录。错误的路径不是错误：它会报告 `0 ok` 并以 `0` 退出，因此请读取文件计数并将零视为失败的运行，而不是采用的应用程序。

将 `export const instant = false`（带 `// TODO: Cache Components adoption` 注释）插入到该目录下每个 `{page,layout,default}` 文件中，跳过已经声明 `instant` 的文件以及任何标记为 `"use client"` 或 `"use server"` 的模块。然后设置 `cacheComponents: true`。TODO 注释是循环的工作队列。

如果代码修改工具不可用（较旧的 `@next/codemod`、沙盒环境、离线运行），请手动重现：对于应用程序目录中每个不是 `"use client"` 或 `"use server"` 且尚未声明 `instant` 的 `{page,layout,default}.{js,jsx,ts,tsx}` 文件，在导入之后插入以下内容：

```ts
// TODO: Cache Components adoption. Refactor this route so this opt-out can be removed.
// See: https://nextjs.org/docs/app/guides/migrating-to-cache-components
export const instant = false
```

代码修改工具故意对每个部分进行排除，而不仅仅是根部分。解析是自上而下的，先执行明确的配置：最高的 `instant = false` 决定了整个子树。在每个部分上排除，删除一个部分的排除项只会验证该部分；子代保留自己的排除项并继续通过。如果只有根部分被排除，则删除它将立即重新启用整个应用程序的验证。

由于最高的排除项获胜，因此自上而下删除它们（首先删除根布局，然后向下遍历）。删除叶子的排除项在祖先仍然持有排除项时不会起作用。

从之前静态的路由和任何掩盖其验证的共享部分中删除排除项。解决它们的错误并确认它们仍然预渲染。单独的缓存数据调用并不能证明路由仍然是静态的。

接下来，运行 `next build` 以暴露代码修改工具无法处理的阻止项。构建是证明，而不是代码修改工具运行——一个直接调用 `new Date()` / `Math.random()` 的共享布局仍然失败，无论排除项如何（参见 [background](#background)）。如果正常构建报告没有定位到调用的同步-I/O 错误，请使用 `next build --debug-prerender --debug-build-paths="app/path/to/page.tsx"` 重新运行该路由。对于它报告的每个同步-I/O 错误：

1. **模块/渲染时的同步-I/O。** 使用路由、原始文件和行号以及构建输出中的 `/docs/messages/` 链接来定位错误。如有必要，在整个存储库中搜索 `new Date()`、`Date.now()`、`Math.random()` 和 `crypto.randomUUID()`（不仅仅是 `app/**/layout.{js,jsx,ts,tsx}`——读取可能存在于任何导入到布局的组件中）。不要更改未报告的匹配项。从链接的错误页面应用适当的选项，然后在临时边界上方添加此注释，该边界仅用于解除构建阻止：

   ```tsx
   // TODO: Cache Components adoption. Added to unblock the build: remove this boundary to re-trigger the error and review the documented options.
   ```

   它与代码修改工具写入的注释共享 `TODO: Cache Components adoption` 前缀，因此检查入站 grep 可以找到它们。删除边界会使错误再次触发及其修复卡片——这与在循环中删除排除项相同。

每次修复后，当可用时重新运行作用域构建，然后再次运行 `next build` 以找到下一个阻止项。重复直到正常构建通过。

构建通过后，确认每个延迟的路由仍然被排除项覆盖，并且没有共享排除项覆盖之前静态的路由。如果应用程序没有之前静态的路由并且根布局仍然延迟，请确认它获得了排除项（`grep -n "export const instant" <app dir>/layout.*`）。根布局渲染每个路由，包括框架路由如 `/_not-found`，所以如果它被遗漏了，请手动将其添加到其中 `export const instant = false`。

像 `/_not-found` 这样的合成路由没有用户文件——当它们阻止时，请修复根布局的排除项，而不是合成路由。客户端组件（`"use client"`）不会获得排除项（从它们导出 `instant` 是构建错误），但它们不是罕见的阻止项。常见的情况是根布局的导航或标题中的客户端组件调用 `usePathname()`/`useSearchParams()`：它会阻止带有 `blocking-prerender-client-hook` 的每个动态路由，而静态路由通过（路径名在预渲染时已知），这会掩盖它直到你到达动态部分。这不是祖先数据修复——请遵循 [错误文档页面](https://nextjs.org/docs/messages/blocking-prerender-client-hook) 中的 `<Suspense>` 配方。只有当客户端路由在服务器数据上阻止时，你才会在其祖先中修复该数据。

### 预步骤结束：检查入站

仅增量。预步骤是可发布的 PR。在开始步骤 2 之前记录通过检查点。除非用户已经在同一任务中要求你完成完整迁移，否则停止并检查入站。用用户的语言与他们交谈；不要说“增量”或其他内部标签；谈论采用、PR 以及应用程序现在做什么。告诉他们：

- 你做了什么：打开了 Cache Components，运行了代码修改工具，迁移了之前静态的路由，修复了剩余的阻止项，并确认构建通过。
- 发生了什么变化：之前静态的路由仍然预渲染。其他页面和布局保留 `// TODO: Cache Components adoption` 排除项。
- 需要检查什么：之前静态的路由保持完全预渲染和可预取，并且延迟路由上的请求特定数据仍然是请求特定的。
- 问题：“在开始逐路由采用 Cache Components 之前，想以自己的 PR 打开它吗？还是继续在这个分支上？” 等待答案。

如果用户已经在同一任务中要求你完成迁移，请在记录此检查点后继续，而不是再次询问相同的问题。

### 直接

设置 `cacheComponents: true` 并移动到 [步骤 2](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)。构建的阻止路由是工作队列。

## 步骤 2：内部循环，一次一个功能移除排除项

“功能”是一个单个产品表面——`app/settings/profile/**`、`app/posts/[slug]/**`——而不是像 `app/dashboard/**` 这样的整个顶层应用程序。完成一个端到端后再开始下一个。

在一个功能内，自上而下遍历（布局在页面之前，首先根布局）。在子代之前移除布局的排除项会暴露布局自己的阻止读取。（直接：没有排除项要移除——修复每个失败的路由；如果一个祖先上的手写排除项掩盖了它，请先移除那个。）

中间遍历时通过构建并不意味着布局是干净的。在子代页面仍然有它们自己的排除项时移除布局的排除项会保持构建通过——每个页面都掩盖了继承的验证。布局的实际阻止读取只有在没有任何子代掩盖它们时才会暴露。不要在布局边界处将功能视为完成。

除非浏览器确实无法访问，否则使用 **带浏览器** 循环。`[next-dev-loop](#verifying-each-fix-at-runtime)` 技能是“浏览器可用”和如何安装它的来源。

### 循环，带浏览器（首选）

每个路由：

- 移除排除项（增量）或针对失败的路由（直接）。
- 在开发环境中重新加载。覆盖干净？跳过验证。覆盖仍然是红色的？修复。
- 修复——获取错误中链接的文档页面（`https://nextjs.org/docs/messages/<slug>`），应用那里的配方。内联覆盖文本是摘要；文档页面是权威来源。
- 在浏览器中验证。确认第一次绘制时可见的内容是你在 shell 中预期的——不是卡在回退上，不是在空 shell 中静默地流式传输所有内容。
- 如果修复影响了共享代码（布局、侧边栏组件），重新检查兄弟节点。共享 shell 的更改可以修复当前路由并破坏兄弟节点。

### 循环，仅构建（后备）

在没有方法驱动浏览器的情况下使用——CI、沙盒、用户没有运行 `next dev` 并且你无法启动一个。信号较弱：确认构建通过并且路由预渲染，但不是静态 shell 与流式传输的内容。

每个路由：

- 移除排除项（增量）或针对失败的路由（直接）。
- 使用 `--debug-build-paths app/<route>/**`（仅该路由）或 `--debug-prerender`（完整构建，但超过第一个失败）。路由通过？继续。仍然阻止？修复。
- 修复——获取错误中链接的文档页面（`https://nextjs.org/docs/messages/<slug>`），应用那里的配方。
- 如果修复影响了共享代码，重新检查兄弟节点。
- 当你将功能移交给标记为构建仅验证的路由时。每个 `◐` 路由在功能完成之前仍需要浏览器通过。

### 循环笔记

- [背景中的三个阻止类](#background) 在就地修复时经常被遗漏。缓存下游获取（`getThing(id)`）不会清除页面主体顶部的 `await params`——将参数承诺推入 `<Suspense>`-包装的子代。
- 模糊调用是用户检查，而不是代理判断。当你不确定哪个修复适合时，阻止代码看起来像安全敏感的，或者用户可能故意保持路由阻止——在编辑之前请阅读 [references/per-page-decisions.md](./references/per-page-decisions.md)。使用 `next-dev-loop` 的浏览器手递手并驱动路由上线，以便用户看到静态 shell → 回退 → 最终内容序列。如果无法进行实时演示，请附加你捕获的快照。
- 不要用注释来描述重构。代码修改工具（或你）应该留下的唯一注释是在排除项上的 `// TODO: Cache Components adoption`，以及用户现有的注释。不要用注释标注每个 `<Suspense>` 边界或 `"use cache"` 调用的作用——代码说明了这一点。只有在代码中无法清楚地理解原因时才添加注释（例如，一个有理由的故意 Block）。
- 对于具有相同机械修复的许多路由，首先验证一个代表性路由。然后批量使用相同配方的不相交路由组，并一起运行共享构建和浏览器检查。

保留功能路由的待办事项列表。当功能中的每个路由都干净时，移动到步骤 3。

## 步骤 3：验证功能

与用户检查入站前的检查清单：

- `next build` 完成而没有阻止路由错误。
- 功能中没有裸 TODO：`grep -rn "TODO: Cache Components adoption"` 找到代码修改工具的排除项注释和预步骤中的同步-I/O 解除。任何留下的 `instant = false` 都是故意记录的 Block——注释已重写为原因（参见 [references/per-page-decisions.md](./references/per-page-decisions.md) → “何时保留 Block 在位”）。任何留下的 `await io()` 或 `await connection()` 都已审查并故意保留，而不是预步骤遗留的。
- 在浏览器中访问的每个路由：确认静态 shell 首先渲染并且每个 `<Suspense>` 回退都解析为其真实内容。如果可能，捕获这两种状态——回退（流中）和最终绘制——以便你有一个流式传输体验演示给用户。如果流速太快无法观察，请在浏览器中限制网络速度。
- 在填充任何其数据可以更新的新缓存后，突变检查确认下一次读取返回预期数据。
- 如果运行时验证失败，请在预采用分支上或恢复其排除项后重现相同路由。已经存在的失败是环境或数据问题，而不是采用回归。

然后与用户检查入站。与预步骤相同的规则：用用户的语言交谈。不要说“功能逐个循环”或其他内部标签；谈论你采用的功能以及用户将看到什么。

- 你做了什么：你触摸了哪些路由，以及每个路由的用户可见结果（例如，“帖子页面现在在骨架后面流式传输文章正文，而布局保持静态”）。
- 发生了什么变化：移除了排除项，添加了回退，引入了缓存边界。
- 展示，不要讲述。遵循 `next-dev-loop` 的浏览器手递手并驱动路由上线，以便用户看到静态 shell → 回退 → 最终内容序列。如果无法进行实时演示，请附加你捕获的快照。
- 给他们点击演示：一个短表，列出功能的路由——打开的 URL 和要查找的内容（什么即时渲染，哪个回退出现，什么流式传输）——以便他们可以自己验证每个路由。
- 问题：“想以功能为 PR 打开并继续下一个，还是在这里停止？” 等待答案。

**琐碎的功能可以跳过检查入站。** 如果采用功能只是移除其 `// TODO: Cache Components adoption` 排除项（没有添加 `<Suspense>`，没有引入 `'use cache'`，没有渲染顺序更改），用户看不到任何不同。继续到下一个功能而不停止；下次检查入站时提及它。

当循环在所有功能上运行时——每个剩余的 `instant = false` 都在原因注释下，`grep -rln "TODO: Cache Components adoption" app` 返回空——如果用户想将体验推进得更远，请指向 [further reading](#further-reading)，或者停止并发布。

### 路由表符号

`ƒ` → `◐` 是采用通常落的地方。`◐ (部分预渲染)` 意味着静态 shell 预渲染，请求时内容流式传输——任何读取 `cookies()`、`headers()`、`params` 或 `searchParams` 的路由的目标状态。某些路由在通过文档的逃生通道进行请求时工作时确实保持 `ƒ` 状态（例如，使用 `await connection()` 的布局）；页面不再被排除，而是真正动态的。不要只为了追逐 `◐` 而删除逃生通道。相反也成立：`instant = false` 并不强制路由为 `ƒ`。符号反映了路由在预渲染时的行为，而不是它导出的验证旋钮。

`◐` 告诉你存在 shell，而不是里面有什么。放置位置过高的 `<Suspense>` 边界（例如，包装整个页面体，或 `<Suspense fallback={null}>` 围绕文章内容）将可见内容从静态 shell 推入流式传输有效负载；构建仍然报告 `◐`，因为 _某个_ shell 预渲染了（通常是只有 `<html><body>` 与框架标记）。路由表无法告诉你 shell 中有什么；浏览器可以。如果 shell 为空并且所有内容都流式传输，请将 `<Suspense>` 边界向下移动到实际动态读取更近的位置。

## 进一步阅读

以下工作可选，存在于文档中——将用户链接到它们，让他们决定下一步做什么。不要在这个技能内带他们走过这些。

- [进行更多即时导航的扫描](./references/dev-only-validations.md) — 这是一个可选的后续步骤，一旦采用完成就不再需要。通过构建通过并不是最终结果，因为开发者在每次页面加载时都会验证每个路由（模拟页面加载和客户端导航），并捕获构建的首次错误退出和子级阴影所跳过的内容。将其作为不希望采用部分预取的用户实现即时导航的较小路径。采用部分预取（下方）会运行相同类型的循环，并且无论如何都符合这些见解，因此建议两者都推荐，并让用户选择哪个，或者是否。参考是执行该循环的循环。
- [`next-partial-prefetching-adoption`](https://github.com/vercel/next.js/tree/canary/skills/next-partial-prefetching-adoption) — 采纳部分预取的后续技能：它启用 `partialPrefetching` 并对每个 `<Link prefetch={true}>` 进行决策表审计（或关闭标志增量采用，由 `instant-link-prefetch-partial` 见解驱动）。它以与该技能序列化缓存组件相同的方式序列化，但见解仅限开发人员，因此它是浏览器点击通过，而不是构建循环。建议在即时导航之后，因为那些修复直接输入到外壳可以预取的每个路由的量。概念存在于 [采用部分预取指南](https://nextjs.org/docs/app/guides/adopting-partial-prefetching) 中。
- [使用端到端测试防止回归](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) — `@next/playwright` 的 [`instant()`](https://nextjs.org/docs/app/api-reference/file-conventions/route-segment-config/instant#testing-instant-navigation) 辅助程序在导航时立即可用的 UI 上断言，因此回归在 CI 中暴露。建议在路由变为即时后：`next-dev-loop` 确认它 _现在_；一个 `instant()` 测试保持它这样。
- [`next-cache-components-optimizer`](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-optimizer) — 一个单独的技能，它增加每个路由的静态外壳，以便更多页面预渲染，更少流式传输。纯粹的优化，不是采用的一部分。
