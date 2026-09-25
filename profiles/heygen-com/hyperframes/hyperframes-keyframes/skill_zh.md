# HyperFrames关键帧

关键帧是一种姿态契约：可见状态、连续的主体身份、安全搜索的运行时、验证过的像素。

使用`hyperframes-animation`进行广泛的场景配方。使用`hyperframes-cli`获取完整的命令文档。仅在选择实现机制时使用`references/keyframe-patterns.md`，而不是视觉风格。

## 创建者编辑边界

关键帧拥有视觉运动，而不是剪辑组装。源范围硬切、修剪、拼接和重新排序属于`/hyperframes-core`：为每个保留的范围创建一个媒体元素，使用`data-start`和`data-duration`放置它，并使用`data-media-start`选择其源偏移量。相邻的范围形成一个硬切。交叉淡入使用不同轨道上的重叠剪辑加上视觉不透明度关键帧；声音淡入使用`/hyperframes-audio`。

| 创建者请求                         | 真实的机制                                                                                                                                                                                                          |
| --------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Punch-in / punch-out                    | 在剪辑内部的非定时视觉/裁剪包装器上使用关键帧`scale`，带有`x`/`y`或百分比平移。使用设置/短缓动进行硬切，使用缓动进行平滑移动。                                                                                               |
| 平滑的多状态缩放或重新构图      | 保留一个主体包装器保持活动，并将多个缩放/重新构图状态作为具有每个片段缓动的姿态阶梯来编写。                                                                                                            |
| 拖动、重新构图或Ken Burns摄像机移动  | 动画包装器平移加上缩放。几何形状是编写的；这不是面部跟踪或自动语义重新构图。                                                                                                                                            |
| 链式摄像机移动                    | 在一个注册的安全搜索时间线上链式标记的变换节拍。                                                                                                                                                         |
| 匹配切或甩动拖动                   | `/hyperframes-animation`拥有视觉交接；`/hyperframes-registry`提供原语；关键帧保留编写的几何形状、方向和速度。没有自动匹配帧发现。                                                                               |
| 裁剪和遮罩重新构图                   | 在内部视觉包装器上插值`clip-path`或遮罩以裁剪/重新构图，而不会改变源时间。多边形关键帧可以形成多边形/遮罩过渡。                                                                                                    |
| 方向性擦除切或虹膜/揭示切            | 动画一个遮罩/剪辑边界跨过重叠的视觉剪辑；`/hyperframes-animation`拥有交接编排。                                                                                                                                   |
| 分屏交接                    | 保持核心放置的两个视觉剪辑，然后关键帧它们的内部裁剪/遮罩包装器和分隔器几何形状。                                                                                                                   |
| 恒定源重时间                  | `/hyperframes-core`拥有标准化的`data-playback-rate`（`0.1..5`）用于渲染安全的图像和保留音调的声音。它对整个媒体元素是恒定的。                                                                                          |
| 源速度斜坡                      | 不支持：没有时间变化的播放速率包络。预处理衍生媒体资产，然后通过核心放置它。                                                                                                                                       |
| 冻结 / 保持                           | 一个视觉姿态、最终源帧或完成的子合成可以保持。不支持任意源中间冻结；预处理一个静止/衍生片段，将其作为自己的剪辑放置，然后使用另一个源范围继续。                                                                      |

当一起编辑图像和声音时，加载`/hyperframes-core`，这个视觉运动技能，以及`/hyperframes-audio`用于淡入、交叉淡入、音量自动化、降低/切割或放置轨道上的效果。

一个视觉过渡或裁剪处理不是一个时间源修剪或拼接。`/hyperframes-core`拥有时间线、剪辑时间和源范围；关键帧仅动画化剪辑内部包装器上的可见交接或裁剪。对于可复制的组合图像/声音配方，使用`/hyperframes-core` → `references/creator-editing-recipes.md`。

## 程序

1. 确定动画主体、可见状态、最终状态和运行时。
2. 选择证明提示的最小机制。如果机制不清楚，请阅读`references/keyframe-patterns.md`。
3. 在声明的运行时中编写安全搜索的关键帧。同步构建并注册运行时实例。
4. 使用`hyperframes lint`、`hyperframes check`、`hyperframes keyframes`、一个聚焦的`--shot`以及证明时间的快照进行验证。
5. 如果证明失败，请修复源关键帧，并在渲染之前重新运行最小的失败诊断。

## 契约

- 命名运动主体。
- 命名证明预期运动所需的姿态，包括最终状态。
- 关键帧可见通道，而不是隐藏的帮助器状态。
- 当连续性重要时保留对象身份。
- 仅在预期运动是替换或溶解时才交叉淡入。
- 保持可读或语义状态足够长，以便可以看到。
- 最终帧是动画的一部分，而不是清理。
- 除非要求，否则不要重置为静止状态。
- 除非要求，否则不要以黑色结束。
- 如果编辑一个起始场景，除非要求重新设计，否则请保留布局、复制、资产、颜色和最终状态。

