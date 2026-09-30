---
name: clone-website
description: 一次性逆向工程并克隆一个或多个网站——逐段提取资源、CSS和内容，并在过程中主动在工作树中派遣并行构建代理。用户在任何时候想要克隆、复制、重建、逆向工程或复制任何网站时都可以使用此功能。同时，在类似“复制此网站”、“重建此页面”、“像素级克隆”的短语触发下也会执行。请提供一个或多个目标URL作为参数。
---

# 克隆网站

你即将逆向工程并重建 **$ARGUMENTS**，制作像素级完美的克隆版本。

当提供多个 URL 时，尽可能并行处理它们，同时将每个网站的提取工件隔离在专门的文件夹中（例如，`docs/research/<hostname>/`）。

这不是一个分两阶段的过程（先检查后构建）。你是一个**在现场巡视的工头**——当你检查页面的每个部分时，你会将详细的规范写入文件，然后将该文件交给一个拥有所有必要资源的专家构建代理。提取和构建是并行进行的，但提取过程非常细致，并会产生可审计的工件。

## 范围默认值

目标是 **$ARGUMENTS** 解析到的页面。克隆该 URL 下可见的内容。除非用户指定其他内容，否则使用这些默认值：

- **保真度级别：** 像素级完美——颜色、间距、排版、动画完全匹配
- **范围内：** 视觉布局和样式、组件结构和交互、响应式设计、用于演示目的的模拟数据
- **范围外：** 真实后端/数据库、认证、实时功能、SEO 优化、无障碍性审核
- **自定义：** 无——纯粹的模拟

如果用户提供了附加说明（特定的保真度级别、自定义内容、额外上下文），请优先考虑这些说明而不是默认值。

## 飞行前检查

1. **需要浏览器自动化。** 检查可用的浏览器 MCP 工具（Chrome MCP、Playwright MCP、Browserbase MCP、Puppeteer MCP 等）。使用可用的工具——如果存在多个工具，优先使用 Chrome MCP。如果没有检测到任何工具，请询问用户他们拥有的浏览器工具以及如何连接它。没有浏览器自动化，这项技能无法工作。
2. 将 **$ARGUMENTS** 解析为一个或多个 URL。规范化并验证每个 URL；如果任何 URL 无效，请要求用户更正它们才能继续。对于每个有效的 URL，使用你的浏览器 MCP 工具验证其可访问性。
3. 验证基础项目构建：`npm run build`。Next.js + shadcn/ui + Tailwind v4 框架应该已经就位。如果没有，请告诉用户先设置它。
4. 如果输出目录不存在，则创建它们：`docs/research/`、`docs/research/components/`、`docs/design-references/`、`scripts/`。对于多个克隆，还准备按网站划分的文件夹，例如 `docs/research/<hostname>/` 和 `docs/design-references/<hostname>/`。
5. 当在一个命令中处理多个网站时，可以选择确认是否并行运行（如果资源允许，推荐）或顺序运行以避免过载。

## 指导原则

这些是区分成功克隆和“差不多就行”的混乱的真理。内化它们——它们应该指导你做出的每一个决定。

### 1. 完整性胜过速度

每个构建代理必须收到做完美工作所需的所有内容：截图、确切的 CSS 值、本地路径下载的资产、真实文本内容、组件结构。如果构建代理必须猜测任何内容——颜色、字体大小、填充值——你就失败了。花额外一分钟提取更多属性，而不是发送一个不完整的简报。

### 2. 小任务，完美结果

当代理接到“构建整个功能部分”的任务时，它会忽略细节——它会估算间距、猜测字体大小，并制作出“差不多就行”但明显错误的内容。当它接到一个具有确切 CSS 值的单个聚焦组件时，它会每次都做到完美。

查看每个部分的复杂性。一个简单的横幅，带有标题和按钮？一个代理。一个复杂的部分，有 3 种不同的卡片变体，每种变体都有独特的悬停状态和内部布局？每个卡片变体一个代理，再加上一个部分包装器的代理。如有疑问，请将其拆分。

**复杂性预算规则：** 如果构建提示的规范内容超过 ~150 行，该部分对于单个代理来说太复杂了。将其拆分成更小的部分。这是一个机械检查——不要用“但它们都有关联”来覆盖它。

### 3. 真实内容，真实资产

