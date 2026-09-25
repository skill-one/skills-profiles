# 克隆网站

你即将逆向工程并重建 **$ARGUMENTS**，以像素级完美的克隆形式呈现。

当提供多个URL时，尽可能并行处理它们，同时将每个网站的提取工件隔离在专用文件夹中（例如，`docs/research/<hostname>/`）。

这不是一个两阶段过程（先检查后构建）。你是一个**在现场巡视的工头**——当你检查页面的每个部分时，你会将详细的规范写入文件，然后将该文件交给一个拥有所有必要资源的专家构建代理。提取和构建是并行进行的，但提取过程是细致的，并产生可审计的工件。

## 范围默认值

目标是 `$ARGUMENTS` 解析到的页面。精确克隆该URL下可见的内容。除非用户另有说明，否则使用这些默认值：

- **保真度级别：** 像素级完美——颜色、间距、排版、动画完全匹配
- **范围内：** 视觉布局和样式、组件结构和交互、响应式设计、用于演示目的的模拟数据
- **范围外：** 真实后端/数据库、认证、实时功能、SEO优化、无障碍性审核
- **自定义：** 无——纯粹的模拟

如果用户提供了额外的说明（特定的保真度级别、自定义项、额外上下文），请优先考虑这些默认值。

## 起飞前检查

1. **需要浏览器自动化。** 检查可用的浏览器MCP工具（Chrome MCP、Playwright MCP、Browserbase MCP、Puppeteer MCP等）。使用可用的工具——如果存在多个，优先使用Chrome MCP。如果没有检测到，请询问用户他们拥有的浏览器工具以及如何连接它。没有浏览器自动化，这项技能无法工作。
2. 解析 `$ARGUMENTS` 作为一个或多个URL。规范化并验证每个URL；如果任何URL无效，请在继续之前要求用户更正它们。对于每个有效的URL，验证它是否可以通过你的浏览器MCP工具访问。
3. 验证基础项目构建：`npm run build`。Next.js + shadcn/ui + Tailwind v4脚手架应该已经就位。如果没有，请告诉用户先设置它。
4. 如果输出目录不存在，则创建它们：`docs/research/`、`docs/research/components/`、`docs/design-references/`、`scripts/`。对于多个克隆，还准备每个站点的文件夹，如`docs/research/<hostname>/`和`docs/design-references/<hostname>/`。
5. 当在一个命令中处理多个网站时，可以选择确认是否并行运行（如果资源允许，则推荐）或顺序运行以避免过载。

## 指导原则

这些是区分成功的克隆和“差不多就行”的混乱的真理。内化它们——它们应该指导你做出的每一个决定。

### 1. 完整性胜过速度

每个构建代理必须收到**所有**它需要完美完成工作的资源：截图、确切的CSS值、下载的资产（带本地路径）、真实文本内容、组件结构。如果构建代理必须猜测任何东西——颜色、字体大小、填充值——你就失败了提取。花额外一分钟提取更多属性，而不是发送不完整的简报。

### 2. 小任务，完美结果

当代理得到“构建整个功能部分”时，它会忽略细节——它会估算间距、猜测字体大小，并产生“差不多就行”但明显错误的东西。当它得到一个具有确切CSS值的单一聚焦组件时，它会每次都做到完美。

查看每个部分并判断其复杂性。一个简单的横幅，带有标题和按钮？一个代理。一个复杂的部分，有3种不同的卡片变体，每种都有独特的悬停状态和内部布局？每个卡片变体一个代理，再加上一个部分包装器代理。如有疑问，请将其拆分。

**复杂性预算规则：** 如果构建提示超过~150行的规范内容，该部分对于单个代理来说太复杂了。将其拆分成更小的部分。这是一个机械检查——不要用“但它所有内容都相关”来覆盖它。

### 3. 真实内容，真实资产

