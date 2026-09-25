# 代码切片英雄

一个完整的方形瓦片表面承载着一条无缝标题。一个想象中的光标穿过表面；附近的瓦片会根据其高斯深度场进行抬升和倾斜，并且只有与标题轮廓相交的单元格会翻转以显示后方的标题。整个网格是一个实例化的 WebGL 2 绘制，共享一个前后纹理对，再加上一个分批投影阴影的渲染过程。复制、文本大小和方形单元格大小是独立的，因此瓦片不会拉伸。扫描方向、缓动强度、光标半径、衰减、深度、弹跳和阴影都是可变的。

组合 ID: `code-slice-hero`。在 30 fps 下持续 8 秒，分辨率为 1920×1080。

## 文件

- `code-slice-hero.html` (24 KB)
- `assets/Geist-Bold.ttf` (65 KB)
- `assets/Geist-OFL.txt` (4 KB)
- `assets/gsap-3.14.2.min.js` (128 KB)
- `assets/GSAP-NOTICE.txt` (1 KB)
- `shadows.js` (10 KB)
- `surface.js` (8 KB)

## 安装

使用 `npx hyperframes add code-slice-hero` 安装；默认情况下，上述文件会放置在 `compositions/code-slice-hero/` 下。然后从主机 `index.html` 中挂载该模块：

```html
<div
  data-composition-id="code-slice-hero"
  data-composition-src="compositions/code-slice-hero/code-slice-hero.html"
  data-start="0"
  data-duration="8"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

通过直接指向组合文件来使用自定义值：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/code-slice-hero/code-slice-hero.html' --variables '{"headline":"MAKE IT","reverseHeadline":"MATTER."}'
```

## 变量

通过 `window.__hyperframes.getVariables()` 在运行时读取；在组合根节点上声明为 `data-composition-variables`（单引号属性，纯 JSON）。

| ID                  | 类型   | 默认           | 标签 / 范围                                     |
| ------------------- | ------ | ----------------- | ------------------------------------------------- | -------------- |
| `headline`          | 字符串 | `"MAKE IT"`       | 文本 · 前方标题最多 32 个字符                |
| `reverseHeadline`   | 字符串 | `"MATTER."`       | 文本 · 后方标题最多 32 个字符                 |
| `direction`         | 枚举   | `"left-to-right"` | 动画 · 扫描方向 (从左到右 或 从右到左)           |
| `sweepDuration`     | 数字   | `4.2`             | 动画 · 扫描持续时间 2.6–4.5 步长 0.05         |
| `sweepEaseStrength` | 数字   | `3`               | 动画 · 扫描缓动强度 0–3 步长 0.05              |
| `flipDuration`      | 数字   | `0.75`            | 动画 · 每个瓦片翻转 0.65–1.65 步长 0.05       |
| `cursorRadius`      | 数字   | `210`             | 光标 · 影响半径 160–480 步长 10             |
| `cursorFalloff`     | 数字   | `1.4`             | 光标 · 影响衰减 0.4–3.5 步长 0.05              |
| `cursorDepth`       | 数字   | `80`              | 光标 · 深度 (+ 向相机) -320–320 步长 10        |
| `tiltStrength`      | 数字   | `55`              | 光标 · 拉伸/倾斜强度 0–55 步长 1             |
| `noiseStrength`     | 数字   | `2`               | 动画 · 有机变化 0–2 步长 0.05                 |
| `flipBounce`        | 数字   | `0.15`            | 动画 · 弹性翻转弹跳 0–0.8 步长 0.05           |
| `cellSize`          | 数字   | `112`             | 切片 · 方形单元格大小 24–120 步长 4           |
| `formationScale`    | 数字   | `1`               | 切片 · 局部形成比例 0.94–1 步长 0.001          |
| `fontSize`          | 数字   | `310`             | 字体 · 最大大小 160–480 步长 5                |
| `behindColor`       | 颜色  | `"#212121"`       | 表面 · 后方瓦片背景                          |
| `shadowStrength`    | 数字   | `0.19`            | 表面 · 投影阴影强度 0–0.65 步长 0.01           |
| `shadowSoftness`    | 数字   | `4`               | 表面 · 投影阴影柔和度 0.5–4 步长 0.1          |

## 运行时合约

- 一个作为 `window.__timelines["code-slice-hero"]` 注册的暂停 GSAP 时间线。
- 在 `hf-seek` CustomEvent 上重新同步；每一帧都是时间的闭式函数（仅使用种子 PRNG，不使用 rAF 循环，不使用 Date.now）。
- 渲染器：GSAP、Canvas 2D、种子 PRNG。
- 外部运行时依赖项：无（本地提供）。
- 本地字体：assets/Geist-Bold.ttf。

## 编辑规则（来自源项目）

1. 保持 `data-composition-variables` 为单引号属性，使用纯 `"` JSON。切勿通过 Studio 的设计面板保存。
2. 不要将 `<canvas>` 放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为 t 的函数；seek 安全性是使模块可渲染的关键。