从实时网站提取实际文本、图像、视频和 SVG。这是一个克隆，不是模拟。使用 `element.textContent`，下载每个 `<img>` 和 `<video>`，将内联 `<svg>` 元素提取为 React 组件。只有在某物明显是会话生成的且唯一的特定情况下，你才会生成内容。

**分层资产很重要。** 看起来像是一个图像的部分通常是多个层——一个背景水彩/渐变，一个前景 UI 模拟 PNG，一个叠加图标。检查每个容器的完整 DOM 树，并列举其中的所有 `<img>` 元素和背景图像，包括绝对定位的叠加层。遗漏一个叠加图像会使克隆看起来空荡荡的，即使背景是正确的。

### 4. 先构建基础

在构建任何东西之前，基础必须存在：全局 CSS 和目标网站的设计令牌（颜色、字体、间距）、内容结构的 TypeScript 类型，以及全局资产（字体、图标）。这是顺序的，不容商议。这之后的所有内容都可以并行。

### 5. 提取外观和行为

网站不是截图——它是一个活生生的东西。元素会移动、改变、出现和消失，作为滚动、悬停、点击、调整大小和时间的响应。如果你只提取每个元素的静态 CSS，你的克隆在截图里看起来是正确的，但在有人实际使用时感觉是死的。

对于每个元素，提取它的**外观**（通过 `getComputedStyle()` 获取的确切计算 CSS）和它的**行为**（什么会改变、什么触发了改变、以及过渡如何发生）。不是“它看起来像 16px”——提取实际计算值。不是“导航在滚动时改变”——记录确切的触发器（滚动位置、IntersectionObserver 阈值、视口交集）、前后状态（两套 CSS 值）和过渡（持续时间、缓动、CSS 过渡与 JS 驱动或 CSS `animation-timeline`）。

要注意的行为示例——这些是说明性的，不是详尽的。页面可能会做这个列表中没有的的事情，你必须捕捉到它们：
- 滚动到某个阈值后，导航栏会缩小、改变背景或获得阴影
- 当元素进入视口时，会动画进入视图（淡入、滑入、交错延迟）
- 滚动时，部分会自动吸附到位（`scroll-snap-type`）
- 垂直平移层移动速度与滚动不同
- 悬停状态会动画（不只是改变——过渡持续时间和缓动很重要）
- 带有进入/退出动画的下拉菜单、模态框、手风琴
- 滚动驱动的进度指示器或不透明度过渡
- 自动播放的轮播或循环内容
- 页面部分之间的暗到亮（或任何主题）过渡
- **循环的选项卡/药丸内容**——按钮通过过渡切换可见的卡片集
- **滚动驱动的选项卡/手风琴切换**——侧边栏中，当内容滚动过去时，活动项会自动更改（IntersectionObserver，不是点击处理程序）
- **平滑滚动库**（Lenis、Locomotive Scroll）——检查 `.lenis` 类或滚动容器包装器

### 6. 在构建之前确定交互模型

这是克隆中最昂贵的错误：构建一个基于点击的 UI，而原始版本是基于滚动的，反之亦然。在为交互部分编写任何构建提示之前，你必须明确回答：**这个部分是由点击、滚动、悬停、时间或它们的组合驱动的？**

如何确定：
1. **不要先点击。** 缓慢滚动通过该部分，观察当你在滚动时是否有东西会自动改变。
2. 如果它们会改变，它是滚动驱动的。提取机制：`IntersectionObserver`、`scroll-snap`、`position: sticky`、`animation-timeline` 或 JS 滚动监听器。
3. 如果滚动时没有变化，那么点击/悬停来测试点击/悬停驱动的交互。
4. 在组件规范中明确记录交互模型：`"INTERACTION MODEL: scroll-driven with IntersectionObserver"` 或 `"INTERACTION MODEL: click-to-switch with opacity transition"`。

一个带有粘性侧边栏和滚动内容面板的部分与一个点击切换内容的选项卡界面从根本上不同。做错了意味着完全重写，而不是 CSS 微调。

### 7. 提取每个状态，而不仅仅是默认状态

许多组件有多个视觉状态——选项卡栏根据选项卡显示不同的卡片，页头在滚动位置 0 与 100 时看起来不同，卡片有悬停效果。你必须提取所有状态，而不仅仅是页面加载时可见的状态。

对于选项卡/状态内容：
- 通过浏览器 MCP 点击每个选项卡/按钮
- 提取每个状态的内容、图像和卡片数据
- 记录哪些内容属于哪个状态
- 注意状态之间的过渡动画（不透明度、滑入、淡入、等）