从实时网站提取实际文本、图像、视频和SVG。这是一个克隆，不是模拟。使用`element.textContent`，下载每个`<img>`和`<video>`，将内联`<svg>`元素提取为React组件。只有在某物明显是服务器生成的并且每个会话都是独特的情况下，你才生成内容。

**分层资产很重要。** 看起来像是一个图像的部分通常是多个图层——一个背景水彩/渐变，一个前景UI模拟PNG，一个覆盖图标。检查每个容器的完整DOM树，并列举其中所有的`<img>`元素和背景图像，包括绝对定位的覆盖层。遗漏一个覆盖图像会使克隆看起来空荡荡的，即使背景是正确的。

### 4. 先构建基础

在构建任何东西之前，直到存在基础：全局CSS与目标网站的设计令牌（颜色、字体、间距），内容结构的TypeScript类型，以及全局资产（字体、favicon）。这是顺序的，不容商议。这之后的一切都可以并行。

### 5. 提取它看起来如何以及它如何行为

网站不是截图——它是一个活生生的东西。元素会移动、改变、出现和消失，以响应滚动、悬停、点击、调整大小和时间。如果你只提取每个元素的静态CSS，你的克隆在截图时会看起来很完美，但在有人实际使用它时会觉得死气沉沉。

对于每个元素，提取它的**外观**（通过`getComputedStyle()`获取的确切计算CSS）和它的**行为**（什么会改变，什么会触发改变，以及过渡如何发生）。不是“它看起来像16px”——提取实际计算值。不是“导航在滚动时改变”——记录确切的触发器（滚动位置、IntersectionObserver阈值、视口交集），以及前后状态（两套CSS值）和过渡（持续时间、缓动、CSS过渡与JS驱动与CSS `animation-timeline`）。

要注意的行为示例——这些是说明性的，不是详尽的。页面可能会做不在列表中的事情，你必须捕捉到它们：
- 一个在滚动到某个阈值后缩小、改变背景或获得阴影的导航栏
- 当它们进入视口时动画进入视图的元素（淡入、滑入、交错延迟）
- 在滚动时自动对齐到位置的章节（`scroll-snap-type`）
- 移动速度与滚动不同的视差层
- 悬停状态动画（不只是改变——过渡持续时间和缓动很重要）
- 带有进入/退出动画的下拉菜单、模态框、手风琴
- 滚动驱动的进度指示器或不透明度过渡
- 自动播放的轮播或循环内容
- 页面部分之间的深色到浅色（或任何主题）过渡
- **循环的选项卡/药丸内容**——按钮切换可见卡片集并带有过渡
- **滚动驱动的选项卡/手风琴切换**——当内容滚动时自动更改的侧边栏（IntersectionObserver，不是点击处理程序）
- **平滑滚动库**（Lenis、Locomotive Scroll）——检查`.lenis`类或滚动容器包装器

### 6. 在构建之前识别交互模型

这是克隆中最昂贵的错误：构建基于点击的UI，而原始是滚动驱动的，反之亦然。在为交互部分编写任何构建提示之前，你必须明确回答：**这个部分是由点击、滚动、悬停、时间还是某种组合驱动的？**

如何确定：
1. **先不点击。** 缓慢滚动通过该部分，观察当您滚动时是否有东西会自行改变。
2. 如果它们会改变，它是滚动驱动的。提取机制：`IntersectionObserver`、`scroll-snap`、`position: sticky`、`animation-timeline`或JS滚动监听器。
3. 如果滚动时没有变化，那么点击/悬停测试交互。
4. 明确记录每个部分的交互模型：**交互模型：滚动驱动，使用IntersectionObserver**或**交互模型：点击切换，带有不透明度过渡**。

一个带有粘性侧边栏和滚动内容面板的部分与一个点击切换内容的选项卡界面根本不同。做错了意味着完全重写，而不是CSS微调。

### 7. 提取每个状态，而不仅仅是默认状态

许多组件有多个视觉状态——选项卡栏根据每个选项卡显示不同的卡片，页眉在滚动位置0与100处看起来不同，卡片有悬停效果。你必须提取所有状态，而不仅仅是页面加载时可见的内容。

