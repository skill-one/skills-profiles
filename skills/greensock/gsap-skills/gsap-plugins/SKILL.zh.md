---
name: gsap-plugins
description: GSAP官方技能，适用于GSAP插件——注册、ScrollToPlugin、ScrollSmoother、Flip、Draggable、Inertia、Observer、SplitText、ScrambleText、SVG及物理插件、CustomEase、EasePack、CustomWiggle、CustomBounce、GSDevTools。当用户询问GSAP插件、滚动到、翻转动画、可拖动、SVG绘制或插件注册时使用。
---

# GSAP 插件

## 何时使用此技能

在使用或审查使用 GSAP 插件的代码时应用：注册插件、scroll-to、翻转/FLIP 动画、可拖动元素、SVG（DrawSVG、MorphSVG、MotionPath）、文本（SplitText、ScrambleText）、物理效果、缓动插件（CustomEase、EasePack、CustomWiggle、CustomBounce）或 GSDevTools。ScrollTrigger 有自己的技能（gsap-scrolltrigger）。

**相关技能：** 核心补间使用 **gsap-core**；ScrollTrigger 使用 **gsap-scrolltrigger**；React 使用 **gsap-react**。

## 许可证 & 安装（重要）

每个 GSAP 插件都是 **免费** 的，包括商业用途。由于 [Webflow 收购了 GSAP](https://gsap.com/blog/webflow-GSAP/)，Club GSAP 已不再是付费层级，**没有插件需要会员资格、许可证密钥或认证令牌**—— 这包括以前仅限 Club 的插件（**SplitText**、**MorphSVG** 等）。

- ✅ 从公共 `gsap` npm 包安装所有内容：`npm install gsap`。所有插件都包含在内——导入它们作为 `gsap/SplitText`、`gsap/MorphSVGPlugin` 等。
- ❌ 不要生成带有 GreenSock 认证令牌的 `.npmrc`，建议使用私有 `npm.greensock.com` 仓库，或告诉用户注册 Club GSAP 以访问插件。这些说明已过时。

## 注册插件

每个插件注册一次，以便 GSAP（和打包器）知道要包含它。使用 **gsap.registerPlugin()** 注册项目中使用的每个插件：

```javascript
import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { Flip } from "gsap/Flip";
import { Draggable } from "gsap/Draggable";

gsap.registerPlugin(ScrollToPlugin, Flip, Draggable);
```

- ✅ 在任何补间或 API 调用中使用插件之前注册。
- ✅ 在 React 中，在顶层或应用程序中注册一次（例如，在第一次使用 useGSAP 之前）；不要在重新渲染的组件中注册。useGSAP 是一个需要在使用前注册的插件。

## 滚动

### ScrollToPlugin

通过动画滚动位置（窗口或可滚动元素）。用于“滚动到元素”或“滚动到位置”，而无需 ScrollTrigger。

```javascript
gsap.registerPlugin(ScrollToPlugin);

gsap.to(window, { duration: 1, scrollTo: { y: 500 } });
gsap.to(window, { duration: 1, scrollTo: { y: "#section", offsetY: 50 } });
gsap.to(scrollContainer, { duration: 1, scrollTo: { x: "max" } });
```

**ScrollToPlugin — 关键配置（scrollTo 对象）：**

| 选项 | 描述 |
|------|------|
| `x`, `y` | 目标滚动位置（数字），或 `"max"` 表示最大值 |
| `element` | 选择器或要滚动到的元素（用于 scroll-into-view） |
| `offsetX`, `offsetY` | 从目标位置起的像素偏移 |

### ScrollSmoother

平滑滚动包装器（平滑原生滚动）。需要 ScrollTrigger 和特定的 DOM 结构（内容包装器 + 平滑包装器）。当需要平滑、惯性式滚动时使用。查看 GSAP 文档进行设置；在注册 ScrollTrigger 之后注册。DOM 结构将如下所示：

```html
<body>
	<div id="smooth-wrapper">
		<div id="smooth-content">
			<!--- 所有内容都在这里 --->
		</div>
	</div>
	<!-- 位置固定的元素可以放在外面 --->
</body>
```

## DOM / UI

### Flip

使用 `Flip.getState()` 捕获状态，然后应用更改（例如，布局或类更改），然后使用 `Flip.from()` 从先前状态动画到新状态（FLIP：First, Last, Invert, Play）。在两个布局状态之间动画时使用（列表、网格、展开/折叠）。

```javascript
gsap.registerPlugin(Flip);

const state = Flip.getState(".item");
// 更改 DOM（重新排序、添加/删除、更改类）
Flip.from(state, { duration: 0.5, ease: "power2.inOut" });
```

**Flip — 关键配置（Flip.from 变量）：**

| 选项 | 描述 |
|------|------|
| `absolute` | 在翻转期间使用 `position: absolute`（默认：`false`） |
| `nested` | 当为 true 时，仅测量第一级子元素（更适合嵌套变换） |
| `scale` | 当为 true 时，缩放元素以适应（避免拉伸）；默认 `true` |
| `simple` | 当为 true 时，仅动画位置/缩放（更快，精度较低） |
| `duration`, `ease` | 标准补间选项 |

#### 更多信息

https://gsap.com/docs/v3/Plugins/Flip

### Draggable

使元素可拖动、可旋转或可抛出，使用鼠标/触摸。用于滑块、卡片、可重新排序的列表或任何拖动交互。

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);

