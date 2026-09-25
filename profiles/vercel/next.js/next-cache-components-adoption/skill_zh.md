# next-cache-components-adoption

在应用中启用缓存组件，并将其引导至通过构建。这项技能按顺序执行工作；每个错误的具体解决方案存在于开发覆盖层的修复卡片和构建的终端输出中。[迁移至缓存组件指南](https://nextjs.org/docs/app/guides/migrating-to-cache-components)是本技能应用的概念和每个API解决方案的权威参考——当技能步骤引用模式（`"use cache"`，`cacheLife`，`<Suspense>`放置等）并希望获得完整解释时，请参考它。

## requires

- **App Router项目。** 缓存组件是App Router的功能；`cacheComponents: true`对`pages/`路由无作用。如果项目有`pages/`或`src/pages/`树但没有`app/`或`src/app/`树，请停止并告知用户——页面到App的迁移是一个独立的项目，不是本技能的一部分。混合应用（同时有`pages/`和`app/`）是没问题的：该标志影响`app/`路由；`pages/`路由不受影响，也不需要选择退出。

- **一个已解析的应用目录。** 首先定位`next.config.{js,ts,mjs,cjs}`：那是项目根目录，从子目录调用的代理否则会针对错误的`cwd`测试`app/`并找到 nothing。在它下面查找`app/`和`src/app/`，并将本技能中的每个命令和glob视为相对于存在的目录。如果两者都存在，Next.js构建`app/`并从不查看`src/app/`，所以它的路由被阴影且未构建——告知用户这一点，并询问要迁移哪个树而不是选择一个。

- **一个可运行的应用。** 整个循环验证`next dev`和浏览器，所以应用必须启动。如果它在导入时读取数据库或必需的环境（例如一个在缺少`DATABASE_URL`时抛出错误的`env.ts`），请在第一步之前确认它确实启动——使用真实环境或您自己设置的本地数据——然后才能进行步骤1。迁移无法针对无法运行的应用进行验证。

- **Next.js 16.3或更高版本。** 该版本是本技能依赖的组件的发布点：顶层`cacheComponents`，`export const instant`，开发覆盖层即时导航验证警告，以及`cache-components-instant-false`代码修改器。如果`next --version`报告低于16.3，请先升级：
  - `npx @next/codemod@latest upgrade latest`应用版本到版本的代码修改器。
  - 阅读相关的[版本升级指南](https://nextjs.org/docs/app/guides/upgrading)（例如[版本16](https://nextjs.org/docs/app/guides/upgrading/version-16))了解代码修改器未涵盖的内容。

- **没有不兼容的配置键。** `cacheComponents: true`在任何仍然导出`dynamic`，`revalidate`或`fetchCache`的文件上出错。在运行代码修改器之前，清点这些导出，然后遵循[迁移指南的每个键部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components)。该指南是翻译每个值的权威来源。`cache-components-instant-false`代码修改器不会删除这些配置。

- **`experimental.dynamicIO`是致命的。** 它被重命名为顶层`cacheComponents`，旧键在任何构建运行之前都会中止——首先删除它（或用`cacheComponents: true`替换）。`experimental.useCache`仍然被接受为已弃用的别名；一旦`cacheComponents: true`被设置，它就是冗余的，所以请删除它以供清晰。

### notes

- **标志之前没有通过的基线。** 如果应用已经使用`"use cache"`，则标志之前的构建会因`please enable the feature flag cacheComponents`而报错。启用标志是您首先做的事情（在Incremental中，在代码修改器之前；在Direct中，在修复路由之前）——不是在获得通过构建之后做的事情。在您的起始摘要中注意这一点，以免它看起来像是一个回归。

- **现有的缓存可以保留。** 遵循迁移指南的[`fetch`和`unstable_cache`部分](https://nextjs.org/docs/app/guides/migrating-to-cache-components#fetch-cache-options)。不要仅仅为了启用缓存组件而重写它们。

- **离线文档。** 指南链接在`node_modules/next/dist/docs/`下有离线副本（自Next.js 16.2以来捆绑），目录布局按顺序编号（例如`node_modules/next/dist/docs/01-app/02-guides/migrating-to-cache-components.md`）。如果您无法预测编号前缀，`find node_modules/next/dist/docs -name '<slug>.md'`可以解决它。`/docs/messages/*`错误页面没有捆绑。

- **较旧版本没有捆绑文档。** 建议用户在开始之前运行`npx @next/codemod@latest agents-md`：它下载与版本匹配的副本到`.next-docs/`并写入`AGENTS.md` / `CLAUDE.md`中的索引。它会修改它们仓库中的文件，所以请先询问，只有在他们想要它时才运行。

## the shape of the work

有一个循环：自上而下遍历路由树，一次一个功能，针对`next dev` + 浏览器采用每个路由。构建是每个功能的最终检查，而不是工作表面。

第一步的选择是是否首先选择退出每个路由的验证，还是边修复路由边进行。无论哪种方式，循环都是相同的：

- **使用安静的预步骤（Incremental）。** 运行代码修改器，修复它无法修复的内容，并完全迁移之前需要静态渲染的路由。其他路由保留它们的选择退出，以便后续的PR处理。
- **不使用（Direct）。** 启用`cacheComponents`并从构建标记的第一个路由开始循环。相同的循环，但每个修复都位于一个分支上，直到采用完成。

在两者中，每个路由的成功条形图都是相同的：**dev循环报告没有错误并且`next build`通过**。在每次功能后与用户确认，并建议提交，但未经他们确认绝不提交。预期大部分时间都在循环中，而不是在预步骤中。

## background

`cacheComponents: true`要求每个路由都是可预渲染的。一个在`<Suspense>`之外读取请求时间数据的路由是“阻塞”的，并且会失败构建。`export const instant = false`将路由标记为允许阻塞，这会清除开发中和构建中的阻塞；在布局中，它在构建期间覆盖整个子树，但客户端导航仍然单独验证每个子段。包裹在`["use cache"]`函数中的读取计为缓存边界，而不是阻塞读取。

当修复引入`"use cache"`时，请遵循缓存指南以[选择数据级别或UI级别的边界并设置其生命周期](https://nextjs.org/docs/app/getting-started/caching#usage)以及[在变异后重新验证](https://nextjs.org/docs/app/getting-started/revalidating)。当结果因参数或捕获值而变化时，使用`["use cache"]`缓存键参考[https://nextjs.org/docs/app/api-reference/directives/use-cache#cache-keys]。

出现三种类型的阻止器，通常按此顺序出现：

每当修复引入`<Suspense>`时，请遵循流指南的[粒度流模式](https://nextjs.org/docs/app/guides/streaming#granular-streaming-with-suspense)和[防止CLS的指导](https://nextjs.org/docs/app/guides/streaming#cls-cumulative-layout-shift)。

1. **请求时间读取** (`cookies()`，`headers()`，`await params`，`await searchParams`)。当在页面或布局的顶部等待时，所有四个都会阻塞。`params`和`searchParams`经常被遗漏，因为它们不像cookies和headers那样被框定为“请求数据”。修复方法是将读取推入一个用`<Suspense>`包装的子组件——对于`params`/`searchParams`，将Promise转发到子组件并在那里等待它；不要在页面顶部等待。

2. **模块/渲染时间的同步IO** (`new Date()`，`Date.now()`，`Math.random()`，`crypto.randomUUID()`)。即使`instant = false`，这些也会导致构建失败——选择退出不会抑制它们。如果它们在共享布局中，它们会阻塞该布局下的所有路由。代码修改器无法修复它们；在运行它之后，使用构建输出中的路由、原始文件和行以及`/docs/messages/`链接来定位错误。如果需要，在整个仓库中grep `new Date()`，`Date.now()`，`Math.random()`和`crypto.randomUUID()`（不仅仅是`app/**/layout.{js,jsx,ts,tsx}`——读取可能存在于任何导入的布局组件中）。不要更改未报告的匹配项。应用链接的错误页面上的适当选项，然后在引入的边界上方添加此评论，该边界仅用于解除构建阻塞：

   ```tsx
   // TODO: Cache Components adoption. Added to unblock the build: remove this boundary to re-trigger the error and review the documented options.
   ```

   它与代码修改器写入的评论共享`TODO: Cache Components adoption`前缀，因此可以在检查时找到它们。删除边界会使错误再次出现，并显示其修复卡片——这与在循环中删除选择退出相同。

每次修复后，当可用时，重新运行作用域构建，然后再次运行`next build`以找到下一个阻止器。重复直到正常构建通过。

构建通过后，确认每个延迟的路由仍然被选择退出覆盖，并且没有共享选择退出覆盖之前静态的路由。如果应用没有之前的静态路由，并且根布局仍然延迟，请确认它获得了选择退出（使用`grep -n "export const instant" <app dir>/layout.*`手动添加`export const instant = false`到它）。根布局渲染每个路由，包括框架路由如`/_not-found`，所以如果它被遗漏，请手动向其添加`export const instant = false`。

合成路由如`/_not-found`没有用户文件——当它们阻塞时，修复根布局的选择退出，而不是合成路由。客户端组件（`"use client"`）不会获得选择退出（从它们导出`instant`是构建错误），但它们不是罕见的阻止器。高频情况是一个客户端组件在根布局的导航或页眉中调用`usePathname()`/`useSearchParams()`：它阻塞每个动态路由使用`blocking-prerender-client-hook`，而静态路由通过（路径名在预渲染时已知），这会掩盖它直到你到达动态段。这不是祖先数据修复——请遵循[错误的文档页面](https://nextjs.org/docs/messages/blocking-prerender-client-hook)以获取`<Suspense>`配方。只有当客户端路由在服务器数据上阻塞时，你才需要在其祖先中修复该数据。

### end of the pre-step: check in

Incremental only. 预步骤是可发布的PR。在开始步骤2的循环之前，记录通过检查点。除非用户已经要求你在同一任务中继续完成完整迁移，否则请停止并检查。用用户的语言与他们交谈；不要说“Incremental”或其他内部标签；谈论采用、PR以及应用现在做什么。告诉他们：

- 你做了什么：启用了缓存组件，运行了代码修改器，迁移了之前静态的路由，修复了剩余的阻止器，并确认构建通过。
- 发生了什么变化：之前静态的路由仍然预渲染。其他页面和布局保留`// TODO: Cache Components adoption`选择退出。
- 需要检查什么：之前静态的路由保持完全预渲染和可预取，并且延迟路由上的请求特定数据仍然是请求特定的。
- 问题：在开始逐路由采用缓存组件之前，是否想将此内容作为单独的PR打开？还是继续在此分支上工作？等待答案。

如果用户已经要求你完成迁移，则在记录此检查点后继续，而不是再次询问相同的问题。

### direct

设置`cacheComponents: true`并移动到[步骤2](#step-2-the-inner-loop-remove-opt-outs-one-feature-at-a-time)。构建的阻止路由是工作队列。

## step 2: the inner loop, remove opt-outs one feature at a time

一个“功能”是一个单个产品表面——`app/settings/profile/**`，`app/posts/[slug]/**`——而不是像`app/dashboard/**`这样的整个顶层应用。完成一个端到端，然后再开始下一个。

在一个功能内，自上而下遍历（布局在页面之前，首先根布局）。在移除布局的选择退出之前，会暴露布局自己的阻止读取。 (Direct: 没有选择退出要移除——修复每个失败的路由；如果一个手写的祖先选择退出阴影它，请先移除那个。)

在遍历过程中通过构建通过并不意味着布局是干净的。在移除布局的选择退出时，如果其子代页面仍然有它们的选择退出，构建仍然通过——每个页面阴影继承的验证。布局的实际阻止读取只有在没有任何东西阴影它们时才会出现。不要在布局边界调用功能完成。

使用**带浏览器的循环**（首选），除非浏览器确实无法访问。`[next-dev-loop](#verifying-each-fix-at-runtime)`技能是“浏览器可用”和如何安装它的权威来源。

### the loop, with a browser (preferred)

每个路由：

- 移除选择退出（Incremental）或针对失败的路由（Direct）。
- 在dev中重新加载。覆盖干净？跳过验证。覆盖仍然为红色？修复。
- 修复——获取从错误链接的文档页面（`https://nextjs.org/docs/messages/<slug>`），在那里应用那里的配方。内联覆盖文本是摘要；文档页面是权威来源。
- 在浏览器中验证。确认第一帧的可见内容是您在壳中预期的——不是卡在回退上，不是默默地从空壳中流式传输所有内容。
- 如果修复触及共享代码（布局、侧边栏组件），请重新检查兄弟节点。共享壳更改可以修复您当前所在的路线，但可能会破坏兄弟节点。

### the loop, build-only (fallback)

在没有办法驱动浏览器的情况下使用——CI、沙盒、用户没有运行`next dev`并且您无法启动一个——使用较弱的信号：确认构建通过并且路由预渲染，但不是什么最终进入了静态壳与流式传输。

每个路由：

- 移除选择退出（Incremental）或针对失败的路由（Direct）。
- 使用`--debug-build-paths app/<route>/**`（仅该路由）或`--debug-prerender`（完整构建，但越过第一个失败）。路由通过？继续。仍然阻止？修复。
- 修复——获取从错误链接的文档页面（`https://nextjs.org/docs/messages/<slug>`），在那里应用那里的配方。
- 如果修复触及共享代码，请重新检查。
- 当您将里程碑交给用户时，将路由标记为仅构建验证。每个`◐`路由在功能完成之前仍然需要浏览器通过。

### loop notes

- 来自背景的[三种阻止器类别](#background)在就地修复时经常被遗漏。缓存下游的`fetch` (`getThing(id)`) 不会清除页面正文顶部的`await params`——将参数Promise推入用`<Suspense>`包装的子组件。
- 模糊调用是用户检查，而不是代理判断。当您不确定哪个修复适合时，阻止代码看起来像安全敏感的，或者用户可能希望路由保持阻止，——在编辑之前，请阅读[参考资料/每页决策.md](./references/per-page-decisions.md)。在询问时显示路由：`next-dev-loop`会话运行浏览器头部，所以驱动到页面并留在屏幕上，以便用户正在查看他们正在决定的事情，如果无法驱动头部浏览器，则使用屏幕截图作为备用。"这个应该保持阻止吗？"在查看页面而不是文件路径时更容易回答。

- 不要用注释来叙述重构。代码修改器（或您）应该留下的唯一评论是在选择退出上`// TODO: Cache Components adoption`，以及用户现有的评论。不要用注释标注每个`<Suspense>`边界或`"use cache"`调用所做的工作——代码本身说明了这一点。只有在代码中不清楚的“原因”时才添加评论（例如，一个有原因的阻止）。

对于具有相同机械修复的许多路由，首先验证一个代表性路由。然后使用相同的配方批量处理不相关的路由组，并一起运行共享构建和浏览器检查。

保留功能路由的待办事项列表。当功能中的每个路由都干净时，移动到步骤3。

## step 3: verify the feature

与用户确认之前的检查清单：

- `next build`完成而没有阻止路由错误。
- 功能中没有裸`TODO`：`grep -rn "TODO: Cache Components adoption"`找到代码修改器的选择退出评论和预步骤中的同步IO解除阻塞。任何留下的`instant = false`是一个故意记录的阻止——评论已重写为原因（参见[参考资料/每页决策.md](./references/per-page-decisions.md) →“何时保留阻止”）。任何留下的`await io()`或`await connection()`都是经过审查并故意保留的，而不是预步骤中遗留的。
- 在浏览器中访问的每个路由：确认静态壳首先渲染，并且每个`<Suspense>`回退都解析为其真实内容。如果可以，捕获这两种状态——回退（流式传输）和最终绘制——以便您有一个流式传输体验演示给用户。如果在浏览器中限制网络速度，如果流式传输太快无法观察。

- 在填充任何其数据可以更新的新缓存后，变异检查确认下次读取返回预期数据。

- 如果运行时验证失败，请在预采用分支或恢复其选择退出时重现相同路由。一个已经存在的失败是环境或数据问题，而不是采用回归。

然后与用户确认。与预步骤相同的规则：用他们的语言说话。不要说“功能逐功能循环”或其他内部标签；谈论您采用的功能以及用户将看到什么。

- 你做了什么：你触摸了哪些路由，以及每个路由的用户可见结果（例如，“帖子页面现在在骨架后面流式传输文章正文，而布局保持静态”）。
- 发生了什么变化：移除选择退出，添加回退，引入缓存边界。
- 展示，不要告诉。`next-dev-loop`会话运行浏览器头部，所以驱动路由对用户生效，以便他们实时看到静态壳→回退→最终内容序列。如果您无法驱动实时浏览器，请附加您捕获的屏幕截图。

- 给他们点击体验：一个短表，列出功能的路由——打开的URL和要查找的内容（什么立即渲染，哪些回退出现，什么流式传输）——以便他们可以自己验证每个路由。

- 问题：“想将此功能作为PR并继续下一个，还是在这里停止？”等待答案。

**简单的功能可以跳过检查入站。** 如果采用功能仅意味着删除其`// TODO: Cache Components adoption`选择退出（没有添加`<Suspense>`，没有引入`'use cache'`，没有渲染顺序更改），用户看不到任何不同。继续下一个功能而无需停止；下次检查入站时提及它。

当循环运行在所有功能上时——每个剩余的`instant = false`位于一个原因评论下，`grep -rln "TODO: Cache Components adoption" app`返回空——如果用户想要将体验推进得更远，请指向[进一步阅读](#further-reading)，或者停止并发布。

### route table glyphs

`ƒ` → `◐`是采用通常到达的地方。`◐ (部分预渲染)`意味着静态壳预渲染，请求时间内容流式传输——任何读取`cookies()`，`headers()`，`params`或`searchParams`的路由的目标状态。有些路由在文档中确实保持`ƒ`，因为它们通过文档中的逃生舱口进行请求时间工作（例如，一个使用`await connection()`的布局）；页面不再被选择退出，而是真正动态的。不要只为了追逐`◐`而删除逃生舱口。反过来也是如此：`instant = false`不会强制路由为`ƒ`。符号反映了路由在预渲染时的行为，而不是它导出的验证旋钮。

`◐`告诉您存在一个壳，而不是壳中有什么。放置`<Suspense>`边界位置过高（例如，包装整个页面正文，或`<Suspense fallback={null}>`围绕文章内容）将可见内容从静态壳推到流式传输的有效负载；构建仍然报告`◐`，因为_某些_壳预渲染了（通常只有`<html><body>`与框架标记）。路由表无法告诉您壳中有什么，浏览器可以。如果壳为空并且所有内容都流式传输，请将`<Suspense>`边界移到更靠近实际动态读取的位置。
