# HyperFrames 关键帧

关键帧是姿态契约：可见状态、主体连续性、可安全跳转的运行状态、已验证的像素。

使用 `hyperframes-animation` 处理通用场景配方；使用 `hyperframes-cli` 获取完整命令文档；仅在选择实现机制时使用 `references/keyframe-patterns.md`，而非视觉风格。

## 创作者编辑边界

关键帧拥有视觉运动，而非剪辑组装。源范围硬切、裁剪、拼接与重排属于 `/hyperframes-core`：为每个保留范围编写一个媒体元素，用 `data-start` 和 `data-duration` 放置，并用 `data-media-start` 选择源偏移。相邻范围构成硬切。交叉淡入淡出使用不同轨道上的重叠剪辑以及视觉不透明度关键帧；声音淡入淡出使用 `/hyperframes-audio`。

| 创作者请求 | 真实机制 |
| ---------- | ------------------------------------------------------------- |
| 入画 / 出画 | 在剪辑内的非定时视觉/裁剪包装器上设置关键帧 `scale`、`x`/`y` 或百分比位移。使用 set/短动画实现硬入画，使用动画实现平滑移动。 |
| 平滑多状态缩放或重构图 | 保持一个主体包装器持续存在，以逐段缓动作为姿态阶梯编写多个缩放/重构图状态。 |
| 平移、重构图或 Ken Burns 相机运动 | 动画化包装器的平移与缩放。几何由作者编写；这不是面部追踪或自动语义重构图。 |
| 链式相机运动 | 在一个已注册的、可安全跳转的时间线上链式连接带标注的变换节拍。 |
| 匹配剪辑或甩镜头 | `/hyperframes-animation` 拥有视觉交接；`/hyperframes-registry` 提供原语；关键帧保留已编写的几何、方向与速度。不存在自动匹配帧发现。 |
| 裁剪与遮罩重构图 | 在内层视觉包装器上对 `clip-path` 或遮罩进行插值，以裁剪/重构图而不改变源时间。多边形关键帧可形成多边形/遮罩转场。 |
| 方向性擦除剪辑或虹膜/揭示剪辑 | 在重叠的视觉剪辑上动画化遮罩/剪辑边界；`/hyperframes-animation` 拥有交接编排。 |
| 分屏交接 | 由核心放置两个视觉剪辑后，再对其内部裁剪/遮罩包装器与分隔几何进行关键帧设置。 |
| 恒定源速率重加速 | `/hyperframes-core` 拥有归一化的 `data-playback-rate`（`0.1..5`），用于渲染安全的画面与保留音高的声音。它对整个媒体元素是恒定的。 |
| 源速度爬升 | 不支持：不存在随时间变化的播放速率包络。先预处理派生媒体资源，再通过核心放置。 |
| 冻结 / 保持 | 视觉姿态、最终源帧或完成的子合成可以保持。不支持的任意源中段冻结；预处理静止/派生片段，将其作为独立剪辑放置，再用另一个源范围恢复。 |

编辑画面与声音时，加载 `/hyperframes-core`、本技能用于视觉运动，以及 `/hyperframes-audio` 用于淡入淡出、交叉淡入淡出、音量自动化、压低/裁切或对已放置轨道的效果。

视觉转场或裁剪处理不是时域源裁剪或拼接。`/hyperframes-core` 拥有时间线、剪辑时序与源范围；关键帧仅在剪辑内部的包装器上动画化可见交接或裁剪。如需可复制的画面/声音组合配方，使用 `/hyperframes-core` → `references/creator-editing-recipes.md`。

## 流程

1. 识别动画主体、可见状态、最终状态与运行时长。
2. 选择能证明提示的最小机制。若机制不明确，仅阅读 `references/keyframe-patterns.md`。
3. 在声明运行时编写可安全跳转的关键帧。同步构建并注册运行实例。
4. 使用 `hyperframes lint`、`hyperframes check`、`hyperframes keyframes`、一次聚焦的 `--shot`，并在验证时刻截取快照。
5. 若验证失败，修复源关键帧，并在渲染前重新运行最小的失败诊断。

## 契约

