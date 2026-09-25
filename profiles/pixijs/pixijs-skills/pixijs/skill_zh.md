PixiJS v8 技能集合的入口。PixiJS 是目前最快的网络库，可在所有设备上运行，并允许您使用 WebGL、WebGPU 和 Canvas（作为后备选项）创建丰富的交互式图形和跨平台应用程序。

## 如何使用此技能

1. 在下方的路由器中找到最适合任务的专用技能。
2. 加载该技能的 `SKILL.md` 并遵循其指导。
3. 如果没有子技能适用（任务引用了下方未列出的特定类、函数、选项或 API 表面），**WebFetch `https://pixijs.download/release/docs/llms.txt`**。该文件是自动生成的、始终最新的完整 PixiJS API 和指南索引，每个条目链接到您可以通过 WebFetch 获取详细内容的 `.html.md` 页面。

有关每个技能的详细描述和触发关键字，请参阅 [references/index.md](references/index.md)。

## 技能路由器

### 基础

| 技能 | 当...加载 |
|---|---|
| [pixijs-application](../pixijs-application/SKILL.md) | 创建或配置 PixiJS `Application`、调用 `app.init()`、访问 `app.stage`/`renderer`/`canvas`/`screen`、调整大小/计时器插件、`app.destroy()`。 |
| [pixijs-core-concepts](../pixijs-core-concepts/SKILL.md) | 理解渲染器管道、选择 WebGL/WebGPU/Canvas、渲染循环内部机制、系统管道、渲染器加载器扩展、渲染到 `RenderTexture`/`RenderTarget`（`flipY`、`mipLevel`、`bind`/`push`/`pop`、深度）、WebGL 上下文丢失和 WebGPU 设备丢失。 |
| [pixijs-create](../pixijs-create/SKILL.md) | 使用 `create-pixi` CLI（捆绑包-vite、创建-Web、框架-React 模板）搭建新项目、将 PixiJS 添加到现有项目，或为 TypeScript 5、6 或 7 设置 `tsconfig.json`（`moduleResolution`、`@webgpu/types`、`@types/web`）。 |
| [pixijs-environments](../pixijs-environments/SKILL.md) | 在 Web Workers、Node/SSR 或严格-CSP 上下文中运行 PixiJS（`DOMAdapter`、`WebWorkerAdapter`、`pixi.js/unsafe-eval`）。 |
| [pixijs-migration-v8](../pixijs-migration-v8/SKILL.md) | 从 v7 升级到 v8 或修复 v7 模式（`beginFill`/`endFill`、`@pixi/*` 包、`BaseTexture`、`DisplayObject`）。 |
| [pixijs-scene-core-concepts](../pixijs-scene-core-concepts/SKILL.md) | 理解场景图的整体：容器与叶子、变换、渲染顺序、遮罩、`RenderLayer`。 |

### 场景对象

| 技能 | 当...加载 |
|---|---|
| [pixijs-scene-container](../pixijs-scene-container/SKILL.md) | 使用 `Container`：`addChild`/`removeChild`、变换、`zIndex`、边界、`toGlobal`/`toLocal`、`destroy`。 |
| [pixijs-scene-sprite](../pixijs-scene-sprite/SKILL.md) | 绘制图像：`Sprite`、`AnimatedSprite`、`NineSliceSprite`、`TilingSprite`。 |
| [pixijs-scene-graphics](../pixijs-scene-graphics/SKILL.md) | 绘制矢量形状或路径：`Graphics`、`GraphicsContext`、`fill`/`stroke`、`FillGradient`、`FillPattern`、`textureSpace`、纹理和图案填充、SVG 导入（`svg()`、渐变）。 |
| [pixijs-scene-text](../pixijs-scene-text/SKILL.md) | 渲染文本：`Text`、`BitmapText`、`HTMLText`、`SplitText`、`TextStyle`。 |
| [pixijs-scene-mesh](../pixijs-scene-mesh/SKILL.md) | 自定义几何图形：`Mesh`、`MeshSimple`、`MeshPlane`、`MeshRope`、`PerspectiveMesh`。 |
| [pixijs-scene-particle-container](../pixijs-scene-particle-container/SKILL.md) | 渲染数千个轻量级精灵：`ParticleContainer`、`Particle`、`dynamicProperties`。 |
| [pixijs-scene-dom-container](../pixijs-scene-dom-container/SKILL.md) | 在画布上叠加 HTML 元素：`DOMContainer`、`pixi.js/dom`。 |
| [pixijs-scene-gif](../pixijs-scene-gif/SKILL.md) | 显示动画 GIF：`GifSprite`、`GifSource`、`pixi.js/gif`。 |
| [pixijs-html-source](../pixijs-html-source/SKILL.md) | 渲染实时 HTML/DOM 元素或快照作为纹理（实验性，需要支持 HTML-in-Canvas 规范的浏览器）：`HTMLSource`、`ElementImageSource`、`pixi.js/html-source`、`requestPaint`。 |

