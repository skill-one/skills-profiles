---
name: next-cache-components-optimizer
description: 通过设置代理循环，在“缓存组件/预渲染页面”下，将 Next.js 路由驱动至即时导航，适用于初始加载（硬导航）和客户端导航（软导航）。将目标编码为失败的 @next/playwright instant() 端到端测试，逐个验证路由，直至变为绿色；发布的测试将防止回归。在以下情况下使用：要求使路由导航即时（其静态外壳立即提交）、修复未预渲染/服务/预取的静态外壳的路由、扩展路由的静态外壳或修复其缓慢的首屏渲染、诊断哪个 Suspense 边界使路由无法进入其静态外壳，或为其中一个编写 instant() 端到端测试。需要 Next.js 16.3+ 及 cacheComponents；若版本较旧，将引导升级。
---

# next-cache-components-optimizer

设置一个代理优化循环，驱动 Next.js 路径从“非即时”变为“即时”，并保持其状态。该循环是测试驱动的：将目标编码为失败的 `@next/playwright` `instant()` 测试，将其修正为绿色，并将测试作为回归保护措施发布。针对每个目标路径运行一次。按顺序工作 P → G 阶段；每个阶段都以一个门控结束。修正配方存储在两个懒惰读取的引用中——`reference/patterns.md`（每个阻塞器类型的“之前→之后”）和 `reference/real-app-patterns.md`（并行路径、认证门控、空壳和响应式骨架失败模式）。仅在阶段指向它时才读取其中一个。

## 不变的是什么，什么是你的

这里有一件固定的事情。其余的都是你的。在处理以下任何命令、平台或环境变量之前，请先阅读此内容，将其视为要求。

- **不变：验证循环。** 除非你能证明它，否则最大化外壳是无用的。证明是一个自动检查：在锁定动态数据的情况下，静态外壳仍然提交。RED 显示差距，GREEN 显示已关闭，测试作为回归保护措施发布。它必须在类似生产的构建上运行，并且不能空泛地通过。一旦建立循环，后续的每个优化都可以通过构造进行验证。循环是交付成果，而不是任何单个路径。

- **机制：`@next/playwright` `instant()`。** 这个技能使用 [`instant()`](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) 作为标尺，而不是秒表（阶段 A）。它来自 `@next/playwright`（与 `@playwright/test` 一起安装，与 `next` 同一发布线），因此它不依赖于任何主机。保留它。手动计时导航太不可靠，无法信任，而这个技能的存在就是为了防止这种失败模式。

- **你的：装置。** 你如何构建、部署、认证、配置 Playwright 以及循环属于你的堆栈，而不是这个技能。本地 `next build && next start`、CI/阶段容器以及每次推送的预览部署都是同样有效的装置；裁决来自构建，而不是平台。阶段 0 将不变量映射到你的存储库。将下面的每个平台名称、环境变量拼写和命令都视为翻译示例，而不是要求。

## 两种导航，两种加载状态

路径通过两种方式到达用户，并且都必须是即时的：

- **初始加载（硬导航）** 提交路径的预渲染静态外壳；延迟部分在其加载骨架（Suspense 回退、`loading.tsx`）后面流式传输。
- **客户端导航（软导航）** 提交目标预取的应用外壳——在部分预取下 `<Link>` 的默认值——仅重新渲染更改的部分。

两种修复模式是相同的；测试仅在导航驱动方式上有所不同（“在测试中驱动导航”下）。两个外壳可以不同；保护你发布的那个，当两者都重要时（`reference/real-app-patterns.md`）。

## 目标

最大化静态外壳是优化目标：最有意义的预渲染内容立即提交，并且只有真实的请求数据随后流式传输。发布的测试确定性地编码 **存在 ∧ 即时**；**非空白** 是工作流通过判断（D1/D2/E）强制的附加标准，因为单独的 `instant()` 通过仅被空白 `fallback={null}` 外壳（空壳失败模式，`reference/real-app-patterns.md`）满足。

