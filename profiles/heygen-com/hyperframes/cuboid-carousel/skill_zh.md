# 长方体轮播

带有卡片内容的圆角斜切长方体从右侧作为一个刚性组飞入，以每个长方体旋转错位巡航，减速到英雄定格，然后从左侧退出。间距由长方体尺寸和最大可达的X半尺寸决定，因此长方体永远不会重叠。四十个变量携带原始DialKit架构：几何形状、材质、灯光、阴影、背景、相机以及每个片段的持续时间和缓动效果。卡片来自内置列表或JSON变量。

组合ID：`cuboid-carousel`。在30fps下持续时间为6.666666666666667秒，分辨率为1920×1080。

## 文件

- `cuboid-carousel.html` (38 KB)
- `assets/Three-LICENSE.txt` (1 KB)
- `assets/addons/environments/RoomEnvironment.js` (5 KB)
- `assets/addons/utils/BufferGeometryUtils.js` (36 KB)
- `assets/cuboid-motion.js` (593 KB)
- `assets/gsap-3.14.2.min.js` (128 KB)
- `assets/GSAP-NOTICE.txt` (1 KB)
- `assets/three.core.min.js` (554 KB)
- `assets/three.module.min.js` (468 KB)

## 安装

使用`npx hyperframes add cuboid-carousel`安装；默认情况下，上述文件将放置在`compositions/cuboid-carousel/`下。然后从主机`index.html`挂载该模块：

```html
<div
  data-composition-id="cuboid-carousel"
  data-composition-src="compositions/cuboid-carousel/cuboid-carousel.html"
  data-start="0"
  data-duration="6.666666666666667"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

通过直接指向组合文件来使用自定义值进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/cuboid-carousel/cuboid-carousel.html' --variables '{"cardsJson":"","heroCard":4}'
```

## 变量

通过`window.__hyperframes.getVariables()`在运行时读取；在组合根上声明为`data-composition-variables`（单引号属性，纯JSON）。

| ID                  | 类型   | 默认值     | 标签/范围                                        |
| ------------------- | ------ | ----------- | ---------------------------------------------------- |
| `cardsJson`         | 字符串 | `""`        | 内容 · 卡片JSON（可选，见源代码中的CARDS） |
| `heroCard`          | 数字   | `4`         | 内容 · 英雄卡片（1基）1–12步长1            |
| `count`             | 数字   | `8`         | 内容 · 重复卡片数量1–12步长1           |
| `gap`               | 数字   | `0.01`      | 布局 · 长方体之间的额外间隙0–1.5步长0.005  |
| `cuboidWidth`       | 数字   | `1.7`       | 长方体 · 宽度0.3–5步长0.01                       |
| `cuboidHeight`      | 数字   | `2.4`       | 长方体 · 高度0.3–6步长0.01                      |
| `cuboidDepth`       | 数字   | `0.14`      | 长方体 · 厚度（深度）0.02–2步长0.01          |
| `cornerRadius`      | 数字   | `0.105`     | 长方体 · 角半径0–0.6步长0.005              |
| `bevelSize`         | 数字   | `0.03`      | 长方体 · 斜切大小（边缘倒角）0–0.3步长0.001  |
| `bevelThickness`    | 数字   | `0.04`      | 长方体 · 斜切厚度0–0.3步长0.001            |
| `smoothness`        | 数字   | `32`        | 长方体 · 光滑度（片段）1–32步长1           |
| `bodyColor`         | 颜色  | `"#242424"` | 长方体 · 身体颜色                                 |
| `roughness`         | 数字   | `0.6`       | 长方体 · 粗糙度0–1步长0.01                     |
| `metalness`         | 数字   | `0.4`       | 长方体 · 金属度0–1步长0.01                     |
| `heroScale`         | 数字   | `1`         | 英雄 · 独立缩放1–1.6步长0.01                |
| `heroFillIntensity` | 数字   | `0.55`      | 英雄 · 脸部光照强度0–2步长0.05            |
| `heroExitX`         | 数字   | `288`       | 英雄 · 退出X旋转角度-720–720步长1       |
| `heroExitY`         | 数字   | `-234`      | 英雄 · 退出Y旋转角度-720–720步长1       |
| `heroExitZ`         | 数字   | `198`       | 英雄 · 退出Z旋转角度-720–720步长1       |
| `ambientIntensity`  | 数字   | `0.35`      | 灯光 · 环境强度0–4步长0.01             |
| `ambientColor`      | 颜色  | `"#ffffff"` | 灯光 · 环境颜色                              |
| `topIntensity`      | 数字   | `3.1`       | 灯光 · 顶部桁架强度0–12步长0.05            |
| `topColor`          | 颜色  | `"#ffffff"` | 灯光 · 顶部桁架颜色                              |
| `bottomIntensity`   | 数字   | `2.15`      | 灯光 · 底部桁架强度0–12步长0.05         |
| `bottomColor`       | 颜色  | `"#ffcaad"` | 灯光 · 底部桁架颜色                           |
| `keyIntensity`      | 数字   | `5`         | 灯光 · 关键桁架强度0–12步长0.05            |
| `keyColor`          | 颜色  | `"#ffe9d6"` | 灯光 · 关键桁架颜色                              |
| `shadowRadius`      | 数字   | `44.5`      | 阴影 · 地图尺寸下的柔和度2048 0–50步长0.5    |
| `shadowMapSize`     | 数字   | `2048`      | 阴影 · 地图尺寸512–4096步长256                 |
| `backdrop`          | 颜色  | `"#0b0d13"` | 背景 · 颜色                                  |
| `cameraFov`         | 数字   | `11`        | 相机 · 初始视场10–90步长0.5        |
| `cameraX`           | 数字   | `-1.65`     | 相机 · 初始X -20–20步长0.05                  |
| `cameraY`           | 数字   | `8.5`       | 相机 · 初始Y -20–20步长0.05                  |
| `cameraZ`           | 数字   | `-8.508708` | 相机 · 初始Z（距离）-20–50步长0.1        |
| `cameraSettleFrame` | 数字   | `70`        | 相机 · 定格帧（30fps）20–90步长1          |
| `handheldStrength`  | 数字   | `1`         | 相机 · 手持定格强度0–1步长0.05        |
| `cameraTargetFov`   | 数字   | `34`        | 相机目标 · 视场10–90步长0.5         |
| `cameraTargetX`     | 数字   | `-7.25`     | 相机目标 · X -20–20步长0.05                   |
| `cameraTargetY`     | 数字   | `1.15`      | 相机目标 · Y -20–20步长0.05                   |
| `cameraTargetZ`     | 数字   | `6.2`       | 相机目标 · Z 2–50步长0.1                      |

## 运行时契约

- 一个已注册为`window.__timelines["cuboid-carousel"]`的暂停GSAP时间轴。
- 在`hf-seek` CustomEvent上重新同步；每一帧都是时间的闭式函数（仅使用种子PRNG，无rAF循环，无Date.now）。
- 渲染器：WebGL、GSAP、Canvas 2D、PMREM、阴影映射。每个活动实例的大致预算为350 MB；一次运行一个。
- 外部运行时依赖项：`./assets/three.module.min.js`、`./assets/addons/`。
- 来自Google Fonts的Web字体：Inter。

## 编辑规则（来自源项目）

1. 保持`data-composition-variables`为单引号属性，使用纯`"` JSON。切勿通过Studio的Design面板保存它。
2. 不要将`<canvas>`放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为t的函数；seek安全性是使模块可渲染的关键。
