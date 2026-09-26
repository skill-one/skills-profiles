# Frost Sequence Camera Orbit

一个完整的22.5秒冰晶序列：标志、第一行文字、第二行文字、破碎和淡出。摄像机围绕固定物体进行轨道运动，并使用较慢的前向飞越进行读取。相同的粒子场承载每个过渡。自定义两个文字时刻和SVG标志；源代码包含可编辑的摄像机和装配时间。

Composition id: `frost-sequence-rig`。时长22.5秒，30 fps，1920×1080。

## 文件

- `frost-sequence-camera-orbit.html` (131 KB)
- `assets/example-logo.svg` (1 KB)
- `assets/fonts/Geist-Bold.ttf` (65 KB)
- `assets/fonts/Geist-OFL.txt` (4 KB)
- `assets/fonts/Geist-Regular.ttf` (65 KB)
- `assets/fonts/Geist-SemiBold.ttf` (65 KB)
- `assets/frost.js` (1.5 MB)
- `assets/Three-LICENSE.txt` (1 KB)
- `assets/ThreeMeshBVH-LICENSE.txt` (1 KB)
- `assets/OpentypeJS-LICENSE.txt` (1 KB)
- `assets/Clipper-LICENSE.txt` (3 KB)
- `assets/gsap-3.14.2.min.js` (128 KB)
- `assets/GSAP-NOTICE.txt` (1 KB)
- `assets/logo.svg` (1 KB)
- `assets/shards-atlas.png` (安装时从CDN获取)
- `assets/test-mark.svg` (1 KB)
- `assets/textures/bluenoise64.png` (12 KB)
- `assets/textures/ice-inclusions-generated.png` (安装时从CDN获取)

## 安装

使用 `npx hyperframes add frost-sequence-camera-orbit` 安装；默认情况下，上述文件位于 `compositions/frost-sequence-camera-orbit/` 下。然后从主机 `index.html` 挂载该模块：

```html
<div
  data-composition-id="frost-sequence-rig"
  data-composition-src="compositions/frost-sequence-camera-orbit/frost-sequence-camera-orbit.html"
  data-start="0"
  data-duration="22.5"
  data-track-index="1"
  data-width="1920"
  data-height="1080"
></div>
```

