# 克隆网站

您即将逆向工程并重建用户请求中的**目标 URL 或 URL**，以像素级完美的克隆形式呈现。

当提供多个 URL 时，将保留每个路径名作为独立的路由，并隔离每个目标的调研、截图、组件和资源。仅查询字符串或片段不同的 URL 共享路径名，因此请在输出计划中明确解决其路由和状态行为。仅在共享基础和输出计划固定后才能并行化页面工作，以便并发构建者不会相互覆盖。

这不是一个两阶段过程（检查然后构建）。您是一个**在现场巡视的工长**——在检查页面的每个部分时，您将详细的规范写入文件，然后将该文件交给一个拥有所有必要资源的专家构建代理。提取和构建是并行进行的，但提取是细致的，并产生可审计的工件。

## 范围默认值

目标是请求的 URL 解析到的页面。精确克隆该 URL 下可见的内容。除非用户另有说明，否则使用这些默认值：

- **保真度级别：** 像素级完美——颜色、间距、排版、动画完全匹配
- **范围内：** 视觉布局和样式、组件结构和交互、响应式设计、用于演示目的的模拟数据
- **范围外：** 真实后端/数据库、身份验证、实时功能、SEO 优化、无障碍性审核
- **自定义：** 无——纯粹的模拟

如果用户提供额外的说明（特定的保真度级别、自定义、额外上下文），请优先考虑这些默认值。

## 输出隔离和路由保留

将每个目标 URL 视为持久的项目输出，而不是替换先前构建内容的许可。

在提取之前选择 `<app-root>`。对于单个应用程序，`<app-root>` 是仓库根目录（`.`）。如果不同的来源需要单独的应用程序，要求用户提供或批准每个来源的预先准备的 Next.js 项目根；验证每个根可以独立构建，并且永远不会将一个来源的输出写入另一个根。

然后为每个目标分配：

- 一个抗冲突的 `<site-key>`：一个可读的来源别名（包括非默认端口）加上规范化来源的 SHA-256 的前 8 个小写十六进制字符。
- 一个抗冲突的 `<page-key>`：一个保留段落的可读路径名别名加上规范化路径名和任何状态查询/片段的 SHA-256 的前 8 个小写十六进制字符；使用 `root-<hash>` 对于 `/`。永远不要单独依赖有损字符替换。
- 一个工件根：`<app-root>/docs/research/<site-key>/<page-key>/`。
- 一个截图根：`<app-root>/docs/design-references/<site-key>/<page-key>/`。
- 一个组件根：`<app-root>/src/components/sites/<site-key>/<page-key>/`，真正的同站共享组件在 `<app-root>/src/components/sites/<site-key>/shared/` 下。
- 一个资源根：`<app-root>/public/sites/<site-key>/<page-key>/`，真正的同站共享资源在 `<app-root>/public/sites/<site-key>/shared/` 下。
- 一个 Next.js 路由文件。

剩余阶段中的所有路径都相对于该目标的 `<app-root>`。在写入之前，验证每个计划的路线、工件根、截图根、组件根、资源根和下载器文件名是唯一的，或者是明确批准的共享位置。

路由默认值：

- 对于未受影响的模板中的第一个单 URL 克隆，`src/app/page.tsx` 处的现有脚手架可能会被替换，以便克隆仍然可以在 `/` 处访问。
- 对于来自同一来源的多个 URL，或任何添加到已包含克隆/用户编写页面的项目中的后续克隆，保留规范化源路径名作为其 App Router URL（例如，`/docs/intro` 变为 `<app-root>/src/app/docs/intro/page.tsx`）。对将触发 App Router 语法 的文件系统段名进行转义：用百分号编码的文件夹拼写而不是创建私有文件夹、插槽、路由组或动态段。在完成前验证构建的路由是否解析到精确的规范化 URL。
- 在写入之前检查每个现有的 `src/app/**/page.tsx`。除非用户明确批准，否则永远不要删除或替换非脚手架路线、组件树、调研文件夹、截图或资源命名空间。
- 如果计划的路线已经存在，请停止并询问是否要更新该路线，选择另一条路线，还是跳过它。
- 来自不同来源的 URL 可能需要不兼容的字体、全局 CSS、布局和元数据。在修改文件之前，询问用户是否想要单独准备的应用程序根（推荐）或有意合并的多站点应用程序，具有路由范围的样式。不要创建未经批准的单一代码库或无声地混合全局基础。