对于选项卡/状态内容：
- 点击每个选项卡/按钮（通过浏览器MCP）
- 提取每个状态的内容、图像和卡片数据
- 记录哪些内容属于哪个状态
- 注意状态之间的过渡动画（不透明度、滑入、淡入等）

对于滚动依赖元素：
- 在滚动位置0（初始状态）捕获计算样式
- 滚动到触发阈值后再次捕获计算样式（滚动状态）
- 比较两个以确定哪些CSS属性发生变化
- 记录过渡CSS（持续时间、缓动、属性）
- 记录确切的触发阈值（滚动位置（像素），或视口交集比例）

### 8. 规范文件是事实来源

每个组件在`docs/research/components/`中都有一个规范文件，在发送任何构建代理之前。该文件是提取工作和构建代理之间的合同。构建代理在其提示中接收规范文件的内容——该文件也作为可审计的工件持久化，用户（或你）可以在出现问题时进行审查。

规范文件不是可选的。它不是一种“有好处”的东西。如果你在发送构建代理之前没有先编写规范文件，你正在基于你能从浏览器MCP会话中记住的内容发送不完整的指令，构建代理会猜测以填补空白。

### 9. 构建必须始终可以编译

每个构建代理必须在完成前验证`npx tsc --noEmit`通过。合并工作树后，你验证`npm run build`通过。一个损坏的构建永远不会被接受，即使只是暂时的。

## 第一阶段：侦察

使用浏览器MCP导航到目标URL。

### 截图
- 在桌面（1440px）和移动（390px）视口下**全页截图**
- 保存到`docs/design-references/`，使用描述性名称
- 这些是你的主参考——构建代理将稍后接收特定部分的裁剪/截图

### 全局提取
在执行任何其他操作之前，从页面中提取以下内容：

**字体**——检查`<link>`标签以查找Google字体或自托管字体。检查关键元素（标题、正文、代码、标签）的计算`font-family`。记录实际使用的每个字体、权重和样式。使用`next/font/google`或`next/font/local`在`src/app/layout.tsx`中配置它们。

**颜色**——从页面计算样式中提取网站的颜色调色板。使用目标网站的实际颜色更新`src/app/globals.css`中的`:root`和`.dark` CSS变量块。将它们映射到shadcn的令牌名称（背景、前景、主要、柔和等），其中适用。为不映射到shadcn令牌的颜色添加自定义属性。

**Favicons & Meta**——下载favicons、apple-touch-icons、OG图像、webmanifest到`public/seo/`。更新`layout.tsx`元数据。

**全局UI模式**——识别任何全站CSS或JS：自定义滚动条隐藏、页面容器的`scroll-snap`、全局关键帧动画、背景滤镜、用作覆盖层的渐变、**平滑滚动库**（Lenis、Locomotive Scroll——检查`.lenis`、`.locomotive-scroll`或自定义滚动容器类）。将它们添加到`globals.css`并注意需要安装的任何库。

### 强制交互扫描

这是一个在截图之后、在执行任何其他操作之前的专用过程。其目的是发现页面上的每个行为——其中许多行为在静态截图中是不可见的。

**滚动扫描：** 通过浏览器MCP缓慢滚动页面从顶部到底部。在每个部分，暂停并观察：
- 页眉的外观是否改变？记录触发位置
- 元素是否动画进入视图？记录哪些元素和动画类型
- 侧边栏或选项卡指示器是否在滚动时自动切换？记录机制
- 是否有滚动对齐点？记录哪些容器

**点击扫描：** 点击看起来可交互的每个元素：
- 每个按钮、选项卡、药丸、链接、卡片
- 记录发生的事情：内容是否改变？是否打开模态框？是否出现下拉菜单？
- 对于选项卡/药丸：点击每个并记录每个状态下的内容

