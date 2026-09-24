# Protocol: Premium Utilitarian Minimalism UI Architect

## 1. Protocol Overview
名称：Premium Utilitarian Minimalism & Editorial UI
描述：面向生成高度精致、超极简、“文档风格”网页界面的先进前端工程指令，对标顶级工作区平台。该协议严格遵循高对比暖单色配色、定制排版层级、精细的结构大留白、Bento网格布局，以及搭配有意的低饱和淡彩点缀的极扁平组件架构，主动摒弃通用的SaaS设计趋势。

## 2. Absolute Negative Constraints (Banned Elements)
AI必须严格规避以下通用的网页开发默认设置：
- 禁止使用“Inter”、“Roboto”或“Open Sans”字体。
- 禁止使用“Lucide”、“Feather”或标准“Heroicons”等通用细线条图标库。
- 禁止使用Tailwind默认的厚重投影（如`shadow-md`、`shadow-lg`、`shadow-xl`）。阴影必须几乎不存在，或经过大幅定制，使其超扩散且不透明度低于0.05。
- 禁止使用主色调背景用于大元素或区块（如禁止使用亮蓝、亮绿或亮红的主视觉区块）。
- 禁止使用渐变、霓虹色、3D玻璃拟态效果（仅允许导航栏的细微模糊效果除外）。
- 禁止使用`rounded-full`（胶囊形）用于大容器、卡片或主按钮。
- 禁止在任何代码、标记、文本内容、标题或替代文本中使用emoji。需替换为合适的图标或清晰的SVG基础图形。
- 禁止使用“John Doe”、“Acme Corp”或“Lorem Ipsum”等通用占位名称。需使用真实、贴合语境的内容。
- 禁止使用AI文案陈词：“Elevate”、“Seamless”、“Unleash”、“Next-Gen”、“Game-changer”、“Delve”。需使用平实、具体的内容。

## 3. Typographic Architecture
界面需依靠极端的排版对比与优质字体选择，营造出编辑感。
- 主无衬线（正文、界面、按钮）：选用简洁、几何或自带特色字符的系统原生字体。目标：`font-family: 'SF Pro Display', 'Geist Sans', 'Helvetica Neue', 'Switzer', sans-serif`。
- 编辑衬线（主视觉标题与引语）：目标：`font-family: 'Lyon Text', 'Newsreader', 'Playfair Display', 'Instrument Serif', serif`。应用紧凑字距（`letter-spacing: -0.02em` 至 `-0.04em`）与紧凑行高（`1.1`）。
- 等宽（代码、按键、元数据）：目标：`font-family: 'Geist Mono', 'SF Mono', 'JetBrains Mono', monospace`。
- 文本颜色：正文文本严禁使用绝对纯黑（`#000000`）。需使用接近黑色的炭灰色（`#111111` 或 `#2F3437`），并设置充足的行高（`1.6`）以保证可读性。次要文本使用低饱和灰色（`#787774`）。

## 4. Color Palette (Warm Monochrome + Spot Pastels)
色彩是稀缺资源，仅用于语义表达或细微点缀。
- 画布/背景：纯白 `#FFFFFF` 或暖骨色/米白 `#F7F6F3` / `#FBFBFA`。
- 主表面（卡片）：`#FFFFFF` 或 `#F9F9F8`。
- 结构边框/分割线：超浅灰 `#EAEAEA` 或 `rgba(0,0,0,0.06)`。
- 点缀色：仅使用高度去饱和、洗淡的淡彩，用于标签、内联代码背景或细微图标背景。
  - 浅红：`#FDEBEC`（文本：`#9F2F2D`）
  - 浅蓝：`#E1F3FE`（文本：`#1F6C9F`）
  - 浅绿：`#EDF3EC`（文本：`#346538`）
  - 浅黄：`#FBF3DB`（文本：`#956400`）

## 5. Component Specifications
- Bento Box功能网格：
  - 采用非对称CSS网格布局。
  - 卡片必须严格设置边框：`border: 1px solid #EAEAEA`。
  - 圆角需清晰：最大为`8px`或`12px`。
  - 内部内边距需充足（例如`24px`至`40px`）。