## 预飞行检查

1. **需要浏览器自动化。** 检查可用的浏览器 MCP 工具（Chrome MCP、Playwright MCP、Browserbase MCP、Puppeteer MCP 等）。使用可用的工具——如果有多个，则优先使用 Chrome MCP。如果没有检测到，请询问用户他们拥有的浏览器工具以及如何连接它。没有浏览器自动化，这项技能就无法工作。
2. 解析用户请求中的目标 URL 或 URL。规范化并验证每个 URL；如果有任何无效的 URL，请要求用户在继续之前更正它们。对于每个有效的 URL，验证它是否可以通过您的浏览器 MCP 工具访问。
3. 验证基础项目构建：`npm run build`。Next.js + shadcn/ui + Tailwind v4 脚手架应该已经就位。如果没有，请告诉用户先设置它。
4. 列出现有路线（`src/app/**/page.tsx`）、站点组件命名空间、调研工件、截图和公共资源。区分未受影响的模板脚手架和现有的克隆或用户编写的工作。
5. 编写输出计划，列出每个目标 URL、`<app-root>`、`<site-key>`、`<page-key>`、目标路线、工件根，以及是否必须更改任何共享基础文件。在编辑之前，与用户解决所有计划的输出中的冲突，相同的路径查询/片段行为和多来源布局决策。
6. 仅创建计划的每个页面/每个站点的目录，如果需要，则创建 `scripts/`。使用唯一的资源下载脚本名称，例如 `scripts/download-assets-<site-key>-<page-key>.mjs`；不要覆盖另一个页面的下载器。
7. 对于来自一个来源的多个页面，一次顺序构建共享基础，然后并行进行页面工作。可选地确认是否要并行运行页面构建器（如果资源允许）或顺序运行以避免过载。

在检查通过之前，请阅读 [references/inspection-guide.md](references/inspection-guide.md) 以获取可重用的视觉、组件、布局和技术审核清单。

## 指导原则

这些是区分成功的克隆和“差不多”的混乱的真理。内化它们——它们应该指导你做出的每一个决定。

### 1. 完整性胜过速度

每个构建代理必须接收到**所有**它需要完美完成工作的内容：截图、确切的 CSS 值、具有本地路径下载的资源、真实文本内容、组件结构。如果构建代理必须猜测任何内容——颜色、字体大小、填充值——你就失败了提取。花额外一分钟提取更多属性，而不是发货不完整的简报。

### 2. 小任务，完美结果

当代理得到“构建整个功能部分”时，它会忽略细节——它会估算间距、猜测字体大小，并产生“差不多”但明显错误的东西。当它得到一个具有确切 CSS 值的单个聚焦组件时，它会每次都做到完美。

查看每个部分并判断其复杂性。一个简单的横幅，带有标题和按钮？一个代理。一个复杂的部分，有 3 种不同的卡片变体，每种卡片都有唯一的悬停状态和内部布局？每个卡片变体一个代理，再加上一个部分包装器代理。如有疑问，请将其拆分。

**复杂性预算规则：** 如果构建提示超过 ~150 行规范内容，该部分对于单个代理来说太复杂了。将其拆分成更小的部分。这是一个机械检查——不要用“但它们都有关联”来覆盖它。

### 3. 真实内容，真实资源