`instant()` 是标尺，不是秒表：断言外壳在锁定下出现；不要计时。可信赖的裁决需要一个生产构建（阶段 A）。

锁定下的 GREEN 是确定性裁决；每个门控都保持其可信赖性。

## 向用户报告

此循环旨在无人值守运行，因此它不会在步骤之间停止询问。处理用户命名的导航，完成它，然后停止。重要的是你如何措辞和展示结果，而不是你如何频繁地中断。下面的机制——装置、RED、GREEN、门控——是你的脚手架；用户永远不会听到这些词。

- **使用他们的语言。** 用用户看到的内容描述差距和结果：“导航到仪表板等待图表查询，然后才绘制任何内容；现在布局和骨架立即绘制，图表随后流式传输”——而不是 RED/GREEN、锁定或阶段字母。

- **展示，而不是讲述。** 当你报告一个路径时，驱动浏览器（或附加之前/之后的截图），以便用户观看外壳立即提交和数据流式传输，而不是阅读断言。之前和之后相同意味着修复没有起作用——回滚它。

- **将运行呈现为用户可以点击的列表结果**——每行一个导航：路径、什么立即提交、什么流式传输——而不是循环的文本记录。

- **仅对真实的分支提出问题**：一个会改变行为的修复、一个安全敏感的读取或一个设计为动态的路径（一个每个链接预取候选者，而不是要增长的外壳）。一个干净的即时修复不是一个分支——继续进行。在没有可以询问的人（无人值守运行）的情况下，不要阻塞：采取安全默认值并注意假设——对于缓存新鲜度选择，将读取延迟在 `<Suspense>` 后面（始终新鲜，仍然即时），而不是猜测 `cacheLife`。

## 工作流

```
- [ ] P  PREREQS      Next.js 16.3+ with cacheComponents: true; upgrade first → below
- [ ] 0  SETUP        once per repo: discover + write instant-nav.rig.md     → rig-template.md
- [ ] A  RIG          production build with the testing API exposed          → below
- [ ] B  BASELINE     unlocked: the marker renders for the test user         → test-template.md
- [ ] C  RED          locked instant(): the shell does not commit            → test-template.md
- [ ] C-gate          VERIFY-RED: stop until the RED is trustworthy          → reference/red-test-robustness.md
- [ ] D  FIX          push each Suspense boundary down to the data it guards → reference/patterns.md
- [ ]      D1 reuse the route's existing loading UI; do not hand-build skeletons
- [ ]      D2 the shell matches the real render at every breakpoint  → reference/real-app-patterns.md
- [ ] E  PARITY       the refactor changed only whether the route is instant
- [ ] F  DIFFERENTIAL revert only the fix → RED; re-apply → GREEN            → reference/red-test-robustness.md
- [ ] G  REVIEW       PR checklist (below)
```

阶段 B 和 C 构建测试；只有来自 C 的锁定测试才发布。

---

## P. 前提条件：当前的 Next.js 与缓存组件

工作流依赖于当前 Next.js 随附的功能：

- **Next.js 16.3+ with `cacheComponents: true`** in `next.config.ts`。没有缓存组件就没有静态外壳可以优化。
- **`@next/playwright`** 在与项目的 `next` 同一发布线上；它提供 `instant()`。使用 `npm ls next @next/playwright`（或项目的包管理器）进行验证，并在它们不同时对齐。匹配的测试 API 在 `next` 运行时中，由 `experimental.exposeTestingApiInProductionBuild` 配置标志（阶段 A）门控。

如果项目不符合这些条件，请先升级（`npx @next/codemod upgrade` 自动化了大部分内容），然后在 `next.config.ts` 中启用缓存组件：

```ts
export default { cacheComponents: true }
```

启用标志会暴露需要首先解决的阻塞路径；`[next-cache-components-adoption](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-adoption)` 技能推动这种采用。一旦应用程序在缓存组件下构建，就使用这个优化器。