## 运行时规则

GSAP：

- 在页面加载时同步构建
- 使用`gsap.timeline({ paused: true })`
- 注册为`window.__timelines[compositionId]`
- 注册键必须匹配`data-composition-id`
- 不要为渲染关键运动调用`tl.play()`
- 保持重复有限

CSS关键帧：

- 有限持续时间和迭代次数
- 确定性延迟
- `animation-fill-mode: both`
- 当时间属于剪辑时使用`data-start`

Anime.js：

- 同步创建
- `autoplay: false`
- 有限持续时间和循环
- 将每个实例推送到`window.__hfAnime`

WAAPI：

- 有限`duration`
- `fill: "both"`
- 确定性构造
- 文本表面没有列出WAAPI；使用`--shot`（它搜索WAAPI）和快照进行验证

永远不要用于渲染关键运动：

- `Date.now()`
- `performance.now()`
- 未播种的`Math.random()`
- 悬停/滚动触发
- 定时器
- 异步创建的时间线
- 未注册的`requestAnimationFrame`
- 无限循环

## GSAP骨架

```js
const root = document.querySelector("[data-composition-id]");
const compositionId = root.dataset.compositionId;
const tl = gsap.timeline({ paused: true });

tl.addLabel("state-a", 0);
tl.to(".subject", {
  keyframes: [
    { x: 0, opacity: 1, duration: 0.2 },
    { x: 120, opacity: 1, duration: 0.4, ease: "power2.out" },
    { x: 100, opacity: 1, duration: 0.2, ease: "power2.inOut" },
  ],
  ease: "none",
});

window.__timelines = window.__timelines || {};
window.__timelines[compositionId] = tl;
```

使用标签进行语义状态。使用位置参数而不是链式延迟。使用`immediateRender: false`为稍后的`from()`/`fromTo()`缓动触摸相同属性。

## 关键帧形式

- 数组关键帧：姿态阶梯，每步持续时间和缓动。
- 百分比关键帧：在一个缓动内的精确时间。
- 属性数组：紧凑的多停止更改。
- 父级上使用`ease: "none"`，当每个停止都携带自己的缓动时。
- 使用`easeEach`，当每个片段都应该共享相同的感觉时。

不要从示例中复制数字距离或时间。根据实际合成几何形状和持续时间导出它们。

对于在两个盒子之间移动的一个主体，优先选择一个连续的变换缓动或FLIP。仅在观众应该感觉到不同的节拍时，才将`x/y/scale`拆分为多个缓动的关键帧；每个片段都改变速度，可以读作一个颠簸。

## 通道

优先使用合成器/视觉通道：`x/y/z`、`xPercent/yPercent`、`scale`、`rotationX/Y/Z`、`skew`、`transformOrigin`、`svgOrigin`、`opacity`、`autoAlpha`、`clip-path`、遮罩、CSS变量、SVG路径/划线值、摄像机变换、着色器统一变量。

避免布局/生命周期通道：`top/left/right/bottom`、`width/height`、`margin/padding`、`display`、`visibility`、晚DOM创建、执行主体运动的帮助器覆盖层。

对于可见性更改，请在注册的安全搜索GSAP时间线上使用`autoAlpha`，或在显式边界处使用零持续时间的`tl.set()`。仅针对非剪辑元素或剪辑内部的包装器进行目标；永远不要针对`.clip`本身。永远不要持续缓动原始`visibility`，并且永远不要缓动`display`。

## 机制选择

选择证明提示的最小机制：

| 需求                                  | 机制                                          |
| ------------------------------------- | -------------------------------------------------- |
| 相同主体改变框或层次结构                | 共享元素 / FLIP                              |
| 主体沿可见路线旅行                   | 路径旅行                                        |
| 笔画增长或跟踪                | 笔画绘制                                        |
| 形状变成另一个形状           | 形状插值                                |
| 揭示边界是可见的            | 剪辑、遮罩或着色器统一变量                      |
| 许多项目按顺序移动            | 错落 / 索引延迟                            |
| 文本本身移动                     | 行、词、字符或带子细分         |
| 表面弯曲、拉伸或裁剪    | 父级/子级计数变换                     |
| UI具有状态                         | 显式状态机                             |
| 场景具有深度                       | DOM 3D、Three.js或WebGL摄像机/对象关键帧 |

机制可以组合，但每个机制都必须澄清想法。装饰不是证明。

## 时间

