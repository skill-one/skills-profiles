# 玻璃碎片标题

Voronoi切割的玻璃窗格从深处飞入，旋转着，最终以标题的瓦片剪影形式着陆，然后飞过相机。每个碎片都是其Voronoi单元中一个抖动的块的Sutherland-Hodgman剪切，因此碎片始终覆盖文字。玻璃和matcap表面获得每片片段的雾；z飞行与易用性解耦，因此碎片明显穿越它。瓦片计数1给出一个单独的窗格。

组合id: `glass-shard-title`。在30 fps下持续时间为12.16秒，分辨率为1920×1080。

## 文件

- `glass-shard-title.html` (16 KB)
- `assets/ferndale_studio_01_1k.hdr` (1.6 MB)
- `assets/fonts/Geist-Bold.ttf` (65 KB)
- `assets/fonts/Geist-Regular.ttf` (65 KB)
- `assets/fonts/Geist-SemiBold.ttf` (65 KB)
- `assets/fonts/Geist-OFL.txt` (4 KB)
- `assets/fonts/cormorant-garamond.woff2` (37 KB)
- `assets/fonts/CormorantGaramond-OFL.txt` (4 KB)
- `assets/glass-main.js` (549 KB)
- `assets/Three-LICENSE.txt` (1 KB)
- `assets/matcap-1.png` (在安装时从CDN获取)

## 安装

使用`npx hyperframes add glass-shard-title`进行安装；默认情况下，上述文件将位于`compositions/glass-shard-title/`下。然后从主机`index.html`挂载该模块：

```html
<div
  data-composition-id="glass-shard-title"
  data-composition-src="compositions/glass-shard-title/glass-shard-title.html"
  data-start="0"
  data-duration="12.16"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

使用自定义值通过直接定位组合文件进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/glass-shard-title/glass-shard-title.html' --variables '{"headline":"Designed in glass","tileCount":8}'
```

## 变量

在运行时通过`window.__hyperframes.getVariables()`读取；在组合根上声明为`data-composition-variables`（单引号属性，纯JSON）。

| id               | 类型   | 默认               | 标签/范围                                 |
| ---------------- | ------ | --------------------- | --------------------------------------------- |
| `headline`       | 字符串 | `"Designed in glass"` | 标题最多40个字符                         |
| `tileCount`      | 数字   | `8`                   | 瓦片1–400步长1                            |
| `roundness`      | 数字   | `0.4`                 | 圆度（0-1）0–1步长0.01                 |
| `bevel`          | 数字   | `0.35`                | 斜角（0-1）0–1步长0.01                     |
| `meshSmooth`     | 数字   | `0.6`                 | 表面平滑度（0-1）0–1步长0.01        |
| `flyInTime`      | 数字   | `2.3`                 | 飞入时间（秒）0.2–6步长0.05               |
| `flyOutTime`     | 数字   | `2.4`                 | 飞出时间（秒）0.2–6步长0.05              |
| `stagger`        | 数字   | `0.27`                | 错位（0-1）0–1步长0.01                   |
| `flyInRotation`  | 数字   | `5`                   | 飞入旋转（0-60）0–60步长0.1          |
| `flyOutRotation` | 数字   | `6`                   | 飞出旋转（0-6）0–6步长0.1           |
| `chaos`          | 数字   | `0.25`                | 轮廓混乱（0-1）0–1步长0.01             |
| `padding`        | 数字   | `1`                   | 边缘填充（0-1）0–1步长0.01              |
| `sizeVariance`   | 数字   | `0.35`                | 尺寸变化（0-1）0–1步长0.01             |
| `gap`            | 数字   | `0.03`                | 瓦片间隙0–0.3步长0.002                     |
| `easePow`        | 数字   | `10`                  | 飞入位置缓动（1-10）1–10步长0.1     |
| `sideDist`       | 数字   | `3`                   | 侧飞距离0–60步长0.5               |
| `zDist`          | 数字   | `-42`                 | z飞入（负数）-400–0步长2           |
| `zOut`           | 数字   | `14`                  | z飞出到（+ = 过相机）-400–60步长2 |
| `fog`            | 数字   | `36`                  | 雾距离（0 = 关闭）0–400步长2           |

## 运行时合约

- 一个暂停的GSAP时间轴注册为`window.__timelines["glass-shard-title"]`。
- 在`hf-seek` CustomEvent上重新同步；每一帧都是时间的闭式函数（仅使用种子PRNG，不使用rAF循环，不使用Date.now）。
- 渲染器：three.js 0.181.2（捆绑），GSAP 3.14.2，Canvas 2D，GLSL着色器，HDR环境，Matcap，种子PRNG，d3-delaunay，阴影映射。每个活动实例的预算大约为350 MB；一次运行一个。
- 外部运行时依赖项：`https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`，`https://cdn.jsdelivr.net/npm/d3-delaunay@6.0.4/dist/d3-delaunay.min.js`。
- 本地字体：assets/fonts/Geist-Regular.ttf，assets/fonts/Geist-SemiBold.ttf，assets/fonts/Geist-Bold.ttf。
- 捆绑代码已内联到组合中（assets/glass-main.js）；编辑.mjs源文件后，使用esbuild重新构建并重新内联。

## 编辑规则（从源项目）

1. 保持`data-composition-variables`为单引号属性，使用纯`"` JSON。切勿通过Studio的设计面板保存它。
2. 不要将`<canvas>`放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为t的函数；seek安全性是使模块可渲染的因素。