从实时网站提取实际文本、图像、视频和 SVG。这是一个克隆，不是模拟。使用 `element.textContent`，下载每个 `<img>` 和 `<video>`，将内联 `<svg>` 元素提取为 React 组件。只有在某物明显是会话唯一的生成内容时，你才生成内容。

**分层资源很重要。** 看起来像是一个图像的部分通常是多个图层——一个背景水彩/渐变，一个前景 UI 模拟 PNG，一个叠加图标。检查每个容器的完整 DOM 树，并枚举其中所有的 `<img>` 元素和背景图像，包括绝对定位的叠加层。遗漏一个叠加图像会使克隆看起来空荡荡的，即使背景是正确的。

### 4. 先构建基础

在构建任何东西之前，直到基础存在：全局 CSS 与目标站点的设计令牌（颜色、字体、间距），内容结构的 TypeScript 类型，以及全局资源（字体、favicon）。这是顺序的，不容商议。之后的一切都可以并行。

### 5. 提取外观和行为

网站不是截图——它是一个活生生的东西。元素会移动、改变、出现和消失，以响应滚动、悬停、点击、调整大小和时间。如果你只提取每个元素的静态 CSS，你的克隆在截图中看起来是正确的，但在有人实际使用它时感觉是死的。

对于每个元素，提取它的**外观**（通过 `getComputedStyle()` 获取的确切计算 CSS）和它的**行为**（什么会改变，什么会触发改变，以及过渡如何发生）。不是“它看起来像 16px”——提取实际计算值。不是“导航在滚动时改变”——记录确切的触发器（滚动位置、IntersectionObserver 阈值、视口交集），以及前后状态（两组 CSS 值），以及过渡（持续时间、缓动、CSS 过渡与 JS 驱动或 CSS `animation-timeline`）。

要观察的行为示例——这些是说明性的，不是详尽的。页面可能会做此列表中未列出的其他事情，你必须捕捉到它们：
- 一个在滚动到某个阈值后收缩、改变背景或获得阴影的导航栏
- 当元素进入视口时动画进入视图的元素（淡入、滑入、交错延迟）
- 在滚动时自动对齐的部分
- 移动速度与滚动不同的视差层
- 悬停状态会动画（不只是改变——过渡持续时间和缓动很重要）
- 具有进入/退出动画的下拉菜单、模态框、手风琴
- 滚动驱动的进度指示器或不透明度过渡
- 自动播放的轮播或循环内容
- 页面部分之间的暗转到亮（或任何主题）过渡
- **循环的选项卡/药丸内容**——按钮使用过渡切换可见的卡片集
- **滚动驱动的选项卡/手风琴切换**——随着内容滚动而自动更改的侧边栏

### 6. 在构建之前确定交互模型

这是克隆中最昂贵的错误：构建基于点击的 UI，而原始版本是基于滚动的，反之亦然。在为交互部分编写任何构建提示之前，你必须明确回答：**这个部分是由点击、滚动、悬停、时间或它们的组合驱动的？**

如何确定：
1. **不要首先点击。** 缓慢滚动通过该部分，观察当您滚动时是否有东西自行改变。
2. 如果它们在滚动时改变，它是滚动驱动的。提取机制：`IntersectionObserver`、`scroll-snap`、`position: sticky`、`animation-timeline` 或 JS 滚动监听器。
3. 如果滚动时没有改变，那么测试点击/悬停以测试交互性。
4. 明确记录交互模型：**“交互模型：基于滚动和 IntersectionObserver”** 或 **“交互模型：基于点击切换和不透明度过渡”**。

具有粘性侧边栏和滚动内容面板的部分与一个选项卡界面不同，其中点击切换内容。弄错意味着完全重写，而不是 CSS 微调。

### 7. 提取每个状态，而不仅仅是默认状态

许多组件有多个视觉状态——选项卡栏根据每个选项卡显示不同的卡片，页眉在滚动位置 0 和 100 时看起来不同，卡片有悬停效果。你必须提取所有状态，而不仅仅是页面加载时可见的内容。