**悬停扫描：** 将鼠标悬停在可能具有悬停状态的每个元素上：
- 按钮、卡片、链接、图像、导航项
- 记录发生的变化：颜色、缩放、阴影、下划线、不透明度

**响应式扫描：** 通过浏览器MCP在3个视口宽度下测试：
- 桌面：1440px
- 平板电脑：768px
- 手机：390px
- 在每个宽度下，注意哪些部分改变布局（列→堆叠、侧边栏消失等），以及大约在哪个断点处发生改变。

将所有发现保存到`docs/research/BEHAVIORS.md`。这是你的行为圣经——在编写每个组件规范时参考它。

### 页面拓扑
从顶部到底部绘制页面的每个独立部分。给每个一个工作名称。记录：
- 他们的视觉顺序
- 哪些是固定/粘性覆盖层与流内容
- 整体页面布局（滚动容器、列结构、z-index层）
- 部分之间的依赖关系（例如，一个覆盖所有内容的浮动导航）
- 每个部分的**交互模型**（静态、点击驱动、滚动驱动、时间驱动）

将此保存为`docs/research/PAGE_TOPOLOGY.md`——它将成为你的装配蓝图。

## 第二阶段：基础构建

这是顺序的。你自己执行它（而不是委托给代理），因为它涉及许多文件：

1. **更新字体**在`layout.tsx`中，以匹配目标网站的实际字体
2. **更新globals.css**，以包含目标网站的颜色令牌、间距值、关键帧动画、实用类和任何**全局滚动行为**（Lenis、平滑滚动CSS、body上的`scroll-snap`）
3. **创建TypeScript接口**在`src/types/`中，用于你观察到的内容结构
4. **提取SVG图标**——找到页面上的所有内联`<svg>`元素，去重，并保存为名为React组件的`src/components/icons.tsx`中的命名文件。按视觉功能命名它们（例如，`SearchIcon`、`ArrowRightIcon`、`LogoIcon`）。
5. **下载全局资产**——编写并运行一个Node.js脚本（`scripts/download-assets.mjs`），将页面上的所有图像、视频和其他二进制资产下载到`public/`。保留有意义的目录结构。
6. 验证：`npm run build`通过

### 资产发现脚本模式

使用浏览器MCP来枚举页面上的所有资产：

```javascript
// 通过浏览器MCP运行此脚本来发现所有资产
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

然后编写一个下载脚本，将所有内容下载到`public/`。使用批量并行下载（一次4个）和适当的错误处理。

## 第三阶段：组件规范和派遣

这是核心循环。对于页面拓扑中的每个部分（从上到下），你执行三个操作：**提取**、**编写规范文件**，然后**派遣构建代理**。

### 第一步：提取

对于每个部分，使用浏览器MCP提取所有内容：

1. **截取**该部分的独立截图（滚动到它，截取视口）。保存到`docs/design-references/`。

2. **提取CSS**对于部分中的每个元素。使用提取脚本——不要手动测量单个属性。每个组件容器运行一次，并捕获完整输出：

```javascript
// 每个组件提取——通过浏览器MCP运行
// 将SELECTOR替换为实际的CSS选择器
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
// 状态A：捕获当前状态的样式（例如，滚动位置0）
// 然后触发状态更改（滚动、点击、悬停通过浏览器MCP）
// 状态B：重新运行提取脚本，对同一元素
// A和B之间的差异就是行为规范
```

明确记录差异：**属性X从VALUE_A变为VALUE_B，由TRIGGER触发，过渡：TRANSITION_CSS。**

4. **提取真实内容**——所有文本、alt属性、aria标签、占位符文本。使用`element.textContent`对于每个文本节点。对于选项卡/状态内容，**点击每个选项卡并提取每个状态的内容**。

5. **识别此部分使用的资产**——哪些从`public/`下载的图像/视频，哪些来自`icons.tsx`的图标组件。检查**分层图像**（同一容器中的多个`<img>`或`background-images`堆叠）。