对于滚动依赖元素：
- 在滚动位置 0（初始状态）捕获计算样式
- 滚动到触发阈值后再次捕获计算样式（滚动状态）
- 比较两个以识别哪些 CSS 属性发生了变化
- 记录过渡 CSS（持续时间、缓动、属性）
- 记录确切的触发阈值（以 px 为单位的滚动位置，或视口交集比例）

### 8. 规范文件是事实来源

在发送任何构建代理之前，每个组件都会在 `docs/research/components/` 中获得一个规范文件。该文件是提取工作和构建代理之间的合同。构建代理在其提示中接收规范文件的内容——该文件还作为可审计的工件持久化，以便用户（或你）可以在出问题时进行审查。

规范文件不是可选的。它不是锦上添花。如果你在编写规范文件之前发送构建代理，你就是在基于你从浏览器 MCP 会话中记住的内容发送不完整的指令，构建代理将猜测以填补空白。

### 9. 构建必须始终可以编译

每个构建代理必须在完成前验证 `npx tsc --noEmit` 通过。合并工作树后，你验证 `npm run build` 通过。一个损坏的构建永远不可接受，即使是暂时的。

## 第一阶段：侦察

使用浏览器 MCP 导航到目标 URL。

### 截图
- 在桌面（1440px）和移动（390px）视口下**全页截图**
- 保存到 `docs/design-references/`，使用描述性名称
- 这些是你的主参考——构建代理将稍后接收特定部分的裁剪/截图

### 全局提取
在执行任何其他操作之前，从页面中提取以下内容：

**字体**——检查 `<link>` 标签以查找 Google 字体或自托管字体。检查关键元素（标题、正文、代码、标签）的计算 `font-family`。记录实际使用的每个字体、权重和样式。使用 `next/font/google` 或 `next/font/local` 在 `src/app/layout.tsx` 中配置它们。

**颜色**——从页面计算样式中提取网站的颜色调色板。使用目标网站的实际颜色更新 `src/app/globals.css` 中的 `:root` 和 `.dark` CSS 变量块。将它们映射到 shadcn 的令牌名称（背景、前景、主要、柔和等），如果适用。为不映射到 shadcn 令牌的颜色添加自定义属性。

**图标和元数据**——下载 favicons、apple-touch-icons、OG 图像、webmanifest 到 `public/seo/`。更新 `layout.tsx` 元数据。

**全局 UI 模式**——识别任何全站 CSS 或 JS：隐藏自定义滚动条、页面容器的滚动快照、全局关键帧动画、背景滤镜、用作叠加层的渐变、**平滑滚动库**（Lenis、Locomotive Scroll——检查 `.lenis`、`.locomotive-scroll` 或自定义滚动容器类）。将这些添加到 `globals.css`，并注意需要安装的任何库。

### 强制交互扫描

这是一个在截图之后、执行任何其他操作之前的专用过程。其目的是发现页面上的所有行为——其中许多在静态截图上是看不见的。

**滚动扫描：** 通过浏览器 MCP 缓慢地从上到下滚动页面。在每个部分，暂停并观察：
- 页头的外观是否改变？记录触发该变化的滚动位置。
- 元素是否动画进入视图？记录哪些元素和动画类型。
- 侧边栏或选项卡指示器是否随着滚动自动切换？记录机制。
- 是否有滚动快照点？记录哪些容器。
- 是否有激活的平滑滚动库？检查非原生滚动行为。

**点击扫描：** 点击看起来是交互的每个元素：
- 每个按钮、选项卡、药丸、链接、卡片
- 记录发生什么：内容是否改变？是否打开模态框？是否出现下拉菜单？
- 对于选项卡/药丸：点击每一个，并记录每个状态出现的内容

**悬停扫描：** 将鼠标悬停在可能具有悬停状态的每个元素上：
- 按钮、卡片、链接、图像、导航项
- 记录什么变化：颜色、缩放、阴影、下划线、不透明度

**响应式扫描：** 通过浏览器 MCP 在 3 个视口宽度下测试：
- 桌面：1440px
- 平板：768px
- 手机：390px
- 在每个宽度下，注意哪些部分会改变布局（列 → 堆叠、侧边栏消失等），以及大约在哪个断点发生变化。

将所有发现保存到 `docs/research/BEHAVIORS.md`。这是你的行为圣经——在编写每个组件规范时参考它。