对于选项卡/状态内容：
- 点击每个选项卡/按钮，并提取每个状态的内容

### 8. Spec 文件是事实来源

每个组件在页面工件根（`docs/research/<site-key>/<page-key>/components/`）下获得规范文件，在构建任何构建代理之前。此文件是提取工作和构建代理之间的合同。构建代理在其提示中接收规范文件的内容——该文件还作为可审计的工件持久存在，以便用户（或你）可以在出现问题时进行审查。

Spec 文件不是可选的。它不是一项“锦上添花”的事情。如果你在构建代理之前没有首先编写 Spec 文件，你正在发货基于你从浏览器 MCP 会话中可以记住的内容的不完整指令，构建代理将猜测以填补空白。

### 9. 构建必须始终编译

每个构建代理必须验证 `npx tsc --noEmit` 通过完成。合并工作树后，你验证 `npm run build` 通过。一个损坏的构建永远不可接受，即使是暂时的。

## 第一阶段：侦察

使用浏览器 MCP 导航到目标 URL。

### 截图
- 在桌面（1440px）和移动（390px）视口处**全页截图**
- 保存到该页面的截图根（`docs/design-references/<site-key>/<page-key>/`）并使用描述性名称
- 这些是您的参考——构建代理将稍后接收针对特定部分的裁剪/截图

### 全局提取
在执行任何其他操作之前，从页面中提取以下内容：

**字体**——检查 `<link>` 标签以检查 Google 字体或自托管字体。检查关键元素（标题、正文、代码、标签）的计算 `font-family`。记录实际使用的每个字体系列、权重和样式。对于单站应用程序，使用 `next/font/google` 或 `next/font/local` 在 `src/app/layout.tsx` 中配置共享字体。在批准的合并多站点应用程序中，保持不兼容的字体/布局问题具有路由范围的样式。

**颜色**——从页面计算样式中提取站点的调色板。对于单站应用程序，将目标颜色合并到 `src/app/globals.css` 中，而不要删除现有路线所需的标记。将它们映射到 shadcn 的标记名称（背景、前景、主要、柔和等），如果合适。在批准的合并多站点应用程序中，使用路由包装器或范围标记名称，而不是替换另一个站点的全局调色板。

**Favicons & Meta**——在计划的站点资源命名空间下下载页面/站点 SEO 资产。仅在它适用于每个路线时，将真正应用程序范围的元数据放在根布局中；否则从目标页面或路由布局导出路线特定的元数据。

**全局 UI 模式**——识别任何站点的 CSS 或 JS：自定义滚动条隐藏、页面容器的滚动快照、全局关键帧动画、背景滤镜、渐变用作叠加层、**平滑滚动库**（Lenis、Locomotive Scroll——检查 `.lenis`、`.locomotive-scroll` 或自定义滚动容器类）。将真正共享的行为合并到 `globals.css`；将页面特定的行为范围到页面中，以便现有路线不会意外更改。

### 强制交互扫描

这是在截图和任何其他操作之前的一个专用过程。其目的是发现页面上的每个行为——其中许多行为在静态截图中是不可见的。

**滚动扫描**：使用浏览器 MCP 缓慢地从顶部滚动到页面底部。在每个部分处暂停并观察：
- 页眉的外观是否改变？记录触发位置。
- 元素是否动画进入视图？记录哪些元素和动画类型。
- 侧边栏或选项卡指示器是否随着滚动自动切换？记录机制。
- 是否有滚动快照点？记录哪些容器。
- 是否有平滑滚动库激活？检查 `.lenis` 类或滚动容器包装器。

**点击扫描**：点击看起来交互的每个元素：
- 每个按钮、选项卡、药丸、链接、卡片
- 记录发生了什么：内容是否改变？是否打开模态框？是否出现下拉菜单？
- 对于选项卡/药丸：点击每个并记录每个状态的内容