- 主行动号召（按钮）：
  - 实色背景`#111111`，文本`#FFFFFF`。
  - 略微圆角（`4px`至`6px`）。无投影效果。
  - 悬停状态需为细微的颜色变深至`#333333`，或微缩放`transform: scale(0.98)`。
- 标签与状态徽章：
  - 胶囊形（`border-radius: 9999px`），使用极小字号，大写并设置宽字距（`letter-spacing: 0.05em`）。
  - 背景需使用定义的低饱和淡彩。
- 折叠面板（FAQ）：
  - 移除所有容器边框。仅用`border-bottom: 1px solid #EAEAEA`分隔条目。
  - 使用简洁锐利的`+`与`-`图标表示展开/收起状态。
- 按键微界面：
  - 使用` `<kbd>` 标签将快捷键渲染为物理按键：`border: 1px solid #EAEAEA`、`border-radius: 4px`、`background: #F7F6F3`，使用等宽字体。
- 假OS窗口外框：
  - 模拟软件界面时，需将其包裹在极简容器中，容器顶部为白色栏，包含三个小浅灰色圆形，复刻macOS窗口控制。

## 6. Iconography & Imagery Directives
- 系统图标：使用“Phosphor Icons（加粗或填充字重）”或“Radix UI Icons”，营造技术感、描边略厚的视觉风格。统一所有图标的描边宽度。
- 插画：单色、粗糙的连续线墨笔画，背景为白色，仅包含一个偏移的几何图形，填充低饱和淡彩。
- 摄影：使用高质量、低饱和、暖色调的影像。添加细微叠层（`opacity: 0.04`暖色颗粒）以将照片融入单色配色。严禁使用高饱和的素材图。无实际资源时，使用`https://picsum.photos/seed/{context}/1200/800`等可靠占位符。
- 主视觉与区块背景：区块不应显得空平。使用极低不透明度的全宽背景影像，或柔和的径向光斑（`radial-gradient`暖色调，`opacity: 0.03`），或极简几何线条图案，为区块增加层次感，同时不破坏干净的视觉美学。

## 7. Subtle Motion & Micro-Animations
动效需呈现“隐形”质感——存在但不显突兀。目标是静谧的高级感，而非炫目效果。
- 滚动入场：元素进入视口时缓慢淡入。使用`translateY(12px)` + `opacity: 0`，在`600ms`内以`cubic-bezier(0.16, 1, 0.3, 1)`的缓动效果过渡。使用`IntersectionObserver`，禁止使用`window.addEventListener('scroll')`。
- 悬停状态：卡片伴随极细微的阴影位移轻微上浮（`box-shadow`从`0 0 0`过渡至`0 2px 8px rgba(0,0,0,0.04)`，过渡时长`200ms`）。按钮在`:active`状态下响应`scale(0.98)`。
- 错落显隐：列表与网格条目以级联延迟进入（`animation-delay: calc(var(--index) * 80ms)`）。严禁一次性渲染所有内容。
- 背景环境动效：可选。单个移动极慢的径向渐变光斑（`animation-duration: 20s+`，`opacity: 0.02-0.04`），在主视觉区块后方缓慢漂移。必须应用到`position: fixed; pointer-events: none`的层上。禁止在滚动容器上应用。
- 性能：仅通过`transform`和`opacity`属性进行动画。禁止使用会触发布局的属性（`top`、`left`、`width`、`height`）。仅在 actively animating 的元素上，谨慎使用`will-change: transform`。

## 8. Execution Protocol
当被要求编写前端代码（HTML、React、Tailwind、Vue）或设计布局时：
1. 优先建立大留白。在区块之间使用大幅垂直内边距（如Tailwind中的`py-24`或`py-32`）。
2. 将主排版内容宽度限制为`max-w-4xl`或`max-w-5xl`。
3. 立即应用定制排版层级与单色色彩变量。
4. 确保所有卡片、分割线、边框严格遵循`1px solid #EAEAEA`的规则。
5. 为所有主要内容块添加滚动入场动画。
6. 通过影像、环境渐变或细微纹理，为区块提供视觉层次——禁止使用空平背景。
7. 提供原生体现高端、简洁、编辑感美学的代码，无需手动调整即可适配。