### 页面拓扑
从上到下绘制页面的每个独立部分。给每个部分一个工作名称。记录：
- 它们的视觉顺序
- 哪些是固定/粘性叠加层与流式内容
- 整体页面布局（滚动容器、列结构、z-index 层）
- 部分之间的依赖关系（例如，一个覆盖所有内容的浮动导航）
- 每个部分的**交互模型**（静态、点击驱动、滚动驱动、时间驱动）

将其保存为 `docs/research/PAGE_TOPOLOGY.md`——它成为你的装配蓝图。

## 第二阶段：基础构建

这是顺序的。自己做（不委托给代理），因为它会触及许多文件：

1. **在 `layout.tsx` 中更新字体**以匹配目标网站的实际字体
2. **更新 `globals.css`**以包含目标的颜色令牌、间距值、关键帧动画、实用类和任何**全局滚动行为**（Lenis、平滑滚动 CSS、body 上的滚动快照）
3. **在 `src/types/` 中创建 TypeScript 接口**以匹配你观察到的内容结构
4. **提取 SVG 图标**——查找页面上的所有内联 `<svg>` 元素，去重，并保存为 `src/components/icons.tsx` 中的命名 React 组件。按视觉功能命名它们（例如，`SearchIcon`、`ArrowRightIcon`、`LogoIcon`）。
5. **下载全局资产**——编写并运行一个 Node.js 脚本（`scripts/download-assets.mjs`），将页面上的所有图像、视频和其他二进制资产下载到 `public/`。保留有意义的目录结构。
6. 验证：`npm run build` 通过

### 资产发现脚本模式

使用浏览器 MCP 列出页面上的所有资产：

```javascript
// 通过浏览器 MCP 运行此脚本以发现所有资产
JSON.stringify({
  images: [...document.querySelectorAll('img')].map(img => ({
    src: img.src || img.currentSrc,
    alt: img.alt,
    width: img.naturalWidth,
    height: img.naturalHeight,
    // 包含父级信息以检测分层组合
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

然后编写一个下载脚本，将所有资源抓取到 `public/` 目录。使用批量并行下载（每次 4 个），并包含适当的错误处理。

## 第 3 阶段：组件规格与分发

这是核心循环。对于页面拓扑中的每个部分（从上到下），你需要执行三件事：**提取**、**编写规格文件**，然后**分发构建器**。

### 步骤 1：提取

对于每个部分，使用浏览器 MCP 提取所有内容：

1. **截图**该部分在隔离状态下的样子（滚动到该位置，对视口进行截图）。保存到 `docs/design-references/`。

2. **提取 CSS**，针对该部分中的每个元素。使用下面的提取脚本——不要手动测量单个属性。每个组件容器运行一次，并捕获完整输出：

```javascript
// 按组件提取——通过浏览器 MCP 运行
// 将 SELECTOR 替换为组件的实际 CSS 选择器
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

3. **提取多状态样式**——对于具有多种状态（滚动触发、悬停、活动选项卡）的任何元素，捕获**两种**状态：

```javascript
// 状态 A：捕获当前状态的样式（例如，滚动位置 0）
// 然后触发状态变化（通过浏览器 MCP 进行滚动、点击、悬停）
// 状态 B：对同一元素重新运行提取脚本
// A 和 B 之间的差异即行为规格
```

明确记录差异：“属性 X 从 VALUE_A 变为 VALUE_B，由 TRIGGER 触发，过渡为：TRANSITION_CSS。”

4. **提取真实内容**——所有文本、alt 属性、aria 标签、占位符文本。对每个文本节点使用 `element.textContent`。对于选项卡/状态化内容，**点击每个选项卡并按状态提取内容**。

5. **识别资产**，该部分使用哪些已下载到 `public/` 的图像/视频，以及来自 `icons.tsx` 的图标组件。检查**分层图像**（在同一容器中堆叠的多个 `<img>` 或背景图像）。

6. **评估复杂度**——该部分包含多少个不同的子组件？不同的子组件是具有独特样式、结构和行为的元素（例如，卡片、导航项、搜索面板）。

### 步骤 2：编写组件规格文件

对于每个部分（或如果你要拆分的话，子组件），在 `docs/research/components/` 中创建一个规格文件。这不是可选的——每个构建器都必须有对应的规格文件。

**文件路径：** `docs/research/components/<component-name>.spec.md`

**模板：**

