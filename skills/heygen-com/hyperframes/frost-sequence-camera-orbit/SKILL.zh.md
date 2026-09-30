---
name: frost-sequence-camera-orbit
description: 一个环绕的摄像机跟随一个冰晶标志，它分解、重新组合成两个文字时刻，然后逐渐淡出。HyperFrames画面，1920×1080，22.5秒，216个变量。
---

# 冰霜序列相机轨道

一个完整的22.5秒冰霜序列：标志、第一行文字、第二行文字、分离和淡出。相机围绕固定物体进行轨道运动，并在面向前方的路径上减速以便读取。相同的粒子场承载每个过渡效果。可自定义两行文字时刻和SVG标志；源文件包含可编辑的相机和组装时间。

组合ID：`frost-sequence-rig`。时长22.5秒，帧率30 fps，分辨率1920×1080。

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

使用 `npx hyperframes add frost-sequence-camera-orbit` 安装；默认情况下，上述文件将位于 `compositions/frost-sequence-camera-orbit/` 下。然后从宿主 `index.html` 中挂载该模块：

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

通过直接指向组合文件来使用自定义值进行渲染：

```sh
npx --yes hyperframes@0.8.12 render 'compositions/frost-sequence-camera-orbit/frost-sequence-camera-orbit.html' --variables '{"headline1":"Hard to|break.","headline2":"Easy to|remember."}'
```

## 变量

通过 `window.__hyperframes.getVariables()` 在运行时读取；在组合根节点上声明为 `data-composition-variables`（单引号属性，纯JSON格式）。