- 仅在澄清因果关系或方向时才使用预期。
- 加速留下休息。
- 峰值证明明确显示机制。
- 随后销售能量和方向。
- 仅在主体应该感觉弹性或触感时才使用超调。
- 恒定速度路径旅行通常需要`ease: "none"`。
- 离散UI状态通常需要锐利的ease-out。
- 重复元素需要有序偏移，而不是相同的时间。
- 最终锁定需要比过渡姿态更长的保持。
- 平滑意味着同一主体的连续速度。
- 除非重叠是故意且经过验证的，否则不要重叠写入相同变换属性的缓动。
- 避免在相同的英雄表面缩放或旅行时动画化大的`clip-path`/遮罩更改；在主移动稳定后使用嵌套揭示。

## 文本

保留行框、字间距、可读性和最终适配。如果文本内部移动，请移动字形或遮罩带，而不仅仅是围绕文本的装饰。拍摄可读帧。

## SVG

对于笔画增长，优先使用`DrawSVGPlugin`，然后是`stroke-dasharray`/`stroke-dashoffset`。对于形状插值，优先使用`MorphSVGPlugin`；当需要时将原语转换为路径，并将复杂的轮廓拆分为更简单的部分。

## 3D

仅缩放是假的深度。在稳定的父级上使用透视、`transform-style: preserve-3d`、z旅行、旋转、摄像机/世界运动、遮挡和层顺序，当对象交叉时。

使用一个或两个诊断角度来暴露深度关系。如果倾斜证明显示没有深度交叉，请改进z/摄像机/遮挡。

## Canvas / WebGL

关键帧摄像机位置、摄像机目标、对象变换、材料不透明度、着色器统一变量和后处理强度通过确定性状态。通过HyperFrames时间渲染。使用`--ghost`，因为标记框无法看到内部canvas运动。

## CLI证明

```bash
npx hyperframes lint
npx hyperframes check
npx hyperframes keyframes .
npx hyperframes keyframes . --json
npx hyperframes keyframes . --runtime all
npx hyperframes keyframes . --selector "<selector>" --shot "<file>" --samples <n>
npx hyperframes keyframes . --selector "<selector>" --shot "<file>" --layout strip --from <t0> --to <t1>
npx hyperframes keyframes . --shot "<file>" --ghost --angle <angle>
npx hyperframes snapshot . --at <times>
```

为真实的动画主体选择`<selector>`。为第一帧、证明姿态、最终减保持和精确最终选择`<times>`。仅当必须证明深度时选择`<angle>`。

| 工具             | 证明                                                                                              |
| ---------------- | --------------------------------------------------------------------------------------------------- |
| `keyframes`      | 目标、显式停止、路径、跟踪、组合的父级/子级运动、CSS停止、Anime注册 |
| `--shot`         | 幽灵、路线形状、时间间距、DOM 3D投影、聚焦选择器证明                        |
| `--layout strip` | 原位运动、重叠、接触、微妙的缩放/不透明度、文本波浪                                |
| `--ghost`        | canvas、WebGL、着色器运动、渲染3D                                                           |
| `snapshot --at`  | 遮罩、文本可读性、完整状态、最终锁定、黑色/重置尾部                                |

如果选择器证明看起来不正确：

1. 重新运行`--json`
2. 找到实际的动画目标
3. 射击该目标
4. 快照完整帧
5. 信任绘制的像素而不是日志

## 诊断阅读

`flat`表示没有显式的中间姿态。`keyframes`表示存在显式停止。`motionPath`表示存在路线。`trace`表示多笔画绘制。`composed with`表示子级运动继承父级运动。

即使幽灵间距也表示恒定速度。聚集的幽灵表示慢入或稳定。大的间隙表示快速旅行。

一个帮助器选择器射击不是证明。一个覆盖损坏的完整帧的洋葱射击不是证明。

## 错误处理

| 失败            | 修复                                                                                |
| ---------------- | ---------------------------------------------------------------------------------- |
| endpoint-only      | 添加中间姿态，保持峰值证明，重新运行`--shot`                                  |
| identity break     | 保持一个元素活跃，使用共享源/最终框，移除替代交叉淡入 |
| fake 3D            | 添加z/摄像机旅行，遮挡，倾斜证明                                       |
| wrong final        | 添加最终保持，快照最终减保持和精确最终                          |
| unseekable runtime | 暂停autoplay，注册实例，移除定时器，同步构建              |
| unreadable text    | 保留行框，减少位移，添加最终保持，快照文本帧     |

## 完成

运行`hyperframes lint`、`hyperframes check`、`hyperframes keyframes`、一个聚焦的`--shot`和快照。确认第一帧、证明姿态、最终减保持、精确最终、主体拥有的运动和没有调试覆盖层。