- 命名移动主体。
- 命名证明所需运动姿态，包括最终状态。
- 关键帧化可见通道，而非隐藏辅助状态。
- 在连续性关键时保留对象身份。
- 仅当意图为替换或溶解时才使用交叉淡入淡出。
- 保持可读或语义状态足够长，以便观察。
- 最终帧是动画的一部分，而非清理工作。
- 除非要求，否则不要重置为静止状态。
- 除非要求，否则不要以黑色结束。
- 编辑起始场景时，除非要求重新设计，否则保留布局、文案、素材、颜色与最终状态。

## 运行规则

GSAP：

- 在页面加载时同步构建
- 使用 `gsap.timeline({ paused: true })`
- 注册为 `window.__timelines[compositionId]`
- 注册表键必须与 `data-composition-id` 匹配
- 不要为渲染关键运动调用 `tl.play()`
- 保持重复次数有限

CSS 关键帧：

- 时长与迭代次数有限
- 确定性的延迟
- `animation-fill-mode: both`
- 当时序属于剪辑时使用 `data-start`

Anime.js：

- 同步创建
- `autoplay: false`
- 时长与循环次数有限
- 将所有实例推入 `window.__hfAnime`

WAAPI：

- 有限时长
- `fill: "both"`
- 确定性的构建
- 文本表面未列出 WAAPI；通过 `--shot`（它会跳转 WAAPI）与快照进行验证

以下内容不得用于渲染关键运动：

- `Date.now()`
- `performance.now()`
- 无种子的 `Math.random()`
- 悬停/滚动触发器
- 定时器
- 异步创建的时序
- 未注册的 `requestAnimationFrame`
- 无限循环

## GSAP 骨架

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

使用标签表达语义状态。使用位置参数而非链式延迟。对于后续影响同一属性的 `from()`/`fromTo()` 补间，使用 `intermediateRender: false`。

## 关键帧形式

- 数组关键帧：逐阶段时长/缓动的姿态阶梯。
- 百分比关键帧：在一个补间内精确控制时间。
- 属性数组：紧凑的多停变化。
- 当每个停点都自带缓动时，父级设置 `ease: "none"`。
- 当每个段落都应拥有相同感受时使用 `easeEach`。

不要从示例中复制数值距离或时间。应根据实际合成的几何与时长推导。

对于主体在两个盒子之间移动的案例，优先使用一个连续的变换补间或 FLIP。仅当观众需要感到不同的节拍时，才将 `x/y/scale` 拆分为多个带缓动的关键帧；每个段落都会改变速度，可能读作停顿。

## 通道

优先使用合成器/视觉通道：`x/y/z`、`xPercent/yPercent`、`scale`、`rotationX/Y/Z`、`skew`、`transformOrigin`、`svgOrigin`、`opacity`、`autoAlpha`、`clip-path`、遮罩、CSS 变量、SVG 路径/虚线值、相机变换、着色器 uniform。

避免布局/生命周期通道：`top/left/right/bottom`、`width/height`、`margin/padding`、`display`、`visibility`、晚期 DOM 创建、用于主体运动的辅助叠加层。

对于可见性变化，在已注册的可跳转 GSAP 时间线上使用 `autoAlpha`，或在明确边界处使用零时长的 `tl.set()`。仅针对非剪辑元素或剪辑内的包装器，永远不要针对 `.clip` 本身。永远不要对原始 `visibility` 做时长补间，也永远不要补间 `display`。

## 机制选择

选择能证明提示的最小机制：

| 需求 | 机制 |
| ---- | ------------------------------------------------ |
| 同一主体改变框或层级 | shared element / FLIP |
| 主体沿可见路径移动 | path travel |
| 描边增长或追踪 | stroke draw |
| 形状变为另一形状 | shape interpolation |
| 显现边界可见 | clip、mask 或 shader uniform |
| 多个元素按顺序移动 | stagger / indexed delay |
| 文本自身移动 | line、word、character 或 band 细分 |
| 表面弯曲、拉伸或裁剪 | parent/child 反变换 |
| UI 有状态 | 显式状态机 |
| 场景有深度 | DOM 3D、Three.js 或 WebGL 相机/对象关键帧 |

机制可以组合，但每种机制都必须明确表达意图。装饰不是证明。

## 时序