**悬停扫描**：悬停在可能具有悬停状态的每个元素上：
- 按钮、卡片、链接、图像、导航项
- 记录发生了什么：颜色、缩放、阴影、下划线、不透明度

**响应式扫描**：使用浏览器 MCP 在 3 个视口宽度处测试：
- 桌面：1440px
- 平板电脑：768px
- 移动设备：390px
- 在每个宽度处，注意哪些部分更改布局（列 → 堆叠，侧边栏消失等），以及大约在哪个断点处发生更改。

将所有发现保存到 `<artifact-root>/BEHAVIORS.md`。这是您的行为圣经——在编写每个组件规范时参考它。

### 页面拓扑
从顶部到底部绘制页面的每个独立部分。给每个一个工作名称。记录：
- 它们的视觉顺序
- 哪些是固定/粘性叠加层与流式内容
- 整体页面布局（滚动容器、列结构、z-index 层）
- 部分之间的依赖关系（例如，一个覆盖所有内容的浮动导航）
- **每个部分的交互模型**（静态 / 点击 / 滚动 / 时间）

将此保存为 `<artifact-root>/PAGE_TOPOLOGY.md`——它将成为您的装配蓝图。

## 第二阶段：基础构建

这是针对每个来源的顺序。由于它会影响共享文件，因此请自行执行（不要委托给代理）。重新阅读输出计划并保留编辑之前存在的每条路线：

1. **合并字体和共享布局行为**，而不要删除现有路线的要求。当行为不是真正应用程序全局时，使用路由布局。
2. **仔细合并全局 CSS**；将页面/站点特定的标记、关键帧、滚动行为和实用程序范围到路由包装器下，以便它们不会发生冲突。
3. **创建命名空间的 TypeScript 接口**，用于您观察到的内容结构；仅在合同匹配时重用现有同站类型。
4. **提取 SVG 图标**——在同站图标下 `src/components/sites/<site-key>/shared/icons.tsx` 中去重相同的同站图标；将页面唯一的图标保留在页面组件命名空间中。按视觉功能命名它们（例如，`SearchIcon`、`ArrowRightIcon`、`LogoIcon`）。
5. **将资源下载到计划的命名空间**——使用页面唯一的下载脚本并写入 `public/sites/<site-key>/<page-key>/` 或批准的同站共享目录。永远不要使用通用文件名覆盖另一个页面的资源。
6. 验证之前存在的每条路线仍然可以构建，然后运行 `npm run build`。

### 资源发现脚本模式

使用浏览器 MCP 列出页面上的所有资源：

```javascript
// 通过浏览器 MCP 运行此脚本来发现所有资源
JSON.stringify({
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src || img.currentSrc,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    // 包括父级信息以检测分层组合
    parentClasses: img.parentElement?.className,
    siblings: img.parentElement ? [...img.parentElement.querySelectorAll('img')].length : 0,
    position: getComputedStyle(img).position,
    zIndex: getComputedStyle(img).zIndex
  })),
  videos: [...document.querySelectorAll('video')].map(v => ({
    src: v.src || v.querySelector('source')?.src,
    poster: v.poster,
    autoplay: v.autoplay,
    loop: v.loop,
    muted: v.muted
  })),
  backgroundImages: [...document.querySelectorAll('*')].filter(el => {
    const bg = getComputedStyle(el).backgroundImage;
    return bg && bg !== 'none';
  }).map(el => ({
    url: getComputedStyle(el).backgroundImage,
    element: el.tagName + '.' + el.className?.split(' ')[0]
  })),
  svgCount: document.querySelectorAll('svg').length,
  fonts: [...new Set([...document.querySelectorAll('*')].slice(0, 200).map(el => getComputedStyle(el).fontFamily))],
  favicons: [...document.querySelectorAll('link[rel*="icon"]')].map(l => ({ href: l.href, sizes: l.sizes?.toString() }))
});
```

然后使用唯一命名的页面下载脚本将所有内容下载到其计划的资源根。使用批量并行下载（一次 4 个）并具有适当的错误处理。

