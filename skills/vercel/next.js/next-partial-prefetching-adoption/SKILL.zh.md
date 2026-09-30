---
name: next-partial-prefetching-adoption
description: 在 Next.js 应用中启用部分预取功能，并了解其提供的洞察。当用户希望启用或采用部分预取功能时，切换 `partialPrefetching` 标志，使用 `export const prefetch = 'partial'` 选项路由，检查 `Link prefetch={true}` 的行为，通过 `instant()` 测试保留现有的预取 UI，或解决 `instant-link-prefetch-partial` 和 `instant-shell-url-data` 洞察。
---

# next-partial-prefetching-adoption

启用部分预取并遍历应用程序，直到每个链接都复用共享的应用程序外壳。这项技能按顺序执行工作；每个洞察的配方都位于开发覆盖层的修复卡及其文档页面上。[采用部分预取的指南](https://nextjs.org/docs/app/guides/adopting-partial-prefetching)是这项技能应用的概念的权威参考。

开发洞察和保留测试是两条不同的路径。洞察仅在 `next dev` 中出现，在开发覆盖层的洞察选项卡中。基于测试的保留测试针对生产类似构建运行 `instant()`，不需要开发服务器。启用标志后，单独的 URL-数据洞察扫描仍然使用 `next dev`。

## 保留门

在使用基于测试的保留时，第一个实施里程碑是通过 `instant()` 标志关闭的测试套件。设置生产测试设备，编写选定的断言，禁用 `partialPrefetching` 运行它们，并记录命令和退出状态。设备需要的仅测试配置是允许的，但在该基线通过之前，不要启用 `partialPrefetching` 或编辑目标、缓存边界或 Link 属性。安装缺失的测试依赖项是达到基线的一部分，而不是首先采用的原因。仅在 `rig-template.md` 确定存储库无法解决的明确障碍时，才使用手动路径，并记录障碍和延迟的测试覆盖率。

用用户将看到的内容与他们交谈——PR、功能以及应用程序启用后的行为——而不是洞察短码或步骤标签。在开始之前，简要告诉他们部分预取会改变什么：链接到路由预取一个共享的应用程序外壳，并且 `prefetch={true}` 也可以解析缓存的 URL 特定内容。审计确定从遗留完整预取要保留哪个 UI。

## 需要

- **采用缓存组件 (`cacheComponents: true`) 并通过构建。** 两者 `partialPrefetching` 和路由级别的 `prefetch` 导出都需要缓存组件。如果关闭，请先使用 [`next-cache-components-adoption`](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-adoption) 并在解决构建阻塞的预渲染错误后返回。这些错误可能会失败 `next build`；仅此技能处理的 `partialPrefetching` 洞察是非阻塞的开发信号。

- **Next.js 16.3 或更高版本。** `partialPrefetching`、`prefetch` 路由段配置和预取洞察都放在那里。

- **一个你可以驾驶的浏览器。** 基于测试的保留使用现有的或最小的生产模式 Playwright 套件；手动保留和最终演示使用运行中的生产应用程序。开发洞察路径和标志后的 URL-数据扫描使用 [`next-dev-loop`](https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop)；在开发通过之前安装它，除非它已经可用（`npx skills add https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop`）。如果应用程序是 webpack 钉定的，直接驾驶浏览器（`agent-browser`、Playwright）——你失去框架交叉检查，而不是洞察；它们仍然在覆盖层和开发日志中。

- **一个可运行的应用程序。** 保留和最终演示需要一个生产类似构建，因为自动预取仅在生产中运行。仅在使用洞察路径或运行标志后的 URL-数据扫描时需要开发服务器；不要仅仅为了确认基于测试的保留案例而启动它。如果应用程序在导入时读取数据库或必需的环境，请确认所选路径使用的环境可以在步骤 1 之前启动。

### 注意事项

- **离线文档。** 指南链接在 `node_modules/next/dist/docs/` 下有离线副本（自 Next.js 16.2 以来捆绑），目录布局按顺序编号（例如 `node_modules/next/dist/docs/01-app/02-guides/adopting-partial-prefetching.md`）。如果你无法预测编号前缀，`find node_modules/next/dist/docs -name '<slug>.md'` 可以解决它。`/docs/messages/*` 错误页面没有捆绑。

- **较旧版本没有捆绑文档。** 在开始之前，建议用户使用 `npx @next/codemod@latest agents-md`：它下载与版本匹配的副本到 `.next-docs/` 并在 `AGENTS.md` 中写入索引。它触及其存储库中的文件，所以先询问，然后只有在他们想要它时才运行它。

## 背景

采用部分预取意味着每个路由都保留重要的预取 UI，现在分为共享的应用程序外壳和任何链接明确请求的额外链接数据。指南是权威参考，用于了解预取包含的内容以及如何决定每个案例；这项技能针对运行中的应用程序按顺序执行这些工作。

决定大多数扫描的陷阱：默认链接仅预热共享的应用程序外壳。由 `params` 或 `searchParams` 键化的路由只有在它采用部分预取并且特定链接使用 [`<Link prefetch={true}>`](https://nextjs.org/docs/app/api-reference/components/link#prefetch) 后才能预取更多；然后 Next.js 在点击之前解析 URL 数据及其后面的任何缓存内容（指南的 [URL 数据](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#url-data) 部分）。

## 工作表面

- **生产模式的 `instant()` 套件——基于测试保留的主要记录。** 重用应用程序的生产构建、测试上下文和 Playwright 设置。首先读取现有的 `instant-nav.rig.md`；如果项目没有 rig，从 **`rig-template.md`** 创建它。相同的测试定义了采用前的遗留目标，并且在每个目标采用部分预取后成为工作队列。开发可以帮助调查失败，但只有这个套件决定预取的 UI 是否被保留。
- **开发服务器终端——洞察路径的主要记录。** 每个验证路由的洞察都记录为 `Error: Route "...": Next.js encountered ...` 行，并带有 `https://nextjs.org/docs/messages/<slug>` 链接。在扫描期间尾随开发日志；它是可搜索的记录，了解在哪里触发了什么，它在 Turbopack 和 webpack 上工作相同。
- **开发覆盖层的洞察选项卡。** 洞察是琥珀色、非阻塞的选项卡。它仅在洞察触发后出现，因此没有任何洞察出现的路由没有任何选项卡——这是干净的状态，而不是缺少功能。不要在安静的路径上寻找选项卡；从上面的开发日志确认干净，这是可靠的信号。前提条件是没有阻塞预渲染错误——那些错误会替换其路由上的洞察（见要求）。无关的问题（ hydration 错误、控制台错误）不会阻止扫描；不要在它上面停滞。当选项卡存在时，覆盖层药丸显示计数和每个洞察都链接到其文档页面。覆盖层在阴影根（`nextjs-portal`）内渲染，因此可访问性树快照看不到它——在需要程序matic 读取或点击它时，评估到 `shadowRoot`。
- **`next-dev-loop`** 驱动导航并读取覆盖层。优先考虑它而不是手工制作的浏览器自动化，原因与缓存组件技能相同（webpack 应用程序：见要求）。当浏览其 `/_next/mcp` 工具时，预取洞察通过 `get_errors` 和覆盖层显示，而不是同样命名的 `get_request_insights`。后一个是跨度和性能记录器（受 `experimental.requestInsights` 限制）并报告与预取无关的内容。

每个洞察都有一个文档页面——打开它。为每个不同的洞察获取链接页面；内联消息是摘要，页面是配方。

## 步骤 1：审计 `<Link prefetch={true}>` 导航（在启用之前）

在此审计和步骤 2 中的遗留基线期间，保持全局标志**关闭**。提前启用它将移除迁移需要测量的遗留行为。如果标志在未发布的工作中已经开启，请使用标志前的提交进行审计和基线。当用户可用时，询问如何以 PR 的语言发布它：

- **一个分支**——整个审计在一个更改中，标志启用并在最后（步骤 4）运行 codemod。
- **逐路由**——每个采用的目标作为自己的 PR 发布。洞察仍然为尚未达到的目标触发，一个实时的工作列表，步骤 4 在最后一个之后到来。

无论哪种方式，工作和顺序都相同——只有提交边界不同。当没有用户可用时，默认按应用程序大小：少量链接一个分支，审计足够大时，审查者需要较小的 diff 时逐路由。在你的报告中注明选择。

在整个源代码树中枚举显式预取和手动预取站点，而不仅限于 `app/`——它们通常位于 `src/components` 或共享 UI 包中。从 `next/link` 导入和重新导出开始，然后跟随自定义包装器到它们的消费者。使用 `rg -n '\bprefetch\b|router\.prefetch' -g '*.tsx' -g '*.jsx' .` 作为候选列表，而不是完整的审计；检查条件属性和转发的 `LinkProps` 以确定有效的生产值。包括每个审计的导航，其有效的生产 Link 值为 `prefetch={true}`：显式 `true`、裸 `prefetch` 属性和解析为 `true` 的表达式。从保留套件中排除默认值 `prefetch="auto"` 和 `prefetch={false}`，因为它们不会请求遗留完整预取。单独审计现有的 [`router.prefetch()`](https://nextjs.org/docs/app/api-reference/functions/use-router#userouter) 调用，因为它们没有 Link 洞察。对于新的手动预取，遵循 [预取指南](https://nextjs.org/docs/app/guides/prefetching#manual-prefetch)。如果没有链接解析为 `prefetch={true}`，就说出来并继续到 [步骤 4](#step-4-enable-the-flag)。

### 选择要保留的内容以及如何验证它

在编写测试或编辑目标之前，遵循指南的 [迁移指南](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#migrate-existing-full-prefetches) 提出值得保留的 UI。以一个简洁的表格呈现结果：

| 导航 | 提出结果 |

分组等效导航。总结将立即准备和流式传输的内容。当一个提案不明确时，在运行的应用程序中显示导航并要求用户确认。如果他们不可用，请遵循指南并记录假设。

在目标 UI 确定后，检查现有的测试设置。`instant()` 辅助程序来自单独的 [`@next/playwright`](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) 包，而不是 `next/experimental/testmode/playwright`。

- **适用的生产模式套件：** 默认使用基于测试的保留。重用项目的 `@next/playwright` 测试、生产脚本、身份验证和现有的 `instant-nav.rig.md`。遵循指南的 [预取 UI 测试工作流](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#verify-prefetched-ui-with-tests) 并在采用之前使完整的标志关闭套件变绿。不变的断言驱动迁移并作为回归覆盖率保留。
- **没有适用的生产模式套件：** 使用项目包管理器和测试约定在 **`rig-template.md`** 中设置生产模式 rig。这是基于测试的采用的一部分，不需要用户在场。
- **Rig 无法可靠运行：** 通过 **`rig-template.md`** 设置和活性检查。仅对于存储库无法解决的明确障碍（例如不可用的凭证或无法访问的生产环境）才回退到手动保留。记录障碍和延迟的测试覆盖率；不要声称基于测试的验证。

不需要用户输入来重用现有套件或创建 rig。仅在存储库无法回答环境问题或目标 UI 本身是产品决策时才询问。如果没有用户可用，请使用指南的安全产品默认值，并为具体的 rig 障碍保留手动验证。将新的预取 UI 视为步骤 7 的工作；在采用后单独验证任何故意删除的内容。

此工作流程针对点击的 `<Link>`。例如 `router.prefetch('/dashboard')` 是手动预取，而不是 Link 预取；将其保留在源审计中，并在步骤 6 中单独验证。

## 步骤 2：捕获遗留基线

在此步骤期间，不要启用 `partialPrefetching` 或编辑路由行为、Link 属性或缓存边界。允许运行 `instant()` 所需的仅测试配置。

对于基于测试的保留，完成 [保留门]：编写完整的 `instant()` 套件并**运行**它针对生产类似 rig，禁用部分预取。测试文件、构建、完成的导航或为用户打印的命令不是基线。在套件实际通过之前不要继续到步骤 3。

对于手动保留，在编辑任何目标之前完成之前/目标清单。仅当通过 `rig-template.md` 确定具体的 rig 障碍时，才回退到此路径，并记录障碍和延迟的测试。

## 步骤 3：采用目标并恢复目标

采用每个审计的目标，使用临时路由配置。路由导出足以让不变的测试在全局标志保持关闭时在目标上执行部分预取：

```tsx
// 参考：https://nextjs.org/docs/app/guides/adopting-partial-prefetching
export const prefetch = 'partial'
```

如果其他 URL 特定 UI 可能值得预取但不是遗留合同的一部分，请在其链接上保持 `prefetch={true}` 并标记路由以供步骤 7：

```tsx
// TODO(per-link-prefetch): 与用户一起评估是否应在点击之前解析 URL 数据。
// 参考：https://nextjs.org/docs/app/guides/optimizing-prefetching
export const prefetch = 'partial'
```

使用确切的缩写，以便步骤 7 可以通过 grep 它们。现在不要选择新的目标 UI；仅恢复从遗留行为中选择的目标。

对于基于测试的保留，在每次目标更改后重新运行受影响的**不变**测试，并将失败视为工作队列。在启用全局标志之前运行完整套件并记录其通过退出状态。对于手动保留，比较采用的生产导航与选定的目标，并记录尚未恢复的内容。应用指南的匹配保留模式以缓存和 Link-prop 变更，并在做出不清楚的新鲜度或缓存决定之前询问用户。上面标记的 URL-数据候选者等待步骤 7。

当恢复目标更改缓存或失效时，请遵循项目的现有验证方法以及 [重新验证](https://nextjs.org/docs/app/getting-started/revalidating) 指南。重用或扩展适用的套件以受影响的生命周期。如果项目不测试此类型的行为，请在采用期间不要引入新的测试基础设施；在生产中手动验证它并记录预期和观察到的结果。绿色的 `instant()` 测试证明准备就绪，而不是缓存正确性。仅在预期行为不明确时才询问用户。

> **如果你添加 `use cache`，请在 `next start` 下验证，而不仅仅是构建。** 在缓存的调用树中的任何 `cookies()`/`headers()`/session 读取在请求时抛出错误，而 `next build` 通过干净。参考 [`use cache`](https://nextjs.org/docs/app/api-reference/directives/use-cache)。

## 步骤 4：启用标志

一旦每个审计的目标都有 `prefetch = 'partial'`，就完成两个步骤。

1. **全局启用标志。** 在 `next.config.ts` 中设置 `partialPrefetching: true`（与 `cacheComponents: true` 一起）。现在每个路由都被采用，所以每个链接都是有效的。
2. **移除冗余的 `prefetch = 'partial'` 导出。** 运行第一方的 `remove-partial-prefetch` codemod 而不是文本查找和替换。它会移除每个 `export const prefetch = 'partial'`，包括在 `TODO(per-link-prefetch)` 标记下方的导出，并移除其生成的 Partial Prefetching 指南注释。TODO 标记及其优化预取指南链接保留用于步骤 7。其他值如 `prefetch = 'force-disabled'` 保留原样。

   ```bash
   npx @next/codemod@canary remove-partial-prefetch ./app
   ```

   在 `src/` 项目中使用 `./src/app` 并检查报告的文件数量。Codemod 拒绝在脏的工作树上运行。先提交或暂存无关的工作，或传递 `--force` 以让其编辑与你的 WIP 一起应用。如果 codemod 不可用（较旧的 `@next/codemod`，沙盒环境，离线运行），手动重现已通过移除每个 `app/**/{page,layout}.{js,jsx,ts,tsx}` 中的 `export const prefetch = 'partial'` 及其生成的 Partial Prefetching 指南注释——保留其他 `prefetch` 值，并将 `TODO(per-link-prefetch)` 标记和优化预取指南链接保留原位。当 codemod 可以运行时，不要手动编辑。

在标志和 codemod 一起应用后，在使用测试支持路径时重新运行锁定保留套件。否则，在最终全局配置下重复记录的生产比较。

## 步骤 5：清理 URL 数据洞察（启用后）

这是仅限开发的二次遍历。Shell 检查仅在标志开启时运行，在导航时触发，永远不会阻塞构建，因此可以在步骤 4 之后随时进行。从具体来源（最后一个 `next build` 路由表或 `app/` 树）构建路由队列，并将其保留为待办事项列表。

逐个功能清理。一个功能是一个单一的产品表面——`app/settings/**`，`app/posts/[slug]/**`——而不是整个顶层区域。完成一个端到端后再开始下一个：在 `next dev` 中加载其路由并解析其洞察。洞察永远不会阻塞构建，每个路由是独立的，因此部分清理会保留可工作的应用，每个功能都是用户可以独立审查或发布的自包含更改。

如果环境无法完成整个清理（慢速首次编译，在负载下崩溃的开发服务器，完全没有浏览器），在交接之前将无浏览器的工 作进行尽可能远。静态采用每个可以的路由：应用从 [`URL 数据`](https://nextjs.org/docs/messages/instant-shell-url-data) 的修复，直到新的 `<Suspense>` 边界，依赖于类型检查。一次通过整个队列——更大的重构不是推迟的理由，询问是否继续到下一个路由或层级不是检查点；继续进行。只有在做出真实判断时才停止，并将这些批量到单个交接报告中：静态采用的路线，仍然需要实时 Shell 检查的路线，以及队列。

关注洞察标签和开发日志中的 `Next.js encountered … data` 行。本步骤添加的信号是 [`URL 数据`](https://nextjs.org/docs/messages/instant-shell-url-data)：在挂起的子树中过高的 `params` 或 `searchParams` 读取将共享 Shell 绑定到一个 URL。这个洞察是狭窄的；它最可靠地出现在 `generateStaticParams` 路由中，其中 `params` 已经在 `<Suspense>` 下，但在 URL 特定的叶边界之前仍然等待。如果触发 `blocking-prerender-*` 错误，请应用相同的结构修复。

开启标志预取会渲染其 App Shell，这比 Cache Components 构建验证了更多路由。因此，在 Cache Components 下干净构建的路由（每个路由 `◐`，无错误）仍然可能在这里第一次渲染其 Shell 时出现 `blocking-prerender-*` 错误——[`运行时数据`](https://nextjs.org/docs/messages/blocking-prerender-runtime) (`cookies()`/`headers()`), [`未缓存数据`](https://nextjs.org/docs/messages/blocking-prerender-dynamic)（未缓存的 `fetch`/DB 调用），或同步 IO 如 `Date.now()`/`new Date()`。这不意味着 Cache Components 采用不完整；这是新的验证达到了构建从未执行的路径。这些不是 Partial Prefetching 洞察——按任何阻塞预取错误的方式修复每个问题。

这些修复很少涉及用户——每个洞察都命名了有问题的读取，其文档页面有修复，所以应用它并继续清理。收集罕见的例外，在最后批量提问：一个完全依赖 URL 的页面（将其全部包装后留下一个空 Shell），或一个应该保留禁用的路由。不要用注释记录重构——`<Suspense>` 边界自己会说明一切。

## 步骤 6：验证

提交给用户前的检查清单：

- **当 Cache Components 采用干净完成时，预期会进行空清理。** 安静的日志是成功，而不是缺失信号。如果你故意探测验证路径，使用一个 `generateStaticParams` 路由，其中 `params` 在 `<Suspense>` 内但 URL 特定的叶边界之前读取；其他形状可能会出现 `blocking-prerender-*` 而不是。
- App Shell 是真实的：对于每个你更改的路由，确认导航后的首次绘制显示预期的共享内容，而不是空 Shell 或卡住的回退。整个页面体周围的 `<Suspense>` 通过空 Shell 验证，这违背了目的。
- 洞察验证 Shell _结构_，而不是预取是否实际发生。在生产运行（自动预取仅在生产中运行）上确认导航到更改的链接会立即跳转到共享 Shell，以验证这一点。
- 对于测试支持的保留，每个锁定的 `instant()` 测试针对审计的 `<Link prefetch={true}>` 通过生产运行。对于手动保留，记录了前后清单和任何延迟的测试后续操作。
- 在填充任何新的或扩展的缓存后，其数据可以更新，变异检查通过适用的现有测试套件或记录的手动检查（当项目没有此类覆盖时）验证下一个读取。
- **如果应用强制预取**，洞察清理不包括它，所以空清理不是证明预取在标志后幸存的证据。在 `next start` 下验证调用：比较 `_rsc` 预取响应或资源时间线前后，并确保任何有意保留的完整预取仍然携带旧调用正在预热的数据。如果现在只返回 App Shell，使用与最近 `<Link prefetch={true}>` 目标相同的决策迁移该调用位置——缓存数据，或将按链接预取行为移至文档支持的 `<Link prefetch={true}>`。
- **在将损坏的路由归咎于标志之前**，使用 `partialPrefetching` 关闭（或在标志前分支）重现已知。标志会暴露现有问题——脆弱的请求时认证网关、重写、部署偏差——更早、更明显，但很少导致它们。如果它关闭标志时也损坏，它不是 Partial Prefetching 问题；在别处修复它，而不是这里。
- `next build` 仍然通过。

然后与用户提交。用他们的语言——不要洞察代码或步骤标签。

- 你做了什么：你审计了哪些链接，哪些目的地你采用了，以及每个链接现在预取什么。
- 发生了什么：删除的属性，添加的 `use cache` 边界，以及哪些路由带有 `TODO(per-link-prefetch)` 标记供以后处理。
- 对生产运行进行演示。自动预取仅在生 产中运行，所以 `next dev` 不会显示结果——运行 `next build` 和 `next start`，并将用户传递该 URL。该运行需要应用的真实环境（数据库、认证、密钥），部分或过时的安装或剩余生成的工件可能会因与采用无关的原因失败构建。从一开始就设定预期，验证是一个完整的、有凭证的生产运行，而不是快速检查。
- 展示，而不是讲述：在头部浏览器中针对生产服务器激活一个链接，让他们看到共享的 App Shell 立即绘制，URL 特定的区域流式传输。只有在无法使用实时浏览器时才附加前后截图。
- 给他们点击体验：每个更改路由的表格——点击的链接，以及点击后预期什么（什么立即绘制，什么流式传输）——让他们可以自行验证每个结果。
- 问题：“在查看哪些路由也应该预取其 URL 特定内容之前，想提交这个（或打开 PR）吗？” 等待答案——采用和按链接预取读作它们自己的更改。

## 步骤 7：按链接预取（可选）

审计标记了超出已保留的遗留合同候选，而不是决定它们。使用 Grep 查找 `TODO(per-link-prefetch)` 并与用户在一次对话中走完列表。每个路由的问题是他们是否希望点击前预取额外的 URL 相关内容，还是导航后流式传输。按链接预取每可预取链接成本一个服务器调用——指南的 [权衡](https://nextjs.org/docs/app/guides/optimizing-prefetching#trade-offs) 部分是检查清单。不要单独做这些调用。

对于没有回答“是”的情况，删除标记并将路由保留在 App Shell 默认下。对于回答“是”的情况，遵循 [优化预取指南](https://nextjs.org/docs/app/guides/optimizing-prefetching)，确认选中的链接针对生产运行，并在验证选定结果后删除标记。

没有 `TODO(per-link-prefetch)` 标记在完成步骤后幸存。按链接优化仍然是采用之外的单独提交或 PR。

最后，在简洁的 `导航 | 可能不再需要的理由` 表格中显示任何有效的 `prefetch={false}` 链接。解释 `false` 禁用所有预取，而 Partial Prefetching 的默认 `auto` 行为仅预取共享的 App Shell，所以添加的排除以避免遗留完整路由预取可能现在不再需要。邀请用户单独重新审视它们。

## 进一步阅读

- [即时导航](https://nextjs.org/docs/app/guides/instant-navigation) — 更广泛的验证模型和加载状态工具。
- [使用端到端测试防止回归](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) — 使用 `@next/playwright` `instant()` 辅助程序构建关闭标志的基线套件，然后将其保留为 CI 回归保护。
- [`next-cache-components-optimizer`](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-optimizer) — 增加每个路由的静态 Shell，以便 App Shell 携带更多。