Draggable.create(".box", { type: "x,y", bounds: "#container", inertia: true });
Draggable.create(".knob", { type: "rotation" });
```

**Draggable — 关键配置选项：**

| 选项 | 描述 |
|------|------|
| `type` | `"x"`、`"y"`、`"x,y"`、`"rotation"`、`"scroll"` |
| `bounds` | 元素、选择器或 `{ minX, maxX, minY, maxY }` 以限制拖动 |
| `inertia` | `true` 以启用抛出/惯性（需要 InertiaPlugin） |
| `edgeResistance` | 0–1；在拖动超出边界时的阻力 |
| `cursor` | 拖动期间的 CSS 光标 |
| `onDragStart`, `onDrag`, `onDragEnd` | 回调；接收事件和目标 |
| `onThrowUpdate`, `onThrowComplete` | 惯性激活时的回调 |

### Inertia (InertiaPlugin)

与 Draggable 一起工作，在释放后产生惯性，或跟踪任何对象任何属性的惯性/速度，以便它可以然后使用简单的补间无缝滑行到停止。在使用 `inertia: true` 时与 Draggable 注册：

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);
Draggable.create(".box", { type: "x,y", inertia: true });
```

或者跟踪属性的速率：
```javascript
InertiaPlugin.track(".box", "x");
```

然后使用 `"auto"` 继续当前速度并滑行到停止：

```javascript
gsap.to(obj, { inertia: { x: "auto" } });
```

### Observer

在设备之间标准化指针和滚动输入。用于滑动手势、滚动方向或自定义手势逻辑，而无需像 ScrollTrigger 那样直接绑定到滚动位置。

```javascript
gsap.registerPlugin(Observer);

Observer.create({
  target: "#area",
  onUp: () => {},
  onDown: () => {},
  onLeft: () => {},
  onRight: () => {},
  tolerance: 10
});
```

**Observer — 关键配置选项：**

| 选项 | 描述 |
|------|------|
| `target` | 要观察的元素或选择器 |
| `onUp`, `onDown`, `onLeft`, `onRight` | 当滑动手势/滚动通过容差在某个方向上时触发的回调 |
| `tolerance` | 检测方向之前像素；默认 10 |
| `type` | `"touch"`、`"pointer"` 或 `"wheel"`（默认：`"touch,pointer"`） |

## 文本

### SplitText

将元素的文本拆分为字符、单词和/或行（每个都在自己的元素中），用于交错或每个单位的动画。在逐字符、逐单词或逐行动画文本时使用。返回一个实例，其中包含 **chars**、**words**、**lines**（当 `mask` 设置时还有 **masks**）。使用 **revert()** 恢复原始标记，或让 **gsap.context()** 恢复。与 **gsap.context()**、**matchMedia()** 和 **useGSAP()** 集成。API：**SplitText.create(target, vars)**（target = 选择器、元素或数组）。