```markdown
# <ComponentName> 规格

## 概述
- **目标文件：** `src/components/<ComponentName>.tsx`
- **截图：** `docs/design-references/<screenshot-name>.png`
- **交互模型：** <static | click-driven | scroll-driven | time-driven>

## DOM 结构
<描述元素层级——什么包含什么>

## 计算样式（来自 getComputedStyle 的精确值）

### 容器
- display: ...
- padding: ...
- maxWidth: ...
- （每个相关属性及其精确值）

### <子元素 1>
- fontSize: ...
- color: ...
- （每个相关属性）

### <子元素 N>
...

## 状态与行为

### <行为名称，例如，“滚动触发的浮动模式”>
- **触发器：** <精确机制——滚动位置 50px，IntersectionObserver rootMargin "-30% 0px"，点击 .tab-button，悬停>
- **状态 A（之前）：** maxWidth: 100vw, boxShadow: none, borderRadius: 0
- **状态 B（之后）：** maxWidth: 1200px, boxShadow: 0 4px 20px rgba(0,0,0,0.1), borderRadius: 16px
- **过渡：** transition: all 0.3s ease
- **实现方法：** <CSS transition + scroll listener | IntersectionObserver | CSS animation-timeline | 等。>

### 悬停状态
- **<元素>：** <属性>：<之前> → <之后>，过渡：<值>

## 按状态内容（如适用）

### 状态：“Featured”
- 标题："..."
- 副标题："..."
- 卡片：[{ title, description, image, link }, ...]

### 状态：“Productivity”
- 标题："..."
- 卡片：[...]

## 资产
- 背景图像：`public/images/<file>.webp`
- 叠加图像：`public/images/<file>.png`
- 使用的图标：<ArrowIcon>, <SearchIcon> 来自 icons.tsx

## 文本内容（逐字）
<所有文本内容，从实时网站复制粘贴>

## 响应式行为
- **桌面端（1440px）：** <布局描述>
- **平板端（768px）：** <哪些发生变化——例如，“保持 2 列，间隙减小到 16px">
- **移动端（390px）：** <哪些发生变化——例如，“堆叠为单列，图像全宽">
- **断点：** 布局在 ~<N>px 处切换
```

填写每个部分。如果某部分不适用（例如，静态页脚没有状态），写“N/A”——但在将“状态与行为”标记为 N/A 之前要三思。即使是页脚也可能在链接上有悬停状态。

### 步骤 3：分发构建器

根据复杂度，在工作树中分发构建器代理：

**简单部分**（1-2 个子组件）：一个构建器代理获得整个部分。

**复杂部分**（3 个或更多不同的子组件）：将其拆分。每个子组件一个代理，外加一个代理用于导入它们的节包裹器。由于包裹器依赖于子组件，子组件构建器先执行。

**每个构建器代理接收的内容：**
- 其组件规格文件的完整内容（内联在提示中——不要说“去读规格文件”）
- `docs/design-references/` 中部分截图的路径
- 要导入哪些共享组件（`icons.tsx`, `cn()`, shadcn 原语）
- 目标文件路径（例如，`src/components/HeroSection.tsx`）
- 指示在结束前使用 `npx tsc --noEmit` 进行验证
- 对于响应式行为：具体的断点值以及哪些发生变化

**不要等待。** 一旦你分发了一个部分的构建器，立即继续提取下一个部分。构建器在他们的分支中并行工作，同时你继续提取。

### 步骤 4：合并

当构建器代理完成其工作时：
- 将他们的工作树分支合并到 main
- 你对每个代理构建的内容有完整上下文，因此智能解决任何冲突
- 每次合并后，验证构建是否仍然通过：`npm run build`
- 如果合并引入类型错误，立即修复它们

提取 → 规格 → 分发 → 合并循环继续，直到所有部分都构建完毕。

## 第 4 阶段：页面组装

所有部分构建并合并后，在 `src/app/page.tsx` 中将所有内容连接起来：

- 导入所有部分组件
- 根据你的拓扑文档实现页面级布局（滚动容器、列结构、粘性定位、z-index 层叠）
- 将真实内容连接到组件 props
- 实现页面级行为：滚动捕捉、滚动驱动动画、暗到亮过渡、相交观察器、平滑滚动（Lenis 等）
- 验证：`npm run build` 干净通过

## 第 5 阶段：视觉 QA 差异

组装后，不要宣布克隆完成。获取并排比较截图：

