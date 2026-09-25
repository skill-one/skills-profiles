# 轨道卡片

一张居中的特色卡片，带有圆形镂空，框住一个点状球体。卡片从右侧进入（0.25–1.80秒），保持时带有微妙的上下浮动和深度漂移，绕着球体中心完整旋转一圈（4.97至5.97秒之间平滑过渡），然后从左侧退出（7.35–8.55秒）。相机路径和卡片F曲线从批准的Blender rig导出，以30fps进行插值；球体保持自身的平移和恒定旋转。标题、描述、强调色和轨道角度是变量；180°和720°无需按键即可使用。

构图ID：`orbit-card`。30fps下时长10秒，1920×1080。

## 文件

- `orbit-card.html` (3 KB)
- `assets/Archivo-LICENSE.txt` (4 KB)
- `assets/Three-LICENSE.txt` (1 KB)
- `assets/archivo-regular.ttf` (108 KB)
- `assets/archivo-semibold.ttf` (109 KB)
- `assets/gsap-3.14.2.min.js` (128 KB)
- `assets/GSAP-NOTICE.txt` (1 KB)
- `assets/orbit-motion.js` (59 KB)
- `assets/orbit-scene.js` (8 KB)
- `assets/three.core.min.js` (554 KB)
- `assets/three.module.min.js` (468 KB)

## 安装

使用 `npx hyperframes add orbit-card` 安装；默认情况下上述文件会放置在 `compositions/orbit-card/` 下。然后从主机 `index.html` 中挂载该模块：

```html
<div
  data-composition-id="orbit-card"
  data-composition-src="compositions/orbit-card/orbit-card.html"
  data-start="0"
  data-duration="10"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

通过直接指向构图文件使用自定义值进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/orbit-card/orbit-card.html' --variables '{"feature1Title":"Always in sync","feature1Desc":"Changes reach every screen the moment they happen."}'
```

## 变量

通过 `window.__hyperframes.getVariables()` 在运行时读取；在构图根节点上声明为 `data-composition-variables`（单引号属性，纯JSON格式）。

| id                 | 类型   | 默认值                                                | 标签 / 范围                          |
| ------------------ | ------ | ------------------------------------------------------ | -------------------------------------- |
| `feature1Title`    | 字符串 | `"Always in sync"`                                     | 卡片标题最多28个字符                |
| `feature1Desc`     | 字符串 | `"Changes reach every screen the moment they happen."` | 卡片描述最多110个字符               |
| `feature1Accent`   | 颜色  | `"#4cc9ff"`                                            | 卡片强调色                          |
| `cardOrbitDegrees` | 数字   | `360`                                                  | 卡片轨道角度 -36000–36000 步长1 |

## 运行时合约

- 一个注册为 `window.__timelines["orbit-card"]` 的暂停GSAP时间轴。
- 在 `hf-seek` CustomEvent上重新同步；每一帧都是时间的闭式函数（仅使用种子PRNG，无rAF循环，无Date.now）。
- 渲染器：GSAP。
- 外部运行时依赖：无（本地提供）。
- 本地字体：assets/archivo-regular.ttf, assets/archivo-semibold.ttf。

## 编辑规则（来自源项目）

1. 保持 `data-composition-variables` 为单引号属性，使用纯 `"` JSON。切勿通过Studio的Design面板保存。
2. 不要在静态标记中放置 `<canvas>`；在运行时创建它。
3. 保持每个视觉状态为t的函数；搜索安全性是使模块可渲染的关键。