```javascript
gsap.registerPlugin(SplitText);

const split = SplitText.create(".heading", { type: "words, chars" });
gsap.from(split.chars, { opacity: 0, y: 20, stagger: 0.03, duration: 0.4 });
// 之后：split.revert() 或让 gsap.context() 清理 revert
```

使用 **onSplit()**（v3.13.0+），动画在每个拆分时运行，并在使用 **autoSplit** 时重新拆分时运行；从 **onSplit()** 返回的补间/时间轴允许 SplitText 清理并同步重新拆分的进度：

```javascript
SplitText.create(".split", {
  type: "lines",
  autoSplit: true,
  onSplit(self) {
    return gsap.from(self.lines, { y: 100, opacity: 0, stagger: 0.05, duration: 0.5 });
  }
});
```

**SplitText — 关键配置（SplitText.create vars）：**

| 选项 | 描述 |
|------|------|
| **type** | 逗号分隔的：`"chars"`、`"words"`、`"lines"`。默认 `"chars,words,lines"`。仅拆分需要的部分（例如，`"words, chars"` 如果不使用行）以提高性能。如果没有使用单词/行而仅拆分字符，请使用 **smartWrap: true** 以防止单词中间的行断裂。 |
| **charsClass**, **wordsClass**, **linesClass** | 每个拆分元素的 CSS 类。追加 `"++"` 以添加递增类（例如，`linesClass: "line++"` → `line1`、`line2`、…）。 |
| **aria** | `"auto"`（默认）、`"hidden"` 或 `"none"`。无障碍性：`"auto"` 在拆分元素上添加 `aria-label`，在行/单词/字符元素上添加 `aria-hidden`，以便屏幕阅读器读取标签；`"hidden"` 隐藏所有内容供阅读器读取；`"none"` 留下 aria 不变。如果嵌套链接/语义必须暴露，请使用 `"none"` 并加上屏幕阅读器专用的副本。 |
| **autoSplit** | 当为 `true` 时，在字体加载完成或元素宽度变化（并拆分行）时重新复位并重新拆分，避免错误的行断裂。**动画必须在 onSplit() 中创建**，以便它们针对新拆分的元素；从 **onSplit()** 返回动画以实现自动清理和重新拆分时的时间同步。 |
| **onSplit(self)** | 拆分完成时的回调（如果 **autoSplit** 为 `true`，则在每个重新拆分时触发）。接收 SplitText 实例。返回 GSAP 补间或时间轴将启用在重新拆分时自动复位/同步该动画。 |
| **mask** | `"lines"`、`"words"` 或 `"chars"`。将每个单位包装在具有 `overflow: clip` 的额外元素中，用于遮罩/揭示效果。仅一种类型；访问实例的 **masks** 数组（如果设置了类，可以使用类 `-mask`）。 |
| **tag** | 包装元素标签；默认 `"div"`。用于 `"span"` 以实现内联（注意：在某些浏览器中，内联元素的变换如旋转/缩放可能无法渲染）。 |
| **deepSlice** | 当为 `true`（默认），嵌套元素（例如 `<strong>`）跨越多行时会被细分，以防止行垂直拉伸。仅适用于拆分行。 |
| **ignore** | 选择器或要保留未拆分的元素（例如 `ignore: "sup"`）。 |
| **smartWrap** | 当仅拆分 **chars** 时，将单词包装在 `white-space: nowrap` span 中，以避免单词中间的行断裂。如果拆分单词或行，则忽略。默认 `false`。 |
| **wordDelimiter** | 单词边界：字符串（默认 `" "`）、正则表达式或 `{ delimiter: RegExp, replaceWith: string }` 用于自定义拆分（例如零宽度连接符用于标签，或非拉丁字符）。 |
| **prepareText(text, parent)** | 接收原始文本和父元素的函数；返回修改后的文本，然后再拆分（例如，为没有空格的语言插入换行标记）。 |
| **propIndex** | 当为 `true` 时，在每个拆分元素上添加一个包含索引的 CSS 变量（例如 `--word: 1`、`--char: 2`）。 |
| **reduceWhiteSpace** | 合并连续空格；默认 `true`。从 v3.13.0 开始也尊重换行符，并可以为 `<pre>` 插入 `<br>`。 |
| **onRevert** | 实例被复位时的回调。 |