这个门控是故意的：该技能针对当前的 Next.js，并且以下所有裁决在旧版本上都没有意义。

## 0. 设置：发现此项目的装置，每个存储库一次

此技能中的原则是固定的；它们运行的底层基础设施是你的。在存储库中首次使用时，发现项目如何构建、部署、认证和测试（首先检查存储库，并且仅在它无法回答的情况下才询问用户），然后将答案写入提交的 `instant-nav.rig.md`。后续运行读取该文件，而不是重新发现。所需的构建、测试上下文、导航合同、迭代循环和文件模板在 **`rig-template.md`** 中。

如果存储库还没有 Playwright e2e 套件，建立最小的套件（`@next/playwright`、一个带有 `baseURL` 的配置和一个认证路径）是此步骤的一部分；循环不假设预存在的套件。

## A. 装置：一个类似生产的构建，测试 API 暴露

建立 `instant-nav.rig.md` 中描述的装置。在所有平台上，两个不变量都成立：

1. **永远不要在 `next dev` 上测量。** 它不会预取，并且其锁定对于阻塞路径是不可靠的，因此开发 `instant()` 结果不是有效的 RED 或 GREEN。
2. **测量的构建必须暴露测试 API。** 否则 `instant()` 沉默地无操作，并且测试空泛地通过（见 `reference/red-test-robustness.md`）。锁定参与证明是阶段 C 的 RED 本身：未修复的目标路径是已知的阻塞路径，并且其锁定下的 RED 显示锁定在此构建上参与（C-gate）；`test-template.md` 中的自验证变体是带内保证。将 `experimental.exposeTestingApiInProductionBuild` 接线到一个对您测量的每个构建都为真且在生产中永远不为真的条件：

   ```ts
   experimental: {
     // 使用您的平台提供的条件，并将其记录在装置文件中：
     //   local:       一个明确的opt-in，如下所示
     //   generic CI:  process.env.DEPLOY_ENV === 'staging'
     //   Vercel:      process.env.VERCEL_ENV === 'preview'
     exposeTestingApiInProductionBuild:
       process.env.EXPOSE_TESTING_API === '1',
   }
   ```

装置是任何类似生产的构建，它暴露了测试 API：本地 `next build && next start`、CI/阶段容器和预览部署都是同样有效的；裁决来自构建，而不是平台。有关设置要求，请参阅 `rig-template.md`。

对于任何已部署或远程构建，轮询装置的 LIVENESS 探针，以确认工件包含 `HEAD`，然后再信任裁决（陈旧的部署读取为假的 RED 或 GREEN）；本地 `next build && next start` 无需任何。探测机制在 `rig-template.md` 中。

## B. 基线（未锁定）：开发框架，不要发布

使用没有 `instant()` 锁定的真实导航，并断言目标 `SHELL_MARKER` 对测试用户渲染：测试套件认证的用户（在 CI 中是 CI 账户；本地是您的 e2e 登录固定装置），及其标志、计划、角色和数据。这建立了标记是真实且可访问的：不是标志门控的，不是重定向的，不是猜测的选择器。套件以测试账户运行，而不是作者的会话；该环境漂移（装置 DRIFT 列表）是不可信赖的 RED 的常见来源。框架和运行命令：**`test-template.md`**。**在 PR 之前删除此基线。**

## C. RED（锁定）+ VERIFY-RED 门控

将相同的导航包装在 `instant()` 中；断言外壳在锁定下提交。这里的 RED 是差距。**这是要发布的测试**
(`test-template.md`)。

当路径有延迟内容时，优先使用自验证变体。如果路径在阻塞时无法构建，或者一个 cookie/会话读取保持 GREEN，请使用 `reference/red-test-robustness.md` 中的 RED 配方。

> **C-gate：在 RED 被验证为可信赖之前不要开始优化。** 一个因为错误原因变红的 RED 会让你优化一个从未出错的路径。

