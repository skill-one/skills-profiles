# next-partial-prefetching-adoption

启用部分预取并遍历应用程序，直到每个链接都复用共享的应用程序外壳。这项技能按顺序执行工作；每个洞察的配方都位于开发覆盖层的修复卡片及其文档页面中。[采用部分预取指南](https://nextjs.org/docs/app/guides/adopting-partial-prefetching)是此技能应用的概念的权威参考。

开发洞察和保留测试是两条不同的路径。洞察仅在 `next dev` 中出现，在开发覆盖层的洞察选项卡中。基于测试的保留测试针对生产类似构建运行 `instant()`，不需要开发服务器。启用标志后，单独的 URL-数据洞察扫描仍然使用 `next dev`。

## 保留门

在使用基于测试的保留时，第一个实施里程碑是通过 `instant()` 的标志关闭套件。设置生产测试设备，编写选定的断言，使用禁用 `partialPrefetching` 运行它们，并记录命令和退出状态。设备需要的仅用于测试的配置是允许的，但在该基线通过之前，不要启用 `partialPrefetching` 或编辑目标、缓存边界或 Link 属性。安装缺失的测试依赖项是达到基线的一部分，而不是首先采用的原因。仅在 `rig-template.md` 确定存储库无法解决的明确障碍时，才使用手动路径，并记录障碍和延迟的测试覆盖率。

用用户将看到的内容与他们交谈——PR、功能以及应用程序启用后的行为——永远不会是洞察符号或步骤标签。在开始之前，简要告诉他们部分预取会改变什么：链接到路由预取一个共享的应用程序外壳，并且 `prefetch={true}` 也可以解析缓存的 URL 特定内容。审计决定从遗留完整预取保留哪个 UI。

## 要求

- **采用缓存组件 (`cacheComponents: true`) 并通过构建。** 两者 `partialPrefetching` 和路由级别的 `prefetch` 导出都需要缓存组件。如果关闭，请首先使用 [`next-cache-components-adoption`](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-adoption) 并在解决构建阻塞的预渲染错误后返回。这些错误可能会失败 `next build`；仅此技能处理的 Partial Prefetching 洞察是非阻塞的开发信号。

- **Next.js 16.3 或更高版本。** `partialPrefetching`、`prefetch` 路由段配置和预取洞察都放在那里。

- **一个你可以驾驶的浏览器。** 基于测试的保留使用现有的或最小的生产模式 Playwright 套件；手动保留和最终演示使用运行中的生产应用程序。开发洞察路径和启用标志后的 URL-数据扫描使用 [`next-dev-loop`](https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop)；在两个开发传递之前安装它，除非它已经可用（`npx skills add https://github.com/vercel/next.js/tree/canary/skills/next-dev-loop`）。如果应用程序是 webpack 钉定的，直接驾驶浏览器（`agent-browser`、Playwright）——你失去框架交叉检查，而不是洞察；它们仍然在覆盖层和开发日志中。

- **一个可运行的应用程序。** 保留和最终演示需要一个类似生产的构建，因为自动预取仅在生产中运行。仅在使用洞察路径或运行启用标志后的 URL-数据扫描时才需要开发服务器；不要仅仅为了确认基于测试的保留案例而启动它。如果应用程序在导入时读取数据库或必需的环境，请确认所选路径使用的环境可以在步骤 1 之前启动。

### 注意事项

- **离线文档。** 指南链接在 `node_modules/next/dist/docs/` 下有离线副本（自 Next.js 16.2 以来捆绑），目录布局按顺序编号（例如 `node_modules/next/dist/docs/01-app/02-guides/adopting-partial-prefetching.md`）。如果你无法预测编号前缀，`find node_modules/next/dist/docs -name '<slug>.md'` 可以解决它。`/docs/messages/*` 错误页面没有捆绑。

- **较旧版本没有捆绑文档。** 在开始之前，建议用户使用 `npx @next/codemod@latest agents-md`：它下载与版本匹配的副本到 `.next-docs/` 并在 `AGENTS.md` 中写入索引。它会修改其存储库中的文件，所以先询问，然后只有在他们想要它时才运行。

## 背景

采用部分预取意味着每个路由都保留重要的预取 UI，现在这些 UI 分为共享的应用程序外壳和任何链接明确请求的额外链接数据。指南是权威参考，用于了解预取包含的内容以及如何决定每个案例；这项技能针对运行中的应用程序按顺序执行该工作。

决定大多数扫描的陷阱是：默认链接仅预热共享的应用程序外壳。由 `params` 或 `searchParams` 键化的路由只有在它采用部分预取并且特定链接使用 [`<Link prefetch={true}>`](https://nextjs.org/docs/app/api-reference/components/link#prefetch) 后才能预取更多内容；然后 Next.js 在点击之前解析它后面的 URL 数据和任何缓存的 内容（指南的 [URL 数据](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#url-data) 部分）。

## 工作表面

- **生产模式的 `instant()` 套件——基于测试的保留的主要记录。** 重复使用应用程序的生产构建、测试上下文和 Playwright 设置。首先读取现有的 `instant-nav.rig.md`；如果项目没有 rig，则从 **`rig-template.md`** 创建它。相同的测试定义了采用前后的遗留目标，并且在每个目标采用部分预取后成为工作队列。开发可以帮助调查失败，但只有此套件决定预取的 UI 是否被保留。
- **开发服务器终端——洞察路径的主要记录。** 每个验证的路线的洞察都记录为 `Error: Route "...": Next.js encountered ...` 行，并带有 `https://nextjs.org/docs/messages/<slug>` 链接。在扫描期间尾随开发日志；它是可搜索的记录，显示了什么在何处触发，它在 Turbopack 和 webpack 上工作相同。
- **开发覆盖层的洞察选项卡。** 洞察是琥珀色、非阻塞的选项卡。它仅在洞察触发后出现，所以一个没有显示任何内容的路线没有任何选项卡——这是干净的状态，而不是缺少功能。不要在安静的路线 上寻找选项卡；从上面的开发日志确认干净，这是可靠的信号。前提条件是没有阻塞预渲染错误——它们会替换其路线上的洞察（见要求）。无关的问题（水合错误、控制台错误）不会阻止扫描；不要在它们上面停滞。当选项卡存在时，覆盖层药丸显示计数，并且每个洞察都有关联其文档页面的修复卡片。覆盖层在阴影根 (`nextjs-portal`) 内渲染，所以可访问性树快照看不到它——在需要程序化读取或点击它时，评估到 `shadowRoot`。
- **`next-dev-loop`** 用于驱动导航并读取覆盖层。优先考虑它而不是手动的浏览器自动化，原因与缓存组件技能相同（webpack 应用程序：见要求）。当浏览其 `/_next/mcp` 工具时，预取洞察通过 `get_errors` 和覆盖层显示，而不是同样命名的 `get_request_insights`。后一个是跨度和性能记录器（受 `experimental.requestInsights` 保护），它不报告任何关于预取的信息。

每个洞察都有一个文档页面——打开它。为每个不同的洞察获取链接的页面；内联消息是摘要，页面是配方。

## 步骤 1：审计 `<Link prefetch={true}>` 导航（启用之前）

在此审计和步骤 2 中的遗留基线期间，保持全局标志 **关闭**。过早启用它将移除迁移需要测量的遗留行为。如果标志在未发布的作品中已经开启，请使用启用标志前的提交进行审计和基线。当用户可用时，询问他们在 PR 语言的如何发布它：

- **一个分支**——整个审计在一个更改中，标志启用并在末尾运行 codemod（步骤 4）。
- **逐路由**——每个采用的目的地都作为自己的 PR 发送。洞察仍然为尚未达到的目的地触发，是一个实时的工作列表，步骤 4 在最后一个之后到来。

无论哪种方式，工作和顺序都相同——只有提交边界不同。当没有用户可用时，默认按应用程序大小：少量链接一个分支，当审计足够大时需要审查者较小的差异时逐路由。在你的报告中注明你的选择。

在整个源树中枚举显式预取和手动预取站点，而不仅仅是 `app/`——它们通常位于 `src/components` 或共享 UI 包中。从 `next/link` 导入和重新导出开始，然后跟随自定义包装器到它们的消费者。使用 `rg -n '\bprefetch\b|router\.prefetch' -g '*.tsx' -g '*.jsx' .` 作为候选列表，而不是作为完整的审计；检查条件属性和转发的 `LinkProps` 以确定有效的生产值。包括每个审计的导航，其有效的生产 Link 值为 `prefetch={true}`：显式 `true`、裸 `prefetch` 属性以及解析为 `true` 的表达式。从保留套件中排除默认值 `prefetch="auto"` 和 `prefetch={false}`，因为它们不会请求遗留完整预取。单独审计现有的 [`router.prefetch()`](https://nextjs.org/docs/app/api-reference/functions/use-router#userouter) 调用，因为它们没有 Link 洞察。对于新的手动预取，请遵循 [预取指南](https://nextjs.org/docs/app/guides/prefetching#manual-prefetch)。如果没有任何链接解析为 `prefetch={true}`，请说明并继续到 [步骤 4](#step-4-enable-the-flag)。

### 选择要保留的内容以及如何验证它

在编写测试或编辑目的地之前，请遵循指南的 [迁移指南](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#migrate-existing-full-prefetches) 来提议要保留的 UI。以简洁的表格呈现结果：

| 导航 | 提议结果 |

| --- | --- |

分组等效导航。总结什么会立即准备就绪，什么会流式传输。当一个提议不明确时，在运行中的应用程序中显示导航，并要求用户确认。如果他们不可用，请遵循指南并记录假设。

在目标 UI 确定后，检查现有的测试设置。`instant()` 辅助程序来自单独的 [`@next/playwright`](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) 包，而不是 `next/experimental/testmode/playwright`。

- **适用的生产模式套件：** 默认使用基于测试的保留。重复使用项目的 `@next/playwright` 测试、生产脚本、身份验证和现有的 `instant-nav.rig.md`。遵循指南的 [使用测试验证预取 UI](https://nextjs.org/docs/app/guides/adopting-partial-prefetching#verify-prefetched-ui-with-tests) 并在采用之前使完整的标志关闭套件变绿。未更改的断言驱动迁移并作为回归覆盖。

- **没有适用的生产模式套件：** 使用项目的包管理器和测试约定在 **`rig-template.md`** 中设置生产模式 rig。这是测试支持的采用的一部分，并且不需要用户存在。

- **Rig 无法可靠运行：** 通过 **`rig-template.md`** 设置和活动检查工作。仅在存储库无法解决具体障碍时才回退到手动保留，例如不可用的凭证或无法访问的生产环境。记录障碍和延迟的测试覆盖范围；不要声称测试支持的验证。

不需要用户输入来重用现有套件或创建 rig。仅在存储库无法回答环境问题或目标 UI 本身是产品决策时才询问。如果没有用户可用，请使用指南的安全产品默认值，并将手动验证保留给具体的 rig 障碍。将新的预取 UI 视为步骤 7 的工作；在采用后单独验证任何故意移除的内容。

此工作流程是针对单击的 `<Link>`。例如 `router.prefetch('/dashboard')` 的直接调用是手动预取，而不是 Link 预取；将其保留在源审计中，并在步骤 6 中单独验证。

## 步骤 2：捕获遗留基线

在此步骤期间，不要启用 `partialPrefetching` 或编辑路由行为、Link 属性或缓存边界。允许运行 `instant()` 所需的仅用于测试的配置。

对于基于测试的保留，完成 [保留门](#preservation-gate)：编写完整的 `instant()` 套件并 **运行** 它针对生产类似 rig，禁用部分预取。测试文件、构建、完成的导航或为用户打印的命令不是基线。在套件实际上通过之前，不要继续到步骤 3。

对于手动保留，在编辑任何目的地之前完成目标/目标清单。仅在通过 `rig-template.md` 确定具体 rig 障碍时才回退到此路径，并记录障碍和延迟的测试。

## 步骤 3：采用目的地并恢复目标

使用临时路线配置采用每个审计的目的地。路线导出足以在全局标志保持关闭时让未更改的测试在该目的地上执行部分预取：

```tsx
// 参考：https://nextjs.org/docs/app/guides/adopting-partial-prefetching
export const prefetch = 'partial'
```

如果其他 URL 特定 UI 可能值得预取，但不是遗留合同的一部分，请在其链接上保持 `prefetch={true}` 并标记该路线为步骤 7：

```tsx
// TODO(per-link-prefetch): 与用户评估是否应在点击之前解析 URL 数据。
// 参考：https://nextjs.org/docs/app/guides/optimizing-prefetching
export const prefetch = 'partial'
```

使用该确切前缀，以便步骤 7 可以grep它们回来。不要现在选择新的目标 UI；仅恢复从遗留行为中选择的目标。

对于基于测试的保留，在每个目的地更改后重新运行受影响的 **未更改** 测试，并将失败视为工作队列。在启用全局标志之前，运行完整套件并记录其通过退出状态。对于手动保留，将采用的生产导航与选定的目标进行比较并记录尚未恢复的内容。应用指南的匹配保留模式来处理缓存和 Link 属性更改，并在做出不明确的 freshness 或缓存决定之前询问用户。上面标记的新的 URL-data 候选者等待步骤 7。

当恢复的目标更改缓存或失效时，请遵循项目的现有验证方法以及 [重新验证](https://nextjs.org/docs/app/getting-started/revalidating) 指南。重用或扩展适用于受影响生命周期的适用套件。如果项目不测试此类型的行为，则不要在采用期间引入新的测试基础设施；在生产中手动验证它并记录预期和观察到的结果。绿色的 `instant()` 测试证明就绪，而不是缓存正确性。仅在预期行为不明确时才询问用户。

> **如果你添加 `use cache`，请在 `next start` 下验证，而不仅仅是构建。** 在缓存的调用树中的任何地方读取 `cookies()`/`headers()`/session 都会在请求时抛出错误，而 `next build` 会干净通过。参考 [`use cache`](https://nextjs.org/docs/app/api-reference/directives/use-cache)。

## 步骤 4：启用标志

一旦每个审计的目的地都有 `prefetch = 'partial'`，就完成两步。

1. **全局启用标志。** 在 `next.config.ts` 中设置 `partialPrefetching: true`（与 `cacheComponents: true` 一起）。现在每个路由都已采用，所以每个链接都是好的。
2. **删除冗余的 `prefetch = 'partial'` 导出。** 运行第一方的 `remove-partial-prefetch` codemod，而不是文本查找和替换。它删除每个 `export const prefetch = 'partial'`，包括在 `TODO(per-link-prefetch)` 标记下方的导出，并删除其生成的部分预取指南评论。TODO 标记及其优化预取指南链接保留为步骤 7。其他值，如 `prefetch = 'force-disabled'`，仍然保留在原位。

   ```bash
   npx @next/codemod@canary remove-partial-prefetch ./app
   ```

   在 `src/` 项目中使用 `./src/app` 并检查报告的文件数。Codemod 拒绝在脏工作树中运行。首先提交或暂存无关的工作，或者传递 `--force` 以让其编辑与你的 WIP 一起提交。如果 codemod 不可用（较旧的 `@next/codemod`、沙盒环境、离线运行），通过手动删除每个 `app/**/{page,layout}.{js,jsx,ts,tsx}` 中的 `export const prefetch = 'partial'` 和其生成的部分预取指南评论来重现它——保留其他 `prefetch` 值，并保留 `TODO(per-link-prefetch)` 标记和优化预取指南链接在它们原来的位置。当 codemod 可以运行时，不要手动编辑。

启用标志和 codemod 一起到达后，如果使用基于测试的路径，请重新运行锁定的保留套件。否则，在最终全局配置下重复记录的生产比较。

## 步骤 5：扫描 URL-data 洞察（启用后）

这是一个仅限开发的第二遍。外壳检查仅在标志开启时运行，在导航时触发，并且永远不会阻止构建，因此它可以在步骤 4 之后随时发生。从具体来源（最后一个 `next build` 路由表或 `app/` 树）构建路线队列，并将其保留为待办事项列表。

逐功能扫描。功能是一个单个产品表面——`app/settings/**`、`app/posts/[slug]/**`——而不是一个顶层区域。完成一个端到端之前，再开始下一个：在 `next dev` 中加载其路由并解析它们的洞察。洞察永远不会阻止构建，每个路由都是独立的，因此部分扫描会留下可工作的应用程序，每个功能都是用户可以自行审查或发布的自包含更改。

如果环境无法完成整个扫描（缓慢的第一编译、在负载下崩溃的开发服务器、完全没有浏览器），请在交出之前尽可能多地完成浏览器无关的工作。采用所有可以静态化的路由：应用来自 [`URL data`](https://nextjs.org/docs/messages/instant-shell-url-data) 的修复，直到新的 `<Suspense>` 边界，依赖于类型检查。一次通过整个队列——更大的重构不是推迟的原因，并且询问是否继续到下一个路由或层级不是检查点；继续前进。只有在进行真正的判断时才停止，并将它们批量到单个交出报告中：您可以静态采用的路由、仍然需要实时外壳检查的路由和队列。

观察洞察选项卡和开发日志中的 `Next.js encountered … data` 行。此步骤添加的信号是 [`URL data`](https://nextjs.org/docs/messages/instant-shell-url-data)：在挂起的子树中位置过高的 `params` 或 `searchParams` 读取将共享外壳绑定到一个 URL。此洞察很窄；它最可靠地出现在 `generateStaticParams` 路由中，其中 `params` 已经在 `<Suspense>` 下，但在 URL 特定叶边界之前仍然等待。如果触发 `blocking-prerender-*` 错误，请应用相同的结构性修复。

加载带有标志的路线会预取其应用程序外壳，这比缓存组件构建验证了更多路由。因此，在缓存组件构建中干净构建的路由（每个路由 `◐`，没有错误）仍然可能在此处第一次其外壳被预取时触发 `blocking-prerender-*` 错误——[`runtime data`](https://nextjs.org/docs/messages/blocking-prerender-runtime) (`cookies()`/`headers()`), [`uncached data`](https://nextjs.org/docs/messages/blocking-prerender-dynamic) (未缓存的 `fetch`/DB 调用), 或同步 IO 如 `Date.now()`/`new Date()`。这并不意味着缓存组件采用不完整；这是新的验证达到了构建从未执行的路径。这些不是部分预取洞察——像任何阻塞预渲染错误一样修复每个错误。

这些修复很少涉及用户——每个洞察都命名了冒犯性的读取，并且它的文档页面有修复，所以应用它并继续扫描。收集罕见的例外，以便在最后批量提问：一个完全由 URL 依赖区域组成的页面（将其全部包装后留下一个空外壳），或者一个应该保留在禁用状态的路由。不要用注释来描述重构——`<Suspense>` 边界会为自己说话。

## 验证

与用户确认之前的清单：

- **当缓存组件采用干净完成时，预期空扫描。** 安静的日志是成功，而不是缺少信号。如果你故意探测验证路径，请使用一个 `generateStaticParams` 路由，其中 `params` 在 `<Suspense>` 内读取，但在 URL 特定叶边界之前，其他形状可能会触发 `blocking-prerender-*` 而不是。
- 应用程序外壳是真实的：对于每个您更改的路由，请确认在导航后的第一次绘制显示预期的共享内容，而不是空外壳或卡住的回退。整个页面主体周围的 `<Suspense>` 通过空外壳验证，这违背了目的。
- 洞察验证外壳 _结构_，而不是预取实际上是否发生。在运行中确认（自动预取仅在运行中运行）导航到更改的链接会立即显示共享外壳。
- 对于基于测试的保留，针对每个审计的 `<Link prefetch={true}>` 的每个锁定 `instant()` 测试在生产运行中通过。对于手动保留，记录了目标/目标清单和任何延迟的测试后续处理。
- 在通过任何可以更新其数据的任何新或扩展缓存后，变异检查通过适用的现有测试套件或记录的手动检查来验证下一次通过适用现有测试套件或记录的手动检查（当项目没有此类覆盖范围时）。
- **如果应用程序强制执行显式预取**，洞察扫描不涵盖它，所以空扫描不是证明预取在标志下存活的证据。在 `next start` 下验证调用：比较 `_rsc` 预取响应或资源时间线，并在之后确保任何有意保留的完整预取仍然携带旧调用正在温暖的数据。如果现在只返回应用程序外壳，请使用最近的 `<Link prefetch={true}>` 目的地相同的决策来迁移该调用位置——缓存数据，或将逐链接预取行为移动到受支持的 `<Link prefetch={true}>`。
- **在将损坏的路由归咎于标志之前**，使用 `partialPrefetching` 关闭（或在启用标志前的分支）重现已知问题。标志会提前并更明显地暴露现有问题——一个易碎的请求时身份验证网关、重写、部署偏差——但很少导致它们。如果它在关闭时也损坏，则它不是部分预取问题；在别处修复它，而不是在这里。
- `next build` 仍然通过。

然后与用户确认。用他们的语言——不要洞察符号或步骤标签。

- 你做了什么：你审计了哪些链接，你采用了哪些目的地，以及每个链接现在预取什么。
- 发生了什么变化：删除的属性、添加的 `use cache` 边界，以及哪些路由带有 `TODO(per-link-prefetch)` 标记以供以后考虑。
- 对生产运行进行演示。自动预取仅在运行中运行，所以 `next dev` 不会显示结果——运行 `next build` 和 `next start`，并将用户传递给该 URL。该运行需要应用程序的真实环境（数据库、身份验证、密钥），并且部分或陈旧的安装或剩余生成的工件可能会因与采用无关的原因而失败构建。事先设定预期，验证是一个完整的、有凭证的生产运行，而不是快速检查。
- 显示，不要告诉：在头部浏览器中针对生产服务器驾驶一个链接，以便他们看到共享的应用程序外壳立即绘制，URL 特定区域流式传输。仅在无法使用头部浏览器时才附加前后截图。
- 给他们点击体验：一个更改路由的表格——点击的链接，以及点击后会发生什么（什么会立即绘制，什么会流式传输）——以便他们可以自行验证每个结果。
- 问题：“在我们查看哪些路由也应该预取其 URL 特定内容之前，你想提交这个（或打开 PR）吗？” 等待答案——采用和逐链接预取读起来最好作为他们自己的更改。

## 步骤 7：逐链接预取（可选）

审计标记了超出已采用遗留合同候选者的内容，而不是决定它们。grep `TODO(per-link-prefetch)` 并与用户在一次对话中步行该列表。每个路由的问题是他们是否希望点击之前预取额外的 URL 依赖内容，还是导航后流式传输可以。逐链接预取每条可预取的链接都会导致一次服务器调用——指南的 [权衡](https://nextjs.org/docs/app/guides/optimizing-prefetching#trade-offs) 部分是清单。不要独自做出这些调用。

对于回答“不”的情况，删除标记并将该路由保留在应用程序外壳默认设置下。对于回答“是”的情况，请遵循 [优化预取指南](https://nextjs.org/docs/app/guides/optimizing-prefetching)，在生产运行中确认选定的链接，并在验证选定结果后删除标记。

没有 `TODO(per-link-prefetch)` 标记在完成步骤后幸存。逐链接优化仍然是与采用分离的单独提交或 PR。最后，显示任何有效的 `prefetch={false}` 链接在一个简洁的 `Navigation | 为什么它可能不再需要` 表格中。解释 `false` 禁用所有预取，而部分预取的默认 `auto` 行为仅预取共享的应用程序外壳，所以添加的禁用可能现在不再需要。邀请用户单独重新审视它们。