## 第三阶段：组件规范和派发

这是核心循环。对于页面拓扑中的每个部分（从上到下），您需要执行三个操作：**提取**，**编写规范文件**，然后**派发构建代理**。

### 第 1 步：提取

对于每个部分，使用浏览器 MCP 提取所有内容：

1. **截图**：在隔离状态下（滚动到它，截图视口）。保存到页面的截图根。
2. **提取 CSS**：对于部分中的每个元素。使用提取脚本——不要手动测量单个属性。对每个组件容器运行一次，并捕获完整输出：

```javascript
// 每个组件提取——通过浏览器 MCP 运行
// 将 SELECTOR 替换为实际的 CSS 选择器
(function(selector) {
  const el = document.querySelector(selector);
  if (!el) return JSON.stringify({ error: 'Element not found: ' + selector });
  const props = [
    'fontSize','fontWeight','fontFamily','lineHeight','letterSpacing','color',
    'textTransform','textDecoration','backgroundColor','background',
    'padding','paddingTop','paddingRight','paddingBottom','paddingLeft',
    'margin','marginTop','marginRight','marginBottom','marginLeft',
    'width','height','maxWidth','minWidth','maxHeight','minHeight',
    'display','flexDirection','justifyContent','alignItems','gap',
    'gridTemplateColumns','gridTemplateRows',
    'borderRadius','border','borderTop','borderBottom','borderLeft','borderRight',
    'boxShadow','overflow','overflowX','overflowY',
    'position','top','right','bottom','left','zIndex',
    'opacity','transform','transition','cursor',
    'objectFit','objectPosition','mixBlendMode','filter','backdropFilter',
    'whiteSpace','textOverflow','WebkitLineClamp'
  ];
  function extractStyles(element) {
    const cs = getComputedStyle(element);
    const styles = {};
    props.forEach(p => { const v = cs[p]; if (v && v !== 'none' && v !== 'normal' && v !== 'auto' && v !== '0px' && v !== 'rgba(0, 0, 0, 0)') styles[p] = v; });
    return styles;
  }
  function walk(element, depth) {
    if (depth > 4) return null;
    const children = [...element.children];
    return {
      tag: element.tagName.toLowerCase(),
      classes: element.className?.toString().split(' ').slice(0, 5).join(' '),
      text: element.childNodes.length === 1 && element.childNodes[0].nodeType === 3 ? element.textContent.trim().slice(0, 200) : null,
      styles: extractStyles(element),
      images: element.tagName === 'IMG' ? { src: element.src, alt: element.alt, naturalWidth: element.naturalWidth, naturalHeight: element.naturalHeight } : null,
      childCount: children.length,
      children: children.slice(0, 20).map(c => walk(c, depth + 1)).filter(Boolean)
    };
  }
  return JSON.stringify(walk(el, 0), null, 2);
})('SELECTOR');
```

3. **提取多状态样式**——对于任何具有多个状态的元素（滚动触发、悬停、活动选项卡），捕获两个状态：

```javascript
// 状态 A：捕获当前状态的样式（例如，滚动位置 0）
// 然后触发状态更改（滚动、点击、悬停通过浏览器 MCP）
// 状态 B：重新运行提取脚本，并在同一个元素上
// A 和 B 之间的差异就是行为规范
```

明确记录差异：**属性 X 从 VALUE_A 变化到 VALUE_B，由 TRIGGER 触发，过渡：TRANSITION_CSS。**

4. **提取真实内容**——所有文本、alt 属性、aria 标签、占位符文本。使用 `element.textContent` 对每个文本节点。对于选项卡/状态内容，**点击每个选项卡并提取每个状态的内容**。

5. **识别此部分使用的资源**——哪些命名空间下载的图像/视频和哪些页面/站点图标组件。检查是否有**分层图像**（多个 `<img>` 或同一容器中的背景图像堆叠）。