解决它的问题是：**`SHELL_MARKER` 是否在无锁定的测试用户下渲染？** 通过以测试用户身份重新运行阶段 B 来回答它，而不是向发布的测试添加断言。两分支解决（否→标记或环境错误；是→真实差距，继续到 D）、完整的不信赖 RED 分类、检查表和工作案例都在
**`reference/red-test-robustness.md`** 中。现在阅读它。

---

## D. 修复：将每个边界下推到它保护的数据

**反模式：一个粗边界。** 树中高处的单个 `<Suspense>` 与页面级回退有三个成本：

- 布局 UI 停留在静态外壳之外：只有它的可丢弃副本被预渲染。
- 当边界解析时，整个子树被替换，这会丢弃客户端状态并改变布局。
- 手动构建的回退随着 UI 变化而漂移，因为它复制了在解析树中也存在的结构。

**修复：提升静态内容，将 Suspense 下推。** 一次同步、同步地渲染布局 UI 在外壳中，并将每个等待包装在仅限于它保护的单个读取的范围内的边界中。只有该叶子流式传输；稳定的祖先被原样重用。

**规则：** 如果一个元素在回退和解析树中都渲染，将其提升到边界之上。

### 最常见的阻塞器：回退路径上的布局中的顶级 `await`

```
app/[locale]/(app)/[tenant]/dashboard/...
       │ generateStaticParams ✅   │ no generateStaticParams → fallback route
```

当路径中的任何动态段缺少 `generateStaticParams` 时，该路径是一个回退路径，并且**所有**参数都延迟到请求时间，包括枚举的参数。布局中的顶级 `await`（`await params`、请求时间会话读取、认证门控）会阻塞整个子树出静态外壳，即使它读取一个静态已知的参数。最小形状：一个缺少 `generateStaticParams` 的动态段路径，加上它上面的布局中的顶级 `await`。

### 修复：延迟门控，渲染子项

无条件渲染 `children`；将顶级 `await` 放入用 `<Suspense fallback={null}>` 包裹的子项中。机制和之前→之后：
`reference/real-app-patterns.md`，“延迟一个认证门控”。

**同时修复外壳下面的页面，而不仅仅是布局。** 页面级的顶级 `await`（通常 `await params`）与布局的阻塞方式相同，所以使页面同步，并将它的动态读取推入一个用 `<Suspense>` 包裹的叶子中。`fallback={null}` 仅在门控在成功时渲染无内容时正确；对于数据，回退必须是一个真实的加载骨架（见 D1）。

每个其他阻塞器形状——`cookies()`/`headers()`、未缓存的获取或数据库读取、`searchParams`、元数据、视口、非确定性值（`Date.now()`、`Math.random()`、`crypto.randomUUID()`）——当你遇到它时都会揭示自己的见解：构建打印一个 `https://nextjs.org/docs/messages/<slug>` 链接。默认构建输出通常被缩写，可能没有可用的堆栈跟踪；添加 `--debug-prerender` 获取完整的失败帧并报告第一个之后的每个阻塞器。使用 `next build --debug-build-paths "app/<route>/**"` 将构建限制到您所在的路径，而不是重新构建整个应用程序。打开该页面并应用其配方；不要从内联消息中即兴创作。

每个形状之前→之后的配方在 `reference/patterns.md` 中，它将其映射到解释它的见解。

那些每个错误页面没有强调的即时导航目标的一些事情：

- **根布局中的边界不足以客户端导航。** 它通过页面加载检查，但留下兄弟客户端导航阻塞；将边界放在源路径和目标路径共享的最低布局以下。

- **保持 LCP 元素**（通常是主标题）在任何边界之外，以便它在外壳中绘制，而不是等待流式传输。

- **绿色检查不总是即时。** `export const instant = false` 在导航仍然阻塞时将段从验证中排除，并且文档 `<body>` 上面的 `<Suspense>` 预渲染一个空外壳——两者都不会使路径即时。

### D1：重用路径的现有加载 UI；不要手动构建骨架