**提示：** 仅拆分要动画的内容（例如，如果仅动画单词，则跳过字符）。对于自定义字体，在字体加载后拆分（例如 `document.fonts.ready.then(...)`）或使用 **autoSplit: true** 与 **onSplit()**。为了避免拆分字符时的 kerning 移动，请使用 CSS `font-kerning: none; text-rendering: optimizeSpeed;`。SplitText 不支持 SVG `<text>`。

**了解更多：** [SplitText](https://gsap.com/docs/v3/Plugins/SplitText/)

### ScrambleText

使用 scramble/glitch 效果动画文本。在用 scramble 揭示或过渡文本时使用。

```javascript
gsap.registerPlugin(ScrambleTextPlugin);

gsap.to(".text", {
  duration: 1,
  scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }
});
```

## SVG

### DrawSVG (DrawSVGPlugin)

通过动画 `stroke-dashoffset` / `stroke-dasharray` 来显示或隐藏 SVG 元素的描边。适用于 `<path>`、`<line>`、`<polyline>`、`<polygon>`、`<rect>`、`<ellipse>`。在“绘制”或“擦除”描边时使用。

**drawSVG 值：** 描述描边沿路径的**可见段**（起始和结束位置），而不是“随时间从 A 动画到 B”。格式：`"start end"` 以百分比或长度表示。示例：`"0% 100%"` = 完整描边；`"20% 80%"` = 描边仅在 20% 到 80% 之间（两端都有间隙）。补间从元素的**当前**段动画到**目标**段——例如 `gsap.to("#path", { drawSVG: "0% 100%" })` 从当前状态到完整描边。单个值（例如 `0`、`"100%"`）表示起始位置为 0：`"100%"` 等同于 `"0% 100%"`。 

**必需：** 元素必须有可见的描边——在 CSS 或作为 SVG 属性中设置 `stroke` 和 `stroke-width`；否则什么都不会绘制。

```javascript
gsap.registerPlugin(DrawSVGPlugin);

// 从无到完整描边
gsap.from("#path", { duration: 1, drawSVG: 0 });
// 或显式段：从 0–0 到 0–100%
gsap.fromTo("#path", { drawSVG: "0% 0%" }, { drawSVG: "0% 100%", duration: 1 });
// 描边仅在中间（两端有间隙）
gsap.to("#path", { duration: 1, drawSVG: "20% 80%" });
```

**注意事项：** 仅影响描边（不影响填充）。优先使用单段 `<path>` 元素；多段路径在某些浏览器中可能渲染异常。`<use>` 的内容无法视觉更改。**DrawSVGPlugin.getLength(element)** 和 **DrawSVGPlugin.getPosition(element)** 返回描边长度和当前位置。

**了解更多：** [DrawSVG](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin)

### MorphSVG (MorphSVGPlugin)

通过动画 `d` 属性（路径数据）将一个 SVG 形状变形为另一个形状。起始和结束形状不需要相同数量的点——MorphSVG 将其转换为三次贝塞尔曲线，并根据需要添加点。用于图标到图标的变形、形状过渡或基于路径的动画。适用于 `<path>`、`<polyline>` 和 `<polygon>`；`<circle>`、`<rect>`、`<ellipse>`、`<line>` 转换为内部或通过 **MorphSVGPlugin.convertToPath(selector | element)**（在 DOM 中替换元素为 `<path>`）。

**morphSVG 值：** 可以是 **选择器**（例如 `"#lightning"`）、**元素**、**原始路径数据**（例如 `"M47.1,0.8 73.3,0.8..."`），或对于多边形/多段线，**点字符串**（例如 `"240,220 240,70 70,70 70,220"`）。对于完整配置，使用 **对象形式**，其中 **shape** 是唯一必需的属性。

```javascript
gsap.registerPlugin(MorphSVGPlugin);

// 如果需要，首先将原始类型转换为路径：
MorphSVGPlugin.convertToPath("circle, rect, ellipse, line");

gsap.to("#diamond", { duration: 1, morphSVG: "#lightning", ease: "power2.inOut" });
// 对象形式：
gsap.to("#diamond", {
  duration: 1,
  morphSVG: { shape: "#lightning", type: "rotational", shapeIndex: 2 }
});

```

**MorphSVG — 关键配置（morphSVG 对象）：**

| 选项 | 描述 |
|------|------|
| **shape** | _(必需)_ 目标形状：选择器、元素或原始路径字符串。 |
| **type** | `"linear"` (默认) 或 `"rotational"`。Rotational 使用角度/长度插值，可以避免变形过程中的折角；当线性效果不理想时尝试使用。 |
| **map** | 段落如何匹配：`"size"` (默认)、`"position"` 或 `"complexity"`。当起始和结束段落不匹配时使用；如果没有有效，则拆分为多个路径并逐个变形。 |
| **shapeIndex** | 指向起始路径映射到结束路径第一个点的偏移量 (避免形状“交叉”或反转)。单段路径使用数字；**数组**用于多段 (例如 `[5, 1, -8]`)。负值反转该段。使用 **shapeIndex: "log"** 一次记录自动计算的值，然后将数字/数组粘贴到补间动画中。**findShapeIndex(start, end)** (单独工具) 提供交互式界面查找合适的值。仅适用于闭合路径。 |
| **smooth** | (v3.14+) 添加平滑点。数字 (例如 `80`)、"auto"，或对象：`{ points: 40 \| "auto", redraw: true \| false, persist: true \| false }`。`redraw: false` 保留原始锚点 (完美保真度，间距不均匀)。`persist: false` 在补间结束时移除添加的点。当默认变形看起来锯齿状或不自然时使用。 |
| **curveMode** | 布尔值 (v3.14+)。插值控制柄角度/长度而不是原始 x/y 以避免曲线上的折角。如果变形在变形中途有折角，尝试使用。 |
| **origin** | **type: "rotational"** 的旋转原点。字符串：`"50% 50%"` (默认) 或 `"20% 60%, 35% 90%"` 用于不同的起始/结束原点。 |
| **precision** | 输出路径数据的十进制位数；默认 `2`。 |
| **precompile** | 预计算路径字符串的数组 (或使用 **precompile: "log"** 一次，从控制台复制)。跳过昂贵的启动计算；用于非常复杂的变形。仅适用于 `<path>` (先转换多边形/折线)。 |
| **render** | 每次更新时调用的函数 (例如绘制到画布)。RawPath 是一个段落数组 (每个段落 = 交替 x,y 三次贝塞尔坐标的数组)。 |
| **updateTarget** | 使用 **render** (例如仅画布) 时，设置 **updateTarget: false** 以防止原始 `<path>` 更新。**MorphSVGPlugin.defaultUpdateTarget** 设置默认值。 |

**工具：** **MorphSVGPlugin.convertToPath(selector | element)** 将圆/矩形/椭圆/线/多边形/折线转换为 DOM 中的 `<path>`。**MorphSVGPlugin.rawPathToString(rawPath)** 和 **stringToRawPath(d)** 在路径字符串和原始数组之间转换。插件在目标上存储原始 `d` (例如用于反向补间：`morphSVG: "#originalId"` 或相同元素)。

**提示：** 对于扭曲或反转的变形，设置 **shapeIndex** (使用 `"log"` 或 findShapeIndex())。对于多段路径，**shapeIndex** 是一个数组 (每段一个值)。仅在第一帧缓慢时预编译；它不会修复变形过程中的卡顿 (如果需要，简化 SVG 或减小尺寸)。

**了解更多：** [MorphSVG](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin)

### MotionPath (MotionPathPlugin)

沿 SVG 路径动画元素。当沿路径移动对象时使用 (例如曲线或自定义路线)。

```javascript
gsap.registerPlugin(MotionPathPlugin);

gsap.to(".dot", {
  duration: 2,
  motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5] }
});
```

**MotionPath — 关键配置 (motionPath 对象)：**

| 选项 | 描述 |
|------|------|
| `path` | SVG 路径元素、选择器或路径数据字符串 |
| `align` | 路径元素或选择器，用于对齐目标 |
| `alignOrigin` | `[x, y]` 原点 (0–1)；默认 `[0.5, 0.5]` |
| `autoRotate` | 旋转元素以跟随路径切线 |
| `curviness` | 0–2；路径平滑度 |

### MotionPathHelper

MotionPath 的可视化编辑器 (对齐、偏移)。开发期间用于调整路径对齐。

```javascript
gsap.registerPlugin(MotionPathPlugin, MotionPathHelperPlugin);

const helper = MotionPathHelper.create(".dot", "#path", { end: 0.5 });
// 在 UI 中调整，然后在动画中使用 helper.path 或 helper.getProgress()
```

## 缓动

### CustomEase

自定义缓动曲线 (三次贝塞尔或 SVG 路径)。当内置缓动不足时使用。基本用法在 gsap-core 中涵盖；在使用时注册：

```javascript
gsap.registerPlugin(CustomEase);
const ease = CustomEase.create("name", ".17,.67,.83,.67");
gsap.to(".el", { x: 100, ease: ease, duration: 1 });
```

### EasePack

添加更多命名缓动 (例如 SlowMo, RoughEase, ExpoScaleEase)。注册并在补间中使用缓动名称。

### CustomWiggle

摇摆/抖动缓动。当值应该“摇摆” (多次振荡) 时使用。

### CustomBounce

可配置强度的弹跳式缓动。

## 物理

### Physics2D (Physics2DPlugin)

2D 物理 (速度、角度、重力)。当使用简单物理动画时使用 (例如抛射物、弹跳)。

```javascript
gsap.registerPlugin(Physics2DPlugin);

gsap.to(".ball", {
  duration: 2,
  physics2D: {
    velocity: 250,
    angle: 80,
    gravity: 500
  }
});
```

### PhysicsProps (PhysicsPropsPlugin)

将物理应用于属性值。用于物理驱动的属性动画。

```javascript
gsap.registerPlugin(PhysicsPropsPlugin);

gsap.to(".obj", {
  duration: 2,
  physicsProps: {
    x: { velocity: 100, end: 300 },
    y: { velocity: -50, acceleration: 200 }
  }
});
```

## 开发

### GSDevTools

用于滚动时间轴、切换动画和调试的 UI。仅用于开发；不要发布。注册并使用时间轴引用创建实例。

```javascript
gsap.registerPlugin(GSDevTools);
GSDevTools.create({ animation: tl });
```

## 其他

### Pixi (PixiPlugin)

将 GSAP 与 PixiJS 集成，用于动画 Pixi 显示对象。当使用 GSAP 动画 Pixi 对象时注册。

```javascript
gsap.registerPlugin(PixiPlugin);

const sprite = new PIXI.Sprite(texture);
gsap.to(sprite, { pixi: { x: 200, y: 100, scale: 1.5 }, duration: 1 });
```

## 最佳实践

- ✅ 使用 **gsap.registerPlugin()** 在首次使用前注册每个插件。
- ✅ 使用 **Flip.getState()** → DOM 变更 → **Flip.from()** 进行布局过渡；使用 **Draggable** + **InertiaPlugin** 进行带惯性的拖动。
- ✅ 组件卸载或元素移除时，还原插件实例 (例如 `SplitTextInstance.revert()`)。

## 不要

- ❌ 在未注册前在补间或 API 中使用插件 (**gsap.registerPlugin()**)。
- ❌ 将 GSDevTools 或仅开发插件发布到生产环境。

### 了解更多

https://gsap.com/docs/v3/Plugins/
