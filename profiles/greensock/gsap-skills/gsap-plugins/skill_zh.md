# GSAP 插件

## 何时使用此技能

在使用或审查使用 GSAP 插件的代码时应用：注册插件、scroll-to、翻转/FLIP 动画、可拖动元素、SVG（DrawSVG、MorphSVG、MotionPath）、文本（SplitText、ScrambleText）、物理、缓动插件（CustomEase、EasePack、CustomWiggle、CustomBounce）或 GSDevTools。ScrollTrigger 有自己的技能（gsap-scrolltrigger）。

**相关技能：** 核心缓动使用 **gsap-core**；ScrollTrigger 使用 **gsap-scrolltrigger**；React 使用 **gsap-react**。

## 许可证与安装（重要）

每个 GSAP 插件都是**免费**的，包括商业用途。由于 [Webflow 收购 GSAP](https://gsap.com/blog/webflow-GSAP/)，Club GSAP 已不再是付费层级，**没有插件需要会员资格、许可证密钥或认证令牌**——这包括以前仅限 Club 的插件（**SplitText**、**MorphSVG** 等）。

- ✅ 从公共 `gsap` npm 包安装所有内容：`npm install gsap`。所有插件都包含在内——导入它们作为 `gsap/SplitText`、`gsap/MorphSVGPlugin` 等。
- ❌ 不要生成带有 GreenSock 认证令牌的 `.npmrc`、建议私有 `npm.greensock.com` 注册中心或告诉用户注册 Club GSAP 以访问插件。这些说明已过时。

## 注册插件

为每个插件注册一次，以便 GSAP（和打包器）知道要包含它。使用 **gsap.registerPlugin()** 在项目中使用的每个插件之前：

```javascript
import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { Flip } from "gsap/Flip";
import { Draggable } from "gsap/Draggable";

gsap.registerPlugin(ScrollToPlugin, Flip, Draggable);
```

- ✅ 在使用插件之前的任何缓动或 API 调用中注册。
- ✅ 在 React 中，在顶层或应用程序中注册一次（例如，在第一个 useGSAP 之前）；不要在重新渲染的组件中注册。useGSAP 是一个需要在使用前注册的插件。

## 滚动

### ScrollToPlugin

动画滚动位置（窗口或可滚动元素）。用于“滚动到元素”或“滚动到位置”，无需 ScrollTrigger。

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
| `element` | 选择器或元素，用于滚动到（用于 scroll-into-view） |
| `offsetX`, `offsetY` | 从目标位置偏移的像素 |

### ScrollSmoother

平滑滚动包装器（平滑原生滚动）。需要 ScrollTrigger 和特定的 DOM 结构（内容包装器 + 平滑包装器）。当需要平滑、惯性式滚动时使用。查看 GSAP 文档进行设置；在 ScrollTrigger 之后注册。DOM 结构将如下所示：

```html
<body>
	<div id="smooth-wrapper">
		<div id="smooth-content">
			<!--- 所有内容都在这里 --->
		</div>
	</div>
	<!-- position: fixed 元素可以放在外面 --->
</body>
```

## DOM / UI

### Flip

使用 `Flip.getState()` 捕获状态，然后应用更改（例如，布局或类更改），然后使用 `Flip.from()` 从先前状态动画到新状态（FLIP：First, Last, Invert, Play）。当在两个布局状态之间动画时使用（列表、网格、展开/折叠）。

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
| `nested` | 当为真时，仅测量子级的第一个级别（更适合嵌套转换） |
| `scale` | 当为真时，缩放元素以适应（避免拉伸）；默认 `true` |
| `simple` | 当为真时，仅动画化位置/缩放（更快，精度较低） |
| `duration`, `ease` | 标准缓动选项 |

#### 更多信息

https://gsap.com/docs/v3/Plugins/Flip

### Draggable

使元素可通过鼠标/触摸拖动、旋转或抛出。用于滑块、卡片、可重新排序的列表或任何拖动交互。

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

与 Draggable 一起使用，用于释放后的惯性，或跟踪任何对象任何属性的惯性/速度，以便它可以然后使用简单的缓动无缝滑行到停止。在使用 `inertia: true` 时与 Draggable 注册：

```javascript
gsap.registerPlugin(Draggable, InertiaPlugin);
Draggable.create(".box", { type: "x,y", inertia: true });
```

或者跟踪属性的速率：
```javascript
InertiaPlugin.track(".box", "x");
```

然后使用 `"auto"` 继续当前速率并滑行到停止：
```javascript
gsap.to(obj, { inertia: { x: "auto" } });
```

### Observer

跨设备标准化指针和滚动输入。用于滑动手势或自定义手势逻辑，而无需像 ScrollTrigger 那样直接绑定到滚动位置。

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
| `onUp`, `onDown`, `onLeft`, `onRight` | 在滑动手势/滚动通过容差时触发的回调 |
| `tolerance` | 检测方向之前像素；默认 10 |
| `type` | `"touch"`、`"pointer"` 或 `"wheel"`（默认：`"touch,pointer"`） |

## 文本

### SplitText

将元素的文本拆分为字符、单词和/或行（每个都在自己的元素中），用于交错或每个单位的动画。当逐字符、逐单词或逐行动画文本时使用。返回一个实例，其中包含 **chars**、**words**、**lines**（当 `mask` 设置时还有 **masks**）。使用 **revert()** 恢复原始标记，或让 **gsap.context()** 恢复。与 **gsap.context()**、**matchMedia()** 和 **useGSAP()** 集成。API：**SplitText.create(target, vars)**（target = 选择器、元素或数组）。

```javascript
gsap.registerPlugin(SplitText);

const split = SplitText.create(".heading", { type: "words, chars" });
gsap.from(split.chars, { opacity: 0, y: 20, stagger: 0.03, duration: 0.4 });
// 之后：split.revert() 或让 gsap.context() 清理 revert
```

使用 **onSplit()**（v3.13.0+），动画在每个拆分上运行，并在使用 **autoSplit** 时重新拆分时运行；从 **onSplit()** 返回缓动/时间轴，让 SplitText 清理并同步重新拆分的进度：

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
| **type** | 用逗号分隔：`"chars"`、`"words"`、`"lines"`。默认 `"chars,words,lines"`。仅拆分需要的部分（例如，`"words, chars"` 如果不使用行）以进行性能优化。如果没有使用单词/行而仅拆分字符，请使用 **smartWrap: true** 以防止奇特的行断裂。 |
| **charsClass**, **wordsClass**, **linesClass** | 每个拆分元素的 CSS 类。追加 `"++"` 以添加递增类（例如，`linesClass: "line++"` → `line1`、`line2`、…）。 |
| **aria** | `"auto"`（默认）、`"hidden"` 或 `"none"`。可访问性：`"auto"` 在拆分元素上添加 `aria-label`，在行/单词/字符元素上添加 `aria-hidden`，以便屏幕阅读器读取标签；`"hidden"` 隐藏所有内容以供阅读器读取；`"none"` 不更改 aria。如果必须暴露嵌套链接/语义，请使用 `"none"` 并加上屏幕阅读器专用的副本。 |
| **autoSplit** | 当为真时，在字体加载完成或元素宽度变化时（并且行被拆分），重新还原并重新拆分，以避免错误的行断裂。**动画必须在 onSplit() 内创建**，以便它们针对新拆分的元素；**返回** 动画以进行自动清理并在重新拆分时同步时间。 |
| **onSplit(self)** | 当拆分完成时（如果 **autoSplit** 为真，则在每个重新拆分时）的回调。接收 SplitText 实例。返回 GSAP 缓动或时间轴将启用在重新拆分时自动还原/同步该动画。 |
| **mask** | `"lines"`、`"words"` 或 `"chars"`。用额外的元素包装每个单位，带有 `overflow: clip` 以用于遮罩/揭示效果。仅一种类型；在实例的 **masks** 数组上访问包装器（如果设置了类，则使用类 `-mask`）。 |
| **tag** | 包装器元素标签；默认 `"div"`。用于 `"span"` 以实现内联（注意：在某些浏览器中，内联元素上的变换如旋转/缩放可能无法渲染）。 |
| **deepSlice** | 当为真（默认）时，将跨越多行的嵌套元素（例如 `<strong>`）细分为多个部分，以防止行垂直拉伸。仅适用于拆分行。 |
| **ignore** | 要保留未拆分的选择器或元素（例如 `ignore: "sup"`）。 |
| **smartWrap** | 当仅拆分 **chars** 时，用 `white-space: nowrap` span 包装单词，以避免单词中间的行断裂。如果拆分单词或行，则忽略。默认 `false`。 |
| **wordDelimiter** | 单词边界：字符串（默认 `" "`）、正则表达式或 `{ delimiter: RegExp, replaceWith: string }` 用于自定义拆分（例如零宽度连接符用于标签，或非拉丁字符）。 |
| **prepareText(text, parent)** | 接收原始文本和父元素的函数；在拆分之前返回修改后的文本（例如，为没有空格的语言插入换行标记）。 |
| **propIndex** | 当为真时，在每个拆分元素上添加带有索引的 CSS 变量（例如 `--word: 1`、`--char: 2`）。 |
| **reduceWhiteSpace** | 压缩连续空格；默认 `true`。从 v3.13.0 开始也尊重行断裂，并可以插入 `<br>` 用于 `<pre>`。 |
| **onRevert** | 实例还原时的回调。 |

**提示：** 仅拆分要动画化的内容（例如，如果仅动画化单词，则跳过字符）。对于自定义字体，在字体加载后拆分（例如 `document.fonts.ready.then(...)`）或使用 **autoSplit: true** 与 **onSplit()**。为了避免拆分字符时的 kerning 移动，请使用 CSS `font-kerning: none; text-rendering: optimizeSpeed;`。SplitText 不支持 SVG `<text>`。

**了解更多：** [SplitText](https://gsap.com/docs/v3/Plugins/SplitText/)

### ScrambleText

使用 scramble/glitch 效果动画文本。当使用 scramble 揭示或过渡文本时使用。

```javascript
gsap.registerPlugin(ScrambleTextPlugin);

gsap.to(".text", {
  duration: 1,
  scrambleText: { text: "New message", chars: "01", revealDelay: 0.5 }
});
```

## SVG

### DrawSVG (DrawSVGPlugin)

通过动画 `stroke-dashoffset` / `stroke-dasharray` 来显示或隐藏 SVG 元素的描边。适用于 `<path>`、`<line>`、`<polyline>`、`<polygon>`、`<rect>`、`<ellipse>`。当“绘制”或“擦除”描边时使用。

**drawSVG 值：** 描述描边沿路径的**可见部分**（起始和结束位置），而不是“随时间从 A 动画到 B”。格式：`"start end"` 以百分比或长度表示。示例：`"0% 100%"` = 完整描边；`"20% 80%"` = 描边仅在 20% 和 80% 之间（两端都有间隙）。缓动从元素的**当前**段动画到**目标**段——例如 `gsap.to("#path", { drawSVG: "0% 100%" })` 从当前状态动画到完整描边。单个值（例如 `0`、`"100%"`）表示起始为 0：`"100%"` 等同于 `"0% 100%"`。 

**必需：** 元素必须有可见的描边——在 CSS 或作为 SVG 属性中设置 `stroke` 和 `stroke-width`；否则什么都不会绘制。

```javascript
gsap.registerPlugin(DrawSVGPlugin);

// 从无到完整描边
gsap.from("#path", { duration: 1, drawSVG: 0 });
// 或者显式段：从 0–0 到 0–100%
gsap.fromTo("#path", { drawSVG: "0% 0%" }, { drawSVG: "0% 100%", duration: 1 });
// 描边仅在中间（两端有间隙）
gsap.to("#path", { duration: 1, drawSVG: "20% 80%" });
```

**注意事项：** 仅影响描边（不影响填充）。优先使用单段 `<path>` 元素；多段路径在某些浏览器中可能渲染异常。`<use>` 的内容无法进行视觉更改。**DrawSVGPlugin.getLength(element)** 和 **DrawSVGPlugin.getPosition(element)** 返回描边长度和当前位置。

**了解更多：** [DrawSVG](https://gsap.com/docs/v3/Plugins/DrawSVGPlugin)

### MorphSVG (MorphSVGPlugin)

将一个 SVG 形状变形为另一个形状，通过动画 `d` 属性（路径数据）。起始和结束形状不需要相同数量的点——MorphSVG 将其转换为三次贝塞尔曲线并按需添加点。用于图标到图标的变形、形状过渡或基于路径的动画。适用于 `<path>`、`<polyline>` 和 `<polygon>`；`<circle>`、`<rect>`、`<ellipse>` 和 `<line>` 内部转换或通过 **MorphSVGPlugin.convertToPath(selector | element)**（在 DOM 中替换元素为 `<path>`）。

**morphSVG 值：** 可以是**选择器**（例如 `"#lightning"`）、**元素**、**原始路径数据**（例如 `"M47.1,0.8 73.3,0.8..."`），或对于多边形/多段线，**点字符串**（例如 `"240,220 240,70 70,70 70,220"`）。对于完整配置，使用**对象形式**，其中 **shape** 是唯一必需的属性。

```javascript
gsap.registerPlugin(MorphSVGPlugin);

// 如果需要，首先将基本类型转换为路径：
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
| **type** | `"linear"`（默认）或 `"rotational"`。旋转使用角度/长度插值，可以避免变形过程中的折点；当线性看起来不对时尝试它。 |
| **map** | 段匹配方式：`"size"`（默认）、`"position"` 或 `"complexity"`。当起始和结束段不匹配时使用；如果没有有效，将路径拆分为多个并分别变形。 |
| **shapeIndex** | 将起始路径中的点映射到结束路径中的第一个点的偏移（避免形状“交叉”或反转）。数字用于单段路径；**数组**用于多段（例如 `[5, 1, -8]`）。负值反转该段。使用 **shapeIndex: "log"** 一次以记录自动计算的值，然后将数字/数组粘贴到缓动中。**findShapeIndex(start, end)**（单独工具）提供交互式 UI 以找到合适的值。仅适用于闭合路径。 |
| **smooth** | (v3.14+) 添加平滑点。数字（例如 `80`）、`"auto"` 或对象：`{ points: 40 \| "auto", redraw: true \| false, persist: true \| false }`。`redraw: false` 保留原始锚点（完美保真度，间距更均匀）。`persist: false` 在缓动结束时移除添加的点。当默认变形看起来参差不齐或自然时使用。 |
| **curveMode** | 布尔值（v3.14+）。插值控制手柄的角度/长度，而不是原始 x/y，以避免曲线上的折点。如果变形在变形过程中有折点，请尝试。 |
| **origin** | 旋转原点，用于 **type: "rotational"**。字符串：`"50% 50%"`（默认）或 `"20% 60%, 35% 90%"` 用于不同的起始/结束原点。 |
| **precision** | 输出路径数据的十进制位数；默认 `2`。 |
| **precompile** | 预编译路径字符串数组（或使用 **precompile: "log"** 一次，从控制台复制）。跳过昂贵的启动计算；用于非常复杂的变形。仅适用于 `<path>`（先转换多边形/多段线）。 |
| **render** | 每次更新时调用的函数（例如绘制到画布）。RawPath 是一个段数组（每个段 = 交替 x,y 三次贝塞尔曲线坐标）。 |
| **updateTarget** | 当使用 **render**（例如仅用于画布）时，设置 **updateTarget: false** 以防止更新原始 `<path>`。**MorphSVGPlugin.defaultUpdateTarget** 设置默认值。 |

**工具：** **MorphSVGPlugin.convertToPath(selector | element)** 将圆/矩形/椭圆/线/多边形/多段线转换为 DOM 中的 `<path>`。**MorphSVGPlugin.rawPathToString(rawPath)** 和 **stringToRawPath(d)** 在路径字符串和原始数组之间转换。插件将原始 `d` 存储在目标上（例如，用于反向缓动：`morphSVG: "#originalId"` 或相同元素）。

**提示：** 对于扭曲或反转的变形，设置 **shapeIndex**（使用 `"log"` 或 findShapeIndex()）。对于多段路径，**shapeIndex** 是一个数组（每个段一个值）。仅在第一帧缓慢时预编译；它不会修复缓动过程中的卡顿（如果需要，请简化 SVG 或减少大小）。 

**了解更多：** [MorphSVG](https://gsap.com/docs/v3/Plugins/MorphSVGPlugin)

### MotionPath (MotionPathPlugin)

沿 SVG 路径动画元素。当移动对象沿路径（例如曲线或自定义路线）时使用。

```javascript
gsap.registerPlugin(MotionPathPlugin);

gsap.to(".dot", {
  duration: 2,
  motionPath: { path: "#path", align: "#path", alignOrigin: [0.5, 0.5] }
});
```

**MotionPath — 关键配置（motionPath 对象）：**

| 选项 | 描述 |
|------|------|
| `path` | SVG 路径元素、选择器或路径数据字符串 |
| `align` | 要对齐的路径元素或选择器 |
| `alignOrigin` | `[x, y]` 原点（0–1）；默认 `[0.5, 0.5]` |
| `autoRotate` | 旋转元素以跟随路径切线 |
| `curviness` | 0–2；路径平滑 |

### MotionPathHelper

MotionPath 的可视化编辑器（对齐、偏移）。在开发过程中使用，以调整路径对齐。

```javascript
gsap.registerPlugin(MotionPathPlugin, MotionPathHelperPlugin);

const helper = MotionPathHelper.create(".dot", "#path", { end: 0.5 });
// 在 UI 中调整，然后在动画中使用 helper.path 或 helper.getProgress() |
```

## 缓动

### CustomEase

自定义缓动曲线（三次贝塞尔曲线或 SVG 路径）。当内置缓动不足时使用。基本用法在 gsap-core 中涵盖；在使用时注册：

```javascript
gsap.registerPlugin(CustomEase);
const ease = CustomEase.create("name", ".17,.67,.83,.67");
gsap.to(".el", { x: 100, ease: ease, duration: 1 });
```

### EasePack

添加更多命名缓动（例如 SlowMo、RoughEase、ExpoScaleEase）。注册并使用缓动名称在缓动中使用。

### CustomWiggle

Wiggle/shake 缓动。当值应该“wobble”（多次振荡）时使用。

### CustomBounce

具有可配置强度的弹跳式缓动。

## 物理

### Physics2D (Physics2DPlugin)

2D 物理（速度、角度、重力）。当使用简单物理动画时使用（例如投射物、弹跳）。

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

用于滚动时间轴、切换动画和调试的 UI。仅在开发过程中使用；不要发布。注册并创建一个带有时间轴引用的实例。

```javascript
gsap.registerPlugin(GSDevTools);
GSDevTools.create({ animation: tl });
```

## 其他

### Pixi (PixiPlugin)

将 GSAP 与 PixiJS 集成，用于动画 Pixi 显示对象。在用 GSAP 动画 Pixi 对象时注册。

```javascript
gsap.registerPlugin(PixiPlugin);

const sprite = new PIXI.Sprite(texture);
gsap.to(sprite, { pixi: { x: 200, y: 100, scale: 1.5 }, duration: 1 });
```

## 最佳实践

- ✅ 使用 **gsap.registerPlugin()** 在使用前注册每个插件。
- ✅ 使用 **Flip.getState()** → DOM 更改 → **Flip.from()** 进行布局过渡；使用 **Draggable** + **InertiaPlugin** 进行带惯性的拖动。
- ✅ 组件卸载或元素移除时还原插件实例（例如 `SplitTextInstance.revert()`）。

## 不要

- ❌ 在使用前未注册插件就使用插件在缓动或 API 中（**gsap.registerPlugin()**）。
- ❌ 将 GSDevTools 或开发插件发布到生产环境。