- 仅当能阐明因果关系或方向时才使用预期。
- 加速后余韵自然。
- 峰值证明让机制清晰可辨。
- 后续余势传递能量与方向。
- 仅当主体应呈现弹性或触感时使用过冲。
- 匀速路径移动通常需要 `ease: "none"`。
- 离散 UI 状态通常需要锐利的缓出。
- 重复元素需要有序偏移，而非相同时序。
- 最终固定需要比过渡姿态更长的保持时间。
- 流畅性意味着同一主体上连续的瞬时速度。
- 不要重叠写入相同变换属性的补间，除非重叠是有意且经过验证的。
- 避免在主表面同时缩放或移动时动画化大的 `clip-path`/遮罩变化；在主动作稳定后使用嵌套显现。

## 文本

保留行盒、字距、可读性与最终适配。如果文本内部移动，应移动字形或遮罩带，而非仅移动文本周围的装饰。对可读帧截取快照。

## SVG

对于描边增长，优先使用 `DrawSVGPlugin`，然后使用 `stroke-dasharray`/`stroke-dashoffset`。对于形状插值，优先使用 `MorphSVGPlugin`；需要时将基础图形转换为路径，并将复杂轮廓拆分为更简单的部分。

## 3D

单独缩放是虚假深度。在稳定父级上使用透视、`transform-style: preserve-3d`、z 移动、旋转、相机/世界运动、遮挡以及对象交叉时的层顺序。

使用一到两个能暴露深度关系的诊断角度。如果倾斜验证未显示深度交叉，则优化 z、相机与遮挡。

## Canvas / WebGL

通过确定的状态关键帧化相机位置、相机目标、对象变换、材质不透明度、着色器 uniform 与后处理强度。从 HyperFrames 时间渲染。使用 `--ghost`，因为标记框无法看到画布内部运动。

## CLI 验证

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

为真实动画主体选择 `<selector>`。为第一帧、验证姿态、最终-保持与精确最终选择 `<times>`。仅在必须证明深度时选择 `<angle>`。

| 工具 | 证明内容 |
| ---- | -------------------------------------------------- |
| `keyframes` | 目标、明确停点、路径、轨迹、组合的父/子运动、CSS 停点、Anime 注册 |
| `--shot` | 幽灵帧、路径形状、时间间距、DOM 3D 投影、聚焦选择器验证 |
| `--layout strip` | 原地运动、重叠、接触、细微缩放/不透明度、文本波动 |
| `--ghost` | 画布、WebGL、着色器运动、渲染的 3D |
| `snapshot --at` | 遮罩、文本可读性、完整状态、最终固定、黑屏/重置尾部 |

若选择器验证看起来错误：

1. 重新运行 `--json`
2. 找到实际动画目标
3. 拍摄该目标
4. 截取完整帧快照
5. 信任绘制的像素而非日志

## 诊断阅读

`flat` 表示无明确中间姿态。`keyframes` 表示存在明确停点。`motionPath` 表示存在路线。`trace` 表示多笔画绘制。`composed with` 表示子运动继承父运动。

即使幽灵帧间距也表示匀速。聚集的幽灵帧表示缓慢进入或趋于稳定。大间隔表示快速移动。

辅助选择器拍摄不是证明。在破损完整帧上的洋葱拍摄不是证明。

## 错误处理

| 故障 | 修复 |
| ---- | ------------------------------------------------ |
| 仅端点 | 添加中间姿态，保持峰值验证，重新运行 `--shot` |
| 身份断裂 | 保持一个元素持续存在，使用共享源/最终框，移除替代交叉淡入淡出 |
| 虚假 3D | 添加 z/相机移动、遮挡、倾斜验证 |
| 最终错误 | 添加最终保持，截取最终-保持与精确最终快照 |
| 不可跳转运行时 | 暂停自动播放，注册实例，移除定时器，同步构建 |
| 文本不可读 | 保留行盒，减小位移，添加最终保持，截取文本帧快照 |

## 完成

运行 `hyperframes lint`、`hyperframes check`、`hyperframes keyframes`、一次聚焦的 `--shot` 与快照。确认第一帧、验证姿态、最终-保持、精确最终、主体自有运动，且无调试叠加。
