# 线框门户标题

通过TTF加载器和多边形偏移，从捆绑的Geist字体构建的挤压线框字母，然后通过一个混乱程度可变的门户爆发效果展现出来。第二个节拍将字母替换为替换短语，带有整词换行和自动类型大小，使用可调节的缓动曲线和沉降故障效果进行错落排列，并可选添加深度雾。

组合ID：`wireframe-portal-title`。在30fps下持续8秒，分辨率为1920×1080。

## 文件

- `wireframe-portal-title.html` (63 KB)
- `assets/fonts/Geist-Bold.ttf` (65 KB)
- `assets/fonts/Geist-Regular.ttf` (65 KB)
- `assets/fonts/Geist-SemiBold.ttf` (65 KB)
- `assets/fonts/Geist-OFL.txt` (4 KB)

## 安装

使用`npx hyperframes add wireframe-portal-title`进行安装；默认情况下，上述文件会放置在`compositions/wireframe-portal-title/`目录下。然后从主机`index.html`中挂载该模块：

```html
<div
  data-composition-id="wireframe-portal-title"
  data-composition-src="compositions/wireframe-portal-title/wireframe-portal-title.html"
  data-start="0"
  data-duration="8"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

通过自定义值直接渲染组合文件：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/wireframe-portal-title/wireframe-portal-title.html' --variables '{"title":"BREAKTHROUGH","replacementPhrase":"Lets do this sir!"}'
```

## 变量

通过`window.__hyperframes.getVariables()`在运行时读取；在组合根节点上声明为`data-composition-variables`（单引号属性，纯JSON格式）。

| id                  | 类型    | 默认值                      | 标签/范围                                       |
| ------------------- | ------- | ---------------------------- | --------------------------------------------------- |
| `title`             | 字符串  | `"BREAKTHROUGH"`             | 标题最多18个字符                                |
| `replacementPhrase` | 字符串  | `"Lets do this sir!"`        | 3D替换短语（自动布局）                          |
| `phraseDuration`    | 数字    | `1.85`                       | 短语过渡持续时间(s) 0.65–2.9 步长0.05          |
| `phraseEasing`      | 数字    | `8`                          | 过渡缓动（1温和 – 8突然） 1–8 步长0.25          |
| `settleGlitch`      | 数字    | `0.2`                        | 字母沉降故障强度 0–4 步长0.05                  |
| `depthFog`          | 布尔值  | `true`                       | 深度雾（早期淡出始终开启）                      |
| `subtitle`          | 字符串  | `"HYPERFRAMES PORTAL TITLE"` | 副标题最多48个字符                            |
| `accent`            | 颜色   | `"#F5C518"`                  | 强调色                                            |
| `burstChaos`        | 数字    | `1`                          | 爆发混乱度（0-2） 0–2 步长0.01                |

## 运行时合约

- 一个注册为`window.__timelines["wireframe-portal-title"]`的暂停的GSAP时间轴。
- 在`hf-seek` CustomEvent上重新同步；每一帧都是时间的闭式函数（仅使用种子PRNG，无rAF循环，无Date.now）。
- 渲染器：three.js 0.181.2，GSAP 3.14.2，Canvas 2D，GLSL着色器，后处理，种子PRNG，Clipper。每个活动实例的大致预算为350 MB；一次运行一个。
- 外部运行时依赖：`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`，`https://cdn.jsdelivr.net/npm/clipper-lib@6.4.2/clipper.js`，`https://cdn.jsdelivr.net/npm/three@0.181.2/build/three.module.js`，`https://cdn.jsdelivr.net/npm/three@0.181.2/examples/jsm/`。
- 本地字体：assets/fonts/Geist-Regular.ttf，assets/fonts/Geist-SemiBold.ttf，assets/fonts/Geist-Bold.ttf。

## 编辑规则（来自源项目）

1. 保持`data-composition-variables`为单引号属性，使用纯`"` JSON。切勿通过Studio的设计面板保存它。
2. 不要在静态标记中放置`<canvas>`；在运行时创建它。
3. 保持每个视觉状态为t的函数；seek安全性是使模块可渲染的关键。
