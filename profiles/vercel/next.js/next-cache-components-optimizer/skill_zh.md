# next-cache-components-optimizer

设置一个代理优化循环，驱动 Next.js 路线从“非即时”变为“即时”，并保持其状态。该循环是测试驱动的：将目标编码为失败的 `@next/playwright` `instant()` 测试，将其修正为绿色，并将测试作为回归保护措施发布。针对每个目标路线运行一次。按顺序工作 P → G 阶段；每个阶段都以一个门控结束。修正配方存储在两个懒惰读取的引用中——`reference/patterns.md`（每个阻塞器类型的“之前→之后”）和 `reference/real-app-patterns.md`（并行路线、认证门控、空壳和响应式骨架失败模式）。仅在阶段指向其时才读取其中一个。

## 不变与你的

这里有一项是固定的。其余的都是你的。在将任何命令、平台或环境变量视为要求之前，请先阅读此内容。

- **不变：验证循环。** 除非你能证明它，否则最大化外壳是无用的。证明是一个自动检查：在锁定动态数据的锁下，静态外壳仍然提交。RED 显示差距，GREEN 显示它已关闭，测试作为回归保护措施发布。它必须在类似生产的构建上运行，并且不能空泛地通过。立起循环一次；之后每个优化都可以通过构造进行验证。循环是交付成果，而不是任何单个路线。
- **机制：`@next/playwright` `instant()`。** 此技能使用 [`instant()`](https://nextjs.org/docs/app/guides/instant-navigation#prevent-regressions-with-e2e-tests) 作为标尺，而不是秒表（阶段 A）。它来自 `@next/playwright`（与 `@playwright/test` 一起安装，与 `next` 同一发布线），因此它不依赖于任何主机。保留它。手动测量导航太不可靠，无法信任，这也是此技能存在的目的。
- **你的：装置。** 你如何构建、部署、认证、配置 Playwright 以及循环属于你的堆栈，而不是此技能。本地 `next build && next start`、CI/阶段容器以及每次推送的预览部署都是同样有效的装置；裁决来自构建，而不是平台。阶段 0 将不变量映射到你的存储库。将下面的每个平台名称、环境变量拼写和命令视为翻译示例，而不是要求。

## 两种导航，两种加载状态

路线通过两种方式到达用户，并且都必须是即时的：

- **初始加载（硬导航）** 提交路线的预渲染静态外壳；延迟部分在其加载骨架（Suspense 回退、`loading.tsx`）后面流式传输。
- **客户端导航（软导航）** 提交目标预取的应用外壳——在部分预取下 `<Link>` 的默认值——仅重新渲染更改的片段。

两种修复模式对于两者都是相同的；测试仅在导航驱动方式上有所不同（“在测试中驱动导航”下）。两种外壳可以不同；保护你发布的那个，当两者都重要时（`reference/real-app-patterns.md`）。

## 目标

最大化静态外壳是优化目标：最有意义的预渲染内容立即提交，并且只有真正按请求的数据随后流式传输。发布的测试确定性地编码 **存在 ∧ 即时**；**非空白** 是工作流通过判断（D1/D2/E）强制的额外标准，因为单独的 `instant()` 通过满足空白 `fallback={null}` 外壳（空壳失败模式，`reference/real-app-patterns.md`）。

`instant()` 是标尺，不是秒表：断言外壳在锁下出现；不要计时。可信赖的裁决需要一个生产构建（阶段 A）。

锁下的 GREEN 是确定性裁决；每个门控都保持其可信赖性。

## 向用户报告

此循环旨在无人值守运行，因此它不会在步骤之间停止询问。工作用户命名的导航，完成它，然后停止。重要的是你如何措辞和展示结果，而不是你如何频繁地中断。下面的机制——装置、RED、GREEN、门控——是你的脚手架；用户永远不会听到这些词。

- **使用他们的语言。** 用用户看到的内容描述差距和结果：“导航到仪表板等待图表查询才能绘制任何内容；现在布局和骨架立即绘制，图表流式传输”——而不是 RED/GREEN、锁或阶段字母。
- **展示，而不是讲述。** 当你报告路线时，驱动浏览器（或附加之前/之后的截图），以便用户观看外壳立即提交和数据流式传输，而不是阅读断言。相同之前和之后意味着修复没有起作用——回滚它。
- **将运行呈现为用户可以点击的列表结果**——每行一个导航：路线、什么立即提交、什么流式传输——而不是循环的文本记录。
- **仅对真正的分支提出问题**：一个会改变行为的修复、一个安全敏感的读取或一个设计为动态的路线（一个按链接预取候选者，而不是要增长的外壳）。一个干净的即时修复不是一个分支——继续进行。在没有可以询问的人（无人值守运行）的情况下，不要阻塞：采取安全默认值并注意假设——对于缓存新鲜度选择，在 `<Suspense>` 后面延迟读取（始终新鲜，仍然即时）而不是猜测 `cacheLife`。

## 工作流程

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

阶段 B 和 C 构建测试；仅从 C 发行的锁定测试。

---

## P. 前提条件：当前带有缓存组件的 Next.js

工作流程依赖于与当前 Next.js 一起发布的框架功能：

- **Next.js 16.3+ with `cacheComponents: true`** in `next.config.ts`。没有缓存组件就没有静态外壳可以优化。
- **`@next/playwright`** 在与项目的 `next` 同一发布线上；它提供 `instant()`。使用 `npm ls next @next/playwright`（或项目的包管理器）进行验证，并在它们不同时对齐。匹配的测试 API 在 `next` 运行时中，由 `experimental.exposeTestingApiInProductionBuild` 配置标志（阶段 A）门控。

如果项目不符合这些条件，请先升级（`npx @next/codemod upgrade` 自动化大部分内容），然后在 `next.config.ts` 中启用缓存组件：

```ts
export default { cacheComponents: true }
```

启用标志会将阻塞路线暴露以首先解决；`[next-cache-components-adoption](https://github.com/vercel/next.js/tree/canary/skills/next-cache-components-adoption)` 技能推动这种采用。一旦应用程序在缓存组件下构建，就使用此优化器。

此门控是故意的：此技能针对当前 Next.js，并且以下所有裁决在旧版本上都没有意义。

## 0. 设置：每个存储库一次发现此项目的装置

此技能中的原则是固定的；它们运行的底层基础设施是你的。在存储库中首次使用时，发现项目如何构建、部署、认证和测试（首先检查存储库，并且仅在它无法回答的情况下才询问用户），然后将答案写入提交的 `instant-nav.rig.md`。之后每次运行都读取该文件，而不是重新发现。所需的构建、测试上下文、导航合同、迭代循环和文件模板在 **`rig-template.md`** 中。

如果存储库还没有 Playwright e2e 套件，立起一个最小的套件（`@next/playwright`、一个带有 `baseURL` 的配置、一个认证路径）是此步骤的一部分；循环不假设预存在的套件。

## A. 装置：一个带有测试 API 暴露的生产构建

立起 `instant-nav.rig.md` 描述的装置。在所有平台上，两个不变量都成立：

1. **永远不在 `next dev` 上测量。** 它不会预取，并且它的锁对于阻塞路线是不可靠的，因此开发 `instant()` 结果不是有效的 RED 或 GREEN。
2. **测量的构建必须暴露测试 API。** 否则 `instant()` 沉默地无操作，并且测试空泛地通过（见 `reference/red-test-robustness.md`）。锁参与证明是阶段 C 的 RED 本身：已知阻塞的路线是其锁下显示 RED，显示此构建上锁参与（C-gate）；`test-template.md` 中的自验证变体是带内保证。将 `experimental.exposeTestingApiInProductionBuild` 接线到一个条件，该条件对于您要测量的每个构建为真，并且在生产中永远不为真：

   ```ts
   experimental: {
     // 使用您的平台提供的条件，并在装置文件中记录它：
     //   本地：显式选择，如下所示
     //   通用 CI：process.env.DEPLOY_ENV === 'staging'
     //   Vercel: process.env.VERCEL_ENV === 'preview'
     exposeTestingApiInProductionBuild:
       process.env.EXPOSE_TESTING_API === '1',
   }
   ```

装置是任何类似生产的构建，它暴露测试 API：本地 `next build && next start`、CI/阶段容器和预览部署都是同样有效的；裁决来自构建，而不是平台。有关设置要求，请参阅 `rig-template.md`。

对于任何已部署或远程构建，轮询装置的 LIVENESS 探针以确认工件包含 `HEAD` 之前才信任裁决（陈旧的部署读取为假的 RED 或 GREEN）；本地 `next build && next start` 无需任何。探测机制在 `rig-template.md` 中。

## B. 基线（未锁定）：开发脚手架，不要发布

使用没有 `instant()` 锁驱动真实导航，并断言目标的外壳标记 **作为测试用户** 渲染：E2E 套件认证的帐户（在 CI 中是 CI 帐户；本地是您的 E2E 登录固定装置），及其标志、计划、角色和数据。这建立了标记是真实的并且可以到达：没有被标志门控、没有被重定向、不是一个猜测的选择器。套件以测试帐户运行，而不是作者会话；该环境漂移（装置 DRIFT 列表）是不可靠 RED 的常见来源。构建和运行命令：**`test-template.md`**。
**在 PR 之前删除此基线。**

## C. RED（锁定）+ VERIFY-RED 门控

将相同的导航包装在 `instant()` 中；断言外壳在锁下提交。这里的 RED 是差距。**这是要发布的测试**
(`test-template.md`)。

当路线有延迟内容时，优先使用自验证变体。如果路线在阻塞时无法构建，或者一个 cookie/会话读取保持 GREEN，请使用 `reference/red-test-robustness.md` 中的 RED 配方。

> **C-gate：在 RED 可信之前不要开始优化。** 一个因为错误原因而变红的 RED 会将您优化到一个从未损坏的路线。

决定性问题：**`SHELL_MARKER` 是否在无锁的情况下作为测试用户渲染？** 通过以测试用户身份重新运行阶段 B 来回答它，而不是在发布的测试中添加断言。两分支解析（没有→标记或环境错误；是→真实差距，继续到 D）、不可靠 RED 的完整分类、检查清单、差异数据食谱、空泛通过失败模式和案例研究都在
**`reference/red-test-robustness.md`** 中。现在阅读它。

---

## D. 修复：将每个边界向下推到它保护的数据

**反模式：一个粗边界。** 树中高处的单个 `<Suspense>` 带有页面级回退有三个成本：

- 布局 UI 停留在静态外壳之外：只有它的抛弃副本被预渲染。
- 当边界解析时，整个子树被替换，这会丢弃客户端状态并改变布局。
- 手动构建的回退随着 UI 变化而漂移，因为它复制了在解析树中也存在的结构。

**修复：提升静态内容，将 Suspense 向下推。** 一次同步、同步地渲染布局 UI 在外壳中，并将每个 await 包裹在仅限于它保护的单个读取的范围内的边界中。只有该叶子流式传输；稳定的祖先被原样重用。

**规则：** 如果一个元素在回退和解析树中都渲染，将其提升到边界之上。

### 最常见的阻塞器：回退路线上的布局中的顶层 `await`

```
app/[locale]/(app)/[tenant]/dashboard/...
       │ generateStaticParams ✅   │ no generateStaticParams → fallback route
```

当路线中的任何动态段缺少 `generateStaticParams` 时，该路线是一个回退路线，并且**所有**参数都延迟到请求时间，包括枚举的参数。布局中的顶层 `await`（`await params`、请求时间会话读取、认证门控）会阻塞整个子树出静态外壳，即使它读取一个静态已知的参数。最小形状：一个缺少 `generateStaticParams` 的动态段路线，加上它上面有一个顶层 `await` 的布局。

### 修复：延迟门控，渲染子项

无条件渲染 `children`；将顶层 `await` 移入 `<Suspense fallback={null}>`-包装的子项中。机制和之前→之后：
`reference/real-app-patterns.md`，"延迟一个认证门控"。

**同时修复外壳下方的页面，而不仅仅是布局。** 页面级的顶层 `await`（通常 `await params`）与布局的阻塞方式相同，因此使页面同步并将它的动态读取推入一个 `<Suspense>`-包装的叶子中。`fallback={null}` 仅当门控在成功时渲染为空时才是正确的；对于数据，回退必须是一个真实的加载骨架（见 D1）。

如果组件没有骨架，将其加载标记提取到它旁边的一个骨架中。不要编写一个镜像页面布局的新骨架：它复制了结构，随着页面变化而漂移，并将设计拉回到一个单一的粗边界。重用组件自己的骨架也使预取的外壳与加载的 UI 保持一致。

见：[流式传输](https://nextjs.org/docs/app/guides/streaming#push-dynamic-access-down)
和 [加载状态](https://nextjs.org/docs/app/guides/instant-navigation#iterate-on-loading-states)。

例外：如果延迟组件对某些用户渲染 `null`（例如，一个标志门控的控件），`fallback={null}` 是正确的，因为骨架会闪烁然后消失。

### D2：外壳必须在每个断点与真实渲染匹配

冻结到一个断点的骨架在其他人断点上错位。按相同方式修复它：一个响应式组件同时渲染实时 UI 和外壳（D1 骨架在其数据槽中），因此断点切换只发生一次。通过在两个宽度上重新断言外壳标记（`await page.setViewportSize({ width: 1280, height: 800 })`，然后 `{ width: 390, height: 844 }`）来验证，或者通过添加一个移动 Playwright 项目，使此门控与其它门控一样机器可检查。详情：
`reference/real-app-patterns.md`。

> **D-gate：当阶段 C 中的锁定测试在类似生产的装置上锁下通过 GREEN 时，阶段 D 才算完成**，而不是代码编译时。那个 GREEN 是修复循环的确定性停止；继续到 E。

如果优化添加或扩展了缓存边界，请遵循
[重新验证](https://nextjs.org/docs/app/getting-started/revalidating)。
通过 `instant()` 测试证明外壳就绪，而不是突变新鲜。

**当 URL 数据无法向下推时**（例如，整个页面依赖于 `params`、`searchParams` 或完整 URL），可能没有有意义的静态外壳可以增长。不要强迫一个。按链接预取可以使软导航即时，但它不在此优化器循环之外：它需要部分预取、`<Link prefetch={true}>` 和缓存的 URL 相关内容。见
[优化预取](https://nextjs.org/docs/app/guides/optimizing-prefetching)
和 `reference/patterns.md` 中的模式 10，以了解要求、成本权衡、手动预取注意事项和 `instant()` 测试陷阱。

## E. PARITY：重构仅改变了路线是否即时

向下推是一个机械转换，而不是重新设计。之后路线必须渲染与之前相同的树、数据、顺序、空和错误状态、重定向和交互；唯一可观察的差异是外壳现在立即提交。验证：

- **相同的渲染输出。** 移动的 `await`s 计算并返回相同的值；流之后，路线显示与基本分支相同的测试用户内容。
- **副作用仍然触发。** 一个延迟的 `redirect()` 或 `notFound()` 仍然发生，在请求时间而不是预渲染期间发生。确认未授权用户仍然重定向，缺少的记录仍然返回 404。
- **两个视口在流之后都达到真实 UI**（D2）。
- **客户端状态幸存。** 因为布局 UI 被提升到稳定外壳而不是在解析时交换，所以打开的菜单、滚动位置、焦点和输入状态在流之间保持不变。
- **预存在的失败保持分离。** 如果路线在更改后出错，请在基本分支上重现它。那里相同的失败是一个环境或数据问题，而不是优化器回归。

如果除了路线是否即时之外有任何其他东西改变，请减少重构。

## F. 差异数据

仅回滚修复 → RED；重新应用 → GREEN；链接两个运行
(`reference/red-test-robustness.md`)。在已部署的装置上，在信任其颜色之前，确认每个运行都是活动的（LIVENESS，阶段 A）。

## G. REVIEW (PR 检查清单)

绿色最终状态意味着如果 RED 从未可信，则毫无意义。测试可信性项目是鲁棒性检查清单
(`reference/red-test-robustness.md`)；确认它们，然后要求以下 PR 特定项目：

- [ ] **差异数据显示**：没有修复的 RED，带有它的 GREEN，运行链接。
- [ ] **PARITY 确认 (E)**：相同内容、重定向和状态。
- [ ] **适用时验证突变**：在填充任何可以更新的缓存后，突变测试确认下一次读取返回预期数据。
- [ ] **重用现有加载 UI (D1)**：没有新的镜像页面骨架。
- [ ] **外壳在桌面和移动宽度上与真实渲染匹配 (D2)**。
- [ ] **删除基线**：仅保留来自 C 的锁定测试。

**整个工作流程的停止条件**：来自 C 的锁定测试在装置上为 GREEN，差异数据（F）保持，并且上述所有项目都已检查。在所有三个都保持之前，你还没有完成。

## 在测试中驱动导航

- **软导航** → 驱动一个真实的 `<Link>` 点击。**初始加载** → 使用 `page.goto()` 在 `instant()` 内部，并使用 `baseURL` 选项。不要用 `goto` 代替软导航裁决；两种外壳可以不同
  (`test-template.md`，`reference/real-app-patterns.md`)。
- 使用并行路线时，只有更改的插槽在软导航时重新渲染；客户端渲染的导航 UI 根本不会重新渲染。不要追逐导航从未触及的插槽
  (`reference/real-app-patterns.md`)。

## 文件

- `rig-template.md`: 阶段 0 生产构建、测试上下文、导航合同和无人值守循环发现。
- `test-template.md`: 两种导航类型的已发布 `instant()` 规格的（阶段 C），以及 PR 之前删除的基线脚手架（阶段 B）。
- `reference/red-test-robustness.md`: C-gate 和阶段 F。不可靠 RED 的分类、检查清单、差异数据食谱、空泛通过失败模式和案例研究。
- `reference/real-app-patterns.md`: 并行路线、延迟一个认证门控、初始加载与软导航外壳、空壳失败模式、响应式骨架不匹配、边缘案例。

## 优化后

一旦目标路线变为即时，检查应用程序是否已经采用部分预取 (`partialPrefetching: true`，或相关目标在增量推出期间仍然使用 `prefetch = 'partial'`)。

机械地检查它：

```bash
rg -n "partialPrefetching|prefetch\s*=\s*['\"]partial['\"]" --glob 'next.config.*' --glob 'app/**' --glob 'src/app/**'
```

如果 `partialPrefetching: true` 在配置中，应用程序已全局采用。如果只有 `prefetch = 'partial'` 匹配，将那些目标段视为在增量推出期间采用，并继续检查任何其他目标路线。

- **已经采用**：对于任何 URL 数据路线，如果它停在上述限制上，请考虑在链接上使用目标 `<Link prefetch={true}>`，在点击之前准备好 URL 特定内容值得每条链接的服务器工作。在默认链接行为之外保持默认，以便共享应用外壳仍然是低成本基线。
- **尚未采用**：建议
  [`next-partial-prefetching-adoption`](https://github.com/vercel/next.js/tree/canary/skills/next-partial-prefetching-adoption)。
  该技能将应用程序移动到更好的预取模型：共享应用外壳默认预取，较少的可见链接的完整预取请求，一个链接审计，以及可选的仅在 URL 特定内容值得额外服务器工作的按链接预取。