使用自定义值通过直接定位Composition文件进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/frost-sequence-camera-orbit/frost-sequence-camera-orbit.html' --variables '{"headline1":"Hard to|break.","headline2":"Easy to|remember."}'
```

## 变量

通过 `window.__hyperframes.getVariables()` 在运行时读取；在Composition根节点上声明为 `data-composition-variables`（单引号属性，纯JSON）。

| id                          | type    | default             | label / 范围                                                                                 |
| --------------------------- | ------- | ------------------- | --------------------------------------------------------------------------------------------- | ------------- | -------------------------- | ------- | ------- |
| `headline1`                 | string  | `"Hard to           | break."`                                                                                      | 第一行文字 (  | = 换行) 最大60个字符 |
| `headline2`                 | string  | `"Easy to           | remember."`                                                                                   | 第二行文字 ( | = 换行) 最大60个字符 |
| `logoUrl`                   | string  | `"assets/logo.svg"` | Logo SVG资源路径（上传到Assets，然后粘贴路径）最大200个字符                         |
| `assemblyMode`              | enum    | `"hybrid"`          | 装配响应（物理                                                                   | 指向) 混合) |
| `materialBaseColor`         | color   | `"#ffffff"`         | 基础颜色                                                                                    |
| `baseRoughness`             | number  | `0.31`              | 基础粗糙度 0–0.5 步长 0.005                                                               |
| `materialTransmission`      | boolean | `true`              | 透射                                                                                  |
| `materialBacklight`         | number  | `0.27`              | 冰层透射 0–2 步长 0.01                                                           |
| `ior`                       | number  | `1.675`             | 折射率 1–2 步长 0.005                                                            |
| `thicknessScale`            | number  | `2.04`              | 厚度比例 0.1–3 步长 0.01                                                               |
| `materialAbsorption`        | boolean | `true`              | 吸收 / 染色                                                                             |
| `attenuationColor`          | color   | `"#d5f4ff"`         | 衰减颜色（白色 = 无吸收，透明玻璃）                                       |
| `attenuationDistance`       | number  | `6.54`              | 衰减距离 0.05–12 步长 0.01                                                        |
| `materialDispersion`        | boolean | `false`             | 散射                                                                                    |
| `dispersion`                | number  | `0.12`              | 散射（0 = 关闭；开/关重新加载） 0–0.3 步长 0.005                                         |
| `materialReflections`       | boolean | `true`              | 反射                                                                                   |
| `envIntensity`              | number  | `2.04`              | 环境强度 0–3 步长 0.01                                                           |
| `specularIntensity`         | number  | `1.44`              | 镜面强度 0–2 步长 0.01                                                              |
| `materialFrost`             | boolean | `true`              | 冰霜                                                                                         |
| `materialInteriorFrost`     | number  | `0`                 | 均匀冰霜 0–1 步长 0.01                                                                   |
| `frostScale`                | number  | `0.7`               | 比例 0.2–6 步长 0.05                                                                         |
| `frostThreshold`            | number  | `0.62`              | 阈值（1 = 无冰霜，透明玻璃） 0–1 步长 0.01                                           |
| `frostSoftness`             | number  | `0.24`              | 柔和度 0.01–1 步长 0.01                                                                     |
| `frostRoughness`            | number  | `0.73`              | 粗糙度 0–1 步长 0.01                                                                       |
| `frostDiffuse`              | number  | `0.11`              | 漫射（冰霜区域捕获多少光线） 0–1 步长 0.01                                    |
| `materialSurfaceBumps`      | boolean | `false`             | 物体表面凸起 / 裂缝凹槽                                                          |
| `materialCrystals`          | boolean | `true`              | 晶体凸起                                                                                 |
| `crystalBump`               | number  | `0.01`              | 晶体凸起 0–1 步长 0.01                                                                    |
| `crystalScale`              | number  | `4`                 | 晶体比例 4–80 步长 1                                                                     |
| `materialGrain`             | boolean | `true`              | 颗粒凸起                                                                                   |
| `materialGrainAmount`       | number  | `0.47`              | 颗粒强度 0–2 步长 0.01                                                                  |
| `materialGrainScale`        | number  | `150`               | 颗粒比例 1–150 步长 1                                                                      |
| `materialCutNormals`        | boolean | `true`              | 裂缝法线                                                                              |
| `materialMicro`             | boolean | `true`              | 微型凸起                                                                                   |
| `microBump`                 | number  | `0.445`             | 微型凸起 0–1 步长 0.005                                                                     |
| `microScale`                | number  | `10`                | 微型比例 10–200 步长 1                                                                     |
| `microCoverage`             | number  | `0.25`              | 微型覆盖率 0–1 步长 0.01                                                                  |
| `bumpMaskScale`             | number  | `1.45`              | 掩码比例 0.1–6 步长 0.05                                                                    |
| `materialRipples`           | boolean | `true`              | 涟漪                                                                                       |
| `rippleBump`                | number  | `0.22`              | 涟漪凸起 0–1 步长 0.01                                                                     |
| `rippleScale`               | number  | `23`                | 涟漪比例 2–30 步长 0.5                                                                    |
| `materialSmudges`           | boolean | `true`              | 污渍                                                                                       |
| `smudgeAmount`              | number  | `0.78`              | 量 0–1 步长 0.01                                                                          |
| `smudgeCoverage`            | number  | `0.58`              | 覆盖率 0–1 步长 0.01                                                                        |
| `smudgeMaskScale`           | number  | `1.85`              | 掩码比例 0.1–6 步长 0.05                                                                    |
| `smudgeAnisotropy`          | number  | `16.5`              | 各向异性 1–20 步长 0.5                                                                      |
| `smudgeRoughness`           | number  | `0.75`              | 粗糙度 0–1 步长 0.01                                                                       |
| `smudgeWhiteness`           | number  | `0.035`             | 白度 0–0.5 步长 0.005                                                                    |
| `smudgeScale`               | number  | `1.3`               | 比例 0.5–10 步长 0.1                                                                         |
| `materialCracks`            | boolean | `true`              | 裂缝                                                                                        |
| `crackLargeScale`           | number  | `2.45`              | 大比例 0.3–8 步长 0.05                                                                   |
| `crackWarp`                 | number  | `0.22`              | 扭曲 0–1.5 步长 0.01                                                                          |
| `crackCoverage`             | number  | `0.19`              | 覆盖率 0–1 步长 0.01                                                                        |
| `crackRegionScale`          | number  | `1.8`               | 区域比例 0.1–4 步长 0.05                                                                  |
| `crackRegionCoverage`       | number  | `0.6`               | 区域覆盖率 0–1 步长 0.01                                                                 |
| `veinScale`                 | number  | `8`                 | 脉管比例 1–20 步长 0.25                                                                     |
| `veinContrast`              | number  | `0.55`              | 脉管对比度 0–1 步长 0.01                                                                   |
| `crackWidth`                | number  | `0.0025`            | 宽度 0.0005–0.02 步长 0.0005                                                                 |
| `crackBrightness`           | number  | `0.65`              | 亮度 0–3 步长 0.01                                                                      |
| `crackDarkness`             | number  | `0.69`              | 黑暗 0–1 步长 0.01                                                                        |
| `crackRefraction`           | number  | `0.076`             | 折射 0–0.1 步长 0.001                                                                   |
| `crackSurfaceStrength`      | number  | `0.16`              | 表面强度 0–1 步长 0.01                                                                |
| `fineScale`                 | number  | `18.4`              | 精细比例 2–20 步长 0.1                                                                      |
| `fineAmount`                | number  | `0.52`              | 精细量 0–1 步长 0.01                                                                     |
| `fineCoverage`              | number  | `1`                 | 精细覆盖率 0–1 步长 0.01                                                                   |
| `materialScatter`           | boolean | `true`              | 内部散射                                                                           |
| `materialInclusionScale`    | number  | `0.05`              | 包裹比例 0.05–3 步长 0.01                                                              |
| `materialInclusionAmount`   | number  | `2`                 | 照片包裹 0–2 步长 0.01                                                         |
| `interiorScatter`           | number  | `0.09`              | 内部散射 0–1 步长 0.01                                                                |
| `materialClearcoat`         | boolean | `true`              | 透明涂层                                                                                     |
| `clearcoat`                 | number  | `0`                 | 透明涂层 0–1 步长 0.01                                                                       |
| `clearcoatRoughness`        | number  | `0`                 | 透明涂层粗糙度 0–1 步长 0.005                                                            |
| `materialShardNormals`      | boolean | `true`              | 碎片法线                                                                                 |
| `spriteNormal`              | number  | `0.15`              | 精灵法线强度 0–2.5 步长 0.05                                                        |
| `materialShardFrost`        | boolean | `true`              | 碎片冰霜                                                                                   |
| `materialShardTransmission` | boolean | `true`              | 碎片透明                                                                            |
| `spriteSeeThrough`          | number  | `1`                 | 透视（0 = 关闭；开/关重新加载） 0–1 步长 0.01                                           |
| `materialShardReflections`  | boolean | `true`              | 碎片反射                                                                             |
| `minPixelSize`              | number  | `0.25`              | 最小像素大小 0–4 步长 0.05                                                              |
| `grainSizeMultiplier`       | number  | `1.05`              | 颗粒大小乘数 0.2–4 步长 0.05                                                         |
| `spriteSize`                | number  | `1.9`               | 精灵大小 0.3–4 步长 0.05                                                                   |
| `spriteTilt`                | number  | `12`                | 精灵倾斜 0–70 步长 1                                                                       |
| `spriteAlphaCut`            | number  | `0.6`               | Alpha切割 0.05–0.6 步长 0.01                                                                  |
| `fontWeight`                | enum    | `"600"`             | 类型 · 重量 (Geist) (400                                                                    | 600           | 700)                       |
| `letterSpacing`             | number  | `0.01`              | 类型 · 字母间距 -0.1–0.4 步长 0.005                                                     |
| `shardAmount`               | number  | `0.44`              | 碎片 · 破碎体积的可见部分（粉末量） 0.02–1 步长 0.01               |
| `strayDust`                 | number  | `24`                | 碎片 · 物体周围的漫反射尘埃 (实验中有 40) 0–200 步长 1            |
| `sliceRadius`               | number  | `0.6`               | 破碎 · 第一个（对角线）切片半径 0.05–1.5 步长 0.01                                      |
| `sliceStrength`             | number  | `21.5`              | 破碎 · 第一个切片强度 1–40 步长 0.5                                                    |
| `finalEjectBoost`           | number  | `2.5`               | 破碎 · 最后破碎：喷射速度和速度限制乘数 1–6 步长 0.1                         |
| `shatterRadius`             | number  | `0.45`              | 破碎 · 随后切片半径（也设置它们的间距） 0.1–1.5 步长 0.01                     |
| `shatterStrength`           | number  | `32.5`              | 破碎 · 随后切片强度 1–40 歡长 0.5                                                |
| `cutThreshold`              | number  | `0.3`               | 调整破碎 · 切割阈值（表面高于此侵蚀） 0.3–0.98 步长 0.01               |
| `cutSoftness`               | number  | `0.19`              | 调整破碎 · 切割柔和度 0.005–0.3 步长 0.005                                                |
| `edgeWidth`                 | number  | `0.19`              | 调整破碎 · 碎片边缘带宽 0.05–0.8 步长 0.01                                       |
| `edgeInset`                 | number  | `0`                 | 调整破碎 · 边缘插入 0–0.3 步长 0.005                                                      |
| `brushSoftness`             | number  | `0.15`              | 调整破碎 · 刷子柔和度（切片边缘衰减） 0.02–1 步长 0.01                        |
| `brushNoise`                | number  | `0.4`               | 调整破碎 · 刷子噪声（粗糙边界） 0–1 步长 0.01                                      |
| `crumbleRate`               | number  | `4.3`               | 调整破碎 · 裂缝沿裂缝的崩溃速率（高 = 整个形状同时崩溃） 0–6 步长 0.05    |
| `crumbleCrackBias`          | number  | `5.1`               | 调整破碎 · 裂缝偏差 0–6 步长 0.05                                                 |
| `crumbleDuration`           | number  | `0.35`              | 调整破碎 · 刷子持续时间 0–2 步长 0.01                                    |
| `ejectSpeed`                | number  | `0.91`              | 飞行 · 喷射速度 0–4 步长 0.01                                                            |
| `ejectSpread`               | number  | `0.48`              | 飞行 · 沿法线喷射扩散 0–3 步长 0.01                                          |
| `ejectTurbulence`           | number  | `4`                 | 飞行 · 喷射湍流 0–4 步长 0.01                                                       |
| `drag`                      | number  | `0`                 | 飞行 · 拖曳（每秒速度衰减） 0–8 步长 0.01                                 |
| `gravity`                   | number  | `0`                 | 飞行 · 重力（0 = 碎片永远不会坠落） 0–2 步长 0.005                                       |
| `turbulence`                | number  | `4`                 | 飞行 · 湍流强度（卷曲噪声） 0–4 步长 0.01                                       |
| `turbulenceScale`           | number  | `2.65`              | 飞行 · 湍流比例 0.2–8 步长 0.05                                                     |
| `turbulenceDecay`           | number  | `3.65`              | 飞行 · 湍流随年龄衰减（低 = 保持旋转） 0.05–4 步长 0.01                    |
| `clumpCohesion`             | number  | `0.9`               | 飞行 · 簇凝聚力（碎片围绕领导者；0 = 无） 0–10 步长 0.05                      |
| `followObject`              | number  | `30`                | 飞行 · 碎片跟随物体运动时间 (s; 30 = 整个飞行) 0–30 步长 0.5             |
| `settleTime`                | number  | `2.2`               | 飞行 · 沉淀时间（速度在此后停止；12 = 从不） 0.3–12 步长 0.05             |
| `settledDrift`              | number  | `1`                 | 飞行 · 沉淀后的有机漂移（卷曲噪声） 0–1 步长 0.005                               |
| `maxSpeed`                  | number  | `26.3`              | 飞行 · 速度限制 1–40 步长 0.1                                                              |
| `repelStrength`             | number  | `30`                | 飞行 · 推出固体形状时 0–30 步长 0.1                            |
| `repelRange`                | number  | `0.97`              | 飞行 · 表面外的推程 0.02–2 步长 0.01                                      |
| `repelRadial`               | number  | `17.5`              | 飞行 · 从形状中心推离（清除口袋和孔洞） 0–60 步长 0.5          |
| `repelRadialRange`          | number  | `3.3`               | 飞行 · 径向推程范围（物体半径） 1–4 步长 0.05                                       |
| `tumble`                    | number  | `1.05`              | 飞行 · 翻滚速率 0–12 步长 0.05                                                           |
| `returnGroupStagger`        | number  | `1.35`              | 装配 · 区域延迟（秒） 0–1.5 步长 0.05                                           |
| `returnGroupScale`          | number  | `2.55`              | 装配 · 区域/噪声大小 0.1–3 步长 0.05                                                |
| `returnGroupSeed`           | number  | `60765`             | 返回 · 簇时间种子 0–65535 步长 1                                                     |
| `formSpread`                | number  | `0`                 | 返回 · 波浪扩散（最近的碎片首先离开，随后） 0–4 步长 0.05                      |
| `waveReach`                 | number  | `10`                | 返回 · 波浪扩散距离 0.2–10 步长 0.1                                 |
| `formJitter`                | number  | `2.8`               | 返回 · 每个碎片的随机延迟（最多此值） 0–3 步长 0.05                            |
| `formFill`                  | number  | `3`                 | 返回 · 空间体填充速率（碎片返回） 0.05–3 歡长 0.05                         |
| `returnSpring`              | number  | `29.9`              | 返回 · 弹簧刚度 0.5–40 步长 0.1                                                     |
| `returnDamping`             | number  | `1.34`              | 返回 · 弹簧阻尼 0.2–2 步长 0.01                                                       |
| `returnRamp`                | number  | `0.45`              | 返回 · 弹簧斜坡（秒内达到全强度） 0–3 步长 0.05               |
| `returnMaxSpeed`            | number  | `60`                | 返回 · 返回时的速度限制 1–60 步长 0.5                                              |
| `alignToSurface`            | number  | `1`                 | 返回 · 碎片转向表面（0 = 保持翻滚） 0–1 步长 0.01                                |
| `alignCurve`                | number  | `3.75`              | 返回 · 返回时的对齐曲线（1 线性，更高 = 更晚） 0.2–4 步长 0.05      |
| `healRate`                  | number  | `3`                 | 返回 · 邻居愈合速率 0.02–3 步长 0.01                                                 |
| `cellRestore`               | number  | `60`                | 返回 · 细胞恢复速率 0–60 步长 0.5                                                      |
| `landedFade`                | number  | `1.65`              | 返回 · 着陆碎片淡出 0–2 步长 0.01                                                      |
| `refrostTime`               | number  | `10.6`              | 返回 · 重新结霜时间 0.2–12 步长 0.1                                                         |
| `keyColor`                  | color   | `"#f0f7ff"`         | 光 · 关键颜色                                                                            |
| `keyIntensity`              | number  | `5.05`              | 光 · 关键强度 0–12 步长 0.05                                                          |
| `keyElevation`              | number  | `42`                | 光 · 关键高度 10–89 步长 0.5                                                          |
| `keyAzimuth`                | number  | `-38`               | 光 · 关键方位 -90–90 步长 0.5                                                           |
| `keySize`                   | number  | `1.25`              | 光 · 关键大小（柔光罩） 0.2–3 步长 0.01                                                    |
| `fill`                      | number  | `0.18`              | 光 · 填充强度（半球，仅漫射：几乎不显示在透明冰上） 0–1.5 步长 0.005 |
| `fillColor`                 | color   | `"#cadde9"`         | 光 · 填充天空颜色                                                                       |
| `fillGroundColor`            | color   | `"#172635"`         | 光 · 填充地面颜色                                                                    |
| `rim`                       | number  | `2.5`               | 光 · 边缘光强度 0–5 步长 0.01                                                      |
| `rimColor`                  | color   | `"#d9f1ff"`         | 光 · 边缘颜色                                                                            |
| `rimElevation`              | number  | `20`                | 光 · 边缘高度（0 = 直后） 0–89 步长 0.5                                     |
| `swayAmplitude`             | number  | `0`                 | 光 · 关键摇摆振幅 0–0.15 步长 0.001                                                  |
| `swayPeriod`                | number  | `35`                | 光 · 关键摇摆周期 2–40 步长 0.5                                                         |
| `envSoftbox`                | number  | `1.1`               | 光 · 环境柔光罩（玻璃上的主光） 0–3 步长 0.01                           |
| `envRim`                    | number  | `1.4`               | 光 · 环境边缘条 0–3 步长 0.01                                                   |
| `envFill`                   | number  | `0.22`              | 光 · 环境前填充 0–1 步长 0.005                                                 |
| `backdropTop`               | color   | `"#050505"`         | 背景板 · 顶部颜色                                                                         |
| `backdropMid`               | color   | `"#050505"`         | 背景板 · 中部颜色                                                                         |
| `backdropBottom`              | color   | `"#050505"`         | 背景板 · 底部颜色                                                                          |
| `backdropCenterX`           | number  | `0.73`              | 背景板 · 花瓣中心 X 0–1 步长 0.005                                                      |
| `backdropCenterY`           | number  | `0.22`              | 背景板 · 花瓣中心 Y 0–2 步长 0.005                                                      |
| `backdropRadius`             | number  | `0.8`               | 背景板 · 花瓣半径 0.1–2 步长 0.005                                                      |
| `backdropFalloff`        | number  | `0.85`              | 背景板 · 花瓣衰减 0.5–6 步长 0.01                                                      |
| `backdropNoise`             | number  | `0`                 | 背景板 · 梯度噪声 0–3 步长 0.05                                                         |
| `bloomThreshold`            | number  | `3`                 | 后处理 · 花瓣阈值 0–3 步长 0.01                                                          |
| `bloomIntensity`            | number  | `0.04`              | 后处理 · 花瓣强度 0–1.5 步长 0.005                                                       |
| `bloomRadius`            | number  | `1`                 | 后处理 · 花瓣半径 0–1 步长 0.005                                                            |
| `monochrome`                | number  | `0.04`              | 后处理 · 单色 0–1 步长 0.01                                                               |
| `tonemap`                   | enum    | `"aces"`            | 后处理 · 色彩映射（agx                                                                           | aces          | 中性                    | 线性) |
| `exposure`                  | number  | `1`                 | 后处理 · 曝光 0.1–4 步长 0.01                                                               |
| `contrast`                  | number  | `1.03`              | 后处理 · 对比度 0.6–1.6 步长 0.005                                                            |
| `blackLift`                 | number  | `0`                 | 后处理 · 黑色提升 0–0.1 步长 0.001                                                            |
| `vignetteStrength`            | number  | `0.14`              | 后处理 · 色外线强度 0–1 步长 0.005                                                       |
| `vignetteSoftness`            | number  | `1.2`               | 后处理 · 色外线柔和度 0.1–1.5 步长 0.005                                                   |
| `vignetteRadius`            | number  | `1.2`               | 后处理 · 色外线半径 0.2–1.6 步长 0.005                                                   |
| `grainStrength`            | number  | `0`                 | 后处理 · 电影颗粒 0–0.15 步长 0.001                                                            |
| `quality`                   | enum    | `"full"`            | 性能 · 质量配置文件 (full                                                           | lite)         |
| `upscaler`                  | enum    | `"fsr1"`            | 性能 · 上采样器 (fsr1                                                                  | taau          | 双线性                   | 原生) |
| `renderScale`               | number  | `1`                 | 性能 · 场景分辨率比例（上采样到 1080p） 0.35–1 步长 0.05                     |
| `shapeResolution`           | enum    | `"256"`             | 形状体素分辨率 (128                                                                   | 256           | 384)                       |
| `erosionResolution`         | enum    | `"96"`              | 性能 · 侵蚀场分辨率（每个轴的体素） (64                                  | 96            | 128                        | 192)    |
| `particleCount`             | enum    | `"100k"`            | 性能 · 粉末粒子 (100k                                                          | 250k          | 500k                       | 1M)     |
| `logoMeshDetail`            | number  | `2`                 | 形状 · Logo网格细节 (1-4; 更高 = 更精细的表面) 1–4 步长 1                             |
| `deformStrength`            | number  | `0`                 | 几何 · 冰晶变形强度 (0 = 原始) 0–0.08 步长 0.001                          |
| `deformScale`            | number  | `0.41`              | 几何 · 噪声特征大小（更大 = 更宽泛） 0.001–0.5 步长 0.001                         |
| `deformSeed`            | number  | `7`                 | 几何 · 变形种子 0–65535 步长 1                                                    |
| `rimAzimuth`            | number  | `-146`              | 光 · 边缘方位 -180–180 步长 1                                                           |
| `rimAngle`             | number  | `26`                | 光 · 边缘光束角度 10–89 步长 1                                                           |
| `rimSize`             | number  | `0.45`              | 光 · 边缘反射大小 0.1–3 步长 0.05                                                   |
| `fillReflectionStrength`    | number  | `0.3`               | 光 · 填充反射强度 0–2 步长 0.01                                                |
| `accentCoolIntensity`    | number  | `3.71`              | 工作室冷色调强调 · 强度 0–4 步长 0.01                                                  |
| `accentCoolReflection`    | number  | `2.31`              | 工作室冷色调强调 · 反射 0–3 步长 0.01                                                 |
| `accentCoolElevation`    | number  | `63`                | 工作室冷色调强调 · 高度 -85–85 步长 1                                                  |
| `accentCoolAzimuth`    | number  | `22`                | 工作室冷色调强调 · 方位 -180–180 步长 1                                                  |
| `accentCoolSize`            | number  | `2.65`              | 工作室冷色调强调 · 大小 0.1–3 步长 0.05                                                  |
| `accentCoolColor`            | color   | `"#ff5900"`         | 工作室冷色调强调 · 颜色                                                                    |
| `accentWarmIntensity`    | number  | `2.99`              | 工作室暖色调强调 · 强度 0–4 步长 0.01                                                  |
| `accentWarmReflection`    | number  | `0.34`              | 工作室暖色调强调 · 反射 0–3 步长 0.01                                                 |
| `accentWarmElevation`    | number  | `30`                | 工作室暖色调强调 · 高度 -85–85 步长 1                                                  |
| `accentWarmAzimuth`    | number  | `-30`               | 工作室暖色调强调 · 方位 -180–180 步长 1                                                  |
| `accentWarmSize`            | number  | `1.2`               | 工作室暖色调强调 · 大小 0.1–3 步长 0.05                                                  |
| `accentWarmColor`            | color   | `"#75aaff"`         | 工作室暖色调强调 · 颜色                                                                    |
| `returnNoiseAmount`         | enum    | `"2"`               | 装配 · 区域模式 (2                                                                | 1             | 0)                         |
| `assemblyFrontDuration`     | number  | `3.2`               | 装配 · 生长持续时间（秒） 0–6 步长 0.05                                            |
| `assemblyOriginX`          | number  | `-0.65`             | 装配 · 生长起始 X -1–1 步长 0.01                                                      |
| `assemblyOriginY`          | number  | `0.55`              | 装配 · 生长起始 Y -1–1 步长 0.01                                                      |
| `assemblyAngle`          | number  | `-35`               | 装配 · 缝合方向（度） -180–180 步长 1                                           |
| `assemblySpread`          | number  | `0.65`              | 装配 · 向外扩散与缝合旅行 0–1 步长 0.01                                        |
| `assemblyFrontNoise`         | number  | `0.35`              | 装配 · 生长边缘不规则性 0–1 步长 0.01                                             |
| `assemblySpeedVariation`     | number  | `0.65`              | 装配 · 返回速度变化 0–1 步长 0.01                                             |
| `assemblyBend`          | number  | `1.2`               | 装配 · 接近路径弯曲 0–3 步长 0.05                                                   |
| `assemblySwirl`          | number  | 装配 · 接近扭曲 0–3 步长 0.05                                                   |
| `assemblyLandingVariation`   | number  | `0.8`               | 装配 · 着陆过渡变化 0–1 步长 0.01                                         |
| `rendererProfile`         | enum    | `"studio"`          | 渲染器实验（需要重新加载） (原始                                               | lookup        | 网格                       | 工作室  | matcap) |
| `textWidth`                 | number  | `6.5`               | 类型 · 标题块宽度（标志宽度为2.6） 1.2–9 步长 0.05                            |
| `textLineHeight`            | number  | `0.95`              | 类型 · 行高 0.7–1.4 步长 0.01                                                          |
| `textDepth`                 | number  | `0.16`              | 类型 · 挤出深度（字体大小的分数） 0.05–0.8 步长 0.01                                         |
| `textBevel`                 | number  | `0.04`              | 类型 · 斜角（字体大小的分数） 0–0.12 步长 0.005                                    |
| `textCorner`                 | number  | `0.008`             | 类型 · 角圆滑度（字体大小的分数） 0–0.06 步长 0.002                          |
| `textMeshDetail`            | number  | `4`                 | 类型 · 文本网格细节 (1-4; 更高 = 更平滑的变形) 1–4 步长 1                             |

## 运行时契约

- 一个暂停的GSAP时间轴注册为 `window.__timelines["frost-sequence-rig"]`。
- 通过 `hf-seek` CustomEvent重新同步；每一帧都是时间的闭式函数（仅种子PRNG，无rAF循环，无Date.now）。
- 渲染器：WebGPU, GSAP, Matcap。
- 外部运行时依赖项：无（本地提供）。

## 编辑规则（来自源项目）

1. 保持 `data-composition-variables` 为单引号属性，使用纯 `"` JSON。不要通过Studio的Design面板保存它。
2. 不要将 `<canvas>` 放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为t的函数；seek安全性是使其可渲染的原因。