### 工具

| 技能 | 当...加载 |
|---|---|
| [pixijs-assets](../pixijs-assets/SKILL.md) | 加载资源：`Assets.init`、`Assets.load`、捆绑包、清单、精灵表、缓存。 |
| [pixijs-color](../pixijs-color/SKILL.md) | 创建或转换颜色：`Color` 类、十六进制/RGB/HSL、`tint`、`premultiply`。 |
| [pixijs-events](../pixijs-events/SKILL.md) | 处理指针/鼠标/触摸/滚轮输入：`eventMode`、`FederatedEvent`、`hitArea`、`cursor`、拖拽。 |
| [pixijs-math](../pixijs-math/SKILL.md) | 点、向量、矩阵、形状、碰撞检测：`Point`、`Matrix`、`Rectangle`、`Polygon`、`Triangle`、`strokeContains`、`containsRect`、`Matrix.decompose`（镜像矩阵）、`toGlobal`/`toLocal`。 |
| [pixijs-ticker](../pixijs-ticker/SKILL.md) | 每帧逻辑或控制渲染循环：`Ticker`、`deltaTime`、`UPDATE_PRIORITY`、`maxFPS`。 |

### 高级

| 技能 | 当...加载 |
|---|---|
| [pixijs-accessibility](../pixijs-accessibility/SKILL.md) | 屏幕阅读器或键盘导航：`AccessibilitySystem`、`accessibleTitle`、`tabIndex`。 |
| [pixijs-blend-modes](../pixijs-blend-modes/SKILL.md) | 使用混合模式合成：`add`、`multiply`、`screen`、`overlay`、`pixi.js/advanced-blend-modes`。 |
| [pixijs-custom-rendering](../pixijs-custom-rendering/SKILL.md) | 编写自定义着色器、uniforms 或批处理器：`Shader.from`、`GlProgram`/`GpuProgram`、`UniformGroup`、自定义 `Filter`、WGSL `override` 常量、`gpuLayout`、`TextureView`、`Buffer.update`、`TexturePool`、渲染捆绑包、自定义管道。 |
| [pixijs-filters](../pixijs-filters/SKILL.md) | 应用视觉效果：`BlurFilter`、`ColorMatrixFilter`、`DisplacementFilter`、`Filter.from`、`pixi-filters`。 |
| [pixijs-performance](../pixijs-performance/SKILL.md) | 分析或优化 FPS、绘制调用、GPU 内存：剔除、`GCSystem`、`cacheAsTexture`、对象池、临时 MSAA 渲染纹理、渲染捆绑包、滤镜纹理尺寸。 |

## 备用方案：标准 PixiJS 文档

如果任务引用了上方任何子技能未涵盖的类、函数、选项或 API 表面，**WebFetch `https://pixijs.download/release/docs/llms.txt`**。它是自动生成的完整 PixiJS API 和指南索引，每个发布都会重新生成。每个条目链接到您可以通过 WebFetch 获取详细内容的 `.html.md` 页面。每当路由表未指向明显匹配时，请使用此备用方案。