在编写任何骨架之前，请按顺序在仓库中查找此路由已存在的加载界面：

1. 路由的 `loading.tsx`；
2. 与组件同位的导出的 `*Skeleton`；
3. 组件内部已存在的 `<Suspense>` 中的后备内容。

**分歧点** 是源路由和目标路由共享的最低布局：软导航仅重新渲染其下方的片段，而初始加载会重新运行从根开始的每个布局。（也称为共享边界。）分歧点以上的 `loading.tsx` 仅填充初始加载的外壳；它位于软导航重新渲染的范围内。目标片段中的 `loading.tsx` 本身是进入该片段的树内边界，并服务于两者。重用实际覆盖您正在发布的导航的边界；在分歧点以下，`loading.tsx` 和同位的骨架在此目的上是可互换的。

如果一个组件没有骨架，请将其加载标记提取到其旁边的同位骨架中。不要编写一个镜像页面布局的新骨架：它会重复结构，随着页面的变化而漂移，并将设计拉回到一个单一的粗边界。重用组件自己的骨架还可以使预取的外壳与加载的界面保持一致。

参见：[流式传输](https://nextjs.org/docs/app/guides/streaming#push-dynamic-access-down) 和 [加载状态](https://nextjs.org/docs/app/guides/instant-navigation#iterate-on-loading-states)。

例外：如果延迟组件对某些用户渲染 `null`（例如，一个标志控制），`fallback={null}` 是正确的，因为骨架会闪烁然后消失。

### D2：外壳必须在每个断点处与实际渲染匹配

冻结到单个断点的骨架在其他断点上会错位。以相同的方式修复它：一个响应式组件渲染实时界面和外壳（D1 骨架在其数据槽中），因此断点切换只发生一次。通过在两个宽度处重新断言外壳标记（`await page.setViewportSize({ width: 1280, height: 800 })`，然后 `{ width: 390, height: 844 }`）或通过添加一个移动 Playwright 项目来验证，这样这个门就像其他门一样机器可检查。详情：
`reference/real-app-patterns.md`。

> **D门：当从阶段 C 锁定的测试在生产构建设备上的锁下变为绿色时，阶段 D 才完成**，而不是代码编译时。那个绿色是修复循环的确定性停止；继续进行 E。

如果优化添加或扩展了缓存边界，请遵循
[重新验证](https://nextjs.org/docs/app/getting-started/revalidating)。
一个通过的 `instant()` 测试证明外壳已准备好，而不是突变新鲜。

**当 URL 数据无法推下**（例如，整个页面依赖于 `params`、`searchParams` 或完整 URL）时，可能没有有意义的静态外壳可以增长。不要强迫一个。按链接预取可以使软导航即时，但它不在这个优化循环之外：它需要部分预取、`<Link prefetch={true}>` 和缓存的 URL 相关内容。参见
[优化预取](https://nextjs.org/docs/app/guides/optimizing-prefetching) 和 `reference/patterns.md` 中的模式 10，以了解要求、成本权衡、手动预取注意事项和 `instant()` 测试陷阱。

## E. 平等性：重构仅改变了路由是否即时

下推是一个机械转换，不是重新设计。之后，路由必须渲染与之前相同的树、数据、顺序、空和错误状态、重定向和交互；唯一可观察的差异是外壳现在立即提交。验证：

- **相同的渲染输出。** 移动的 `await`s 计算并返回相同的值；流之后，路由显示与测试用户的基本分支相同的內容。
- **副作用仍然触发。** 延迟的 `redirect()` 或 `notFound()` 仍然发生，但在请求时而不是在预渲染期间。确认未授权用户仍然被重定向，缺少的记录仍然返回 404。
- **两个视口在流之后达到实际界面**（D2）。
- **客户端状态存活。** 因为布局 UI 被提升到稳定的外壳中而不是在解析时交换，所以打开的菜单、滚动位置、焦点和输入状态在流之间保持一致。
- **现有的失败保持分离。** 如果路由在更改后出错，请在基本分支上重现它。在那里相同的失败是环境或数据问题，而不是优化回归。

如果除了路由是否即时之外还有其他任何东西改变了，请减少重构。

## F. 差异

仅还原修复 → RED；重新应用 → GREEN；链接两个运行
(`reference/red-test-robustness.md`)。在一个已部署的设备上，在信任其颜色之前，确认每个运行都是活跃的（LIVENESS，阶段 A）。

## G. 审查（PR 清单）

绿色的最终状态如果 RED 从未值得信任，那就毫无意义。测试可信度项目是稳健性清单
(`reference/red-test-robustness.md`)；确认它们，然后要求这些 PR 特定的项目：

- [ ] **差异显示**：没有修复的 RED，有它的 GREEN，运行链接。
- [ ] **平等性确认 (E)**：相同的内容、重定向和状态。
- [ ] **在适用时验证突变**：在填充任何可以更新的缓存后，突变测试确认下一次读取返回预期数据。
- [ ] **重用现有的加载界面 (D1)**：没有新的镜像页面骨架。
- [ ] **外壳在桌面和移动宽度处与实际渲染匹配 (D2)**。
- [ ] **基线已移除**：只剩下从 C 来的锁定测试。

**整个工作流程的停止条件**：从 C 来的锁定测试在设备上为绿色，差异 (F) 持有，并且上述每个项目都已检查。直到这三个都成立，你才完成。

## 在测试中驱动导航

- **软导航** → 驱动一个真实的 `<Link>` 点击。**初始加载** → 在 `instant()` 内部使用 `baseURL` 选项使用 `page.goto()`。不要用 `goto` 代替软导航的判断；这两个外壳可能不同
  (`test-template.md`，`reference/real-app-patterns.md`)。
- 与并行路由一起，只有更改的插槽在软导航时重新渲染；客户端渲染的导航界面根本不会重新渲染。不要追逐导航从未触及的插槽
  (`reference/real-app-patterns.md`)。

## 文件

- `rig-template.md`：阶段 0 的生产构建、测试上下文、导航合同和无人值守循环发现。
- `test-template.md`：两种导航类型的已发布的 `instant()` 规范（阶段 C），以及 PR 之前删除的基线脚手架（阶段 B）。
- `reference/red-test-robustness.md`：C 门和阶段 F。不可信 RED 的分类、清单、差异配方、空通过失败模式和工作案例。
- `reference/real-app-patterns.md`：并行路由、延迟身份验证门、初始加载与软导航外壳、空外壳失败模式、响应式骨架不匹配、边缘案例。

## 优化后

一旦目标路由变为即时，请检查应用程序是否已经采用部分预取 (`partialPrefetching: true`，或相关目标在增量发布期间仍然使用 `prefetch = 'partial'`)。

机械地执行该检查：

```bash
rg -n "partialPrefetching|prefetch\s*=\s*['\"]partial['\"]" --glob 'next.config.*' --glob 'app/**' --glob 'src/app/**'
```

如果 `partialPrefetching: true` 在配置中，应用程序已全局采用。如果只有 `prefetch = 'partial'` 匹配，请将那些目标片段视为在增量发布期间采用，并继续检查任何其他目标路由。

- **已采用**：对于任何 URL-数据路由，如果停止在上述限制处，请考虑在链接上使用 `<Link prefetch={true}>`，在点击之前准备好该 URL 特定内容值得每条链接的服务器工作。在其他地方保持默认链接行为，以便共享应用外壳仍然是低成本基线。
- **尚未采用**：建议
  [`next-partial-prefetching-adoption`](https://github.com/vercel/next.js/tree/canary/skills/next-partial-prefetching-adoption)。该技能将应用程序移动到更好的预取模型：共享应用外壳默认预取，可见链接的重复完整预取请求更少，对现有 `<Link prefetch={true}>` 使用的链接审计，以及仅在 URL 特定内容值得额外服务器工作时的可选每条链接预取。