| id                          | type    | default             | label / range                                                                                 |
| --------------------------- | ------- | ------------------- | --------------------------------------------------------------------------------------------- | ------------- | -------------------------- | ------- | ------- |
| `headline1`                 | string  | `"Hard to           | break."`                                                                                      | First text (  | = line break) max 60 chars |
| `headline2`                 | string  | `"Easy to           | remember."`                                                                                   | Second text ( | = line break) max 60 chars |
| `logoUrl`                   | string  | `"assets/logo.svg"` | Logo SVG asset path (upload in Assets, then paste path) max 200 chars                         |
| `assemblyMode`              | enum    | `"hybrid"`          | Assembly response (physical                                                                   | directed      | hybrid)                    |
| `materialBaseColor`         | color   | `"#ffffff"`         | Base color                                                                                    |
| `baseRoughness`             | number  | `0.31`              | Base roughness 0–0.5 step 0.005                                                               |
| `materialTransmission`      | boolean | `true`              | Transmission                                                                                  |
| `materialBacklight`         | number  | `0.27`              | Backlight through ice 0–2 step 0.01                                                           |
| `ior`                       | number  | `1.675`             | Index of refraction 1–2 step 0.005                                                            |
| `thicknessScale`            | number  | `2.04`              | Thickness scale 0.1–3 step 0.01                                                               |
| `materialAbsorption`        | boolean | `true`              | Absorption / tint                                                                             |
| `attenuationColor`          | color   | `"#d5f4ff"`         | Attenuation colour (white = no absorption, clear glass)                                       |
| `attenuationDistance`       | number  | `6.54`              | Attenuation distance 0.05–12 step 0.01                                                        |
| `materialDispersion`        | boolean | `false`             | Dispersion                                                                                    |
| `dispersion`                | number  | `0.12`              | Dispersion (0 = off; on/off reloads) 0–0.3 step 0.005                                         |
| `materialReflections`       | boolean | `true`              | Reflections                                                                                   |
| `envIntensity`              | number  | `2.04`              | Environment intensity 0–3 step 0.01                                                           |
| `specularIntensity`         | number  | `1.44`              | Specular intensity 0–2 step 0.01                                                              |
| `materialFrost`             | boolean | `true`              | Frost                                                                                         |
| `materialInteriorFrost`     | number  | `0`                 | Uniform frost 0–1 step 0.01                                                                   |
| `frostScale`                | number  | `0.7`               | Scale 0.2–6 step 0.05                                                                         |
| `frostThreshold`            | number  | `0.62`              | Threshold (1 = no frost, clear glass) 0–1 step 0.01                                           |
| `frostSoftness`             | number  | `0.24`              | Softness 0.01–1 step 0.01                                                                     |
| `frostRoughness`            | number  | `0.73`              | Roughness 0–1 step 0.01                                                                       |
| `frostDiffuse`              | number  | `0.11`              | Diffuse (how much light frosted areas catch) 0–1 step 0.01                                    |
| `materialSurfaceBumps`      | boolean | `false`             | Object surface bumps / crack notches                                                          |
| `materialCrystals`          | boolean | `true`              | Crystal bumps                                                                                 |
| `crystalBump`               | number  | `0.01`              | Crystal bump 0–1 step 0.01                                                                    |
| `crystalScale`              | number  | `4`                 | Crystal scale 4–80 step 1                                                                     |
| `materialGrain`             | boolean | `true`              | Grain bumps                                                                                   |
| `materialGrainAmount`       | number  | `0.47`              | Grain strength 0–2 step 0.01                                                                  |
| `materialGrainScale`        | number  | `150`               | Grain scale 1–150 step 1                                                                      |
| `materialCutNormals`        | boolean | `true`              | Fracture normals                                                                              |
| `materialMicro`             | boolean | `true`              | Micro bumps                                                                                   |
| `microBump`                 | number  | `0.445`             | Micro bump 0–1 step 0.005                                                                     |
| `microScale`                | number  | `10`                | Micro scale 10–200 step 1                                                                     |
| `microCoverage`             | number  | `0.25`              | Micro coverage 0–1 step 0.01                                                                  |
| `bumpMaskScale`             | number  | `1.45`              | Mask scale 0.1–6 step 0.05                                                                    |
| `materialRipples`           | boolean | `true`              | Ripples                                                                                       |
| `rippleBump`                | number  | `0.22`              | Ripple bump 0–1 step 0.01                                                                     |
| `rippleScale`               | number  | `23`                | Ripple scale 2–30 step 0.5                                                                    |
| `materialSmudges`           | boolean | `true`              | Smudges                                                                                       |
| `smudgeAmount`              | number  | `0.78`              | Amount 0–1 step 0.01                                                                          |
| `smudgeCoverage`            | number  | `0.58`              | Coverage 0–1 step 0.01                                                                        |
| `smudgeMaskScale`           | number  | `1.85`              | Mask scale 0.1–6 step 0.05                                                                    |
| `smudgeAnisotropy`          | number  | `16.5`              | Anisotropy 1–20 step 0.5                                                                      |
| `smudgeRoughness`           | number  | `0.75`              | Roughness 0–1 step 0.01                                                                       |
| `smudgeWhiteness`           | number  | `0.035`             | Whiteness 0–0.5 step 0.005                                                                    |
| `smudgeScale`               | number  | `1.3`               | Scale 0.5–10 step 0.1                                                                         |
| `materialCracks`            | boolean | `true`              | Cracks                                                                                        |
| `crackLargeScale`           | number  | `2.45`              | Large scale 0.3–8 step 0.05                                                                   |
| `crackWarp`                 | number  | `0.22`              | Warp 0–1.5 step 0.01                                                                          |
| `crackCoverage`             | number  | `0.19`              | Coverage 0–1 step 0.01                                                                        |
| `crackRegionScale`          | number  | `1.8`               | Region scale 0.1–4 step 0.05                                                                  |
| `crackRegionCoverage`       | number  | `0.6`               | Region coverage 0–1 step 0.01                                                                 |
| `veinScale`                 | number  | `8`                 | Vein scale 1–20 step 0.25                                                                     |
| `veinContrast`              | number  | `0.55`              | Vein contrast 0–1 step 0.01                                                                   |
| `crackWidth`                | number  | `0.0025`            | Width 0.0005–0.02 step 0.0005                                                                 |
| `crackBrightness`           | number  | `0.65`              | Brightness 0–3 step 0.01                                                                      |
| `crackDarkness`             | number  | `0.69`              | Darkness 0–1 step 0.01                                                                        |
| `crackRefraction`           | number  | `0.076`             | Refraction 0–0.1 step 0.001                                                                   |
| `crackSurfaceStrength`      | number  | `0.16`              | Surface strength 0–1 step 0.01                                                                |
| `fineScale`                 | number  | `18.4`              | Fine scale 2–20 step 0.1                                                                      |
| `fineAmount`                | number  | `0.52`              | Fine amount 0–1 step 0.01                                                                     |
| `fineCoverage`              | number  | `1`                 | Fine coverage 0–1 step 0.01                                                                   |
| `materialScatter`           | boolean | `true`              | Internal scattering                                                                           |
| `materialInclusionScale`    | number  | `0.05`              | Inclusion scale 0.05–3 step 0.01                                                              |
| `materialInclusionAmount`   | number  | `2`                 | Photographic inclusions 0–2 step 0.01                                                         |
| `interiorScatter`           | number  | `0.09`              | Interior scatter 0–1 step 0.01                                                                |
| `materialClearcoat`         | boolean | `true`              | Clearcoat                                                                                     |
| `clearcoat`                 | number  | `0`                 | Clearcoat 0–1 step 0.01                                                                       |
| `clearcoatRoughness`        | number  | `0`                 | Clearcoat roughness 0–1 step 0.005                                                            |
| `materialShardNormals`      | boolean | `true`              | Shard normals                                                                                 |
| `spriteNormal`              | number  | `0.15`              | Sprite normal strength 0–2.5 step 0.05                                                        |
| `materialShardFrost`        | boolean | `true`              | Shard frost                                                                                   |
| `materialShardTransmission` | boolean | `true`              | Shard transparency                                                                            |
| `spriteSeeThrough`          | number  | `1`                 | See-through (0 = off; on/off reloads) 0–1 step 0.01                                           |
| `materialShardReflections`  | boolean | `true`              | Shard reflections                                                                             |
| `minPixelSize`              | number  | `0.25`              | Minimum pixel size 0–4 step 0.05                                                              |
| `grainSizeMultiplier`       | number  | `1.05`              | Grain size multiplier 0.2–4 step 0.05                                                         |
| `spriteSize`                | number  | `1.9`               | Sprite size 0.3–4 step 0.05                                                                   |
| `spriteTilt`                | number  | `12`                | Sprite tilt 0–70 step 1                                                                       |
| `spriteAlphaCut`            | number  | `0.6`               | Alpha cut 0.05–0.6 step 0.01                                                                  |
| `fontWeight`                | enum    | `"600"`             | Type · Weight (Geist) (400                                                                    | 600           | 700)                       |
| `letterSpacing`             | number  | `0.01`              | Type · Letter spacing -0.1–0.4 step 0.005                                                     |
| `shardAmount`               | number  | `0.44`              | Shards · Visible fraction of the broken volume (Powder amount) 0.02–1 step 0.01               |
| `strayDust`                 | number  | `24`                | Shards · Ambient dust motes around the object (the experiment had 40) 0–200 step 1            |
| `sliceRadius`               | number  | `0.6`               | Break · First (diagonal) slice radius 0.05–1.5 step 0.01                                      |
| `sliceStrength`             | number  | `21.5`              | Break · First slice strength 1–40 step 0.5                                                    |
| `finalEjectBoost`           | number  | `2.5`               | Break · Last break: eject speed and speed cap multiplier 1–6 step 0.1                         |
| `shatterRadius`             | number  | `0.45`              | Break · Follow-up slice radius (sets their spacing too) 0.1–1.5 step 0.01                     |
| `shatterStrength`           | number  | `32.5`              | Break · Follow-up slice strength 1–40 step 0.5                                                |
| `cutThreshold`              | number  | `0.3`               | Tune break · Cut threshold (surface gone above this erosion) 0.3–0.98 step 0.01               |
| `cutSoftness`               | number  | `0.19`              | Tune break · Cut softness 0.005–0.3 step 0.005                                                |
| `edgeWidth`                 | number  | `0.19`              | Tune break · Crumbly edge band width 0.05–0.8 step 0.01                                       |
| `edgeInset`                 | number  | `0`                 | Tune break · Edge inset 0–0.3 step 0.005                                                      |
| `brushSoftness`             | number  | `0.15`              | 调整断裂 · 笔刷柔软度（切片边缘衰减）0.02–1 步长 0.01                        |
| `brushNoise`                | number  | `0.4`               | 调整断裂 · 笔刷噪声（不规则边界）0–1 步长 0.01                                      |
| `crumbleRate`               | number  | `4.3`               | 调整断裂 · 沿裂缝的碎裂速率（高 = 整个形状一次性碎裂）0–6 步长 0.05    |
| `crumbleCrackBias`          | number  | `5.1`               | 调整断裂 · 碎裂裂缝偏差 0–6 步长 0.05                                                 |
| `crumbleDuration`           | number  | `0.35`              | 调整断裂 · 笔画后的碎裂持续时间 0–2 步长 0.01                                    |
| `ejectSpeed`                | number  | `0.91`              | 飞行 · 排出速度 0–4 步长 0.01                                                            |
| `ejectSpread`               | number  | `0.48`              | 飞行 · 沿法线方向的排出扩散 0–3 步长 0.01                                          |
| `ejectTurbulence`           | number  | `4`                 | 飞行 · 排出湍流 0–4 步长 0.01                                                       |
| `drag`                      | number  | `0`                 | 飞行 · 阻力（每秒速度衰减量）0–8 步长 0.01                                 |
| `gravity`                   | number  | `0`                 | 飞行 · 重力（0 = 碎片永不坠落）0–2 步长 0.005                                       |
| `turbulence`                | number  | `4`                 | 飞行 · 湍流强度（涡旋噪声）0–4 步长 0.01                                       |
| `turbulenceScale`           | number  | `2.65`              | 飞行 · 湍流比例 0.2–8 步长 0.05                                                     |
| `turbulenceDecay`           | number  | `3.65`              | 飞行 · 湍流随时间衰减（低 = 保持旋转）0.05–4 步长 0.01                    |
| `clumpCohesion`             | number  | `0.9`               | 飞行 · 碎片团凝聚力（碎片围绕领导者旋转；0 = 无）0–10 步长 0.05                      |
| `followObject`              | number  | `30`                | 飞行 · 碎片跟随物体运动时间（s；30 = 整个飞行）0–30 步长 0.5             |
| `settleTime`                | number  | `2.2`               | 飞行 · 沉降时间（速度在此后消失；12 = 永不）0.3–12 步长 0.05             |
| `settledDrift`              | number  | `1`                 | 飞行 · 沉降后的有机漂移（涡旋噪声）0–1 步长 0.005                               |
| `maxSpeed`                  | number  | `26.3`              | 飞行 · 速度上限 1–40 步长 0.1                                                              |
| `repelStrength`             | number  | `30`                | 飞行 · 在碎裂时将固体形状推出去 0–30 步长 0.1                            |
| `repelRange`                | number  | `0.97`              | 飞行 · 表面外的推力范围 0.02–2 步长 0.01                                      |
| `repelRadial`               | number  | `17.5`              | 飞行 · 从形状中心推开（清除口袋和空洞）0–60 步长 0.5          |
| `repelRadialRange`          | number  | `3.3`               | 飞行 · 径向推力范围（对象半径）1–4 步长 0.05                                       |
| `tumble`                    | number  | `1.05`              | 飞行 · 翻滚速率 0–12 步长 0.05                                                           |
| `returnGroupStagger`        | number  | `1.35`              | 组装 · 区域延迟（秒）0–1.5 步长 0.05                                           |
| `returnGroupScale`          | number  | `2.55`              | 组装 · 区域/噪声大小 0.1–3 步长 0.05                                                |
| `returnGroupSeed`           | number  | `60765`             | 返回 · 组团时间种子 0–65535 步长 1                                                     |
| `formSpread`                | number  | `0`                 | 返回 · 波浪扩散（最近的碎片最先离开，秒）0–4 步长 0.05                      |
| `waveReach`                 | number  | `10`                | 返回 · 波浪扩散距离 0.2–10 步长 0.1                                 |
| `formJitter`                | number  | `2.8`               | 返回 · 每个碎片的随机延迟（随机延迟量）0–3 步长 0.05                            |
| `formFill`                  | number  | `3`                 | 返回 · 无碎片返回的体素填充速率 0.05–3 步长 0.05                         |
| `returnSpring`              | number  | `29.9`              | 返回 · 弹簧刚度 0.5–40 步长 0.1                                                     |
| `returnDamping`             | number  | `1.34`              | 返回 · 弹簧阻尼 0.2–2 步长 0.01                                                       |
| `returnRamp`                | number  | `0.45`              | 返回 · 弹簧预充能（秒，直到完全强度）0–3 步长 0.05               |
| `returnMaxSpeed`            | number  | `60`                | 返回 · 返回途中的速度上限 1–60 步长 0.5                                              |
| `alignToSurface`            | number  | `1`                 | 返回 · 碎片转向平铺表面（0 = 保持翻滚）0–1 步长 0.01                  |
| `alignCurve`                | number  | `3.75`              | 返回 · 返回途中的对齐曲线（1 线性，更高 = 更晚）0.2–4 步长 0.05      |
| `healRate`                  | number  | `3`                 | 返回 · 邻居自愈速率 0.02–3 步长 0.01                                                 |
| `cellRestore`               | number  | `60`                | 返回 · 细胞恢复速率 0–60 步长 0.5                                                      |
| `landedFade`                | number  | `1.65`              | 返回 · 着陆碎片淡出 0–2 步长 0.01                                                      |
| `refrostTime`               | number  | `10.6`              | 返回 · 再冻结时间 0.2–12 步长 0.1                                                         |
| `keyColor`                  | color   | `"#f0f7ff"`         | 光照 · 主色                                                                            |
| `keyIntensity`              | number  | `5.05`              | 光照 · 主光强度 0–12 步长 0.05                                                          |
| `keyElevation`              | number  | `42`                | 光照 · 主光高度 10–89 步长 0.5                                                          |
| `keyAzimuth`                | number  | `-38`               | 光照 · 主光方位角 -90–90 步长 0.5                                                           |
| `keySize`                   | number  | `1.25`              | 光照 · 主光大小（柔光罩）0.2–3 步长 0.01                                                    |
| `fill`                      | number  | `0.18`              | 光照 · 填充强度（半球，仅漫反射：几乎不显示在透明冰上）0–1.5 步长 0.005 |
| `fillColor`                 | color   | `"#cadde9"`         | 光照 · 填充天空颜色                                                                       |
| `fillGroundColor`           | color   | `"#172635"`         | 光照 · 填充地面颜色                                                                    |
| `rim`                       | number  | `2.5`               | 光照 · 轮廓光强度 0–5 步长 0.01                                                      |
| `rimColor`                  | color   | `"#d9f1ff"`         | 光照 · 轮廓光颜色                                                                            |
| `rimElevation`              | number  | `20`                | 光照 · 轮廓光高度（0 = 直线后方）0–89 步长 0.5                                     |
| `swayAmplitude`             | number  | `0`                 | 光照 · 主光摇摆幅度 0–0.15 步长 0.001                                                  |
| `swayPeriod`                | number  | `35`                | 光照 · 主光摇摆周期 2–40 步长 0.5                                                         |
| `envSoftbox`                | number  | `1.1`               | 光照 · 环境柔光罩（玻璃上的主光）0–3 步长 0.01                           |
| `envRim`                    | number  | `1.4`               | 光照 · 环境轮廓光带 0–3 步长 0.01                                                   |
| `envFill`                   | number  | `0.22`              | 光照 · 环境正面填充 0–1 步长 0.005                                                 |
| `backdropTop`               | color   | `"#050505"`         | 背景板 · 顶部颜色                                                                         |
| `backdropMid`               | color   | `"#050505"`         | 背景板 · 中部颜色                                                                         |
| `backdropBottom`            | color   | `"#050505"`         | 背景板 · 底部颜色                                                                      |
| `backdropCenterX`           | number  | `0.73`              | 背景板 · 花瓣中心 X 0–1 步长 0.005                                                      |
| `backdropCenterY`           | number  | `0.22`              | 背景板 · 花瓣中心 Y 0–2 步长 0.005                                                      |
| `backdropRadius`            | number  | `0.8`               | 背景板 · 花瓣半径 0.1–2 步长 0.005                                                      |
| `backdropFalloff`           | number  | `0.85`              | 背景板 · 花瓣衰减 0.5–6 步长 0.01                                                      |
| `backdropNoise`             | number  | `0`                 | 背景板 · 梯度噪声 0–3 步长 0.05                                                         |
| `bloomThreshold`            | number  | `3`                 | 后处理 · 花瓣阈值 0–3 步长 0.01                                                          |
| `bloomIntensity`            | number  | `0.04`              | 后处理 · 花瓣强度 0–1.5 步长 0.005                                                       |
| `bloomRadius`               | number  | `1`                 | 后处理 · 花瓣半径 0–1 步长 0.005                                                            |
| `monochrome`                | number  | `0.04`              | 后处理 · 单色 0–1 步长 0.01                                                               |
| `tonemap`                   | enum    | `"aces"`            | 后处理 · 色彩映射（agx                                                                           | aces          | neutral                    | linear) |
| `exposure`                  | number  | `1`                 | 后处理 · 曝光 0.1–4 步长 0.01                                                               |
| `contrast`                  | number  | `1.03`              | 后处理 · 对比度 0.6–1.6 步长 0.005                                                            |
| `blackLift`                 | number  | `0`                 | 后处理 · 黑色提升 0–0.1 步长 0.001                                                            |
| `vignetteStrength`          | number  | `0.14`              | 后处理 · 轮廓暗角强度 0–1 步长 0.005                                                       |
| `vignetteSoftness`          | number  | `1.2`               | 后处理 · 轮廓暗角柔和度 0.1–1.5 步长 0.005                                                   |
| `vignetteRadius`            | number  | `1.2`               | 后处理 · 轮廓暗角半径 0.2–1.6 步长 0.005                                                     |
| `grainStrength`             | number  | `0`                 | 后处理 · 胶片颗粒 0–0.15 步长 0.001                                                           |
| `quality`                   | enum    | `"full"`            | 性能 · 质量配置文件（全                                                           | lite)         |
| `upscaler`                  | enum    | `"fsr1"`            | 性能 · 上采样器（fsr1                                                                  | taau          | bilinear                   | native) |
| `renderScale`               | number  | `1`                 | 性能 · 场景分辨率比例（上采样至 1080p）0.35–1 步长 0.05                     |
| `shapeResolution`           | enum    | `"256"`             | 形状体素分辨率（128                                                                   | 256           | 384)                       |
| `erosionResolution`         | enum    | `"96"`              | 性能 · 侵蚀场分辨率（轴每轴的体素数）(64                                  | 96            | 128                        | 192)    |
| `particleCount`             | enum    | `"100k"`            | 性能 · 粉末粒子（100k                                                          | 250k          | 500k                       | 1M)     |
| `logoMeshDetail`            | number  | `2`                 | 形状 · Logo 网格细节（1-4；更高 = 更精细表面）1–4 步长 1                             |
| `deformStrength`            | number  | `0`                 | 几何 · 冰变形强度（0 = 原始）0–0.08 步长 0.001                          |
| `deformScale`               | number  | `0.41`              | 几何 · 噪声特征大小（更大 = 更宽）0.001–0.5 步长 0.001                         |
| `deformSeed`                | number  | `7`                 | 几何 · 变形种子 0–65535 步长 1                                                    |
| `rimAzimuth`                | number  | `-146`              | 光照 · 轮廓光方位角 -180–180 步长 1                                                           |
| `rimAngle`                  | number  | `26`                | 光照 · 轮廓光束角度 10–89 步长 1                                                           |
| `rimSize`                   | number  | `0.45`              | 光照 · 轮廓光反射大小 0.1–3 步长 0.05                                                   |
| `fillReflectionStrength`    | number  | `0.3`               | 光照 · 填充光反射强度 0–2 步长 0.01                                                |
| `accentCoolIntensity`       | number  | `3.71`              | 工作室冷色调 · 强度 0–4 步长 0.01                                                  |
| `accentCoolReflection`      | number  | `2.31`              | 工作室冷色调 · 反射 0–3 步长 0.01                                                 |
| `accentCoolElevation`       | number  | `63`                | 工作室冷色调 · 高度 -85–85 步长 1                                                  |
| `accentCoolAzimuth`         | number  | `22`                | 工作室冷色调 · 方位角 -180–180 步长 1                                                  |
| `accentCoolSize`            | number  | `2.65`              | 工作室冷色调 · 大小 0.1–3 步长 0.05                                                     |
| `accentCoolColor`           | color   | `"#ff5900"`         | 工作室冷色调 · 颜色                                                                    |
| `accentWarmIntensity`       | number  | `2.99`              | 工作室暖色调 · 强度 0–4 步长 0.01                                                  |
| `accentWarmElevation`       | number  | `30`                | Studio 温暖强调 · 垂直位移 -85–85 步长 1                                                  |
| `accentWarmAzimuth`         | number  | `-30`               | Studio 温暖强调 · 方位角 -180–180 步长 1                                                  |
| `accentWarmSize`            | number  | `1.2`               | Studio 温暖强调 · 大小 0.1–3 步长 0.05                                                     |
| `accentWarmColor`           | color   | `"#75aaff"`         | Studio 温暖强调 · 颜色                                                                    |
| `returnNoiseAmount`         | enum    | `"2"`               | 组装 · 区域图案 (2 1 0)                         |
| `assemblyFrontDuration`     | number  | `3.2`               | 组装 · 生长持续时间 (秒) 0–6 步长 0.05                                                        |
| `assemblyOriginX`           | number  | `-0.65`             | 组装 · 生长起始 X -1–1 步长 0.01                                                               |
| `assemblyOriginY`           | number  | `0.55`              | 组装 · 生长起始 Y -1–1 步长 0.01                                                               |
| `assemblyAngle`             | number  | `-35`               | 组装 · 缝合方向 (度) -180–180 步长 1                                                           |
| `assemblySpread`            | number  | `0.65`              | 组装 · 相对于缝合的向外扩散 0–1 步长 0.01                                                      |
| `assemblyFrontNoise`        | number  | `0.35`              | 组装 · 生长边缘不规则性 0–1 步长 0.01                                                         |
| `assemblySpeedVariation`    | number  | `0.65`              | 组装 · 返回速度变化 0–1 步长 0.01                                                            |
| `assemblyBend`              | number  | `1.2`               | 组装 · 接近路径弯曲 0–3 步长 0.05                                                              |
| `assemblySwirl`             | number  | `1.1`               | 组装 · 接近扭曲 0–3 步长 0.05                                                                 |
| `assemblyLandingVariation`  | number  | `0.8`               | 组装 · 着陆过渡变化 0–1 步长 0.01                                                              |
| `rendererProfile`           | enum    | `"studio"`          | 渲染器实验 (需要重新加载) (原始 lookup 网格 studio matcap) |
| `textWidth`                 | number  | `6.5`               | 字体 · 标题块宽度 (标记宽 2.6) 1.2–9 步长 0.05                                                  |
| `textLineHeight`            | number  | `0.95`              | 字体 · 行高 0.7–1.4 步长 0.01                                                                 |
| `textDepth`                 | number  | `0.16`              | 字体 · 拉伸深度 (字体大小的分数) 0.05–0.8 步长 0.01                                             |
| `textBevel`                 | number  | `0.04`              | 字体 · 斜角 (字体大小的分数) 0–0.12 步长 0.005                                                  |
| `textCorner`                | number  | `0.008`             | 字体 · 角圆润 (字体大小的分数) 0–0.06 步长 0.002                                                 |
| `textMeshDetail`            | number  | `4`                 | 字体 · 文本网格细节 (1-4; 更高 = 更平滑的变形) 1–4 步长 1                                          |

## 运行时合约

- 一个注册为 `window.__timelines["frost-sequence-rig"]` 的暂停的 GSAP 时间轴。
- 在 `hf-seek` CustomEvent 上重新同步；每一帧都是时间的闭式函数 (仅使用播种 PRNG，无 rAF 循环，无 Date.now)。
- 渲染器：WebGPU, GSAP, Matcap。
- 外部运行时依赖项：无 (本地提供)。

## 编辑规则 (来自源项目)

1. 保持 `data-composition-variables` 为单引号属性，使用纯 `"` JSON。切勿通过 Studio 的设计面板保存。
2. 不要将 `<canvas>` 放在静态标记中；在运行时创建它。
3. 保持每个视觉状态为 t 的函数；seek 安全性是使块可渲染的关键。