1. 并排打开原始网站和你的克隆（或在相同的视口宽度下截图）
2. 按部分从上到下比较，在桌面端（1440px）
3. 在移动端（390px）再次比较
4. 对于发现的每个差异：
   - 检查组件规格文件——值是否正确提取？
   - 如果规格错误：从浏览器 MCP 重新提取，更新规格，修复组件
   - 如果规格正确但构建器搞错了：修复组件以匹配规格
5. 测试所有交互行为：滚动页面，点击每个按钮/选项卡，悬停在交互元素上
6. 验证平滑滚动手感正确，头部过渡工作，选项卡切换工作，动画播放

只有在此视觉 QA 通过后，克隆才算完成。

## 分发前检查清单

在分发任何构建器代理之前，验证你可以勾选每个框。如果不能，回去提取更多内容。

- [ ] 规格文件已写入 `docs/research/components/<name>.spec.md`，所有部分已填写
- [ ] 规格中的每个 CSS 值都来自 `getComputedStyle()`，而非估算
- [ ] 已识别并记录交互模型（静态 / 点击 / 滚动 / 时间）
- [ ] 对于有状态的组件：每个状态的内容和样式都已捕获
- [ ] 对于滚动驱动的组件：触发阈值、前/后样式和过渡已记录
- [ ] 对于悬停状态：前/后值和过渡时序已记录
- [ ] 部分中的所有图像已识别（包括叠加和分层组合）
- [ ] 响应式行为已记录至少为桌面端和移动端
- [ ] 文本内容逐字来自网站，而非改写
- [ ] 构建器提示少于 ~150 行规格；如果超过，该部分需要拆分

## 不要做什么

这些是之前失败克隆的教训——每一个都导致了数小时的重做：

- **不要构建基于点击的选项卡，如果原始是滚动驱动的（或反之）。** 首先通过滚动确定交互模型。这是成本最高的错误 #1——它需要完全重写，而非 CSS 修复。
- **不要仅提取默认状态。** 如果有选项卡在加载时显示“Featured”，点击 Productivity, Creative, Lifestyle 并提取每个的卡片/内容。如果头部在滚动时变化，捕获位置 0 和位置 100+ 的样式。
- **不要漏掉叠加/分层图像。** 背景水彩 + 前景 UI 模型 = 2 张图像。检查每个容器的 DOM 树是否有多个 `<img>` 元素和定位叠加。
- **不要为实际上是视频/动画的内容构建模型组件。** 在构建视频所示内容的复杂 HTML 模型之前，检查部分是否使用 `<video>`、Lottie 或 canvas。
- **不要近似 CSS 类。** 如果计算值为 `18px` 而 `text-lg` 是 `18px/28px` 但实际行高为 `24px`，那么“它看起来像 `text-lg`”就是错的。提取精确值。
- **不要在一个单体提交中构建所有内容。** 此流程的目的正是在每个步骤进行验证构建的增量进展。
- **不要在构建器提示中引用文档。** 每个构建器在其提示中获得内联的 CSS 规格——绝不“参见 DESIGN_TOKENS.md 获取颜色”。构建器应完全不需要阅读外部文档。
- **不要跳过资产提取。** 没有真实的图像、视频和字体，无论 CSS 多么完美，克隆都会看起来假。
- **不要给构建器代理过大的范围。** 如果你正在编写构建器提示且因为部分复杂而变得很长，这是将其拆分为更小任务的信号。
- **不要将不相关的部分捆绑到一个代理中。** CTA 部分和页脚是具有不同设计的不同组件——不要把它们都交给一个代理并希望一切顺利。
- **不要跳过响应式提取。** 如果你只在桌面宽度检查，克隆将在平板和移动端破裂。在提取期间测试 1440、768 和 390。
- **不要忘记平滑滚动库。** 检查 Lenis（`.lenis` 类）、Locomotive Scroll 或类似项。默认浏览器滚动感觉明显不同，用户会立即注意到。
- **不要在没有规格文件的情况下分发构建器。** 规格文件强制穷尽提取并创建可审计的工件。跳过它意味着构建器只能获得你能从记忆中放入提示的内容。

## 完成

完成时，报告：
- 构建的总部分数
- 创建的总组件数
- 编写的总规格文件数（应与组件匹配）
- 下载的总资产数（图像、视频、SVG、字体）
- 构建状态（`npm run build` 结果）
- 视觉 QA 结果（任何剩余差异）
- 任何已知的差距或限制
