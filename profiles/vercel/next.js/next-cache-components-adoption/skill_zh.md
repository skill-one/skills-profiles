# next-cache-components-adoption

在一个应用上启用缓存组件并引导它通过一次成功的构建。这项技能按顺序执行工作；针对每个错误的配方存在于开发覆盖层的修复卡片和构建的终端输出中。有关此技能应用的概念和每个API配方的权威参考，请参阅[迁移到缓存组件指南](https://nextjs.org/docs/app/guides/migrating-to-cache-components)。当技能步骤引用模式（`"use cache"`、`cacheLife`、`<Suspense>`放置等）并您想要完整的解释时，请参考该指南。

## requires

- **App Router项目。** 缓存组件是App Router的功能；`cacheComponents: true`对`pages/`路由无作用。如果项目有`pages/`或`src/pages/`树但没有`app/`或`src/app/`树，请停止并告知用户——页面到App的迁移是一个独立的项目，不是这项技能的一部分。一个混合应用（同时有`pages/`和`app/`）是没问题的：该标志影响`app/`路由；`pages/`路由不受影响，也不需要选择退出。

- **一个已解析的应用目录。** 首先定位`next.config.{js,ts,mjs,cjs}`：那是项目根目录，从子目录调用的代理否则会针对错误的`cwd`测试`app/`并找不到任何东西。在它下面查找`app/`和`src/app/`，并将这项技能中的每个命令和glob视为相对于存在的目录。如果两者都存在，Next.js构建`app/`并从不查看`src/app/`，所以它的路由被阴影且未构建——告知用户这一点，并询问要迁移哪个树而不是选择一个。

- **一个可运行的应用。** 整个循环针对`next dev`和浏览器进行验证，所以应用必须启动。如果它在导入时读取数据库或必需的环境（例如一个在缺少`DATABASE_URL`时抛出错误的`env.ts`），请在步骤1之前确认它确实启动了——使用真实环境或您自己设置的真实数据——然后才能进行步骤1。无法运行的应用无法进行采用验证。

- **Next.js 16.3或更高版本。** 该版本是这项技能依赖的组件的发布点：顶层`cacheComponents`、`export const instant`、开发覆盖层即时导航验证警告以及`cache-components-instant-false`代码修改器。如果`next --version`报告低于16.3，请先升级：
  - `npx @next/codemod@latest upgrade latest`应用版本到版本的代码修改器。
  - 阅读相关的[版本升级指南](https://nextjs.org/docs/app/guides/upgrading)（例如[版本16](https://nextjs.org/docs/app/guides/upgrading/version-16))，了解代码修改器未涵盖的内容。

- **没有不兼容的配置键。** `cacheComponents: true`在任何仍然导出`dynamic`、`revalidate`或`fetchCache`的文件上都会报错。在运行代码修改器之前，清点这些导出，然后遵循[迁移指南的每个键部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components)。该指南是翻译每个值的权威来源。`cache-components-instant-false`代码修改器不会删除这些配置。

- **`experimental.dynamicIO`是致命的。** 它被重命名为顶层`cacheComponents`，旧键在任何构建运行之前都会中止——请先删除它（或用`cacheComponents: true`替换）。`experimental.useCache`仍然被接受为已弃用的别名；一旦`cacheComponents: true`被设置，它就是冗余的，所以请删除它以保持清晰。

### notes

- **标志之前没有通过基线。** 如果应用已经使用`"use cache"`，则标志之前的构建会因为`please enable the feature flag cacheComponents`而报错。启用标志是您首先做的事情（在增量中，在代码修改器之前；在直接中，在修复路由之前）——不是在得到一个通过构建之后做的事情。在您的起始摘要中注意这一点，以免它看起来像是一个回归。

- **现有的缓存可以保留。** 遵循迁移指南的[`fetch`和`unstable_cache`部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components#fetch-cache-options)。不要仅仅为了启用缓存组件而重写它们。

- **离线文档。** 指南链接在`node_modules/next/dist/docs/`下有离线副本（自Next.js 16.2以来捆绑），目录布局按顺序编号（例如`node_modules/next/dist/docs/01-app/02-guides/migrating-to-cache-components.md`）。如果您无法预测编号前缀，`find node_modules/next/dist/docs -name '<slug>.md'`可以解决它。`/docs/messages/*`错误页面没有捆绑。

- **较旧版本没有捆绑的文档。** 在开始之前建议用户运行`npx @next/codemod@latest agents-md`：它下载与版本匹配的副本到`.next-docs/`并写入`AGENTS.md`中的索引。它会触及它们仓库中的文件，所以请先询问他们，只有在他们想要它时才运行。

## the shape of the work

有一个循环：自上而下遍历路由树，一次一个功能，对每个路由采用`next dev` + 浏览器。构建是每个功能的最终检查，而不是工作表面。

步骤1的选择是首先将所有路由从验证中排除，还是边修复路由边进行。无论哪种方式，循环都是相同的：

- **使用安静的预步骤（Incremental）。** 运行代码修改器，修复它无法修复的内容，并完全迁移之前需要静态渲染的路由。其他路由保留它们的排除选项，以便后续的PR处理。
- **不使用（Direct）。** 启用`cacheComponents`并从构建标记的第一个路由开始循环。相同的循环，但每个修复都位于一个分支上，直到采用完成。

在两者中，每个路由的成功条形图都是相同的：**dev loop报告没有错误并且`next build`通过**。在每次功能后与用户确认，并建议提交，但未经他们确认绝不提交。预期大部分时间都在循环中，而不是在预步骤中。

## background

`cacheComponents: true`要求每个路由都是可预渲染的。一个在`<Suspense>`之外读取请求时间数据的路由是“阻塞”的，并且会失败构建。`export const instant = false`将路由标记为允许阻塞，这会清除开发中和构建中的阻塞；在布局中，它在构建期间覆盖整个子树，但客户端导航仍然单独验证每个子段。包裹在`["use cache"]`函数中的读取计为缓存边界，而不是阻塞读取。

当修复引入`"use cache"`时，请遵循缓存指南以[选择数据级别或UI级别的边界并设置其生命周期](https://nextjs.org/docs/app/getting-started/caching#usage)以及[在变异后重新验证](https://nextjs.org/docs/app/getting-started/revalidating)。当结果因参数或捕获值而变化时，使用`["use cache"]`缓存键参考[https://nextjs.org/docs/app/api-reference/directives/use-cache#cache-keys]。

出现三种类型的阻塞，通常按此顺序出现：

每当修复引入`<Suspense>`时，请遵循流指南的[粒度流模式](https://nextjs.org/docs/app/guides/streaming#granular-streaming-with-suspense)和[防止CLS的指导](https://nextjs.org/docs/app/guides/streaming#cls-cumulative-layout-shift)。

1. **请求时间读取** (`cookies()`、`headers()`、`await params`、`await searchParams`)。当在页面或布局的顶部等待时，这四个都会阻塞。`params`和`searchParams`经常被遗漏，因为它们不像cookies和headers那样被框定为“请求数据”。修复方法是将读取推入一个用`<Suspense>`包装的子组件——对于`params`/`searchParams`，将Promise转发到子组件并在那里等待它；不要在页面顶部等待。

2. **模块/渲染时间的同步IO** (`new Date()`、`Date.now()`、`Math.random()`、`crypto.randomUUID()`)。即使`instant = false`，这些也会导致构建失败——排除选项不会抑制它们。如果它们在一个共享布局中，它们会阻塞该布局下的所有路由。代码修改器无法修复它们；在运行它之后，使用每个构建错误及其链接的文档来识别需要手动翻译的报告调用（参见[增量预步骤](#incremental)）。

3. **读取请求数据的`"use cache"`文件。** 一个具有顶层`"use cache"`指令的文件不能导出`instant`；将两者结合会导致错误，`Only async functions are allowed to be exported in a "use cache" file.`，这意味着该指令不适合该路由。在运行代码修改器之前删除它。

## working surfaces

### finding blocking routes

在您工作时，优先使用`next dev`而不是`next build`。

- **`next dev`** — 工作表面。访问一个路由；它的阻塞错误会在开发覆盖层中显示，带有完整的堆栈跟踪和链接到每个错误文档的修复卡片。一次修复一个路由——错误不会在一个地方累积。路由本身仍然返回HTTP 200，所以请阅读覆盖层（或`.next-dev.log`），而不是状态代码。清除覆盖层是调用路由干净的一半——另一半是浏览器验证（见[步骤2](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)）并通过该路由的通过构建验证。

- **`next build`** — 仅检测。构建是`next dev`的权威检查，不是它的替代品。将其用作每个功能循环的最后一个门禁（通过构建是成功的一部分）并在整个应用中进行最终验证。在增量中，构建还确认预步骤（代码修改器排除了每个页面和布局，没有共享布局仍然有同步IO阻塞）在您提交该PR之前。不要在您正在处理路由时用构建代替开发循环——通过编译成功并不能告诉您最终进入了静态外壳和什么流了。默认情况下，构建会在第一个阻塞路由处停止，所以它也不适合估计工作量。有两个标志在迭代时很有帮助：`--debug-build-paths`仅构建您命名的路由（逗号分隔的文件路径模式，相对于项目根目录，例如`--debug-build-paths="app/admin/**/page.tsx"`——不是URL路径；`--debug-build-paths="app/(marketing)/about/page.tsx"`——不是`/about`；`--debug-build-paths="app/admin"`匹配不到任何东西并静默构建零路由），以及`--debug-prerender`禁用早期退出，以便构建继续通过第一个预渲染失败，报告每个阻塞路由，并打印更完整的堆栈跟踪，其中包含原始文件和行。

每个阻塞错误都有一个文档页面——打开它。开发覆盖层和构建终端都会打印每个错误时`https://nextjs.org/docs/messages/<slug>`的链接。该页面是修复的权威配方；内联消息只是一个摘要。获取您遇到的每个不同错误的链接，即使您认为您知道该模式——配方会发展，相同的错误类别可能具有不同的正确修复，具体取决于路由读取的内容。不要仅凭内联消息进行即兴创作。（`/docs/messages/*`页面没有离线捆绑；如果您没有网络，请回退到`node_modules/next/dist/docs`下的每个API指南，并注意局限性。）

### verifying each fix at runtime

通过构建或清除覆盖层并不能证明路由实际上表现良好——缓存组件是一个运行时问题（一个静态外壳与流式数据）。在每次修复后进行验证，而不仅仅是在结束时。

按优先顺序：

1. **[`next-dev-loop`](https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop) — 强烈推荐。** 通过`agent-browser`将`/_next/mcp`与实时浏览器进行交叉检查，并在一次传递中显示编译和运行时问题。诊断（React树，suspense边界，控制台+网络）比手动操作`next dev`更丰富。

   在开始循环之前安装它。不要等到您遇到`next dev`单独无法解释的东西。它随这项技能一起提供，所以请先检查它是否已经可用，如果没有，请安装它：

   ```bash
   npx skills add https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop
   ```

   该技能声明其所需的`agent-browser`版本，并引导您完成它。

   **需要Turbopack。** 如果`package.json`的`dev`脚本传递`--webpack`，请向用户报告并询问是否有理由停留在webpack上。如果没有，请切换到Turbopack（Next.js 16.3+的默认值）。如果他们想保留webpack，请跳过此安装并使用[仅构建循环](#the-loop-build-only-fallback)代替。

   您不需要权限来安装`next-dev-loop`本身。它是一个工具，就像安装一个开发依赖一样。如果用户在场，请简要告诉他们您正在安装它以进行验证。在非交互式运行（CI，仪表板，沙盒）中，无需询问即可安装它——“无法提示用户”不是跳过的理由。唯一合法的跳过是一个真正的技术障碍：没有网络，没有npm，只读文件系统，声明的无新依赖政策，或webpack-only开发脚本。如果您跳过，请在最终报告中命名具体的阻塞器。

2. **您自己可以驾驶的浏览器。** Playwright，`agent-browser`直接，任何浏览器自动化工具。仅在`next-dev-loop`确实受阻时使用。您将错过框架侧检查（`/_next/mcp`），所以DOM断言并不能捕获每个回归——对您称为“验证”要更加谨慎。

3. **仅构建。** 如果您完全无法运行开发服务器，构建是您唯一的信号。`○ (Static)`路由没有`<Suspense>`会被构建完全验证（没有流式测试的内容）。`◐ (Partial Prerender)`路由仅外壳验证——在您报告时标记它们。

4. **完全没有任何工具。** 请用户运行开发服务器（或构建）并报告他们看到的内容，或者将您已达到的阶段移交给用户。

## step 1: choose a strategy

根据用户想要的PR，而不是工作的大小来询问用户。在与用户交谈时，永远不要使用内部标签（Incremental，Direct）——那是您自己的脚手架。请根据PR和功能询问，例如：`"Do you want me to first open a PR that turns on Cache Components and opts every route out of validation, then handle the actual route adoptions feature-by-feature in follow-up PRs? Or do everything on one branch?"` 即使在很小的应用中，增量路径仍然有价值（审查大小的PR，可回滚，`// TODO: Cache Components adoption`标记也双作您下次会话的工作队列）。不要为他们选择。

如果没有用户，默认为**Incremental**并记录选择。

尊重请求中明确的选项。如果用户要求增量迁移，并且还要求您完成迁移，请在继续到剩余路由之前建立和验证增量检查点。 “完成”设置了停止点；它不会改变选择的策略。

- **Incremental** — 安静的预步骤 + 循环。运行代码修改器以排除每个页面和布局的验证，使构建通过，停止并检查与用户（见[预步骤的结束](#end-of-the-pre-step-check-in)），然后进入[步骤2的循环](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)并作为后续PR提交每个功能。

- **Direct** — 跳过预步骤。启用`cacheComponents`并直接进入[步骤2的循环](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)；构建的阻塞路由是工作队列。

### incremental

在调用代码修改器之前，跨整个应用目录grep `^export const (revalidate|dynamic|fetchCache)`，并遵循迁移指南中的每个匹配项。将使用`dynamic = 'force-static'`或`dynamic = 'error'`的路由标记为在此PR中完全迁移。代码修改器不会删除不兼容的配置。

代码修改器拒绝在脏工作树中运行。首先提交或暂存无关的工作，或者传递`--force`以允许其编辑与您的WIP一起生效。常见的误报：如果您最近升级了Next.js，`package.json`和锁文件将已经脏——首先提交这些。
