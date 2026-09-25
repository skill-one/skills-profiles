# 标题部分

带有纹理的密集树冠横扫画面，景深浅，然后分开露出第一条标题；第二条标题被提升深度后从相机前经过。几片叶子停留在文字上，保持微风。字体、粗细、大小、字间距、叶子数量、扫动速度和保留的叶子微风是可变参数。

构图ID：`canopy-part-title`。时长12秒，30fps，1920×1080。

## 文件

- `canopy-part-title.html` (57 KB)
- `assets/leaf-surface-color.webp` (64 KB)
- `assets/leaf-surface-normal.webp` (136 KB)

## 安装

使用 `npx hyperframes add canopy-part-title` 安装；默认情况下，上述文件将位于 `compositions/canopy-part-title/` 下。然后从主机 `index.html` 中挂载该模块：

```html
<div
  data-composition-id="canopy-part-title"
  data-composition-src="compositions/canopy-part-title/canopy-part-title.html"
  data-start="0"
  data-duration="12"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

通过直接指向构图文件使用自定义值进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/canopy-part-title/canopy-part-title.html' --variables '{"headline1":"Understory","headline2":"Move slowly"}'
```

## 变量

通过 `window.__hyperframes.getVariables()` 在运行时读取；在构图根上声明为 `data-composition-variables`（单引号属性，纯JSON）。

| id               | 类型   | 默认         | 标签 / 范围                            |
| ---------------- | ------ | --------------- | ---------------------------------------- |
| `headline1`      | string | `"Understory"`  | 标题1                                  |
| `headline2`      | string | `"Move slowly"` | 标题2                                  |
| `font`           | string | `"Helvetica"`   | 标题字体                                |
| `fontWeight`     | number | `900`           | 字体粗细 100–900 步长 100              |
| `fontSize`       | number | `1`             | 字体大小（1 = 自动适配） 0.3–2 步长 0.01 |
| `letterSpacing`  | number | `0.01`          | 字间距（em） -0.2–1 步长 0.01          |
| `background`     | color  | `"#020805"`     | 背景                                    |
| `leafCount`      | number | `170`           | 每次扫动叶子数量 40–320 步长 1          |
| `stayCount`      | number | `5`             | 停留的叶子数量 0–20 步长 1            |
| `sweepSpeed`     | number | `1`             | 扫动速度 0.3–3 步长 0.05              |
| `retainedBreeze` | number | `1`             | 保留的叶子微风 0–2 步长 0.05          |

## 运行时合约

- 一个注册为 `window.__timelines["canopy-part-title"]` 的暂停的GSAP时间轴。
- 在 `hf-seek` CustomEvent上重新同步；每一帧都是时间的闭式函数（仅使用种子PRNG，无rAF循环，无Date.now）。
- 渲染器：three.js 0.170.0，GSAP 3.14.2，Canvas 2D，后处理，种子PRNG，阴影映射。每个活动实例的大致预算为350 MB；一次运行一个。
- 外部运行时依赖项：`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`，`https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js`，`https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/postprocessing/EffectComposer.js`，`https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/postprocessing/RenderPass.js`，`https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/postprocessing/BokehPass.js`。
- 来自Google Fonts的网页字体：Gelasio。

## 编辑规则（来自源项目）

1. 保持 `data-composition-variables` 为单引号属性，使用纯 `"` JSON。切勿通过Studio的设计面板保存。
2. 不要将 `<canvas>` 放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为t的函数；seek安全性是使模块可渲染的关键。
